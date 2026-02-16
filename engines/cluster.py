"""Cluster comparison engine — the killer feature."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from config import COGNATES_FILE, FAMILY_COLORS, FAMILY_LABELS, FAMILY_EMOJIS


class ClusterEngine:
    """Engine for cross-language cluster comparison."""

    def __init__(self, db):
        self.db = db
        self._cognates_cache: Optional[dict] = None

    @property
    def cognates(self) -> dict:
        if self._cognates_cache is None:
            self._cognates_cache = self._load_cognates()
        return self._cognates_cache

    def _load_cognates(self) -> dict:
        """Load cognate mappings from JSON."""
        if not COGNATES_FILE.exists():
            return {"concepts": []}
        with open(COGNATES_FILE, encoding="utf-8") as f:
            return json.load(f)

    def find_concept(self, query: str) -> Optional[dict]:
        """Find a concept by German, English word, or concept ID."""
        query_lower = query.lower().strip()
        for concept in self.cognates.get("concepts", []):
            if (concept.get("id", "").lower() == query_lower
                    or concept.get("de", "").lower() == query_lower
                    or concept.get("en", "").lower() == query_lower):
                return concept
        return None

    def search_concepts(self, query: str) -> list[dict]:
        """Search concepts by partial match."""
        query_lower = query.lower().strip()
        results = []
        for concept in self.cognates.get("concepts", []):
            if (query_lower in concept.get("id", "").lower()
                    or query_lower in concept.get("de", "").lower()
                    or query_lower in concept.get("en", "").lower()):
                results.append(concept)
        return results

    def get_cluster_data(self, concept: dict) -> dict:
        """Organize concept translations by language family for display."""
        translations = concept.get("translations", {})
        languages = self.db.get_all_languages()
        lang_map = {lang["id"]: lang for lang in languages}

        # Get learned status from review cards
        learned_words = set()
        for lang_id in translations:
            words = self.db.get_words_by_concept(concept["id"])
            for w in words:
                card = self.db.conn.execute(
                    "SELECT id FROM review_cards WHERE word_id = ?",
                    (w["id"],)
                ).fetchone()
                if card:
                    learned_words.add(w["language_id"])

        families = {}
        family_order = ["slavic", "romance", "sinosphere", "uralic"]

        for family in family_order:
            family_langs = [l for l in languages if l["family"] == family]
            family_entries = []
            for lang in family_langs:
                lid = lang["id"]
                if lid in translations:
                    t = translations[lid]
                    entry = {
                        "lang_id": lid,
                        "lang_name": lang["name"],
                        "flag": lang["flag"],
                        "word": t.get("word", ""),
                        "romanization": t.get("romanization", ""),
                        "pronunciation_hint": t.get("pronunciation_hint", ""),
                        "tone": t.get("tone"),
                        "note": t.get("note", ""),
                        "similarity_to": t.get("similarity_to", {}),
                        "learned": lid in learned_words,
                        "family": family,
                        "subfamily": lang.get("subfamily", ""),
                    }
                    family_entries.append(entry)
            if family_entries:
                families[family] = family_entries

        # Count efficiency
        total_langs = sum(len(v) for v in families.values())
        unique_roots = len(families)

        return {
            "concept": concept,
            "families": families,
            "total_languages": total_langs,
            "unique_roots": unique_roots,
            "efficiency_msg": f"{unique_roots} Wörter lernen → {total_langs} Sprachen abdecken!",
        }

    def get_cluster_efficiency(self) -> dict:
        """Calculate overall cluster efficiency stats."""
        learned = self.db.get_learned_count_by_language()
        total_learned = sum(learned.values())

        # Calculate transfer bonus
        languages = self.db.get_all_languages()
        lang_map = {l["id"]: l for l in languages}

        transfer_bonus = 0
        # For each learned word, check if related words in cluster languages
        # are implicitly covered
        concepts_data = self.cognates.get("concepts", [])
        covered_set = set()

        for concept in concepts_data:
            translations = concept.get("translations", {})
            # Check which languages have this concept learned
            learned_langs = []
            for lid in translations:
                if lid in learned and learned[lid] > 0:
                    # Check if this specific concept is learned
                    words = self.db.get_words_by_concept(concept["id"])
                    for w in words:
                        if w["language_id"] == lid:
                            card = self.db.conn.execute(
                                "SELECT id FROM review_cards WHERE word_id = ?",
                                (w["id"],)
                            ).fetchone()
                            if card:
                                learned_langs.append(lid)
                                break

            if learned_langs:
                # Count all languages that have this concept as bonus
                for lid in translations:
                    if lid not in learned_langs:
                        key = f"{concept['id']}:{lid}"
                        if key not in covered_set:
                            # Check similarity
                            t = translations[lid]
                            sim = t.get("similarity_to", {})
                            for ref_lang in learned_langs:
                                if ref_lang in sim:
                                    score = sim[ref_lang]
                                    if isinstance(score, (int, float)) and score >= 0.7:
                                        covered_set.add(key)
                                        transfer_bonus += 1
                                        break

        effective = total_learned + transfer_bonus
        efficiency = round(effective / max(total_learned, 1) * 100)

        return {
            "unique_learned": total_learned,
            "transfer_bonus": transfer_bonus,
            "effective_total": effective,
            "efficiency_percent": efficiency,
        }

    def get_word_of_the_day(self) -> Optional[dict]:
        """Pick a concept with high cluster efficiency as word of the day."""
        from datetime import date
        concepts = self.cognates.get("concepts", [])
        if not concepts:
            return None
        # Use day of year to cycle through concepts
        day = date.today().timetuple().tm_yday
        idx = day % len(concepts)
        return concepts[idx]

    def get_family_label(self, family: str) -> str:
        return FAMILY_LABELS.get(family, family.upper())

    def get_family_color(self, family: str) -> str:
        return FAMILY_COLORS.get(family, "white")

    def get_family_emoji(self, family: str) -> str:
        return FAMILY_EMOJIS.get(family, "")
