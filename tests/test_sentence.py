"""Tests for the sentence translation engine."""

import pytest
from engines.sentence import SentenceEngine


@pytest.fixture
def sentence_engine(populated_db):
    """SentenceEngine with populated database."""
    return SentenceEngine(populated_db)


def test_templates_loaded(sentence_engine):
    """Templates are loaded from JSON file."""
    sentences = sentence_engine.get_all_sentences()
    assert isinstance(sentences, list)
    assert len(sentences) >= 10  # At least our original 13


def test_get_categories(sentence_engine):
    """Categories are extracted from templates."""
    cats = sentence_engine.get_categories()
    assert isinstance(cats, list)
    assert "greetings" in cats
    assert "travel" in cats


def test_get_sentences_by_category(sentence_engine):
    """Category filter returns correct sentences."""
    greetings = sentence_engine.get_sentences_by_category("greetings")
    assert len(greetings) >= 1
    for s in greetings:
        assert s["category"] == "greetings"


def test_search_sentences(sentence_engine):
    """Search finds sentences by German text."""
    results = sentence_engine.search_sentences("Hallo")
    assert len(results) >= 1


def test_find_best_match_exact(sentence_engine):
    """Exact match works for German input."""
    match = sentence_engine.find_best_match("Ich liebe dich.")
    assert match is not None
    assert match["id"] == "i_love_you"


def test_find_best_match_english(sentence_engine):
    """Exact match works for English input."""
    match = sentence_engine.find_best_match("I love you.")
    assert match is not None


def test_find_best_match_partial(sentence_engine):
    """Partial match works."""
    match = sentence_engine.find_best_match("liebe")
    assert match is not None


def test_find_best_match_none(sentence_engine):
    """No match returns None."""
    match = sentence_engine.find_best_match("xyzzyplugh")
    assert match is None


def test_get_sentence_translations(sentence_engine):
    """Translations are returned with family grouping."""
    sentences = sentence_engine.get_all_sentences()
    if sentences:
        data = sentence_engine.get_sentence_translations(sentences[0])
        assert "sentence" in data
        assert "families" in data
