"""
Vocabulary REST API — endpoints for the Next.js dashboard.
"""

import math
from datetime import date
from fastapi import APIRouter, HTTPException, Query

from api.core.db import vocabulary_col, word_states_col, daily_log_col

router = APIRouter(prefix="/vocab")


# ── GET /vocab ──────────────────────────────────────────
@router.get("")
async def list_vocabulary(
    hsk_level: int | None = Query(default=None, ge=1, le=4),
    status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
):
    """
    Paginated vocabulary list with optional HSK level and SRS status filters.
    Each word is joined with its word_state for the dashboard.
    """
    query: dict = {}
    if hsk_level is not None:
        query["hsk_level"] = hsk_level

    skip = (page - 1) * per_page
    total = await vocabulary_col().count_documents(query)

    cursor = vocabulary_col().find(query).sort("hsk_level", 1).skip(skip).limit(per_page)
    words = [doc async for doc in cursor]

    # Batch join with word_states
    hanzi_list = [w["hanzi"] for w in words]
    states_cursor = word_states_col().find({"hanzi": {"$in": hanzi_list}})
    states_map = {s["hanzi"]: s async for s in states_cursor}

    result = []
    for w in words:
        w.pop("_id", None)
        state = states_map.get(w["hanzi"], {})
        state.pop("_id", None)
        reps = state.get("repetitions", 0)
        mastery = (
            "mastered" if reps > 5
            else "reviewing" if reps > 2
            else "learning" if reps > 0
            else "new"
        )
        result.append({**w, "state": state, "mastery_level": mastery})

    return {
        "data": result,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": math.ceil(total / per_page),
        },
    }


# ── GET /vocab/{hanzi} ──────────────────────────────────
@router.get("/{hanzi}")
async def get_word(hanzi: str):
    """Single word detail with full SRS state."""
    vocab = await vocabulary_col().find_one({"hanzi": hanzi})
    if not vocab:
        raise HTTPException(status_code=404, detail=f"Word '{hanzi}' not found.")
    vocab.pop("_id", None)

    state = await word_states_col().find_one({"hanzi": hanzi})
    if state:
        state.pop("_id", None)

    return {**vocab, "state": state}



