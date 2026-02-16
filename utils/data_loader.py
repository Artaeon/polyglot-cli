"""Data loading and upgrade routines for initial vocabulary imports."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from config import COGNATES_FILE, DATA_VERSION, LANGUAGES_FILE, WORDS_DIR
from models import Language

if TYPE_CHECKING:
    from db.database import Database

logger = logging.getLogger(__name__)


class DataLoader:
    """Loads or upgrades static language data into the database."""

    def __init__(self, db: Database) -> None:
        self.db = db

    def load_if_needed(self) -> dict[str, int]:
        """Import data if DB is empty or bundled data version changed."""
        current_version = self.db.get_setting("data_version", "")
        has_languages = bool(self.db.get_all_languages())

        if has_languages and current_version == DATA_VERSION:
            return {"languages": 0, "words": 0, "concepts": 0}

        stats = {"languages": 0, "words": 0, "concepts": 0}
        with self.db.transaction():
            stats["languages"] = self._load_languages()
            stats["words"] = self._load_words_incremental()
            stats["concepts"] = self._load_concepts()
            self.db.set_setting("data_version", DATA_VERSION)

        return stats

    def _load_languages(self) -> int:
        if not LANGUAGES_FILE.exists():
            return 0

        with open(LANGUAGES_FILE, encoding="utf-8") as f:
            lang_data = json.load(f)

        inserted = 0
        for ld in lang_data.get("languages", []):
            palace = ld.get("default_palace", {})
            lang = Language(
                id=ld["id"],
                name=ld["name"],
                native_name=ld.get("native_name", ""),
                flag=ld.get("flag", ""),
                family=ld.get("family", ""),
                subfamily=ld.get("subfamily", ""),
                script=ld.get("script", ""),
                difficulty_tier=ld.get("difficulty_tier", 3),
                palace_name=palace.get("name", ""),
                palace_description=palace.get("description", ""),
                palace_theme=palace.get("theme", ""),
                palace_stations=palace.get("stations", []),
            )
            self.db.insert_language(lang)
            if palace.get("stations"):
                self.db.init_palace_stations(lang.id, palace["stations"])
            inserted += 1

        return inserted

    def _load_words_incremental(self) -> int:
        if not WORDS_DIR.exists():
            return 0

        inserted_total = 0

        for vocab_file in sorted(WORDS_DIR.glob("*.json")):
            try:
                with open(vocab_file, encoding="utf-8") as f:
                    vocab_data = json.load(f)

                lang_id = vocab_data.get("language_id", "")
                if not lang_id:
                    continue

                existing = self.db.get_existing_word_keys(lang_id)
                candidates: list[dict] = []
                for w in vocab_data.get("words", []):
                    key = (w.get("word", ""), w.get("meaning_de", ""))
                    if not key[0] or key in existing:
                        continue
                    candidates.append(
                        {
                            "language_id": lang_id,
                            "word": w.get("word", ""),
                            "romanization": w.get("romanization", ""),
                            "pronunciation_hint": w.get("pronunciation_hint", ""),
                            "meaning_de": w.get("meaning_de", ""),
                            "meaning_en": w.get("meaning_en", ""),
                            "category": w.get("category", ""),
                            "frequency_rank": w.get("frequency_rank", 0),
                            "concept_id": w.get("concept_id", ""),
                            "tone": w.get("tone"),
                            "notes": w.get("notes", ""),
                        }
                    )

                if candidates:
                    self.db.insert_words_bulk(candidates)
                    inserted_total += len(candidates)
            except (json.JSONDecodeError, KeyError) as exc:
                logger.warning("Error loading %s: %s", vocab_file.name, exc)

        return inserted_total

    def _load_concepts(self) -> int:
        if not COGNATES_FILE.exists():
            return 0

        with open(COGNATES_FILE, encoding="utf-8") as f:
            cognates = json.load(f)

        inserted = 0
        for concept in cognates.get("concepts", []):
            self.db.insert_concept(concept)
            inserted += 1

        return inserted
