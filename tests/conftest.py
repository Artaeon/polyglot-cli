"""Shared test fixtures for PolyglotCLI."""

import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import sqlite3
import pytest
from db.database import Database
from models import Word, Language


@pytest.fixture
def tmp_db(tmp_path):
    """Create a temporary database with schema initialized."""
    db_path = tmp_path / "test.db"
    db = Database(db_path)
    db.init_schema()
    yield db
    db.close()


@pytest.fixture
def sample_languages():
    """Sample language data for testing."""
    return [
        Language(
            id="ru", name="Russian", native_name="Русский", flag="🇷🇺",
            family="slavic", subfamily="east_slavic", script="cyrillic",
            difficulty_tier=2, palace_name="Kreml", palace_theme="golden",
        ),
        Language(
            id="es", name="Spanish", native_name="Español", flag="🇪🇸",
            family="romance", subfamily="iberian", script="latin",
            difficulty_tier=1, palace_name="Alhambra", palace_theme="moorish",
        ),
        Language(
            id="zh", name="Chinese", native_name="中文", flag="🇨🇳",
            family="sinosphere", subfamily="chinese", script="hanzi",
            difficulty_tier=4, palace_name="Verbotene Stadt", palace_theme="imperial",
        ),
    ]


@pytest.fixture
def sample_words():
    """Sample word data for testing."""
    return [
        Word(id=0, language_id="ru", word="вода", romanization="voda",
             meaning_de="Wasser", meaning_en="water", category="nomen",
             frequency_rank=1, concept_id="water"),
        Word(id=0, language_id="ru", word="хлеб", romanization="khleb",
             meaning_de="Brot", meaning_en="bread", category="nomen",
             frequency_rank=2, concept_id="bread"),
        Word(id=0, language_id="ru", word="хороший", romanization="khoroshiy",
             meaning_de="gut", meaning_en="good", category="adjektive",
             frequency_rank=3, concept_id="good"),
        Word(id=0, language_id="es", word="agua",
             meaning_de="Wasser", meaning_en="water", category="nomen",
             frequency_rank=1, concept_id="water"),
        Word(id=0, language_id="es", word="pan",
             meaning_de="Brot", meaning_en="bread", category="nomen",
             frequency_rank=2, concept_id="bread"),
        Word(id=0, language_id="zh", word="水", romanization="shuǐ",
             meaning_de="Wasser", meaning_en="water", category="nomen",
             frequency_rank=1, concept_id="water", tone=3),
    ]


@pytest.fixture
def populated_db(tmp_db, sample_languages, sample_words):
    """Database with languages and words pre-loaded."""
    for lang in sample_languages:
        tmp_db.insert_language(lang)
    for word in sample_words:
        tmp_db.insert_word(word)
    return tmp_db


@pytest.fixture
def app(populated_db):
    """Minimal AppContext with populated database (no full engine init)."""
    from app import AppContext
    ctx = AppContext()
    ctx.db = populated_db
    return ctx
