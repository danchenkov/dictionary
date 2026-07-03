from __future__ import annotations

from typing import Optional

from dictionary.types import Entry, Distractor

from dictionary.sources.openai_api import fetch_openai_definitions
from dictionary.validators import is_valid_distractor
from dictionary.normalize import normalize_definition


MAX_CANDIDATES = 15
MAX_FINAL = 10


def generate_distractors(entry: Entry) -> list[Distractor]:
    """
    Generate POS-aware distractors for a dictionary entry.
    """

    word = entry["word"]
    pos = entry.get("pos")
    canonical = entry["canonical"]["text"]

    existing_texts = _collect_existing_texts(entry)

    raw = _generate_candidates(word, canonical, pos)

    filtered = _filter_candidates(
        word=word,
        candidates=raw,
        existing=existing_texts,
    )

    filtered = _score_candidates(filtered)
    filtered = filtered[:MAX_FINAL]

    return [
        {
            "text": d,
            "source": "openai",
            "status": "generated",
            "reviewed": False,
        }
        for d in filtered
    ]


# -----------------------------
# Candidate generation (LLM)
# -----------------------------

def _generate_candidates(
    word: str,
    canonical: str,
    pos: Optional[str],
) -> list[str]:
    """
    Ask LLM for plausible but incorrect distractors.
    """

    from dictionary.sources.openai_api import client

    if client is None:
        return []

    prompt = f"""
Word: {word}
Part of speech: {pos}
Correct definition: {canonical}

Generate {MAX_CANDIDATES} DEFINITELY WRONG dictionary definitions.

Rules:
- Must match part of speech: {pos}
- Must NOT overlap meaning
- Must NOT be synonyms
- Must be plausible but incorrect
- Max 12 words
- One per line
- No numbering or bullets
- No explanations
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You generate distractors for exams."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
        )

        content = response.choices[0].message.content or ""
        lines: list[str] = []

        for raw in content.split("\n"):
            line = raw.strip()

            if not line:
                continue

            line = line.lstrip("-•* ").strip()
            line = normalize_definition(line)

            if line:
                lines.append(line)

        return lines

    except Exception as e:
        print(f"[DISTRACTOR ERROR] {word}: {e}")
        return []


# -----------------------------
# Filtering
# -----------------------------

def _filter_candidates(
    word: str,
    candidates: list[str],
    existing: set[str],
) -> list[str]:
    seen: set[str] = set()
    results: list[str] = []

    existing_lower = {e.lower() for e in existing}

    for c in candidates:
        c_clean = c.strip()

        if not c_clean:
            continue

        if not is_valid_distractor(word, c_clean):
            continue

        if c_clean.lower() in existing_lower:
            continue

        if c_clean.lower() in seen:
            continue

        seen.add(c_clean.lower())
        results.append(c_clean)

    return results


# -----------------------------
# Ranking heuristic (V1 simple)
# -----------------------------

def _score_candidates(candidates: list[str]) -> list[str]:
    """
    Simple heuristic:
    - prefer medium-length definitions
    - avoid extremes
    """

    return sorted(
        candidates,
        key=lambda s: (abs(len(s) - 60), len(s))
    )


# -----------------------------
# Existing content collector
# -----------------------------

def _collect_existing_texts(entry: Entry) -> set[str]:
    texts: set[str] = set()

    for d in entry.get("entries", []):
        texts.add(d["text"])

    texts.add(entry["canonical"]["text"])

    for d in entry.get("distractors", []):
        texts.add(d["text"])

    return texts