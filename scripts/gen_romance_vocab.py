#!/usr/bin/env python3
"""
Generate new vocabulary entries for the 5 Romance languages:
Italian (it), Spanish (es), Portuguese (pt), French (fr), Romanian (ro).

Adds 4 new categories (koerper_gesundheit, essen_trinken, natur_wetter,
beruf_bildung) with ~25 words each to each language JSON file.

Skips any concept_ids that already exist in the target file.
"""

import json
import os
import sys

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "words")

LANGUAGE_FILES = {
    "it": "italian.json",
    "es": "spanish.json",
    "pt": "portuguese.json",
    "fr": "french.json",
    "ro": "romanian.json",
}

# ---------------------------------------------------------------------------
# Category / concept metadata (shared across all languages)
# ---------------------------------------------------------------------------
CATEGORIES = {
    "koerper_gesundheit": [
        {"concept_id": "hand",          "meaning_de": "Hand",           "meaning_en": "hand"},
        {"concept_id": "fuss",          "meaning_de": "Fu\u00df",      "meaning_en": "foot"},
        {"concept_id": "zahn",          "meaning_de": "Zahn",          "meaning_en": "tooth"},
        {"concept_id": "ohr",           "meaning_de": "Ohr",           "meaning_en": "ear"},
        {"concept_id": "nase",          "meaning_de": "Nase",          "meaning_en": "nose"},
        {"concept_id": "mund",          "meaning_de": "Mund",          "meaning_en": "mouth"},
        {"concept_id": "finger",        "meaning_de": "Finger",        "meaning_en": "finger"},
        {"concept_id": "ruecken",       "meaning_de": "R\u00fccken",   "meaning_en": "back"},
        {"concept_id": "arm_body",      "meaning_de": "Arm",           "meaning_en": "arm"},
        {"concept_id": "bein",          "meaning_de": "Bein",          "meaning_en": "leg"},
        {"concept_id": "haut",          "meaning_de": "Haut",          "meaning_en": "skin"},
        {"concept_id": "blut",          "meaning_de": "Blut",          "meaning_en": "blood"},
        {"concept_id": "knochen",       "meaning_de": "Knochen",       "meaning_en": "bone"},
        {"concept_id": "krankenhaus",   "meaning_de": "Krankenhaus",   "meaning_en": "hospital"},
        {"concept_id": "medizin",       "meaning_de": "Medizin",       "meaning_en": "medicine"},
        {"concept_id": "krank",         "meaning_de": "krank",         "meaning_en": "sick"},
        {"concept_id": "gesund",        "meaning_de": "gesund",        "meaning_en": "healthy"},
        {"concept_id": "bauch",         "meaning_de": "Bauch",         "meaning_en": "stomach"},
        {"concept_id": "arzt",          "meaning_de": "Arzt",          "meaning_en": "doctor"},
        {"concept_id": "schmerz",       "meaning_de": "Schmerz",       "meaning_en": "pain"},
        {"concept_id": "fieber",        "meaning_de": "Fieber",        "meaning_en": "fever"},
        {"concept_id": "husten",        "meaning_de": "Husten",        "meaning_en": "cough"},
        {"concept_id": "apotheke",      "meaning_de": "Apotheke",      "meaning_en": "pharmacy"},
        {"concept_id": "zunge",         "meaning_de": "Zunge",         "meaning_en": "tongue"},
        {"concept_id": "schulter",      "meaning_de": "Schulter",      "meaning_en": "shoulder"},
    ],
    "essen_trinken": [
        {"concept_id": "fleisch",       "meaning_de": "Fleisch",       "meaning_en": "meat"},
        {"concept_id": "fisch",         "meaning_de": "Fisch",         "meaning_en": "fish"},
        {"concept_id": "reis",          "meaning_de": "Reis",          "meaning_en": "rice"},
        {"concept_id": "kaffee",        "meaning_de": "Kaffee",        "meaning_en": "coffee"},
        {"concept_id": "tee",           "meaning_de": "Tee",           "meaning_en": "tea"},
        {"concept_id": "bier",          "meaning_de": "Bier",          "meaning_en": "beer"},
        {"concept_id": "wein",          "meaning_de": "Wein",          "meaning_en": "wine"},
        {"concept_id": "suppe",         "meaning_de": "Suppe",         "meaning_en": "soup"},
        {"concept_id": "gemuese",       "meaning_de": "Gem\u00fcse",   "meaning_en": "vegetables"},
        {"concept_id": "obst",          "meaning_de": "Obst",          "meaning_en": "fruit"},
        {"concept_id": "ei",            "meaning_de": "Ei",            "meaning_en": "egg"},
        {"concept_id": "kaese",         "meaning_de": "K\u00e4se",     "meaning_en": "cheese"},
        {"concept_id": "zucker",        "meaning_de": "Zucker",        "meaning_en": "sugar"},
        {"concept_id": "salz",          "meaning_de": "Salz",          "meaning_en": "salt"},
        {"concept_id": "butter",        "meaning_de": "Butter",        "meaning_en": "butter"},
        {"concept_id": "oel",           "meaning_de": "\u00d6l",       "meaning_en": "oil"},
        {"concept_id": "kartoffel",     "meaning_de": "Kartoffel",     "meaning_en": "potato"},
        {"concept_id": "huhn",          "meaning_de": "Huhn",          "meaning_en": "chicken"},
        {"concept_id": "tomate",        "meaning_de": "Tomate",        "meaning_en": "tomato"},
        {"concept_id": "apfel",         "meaning_de": "Apfel",         "meaning_en": "apple"},
        {"concept_id": "kuchen",        "meaning_de": "Kuchen",        "meaning_en": "cake"},
        {"concept_id": "kochen",        "meaning_de": "kochen",        "meaning_en": "to cook"},
        {"concept_id": "restaurant",    "meaning_de": "Restaurant",    "meaning_en": "restaurant"},
        {"concept_id": "fruehstueck",   "meaning_de": "Fr\u00fchst\u00fcck", "meaning_en": "breakfast"},
        {"concept_id": "abendessen",    "meaning_de": "Abendessen",    "meaning_en": "dinner"},
    ],
    "natur_wetter": [
        {"concept_id": "wald",          "meaning_de": "Wald",          "meaning_en": "forest"},
        {"concept_id": "himmel",        "meaning_de": "Himmel",        "meaning_en": "sky"},
        {"concept_id": "stern",         "meaning_de": "Stern",         "meaning_en": "star"},
        {"concept_id": "erde",          "meaning_de": "Erde",          "meaning_en": "earth"},
        {"concept_id": "wind",          "meaning_de": "Wind",          "meaning_en": "wind"},
        {"concept_id": "wolke",         "meaning_de": "Wolke",         "meaning_en": "cloud"},
        {"concept_id": "donner",        "meaning_de": "Donner",        "meaning_en": "thunder"},
        {"concept_id": "insel",         "meaning_de": "Insel",         "meaning_en": "island"},
        {"concept_id": "see_lake",      "meaning_de": "See",           "meaning_en": "lake"},
        {"concept_id": "gras",          "meaning_de": "Gras",          "meaning_en": "grass"},
        {"concept_id": "stein",         "meaning_de": "Stein",         "meaning_en": "stone"},
        {"concept_id": "sand",          "meaning_de": "Sand",          "meaning_en": "sand"},
        {"concept_id": "eis",           "meaning_de": "Eis",           "meaning_en": "ice"},
        {"concept_id": "nebel",         "meaning_de": "Nebel",         "meaning_en": "fog"},
        {"concept_id": "strand",        "meaning_de": "Strand",        "meaning_en": "beach"},
        {"concept_id": "wueste",        "meaning_de": "W\u00fcste",    "meaning_en": "desert"},
        {"concept_id": "fruehling",     "meaning_de": "Fr\u00fchling", "meaning_en": "spring"},
        {"concept_id": "sommer",        "meaning_de": "Sommer",        "meaning_en": "summer"},
        {"concept_id": "herbst",        "meaning_de": "Herbst",        "meaning_en": "autumn"},
        {"concept_id": "winter",        "meaning_de": "Winter",        "meaning_en": "winter"},
        {"concept_id": "luft",          "meaning_de": "Luft",          "meaning_en": "air"},
        {"concept_id": "feuer",         "meaning_de": "Feuer",         "meaning_en": "fire"},
        {"concept_id": "sturm",         "meaning_de": "Sturm",         "meaning_en": "storm"},
        {"concept_id": "regenbogen",    "meaning_de": "Regenbogen",    "meaning_en": "rainbow"},
        {"concept_id": "feld",          "meaning_de": "Feld",          "meaning_en": "field"},
    ],
    "beruf_bildung": [
        {"concept_id": "lehrer",        "meaning_de": "Lehrer",        "meaning_en": "teacher"},
        {"concept_id": "schueler",      "meaning_de": "Sch\u00fcler",  "meaning_en": "student"},
        {"concept_id": "buero",         "meaning_de": "B\u00fcro",     "meaning_en": "office"},
        {"concept_id": "computer",      "meaning_de": "Computer",      "meaning_en": "computer"},
        {"concept_id": "universitaet",  "meaning_de": "Universit\u00e4t", "meaning_en": "university"},
        {"concept_id": "pruefung",      "meaning_de": "Pr\u00fcfung",  "meaning_en": "exam"},
        {"concept_id": "beruf",         "meaning_de": "Beruf",         "meaning_en": "profession"},
        {"concept_id": "chef",          "meaning_de": "Chef",          "meaning_en": "boss"},
        {"concept_id": "gehalt",        "meaning_de": "Gehalt",        "meaning_en": "salary"},
        {"concept_id": "ingenieur",     "meaning_de": "Ingenieur",     "meaning_en": "engineer"},
        {"concept_id": "rechtsanwalt",  "meaning_de": "Rechtsanwalt",  "meaning_en": "lawyer"},
        {"concept_id": "polizist",      "meaning_de": "Polizist",      "meaning_en": "police officer"},
        {"concept_id": "wissenschaft",  "meaning_de": "Wissenschaft",  "meaning_en": "science"},
        {"concept_id": "mathematik",    "meaning_de": "Mathematik",    "meaning_en": "mathematics"},
        {"concept_id": "geschichte",    "meaning_de": "Geschichte",    "meaning_en": "history"},
        {"concept_id": "sprache_lang",  "meaning_de": "Sprache",       "meaning_en": "language"},
        {"concept_id": "bibliothek",    "meaning_de": "Bibliothek",    "meaning_en": "library"},
        {"concept_id": "klasse",        "meaning_de": "Klasse",        "meaning_en": "class"},
        {"concept_id": "studieren",     "meaning_de": "studieren",     "meaning_en": "to study"},
        {"concept_id": "unterrichten",  "meaning_de": "unterrichten",  "meaning_en": "to teach"},
        {"concept_id": "aufgabe",       "meaning_de": "Aufgabe",       "meaning_en": "task"},
        {"concept_id": "erfahrung",     "meaning_de": "Erfahrung",     "meaning_en": "experience"},
        {"concept_id": "unternehmen",   "meaning_de": "Unternehmen",   "meaning_en": "company"},
        {"concept_id": "projekt",       "meaning_de": "Projekt",       "meaning_en": "project"},
        {"concept_id": "meeting",       "meaning_de": "Besprechung",   "meaning_en": "meeting"},
    ],
}

# ---------------------------------------------------------------------------
# Per-language translations: {lang: {concept_id: (word, pronunciation_hint, notes)}}
# ---------------------------------------------------------------------------
TRANSLATIONS = {
    # ==================================================================
    # ITALIAN
    # ==================================================================
    "it": {
        # --- koerper_gesundheit ---
        "hand":         ("mano",       "MAH-noh (betont auf 1. Silbe)",                                               "Feminine, irregular plural: mani"),
        "fuss":         ("piede",      "PYEH-deh (betont auf 1. Silbe; 'ie' = Diphthong)",                            "Masculine; plural: piedi"),
        "zahn":         ("dente",      "DEHN-teh (betont auf 1. Silbe; Doppelkonsonant-Klarheit)",                    "Masculine; plural: denti"),
        "ohr":          ("orecchio",   "oh-REHK-kyoh (betont auf 2. Silbe; 'cch' = langer k-Laut)",                  "Masculine; plural: orecchie (feminine!)"),
        "nase":         ("naso",       "NAH-zoh (betont auf 1. Silbe; 's' stimmhaft zwischen Vokalen)",              ""),
        "mund":         ("bocca",      "BOHK-kah (betont auf 1. Silbe; Doppel-c = langer k-Laut)",                   "Feminine"),
        "finger":       ("dito",       "DEE-toh (betont auf 1. Silbe)",                                               "Masculine; irregular plural: dita (feminine!)"),
        "ruecken":      ("schiena",    "SKYEH-nah ('sch' = sk vor 'ie'; betont auf 1. Silbe)",                        "Feminine"),
        "arm_body":     ("braccio",    "BRAHT-tschoh (betont auf 1. Silbe; 'cc' vor 'i' = 'tsch')",                  "Masculine; irregular plural: braccia (feminine!)"),
        "bein":         ("gamba",      "GAHM-bah (betont auf 1. Silbe; hartes 'g')",                                  "Feminine"),
        "haut":         ("pelle",      "PEHL-leh (betont auf 1. Silbe; Doppel-l)",                                    "Feminine"),
        "blut":         ("sangue",     "SAHN-gweh (betont auf 1. Silbe; 'gu' vor 'e' = 'gw')",                       "Masculine"),
        "knochen":      ("osso",       "OHS-soh (betont auf 1. Silbe; Doppel-s)",                                     "Masculine; irregular plural: ossa (feminine!)"),
        "krankenhaus":  ("ospedale",   "oh-speh-DAH-leh (betont auf 3. Silbe)",                                       "Masculine"),
        "medizin":      ("medicina",   "meh-dee-TSCHEE-nah (betont auf 3. Silbe; 'c' vor 'i' = 'tsch')",            "Feminine"),
        "krank":        ("malato",     "mah-LAH-toh (betont auf 2. Silbe)",                                           "Also used as noun: il malato = the patient"),
        "gesund":       ("sano",       "SAH-noh (betont auf 1. Silbe)",                                               ""),
        "bauch":        ("stomaco",    "STOH-mah-koh (betont auf 1. Silbe; 'c' vor 'o' = 'k')",                      "Masculine"),
        "arzt":         ("medico",     "MEH-dee-koh (betont auf 1. Silbe; 'c' vor 'o' = 'k')",                       "Masculine; feminine: medica"),
        "schmerz":      ("dolore",     "doh-LOH-reh (betont auf 2. Silbe)",                                           "Masculine"),
        "fieber":       ("febbre",     "FEHB-breh (betont auf 1. Silbe; Doppel-b)",                                   "Feminine"),
        "husten":       ("tosse",      "TOHS-seh (betont auf 1. Silbe; Doppel-s)",                                    "Feminine"),
        "apotheke":     ("farmacia",   "fahr-mah-TSCHEE-ah (betont auf 3. Silbe; 'c' vor 'i' = 'tsch')",            "Feminine"),
        "zunge":        ("lingua",     "LEEN-gwah (betont auf 1. Silbe; 'gu' vor 'a' = 'gw')",                       "Feminine; also means 'language'"),
        "schulter":     ("spalla",     "SPAHL-lah (betont auf 1. Silbe; Doppel-l)",                                   "Feminine"),

        # --- essen_trinken ---
        "fleisch":      ("carne",      "KAHR-neh (betont auf 1. Silbe; 'c' vor 'a' = 'k')",                          "Feminine"),
        "fisch":        ("pesce",      "PEH-scheh (betont auf 1. Silbe; 'sc' vor 'e' = 'sch')",                      "Masculine"),
        "reis":         ("riso",       "REE-zoh (betont auf 1. Silbe; 's' stimmhaft zwischen Vokalen)",              "Masculine; also means 'laughter'"),
        "kaffee":       ("caff\u00e8", "kahf-FEH (betont auf 2. Silbe; Doppel-f; offenes 'e')",                      "Masculine; invariable"),
        "tee":          ("t\u00e8",    "TEH (eine Silbe; offenes 'e')",                                                "Masculine; invariable"),
        "bier":         ("birra",      "BEER-rah (betont auf 1. Silbe; Doppel-r gerollt)",                            "Feminine"),
        "wein":         ("vino",       "VEE-noh (betont auf 1. Silbe)",                                                "Masculine"),
        "suppe":        ("zuppa",      "TSOOP-pah (betont auf 1. Silbe; 'z' = 'ts'; Doppel-p)",                      "Feminine"),
        "gemuese":      ("verdura",    "vehr-DOO-rah (betont auf 2. Silbe)",                                           "Feminine; often used in plural: verdure"),
        "obst":         ("frutta",     "FROOT-tah (betont auf 1. Silbe; Doppel-t)",                                   "Feminine; collective noun"),
        "ei":           ("uovo",       "WOH-voh (betont auf 1. Silbe; 'uo' = Diphthong)",                             "Masculine; irregular plural: uova (feminine!)"),
        "kaese":        ("formaggio",  "fohr-MAHD-joh (betont auf 2. Silbe; 'gg' vor 'i' = langer 'dsch')",          "Masculine"),
        "zucker":       ("zucchero",   "TSOOK-keh-roh (betont auf 1. Silbe; 'z' = 'ts'; 'cch' = langer k)",          "Masculine"),
        "salz":         ("sale",       "SAH-leh (betont auf 1. Silbe)",                                                "Masculine"),
        "butter":       ("burro",      "BOOR-roh (betont auf 1. Silbe; Doppel-r gerollt)",                            "Masculine"),
        "oel":          ("olio",       "OH-lyoh (betont auf 1. Silbe; 'li' vor Vokal = 'lj')",                        "Masculine"),
        "kartoffel":    ("patata",     "pah-TAH-tah (betont auf 2. Silbe)",                                            "Feminine"),
        "huhn":         ("pollo",      "POHL-loh (betont auf 1. Silbe; Doppel-l)",                                    "Masculine"),
        "tomate":       ("pomodoro",   "poh-moh-DOH-roh (betont auf 3. Silbe)",                                       "Masculine; plural: pomodori"),
        "apfel":        ("mela",       "MEH-lah (betont auf 1. Silbe)",                                                "Feminine"),
        "kuchen":       ("torta",      "TOHR-tah (betont auf 1. Silbe)",                                               "Feminine"),
        "kochen":       ("cucinare",   "koo-tschee-NAH-reh (betont auf 3. Silbe; 'c' vor 'i' = 'tsch')",            "Regular -are verb"),
        "restaurant":   ("ristorante", "ree-stoh-RAHN-teh (betont auf 3. Silbe)",                                     "Masculine"),
        "fruehstueck":  ("colazione",  "koh-lah-TSYOH-neh (betont auf 3. Silbe; 'z' = 'ts')",                        "Feminine"),
        "abendessen":   ("cena",       "TSCHEH-nah (betont auf 1. Silbe; 'c' vor 'e' = 'tsch')",                     "Feminine"),

        # --- natur_wetter ---
        "wald":         ("foresta",    "foh-REH-stah (betont auf 2. Silbe)",                                           "Feminine; also: bosco (masculine)"),
        "himmel":       ("cielo",      "TSCHEH-loh (betont auf 1. Silbe; 'c' vor 'i' = 'tsch')",                     "Masculine"),
        "stern":        ("stella",     "STEHL-lah (betont auf 1. Silbe; Doppel-l)",                                   "Feminine"),
        "erde":         ("terra",      "TEHR-rah (betont auf 1. Silbe; Doppel-r gerollt)",                            "Feminine"),
        "wind":         ("vento",      "VEHN-toh (betont auf 1. Silbe)",                                               "Masculine"),
        "wolke":        ("nuvola",     "NOO-voh-lah (betont auf 1. Silbe)",                                            "Feminine"),
        "donner":       ("tuono",      "TWOH-noh (betont auf 1. Silbe; 'uo' = Diphthong)",                            "Masculine"),
        "insel":        ("isola",      "EE-zoh-lah (betont auf 1. Silbe; 's' stimmhaft zwischen Vokalen)",           "Feminine"),
        "see_lake":     ("lago",       "LAH-goh (betont auf 1. Silbe; hartes 'g')",                                   "Masculine; plural: laghi"),
        "gras":         ("erba",       "EHR-bah (betont auf 1. Silbe)",                                                "Feminine"),
        "stein":        ("pietra",     "PYEH-trah (betont auf 1. Silbe; 'ie' = Diphthong)",                           "Feminine"),
        "sand":         ("sabbia",     "SAHB-byah (betont auf 1. Silbe; Doppel-b)",                                   "Feminine"),
        "eis":          ("ghiaccio",   "GYAHT-tschoh (betont auf 1. Silbe; 'gh' = hartes 'g'; 'cc' vor 'i' = 'tsch')", "Masculine"),
        "nebel":        ("nebbia",     "NEHB-byah (betont auf 1. Silbe; Doppel-b)",                                   "Feminine"),
        "strand":       ("spiaggia",   "SPYAHD-jah (betont auf 1. Silbe; 'gg' vor 'i' = langer 'dsch')",            "Feminine"),
        "wueste":       ("deserto",    "deh-ZEHR-toh (betont auf 2. Silbe; 's' stimmhaft)",                           "Masculine"),
        "fruehling":    ("primavera",  "pree-mah-VEH-rah (betont auf 3. Silbe)",                                      "Feminine"),
        "sommer":       ("estate",     "eh-STAH-teh (betont auf 2. Silbe)",                                            "Feminine"),
        "herbst":       ("autunno",    "ah-oo-TOON-noh (betont auf 2. Silbe; Doppel-n)",                              "Masculine"),
        "winter":       ("inverno",    "een-VEHR-noh (betont auf 2. Silbe)",                                           "Masculine"),
        "luft":         ("aria",       "AH-ryah (betont auf 1. Silbe)",                                                "Feminine"),
        "feuer":        ("fuoco",      "FWOH-koh (betont auf 1. Silbe; 'uo' = Diphthong)",                            "Masculine"),
        "sturm":        ("tempesta",   "tehm-PEH-stah (betont auf 2. Silbe)",                                         "Feminine"),
        "regenbogen":   ("arcobaleno", "ahr-koh-bah-LEH-noh (betont auf 4. Silbe)",                                   "Masculine"),
        "feld":         ("campo",      "KAHM-poh (betont auf 1. Silbe)",                                               "Masculine"),

        # --- beruf_bildung ---
        "lehrer":       ("insegnante",  "een-seh-NYAHN-teh (betont auf 3. Silbe; 'gn' = 'nj' wie in 'Cognac')",     "Masculine/Feminine (same form)"),
        "schueler":     ("studente",    "stoo-DEHN-teh (betont auf 2. Silbe)",                                        "Masculine; feminine: studentessa"),
        "buero":        ("ufficio",     "oof-FEE-tschoh (betont auf 2. Silbe; Doppel-f; 'c' vor 'i' = 'tsch')",     "Masculine"),
        "computer":     ("computer",    "kohm-PYOO-tehr (betont auf 2. Silbe; wie im Englischen)",                    "Masculine; invariable"),
        "universitaet": ("universit\u00e0", "oo-nee-vehr-see-TAH (betont auf letzte Silbe; Akzent auf \u00e0)",      "Feminine; invariable"),
        "pruefung":     ("esame",       "eh-ZAH-meh (betont auf 2. Silbe; 's' stimmhaft)",                           "Masculine"),
        "beruf":        ("professione", "proh-fehs-SYOH-neh (betont auf 3. Silbe)",                                   "Feminine"),
        "chef":         ("capo",        "KAH-poh (betont auf 1. Silbe)",                                              "Masculine; feminine: capa (rare)"),
        "gehalt":       ("stipendio",   "stee-PEHN-dyoh (betont auf 2. Silbe)",                                       "Masculine"),
        "ingenieur":    ("ingegnere",   "een-jeh-NYEH-reh (betont auf 3. Silbe; 'gn' = 'nj')",                       "Masculine; feminine: ingegnera (rare)"),
        "rechtsanwalt": ("avvocato",    "ahv-voh-KAH-toh (betont auf 3. Silbe; Doppel-v)",                           "Masculine; feminine: avvocata/avvocatessa"),
        "polizist":     ("poliziotto",  "poh-lee-tsee-OHT-toh (betont auf 4. Silbe; 'z' = 'ts'; Doppel-t)",         "Masculine; feminine: poliziotta"),
        "wissenschaft": ("scienza",     "SHEHN-tsah (betont auf 1. Silbe; 'sc' vor 'i' = 'sch'; 'z' = 'ts')",       "Feminine"),
        "mathematik":   ("matematica",  "mah-teh-MAH-tee-kah (betont auf 3. Silbe)",                                  "Feminine"),
        "geschichte":   ("storia",      "STOH-ryah (betont auf 1. Silbe)",                                             "Feminine"),
        "sprache_lang": ("lingua",      "LEEN-gwah (betont auf 1. Silbe; 'gu' vor 'a' = 'gw')",                      "Feminine; also means 'tongue'"),
        "bibliothek":   ("biblioteca",  "bee-blee-oh-TEH-kah (betont auf 4. Silbe)",                                  "Feminine"),
        "klasse":       ("classe",      "KLAHS-seh (betont auf 1. Silbe; Doppel-s)",                                  "Feminine"),
        "studieren":    ("studiare",    "stoo-DYAH-reh (betont auf 2. Silbe; 'i' gleitet)",                           "Regular -are verb"),
        "unterrichten": ("insegnare",   "een-seh-NYAH-reh (betont auf 3. Silbe; 'gn' = 'nj')",                       "Regular -are verb"),
        "aufgabe":      ("compito",     "KOHM-pee-toh (betont auf 1. Silbe)",                                         "Masculine"),
        "erfahrung":    ("esperienza",  "eh-speh-RYEHN-tsah (betont auf 3. Silbe; 'z' = 'ts')",                      "Feminine"),
        "unternehmen":  ("azienda",     "ah-TSYEHN-dah (betont auf 2. Silbe; 'z' = 'ts')",                           "Feminine"),
        "projekt":      ("progetto",    "proh-JEHT-toh (betont auf 2. Silbe; 'g' vor 'e' = 'dsch'; Doppel-t)",       "Masculine"),
        "meeting":      ("riunione",    "ree-oo-NYOH-neh (betont auf 3. Silbe)",                                      "Feminine"),
    },

    # ==================================================================
    # SPANISH
    # ==================================================================
    "es": {
        # --- koerper_gesundheit ---
        "hand":         ("mano",       "MAH-noh (betont auf 1. Silbe)",                                               "Feminine despite ending in -o"),
        "fuss":         ("pie",        "PYEH (eine Silbe; Diphthong 'ie')",                                           "Masculine"),
        "zahn":         ("diente",     "DYEHN-teh (betont auf 1. Silbe; 'ie' = Diphthong)",                          "Masculine"),
        "ohr":          ("oreja",      "oh-REH-hah (betont auf 2. Silbe; 'j' = deutsches 'ch' in 'ach')",            "Feminine"),
        "nase":         ("nariz",      "nah-REES (betont auf 2. Silbe; 'z' = 's' in Latam, 'th' in Spanien)",        "Feminine"),
        "mund":         ("boca",       "BOH-kah (betont auf 1. Silbe)",                                                "Feminine"),
        "finger":       ("dedo",       "DEH-doh (betont auf 1. Silbe; 'd' weich zwischen Vokalen)",                  "Masculine; also means 'toe'"),
        "ruecken":      ("espalda",    "ehs-PAHL-dah (betont auf 2. Silbe)",                                          "Feminine"),
        "arm_body":     ("brazo",      "BRAH-soh (betont auf 1. Silbe; 'z' = 's'/'th')",                             "Masculine"),
        "bein":         ("pierna",     "PYEHR-nah (betont auf 1. Silbe; 'ie' = Diphthong)",                           "Feminine"),
        "haut":         ("piel",       "PYEHL (eine Silbe; 'ie' = Diphthong)",                                        "Feminine"),
        "blut":         ("sangre",     "SAHN-greh (betont auf 1. Silbe)",                                              "Feminine"),
        "knochen":      ("hueso",      "WEH-soh (betont auf 1. Silbe; 'h' stumm; 'ue' = Diphthong)",                 "Masculine"),
        "krankenhaus":  ("hospital",   "ohs-pee-TAHL (betont auf 3. Silbe; 'h' stumm)",                               "Masculine"),
        "medizin":      ("medicina",   "meh-dee-SEE-nah (betont auf 3. Silbe; 'c' vor 'i' = 's'/'th')",              "Feminine"),
        "krank":        ("enfermo",    "ehn-FEHR-moh (betont auf 2. Silbe)",                                           "Also noun: patient"),
        "gesund":       ("sano",       "SAH-noh (betont auf 1. Silbe)",                                                ""),
        "bauch":        ("est\u00f3mago", "ehs-TOH-mah-goh (betont auf 2. Silbe; Akzent auf 'o')",                   "Masculine"),
        "arzt":         ("m\u00e9dico",   "MEH-dee-koh (betont auf 1. Silbe; esdr\u00fajula)",                        "Masculine; feminine: m\u00e9dica"),
        "schmerz":      ("dolor",      "doh-LOHR (betont auf 2. Silbe)",                                               "Masculine"),
        "fieber":       ("fiebre",     "FYEH-breh (betont auf 1. Silbe; 'ie' = Diphthong)",                           "Feminine"),
        "husten":       ("tos",        "TOHS (eine Silbe; 's' stimmlos)",                                              "Feminine"),
        "apotheke":     ("farmacia",   "fahr-MAH-syah (betont auf 2. Silbe; 'c' vor 'i' = 's'/'th')",                "Feminine"),
        "zunge":        ("lengua",     "LEHN-gwah (betont auf 1. Silbe; 'gu' vor 'a' = 'gw')",                       "Feminine; also means 'language'"),
        "schulter":     ("hombro",     "OHM-broh (betont auf 1. Silbe; 'h' stumm)",                                   "Masculine"),

        # --- essen_trinken ---
        "fleisch":      ("carne",      "KAHR-neh (betont auf 1. Silbe)",                                               "Feminine"),
        "fisch":        ("pescado",    "pehs-KAH-doh (betont auf 2. Silbe)",                                           "Masculine; pez = live fish"),
        "reis":         ("arroz",      "ah-RROHS (betont auf 2. Silbe; 'rr' stark gerollt; 'z' = 's'/'th')",         "Masculine"),
        "kaffee":       ("caf\u00e9",  "kah-FEH (betont auf 2. Silbe; Akzent auf 'e')",                               "Masculine"),
        "tee":          ("t\u00e9",    "TEH (eine Silbe; Akzent auf 'e')",                                             "Masculine"),
        "bier":         ("cerveza",    "sehr-VEH-sah (betont auf 2. Silbe; 'c' vor 'e' = 's'/'th'; 'z' = 's'/'th')", "Feminine"),
        "wein":         ("vino",       "VEE-noh (betont auf 1. Silbe; 'v' = weiches 'b')",                            "Masculine"),
        "suppe":        ("sopa",       "SOH-pah (betont auf 1. Silbe)",                                                "Feminine"),
        "gemuese":      ("verduras",   "vehr-DOO-rahs (betont auf 2. Silbe; 'v' = weiches 'b')",                      "Feminine plural; singular: verdura"),
        "obst":         ("fruta",      "FROO-tah (betont auf 1. Silbe)",                                               "Feminine"),
        "ei":           ("huevo",      "WEH-voh (betont auf 1. Silbe; 'h' stumm; 'ue' = Diphthong)",                  "Masculine"),
        "kaese":        ("queso",      "KEH-soh (betont auf 1. Silbe; 'qu' = 'k')",                                   "Masculine"),
        "zucker":       ("az\u00facar","ah-SOO-kahr (betont auf 2. Silbe; 'z' = 's'/'th')",                           "Masculine"),
        "salz":         ("sal",        "SAHL (eine Silbe)",                                                             "Feminine"),
        "butter":       ("mantequilla","mahn-teh-KEE-yah (betont auf 3. Silbe; 'll' = 'j')",                          "Feminine"),
        "oel":          ("aceite",     "ah-SAY-teh (betont auf 2. Silbe; 'c' vor 'e' = 's'/'th')",                    "Masculine"),
        "kartoffel":    ("patata",     "pah-TAH-tah (betont auf 2. Silbe)",                                            "Feminine; Latam: papa"),
        "huhn":         ("pollo",      "POH-yoh (betont auf 1. Silbe; 'll' = 'j')",                                   "Masculine"),
        "tomate":       ("tomate",     "toh-MAH-teh (betont auf 2. Silbe)",                                            "Masculine"),
        "apfel":        ("manzana",    "mahn-SAH-nah (betont auf 2. Silbe; 'z' = 's'/'th')",                          "Feminine"),
        "kuchen":       ("pastel",     "pahs-TEHL (betont auf 2. Silbe)",                                              "Masculine; also: tarta"),
        "kochen":       ("cocinar",    "koh-see-NAHR (betont auf 3. Silbe; 'c' vor 'i' = 's'/'th')",                  "Regular -ar verb"),
        "restaurant":   ("restaurante","rehs-tah-oo-RAHN-teh (betont auf 4. Silbe; gerolltes 'r')",                   "Masculine"),
        "fruehstueck":  ("desayuno",   "deh-sah-YOO-noh (betont auf 3. Silbe; 'y' = 'j')",                           "Masculine"),
        "abendessen":   ("cena",       "SEH-nah (betont auf 1. Silbe; 'c' vor 'e' = 's'/'th')",                      "Feminine"),

        # --- natur_wetter ---
        "wald":         ("bosque",     "BOHS-keh (betont auf 1. Silbe; 'qu' = 'k')",                                  "Masculine"),
        "himmel":       ("cielo",      "SYEH-loh (betont auf 1. Silbe; 'c' vor 'i' = 's'/'th')",                     "Masculine"),
        "stern":        ("estrella",   "ehs-TREH-yah (betont auf 2. Silbe; 'll' = 'j'; gerolltes 'r')",              "Feminine"),
        "erde":         ("tierra",     "TYEHR-rah (betont auf 1. Silbe; 'ie' = Diphthong; 'rr' gerollt)",            "Feminine"),
        "wind":         ("viento",     "VYEHN-toh (betont auf 1. Silbe; 'v' = weiches 'b'; 'ie' = Diphthong)",       "Masculine"),
        "wolke":        ("nube",       "NOO-beh (betont auf 1. Silbe)",                                                "Feminine"),
        "donner":       ("trueno",     "TRWEH-noh (betont auf 1. Silbe; 'ue' = Diphthong; gerolltes 'r')",           "Masculine"),
        "insel":        ("isla",       "EES-lah (betont auf 1. Silbe)",                                                "Feminine"),
        "see_lake":     ("lago",       "LAH-goh (betont auf 1. Silbe; hartes 'g')",                                   "Masculine"),
        "gras":         ("hierba",     "YEHR-bah (betont auf 1. Silbe; 'h' stumm; 'ie' = Diphthong)",                "Feminine"),
        "stein":        ("piedra",     "PYEH-drah (betont auf 1. Silbe; 'ie' = Diphthong)",                           "Feminine"),
        "sand":         ("arena",      "ah-REH-nah (betont auf 2. Silbe; gerolltes 'r')",                             "Feminine"),
        "eis":          ("hielo",      "YEH-loh (betont auf 1. Silbe; 'h' stumm; 'ie' = Diphthong)",                 "Masculine"),
        "nebel":        ("niebla",     "NYEH-blah (betont auf 1. Silbe; 'ie' = Diphthong)",                           "Feminine"),
        "strand":       ("playa",      "PLAH-yah (betont auf 1. Silbe; 'y' = 'j')",                                   "Feminine"),
        "wueste":       ("desierto",   "deh-SYEHR-toh (betont auf 2. Silbe; 'ie' = Diphthong)",                       "Masculine"),
        "fruehling":    ("primavera",  "pree-mah-VEH-rah (betont auf 3. Silbe; gerolltes 'r')",                       "Feminine"),
        "sommer":       ("verano",     "veh-RAH-noh (betont auf 2. Silbe; 'v' = weiches 'b'; gerolltes 'r')",        "Masculine"),
        "herbst":       ("oto\u00f1o", "oh-TOH-nyoh (betont auf 2. Silbe; '\u00f1' = 'nj')",                         "Masculine"),
        "winter":       ("invierno",   "een-VYEHR-noh (betont auf 2. Silbe; 'v' = weiches 'b'; 'ie' = Diphthong)",   "Masculine"),
        "luft":         ("aire",       "AH-ee-reh (betont auf 1. Silbe; Diphthong 'ai')",                             "Masculine"),
        "feuer":        ("fuego",      "FWEH-goh (betont auf 1. Silbe; 'ue' = Diphthong)",                            "Masculine"),
        "sturm":        ("tormenta",   "tohr-MEHN-tah (betont auf 2. Silbe; gerolltes 'r')",                          "Feminine"),
        "regenbogen":   ("arco\u00edris", "ahr-koh-EE-rees (betont auf 3. Silbe; Akzent auf '\u00ed')",               "Masculine"),
        "feld":         ("campo",      "KAHM-poh (betont auf 1. Silbe)",                                               "Masculine"),

        # --- beruf_bildung ---
        "lehrer":       ("profesor",      "proh-feh-SOHR (betont auf 3. Silbe; gerolltes 'r')",                       "Masculine; feminine: profesora"),
        "schueler":     ("estudiante",    "ehs-too-DYAHN-teh (betont auf 3. Silbe)",                                  "Masculine/Feminine (same form)"),
        "buero":        ("oficina",       "oh-fee-SEE-nah (betont auf 3. Silbe; 'c' vor 'i' = 's'/'th')",            "Feminine"),
        "computer":     ("computadora",   "kohm-poo-tah-DOH-rah (betont auf 4. Silbe)",                               "Feminine; Spain: ordenador (masculine)"),
        "universitaet": ("universidad",   "oo-nee-vehr-see-DAHD (betont auf 5. Silbe; 'd' am Ende weich)",            "Feminine"),
        "pruefung":     ("examen",        "ehk-SAH-mehn (betont auf 2. Silbe; 'x' = 'ks')",                           "Masculine; plural: ex\u00e1menes"),
        "beruf":        ("profesi\u00f3n","proh-feh-SYOHN (betont auf 3. Silbe; Akzent auf '\u00f3')",                "Feminine"),
        "chef":         ("jefe",          "HEH-feh (betont auf 1. Silbe; 'j' = deutsches 'ch' in 'ach')",            "Masculine; feminine: jefa"),
        "gehalt":       ("salario",       "sah-LAH-ryoh (betont auf 2. Silbe)",                                        "Masculine"),
        "ingenieur":    ("ingeniero",     "een-heh-NYEH-roh (betont auf 3. Silbe; 'g' vor 'e' = 'ch'/'h')",          "Masculine; feminine: ingeniera"),
        "rechtsanwalt": ("abogado",       "ah-boh-GAH-doh (betont auf 3. Silbe; 'b' weich; 'g' hart)",               "Masculine; feminine: abogada"),
        "polizist":     ("polic\u00eda",  "poh-lee-SEE-ah (betont auf 3. Silbe; Akzent bricht Diphthong)",            "Masculine/Feminine (same form)"),
        "wissenschaft": ("ciencia",       "SYEHN-syah (betont auf 1. Silbe; 'c' vor 'i' = 's'/'th')",                "Feminine"),
        "mathematik":   ("matem\u00e1ticas", "mah-teh-MAH-tee-kahs (betont auf 3. Silbe)",                            "Feminine plural"),
        "geschichte":   ("historia",      "ees-TOH-ryah (betont auf 2. Silbe; 'h' stumm)",                            "Feminine"),
        "sprache_lang": ("idioma",        "ee-DYOH-mah (betont auf 2. Silbe; Diphthong 'io')",                        "Masculine despite ending in -a; also: lengua"),
        "bibliothek":   ("biblioteca",    "bee-blyoh-TEH-kah (betont auf 3. Silbe)",                                  "Feminine"),
        "klasse":       ("clase",         "KLAH-seh (betont auf 1. Silbe)",                                            "Feminine"),
        "studieren":    ("estudiar",      "ehs-too-DYAHR (betont auf 3. Silbe)",                                       "Regular -ar verb"),
        "unterrichten": ("ense\u00f1ar",  "ehn-seh-NYAHR (betont auf 3. Silbe; '\u00f1' = 'nj')",                    "Regular -ar verb"),
        "aufgabe":      ("tarea",         "tah-REH-ah (betont auf 2. Silbe)",                                          "Feminine"),
        "erfahrung":    ("experiencia",   "ehks-peh-RYEHN-syah (betont auf 3. Silbe; 'x' = 'ks')",                   "Feminine"),
        "unternehmen":  ("empresa",       "ehm-PREH-sah (betont auf 2. Silbe)",                                        "Feminine"),
        "projekt":      ("proyecto",      "proh-YEHK-toh (betont auf 2. Silbe; 'y' = 'j')",                           "Masculine"),
        "meeting":      ("reuni\u00f3n",  "reh-oo-NYOHN (betont auf 3. Silbe; Akzent auf '\u00f3'; gerolltes 'r')",  "Feminine"),
    },

    # ==================================================================
    # PORTUGUESE
    # ==================================================================
    "pt": {
        # --- koerper_gesundheit ---
        "hand":         ("m\u00e3o",      "MOWNG ('m' + nasales 'au'; eine Silbe durch die Nase)",                    "Feminine; plural: m\u00e3os"),
        "fuss":         ("p\u00e9",       "PEH (eine Silbe; offenes 'e' mit Akzent)",                                  "Masculine; plural: p\u00e9s"),
        "zahn":         ("dente",         "DEHN-tee (betont auf 1. Silbe; 'e' am Ende = 'i' in Brasilien)",            "Masculine"),
        "ohr":          ("orelha",        "oh-REH-lyah (betont auf 2. Silbe; 'lh' = 'lj')",                           "Feminine"),
        "nase":         ("nariz",         "nah-REESH (betont auf 2. Silbe; 'z' am Ende = 'sch')",                      "Masculine"),
        "mund":         ("boca",          "BOH-kah (betont auf 1. Silbe)",                                              "Feminine"),
        "finger":       ("dedo",          "DEH-doo (betont auf 1. Silbe; 'o' am Ende = 'u')",                          "Masculine; also means 'toe'"),
        "ruecken":      ("costas",        "KOHSH-tahsh (betont auf 1. Silbe; 's' = 'sch')",                            "Feminine plural; always used in plural"),
        "arm_body":     ("bra\u00e7o",    "BRAH-soo (betont auf 1. Silbe; '\u00e7' = 's')",                            "Masculine"),
        "bein":         ("perna",         "PEHR-nah (betont auf 1. Silbe)",                                              "Feminine"),
        "haut":         ("pele",          "PEH-lee (betont auf 1. Silbe; 'e' am Ende = 'i')",                          "Feminine"),
        "blut":         ("sangue",        "SAHN-gee (betont auf 1. Silbe; 'gu' vor 'e' = 'g' + kurzes 'i')",          "Masculine"),
        "knochen":      ("osso",          "OH-soo (betont auf 1. Silbe; Doppel-s stimmlos)",                            "Masculine"),
        "krankenhaus":  ("hospital",      "ohsh-pee-TAHL (betont auf 3. Silbe; 'h' stumm; 's' vor 'p' = 'sch')",     "Masculine"),
        "medizin":      ("medicina",      "meh-dee-SEE-nah (betont auf 3. Silbe)",                                      "Feminine"),
        "krank":        ("doente",        "doo-EHN-tee (betont auf 2. Silbe; 'e' am Ende = 'i')",                      "Masculine/Feminine (same form)"),
        "gesund":       ("saud\u00e1vel", "sah-oo-DAH-vehl (betont auf 3. Silbe; Akzent auf '\u00e1')",               "Masculine/Feminine (same form)"),
        "bauch":        ("est\u00f4mago", "esh-TOH-mah-goo (betont auf 2. Silbe; '\u00f4' = geschlossenes 'o')",      "Masculine"),
        "arzt":         ("m\u00e9dico",   "MEH-dee-koo (betont auf 1. Silbe; Akzent auf '\u00e9')",                    "Masculine; feminine: m\u00e9dica"),
        "schmerz":      ("dor",           "DOHR (eine Silbe; 'r' am Ende uvul\u00e4r)",                                "Feminine"),
        "fieber":       ("febre",         "FEH-bree (betont auf 1. Silbe; 'e' am Ende = 'i')",                        "Feminine"),
        "husten":       ("tosse",         "TOH-see (betont auf 1. Silbe; Doppel-s stimmlos)",                           "Feminine"),
        "apotheke":     ("farm\u00e1cia", "fahr-MAH-syah (betont auf 2. Silbe; Akzent auf '\u00e1')",                 "Feminine"),
        "zunge":        ("l\u00edngua",   "LEEN-gwah (betont auf 1. Silbe; Akzent auf '\u00ed'; 'gu' = 'gw')",        "Feminine; also means 'language'"),
        "schulter":     ("ombro",         "OHM-broo (betont auf 1. Silbe)",                                             "Masculine"),

        # --- essen_trinken ---
        "fleisch":      ("carne",         "KAHR-nee (betont auf 1. Silbe; 'e' am Ende = 'i')",                        "Feminine"),
        "fisch":        ("peixe",         "PAY-shee (betont auf 1. Silbe; 'ei' = 'ay'; 'x' = 'sch')",                "Masculine"),
        "reis":         ("arroz",         "ah-ROHSH (betont auf 2. Silbe; 'rr' uvul\u00e4r; 'z' am Ende = 'sch')",   "Masculine"),
        "kaffee":       ("caf\u00e9",     "kah-FEH (betont auf 2. Silbe; Akzent auf '\u00e9')",                        "Masculine"),
        "tee":          ("ch\u00e1",      "SHAH (eine Silbe; 'ch' = 'sch')",                                            "Masculine"),
        "bier":         ("cerveja",       "sehr-VEH-zhah (betont auf 2. Silbe; 'j' = stimmhaftes 'sch')",             "Feminine"),
        "wein":         ("vinho",         "VEE-nyoo (betont auf 1. Silbe; 'nh' = 'nj')",                               "Masculine"),
        "suppe":        ("sopa",          "SOH-pah (betont auf 1. Silbe)",                                              "Feminine"),
        "gemuese":      ("legumes",       "leh-GOO-meesh (betont auf 2. Silbe; 's' am Ende = 'sch')",                 "Masculine plural"),
        "obst":         ("fruta",         "FROO-tah (betont auf 1. Silbe)",                                             "Feminine"),
        "ei":           ("ovo",           "OH-voo (betont auf 1. Silbe)",                                               "Masculine"),
        "kaese":        ("queijo",        "KAY-zhoo (betont auf 1. Silbe; 'ei' = 'ay'; 'j' = stimmhaftes 'sch')",     "Masculine"),
        "zucker":       ("a\u00e7\u00facar", "ah-SOO-kahr (betont auf 2. Silbe; '\u00e7' = 's')",                     "Masculine"),
        "salz":         ("sal",           "SAHL (eine Silbe)",                                                           "Masculine"),
        "butter":       ("manteiga",      "mahn-TAY-gah (betont auf 2. Silbe; 'ei' = 'ay')",                           "Feminine"),
        "oel":          ("\u00f3leo",      "OH-lyoo (betont auf 1. Silbe; Akzent auf '\u00f3')",                        "Masculine"),
        "kartoffel":    ("batata",        "bah-TAH-tah (betont auf 2. Silbe)",                                          "Feminine"),
        "huhn":         ("frango",        "FRAHN-goo (betont auf 1. Silbe; nasales 'an')",                              "Masculine"),
        "tomate":       ("tomate",        "toh-MAH-tee (betont auf 2. Silbe; 'e' am Ende = 'i')",                     "Masculine"),
        "apfel":        ("ma\u00e7\u00e3","mah-SAHNG (betont auf 2. Silbe; '\u00e7' = 's'; '\u00e3' = nasales 'a')", "Feminine"),
        "kuchen":       ("bolo",          "BOH-loo (betont auf 1. Silbe)",                                              "Masculine"),
        "kochen":       ("cozinhar",      "koh-zee-NYAHR (betont auf 3. Silbe; 'nh' = 'nj')",                         "Regular -ar verb"),
        "restaurant":   ("restaurante",   "rehsh-tah-oo-RAHN-tee (betont auf 4. Silbe; 's' vor 't' = 'sch')",        "Masculine"),
        "fruehstueck":  ("pequeno-almo\u00e7o", "peh-KEH-noo ahl-MOH-soo (PT); caf\u00e9 da manh\u00e3 in Brasilien", "Masculine"),
        "abendessen":   ("jantar",        "zhahn-TAHR (betont auf 2. Silbe; 'j' = stimmhaftes 'sch'; nasales 'an')",  "Masculine; also verb: to dine"),

        # --- natur_wetter ---
        "wald":         ("floresta",      "floh-REHSH-tah (betont auf 2. Silbe; 's' vor 't' = 'sch')",                "Feminine"),
        "himmel":       ("c\u00e9u",      "SEH-oo (eine Silbe; Diphthong 'eu'; 'c' vor 'e' = 's')",                  "Masculine"),
        "stern":        ("estrela",       "esh-TREH-lah (betont auf 2. Silbe; 'es' = 'esch')",                        "Feminine"),
        "erde":         ("terra",         "TEH-rah (betont auf 1. Silbe; 'rr' uvul\u00e4r)",                           "Feminine"),
        "wind":         ("vento",         "VEHN-too (betont auf 1. Silbe)",                                             "Masculine"),
        "wolke":        ("nuvem",         "NOO-vehng (betont auf 1. Silbe; 'em' = nasales 'eng')",                     "Feminine"),
        "donner":       ("trov\u00e3o",   "troh-VOWNG (betont auf 2. Silbe; '\u00e3o' = nasales 'au')",               "Masculine"),
        "insel":        ("ilha",          "EE-lyah (betont auf 1. Silbe; 'lh' = 'lj')",                                "Feminine"),
        "see_lake":     ("lago",          "LAH-goo (betont auf 1. Silbe)",                                              "Masculine"),
        "gras":         ("relva",         "REHL-vah (betont auf 1. Silbe; 'r' am Anfang uvul\u00e4r)",                "Feminine; Brazil: grama"),
        "stein":        ("pedra",         "PEH-drah (betont auf 1. Silbe)",                                             "Feminine"),
        "sand":         ("areia",         "ah-RAY-ah (betont auf 2. Silbe; 'ei' = 'ay')",                              "Feminine"),
        "eis":          ("gelo",          "ZHEH-loo (betont auf 1. Silbe; 'g' vor 'e' = stimmhaftes 'sch')",          "Masculine"),
        "nebel":        ("nevoeiro",      "neh-voo-AY-roo (betont auf 3. Silbe; 'ei' = 'ay')",                        "Masculine"),
        "strand":       ("praia",         "PRAH-yah (betont auf 1. Silbe; 'ai' = 'ay')",                               "Feminine"),
        "wueste":       ("deserto",       "deh-ZEHR-too (betont auf 2. Silbe; 's' stimmhaft)",                         "Masculine"),
        "fruehling":    ("primavera",     "pree-mah-VEH-rah (betont auf 3. Silbe)",                                    "Feminine"),
        "sommer":       ("ver\u00e3o",    "veh-ROWNG (betont auf 2. Silbe; '\u00e3o' = nasales 'au')",                "Masculine"),
        "herbst":       ("outono",        "oh-TOH-noo (betont auf 2. Silbe; 'ou' = 'oh')",                            "Masculine"),
        "winter":       ("inverno",       "een-VEHR-noo (betont auf 2. Silbe)",                                         "Masculine"),
        "luft":         ("ar",            "AHR (eine Silbe; 'r' am Ende uvul\u00e4r)",                                 "Masculine"),
        "feuer":        ("fogo",          "FOH-goo (betont auf 1. Silbe)",                                              "Masculine"),
        "sturm":        ("tempestade",    "tehm-pehsh-TAH-dee (betont auf 3. Silbe; 's' vor 't' = 'sch')",            "Feminine"),
        "regenbogen":   ("arco-\u00edris","AHR-koo EE-reesh (betont: 'AHR' und 'EE'; 's' am Ende = 'sch')",          "Masculine"),
        "feld":         ("campo",         "KAHM-poo (betont auf 1. Silbe)",                                             "Masculine"),

        # --- beruf_bildung ---
        "lehrer":       ("professor",     "proh-feh-SOHR (betont auf 3. Silbe; 'r' am Ende uvul\u00e4r)",             "Masculine; feminine: professora"),
        "schueler":     ("estudante",     "esh-too-DAHN-tee (betont auf 3. Silbe; 'es' = 'esch')",                    "Masculine/Feminine (same form)"),
        "buero":        ("escrit\u00f3rio", "esh-kree-TOH-ryoo (betont auf 3. Silbe; 'es' = 'esch')",                "Masculine"),
        "computer":     ("computador",    "kohm-poo-tah-DOHR (betont auf 4. Silbe; 'r' am Ende uvul\u00e4r)",        "Masculine"),
        "universitaet": ("universidade",  "oo-nee-vehr-see-DAH-dee (betont auf 5. Silbe; 'de' = 'dji' in Brasilien)","Feminine"),
        "pruefung":     ("exame",         "eh-ZAH-mee (betont auf 2. Silbe; 'x' = 'z')",                              "Masculine"),
        "beruf":        ("profiss\u00e3o","proh-fee-SOWNG (betont auf 3. Silbe; '\u00e3o' = nasales 'au')",           "Feminine"),
        "chef":         ("chefe",         "SHEH-fee (betont auf 1. Silbe; 'ch' = 'sch')",                              "Masculine/Feminine (same form)"),
        "gehalt":       ("sal\u00e1rio",  "sah-LAH-ryoo (betont auf 2. Silbe; Akzent auf '\u00e1')",                  "Masculine"),
        "ingenieur":    ("engenheiro",    "ehn-zheh-NYAY-roo (betont auf 3. Silbe; 'nh' = 'nj'; 'g' vor 'e' = 'zh')","Masculine; feminine: engenheira"),
        "rechtsanwalt": ("advogado",      "ahd-voh-GAH-doo (betont auf 3. Silbe; 'd' vor 'v' = weich)",              "Masculine; feminine: advogada"),
        "polizist":     ("pol\u00edcia",  "poh-LEE-syah (betont auf 2. Silbe; Akzent auf '\u00ed')",                  "Feminine (institution) or Masculine/Feminine (officer)"),
        "wissenschaft": ("ci\u00eancia",  "see-EHN-syah (betont auf 2. Silbe; '\u00ea' = geschlossenes 'e')",        "Feminine"),
        "mathematik":   ("matem\u00e1tica","mah-teh-MAH-tee-kah (betont auf 3. Silbe)",                               "Feminine"),
        "geschichte":   ("hist\u00f3ria", "eesh-TOH-ryah (betont auf 2. Silbe; 'h' stumm; 'is' = 'isch')",           "Feminine"),
        "sprache_lang": ("l\u00edngua",   "LEEN-gwah (betont auf 1. Silbe; Akzent auf '\u00ed'; 'gu' = 'gw')",       "Feminine; also means 'tongue'"),
        "bibliothek":   ("biblioteca",    "bee-blee-oh-TEH-kah (betont auf 4. Silbe)",                                 "Feminine"),
        "klasse":       ("classe",        "KLAH-see (betont auf 1. Silbe; Doppel-s stimmlos)",                         "Feminine"),
        "studieren":    ("estudar",       "esh-too-DAHR (betont auf 3. Silbe; 'es' = 'esch')",                        "Regular -ar verb"),
        "unterrichten": ("ensinar",       "ehn-see-NAHR (betont auf 3. Silbe)",                                        "Regular -ar verb"),
        "aufgabe":      ("tarefa",        "tah-REH-fah (betont auf 2. Silbe)",                                         "Feminine"),
        "erfahrung":    ("experi\u00eancia", "esh-peh-ree-EHN-syah (betont auf 4. Silbe; 'x' = 'sch')",              "Feminine"),
        "unternehmen":  ("empresa",       "ehm-PREH-zah (betont auf 2. Silbe; 's' stimmhaft)",                        "Feminine"),
        "projekt":      ("projeto",       "proh-ZHEH-too (betont auf 2. Silbe; 'j' = stimmhaftes 'sch')",            "Masculine"),
        "meeting":      ("reuni\u00e3o",  "heh-oo-nee-OWNG (betont auf 4. Silbe; 'r' am Anfang uvul\u00e4r; '\u00e3o' = nasales 'au')", "Feminine"),
    },

    # ==================================================================
    # FRENCH
    # ==================================================================
    "fr": {
        # --- koerper_gesundheit ---
        "hand":         ("main",           "MAHNG (eine Silbe; nasaler Vokal 'ain' = '\u00e4ng' durch die Nase)",     "Feminine"),
        "fuss":         ("pied",           "PYEH (eine Silbe; 'd' ist stumm)",                                         "Masculine"),
        "zahn":         ("dent",           "DAHNG (eine Silbe; nasaler Vokal; 't' stumm)",                              "Feminine"),
        "ohr":          ("oreille",        "oh-RAY (betont auf 2. Silbe; 'eille' = 'ay')",                              "Feminine"),
        "nase":         ("nez",            "NEH (eine Silbe; 'z' stumm)",                                               "Masculine; invariable in plural"),
        "mund":         ("bouche",         "BUSCH (eine Silbe; 'ou' = 'u'; 'ch' = 'sch')",                              "Feminine"),
        "finger":       ("doigt",          "DWAH (eine Silbe; 'oigt' = 'wa'; 'g' und 't' stumm)",                      "Masculine"),
        "ruecken":      ("dos",            "DOH (eine Silbe; 's' stumm)",                                               "Masculine"),
        "arm_body":     ("bras",           "BRAH (eine Silbe; 's' stumm)",                                              "Masculine"),
        "bein":         ("jambe",          "ZHAHMB (eine Silbe; 'j' = stimmhaftes 'sch'; nasales 'am')",               "Feminine"),
        "haut":         ("peau",           "POH (eine Silbe; 'eau' = 'oh')",                                            "Feminine"),
        "blut":         ("sang",           "SAHNG (eine Silbe; nasaler Vokal; 'g' stumm)",                              "Masculine"),
        "knochen":      ("os",             "OHS (eine Silbe); Plural: OH (stummes 's')",                                "Masculine"),
        "krankenhaus":  ("h\u00f4pital",   "oh-pee-TAHL (betont auf 3. Silbe; 'h' stumm; '\u00f4' = geschlossenes 'o')", "Masculine"),
        "medizin":      ("m\u00e9dicament","meh-dee-kah-MAHNG (betont auf 4. Silbe; nasaler Endvokal)",                "Masculine; means the medication/drug"),
        "krank":        ("malade",         "mah-LAHD (betont auf 2. Silbe; 'e' am Ende stumm)",                        "Masculine/Feminine (same form)"),
        "gesund":       ("en bonne sant\u00e9", "ahng BOHN sahn-TEH (3 W\u00f6rter; nasale Vokale)",                  "Adjectival phrase; santé = health"),
        "bauch":        ("ventre",         "VAHNTR (eine Silbe; nasales 'en'; 'e' am Ende stumm)",                     "Masculine"),
        "arzt":         ("m\u00e9decin",   "MEHD-sahng (betont auf 2. Silbe; nasaler Endvokal; Akzent auf '\u00e9')", "Masculine; feminine: m\u00e9decin (same) or m\u00e9decine (rare)"),
        "schmerz":      ("douleur",        "doo-LUHR (betont auf 2. Silbe; 'ou' = 'u')",                               "Feminine"),
        "fieber":       ("fi\u00e8vre",    "FYEHVR (eine Silbe; '\u00e8' = offenes 'e')",                              "Feminine"),
        "husten":       ("toux",           "TOO (eine Silbe; 'x' stumm)",                                              "Feminine; invariable"),
        "apotheke":     ("pharmacie",      "fahr-mah-SEE (betont auf 3. Silbe; 'ph' = 'f')",                           "Feminine"),
        "zunge":        ("langue",         "LAHNGG (eine Silbe; nasales 'an'; 'gu' = 'g'; 'e' stumm)",                 "Feminine; also means 'language'"),
        "schulter":     ("\u00e9paule",    "eh-POHL (betont auf 2. Silbe; '\u00e9' = geschlossenes 'e')",              "Feminine"),

        # --- essen_trinken ---
        "fleisch":      ("viande",         "VYAHND (eine Silbe; nasales 'an'; 'e' stumm)",                              "Feminine"),
        "fisch":        ("poisson",        "pwah-SOHNG (betont auf 2. Silbe; 'oi' = 'wa'; nasaler Endvokal)",          "Masculine"),
        "reis":         ("riz",            "REE (eine Silbe; 'z' stumm)",                                               "Masculine"),
        "kaffee":       ("caf\u00e9",      "kah-FEH (betont auf 2. Silbe; Akzent auf '\u00e9')",                        "Masculine"),
        "tee":          ("th\u00e9",       "TEH (eine Silbe; 'th' = 't'; '\u00e9' = geschlossenes 'e')",               "Masculine"),
        "bier":         ("bi\u00e8re",     "BYEHR (eine Silbe; '\u00e8' = offenes 'e')",                                "Feminine"),
        "wein":         ("vin",            "VAHNG (eine Silbe; nasaler Vokal 'in' = '\u00e4ng' durch die Nase)",        "Masculine"),
        "suppe":        ("soupe",          "SOUP (eine Silbe; 'ou' = 'u'; 'e' stumm)",                                  "Feminine"),
        "gemuese":      ("l\u00e9gumes",   "leh-G\u00dcM (betont auf 2. Silbe; 'u' = deutsches '\u00fc'; 'es' stumm)","Masculine plural"),
        "obst":         ("fruit",          "FR\u00dc-EE (eine Silbe; 'u' = '\u00fc'; 'i' gesprochen; 't' stumm)",     "Masculine"),
        "ei":           ("\u0153uf",       "\u00d6F (eine Silbe; '\u0153' = '\u00f6')",                                 "Masculine; plural: \u0153ufs (gesprochen: '\u00f6'!)"),
        "kaese":        ("fromage",        "froh-MAHZH (betont auf 2. Silbe; 'g' vor 'e' = stimmhaftes 'sch')",        "Masculine"),
        "zucker":       ("sucre",          "S\u00dcKR (eine Silbe; 'u' = '\u00fc'; 'e' stumm)",                        "Masculine"),
        "salz":         ("sel",            "SEHL (eine Silbe)",                                                          "Masculine"),
        "butter":       ("beurre",         "BUHR (eine Silbe; 'eu' = '\u00f6'; Doppel-r)",                              "Masculine"),
        "oel":          ("huile",          "\u00dc-IHL (zwei Silben; 'h' stumm; 'u' = '\u00fc')",                       "Feminine"),
        "kartoffel":    ("pomme de terre", "POHM duh TEHR (3 W\u00f6rter; w\u00f6rtlich: Apfel der Erde)",             "Feminine"),
        "huhn":         ("poulet",         "poo-LEH (betont auf 2. Silbe; 't' stumm)",                                  "Masculine"),
        "tomate":       ("tomate",         "toh-MAHT (betont auf 2. Silbe; 'e' stumm)",                                 "Feminine"),
        "apfel":        ("pomme",          "POHM (eine Silbe; Doppel-m; 'e' stumm)",                                    "Feminine"),
        "kuchen":       ("g\u00e2teau",    "gah-TOH (betont auf 2. Silbe; '\u00e2' = langes 'a'; 'eau' = 'oh')",      "Masculine"),
        "kochen":       ("cuisiner",       "k\u00fc-ee-zee-NEH (betont auf 4. Silbe; 'u' = '\u00fc'; 'er' = 'eh')",   "Regular -er verb"),
        "restaurant":   ("restaurant",     "rehs-toh-RAHNG (betont auf 3. Silbe; nasaler Endvokal; 't' stumm)",        "Masculine"),
        "fruehstueck":  ("petit-d\u00e9jeuner", "puh-tee deh-zhuh-NEH (betont auf letzte Silbe; 'eu' = '\u00f6')",   "Masculine"),
        "abendessen":   ("d\u00eener",     "dee-NEH (betont auf 2. Silbe; '\u00ee' = langes 'i'; 'er' = 'eh')",       "Masculine; also verb: to dine"),

        # --- natur_wetter ---
        "wald":         ("for\u00eat",     "foh-REH (betont auf 2. Silbe; '\u00ea' = offenes 'e'; 't' stumm)",        "Feminine"),
        "himmel":       ("ciel",           "SYEHL (eine Silbe; 'c' vor 'i' = 's')",                                    "Masculine"),
        "stern":        ("\u00e9toile",    "eh-TWAHL (betont auf 2. Silbe; '\u00e9' = geschlossenes 'e'; 'oi' = 'wa')","Feminine"),
        "erde":         ("terre",          "TEHR (eine Silbe; Doppel-r; 'e' stumm)",                                    "Feminine"),
        "wind":         ("vent",           "VAHNG (eine Silbe; nasaler Vokal; 't' stumm)",                              "Masculine"),
        "wolke":        ("nuage",          "n\u00fc-AHZH (betont auf 2. Silbe; 'u' = '\u00fc'; 'g' vor 'e' = stimmhaftes 'sch')", "Masculine"),
        "donner":       ("tonnerre",       "toh-NEHR (betont auf 2. Silbe; Doppel-n; 'e' am Ende stumm)",              "Masculine"),
        "insel":        ("\u00eele",       "EEL (eine Silbe; '\u00ee' = langes 'i'; 'e' stumm)",                       "Feminine"),
        "see_lake":     ("lac",            "LAHK (eine Silbe; 'c' gesprochen)",                                         "Masculine"),
        "gras":         ("herbe",          "EHRB (eine Silbe; 'h' stumm; 'e' stumm)",                                  "Feminine"),
        "stein":        ("pierre",         "PYEHR (eine Silbe; 'rr'; 'e' stumm)",                                       "Feminine"),
        "sand":         ("sable",          "SAHBL (eine Silbe; 'e' stumm)",                                              "Masculine"),
        "eis":          ("glace",          "GLAHS (eine Silbe; 'c' vor 'e' = 's'; 'e' stumm)",                         "Feminine; also means 'ice cream'"),
        "nebel":        ("brouillard",     "broo-YAHR (betont auf 2. Silbe; 'ou' = 'u'; 'ill' = 'ij'; 'd' stumm)",    "Masculine"),
        "strand":       ("plage",          "PLAHZH (eine Silbe; 'g' vor 'e' = stimmhaftes 'sch'; 'e' stumm)",         "Feminine"),
        "wueste":       ("d\u00e9sert",    "deh-ZEHR (betont auf 2. Silbe; '\u00e9' = geschlossenes 'e'; 't' stumm)", "Masculine"),
        "fruehling":    ("printemps",      "prahng-TAHNG (betont auf 2. Silbe; beide Silben nasal; 's' stumm)",        "Masculine"),
        "sommer":       ("\u00e9t\u00e9",  "eh-TEH (betont auf 2. Silbe; beide '\u00e9' geschlossen)",                "Masculine"),
        "herbst":       ("automne",        "oh-TOHN (betont auf 2. Silbe; 'au' = 'oh'; 'mn' = 'n'; 'e' stumm)",       "Masculine"),
        "winter":       ("hiver",          "ee-VEHR (betont auf 2. Silbe; 'h' stumm; 'er' = '\u00e4r')",              "Masculine"),
        "luft":         ("air",            "EHR (eine Silbe; 'ai' = offenes 'e')",                                      "Masculine"),
        "feuer":        ("feu",            "F\u00d6 (eine Silbe; 'eu' = '\u00f6')",                                    "Masculine"),
        "sturm":        ("temp\u00eate",   "tahm-PEHT (betont auf 2. Silbe; nasales 'em'; '\u00ea' = offenes 'e')",   "Feminine"),
        "regenbogen":   ("arc-en-ciel",    "AHR-kahng-SYEHL (3 Silben; nasales 'en'; 'c' vor 'i' = 's')",            "Masculine"),
        "feld":         ("champ",          "SHAHNG (eine Silbe; 'ch' = 'sch'; nasaler Vokal; 'p' stumm)",              "Masculine"),

        # --- beruf_bildung ---
        "lehrer":       ("professeur",     "proh-feh-SUHR (betont auf 3. Silbe; 'eu' = '\u00f6'; 'r' gesprochen)",    "Masculine; feminine: professeure/professeuse"),
        "schueler":     ("\u00e9tudiant",  "eh-t\u00fc-DYAHNG (betont auf 3. Silbe; nasaler Endvokal; 't' stumm)",    "Masculine; feminine: \u00e9tudiante"),
        "buero":        ("bureau",         "b\u00fc-ROH (betont auf 2. Silbe; 'u' = '\u00fc'; 'eau' = 'oh')",         "Masculine"),
        "computer":     ("ordinateur",     "ohr-dee-nah-TUHR (betont auf 4. Silbe; 'eu' = '\u00f6'; 'r' gesprochen)","Masculine"),
        "universitaet": ("universit\u00e9","\u00fc-nee-vehr-see-TEH (betont auf 5. Silbe; Akzent auf '\u00e9')",     "Feminine"),
        "pruefung":     ("examen",         "ehg-zah-MAHNG (betont auf 3. Silbe; 'x' = 'gz'; nasaler Endvokal)",       "Masculine"),
        "beruf":        ("profession",     "proh-feh-SYOHNG (betont auf 3. Silbe; nasaler Endvokal)",                   "Feminine"),
        "chef":         ("patron",         "pah-TROHNG (betont auf 2. Silbe; nasaler Endvokal)",                        "Masculine; feminine: patronne"),
        "gehalt":       ("salaire",        "sah-LEHR (betont auf 2. Silbe; 'ai' = offenes 'e'; 'e' stumm)",           "Masculine"),
        "ingenieur":    ("ing\u00e9nieur", "ahng-zheh-NYUHR (betont auf 3. Silbe; nasales 'in'; 'g' = stimmhaftes 'sch')", "Masculine; feminine: ing\u00e9nieure"),
        "rechtsanwalt": ("avocat",         "ah-voh-KAH (betont auf 3. Silbe; 't' stumm)",                              "Masculine; feminine: avocate"),
        "polizist":     ("policier",       "poh-lee-SYEH (betont auf 3. Silbe; 'er' = 'eh')",                          "Masculine; feminine: polici\u00e8re"),
        "wissenschaft": ("science",        "SYAHNGS (eine Silbe; 'sc' = 's'; 'ien' = nasales 'i\u00e4ng'; 'ce' = 's')", "Feminine"),
        "mathematik":   ("math\u00e9matiques", "mah-teh-mah-TEEK (betont auf 4. Silbe; 'qu' = 'k'; 'es' stumm)",     "Feminine plural"),
        "geschichte":   ("histoire",       "ees-TWAHR (betont auf 2. Silbe; 'h' stumm; 'oi' = 'wa')",                 "Feminine"),
        "sprache_lang": ("langue",         "LAHNGG (eine Silbe; nasales 'an'; 'gu' = 'g'; 'e' stumm)",                 "Feminine; also means 'tongue'"),
        "bibliothek":   ("biblioth\u00e8que", "bee-blee-oh-TEHK (betont auf 4. Silbe; '\u00e8' = offenes 'e'; 'que' = 'k')", "Feminine"),
        "klasse":       ("classe",         "KLAHS (eine Silbe; 'e' stumm)",                                            "Feminine"),
        "studieren":    ("\u00e9tudier",   "eh-t\u00fc-DYEH (betont auf 3. Silbe; '\u00e9' = geschlossenes 'e'; 'er' = 'eh')", "Regular -er verb"),
        "unterrichten": ("enseigner",      "ahng-seh-NYEH (betont auf 3. Silbe; nasales 'en'; 'gn' = 'nj'; 'er' = 'eh')", "Regular -er verb"),
        "aufgabe":      ("t\u00e2che",     "TAHSCH (eine Silbe; '\u00e2' = langes 'a'; 'ch' = 'sch'; 'e' stumm)",    "Feminine"),
        "erfahrung":    ("exp\u00e9rience","ehks-peh-RYAHNGS (betont auf 3. Silbe; nasales 'en'; 'ce' = 's')",       "Feminine"),
        "unternehmen":  ("entreprise",     "ahng-truh-PREEZ (betont auf 3. Silbe; nasales 'en'; 'e' stumm)",           "Feminine"),
        "projekt":      ("projet",         "proh-ZHEH (betont auf 2. Silbe; 'j' = stimmhaftes 'sch'; 't' stumm)",    "Masculine"),
        "meeting":      ("r\u00e9union",   "reh-\u00fc-NYOHNG (betont auf 3. Silbe; '\u00e9' geschlossen; nasaler Endvokal)", "Feminine"),
    },

    # ==================================================================
    # ROMANIAN
    # ==================================================================
    "ro": {
        # --- koerper_gesundheit ---
        "hand":         ("m\u00e2n\u0103",  "MUH-nuh ('\u00e2' = dumpfes '\u00e4' hinten im Mund; '\u0103' = kurzes '\u00e4')", "Feminine; plural: m\u00e2ini"),
        "fuss":         ("picior",           "pee-TSCHOR (betont auf 2. Silbe; 'c' vor 'i' = 'tsch')",                  "Neuter; also means 'leg' (context-dependent)"),
        "zahn":         ("dinte",            "DEEN-teh (betont auf 1. Silbe)",                                           "Masculine; plural: din\u021bi"),
        "ohr":          ("ureche",           "oo-REH-keh (betont auf 2. Silbe)",                                         "Feminine; plural: urechi"),
        "nase":         ("nas",              "NAHS (eine Silbe)",                                                         "Neuter"),
        "mund":         ("gur\u0103",        "GOO-ruh (betont auf 1. Silbe; '\u0103' = kurzes '\u00e4')",                "Feminine"),
        "finger":       ("deget",            "DEH-jet (betont auf 1. Silbe; 'g' vor 'e' = 'dsch')",                     "Neuter; plural: degete"),
        "ruecken":      ("spate",            "SPAH-teh (betont auf 1. Silbe)",                                           "Neuter"),
        "arm_body":     ("bra\u021b",        "BRAHTS ('\u021b' = 'ts' wie in deutsch 'Zahn')",                           "Neuter"),
        "bein":         ("picior",           "pee-TSCHOR (betont auf 2. Silbe; 'c' vor 'i' = 'tsch')",                  "Neuter; same word as 'foot' in Romanian"),
        "haut":         ("piele",            "PYEH-leh (betont auf 1. Silbe; 'ie' = Diphthong)",                        "Feminine"),
        "blut":         ("s\u00e2nge",       "SUHN-dscheh ('\u00e2' = dumpfer Vokal; 'g' vor 'e' = 'dsch')",           "Neuter"),
        "knochen":      ("os",               "OHS (eine Silbe)",                                                          "Neuter; plural: oase"),
        "krankenhaus":  ("spital",           "spee-TAHL (betont auf 2. Silbe)",                                          "Neuter"),
        "medizin":      ("medicament",       "meh-dee-kah-MEHNT (betont auf 4. Silbe)",                                  "Neuter; means medication/drug"),
        "krank":        ("bolnav",           "bohl-NAHV (betont auf 2. Silbe)",                                          "Feminine: bolnav\u0103"),
        "gesund":       ("s\u0103n\u0103tos","suh-nuh-TOHS (betont auf 3. Silbe; '\u0103' = kurzes '\u00e4')",         "Feminine: s\u0103n\u0103toas\u0103"),
        "bauch":        ("stomac",           "stoh-MAHK (betont auf 2. Silbe)",                                          "Neuter"),
        "arzt":         ("medic",            "MEH-deek (betont auf 1. Silbe)",                                           "Masculine; feminine: medic\u0103 (rare, usually same form)"),
        "schmerz":      ("durere",           "doo-REH-reh (betont auf 2. Silbe)",                                        "Feminine"),
        "fieber":       ("febr\u0103",       "FEH-bruh (betont auf 1. Silbe; '\u0103' = kurzes '\u00e4')",              "Feminine"),
        "husten":       ("tuse",             "TOO-seh (betont auf 1. Silbe)",                                            "Feminine"),
        "apotheke":     ("farmacie",         "fahr-mah-TSCHEE-eh (betont auf 3. Silbe; 'c' vor 'i' = 'tsch')",         "Feminine"),
        "zunge":        ("limb\u0103",       "LEEM-buh (betont auf 1. Silbe; '\u0103' = kurzes '\u00e4')",              "Feminine; also means 'language'"),
        "schulter":     ("um\u0103r",        "OO-muhr (betont auf 1. Silbe; '\u0103' = kurzes '\u00e4')",               "Neuter; plural: umeri"),

        # --- essen_trinken ---
        "fleisch":      ("carne",            "KAHR-neh (betont auf 1. Silbe)",                                           "Feminine"),
        "fisch":        ("pe\u0219te",       "PEHSCH-teh (betont auf 1. Silbe; '\u0219' = 'sch')",                      "Masculine"),
        "reis":         ("orez",             "oh-REHZ (betont auf 2. Silbe)",                                            "Neuter"),
        "kaffee":       ("cafea",            "kah-FYAH (betont auf 2. Silbe; 'ea' = Diphthong)",                         "Feminine"),
        "tee":          ("ceai",             "tschah-EE (betont auf 2. Silbe; 'c' vor 'e' = 'tsch')",                   "Neuter"),
        "bier":         ("bere",             "BEH-reh (betont auf 1. Silbe)",                                            "Feminine"),
        "wein":         ("vin",              "VEEN (eine Silbe)",                                                         "Neuter"),
        "suppe":        ("sup\u0103",        "SOO-puh (betont auf 1. Silbe; '\u0103' = kurzes '\u00e4')",               "Feminine"),
        "gemuese":      ("legume",           "leh-GOO-meh (betont auf 2. Silbe)",                                        "Neuter plural; singular: legum\u0103"),
        "obst":         ("fructe",           "FROOK-teh (betont auf 1. Silbe)",                                          "Neuter plural; singular: fruct"),
        "ei":           ("ou",               "OH-oo (Diphthong; eine Silbe)",                                            "Neuter; plural: ou\u0103"),
        "kaese":        ("br\u00e2nz\u0103","BRUHN-zuh ('\u00e2' = dumpfer Vokal; '\u0103' = kurzes '\u00e4')",        "Feminine"),
        "zucker":       ("zah\u0103r",       "zah-HUHR (betont auf 2. Silbe; 'h' gehaucht)",                            "Neuter"),
        "salz":         ("sare",             "SAH-reh (betont auf 1. Silbe)",                                            "Feminine"),
        "butter":       ("unt",              "OONT (eine Silbe; 'u' = 'u')",                                             "Neuter"),
        "oel":          ("ulei",             "oo-LAY (betont auf 2. Silbe; 'ei' = 'ay')",                               "Neuter"),
        "kartoffel":    ("cartof",           "kahr-TOHF (betont auf 2. Silbe)",                                          "Masculine; plural: cartofi"),
        "huhn":         ("pui",              "POOY (eine Silbe; Diphthong 'ui')",                                        "Masculine"),
        "tomate":       ("ro\u0219ie",       "ROH-shee-eh (betont auf 1. Silbe; '\u0219' = 'sch')",                     "Feminine"),
        "apfel":        ("m\u0103r",         "MUHR (eine Silbe; '\u0103' = kurzes '\u00e4')",                           "Neuter; plural: mere"),
        "kuchen":       ("tort",             "TOHRT (eine Silbe)",                                                        "Neuter"),
        "kochen":       ("a g\u0103ti",      "ah GUH-tee (betont auf 2. Silbe; '\u0103' = kurzes '\u00e4')",           "Conjugation: eu g\u0103tesc"),
        "restaurant":   ("restaurant",       "rehs-tah-oo-RAHNT (betont auf 4. Silbe; 't' am Ende gesprochen)",         "Neuter"),
        "fruehstueck":  ("mic dejun",        "MEEK deh-ZHOON (betont: 'MEEK' und 'ZHOON'; 'j' = stimmhaftes 'sch')",  "Neuter"),
        "abendessen":   ("cin\u0103",        "TSCHEE-nuh (betont auf 1. Silbe; 'c' vor 'i' = 'tsch'; '\u0103' = '\u00e4')", "Feminine"),

        # --- natur_wetter ---
        "wald":         ("p\u0103dure",      "puh-DOO-reh (betont auf 2. Silbe; '\u0103' = kurzes '\u00e4')",          "Feminine"),
        "himmel":       ("cer",              "TSCHER (eine Silbe; 'c' vor 'e' = 'tsch')",                               "Neuter"),
        "stern":        ("stea",             "STYAH (eine Silbe; 'ea' = Diphthong)",                                     "Feminine; plural: stele"),
        "erde":         ("p\u0103m\u00e2nt", "puh-MUHNT (betont auf 2. Silbe; '\u0103' = '\u00e4'; '\u00e2' = dumpfer Vokal)", "Neuter"),
        "wind":         ("v\u00e2nt",        "VUHNT (eine Silbe; '\u00e2' = dumpfer Vokal hinten)",                     "Neuter"),
        "wolke":        ("nor",              "NOHR (eine Silbe)",                                                         "Masculine; plural: nori"),
        "donner":       ("tunet",            "TOO-neht (betont auf 1. Silbe)",                                           "Neuter"),
        "insel":        ("insul\u0103",      "een-SOO-luh (betont auf 2. Silbe; '\u0103' = kurzes '\u00e4')",          "Feminine"),
        "see_lake":     ("lac",              "LAHK (eine Silbe)",                                                         "Neuter; plural: lacuri"),
        "gras":         ("iarb\u0103",       "YAHR-buh (betont auf 1. Silbe; '\u0103' = kurzes '\u00e4')",             "Feminine"),
        "stein":        ("piatr\u0103",      "PYAH-truh (betont auf 1. Silbe; '\u0103' = kurzes '\u00e4')",            "Feminine"),
        "sand":         ("nisip",            "nee-SEEP (betont auf 2. Silbe)",                                           "Neuter"),
        "eis":          ("ghea\u021b\u0103", "GYAH-tsuh (betont auf 1. Silbe; 'gh' = hartes 'g'; '\u021b' = 'ts'; '\u0103' = '\u00e4')", "Feminine"),
        "nebel":        ("cea\u021b\u0103",  "TSCHAH-tsuh (betont auf 1. Silbe; 'c' vor 'e' = 'tsch'; '\u021b' = 'ts')", "Feminine"),
        "strand":       ("plaj\u0103",       "PLAH-zhuh (betont auf 1. Silbe; 'j' = stimmhaftes 'sch'; '\u0103' = '\u00e4')", "Feminine"),
        "wueste":       ("de\u0219ert",      "deh-SHEHRT (betont auf 2. Silbe; '\u0219' = 'sch')",                     "Neuter"),
        "fruehling":    ("prim\u0103var\u0103", "pree-muh-VAH-ruh (betont auf 3. Silbe; '\u0103' = kurzes '\u00e4')", "Feminine"),
        "sommer":       ("var\u0103",        "VAH-ruh (betont auf 1. Silbe; '\u0103' = kurzes '\u00e4')",              "Feminine"),
        "herbst":       ("toamn\u0103",      "TWAHM-nuh (betont auf 1. Silbe; 'oa' = Diphthong; '\u0103' = '\u00e4')", "Feminine"),
        "winter":       ("iarn\u0103",       "YAHR-nuh (betont auf 1. Silbe; 'ia' = 'ya'; '\u0103' = '\u00e4')",      "Feminine"),
        "luft":         ("aer",              "AH-ehr (zwei Silben)",                                                      "Neuter"),
        "feuer":        ("foc",              "FOHK (eine Silbe)",                                                         "Neuter; plural: focuri"),
        "sturm":        ("furtun\u0103",     "foor-TOO-nuh (betont auf 2. Silbe; '\u0103' = kurzes '\u00e4')",         "Feminine"),
        "regenbogen":   ("curcubeu",         "koor-koo-BEH-oo (betont auf 3. Silbe; Diphthong 'eu')",                  "Neuter"),
        "feld":         ("c\u00e2mp",        "KUHMP (eine Silbe; '\u00e2' = dumpfer Vokal hinten)",                    "Neuter; plural: c\u00e2mpuri"),

        # --- beruf_bildung ---
        "lehrer":       ("profesor",         "proh-feh-SOHR (betont auf 3. Silbe)",                                     "Masculine; feminine: profesoar\u0103"),
        "schueler":     ("student",          "stoo-DEHNT (betont auf 2. Silbe)",                                         "Masculine; feminine: student\u0103"),
        "buero":        ("birou",            "bee-ROH-oo (betont auf 2. Silbe; Diphthong 'ou')",                        "Neuter"),
        "computer":     ("calculator",       "kahl-koo-lah-TOHR (betont auf 4. Silbe)",                                 "Neuter"),
        "universitaet": ("universitate",     "oo-nee-vehr-see-TAH-teh (betont auf 5. Silbe)",                           "Feminine"),
        "pruefung":     ("examen",           "ehk-ZAH-mehn (betont auf 2. Silbe; 'x' = 'ks'/'gz')",                   "Neuter; plural: examene"),
        "beruf":        ("profesie",         "proh-feh-SEE-eh (betont auf 3. Silbe)",                                   "Feminine"),
        "chef":         ("\u0219ef",         "SHEHF (eine Silbe; '\u0219' = 'sch')",                                   "Masculine; feminine: \u0219ef\u0103"),
        "gehalt":       ("salariu",          "sah-LAH-ree-oo (betont auf 2. Silbe; 'iu' = Diphthong)",                 "Neuter"),
        "ingenieur":    ("inginer",          "een-zhee-NEHR (betont auf 3. Silbe; 'g' vor 'i' = 'dsch')",              "Masculine; feminine: inginer\u0103 (rare)"),
        "rechtsanwalt": ("avocat",           "ah-voh-KAHT (betont auf 3. Silbe)",                                       "Masculine; feminine: avocat\u0103"),
        "polizist":     ("poli\u021bist",    "poh-lee-TSEEST (betont auf 3. Silbe; '\u021b' = 'ts')",                  "Masculine; feminine: poli\u021bist\u0103"),
        "wissenschaft": ("\u0219tiin\u021b\u0103", "SHTEE-een-tsuh (betont auf 1. Silbe; '\u0219' = 'sch'; '\u021b' = 'ts'; '\u0103' = '\u00e4')", "Feminine"),
        "mathematik":   ("matematic\u0103",  "mah-teh-mah-TEE-kuh (betont auf 4. Silbe; '\u0103' = '\u00e4')",        "Feminine"),
        "geschichte":   ("istorie",          "ees-TOH-ree-eh (betont auf 2. Silbe)",                                    "Feminine"),
        "sprache_lang": ("limb\u0103",       "LEEM-buh (betont auf 1. Silbe; '\u0103' = kurzes '\u00e4')",             "Feminine; also means 'tongue'"),
        "bibliothek":   ("bibliotec\u0103",  "bee-blee-oh-TEH-kuh (betont auf 4. Silbe; '\u0103' = '\u00e4')",        "Feminine"),
        "klasse":       ("clas\u0103",       "KLAH-suh (betont auf 1. Silbe; '\u0103' = kurzes '\u00e4')",             "Feminine"),
        "studieren":    ("a studia",         "ah stoo-dee-AH (betont auf 3. Silbe des Verbs)",                          "Conjugation: eu studiez"),
        "unterrichten": ("a preda",          "ah PREH-dah (betont auf 1. Silbe des Verbs)",                             "Conjugation: eu predau"),
        "aufgabe":      ("sarcin\u0103",     "sahr-TSCHEE-nuh (betont auf 2. Silbe; 'c' vor 'i' = 'tsch'; '\u0103' = '\u00e4')", "Feminine"),
        "erfahrung":    ("experien\u021b\u0103", "ehks-peh-ree-EHN-tsuh (betont auf 4. Silbe; '\u021b' = 'ts')",     "Feminine"),
        "unternehmen":  ("companie",         "kohm-pah-NEE-eh (betont auf 3. Silbe)",                                   "Feminine"),
        "projekt":      ("proiect",          "proh-YEHKT (betont auf 2. Silbe; 'oi' = Diphthong; 'ct' gesprochen)",   "Neuter"),
        "meeting":      ("\u0219edin\u021b\u0103", "sheh-DEEN-tsuh (betont auf 2. Silbe; '\u0219' = 'sch'; '\u021b' = 'ts'; '\u0103' = '\u00e4')", "Feminine"),
    },
}


# ---------------------------------------------------------------------------
# Entry builder
# ---------------------------------------------------------------------------
def make_entry(
    word: str,
    pronunciation_hint: str,
    meaning_de: str,
    meaning_en: str,
    category: str,
    frequency_rank: int,
    concept_id: str,
    notes: str,
) -> dict:
    """Build a single vocabulary entry dict."""
    return {
        "word": word,
        "romanization": "",
        "pronunciation_hint": pronunciation_hint,
        "meaning_de": meaning_de,
        "meaning_en": meaning_en,
        "category": category,
        "frequency_rank": frequency_rank,
        "concept_id": concept_id,
        "tone": None,
        "notes": notes,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    for lang_code, filename in LANGUAGE_FILES.items():
        filepath = os.path.join(DATA_DIR, filename)

        if not os.path.isfile(filepath):
            print(f"[SKIP] File not found: {filepath}")
            continue

        # Load existing data
        with open(filepath, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        words = data["words"]

        # Build set of existing concept_ids for duplicate detection
        existing_ids = {w["concept_id"] for w in words}

        # Find current max frequency_rank
        max_rank = max(w["frequency_rank"] for w in words)
        next_rank = max_rank + 1

        lang_translations = TRANSLATIONS[lang_code]
        added = 0
        skipped = 0

        for category_name, concepts in CATEGORIES.items():
            for concept in concepts:
                cid = concept["concept_id"]

                if cid in existing_ids:
                    skipped += 1
                    continue

                if cid not in lang_translations:
                    print(
                        f"  [WARN] {lang_code}: No translation for concept_id '{cid}'"
                    )
                    continue

                word_text, pron_hint, notes = lang_translations[cid]
                entry = make_entry(
                    word=word_text,
                    pronunciation_hint=pron_hint,
                    meaning_de=concept["meaning_de"],
                    meaning_en=concept["meaning_en"],
                    category=category_name,
                    frequency_rank=next_rank,
                    concept_id=cid,
                    notes=notes,
                )
                words.append(entry)
                existing_ids.add(cid)
                next_rank += 1
                added += 1

        # Detect original formatting style (pretty vs compact)
        # Italian, French, Romanian use pretty-printed (multi-line per entry)
        # Spanish, Portuguese use compact (single-line per entry)
        pretty_languages = {"it", "fr", "ro"}

        if lang_code in pretty_languages:
            output = json.dumps(data, ensure_ascii=False, indent=2)
        else:
            # Compact style: object on one line, but array elements on separate lines
            # Build output manually to match existing format
            lines = ['{\n  "language_id": "' + data["language_id"] + '",\n  "words": [']
            for i, w in enumerate(words):
                entry_json = json.dumps(w, ensure_ascii=False)
                if i < len(words) - 1:
                    lines.append("    " + entry_json + ",")
                else:
                    lines.append("    " + entry_json)
            lines.append("  ]")
            lines.append("}")
            output = "\n".join(lines) + "\n"

        with open(filepath, "w", encoding="utf-8") as fh:
            if lang_code in pretty_languages:
                fh.write(output + "\n")
            else:
                fh.write(output)

        print(
            f"[OK] {lang_code} ({filename}): added {added} words, "
            f"skipped {skipped} duplicates, "
            f"new max_rank={next_rank - 1}"
        )


if __name__ == "__main__":
    main()
