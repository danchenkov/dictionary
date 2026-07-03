import re

def clean_definition(text: str) -> str:
    """
    Removes leading numbering like:
    '1. ', '2) ', '3 - ', etc.
    """

    if not text:
        return text

    return re.sub(r'^\s*\d+\s*[\.\)\-–]\s*', '', text).strip()


def normalize_definition(text):
    text = clean_definition(text)

    # unify spacing around semicolons
    text = re.sub(r'\s*;\s*', '; ', text)

    # remove trailing periods (optional style decision)
    text = text.strip()

    return text


def normalize_mw_definition(word: str, text: str) -> str:
    if not text:
        return text

    t = text.strip()

    # -----------------------------
    # 1. Remove cross-reference tails
    # -----------------------------
    t = re.sub(r'—.*?(see|usu\.|usually|cf\.).*$', '', t, flags=re.IGNORECASE)
    t = re.sub(r'\b(see also|see)\b.*$', '', t, flags=re.IGNORECASE)

    # -----------------------------
    # 2. Remove " + to" style notes
    # -----------------------------
    t = re.sub(r'—\s*usually\s*\+\s*to.*$', '', t, flags=re.IGNORECASE)

    # -----------------------------
    # 3. Normalize separators
    # -----------------------------
    t = re.sub(r'\s*;\s*also\s*:?$', '', t, flags=re.IGNORECASE)
    t = re.sub(r'\s*;\s*or\s*$', '', t, flags=re.IGNORECASE)

    # -----------------------------
    # 4. Remove self-references
    # -----------------------------
    # crude but effective: word replacement (case-insensitive)
    pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
    t = pattern.sub("[THING]", t)

    # -----------------------------
    # 5. Clean up artifacts
    # -----------------------------
    t = re.sub(r'\s+', ' ', t).strip()

    return t

