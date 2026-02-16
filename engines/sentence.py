"""Sentence translation engine — input a sentence, see it in all 22 languages."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

from config import DATA_DIR, FAMILY_COLORS, FAMILY_LABELS


SENTENCES_FILE = DATA_DIR / "sentences" / "templates.json"


class SentenceEngine:
    """Provides sentence-level translation across all 22 languages."""

    def __init__(self, db):
        self.db = db
        self._templates: list[dict] = []
        self._load_templates()

    def _load_templates(self):
        """Load sentence templates from JSON."""
        if SENTENCES_FILE.exists():
            with open(SENTENCES_FILE, encoding="utf-8") as f:
                data = json.load(f)
            self._templates = data.get("sentences", [])

    def get_categories(self) -> list[str]:
        """Get all available sentence categories."""
        cats = set()
        for s in self._templates:
            cats.add(s.get("category", ""))
        return sorted(cats)

    def get_sentences_by_category(self, category: str) -> list[dict]:
        """Get all sentences in a category."""
        return [s for s in self._templates if s.get("category") == category]

    def search_sentences(self, query: str) -> list[dict]:
        """Search sentences by German or English text, or by ID."""
        query_lower = query.lower()
        results = []
        for s in self._templates:
            if (query_lower in s.get("de", "").lower() or
                    query_lower in s.get("en", "").lower() or
                    query_lower in s.get("id", "").lower()):
                results.append(s)
        return results

    def find_best_match(self, query: str) -> Optional[dict]:
        """Find the best matching sentence template for user input."""
        query_norm = self._normalize_text(query)

        # Helpful intent shortcuts for common user phrasing
        if "my name is" in query_norm:
            sentence = self.get_sentence_by_id("my_name_is")
            if sentence:
                return sentence
        if "i don't understand" in query_norm or "i dont understand" in query_norm:
            sentence = self.get_sentence_by_id("i_dont_understand")
            if sentence:
                return sentence

        # Try matching sentence fragments (before/after comma, and/or, etc.)
        fragments = [frag.strip() for frag in re.split(r",|;| and | und ", query_norm) if frag.strip()]

        # Exact match first
        for s in self._templates:
            de = self._normalize_text(s.get("de", ""))
            en = self._normalize_text(s.get("en", ""))
            if query_norm == de or query_norm == en:
                return s
            for fragment in fragments:
                if fragment == de or fragment == en:
                    return s

        # Fuzzy token overlap fallback
        q_tokens = set(query_norm.split())
        best_score = 0
        best_match = None

        for s in self._templates:
            de_tokens = set(self._normalize_text(s.get("de", "")).split())
            en_tokens = set(self._normalize_text(s.get("en", "")).split())
            overlap = max(len(q_tokens & de_tokens), len(q_tokens & en_tokens))
            if overlap > best_score:
                best_score = overlap
                best_match = s

        if best_match and best_score >= 2:
            return best_match

        # Partial match — look for key words
        results = self.search_sentences(query_norm)
        if results:
            return results[0]

        return None

    def _normalize_text(self, text: str) -> str:
        """Normalize text for robust sentence matching."""
        cleaned = re.sub(r"[^\w\s]", " ", text.lower())
        return " ".join(cleaned.split())

    def get_sentence_translations(self, sentence: dict) -> dict:
        """Get formatted translation data for display.

        Returns a dict with:
          - sentence: the original sentence dict
          - families: dict of family -> list of translation entries
        """
        translations = sentence.get("translations", {})
        languages = self.db.get_all_languages()

        # Build lang lookup
        lang_map = {}
        for lang in languages:
            lang_map[lang["id"]] = lang

        families: dict[str, list] = {}

        for lang_id, trans in translations.items():
            lang = lang_map.get(lang_id)
            if not lang:
                continue

            family = lang.get("family", "other")
            if family not in families:
                families[family] = []

            entry = {
                "lang_id": lang_id,
                "lang_name": lang["name"],
                "flag": lang.get("flag", ""),
                "family": family,
                "text": trans.get("text", ""),
                "romanization": trans.get("romanization") or "",
                "pronunciation": trans.get("pronunciation", ""),
                "grammar": trans.get("grammar", ""),
            }
            families[family].append(entry)

        # Sort families in canonical order
        family_order = ["slavic", "romance", "sinosphere", "uralic"]
        sorted_families = {}
        for f in family_order:
            if f in families:
                sorted_families[f] = families[f]
        for f in families:
            if f not in sorted_families:
                sorted_families[f] = families[f]

        return {
            "sentence": sentence,
            "families": sorted_families,
        }

    def word_by_word_lookup(self, query: str) -> list[dict]:
        """For sentences not in templates, try word-by-word DB lookup.

        Returns a list of found words across all languages.
        """
        words = query.lower().strip().split()
        results = []

        for word in words:
            # Search by German meaning
            found = self.db.search_words(word)
            if found:
                # Group by concept_id to avoid duplicates
                seen_concepts = set()
                for f in found:
                    cid = f.get("concept_id", "")
                    if cid and cid not in seen_concepts:
                        seen_concepts.add(cid)
                        results.append({
                            "query_word": word,
                            "concept_id": cid,
                            "matches": [
                                r for r in found if r.get("concept_id") == cid
                            ],
                        })
                    elif not cid:
                        results.append({
                            "query_word": word,
                            "concept_id": "",
                            "matches": [f],
                        })
        return results

    def get_all_sentences(self) -> list[dict]:
        """Get all available sentence templates."""
        return self._templates

    def get_sentence_by_id(self, sentence_id: str) -> Optional[dict]:
        """Get a specific sentence by its ID."""
        for s in self._templates:
            if s.get("id") == sentence_id:
                return s
        return None
