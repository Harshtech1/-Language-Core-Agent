"""
Spaced Repetition Engine — Modified SuperMemo-2 Algorithm.

The next review interval is calculated as:
    I(n) = I(n-1) × EF

Where:
    - I(n) is the inter-repetition interval after n repetitions
    - EF is the Ease Factor (≥ 1.3), adjusted by answer quality
    - Quality scores range 0–5 (mapped from LLM evaluation)
"""

from datetime import date, timedelta


def calculate_next_review(
    quality_score: int,
    repetitions: int,
    ease_factor: float,
    interval: int,
) -> dict:
    """
    Calculate the next review state based on the user's answer quality.

    Args:
        quality_score: 0–5 scale determined by the LLM evaluating
                       the user's evening sentence.
                       5 = perfect, 4 = correct with hesitation,
                       3 = correct with difficulty, 2 = incorrect but close,
                       1 = incorrect, 0 = complete blackout.
        repetitions:   Number of consecutive correct recalls.
        ease_factor:   Current ease factor (starts at 2.5).
        interval:      Current interval in days.

    Returns:
        dict with updated repetitions, ease_factor, interval, and
        the calculated next_review date.
    """
    if quality_score < 0 or quality_score > 5:
        raise ValueError(f"quality_score must be 0-5, got {quality_score}")

    if quality_score >= 3:
        # Correct response — extend the interval
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = round(interval * ease_factor)
        repetitions += 1
        # Adjust ease factor using SM-2 formula
        ease_factor = ease_factor + (
            0.1 - (5 - quality_score) * (0.08 + (5 - quality_score) * 0.02)
        )
    else:
        # Failed — reset to the beginning
        repetitions = 0
        interval = 1

    # EF floor — never let cards become impossible
    ease_factor = max(1.3, ease_factor)

    # Cap interval at 365 days — even "mastered" words get reviewed yearly
    interval = min(interval, 365)

    return {
        "repetitions": repetitions,
        "ease_factor": round(ease_factor, 4),
        "interval": interval,
        "next_review": (date.today() + timedelta(days=interval)).isoformat(),
    }


def quality_from_llm_score(llm_score: float) -> int:
    """
    Map a 0.0–1.0 LLM evaluation score to the SM-2 0–5 quality scale.

    The LLM returns a float score based on grammar accuracy, proper usage,
    and contextual correctness of the user's sentence.
    """
    if llm_score >= 0.95:
        return 5  # Perfect recall and usage
    elif llm_score >= 0.80:
        return 4  # Correct with minor hesitation
    elif llm_score >= 0.60:
        return 3  # Correct with serious difficulty
    elif llm_score >= 0.40:
        return 2  # Incorrect but showed familiarity
    elif llm_score >= 0.20:
        return 1  # Incorrect, vague memory
    else:
        return 0  # Complete blackout
