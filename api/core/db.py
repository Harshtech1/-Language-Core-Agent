"""
Async MongoDB client using Motor.

Usage:
    from api.core.db import get_db
    db = get_db()
    words = db.vocabulary
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from api.config import get_settings

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


async def connect_db() -> None:
    """Open the Motor connection pool. Called once at app startup."""
    global _client, _db
    settings = get_settings()
    _client = AsyncIOMotorClient(settings.mongodb_uri)
    _db = _client[settings.db_name]

    # Verify connectivity
    await _client.admin.command("ping")
    print(f"[db] Connected to MongoDB — database: {settings.db_name}")


async def close_db() -> None:
    """Drain the connection pool. Called at app shutdown."""
    global _client, _db
    if _client is not None:
        _client.close()
        _client = None
        _db = None
        print("[db] MongoDB connection closed.")


def get_db() -> AsyncIOMotorDatabase:
    """
    Return the active database handle.
    Must be called after connect_db() has completed.
    """
    if _db is None:
        raise RuntimeError(
            "Database not initialized. Ensure connect_db() is called at startup."
        )
    return _db


# ── Collection helpers ──────────────────────────────────
def vocabulary_col():
    """HSK word bank — ~1,200 documents."""
    return get_db()["vocabulary"]


def word_states_col():
    """Per-word SRS tracking (one doc per hanzi)."""
    return get_db()["word_states"]


def daily_log_col():
    """Audit log of daily pushes and evaluations."""
    return get_db()["daily_log"]
