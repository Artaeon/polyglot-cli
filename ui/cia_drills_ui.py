"""CIA drills UI — timed displays, countdown timers, language switch banners."""

from __future__ import annotations

import time

from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich import box

from ui.terminal import console


def show_cia_menu() -> str:
    """Show CIA drills submenu."""
    console.print(Panel(
        "[bold]\U0001f575\ufe0f  CIA-INTENSIV-DRILLS[/bold]",
        border_style="bold red",
    ))

    items = [
        ("[1]", "\U0001f441\ufe0f ", "Shadowing", "Sehen, merken, tippen"),
        ("[2]", "\u26a1", "Rapid Association", "Uebersetzen unter Zeitdruck"),
        ("[3]", "\U0001f504", "Context Switching", "Schneller Sprachwechsel"),
        ("[4]", "\U0001f9e9", "Pattern Recognition", "Muster erkennen"),
        ("[5]", "\U0001f30d", "Immersion Block", "Volle Immersion"),
        ("[6]", "\U0001f504", "Back-Translation", "Hin und zurueck"),
        ("[0]", "", "Zurueck", ""),
    ]

    for item in items:
        key, emoji, label = item[0], item[1], item[2]
        hint = f"  \u2190 {item[3]}" if item[3] else ""
        style = "dim" if key == "[0]" else "white"
        console.print(f"  {key} {emoji} {label}[dim]{hint}[/dim]", style=style)

    console.print()
    from rich.prompt import Prompt
    return Prompt.ask("  >", default="0").strip()


def show_shadowing_word(word: str, romanization: str = "",
                         seconds: float = 3.0):
    """Display a word briefly for shadowing drill."""
    display = f"[bold]{word}[/bold]"
    if romanization:
        display += f"  ({romanization})"

    console.print(Panel(
        f"\n  {display}\n",
        border_style="bold cyan",
        title=f"\U0001f441\ufe0f  Merken! ({seconds:.1f}s)",
    ))

    time.sleep(seconds)

    # Clear the word
    console.print("\n  [dim]... aus dem Gedaechtnis tippen![/dim]\n")


def show_rapid_timer(time_limit_ms: int, flag: str = "",
                     lang_name: str = ""):
    """Show time limit indicator for rapid drills."""
    seconds = time_limit_ms / 1000
    console.print(
        f"  {flag} {lang_name} | \u23f1\ufe0f  "
        f"[bold yellow]{seconds:.1f}s[/bold yellow]",
    )


def show_context_switch_banner(flag: str, lang_name: str):
    """Show language switch banner during context switching."""
    console.print()
    console.print(Panel(
        f"[bold]{flag} {lang_name}[/bold]",
        border_style="bold magenta",
        title="\U0001f504 SPRACHWECHSEL",
    ))


def show_immersion_header(flag: str, lang_name: str,
                           duration_min: int = 5):
    """Show immersion block header."""
    console.print(Panel(
        f"[bold]\U0001f30d IMMERSION: {flag} {lang_name}[/bold]\n"
        f"Dauer: {duration_min} Minuten\n"
        f"Alles auf {lang_name}!",
        border_style="bold green",
    ))


def show_immersion_feedback(text: str, correct: bool):
    """Show feedback in target language during immersion."""
    style = "bold green" if correct else "bold red"
    console.print(f"  [{style}]{text}[/{style}]")


def show_back_translation_step(step: int, word: str,
                                romanization: str = ""):
    """Show back-translation step indicator."""
    labels = {1: "Zielsprache \u2192 Deutsch", 2: "Deutsch \u2192 Zielsprache"}
    display = word
    if romanization:
        display += f" ({romanization})"
    console.print(
        f"\n  Schritt {step}: [bold]{labels.get(step, '')}[/bold]"
    )
    console.print(f"  [bold]{display}[/bold]")


def show_drill_summary(drill_type: str, attempted: int, correct: int,
                        duration_seconds: int, avg_ms: int = 0):
    """Show drill session summary."""
    pct = round(correct / max(attempted, 1) * 100)
    duration_str = f"{duration_seconds // 60}:{duration_seconds % 60:02d}"

    content = (
        f"Typ: [bold]{drill_type}[/bold]\n"
        f"Ergebnis: [bold]{correct}/{attempted}[/bold] ({pct}%)\n"
        f"Dauer: {duration_str}"
    )
    if avg_ms > 0:
        content += f"\nDurchschnittliche Reaktionszeit: {avg_ms}ms"

    console.print(Panel(
        content,
        border_style="bold cyan",
        title="\U0001f4ca DRILL-ERGEBNIS",
    ))
