#!/usr/bin/env python3
"""Validate local language content quality (fully offline).

Checks:
- JSON readability
- Required word fields
- Category validity
- Duplicate entries
- Pack concept consistency across languages
- Sentence template language coverage
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
WORDS = DATA / "words"
LANGUAGES = DATA / "languages.json"
SENTENCES = DATA / "sentences" / "templates.json"

REQUIRED_WORD_KEYS = {
    "word",
    "romanization",
    "pronunciation_hint",
    "meaning_de",
    "meaning_en",
    "category",
    "frequency_rank",
    "concept_id",
    "tone",
    "notes",
}

ALLOWED_CATEGORIES = {
    "pronomen_basics",
    "verben",
    "nomen",
    "adjektive",
    "zahlen",
    "phrasen",
    "zeitwoerter_konjunktionen",
    "fragen_richtungen",
    "koerper_gesundheit",
    "essen_trinken",
    "natur_wetter",
    "beruf_bildung",
}


def load_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def validate_word_files(language_ids: set[str]) -> list[str]:
    errors: list[str] = []

    seen_rows: set[tuple[str, str, str, str]] = set()
    pack_concepts: dict[str, list[tuple[str, set[str]]]] = defaultdict(list)

    for file in sorted(WORDS.glob("*.json")):
        try:
            payload = load_json(file)
        except Exception as exc:
            errors.append(f"{file.name}: invalid JSON ({exc})")
            continue

        lang_id = payload.get("language_id")
        if not isinstance(lang_id, str) or not lang_id:
            errors.append(f"{file.name}: missing language_id")
            continue

        if lang_id not in language_ids:
            errors.append(f"{file.name}: unknown language_id '{lang_id}'")

        words = payload.get("words", [])
        if not isinstance(words, list):
            errors.append(f"{file.name}: words must be a list")
            continue

        concept_ids_in_file: set[str] = set()

        for i, row in enumerate(words, 1):
            if not isinstance(row, dict):
                errors.append(f"{file.name}#{i}: word row must be object")
                continue

            missing = REQUIRED_WORD_KEYS - set(row.keys())
            if missing:
                errors.append(f"{file.name}#{i}: missing keys {sorted(missing)}")

            category = row.get("category")
            if category not in ALLOWED_CATEGORIES:
                errors.append(f"{file.name}#{i}: invalid category '{category}'")

            rank = row.get("frequency_rank")
            if not isinstance(rank, int) or rank <= 0:
                errors.append(f"{file.name}#{i}: frequency_rank must be positive int")

            key = (
                lang_id,
                str(row.get("word", "")).strip(),
                str(row.get("meaning_de", "")).strip(),
                str(row.get("concept_id", "")).strip(),
            )
            if key in seen_rows:
                errors.append(f"{file.name}#{i}: duplicate word tuple {key}")
            seen_rows.add(key)

            cid = str(row.get("concept_id", "")).strip()
            if cid:
                concept_ids_in_file.add(cid)

        m = re.search(r"_pack(\d+)\.json$", file.name)
        if m:
            pack_key = m.group(1)
            pack_concepts[pack_key].append((lang_id, concept_ids_in_file))

    # Validate pack concept consistency across languages for packN files
    for pack, items in sorted(pack_concepts.items()):
        if not items:
            continue
        baseline = items[0][1]
        for lang_id, concepts in items[1:]:
            if concepts != baseline:
                errors.append(
                    f"pack{pack}: concept mismatch for {lang_id} (expected {sorted(baseline)}, got {sorted(concepts)})"
                )

    return errors


def validate_sentence_templates(language_ids: set[str]) -> list[str]:
    errors: list[str] = []
    try:
        payload = load_json(SENTENCES)
    except Exception as exc:
        return [f"templates.json invalid JSON ({exc})"]

    sentences = payload.get("sentences", [])
    if not isinstance(sentences, list):
        return ["templates.json: 'sentences' must be a list"]

    for i, s in enumerate(sentences, 1):
        if not isinstance(s, dict):
            errors.append(f"templates#{i}: sentence must be object")
            continue
        for key in ("id", "de", "en", "translations"):
            if key not in s:
                errors.append(f"templates#{i}: missing '{key}'")
        translations = s.get("translations", {})
        if not isinstance(translations, dict):
            errors.append(f"templates#{i}: translations must be object")
            continue
        missing_langs = sorted(language_ids - set(translations.keys()))
        if missing_langs:
            errors.append(f"templates#{i} ({s.get('id')}): missing langs {missing_langs}")

    return errors


def main() -> int:
    lang_payload = load_json(LANGUAGES)
    language_ids = {x["id"] for x in lang_payload.get("languages", []) if "id" in x}

    errors: list[str] = []
    errors.extend(validate_word_files(language_ids))
    errors.extend(validate_sentence_templates(language_ids))

    if errors:
        print("❌ Content validation failed:")
        for e in errors:
            print(f" - {e}")
        return 1

    print("✅ Content validation passed")
    print(f"Languages: {len(language_ids)}")
    print(f"Word files: {len(list(WORDS.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
