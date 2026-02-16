"""Advanced statistics UI — Rich ASCII charts and tables."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from rich import box
from rich.panel import Panel
from rich.table import Table

from ui.terminal import console

if TYPE_CHECKING:
    from app import AppContext

logger = logging.getLogger(__name__)


def run_statistics_ui(app: AppContext) -> None:
    """Main advanced statistics interface."""
    from ui import terminal as ui

    while True:
        ui.clear_screen()
        console.print("\n  [bold]\U0001f4ca ERWEITERTE STATISTIKEN[/bold]\n")
        console.print("  [1] Retention-Kurve (30 Tage)")
        console.print("  [2] Schwache Bereiche")
        console.print("  [3] Lerngeschwindigkeit")
        console.print("  [4] Kategorien-Aufschluesselung")
        console.print("  [5] Sprachvergleich")
        console.print("  [0] Zurueck\n")

        choice = ui.ask_int(">", default=0)

        if choice == 0:
            return
        elif choice == 1:
            _show_retention_curve(app)
        elif choice == 2:
            _show_weak_areas(app)
        elif choice == 3:
            _show_learning_velocity(app)
        elif choice == 4:
            _show_category_breakdown(app)
        elif choice == 5:
            _show_language_comparison(app)

        ui.wait_for_enter()


def _show_retention_curve(app: AppContext) -> None:
    """Display retention curve as ASCII bar chart."""
    from ui import terminal as ui
    ui.clear_screen()

    data = app.statistics_engine.retention_curve(30)
    console.print(Panel(
        "[bold]Retention-Kurve (30 Tage)[/bold]",
        border_style="cyan",
    ))

    if not any(d["total"] > 0 for d in data):
        console.print("  Noch keine Review-Daten vorhanden.")
        return

    for d in data:
        if d["total"] == 0:
            continue
        bar_len = d["rate"] // 5
        bar = "\u2588" * bar_len + "\u2591" * (20 - bar_len)
        day = d["date"][-5:]  # MM-DD
        console.print(f"  {day} [{bar}] {d['rate']}% ({d['correct']}/{d['total']})")


def _show_weak_areas(app: AppContext) -> None:
    """Display words that need the most practice."""
    from ui import terminal as ui
    ui.clear_screen()

    words = app.statistics_engine.weak_areas(15)
    if not words:
        console.print("  Noch nicht genug Daten fuer schwache Bereiche.")
        return

    table = Table(
        title="\U0001f534 Schwache Bereiche",
        box=box.ROUNDED,
        border_style="red",
    )
    table.add_column("Sprache", width=12)
    table.add_column("Wort", min_width=15)
    table.add_column("Bedeutung", min_width=15)
    table.add_column("Ease", width=6)
    table.add_column("Richtig", width=10)

    for w in words:
        word_display = w["word"]
        if w.get("romanization"):
            word_display += f" ({w['romanization']})"
        reviews = w.get("total_reviews", 0) or 0
        correct = w.get("correct_reviews", 0) or 0
        pct = round(correct / max(reviews, 1) * 100)
        table.add_row(
            f"{w.get('flag', '')} {w.get('lang_name', '')}",
            word_display,
            w["meaning_de"],
            f"{w['ease_factor']:.1f}",
            f"{correct}/{reviews} ({pct}%)",
        )

    console.print(table)


def _show_learning_velocity(app: AppContext) -> None:
    """Display learning velocity stats."""
    from ui import terminal as ui
    ui.clear_screen()

    vel = app.statistics_engine.learning_velocity(30)

    trend_emoji = {
        "up": "\u2b06\ufe0f",
        "down": "\u2b07\ufe0f",
        "stable": "\u27a1\ufe0f",
    }

    console.print(Panel(
        f"[bold]Lerngeschwindigkeit (30 Tage)[/bold]\n\n"
        f"  Gesamt gelernt: [bold]{vel['total']}[/bold] Woerter\n"
        f"  Durchschnitt: [bold]{vel['average_per_day']}[/bold] pro Tag\n"
        f"  Trend: {trend_emoji.get(vel['trend'], '')} {vel['trend_pct']:+d}%",
        border_style="cyan",
    ))

    # Mini sparkline of last 14 days
    counts = [d["count"] for d in vel["daily_counts"][-14:]]
    if any(c > 0 for c in counts):
        max_c = max(counts) or 1
        console.print("\n  Letzte 14 Tage:")
        for d in vel["daily_counts"][-14:]:
            bar_len = round(d["count"] / max_c * 20)
            bar = "\u2588" * bar_len
            day = d["date"][-5:]
            console.print(f"  {day} {bar} {d['count']}")


def _show_category_breakdown(app: AppContext) -> None:
    """Display performance by word category."""
    from ui import terminal as ui
    ui.clear_screen()

    data = app.statistics_engine.category_breakdown()
    if not data:
        console.print("  Noch keine Daten vorhanden.")
        return

    from config import CATEGORY_LABELS
    table = Table(
        title="\U0001f4ca Kategorien-Aufschluesselung",
        box=box.ROUNDED,
        border_style="blue",
    )
    table.add_column("Kategorie", min_width=20)
    table.add_column("Woerter", width=8)
    table.add_column("Ease", width=6)
    table.add_column("Genauigkeit", width=12)

    for d in data:
        label = CATEGORY_LABELS.get(d["category"], d["category"])
        table.add_row(
            label,
            str(d["total_words"]),
            f"{d['avg_ease']:.1f}",
            f"{d['accuracy']}%",
        )

    console.print(table)


def _show_language_comparison(app: AppContext) -> None:
    """Display cross-language comparison table."""
    from ui import terminal as ui
    ui.clear_screen()

    data = app.statistics_engine.language_comparison()
    if not data:
        console.print("  Noch keine Daten vorhanden.")
        return

    table = Table(
        title="\U0001f30d Sprachvergleich",
        box=box.ROUNDED,
        border_style="green",
    )
    table.add_column("Sprache", min_width=14)
    table.add_column("Gelernt", width=10)
    table.add_column("Fortschritt", width=12)
    table.add_column("Ease", width=6)
    table.add_column("Genauigkeit", width=12)

    for d in data:
        table.add_row(
            f"{d['flag']} {d['name']}",
            f"{d['learned']}/{d['total']}",
            f"{d['pct']}%",
            f"{d['avg_ease']:.1f}",
            f"{d['accuracy']}%",
        )

    console.print(table)
