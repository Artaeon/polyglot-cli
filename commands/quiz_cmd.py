"""Quiz commands — cloze, conjugation, and builder exercises."""

from __future__ import annotations

import logging
import random
from typing import TYPE_CHECKING

from rich.panel import Panel

from ui.terminal import console
from ui.gamification_ui import show_xp_gain, show_level_up

if TYPE_CHECKING:
    from app import AppContext

logger = logging.getLogger(__name__)


def run_cloze(app: AppContext) -> None:
    """Run cloze (gap-fill) exercise session."""
    from ui import terminal as ui

    ui.clear_screen()
    console.print("\n  [bold]\U0001f4dd LUECKENTEXT[/bold]\n")

    languages = app.db.get_all_languages()
    lang_id = ui.show_language_selector(languages, "Sprache fuer Lueckentext")
    if not lang_id:
        return

    learned = app.cloze_engine._get_learned_words(lang_id)
    if not learned:
        ui.show_error("Noch keine Woerter gelernt in dieser Sprache! Lerne zuerst neue Woerter.")
        ui.wait_for_enter()
        return

    console.print("\n  Schwierigkeit:")
    console.print("  [1] Multiple Choice")
    console.print("  [2] Freitext")
    console.print("  [3] Gemischt")
    difficulty_choice = ui.ask_int(">", default=1)
    difficulty = {1: "mc", 2: "free", 3: "mixed"}.get(difficulty_choice, "mixed")

    count = ui.ask_int("Anzahl Uebungen (5-20):", default=10)
    count = max(5, min(20, count))

    items = app.cloze_engine.get_session_items(lang_id, count, difficulty)
    if not items:
        ui.show_error("Nicht genug Daten fuer Lueckentext-Uebungen.")
        ui.wait_for_enter()
        return

    correct_count = 0
    total = len(items)

    for i, item in enumerate(items):
        ui.clear_screen()
        console.print(Panel(
            f"\U0001f4dd LUECKENTEXT \u2014 {i + 1}/{total}",
            border_style="bold yellow",
        ))

        console.print(f"\n  [dim]DE: {item['german_ref']}[/dim]")
        console.print(f"\n  {item['sentence']}\n")

        if item.get("expected_romanization"):
            console.print("  [dim]Romanisierung verfuegbar[/dim]")

        user_answer = None
        if difficulty == "mc" or (difficulty == "mixed" and i % 2 == 0):
            options = [item["expected"]] + item.get("distractors", [])
            random.shuffle(options)
            for j, opt in enumerate(options, 1):
                console.print(f"  [{j}] {opt}")
            console.print()
            choice = ui.ask_int(">", default=1)
            if 1 <= choice <= len(options):
                user_answer = options[choice - 1]
        else:
            user_answer = ui.ask_text("Deine Antwort:")

        correct = app.cloze_engine.check_cloze_answer(
            user_answer or "", item["expected"],
            item.get("expected_romanization", ""),
        )

        if correct:
            correct_count += 1
            ui.show_success(f"Richtig! {item['full_sentence']}")
        else:
            console.print(
                f"  \u274c [bold red]Falsch![/bold red]  "
                f"Richtig: [bold]{item['expected']}[/bold]"
            )
            if item.get("expected_romanization"):
                console.print(f"  ({item['expected_romanization']})")
            console.print(f"  Ganzer Satz: {item['full_sentence']}")

        app.cloze_engine.process_cloze_result(
            item["word_id"], correct, item["type"], difficulty,
        )

        quality = 5 if correct else 1
        xp_info = app.gamification.award_xp("cloze", quality, lang_id)
        show_xp_gain(xp_info)

        app.session.words_reviewed += 1
        app.session.languages.add(lang_id)

        if i < total - 1:
            ui.wait_for_enter("Druecke [Enter] fuer naechste Uebung...")

    pct = round(correct_count / max(total, 1) * 100)
    console.print(f"\n  \U0001f389 Session beendet! {correct_count}/{total} richtig ({pct}%)")
    ui.wait_for_enter()


def run_conjugation(app: AppContext) -> None:
    """Run verb conjugation drill session."""
    from ui import terminal as ui
    from rich.table import Table
    from rich import box

    ui.clear_screen()
    console.print("\n  [bold]\U0001f4d6 KONJUGATION[/bold]\n")

    available_langs = app.conjugation_engine.get_available_languages()
    if not available_langs:
        ui.show_error("Keine Konjugationsdaten verfuegbar!")
        ui.wait_for_enter()
        return

    all_langs = app.db.get_all_languages()
    conj_langs = [lang for lang in all_langs if lang["id"] in available_langs]
    if not conj_langs:
        ui.show_error("Keine passenden Sprachen gefunden!")
        ui.wait_for_enter()
        return

    lang_id = ui.show_language_selector(conj_langs, "Sprache fuer Konjugation")
    if not lang_id:
        return

    console.print("\n  Modus:")
    console.print("  [1] Vorwaerts (Infinitiv -> Konjugierte Form)")
    console.print("  [2] Rueckwaerts (Form -> Infinitiv + Person)")
    console.print("  [3] Gemischt")
    console.print("  [4] Verbtabelle anzeigen")
    console.print("  [5] Meisterschaft-Uebersicht")
    mode = ui.ask_int(">", default=1)

    if mode == 4:
        _show_verb_table(app, lang_id)
        return
    if mode == 5:
        _show_conjugation_mastery(app, lang_id)
        return

    tenses = app.conjugation_engine.get_tenses(lang_id)
    tense_labels = app.conjugation_engine.get_tense_labels(lang_id)
    console.print("\n  Tempus:")
    console.print("  [0] Alle")
    for i, t in enumerate(tenses, 1):
        console.print(f"  [{i}] {tense_labels.get(t, t)}")
    tense_choice = ui.ask_int(">", default=0)
    tense_filter = tenses[tense_choice - 1] if 1 <= tense_choice <= len(tenses) else None

    count = ui.ask_int("Anzahl Uebungen (5-20):", default=10)
    count = max(5, min(20, count))

    if mode == 1:
        items = app.conjugation_engine.prepare_forward_drill(lang_id, tense_filter, count)
    elif mode == 2:
        items = app.conjugation_engine.prepare_reverse_drill(lang_id, tense_filter, count)
    else:
        items = app.conjugation_engine.prepare_mixed_drill(lang_id, tense_filter, count)

    if not items:
        ui.show_error("Nicht genug Daten fuer Konjugations-Drill!")
        ui.wait_for_enter()
        return

    correct_count = 0
    total = len(items)

    for i, item in enumerate(items):
        ui.clear_screen()
        console.print(Panel(
            f"\U0001f4d6 KONJUGATION \u2014 {i + 1}/{total}",
            border_style="bold blue",
        ))

        if item["type"] == "forward":
            console.print(f"\n  Infinitiv: [bold]{item['infinitive']}[/bold]")
            if item.get("romanization"):
                console.print(f"  ({item['romanization']})")
            console.print(f"  Person: [bold]{item['person_label']}[/bold]")
            console.print(f"  Tempus: [bold]{item['tense_label']}[/bold]\n")

            answer = ui.ask_text("Konjugierte Form:")
            correct = app.conjugation_engine.check_conjugation_answer(
                answer, item["expected"], item.get("expected_romanization", ""),
            )
            correct_answer = item["expected"]
            if item.get("expected_romanization"):
                correct_answer += f" ({item['expected_romanization']})"
        else:  # reverse
            console.print(f"\n  Konjugierte Form: [bold]{item['conjugated_form']}[/bold]")
            if item.get("conjugated_romanization"):
                console.print(f"  ({item['conjugated_romanization']})")
            console.print()

            answer = ui.ask_text("Infinitiv:")
            correct = app.conjugation_engine.check_conjugation_answer(
                answer, item["expected_infinitive"],
            )
            correct_answer = f"{item['expected_infinitive']} ({item['person_label']}, {item['tense_label']})"

        if correct:
            correct_count += 1
            ui.show_success(f"Richtig! {correct_answer}")
        else:
            console.print(
                f"  \u274c [bold red]Falsch![/bold red]  "
                f"Richtig: [bold]{correct_answer}[/bold]"
            )

        if item.get("pattern_id"):
            pattern = app.conjugation_engine.get_pattern_explanation(lang_id, item["pattern_id"])
            if pattern:
                console.print(f"  [dim]\U0001f4a1 Regel: {pattern.get('rule_de', '')}[/dim]")

        verb = item.get("verb", {})
        app.conjugation_engine.process_conjugation_result(
            lang_id, verb.get("concept_id", ""),
            item.get("tense", ""), item.get("person", item.get("expected_person", "")),
            correct,
        )
        quality = 5 if correct else 1
        xp_info = app.gamification.award_xp("conjugation", quality, lang_id)
        show_xp_gain(xp_info)

        app.session.words_reviewed += 1
        app.session.languages.add(lang_id)

        if i < total - 1:
            ui.wait_for_enter("Druecke [Enter] fuer naechste Uebung...")

    pct = round(correct_count / max(total, 1) * 100)
    console.print(f"\n  \U0001f389 Session beendet! {correct_count}/{total} richtig ({pct}%)")
    ui.wait_for_enter()


def _show_verb_table(app: AppContext, lang_id: str) -> None:
    """Show full conjugation table for a verb."""
    from ui import terminal as ui
    from rich.table import Table
    from rich import box

    verbs = app.conjugation_engine.get_verbs(lang_id)
    if not verbs:
        ui.show_error("Keine Verben verfuegbar!")
        ui.wait_for_enter()
        return

    console.print("\n  Verb waehlen:")
    for i, v in enumerate(verbs, 1):
        inf = v["infinitive"]
        rom = v.get("romanization", "")
        display = f"{inf} ({rom})" if rom else inf
        console.print(f"  [{i:2d}] {display}")
    console.print()

    choice = ui.ask_int(">", default=1)
    if not (1 <= choice <= len(verbs)):
        return

    verb = verbs[choice - 1]
    person_labels = app.conjugation_engine.get_person_labels(lang_id)
    tense_labels = app.conjugation_engine.get_tense_labels(lang_id)
    persons = app.conjugation_engine.get_persons(lang_id)

    inf_display = verb["infinitive"]
    if verb.get("romanization"):
        inf_display += f" ({verb['romanization']})"

    table = Table(
        title=f"\U0001f4d6 {inf_display}",
        box=box.ROUNDED,
        border_style="blue",
    )
    table.add_column("Person", min_width=18)
    forms = verb.get("forms") or verb.get("conjugations") or {}
    for tense in forms.keys():
        table.add_column(tense_labels.get(tense, tense), min_width=15)

    for person in persons:
        row = [person_labels.get(person, person)]
        for tense in forms.keys():
            form_data = forms.get(tense, {}).get(person, {})
            form = form_data.get("form", "-")
            rom = form_data.get("romanization", "")
            cell = f"{form} ({rom})" if rom else form
            row.append(cell)
        table.add_row(*row)

    ui.clear_screen()
    console.print(table)
    ui.wait_for_enter()


def _show_conjugation_mastery(app: AppContext, lang_id: str) -> None:
    """Show conjugation mastery overview."""
    from ui import terminal as ui
    from rich.table import Table
    from rich import box

    mastery = app.conjugation_engine.get_mastery_overview(lang_id)
    if not mastery:
        ui.show_info("Noch keine Konjugations-Uebungen absolviert!")
        ui.wait_for_enter()
        return

    tense_labels = app.conjugation_engine.get_tense_labels(lang_id)

    table = Table(
        title="\U0001f3c6 Konjugations-Meisterschaft",
        box=box.ROUNDED, border_style="green",
    )
    table.add_column("Verb", min_width=15)

    all_tenses: set[str] = set()
    for verb_data in mastery.values():
        all_tenses.update(verb_data.keys())
    for t in sorted(all_tenses):
        table.add_column(tense_labels.get(t, t), min_width=10)

    for verb_id, verb_data in mastery.items():
        row = [verb_id]
        for t in sorted(all_tenses):
            info = verb_data.get(t, {"total": 0, "mastered": 0})
            if info["total"] > 0:
                pct = round(info["mastered"] / info["total"] * 100)
                row.append(f"{pct}% ({info['mastered']}/{info['total']})")
            else:
                row.append("-")
        table.add_row(*row)

    ui.clear_screen()
    console.print(table)
    ui.wait_for_enter()


def run_builder(app: AppContext) -> None:
    """Run sentence builder exercises."""
    from ui import terminal as ui

    ui.clear_screen()
    console.print("\n  [bold]\U0001f3d7\ufe0f  SATZBAU[/bold]\n")

    languages = app.db.get_all_languages()
    lang_id = ui.show_language_selector(languages, "Sprache fuer Satzbau")
    if not lang_id:
        return

    can_start, reason = app.builder_engine.can_start(lang_id)
    if not can_start:
        ui.show_error(reason)
        ui.wait_for_enter()
        return

    count = ui.ask_int("Anzahl Uebungen (5-15):", default=8)
    count = max(5, min(15, count))

    exercises = app.builder_engine.get_session_exercises(lang_id, count)
    if not exercises:
        ui.show_error("Nicht genug Daten fuer Satzbau-Uebungen.")
        ui.wait_for_enter()
        return

    correct_count = 0
    total = len(exercises)
    current_diff = 1
    streak = 0

    for i, ex in enumerate(exercises):
        ui.clear_screen()
        console.print(Panel(
            f"\U0001f3d7\ufe0f  SATZBAU \u2014 {i + 1}/{total} (Stufe {current_diff})",
            border_style="bold green",
        ))

        console.print(f"\n  [dim]Muster: {ex['pattern']['name_de']}[/dim]")
        console.print(f"  [dim]{ex.get('grammar_note', '')}[/dim]")
        console.print(f"\n  Bedeutung: [bold]{ex['german_hint']}[/bold]\n")

        if current_diff <= 2:
            console.print("  Wortbank:")
            for j, word in enumerate(ex["word_bank"], 1):
                console.print(f"  [{j}] {word}", end="  ")
            console.print("\n")
            console.print("  [dim]Tipp: Woerter in der richtigen Reihenfolge eingeben[/dim]\n")

        answer = ui.ask_text("Dein Satz:")
        result = app.builder_engine.check_sentence(
            answer, ex["target_sentence"],
            ex.get("flexible_order", False), lang_id,
        )

        if result["correct"]:
            correct_count += 1
            streak += 1
            ui.show_success(f"Richtig! {ex['target_sentence']}")
            if result.get("note"):
                console.print(f"  [dim]{result['note']}[/dim]")
            if streak >= 3 and current_diff < 3:
                current_diff += 1
                streak = 0
                console.print(f"  \u2b06\ufe0f  [bold]Schwierigkeit erhoeht auf Stufe {current_diff}![/bold]")
        else:
            streak = max(0, streak - 2)
            console.print(
                f"  \u274c [bold red]Falsch![/bold red]  "
                f"Richtig: [bold]{ex['target_sentence']}[/bold]"
            )
            if streak <= -2 and current_diff > 1:
                current_diff -= 1
                streak = 0

        app.builder_engine.process_result(
            lang_id, ex["pattern"]["id"], ex["difficulty"], result["correct"],
        )
        quality = 5 if result["correct"] else 1
        xp_info = app.gamification.award_xp("builder", quality, lang_id)
        show_xp_gain(xp_info)

        app.session.words_reviewed += 1
        app.session.languages.add(lang_id)

        if i < total - 1:
            ui.wait_for_enter("Druecke [Enter] fuer naechste Uebung...")

    pct = round(correct_count / max(total, 1) * 100)
    console.print(f"\n  \U0001f389 Session beendet! {correct_count}/{total} richtig ({pct}%)")
    ui.wait_for_enter()
