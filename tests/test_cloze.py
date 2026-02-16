"""Tests for the cloze exercise engine."""

import pytest
from engines.cloze import ClozeEngine
from engines.sentence import SentenceEngine


@pytest.fixture
def cloze_engine(populated_db):
    """ClozeEngine with populated database."""
    sentence = SentenceEngine(populated_db)
    return ClozeEngine(populated_db, sentence)


def test_word_in_sentence_latin(cloze_engine):
    """Latin-script word detection works with word boundaries."""
    assert cloze_engine._word_in_sentence("agua", "El agua es fría.", "es") is True
    assert cloze_engine._word_in_sentence("gua", "El agua es fría.", "es") is False


def test_word_in_sentence_cjk(cloze_engine):
    """CJK substring matching works."""
    assert cloze_engine._word_in_sentence("水", "我喝水", "zh") is True
    assert cloze_engine._word_in_sentence("火", "我喝水", "zh") is False


def test_blank_word_latin(cloze_engine):
    """Blanking replaces word with ___ in Latin text."""
    result = cloze_engine._blank_word("El agua es fría.", "agua", "es")
    assert "___" in result
    assert "agua" not in result


def test_blank_word_cjk(cloze_engine):
    """Blanking replaces word with ___ in CJK text."""
    result = cloze_engine._blank_word("我喝水", "水", "zh")
    assert result == "我喝___"


def test_check_cloze_answer_correct(cloze_engine):
    """Correct answer passes check."""
    assert cloze_engine.check_cloze_answer("вода", "вода") is True


def test_check_cloze_answer_romanization(cloze_engine):
    """Romanization is accepted as answer."""
    assert cloze_engine.check_cloze_answer("voda", "вода", alt_romanization="voda") is True


def test_session_items_no_learned_words(cloze_engine):
    """No session items when no words are learned."""
    items = cloze_engine.get_session_items("ru", count=5)
    assert len(items) == 0


def test_context_clozes_with_learned_words(populated_db):
    """Context cloze items generated when words are learned."""
    sentence = SentenceEngine(populated_db)
    engine = ClozeEngine(populated_db, sentence)

    # Learn all Russian words
    words = populated_db.get_words_by_language("ru")
    for w in words:
        populated_db.create_review_card(w["id"])

    items = engine._generate_context_clozes("ru", 3, "mixed")
    assert len(items) > 0
    assert items[0]["type"] == "word_context_cloze"
    assert "expected" in items[0]


def test_process_cloze_result(populated_db):
    """Cloze result is recorded in tracking table."""
    sentence = SentenceEngine(populated_db)
    engine = ClozeEngine(populated_db, sentence)

    words = populated_db.get_words_by_language("ru")
    wid = words[0]["id"]

    engine.process_cloze_result(wid, correct=True, cloze_type="sentence")

    row = populated_db.conn.execute(
        "SELECT * FROM cloze_performance WHERE word_id = ?", (wid,)
    ).fetchone()
    assert row is not None
    assert row["attempts"] == 1
    assert row["correct"] == 1


def test_process_cloze_result_updates(populated_db):
    """Repeated cloze results update existing record."""
    sentence = SentenceEngine(populated_db)
    engine = ClozeEngine(populated_db, sentence)

    words = populated_db.get_words_by_language("ru")
    wid = words[0]["id"]

    engine.process_cloze_result(wid, correct=True, cloze_type="sentence")
    engine.process_cloze_result(wid, correct=False, cloze_type="sentence")

    row = populated_db.conn.execute(
        "SELECT * FROM cloze_performance WHERE word_id = ?", (wid,)
    ).fetchone()
    assert row["attempts"] == 2
    assert row["correct"] == 1
