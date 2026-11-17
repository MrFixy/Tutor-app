"""
Phase 3 / Week 7 - stats quiz generator.

Given a stats subtopic + difficulty, ask Ollama for N JSON-structured
multiple-choice questions. Same validate-then-one-retry shape as
app/classifier.py: try once, retry once with a stricter reminder, and
fall back to a small canned question set rather than a 500 if the model
still can't produce valid JSON.
"""
from pydantic import ValidationError

from app.ollama_client import generate_json, OllamaError
from app.prompts.quiz_prompts import build_quiz_system_prompt, RETRY_SUFFIX
from app.schemas import QuizQuestion, QuizQuestionSet

FALLBACK_QUESTIONS = [
    QuizQuestion(
        stem="A dataset is 2, 4, 4, 4, 5, 5, 7, 9. What is the mode?",
        choices=["2", "4", "5", "9"],
        correct_index=1,
        explanation="4 appears three times, more than any other value, so it's the mode.",
    ),
    QuizQuestion(
        stem="Which measure of spread is most affected by a single extreme outlier?",
        choices=["Median", "Mode", "Range", "Interquartile range (IQR)"],
        correct_index=2,
        explanation="Range only looks at the max and min, so one extreme value shifts it directly.",
    ),
]


def _validate(raw: dict, expected_count: int) -> list[QuizQuestion]:
    parsed = QuizQuestionSet.model_validate(raw)
    if len(parsed.questions) != expected_count:
        raise ValueError(
            f"expected {expected_count} questions, got {len(parsed.questions)}"
        )
    return parsed.questions


async def generate_stats_quiz(
    subtopic: str, difficulty: str = "beginner", count: int = 3
) -> list[QuizQuestion]:
    system_prompt = build_quiz_system_prompt(subtopic, difficulty, count)
    prompt = f"Generate {count} quiz questions on: {subtopic}"

    # attempt 1
    try:
        raw = await generate_json(prompt, system=system_prompt)
        return _validate(raw, count)
    except (OllamaError, ValidationError, ValueError):
        pass

    # attempt 2: one retry with a stricter reminder
    try:
        raw = await generate_json(
            prompt, system=system_prompt + RETRY_SUFFIX.format(count=count)
        )
        return _validate(raw, count)
    except (OllamaError, ValidationError, ValueError):
        # Fall back to a small canned set rather than failing the request.
        # Not topic-matched, but keeps the practice loop usable if the
        # local model is struggling with structured output.
        return FALLBACK_QUESTIONS[:count] if count <= len(FALLBACK_QUESTIONS) else FALLBACK_QUESTIONS
