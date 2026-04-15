"""
Telegram Bot — Full implementation.

Handles:
  - /start  → welcome message + CHAT_ID verification
  - Incoming text messages → forward to main FastAPI webhook for SRS evaluation
  - Webhook registration helper

Run standalone for local testing:
    python -m workers.telegram_bot
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

import httpx
import uvicorn
from fastapi import FastAPI, Request, Response

# Allow running as `python -m workers.telegram_bot` from repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("telegram_bot")

TELEGRAM_BASE = "https://api.telegram.org"
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CONFIGURED_CHAT_IDS = [cid.strip() for cid in os.getenv("TELEGRAM_ALLOWED_CHAT_IDS", "").split(",") if cid.strip()]
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

app = FastAPI(title="HSK Agent — Telegram Webhook Proxy", version="0.1.0")


# ── Helpers ──────────────────────────────────────────────

async def send_telegram(chat_id: str, text: str, parse_mode: str = "HTML") -> dict:
    """Send a raw Telegram message to any chat_id."""
    url = f"{TELEGRAM_BASE}/bot{BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            url,
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode,
                "disable_web_page_preview": True,
            },
        )
        return resp.json()


async def handle_start_command(chat_id: str, user_name: str) -> None:
    """Handle the /start command — send welcome + verify chat ID."""
    is_authorised = chat_id in CONFIGURED_CHAT_IDS

    if is_authorised:
        welcome = f"""🀄 <b>语言核心 — Language Core</b>

你好, {user_name}! 欢迎！

✅ <b>Bot connected successfully.</b>
Your CHAT_ID is verified. The agent is active.

<b>How this works:</b>
  ☀️ <b>08:00</b> — Morning lesson with etymology &amp; cultural nuance
  🌙 <b>20:00</b> — Evening quiz: write a sentence using today's word
  📊 I evaluate your grammar and schedule your next review

<i>Your 730-day journey to HSK 4 mastery begins now.</i>

加油! 💪"""
    else:
        welcome = f"""⚠️ <b>Unauthorized Chat</b>

Your Chat ID: <code>{chat_id}</code>

This bot is configured for a specific user.
If you believe this is an error, update <code>TELEGRAM_CHAT_ID</code> in your <code>.env</code> file.

<i>Expected: {CONFIGURED_CHAT_ID[:4]}****</i>"""

    await send_telegram(chat_id, welcome)
    logger.info(f"[/start] chat_id={chat_id} authorised={is_authorised}")


async def forward_to_api(payload: dict) -> None:
    """
    Forward the Telegram update to the main FastAPI /webhook/telegram endpoint.
    The main API handles evaluation logic, SRS updates, and reply formatting.
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            await client.post(
                f"{API_BASE_URL}/webhook/telegram",
                json=payload,
            )
        except httpx.ConnectError:
            logger.error(f"[forward] Cannot reach API at {API_BASE_URL}. Is the FastAPI server running?")


# ── Webhook Receiver ─────────────────────────────────────

@app.post("/telegram/update")
async def receive_update(request: Request):
    """
    Entry point for all Telegram updates.

    Set your webhook URL to: https://<render-url>/telegram/update

    Handles:
      - /start command inline (fast response, no API call needed)
      - All other text messages → forwarded to main API for SRS evaluation
      - Ignores non-message updates (inline queries, etc.)
    """
    try:
        payload = await request.json()
    except Exception:
        return Response(content='{"ok": true}', media_type="application/json")

    message = payload.get("message", {})
    if not message:
        # Could be edited_message, callback_query, etc. — ignore for now
        return Response(content='{"ok": true}', media_type="application/json")

    text = message.get("text", "").strip()
    chat = message.get("chat", {})
    chat_id = str(chat.get("id", ""))
    user = message.get("from", {})
    user_name = user.get("first_name", "Learner")

    if not text or not chat_id:
        return Response(content='{"ok": true}', media_type="application/json")

    logger.info(f"[update] chat_id={chat_id} text={text[:60]!r}")

    # Handle /start inline — no API call required
    if text == "/start":
        await handle_start_command(chat_id, user_name)
        return Response(content='{"ok": true}', media_type="application/json")

    # Block unauthorized chats before forwarding
    if chat_id not in CONFIGURED_CHAT_IDS:
        await send_telegram(
            chat_id,
            f"⚠️ Unauthorized. Your Chat ID: <code>{chat_id}</code>. Contact the owner to be added to the allowlist.",
        )
        return Response(content='{"ok": true}', media_type="application/json")

    # Forward all other messages to the main API for evaluation
    await forward_to_api(payload)

    return Response(content='{"ok": true}', media_type="application/json")


@app.get("/health")
async def health():
    return {"status": "ok", "bot_configured": bool(BOT_TOKEN), "api_base": API_BASE_URL}


# ── Webhook Registration ──────────────────────────────────

async def register_webhook(webhook_url: str) -> None:
    """Register this server's URL with the Telegram BotFather API."""
    url = f"{TELEGRAM_BASE}/bot{BOT_TOKEN}/setWebhook"
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json={"url": webhook_url})
        data = resp.json()
        if data.get("ok"):
            logger.info(f"[webhook] ✅ Registered: {webhook_url}")
        else:
            logger.error(f"[webhook] ❌ Registration failed: {data}")


async def delete_webhook() -> None:
    """Delete the currently set webhook (useful for local polling mode)."""
    url = f"{TELEGRAM_BASE}/bot{BOT_TOKEN}/deleteWebhook"
    async with httpx.AsyncClient() as client:
        resp = await client.post(url)
        data = resp.json()
        logger.info(f"[webhook] deleteWebhook → {data}")


async def get_webhook_info() -> dict:
    """Get current webhook status from Telegram."""
    url = f"{TELEGRAM_BASE}/bot{BOT_TOKEN}/getWebhookInfo"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        return resp.json()


# ── CLI Entry Point ───────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="HSK Agent Telegram Webhook Server")
    parser.add_argument("--webhook-url", type=str, default=os.getenv("WEBHOOK_URL", ""), help="Public URL to register with Telegram")
    parser.add_argument("--port", type=int, default=8001, help="Port to run the webhook server on")
    parser.add_argument("--info", action="store_true", help="Print current webhook info and exit")
    parser.add_argument("--delete-webhook", action="store_true", help="Delete current webhook and exit")
    args = parser.parse_args()

    if args.info:
        info = asyncio.run(get_webhook_info())
        print(json.dumps(info, indent=2, ensure_ascii=False))
        sys.exit(0)

    if args.delete_webhook:
        asyncio.run(delete_webhook())
        sys.exit(0)

    if args.webhook_url:
        asyncio.run(register_webhook(args.webhook_url))

    logger.info(f"Starting Telegram webhook server on 0.0.0.0:{args.port}")
    uvicorn.run(app, host="0.0.0.0", port=args.port)
