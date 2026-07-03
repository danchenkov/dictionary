from __future__ import annotations

import re
from typing import Optional


# -----------------------------
# Definition validation
# -----------------------------

def is_valid_definition(word: str, text: str) -> bool:
    """
    Basic sanity checks for dictionary definitions.
    """

    if not text:
        return False

    t = text.strip().lower()
    w = word.strip().lower()

    # reject empty / trivial
    if len(t) < 3:
        return False

    # reject self-referential definitions
    if t == w:
        return False

    # reject definitions that are just punctuation or garbage
    if re.fullmatch(r"[\[\]\(\)\{\}•\-–—]+", t):
        return False

    # reject obvious placeholder artifacts
    if t in {"thing", "[thing]"}:
        return False

    return True


# -----------------------------
# Distractor validation
# -----------------------------

def is_valid_distractor(word: str, text: str) -> bool:
    """
    Ensures distractor is not accidentally valid or related.
    """

    if not is_valid_definition(word, text):
        return False

    t = text.lower()

    # avoid direct word reuse
    if word.lower() in t:
        return False

    # avoid too short / too vague outputs
    if len(t.split()) < 3:
        return False

    return True


# -----------------------------
# POS compatibility (hard filter)
# -----------------------------

def is_pos_compatible(
    entry_pos: Optional[str],
    text: str,
) -> bool:
    """
    Lightweight heuristic POS filter (V1).

    This is NOT linguistic-grade—just a safety layer.
    """

    if not entry_pos:
        return True

    t = text.lower()
    pos = entry_pos.lower()

    # -------------------------
    # verb heuristics
    # -------------------------
    if pos.startswith("v"):
        # verbs often start with "to"
        if t.startswith("to "):
            return True
        # reject noun-like patterns
        if t.startswith(("a ", "an ", "the ")):
            return False

    # -------------------------
    # noun heuristics
    # -------------------------
    if pos.startswith("n"):
        # allow most noun-like structures
        return True

    # -------------------------
    # adjective heuristics
    # -------------------------
    if pos.startswith("adj"):
        # adjectives often start descriptive, but we keep permissive
        return True

    # -------------------------
    # adverb heuristics
    # -------------------------
    if pos.startswith("adv"):
        return True

    return True