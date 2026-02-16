"""Cloze exercise engine — gap-fill exercises from sentences and words."""

from __future__ import annotations

import random
from datetime import date, datetime
from typing import Optional


class ClozeEngine:
    """Generate and evaluate cloze (gap-fill) exercises."""

    def __init__(self, db, sentence_engine):
        self.db = db
        self.sentence_engine = sentence_engine

    def get_session_items(self, lang_id: str, count: int = 10,
                          difficulty: str = "mixed") -> list[dict]:
        """Get a batch of mixed cloze items for a session."""
        items = []

        # Try sentence-based clozes
        sentence_items = self._generate_sentence_clozes(lang_id, count, difficulty)
        items.extend(sentence_items)

        # Fill remaining with word-in-context clozes
        remaining = count - len(items)
        if remaining > 0:
            context_items = self._generate_context_clozes(lang_id, remaining, difficulty)
            items.extend(context_items)

        random.shuffle(items)
        return items[:count]

    def _generate_sentence_clozes(self, lang_id: str, count: int,
                                   difficulty: str) -> list[dict]:
        """Generate cloze items from sentence templates."""
        # Get learned words for this language
        learned_words = self._get_learned_words(lang_id)
        if not learned_words:
            return []

        items = []
        sentences = self.sentence_engine.get_all_sentences()
        if not sentences:
            return []

        random.shuffle(sentences)

        for sentence in sentences[:count * 3]:
            translations = sentence.get("translations", {})
            lang_trans = translations.get(lang_id, {})
            if not lang_trans:
                continue

            sentence_text = lang_trans.get("text", "")
            if not sentence_text:
                continue

            # Try to find a learned word in this sentence
            for word_data in learned_words:
                word = word_data["word"]
                if self._word_in_sentence(word, sentence_text, lang_id):
                    blanked = self._blank_word(sentence_text, word, lang_id)
                    if blanked == sentence_text:
                        continue

                    # Generate distractors
                    distractors = self._get_distractors(word_data, lang_id, 3)

                    item = {
                        "type": "sentence_cloze",
                        "sentence": blanked,
                        "full_sentence": sentence_text,
                        "expected": word,
                        "expected_romanization": word_data.get("romanization", ""),
                        "meaning_de": word_data.get("meaning_de", ""),
                        "german_ref": sentence.get("de", ""),
                        "word_id": word_data["id"],
                        "distractors": distractors,
                        "difficulty": difficulty,
                        "lang_id": lang_id,
                    }
                    items.append(item)
                    break

            if len(items) >= count:
                break

        return items

    def _generate_context_clozes(self, lang_id: str, count: int,
                                  difficulty: str) -> list[dict]:
        """Generate simple context cloze items (word in short phrase)."""
        learned_words = self._get_learned_words(lang_id)
        if not learned_words:
            return []

        random.shuffle(learned_words)
        items = []

        for word_data in learned_words[:count * 2]:
            word = word_data["word"]
            meaning = word_data.get("meaning_de", "")

            # Create a simple context hint
            context = f"___ ({meaning})"
            distractors = self._get_distractors(word_data, lang_id, 3)

            item = {
                "type": "word_context_cloze",
                "sentence": context,
                "full_sentence": word,
                "expected": word,
                "expected_romanization": word_data.get("romanization", ""),
                "meaning_de": meaning,
                "german_ref": meaning,
                "word_id": word_data["id"],
                "distractors": distractors,
                "difficulty": difficulty,
                "lang_id": lang_id,
            }
            items.append(item)

            if len(items) >= count:
                break

        return items

    def _get_learned_words(self, lang_id: str) -> list[dict]:
        """Get words that have been learned (have review cards)."""
        from utils.word_fetch import get_learned_words
        return get_learned_words(self.db, lang_id)

    def _word_in_sentence(self, word: str, sentence: str, lang_id: str) -> bool:
        """Check if a word appears in a sentence (script-aware)."""
        # CJK languages: no spaces, use substring match
        if lang_id in ("zh", "ja", "ko"):
            return word in sentence
        # Other languages: word boundary match
        sentence_lower = sentence.lower()
        word_lower = word.lower()
        words_in_sentence = sentence_lower.replace(",", " ").replace(".", " ").split()
        return word_lower in words_in_sentence

    def _blank_word(self, sentence: str, word: str, lang_id: str) -> str:
        """Replace the word in the sentence with ___."""
        if lang_id in ("zh", "ja", "ko"):
            return sentence.replace(word, "___", 1)
        # For space-separated languages
        import re
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        return pattern.sub("___", sentence, count=1)

    def _get_distractors(self, correct_word: dict, lang_id: str,
                          count: int = 3) -> list[str]:
        """Get distractor words from same language and category."""
        rows = self.db.conn.execute(
            """SELECT word FROM words
               WHERE language_id = ? AND id != ?
               AND category = ?
               ORDER BY RANDOM() LIMIT ?""",
            (lang_id, correct_word["id"],
             correct_word.get("category", ""), count),
        ).fetchall()

        distractors = [r["word"] for r in rows]

        # Fill if not enough
        if len(distractors) < count:
            extra = self.db.conn.execute(
                """SELECT word FROM words
                   WHERE language_id = ? AND id != ?
                   ORDER BY RANDOM() LIMIT ?""",
                (lang_id, correct_word["id"], count - len(distractors)),
            ).fetchall()
            distractors.extend(r["word"] for r in extra)

        return distractors[:count]

    def check_cloze_answer(self, user_input: str, expected: str,
                            alt_romanization: str = "") -> bool:
        """Check answer with fuzzy matching, accept romanization."""
        from utils.answer_check import check_answer
        return check_answer(user_input, expected, alt_romanization=alt_romanization)

    def process_cloze_result(self, word_id: int, correct: bool,
                              cloze_type: str = "sentence",
                              difficulty: str = "mixed",
                              sentence_template_id: str = ""):
        """Record cloze result and update tracking."""
        today = date.today().isoformat()

        # Check if record exists
        row = self.db.conn.execute(
            """SELECT * FROM cloze_performance
               WHERE word_id = ? AND cloze_type = ?""",
            (word_id, cloze_type),
        ).fetchone()

        if row:
            self.db.conn.execute(
                """UPDATE cloze_performance
                   SET attempts = attempts + 1,
                       correct = correct + ?,
                       last_attempted = ?
                   WHERE id = ?""",
                (1 if correct else 0, today, row["id"]),
            )
        else:
            self.db.conn.execute(
                """INSERT INTO cloze_performance
                   (word_id, sentence_template_id, cloze_type, difficulty,
                    attempts, correct, last_attempted)
                   VALUES (?, ?, ?, ?, 1, ?, ?)""",
                (word_id, sentence_template_id, cloze_type, difficulty,
                 1 if correct else 0, today),
            )
        self.db.conn.commit()
