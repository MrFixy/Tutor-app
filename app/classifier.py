"""
Phase 1 - Core NLP layer: intent classification.

Given a raw learner question, classify it into:
  - domain:   "stats" | "coding"
  - subtopic: one of the closed vocabularies in schemas.py
  - confidence: 0-1

Flow:
  1. Build a structured prompt instructing the model to answer ONLY as JSON.
  2. Call Ollama with format=json.
  3. Validate against IntentClassification + the closed subtopic vocab.
  4. If invalid (bad JSON, unknown subtopic, missing field): retry ONCE with
     a stricter follow-up prompt that shows the model its own bad output.
  5. If it still fails, fall back to a low-confidence default rather than
     crashing the /chat endpoint.
"""
from typing import get_args

from pydantic import ValidationError

from app.ollama_client import generate_json, OllamaError
from app.prompts.goal_prompts import (
    GOAL_CHECK_SYSTEM,
    GOAL_CHECK_RETRY_SUFFIX,
)
from app.schemas import GoalCheckResponse, IntentClassification, StatsSubtopic, CodingSubtopic

STATS_SUBTOPICS = set(get_args(StatsSubtopic))
CODING_SUBTOPICS = set(get_args(CodingSubtopic))

SYSTEM_PROMPT = f"""You are an intent classifier for a stats & coding tutoring app.
Classify the learner's question into exactly one domain and one subtopic.

Valid domains: "stats", "coding"

Valid subtopics when domain="stats": {sorted(STATS_SUBTOPICS)}
Valid subtopics when domain="coding": {sorted(CODING_SUBTOPICS)}

Respond with ONLY a JSON object, no prose, no markdown fences, matching exactly:
{{"domain": "stats" | "coding", "subtopic": "<one of the valid subtopics above>", "confidence": <float 0-1>, "rationale": "<one short sentence>"}}

If the question doesn't clearly fit a specific subtopic, use "other_stats" or "other_coding".
If the question is not about stats or coding at all, still pick the closer domain and use the "other_*" subtopic with a low confidence score.
"""

RETRY_SYSTEM_SUFFIX = """

Your previous response was not valid. It must be a single JSON object with
exactly the keys domain, subtopic, confidence, rationale, and subtopic must
be one of the listed valid values. Try again, JSON only.
"""

FALLBACK = IntentClassification(
    domain="stats",
    subtopic="other_stats",
    confidence=0.0,
    rationale="fallback: classifier could not produce valid output",
)


def _validate(raw: dict) -> IntentClassification:
    parsed = IntentClassification.model_validate(raw)
    valid_set = STATS_SUBTOPICS if parsed.domain == "stats" else CODING_SUBTOPICS
    if parsed.subtopic not in valid_set:
        raise ValueError(f"subtopic {parsed.subtopic!r} not valid for domain {parsed.domain!r}")
    return parsed


async def classify_question(text: str) -> IntentClassification:
    prompt = f"Learner question: {text}"

    # attempt 1
    try:
        raw = await generate_json(prompt, system=SYSTEM_PROMPT)
        return _validate(raw)
    except (OllamaError, ValidationError, ValueError):
        pass

    # attempt 2: one retry with a stricter reminder
    try:
        raw = await generate_json(prompt, system=SYSTEM_PROMPT + RETRY_SYSTEM_SUFFIX)
        return _validate(raw)
    except (OllamaError, ValidationError, ValueError):
        return FALLBACK


# Redesign: lightweight pre-check run before classify_question() when the
# caller is the /chat flow deciding whether to route into the goal/roadmap
# path or the normal explain path. Same format=json + validate + one-retry
# pattern; falls back to "not a goal" (the safer default -- worst case a
# goal statement gets treated as an ordinary question) rather than raising.
GOAL_FALLBACK = GoalCheckResponse(is_goal=False)


async def classify_goal_statement(text: str) -> GoalCheckResponse:
    prompt = f"Learner message: {text}"

    try:
        raw = await generate_json(prompt, system=GOAL_CHECK_SYSTEM)
        return GoalCheckResponse.model_validate(raw)
    except (OllamaError, ValidationError):
        pass

    try:
        raw = await generate_json(prompt, system=GOAL_CHECK_SYSTEM + GOAL_CHECK_RETRY_SUFFIX)
        return GoalCheckResponse.model_validate(raw)
    except (OllamaError, ValidationError):
        return GOAL_FALLBACK
