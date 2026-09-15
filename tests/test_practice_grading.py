"""
Phase 3 - unit tests for the pieces of the practice loop that don't need a
live Ollama or Judge0 instance: the pass/fail summarization logic in
code_checker.py, and the JSON-schema validation in quiz.py/code_exercise.py.

For the full loop against real services, see tests/test_practice_e2e.py.
"""
from app.code_checker import summarize
from app.quiz import _validate as validate_quiz
from app.code_exercise import _validate as validate_exercise
from app.schemas import CodeTestResult


def _result(passed, stdin="1\n", expected="x", actual="x", status="Accepted"):
    return CodeTestResult(
        passed=passed, stdin=stdin, expected_output=expected, actual_output=actual, status=status
    )


def test_summarize_all_passed():
    results = [_result(True), _result(True), _result(True)]
    all_passed, score, feedback = summarize(results)
    assert all_passed is True
    assert score == 1.0
    assert "3/3" not in feedback  # uses the "All N passed" phrasing instead
    assert "All 3" in feedback


def test_summarize_partial_failure_reports_first_failure():
    results = [
        _result(True),
        _result(False, stdin="2\n", expected="even", actual="odd", status="Wrong Answer"),
        _result(True),
    ]
    all_passed, score, feedback = summarize(results)
    assert all_passed is False
    assert score == 2 / 3
    assert "2/3" in feedback
    assert "Wrong Answer" in feedback


def test_summarize_empty_results():
    all_passed, score, feedback = summarize([])
    assert all_passed is True  # vacuously true: 0/0 passed
    assert score == 0.0


def test_quiz_validate_accepts_matching_count():
    raw = {
        "questions": [
            {
                "stem": "What is the mean of 2 and 4?",
                "choices": ["2", "3", "4", "6"],
                "correct_index": 1,
                "explanation": "(2+4)/2 = 3",
            }
        ]
    }
    questions = validate_quiz(raw, expected_count=1)
    assert len(questions) == 1
    assert questions[0].correct_index == 1


def test_quiz_validate_rejects_wrong_count():
    raw = {
        "questions": [
            {
                "stem": "Q1",
                "choices": ["a", "b", "c", "d"],
                "correct_index": 0,
                "explanation": "e",
            }
        ]
    }
    try:
        validate_quiz(raw, expected_count=3)
        assert False, "expected ValueError for mismatched question count"
    except ValueError:
        pass


def test_code_exercise_validate_accepts_matching_count():
    raw = {
        "prompt": "Print the square of the input integer.",
        "starter_code": "n = int(input())\n# TODO\n",
        "test_cases": [
            {"stdin": "3\n", "expected_output": "9"},
            {"stdin": "0\n", "expected_output": "0"},
        ],
    }
    exercise = validate_exercise(raw, expected_count=2)
    assert len(exercise.test_cases) == 2
    assert exercise.test_cases[0].expected_output == "9"


def test_code_exercise_validate_rejects_wrong_count():
    raw = {
        "prompt": "p",
        "starter_code": "s",
        "test_cases": [{"stdin": "1\n", "expected_output": "1"}],
    }
    try:
        validate_exercise(raw, expected_count=3)
        assert False, "expected ValueError for mismatched test case count"
    except ValueError:
        pass
