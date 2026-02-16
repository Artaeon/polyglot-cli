"""Tests for the cluster comparison engine."""

import sys
import json
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database import Database
from engines.cluster import ClusterEngine


def _make_db():
    """Create a temporary in-memory database."""
    db = Database(Path(tempfile.mktemp(suffix=".db")))
    db.init_schema()
    return db


def _make_engine(db):
    """Create a cluster engine with test data."""
    engine = ClusterEngine(db)
    engine._cognates_cache = {
        "concepts": [
            {
                "id": "water",
                "de": "Wasser",
                "en": "water",
                "category": "nomen",
                "frequency_rank": 85,
                "translations": {
                    "ru": {"word": "вода", "romanization": "voda"},
                    "sk": {"word": "voda", "similarity_to": {"ru": 1.0}},
                    "it": {"word": "acqua"},
                    "es": {"word": "agua", "similarity_to": {"it": 0.85}},
                    "zh": {"word": "水", "romanization": "shuǐ", "tone": 3},
                },
                "etymology_note": "Proto-Slavic *voda",
                "mnemonic_hint": "Vodka = Wässerchen!",
            },
            {
                "id": "bread",
                "de": "Brot",
                "en": "bread",
                "category": "nomen",
                "frequency_rank": 120,
                "translations": {
                    "ru": {"word": "хлеб", "romanization": "khleb"},
                    "sk": {"word": "chlieb", "similarity_to": {"ru": 0.85}},
                },
            },
        ]
    }
    return engine


def test_find_concept_by_german():
    db = _make_db()
    engine = _make_engine(db)
    result = engine.find_concept("Wasser")
    assert result is not None
    assert result["id"] == "water"
    db.close()


def test_find_concept_by_english():
    db = _make_db()
    engine = _make_engine(db)
    result = engine.find_concept("water")
    assert result is not None
    assert result["id"] == "water"
    db.close()


def test_find_concept_by_id():
    db = _make_db()
    engine = _make_engine(db)
    result = engine.find_concept("bread")
    assert result is not None
    assert result["de"] == "Brot"
    db.close()


def test_find_concept_not_found():
    db = _make_db()
    engine = _make_engine(db)
    result = engine.find_concept("xyznonexistent")
    assert result is None
    db.close()


def test_search_concepts():
    db = _make_db()
    engine = _make_engine(db)
    results = engine.search_concepts("Br")
    assert len(results) == 1
    assert results[0]["id"] == "bread"
    db.close()


def test_get_cluster_data():
    db = _make_db()
    # Insert languages for the test
    from models import Language
    for lid, name, flag, family in [
        ("ru", "Russisch", "🇷🇺", "slavic"),
        ("sk", "Slowakisch", "🇸🇰", "slavic"),
        ("it", "Italienisch", "🇮🇹", "romance"),
        ("es", "Spanisch", "🇪🇸", "romance"),
        ("zh", "Chinesisch", "🇨🇳", "sinosphere"),
    ]:
        db.insert_language(Language(
            id=lid, name=name, native_name=name, flag=flag,
            family=family, subfamily="", script="latin",
            difficulty_tier=2,
        ))

    engine = _make_engine(db)
    concept = engine.find_concept("water")
    data = engine.get_cluster_data(concept)

    assert "families" in data
    assert "slavic" in data["families"]
    assert "romance" in data["families"]
    assert "sinosphere" in data["families"]
    assert data["total_languages"] == 5
    db.close()


def test_word_of_the_day():
    db = _make_db()
    engine = _make_engine(db)
    wotd = engine.get_word_of_the_day()
    assert wotd is not None
    assert "id" in wotd
    db.close()


def test_family_labels():
    db = _make_db()
    engine = _make_engine(db)
    assert engine.get_family_label("slavic") == "SLAWISCH"
    assert engine.get_family_label("romance") == "ROMANISCH"
    assert engine.get_family_color("slavic") == "blue"
    db.close()


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
