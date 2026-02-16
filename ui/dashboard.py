"""Statistics dashboard for PolyglotCLI."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.text import Text
from rich import box

from config import FAMILY_COLORS, FAMILY_LABELS, FAMILY_EMOJIS
from ui.terminal import show_progress_bar, get_level_indicator, console


def show_dashboard(summary: dict, plan: dict, progress: list[dict],
                   xp_summary: dict = None, daily_status: dict = None):
    """Show the full dashboard with progress and daily plan."""
    sprint_day = summary["sprint_day"]
    sprint_days = summary["sprint_days"]
    streak = summary["streak"]
    time_today = summary["time_today"]
    total_learned = summary["total_learned"]
    cluster_eff = summary["cluster_efficiency"]

    # Header
    console.print()
    console.print(Panel(
        f"[bold]\U0001f4ca POLYGLOT DASHBOARD \u2014 Tag {sprint_day}/{sprint_days}[/bold]",
        border_style="bold cyan",
    ))

    # XP bar (if gamification data available)
    if xp_summary:
        from ui.gamification_ui import show_xp_bar
        show_xp_bar(xp_summary)

    # Summary line
    effective = cluster_eff["effective_total"]
    console.print(
        f"\n  \U0001f525 Streak: [bold]{streak}[/bold] Tage | "
        f"\u23f1\ufe0f  Heute: [bold]{time_today}[/bold] Min | "
        f"\U0001f4da Total: [bold]{effective}[/bold] W\u00f6rter"
    )
    console.print()

    # Progress by family
    _show_family_progress(progress)

    # Cluster efficiency
    console.print()
    _show_cluster_efficiency(cluster_eff)

    # Daily plan
    console.print()
    _show_daily_plan(plan, sprint_day)


def _show_family_progress(progress: list[dict]):
    """Show progress grouped by language family."""
    families_order = ["slavic", "romance", "sinosphere", "uralic"]
    family_counts = {
        "slavic": "10 Sprachen",
        "romance": "5 Sprachen",
        "sinosphere": "4 Sprachen",
        "uralic": "3 Sprachen",
    }

    for family in families_order:
        color = FAMILY_COLORS.get(family, "white")
        emoji = FAMILY_EMOJIS.get(family, "")
        label = FAMILY_LABELS.get(family, family.upper())
        count_label = family_counts.get(family, "")

        console.print(
            f"  {emoji} [bold {color}]{label}[/bold {color}] ({count_label})"
        )

        family_langs = [p for p in progress if p["family"] == family]
        family_langs.sort(key=lambda x: -x["learned"])

        for lang in family_langs:
            bar = show_progress_bar(lang["learned"], max(lang["total"], 200))
            indicator = get_level_indicator(lang["level"])
            name = lang["name"]
            if len(name) > 12:
                name = name[:10] + "."

            console.print(
                f"  {lang['flag']} {name:<12s} {bar}  "
                f"{lang['level']:<4s} {indicator}"
            )

        console.print()


def _show_cluster_efficiency(cluster_eff: dict):
    """Show cluster efficiency stats."""
    unique = cluster_eff["unique_learned"]
    bonus = cluster_eff["transfer_bonus"]
    effective = cluster_eff["effective_total"]
    pct = cluster_eff["efficiency_percent"]

    eff_panel = (
        f"Tats\u00e4chlich gelernt:  [bold]{unique}[/bold] unique W\u00f6rter\n"
        f"Durch Transfer:      [bold green]+{bonus}[/bold green] W\u00f6rter "
        f"(cluster bonus!)\n"
        f"Effektiv:             [bold]{effective}[/bold] W\u00f6rter \u00fcber 22 Sprachen\n"
        f"Transfer-Rate:        [bold green]{pct}%[/bold green] Effizienz \U0001f3af"
    )
    console.print(Panel(
        eff_panel,
        title="\U0001f4c8 CLUSTER-EFFIZIENZ",
        border_style="green",
    ))


def _show_daily_plan(plan: dict, sprint_day: int):
    """Show today's learning plan."""
    from datetime import date
    import locale

    today = date.today()
    weekdays_de = [
        "Montag", "Dienstag", "Mittwoch", "Donnerstag",
        "Freitag", "Samstag", "Sonntag",
    ]
    weekday = weekdays_de[today.weekday()]

    total_due = plan["total_due"]
    due_by_lang = plan["due_by_language"]
    focus = plan.get("focus_languages", [])
    new_words = plan["recommended_new_words"]

    lines = [f"[bold]\U0001f4c5 HEUTE \u2014 {weekday}, Tag {sprint_day}[/bold]\n"]

    # Focus languages
    primary = [f for f in focus if f.get("priority") == "primary"]
    if primary:
        names = ", ".join(f"{f['flag']} {f['name']}" for f in primary)
        lines.append(f"  \U0001f535 Fokus: {names} (45 Min empfohlen)")

    # Due reviews
    if total_due > 0:
        due_parts = []
        for lid, cnt in sorted(due_by_lang.items(), key=lambda x: -x[1])[:5]:
            due_parts.append(f"{lid.upper()} {cnt}")
        due_str = ", ".join(due_parts)
        lines.append(
            f"  \U0001f504 F\u00e4llige Reviews: [bold]{total_due}[/bold] "
            f"Karten ({due_str})"
        )
    else:
        lines.append("  \U0001f504 Keine Reviews f\u00e4llig! \u2705")

    # New words recommendation
    lines.append(f"  \U0001f9e0 Neue W\u00f6rter: +{new_words} empfohlen")

    # Word of the day
    wotd = plan.get("word_of_the_day")
    if wotd:
        lines.append(
            f'  \U0001f517 Cluster des Tages: "{wotd.get("de", "")}" '
            f'\u2014 W\u00f6rter in allen 22 Sprachen'
        )

    console.print(Panel(
        "\n".join(lines),
        border_style="yellow",
    ))


def show_statistics(summary: dict, progress: list[dict],
                    review_stats: dict, forecast: dict,
                    weakest: dict = None, fastest: dict = None):
    """Show detailed statistics view."""
    console.print()
    console.print(Panel(
        "[bold]\U0001f4c8 DETAILLIERTE STATISTIKEN[/bold]",
        border_style="bold cyan",
    ))

    # Review health
    if review_stats.get("total"):
        avg_ease = review_stats.get("avg_ease", 2.5) or 2.5
        total_rev = review_stats.get("total_reviews", 0) or 0
        correct_rev = review_stats.get("correct_reviews", 0) or 0
        retention = round(correct_rev / max(total_rev, 1) * 100)
        health = "gut" if avg_ease > 2.0 else "niedrig"

        console.print(f"\n  \U0001f4ca SRS-Gesundheit:")
        console.print(
            f"     Durchschnittliche Ease: {avg_ease:.2f} ({health})"
        )
        console.print(f"     Retention-Rate: {retention}%")
        console.print(f"     Total Reviews: {total_rev}")

    # Review forecast
    if forecast:
        console.print(f"\n  \U0001f4c5 Review-Vorhersage (n\u00e4chste 7 Tage):")
        for day, count in list(forecast.items())[:7]:
            bar = "\u2588" * min(count, 30) if count > 0 else "\u2500"
            console.print(f"     {day}: {bar} ({count})")

    # Weakest language
    if weakest:
        console.print(
            f"\n  \u26a0\ufe0f  Schw\u00e4chste Sprache: "
            f"{weakest['flag']} {weakest['name']} "
            f"({weakest['retention']}% Retention)"
        )

    # Fastest growing
    if fastest:
        console.print(
            f"  \U0001f680 Am schnellsten wachsend: "
            f"{fastest['flag']} {fastest['name']} "
            f"(+{fastest['new_words']} in 7 Tagen)"
        )

    console.print()


def show_family_tree(progress: list[dict]):
    """Show ASCII art language family tree."""
    console.print()
    console.print(Panel(
        "[bold]\U0001f333 Deine Sprach-Familien[/bold]",
        border_style="bold cyan",
    ))

    prog_map = {p["id"]: p for p in progress}

    def bar(lang_id: str) -> str:
        p = prog_map.get(lang_id, {})
        learned = p.get("learned", 0)
        blocks = min(learned // 20, 10)
        return "\u2588" * max(blocks, 0) or "\u2591"

    tree = f"""
  Proto-Indo-European
  \u251c\u2500\u2500 \U0001f535 Slawisch (Proto-Slavic)
  \u2502   \u251c\u2500\u2500 Ost: \U0001f1f7\U0001f1fa {bar('ru')} \u00b7 \U0001f1fa\U0001f1e6 {bar('uk')} \u00b7 \U0001f1e7\U0001f1fe {bar('be')}
  \u2502   \u251c\u2500\u2500 West: \U0001f1f8\U0001f1f0 {bar('sk')} \u00b7 \U0001f1e8\U0001f1ff {bar('cs')} \u00b7 \U0001f1f5\U0001f1f1 {bar('pl')}
  \u2502   \u2514\u2500\u2500 S\u00fcd:  \U0001f1f8\U0001f1ee {bar('sl')} \u00b7 \U0001f1ed\U0001f1f7 {bar('hr')} \u00b7 \U0001f1e7\U0001f1ec {bar('bg')} \u00b7 \U0001f1f2\U0001f1f0 {bar('mk')}
  \u251c\u2500\u2500 \U0001f7e2 Romanisch (Vulgar Latin)
  \u2502   \u251c\u2500\u2500 \U0001f1ee\U0001f1f9 {bar('it')} \u00b7 \U0001f1ea\U0001f1f8 {bar('es')} \u00b7 \U0001f1f5\U0001f1f9 {bar('pt')}
  \u2502   \u251c\u2500\u2500 \U0001f1eb\U0001f1f7 {bar('fr')}
  \u2502   \u2514\u2500\u2500 \U0001f1f7\U0001f1f4 {bar('ro')} (Br\u00fccke zu Slawisch!)
  \u2514\u2500\u2500 \U0001f537 Germanisch
      \u251c\u2500\u2500 \U0001f1e9\U0001f1ea \u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588 (Basis)
      \u2514\u2500\u2500 \U0001f1ec\U0001f1e7 \u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588 (Basis)

  Ural-Altaisch
  \u2514\u2500\u2500 \U0001f7e1 Uralisch (Proto-Uralic)
      \u251c\u2500\u2500 \U0001f1ed\U0001f1fa {bar('hu')}
      \u2514\u2500\u2500 Finno-Ugrisch: \U0001f1eb\U0001f1ee {bar('fi')} \u00b7 \U0001f1ea\U0001f1ea {bar('et')}

  Sino-Tibetisch
  \u2514\u2500\u2500 \U0001f534 Sinosph\u00e4re
      \u251c\u2500\u2500 \U0001f1e8\U0001f1f3 {bar('zh')} (Basis)
      \u251c\u2500\u2500 \U0001f1ef\U0001f1f5 {bar('ja')} (Kanji-Transfer)
      \u251c\u2500\u2500 \U0001f1f0\U0001f1f7 {bar('ko')} (Sino-Korean)
      \u2514\u2500\u2500 \U0001f1fb\U0001f1f3 {bar('vi')} (Sino-Vietnamese)

  Bar = dein Fortschritt"""

    console.print(tree)
    console.print()
