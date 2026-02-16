"""Speed learning UI — keyword cards, micro-session timer, chain display,
hint progression."""

from __future__ import annotations

from rich.panel import Panel
from rich.table import Table
from rich import box

from ui.terminal import console


def show_keyword_card(word: dict, keyword: str, story: str = ""):
    """Display a keyword mnemonic card."""
    w = word.get("word", "")
    rom = word.get("romanization", "")
    meaning = word.get("meaning_de", "")

    content = f"[bold]{w}[/bold]"
    if rom:
        content += f"  ({rom})"
    content += f"\n= {meaning}\n\n"
    content += f"\U0001f511 Keyword: [bold yellow]{keyword}[/bold yellow]"
    if story:
        content += f"\n\U0001f4d6 Story: [italic]{story}[/italic]"

    console.print(Panel(content, border_style="yellow", title="\U0001f511 Keyword-Methode"))


def show_micro_session_header(count: int, lang: str = ""):
    """Show micro-session header with timer info."""
    lang_str = f" — {lang}" if lang else ""
    console.print(Panel(
        f"[bold]\u23f1\ufe0f  MICRO-SESSION{lang_str}[/bold]\n"
        f"{count} Woerter | 2 Minuten | Schnell & fokussiert",
        border_style="bold cyan",
    ))


def show_interleaved_header(count: int, lang_count: int):
    """Show interleaved session header."""
    console.print(Panel(
        f"[bold]\U0001f500 INTERLEAVING SESSION[/bold]\n"
        f"{count} Woerter | {lang_count} Sprachen | Maximale Diversitaet",
        border_style="bold green",
    ))


def show_dual_coding(word: dict, scene: str):
    """Show word with emoji visual scene."""
    w = word.get("word", "")
    meaning = word.get("meaning_de", "")

    console.print(Panel(
        f"[bold]{w}[/bold] = {meaning}\n\n"
        f"  {scene}",
        border_style="magenta",
        title="\U0001f3a8 Dual Coding",
    ))


def show_recall_chain_status(chain_length: int, best: int):
    """Show current chain length and record."""
    bar = "\U0001f517" * chain_length if chain_length > 0 else "\u2500"
    console.print(
        f"\n  \U0001f517 Kette: {bar}  Laenge: [bold]{chain_length}[/bold] "
        f"| Rekord: [bold yellow]{best}[/bold yellow]"
    )


def show_chain_break(chain_length: int, best: int):
    """Show chain break message."""
    msg = f"Kette gerissen bei [bold]{chain_length}[/bold]!"
    if chain_length > best:
        msg += f"\n\U0001f389 [bold yellow]NEUER REKORD![/bold yellow]"
    console.print(Panel(msg, border_style="red", title="\U0001f4a5 Kettenbruch"))


def show_error_drill_header(count: int, lang: str = ""):
    """Show error-focused drill header."""
    lang_str = f" — {lang}" if lang else ""
    console.print(Panel(
        f"[bold]\U0001f6a8 FEHLER-DRILLING{lang_str}[/bold]\n"
        f"{count} schwierige Woerter | Intensives Training",
        border_style="bold red",
    ))


def show_progressive_hint(hint: str, level: int):
    """Show a progressive hint."""
    console.print(
        f"  \U0001f4a1 Hinweis (Stufe {level}): [bold yellow]{hint}[/bold yellow]"
    )


def show_speed_menu() -> str:
    """Show speed learning submenu."""
    console.print(Panel(
        "[bold]\u26a1 SPEED-LEARNING[/bold]",
        border_style="bold yellow",
    ))

    items = [
        ("[1]", "\U0001f511", "Keyword-Methode", "Phonetische Eselsbruecken"),
        ("[2]", "\u23f1\ufe0f ", "Micro-Session", "2-Minuten-Sprint"),
        ("[3]", "\U0001f500", "Interleaving", "Gemischtes Training"),
        ("[4]", "\U0001f3a8", "Dual Coding", "Wort + Bild"),
        ("[5]", "\U0001f517", "Recall-Kette", "Wort-Assoziationskette"),
        ("[6]", "\U0001f6a8", "Fehler-Drilling", "Schwaechen gezielt ueben"),
        ("[7]", "\U0001f4a1", "Progressive Hints", "Buchstabe fuer Buchstabe"),
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
