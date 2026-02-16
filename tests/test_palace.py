"""Tests for the Memory Palace trainer."""

import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database import Database
from engines.cluster import ClusterEngine
from engines.palace import PalaceEngine
from models import Language, Word


def _setup():
    """Create test database with sample data."""
    db = Database(Path(tempfile.mktemp(suffix=".db")))
    db.init_schema()

    # Insert a language
    lang = Language(
        id="sk", name="Slowakisch", native_name="Slovenčina",
        flag="🇸🇰", family="slavic", subfamily="west_slavic",
        script="latin", difficulty_tier=1,
        palace_name="Weg zur Arbeit", palace_theme="Normal",
        palace_stations=["Haustür", "Bushaltestelle", "Kreuzung"],
    )
    db.insert_language(lang)
    db.init_palace_stations("sk", ["Haustür", "Bushaltestelle", "Kreuzung"])

    # Insert words
    w1_id = db.insert_word(Word(
        id=0, language_id="sk", word="voda", meaning_de="Wasser",
        meaning_en="water", category="nomen", frequency_rank=85,
        concept_id="water",
    ))
    w2_id = db.insert_word(Word(
        id=0, language_id="sk", word="chlieb", meaning_de="Brot",
        meaning_en="bread", category="nomen", frequency_rank=120,
        concept_id="bread",
    ))

    cluster = ClusterEngine(db)
    cluster._cognates_cache = {"concepts": []}
    palace = PalaceEngine(db, cluster)

    return db, palace, w1_id, w2_id


def test_get_palace_info():
    db, palace, _, _ = _setup()
    info = palace.get_palace_info("sk")
    assert info is not None
    assert info["palace_name"] == "Weg zur Arbeit"
    assert info["total_stations"] == 3
    assert info["filled_stations"] == 0
    db.close()


def test_get_next_empty_station():
    db, palace, _, _ = _setup()
    station = palace.get_next_empty_station("sk")
    assert station is not None
    assert station["station_number"] == 1
    assert station["station_name"] == "Haustür"
    db.close()


def test_assign_word_to_station():
    db, palace, w1_id, _ = _setup()
    station = palace.get_next_empty_station("sk")
    palace.assign_word(station["id"], w1_id, "Wasser fließt durch die Haustür")

    # Check station is now filled
    info = palace.get_palace_info("sk")
    assert info["filled_stations"] == 1

    # Check review card was created
    cards = db.get_due_cards("sk")
    assert len(cards) == 1
    db.close()


def test_next_empty_after_filling():
    db, palace, w1_id, w2_id = _setup()
    station1 = palace.get_next_empty_station("sk")
    palace.assign_word(station1["id"], w1_id, "mnemonic 1")

    station2 = palace.get_next_empty_station("sk")
    assert station2 is not None
    assert station2["station_number"] == 2
    db.close()


def test_review_palace():
    db, palace, w1_id, w2_id = _setup()

    # Fill two stations
    station1 = palace.get_next_empty_station("sk")
    palace.assign_word(station1["id"], w1_id, "mnemonic 1")
    station2 = palace.get_next_empty_station("sk")
    palace.assign_word(station2["id"], w2_id, "mnemonic 2")

    filled = palace.review_palace("sk")
    assert len(filled) == 2
    db.close()


def test_add_station():
    db, palace, _, _ = _setup()
    num = palace.add_station("sk", "Neue Station")
    assert num == 4

    info = palace.get_palace_info("sk")
    assert info["total_stations"] == 4
    db.close()


def test_mnemonic_suggestion():
    db, palace, _, _ = _setup()
    word = {"word": "voda", "romanization": "", "meaning_de": "Wasser"}
    station = {"station_name": "Haustür"}
    suggestion = palace.get_mnemonic_suggestion(word, station)
    assert "Haustür" in suggestion
    assert "voda" in suggestion
    db.close()


def test_palace_not_found():
    db, palace, _, _ = _setup()
    info = palace.get_palace_info("nonexistent")
    assert info is None
    db.close()


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
