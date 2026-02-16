"""Tests for the custom vocabulary engine."""

import pytest
from engines.custom_vocab import CustomVocabEngine


@pytest.fixture
def custom_engine(populated_db):
    """CustomVocabEngine with populated database."""
    return CustomVocabEngine(populated_db)


def test_add_word(custom_engine):
    """Adding a custom word inserts into both tables."""
    cid = custom_engine.add_word(
        language_id="ru", word="тест", meaning_de="Test",
        meaning_en="test", romanization="test", tags="testing",
    )
    assert cid > 0

    # Should appear in custom_words
    words = custom_engine.get_custom_words()
    assert len(words) == 1
    assert words[0]["word"] == "тест"


def test_delete_custom_word(custom_engine):
    """Deleting removes from both tables."""
    cid = custom_engine.add_word(
        language_id="ru", word="удалить", meaning_de="loeschen",
    )
    assert custom_engine.delete_custom_word(cid) is True
    assert len(custom_engine.get_custom_words()) == 0


def test_delete_nonexistent(custom_engine):
    """Deleting non-existent word returns False."""
    assert custom_engine.delete_custom_word(9999) is False


def test_get_count(custom_engine):
    """Count returns correct number."""
    assert custom_engine.get_count() == 0
    custom_engine.add_word("ru", "слово", "Wort")
    assert custom_engine.get_count() == 1


def test_import_csv(custom_engine):
    """CSV import works."""
    csv_text = "word,meaning_de,meaning_en,romanization\nкот,Kater,cat,kot\nпёс,Hund,dog,pyos"
    count = custom_engine.import_csv(csv_text, "ru")
    assert count == 2
    words = custom_engine.get_custom_words()
    assert len(words) == 2


def test_export_csv(custom_engine):
    """CSV export produces valid CSV."""
    custom_engine.add_word("ru", "кот", "Kater", romanization="kot")
    csv_text = custom_engine.export_csv()
    assert "кот" in csv_text
    assert "Kater" in csv_text


def test_export_json(custom_engine):
    """JSON export produces valid JSON."""
    import json
    custom_engine.add_word("es", "gato", "Katze")
    json_text = custom_engine.export_json()
    data = json.loads(json_text)
    assert isinstance(data, (list, dict))
    # Handle both list and dict formats
    if isinstance(data, list):
        assert len(data) == 1
        assert data[0]["word"] == "gato"
    else:
        # Dict format with nested structure
        assert "gato" in json_text
