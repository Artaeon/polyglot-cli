"""Quiz engine — multiple choice, typing, reverse, and cluster quiz modes."""

from __future__ import annotations

import random
from typing import Optional

from engines.srs import review_card


class QuizEngine:
    """Manages quiz sessions with different modes."""

    def __init__(self, db, cluster_engine):
        self.db = db
        self.cluster = cluster_engine

    def get_distractors(self, correct_word: dict, count: int = 3) -> list[dict]:
        """Get random wrong answers from the same language and category."""
        lang_id = correct_word["language_id"]
        all_words = self.db.get_words_by_language(lang_id)
        candidates = [
            w for w in all_words
            if w["id"] != correct_word["word_id"]
            and w["meaning_de"] != correct_word["meaning_de"]
        ]
        if len(candidates) < count:
            # Fallback: get from any language
            other = self.db.conn.execute(
                """SELECT DISTINCT meaning_de FROM words
                   WHERE meaning_de != ? AND language_id = ?
                   ORDER BY RANDOM() LIMIT ?""",
                (correct_word["meaning_de"], lang_id, count),
            ).fetchall()
            candidates = [{"meaning_de": r["meaning_de"]} for r in other]

        selected = random.sample(candidates, min(count, len(candidates)))
        return selected

    def prepare_recognition_card(self, card: dict) -> dict:
        """Prepare a multiple-choice recognition quiz card."""
        distractors = self.get_distractors(card)
        options = [{"text": card["meaning_de"], "correct": True}]
        for d in distractors:
            options.append({"text": d["meaning_de"], "correct": False})
        random.shuffle(options)

        display_word = card["word"]
        if card.get("romanization"):
            display_word += f" ({card['romanization']})"

        return {
            "mode": "recognition",
            "card": card,
            "question": display_word,
            "options": options,
            "lang_name": card.get("lang_name", ""),
            "flag": card.get("flag", ""),
        }

    def prepare_recall_card(self, card: dict) -> dict:
        """Prepare a typing recall quiz card."""
        display_meaning = card["meaning_de"]
        expected = card["word"].lower().strip()
        alt_expected = card.get("romanization", "").lower().strip() if card.get("romanization") else None

        return {
            "mode": "recall",
            "card": card,
            "question": display_meaning,
            "expected": expected,
            "alt_expected": alt_expected,
            "lang_name": card.get("lang_name", ""),
            "flag": card.get("flag", ""),
        }

    def prepare_reverse_card(self, card: dict) -> dict:
        """Prepare a reverse quiz card (target → German)."""
        display_word = card["word"]
        if card.get("romanization"):
            display_word += f" ({card['romanization']})"

        return {
            "mode": "reverse",
            "card": card,
            "question": display_word,
            "expected": card["meaning_de"].lower().strip(),
            "lang_name": card.get("lang_name", ""),
            "flag": card.get("flag", ""),
        }

    def prepare_cluster_card(self, concept: dict) -> Optional[dict]:
        """Prepare a cluster quiz card."""
        if not concept:
            return None

        translations = concept.get("translations", {})
        if not translations:
            return None

        # Collect example words from a family
        examples = []
        for lid, t in translations.items():
            word = t.get("word", "")
            rom = t.get("romanization", "")
            if word:
                display = f"{word}"
                if rom:
                    display += f" ({rom})"
                examples.append(display)
            if len(examples) >= 3:
                break

        question_text = " / ".join(examples)
        correct = concept.get("de", "")

        # Generate distractors from other concepts
        all_concepts = self.cluster.cognates.get("concepts", [])
        other_concepts = [c for c in all_concepts if c["id"] != concept["id"]]
        distractors = random.sample(
            other_concepts, min(3, len(other_concepts))
        )

        options = [{"text": correct, "correct": True}]
        for d in distractors:
            options.append({"text": d.get("de", d["id"]), "correct": False})
        random.shuffle(options)

        return {
            "mode": "cluster",
            "concept": concept,
            "question": question_text,
            "options": options,
        }

    def check_answer(self, user_input: str, expected: str,
                     alt_expected: str = None) -> bool:
        """Check if user answer matches expected (fuzzy)."""
        from utils.answer_check import check_answer
        return check_answer(user_input, expected, alt_expected=alt_expected)

    def process_review(self, card_id: int, quality: int) -> dict:
        """Process review result and return updated card info."""
        return review_card(self.db, card_id, quality)

    def get_cluster_hint(self, concept_id: str) -> list[dict]:
        """Get cluster hints for a concept after answering."""
        concept = self.cluster.find_concept(concept_id)
        if not concept:
            return []

        hints = []
        translations = concept.get("translations", {})
        languages = self.db.get_all_languages()
        lang_map = {l["id"]: l for l in languages}

        for lid, t in translations.items():
            if lid in lang_map:
                hints.append({
                    "flag": lang_map[lid]["flag"],
                    "word": t.get("word", ""),
                    "romanization": t.get("romanization", ""),
                })
        return hints
