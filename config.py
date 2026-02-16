"""PolyglotCLI configuration — paths, constants, defaults."""

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
WORDS_DIR = DATA_DIR / "words"
CLUSTERS_DIR = DATA_DIR / "clusters"
DB_DIR = BASE_DIR / "db"
DB_PATH = DB_DIR / "polyglot.db"
LANGUAGES_FILE = DATA_DIR / "languages.json"
COGNATES_FILE = CLUSTERS_DIR / "cognates.json"
DATA_VERSION = "2026.08"

# SRS defaults
SRS_INITIAL_EASE = 2.5
SRS_MIN_EASE = 1.3
SRS_INITIAL_INTERVAL = 0

# Sprint
DEFAULT_SPRINT_DAYS = 30
DEFAULT_DAILY_MINUTES = 90
DEFAULT_NEW_WORDS_PER_SESSION = 15

# CEFR thresholds (words known)
CEFR_LEVELS = {
    "pre": (0, 49),
    "A1-": (50, 99),
    "A1": (100, 199),
    "A1+": (200, 299),
    "A2-": (300, 499),
    "A2": (500, 699),
    "A2+": (700, 999),
    "B1-": (1000, float("inf")),
}

# Language family colors (for rich)
FAMILY_COLORS = {
    "slavic": "blue",
    "romance": "green",
    "sinosphere": "red",
    "uralic": "yellow",
    "germanic": "cyan",
}

FAMILY_LABELS = {
    "slavic": "SLAWISCH",
    "romance": "ROMANISCH",
    "sinosphere": "SINOSPHÄRE",
    "uralic": "URALISCH",
    "germanic": "GERMANISCH",
}

FAMILY_EMOJIS = {
    "slavic": "\U0001f535",
    "romance": "\U0001f7e2",
    "sinosphere": "\U0001f534",
    "uralic": "\U0001f7e1",
    "germanic": "\U0001f537",
}

# Quality grade labels for SRS
QUALITY_LABELS = [
    ("\u2b1b", "Blackout", "keine Ahnung"),
    ("\U0001f7e5", "Falsch", "aber jetzt erinnert"),
    ("\U0001f7e7", "Schwer", "mit viel Mühe erinnert"),
    ("\U0001f7e8", "Mittel", "nach Nachdenken"),
    ("\U0001f7e9", "Leicht", "erinnert mit kurzem Zögern"),
    ("\U0001f7e2", "Perfekt", "sofort gewusst"),
]

# Exercise limits
MIN_EXERCISE_COUNT = 5
MAX_EXERCISE_COUNT = 20

# Speed learning
MICRO_SESSION_SECONDS = 120
RAPID_ASSOC_DEFAULT_MS = 5000

# Mastery
MASTERY_STREAK_THRESHOLD = 3

# Shadowing exposure levels (seconds)
SHADOWING_EXPOSURE_LEVELS = {1: 4.0, 2: 3.0, 3: 2.0, 4: 1.5}

# Daily challenge
DAILY_CHALLENGE_BASE_XP = 50
DAILY_CHALLENGE_PERFECT_MULTIPLIER = 2

# Categories
WORD_CATEGORIES = [
    "pronomen_basics",
    "verben",
    "nomen",
    "adjektive",
    "zahlen",
    "phrasen",
    "zeitwoerter_konjunktionen",
    "fragen_richtungen",
    "koerper_gesundheit",
    "essen_trinken",
    "natur_wetter",
    "beruf_bildung",
]

# New feature paths
CONJUGATIONS_DIR = DATA_DIR / "conjugations"
BUILDER_DIR = DATA_DIR / "builder"
SENTENCES_FILE = DATA_DIR / "sentences" / "templates.json"

# XP constants
XP_BASE = {
    "review": 10,
    "learn": 25,
    "cloze": 15,
    "conjugation": 15,
    "drill": 15,
    "builder": 15,
    "speed": 15,
    "cia": 20,
}

# Rank names (German) by level thresholds
RANK_NAMES = [
    (1, "Anfaenger"),
    (5, "Wanderer"),
    (10, "Entdecker"),
    (15, "Sprachreisender"),
    (20, "Linguist"),
    (25, "Kenner"),
    (30, "Virtuose"),
    (35, "Polyglot"),
    (40, "Meister"),
    (45, "Grossmeister"),
]

CATEGORY_LABELS = {
    "pronomen_basics": "Pronomen & Basics",
    "verben": "Verben",
    "nomen": "Nomen (Alltag)",
    "adjektive": "Adjektive",
    "zahlen": "Zahlen",
    "phrasen": "Phrasen & Gruesze",
    "zeitwoerter_konjunktionen": "Zeitwoerter & Konjunktionen",
    "fragen_richtungen": "Fragen & Richtungen",
    "koerper_gesundheit": "Koerper & Gesundheit",
    "essen_trinken": "Essen & Trinken",
    "natur_wetter": "Natur & Wetter",
    "beruf_bildung": "Beruf & Bildung",
}

# XP actions for new features
XP_BASE_DAILY = 50
