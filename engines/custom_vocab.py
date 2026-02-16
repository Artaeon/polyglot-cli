"""Custom vocabulary engine — add, import, export user-defined words."""

from __future__ import annotations

import csv
import io
import json
import logging
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from db.database import Database

logger = logging.getLogger(__name__)


class CustomVocabEngine:
    """Manage user-defined custom vocabulary words."""

    def __init__(self, db: Database) -> None:
        self.db = db

    def add_word(
        self,
        language_id: str,
        word: str,
        meaning_de: str,
        meaning_en: str = "",
        romanization: str = "",
        tags: str = "",
        source: str = "manual",
    ) -> int:
        """Add a custom word and create a corresponding entry in the words table."""
        # Insert into custom_words tracking table
        cur = self.db.conn.execute(
            """INSERT INTO custom_words
               (language_id, word, romanization, meaning_de, meaning_en, tags, source)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (language_id, word, romanization, meaning_de, meaning_en, tags, source),
        )
        custom_id = cur.lastrowid

        # Also insert into main words table for SRS integration
        self.db.conn.execute(
            """INSERT INTO words
               (language_id, word, romanization, meaning_de, meaning_en,
                category, frequency_rank, concept_id, notes)
               VALUES (?, ?, ?, ?, ?, 'custom', 9999, '', ?)""",
            (language_id, word, romanization, meaning_de, meaning_en,
             f"custom:{custom_id}"),
        )
        self.db.conn.commit()
        return custom_id

    def delete_custom_word(self, custom_id: int) -> bool:
        """Delete a custom word and its words table entry."""
        row = self.db.conn.execute(
            "SELECT * FROM custom_words WHERE id = ?", (custom_id,)
        ).fetchone()
        if not row:
            return False

        # Delete from words table
        self.db.conn.execute(
            "DELETE FROM words WHERE notes = ?",
            (f"custom:{custom_id}",),
        )
        # Delete from custom_words
        self.db.conn.execute(
            "DELETE FROM custom_words WHERE id = ?",
            (custom_id,),
        )
        self.db.conn.commit()
        return True

    def get_custom_words(self, language_id: str | None = None) -> list[dict]:
        """Get all custom words, optionally filtered by language."""
        if language_id:
            rows = self.db.conn.execute(
                "SELECT * FROM custom_words WHERE language_id = ? ORDER BY created_at DESC",
                (language_id,),
            ).fetchall()
        else:
            rows = self.db.conn.execute(
                "SELECT * FROM custom_words ORDER BY created_at DESC"
            ).fetchall()
        return [dict(r) for r in rows]

    def import_csv(self, csv_text: str, language_id: str) -> int:
        """Import words from CSV text. Returns count of imported words.

        Expected CSV format: word,meaning_de,meaning_en,romanization,tags
        """
        reader = csv.DictReader(io.StringIO(csv_text))
        count = 0
        for row in reader:
            word = row.get("word", "").strip()
            meaning_de = row.get("meaning_de", "").strip()
            if not word or not meaning_de:
                continue
            self.add_word(
                language_id=language_id,
                word=word,
                meaning_de=meaning_de,
                meaning_en=row.get("meaning_en", "").strip(),
                romanization=row.get("romanization", "").strip(),
                tags=row.get("tags", "").strip(),
                source="csv_import",
            )
            count += 1
        return count

    def import_json(self, json_text: str, language_id: str) -> int:
        """Import words from JSON text. Returns count of imported words.

        Expected format: [{"word": "...", "meaning_de": "...", ...}, ...]
        """
        data = json.loads(json_text)
        if not isinstance(data, list):
            data = data.get("words", [])

        count = 0
        for item in data:
            word = item.get("word", "").strip()
            meaning_de = item.get("meaning_de", "").strip()
            if not word or not meaning_de:
                continue
            self.add_word(
                language_id=language_id,
                word=word,
                meaning_de=meaning_de,
                meaning_en=item.get("meaning_en", ""),
                romanization=item.get("romanization", ""),
                tags=item.get("tags", ""),
                source="json_import",
            )
            count += 1
        return count

    def export_csv(self, language_id: str | None = None) -> str:
        """Export custom words as CSV string."""
        words = self.get_custom_words(language_id)
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=["language_id", "word", "romanization", "meaning_de",
                        "meaning_en", "tags", "source"],
        )
        writer.writeheader()
        for w in words:
            writer.writerow({
                "language_id": w["language_id"],
                "word": w["word"],
                "romanization": w.get("romanization", ""),
                "meaning_de": w["meaning_de"],
                "meaning_en": w.get("meaning_en", ""),
                "tags": w.get("tags", ""),
                "source": w.get("source", ""),
            })
        return output.getvalue()

    def export_json(self, language_id: str | None = None) -> str:
        """Export custom words as JSON string."""
        words = self.get_custom_words(language_id)
        clean = []
        for w in words:
            clean.append({
                "language_id": w["language_id"],
                "word": w["word"],
                "romanization": w.get("romanization", ""),
                "meaning_de": w["meaning_de"],
                "meaning_en": w.get("meaning_en", ""),
                "tags": w.get("tags", ""),
            })
        return json.dumps({"words": clean}, ensure_ascii=False, indent=2)

    def get_count(self, language_id: str | None = None) -> int:
        """Get count of custom words."""
        if language_id:
            row = self.db.conn.execute(
                "SELECT COUNT(*) as cnt FROM custom_words WHERE language_id = ?",
                (language_id,),
            ).fetchone()
        else:
            row = self.db.conn.execute(
                "SELECT COUNT(*) as cnt FROM custom_words"
            ).fetchone()
        return row["cnt"] if row else 0
