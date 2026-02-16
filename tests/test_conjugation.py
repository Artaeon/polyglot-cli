"""Tests for the conjugation engine — data loading, drills, mastery."""

import pytest
from engines.conjugation import ConjugationEngine


@pytest.fixture
def conj_engine(populated_db):
    """ConjugationEngine with populated database."""
    return ConjugationEngine(populated_db)


def test_get_available_languages(conj_engine):
    """Available languages lists existing conjugation files."""
    langs = conj_engine.get_available_languages()
    assert isinstance(langs, list)
    # At least the original 6 files should exist
    assert "ru" in langs
    assert "es" in langs


def test_get_verbs(conj_engine):
    """Getting verbs for a supported language returns data."""
    verbs = conj_engine.get_verbs("ru")
    assert len(verbs) > 0
    assert "infinitive" in verbs[0] or "concept_id" in verbs[0]


def test_get_verbs_unsupported(conj_engine):
    """Getting verbs for unsupported language returns empty."""
    verbs = conj_engine.get_verbs("xx")
    assert verbs == []


def test_get_tenses(conj_engine):
    """Tenses are returned for supported languages."""
    tenses = conj_engine.get_tenses("ru")
    assert "present" in tenses


def test_get_persons(conj_engine):
    """Person labels are returned."""
    persons = conj_engine.get_persons("ru")
    assert "1sg" in persons
    assert "3pl" in persons


def test_get_person_labels(conj_engine):
    """German person labels are available."""
    labels = conj_engine.get_person_labels("es")
    assert isinstance(labels, dict)
    if labels:
        assert "1sg" in labels


def test_get_tense_labels(conj_engine):
    """German tense labels are available."""
    labels = conj_engine.get_tense_labels("fr")
    assert isinstance(labels, dict)


def test_caching(conj_engine):
    """Language data is cached after first load."""
    conj_engine.get_verbs("ru")
    assert "ru" in conj_engine._cache
    # Second call should use cache
    verbs = conj_engine.get_verbs("ru")
    assert len(verbs) > 0
