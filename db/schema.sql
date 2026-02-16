-- PolyglotCLI Database Schema

CREATE TABLE IF NOT EXISTS languages (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    native_name TEXT,
    flag TEXT,
    family TEXT,
    subfamily TEXT,
    script TEXT,
    difficulty_tier INTEGER,
    palace_name TEXT,
    palace_theme TEXT
);

CREATE TABLE IF NOT EXISTS words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    language_id TEXT REFERENCES languages(id),
    word TEXT NOT NULL,
    romanization TEXT,
    pronunciation_hint TEXT,
    meaning_de TEXT NOT NULL,
    meaning_en TEXT,
    category TEXT,
    frequency_rank INTEGER,
    concept_id TEXT,
    tone INTEGER,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS review_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER REFERENCES words(id),
    ease_factor REAL DEFAULT 2.5,
    interval INTEGER DEFAULT 0,
    repetitions INTEGER DEFAULT 0,
    next_review_date TEXT,
    last_review_date TEXT,
    total_reviews INTEGER DEFAULT 0,
    correct_reviews INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS palace_stations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    language_id TEXT REFERENCES languages(id),
    station_number INTEGER,
    station_name TEXT,
    word_id INTEGER REFERENCES words(id),
    user_mnemonic TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    duration_minutes INTEGER DEFAULT 0,
    words_learned INTEGER DEFAULT 0,
    words_reviewed INTEGER DEFAULT 0,
    languages_practiced TEXT,
    session_type TEXT
);

CREATE TABLE IF NOT EXISTS concepts (
    id TEXT PRIMARY KEY,
    meaning_de TEXT,
    meaning_en TEXT,
    category TEXT,
    frequency_rank INTEGER,
    etymology_note TEXT,
    mnemonic_hint TEXT
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_words_language ON words(language_id);
CREATE INDEX IF NOT EXISTS idx_words_concept ON words(concept_id);
CREATE INDEX IF NOT EXISTS idx_words_category ON words(category);
CREATE INDEX IF NOT EXISTS idx_review_next ON review_cards(next_review_date);
CREATE INDEX IF NOT EXISTS idx_review_word ON review_cards(word_id);
CREATE INDEX IF NOT EXISTS idx_palace_language ON palace_stations(language_id);
CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions(date);

-- ── Gamification & XP ────────────────────────────────────────

CREATE TABLE IF NOT EXISTS xp_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    action_type TEXT NOT NULL,
    base_xp INTEGER NOT NULL,
    quality_multiplier REAL DEFAULT 1.0,
    streak_bonus REAL DEFAULT 1.0,
    total_xp INTEGER NOT NULL,
    language_id TEXT,
    details TEXT
);

CREATE TABLE IF NOT EXISTS achievements (
    id TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    name_de TEXT NOT NULL,
    name_en TEXT NOT NULL,
    description_de TEXT,
    icon TEXT,
    threshold_value INTEGER,
    unlocked_at TEXT,
    xp_reward INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_xp_log_action ON xp_log(action_type);
CREATE INDEX IF NOT EXISTS idx_xp_log_lang ON xp_log(language_id);

-- ── Cloze Performance ────────────────────────────────────────

CREATE TABLE IF NOT EXISTS cloze_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER REFERENCES words(id),
    sentence_template_id TEXT,
    cloze_type TEXT,
    difficulty TEXT,
    attempts INTEGER DEFAULT 0,
    correct INTEGER DEFAULT 0,
    last_attempted TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cloze_word ON cloze_performance(word_id);

-- ── Conjugation Mastery ──────────────────────────────────────

CREATE TABLE IF NOT EXISTS conjugation_mastery (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    language_id TEXT REFERENCES languages(id),
    verb_concept_id TEXT,
    tense TEXT NOT NULL,
    person TEXT NOT NULL,
    attempts INTEGER DEFAULT 0,
    correct INTEGER DEFAULT 0,
    streak INTEGER DEFAULT 0,
    mastered BOOLEAN DEFAULT 0,
    last_attempted TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_conj_unique
    ON conjugation_mastery(language_id, verb_concept_id, tense, person);

-- ── Sentence Builder Performance ─────────────────────────────

CREATE TABLE IF NOT EXISTS builder_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    language_id TEXT REFERENCES languages(id),
    pattern_id TEXT,
    difficulty INTEGER,
    attempts INTEGER DEFAULT 0,
    correct INTEGER DEFAULT 0,
    last_attempted TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ── Speed Learning ───────────────────────────────────────────

CREATE TABLE IF NOT EXISTS keyword_mnemonics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER REFERENCES words(id) UNIQUE,
    keyword TEXT NOT NULL,
    story TEXT,
    user_created INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recall_chains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chain_date TEXT DEFAULT CURRENT_DATE,
    chain_length INTEGER DEFAULT 0,
    best_chain_length INTEGER DEFAULT 0
);

-- ── CIA Drill Sessions ───────────────────────────────────────

CREATE TABLE IF NOT EXISTS drill_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    drill_type TEXT NOT NULL,
    started_at TEXT DEFAULT CURRENT_TIMESTAMP,
    duration_seconds INTEGER,
    words_attempted INTEGER DEFAULT 0,
    words_correct INTEGER DEFAULT 0,
    avg_response_ms INTEGER,
    languages_used TEXT,
    difficulty_level INTEGER DEFAULT 1
);

-- ── Daily Challenges ───────────────────────────────────────────

CREATE TABLE IF NOT EXISTS daily_challenges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    challenge_date TEXT NOT NULL UNIQUE,
    challenge_type TEXT NOT NULL,
    data_json TEXT,
    completed INTEGER DEFAULT 0,
    score INTEGER DEFAULT 0,
    max_score INTEGER DEFAULT 0,
    xp_earned INTEGER DEFAULT 0,
    completed_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_daily_challenge_date ON daily_challenges(challenge_date);

-- ── Custom Vocabulary ──────────────────────────────────────────

CREATE TABLE IF NOT EXISTS custom_words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    language_id TEXT REFERENCES languages(id),
    word TEXT NOT NULL,
    romanization TEXT,
    meaning_de TEXT NOT NULL,
    meaning_en TEXT,
    tags TEXT,
    source TEXT DEFAULT 'manual',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_custom_words_lang ON custom_words(language_id);

-- ── Adaptive Difficulty ────────────────────────────────────────

CREATE TABLE IF NOT EXISTS difficulty_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    language_id TEXT REFERENCES languages(id),
    engine_type TEXT NOT NULL,
    current_difficulty REAL DEFAULT 1.0,
    consecutive_correct INTEGER DEFAULT 0,
    consecutive_wrong INTEGER DEFAULT 0,
    total_attempts INTEGER DEFAULT 0,
    last_updated TEXT,
    UNIQUE(language_id, engine_type)
);
