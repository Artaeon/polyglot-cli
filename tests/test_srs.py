"""Tests for the SM-2 spaced repetition algorithm."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engines.srs import sm2, next_review_date


def test_sm2_correct_first_time():
    """First correct answer should set interval to 1."""
    reps, ease, interval = sm2(quality=4, repetitions=0,
                                ease_factor=2.5, interval=0)
    assert reps == 1
    assert interval == 1
    assert ease >= 1.3


def test_sm2_correct_second_time():
    """Second correct answer should set interval to 6."""
    reps, ease, interval = sm2(quality=4, repetitions=1,
                                ease_factor=2.5, interval=1)
    assert reps == 2
    assert interval == 6


def test_sm2_correct_third_time():
    """Third correct answer should multiply interval by ease."""
    reps, ease, interval = sm2(quality=4, repetitions=2,
                                ease_factor=2.5, interval=6)
    assert reps == 3
    assert interval == 15  # round(6 * 2.5)


def test_sm2_incorrect_resets():
    """Incorrect answer should reset repetitions and interval."""
    reps, ease, interval = sm2(quality=1, repetitions=5,
                                ease_factor=2.5, interval=30)
    assert reps == 0
    assert interval == 1


def test_sm2_ease_never_below_minimum():
    """Ease factor should never go below 1.3."""
    _, ease, _ = sm2(quality=0, repetitions=0,
                     ease_factor=1.3, interval=0)
    assert ease >= 1.3


def test_sm2_perfect_increases_ease():
    """Perfect recall (quality=5) should increase ease factor."""
    _, ease, _ = sm2(quality=5, repetitions=0,
                     ease_factor=2.5, interval=0)
    assert ease > 2.5


def test_sm2_difficult_decreases_ease():
    """Difficult recall (quality=3) should decrease ease factor."""
    _, ease, _ = sm2(quality=3, repetitions=0,
                     ease_factor=2.5, interval=0)
    assert ease < 2.5


def test_sm2_quality_boundary():
    """Quality of exactly 3 should count as correct."""
    reps, _, interval = sm2(quality=3, repetitions=0,
                             ease_factor=2.5, interval=0)
    assert reps == 1
    assert interval == 1


def test_sm2_quality_2_is_incorrect():
    """Quality of 2 should count as incorrect."""
    reps, _, interval = sm2(quality=2, repetitions=3,
                             ease_factor=2.5, interval=15)
    assert reps == 0
    assert interval == 1


def test_next_review_date_format():
    """Next review date should be ISO format."""
    result = next_review_date(1)
    assert len(result) == 10  # YYYY-MM-DD
    assert result[4] == "-"


def test_sm2_long_sequence():
    """Test a realistic sequence of reviews."""
    reps, ease, interval = 0, 2.5, 0

    # Perfect recalls
    for _ in range(5):
        reps, ease, interval = sm2(5, reps, ease, interval)

    assert reps == 5
    assert interval > 30  # Should have grown significantly
    assert ease > 2.5

    # One failure
    reps, ease, interval = sm2(1, reps, ease, interval)
    assert reps == 0
    assert interval == 1


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
