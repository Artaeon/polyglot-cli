"""Unified word-fetching queries used by multiple engines."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from db.database import Database


def get_learned_words(db: Database, lang_id: str) -> list[dict]:
    """Get words that have been learned (have review cards) for a language."""
    rows = db.conn.execute(
        """SELECT w.* FROM words w
           JOIN review_cards rc ON w.id = rc.word_id
           WHERE w.language_id = ?
           ORDER BY RANDOM()""",
        (lang_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def get_learned_cards(db: Database, lang_id: str, count: int = 10) -> list[dict]:
    """Get learned words with language info for a language."""
    rows = db.conn.execute(
        """SELECT w.*, w.id as word_id,
                  l.flag, l.name as lang_name
           FROM words w
           JOIN review_cards rc ON w.id = rc.word_id
           JOIN languages l ON w.language_id = l.id
           WHERE w.language_id = ?
           ORDER BY RANDOM() LIMIT ?""",
        (lang_id, count),
    ).fetchall()
    return [dict(r) for r in rows]


def get_multi_lang_cards(
    db: Database, lang_ids: list[str], count: int = 20
) -> list[dict]:
    """Get learned words across multiple languages."""
    if not lang_ids:
        return []
    placeholders = ",".join("?" * len(lang_ids))
    rows = db.conn.execute(
        f"""SELECT w.*, w.id as word_id,
                   l.flag, l.name as lang_name
            FROM words w
            JOIN review_cards rc ON w.id = rc.word_id
            JOIN languages l ON w.language_id = l.id
            WHERE w.language_id IN ({placeholders})
            ORDER BY RANDOM() LIMIT ?""",
        (*lang_ids, count),
    ).fetchall()
    return [dict(r) for r in rows]


def get_distractors(
    db: Database,
    correct_word: dict,
    lang_id: str,
    count: int = 3,
    field: str = "word",
) -> list[str]:
    """Get distractor words from same language and category."""
    rows = db.conn.execute(
        """SELECT {field} FROM words
           WHERE language_id = ? AND id != ?
           AND category = ?
           ORDER BY RANDOM() LIMIT ?""".format(field=field),
        (lang_id, correct_word["id"], correct_word.get("category", ""), count),
    ).fetchall()

    distractors = [r[field] for r in rows]

    # Fill if not enough from same category
    if len(distractors) < count:
        extra = db.conn.execute(
            """SELECT {field} FROM words
               WHERE language_id = ? AND id != ?
               ORDER BY RANDOM() LIMIT ?""".format(field=field),
            (lang_id, correct_word["id"], count - len(distractors)),
        ).fetchall()
        distractors.extend(r[field] for r in extra)

    return distractors[:count]
