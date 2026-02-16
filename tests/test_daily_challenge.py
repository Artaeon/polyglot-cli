"""Tests for the daily challenge engine."""

import pytest
from engines.daily_challenge import DailyChallengeEngine, CHALLENGE_TYPES
from engines.gamification import GamificationEngine


@pytest.fixture
def challenge_engine(populated_db):
    """DailyChallengeEngine with populated database."""
    gam = GamificationEngine(populated_db)
    gam._init_achievements()
    return DailyChallengeEngine(populated_db, gam)


def test_get_today_challenge(challenge_engine):
    """Today's challenge is created on first access."""
    challenge = challenge_engine.get_today_challenge()
    assert challenge is not None
    assert challenge["challenge_type"] in CHALLENGE_TYPES
    assert challenge["completed"] == 0


def test_challenge_is_deterministic(challenge_engine):
    """Same day returns same challenge."""
    c1 = challenge_engine.get_today_challenge()
    c2 = challenge_engine.get_today_challenge()
    assert c1["challenge_type"] == c2["challenge_type"]


def test_complete_challenge(challenge_engine):
    """Completing a challenge records score and XP."""
    challenge_engine.get_today_challenge()
    result = challenge_engine.complete_challenge(score=7)
    assert result["score"] == 7
    assert result["xp_earned"] > 0


def test_complete_challenge_perfect(challenge_engine):
    """Perfect score gives bonus XP."""
    challenge = challenge_engine.get_today_challenge()
    max_score = challenge["max_score"]
    result = challenge_engine.complete_challenge(score=max_score)
    assert result.get("perfect") is True
    assert result["xp_earned"] > 0


def test_double_complete(challenge_engine):
    """Completing twice returns already_completed."""
    challenge_engine.get_today_challenge()
    challenge_engine.complete_challenge(score=5)
    result = challenge_engine.complete_challenge(score=10)
    assert result.get("already_completed") is True
