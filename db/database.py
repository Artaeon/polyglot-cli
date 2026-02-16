"""SQLite database manager for PolyglotCLI."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from config import DB_PATH, DB_DIR
from models import Word, ReviewCard, PalaceStation, Session, Language


class Database:
    """SQLite database manager with lazy connection."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        self._transaction_depth: int = 0

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA foreign_keys=ON")
        return self._conn

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    @contextmanager
    def transaction(self):
        self._transaction_depth += 1
        try:
            yield self.conn
            self._transaction_depth -= 1
            if self._transaction_depth == 0:
                self.conn.commit()
        except Exception:
            self._transaction_depth = 0
            self.conn.rollback()
            raise

    def _commit(self) -> None:
        """Commit only when not inside a managed transaction."""
        if self._transaction_depth == 0:
            self.conn.commit()

    def init_schema(self):
        """Initialize database from schema.sql."""
        schema_path = Path(__file__).parent / "schema.sql"
        with open(schema_path) as f:
            self.conn.executescript(f.read())

    # ── Languages ──────────────────────────────────────────────

    def insert_language(self, lang: Language):
        self.conn.execute(
            """INSERT OR REPLACE INTO languages
               (id, name, native_name, flag, family, subfamily, script,
                difficulty_tier, palace_name, palace_theme)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (lang.id, lang.name, lang.native_name, lang.flag, lang.family,
             lang.subfamily, lang.script, lang.difficulty_tier,
             lang.palace_name, lang.palace_theme),
        )
        self._commit()

    def get_language(self, lang_id: str) -> Optional[dict]:
        row = self.conn.execute(
            "SELECT * FROM languages WHERE id = ?", (lang_id,)
        ).fetchone()
        return dict(row) if row else None

    def get_all_languages(self) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM languages ORDER BY difficulty_tier, family, name"
        ).fetchall()
        return [dict(r) for r in rows]

    def get_languages_by_family(self, family: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM languages WHERE family = ? ORDER BY subfamily, name",
            (family,),
        ).fetchall()
        return [dict(r) for r in rows]

    # ── Words ──────────────────────────────────────────────────

    def insert_word(self, word: Word) -> int:
        cur = self.conn.execute(
            """INSERT INTO words
               (language_id, word, romanization, pronunciation_hint,
                meaning_de, meaning_en, category, frequency_rank,
                concept_id, tone, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (word.language_id, word.word, word.romanization,
             word.pronunciation_hint, word.meaning_de, word.meaning_en,
             word.category, word.frequency_rank, word.concept_id,
             word.tone, word.notes),
        )
        self._commit()
        return cur.lastrowid

    def insert_words_bulk(self, words: list[dict]):
        """Bulk insert words from dicts."""
        self.conn.executemany(
            """INSERT OR IGNORE INTO words
               (language_id, word, romanization, pronunciation_hint,
                meaning_de, meaning_en, category, frequency_rank,
                concept_id, tone, notes)
               VALUES (:language_id, :word, :romanization, :pronunciation_hint,
                :meaning_de, :meaning_en, :category, :frequency_rank,
                :concept_id, :tone, :notes)""",
            words,
        )
        self._commit()

    def get_existing_word_keys(self, language_id: str) -> set[tuple[str, str]]:
        """Return existing (word, meaning_de) keys for one language."""
        rows = self.conn.execute(
            "SELECT word, meaning_de FROM words WHERE language_id = ?",
            (language_id,),
        ).fetchall()
        return {(r["word"], r["meaning_de"]) for r in rows}

    def get_word(self, word_id: int) -> Optional[dict]:
        row = self.conn.execute(
            "SELECT * FROM words WHERE id = ?", (word_id,)
        ).fetchone()
        return dict(row) if row else None

    def get_words_by_language(self, lang_id: str, category: str = None,
                              limit: int = None) -> list[dict]:
        sql = "SELECT * FROM words WHERE language_id = ?"
        params: list = [lang_id]
        if category:
            sql += " AND category = ?"
            params.append(category)
        sql += " ORDER BY frequency_rank"
        if limit:
            sql += " LIMIT ?"
            params.append(limit)
        return [dict(r) for r in self.conn.execute(sql, params).fetchall()]

    def get_words_by_concept(self, concept_id: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT w.*, l.flag, l.name as lang_name, l.family, l.subfamily "
            "FROM words w JOIN languages l ON w.language_id = l.id "
            "WHERE w.concept_id = ? ORDER BY l.family, l.subfamily, l.name",
            (concept_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    def search_words(self, query: str) -> list[dict]:
        """Search words by word text, meaning, or concept_id."""
        q = f"%{query}%"
        rows = self.conn.execute(
            """SELECT w.*, l.flag, l.name as lang_name, l.family
               FROM words w JOIN languages l ON w.language_id = l.id
               WHERE w.word LIKE ? OR w.meaning_de LIKE ? OR w.meaning_en LIKE ?
                  OR w.concept_id LIKE ? OR w.romanization LIKE ?
               ORDER BY w.frequency_rank LIMIT 100""",
            (q, q, q, q, q),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_word_count_by_language(self) -> dict[str, int]:
        rows = self.conn.execute(
            "SELECT language_id, COUNT(*) as cnt FROM words GROUP BY language_id"
        ).fetchall()
        return {r["language_id"]: r["cnt"] for r in rows}

    def get_unlearned_words(self, lang_id: str, limit: int = 15) -> list[dict]:
        """Get words that don't have a review card yet."""
        rows = self.conn.execute(
            """SELECT w.* FROM words w
               WHERE w.language_id = ?
                 AND w.id NOT IN (SELECT word_id FROM review_cards)
               ORDER BY w.frequency_rank
               LIMIT ?""",
            (lang_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]

    # ── Review Cards ───────────────────────────────────────────

    def create_review_card(self, word_id: int) -> int:
        today = date.today().isoformat()
        cur = self.conn.execute(
            """INSERT OR IGNORE INTO review_cards
               (word_id, ease_factor, interval, repetitions,
                next_review_date, created_at)
               VALUES (?, 2.5, 0, 0, ?, ?)""",
            (word_id, today, datetime.now().isoformat()),
        )
        self._commit()
        return cur.lastrowid

    def get_due_cards(self, lang_id: str = None,
                      family: str = None) -> list[dict]:
        """Get all cards due for review today or earlier."""
        today = date.today().isoformat()
        sql = """SELECT rc.*, w.word, w.romanization, w.meaning_de, w.meaning_en,
                        w.language_id, w.pronunciation_hint, w.concept_id,
                        w.category, w.tone, w.notes,
                        l.flag, l.name as lang_name, l.family
                 FROM review_cards rc
                 JOIN words w ON rc.word_id = w.id
                 JOIN languages l ON w.language_id = l.id
                 WHERE rc.next_review_date <= ?"""
        params: list = [today]
        if lang_id:
            sql += " AND w.language_id = ?"
            params.append(lang_id)
        if family:
            sql += " AND l.family = ?"
            params.append(family)
        sql += " ORDER BY rc.next_review_date, rc.ease_factor"
        return [dict(r) for r in self.conn.execute(sql, params).fetchall()]

    def get_due_count_by_language(self) -> dict[str, int]:
        today = date.today().isoformat()
        rows = self.conn.execute(
            """SELECT w.language_id, COUNT(*) as cnt
               FROM review_cards rc
               JOIN words w ON rc.word_id = w.id
               WHERE rc.next_review_date <= ?
               GROUP BY w.language_id""",
            (today,),
        ).fetchall()
        return {r["language_id"]: r["cnt"] for r in rows}

    def update_review_card(self, card_id: int, ease_factor: float,
                           interval: int, repetitions: int,
                           next_review_date: str, correct: bool):
        today = date.today().isoformat()
        self.conn.execute(
            """UPDATE review_cards
               SET ease_factor = ?, interval = ?, repetitions = ?,
                   next_review_date = ?, last_review_date = ?,
                   total_reviews = total_reviews + 1,
                   correct_reviews = correct_reviews + ?
               WHERE id = ?""",
            (ease_factor, interval, repetitions, next_review_date,
             today, 1 if correct else 0, card_id),
        )
        self._commit()

    def get_learned_count_by_language(self) -> dict[str, int]:
        """Count words that have review cards (= learned)."""
        rows = self.conn.execute(
            """SELECT w.language_id, COUNT(*) as cnt
               FROM review_cards rc
               JOIN words w ON rc.word_id = w.id
               GROUP BY w.language_id"""
        ).fetchall()
        return {r["language_id"]: r["cnt"] for r in rows}

    def get_total_learned(self) -> int:
        row = self.conn.execute(
            "SELECT COUNT(*) as cnt FROM review_cards"
        ).fetchone()
        return row["cnt"] if row else 0

    def get_review_stats(self) -> dict:
        """Get overall review statistics."""
        row = self.conn.execute(
            """SELECT COUNT(*) as total,
                      AVG(ease_factor) as avg_ease,
                      SUM(total_reviews) as total_reviews,
                      SUM(correct_reviews) as correct_reviews
               FROM review_cards"""
        ).fetchone()
        return dict(row) if row else {}

    # ── Palace Stations ────────────────────────────────────────

    def init_palace_stations(self, language_id: str, stations: list[str]):
        """Create empty palace stations for a language."""
        for i, name in enumerate(stations):
            self.conn.execute(
                """INSERT OR IGNORE INTO palace_stations
                   (language_id, station_number, station_name)
                   VALUES (?, ?, ?)""",
                (language_id, i + 1, name),
            )
        self._commit()

    def get_palace_stations(self, language_id: str) -> list[dict]:
        rows = self.conn.execute(
            """SELECT ps.*, w.word, w.meaning_de, w.romanization
               FROM palace_stations ps
               LEFT JOIN words w ON ps.word_id = w.id
               WHERE ps.language_id = ?
               ORDER BY ps.station_number""",
            (language_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    def assign_word_to_station(self, station_id: int, word_id: int,
                                mnemonic: str = ""):
        self.conn.execute(
            """UPDATE palace_stations
               SET word_id = ?, user_mnemonic = ?
               WHERE id = ?""",
            (word_id, mnemonic, station_id),
        )
        self._commit()

    def update_station_mnemonic(self, station_id: int, mnemonic: str):
        self.conn.execute(
            "UPDATE palace_stations SET user_mnemonic = ? WHERE id = ?",
            (mnemonic, station_id),
        )
        self._commit()

    # ── Sessions ───────────────────────────────────────────────

    def log_session(self, session_type: str, duration: int,
                    words_learned: int, words_reviewed: int,
                    languages: list[str]):
        self.conn.execute(
            """INSERT INTO sessions
               (date, duration_minutes, words_learned, words_reviewed,
                languages_practiced, session_type)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (date.today().isoformat(), duration, words_learned,
             words_reviewed, json.dumps(languages), session_type),
        )
        self._commit()

    def get_today_sessions(self) -> list[dict]:
        today = date.today().isoformat()
        rows = self.conn.execute(
            "SELECT * FROM sessions WHERE date = ?", (today,)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_total_time_today(self) -> int:
        today = date.today().isoformat()
        row = self.conn.execute(
            "SELECT COALESCE(SUM(duration_minutes), 0) as total "
            "FROM sessions WHERE date = ?",
            (today,),
        ).fetchone()
        return row["total"]

    def get_streak(self) -> int:
        """Calculate consecutive days with at least 1 session."""
        rows = self.conn.execute(
            "SELECT DISTINCT date FROM sessions ORDER BY date DESC"
        ).fetchall()
        if not rows:
            return 0
        dates = [r["date"] for r in rows]
        today = date.today().isoformat()
        if dates[0] != today:
            # Check if yesterday is there (still valid streak)
            from datetime import timedelta
            yesterday = (date.today() - timedelta(days=1)).isoformat()
            if dates[0] != yesterday:
                return 0
        streak = 1
        for i in range(len(dates) - 1):
            from datetime import timedelta
            d1 = date.fromisoformat(dates[i])
            d2 = date.fromisoformat(dates[i + 1])
            if (d1 - d2).days == 1:
                streak += 1
            else:
                break
        return streak

    def get_sprint_day(self) -> int:
        """Get current sprint day number."""
        row = self.conn.execute(
            "SELECT value FROM settings WHERE key = 'sprint_start'"
        ).fetchone()
        if not row:
            return 1
        start = date.fromisoformat(row["value"])
        return (date.today() - start).days + 1

    # ── Concepts ───────────────────────────────────────────────

    def insert_concept(self, concept: dict):
        self.conn.execute(
            """INSERT OR REPLACE INTO concepts
               (id, meaning_de, meaning_en, category, frequency_rank,
                etymology_note, mnemonic_hint)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (concept["id"], concept.get("de", ""), concept.get("en", ""),
             concept.get("category", ""), concept.get("frequency_rank", 0),
             concept.get("etymology_note", ""), concept.get("mnemonic_hint", "")),
        )
        self._commit()

    def get_concept(self, concept_id: str) -> Optional[dict]:
        row = self.conn.execute(
            "SELECT * FROM concepts WHERE id = ?", (concept_id,)
        ).fetchone()
        return dict(row) if row else None

    def get_all_concepts(self) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM concepts ORDER BY frequency_rank"
        ).fetchall()
        return [dict(r) for r in rows]

    def search_concepts(self, query: str) -> list[dict]:
        q = f"%{query}%"
        rows = self.conn.execute(
            """SELECT * FROM concepts
               WHERE id LIKE ? OR meaning_de LIKE ? OR meaning_en LIKE ?
               ORDER BY frequency_rank LIMIT 20""",
            (q, q, q),
        ).fetchall()
        return [dict(r) for r in rows]

    # ── Settings ───────────────────────────────────────────────

    def set_setting(self, key: str, value: str):
        self.conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value),
        )
        self._commit()

    def get_setting(self, key: str, default: str = "") -> str:
        row = self.conn.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        ).fetchone()
        return row["value"] if row else default

    def get_all_settings(self) -> dict[str, str]:
        rows = self.conn.execute("SELECT * FROM settings").fetchall()
        return {r["key"]: r["value"] for r in rows}
