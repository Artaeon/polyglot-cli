#!/usr/bin/env python3
"""Compute per-language content quality scores (offline, deterministic).

Metrics per language:
- raw_count
- unique_ratio
- category_coverage
- cefr_tag_coverage
- quality_score (0..100)

Can fail CI with `--fail-under-avg` and `--fail-under-min`.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
WORDS = DATA / "words"
LANGUAGES = DATA / "languages.json"

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


def compute_scores() -> dict:
    language_ids = [x["id"] for x in load_json(LANGUAGES).get("languages", [])]

    rows = defaultdict(list)
    for fp in sorted(WORDS.glob("*.json")):
        payload = load_json(fp)
        lang_id = payload.get("language_id")
        if lang_id:
            rows[lang_id].extend(payload.get("words", []))

    report = {"languages": {}}

    for lid in language_ids:
        words = rows.get(lid, [])
        raw_count = len(words)

        unique = {
            (
                str(w.get("word", "")).strip(),
                str(w.get("meaning_de", "")).strip(),
                str(w.get("concept_id", "")).strip(),
            )
            for w in words
        }
        unique_ratio = (len(unique) / raw_count) if raw_count else 0.0

        categories = {str(w.get("category", "")).strip() for w in words}
        valid_categories = categories.intersection(ALLOWED_CATEGORIES)
        category_coverage = len(valid_categories) / len(ALLOWED_CATEGORIES)

        cefr_tagged = sum(1 for w in words if "cefr:" in str(w.get("notes", "")))
        cefr_coverage = (cefr_tagged / raw_count) if raw_count else 0.0

        volume = min(raw_count / 400.0, 1.0)

        score = round(
            100
            * (
                0.40 * unique_ratio
                + 0.25 * category_coverage
                + 0.20 * cefr_coverage
                + 0.15 * volume
            ),
            2,
        )

        report["languages"][lid] = {
            "raw_count": raw_count,
            "unique_count": len(unique),
            "unique_ratio": round(unique_ratio, 4),
            "category_coverage": round(category_coverage, 4),
            "cefr_tag_coverage": round(cefr_coverage, 4),
            "quality_score": score,
        }

    scores = [x["quality_score"] for x in report["languages"].values()] or [0.0]
    report["summary"] = {
        "avg_score": round(sum(scores) / len(scores), 2),
        "min_score": round(min(scores), 2),
        "max_score": round(max(scores), 2),
        "languages": len(report["languages"]),
    }

    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", default="", help="optional output JSON file")
    parser.add_argument("--fail-under-avg", type=float, default=0.0)
    parser.add_argument("--fail-under-min", type=float, default=0.0)
    args = parser.parse_args()

    report = compute_scores()

    print("Content quality report")
    for lid, data in sorted(report["languages"].items()):
        print(
            f" - {lid}: score={data['quality_score']:.2f} "
            f"raw={data['raw_count']} "
            f"unique={data['unique_ratio']:.2%} "
            f"cats={data['category_coverage']:.2%} "
            f"cefr={data['cefr_tag_coverage']:.2%}"
        )

    s = report["summary"]
    print(
        f"Summary: avg={s['avg_score']:.2f} min={s['min_score']:.2f} "
        f"max={s['max_score']:.2f} langs={s['languages']}"
    )

    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.fail_under_avg and s["avg_score"] < args.fail_under_avg:
        print(
            f"FAIL: average score {s['avg_score']:.2f} < required {args.fail_under_avg:.2f}"
        )
        return 1

    if args.fail_under_min and s["min_score"] < args.fail_under_min:
        print(
            f"FAIL: min score {s['min_score']:.2f} < required {args.fail_under_min:.2f}"
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
