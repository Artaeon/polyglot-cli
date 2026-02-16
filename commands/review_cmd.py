"""Review command — SRS review session."""

from __future__ import annotations

import logging
import random
from typing import TYPE_CHECKING

from ui.terminal import console
from ui.gamification_ui import show_xp_gain, show_level_up

if TYPE_CHECKING:
    from app import AppContext

logger = logging.getLogger(__name__)


def run_review(app: AppContext, lang_filter: str | None = None) -> None:
    """Run SRS review session."""
    from ui import terminal as ui

    cards = app.db.get_due_cards(lang_id=lang_filter)
    if not cards:
        ui.clear_screen()
        if lang_filter:
            ui.show_info(f"Keine faelligen Reviews fuer {lang_filter.upper()}!")
        else:
            ui.show_info("Keine faelligen Reviews! Alles aufgearbeitet! \u2705")
        ui.wait_for_enter()
        return

    ui.clear_screen()
    total = len(cards)
    console.print(f"\n  \U0001f504 [bold]Review-Session: {total} Karten[/bold]\n")

    random.shuffle(cards)
    modes = ["recognition", "recall", "reverse"]

    for i, card in enumerate(cards):
        ui.clear_screen()
        mode = random.choice(modes)
        lang_name = card.get("lang_name", "")
        flag = card.get("flag", "")

        ui.show_quiz_header(lang_name, flag, i + 1, total)

        correct = False
        correct_answer = card["meaning_de"]

        if mode == "recognition":
            quiz_card = app.quiz_engine.prepare_recognition_card(card)
            choice = ui.show_recognition_quiz(quiz_card)
            if choice is not None:
                correct = quiz_card["options"][choice]["correct"]
                if not correct:
                    correct_answer = card["meaning_de"]
        elif mode == "recall":
            quiz_card = app.quiz_engine.prepare_recall_card(card)
            answer = ui.show_recall_quiz(quiz_card)
            if answer:
                correct = app.quiz_engine.check_answer(
                    answer, quiz_card["expected"],
                    quiz_card.get("alt_expected"),
                )
                correct_answer = f'{card["word"]}'
                if card.get("romanization"):
                    correct_answer += f' ({card["romanization"]})'
        else:  # reverse
            quiz_card = app.quiz_engine.prepare_reverse_card(card)
            answer = ui.show_reverse_quiz(quiz_card)
            if answer:
                correct = app.quiz_engine.check_answer(answer, quiz_card["expected"])
                correct_answer = card["meaning_de"]

        # Show cluster hints
        hints = []
        if card.get("concept_id"):
            hints = app.quiz_engine.get_cluster_hint(card["concept_id"])

        ui.show_answer_result(correct, correct_answer, hints[:6])

        # Get quality rating
        quality = ui.show_quality_prompt()

        # Process review
        result = app.quiz_engine.process_review(card["id"], quality)
        if result:
            ui.show_review_result(result)

        # Award XP
        old_level = app.gamification.get_level()
        xp_info = app.gamification.award_xp("review", quality, card["language_id"])
        show_xp_gain(xp_info)
        new_level = app.gamification.get_level()
        if new_level["level"] > old_level["level"]:
            show_level_up(old_level["level"], new_level["level"], new_level["rank"])

        app.session.words_reviewed += 1
        app.session.languages.add(card["language_id"])

        if i < total - 1:
            ui.wait_for_enter("Druecke [Enter] fuer naechste Karte...")

    console.print(f"\n  \U0001f389 Review-Session beendet! {total} Karten bearbeitet.")
    ui.wait_for_enter()
