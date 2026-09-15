"""
Phase 3 / Week 8 - coding exercise generator.

Mirrors app/quiz.py's shape: validate-then-one-retry JSON generation, with
a canned fallback exercise so the practice loop stays usable if the local
model can't produce valid structured output.
"""
from pydantic import ValidationError

from app.ollama_client import generate_json, OllamaError
from app.prompts.code_exercise_prompts import build_code_exercise_system_prompt, RETRY_SUFFIX
from app.schemas import CodeExercise

DEFAULT_TEST_CASE_COUNT = 3

FALLBACK_EXERCISE = CodeExercise(
    prompt=(
        "Read an integer n from stdin and print whether it's even or odd, "
        "as exactly 'even' or 'odd'."
    ),
    starter_code=(
        "n = int(input())\n"
        "# TODO: print 'even' if n is even, 'odd' otherwise\n"
    ),
    test_cases=[
        {"stdin": "4\n", "expected_output": "even"},
        {"stdin": "7\n", "expected_output": "odd"},
        {"stdin": "0\n", "expected_output": "even"},
    ],
)


def _validate(raw: dict, expected_count: int) -> CodeExercise:
    parsed = CodeExercise.model_validate(raw)
    if len(parsed.test_cases) != expected_count:
        raise ValueError(
            f"expected {expected_count} test cases, got {len(parsed.test_cases)}"
        )
    return parsed


async def generate_coding_exercise(
    subtopic: str, difficulty: str = "beginner", count: int = DEFAULT_TEST_CASE_COUNT
) -> CodeExercise:
    system_prompt = build_code_exercise_system_prompt(subtopic, difficulty, count)
    prompt = f"Generate a coding exercise on: {subtopic}"

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
        return FALLBACK_EXERCISE
