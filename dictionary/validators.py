import re

INVALID_PATTERNS = {
    "[THING]",
    "thing",
    "",
}


def is_valid_definition(
    word: str,
    definition: str,
) -> bool:
    if not definition:
        return False

    t = definition.strip().lower()

    # -----------------------------
    # 1. reject exact word echo
    # -----------------------------
    if t == word:
        return False

    # -----------------------------
    # 2. reject trivial prefix echo
    # -----------------------------
    if t.startswith(word + " "):
        return False

    # -----------------------------
    # 3. obvious invalid tokens
    # -----------------------------
    if t in INVALID_PATTERNS:
        return False

    # -----------------------------
    # 4. too short (heuristic)
    # -----------------------------
    if len(t.split()) < 3:
        return False

    # -----------------------------
    # 5. only punctuation / noise
    # -----------------------------
    if re.fullmatch(r"[\W_]+", t):
        return False

    # -----------------------------
    # 6. circular definition (simple check)
    # -----------------------------
    if word.lower() in t:
        # not always bad, but flag weak cases like:
        # "to debauch someone by debauch"
        if t.count(word.lower()) > 1:
            return False

    # -----------------------------
    # 7. junk prefixes (MW leftovers)
    # -----------------------------
    if t.startswith(("see", "cf", "usu", "usually")):
        return False

    return True


def is_valid_distractor(word: str, distractor: str, pos: str | None = None) -> bool:
    if not distractor:
        return False

    t = distractor.strip().lower()

    # -----------------------------
    # 1. reject exact word echo
    # -----------------------------
    if t == word:
        return False

    # -----------------------------
    # 2. reject trivial prefix echo
    # -----------------------------
    if t.startswith(word + " "):
        return False

    # -----------------------------
    # 3. obvious invalid tokens
    # -----------------------------
    if t in INVALID_PATTERNS:
        return False

    # -----------------------------
    # 4. too short (heuristic)
    # -----------------------------
    if len(t.split()) < 3:
        return False

    # -----------------------------
    # 5. only punctuation / noise
    # -----------------------------
    if re.fullmatch(r"[\W_]+", t):
        return False

    # -----------------------------
    # 6. circular definition (simple check)
    # -----------------------------
    if word.lower() in t:
        # not always bad, but flag weak cases like:
        # "to debauch someone by debauch"
        if t.count(word.lower()) > 1:
            return False

    # -----------------------------
    # 7. junk prefixes (MW leftovers)
    # -----------------------------
    if t.startswith(("see", "cf", "usu", "usually")):
        return False

    return True


def score_definition(
    definition: str,
) -> float:
    # cheat
    return 0.0 * len(definition)