"""Daily plan generator and progress tracker."""

from __future__ import annotations

from datetime import date
from typing import Optional

from config import CEFR_LEVELS, DEFAULT_NEW_WORDS_PER_SESSION


class PlannerEngine:
    """Generates daily learning plans and tracks progress."""

    def __init__(self, db, cluster_engine):
        self.db = db
        self.cluster = cluster_engine

    def get_cefr_level(self, word_count: int) -> str:
        """Determine CEFR level from word count."""
        for level, (low, high) in CEFR_LEVELS.items():
            if low <= word_count <= high:
                return level
        return "B1-"

    def get_progress_by_language(self) -> list[dict]:
        """Get progress for all languages."""
        languages = self.db.get_all_languages()
        learned = self.db.get_learned_count_by_language()
        word_counts = self.db.get_word_count_by_language()
        due_counts = self.db.get_due_count_by_language()

        progress = []
        for lang in languages:
            lid = lang["id"]
            count = learned.get(lid, 0)
            total = word_counts.get(lid, 0)
            due = due_counts.get(lid, 0)
            level = self.get_cefr_level(count)

            progress.append({
                "id": lid,
                "name": lang["name"],
                "flag": lang["flag"],
                "family": lang["family"],
                "subfamily": lang.get("subfamily", ""),
                "learned": count,
                "total": total,
                "due": due,
                "level": level,
                "difficulty_tier": lang["difficulty_tier"],
            })

        return progress

    def get_daily_plan(self) -> dict:
        """Generate today's learning plan."""
        sprint_day = self.db.get_sprint_day()
        daily_minutes = int(self.db.get_setting("daily_minutes", "90"))
        progress = self.get_progress_by_language()
        due_counts = self.db.get_due_count_by_language()
        total_due = sum(due_counts.values())

        # Determine focus language based on sprint week
        week = (sprint_day - 1) // 7 + 1
        focus = self._get_focus_languages(week, progress)
        recommended_cefr = self.get_recommended_cefr_target(progress, focus)

        # Word of the day
        wotd = self.cluster.get_word_of_the_day()

        return {
            "sprint_day": sprint_day,
            "week": week,
            "daily_minutes": daily_minutes,
            "total_due": total_due,
            "due_by_language": due_counts,
            "focus_languages": focus,
            "recommended_cefr": recommended_cefr,
            "recommended_new_words": DEFAULT_NEW_WORDS_PER_SESSION,
            "word_of_the_day": wotd,
            "progress": progress,
        }

    def get_recommended_cefr_target(
        self,
        progress: list[dict] | None = None,
        focus_languages: list[dict] | None = None,
    ) -> str:
        """Recommend a CEFR band for phrase-heavy drills.

        Uses average learned word count of current focus languages.
        """
        progress = progress or self.get_progress_by_language()
        focus_languages = focus_languages or []

        if focus_languages:
            values = [f.get("learned", 0) for f in focus_languages]
        else:
            values = [p.get("learned", 0) for p in progress]

        avg_learned = sum(values) / max(len(values), 1)

        if avg_learned < 120:
            return "A1"
        if avg_learned < 280:
            return "A1+"
        if avg_learned < 500:
            return "A2-"
        if avg_learned < 750:
            return "A2"
        if avg_learned < 1000:
            return "A2+"
        return "B1-"

    def _get_focus_languages(self, week: int,
                              progress: list[dict]) -> list[dict]:
        """Determine focus languages for the current week."""
        # Week-based focus schedule
        schedules = {
            1: {"primary": ["ru"], "secondary": ["zh", "hu"],
                "note": "Russisch intensiv + Chinesisch & Ungarisch Intro"},
            2: {"primary": ["sk"], "secondary": ["ru", "zh", "it"],
                "note": "Slowakisch Fokus (Russisch als Brücke)"},
            3: {"primary": ["bg", "sl"], "secondary": ["ru", "sk", "zh", "it"],
                "note": "Bulgarisch + Slowenisch Rotation"},
            4: {"primary": ["uk", "be", "cs", "es", "pt"],
                "secondary": ["fi", "et", "mk", "ko", "ja", "vi"],
                "note": "Konsolidierung + Transfer-Sprachen"},
        }
        if week > 4:
            week = 4  # Repeat week 4 pattern

        schedule = schedules.get(week, schedules[4])

        focus = []
        prog_map = {p["id"]: p for p in progress}
        for lid in schedule["primary"]:
            if lid in prog_map:
                entry = prog_map[lid].copy()
                entry["priority"] = "primary"
                focus.append(entry)
        for lid in schedule["secondary"]:
            if lid in prog_map:
                entry = prog_map[lid].copy()
                entry["priority"] = "secondary"
                focus.append(entry)

        return focus

    def get_sprint_summary(self) -> dict:
        """Get overall sprint progress summary."""
        sprint_day = self.db.get_sprint_day()
        sprint_days = int(self.db.get_setting("sprint_days", "30"))
        streak = self.db.get_streak()
        time_today = self.db.get_total_time_today()
        total_learned = self.db.get_total_learned()
        cluster_eff = self.cluster.get_cluster_efficiency()

        return {
            "sprint_day": sprint_day,
            "sprint_days": sprint_days,
            "streak": streak,
            "time_today": time_today,
            "total_learned": total_learned,
            "cluster_efficiency": cluster_eff,
        }

    def get_review_forecast(self, days: int = 7) -> dict[str, int]:
        """Forecast how many cards will be due each day this week."""
        from datetime import timedelta
        forecast = {}
        for i in range(days):
            d = (date.today() + timedelta(days=i)).isoformat()
            row = self.db.conn.execute(
                """SELECT COUNT(*) as cnt FROM review_cards
                   WHERE next_review_date = ?""",
                (d,),
            ).fetchone()
            forecast[d] = row["cnt"] if row else 0
        return forecast

    def get_weakest_language(self) -> Optional[dict]:
        """Find language with lowest retention rate."""
        rows = self.db.conn.execute(
            """SELECT w.language_id, l.name, l.flag,
                      SUM(rc.correct_reviews) as correct,
                      SUM(rc.total_reviews) as total
               FROM review_cards rc
               JOIN words w ON rc.word_id = w.id
               JOIN languages l ON w.language_id = l.id
               WHERE rc.total_reviews > 0
               GROUP BY w.language_id
               ORDER BY (CAST(SUM(rc.correct_reviews) AS REAL) /
                        SUM(rc.total_reviews))
               LIMIT 1"""
        ).fetchone()
        if row:
            return {
                "id": row["language_id"],
                "name": row["name"],
                "flag": row["flag"],
                "retention": round(row["correct"] / max(row["total"], 1) * 100),
            }
        return None

    def get_fastest_growing(self) -> Optional[dict]:
        """Find language with most words added in last 7 days."""
        from datetime import timedelta
        week_ago = (date.today() - timedelta(days=7)).isoformat()
        row = self.db.conn.execute(
            """SELECT w.language_id, l.name, l.flag, COUNT(*) as cnt
               FROM review_cards rc
               JOIN words w ON rc.word_id = w.id
               JOIN languages l ON w.language_id = l.id
               WHERE rc.created_at >= ?
               GROUP BY w.language_id
               ORDER BY cnt DESC
               LIMIT 1""",
            (week_ago,),
        ).fetchone()
        if row:
            return {
                "id": row["language_id"],
                "name": row["name"],
                "flag": row["flag"],
                "new_words": row["cnt"],
            }
        return None
