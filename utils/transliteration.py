"""Transliteration helpers for Cyrillic, Hanzi, Hangul."""

# Cyrillic to Latin transliteration (scientific/ISO 9)
CYRILLIC_TO_LATIN = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d",
    "е": "e", "ё": "yo", "ж": "zh", "з": "z", "и": "i",
    "й": "y", "к": "k", "л": "l", "м": "m", "н": "n",
    "о": "o", "п": "p", "р": "r", "с": "s", "т": "t",
    "у": "u", "ф": "f", "х": "kh", "ц": "ts", "ч": "ch",
    "ш": "sh", "щ": "shch", "ъ": "", "ы": "y", "ь": "'",
    "э": "e", "ю": "yu", "я": "ya",
    # Ukrainian extras
    "і": "i", "ї": "yi", "є": "ye", "ґ": "g",
    # Belarusian extras
    "ў": "w",
    # Macedonian extras
    "ќ": "kj", "ѓ": "gj", "љ": "lj", "њ": "nj", "џ": "dz",
    "ј": "j", "ѕ": "dz",
    # Bulgarian
    "щ": "sht",
}


def transliterate_cyrillic(text: str) -> str:
    """Transliterate Cyrillic text to Latin."""
    result = []
    for char in text:
        lower = char.lower()
        if lower in CYRILLIC_TO_LATIN:
            trans = CYRILLIC_TO_LATIN[lower]
            if char.isupper() and trans:
                trans = trans[0].upper() + trans[1:]
            result.append(trans)
        else:
            result.append(char)
    return "".join(result)


def is_cyrillic(text: str) -> bool:
    """Check if text contains Cyrillic characters."""
    return any("\u0400" <= c <= "\u04ff" for c in text)


def is_cjk(text: str) -> bool:
    """Check if text contains CJK characters."""
    return any("\u4e00" <= c <= "\u9fff" for c in text)


def is_hangul(text: str) -> bool:
    """Check if text contains Hangul characters."""
    return any("\uac00" <= c <= "\ud7af" or "\u1100" <= c <= "\u11ff" for c in text)


def format_word_display(word: str, romanization: str = "",
                        pronunciation_hint: str = "") -> str:
    """Format a word for terminal display with romanization."""
    parts = [word]
    if romanization:
        parts.append(f"({romanization})")
    if pronunciation_hint:
        parts.append(f"[{pronunciation_hint}]")
    return " ".join(parts)
