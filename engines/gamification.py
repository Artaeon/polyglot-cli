"""Gamification engine — XP, levels, achievements."""

from __future__ import annotations

import json
import math
from datetime import date, datetime
from typing import Optional


# Achievement definitions
ACHIEVEMENT_DEFS = [
    # Word milestones
    {"id": "words_10", "category": "words", "name_de": "Erste Schritte", "name_en": "First Steps",
     "description_de": "10 Woerter gelernt", "icon": "\U0001f476", "threshold_value": 10, "xp_reward": 50},
    {"id": "words_50", "category": "words", "name_de": "Wortsammler", "name_en": "Word Collector",
     "description_de": "50 Woerter gelernt", "icon": "\U0001f4da", "threshold_value": 50, "xp_reward": 100},
    {"id": "words_100", "category": "words", "name_de": "Vokabelkenner", "name_en": "Vocabulary Builder",
     "description_de": "100 Woerter gelernt", "icon": "\U0001f3c6", "threshold_value": 100, "xp_reward": 200},
    {"id": "words_500", "category": "words", "name_de": "Wortmeister", "name_en": "Word Master",
     "description_de": "500 Woerter gelernt", "icon": "\U0001f451", "threshold_value": 500, "xp_reward": 500},
    # Streak milestones
    {"id": "streak_3", "category": "streak", "name_de": "Dranbleiber", "name_en": "Consistent",
     "description_de": "3-Tage-Streak", "icon": "\U0001f525", "threshold_value": 3, "xp_reward": 30},
    {"id": "streak_7", "category": "streak", "name_de": "Wochenkrieger", "name_en": "Week Warrior",
     "description_de": "7-Tage-Streak", "icon": "\U0001f525", "threshold_value": 7, "xp_reward": 70},
    {"id": "streak_14", "category": "streak", "name_de": "Halbmondheld", "name_en": "Fortnight Hero",
     "description_de": "14-Tage-Streak", "icon": "\U0001f525", "threshold_value": 14, "xp_reward": 150},
    {"id": "streak_30", "category": "streak", "name_de": "Monatsmacher", "name_en": "Monthly Master",
     "description_de": "30-Tage-Streak", "icon": "\U0001f525", "threshold_value": 30, "xp_reward": 300},
    # Language milestones
    {"id": "lang_1", "category": "language", "name_de": "Erstsprache", "name_en": "First Language",
     "description_de": "Erstes Wort in einer Sprache", "icon": "\U0001f1ea\U0001f1fa", "threshold_value": 1, "xp_reward": 25},
    {"id": "lang_5", "category": "language", "name_de": "Mehrsprachig", "name_en": "Multilingual",
     "description_de": "5 Sprachen begonnen", "icon": "\U0001f30d", "threshold_value": 5, "xp_reward": 100},
    {"id": "lang_10", "category": "language", "name_de": "Dekade", "name_en": "Decade",
     "description_de": "10 Sprachen begonnen", "icon": "\U0001f30d", "threshold_value": 10, "xp_reward": 250},
    {"id": "lang_22", "category": "language", "name_de": "Polyglot", "name_en": "Polyglot",
     "description_de": "Alle 22 Sprachen begonnen", "icon": "\U0001f30d", "threshold_value": 22, "xp_reward": 500},
    # Family milestones
    {"id": "family_slavic", "category": "family", "name_de": "Slawist", "name_en": "Slavist",
     "description_de": "Woerter in allen slawischen Sprachen", "icon": "\U0001f535", "threshold_value": 10, "xp_reward": 200},
    {"id": "family_romance", "category": "family", "name_de": "Romanist", "name_en": "Romanist",
     "description_de": "Woerter in allen romanischen Sprachen", "icon": "\U0001f7e2", "threshold_value": 5, "xp_reward": 150},
    {"id": "family_sino", "category": "family", "name_de": "Sinologe", "name_en": "Sinologist",
     "description_de": "Woerter in allen Sinosphaere-Sprachen", "icon": "\U0001f534", "threshold_value": 4, "xp_reward": 150},
    {"id": "family_uralic", "category": "family", "name_de": "Uralist", "name_en": "Uralist",
     "description_de": "Woerter in allen uralischen Sprachen", "icon": "\U0001f7e1", "threshold_value": 3, "xp_reward": 100},
    # Session milestones
    {"id": "perfect_session", "category": "session", "name_de": "Perfektionist", "name_en": "Perfectionist",
     "description_de": "Perfekte Review-Session (100%)", "icon": "\U0001f4af", "threshold_value": 1, "xp_reward": 50},
    {"id": "reviews_100", "category": "session", "name_de": "Review-Maschine", "name_en": "Review Machine",
     "description_de": "100 Reviews abgeschlossen", "icon": "\U0001f504", "threshold_value": 100, "xp_reward": 100},
    {"id": "reviews_500", "category": "session", "name_de": "Review-Monster", "name_en": "Review Monster",
     "description_de": "500 Reviews abgeschlossen", "icon": "\U0001f504", "threshold_value": 500, "xp_reward": 250},
    # ── New achievements (Phase 2e) ──────────────────────────────
    # Word milestones extended
    {"id": "words_250", "category": "words", "name_de": "Wortakrobat", "name_en": "Word Acrobat",
     "description_de": "250 Woerter gelernt", "icon": "\U0001f3c5", "threshold_value": 250, "xp_reward": 300},
    {"id": "words_1000", "category": "words", "name_de": "Lexikon", "name_en": "Lexicon",
     "description_de": "1000 Woerter gelernt", "icon": "\U0001f4d6", "threshold_value": 1000, "xp_reward": 1000},
    # Streak extended
    {"id": "streak_60", "category": "streak", "name_de": "Marathonlaeufer", "name_en": "Marathon Runner",
     "description_de": "60-Tage-Streak", "icon": "\U0001f525", "threshold_value": 60, "xp_reward": 500},
    {"id": "streak_100", "category": "streak", "name_de": "Unaufhaltsam", "name_en": "Unstoppable",
     "description_de": "100-Tage-Streak", "icon": "\U0001f525", "threshold_value": 100, "xp_reward": 1000},
    # XP milestones (new category)
    {"id": "xp_1000", "category": "xp", "name_de": "XP-Sammler", "name_en": "XP Collector",
     "description_de": "1.000 XP gesammelt", "icon": "\u2b50", "threshold_value": 1000, "xp_reward": 50},
    {"id": "xp_5000", "category": "xp", "name_de": "XP-Jaeger", "name_en": "XP Hunter",
     "description_de": "5.000 XP gesammelt", "icon": "\u2b50", "threshold_value": 5000, "xp_reward": 100},
    {"id": "xp_10000", "category": "xp", "name_de": "XP-Legende", "name_en": "XP Legend",
     "description_de": "10.000 XP gesammelt", "icon": "\u2b50", "threshold_value": 10000, "xp_reward": 200},
    # Daily challenge milestones (new category)
    {"id": "daily_1", "category": "daily", "name_de": "Erste Challenge", "name_en": "First Challenge",
     "description_de": "Erste Daily Challenge abgeschlossen", "icon": "\U0001f3af", "threshold_value": 1, "xp_reward": 25},
    {"id": "daily_7", "category": "daily", "name_de": "Wochen-Champion", "name_en": "Week Champion",
     "description_de": "7 Daily Challenges abgeschlossen", "icon": "\U0001f3af", "threshold_value": 7, "xp_reward": 100},
    {"id": "daily_30", "category": "daily", "name_de": "Monats-Champion", "name_en": "Month Champion",
     "description_de": "30 Daily Challenges abgeschlossen", "icon": "\U0001f3af", "threshold_value": 30, "xp_reward": 300},
    # Conjugation milestones
    {"id": "conj_first", "category": "conjugation", "name_de": "Verb-Entdecker", "name_en": "Verb Explorer",
     "description_de": "Erstes Verb konjugiert", "icon": "\U0001f4d6", "threshold_value": 1, "xp_reward": 25},
    {"id": "conj_10", "category": "conjugation", "name_de": "Verb-Meister", "name_en": "Verb Master",
     "description_de": "10 Verben gemeistert", "icon": "\U0001f4d6", "threshold_value": 10, "xp_reward": 200},
    # Builder milestones
    {"id": "builder_first", "category": "builder", "name_de": "Satz-Anfaenger", "name_en": "Sentence Beginner",
     "description_de": "Ersten Satz gebaut", "icon": "\U0001f3d7\ufe0f", "threshold_value": 1, "xp_reward": 25},
    {"id": "builder_50", "category": "builder", "name_de": "Satz-Architekt", "name_en": "Sentence Architect",
     "description_de": "50 Saetze gebaut", "icon": "\U0001f3d7\ufe0f", "threshold_value": 50, "xp_reward": 200},
    # Speed/CIA milestones
    {"id": "chain_10", "category": "speed", "name_de": "Ketten-Held", "name_en": "Chain Hero",
     "description_de": "10er Recall-Kette", "icon": "\U0001f517", "threshold_value": 10, "xp_reward": 100},
    {"id": "drill_perfect", "category": "cia", "name_de": "Perfekter Drill", "name_en": "Perfect Drill",
     "description_de": "CIA-Drill mit 100% abgeschlossen", "icon": "\U0001f575\ufe0f", "threshold_value": 1, "xp_reward": 100},
    # Custom vocab milestones
    {"id": "custom_first", "category": "custom", "name_de": "Eigenes Wort", "name_en": "Own Word",
     "description_de": "Erstes eigenes Wort hinzugefuegt", "icon": "\u270d\ufe0f", "threshold_value": 1, "xp_reward": 25},
    {"id": "custom_50", "category": "custom", "name_de": "Wort-Schmied", "name_en": "Word Smith",
     "description_de": "50 eigene Woerter hinzugefuegt", "icon": "\u270d\ufe0f", "threshold_value": 50, "xp_reward": 200},
    # Accuracy milestone
    {"id": "accuracy_90", "category": "accuracy", "name_de": "Scharfschuetze", "name_en": "Sharpshooter",
     "description_de": "90% Genauigkeit ueber 100 Reviews", "icon": "\U0001f3af", "threshold_value": 90, "xp_reward": 200},
    # Level milestones
    {"id": "level_10", "category": "level", "name_de": "Zehnter Level", "name_en": "Level Ten",
     "description_de": "Level 10 erreicht", "icon": "\U0001f31f", "threshold_value": 10, "xp_reward": 100},
    {"id": "level_25", "category": "level", "name_de": "Silber-Rang", "name_en": "Silver Rank",
     "description_de": "Level 25 erreicht", "icon": "\U0001f31f", "threshold_value": 25, "xp_reward": 300},
]

FAMILY_LANGS = {
    "slavic": ["ru", "uk", "be", "sk", "cs", "pl", "sl", "hr", "bg", "mk"],
    "romance": ["it", "es", "pt", "fr", "ro"],
    "sinosphere": ["zh", "ja", "ko", "vi"],
    "uralic": ["hu", "fi", "et"],
}


class GamificationEngine:
    """XP, levels, and achievements system."""

    def __init__(self, db):
        self.db = db
        self._init_achievements()

    def _init_achievements(self):
        """Seed achievement definitions into DB if not present."""
        for a in ACHIEVEMENT_DEFS:
            self.db.conn.execute(
                """INSERT OR IGNORE INTO achievements
                   (id, category, name_de, name_en, description_de, icon,
                    threshold_value, xp_reward)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (a["id"], a["category"], a["name_de"], a["name_en"],
                 a["description_de"], a["icon"], a["threshold_value"],
                 a["xp_reward"]),
            )
        self.db.conn.commit()

    def award_xp(self, action_type: str, quality: int = 3,
                  language_id: str = None, details: str = "") -> dict:
        """Calculate and log XP for an action. Returns XP info dict."""
        from config import XP_BASE
        base_xp = XP_BASE.get(action_type, 10)

        # Quality multiplier: 0.5 + (quality/5) * 0.5
        quality_mult = 0.5 + (min(max(quality, 0), 5) / 5) * 0.5

        # Streak bonus: 1.0 + min(streak, 30) * 0.02
        streak = self.db.get_streak()
        streak_bonus = 1.0 + min(streak, 30) * 0.02

        total_xp = round(base_xp * quality_mult * streak_bonus)

        self.db.conn.execute(
            """INSERT INTO xp_log
               (action_type, base_xp, quality_multiplier, streak_bonus,
                total_xp, language_id, details)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (action_type, base_xp, quality_mult, streak_bonus,
             total_xp, language_id, details),
        )
        self.db.conn.commit()

        # Check achievements
        newly_unlocked = self.check_achievements()

        return {
            "base_xp": base_xp,
            "quality_mult": quality_mult,
            "streak_bonus": streak_bonus,
            "total_xp": total_xp,
            "newly_unlocked": newly_unlocked,
        }

    def get_total_xp(self) -> int:
        """Get total accumulated XP."""
        row = self.db.conn.execute(
            "SELECT COALESCE(SUM(total_xp), 0) as total FROM xp_log"
        ).fetchone()
        return row["total"]

    def get_today_xp(self) -> int:
        """Get XP earned today."""
        today = date.today().isoformat()
        row = self.db.conn.execute(
            "SELECT COALESCE(SUM(total_xp), 0) as total FROM xp_log "
            "WHERE DATE(timestamp) = ?",
            (today,),
        ).fetchone()
        return row["total"]

    def get_level(self, total_xp: int = None) -> dict:
        """Return level (1-50), rank name, progress to next."""
        if total_xp is None:
            total_xp = self.get_total_xp()

        level = 1
        while level < 50:
            threshold = self._level_threshold(level + 1)
            if total_xp < threshold:
                break
            level += 1

        current_threshold = self._level_threshold(level)
        next_threshold = self._level_threshold(level + 1)
        progress = total_xp - current_threshold
        needed = next_threshold - current_threshold

        # Get rank name
        from config import RANK_NAMES
        rank = "Anfaenger"
        for min_level, name in RANK_NAMES:
            if level >= min_level:
                rank = name

        return {
            "level": level,
            "rank": rank,
            "total_xp": total_xp,
            "current_threshold": current_threshold,
            "next_threshold": next_threshold,
            "progress": progress,
            "needed": needed,
            "progress_pct": round(progress / max(needed, 1) * 100),
        }

    @staticmethod
    def _level_threshold(n: int) -> int:
        """XP threshold for level n: round(50 * n^1.5)."""
        return round(50 * (n ** 1.5))

    def check_achievements(self) -> list[dict]:
        """Check all milestone categories, return newly unlocked."""
        newly_unlocked = []

        # Word milestones
        total_learned = self.db.get_total_learned()
        newly_unlocked.extend(
            self._check_threshold("words", total_learned,
                                  ["words_10", "words_50", "words_100", "words_250",
                                   "words_500", "words_1000"])
        )

        # Streak milestones
        streak = self.db.get_streak()
        newly_unlocked.extend(
            self._check_threshold("streak", streak,
                                  ["streak_3", "streak_7", "streak_14", "streak_30",
                                   "streak_60", "streak_100"])
        )

        # Language milestones
        learned_by_lang = self.db.get_learned_count_by_language()
        langs_started = len([l for l, c in learned_by_lang.items() if c > 0])
        newly_unlocked.extend(
            self._check_threshold("language", langs_started,
                                  ["lang_1", "lang_5", "lang_10", "lang_22"])
        )

        # Family milestones
        for family_id, family_key in [
            ("family_slavic", "slavic"), ("family_romance", "romance"),
            ("family_sino", "sinosphere"), ("family_uralic", "uralic"),
        ]:
            family_langs = FAMILY_LANGS.get(family_key, [])
            langs_with_words = sum(
                1 for lang in family_langs
                if learned_by_lang.get(lang, 0) > 0
            )
            if langs_with_words >= len(family_langs):
                newly_unlocked.extend(self._unlock_if_new(family_id))

        # Review milestones
        review_stats = self.db.get_review_stats()
        total_reviews = review_stats.get("total_reviews", 0) or 0
        newly_unlocked.extend(
            self._check_threshold("session", total_reviews,
                                  ["reviews_100", "reviews_500"])
        )

        # XP milestones
        total_xp = self.get_total_xp()
        newly_unlocked.extend(
            self._check_threshold("xp", total_xp,
                                  ["xp_1000", "xp_5000", "xp_10000"])
        )

        # Level milestones
        level = self.get_level(total_xp)["level"]
        newly_unlocked.extend(
            self._check_threshold("level", level,
                                  ["level_10", "level_25"])
        )

        # Daily challenge milestones
        daily_count = self._safe_count(
            "SELECT COUNT(*) FROM daily_challenges WHERE completed = 1"
        )
        newly_unlocked.extend(
            self._check_threshold("daily", daily_count,
                                  ["daily_1", "daily_7", "daily_30"])
        )

        # Conjugation milestones
        conj_mastered = self._safe_count(
            "SELECT COUNT(DISTINCT verb_concept_id || '-' || tense) "
            "FROM conjugation_mastery WHERE mastered = 1"
        )
        newly_unlocked.extend(
            self._check_threshold("conjugation", conj_mastered,
                                  ["conj_first", "conj_10"])
        )

        # Builder milestones
        builder_total = self._safe_count(
            "SELECT COALESCE(SUM(attempts), 0) FROM builder_performance"
        )
        newly_unlocked.extend(
            self._check_threshold("builder", builder_total,
                                  ["builder_first", "builder_50"])
        )

        # Speed recall chain milestone
        best_chain = self._safe_count(
            "SELECT COALESCE(MAX(best_chain_length), 0) FROM recall_chains"
        )
        newly_unlocked.extend(
            self._check_threshold("speed", best_chain, ["chain_10"])
        )

        # CIA drill perfect milestone
        perfect_drills = self._safe_count(
            "SELECT COUNT(*) FROM drill_sessions "
            "WHERE words_attempted > 0 AND words_correct = words_attempted"
        )
        newly_unlocked.extend(
            self._check_threshold("cia", perfect_drills, ["drill_perfect"])
        )

        # Custom vocab milestones
        custom_count = self._safe_count(
            "SELECT COUNT(*) FROM custom_words"
        )
        newly_unlocked.extend(
            self._check_threshold("custom", custom_count,
                                  ["custom_first", "custom_50"])
        )

        # Accuracy milestone (90%+ over 100+ reviews)
        acc_row = self._safe_query(
            "SELECT SUM(total_reviews) as total, SUM(correct_reviews) as correct "
            "FROM review_cards"
        )
        if acc_row:
            acc_total = acc_row["total"] or 0
            acc_correct = acc_row["correct"] or 0
            if acc_total >= 100:
                accuracy = round(acc_correct / acc_total * 100)
                newly_unlocked.extend(
                    self._check_threshold("accuracy", accuracy, ["accuracy_90"])
                )

        return newly_unlocked

    def _safe_count(self, sql: str) -> int:
        """Execute a COUNT query, returning 0 if the table doesn't exist."""
        try:
            row = self.db.conn.execute(sql).fetchone()
            return row[0] if row else 0
        except Exception:
            return 0

    def _safe_query(self, sql: str) -> dict | None:
        """Execute a query, returning None if the table doesn't exist."""
        try:
            row = self.db.conn.execute(sql).fetchone()
            return dict(row) if row else None
        except Exception:
            return None

    def _check_threshold(self, category: str, value: int,
                         achievement_ids: list[str]) -> list[dict]:
        """Check value against achievement thresholds."""
        newly = []
        for aid in achievement_ids:
            row = self.db.conn.execute(
                "SELECT * FROM achievements WHERE id = ?", (aid,)
            ).fetchone()
            if row and not row["unlocked_at"] and value >= row["threshold_value"]:
                newly.extend(self._unlock_if_new(aid))
        return newly

    def _unlock_if_new(self, achievement_id: str) -> list[dict]:
        """Unlock an achievement if not already unlocked."""
        row = self.db.conn.execute(
            "SELECT * FROM achievements WHERE id = ?", (achievement_id,)
        ).fetchone()
        if not row or row["unlocked_at"]:
            return []

        now = datetime.now().isoformat()
        self.db.conn.execute(
            "UPDATE achievements SET unlocked_at = ? WHERE id = ?",
            (now, achievement_id),
        )
        self.db.conn.commit()

        achievement = dict(row)
        achievement["unlocked_at"] = now

        # Award achievement XP
        if achievement["xp_reward"] > 0:
            self.db.conn.execute(
                """INSERT INTO xp_log
                   (action_type, base_xp, quality_multiplier, streak_bonus,
                    total_xp, details)
                   VALUES ('achievement', ?, 1.0, 1.0, ?, ?)""",
                (achievement["xp_reward"], achievement["xp_reward"],
                 f"Achievement: {achievement['name_de']}"),
            )
            self.db.conn.commit()

        return [achievement]

    def mark_perfect_session(self):
        """Call after a perfect review session (all correct)."""
        self._unlock_if_new("perfect_session")

    def get_xp_summary(self) -> dict:
        """Total XP, level, today's XP, streak info."""
        total_xp = self.get_total_xp()
        level_info = self.get_level(total_xp)
        today_xp = self.get_today_xp()
        streak = self.db.get_streak()

        return {
            **level_info,
            "today_xp": today_xp,
            "streak": streak,
        }

    def get_achievements_by_category(self) -> dict[str, list[dict]]:
        """Grouped achievements for display panel."""
        rows = self.db.conn.execute(
            "SELECT * FROM achievements ORDER BY category, threshold_value"
        ).fetchall()

        categories: dict[str, list[dict]] = {}
        for r in rows:
            d = dict(r)
            cat = d["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(d)
        return categories
