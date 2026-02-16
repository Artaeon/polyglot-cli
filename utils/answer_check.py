"""Unified answer checking with fuzzy matching for all engines."""

from __future__ import annotations


def check_answer(
    user_input: str,
    expected: str,
    alt_expected: str | None = None,
    alt_romanization: str | None = None,
) -> bool:
    """Check if user answer matches expected, with fuzzy matching.

    Handles: case folding, romanization fallback, Cyrillic ё/е equivalence,
    whitespace normalization.
    """
    if not user_input:
        return False

    user = _normalize(user_input)
    exp = _normalize(expected)

    if user == exp:
        return True

    # Accept alternative expected (e.g. romanization from recall card)
    if alt_expected and user == _normalize(alt_expected):
        return True

    # Accept romanization variant
    if alt_romanization and user == _normalize(alt_romanization):
        return True

    # Russian ё/е equivalence
    if _yo_normalize(user) == _yo_normalize(exp):
        return True

    return False


def _normalize(text: str) -> str:
    """Lowercase, strip, collapse whitespace."""
    return " ".join(text.strip().lower().split())


def _yo_normalize(text: str) -> str:
    """Normalize Cyrillic ё to е for comparison."""
    return text.replace("ё", "е")
