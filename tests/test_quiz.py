"""Tests for the quiz engine — distractors, card prep, review processing."""

import pytest
from engines.quiz import QuizEngine
from engines.cluster import ClusterEngine


@pytest.fixture
def quiz_engine(populated_db):
    """QuizEngine with populated database."""
    cluster = ClusterEngine(populated_db)
    return QuizEngine(populated_db, cluster)


def _make_card(word_dict):
    """Create a minimal review card dict from a word dict."""
    card = dict(word_dict)
    card["word_id"] = card["id"]
    card["flag"] = ""
    card["lang_name"] = ""
    card["family"] = ""
    return card


def test_get_distractors(quiz_engine):
    """Distractors are returned for a word."""
    words = quiz_engine.db.get_words_by_language("ru")
    card = _make_card(words[0])
    distractors = quiz_engine.get_distractors(card, count=2)
    assert isinstance(distractors, list)
    # Distractors should not match correct answer
    for d in distractors:
        assert d["meaning_de"] != card["meaning_de"]


def test_prepare_recognition_card(quiz_engine):
    """Recognition card has options with one correct."""
    words = quiz_engine.db.get_words_by_language("ru")
    card = _make_card(words[0])
    result = quiz_engine.prepare_recognition_card(card)
    assert result["mode"] == "recognition"
    assert any(o["correct"] for o in result["options"])
    assert len(result["options"]) >= 2


def test_prepare_recall_card(quiz_engine):
    """Recall card has expected answer."""
    words = quiz_engine.db.get_words_by_language("ru")
    card = _make_card(words[0])
    result = quiz_engine.prepare_recall_card(card)
    assert result["mode"] == "recall"
    assert "expected" in result
    assert result["question"] == card["meaning_de"]


def test_prepare_reverse_card(quiz_engine):
    """Reverse card expects German meaning."""
    words = quiz_engine.db.get_words_by_language("ru")
    card = _make_card(words[0])
    result = quiz_engine.prepare_reverse_card(card)
    assert result["mode"] == "reverse"
    assert "expected" in result


def test_distractors_fallback_few_words(populated_db):
    """Distractors still work when there are few words."""
    cluster = ClusterEngine(populated_db)
    engine = QuizEngine(populated_db, cluster)
    # zh only has 1 word, so distractors need fallback
    words = engine.db.get_words_by_language("zh")
    card = _make_card(words[0])
    distractors = engine.get_distractors(card, count=3)
    assert isinstance(distractors, list)


def test_recognition_card_has_question(quiz_engine):
    """Recognition card includes romanization in question if available."""
    words = quiz_engine.db.get_words_by_language("ru")
    card = _make_card(words[0])
    result = quiz_engine.prepare_recognition_card(card)
    # Russian words have romanization, so question should include it
    if card.get("romanization"):
        assert card["romanization"] in result["question"]
