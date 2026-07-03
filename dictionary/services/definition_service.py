from __future__ import annotations

from typing import Optional

from dictionary.types import Entry, Definition

from dictionary.sources.mw_api import fetch_mw_definitions
from dictionary.sources.openai_api import fetch_openai_definitions


class DefinitionResult:
    """
    Internal normalized result for a word.
    """

    def __init__(
        self,
        word: str,
        pos: Optional[str],
        definitions: list[Definition],
        source_primary: str,
    ) -> None:
        self.word = word
        self.pos = pos
        self.definitions = definitions
        self.source_primary = source_primary


def extract_pos(entries: list[Definition]) -> str | None:
    for e in entries:
        pos = e.get("pos")
        if pos:
            return pos
    return None


def fetch_definitions(
    word: str,
    use_openai_fallback: bool = True,
    enrich_with_openai: bool = True,
) -> DefinitionResult:
    """
    Unified definition pipeline.

    Strategy:
    1. Try Merriam-Webster first (authoritative)
    2. If empty → fallback to OpenAI
    3. Optionally enrich MW with OpenAI extras
    """

    mw_entries, mw_pos = fetch_mw_definitions(word)

    openai_entries: list[Definition] = []

    # -----------------------------------
    # CASE 1: MW exists
    # -----------------------------------
    if mw_entries:
        if enrich_with_openai:
            openai_entries = fetch_openai_definitions(word, pos=mw_pos)

        definitions = _merge_definitions(mw_entries, openai_entries)

        return DefinitionResult(
            word=word,
            pos=mw_pos,
            definitions=definitions,
            source_primary="merriam-webster",
        )

    # -----------------------------------
    # CASE 2: MW missing → OpenAI fallback
    # -----------------------------------
    if use_openai_fallback:
        openai_entries = fetch_openai_definitions(word)

        return DefinitionResult(
            word=word,
            pos=mw_pos,
            definitions=openai_entries,
            source_primary="openai",
        )

    # -----------------------------------
    # CASE 3: nothing found
    # -----------------------------------
    return DefinitionResult(
        word=word,
        pos=None,
        definitions=[],
        source_primary="none",
    )


def _merge_definitions(
    mw: list[Definition],
    ai: list[Definition],
) -> list[Definition]:
    """
    Merge MW + AI while avoiding duplicates.
    MW always stays primary.
    """

    seen: set[str] = set()

    merged: list[Definition] = []

    for d in mw + ai:
        text = d["text"].strip()
        key = text.lower()

        if key in seen:
            continue

        seen.add(key)
        merged.append(d)

    return merged