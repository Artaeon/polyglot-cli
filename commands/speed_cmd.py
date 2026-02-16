"""Speed learning command — 7 techniques."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from rich.panel import Panel

from ui.terminal import console
from ui.gamification_ui import show_xp_gain
from ui import speed_learn_ui

if TYPE_CHECKING:
    from app import AppContext

logger = logging.getLogger(__name__)


def run_speed_learning(app: AppContext) -> None:
    """Speed learning submenu with 7 techniques."""
    from ui import terminal as ui

    while True:
        ui.clear_screen()
        choice = speed_learn_ui.show_speed_menu()

        try:
            if choice == "0":
                return
            elif choice == "1":
                _run_keyword_method(app)
            elif choice == "2":
                _run_micro_session(app)
            elif choice == "3":
                _run_interleaving(app)
            elif choice == "4":
                _run_dual_coding(app)
            elif choice == "5":
                _run_recall_chain(app)
            elif choice == "6":
                _run_error_drilling(app)
            elif choice == "7":
                _run_progressive_hints(app)
        except KeyboardInterrupt:
            continue


def _run_keyword_method(app: AppContext) -> None:
    """Keyword mnemonic technique."""
    from ui import terminal as ui

    languages = app.db.get_all_languages()
    lang_id = ui.show_language_selector(languages, "Sprache fuer Keywords")
    if not lang_id:
        return

    words = app.speed_engine.prepare_micro_session(lang_id, 5)
    if not words:
        ui.show_info("Noch keine Woerter zum Ueben!")
        ui.wait_for_enter()
        return

    for word in words:
        ui.clear_screen()
        existing = app.speed_engine.get_keyword(word.get("word_id", word.get("id", 0)))
        if existing:
            keyword = existing["keyword"]
            story = existing.get("story", "")
        else:
            keyword = app.speed_engine.generate_keyword(word)
            story = ""

        speed_learn_ui.show_keyword_card(word, keyword, story)

        console.print("\n  [1] Eigenes Keyword erstellen  [Enter] Weiter")
        action = ui.ask_text(">", default="")
        if action == "1":
            new_kw = ui.ask_text("Dein Keyword:")
            new_story = ui.ask_text("Deine Story (optional):")
            if new_kw:
                app.speed_engine.save_user_keyword(
                    word.get("word_id", word.get("id", 0)), new_kw, new_story,
                )
                ui.show_success("Keyword gespeichert!")

    ui.wait_for_enter()


def _run_micro_session(app: AppContext) -> None:
    """2-minute micro review session."""
    from ui import terminal as ui

    lang_id = None
    console.print("\n  [1] Alle Sprachen  [2] Eine Sprache waehlen")
    if ui.ask_int(">", default=1) == 2:
        languages = app.db.get_all_languages()
        lang_id = ui.show_language_selector(languages, "Sprache")
        if not lang_id:
            return

    words = app.speed_engine.prepare_micro_session(lang_id, 10)
    if not words:
        ui.show_info("Keine Woerter zum Ueben verfuegbar!")
        ui.wait_for_enter()
        return

    ui.clear_screen()
    lang_name = words[0].get("lang_name", "") if lang_id else "Gemischt"
    speed_learn_ui.show_micro_session_header(len(words), lang_name)

    start_time = time.time()
    correct_count = 0

    for i, word in enumerate(words):
        elapsed = time.time() - start_time
        if elapsed > 120:
            console.print("\n  \u23f1\ufe0f  [bold]Zeit abgelaufen![/bold]")
            break

        remaining = max(0, 120 - int(elapsed))
        console.print(f"\n  [{i+1}/{len(words)}] \u23f1\ufe0f {remaining}s")
        console.print(f"  {word.get('flag', '')} Was bedeutet [bold]{word['word']}[/bold]?")
        if word.get("romanization"):
            console.print(f"  [dim]({word['romanization']})[/dim]")

        answer = ui.ask_text(">")
        expected = word["meaning_de"].lower()
        if answer and answer.strip().lower() == expected:
            correct_count += 1
            console.print("  \u2705 Richtig!")
        else:
            console.print(f"  \u274c {word['meaning_de']}")

        xp_info = app.gamification.award_xp(
            "speed", 5 if answer and answer.strip().lower() == expected else 1,
            word.get("language_id"),
        )
        show_xp_gain(xp_info)

    duration = int(time.time() - start_time)
    console.print(f"\n  \U0001f389 Micro-Session: {correct_count}/{len(words)} in {duration}s")
    ui.wait_for_enter()


def _run_interleaving(app: AppContext) -> None:
    """Interleaved multi-language session."""
    from ui import terminal as ui

    words = app.speed_engine.prepare_interleaved_session(15)
    if not words:
        ui.show_info("Nicht genug gelernte Woerter fuer Interleaving!")
        ui.wait_for_enter()
        return

    lang_count = len(set(w["language_id"] for w in words))
    ui.clear_screen()
    speed_learn_ui.show_interleaved_header(len(words), lang_count)

    correct_count = 0
    for i, word in enumerate(words):
        console.print(f"\n  [{i+1}/{len(words)}] {word.get('flag', '')} {word.get('lang_name', '')}")
        console.print(f"  Was bedeutet [bold]{word['word']}[/bold]?")
        if word.get("romanization"):
            console.print(f"  [dim]({word['romanization']})[/dim]")

        answer = ui.ask_text(">")
        expected = word["meaning_de"].lower()
        correct = answer and answer.strip().lower() == expected
        if correct:
            correct_count += 1
            console.print("  \u2705 Richtig!")
        else:
            console.print(f"  \u274c {word['meaning_de']}")

        xp_info = app.gamification.award_xp("speed", 5 if correct else 1, word.get("language_id"))
        if xp_info["total_xp"] > 0:
            xp_info["total_xp"] = round(xp_info["total_xp"] * 1.2)
        show_xp_gain(xp_info)

    pct = round(correct_count / max(len(words), 1) * 100)
    console.print(f"\n  \U0001f389 Interleaving: {correct_count}/{len(words)} ({pct}%)")
    ui.wait_for_enter()


def _run_dual_coding(app: AppContext) -> None:
    """Dual coding — word + visual emoji scene."""
    from ui import terminal as ui

    languages = app.db.get_all_languages()
    lang_id = ui.show_language_selector(languages, "Sprache")
    if not lang_id:
        return

    words = app.speed_engine.prepare_micro_session(lang_id, 8)
    if not words:
        ui.show_info("Keine Woerter verfuegbar!")
        ui.wait_for_enter()
        return

    for word in words:
        ui.clear_screen()
        scene = app.speed_engine.get_dual_coding(word)
        speed_learn_ui.show_dual_coding(word, scene)
        ui.wait_for_enter("Naechstes Wort...")

    ui.wait_for_enter()


def _run_recall_chain(app: AppContext) -> None:
    """Active recall chain — word association game."""
    from ui import terminal as ui

    words = app.speed_engine.prepare_micro_session(count=1)
    if not words:
        ui.show_info("Keine Woerter verfuegbar!")
        ui.wait_for_enter()
        return

    ui.clear_screen()
    best = app.speed_engine.get_best_chain()
    console.print(Panel(
        "[bold]\U0001f517 RECALL-KETTE[/bold]\n"
        "Uebersetze jedes Wort! Kette reisst bei Fehler.\n"
        f"Aktueller Rekord: [bold yellow]{best}[/bold yellow]",
        border_style="bold yellow",
    ))

    current = words[0]
    history = [current.get("word_id", current.get("id", 0))]
    chain_length = 0

    while True:
        console.print(f"\n  {current.get('flag', '')} [bold]{current['word']}[/bold]")
        if current.get("romanization"):
            console.print(f"  [dim]({current['romanization']})[/dim]")

        answer = ui.ask_text("Bedeutung:")
        expected = current["meaning_de"].lower()

        if answer and answer.strip().lower() == expected:
            chain_length += 1
            speed_learn_ui.show_recall_chain_status(chain_length, best)
            ui.show_success("Richtig!")

            next_word = app.speed_engine.get_next_chain_word(current, history)
            if not next_word:
                console.print("  Keine weiteren Woerter! Kette endet.")
                break
            history.append(next_word.get("word_id", next_word.get("id", 0)))
            current = next_word
        else:
            speed_learn_ui.show_chain_break(chain_length, best)
            console.print(f"  Richtig waere: [bold]{current['meaning_de']}[/bold]")
            break

    app.speed_engine.save_chain_result(chain_length)
    if chain_length > 0:
        xp_info = app.gamification.award_xp("speed", min(5, chain_length))
        show_xp_gain(xp_info)

    ui.wait_for_enter()


def _run_error_drilling(app: AppContext) -> None:
    """Error-focused intensive drilling."""
    from ui import terminal as ui

    lang_id = None
    console.print("\n  [1] Alle Sprachen  [2] Eine Sprache waehlen")
    if ui.ask_int(">", default=1) == 2:
        languages = app.db.get_all_languages()
        lang_id = ui.show_language_selector(languages, "Sprache")

    words = app.speed_engine.get_error_focused_words(15, lang_id)
    if not words:
        ui.show_info("Keine schwierigen Woerter gefunden! Alles gut gelernt!")
        ui.wait_for_enter()
        return

    ui.clear_screen()
    lang_name = words[0].get("lang_name", "") if lang_id else "Gemischt"
    speed_learn_ui.show_error_drill_header(len(words), lang_name)

    correct_count = 0
    queue = list(words)
    idx = 0
    total_attempted = 0

    while idx < len(queue) and total_attempted < 30:
        word = queue[idx]
        total_attempted += 1
        console.print(f"\n  [{total_attempted}] {word.get('flag', '')} {word.get('lang_name', '')}")
        console.print(f"  Was bedeutet [bold]{word['word']}[/bold]?")
        if word.get("romanization"):
            console.print(f"  [dim]({word['romanization']})[/dim]")

        answer = ui.ask_text(">")
        expected = word["meaning_de"].lower()
        correct = answer and answer.strip().lower() == expected

        if correct:
            correct_count += 1
            console.print("  \u2705 Richtig!")
        else:
            console.print(f"  \u274c {word['meaning_de']}")
            if idx + 3 < len(queue) + 5:
                queue.insert(min(idx + 4, len(queue)), word)

        xp_info = app.gamification.award_xp("speed", 5 if correct else 1, word.get("language_id"))
        show_xp_gain(xp_info)
        idx += 1

    pct = round(correct_count / max(total_attempted, 1) * 100)
    console.print(f"\n  \U0001f389 Fehler-Drilling: {correct_count}/{total_attempted} ({pct}%)")
    ui.wait_for_enter()


def _run_progressive_hints(app: AppContext) -> None:
    """Progressive hint review."""
    from ui import terminal as ui

    languages = app.db.get_all_languages()
    lang_id = ui.show_language_selector(languages, "Sprache")
    if not lang_id:
        return

    words = app.speed_engine.prepare_micro_session(lang_id, 8)
    if not words:
        ui.show_info("Keine Woerter verfuegbar!")
        ui.wait_for_enter()
        return

    ui.clear_screen()
    console.print(Panel(
        "[bold]\U0001f4a1 PROGRESSIVE HINTS[/bold]\n"
        "Uebersetze das Wort! Druecke [h] fuer einen Hinweis.",
        border_style="bold cyan",
    ))

    for word in words:
        console.print(f"\n  Was heisst [bold]{word['meaning_de']}[/bold]?")
        expected = word["word"]
        hint_level = 0

        while True:
            answer = ui.ask_text("> (oder [h] fuer Hinweis)")
            if answer.lower() == "h":
                hint_level += 1
                hint = app.speed_engine.get_progressive_hint(expected, hint_level)
                speed_learn_ui.show_progressive_hint(hint, hint_level)
                continue

            correct = (answer.strip().lower() == expected.lower())
            if word.get("romanization") and answer.strip().lower() == word["romanization"].lower():
                correct = True

            if correct:
                ui.show_success(f"{expected}")
                quality = max(1, 5 - hint_level)
                xp_info = app.gamification.award_xp("speed", quality, lang_id)
                show_xp_gain(xp_info)
            else:
                console.print(f"  \u274c Richtig: [bold]{expected}[/bold]")
                if word.get("romanization"):
                    console.print(f"  ({word['romanization']})")
            break

    ui.wait_for_enter()
