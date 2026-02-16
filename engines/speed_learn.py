"""Speed learning engine — keyword method, micro-sessions, interleaving,
dual coding, recall chains, error-focused drilling, progressive hints."""

from __future__ import annotations

import random
from datetime import date
from typing import Optional


CEFR_ORDER = ("A1", "A1+", "A2-", "A2", "A2+", "B1-")


# Emoji scenes for dual coding
DUAL_CODING_SCENES = {
    "water": "\U0001f4a7\U0001f30a ~~~~ Wasser fliesst",
    "food": "\U0001f37d\ufe0f\U0001f372 Essen dampft",
    "house": "\U0001f3e0\U0001f3e1 Haus mit Garten",
    "fire": "\U0001f525\U0001f9ef Feuer brennt",
    "sun": "\u2600\ufe0f\U0001f31e Sonne scheint",
    "moon": "\U0001f319\u2b50 Mond und Sterne",
    "book": "\U0001f4d6\U0001f4da Buecher gestapelt",
    "tree": "\U0001f333\U0001f343 Baum mit Blaettern",
    "car": "\U0001f697\U0001f6e3\ufe0f Auto faehrt",
    "dog": "\U0001f415\U0001f9b4 Hund mit Knochen",
    "cat": "\U0001f431\U0001f3e0 Katze im Haus",
    "heart": "\u2764\ufe0f\U0001f495 Herz schlaegt",
    "money": "\U0001f4b0\U0001f4b5 Geld zaehlen",
    "time": "\u23f0\u231b Uhr tickt",
    "work": "\U0001f4bc\U0001f4bb Am Schreibtisch",
    "sleep": "\U0001f634\U0001f6cf\ufe0f Im Bett schlafen",
    "eat": "\U0001f37d\ufe0f\U0001f60b Lecker essen",
    "drink": "\U0001f964\U0001f943 Trinken geniessen",
    "walk": "\U0001f6b6\U0001f3de\ufe0f Spaziergang",
    "speak": "\U0001f5e3\ufe0f\U0001f4ac Reden und diskutieren",
}


class SpeedLearnEngine:
    """Speed learning techniques engine."""

    def __init__(self, db, cluster_engine):
        self.db = db
        self.cluster_engine = cluster_engine

    @staticmethod
    def _normalize_cefr(target_cefr: str | None) -> str | None:
        if not target_cefr:
            return None
        cefr = target_cefr.strip().upper()
        return cefr if cefr in CEFR_ORDER else None

    def _cefr_where_clause(self, target_cefr: str | None,
                           include_lower: bool = True) -> tuple[str, list[str]]:
        """Return SQL WHERE snippet + parameters for CEFR filtering.

        CEFR tags are stored in notes as `cefr:<level>`.
        """
        cefr = self._normalize_cefr(target_cefr)
        if not cefr:
            return "", []

        if include_lower:
            idx = CEFR_ORDER.index(cefr)
            levels = CEFR_ORDER[:idx + 1]
        else:
            levels = (cefr,)

        clause = " AND (" + " OR ".join("w.notes LIKE ?" for _ in levels) + ")"
        params = [f"%cefr:{lvl}%" for lvl in levels]
        return clause, params

    # ── 1. Keyword Method ────────────────────────────────────────

    def generate_keyword(self, word: dict) -> str:
        """Auto-generate a phonetic keyword mnemonic."""
        w = word.get("word", "")
        rom = word.get("romanization", "") or w
        meaning = word.get("meaning_de", "")

        # Take first syllable of romanization and create phonetic link
        if len(rom) >= 4:
            sound = rom[:4]
        elif len(rom) >= 2:
            sound = rom[:2]
        else:
            sound = rom

        return f'"{sound}..." klingt wie... -> {meaning}'

    def get_keyword(self, word_id: int) -> Optional[dict]:
        """Get saved keyword mnemonic for a word."""
        row = self.db.conn.execute(
            "SELECT * FROM keyword_mnemonics WHERE word_id = ?",
            (word_id,),
        ).fetchone()
        return dict(row) if row else None

    def save_user_keyword(self, word_id: int, keyword: str,
                          story: str = ""):
        """Save a user-authored keyword mnemonic."""
        self.db.conn.execute(
            """INSERT OR REPLACE INTO keyword_mnemonics
               (word_id, keyword, story, user_created)
               VALUES (?, ?, ?, 1)""",
            (word_id, keyword, story),
        )
        self.db.conn.commit()

    # ── 2. Micro-Sessions ───────────────────────────────────────

    def prepare_micro_session(self, lang_id: str = None,
                               count: int = 10,
                               target_cefr: str | None = None,
                               include_lower_cefr: bool = True) -> list[dict]:
        """Select ~10 words optimized for retention in 2-minute burst."""
        # Priority: due cards > lowest ease > recently learned
        today = date.today().isoformat()

        sql = """SELECT rc.*, w.word, w.romanization, w.meaning_de,
                        w.meaning_en, w.language_id, w.pronunciation_hint,
                        w.concept_id, w.category, w.id as word_id,
                        l.flag, l.name as lang_name
                 FROM review_cards rc
                 JOIN words w ON rc.word_id = w.id
                 JOIN languages l ON w.language_id = l.id
                 WHERE rc.next_review_date <= ?"""
        params: list = [today]

        if lang_id:
            sql += " AND w.language_id = ?"
            params.append(lang_id)

        cefr_clause, cefr_params = self._cefr_where_clause(
            target_cefr,
            include_lower=include_lower_cefr,
        )
        if cefr_clause:
            sql += cefr_clause
            params.extend(cefr_params)

        sql += " ORDER BY rc.ease_factor ASC, rc.next_review_date ASC LIMIT ?"
        params.append(count)

        rows = self.db.conn.execute(sql, params).fetchall()
        cards = [dict(r) for r in rows]

        # If not enough due cards, add recently learned
        if len(cards) < count:
            remaining = count - len(cards)
            existing_ids = {c["word_id"] for c in cards}
            sql2 = """SELECT rc.*, w.word, w.romanization, w.meaning_de,
                             w.meaning_en, w.language_id, w.pronunciation_hint,
                             w.concept_id, w.category, w.id as word_id,
                             l.flag, l.name as lang_name
                      FROM review_cards rc
                      JOIN words w ON rc.word_id = w.id
                      JOIN languages l ON w.language_id = l.id"""
            params2: list = []
            if lang_id:
                sql2 += " WHERE w.language_id = ?"
                params2.append(lang_id)

            # Keep CEFR preference in fallback set where possible.
            if cefr_clause:
                if " WHERE " in sql2:
                    sql2 += cefr_clause
                else:
                    sql2 += " WHERE " + cefr_clause.removeprefix(" AND ")
                params2.extend(cefr_params)

            sql2 += " ORDER BY rc.created_at DESC LIMIT ?"
            params2.append(remaining + len(existing_ids))

            rows2 = self.db.conn.execute(sql2, params2).fetchall()
            for r in rows2:
                d = dict(r)
                if d["word_id"] not in existing_ids:
                    cards.append(d)
                    existing_ids.add(d["word_id"])
                    if len(cards) >= count:
                        break

        return cards

    # ── 3. Interleaving ─────────────────────────────────────────

    def prepare_interleaved_session(self, count: int = 15,
                                     lang_ids: list[str] = None,
                                     target_cefr: str | None = None,
                                     include_lower_cefr: bool = True) -> list[dict]:
        """Shuffle to maximize diversity — no two consecutive same lang+cat."""
        sql = """SELECT rc.*, w.word, w.romanization, w.meaning_de,
                        w.meaning_en, w.language_id, w.pronunciation_hint,
                        w.concept_id, w.category, w.id as word_id,
                        l.flag, l.name as lang_name
                 FROM review_cards rc
                 JOIN words w ON rc.word_id = w.id
                 JOIN languages l ON w.language_id = l.id"""
        params: list[str | int] = []
        where: list[str] = []

        if lang_ids:
            placeholders = ",".join("?" * len(lang_ids))
            where.append(f"w.language_id IN ({placeholders})")
            params.extend(lang_ids)

        cefr_clause, cefr_params = self._cefr_where_clause(
            target_cefr,
            include_lower=include_lower_cefr,
        )
        if cefr_clause:
            where.append(cefr_clause.removeprefix(" AND "))
            params.extend(cefr_params)

        if where:
            sql += " WHERE " + " AND ".join(where)

        sql += " ORDER BY RANDOM() LIMIT ?"
        params.append(count * 3)

        rows = self.db.conn.execute(sql, params).fetchall()
        pool = [dict(r) for r in rows]

        # Interleave: no two consecutive share language AND category
        result = []
        while pool and len(result) < count:
            for i, card in enumerate(pool):
                if not result:
                    result.append(pool.pop(i))
                    break
                prev = result[-1]
                if (card["language_id"] != prev["language_id"] or
                        card["category"] != prev["category"]):
                    result.append(pool.pop(i))
                    break
            else:
                # No perfect match, just take first
                if pool:
                    result.append(pool.pop(0))

        return result

    # ── 4. Dual Coding ──────────────────────────────────────────

    def get_dual_coding(self, word: dict) -> str:
        """Return emoji scene per concept."""
        concept_id = word.get("concept_id", "")
        meaning = word.get("meaning_de", "").lower()

        # Check direct concept match
        if concept_id in DUAL_CODING_SCENES:
            return DUAL_CODING_SCENES[concept_id]

        # Check meaning keywords
        for key, scene in DUAL_CODING_SCENES.items():
            if key in meaning or key in concept_id:
                return scene

        # Default: generic learning scene
        return f"\U0001f4a1 {word.get('word', '')} = {word.get('meaning_de', '')}"

    # ── 5. Active Recall Chains ─────────────────────────────────

    def start_recall_chain(self, seed_word: dict) -> dict:
        """Start a recall chain from a seed word."""
        return {
            "current_word": seed_word,
            "chain_length": 0,
            "history": [seed_word["id"]],
        }

    def get_next_chain_word(self, current: dict,
                             history: list[int]) -> Optional[dict]:
        """Get next word in chain — related by concept or cluster."""
        concept_id = current.get("concept_id", "")
        lang_id = current.get("language_id", "")

        # Try same concept, different language
        if concept_id:
            rows = self.db.conn.execute(
                """SELECT w.*, l.flag, l.name as lang_name
                   FROM words w
                   JOIN review_cards rc ON w.id = rc.word_id
                   JOIN languages l ON w.language_id = l.id
                   WHERE w.concept_id = ? AND w.id NOT IN ({})
                   ORDER BY RANDOM() LIMIT 1""".format(
                    ",".join("?" * len(history))
                ),
                (concept_id, *history),
            ).fetchone()
            if rows:
                return dict(rows)

        # Try same category, same language
        category = current.get("category", "")
        rows = self.db.conn.execute(
            """SELECT w.*, l.flag, l.name as lang_name
               FROM words w
               JOIN review_cards rc ON w.id = rc.word_id
               JOIN languages l ON w.language_id = l.id
               WHERE w.language_id = ? AND w.category = ?
               AND w.id NOT IN ({})
               ORDER BY RANDOM() LIMIT 1""".format(
                ",".join("?" * len(history))
            ),
            (lang_id, category, *history),
        ).fetchone()
        if rows:
            return dict(rows)

        # Any learned word not in history
        rows = self.db.conn.execute(
            """SELECT w.*, l.flag, l.name as lang_name
               FROM words w
               JOIN review_cards rc ON w.id = rc.word_id
               JOIN languages l ON w.language_id = l.id
               WHERE w.id NOT IN ({})
               ORDER BY RANDOM() LIMIT 1""".format(
                ",".join("?" * len(history))
            ),
            tuple(history),
        ).fetchone()
        return dict(rows) if rows else None

    def save_chain_result(self, chain_length: int):
        """Save recall chain result."""
        today = date.today().isoformat()

        # Get current best
        row = self.db.conn.execute(
            "SELECT * FROM recall_chains WHERE chain_date = ?",
            (today,),
        ).fetchone()

        if row:
            best = max(row["best_chain_length"], chain_length)
            self.db.conn.execute(
                """UPDATE recall_chains
                   SET chain_length = ?, best_chain_length = ?
                   WHERE id = ?""",
                (chain_length, best, row["id"]),
            )
        else:
            self.db.conn.execute(
                """INSERT INTO recall_chains
                   (chain_date, chain_length, best_chain_length)
                   VALUES (?, ?, ?)""",
                (today, chain_length, chain_length),
            )
        self.db.conn.commit()

    def get_best_chain(self) -> int:
        """Get all-time best chain length."""
        row = self.db.conn.execute(
            "SELECT MAX(best_chain_length) as best FROM recall_chains"
        ).fetchone()
        return row["best"] if row and row["best"] else 0

    # ── 6. Error-Focused Drilling ────────────────────────────────

    def get_error_focused_words(self, limit: int = 15,
                                 lang_id: str = None,
                                 target_cefr: str | None = None,
                                 include_lower_cefr: bool = True) -> list[dict]:
        """Get cards with ease < 1.8 or retention < 50%."""
        sql = """SELECT rc.*, w.word, w.romanization, w.meaning_de,
                        w.meaning_en, w.language_id, w.pronunciation_hint,
                        w.concept_id, w.category, w.id as word_id,
                        l.flag, l.name as lang_name
                 FROM review_cards rc
                 JOIN words w ON rc.word_id = w.id
                 JOIN languages l ON w.language_id = l.id
                 WHERE (rc.ease_factor < 1.8
                        OR (rc.total_reviews > 2
                            AND CAST(rc.correct_reviews AS REAL) /
                                rc.total_reviews < 0.5))"""
        params: list = []

        if lang_id:
            sql += " AND w.language_id = ?"
            params.append(lang_id)

        cefr_clause, cefr_params = self._cefr_where_clause(
            target_cefr,
            include_lower=include_lower_cefr,
        )
        if cefr_clause:
            sql += cefr_clause
            params.extend(cefr_params)

        sql += " ORDER BY rc.ease_factor ASC LIMIT ?"
        params.append(limit)

        rows = self.db.conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

    # ── 7. Progressive Hints ────────────────────────────────────

    @staticmethod
    def get_progressive_hint(word: str, hint_level: int) -> str:
        """Reveal characters progressively: s____ -> so___ -> sob__."""
        if not word:
            return "___"
        revealed = min(hint_level, len(word))
        return word[:revealed] + "_" * (len(word) - revealed)
