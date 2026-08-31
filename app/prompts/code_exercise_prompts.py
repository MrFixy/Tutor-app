"""
Phase 3 / Week 8 - coding exercise generation prompt.

Exercises are graded via Judge0, which runs a program against stdin and
compares raw stdout, so we ask the model for a *complete, runnable*
Python script (reads input() if needed, prints the answer) plus a small
set of stdin/expected-stdout test cases -- not just a bare function --
to keep grading a simple stdin/stdout diff rather than a custom harness.
"""
from app.prompts.coding_prompts import CODING_TOPIC_SYSTEM

CODE_EXERCISE_JSON_INSTRUCTIONS = """You are writing a short coding exercise for a Python coding-tutor app.
The exercise will be graded by running the learner's submitted Python script
and comparing its printed stdout, line for line, against an expected output
-- so it must be a complete, runnable script (use input() to read stdin if
the exercise needs input; use print() for the answer), not a bare function.

Respond with ONLY a JSON object, no prose, no markdown fences, matching exactly:
{{"prompt": "<exercise description, plain text>",
  "starter_code": "<a short starter script with a TODO the learner fills in, valid Python>",
  "test_cases": [
    {{"stdin": "<input to feed the program, may be empty string>", "expected_output": "<exact expected stdout, trailing newline not required>"}}
    ... ({count} items total)
  ]}}

Rules:
- Exactly {count} test cases, covering at least one edge case (empty input, zero, negative number, etc. as relevant to the topic).
- expected_output must be EXACTLY what a correct solution would print (no extra commentary).
- Keep the exercise solvable in a few lines of standard-library-only Python.
- Match the difficulty level given below.
"""

RETRY_SUFFIX = """

Your previous response was not valid JSON matching the required schema
(top-level object with prompt/starter_code/test_cases, test_cases an array
of exactly {count} {{stdin, expected_output}} items). Try again, JSON only.
"""


def build_code_exercise_system_prompt(subtopic: str, difficulty: str, count: int) -> str:
    topic_instructions = CODING_TOPIC_SYSTEM.get(subtopic, CODING_TOPIC_SYSTEM["other_coding"])
    difficulty_line = f"Difficulty level: {difficulty}."
    return "\n\n".join([
        topic_instructions.strip(),
        difficulty_line,
        CODE_EXERCISE_JSON_INSTRUCTIONS.format(count=count),
    ])
