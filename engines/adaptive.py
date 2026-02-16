"""Adaptive difficulty engine — adjusts exercise difficulty based on performance."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from db.database import Database

logger = logging.getLogger(__name__)

# Difficulty scale
MIN_DIFFICULTY = 0.5
MAX_DIFFICULTY = 5.0
DEFAULT_DIFFICULTY = 1.0

# Thresholds
CORRECT_STREAK_TO_INCREASE = 5
WRONG_STREAK_TO_DECREASE = 3

# Adjustment amounts
DIFFICULTY_INCREASE = 0.3
DIFFICULTY_DECREASE = 0.5


class AdaptiveDifficultyEngine:
    """Manages per-language, per-engine difficulty profiles."""

    def __init__(self, db: Database) -> None:
        self.db = db

    def get_difficulty(self, language_id: str, engine_type: str) -> float:
        """Get current difficulty level for a language+engine pair."""
        row = self.db.conn.execute(
            """SELECT current_difficulty FROM difficulty_profile
               WHERE language_id = ? AND engine_type = ?""",
            (language_id, engine_type),
        ).fetchone()
        return row["current_difficulty"] if row else DEFAULT_DIFFICULTY

    def record_attempt(self, language_id: str, engine_type: str,
                       correct: bool) -> dict:
        """Record an attempt and adjust difficulty accordingly.

        Returns dict with new difficulty and whether it changed.
        """
        row = self.db.conn.execute(
            """SELECT * FROM difficulty_profile
               WHERE language_id = ? AND engine_type = ?""",
            (language_id, engine_type),
        ).fetchone()

        now = datetime.now().isoformat()

        if not row:
            # Create profile
            self.db.conn.execute(
                """INSERT INTO difficulty_profile
                   (language_id, engine_type, current_difficulty,
                    consecutive_correct, consecutive_wrong,
                    total_attempts, last_updated)
                   VALUES (?, ?, ?, ?, ?, 1, ?)""",
                (language_id, engine_type, DEFAULT_DIFFICULTY,
                 1 if correct else 0, 0 if correct else 1, now),
            )
            self.db.conn.commit()
            return {
                "difficulty": DEFAULT_DIFFICULTY,
                "changed": False,
                "direction": None,
            }

        profile = dict(row)
        old_diff = profile["current_difficulty"]

        if correct:
            cons_correct = profile["consecutive_correct"] + 1
            cons_wrong = 0
        else:
            cons_correct = 0
            cons_wrong = profile["consecutive_wrong"] + 1

        new_diff = old_diff
        direction = None

        # Increase difficulty after streak of correct answers
        if cons_correct >= CORRECT_STREAK_TO_INCREASE:
            new_diff = min(MAX_DIFFICULTY, old_diff + DIFFICULTY_INCREASE)
            cons_correct = 0
            direction = "up"

        # Decrease difficulty after streak of wrong answers
        if cons_wrong >= WRONG_STREAK_TO_DECREASE:
            new_diff = max(MIN_DIFFICULTY, old_diff - DIFFICULTY_DECREASE)
            cons_wrong = 0
            direction = "down"

        self.db.conn.execute(
            """UPDATE difficulty_profile
               SET current_difficulty = ?,
                   consecutive_correct = ?,
                   consecutive_wrong = ?,
                   total_attempts = total_attempts + 1,
                   last_updated = ?
               WHERE id = ?""",
            (new_diff, cons_correct, cons_wrong, now, profile["id"]),
        )
        self.db.conn.commit()

        return {
            "difficulty": new_diff,
            "changed": new_diff != old_diff,
            "direction": direction,
        }

    def get_all_profiles(self, language_id: str | None = None) -> list[dict]:
        """Get all difficulty profiles, optionally filtered by language."""
        if language_id:
            rows = self.db.conn.execute(
                """SELECT * FROM difficulty_profile
                   WHERE language_id = ?
                   ORDER BY engine_type""",
                (language_id,),
            ).fetchall()
        else:
            rows = self.db.conn.execute(
                "SELECT * FROM difficulty_profile ORDER BY language_id, engine_type"
            ).fetchall()
        return [dict(r) for r in rows]

    def get_distractor_count(self, difficulty: float) -> int:
        """Scale distractor count with difficulty."""
        if difficulty < 1.5:
            return 3
        elif difficulty < 3.0:
            return 4
        else:
            return 5

    def get_time_pressure(self, base_ms: int, difficulty: float) -> int:
        """Scale time limit with difficulty."""
        factor = max(0.4, 1.0 - (difficulty - 1.0) * 0.15)
        return max(1500, int(base_ms * factor))
