"""
HSK Agent API — Configuration via environment variables.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    All config is loaded from environment variables (or .env file).
    See .env.example for the full list.
    """

    # ── MongoDB ────────────────────────────────────────
    mongodb_uri: str = "mongodb://localhost:27017"
    db_name: str = "hsk_agent"

    # ── OpenRouter ─────────────────────────────────────
    openrouter_api_key: str = ""
    model_lesson: str = "anthropic/claude-3.5-sonnet"
    model_eval: str = "google/gemini-3.1-flash-lite"

    # ── Telegram ───────────────────────────────────────
    telegram_bot_token: str = ""
    telegram_allowed_chat_ids: str = "" # Comma-separated list for multi-user/testing

    # ── Cron Security ──────────────────────────────────
    cron_secret: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
