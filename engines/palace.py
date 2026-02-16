"""Memory Palace trainer engine."""

from __future__ import annotations

from typing import Optional


class PalaceEngine:
    """Manages Memory Palace training and review."""

    def __init__(self, db, cluster_engine):
        self.db = db
        self.cluster = cluster_engine

    def get_palace_info(self, language_id: str) -> Optional[dict]:
        """Get palace metadata for a language."""
        lang = self.db.get_language(language_id)
        if not lang:
            return None
        stations = self.db.get_palace_stations(language_id)
        filled = sum(1 for s in stations if s.get("word_id"))
        return {
            "language": lang,
            "palace_name": lang.get("palace_name", ""),
            "palace_theme": lang.get("palace_theme", ""),
            "stations": stations,
            "total_stations": len(stations),
            "filled_stations": filled,
        }

    def get_next_empty_station(self, language_id: str) -> Optional[dict]:
        """Find the next empty station in a palace."""
        stations = self.db.get_palace_stations(language_id)
        for s in stations:
            if not s.get("word_id"):
                return s
        return None

    def get_next_word_for_palace(self, language_id: str) -> Optional[dict]:
        """Get the next unlearned word to place in the palace."""
        words = self.db.get_unlearned_words(language_id, limit=1)
        return words[0] if words else None

    def assign_word(self, station_id: int, word_id: int, mnemonic: str = ""):
        """Assign a word to a palace station and create review card."""
        self.db.assign_word_to_station(station_id, word_id, mnemonic)
        self.db.create_review_card(word_id)

    def get_cluster_for_word(self, word: dict) -> list[dict]:
        """Get cluster connections for a word being placed in a palace."""
        concept_id = word.get("concept_id", "")
        if not concept_id:
            return []

        concept = self.cluster.find_concept(concept_id)
        if not concept:
            return []

        translations = concept.get("translations", {})
        languages = self.db.get_all_languages()
        lang_map = {l["id"]: l for l in languages}
        current_lang = word.get("language_id", "")

        related = []
        for lid, t in translations.items():
            if lid != current_lang and lid in lang_map:
                sim = t.get("similarity_to", {})
                # Check similarity to current language
                sim_score = sim.get(current_lang)
                if sim_score and isinstance(sim_score, (int, float)) and sim_score >= 0.7:
                    related.append({
                        "flag": lang_map[lid]["flag"],
                        "word": t.get("word", ""),
                        "romanization": t.get("romanization", ""),
                        "similarity": sim_score,
                    })
        return sorted(related, key=lambda x: x["similarity"], reverse=True)

    def get_mnemonic_suggestion(self, word: dict, station: dict) -> str:
        """Generate a mnemonic suggestion for a word at a station."""
        w = word.get("word", "")
        rom = word.get("romanization", "")
        meaning = word.get("meaning_de", "")
        station_name = station.get("station_name", "")

        display = rom if rom else w
        return (
            f'Stell dir vor: An der Station "{station_name}" '
            f'siehst du etwas, das dich an "{display}" ({meaning}) erinnert.'
        )

    def review_palace(self, language_id: str) -> list[dict]:
        """Get all filled stations for palace review."""
        stations = self.db.get_palace_stations(language_id)
        return [s for s in stations if s.get("word_id")]

    def add_station(self, language_id: str, station_name: str) -> int:
        """Add a new station to a palace."""
        stations = self.db.get_palace_stations(language_id)
        next_num = len(stations) + 1
        self.db.conn.execute(
            """INSERT INTO palace_stations
               (language_id, station_number, station_name)
               VALUES (?, ?, ?)""",
            (language_id, next_num, station_name),
        )
        self.db.conn.commit()
        return next_num
