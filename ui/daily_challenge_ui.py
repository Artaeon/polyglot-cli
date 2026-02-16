"""Daily challenge UI — display and interaction for daily challenges."""

from __future__ import annotations

import json
import logging
import time
from typing import TYPE_CHECKING

from rich.panel import Panel

from ui.terminal import console
from ui.gamification_ui import show_xp_gain

if TYPE_CHECKING:
    from app import AppContext

logger = logging.getLogger(__name__)


def run_daily_challenge_ui(app: AppContext) -> None:
    """Main daily challenge interface."""
    from ui import terminal as ui

    ui.clear_screen()
    console.print("\n  [bold]\U0001f3af TAEGLICHE HERAUSFORDERUNG[/bold]\n")

    challenge = app.daily_challenge_engine.get_today_challenge()
    data = json.loads(challenge.get("data_json", "{}"))

    if challenge.get("completed"):
        console.print(Panel(
            f"  \u2705 Heute bereits abgeschlossen!\n"
            f"  Typ: {challenge['challenge_type']}\n"
            f"  Ergebnis: {challenge['score']}/{challenge['max_score']}\n"
            f"  XP verdient: {challenge['xp_earned']}",
            title="Heutige Challenge",
            border_style="green",
        ))

        # Show streak
        streak = app.daily_challenge_engine.get_streak()
        if streak > 1:
            console.print(f"\n  \U0001f525 Challenge-Streak: {streak} Tage!")

        ui.wait_for_enter()
        return

    console.print(Panel(
        f"  {data.get('description_de', 'Tagesherausforderung')}\n"
        f"  Typ: [bold]{challenge['challenge_type']}[/bold]\n"
        f"  Max Punkte: {challenge.get('max_score', 10)}",
        title="\U0001f3af Heutige Challenge",
        border_style="bold yellow",
    ))

    if not ui.ask_confirm("\nChallenge starten?", default=True):
        return

    # Run the challenge based on type
    score = _run_challenge(app, challenge["challenge_type"], data)

    # Complete and show results
    result = app.daily_challenge_engine.complete_challenge(score)

    ui.clear_screen()
    if result.get("already_completed"):
        console.print("  Challenge bereits abgeschlossen!")
    else:
        emoji = "\U0001f3c6" if result.get("perfect") else "\U0001f389"
        console.print(Panel(
            f"  {emoji} Challenge abgeschlossen!\n\n"
            f"  Ergebnis: [bold]{result['score']}/{result['max_score']}[/bold]\n"
            f"  XP verdient: [bold green]+{result['xp_earned']} XP[/bold green]"
            + ("\n  \U0001f4af PERFEKT! Doppelte XP!" if result.get("perfect") else ""),
            title="Ergebnis",
            border_style="bold green" if result.get("perfect") else "bold yellow",
        ))

    streak = app.daily_challenge_engine.get_streak()
    if streak > 1:
        console.print(f"\n  \U0001f525 Challenge-Streak: {streak} Tage!")

    ui.wait_for_enter()


def _run_challenge(app: AppContext, challenge_type: str, data: dict) -> int:
    """Execute a challenge and return the score."""
    from ui import terminal as ui

    count = data.get("count", 10)
    score = 0

    if challenge_type in ("vocab_blitz", "speed_round"):
        score = _run_vocab_challenge(app, count, data.get("time_limit", 120))
    elif challenge_type == "mixed_review":
        score = _run_mixed_challenge(app, count)
    elif challenge_type == "polyglot_test":
        score = _run_polyglot_test(app, count)
    else:
        # Fallback: simple vocab quiz
        score = _run_vocab_challenge(app, count, 0)

    return score


def _run_vocab_challenge(app: AppContext, count: int, time_limit: int) -> int:
    """Vocabulary translation challenge."""
    from ui import terminal as ui

    words = app.speed_engine.prepare_micro_session(count=count)
    if not words:
        console.print("  Keine Woerter verfuegbar!")
        return 0

    start = time.time()
    score = 0

    for i, word in enumerate(words[:count]):
        if time_limit and (time.time() - start) > time_limit:
            console.print("\n  \u23f1\ufe0f Zeit abgelaufen!")
            break

        remaining = ""
        if time_limit:
            remaining = f" [\u23f1\ufe0f {max(0, time_limit - int(time.time() - start))}s]"

        console.print(
            f"\n  [{i+1}/{count}]{remaining} "
            f"{word.get('flag', '')} [bold]{word['word']}[/bold]"
        )
        if word.get("romanization"):
            console.print(f"  [dim]({word['romanization']})[/dim]")

        answer = ui.ask_text("Bedeutung:")
        if answer and answer.strip().lower() == word["meaning_de"].lower():
            score += 1
            console.print("  \u2705 Richtig!")
        else:
            console.print(f"  \u274c {word['meaning_de']}")

    return score


def _run_mixed_challenge(app: AppContext, count: int) -> int:
    """Mixed exercise challenge."""
    return _run_vocab_challenge(app, count, 0)


def _run_polyglot_test(app: AppContext, count: int) -> int:
    """Multi-language challenge."""
    from ui import terminal as ui

    words = app.speed_engine.prepare_interleaved_session(count)
    if not words:
        console.print("  Keine Woerter verfuegbar!")
        return 0

    score = 0
    for i, word in enumerate(words[:count]):
        console.print(
            f"\n  [{i+1}/{count}] {word.get('flag', '')} {word.get('lang_name', '')}"
        )
        console.print(f"  [bold]{word['word']}[/bold]")
        if word.get("romanization"):
            console.print(f"  [dim]({word['romanization']})[/dim]")

        answer = ui.ask_text("Bedeutung:")
        if answer and answer.strip().lower() == word["meaning_de"].lower():
            score += 1
            console.print("  \u2705 Richtig!")
        else:
            console.print(f"  \u274c {word['meaning_de']}")

    return score
