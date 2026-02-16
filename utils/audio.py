"""Optional pronunciation hints — text-based, no audio dependencies."""


def get_pronunciation_hint(word: str, language_id: str,
                           romanization: str = "") -> str:
    """Return German-phonetic approximation for pronunciation."""
    # This provides basic hints; actual pronunciation data comes from
    # the vocabulary JSON files
    if romanization:
        return romanization
    return word
