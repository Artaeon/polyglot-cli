"""Tests for the Database class — CRUD, search, streak, settings, transactions."""

from datetime import date, timedelta
from models import Word, Language


def test_insert_and_get_language(tmp_db, sample_languages):
    """Language insert and retrieval works."""
    lang = sample_languages[0]
    tmp_db.insert_language(lang)
    result = tmp_db.get_language("ru")
    assert result is not None
    assert result["name"] == "Russian"
    assert result["family"] == "slavic"


def test_get_all_languages(populated_db):
    """All inserted languages are returned."""
    langs = populated_db.get_all_languages()
    assert len(langs) == 3
    ids = {l["id"] for l in langs}
    assert ids == {"ru", "es", "zh"}


def test_get_languages_by_family(populated_db):
    """Family filter works."""
    slavic = populated_db.get_languages_by_family("slavic")
    assert len(slavic) == 1
    assert slavic[0]["id"] == "ru"


def test_insert_and_get_word(tmp_db, sample_languages, sample_words):
    """Word insert returns an ID and retrieval works."""
    tmp_db.insert_language(sample_languages[0])
    word = sample_words[0]
    word_id = tmp_db.insert_word(word)
    assert word_id > 0
    result = tmp_db.get_word(word_id)
    assert result["word"] == "вода"
    assert result["meaning_de"] == "Wasser"


def test_get_words_by_language(populated_db):
    """Words are filtered by language."""
    ru_words = populated_db.get_words_by_language("ru")
    assert len(ru_words) == 3
    es_words = populated_db.get_words_by_language("es")
    assert len(es_words) == 2


def test_get_words_by_category(populated_db):
    """Category filter works."""
    nouns = populated_db.get_words_by_language("ru", category="nomen")
    assert len(nouns) == 2
    adj = populated_db.get_words_by_language("ru", category="adjektive")
    assert len(adj) == 1


def test_search_words(populated_db):
    """Search by word, meaning, and concept works."""
    results = populated_db.search_words("Wasser")
    assert len(results) >= 2  # ru + es + zh all have "Wasser"

    results = populated_db.search_words("voda")
    assert len(results) >= 1


def test_bulk_insert_words(tmp_db, sample_languages):
    """Bulk insert works with dicts."""
    tmp_db.insert_language(sample_languages[0])
    words = [
        {"language_id": "ru", "word": "дом", "romanization": "dom",
         "pronunciation_hint": "DOM", "meaning_de": "Haus", "meaning_en": "house",
         "category": "nomen", "frequency_rank": 10, "concept_id": "house",
         "tone": None, "notes": ""},
        {"language_id": "ru", "word": "кот", "romanization": "kot",
         "pronunciation_hint": "KOT", "meaning_de": "Kater", "meaning_en": "cat",
         "category": "nomen", "frequency_rank": 11, "concept_id": "cat",
         "tone": None, "notes": ""},
    ]
    tmp_db.insert_words_bulk(words)
    all_words = tmp_db.get_words_by_language("ru")
    assert len(all_words) == 2


def test_create_and_get_review_card(populated_db):
    """Review card creation and due card retrieval."""
    words = populated_db.get_words_by_language("ru")
    word_id = words[0]["id"]
    card_id = populated_db.create_review_card(word_id)
    assert card_id > 0

    due = populated_db.get_due_cards(lang_id="ru")
    assert len(due) >= 1


def test_update_review_card(populated_db):
    """Review card update modifies ease/interval/reps."""
    words = populated_db.get_words_by_language("ru")
    word_id = words[0]["id"]
    card_id = populated_db.create_review_card(word_id)

    future = (date.today() + timedelta(days=6)).isoformat()
    populated_db.update_review_card(
        card_id, ease_factor=2.6, interval=6, repetitions=2,
        next_review_date=future, correct=True,
    )

    due = populated_db.get_due_cards(lang_id="ru")
    # Card should NOT be due now since next_review is in the future
    due_ids = [d["id"] for d in due]
    assert card_id not in due_ids


def test_settings(tmp_db):
    """Settings get/set round-trip works."""
    tmp_db.init_schema()
    tmp_db.set_setting("daily_minutes", "60")
    assert tmp_db.get_setting("daily_minutes") == "60"

    # Overwrite
    tmp_db.set_setting("daily_minutes", "90")
    assert tmp_db.get_setting("daily_minutes") == "90"


def test_get_all_settings(tmp_db):
    """All settings returned as dict."""
    tmp_db.init_schema()
    tmp_db.set_setting("daily_minutes", "90")
    tmp_db.set_setting("user_name", "Tester")
    settings = tmp_db.get_all_settings()
    assert settings["daily_minutes"] == "90"
    assert settings["user_name"] == "Tester"


def test_word_count_by_language(populated_db):
    """Word count grouped by language."""
    counts = populated_db.get_word_count_by_language()
    assert counts["ru"] == 3
    assert counts["es"] == 2
    assert counts["zh"] == 1
