"""Rich terminal UI — colors, tables, progress bars, panels."""

from __future__ import annotations

import os
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.markdown import Markdown
from rich import box

from config import FAMILY_COLORS, FAMILY_LABELS, FAMILY_EMOJIS, CEFR_LEVELS

console = Console()


def clear_screen():
    """Clear terminal screen."""
    if os.environ.get("POLYGLOT_NO_CLEAR"):
        return
    console.clear()


def show_banner():
    """Show the main application banner."""
    banner = Text()
    banner.append("\n   \U0001f30d POLYGLOT CLI", style="bold white")
    banner.append(" — Cluster Language Learner\n", style="white")
    banner.append("   " + "\u2500" * 45 + "\n", style="dim")
    banner.append("   22 Sprachen \u00b7 4 Familien \u00b7 1 System\n", style="dim cyan")

    console.print(Panel(banner, box=box.DOUBLE, border_style="bold cyan",
                        padding=(0, 2)))


def show_welcome(sprint_day: int, sprint_days: int):
    """Show welcome message with sprint info."""
    console.print(
        f"\n  Willkommen zur\u00fcck! Tag [bold]{sprint_day}[/bold] "
        f"deines {sprint_days}-Tage-Sprints.\n",
        style="white",
    )


def show_main_menu() -> str:
    """Display main menu and get user choice."""
    menu_items = [
        ("[1]", "\U0001f4ca", "Dashboard & Tagesplan"),
        ("[2]", "\U0001f517", "Cluster-Vergleich", "Wort in allen Sprachen"),
        ("[3]", "\U0001f504", "Review (SRS Quiz)"),
        ("[4]", "\U0001f9e0", "Neue W\u00f6rter lernen", "Memory Palace"),
        ("[5]", "\U0001f4dd", "Satz\u00fcbersetzen", "Satz in alle 22 Sprachen"),
        ("[6]", "\U0001f3db\ufe0f ", "Pal\u00e4ste verwalten"),
        ("[7]", "\U0001f4c8", "Statistiken & Export"),
        ("[8]", "\U0001f50d", "Wort suchen"),
        ("[9]", "\u2699\ufe0f ", "Einstellungen"),
        ("[10]", "\U0001f4dd", "L\u00fcckentext", "Cloze-\u00dcbungen"),
        ("[11]", "\U0001f4d6", "Konjugation", "Verb-Drills"),
        ("[12]", "\U0001f3d7\ufe0f ", "Satzbau", "S\u00e4tze konstruieren"),
        ("[a]", "\U0001f3c6", "Erfolge & XP"),
        ("[c]", "\U0001f575\ufe0f ", "CIA-Drills", "Intensiv-Training"),
        ("[s]", "\u26a1", "Speed-Learning", "Ultra-schnell lernen"),
        ("[q]", "", "Beenden"),
    ]

    for item in menu_items:
        key, emoji, label = item[0], item[1], item[2]
        hint = f"  \u2190 {item[3]}" if len(item) > 3 else ""
        style = "dim" if key == "[q]" else "white"
        console.print(f"  {key} {emoji} {label}[dim]{hint}[/dim]", style=style)

    console.print()
    return Prompt.ask("  >", default="1").strip().lower()


def show_due_badge(count: int):
    """Show badge for due reviews."""
    if count > 0:
        console.print(
            f"  [bold yellow]\u2190 {count} Karten f\u00e4llig![/bold yellow]"
        )


# ── Cluster Display ───────────────────────────────────────────

def show_cluster_comparison(cluster_data: dict):
    """Display the full cluster comparison for a concept."""
    concept = cluster_data["concept"]
    families = cluster_data["families"]

    console.print()
    console.print(Panel(
        f'[bold]\U0001f517 CLUSTER-VERGLEICH: "{concept.get("de", "")}" '
        f'({concept.get("en", "")})[/bold]',
        border_style="bold cyan",
    ))

    for family, entries in families.items():
        color = FAMILY_COLORS.get(family, "white")
        emoji = FAMILY_EMOJIS.get(family, "")
        label = FAMILY_LABELS.get(family, family.upper())

        table = Table(
            box=box.ROUNDED,
            border_style=color,
            title=f"{emoji} {label}",
            title_style=f"bold {color}",
            show_header=False,
            padding=(0, 1),
            expand=False,
        )
        table.add_column("Flag", width=4)
        table.add_column("Wort", min_width=15)
        table.add_column("Info", min_width=25)

        for entry in entries:
            word_display = entry["word"]
            if entry.get("romanization"):
                word_display += f"  ({entry['romanization']})"

            # Status / similarity info
            if entry.get("learned"):
                info = "\u2705 gelernt"
            elif entry.get("similarity_to"):
                sim = entry["similarity_to"]
                # Get first similarity reference
                for ref_lang, score in sim.items():
                    if isinstance(score, (int, float)):
                        if score >= 0.95:
                            info = f"\u2248 identisch mit {ref_lang.upper()}"
                        elif score >= 0.85:
                            info = f"\u2248 {int(score*100)}% \u00e4hnlich"
                        elif score >= 0.70:
                            info = f"\u2248 {int(score*100)}% \u00e4hnlich"
                        else:
                            info = f"\u2248 {int(score*100)}% verwandt"
                        break
                    elif isinstance(score, str):
                        info = score
                        break
                else:
                    info = "\u2b1c neu"
            else:
                info = "\u2b1c neu"

            # Add note if present
            if entry.get("note"):
                info += f"  ({entry['note']})"

            table.add_row(entry["flag"], word_display, info)

        console.print(table)

        # Family efficiency hint
        count = len(entries)
        if count > 1:
            console.print(
                f"  \U0001f4a1 1 Wort gelernt \u2192 {count} Sprachen abgedeckt!",
                style=f"italic {color}",
            )
        console.print()

    # Reference languages
    ref_table = Table(
        box=box.ROUNDED,
        border_style="cyan",
        title="\U0001f537 Referenz (deine Sprachen)",
        title_style="bold cyan",
        show_header=False,
        padding=(0, 1),
        expand=False,
    )
    ref_table.add_column("Flag", width=4)
    ref_table.add_column("Wort", min_width=15)
    ref_table.add_column("Info", min_width=25)
    ref_table.add_row("\U0001f1e9\U0001f1ea", concept.get("de", ""),
                      "\U0001f3e0 Muttersprache")
    ref_table.add_row("\U0001f1ec\U0001f1e7", concept.get("en", ""),
                      "\U0001f3e0 flie\u00dfend")
    console.print(ref_table)

    # Overall efficiency
    console.print()
    console.print(Panel(
        f"\U0001f4ca Effizienz: {cluster_data['efficiency_msg']}",
        border_style="bold green",
    ))

    # Etymology and mnemonic
    if concept.get("etymology_note"):
        console.print(
            f"\n  \U0001f4dc [italic]{concept['etymology_note']}[/italic]"
        )
    if concept.get("mnemonic_hint"):
        console.print(
            f"  \U0001f4a1 [italic]{concept['mnemonic_hint']}[/italic]"
        )
    console.print()


# ── Quiz Display ──────────────────────────────────────────────

def show_quiz_header(lang_name: str, flag: str, card_num: int,
                     total: int, mode: str = "REVIEW"):
    """Show quiz card header."""
    console.print()
    console.print(Panel(
        f"\U0001f504 {mode} \u2014 {flag} {lang_name} \u2014 "
        f"Karte {card_num}/{total}",
        border_style="bold yellow",
    ))


def show_recognition_quiz(quiz_card: dict) -> Optional[int]:
    """Display multiple choice quiz and get answer."""
    console.print(f'\n  Was bedeutet "[bold]{quiz_card["question"]}[/bold]"?\n')

    for i, opt in enumerate(quiz_card["options"], 1):
        console.print(f"  [{i}] {opt['text']}")

    console.print()
    try:
        choice = IntPrompt.ask("  >", default=1)
        if 1 <= choice <= len(quiz_card["options"]):
            return choice - 1
    except (ValueError, KeyboardInterrupt):
        pass
    return None


def show_recall_quiz(quiz_card: dict) -> Optional[str]:
    """Display typing quiz and get answer."""
    lang = quiz_card.get("lang_name", "")
    console.print(
        f'\n  Wie hei\u00dft "[bold]{quiz_card["question"]}[/bold]" auf {lang}?'
    )
    console.print("  [dim](Tipp: Schreib in Transliteration oder Originalschrift)[/dim]\n")

    try:
        return Prompt.ask("  >")
    except KeyboardInterrupt:
        return None


def show_reverse_quiz(quiz_card: dict) -> Optional[str]:
    """Display reverse quiz (target → German)."""
    flag = quiz_card.get("flag", "")
    console.print(f'\n  {flag} "[bold]{quiz_card["question"]}[/bold]" = ?\n')

    try:
        return Prompt.ask("  >")
    except KeyboardInterrupt:
        return None


def show_answer_result(correct: bool, correct_answer: str,
                       cluster_hints: list[dict] = None):
    """Show if answer was correct and cluster hints."""
    if correct:
        console.print(f"\n  \u2705 [bold green]Richtig![/bold green]  {correct_answer}")
    else:
        console.print(
            f"\n  \u274c [bold red]Falsch![/bold red]  "
            f"Richtige Antwort: [bold]{correct_answer}[/bold]"
        )

    if cluster_hints:
        console.print("\n  \U0001f517 Cluster-Verwandte:")
        hint_parts = []
        for h in cluster_hints[:6]:
            word = h["word"]
            if h.get("romanization"):
                word += f" ({h['romanization']})"
            hint_parts.append(f"{h['flag']} {word}")
        console.print("     " + "  ".join(hint_parts))


def show_quality_prompt() -> int:
    """Ask user to rate difficulty (SM-2 quality 0-5)."""
    console.print("\n  Wie schwer war das?")
    grades = [
        ("[0]", "\u2b1b", "Blackout", "keine Ahnung"),
        ("[1]", "\U0001f7e5", "Falsch", "aber jetzt erinnert"),
        ("[2]", "\U0001f7e7", "Schwer", "mit viel M\u00fche erinnert"),
        ("[3]", "\U0001f7e8", "Mittel", "nach Nachdenken"),
        ("[4]", "\U0001f7e9", "Leicht", "erinnert mit kurzem Z\u00f6gern"),
        ("[5]", "\U0001f7e2", "Perfekt", "sofort gewusst"),
    ]
    for key, emoji, label, desc in grades:
        console.print(f"  {key} {emoji} {label} \u2014 {desc}")
    console.print()
    try:
        q = IntPrompt.ask("  >", default=3)
        return max(0, min(5, q))
    except (ValueError, KeyboardInterrupt):
        return 3


def show_review_result(result: dict):
    """Show next review date after rating."""
    console.print(
        f"\n  N\u00e4chste Review: in [bold]{result['interval']}[/bold] "
        f"Tag(en) ({result['next_review_date']})",
        style="dim",
    )


# ── Palace Display ────────────────────────────────────────────

def show_palace_header(palace_info: dict):
    """Show memory palace header."""
    lang = palace_info["language"]
    console.print()
    console.print(Panel(
        f"\U0001f9e0 MEMORY PALACE \u2014 {lang['flag']} {lang['name']}\n"
        f"\U0001f4cd Ort: {palace_info['palace_name']}\n"
        f"\U0001f3a8 Theme: {palace_info['palace_theme']}",
        border_style="bold magenta",
    ))


def show_palace_station(station: dict, total: int, word: dict = None,
                        cluster_hints: list = None, mnemonic: str = ""):
    """Show a single palace station with word."""
    num = station["station_number"]
    name = station["station_name"]

    console.print(
        f"\n  Station {num} von {total}: [bold]{name}[/bold]\n"
    )

    if word:
        display = word.get("word", "")
        rom = word.get("romanization", "")
        meaning = word.get("meaning_de", "")
        hint = word.get("pronunciation_hint", "")

        console.print(f"  Neues Wort: [bold]{display}[/bold] ({meaning})")
        if rom:
            console.print(f"  Romanisierung: {rom}")
        if hint:
            console.print(f"  Aussprache: {hint}")

        if cluster_hints:
            console.print("\n  \U0001f517 Cluster-Verwandte:")
            for h in cluster_hints[:5]:
                w = h["word"]
                if h.get("romanization"):
                    w += f" ({h['romanization']})"
                sim = h.get("similarity", "")
                sim_str = f" \u2248 {int(sim*100)}%" if isinstance(sim, float) else ""
                console.print(f"     {h['flag']} {w}{sim_str}")

        if mnemonic:
            console.print(f"\n  \U0001f4a1 Mnemonic-Vorschlag:")
            console.print(f"  [italic]{mnemonic}[/italic]")


def show_palace_overview(palace_info: dict):
    """Show palace overview with all stations."""
    stations = palace_info["stations"]
    filled = palace_info["filled_stations"]
    total = palace_info["total_stations"]

    table = Table(
        title=f"\U0001f3db\ufe0f  {palace_info['palace_name']} ({filled}/{total} belegt)",
        box=box.ROUNDED,
        border_style="magenta",
    )
    table.add_column("#", width=3, justify="right")
    table.add_column("Station", min_width=15)
    table.add_column("Wort", min_width=15)
    table.add_column("Bedeutung", min_width=15)
    table.add_column("Mnemonic", min_width=20)

    for s in stations:
        num = str(s["station_number"])
        name = s["station_name"]
        word = s.get("word", "") or ""
        meaning = s.get("meaning_de", "") or ""
        mnemonic = s.get("user_mnemonic", "") or ""

        if word:
            style = "green"
            rom = s.get("romanization", "")
            if rom:
                word = f"{word} ({rom})"
        else:
            style = "dim"
            word = "\u2500"
            meaning = "\u2500"

        table.add_row(num, name, word, meaning, mnemonic[:30], style=style)

    console.print(table)


# ── Language Selection ────────────────────────────────────────

def show_language_selector(languages: list[dict],
                           prompt_text: str = "Sprache w\u00e4hlen") -> Optional[str]:
    """Show language selection menu and return chosen language ID."""
    current_family = ""
    for i, lang in enumerate(languages, 1):
        if lang["family"] != current_family:
            current_family = lang["family"]
            color = FAMILY_COLORS.get(current_family, "white")
            label = FAMILY_LABELS.get(current_family, current_family.upper())
            emoji = FAMILY_EMOJIS.get(current_family, "")
            console.print(f"\n  {emoji} [bold {color}]{label}[/bold {color}]")
        console.print(f"  [{i:2d}] {lang['flag']} {lang['name']}")

    console.print(f"\n  [ 0] Zur\u00fcck")
    console.print()

    try:
        choice = IntPrompt.ask(f"  {prompt_text}", default=0)
        if 1 <= choice <= len(languages):
            return languages[choice - 1]["id"]
    except (ValueError, KeyboardInterrupt):
        pass
    return None


# ── Progress Display ──────────────────────────────────────────

def show_progress_bar(current: int, total: int, label: str = "",
                      color: str = "green") -> str:
    """Create a text-based progress bar."""
    width = 19
    filled = int(width * current / max(total, 1))
    filled = min(filled, width)
    bar = "\u2588" * filled + "\u2591" * (width - filled)
    return f"{bar}  {current}/{total}"


def get_level_indicator(level: str) -> str:
    """Get visual indicator for CEFR level."""
    indicators = {
        "pre": "\U0001f195",
        "A1-": "\U0001f4c8",
        "A1": "\U0001f4c8",
        "A1+": "\U0001f4c8",
        "A2-": "\U0001f4c8",
        "A2": "\U0001f525",
        "A2+": "\U0001f525",
        "B1-": "\U0001f525",
    }
    return indicators.get(level, "")


# ── Prompts ───────────────────────────────────────────────────

def ask_text(prompt_text: str, default: str = "") -> str:
    """Simple text prompt."""
    try:
        return Prompt.ask(f"  {prompt_text}", default=default)
    except KeyboardInterrupt:
        return default


def ask_int(prompt_text: str, default: int = 0) -> int:
    """Simple integer prompt."""
    try:
        return IntPrompt.ask(f"  {prompt_text}", default=default)
    except (ValueError, KeyboardInterrupt):
        return default


def ask_confirm(prompt_text: str, default: bool = True) -> bool:
    """Yes/no confirmation prompt."""
    try:
        return Confirm.ask(f"  {prompt_text}", default=default)
    except KeyboardInterrupt:
        return default


def show_message(text: str, style: str = ""):
    """Show a simple message."""
    console.print(f"  {text}", style=style)


def show_error(text: str):
    """Show error message."""
    console.print(f"  \u274c {text}", style="bold red")


def show_success(text: str):
    """Show success message."""
    console.print(f"  \u2705 {text}", style="bold green")


def show_info(text: str):
    """Show info message."""
    console.print(f"  \U0001f4a1 {text}", style="italic cyan")


def wait_for_enter(text: str = "Dr\u00fccke [Enter] zum Fortfahren..."):
    """Wait for user to press enter."""
    try:
        Prompt.ask(f"\n  {text}", default="")
    except KeyboardInterrupt:
        pass


# ── Sentence Translation Display ────────────────────────────

def show_sentence_translations(data: dict):
    """Display a sentence translated into all 22 languages with grammar."""
    sentence = data["sentence"]
    families = data["families"]

    console.print()
    console.print(Panel(
        f'[bold]\U0001f4dd SATZ\u00dcBERSETZUNG[/bold]\n\n'
        f'\U0001f1e9\U0001f1ea [bold]{sentence.get("de", "")}[/bold]\n'
        f'\U0001f1ec\U0001f1e7 {sentence.get("en", "")}\n\n'
        f'[dim]{sentence.get("grammar_note_de", "")}[/dim]',
        border_style="bold cyan",
    ))

    for family, entries in families.items():
        color = FAMILY_COLORS.get(family, "white")
        label = FAMILY_LABELS.get(family, family.upper())
        emoji = FAMILY_EMOJIS.get(family, "")

        table = Table(
            box=box.ROUNDED,
            border_style=color,
            title=f"{emoji} {label}",
            title_style=f"bold {color}",
            show_header=True,
            padding=(0, 1),
            expand=True,
        )
        table.add_column("", width=4)
        table.add_column("Sprache", width=12)
        table.add_column("Satz", min_width=25, ratio=2)
        table.add_column("Aussprache", min_width=20, ratio=1)

        for entry in entries:
            text = entry["text"]
            if entry.get("romanization"):
                text += f"\n[dim]({entry['romanization']})[/dim]"

            pron = entry.get("pronunciation", "")
            if pron:
                pron = f"[italic]{pron}[/italic]"

            table.add_row(
                entry["flag"],
                entry["lang_name"],
                text,
                pron,
            )

        console.print(table)
        console.print()

    # Show grammar details
    console.print(Panel(
        "[bold]\U0001f4da Grammatik-Details[/bold]",
        border_style="bold yellow",
    ))

    for family, entries in families.items():
        color = FAMILY_COLORS.get(family, "white")
        label = FAMILY_LABELS.get(family, family.upper())
        console.print(f"\n  [{color}]{label}[/{color}]")

        for entry in entries:
            if entry.get("grammar"):
                console.print(
                    f"  {entry['flag']} [bold]{entry['lang_name']}[/bold]: "
                    f"[dim]{entry['grammar']}[/dim]"
                )

    console.print()


def show_sentence_categories(categories: list[str]) -> str:
    """Show sentence category selector."""
    cat_labels = {
        "greetings": "\U0001f44b Begr\u00fc\u00dfungen & Basics",
        "introductions": "\U0001f464 Vorstellung",
        "daily_life": "\U0001f3e0 Alltag",
        "travel": "\u2708\ufe0f  Reisen",
        "shopping": "\U0001f6d2 Einkaufen",
        "food": "\U0001f37d\ufe0f  Essen & Trinken",
        "questions": "\u2753 Fragen",
        "feelings": "\u2764\ufe0f  Gef\u00fchle",
        "time": "\u23f0 Zeit",
        "weather": "\u2600\ufe0f  Wetter",
    }

    console.print("\n  Kategorien:")
    for i, cat in enumerate(categories, 1):
        label = cat_labels.get(cat, cat.title())
        console.print(f"  [{i:2d}] {label}")

    console.print(f"\n  [ 0] Zur\u00fcck")
    console.print()

    try:
        choice = IntPrompt.ask("  Kategorie", default=0)
        if 1 <= choice <= len(categories):
            return categories[choice - 1]
    except (ValueError, KeyboardInterrupt):
        pass
    return ""


def show_sentence_list(sentences: list[dict]) -> int:
    """Show list of sentences in a category and return choice index."""
    for i, s in enumerate(sentences, 1):
        console.print(f"  [{i}] {s.get('de', '')}  [dim]({s.get('en', '')})[/dim]")

    console.print(f"\n  [0] Zur\u00fcck")
    console.print()

    try:
        choice = IntPrompt.ask("  Satz w\u00e4hlen", default=0)
        if 1 <= choice <= len(sentences):
            return choice - 1
    except (ValueError, KeyboardInterrupt):
        pass
    return -1


def show_word_lookup_results(results: list[dict]):
    """Show word-by-word lookup results when no template matches."""
    if not results:
        show_error("Kein passender Satz und keine Wort-Treffer gefunden.")
        return

    console.print(Panel(
        "[bold]\U0001f50d Wort-f\u00fcr-Wort Suche[/bold]\n"
        "[dim]Kein exakter Satz gefunden. Hier sind die einzelnen W\u00f6rter:[/dim]",
        border_style="yellow",
    ))

    for result in results:
        word = result["query_word"]
        matches = result["matches"]

        console.print(f'\n  [bold]"{word}"[/bold]:')

        table = Table(box=box.SIMPLE, padding=(0, 1), expand=False)
        table.add_column("", width=4)
        table.add_column("Sprache", width=12)
        table.add_column("Wort", min_width=15)
        table.add_column("Aussprache", min_width=15)

        shown = set()
        for m in matches[:22]:
            lang_key = m.get("language_id", "")
            if lang_key in shown:
                continue
            shown.add(lang_key)

            w = m["word"]
            if m.get("romanization"):
                w += f" ({m['romanization']})"
            pron = m.get("pronunciation_hint", "")

            table.add_row(
                m.get("flag", ""),
                m.get("lang_name", lang_key),
                w,
                pron,
            )

        console.print(table)
