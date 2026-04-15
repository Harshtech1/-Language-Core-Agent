"""
OpenRouter API client — routes all LLM calls through openrouter.ai.

Supports the dual-model strategy:
    - Morning lessons: anthropic/claude-3.5-sonnet (premium)
    - Evening evaluations: google/gemini-3.1-flash-lite (budget)
"""

import httpx
import asyncio
import json
from typing import Any

from api.config import get_settings

OPENROUTER_BASE = "https://openrouter.ai/api/v1/chat/completions"
MAX_RETRIES = 3
RETRY_BACKOFF = 2  # seconds, exponential


async def call_llm(
    messages: list[dict[str, str]],
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 2048,
    response_format: dict | None = None,
) -> str:
    """
    Send a chat completion request to OpenRouter.

    Args:
        messages:        Standard OpenAI-format message list.
        model:           OpenRouter model string. Defaults to config's lesson model.
        temperature:     Creativity dial (0=deterministic, 1=creative).
        max_tokens:      Max output tokens.
        response_format: Optional structured output format (e.g., {"type": "json_object"}).

    Returns:
        The assistant's response content as a string.

    Raises:
        httpx.HTTPStatusError on non-200 after all retries.
    """
    settings = get_settings()
    model = model or settings.model_lesson

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/hsk-agent",
        "X-Title": "Language Core Agent",
    }

    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    if response_format:
        payload["response_format"] = response_format

    last_error: Exception | None = None

    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    OPENROUTER_BASE,
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except (httpx.HTTPStatusError, httpx.ConnectError, KeyError) as e:
            last_error = e
            if attempt < MAX_RETRIES - 1:
                wait = RETRY_BACKOFF ** (attempt + 1)
                print(f"[openrouter] Attempt {attempt + 1} failed: {e}. Retrying in {wait}s...")
                await asyncio.sleep(wait)

    raise RuntimeError(
        f"OpenRouter API failed after {MAX_RETRIES} attempts. Last error: {last_error}"
    )


async def generate_lesson_payload(hanzi: str, pinyin: str, meaning: str) -> str:
    """
    Generate a rich daily lesson for a single character/word.
    Uses the premium lesson model (Claude Sonnet).
    """
    prompt = f"""You are a strict Mandarin linguistics professor and cultural historian.
Generate a comprehensive daily lesson payload for the Chinese character/word:

Character: {hanzi}
Pinyin: {pinyin}
Base meaning: {meaning}

Respond in valid JSON with this exact structure:
{{
  "hanzi": "{hanzi}",
  "pinyin": "{pinyin}",
  "tone_description": "description of the tone pattern",
  "radical": "radical breakdown with meaning",
  "meaning_core": "expanded core meaning",
  "etymology": "character origin story and evolution (2-3 sentences)",
  "example_sentences": [
    {{"zh": "...", "pinyin": "...", "en": "..."}},
    {{"zh": "...", "pinyin": "...", "en": "..."}}
  ],
  "cultural_note": "how this word appears in modern Chinese culture or slang (1-2 sentences)",
  "memory_hook": "a vivid visual mnemonic to remember this character (1 sentence)",
  "stroke_order_url": "a direct URL to a stroke order animation GIF for this character (e.g. from hanzi5.com or similar reliable source)",
  "common_compounds": [
    {{"zh": "...", "pinyin": "...", "en": "..."}}
  ]
}}

Rules:
- Example sentences must be appropriate for HSK 1-4 level
- The memory hook must be creative and visual
- Etymology must reference the actual radical components
- Return ONLY the JSON, no markdown fences"""

    settings = get_settings()
    return await call_llm(
        messages=[{"role": "user", "content": prompt}],
        model=settings.model_lesson,
        temperature=0.6,
        response_format={"type": "json_object"},
    )


async def evaluate_user_sentence(
    hanzi: str, user_sentence: str, expected_meaning: str
) -> str:
    """
    Evaluate a user's sentence for grammar and contextual accuracy.
    Uses the budget evaluation model (Gemini Flash Lite).
    """
    prompt = f"""You are a Mandarin grammar evaluator for an HSK learner.

The student was asked to use the word "{hanzi}" (meaning: {expected_meaning}) in a sentence.

Student's sentence: "{user_sentence}"

Evaluate the sentence and respond in valid JSON:
{{
  "score": 0.0-1.0,
  "grammar_correct": true/false,
  "word_used_properly": true/false,
  "corrected_sentence": "corrected version if needed, or the original if correct",
  "feedback": "specific, encouraging feedback in English (2-3 sentences)",
  "grammar_notes": "brief grammar point explanation if relevant"
}}

Scoring guide:
- 1.0: Perfect grammar, excellent contextual usage
- 0.8: Minor tone/measure word issues but correct meaning
- 0.6: Understandable but with clear grammar errors
- 0.4: Attempted but incorrect usage of the target word
- 0.2: Barely related to the target word
- 0.0: No meaningful attempt

Return ONLY the JSON, no markdown fences."""

    settings = get_settings()
    return await call_llm(
        messages=[{"role": "user", "content": prompt}],
        model=settings.model_eval,
        temperature=0.3,
        response_format={"type": "json_object"},
    )
