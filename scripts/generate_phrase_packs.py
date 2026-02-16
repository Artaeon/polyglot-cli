#!/usr/bin/env python3
"""Generate multilingual phrase packs from validated sentence templates.

Creates pack5..pack10 files for all languages using existing
translations in data/sentences/templates.json.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
WORDS_DIR = DATA / "words"
LANGUAGES_FILE = DATA / "languages.json"
SENTENCES_FILE = DATA / "sentences" / "templates.json"

CATEGORY_MAP = {
    "greetings": "phrasen",
    "introductions": "phrasen",
    "daily_life": "phrasen",
    "travel": "fragen_richtungen",
    "shopping": "phrasen",
    "food": "essen_trinken",
    "questions": "fragen_richtungen",
    "feelings": "phrasen",
    "time": "phrasen",
    "weather": "natur_wetter",
}

PACK_DEFS = {
    5: [
        "hello_how_are_you",
        "my_name_is",
        "i_dont_understand",
        "where_is",
        "how_much_cost",
        "i_would_like",
        "thank_you_very_much",
        "water_please",
    ],
    6: [
        "i_speak_language",
        "what_time_is_it",
        "the_weather_is_nice",
        "i_am_hungry",
        "i_love_you",
        "hello_how_are_you",
        "where_is",
        "how_much_cost",
    ],
    7: [
        "my_name_is",
        "i_speak_language",
        "i_dont_understand",
        "i_would_like",
        "thank_you_very_much",
        "what_time_is_it",
        "the_weather_is_nice",
        "water_please",
    ],
    8: [
        "hello_how_are_you",
        "my_name_is",
        "i_speak_language",
        "where_is",
        "how_much_cost",
        "i_would_like",
        "what_time_is_it",
        "the_weather_is_nice",
    ],
    9: [
        "i_dont_understand",
        "where_is",
        "i_am_hungry",
        "i_love_you",
        "thank_you_very_much",
        "water_please",
        "how_much_cost",
        "my_name_is",
    ],
    10: [
        "hello_how_are_you",
        "i_dont_understand",
        "where_is",
        "how_much_cost",
        "i_would_like",
        "i_am_hungry",
        "water_please",
        "thank_you_very_much",
    ],
}


def load_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    languages = [x["id"] for x in load_json(LANGUAGES_FILE).get("languages", [])]
    sentences = load_json(SENTENCES_FILE).get("sentences", [])
    sentence_map = {s["id"]: s for s in sentences}

    generated_files = 0

    for pack_num, template_ids in PACK_DEFS.items():
        base_rank = 1400 + (pack_num - 5) * 100

        for lang_id in languages:
            words = []

            for offset, sid in enumerate(template_ids, 1):
                s = sentence_map[sid]
                trans = s.get("translations", {}).get(lang_id, {})
                text = trans.get("text", "")

                words.append(
                    {
                        "word": text,
                        "romanization": trans.get("romanization") or "",
                        "pronunciation_hint": trans.get("pronunciation", ""),
                        "meaning_de": s.get("de", ""),
                        "meaning_en": s.get("en", ""),
                        "category": CATEGORY_MAP.get(s.get("category", ""), "phrasen"),
                        "frequency_rank": base_rank + offset,
                        "concept_id": f"tpl{pack_num}_{sid}",
                        "tone": None,
                        "notes": f"template_pack_{pack_num}",
                    }
                )

            payload = {
                "language_id": lang_id,
                "words": words,
            }

            out = WORDS_DIR / f"{lang_id}_pack{pack_num}.json"
            out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            generated_files += 1

    print(f"Generated {generated_files} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
