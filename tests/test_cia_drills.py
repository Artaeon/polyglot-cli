"""Tests for the CIA intensive drill engine."""

import pytest
from engines.cia_drills import CIADrillEngine
from engines.cluster import ClusterEngine
from engines.quiz import QuizEngine


@pytest.fixture
def cia_engine(populated_db):
    """CIADrillEngine with populated database."""
    cluster = ClusterEngine(populated_db)
    quiz = QuizEngine(populated_db, cluster)
    return CIADrillEngine(populated_db, cluster, quiz)


@pytest.fixture
def learned_cia(populated_db):
    """CIA engine with all words learned."""
    for lang in ["ru", "es", "zh"]:
        for w in populated_db.get_words_by_language(lang):
            populated_db.create_review_card(w["id"])
    cluster = ClusterEngine(populated_db)
    quiz = QuizEngine(populated_db, cluster)
    return CIADrillEngine(populated_db, cluster, quiz)


def test_shadowing_no_learned(cia_engine):
    """Shadowing with no learned words returns empty."""
    items = cia_engine.prepare_shadowing_round("ru", count=5)
    assert len(items) == 0


def test_shadowing_with_learned(learned_cia):
    """Shadowing prepares items with exposure time."""
    items = learned_cia.prepare_shadowing_round("ru", exposure_seconds=2.0, count=5)
    assert len(items) > 0
    assert items[0]["type"] == "shadowing"
    assert items[0]["exposure_seconds"] == 2.0
    assert "word" in items[0]
    assert "meaning_de" in items[0]


def test_rapid_association_with_learned(learned_cia):
    """Rapid association generates timed items."""
    items = learned_cia.prepare_rapid_association(["ru", "es"], time_limit_ms=5000, count=5)
    assert len(items) > 0
    assert items[0]["type"] == "rapid_association"
    assert items[0]["time_limit_ms"] <= 5000


def test_rapid_association_adaptive_timing(learned_cia):
    """Later items in rapid association have tighter time limits."""
    items = learned_cia.prepare_rapid_association(["ru", "es"], time_limit_ms=5000, count=10)
    if len(items) >= 2:
        assert items[-1]["time_limit_ms"] <= items[0]["time_limit_ms"]


def test_immersion_feedback(cia_engine):
    """Immersion feedback returns localized strings."""
    feedback = cia_engine._get_immersion_feedback("ru")
    assert feedback["correct"] == "Правильно!"
    assert feedback["incorrect"] == "Неправильно!"


def test_immersion_feedback_default(cia_engine):
    """Unknown language falls back to German feedback."""
    feedback = cia_engine._get_immersion_feedback("unknown")
    assert feedback["correct"] == "Richtig!"


def test_back_translation_with_learned(learned_cia):
    """Back translation generates items."""
    items = learned_cia.prepare_back_translation("ru", count=5)
    assert len(items) > 0
    assert items[0]["type"] == "back_translation"
    assert "word" in items[0]
    assert "meaning_de" in items[0]


def test_log_drill_session(cia_engine):
    """Drill session is logged to database."""
    cia_engine.log_drill_session(
        drill_type="shadowing",
        duration_seconds=120,
        words_attempted=10,
        words_correct=8,
        avg_response_ms=1500,
        languages_used=["ru"],
        difficulty_level=2,
    )
    row = cia_engine.db.conn.execute(
        "SELECT * FROM drill_sessions WHERE drill_type = 'shadowing'"
    ).fetchone()
    assert row is not None
    assert row["words_attempted"] == 10
    assert row["words_correct"] == 8
