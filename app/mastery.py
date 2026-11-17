"""
Phase 4 (Week 9-10) - mastery scoring + difficulty adjustment.

Week 9: roll each `attempts` row's outcome into the (user, domain,
subtopic) `mastery_score` row via an exponential moving average, so
recent performance outweighs old attempts rather than a flat lifetime
average. Every quiz/code submission in practice.py calls
update_mastery() right after the Attempt is written.

Week 10: map mastery_score -> a difficulty level, and feed that back
into the explanation engine (explain.py) via /chat and /explain in
main.py, so a learner who's scoring well on a subtopic gets pushed to
"intermediate"/"advanced" explanations without asking, and one who's
struggling stays at "beginner".
"""
from typing import Literal

from sqlalchemy.orm import Session

from app import models

DifficultyLevel = Literal["beginner", "intermediate", "advanced"]

# EMA smoothing factor: higher weights the most recent attempt more heavily.
ALPHA = 0.3
# Seed score for a (user, domain, subtopic) with no attempts yet -- neutral,
# not zero, so one early wrong answer doesn't read as "knows nothing".
NEUTRAL_SCORE = 0.5

# Don't move off "beginner" until there's enough signal that one lucky or
# unlucky attempt can't swing the difficulty.
MIN_ATTEMPTS_FOR_ADJUSTMENT = 3

ADVANCED_THRESHOLD = 0.75
INTERMEDIATE_THRESHOLD = 0.4


def update_mastery(
    db: Session, user_id: int, domain: str, subtopic: str, outcome: float
) -> models.MasteryScore:
    """
    Rolls one attempt's outcome (0.0-1.0, same scale as Attempt.score) into
    the mastery_score row for (user_id, domain, subtopic):

        new_score = old_score + ALPHA * (outcome - old_score)

    Creates the row (seeded at NEUTRAL_SCORE) on the first attempt. Caller
    is expected to db.commit() -- this only flushes, so it can share a
    transaction with the Attempt insert.
    """
    row = (
        db.query(models.MasteryScore)
        .filter_by(user_id=user_id, domain=domain, subtopic=subtopic)
        .one_or_none()
    )
    if row is None:
        row = models.MasteryScore(
            user_id=user_id,
            domain=domain,
            subtopic=subtopic,
            score=NEUTRAL_SCORE,
            attempts_count=0,
        )
        db.add(row)

    row.score = row.score + ALPHA * (outcome - row.score)
    row.attempts_count += 1
    db.flush()
    return row


def difficulty_for_score(score: float, attempts_count: int) -> DifficultyLevel:
    """Week 10 difficulty-adjustment rule, as a pure function for testing."""
    if attempts_count < MIN_ATTEMPTS_FOR_ADJUSTMENT:
        return "beginner"
    if score >= ADVANCED_THRESHOLD:
        return "advanced"
    if score >= INTERMEDIATE_THRESHOLD:
        return "intermediate"
    return "beginner"


def get_recommended_difficulty(db: Session, user_id: int, domain: str, subtopic: str) -> DifficultyLevel:
    """Current mastery-driven difficulty for (user, domain, subtopic); 'beginner' if no history."""
    row = (
        db.query(models.MasteryScore)
        .filter_by(user_id=user_id, domain=domain, subtopic=subtopic)
        .one_or_none()
    )
    if row is None:
        return "beginner"
    return difficulty_for_score(row.score, row.attempts_count)


def get_all_mastery(db: Session, user_id: int) -> list[models.MasteryScore]:
    """All mastery_score rows for a user -- backs GET /mastery/{user_id} for the Week 11 pilot."""
    return (
        db.query(models.MasteryScore)
        .filter_by(user_id=user_id)
        .order_by(models.MasteryScore.domain, models.MasteryScore.subtopic)
        .all()
    )
