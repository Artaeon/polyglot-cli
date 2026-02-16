"""Advanced statistics engine — retention curves, weak areas, learning velocity."""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from db.database import Database

logger = logging.getLogger(__name__)


class StatisticsEngine:
    """Advanced analytics for learning progress."""

    def __init__(self, db: Database) -> None:
        self.db = db

    def retention_curve(self, days: int = 30) -> list[dict]:
        """Daily retention rate (correct/total reviews) over N days."""
        results = []
        today = date.today()
        for i in range(days):
            d = (today - timedelta(days=days - 1 - i)).isoformat()
            row = self.db.conn.execute(
                """SELECT COUNT(*) as total,
                          SUM(CASE WHEN correct_reviews > 0 THEN 1 ELSE 0 END) as correct
                   FROM review_cards
                   WHERE last_review_date = ?""",
                (d,),
            ).fetchone()
            total = row["total"] if row else 0
            correct = (row["correct"] or 0) if row else 0
            rate = round(correct / max(total, 1) * 100)
            results.append({"date": d, "total": total, "correct": correct, "rate": rate})
        return results

    def forgetting_curve(self) -> list[dict]:
        """Accuracy grouped by review interval length."""
        rows = self.db.conn.execute(
            """SELECT interval,
                      COUNT(*) as count,
                      AVG(CASE WHEN correct_reviews > 0
                          THEN CAST(correct_reviews AS REAL) / NULLIF(total_reviews, 0)
                          ELSE 0 END) as avg_accuracy
               FROM review_cards
               WHERE total_reviews > 0
               GROUP BY interval
               ORDER BY interval"""
        ).fetchall()
        return [
            {
                "interval": r["interval"],
                "count": r["count"],
                "accuracy": round((r["avg_accuracy"] or 0) * 100),
            }
            for r in rows
        ]

    def weak_areas(self, limit: int = 20) -> list[dict]:
        """Words with lowest ease factor (hardest to remember)."""
        rows = self.db.conn.execute(
            """SELECT rc.ease_factor, rc.total_reviews, rc.correct_reviews,
                      w.word, w.romanization, w.meaning_de,
                      w.language_id, w.category,
                      l.flag, l.name as lang_name
               FROM review_cards rc
               JOIN words w ON rc.word_id = w.id
               JOIN languages l ON w.language_id = l.id
               WHERE rc.total_reviews >= 2
               ORDER BY rc.ease_factor ASC
               LIMIT ?""",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]

    def learning_velocity(self, days: int = 30) -> dict:
        """Words learned per day with trend analysis."""
        today = date.today()
        daily_counts: list[dict] = []

        for i in range(days):
            d = (today - timedelta(days=days - 1 - i)).isoformat()
            row = self.db.conn.execute(
                """SELECT COUNT(*) as cnt FROM review_cards
                   WHERE DATE(created_at) = ?""",
                (d,),
            ).fetchone()
            daily_counts.append({"date": d, "count": row["cnt"] if row else 0})

        counts = [d["count"] for d in daily_counts]
        total = sum(counts)
        avg = round(total / max(days, 1), 1)

        # Simple trend: compare last 7 days to previous 7 days
        recent = sum(counts[-7:])
        previous = sum(counts[-14:-7]) if len(counts) >= 14 else sum(counts[:7])
        if previous > 0:
            trend_pct = round((recent - previous) / previous * 100)
        else:
            trend_pct = 0

        return {
            "daily_counts": daily_counts,
            "total": total,
            "average_per_day": avg,
            "trend_pct": trend_pct,
            "trend": "up" if trend_pct > 5 else ("down" if trend_pct < -5 else "stable"),
        }

    def category_breakdown(self) -> list[dict]:
        """Performance breakdown by word category."""
        rows = self.db.conn.execute(
            """SELECT w.category,
                      COUNT(*) as total_words,
                      AVG(rc.ease_factor) as avg_ease,
                      SUM(rc.correct_reviews) as total_correct,
                      SUM(rc.total_reviews) as total_reviews
               FROM review_cards rc
               JOIN words w ON rc.word_id = w.id
               GROUP BY w.category
               ORDER BY avg_ease ASC"""
        ).fetchall()
        return [
            {
                "category": r["category"],
                "total_words": r["total_words"],
                "avg_ease": round(r["avg_ease"] or 0, 2),
                "accuracy": round(
                    (r["total_correct"] or 0) / max(r["total_reviews"] or 1, 1) * 100
                ),
            }
            for r in rows
        ]

    def language_comparison(self) -> list[dict]:
        """Cross-language progress comparison table."""
        rows = self.db.conn.execute(
            """SELECT l.id, l.name, l.flag, l.family,
                      COUNT(rc.id) as learned,
                      (SELECT COUNT(*) FROM words w2 WHERE w2.language_id = l.id) as total,
                      AVG(rc.ease_factor) as avg_ease,
                      SUM(rc.correct_reviews) as correct,
                      SUM(rc.total_reviews) as reviews
               FROM languages l
               LEFT JOIN words w ON l.id = w.language_id
               LEFT JOIN review_cards rc ON w.id = rc.word_id
               GROUP BY l.id
               HAVING learned > 0
               ORDER BY learned DESC"""
        ).fetchall()
        return [
            {
                "id": r["id"],
                "name": r["name"],
                "flag": r["flag"],
                "family": r["family"],
                "learned": r["learned"],
                "total": r["total"],
                "pct": round(r["learned"] / max(r["total"], 1) * 100),
                "avg_ease": round(r["avg_ease"] or 0, 2),
                "accuracy": round(
                    (r["correct"] or 0) / max(r["reviews"] or 1, 1) * 100
                ),
            }
            for r in rows
        ]

    def session_stats(self, days: int = 30) -> dict:
        """Session statistics over N days."""
        cutoff = (date.today() - timedelta(days=days)).isoformat()
        rows = self.db.conn.execute(
            """SELECT COUNT(*) as sessions,
                      COALESCE(SUM(duration_minutes), 0) as total_minutes,
                      COALESCE(SUM(words_learned), 0) as words_learned,
                      COALESCE(SUM(words_reviewed), 0) as words_reviewed
               FROM sessions
               WHERE date >= ?""",
            (cutoff,),
        ).fetchone()
        return dict(rows) if rows else {}
