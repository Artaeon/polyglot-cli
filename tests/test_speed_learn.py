"""Tests for the speed learning engine."""

import pytest
from engines.speed_learn import SpeedLearnEngine, DUAL_CODING_SCENES
from engines.cluster import ClusterEngine


@pytest.fixture
def speed_engine(populated_db):
    """SpeedLearnEngine with populated database."""
    cluster = ClusterEngine(populated_db)
    return SpeedLearnEngine(populated_db, cluster)


@pytest.fixture
def learned_db(populated_db):
    """Database with all words having review cards."""
    for lang in ["ru", "es", "zh"]:
        words = populated_db.get_words_by_language(lang)
        for w in words:
            populated_db.create_review_card(w["id"])
    return populated_db


def test_generate_keyword(speed_engine):
    """Keyword generation creates mnemonic string."""
    word = {"word": "вода", "romanization": "voda", "meaning_de": "Wasser"}
    keyword = speed_engine.generate_keyword(word)
    assert "voda" in keyword
    assert "Wasser" in keyword


def test_generate_keyword_short_word(speed_engine):
    """Keyword works for short words."""
    word = {"word": "水", "romanization": "shui", "meaning_de": "Wasser"}
    keyword = speed_engine.generate_keyword(word)
    assert "Wasser" in keyword


def test_save_and_get_keyword(populated_db):
    """User keywords are saved and retrieved."""
    cluster = ClusterEngine(populated_db)
    engine = SpeedLearnEngine(populated_db, cluster)

    words = populated_db.get_words_by_language("ru")
    wid = words[0]["id"]

    engine.save_user_keyword(wid, "Vodka", "Vodka erinnert an Wasser")

    saved = engine.get_keyword(wid)
    assert saved is not None
    assert saved["keyword"] == "Vodka"
    assert saved["story"] == "Vodka erinnert an Wasser"


def test_get_keyword_not_found(speed_engine):
    """Getting non-existent keyword returns None."""
    assert speed_engine.get_keyword(9999) is None


def test_dual_coding_scenes():
    """DUAL_CODING_SCENES has entries."""
    assert len(DUAL_CODING_SCENES) > 0
    assert "water" in DUAL_CODING_SCENES


def test_get_dual_coding_known_concept(speed_engine):
    """Dual coding returns emoji scene for known concept."""
    word = {"concept_id": "water", "word": "вода", "meaning_de": "Wasser"}
    scene = speed_engine.get_dual_coding(word)
    assert "Wasser" in scene


def test_get_dual_coding_fallback(speed_engine):
    """Dual coding returns generic fallback for unknown concept."""
    word = {"concept_id": "unknown_xyz", "word": "тест", "meaning_de": "Test"}
    scene = speed_engine.get_dual_coding(word)
    assert "тест" in scene
    assert "Test" in scene


def test_progressive_hint_level_0():
    """Level 0 hint shows all underscores."""
    hint = SpeedLearnEngine.get_progressive_hint("вода", 0)
    assert hint == "____"


def test_progressive_hint_level_1():
    """Level 1 hint reveals first character."""
    hint = SpeedLearnEngine.get_progressive_hint("вода", 1)
    assert hint == "в___"


def test_progressive_hint_full():
    """Full hint reveals entire word."""
    hint = SpeedLearnEngine.get_progressive_hint("вода", 10)
    assert hint == "вода"


def test_progressive_hint_empty():
    """Empty word returns underscores."""
    hint = SpeedLearnEngine.get_progressive_hint("", 3)
    assert hint == "___"


def test_micro_session_empty(speed_engine):
    """No micro session items without learned words."""
    cards = speed_engine.prepare_micro_session("ru", count=5)
    assert len(cards) == 0


def test_micro_session_with_learned(learned_db):
    """Micro session returns cards for learned words."""
    cluster = ClusterEngine(learned_db)
    engine = SpeedLearnEngine(learned_db, cluster)

    cards = engine.prepare_micro_session("ru", count=5)
    assert len(cards) > 0
    assert "word" in cards[0]


def test_recall_chain_start(speed_engine):
    """Recall chain starts with seed word."""
    seed = {"id": 1, "word": "вода", "concept_id": "water"}
    chain = speed_engine.start_recall_chain(seed)
    assert chain["chain_length"] == 0
    assert chain["history"] == [1]


def test_save_and_get_best_chain(speed_engine):
    """Chain results are saved and best chain retrieved."""
    speed_engine.save_chain_result(5)
    speed_engine.save_chain_result(3)
    best = speed_engine.get_best_chain()
    assert best == 5


def test_error_focused_words_empty(speed_engine):
    """No error words with fresh database."""
    words = speed_engine.get_error_focused_words(limit=10)
    assert len(words) == 0
