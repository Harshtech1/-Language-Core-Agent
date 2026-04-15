"""
Telegram Bot integration — push messages and receive webhook replies.
"""

import httpx
from api.config import get_settings

TELEGRAM_BASE = "https://api.telegram.org"


def _primary_chat_id(settings) -> str:
    """
    Return the first chat ID from TELEGRAM_ALLOWED_CHAT_IDS.
    This is the owner's ID and the target for all scheduled pushes.
    """
    ids = [cid.strip() for cid in settings.telegram_allowed_chat_ids.split(",") if cid.strip()]
    if not ids:
        raise RuntimeError(
            "TELEGRAM_ALLOWED_CHAT_IDS is not set. Add at least one chat ID to .env."
        )
    return ids[0]


async def send_message(text: str, parse_mode: str = "HTML") -> dict:
    """
    Send a message to the primary (owner) Telegram chat.
    The primary chat is the first ID in TELEGRAM_ALLOWED_CHAT_IDS.

    Args:
        text:       Message content (supports HTML formatting).
        parse_mode: "HTML" or "Markdown".

    Returns:
        Telegram API response dict.
    """
    settings = get_settings()
    url = f"{TELEGRAM_BASE}/bot{settings.telegram_bot_token}/sendMessage"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            url,
            json={
                "chat_id": _primary_chat_id(settings),
                "text": text,
                "parse_mode": parse_mode,
                "disable_web_page_preview": True,
            },
        )
        response.raise_for_status()
        return response.json()


def format_lesson_message(lesson: dict) -> str:
    """
    Format a lesson payload dict into a rich Telegram HTML message.
    """
    sentences = ""
    for s in lesson.get("example_sentences", []):
        sentences += f"  • {s['zh']}\n    {s['pinyin']}\n    <i>{s['en']}</i>\n\n"

    compounds = ""
    for c in lesson.get("common_compounds", []):
        compounds += f"  • {c['zh']} ({c['pinyin']}) — {c['en']}\n"

    return f"""🀄 <b>Daily Word — 语言核心</b>

<b>{lesson['hanzi']}</b>  ·  {lesson['pinyin']}
{lesson.get('tone_description', '')}

📖 <b>Meaning:</b> {lesson['meaning_core']}

🔍 <b>Radical:</b> {lesson.get('radical', 'N/A')}

📜 <b>Etymology:</b>
{lesson.get('etymology', '')}

✍️ <b>Example Sentences:</b>
{sentences}
🧠 <b>Memory Hook:</b>
{lesson.get('memory_hook', '')}

🏛 <b>Cultural Note:</b>
{lesson.get('cultural_note', '')}

📦 <b>Common Compounds:</b>
{compounds}
━━━━━━━━━━━━━━━━━━
🎬 <a href="{lesson.get('stroke_order_url', '#')}"><b>View Stroke Order Animation</b></a>

<i>Reply tonight with a sentence using this word.</i>"""


def format_quiz_prompt(hanzi: str, meaning: str) -> str:
    """Format the evening quiz prompt."""
    return f"""🧪 <b>Evening Quiz — 语言核心</b>

Today's word: <b>{hanzi}</b> ({meaning})

<i>Write a sentence in Chinese using this word.
I'll evaluate your grammar and usage.</i>

━━━━━━━━━━━━━━━━━━
<i>Reply with your sentence below 👇</i>"""


def format_eval_result(evaluation: dict, hanzi: str) -> str:
    """Format the LLM evaluation result for Telegram."""
    score = evaluation.get("score", 0)
    stars = "⭐" * round(score * 5)

    return f"""📊 <b>Evaluation — {hanzi}</b>

Score: {stars} ({score:.0%})
Grammar: {'✅' if evaluation.get('grammar_correct') else '❌'}
Word Usage: {'✅' if evaluation.get('word_used_properly') else '❌'}

{f"✏️ <b>Corrected:</b> {evaluation['corrected_sentence']}" if not evaluation.get('grammar_correct') else ""}

💬 <b>Feedback:</b>
{evaluation.get('feedback', '')}

{f"📝 <b>Grammar Note:</b> {evaluation.get('grammar_notes', '')}" if evaluation.get('grammar_notes') else ""}

━━━━━━━━━━━━━━━━━━
<i>See you tomorrow morning! 加油! 💪</i>"""
