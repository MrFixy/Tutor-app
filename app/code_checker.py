"""
Phase 3 / Week 8 - coding exercise checker.

Runs a learner's submitted script against every test case for an exercise
via Judge0 and reports pass/fail per case. One Judge0 submission per test
case (simplest correct approach for a handful of small stdin/stdout cases;
if exercises grow to need dozens of cases, batch via Judge0's
/submissions/batch endpoint instead).
"""
from app.judge0_client import run_submission, Judge0Error, ACCEPTED_STATUS_ID
from app.schemas import CodeExercise, CodeTestCase, CodeTestResult


def _normalize(s: str) -> str:
    """Judge0 already trims trailing newline in stdout, but be defensive
    about surrounding whitespace differences that shouldn't fail a
    beginner's otherwise-correct submission."""
    return s.strip() if s is not None else ""


async def _run_one_case(source_code: str, case: CodeTestCase) -> CodeTestResult:
    try:
        result = await run_submission(
            source_code=source_code,
            stdin=case.stdin,
            expected_output=case.expected_output,
        )
    except Judge0Error as e:
        return CodeTestResult(
            passed=False,
            stdin=case.stdin,
            expected_output=case.expected_output,
            actual_output="",
            status="Judge0 unreachable",
            stderr=str(e),
        )

    status = result.get("status", {})
    status_desc = status.get("description", "Unknown")
    stdout = _normalize(result.get("stdout") or "")
    stderr = result.get("stderr") or result.get("compile_output")

    # Trust Judge0's own comparison (status.id == Accepted) when it ran
    # the comparison for us; fall back to our own normalized diff so
    # trailing-newline differences don't unfairly fail a submission.
    passed = status.get("id") == ACCEPTED_STATUS_ID or stdout == _normalize(case.expected_output)

    return CodeTestResult(
        passed=passed,
        stdin=case.stdin,
        expected_output=case.expected_output,
        actual_output=stdout,
        status=status_desc,
        stderr=stderr,
    )


async def check_submission(source_code: str, exercise: CodeExercise) -> list[CodeTestResult]:
    """Runs source_code against every test case in exercise, sequentially.
    Sequential (not gathered concurrently) on purpose: a shared self-hosted
    Judge0 instance typically has few worker processes, so a burst of
    parallel submissions from one learner just queues behind itself."""
    results = []
    for case in exercise.test_cases:
        results.append(await _run_one_case(source_code, case))
    return results


def summarize(results: list[CodeTestResult]) -> tuple[bool, float, str]:
    total = len(results)
    passed_count = sum(r.passed for r in results)
    all_passed = passed_count == total
    score = passed_count / total if total else 0.0

    if all_passed:
        feedback = f"All {total} test case(s) passed."
    else:
        first_fail = next(r for r in results if not r.passed)
        feedback = (
            f"{passed_count}/{total} test case(s) passed. "
            f"First failure -- input: {first_fail.stdin!r}, "
            f"expected: {first_fail.expected_output!r}, "
            f"got: {first_fail.actual_output!r} ({first_fail.status})."
        )
        if first_fail.stderr:
            feedback += f" stderr: {first_fail.stderr.strip()[:300]}"

    return all_passed, score, feedback
