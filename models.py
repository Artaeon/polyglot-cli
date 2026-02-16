"""Data models for PolyglotCLI."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


@dataclass
class Language:
    id: str
    name: str
    native_name: str
    flag: str
    family: str
    subfamily: str
    script: str
    difficulty_tier: int
    cluster_languages: list[str] = field(default_factory=list)
    transfer_rates: dict[str, float] = field(default_factory=dict)
    palace_name: str = ""
    palace_description: str = ""
    palace_theme: str = ""
    palace_stations: list[str] = field(default_factory=list)


@dataclass
class Word:
    id: int
    language_id: str
    word: str
    meaning_de: str
    meaning_en: str = ""
    romanization: str = ""
    pronunciation_hint: str = ""
    category: str = ""
    frequency_rank: int = 0
    concept_id: str = ""
    tone: Optional[int] = None
    notes: str = ""


@dataclass
class ReviewCard:
    id: int
    word_id: int
    ease_factor: float = 2.5
    interval: int = 0
    repetitions: int = 0
    next_review_date: Optional[date] = None
    last_review_date: Optional[date] = None
    total_reviews: int = 0
    correct_reviews: int = 0
    created_at: Optional[datetime] = None


@dataclass
class PalaceStation:
    id: int
    language_id: str
    station_number: int
    station_name: str
    word_id: Optional[int] = None
    user_mnemonic: str = ""
    created_at: Optional[datetime] = None


@dataclass
class Session:
    id: int
    date: str
    duration_minutes: int = 0
    words_learned: int = 0
    words_reviewed: int = 0
    languages_practiced: list[str] = field(default_factory=list)
    session_type: str = ""


@dataclass
class Concept:
    id: str
    meaning_de: str
    meaning_en: str
    category: str
    frequency_rank: int = 0
    etymology_note: str = ""
    mnemonic_hint: str = ""
    translations: dict = field(default_factory=dict)


@dataclass
class ClusterTranslation:
    word: str
    romanization: str = ""
    pronunciation_hint: str = ""
    tone: Optional[int] = None
    note: str = ""
    similarity_to: dict[str, float | str] = field(default_factory=dict)


@dataclass
class UserProfile:
    name: str = ""
    known_languages: list[str] = field(default_factory=list)
    daily_minutes: int = 90
    sprint_days: int = 30
    sprint_start: str = ""
    interface_language: str = "de"
