"""Misc commands — dashboard, stats, search, export, settings, achievements, sentences."""

from __future__ import annotations

import json
import logging
import sys
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

from ui.terminal import console
from ui.dashboard import show_dashboard, show_statistics, show_family_tree
from ui.gamification_ui import show_achievements_panel

if TYPE_CHECKING:
    from app import AppContext

logger = logging.getLogger(__name__)


def run_cluster_comparison(app: AppContext, query: str = "") -> None:
    """Run the cluster comparison feature."""
    from ui import terminal as ui

    ui.clear_screen()
    console.print("\n  [bold]\U0001f517 CLUSTER-VERGLEICH[/bold]")
    console.print("  Gib ein Wort ein (Deutsch oder Englisch):\n")

    if not query:
        query = ui.ask_text("Wort:")
    if not query:
        return

    concept = app.cluster_engine.find_concept(query)
    if not concept:
        results = app.cluster_engine.search_concepts(query)
        if results:
            console.print(f"\n  Gefunden: {len(results)} Ergebnis(se)")
            for i, r in enumerate(results[:10], 1):
                console.print(
                    f"  [{i}] {r.get('de', '')} ({r.get('en', '')})"
                )
            choice = ui.ask_int("\nAuswahl:", default=1)
            if 1 <= choice <= len(results):
                concept = results[choice - 1]
            else:
                return
        else:
            ui.show_error(
                f'Kein Cluster gefunden fuer "{query}". '
                "Versuche ein anderes Wort."
            )
            ui.wait_for_enter()
            return

    cluster_data = app.cluster_engine.get_cluster_data(concept)
    ui.show_cluster_comparison(cluster_data)
    ui.wait_for_enter()


def run_search(app: AppContext, query: str = "") -> None:
    """Search across all languages."""
    from ui import terminal as ui
    from rich.table import Table
    from rich import box

    ui.clear_screen()
    console.print("\n  [bold]\U0001f50d WORT SUCHEN[/bold]\n")

    if not query:
        query = ui.ask_text("Suchbegriff:")
    if not query:
        return

    results = app.db.search_words(query)
    if not results:
        concepts = app.cluster_engine.search_concepts(query)
        if concepts:
            console.print(f"\n  Cluster-Ergebnisse fuer '{query}':")
            for i, c in enumerate(concepts[:5], 1):
                console.print(
                    f"  [{i}] {c.get('de', '')} ({c.get('en', '')})"
                )
            choice = ui.ask_int("\nCluster anzeigen?", default=1)
            if 1 <= choice <= len(concepts):
                run_cluster_comparison(app, concepts[choice - 1].get("de", ""))
            return
        ui.show_error(f'Keine Ergebnisse fuer "{query}".')
        ui.wait_for_enter()
        return

    table = Table(
        title=f'\U0001f50d Ergebnisse fuer "{query}" ({len(results)} Treffer)',
        box=box.ROUNDED,
        border_style="cyan",
    )
    table.add_column("Sprache", width=14)
    table.add_column("Wort", min_width=15)
    table.add_column("Bedeutung", min_width=15)
    table.add_column("Kategorie", width=12)

    for r in results[:30]:
        flag = r.get("flag", "")
        lang_name = r.get("lang_name", "")
        word = r["word"]
        if r.get("romanization"):
            word += f" ({r['romanization']})"
        table.add_row(
            f"{flag} {lang_name}",
            word,
            r["meaning_de"],
            r.get("category", ""),
        )

    console.print(table)
    ui.wait_for_enter()


def run_statistics(app: AppContext) -> None:
    """Show detailed statistics."""
    from ui import terminal as ui

    ui.clear_screen()

    summary = app.planner.get_sprint_summary()
    progress = app.planner.get_progress_by_language()
    review_stats = app.db.get_review_stats()
    forecast = app.planner.get_review_forecast()
    weakest = app.planner.get_weakest_language()
    fastest = app.planner.get_fastest_growing()

    show_statistics(summary, progress, review_stats, forecast, weakest, fastest)

    console.print("\n  [1] Sprach-Stammbaum  [2] Export  [0] Zurueck")
    choice = ui.ask_int(">", default=0)

    if choice == 1:
        ui.clear_screen()
        show_family_tree(progress)
        ui.wait_for_enter()
    elif choice == 2:
        run_export(app)


def run_export(app: AppContext) -> None:
    """Export progress as JSON."""
    from ui import terminal as ui

    progress = app.planner.get_progress_by_language()
    summary = app.planner.get_sprint_summary()

    export_data = {
        "export_date": date.today().isoformat(),
        "summary": summary,
        "progress": progress,
    }

    export_path = Path("polyglot_export.json")
    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)

    ui.show_success(f"Exportiert nach {export_path.absolute()}")
    ui.wait_for_enter()


def run_settings(app: AppContext) -> None:
    """Settings management."""
    from ui import terminal as ui

    ui.clear_screen()
    settings = app.db.get_all_settings()

    console.print("\n  [bold]\u2699\ufe0f  EINSTELLUNGEN[/bold]\n")

    daily = settings.get("daily_minutes", "90")
    sprint_day = app.db.get_sprint_day()
    sprint_days = settings.get("sprint_days", "30")
    name = settings.get("user_name", "Lerner")

    console.print(f"  [1] \U0001f3af Taegliches Lernziel: {daily} Min")
    console.print(f"  [2] \U0001f4c5 Sprint-Tag: {sprint_day}/{sprint_days}")
    console.print(f"  [3] \U0001f464 Name: {name}")
    console.print(f"  [4] \U0001f517 Cluster-Hints bei Review: An")
    console.print(f"  [5] \U0001f4dd Transliteration anzeigen: An")
    console.print(f"  [6] \U0001f504 Datenbank zuruecksetzen")
    console.print(f"  [0] Zurueck\n")

    choice = ui.ask_int(">", default=0)

    if choice == 1:
        new_min = ui.ask_int("Neue Minutenzahl:", default=int(daily))
        app.db.set_setting("daily_minutes", str(new_min))
        ui.show_success(f"Lernziel auf {new_min} Min gesetzt.")
    elif choice == 3:
        new_name = ui.ask_text("Neuer Name:", default=name)
        app.db.set_setting("user_name", new_name)
        ui.show_success(f"Name geaendert zu {new_name}.")
    elif choice == 6:
        if ui.ask_confirm("Wirklich ALLE Daten loeschen?", default=False):
            app.db.close()
            import os
            from config import DB_PATH
            if DB_PATH.exists():
                os.remove(DB_PATH)
            ui.show_success("Datenbank zurueckgesetzt. Neustart erforderlich.")
            sys.exit(0)

    ui.wait_for_enter()


def run_dashboard(app: AppContext) -> None:
    """Show dashboard and daily plan."""
    from ui import terminal as ui

    ui.clear_screen()
    summary = app.planner.get_sprint_summary()
    plan = app.planner.get_daily_plan()
    progress = app.planner.get_progress_by_language()
    xp_summary = app.gamification.get_xp_summary()

    # Include daily challenge status if engine exists
    daily_status = None
    if app.daily_challenge_engine:
        daily_status = app.daily_challenge_engine.get_today_status()

    show_dashboard(summary, plan, progress, xp_summary, daily_status)
    ui.wait_for_enter()


def run_achievements(app: AppContext) -> None:
    """Show achievements and XP overview."""
    from ui import terminal as ui

    ui.clear_screen()
    xp_summary = app.gamification.get_xp_summary()
    achievements = app.gamification.get_achievements_by_category()
    show_achievements_panel(achievements, xp_summary)
    ui.wait_for_enter()


def run_custom_vocab_menu(app: AppContext) -> None:
    """Custom vocabulary management menu."""
    from ui import terminal as ui

    while True:
        ui.clear_screen()
        console.print("\n  [bold]\U0001f4dd EIGENE VOKABELN[/bold]\n")

        count = app.custom_vocab_engine.get_count()
        console.print(f"  Eigene Woerter: {count}\n")
        console.print("  [1] Wort hinzufuegen")
        console.print("  [2] Woerter anzeigen")
        console.print("  [3] CSV importieren")
        console.print("  [4] JSON importieren")
        console.print("  [5] CSV exportieren")
        console.print("  [6] JSON exportieren")
        console.print("  [7] Wort loeschen")
        console.print("  [0] Zurueck\n")

        choice = ui.ask_int(">", default=0)

        if choice == 0:
            return
        elif choice == 1:
            languages = app.db.get_all_languages()
            lang_id = ui.show_language_selector(languages, "Sprache")
            if not lang_id:
                continue
            word = ui.ask_text("Wort:")
            if not word:
                continue
            meaning_de = ui.ask_text("Bedeutung (DE):")
            if not meaning_de:
                continue
            meaning_en = ui.ask_text("Bedeutung (EN, optional):", default="")
            romanization = ui.ask_text("Romanisierung (optional):", default="")
            tags = ui.ask_text("Tags (optional):", default="")

            app.custom_vocab_engine.add_word(
                lang_id, word, meaning_de, meaning_en, romanization, tags,
            )
            ui.show_success(f"'{word}' hinzugefuegt!")
            ui.wait_for_enter()

        elif choice == 2:
            words = app.custom_vocab_engine.get_custom_words()
            if not words:
                ui.show_info("Keine eigenen Woerter vorhanden.")
                ui.wait_for_enter()
                continue
            from rich.table import Table
            from rich import box as richbox
            table = Table(title="Eigene Vokabeln", box=richbox.ROUNDED, border_style="cyan")
            table.add_column("ID", width=4)
            table.add_column("Sprache", width=6)
            table.add_column("Wort", min_width=12)
            table.add_column("Bedeutung", min_width=15)
            table.add_column("Tags", width=10)
            for w in words[:50]:
                table.add_row(
                    str(w["id"]),
                    w["language_id"],
                    w["word"],
                    w["meaning_de"],
                    w.get("tags", ""),
                )
            console.print(table)
            ui.wait_for_enter()

        elif choice == 3:
            path = ui.ask_text("CSV-Datei Pfad:")
            if not path:
                continue
            languages = app.db.get_all_languages()
            lang_id = ui.show_language_selector(languages, "Sprache")
            if not lang_id:
                continue
            try:
                with open(path, encoding="utf-8") as f:
                    count = app.custom_vocab_engine.import_csv(f.read(), lang_id)
                ui.show_success(f"{count} Woerter importiert!")
            except FileNotFoundError:
                ui.show_error("Datei nicht gefunden!")
            ui.wait_for_enter()

        elif choice == 4:
            path = ui.ask_text("JSON-Datei Pfad:")
            if not path:
                continue
            languages = app.db.get_all_languages()
            lang_id = ui.show_language_selector(languages, "Sprache")
            if not lang_id:
                continue
            try:
                with open(path, encoding="utf-8") as f:
                    count = app.custom_vocab_engine.import_json(f.read(), lang_id)
                ui.show_success(f"{count} Woerter importiert!")
            except FileNotFoundError:
                ui.show_error("Datei nicht gefunden!")
            ui.wait_for_enter()

        elif choice == 5:
            csv_text = app.custom_vocab_engine.export_csv()
            path = "custom_vocab_export.csv"
            with open(path, "w", encoding="utf-8") as f:
                f.write(csv_text)
            ui.show_success(f"Exportiert nach {path}")
            ui.wait_for_enter()

        elif choice == 6:
            json_text = app.custom_vocab_engine.export_json()
            path = "custom_vocab_export.json"
            with open(path, "w", encoding="utf-8") as f:
                f.write(json_text)
            ui.show_success(f"Exportiert nach {path}")
            ui.wait_for_enter()

        elif choice == 7:
            word_id = ui.ask_int("ID des Wortes zum Loeschen:")
            if app.custom_vocab_engine.delete_custom_word(word_id):
                ui.show_success("Wort geloescht!")
            else:
                ui.show_error("Wort nicht gefunden!")
            ui.wait_for_enter()


def run_sentence_translation(app: AppContext, query: str = "") -> None:
    """Translate a sentence into all 22 languages."""
    from ui import terminal as ui

    ui.clear_screen()
    console.print("\n  [bold]\U0001f4dd SATZUEBERSETZUNG[/bold]")
    console.print("  Uebersetze einen Satz in alle 22 Sprachen!\n")

    console.print("  [1] Satz eingeben (Deutsch/Englisch)")
    console.print("  [2] Vorlagen nach Kategorie durchsuchen")
    console.print("  [3] Alle Vorlagen anzeigen")
    console.print("  [0] Zurueck\n")

    choice = ui.ask_int(">", default=1)

    if choice == 0:
        return
    elif choice == 2:
        categories = app.sentence_engine.get_categories()
        if not categories:
            ui.show_error("Keine Satz-Vorlagen geladen!")
            ui.wait_for_enter()
            return

        cat = ui.show_sentence_categories(categories)
        if not cat:
            return

        sentences = app.sentence_engine.get_sentences_by_category(cat)
        if not sentences:
            ui.show_error("Keine Saetze in dieser Kategorie!")
            ui.wait_for_enter()
            return

        idx = ui.show_sentence_list(sentences)
        if idx < 0:
            return

        sentence = sentences[idx]
        data = app.sentence_engine.get_sentence_translations(sentence)
        ui.clear_screen()
        ui.show_sentence_translations(data)
        ui.wait_for_enter()

    elif choice == 3:
        sentences = app.sentence_engine.get_all_sentences()
        if not sentences:
            ui.show_error("Keine Satz-Vorlagen geladen!")
            ui.wait_for_enter()
            return

        idx = ui.show_sentence_list(sentences)
        if idx < 0:
            return

        sentence = sentences[idx]
        data = app.sentence_engine.get_sentence_translations(sentence)
        ui.clear_screen()
        ui.show_sentence_translations(data)
        ui.wait_for_enter()

    else:
        if not query:
            query = ui.ask_text("Satz eingeben:")
        if not query:
            return

        match = app.sentence_engine.find_best_match(query)
        if match:
            data = app.sentence_engine.get_sentence_translations(match)
            ui.clear_screen()
            ui.show_sentence_translations(data)
        else:
            ui.clear_screen()
            results = app.sentence_engine.word_by_word_lookup(query)
            ui.show_word_lookup_results(results)

        ui.wait_for_enter()
