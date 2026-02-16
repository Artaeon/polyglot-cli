"""Tests for the unified answer checking utility."""

from utils.answer_check import check_answer


def test_exact_match():
    """Exact match returns True."""
    assert check_answer("Wasser", "Wasser") is True


def test_case_insensitive():
    """Case is ignored."""
    assert check_answer("wasser", "Wasser") is True
    assert check_answer("WASSER", "Wasser") is True


def test_whitespace_normalization():
    """Extra whitespace is collapsed."""
    assert check_answer("  Wasser  ", "Wasser") is True
    assert check_answer("guten  Tag", "guten Tag") is True


def test_romanization_fallback():
    """Romanization is accepted as alternative."""
    assert check_answer("voda", "вода", alt_romanization="voda") is True


def test_alt_expected():
    """Alternative expected string is checked."""
    assert check_answer("water", "Wasser", alt_expected="water") is True


def test_cyrillic_yo_equivalence():
    """Russian ё/е are treated as equivalent."""
    assert check_answer("ещё", "ещё") is True
    assert check_answer("еще", "ещё") is True
    assert check_answer("ещё", "еще") is True


def test_empty_input():
    """Empty input returns False."""
    assert check_answer("", "Wasser") is False
    assert check_answer("  ", "Wasser") is False


def test_wrong_answer():
    """Wrong answer returns False."""
    assert check_answer("Brot", "Wasser") is False


def test_no_romanization_no_match():
    """Without romanization param, romanization text doesn't match."""
    assert check_answer("voda", "вода") is False
