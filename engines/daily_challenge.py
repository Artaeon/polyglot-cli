"""Daily challenge engine — deterministic daily exercises with XP rewards."""

from __future__ import annotations

import hashlib
import json
import logging
import random
from datetime import date, datetime
from typing import TYPE_CHECKING

from config import DAILY_CHALLENGE_BASE_XP, DAILY_CHALLENGE_PERFECT_MULTIPLIER

if TYPE_CHECKING:
    from db.database import Database
    from engines.gamification import GamificationEngine

logger = logging.getLogger(__name__)

CHALLENGE_TYPES = [
    "vocab_blitz",
    "conjugation_drill",
    "cluster_quiz",
    "sentence_builder",
    "speed_round",
    "mixed_review",
    "polyglot_test",
]


class DailyChallengeEngine:
    """Generates and manages daily challenges."""

    def __init__(self, db: Database, gamification: GamificationEngine) -> None:
        self.db = db
        self.gamification = gamification

    def _date_seed(self, d: date | None = None) -> int:
        """Deterministic seed from date."""
        d = d or date.today()
        h = hashlib.md5(d.isoformat().encode()).hexdigest()
        return int(h[:8], 16)

    def get_today_challenge(self) -> dict:
        """Get or create today's challenge."""
        today = date.today().isoformat()

        row = self.db.conn.execute(
            "SELECT * FROM daily_challenges WHERE challenge_date = ?",
            (today,),
        ).fetchone()

        if row:
            return dict(row)

        # Create new challenge
        seed = self._date_seed()
        rng = random.Random(seed)
        challenge_type = rng.choice(CHALLENGE_TYPES)

        data = self._generate_challenge_data(challenge_type, rng)

        self.db.conn.execute(
            """INSERT INTO daily_challenges
               (challenge_date, challenge_type, data_json, max_score)
               VALUES (?, ?, ?, ?)""",
            (today, challenge_type, json.dumps(data), data.get("max_score", 10)),
        )
        self.db.conn.commit()

        return {
            "challenge_date": today,
            "challenge_type": challenge_type,
            "data_json": json.dumps(data),
            "completed": 0,
            "score": 0,
            "max_score": data.get("max_score", 10),
            "xp_earned": 0,
        }

    def _generate_challenge_data(self, challenge_type: str,
                                  rng: random.Random) -> dict:
        """Generate challenge parameters based on type."""
        data: dict = {"type": challenge_type, "max_score": 10}

        if challenge_type == "vocab_blitz":
            data["count"] = 10
            data["time_limit"] = 120
            data["description_de"] = "Uebersetze 10 Woerter in 2 Minuten!"
        elif challenge_type == "conjugation_drill":
            data["count"] = 8
            data["description_de"] = "Konjugiere 8 Verben richtig!"
        elif challenge_type == "cluster_quiz":
            data["count"] = 5
            data["description_de"] = "Erkenne 5 Wort-Cluster!"
        elif challenge_type == "sentence_builder":
            data["count"] = 5
            data["max_score"] = 5
            data["description_de"] = "Baue 5 Saetze korrekt!"
        elif challenge_type == "speed_round":
            data["count"] = 15
            data["time_limit"] = 90
            data["max_score"] = 15
            data["description_de"] = "Speed-Runde: 15 Woerter, 90 Sekunden!"
        elif challenge_type == "mixed_review":
            data["count"] = 10
            data["description_de"] = "Gemischte Uebungen aus allen Modi!"
        elif challenge_type == "polyglot_test":
            data["count"] = 10
            data["max_score"] = 10
            data["description_de"] = "Teste dein Wissen in mehreren Sprachen!"

        return data

    def complete_challenge(self, score: int) -> dict:
        """Mark today's challenge as complete, award XP."""
        today = date.today().isoformat()
        challenge = self.get_today_challenge()

        if challenge.get("completed"):
            return {"already_completed": True, "xp_earned": 0}

        max_score = challenge.get("max_score", 10)
        pct = score / max(max_score, 1)

        # XP: base 50-150, 2x for perfect
        base_xp = round(DAILY_CHALLENGE_BASE_XP + (pct * 100))
        if score >= max_score:
            base_xp *= DAILY_CHALLENGE_PERFECT_MULTIPLIER

        self.db.conn.execute(
            """UPDATE daily_challenges
               SET completed = 1, score = ?, xp_earned = ?,
                   completed_at = ?
               WHERE challenge_date = ?""",
            (score, base_xp, datetime.now().isoformat(), today),
        )
        self.db.conn.commit()

        # Award XP via gamification
        self.db.conn.execute(
            """INSERT INTO xp_log
               (action_type, base_xp, quality_multiplier, streak_bonus,
                total_xp, details)
               VALUES ('daily_challenge', ?, 1.0, 1.0, ?, ?)""",
            (base_xp, base_xp, f"Daily Challenge: {challenge['challenge_type']}"),
        )
        self.db.conn.commit()

        return {
            "already_completed": False,
            "score": score,
            "max_score": max_score,
            "xp_earned": base_xp,
            "perfect": score >= max_score,
        }

    def get_today_status(self) -> dict:
        """Get today's challenge status for dashboard display."""
        today = date.today().isoformat()
        row = self.db.conn.execute(
            "SELECT * FROM daily_challenges WHERE challenge_date = ?",
            (today,),
        ).fetchone()

        if not row:
            return {"available": True, "completed": False}

        d = dict(row)
        return {
            "available": True,
            "completed": bool(d.get("completed")),
            "challenge_type": d.get("challenge_type", ""),
            "score": d.get("score", 0),
            "max_score": d.get("max_score", 0),
            "xp_earned": d.get("xp_earned", 0),
        }

    def get_challenge_history(self, limit: int = 30) -> list[dict]:
        """Get recent challenge history."""
        rows = self.db.conn.execute(
            """SELECT * FROM daily_challenges
               WHERE completed = 1
               ORDER BY challenge_date DESC LIMIT ?""",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_streak(self) -> int:
        """Count consecutive days with completed challenges."""
        rows = self.db.conn.execute(
            """SELECT challenge_date FROM daily_challenges
               WHERE completed = 1
               ORDER BY challenge_date DESC"""
        ).fetchall()
        if not rows:
            return 0

        from datetime import timedelta
        dates = [date.fromisoformat(r["challenge_date"]) for r in rows]
        today = date.today()

        if dates[0] != today and dates[0] != today - timedelta(days=1):
            return 0

        streak = 1
        for i in range(len(dates) - 1):
            if (dates[i] - dates[i + 1]).days == 1:
                streak += 1
            else:
                break
        return streak
