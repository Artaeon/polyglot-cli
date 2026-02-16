"""Verb conjugation drill engine."""

from __future__ import annotations

import json
import random
from datetime import date
from pathlib import Path
from typing import Optional

from config import CONJUGATIONS_DIR


class ConjugationEngine:
    """Verb conjugation drills with pattern explanations and mastery tracking."""

    def __init__(self, db):
        self.db = db
        self._cache: dict[str, dict] = {}

    def _load_lang_data(self, lang_id: str) -> Optional[dict]:
        """Load conjugation data for a language."""
        if lang_id in self._cache:
            return self._cache[lang_id]

        file_path = CONJUGATIONS_DIR / f"{lang_id}.json"
        if not file_path.exists():
            return None

        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
        self._cache[lang_id] = data
        return data

    def get_available_languages(self) -> list[str]:
        """Return language IDs that have conjugation files."""
        if not CONJUGATIONS_DIR.exists():
            return []
        return sorted(
            p.stem for p in CONJUGATIONS_DIR.glob("*.json")
        )

    @staticmethod
    def _get_verb_forms(verb: dict) -> dict:
        """Get forms from verb, supporting both 'forms' and 'conjugations' keys."""
        return verb.get("forms") or verb.get("conjugations") or {}

    def get_verbs(self, lang_id: str) -> list[dict]:
        """Get all verbs for a language."""
        data = self._load_lang_data(lang_id)
        if not data:
            return []
        return data.get("verbs", [])

    def get_tenses(self, lang_id: str) -> list[str]:
        """Get available tenses for a language."""
        data = self._load_lang_data(lang_id)
        if not data:
            return []
        return data.get("meta", {}).get("tenses", [])

    def get_persons(self, lang_id: str) -> list[str]:
        """Get person labels for a language."""
        data = self._load_lang_data(lang_id)
        if not data:
            return []
        return data.get("meta", {}).get("persons", [])

    def get_person_labels(self, lang_id: str) -> dict[str, str]:
        """Get German labels for persons."""
        data = self._load_lang_data(lang_id)
        if not data:
            return {}
        return data.get("meta", {}).get("person_labels_de", {})

    def get_tense_labels(self, lang_id: str) -> dict[str, str]:
        """Get German labels for tenses."""
        data = self._load_lang_data(lang_id)
        if not data:
            return {}
        return data.get("meta", {}).get("tense_labels_de", {})

    def prepare_forward_drill(self, lang_id: str, tense_filter: str = None,
                               count: int = 10) -> list[dict]:
        """Forward drill: infinitive + person -> type conjugated form."""
        verbs = self.get_verbs(lang_id)
        if not verbs:
            return []

        person_labels = self.get_person_labels(lang_id)
        tense_labels = self.get_tense_labels(lang_id)
        items = []

        for verb in verbs:
            forms = self._get_verb_forms(verb)
            for tense, tense_forms in forms.items():
                if tense_filter and tense != tense_filter:
                    continue
                for person, form_data in tense_forms.items():
                    items.append({
                        "type": "forward",
                        "verb": verb,
                        "infinitive": verb["infinitive"],
                        "romanization": verb.get("romanization", ""),
                        "concept_id": verb.get("concept_id", ""),
                        "tense": tense,
                        "tense_label": tense_labels.get(tense, tense),
                        "person": person,
                        "person_label": person_labels.get(person, person),
                        "expected": form_data.get("form", ""),
                        "expected_romanization": form_data.get("romanization", ""),
                        "pattern_id": verb.get("pattern_id", ""),
                        "lang_id": lang_id,
                    })

        random.shuffle(items)
        return items[:count]

    def prepare_reverse_drill(self, lang_id: str, tense_filter: str = None,
                               count: int = 10) -> list[dict]:
        """Reverse drill: conjugated form -> identify infinitive + person."""
        verbs = self.get_verbs(lang_id)
        if not verbs:
            return []

        person_labels = self.get_person_labels(lang_id)
        tense_labels = self.get_tense_labels(lang_id)
        items = []

        for verb in verbs:
            forms = self._get_verb_forms(verb)
            for tense, tense_forms in forms.items():
                if tense_filter and tense != tense_filter:
                    continue
                for person, form_data in tense_forms.items():
                    items.append({
                        "type": "reverse",
                        "verb": verb,
                        "conjugated_form": form_data.get("form", ""),
                        "conjugated_romanization": form_data.get("romanization", ""),
                        "expected_infinitive": verb["infinitive"],
                        "expected_person": person,
                        "expected_tense": tense,
                        "tense_label": tense_labels.get(tense, tense),
                        "person_label": person_labels.get(person, person),
                        "concept_id": verb.get("concept_id", ""),
                        "pattern_id": verb.get("pattern_id", ""),
                        "lang_id": lang_id,
                    })

        random.shuffle(items)
        return items[:count]

    def prepare_mixed_drill(self, lang_id: str, tense_filter: str = None,
                             count: int = 10) -> list[dict]:
        """Mixed forward and reverse drills."""
        forward = self.prepare_forward_drill(lang_id, tense_filter, count)
        reverse = self.prepare_reverse_drill(lang_id, tense_filter, count)
        items = forward[:count // 2] + reverse[:count // 2]
        random.shuffle(items)
        return items[:count]

    def check_conjugation_answer(self, user_input: str, expected: str,
                                  alt_romanization: str = "") -> bool:
        """Check answer, accepting script or romanization."""
        from utils.answer_check import check_answer
        return check_answer(user_input, expected, alt_romanization=alt_romanization)

    def get_pattern_explanation(self, lang_id: str,
                                 pattern_id: str) -> Optional[dict]:
        """Get conjugation pattern rule display."""
        data = self._load_lang_data(lang_id)
        if not data:
            return None
        for pattern in data.get("conjugation_patterns", []):
            if pattern["pattern_id"] == pattern_id:
                return pattern
        return None

    def get_verb_full_table(self, lang_id: str,
                             verb_concept_id: str) -> Optional[dict]:
        """Get full conjugation table for a verb."""
        verbs = self.get_verbs(lang_id)
        for verb in verbs:
            if verb.get("concept_id") == verb_concept_id:
                return verb
        return None

    def process_conjugation_result(self, lang_id: str, verb_concept_id: str,
                                    tense: str, person: str,
                                    correct: bool):
        """Record conjugation drill result."""
        today = date.today().isoformat()

        row = self.db.conn.execute(
            """SELECT * FROM conjugation_mastery
               WHERE language_id = ? AND verb_concept_id = ?
               AND tense = ? AND person = ?""",
            (lang_id, verb_concept_id, tense, person),
        ).fetchone()

        if row:
            new_streak = (row["streak"] + 1) if correct else 0
            mastered = 1 if new_streak >= 3 else 0
            self.db.conn.execute(
                """UPDATE conjugation_mastery
                   SET attempts = attempts + 1,
                       correct = correct + ?,
                       streak = ?,
                       mastered = ?,
                       last_attempted = ?
                   WHERE id = ?""",
                (1 if correct else 0, new_streak, mastered, today, row["id"]),
            )
        else:
            self.db.conn.execute(
                """INSERT INTO conjugation_mastery
                   (language_id, verb_concept_id, tense, person,
                    attempts, correct, streak, mastered, last_attempted)
                   VALUES (?, ?, ?, ?, 1, ?, ?, 0, ?)""",
                (lang_id, verb_concept_id, tense, person,
                 1 if correct else 0, 1 if correct else 0, today),
            )
        self.db.conn.commit()

    def get_mastery_overview(self, lang_id: str) -> dict:
        """Get verb x tense mastery grid."""
        rows = self.db.conn.execute(
            """SELECT verb_concept_id, tense, person,
                      attempts, correct, mastered
               FROM conjugation_mastery
               WHERE language_id = ?""",
            (lang_id,),
        ).fetchall()

        mastery = {}
        for r in rows:
            key = r["verb_concept_id"]
            if key not in mastery:
                mastery[key] = {}
            tense = r["tense"]
            if tense not in mastery[key]:
                mastery[key][tense] = {"total": 0, "mastered": 0}
            mastery[key][tense]["total"] += 1
            if r["mastered"]:
                mastery[key][tense]["mastered"] += 1

        return mastery
