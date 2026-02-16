"""CIA intensive drill engine — timed, high-pressure language exercises."""

from __future__ import annotations

import json
import random
import time
from datetime import datetime
from typing import Optional


class CIADrillEngine:
    """CIA-style intensive drills: shadowing, rapid association,
    context switching, pattern recognition, immersion, back-translation."""

    def __init__(self, db, cluster_engine, quiz_engine):
        self.db = db
        self.cluster_engine = cluster_engine
        self.quiz_engine = quiz_engine

    # ── 1. Shadowing ────────────────────────────────────────────

    def prepare_shadowing_round(self, lang_id: str,
                                 exposure_seconds: float = 3.0,
                                 count: int = 10) -> list[dict]:
        """Prepare words for shadowing drill: see, disappear, type from memory."""
        cards = self._get_learned_cards(lang_id, count)
        items = []
        for card in cards:
            items.append({
                "type": "shadowing",
                "word": card["word"],
                "romanization": card.get("romanization", ""),
                "meaning_de": card["meaning_de"],
                "exposure_seconds": exposure_seconds,
                "word_id": card.get("word_id", card.get("id")),
                "lang_id": lang_id,
            })
        return items

    # ── 2. Rapid Word Association ───────────────────────────────

    def prepare_rapid_association(self, lang_ids: list[str],
                                   time_limit_ms: int = 5000,
                                   count: int = 20) -> list[dict]:
        """Translate before timer expires, adaptive speed."""
        items = []
        cards = self._get_multi_lang_cards(lang_ids, count)
        for i, card in enumerate(cards):
            # Adaptive: max(2000, base_ms * (1.0 - round * 0.03))
            adaptive_ms = max(2000, int(time_limit_ms * (1.0 - i * 0.03)))
            items.append({
                "type": "rapid_association",
                "word": card["word"],
                "romanization": card.get("romanization", ""),
                "meaning_de": card["meaning_de"],
                "language_id": card["language_id"],
                "flag": card.get("flag", ""),
                "lang_name": card.get("lang_name", ""),
                "time_limit_ms": adaptive_ms,
                "word_id": card.get("word_id", card.get("id")),
            })
        return items

    # ── 3. Context Switching ────────────────────────────────────

    def prepare_context_switch(self, lang_ids: list[str],
                                count: int = 15) -> list[dict]:
        """Same concept across languages, rapid switching."""
        items = []
        # Get concepts that have words in multiple selected languages
        concepts = self.db.get_all_concepts()
        random.shuffle(concepts)

        for concept in concepts:
            if len(items) >= count:
                break
            concept_words = self.db.get_words_by_concept(concept["id"])
            # Filter to selected languages with review cards
            matching = []
            for w in concept_words:
                if w["language_id"] in lang_ids:
                    # Check if learned
                    has_card = self.db.conn.execute(
                        "SELECT 1 FROM review_cards WHERE word_id = ?",
                        (w["id"],),
                    ).fetchone()
                    if has_card:
                        matching.append(w)

            if len(matching) >= 2:
                # Create switching sequence
                for w in matching[:3]:
                    items.append({
                        "type": "context_switch",
                        "word": w["word"],
                        "romanization": w.get("romanization", ""),
                        "meaning_de": concept.get("meaning_de", ""),
                        "meaning_en": concept.get("meaning_en", ""),
                        "language_id": w["language_id"],
                        "flag": w.get("flag", ""),
                        "lang_name": w.get("lang_name", ""),
                        "concept_id": concept["id"],
                        "word_id": w["id"],
                    })

        return items[:count]

    # ── 4. Pattern Recognition ──────────────────────────────────

    def prepare_pattern_drill(self, lang_id: str,
                               count: int = 5) -> list[dict]:
        """Show examples, user applies pattern to new input."""
        cards = self._get_learned_cards(lang_id, count * 4)
        if len(cards) < 4:
            return []

        items = []
        # Group by category
        by_cat: dict[str, list] = {}
        for c in cards:
            cat = c.get("category", "")
            if cat not in by_cat:
                by_cat[cat] = []
            by_cat[cat].append(c)

        for cat, cat_cards in by_cat.items():
            if len(cat_cards) < 4 or len(items) >= count:
                continue

            random.shuffle(cat_cards)
            examples = cat_cards[:3]
            test = cat_cards[3]

            items.append({
                "type": "pattern_recognition",
                "examples": [
                    {"word": e["word"],
                     "romanization": e.get("romanization", ""),
                     "meaning_de": e["meaning_de"]}
                    for e in examples
                ],
                "test_meaning": test["meaning_de"],
                "expected": test["word"],
                "expected_romanization": test.get("romanization", ""),
                "category": cat,
                "lang_id": lang_id,
                "word_id": test.get("word_id", test.get("id")),
            })

        return items[:count]

    # ── 5. Immersion Block ──────────────────────────────────────

    def prepare_immersion_block(self, lang_id: str,
                                 count: int = 10) -> dict:
        """Prepare an immersion block where UI is in target language."""
        cards = self._get_learned_cards(lang_id, count)
        lang = self.db.get_language(lang_id)

        # Get basic feedback words if available
        feedback = self._get_immersion_feedback(lang_id)

        return {
            "type": "immersion",
            "lang_id": lang_id,
            "lang_name": lang.get("name", "") if lang else "",
            "flag": lang.get("flag", "") if lang else "",
            "cards": cards,
            "feedback": feedback,
        }

    def _get_immersion_feedback(self, lang_id: str) -> dict:
        """Get correct/incorrect feedback words in target language."""
        # Lookup common feedback words
        defaults = {
            "correct": "Richtig!",
            "incorrect": "Falsch!",
            "next": "Weiter",
        }

        feedback_map = {
            "ru": {"correct": "Правильно!", "incorrect": "Неправильно!", "next": "Далее"},
            "uk": {"correct": "Правильно!", "incorrect": "Неправильно!", "next": "Далі"},
            "es": {"correct": "¡Correcto!", "incorrect": "¡Incorrecto!", "next": "Siguiente"},
            "fr": {"correct": "Correct!", "incorrect": "Incorrect!", "next": "Suivant"},
            "it": {"correct": "Corretto!", "incorrect": "Sbagliato!", "next": "Avanti"},
            "pt": {"correct": "Correto!", "incorrect": "Incorreto!", "next": "Próximo"},
            "pl": {"correct": "Dobrze!", "incorrect": "Źle!", "next": "Dalej"},
            "cs": {"correct": "Správně!", "incorrect": "Špatně!", "next": "Dále"},
            "sk": {"correct": "Správne!", "incorrect": "Nesprávne!", "next": "Ďalej"},
            "zh": {"correct": "正确！", "incorrect": "错误！", "next": "下一个"},
            "ja": {"correct": "正解！", "incorrect": "不正解！", "next": "次へ"},
            "ko": {"correct": "정답!", "incorrect": "오답!", "next": "다음"},
            "fi": {"correct": "Oikein!", "incorrect": "Väärin!", "next": "Seuraava"},
            "hu": {"correct": "Helyes!", "incorrect": "Helytelen!", "next": "Következő"},
        }

        return feedback_map.get(lang_id, defaults)

    # ── 6. Back-Translation ─────────────────────────────────────

    def prepare_back_translation(self, lang_id: str,
                                  count: int = 10) -> list[dict]:
        """Target -> German -> Target, compare."""
        cards = self._get_learned_cards(lang_id, count)
        items = []
        for card in cards:
            items.append({
                "type": "back_translation",
                "word": card["word"],
                "romanization": card.get("romanization", ""),
                "meaning_de": card["meaning_de"],
                "language_id": lang_id,
                "word_id": card.get("word_id", card.get("id")),
            })
        return items

    # ── Session Logging ─────────────────────────────────────────

    def log_drill_session(self, drill_type: str, duration_seconds: int,
                           words_attempted: int, words_correct: int,
                           avg_response_ms: int = 0,
                           languages_used: list[str] = None,
                           difficulty_level: int = 1):
        """Log a completed drill session."""
        self.db.conn.execute(
            """INSERT INTO drill_sessions
               (drill_type, duration_seconds, words_attempted,
                words_correct, avg_response_ms, languages_used,
                difficulty_level)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (drill_type, duration_seconds, words_attempted,
             words_correct, avg_response_ms,
             json.dumps(languages_used or []), difficulty_level),
        )
        self.db.conn.commit()

    # ── Helpers ─────────────────────────────────────────────────

    def _get_learned_cards(self, lang_id: str,
                            count: int = 10) -> list[dict]:
        """Get learned words for a language."""
        from utils.word_fetch import get_learned_cards
        return get_learned_cards(self.db, lang_id, count)

    def _get_multi_lang_cards(self, lang_ids: list[str],
                               count: int = 20) -> list[dict]:
        """Get learned words across multiple languages."""
        from utils.word_fetch import get_multi_lang_cards
        return get_multi_lang_cards(self.db, lang_ids, count)
