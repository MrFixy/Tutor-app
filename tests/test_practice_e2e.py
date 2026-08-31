"""
Phase 3 - end-to-end smoke test: generate a quiz question, answer it,
generate a coding exercise, submit a solution, and check the recorded
attempt. Requires Ollama, Judge0 (docker-compose.judge0.yml), and the
tutor Postgres all running -- skipped automatically if any of them
aren't reachable, so this doesn't break `pytest` in a plain checkout.

Run explicitly once your local services are up:
    pytest tests/test_practice_e2e.py -v
"""
import pytest

from app.db import SessionLocal, Base, engine
from app import models  # noqa: F401
from app.ollama_client import ping as ollama_ping
from app.judge0_client import ping as judge0_ping
from app import practice


async def _services_up() -> bool:
    return await ollama_ping() and await judge0_ping()


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.mark.asyncio
async def test_quiz_round_trip(db):
    if not await _services_up():
        pytest.skip("Ollama and/or Judge0 not reachable -- skipping live smoke test")

    questions = await practice.start_quiz(
        db, user_id=1, session_id=None, subtopic="descriptive_stats", difficulty="beginner", count=1
    )
    assert len(questions) == 1
    q = questions[0]
    assert len(q.choices) == 4

    # Answer with index 0; regardless of correctness, submit should succeed
    # and correctly report whether it matched the stored answer.
    result = await practice.submit_quiz_answer(db, user_id=1, question_id=q.question_id, chosen_index=0)
    assert result.question_id == q.question_id
    assert result.correct == (result.correct_index == 0)


@pytest.mark.asyncio
async def test_coding_exercise_round_trip(db):
    if not await _services_up():
        pytest.skip("Ollama and/or Judge0 not reachable -- skipping live smoke test")

    exercise = await practice.start_code_exercise(
        db, user_id=1, session_id=None, subtopic="syntax_basics", difficulty="beginner"
    )
    assert exercise.question_id

    # Submit deliberately broken code -- we're checking the grading pipeline
    # wires together end-to-end, not that the model always writes solvable
    # exercises.
    result = await practice.submit_code_answer(
        db, user_id=1, question_id=exercise.question_id, source_code="raise RuntimeError('nope')"
    )
    assert result.passed is False
    assert 0.0 <= result.score <= 1.0
    assert len(result.results) >= 1
