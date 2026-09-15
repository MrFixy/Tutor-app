"""
Phase 3 / Week 7 - quiz generation prompt.

Reuses the same per-subtopic teaching framing from stats_prompts.py so the
quiz questions stay consistent with what the explanation engine already
taught, then layers on strict JSON-output instructions (same format=json +
validate + one-retry pattern as classifier.py).
"""
from app.prompts.stats_prompts import STATS_TOPIC_SYSTEM

QUIZ_JSON_INSTRUCTIONS = """You are writing multiple-choice quiz questions for a stats tutoring app.

Respond with ONLY a JSON object, no prose, no markdown fences, matching exactly:
{{"questions": [
  {{"stem": "<question text>", "choices": ["<a>", "<b>", "<c>", "<d>"], "correct_index": <0-3>, "explanation": "<one short sentence on why the correct answer is correct>"}}
  ... ({count} items total)
]}}

Rules:
- Exactly {count} questions, each with exactly 4 choices.
- Only one choice is correct per question; the other three should be plausible but wrong.
- Vary which index (0-3) holds the correct answer across questions -- don't always put it in the same slot.
- Match the difficulty level given below.
- Keep each stem self-contained (no "as discussed above" references).
"""

RETRY_SUFFIX = """

Your previous response was not valid JSON matching the required schema
(top-level object with a "questions" array of exactly {count} items, each
with stem/choices[4]/correct_index/explanation). Try again, JSON only.
"""


def build_quiz_system_prompt(subtopic: str, difficulty: str, count: int) -> str:
    topic_instructions = STATS_TOPIC_SYSTEM.get(subtopic, STATS_TOPIC_SYSTEM["other_stats"])
    difficulty_line = f"Difficulty level: {difficulty}."
    return "\n\n".join([
        topic_instructions.strip(),
        difficulty_line,
        QUIZ_JSON_INSTRUCTIONS.format(count=count),
    ])
