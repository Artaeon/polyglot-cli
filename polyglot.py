#!/usr/bin/env python3
"""PolyglotCLI — Cluster Language Learner for 22+ languages."""

from __future__ import annotations

import json
import logging
import signal
import sys
from datetime import date
from pathlib import Path

import click

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app import AppContext
from config import (
    DEFAULT_SPRINT_DAYS, DEFAULT_DAILY_MINUTES,
)
from ui import terminal as ui
from ui.terminal import console
from utils.data_loader import DataLoader

logger = logging.getLogger(__name__)


# ── Data Loading ──────────────────────────────────────────────

def load_data_if_needed(app: AppContext) -> None:
    """Load vocabulary and language data into DB if not already loaded."""
    loader = DataLoader(app.db)
    ui.show_message("Pruefe Sprachdaten...")
    stats = loader.load_if_needed()

    total = stats["languages"] + stats["words"] + stats["concepts"]
    if total == 0:
        return

    ui.show_success(
        "Sprachdaten aktualisiert: "
        f"{stats['languages']} Sprachen, "
        f"{stats['words']} Woerter, "
        f"{stats['concepts']} Konzepte"
    )


# ── Setup Wizard ──────────────────────────────────────────────

def run_setup_wizard(app: AppContext) -> None:
    """First-time setup wizard."""
    ui.clear_screen()
    console.print("""
  [bold]\U0001f30d Willkommen bei PolyglotCLI![/bold]
  \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500

  Lass uns dein Profil einrichten.
""")

    name = ui.ask_text("Dein Name:", default="Lerner")
    app.db.set_setting("user_name", name)

    console.print("""
  Welche Sprachen sprichst du bereits?
  [1] \U0001f1e9\U0001f1ea Deutsch (Muttersprache)
  [2] \U0001f1ec\U0001f1e7 Englisch
  [3] \U0001f1f7\U0001f1fa Russisch (Grundkenntnisse)
  [0] Fertig
""")
    known = ui.ask_text("Auswahl (z.B. 1,2,3):", default="1,2,3")
    known_langs = []
    if "1" in known:
        known_langs.append("de")
    if "2" in known:
        known_langs.append("en")
    if "3" in known:
        known_langs.append("ru")
    app.db.set_setting("known_languages", json.dumps(known_langs))

    console.print("""
  Wie viele Minuten pro Tag moechtest du lernen?
  [1] 30 Min (entspannt)
  [2] 60 Min (ambitioniert)
  [3] 90 Min (Intensiv-Sprint)
  [4] Eigene Angabe
""")
    choice = ui.ask_int("Auswahl:", default=3)
    minutes_map = {1: 30, 2: 60, 3: 90}
    if choice in minutes_map:
        daily_min = minutes_map[choice]
    else:
        daily_min = ui.ask_int("Minuten pro Tag:", default=90)
    app.db.set_setting("daily_minutes", str(daily_min))

    sprint_days = DEFAULT_SPRINT_DAYS
    if ui.ask_confirm(f"Sprint-Dauer: {sprint_days} Tage?", default=True):
        app.db.set_setting("sprint_days", str(sprint_days))
    else:
        sprint_days = ui.ask_int("Sprint-Tage:", default=30)
        app.db.set_setting("sprint_days", str(sprint_days))

    app.db.set_setting("sprint_start", date.today().isoformat())
    app.db.set_setting("setup_done", "1")

    console.print(f"""
  \u2705 [bold green]Profil erstellt![/bold green]
  Dein {sprint_days}-Tage-Sprint startet JETZT.
""")

    if "ru" in known_langs:
        console.print("""  Deine Russisch-Kenntnisse geben dir einen Vorsprung:
    \u2192 ~85% Transfer zu Ukrainisch & Belarussisch
    \u2192 ~40-50% Transfer zu Slowakisch & Bulgarisch
    \u2192 Slawische Gruppe wird dein staerkstes Cluster!
""")

    ui.wait_for_enter()


# ── Main Menu Loop ───────────────────────────────────────────

def main_menu(app: AppContext) -> None:
    """Main interactive menu loop."""
    from commands.review_cmd import run_review
    from commands.learn_cmd import run_learn_new, run_palace_management
    from commands.quiz_cmd import run_cloze, run_conjugation, run_builder
    from commands.speed_cmd import run_speed_learning
    from commands.cia_cmd import run_cia_drills
    from commands.misc_cmd import (
        run_cluster_comparison, run_search, run_statistics,
        run_dashboard, run_settings, run_achievements,
        run_sentence_translation, run_export,
    )

    app.start_session()

    while True:
        ui.clear_screen()
        ui.show_banner()

        sprint_day = app.db.get_sprint_day()
        sprint_days = int(app.db.get_setting("sprint_days", "30"))
        ui.show_welcome(sprint_day, sprint_days)

        due = app.db.get_due_count_by_language()
        total_due = sum(due.values())

        choice = ui.show_main_menu()

        try:
            if choice == "1":
                run_dashboard(app)
            elif choice == "2":
                run_cluster_comparison(app)
            elif choice == "3":
                if total_due > 0:
                    console.print(
                        f"\n  {total_due} Karten faellig. "
                        "Alle reviewen oder nach Sprache filtern?"
                    )
                    console.print("  [1] Alle  [2] Nach Sprache filtern")
                    filter_choice = ui.ask_int(">", default=1)
                    if filter_choice == 2:
                        languages = app.db.get_all_languages()
                        lang_id = ui.show_language_selector(
                            languages, "Sprache filtern"
                        )
                        run_review(app, lang_id)
                    else:
                        run_review(app)
                else:
                    run_review(app)
            elif choice == "4":
                run_learn_new(app)
            elif choice == "5":
                run_sentence_translation(app)
            elif choice == "6":
                run_palace_management(app)
            elif choice == "7":
                run_statistics(app)
            elif choice == "8":
                run_search(app)
            elif choice == "9":
                run_settings(app)
            elif choice == "10":
                run_cloze(app)
            elif choice == "11":
                run_conjugation(app)
            elif choice == "12":
                run_builder(app)
            elif choice == "13":
                _run_daily_challenge(app)
            elif choice == "14":
                _run_custom_vocab(app)
            elif choice == "15":
                _run_advanced_stats(app)
            elif choice == "a":
                run_achievements(app)
            elif choice == "c":
                run_cia_drills(app)
            elif choice == "s":
                run_speed_learning(app)
            elif choice in ("q", "quit", "exit"):
                app.end_session("mixed")
                console.print(
                    "\n  [bold]Tschuess! Bis morgen! \U0001f30d[/bold]\n"
                )
                break
        except KeyboardInterrupt:
            continue
        except Exception as e:
            logger.exception("Error in main menu")
            ui.show_error(f"Fehler: {e}")
            ui.wait_for_enter()


def _run_daily_challenge(app: AppContext) -> None:
    """Run daily challenge from menu."""
    if not app.daily_challenge_engine:
        ui.show_error("Daily Challenge Engine nicht verfuegbar.")
        ui.wait_for_enter()
        return
    from ui.daily_challenge_ui import run_daily_challenge_ui
    run_daily_challenge_ui(app)


def _run_custom_vocab(app: AppContext) -> None:
    """Run custom vocabulary management from menu."""
    if not app.custom_vocab_engine:
        ui.show_error("Custom Vocab Engine nicht verfuegbar.")
        ui.wait_for_enter()
        return
    from commands.misc_cmd import run_custom_vocab_menu
    run_custom_vocab_menu(app)


def _run_advanced_stats(app: AppContext) -> None:
    """Run advanced statistics from menu."""
    if not app.statistics_engine:
        ui.show_error("Statistik-Engine nicht verfuegbar.")
        ui.wait_for_enter()
        return
    from ui.statistics_ui import run_statistics_ui
    run_statistics_ui(app)


# ── CLI Interface ────────────────────────────────────────────

def _setup_logging(verbose: bool = False) -> None:
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(name)s %(levelname)s: %(message)s",
        handlers=[
            logging.FileHandler("polyglot.log", encoding="utf-8"),
        ],
    )
    if verbose:
        logging.getLogger().addHandler(logging.StreamHandler())


@click.group(invoke_without_command=True)
@click.option("--verbose", is_flag=True, help="Enable debug logging")
@click.pass_context
def cli(ctx, verbose):
    """PolyglotCLI — Cluster Language Learner fuer 22+ Sprachen."""
    _setup_logging(verbose)

    app = AppContext()
    app.init()
    ctx.obj = app

    load_data_if_needed(app)

    # Check first-time setup
    if app.db.get_setting("setup_done") != "1":
        run_setup_wizard(app)

    if ctx.invoked_subcommand is None:
        main_menu(app)


@cli.command()
@click.argument("word")
@click.pass_obj
def cluster(app, word):
    """Cluster-Vergleich: Zeige ein Wort in allen 22 Sprachen."""
    from commands.misc_cmd import run_cluster_comparison
    run_cluster_comparison(app, word)


@cli.command()
@click.option("--lang", default=None, help="Sprache filtern (z.B. ru, sk)")
@click.pass_obj
def review(app, lang):
    """SRS Review-Session starten."""
    from commands.review_cmd import run_review
    app.start_session()
    run_review(app, lang)
    app.end_session("review")


@cli.command()
@click.argument("lang", required=False)
@click.pass_obj
def learn(app, lang):
    """Neue Woerter lernen (Memory Palace)."""
    from commands.learn_cmd import run_learn_new
    app.start_session()
    run_learn_new(app, lang)
    app.end_session("new_words")


@cli.command()
@click.argument("lang", required=False)
@click.pass_obj
def palace(app, lang):
    """Memory Palace anzeigen/verwalten."""
    from commands.learn_cmd import run_palace_management
    if lang:
        palace_info = app.palace_engine.get_palace_info(lang)
        if palace_info:
            ui.show_palace_header(palace_info)
            ui.show_palace_overview(palace_info)
            ui.wait_for_enter()
        else:
            ui.show_error(f"Sprache '{lang}' nicht gefunden!")
    else:
        run_palace_management(app)


@cli.command()
@click.pass_obj
def dashboard(app):
    """Dashboard und Tagesplan anzeigen."""
    from commands.misc_cmd import run_dashboard
    run_dashboard(app)


@cli.command()
@click.pass_obj
def stats(app):
    """Detaillierte Statistiken anzeigen."""
    from commands.misc_cmd import run_statistics
    run_statistics(app)


@cli.command()
@click.argument("sentence", required=False)
@click.pass_obj
def translate(app, sentence):
    """Satz in alle 22 Sprachen uebersetzen."""
    from commands.misc_cmd import run_sentence_translation
    if sentence:
        match = app.sentence_engine.find_best_match(sentence)
        if match:
            data = app.sentence_engine.get_sentence_translations(match)
            ui.show_sentence_translations(data)
        else:
            results = app.sentence_engine.word_by_word_lookup(sentence)
            ui.show_word_lookup_results(results)
    else:
        run_sentence_translation(app)


@cli.command()
@click.argument("query")
@click.pass_obj
def search(app, query):
    """Wort suchen ueber alle Sprachen."""
    from commands.misc_cmd import run_search
    run_search(app, query)


@cli.command(name="export")
@click.pass_obj
def export_cmd(app):
    """Fortschritt als JSON exportieren."""
    from commands.misc_cmd import run_export
    run_export(app)


@cli.command()
@click.pass_obj
def micro(app):
    """Micro-Session: 2-Minuten-Sprint."""
    from commands.speed_cmd import _run_micro_session
    app.start_session()
    _run_micro_session(app)
    app.end_session("micro")


@cli.command(name="init")
@click.pass_obj
def init_cmd(app):
    """Ersteinrichtung starten."""
    run_setup_wizard(app)


# ── Entry Point ──────────────────────────────────────────────

def handle_sigint(sig, frame):
    """Handle Ctrl+C gracefully."""
    console.print("\n\n  Sitzung gespeichert. Tschuess! \U0001f30d\n")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_sigint)
    cli()
