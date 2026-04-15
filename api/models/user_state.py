"""
Pydantic models — Per-word Spaced Repetition state schema.
"""

from pydantic import BaseModel, Field
from typing import Literal
from datetime import date


class WordState(BaseModel):
    """
    SRS tracking state for a single word, stored in 'word_states' collection.
    One document per hanzi. Created with defaults when word is first due.
    """

    hanzi: str = Field(..., description="Chinese character(s) — matches vocabulary.hanzi")
    repetitions: int = Field(default=0, description="Consecutive correct recall count (SM-2)")
    ease_factor: float = Field(default=2.5, description="SM-2 ease factor, minimum 1.3")
    interval: int = Field(default=1, description="Days until next review")
    next_review: date = Field(
        default_factory=date.today,
        description="Next scheduled review date",
    )
    last_quality: int | None = Field(
        default=None,
        ge=0,
        le=5,
        description="Quality score from last evaluation (0–5)",
    )
    status: Literal["new", "sent", "evaluated"] = Field(
        default="new",
        description=(
            "new=not yet sent today, "
            "sent=morning message delivered, "
            "evaluated=evening quiz graded"
        ),
    )
    streak: int = Field(default=0, description="Current daily streak (quality >= 3)")
    total_reviews: int = Field(default=0, description="Lifetime review count")


class WordStateResponse(WordState):
    """Word state decorated with computed fields for the API."""

    mastery_level: Literal["new", "learning", "reviewing", "mastered"] = "new"

    @classmethod
    def from_state(cls, state: WordState) -> "WordStateResponse":
        data = state.model_dump()
        reps = state.repetitions
        if reps == 0:
            mastery = "new"
        elif reps <= 2:
            mastery = "learning"
        elif reps <= 5:
            mastery = "reviewing"
        else:
            mastery = "mastered"
        return cls(**data, mastery_level=mastery)


class EvaluationResult(BaseModel):
    """Structured response from the LLM evening evaluation."""

    score: float = Field(..., ge=0.0, le=1.0)
    grammar_correct: bool
    word_used_properly: bool
    corrected_sentence: str
    feedback: str
    grammar_notes: str = ""


class DailyLogEntry(BaseModel):
    """Audit log entry for each cron event, stored in 'daily_log' collection."""

    date: str = Field(..., description="ISO date string YYYY-MM-DD")
    hanzi: str
    event: Literal["daily_push", "evening_quiz", "evaluation"]
    status: Literal["success", "failed"]
    model_used: str = ""
    error: str | None = None
