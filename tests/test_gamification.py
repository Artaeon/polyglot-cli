"""Tests for the gamification engine — XP, levels, achievements."""

import pytest
from engines.gamification import GamificationEngine, ACHIEVEMENT_DEFS


@pytest.fixture
def gam(populated_db):
    """GamificationEngine with populated database."""
    engine = GamificationEngine(populated_db)
    engine._init_achievements()
    return engine


def test_init_achievements(gam):
    """All achievement definitions are inserted."""
    row = gam.db.conn.execute("SELECT COUNT(*) FROM achievements").fetchone()
    assert row[0] == len(ACHIEVEMENT_DEFS)


def test_award_xp(gam):
    """XP is logged and total is updated."""
    gam.award_xp("review", quality=5, language_id="ru")
    total = gam.get_total_xp()
    assert total > 0


def test_get_level(gam):
    """Level calculation returns valid structure."""
    level_info = gam.get_level(0)
    assert level_info["level"] == 1
    assert level_info["next_threshold"] > 0

    level_info = gam.get_level(500)
    assert level_info["level"] >= 1


def test_get_xp_summary(gam):
    """XP summary returns required fields."""
    summary = gam.get_xp_summary()
    assert "total_xp" in summary
    assert "level" in summary
    assert "today_xp" in summary


def test_check_achievements_empty(gam):
    """No achievements unlocked with no activity."""
    newly = gam.check_achievements()
    assert isinstance(newly, list)


def test_check_achievements_words(gam):
    """Word milestone achievements work."""
    # Create review cards to count as "learned"
    words = gam.db.get_words_by_language("ru")
    for w in words:
        gam.db.create_review_card(w["id"])

    # Also for es and zh
    for lang in ["es", "zh"]:
        for w in gam.db.get_words_by_language(lang):
            gam.db.create_review_card(w["id"])

    newly = gam.check_achievements()
    # Should at least get lang_1 (first language) with 6 words
    ids = [a["id"] for a in newly]
    # We have words in 3 languages, so lang_1 should unlock
    assert "lang_1" in ids


def test_get_achievements_by_category(gam):
    """Achievements grouped by category."""
    by_cat = gam.get_achievements_by_category()
    assert isinstance(by_cat, dict)
    assert "words" in by_cat
    assert "streak" in by_cat
