"""
Phase 4 - unit tests for the pure, DB-free logic in app/mastery.py:
difficulty_for_score()'s thresholds. update_mastery()/get_all_mastery()
need a live Session and are exercised in tests/test_practice_e2e.py instead.
"""
from app.mastery import (
    ADVANCED_THRESHOLD,
    INTERMEDIATE_THRESHOLD,
    MIN_ATTEMPTS_FOR_ADJUSTMENT,
    difficulty_for_score,
)


def test_stays_beginner_below_min_attempts_even_with_high_score():
    assert difficulty_for_score(0.95, MIN_ATTEMPTS_FOR_ADJUSTMENT - 1) == "beginner"


def test_low_score_is_beginner_once_min_attempts_met():
    assert difficulty_for_score(0.1, MIN_ATTEMPTS_FOR_ADJUSTMENT) == "beginner"


def test_mid_score_is_intermediate():
    assert difficulty_for_score(INTERMEDIATE_THRESHOLD, MIN_ATTEMPTS_FOR_ADJUSTMENT) == "intermediate"
    assert difficulty_for_score(0.6, MIN_ATTEMPTS_FOR_ADJUSTMENT) == "intermediate"


def test_high_score_is_advanced():
    assert difficulty_for_score(ADVANCED_THRESHOLD, MIN_ATTEMPTS_FOR_ADJUSTMENT) == "advanced"
    assert difficulty_for_score(1.0, 50) == "advanced"


def test_threshold_is_exclusive_below_intermediate():
    just_under = INTERMEDIATE_THRESHOLD - 0.01
    assert difficulty_for_score(just_under, MIN_ATTEMPTS_FOR_ADJUSTMENT) == "beginner"
