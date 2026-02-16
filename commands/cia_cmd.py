"""CIA drills command — intensive timed exercises."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from rich.panel import Panel

from ui.terminal import console
from ui.gamification_ui import show_xp_gain
from ui import cia_drills_ui

if TYPE_CHECKING:
    from app import AppContext

logger = logging.getLogger(__name__)


def run_cia_drills(app: AppContext) -> None:
    """CIA-style intensive drills submenu."""
    from ui import terminal as ui

    while True:
        ui.clear_screen()
        choice = cia_drills_ui.show_cia_menu()

        try:
            if choice == "0":
                return
            elif choice == "1":
                _run_shadowing(app)
            elif choice == "2":
                _run_rapid_association(app)
            elif choice == "3":
                _run_context_switching(app)
            elif choice == "4":
                _run_pattern_recognition(app)
            elif choice == "5":
                _run_immersion_block(app)
            elif choice == "6":
                _run_back_translation(app)
        except KeyboardInterrupt:
            continue


def _run_shadowing(app: AppContext) -> None:
    """Shadowing drill — see word, it disappears, type from memory."""
    from ui import terminal as ui

    languages = app.db.get_all_languages()
    lang_id = ui.show_language_selector(languages, "Sprache fuer Shadowing")
    if not lang_id:
        return

    console.print("\n  Belichtungszeit (Sekunden):")
    console.print("  [1] 4s (Einfach)  [2] 3s  [3] 2s  [4] 1.5s (Schwer)")
    exp_choice = ui.ask_int(">", default=2)
    exposure = {1: 4.0, 2: 3.0, 3: 2.0, 4: 1.5}.get(exp_choice, 3.0)

    items = app.cia_engine.prepare_shadowing_round(lang_id, exposure, 10)
    if not items:
        ui.show_info("Keine Woerter verfuegbar!")
        ui.wait_for_enter()
        return

    start_time = time.time()
    correct_count = 0
    total = len(items)

    for i, item in enumerate(items):
        ui.clear_screen()
        console.print(f"  [{i+1}/{total}]")

        cia_drills_ui.show_shadowing_word(
            item["word"], item.get("romanization", ""), item["exposure_seconds"],
        )

        answer = ui.ask_text("Tippe das Wort:")
        expected = item["word"]
        rom = item.get("romanization", "")
        correct = (answer.strip().lower() == expected.lower() or
                   (rom and answer.strip().lower() == rom.lower()))

        if correct:
            correct_count += 1
            ui.show_success(f"{expected} = {item['meaning_de']}")
        else:
            console.print(f"  \u274c Richtig: [bold]{expected}[/bold] = {item['meaning_de']}")

        xp_info = app.gamification.award_xp("cia", 5 if correct else 1, lang_id)
        show_xp_gain(xp_info)

    duration = int(time.time() - start_time)
    cia_drills_ui.show_drill_summary("Shadowing", total, correct_count, duration)
    app.cia_engine.log_drill_session("shadowing", duration, total, correct_count, 0, [lang_id])
    ui.wait_for_enter()


def _run_rapid_association(app: AppContext) -> None:
    """Rapid word association — translate under time pressure."""
    from ui import terminal as ui

    console.print("\n  Sprachen waehlen (mind. 1):")
    languages = app.db.get_all_languages()
    lang_id = ui.show_language_selector(languages, "Sprache")
    if not lang_id:
        return

    items = app.cia_engine.prepare_rapid_association([lang_id], 5000, 15)
    if not items:
        ui.show_info("Keine Woerter verfuegbar!")
        ui.wait_for_enter()
        return

    start_time = time.time()
    correct_count = 0
    total = len(items)
    response_times: list[int] = []

    for i, item in enumerate(items):
        ui.clear_screen()
        console.print(f"  [{i+1}/{total}]")
        cia_drills_ui.show_rapid_timer(
            item["time_limit_ms"], item.get("flag", ""), item.get("lang_name", ""),
        )
        console.print(f"\n  [bold]{item['word']}[/bold]")
        if item.get("romanization"):
            console.print(f"  [dim]({item['romanization']})[/dim]")

        word_start = time.time()
        answer = ui.ask_text("Bedeutung:")
        response_ms = int((time.time() - word_start) * 1000)
        response_times.append(response_ms)

        expected = item["meaning_de"].lower()
        timed_out = response_ms > item["time_limit_ms"]
        correct = answer and answer.strip().lower() == expected and not timed_out

        if timed_out:
            console.print(f"  \u23f0 [bold red]Zu langsam! ({response_ms}ms)[/bold red]")
            console.print(f"  Richtig: {item['meaning_de']}")
        elif correct:
            correct_count += 1
            bonus = " \u26a1" if response_ms < 3000 else ""
            console.print(f"  \u2705 Richtig! ({response_ms}ms){bonus}")
        else:
            console.print(f"  \u274c {item['meaning_de']} ({response_ms}ms)")

        quality = 5 if correct else (2 if timed_out else 1)
        xp_info = app.gamification.award_xp("cia", quality, item.get("language_id"))
        show_xp_gain(xp_info)

    duration = int(time.time() - start_time)
    avg_ms = round(sum(response_times) / max(len(response_times), 1))
    cia_drills_ui.show_drill_summary("Rapid Association", total, correct_count, duration, avg_ms)
    app.cia_engine.log_drill_session("rapid_association", duration, total, correct_count, avg_ms, [lang_id])
    ui.wait_for_enter()


def _run_context_switching(app: AppContext) -> None:
    """Context switching — same concept across languages."""
    from ui import terminal as ui

    console.print("\n  Zwei oder mehr Sprachen waehlen:")
    languages = app.db.get_all_languages()

    lang_ids: list[str] = []
    for _ in range(3):
        console.print(f"\n  Sprache {len(lang_ids) + 1} (0 = fertig):")
        lid = ui.show_language_selector(languages, "Sprache")
        if lid:
            lang_ids.append(lid)
        else:
            break

    if len(lang_ids) < 2:
        ui.show_error("Mindestens 2 Sprachen noetig!")
        ui.wait_for_enter()
        return

    items = app.cia_engine.prepare_context_switch(lang_ids, 15)
    if not items:
        ui.show_info("Nicht genug gemeinsame Woerter!")
        ui.wait_for_enter()
        return

    start_time = time.time()
    correct_count = 0
    total = len(items)
    prev_lang = ""

    for i, item in enumerate(items):
        if item["language_id"] != prev_lang:
            cia_drills_ui.show_context_switch_banner(item.get("flag", ""), item.get("lang_name", ""))
            prev_lang = item["language_id"]

        console.print(f"\n  [{i+1}/{total}] Was heisst [bold]{item['meaning_de']}[/bold]?")
        answer = ui.ask_text(">")
        expected = item["word"].lower()
        rom = item.get("romanization", "")
        correct = (answer and (answer.strip().lower() == expected or
                               (rom and answer.strip().lower() == rom.lower())))

        if correct:
            correct_count += 1
            ui.show_success(item["word"])
        else:
            console.print(f"  \u274c [bold]{item['word']}[/bold]")
            if rom:
                console.print(f"  ({rom})")

        xp_info = app.gamification.award_xp("cia", 5 if correct else 1, item["language_id"])
        show_xp_gain(xp_info)

    duration = int(time.time() - start_time)
    cia_drills_ui.show_drill_summary("Context Switch", total, correct_count, duration)
    app.cia_engine.log_drill_session("context_switch", duration, total, correct_count, 0, lang_ids)
    ui.wait_for_enter()


def _run_pattern_recognition(app: AppContext) -> None:
    """Pattern recognition drill."""
    from ui import terminal as ui

    languages = app.db.get_all_languages()
    lang_id = ui.show_language_selector(languages, "Sprache")
    if not lang_id:
        return

    items = app.cia_engine.prepare_pattern_drill(lang_id, 5)
    if not items:
        ui.show_info("Nicht genug Woerter fuer Pattern-Drill!")
        ui.wait_for_enter()
        return

    start_time = time.time()
    correct_count = 0

    for i, item in enumerate(items):
        ui.clear_screen()
        console.print(Panel(
            f"\U0001f9e9 PATTERN RECOGNITION \u2014 {i+1}/{len(items)}",
            border_style="bold magenta",
        ))

        console.print(f"\n  Kategorie: [dim]{item['category']}[/dim]")
        console.print("\n  Beispiele:")
        for ex in item["examples"]:
            display = ex["word"]
            if ex.get("romanization"):
                display += f" ({ex['romanization']})"
            console.print(f"  \u2022 {display} = {ex['meaning_de']}")

        console.print(f"\n  Wie heisst [bold]{item['test_meaning']}[/bold]?")
        answer = ui.ask_text(">")

        expected = item["expected"]
        rom = item.get("expected_romanization", "")
        correct = (answer and (answer.strip().lower() == expected.lower() or
                               (rom and answer.strip().lower() == rom.lower())))

        if correct:
            correct_count += 1
            ui.show_success(expected)
        else:
            console.print(f"  \u274c Richtig: [bold]{expected}[/bold]")
            if rom:
                console.print(f"  ({rom})")

        xp_info = app.gamification.award_xp("cia", 5 if correct else 1, lang_id)
        show_xp_gain(xp_info)

    duration = int(time.time() - start_time)
    cia_drills_ui.show_drill_summary("Pattern Recognition", len(items), correct_count, duration)
    app.cia_engine.log_drill_session("pattern_recognition", duration, len(items), correct_count, 0, [lang_id])
    ui.wait_for_enter()


def _run_immersion_block(app: AppContext) -> None:
    """Full immersion block in target language."""
    from ui import terminal as ui

    languages = app.db.get_all_languages()
    lang_id = ui.show_language_selector(languages, "Sprache fuer Immersion")
    if not lang_id:
        return

    block = app.cia_engine.prepare_immersion_block(lang_id, 10)
    if not block["cards"]:
        ui.show_info("Keine Woerter verfuegbar!")
        ui.wait_for_enter()
        return

    ui.clear_screen()
    cia_drills_ui.show_immersion_header(block["flag"], block["lang_name"], 5)

    feedback = block["feedback"]
    correct_count = 0
    total = len(block["cards"])

    for i, card in enumerate(block["cards"]):
        console.print(f"\n  [{i+1}/{total}] [bold]{card['meaning_de']}[/bold] = ?")
        answer = ui.ask_text(">")

        expected = card["word"].lower()
        rom = card.get("romanization", "")
        correct = (answer and (answer.strip().lower() == expected or
                               (rom and answer.strip().lower() == rom.lower())))

        if correct:
            correct_count += 1
            cia_drills_ui.show_immersion_feedback(feedback.get("correct", "Richtig!"), True)
        else:
            cia_drills_ui.show_immersion_feedback(feedback.get("incorrect", "Falsch!"), False)
            console.print(f"  \u2192 [bold]{card['word']}[/bold]")
            if rom:
                console.print(f"  ({rom})")

        xp_info = app.gamification.award_xp("cia", 5 if correct else 1, lang_id)
        show_xp_gain(xp_info)

    pct = round(correct_count / max(total, 1) * 100)
    console.print(f"\n  {feedback.get('correct', 'Richtig')}: {correct_count}/{total} ({pct}%)")
    app.cia_engine.log_drill_session("immersion", 0, total, correct_count, 0, [lang_id])
    ui.wait_for_enter()


def _run_back_translation(app: AppContext) -> None:
    """Back-translation drill: target -> DE -> target."""
    from ui import terminal as ui

    languages = app.db.get_all_languages()
    lang_id = ui.show_language_selector(languages, "Sprache")
    if not lang_id:
        return

    items = app.cia_engine.prepare_back_translation(lang_id, 8)
    if not items:
        ui.show_info("Keine Woerter verfuegbar!")
        ui.wait_for_enter()
        return

    start_time = time.time()
    correct_count = 0

    for i, item in enumerate(items):
        ui.clear_screen()
        console.print(Panel(
            f"\U0001f504 BACK-TRANSLATION \u2014 {i+1}/{len(items)}",
            border_style="bold cyan",
        ))

        cia_drills_ui.show_back_translation_step(1, item["word"], item.get("romanization", ""))
        answer_de = ui.ask_text("Auf Deutsch:")
        step1_correct = answer_de and answer_de.strip().lower() == item["meaning_de"].lower()

        if step1_correct:
            console.print("  \u2705 Richtig!")
        else:
            console.print(f"  \u274c Richtig: {item['meaning_de']}")

        cia_drills_ui.show_back_translation_step(2, item["meaning_de"])
        answer_target = ui.ask_text("Zurueck:")

        expected = item["word"].lower()
        rom = item.get("romanization", "")
        step2_correct = (answer_target and
                        (answer_target.strip().lower() == expected or
                         (rom and answer_target.strip().lower() == rom.lower())))

        if step2_correct:
            correct_count += 1
            ui.show_success(item["word"])
        else:
            console.print(f"  \u274c Richtig: [bold]{item['word']}[/bold]")

        quality = 5 if (step1_correct and step2_correct) else (3 if step1_correct or step2_correct else 1)
        xp_info = app.gamification.award_xp("cia", quality, lang_id)
        show_xp_gain(xp_info)

    duration = int(time.time() - start_time)
    cia_drills_ui.show_drill_summary("Back-Translation", len(items), correct_count, duration)
    app.cia_engine.log_drill_session("back_translation", duration, len(items), correct_count, 0, [lang_id])
    ui.wait_for_enter()
