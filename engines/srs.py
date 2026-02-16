"""Spaced Repetition System — SM-2 algorithm implementation."""

from __future__ import annotations

from datetime import date, timedelta

from config import SRS_INITIAL_EASE, SRS_MIN_EASE


def sm2(quality: int, repetitions: int, ease_factor: float,
        interval: int) -> tuple[int, float, int]:
    """SM-2 algorithm (SuperMemo 2).

    Args:
        quality: 0-5 (0=complete blackout, 5=perfect recall)
        repetitions: number of successful reviews in a row
        ease_factor: current ease factor (starts at 2.5)
        interval: current interval in days

    Returns:
        (new_repetitions, new_ease_factor, new_interval)
    """
    if quality >= 3:  # Correct response
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = round(interval * ease_factor)
        repetitions += 1
    else:  # Incorrect
        repetitions = 0
        interval = 1

    ease_factor = max(
        SRS_MIN_EASE,
        ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)),
    )
    return repetitions, ease_factor, interval


def next_review_date(interval: int) -> str:
    """Calculate next review date from interval."""
    return (date.today() + timedelta(days=interval)).isoformat()


def review_card(db, card_id: int, quality: int):
    """Process a review for a card and update in database.

    Args:
        db: Database instance
        card_id: review card ID
        quality: 0-5 grade
    """
    # Get current card state
    row = db.conn.execute(
        "SELECT * FROM review_cards WHERE id = ?", (card_id,)
    ).fetchone()
    if not row:
        return

    new_reps, new_ease, new_interval = sm2(
        quality, row["repetitions"], row["ease_factor"], row["interval"]
    )
    new_date = next_review_date(new_interval)
    correct = quality >= 3

    db.update_review_card(
        card_id, new_ease, new_interval, new_reps, new_date, correct
    )

    return {
        "ease_factor": new_ease,
        "interval": new_interval,
        "repetitions": new_reps,
        "next_review_date": new_date,
        "correct": correct,
    }
