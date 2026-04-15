"""
Cron routes — the two daily automated events.

POST /cron/daily-word   → 08:00 IST  — generate lesson, push to Telegram
POST /cron/evening-quiz → 20:00 IST  — send quiz prompt via Telegram
POST /cron/evaluate     → Telegram webhook → evaluate user's reply, update SRS
"""

import json
import logging
from datetime import date

from fastapi import APIRouter, Header, HTTPException, Request

from api.config import get_settings
from api.core.db import vocabulary_col, word_states_col, daily_log_col
from api.core.openrouter import generate_lesson_payload, evaluate_user_sentence
from api.core.srs import calculate_next_review, quality_from_llm_score
from api.core.telegram import (
    send_message,
    format_lesson_message,
    format_quiz_prompt,
    format_eval_result,
)
from api.models.user_state import EvaluationResult, DailyLogEntry

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Security helper ─────────────────────────────────────
def verify_cron_secret(x_cron_secret: str = Header(default="")):
    """Protect cron endpoints from unauthorized calls."""
    settings = get_settings()
    if settings.cron_secret and x_cron_secret != settings.cron_secret:
        raise HTTPException(status_code=401, detail="Invalid cron secret")


# ── Shared state key for today's word ───────────────────
async def get_todays_word() -> dict | None:
    """
    Fetch the word scheduled for today: the one with next_review <= today
    and status == 'new' (or 'sent' if morning already ran).
    Falls back to the first 'new' word if no specific review is due.
    """
    today = date.today().isoformat()
    col = word_states_col()

    # Priority 1: word due for spaced repetition review today
    state = await col.find_one(
        {"next_review": {"$lte": today}, "status": "new"},
        sort=[("next_review", 1)],
    )

    if state:
        vocab = await vocabulary_col().find_one({"hanzi": state["hanzi"]})
        return {**vocab, "state": state} if vocab else None

    # Priority 2: pick next unseen word in order (for new words)
    vocab = await vocabulary_col().find_one(
        {"hanzi": {"$nin": await _seen_hanzi()}},
        sort=[("hsk_level", 1)],
    )
    return vocab


async def _seen_hanzi() -> list[str]:
    """Return list of hanzi that have ever been sent."""
    col = word_states_col()
    cursor = col.find({}, {"hanzi": 1})
    return [doc["hanzi"] async for doc in cursor]


# ── POST /cron/daily-word ───────────────────────────────
@router.post("/cron/daily-word")
async def trigger_daily_word(x_cron_secret: str = Header(default="")):
    """
    Event 1 — 08:00 IST
    1. Query MongoDB for today's scheduled word
    2. Call OpenRouter (Claude Sonnet) for lesson payload
    3. Push formatted message to Telegram
    4. Update word_states status to 'sent'
    5. Write audit log
    """
    verify_cron_secret(x_cron_secret)
    today = date.today().isoformat()
    settings = get_settings()

    word = await get_todays_word()
    if not word:
        msg = "No words available. Seed the database first."
        logger.error(msg)
        raise HTTPException(status_code=404, detail=msg)

    hanzi = word["hanzi"]
    pinyin = word.get("pinyin", "")
    meaning = word.get("meaning", "")

    log_entry = {
        "date": today,
        "hanzi": hanzi,
        "event": "daily_push",
        "status": "failed",
        "model_used": settings.model_lesson,
    }

    try:
        # 1. Generate lesson via LLM
        lesson_json_str = await generate_lesson_payload(hanzi, pinyin, meaning)
        lesson = json.loads(lesson_json_str)

        # 2. Format and push to Telegram
        message = format_lesson_message(lesson)
        await send_message(message)

        # 3. Upsert word state → status: sent
        await word_states_col().update_one(
            {"hanzi": hanzi},
            {
                "$set": {
                    "hanzi": hanzi,
                    "status": "sent",
                    "next_review": today,
                },
                "$setOnInsert": {
                    "repetitions": 0,
                    "ease_factor": 2.5,
                    "interval": 1,
                    "streak": 0,
                    "total_reviews": 0,
                    "last_quality": None,
                },
            },
            upsert=True,
        )

        # 4. Log success
        log_entry["status"] = "success"
        await daily_log_col().insert_one(log_entry)

        logger.info(f"[cron:daily-word] Pushed '{hanzi}' to Telegram.")
        return {"status": "success", "word": hanzi, "model": settings.model_lesson}

    except Exception as e:
        log_entry["error"] = str(e)
        await daily_log_col().insert_one(log_entry)
        logger.exception(f"[cron:daily-word] Failed for '{hanzi}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── POST /cron/evening-quiz ─────────────────────────────
@router.post("/cron/evening-quiz")
async def trigger_evening_quiz(x_cron_secret: str = Header(default="")):
    """
    Event 2 — 20:00 IST
    Sends the quiz prompt for today's word via Telegram.
    The user's Telegram reply is handled by the webhook endpoint below.
    """
    verify_cron_secret(x_cron_secret)
    today = date.today().isoformat()

    # Find today's sent word
    state = await word_states_col().find_one(
        {"next_review": today, "status": "sent"}
    )
    if not state:
        # Fallback: find most recently sent word
        state = await word_states_col().find_one(
            {"status": "sent"}, sort=[("next_review", -1)]
        )

    if not state:
        raise HTTPException(status_code=404, detail="No word in 'sent' state found.")

    hanzi = state["hanzi"]
    vocab = await vocabulary_col().find_one({"hanzi": hanzi})
    meaning = vocab.get("meaning", "") if vocab else ""

    log_entry = {
        "date": today,
        "hanzi": hanzi,
        "event": "evening_quiz",
        "status": "failed",
    }

    try:
        message = format_quiz_prompt(hanzi, meaning)
        await send_message(message)

        log_entry["status"] = "success"
        await daily_log_col().insert_one(log_entry)

        logger.info(f"[cron:evening-quiz] Sent quiz for '{hanzi}'.")
        return {"status": "success", "word": hanzi}

    except Exception as e:
        log_entry["error"] = str(e)
        await daily_log_col().insert_one(log_entry)
        raise HTTPException(status_code=500, detail=str(e))


# ── POST /webhook/telegram ──────────────────────────────
@router.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    """
    Telegram webhook receiver.
    Triggered whenever the user sends any message to the bot.
    On receipt: evaluate the sentence, update SRS, reply with feedback.
    """
    settings = get_settings()
    today = date.today().isoformat()

    try:
        data = await request.json()
    except Exception:
        return {"ok": True}  # Ignore malformed payloads silently

    message = data.get("message", {})
    text = message.get("text", "").strip()
    chat_id = str(message.get("chat", {}).get("id", ""))

    # Only process messages from the configured chat list
    allowed_ids = [cid.strip() for cid in settings.telegram_allowed_chat_ids.split(",") if cid.strip()]
    if chat_id not in allowed_ids:
        return {"ok": True}

    if not text or text.startswith("/"):
        return {"ok": True}  # Ignore commands and empty messages

    # Find today's sent word awaiting evaluation
    state = await word_states_col().find_one(
        {"status": "sent"}
    )
    if not state:
        await send_message("⚠️ No active quiz found. Wait for the next morning lesson!")
        return {"ok": True}

    hanzi = state["hanzi"]
    vocab = await vocabulary_col().find_one({"hanzi": hanzi})
    meaning = vocab.get("meaning", "") if vocab else ""

    log_entry = {
        "date": today,
        "hanzi": hanzi,
        "event": "evaluation",
        "status": "failed",
        "model_used": settings.model_eval,
    }

    try:
        # 1. Evaluate with LLM (Gemini Flash Lite)
        eval_json_str = await evaluate_user_sentence(hanzi, text, meaning)
        eval_data = json.loads(eval_json_str)
        evaluation = EvaluationResult(**eval_data)

        # 2. Map score → SM-2 quality
        quality = quality_from_llm_score(evaluation.score)

        # 3. Calculate new SRS interval
        new_srs = calculate_next_review(
            quality_score=quality,
            repetitions=state.get("repetitions", 0),
            ease_factor=state.get("ease_factor", 2.5),
            interval=state.get("interval", 1),
        )

        # 4. Update word_states in MongoDB
        streak = state.get("streak", 0)
        new_streak = (streak + 1) if quality >= 3 else 0

        await word_states_col().update_one(
            {"hanzi": hanzi},
            {
                "$set": {
                    "status": "evaluated",
                    "last_quality": quality,
                    "streak": new_streak,
                    "repetitions": new_srs["repetitions"],
                    "ease_factor": new_srs["ease_factor"],
                    "interval": new_srs["interval"],
                    "next_review": new_srs["next_review"],
                    "total_reviews": state.get("total_reviews", 0) + 1,
                }
            },
        )

        # 5. Send evaluation result to Telegram
        reply = format_eval_result(eval_data, hanzi)
        await send_message(reply)

        log_entry["status"] = "success"
        await daily_log_col().insert_one(log_entry)

        logger.info(
            f"[webhook] Evaluated '{hanzi}' → quality={quality}, next_review={new_srs['next_review']}"
        )
        return {"ok": True}

    except Exception as e:
        log_entry["error"] = str(e)
        await daily_log_col().insert_one(log_entry)
        logger.exception(f"[webhook] Evaluation failed for '{hanzi}': {e}")
        await send_message(f"⚠️ Evaluation failed: {e}\nTry again or check the logs.")
        return {"ok": True}
