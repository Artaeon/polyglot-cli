"""Gamification UI — XP gain display, level-up, achievements panel."""

from __future__ import annotations

from rich.panel import Panel
from rich.table import Table
from rich import box

from ui.terminal import console, show_progress_bar


def show_xp_gain(xp_info: dict):
    """Show inline XP gain after an action."""
    total = xp_info["total_xp"]
    parts = [f"[bold yellow]+{total} XP[/bold yellow]"]

    if xp_info.get("streak_bonus", 1.0) > 1.0:
        bonus_pct = round((xp_info["streak_bonus"] - 1.0) * 100)
        parts.append(f"[dim](Streak +{bonus_pct}%)[/dim]")

    console.print(f"  \u2b50 {' '.join(parts)}")

    # Show newly unlocked achievements
    for a in xp_info.get("newly_unlocked", []):
        console.print(
            f"\n  \U0001f3c6 [bold magenta]ACHIEVEMENT FREIGESCHALTET![/bold magenta]"
        )
        console.print(
            f"  {a['icon']} [bold]{a['name_de']}[/bold] — {a['description_de']}"
        )
        if a.get("xp_reward"):
            console.print(
                f"  [yellow]+{a['xp_reward']} Bonus-XP![/yellow]"
            )


def show_level_up(old_level: int, new_level: int, rank: str):
    """Celebrate a level-up."""
    console.print()
    console.print(Panel(
        f"\U0001f389 [bold yellow]LEVEL UP![/bold yellow]\n\n"
        f"Level {old_level} \u2192 [bold]{new_level}[/bold]\n"
        f"Rang: [bold magenta]{rank}[/bold magenta]",
        border_style="bold yellow",
        title="\u2b50 AUFSTIEG \u2b50",
    ))


def show_xp_bar(level_info: dict):
    """Show compact XP bar for dashboard."""
    level = level_info["level"]
    rank = level_info["rank"]
    progress = level_info["progress"]
    needed = level_info["needed"]
    total_xp = level_info["total_xp"]

    bar = show_progress_bar(progress, needed, color="yellow")
    console.print(
        f"  \u2b50 Level [bold]{level}[/bold] ({rank}) | "
        f"{bar} | {total_xp} XP total"
    )


def show_achievements_panel(achievements_by_cat: dict, xp_summary: dict):
    """Full achievements & XP overview panel."""
    console.print()
    console.print(Panel(
        f"[bold]\U0001f3c6 ERFOLGE & XP[/bold]",
        border_style="bold yellow",
    ))

    # XP summary
    show_xp_bar(xp_summary)
    console.print(
        f"  Heute: [bold]+{xp_summary['today_xp']}[/bold] XP | "
        f"Streak: [bold]{xp_summary['streak']}[/bold] Tage"
    )
    console.print()

    cat_labels = {
        "words": "\U0001f4da Wort-Meilensteine",
        "streak": "\U0001f525 Streak-Meilensteine",
        "language": "\U0001f30d Sprach-Meilensteine",
        "family": "\U0001f517 Familien-Meilensteine",
        "session": "\U0001f504 Session-Meilensteine",
    }

    for cat, achievements in achievements_by_cat.items():
        label = cat_labels.get(cat, cat.title())
        table = Table(
            title=label,
            box=box.SIMPLE,
            show_header=False,
            padding=(0, 1),
            expand=False,
        )
        table.add_column("Icon", width=3)
        table.add_column("Name", min_width=18)
        table.add_column("Beschreibung", min_width=25)
        table.add_column("Status", width=12)

        for a in achievements:
            icon = a["icon"]
            name = a["name_de"]
            desc = a["description_de"] or ""
            if a["unlocked_at"]:
                status = "\u2705 Freigeschaltet"
                style = "green"
            else:
                status = "\U0001f512 Gesperrt"
                style = "dim"

            table.add_row(icon, name, desc, status, style=style)

        console.print(table)
        console.print()
