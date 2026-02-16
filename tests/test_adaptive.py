"""Tests for the adaptive difficulty engine."""

import pytest
from engines.adaptive import AdaptiveDifficultyEngine


@pytest.fixture
def adaptive_engine(populated_db):
    """AdaptiveDifficultyEngine with populated database."""
    return AdaptiveDifficultyEngine(populated_db)


def test_get_difficulty_default(adaptive_engine):
    """Default difficulty is 1.0."""
    d = adaptive_engine.get_difficulty("ru", "quiz")
    assert d == 1.0


def test_record_attempt_correct(adaptive_engine):
    """Correct answers increase consecutive_correct."""
    adaptive_engine.record_attempt("ru", "quiz", correct=True)
    profiles = adaptive_engine.get_all_profiles("ru")
    quiz_profile = [p for p in profiles if p["engine_type"] == "quiz"]
    assert len(quiz_profile) == 1
    assert quiz_profile[0]["consecutive_correct"] == 1
    assert quiz_profile[0]["consecutive_wrong"] == 0


def test_record_attempt_wrong(adaptive_engine):
    """Wrong answers increase consecutive_wrong."""
    adaptive_engine.record_attempt("ru", "quiz", correct=False)
    profiles = adaptive_engine.get_all_profiles("ru")
    quiz_profile = [p for p in profiles if p["engine_type"] == "quiz"]
    assert len(quiz_profile) == 1
    assert quiz_profile[0]["consecutive_wrong"] == 1
    assert quiz_profile[0]["consecutive_correct"] == 0


def test_difficulty_increases(adaptive_engine):
    """Difficulty increases after consecutive correct answers."""
    for _ in range(6):
        adaptive_engine.record_attempt("ru", "quiz", correct=True)
    d = adaptive_engine.get_difficulty("ru", "quiz")
    assert d > 1.0


def test_difficulty_decreases(adaptive_engine):
    """Difficulty decreases after consecutive wrong answers."""
    # First set a higher difficulty
    for _ in range(6):
        adaptive_engine.record_attempt("ru", "quiz", correct=True)
    high = adaptive_engine.get_difficulty("ru", "quiz")

    # Now fail repeatedly
    for _ in range(4):
        adaptive_engine.record_attempt("ru", "quiz", correct=False)
    low = adaptive_engine.get_difficulty("ru", "quiz")
    assert low < high
