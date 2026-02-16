"""Sentence builder engine — construct sentences from learned vocabulary."""

from __future__ import annotations

import random
from datetime import date
from typing import Optional


# Language families with flexible word order
FLEXIBLE_ORDER_FAMILIES = {"slavic"}
# SOV languages
SOV_LANGUAGES = {"ja", "ko"}
# CJK no-space languages
NO_SPACE_LANGUAGES = {"zh", "ja"}


class SentenceBuilderEngine:
    """Sentence construction exercises with adaptive difficulty."""

    def __init__(self, db, sentence_engine):
        self.db = db
        self.sentence_engine = sentence_engine
        self._patterns = None

    @property
    def patterns(self) -> list[dict]:
        if self._patterns is None:
            self._patterns = self._load_patterns()
        return self._patterns

    def _load_patterns(self) -> list[dict]:
        """Load sentence structure patterns."""
        from config import BUILDER_DIR
        patterns_file = BUILDER_DIR / "patterns.json"
        if not patterns_file.exists():
            return self._default_patterns()
        import json
        with open(patterns_file, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("patterns", [])

    @staticmethod
    def _default_patterns() -> list[dict]:
        """Built-in patterns if no file exists."""
        return [
            {
                "id": "sv_simple", "name_de": "Subjekt + Verb",
                "difficulty": 1, "word_count": 2,
                "structure": ["pronomen_basics", "verben"],
                "grammar_note_de": "Einfacher Subjekt-Verb-Satz",
            },
            {
                "id": "svo_simple", "name_de": "Subjekt + Verb + Objekt",
                "difficulty": 2, "word_count": 3,
                "structure": ["pronomen_basics", "verben", "nomen"],
                "grammar_note_de": "Einfacher SVO-Satz",
            },
            {
                "id": "sva", "name_de": "Subjekt + Verb + Adjektiv",
                "difficulty": 2, "word_count": 3,
                "structure": ["pronomen_basics", "verben", "adjektive"],
                "grammar_note_de": "Satz mit Adjektiv",
            },
            {
                "id": "phrase", "name_de": "Phrase + Nomen",
                "difficulty": 1, "word_count": 2,
                "structure": ["phrasen", "nomen"],
                "grammar_note_de": "Einfache Phrase mit Nomen",
            },
            {
                "id": "svon", "name_de": "Subjekt + Verb + Objekt + Nomen",
                "difficulty": 3, "word_count": 4,
                "structure": ["pronomen_basics", "verben", "adjektive", "nomen"],
                "grammar_note_de": "Komplexerer Satz mit Adjektiv und Nomen",
            },
        ]

    def get_learned_vocabulary(self, lang_id: str) -> dict[str, list[dict]]:
        """Get learned words grouped by category."""
        from utils.word_fetch import get_learned_words
        words = get_learned_words(self.db, lang_id)

        grouped: dict[str, list[dict]] = {}
        for d in words:
            cat = d.get("category", "")
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append(d)
        return grouped

    def can_start(self, lang_id: str) -> tuple[bool, str]:
        """Check if user has enough vocabulary to start exercises."""
        vocab = self.get_learned_vocabulary(lang_id)
        total_words = sum(len(v) for v in vocab.values())
        categories = len(vocab)

        if total_words < 5:
            return False, f"Mindestens 5 Woerter noetig (du hast {total_words})."
        if categories < 2:
            return False, f"Mindestens 2 Kategorien noetig (du hast {categories})."
        return True, ""

    def get_available_patterns(self, lang_id: str) -> list[dict]:
        """Get patterns possible with user's known words."""
        vocab = self.get_learned_vocabulary(lang_id)
        available = []
        for pattern in self.patterns:
            structure = pattern.get("structure", [])
            if all(cat in vocab and len(vocab[cat]) > 0 for cat in structure):
                available.append(pattern)
        return available

    def generate_exercise(self, lang_id: str,
                          difficulty: int = None) -> Optional[dict]:
        """Generate a sentence building exercise."""
        available = self.get_available_patterns(lang_id)
        if not available:
            return None

        if difficulty is not None:
            filtered = [p for p in available if p["difficulty"] <= difficulty]
            if filtered:
                available = filtered

        pattern = random.choice(available)
        vocab = self.get_learned_vocabulary(lang_id)
        lang_data = self.db.get_language(lang_id)
        family = lang_data.get("family", "") if lang_data else ""

        # Pick words for each slot
        selected_words = []
        for category in pattern["structure"]:
            cat_words = vocab.get(category, [])
            if cat_words:
                selected_words.append(random.choice(cat_words))

        if len(selected_words) != len(pattern["structure"]):
            return None

        # Build target sentence
        target_words = [w["word"] for w in selected_words]
        target_meanings = [w["meaning_de"] for w in selected_words]

        # Reorder for SOV languages
        if lang_id in SOV_LANGUAGES and len(target_words) >= 3:
            # Move verb to end: S O V
            verb_idx = None
            for i, cat in enumerate(pattern["structure"]):
                if cat == "verben":
                    verb_idx = i
                    break
            if verb_idx is not None and verb_idx < len(target_words) - 1:
                verb_word = target_words.pop(verb_idx)
                target_words.append(verb_word)
                verb_meaning = target_meanings.pop(verb_idx)
                target_meanings.append(verb_meaning)

        # Build target sentence string
        separator = "" if lang_id in NO_SPACE_LANGUAGES else " "
        target_sentence = separator.join(target_words)

        # Create word bank with distractors
        all_distractors = []
        for cat_words in vocab.values():
            all_distractors.extend(cat_words)
        distractor_words = [
            w["word"] for w in random.sample(
                all_distractors, min(3, len(all_distractors))
            )
            if w["word"] not in target_words
        ]

        word_bank = target_words.copy() + distractor_words[:2]
        random.shuffle(word_bank)

        # Determine if word order is flexible
        flexible_order = family in FLEXIBLE_ORDER_FAMILIES

        return {
            "pattern": pattern,
            "target_words": target_words,
            "target_sentence": target_sentence,
            "target_meanings": target_meanings,
            "german_hint": " ".join(target_meanings),
            "word_bank": word_bank,
            "selected_word_data": selected_words,
            "flexible_order": flexible_order,
            "lang_id": lang_id,
            "difficulty": pattern["difficulty"],
            "grammar_note": pattern.get("grammar_note_de", ""),
        }

    def check_sentence(self, user_input: str, expected: str,
                        word_order_flexible: bool = False,
                        lang_id: str = "") -> dict:
        """Check user's sentence against expected."""
        user_clean = user_input.strip().lower()
        expected_clean = expected.strip().lower()

        if user_clean == expected_clean:
            return {"correct": True, "exact": True}

        if word_order_flexible:
            separator = "" if lang_id in NO_SPACE_LANGUAGES else " "
            user_words = set(user_clean.split(separator)) if separator else set(user_clean)
            expected_words = set(expected_clean.split(separator)) if separator else set(expected_clean)
            if user_words == expected_words:
                return {"correct": True, "exact": False,
                        "note": "Wortreihenfolge akzeptiert (flexibel)"}

        return {"correct": False, "exact": False}

    def get_session_exercises(self, lang_id: str, count: int = 10,
                               difficulty: int = None) -> list[dict]:
        """Get a batch of exercises with auto-progressing difficulty."""
        exercises = []
        current_diff = difficulty or 1
        correct_streak = 0

        for _ in range(count * 2):
            exercise = self.generate_exercise(lang_id, current_diff)
            if exercise:
                exercises.append(exercise)
                if len(exercises) >= count:
                    break

        return exercises

    def process_result(self, lang_id: str, pattern_id: str,
                        difficulty: int, correct: bool):
        """Record builder exercise result."""
        today = date.today().isoformat()

        row = self.db.conn.execute(
            """SELECT * FROM builder_performance
               WHERE language_id = ? AND pattern_id = ?""",
            (lang_id, pattern_id),
        ).fetchone()

        if row:
            self.db.conn.execute(
                """UPDATE builder_performance
                   SET attempts = attempts + 1,
                       correct = correct + ?,
                       last_attempted = ?
                   WHERE id = ?""",
                (1 if correct else 0, today, row["id"]),
            )
        else:
            self.db.conn.execute(
                """INSERT INTO builder_performance
                   (language_id, pattern_id, difficulty,
                    attempts, correct, last_attempted)
                   VALUES (?, ?, ?, 1, ?, ?)""",
                (lang_id, pattern_id, difficulty,
                 1 if correct else 0, today),
            )
        self.db.conn.commit()
