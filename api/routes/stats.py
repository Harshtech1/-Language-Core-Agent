"""
Stats API — aggregated learning metrics for the Next.js dashboard.
Mounted at /stats (no prefix conflict with /vocab router).
"""

from datetime import date, timedelta
from fastapi import APIRouter

from api.core.db import vocabulary_col, word_states_col, daily_log_col

router = APIRouter(prefix="/stats")


def _yesterday() -> str:
    return (date.today() - timedelta(days=1)).isoformat()


def _days_between(d1: str, d2: str) -> int:
    from datetime import datetime
    dt1 = datetime.fromisoformat(d1)
    dt2 = datetime.fromisoformat(d2)
    return abs((dt2 - dt1).days)


@router.get("/overview")
async def get_stats_overview():
    """
    Aggregated stats for the dashboard hero section.
    Returns streak, mastered count, due today, and per-level breakdown.
    Called by Next.js page.tsx on every render (revalidate: 0).
    """
    today = date.today().isoformat()

    total_words = await vocabulary_col().count_documents({})
    mastered = await word_states_col().count_documents({"repetitions": {"$gt": 5}})
    due_today = await word_states_col().count_documents(
        {"next_review": {"$lte": today}, "status": "new"}
    )
    total_reviewed = await word_states_col().count_documents({"total_reviews": {"$gt": 0}})

    # ── Streak calculation ────────────────────────────────
    # Walk back from today through the evaluation log
    streak = 0
    prev_date = None
    async for log in daily_log_col().find(
        {"event": "evaluation", "status": "success"},
        sort=[("date", -1)],
        limit=30,
    ):
        log_date = log.get("date")
        if prev_date is None:
            if log_date in (today, _yesterday()):
                streak = 1
                prev_date = log_date
            else:
                break
        else:
            if _days_between(log_date, prev_date) == 1:
                streak += 1
                prev_date = log_date
            else:
                break

    # ── Per-level breakdown (N+1 is fine at this scale) ──
    level_stats = []
    for level in range(1, 5):
        count = await vocabulary_col().count_documents({"hsk_level": level})
        learned = 0
        async for w in vocabulary_col().find({"hsk_level": level}, {"hanzi": 1}):
            s = await word_states_col().find_one({"hanzi": w["hanzi"]})
            if s and s.get("repetitions", 0) > 0:
                learned += 1
        level_stats.append({
            "level": level,
            "total": count,
            "learned": learned,
            "pct": round(learned / count * 100, 1) if count > 0 else 0.0,
        })

    return {
        "streak": streak,
        "mastered": mastered,
        "due_today": due_today,
        "total_words": total_words,
        "total_reviewed": total_reviewed,
        "days_remaining": max(0, 730 - total_reviewed),
        "level_breakdown": level_stats,
    }
