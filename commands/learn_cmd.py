"""Learn command — learn new words and manage memory palaces."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ui.terminal import console
from ui.gamification_ui import show_xp_gain, show_level_up

if TYPE_CHECKING:
    from app import AppContext

logger = logging.getLogger(__name__)


def run_learn_new(app: AppContext, lang_id: str | None = None) -> None:
    """Learn new words using Memory Palace."""
    from ui import terminal as ui

    if not lang_id:
        languages = app.db.get_all_languages()
        lang_id = ui.show_language_selector(languages, "Sprache zum Lernen")
        if not lang_id:
            return

    palace_info = app.palace_engine.get_palace_info(lang_id)
    if not palace_info:
        ui.show_error("Sprache nicht gefunden!")
        return

    ui.clear_screen()
    ui.show_palace_header(palace_info)

    station = app.palace_engine.get_next_empty_station(lang_id)
    if not station:
        ui.show_info("Alle Stationen belegt! Erstelle neue oder review bestehende.")
        if ui.ask_confirm("Neue Station hinzufuegen?"):
            name = ui.ask_text("Stationsname:")
            if name:
                app.palace_engine.add_station(lang_id, name)
                station = app.palace_engine.get_next_empty_station(lang_id)
        if not station:
            ui.wait_for_enter()
            return

    word = app.palace_engine.get_next_word_for_palace(lang_id)
    if not word:
        ui.show_info("Keine neuen Woerter verfuegbar fuer diese Sprache!")
        ui.wait_for_enter()
        return

    total_stations = palace_info["total_stations"]

    while station and word:
        ui.clear_screen()
        ui.show_palace_header(palace_info)

        cluster_hints = app.palace_engine.get_cluster_for_word(word)
        mnemonic = app.palace_engine.get_mnemonic_suggestion(word, station)

        ui.show_palace_station(
            station, total_stations, word,
            cluster_hints, mnemonic,
        )

        console.print(
            "\n  \U0001f4ad Erstelle dein eigenes Bild fuer diese Station:"
        )
        user_mnemonic = ui.ask_text(
            "Dein Mnemonic (oder Enter fuer Vorschlag):"
        )
        if not user_mnemonic:
            user_mnemonic = mnemonic

        app.palace_engine.assign_word(station["id"], word["id"], user_mnemonic)

        old_level = app.gamification.get_level()
        xp_info = app.gamification.award_xp("learn", 5, lang_id)
        show_xp_gain(xp_info)
        new_level = app.gamification.get_level()
        if new_level["level"] > old_level["level"]:
            show_level_up(old_level["level"], new_level["level"], new_level["rank"])

        app.session.words_learned += 1
        app.session.languages.add(lang_id)

        filled = palace_info["filled_stations"] + 1
        ui.show_success(
            f"Gespeichert! Du hast jetzt {filled}/{total_stations} "
            f"Stationen in deinem Palast."
        )

        console.print("\n  [Enter] Naechste Station  [s] Ueberspringen  "
                      "[r] Review bisherige  [q] Zurueck")
        choice = ui.ask_text(">", default="")
        if choice.lower() == "q":
            break
        elif choice.lower() == "r":
            run_palace_review(app, lang_id)

        station = app.palace_engine.get_next_empty_station(lang_id)
        word = app.palace_engine.get_next_word_for_palace(lang_id) if station else None

    if not station:
        ui.show_info("Alle Stationen belegt!")
    if not word:
        ui.show_info("Keine weiteren Woerter verfuegbar!")
    ui.wait_for_enter()


def run_palace_management(app: AppContext) -> None:
    """Manage memory palaces."""
    from ui import terminal as ui

    ui.clear_screen()
    console.print("\n  [bold]\U0001f3db\ufe0f  PALAESTE VERWALTEN[/bold]\n")

    languages = app.db.get_all_languages()
    lang_id = ui.show_language_selector(languages, "Palast anzeigen")
    if not lang_id:
        return

    palace_info = app.palace_engine.get_palace_info(lang_id)
    if not palace_info:
        ui.show_error("Palast nicht gefunden!")
        return

    ui.clear_screen()
    ui.show_palace_header(palace_info)
    ui.show_palace_overview(palace_info)

    console.print(
        "\n  [1] Review  [2] Neue Station  [3] Neues Wort platzieren  [0] Zurueck"
    )
    choice = ui.ask_int(">", default=0)

    if choice == 1:
        run_palace_review(app, lang_id)
    elif choice == 2:
        name = ui.ask_text("Neuer Stationsname:")
        if name:
            num = app.palace_engine.add_station(lang_id, name)
            ui.show_success(f"Station {num} '{name}' hinzugefuegt!")
            ui.wait_for_enter()
    elif choice == 3:
        run_learn_new(app, lang_id)


def run_palace_review(app: AppContext, lang_id: str) -> None:
    """Review filled palace stations."""
    from ui import terminal as ui

    stations = app.palace_engine.review_palace(lang_id)
    if not stations:
        ui.show_info("Keine belegten Stationen zum Reviewen!")
        ui.wait_for_enter()
        return

    ui.clear_screen()
    lang = app.db.get_language(lang_id)
    console.print(
        f"\n  \U0001f3db\ufe0f  [bold]Palast-Review: "
        f"{lang['flag']} {lang['name']}[/bold]\n"
    )
    console.print(
        "  Gehe durch deinen Palast und erinnere dich an jedes Wort.\n"
    )

    for station in stations:
        console.print(
            f"  Station {station['station_number']}: "
            f"[bold]{station['station_name']}[/bold]"
        )
        console.print(f"  \U0001f4ad Mnemonic: [italic]{station.get('user_mnemonic', '')}[/italic]")

        answer = ui.ask_text("Welches Wort?")
        word = station.get("word", "")
        rom = station.get("romanization", "")
        meaning = station.get("meaning_de", "")

        if answer and (answer.lower() == word.lower() or
                       (rom and answer.lower() == rom.lower())):
            ui.show_success(f"{word} ({meaning})")
        else:
            console.print(
                f"  \u27a1\ufe0f  {word}"
                + (f" ({rom})" if rom else "")
                + f" = {meaning}"
            )
        console.print()

    ui.wait_for_enter()
