"""
Phase 3 - practice loop.

Connects Phase 2's explanation output to a practice attempt:
  1. generate a quiz (stats) or coding exercise (coding) for a subtopic
  2. persist it as a `questions` row -- reusing the same table Phase 2
     writes explanations to, so classified_json now doubles as storage
     for the generated quiz/exercise payload (choices+answer, or
     prompt+test cases). This keeps every "thing put in front of the
     learner" in one table instead of adding new ones.
  3. grade the learner's submission (quiz choice, or code via Judge0) and
     write an `attempts` row.

Phase 4 (Week 9): after each attempt is graded, its outcome is also
rolled into the (user, domain, subtopic) `mastery_score` row via
mastery.update_mastery() -- see app/mastery.py for the EMA and the
Week 10 difficulty-adjustment rules that read it back.
"""
from typing import Optional

from sqlalchemy.orm import Session

from app import models
from app import mastery
from app import user_service
from app.code_checker import check_submission, summarize
from app.code_exercise import generate_coding_exercise
from app.quiz import generate_stats_quiz
from app.schemas import (
    CodeExercise,
    CodeExerciseOut,
    CodeSubmitResponse,
    QuizQuestionOut,
    QuizSubmitResponse,
)


# ---------- stats quiz ----------

async def start_quiz(
    db: Session, user_id: int, session_id: Optional[int], subtopic: str, difficulty: str, count: int
) -> list[QuizQuestionOut]:
    # Phase 6 (Week 14) bug fix: see user_service.py -- must run before any
    # write below that references user_id/session_id.
    user_service.get_or_create_user(db, user_id)
    session_id = user_service.get_or_create_session(db, session_id, user_id)

    questions = await generate_stats_quiz(subtopic, difficulty, count)

    out = []
    for q in questions:
        row = models.Question(
            session_id=session_id,
            user_id=user_id,
            raw_text=q.stem,
            intent_domain="stats",
            intent_subtopic=subtopic,
            intent_confidence=1.0,  # topic is chosen directly, not classified
            classified_json={
                "kind": "quiz",
                "choices": q.choices,
                "correct_index": q.correct_index,
                "explanation": q.explanation,
            },
        )
        db.add(row)
        db.flush()  # populate row.id without a full commit yet
        out.append(QuizQuestionOut(question_id=row.id, stem=q.stem, choices=q.choices))

    db.commit()
    return out


async def submit_quiz_answer(
    db: Session, user_id: int, question_id: int, chosen_index: int
) -> QuizSubmitResponse:
    user_service.get_or_create_user(db, user_id)  # defensive: see user_service.py

    row = db.get(models.Question, question_id)
    if row is None or not row.classified_json or row.classified_json.get("kind") != "quiz":
        raise ValueError(f"no quiz question found with id={question_id}")

    correct_index = row.classified_json["correct_index"]
    explanation = row.classified_json["explanation"]
    correct = chosen_index == correct_index
    feedback = "Correct!" if correct else f"Not quite -- the correct answer was choice {correct_index + 1}."

    attempt = models.Attempt(
        user_id=user_id,
        question_id=question_id,
        attempt_type="quiz",
        submission=str(chosen_index),
        is_correct=correct,
        score=1.0 if correct else 0.0,
        feedback=f"{feedback} {explanation}",
    )
    db.add(attempt)
    mastery.update_mastery(db, user_id, row.intent_domain, row.intent_subtopic, attempt.score)
    db.commit()

    return QuizSubmitResponse(
        question_id=question_id,
        correct=correct,
        correct_index=correct_index,
        explanation=explanation,
        feedback=attempt.feedback,
    )


# ---------- coding exercise ----------

async def start_code_exercise(
    db: Session, user_id: int, session_id: Optional[int], subtopic: str, difficulty: str
) -> CodeExerciseOut:
    # Phase 6 (Week 14) bug fix: see user_service.py.
    user_service.get_or_create_user(db, user_id)
    session_id = user_service.get_or_create_session(db, session_id, user_id)

    exercise = await generate_coding_exercise(subtopic, difficulty)

    row = models.Question(
        session_id=session_id,
        user_id=user_id,
        raw_text=exercise.prompt,
        intent_domain="coding",
        intent_subtopic=subtopic,
        intent_confidence=1.0,
        classified_json={
            "kind": "code_exercise",
            "starter_code": exercise.starter_code,
            "test_cases": [tc.model_dump() for tc in exercise.test_cases],
        },
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    return CodeExerciseOut(question_id=row.id, prompt=exercise.prompt, starter_code=exercise.starter_code)


async def submit_code_answer(
    db: Session, user_id: int, question_id: int, source_code: str
) -> CodeSubmitResponse:
    user_service.get_or_create_user(db, user_id)  # defensive: see user_service.py

    row = db.get(models.Question, question_id)
    if row is None or not row.classified_json or row.classified_json.get("kind") != "code_exercise":
        raise ValueError(f"no coding exercise found with id={question_id}")

    exercise = CodeExercise(
        prompt=row.raw_text,
        starter_code=row.classified_json["starter_code"],
        test_cases=row.classified_json["test_cases"],
    )

    results = await check_submission(source_code, exercise)
    all_passed, score, feedback = summarize(results)

    attempt = models.Attempt(
        user_id=user_id,
        question_id=question_id,
        attempt_type="code",
        submission=source_code,
        is_correct=all_passed,
        score=score,
        feedback=feedback,
    )
    db.add(attempt)
    mastery.update_mastery(db, user_id, row.intent_domain, row.intent_subtopic, attempt.score)
    db.commit()

    return CodeSubmitResponse(
        question_id=question_id,
        passed=all_passed,
        score=score,
        results=results,
        feedback=feedback,
    )
