"""Tests for incremental data loading."""

import json

from utils.data_loader import DataLoader


def test_load_if_needed_sets_data_version(tmp_db, tmp_path, monkeypatch):
    languages_file = tmp_path / "languages.json"
    words_dir = tmp_path / "words"
    words_dir.mkdir(parents=True)
    cognates_file = tmp_path / "cognates.json"

    languages_file.write_text(
        json.dumps(
            {
                "languages": [
                    {
                        "id": "xx",
                        "name": "TestLang",
                        "native_name": "TestLang",
                        "flag": "🏳️",
                        "family": "test",
                        "subfamily": "test",
                        "script": "latin",
                        "difficulty_tier": 1,
                        "default_palace": {"name": "", "description": "", "theme": "", "stations": []},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    (words_dir / "test_words.json").write_text(
        json.dumps(
            {
                "language_id": "xx",
                "words": [
                    {
                        "word": "salut",
                        "romanization": "",
                        "pronunciation_hint": "",
                        "meaning_de": "hallo",
                        "meaning_en": "hello",
                        "category": "phrasen",
                        "frequency_rank": 1,
                        "concept_id": "hello",
                        "tone": None,
                        "notes": "",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    cognates_file.write_text(
        json.dumps(
            {
                "concepts": [
                    {
                        "id": "hello",
                        "de": "hallo",
                        "en": "hello",
                        "category": "phrasen",
                        "frequency_rank": 1,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr("utils.data_loader.LANGUAGES_FILE", languages_file)
    monkeypatch.setattr("utils.data_loader.WORDS_DIR", words_dir)
    monkeypatch.setattr("utils.data_loader.COGNATES_FILE", cognates_file)
    monkeypatch.setattr("utils.data_loader.DATA_VERSION", "test.1")

    loader = DataLoader(tmp_db)
    stats = loader.load_if_needed()

    assert stats["languages"] == 1
    assert stats["words"] == 1
    assert stats["concepts"] == 1
    assert tmp_db.get_setting("data_version") == "test.1"


def test_load_if_needed_is_incremental(tmp_db, tmp_path, monkeypatch):
    languages_file = tmp_path / "languages.json"
    words_dir = tmp_path / "words"
    words_dir.mkdir(parents=True)
    cognates_file = tmp_path / "cognates.json"

    languages_file.write_text(
        json.dumps(
            {
                "languages": [
                    {
                        "id": "xx",
                        "name": "TestLang",
                        "native_name": "TestLang",
                        "flag": "🏳️",
                        "family": "test",
                        "subfamily": "test",
                        "script": "latin",
                        "difficulty_tier": 1,
                        "default_palace": {"name": "", "description": "", "theme": "", "stations": []},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    word_payload = {
        "language_id": "xx",
        "words": [
            {
                "word": "salut",
                "romanization": "",
                "pronunciation_hint": "",
                "meaning_de": "hallo",
                "meaning_en": "hello",
                "category": "phrasen",
                "frequency_rank": 1,
                "concept_id": "hello",
                "tone": None,
                "notes": "",
            }
        ],
    }

    (words_dir / "test_words.json").write_text(
        json.dumps(word_payload),
        encoding="utf-8",
    )

    cognates_file.write_text(
        json.dumps({"concepts": []}),
        encoding="utf-8",
    )

    monkeypatch.setattr("utils.data_loader.LANGUAGES_FILE", languages_file)
    monkeypatch.setattr("utils.data_loader.WORDS_DIR", words_dir)
    monkeypatch.setattr("utils.data_loader.COGNATES_FILE", cognates_file)
    monkeypatch.setattr("utils.data_loader.DATA_VERSION", "test.2")

    loader = DataLoader(tmp_db)
    first = loader.load_if_needed()
    second = loader.load_if_needed()

    assert first["words"] == 1
    assert second["words"] == 0
