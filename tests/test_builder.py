"""Tests for the sentence builder engine."""

import pytest
from engines.builder import SentenceBuilderEngine, SOV_LANGUAGES, FLEXIBLE_ORDER_FAMILIES
from engines.sentence import SentenceEngine


@pytest.fixture
def builder_engine(populated_db):
    """SentenceBuilderEngine with populated database."""
    sentence = SentenceEngine(populated_db)
    return SentenceBuilderEngine(populated_db, sentence)


def test_patterns_loaded(builder_engine):
    """Patterns are loaded from JSON or defaults."""
    patterns = builder_engine.patterns
    assert isinstance(patterns, list)
    assert len(patterns) > 0
    assert "id" in patterns[0]
    assert "structure" in patterns[0]


def test_can_start_insufficient_words(builder_engine):
    """Can't start with too few words."""
    can, msg = builder_engine.can_start("zh")
    # zh has only 1 word, insufficient
    assert can is False
    assert "Woerter" in msg or "Kategorien" in msg


def test_can_start_with_learned_words(populated_db):
    """Can start when enough words are learned (have review cards)."""
    from models import Word
    sentence = SentenceEngine(populated_db)
    engine = SentenceBuilderEngine(populated_db, sentence)

    # Add extra words so we have >= 5 total in >= 2 categories
    extras = [
        Word(id=0, language_id="ru", word="большой", romanization="bolshoy",
             meaning_de="gross", meaning_en="big", category="adjektive",
             frequency_rank=10, concept_id="big"),
        Word(id=0, language_id="ru", word="дом", romanization="dom",
             meaning_de="Haus", meaning_en="house", category="nomen",
             frequency_rank=11, concept_id="house"),
    ]
    for w in extras:
        populated_db.insert_word(w)

    # Create review cards for all ru words (making them "learned")
    words = populated_db.get_words_by_language("ru")
    for w in words:
        populated_db.create_review_card(w["id"])

    can, msg = engine.can_start("ru")
    # 5 words in 2 categories (nomen + adjektive) - meets threshold
    assert can is True


def test_get_available_patterns(populated_db):
    """Available patterns depend on learned vocabulary."""
    sentence = SentenceEngine(populated_db)
    engine = SentenceBuilderEngine(populated_db, sentence)

    # Without learned words, no patterns available
    patterns = engine.get_available_patterns("ru")
    assert len(patterns) == 0

    # Learn words
    for w in populated_db.get_words_by_language("ru"):
        populated_db.create_review_card(w["id"])

    patterns = engine.get_available_patterns("ru")
    # With nomen + adjektive categories, some patterns should be available
    assert isinstance(patterns, list)


def test_sov_languages():
    """SOV language set is defined correctly."""
    assert "ja" in SOV_LANGUAGES
    assert "ko" in SOV_LANGUAGES
    assert "ru" not in SOV_LANGUAGES


def test_flexible_order_families():
    """Flexible order families include slavic."""
    assert "slavic" in FLEXIBLE_ORDER_FAMILIES
