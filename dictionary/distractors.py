from __future__ import annotations

import os

from openai import OpenAI

from dictionary.normalize import normalize_definition
from dictionary.types import Distractor, Entry
from dictionary.validators import is_valid_distractor

OPENAI_API_KEY = os.getenv("OPENAPI_DICTIONARY_API_KEY")

client: OpenAI | None = (
    OpenAI(api_key=OPENAI_API_KEY)
    if OPENAI_API_KEY
    else None
)

def generate_distractors(
    entry: Entry,
) -> list[Distractor]:
    """
    Generate candidate distractors for a YAML entry.

    Returns:
        list[Distractor]
    """

    if not client:
        return []

    word = entry["word"]
    canonical = entry["canonical"]["text"]
    pos = entry.get("pos")

    existing = {
        e["text"].lower()
        for e in entry["entries"]
    }

    existing.add(entry["canonical"]["text"].lower())

    raw_candidates = _generate_candidates(
        word,
        canonical,
        pos,
    )

    candidates = _filter_candidates(
        word,
        raw_candidates,
        existing,
    )

    candidates = _order_candidates(candidates)

    candidates = candidates[:10]

    print(
        f"    {len(raw_candidates)} generated, "
        f"{len(candidates)} survived filtering"
    )

    return _build_objects(candidates)


def _generate_candidates(
    word: str,
    definition: str,
    pos: str | None,
) -> list[str]:
    if not client:
        return []

    try:
        prompt = f"""
Word:
{word}

Part of speech:
{pos}

Correct definition:
{definition}

Generate 15 plausible but definitely incorrect dictionary definitions.
The definitions should resemble Merriam-Webster style.
They should sound believable to an English learner but must not correctly define the word.
All distractors MUST match this part of speech.

The distractors should belong to the same grammatical category.

Examples:

If the word is a noun, generate noun definitions.

If the word is a verb, generate verb definitions.

If the word is an adjective, generate adjective definitions.

If the word is an adverb, generate adverb definitions.

If the word is a phrase, generate phrase definitions.

The distractors should look like they could belong to another word of the same part of speech.

Rules:

- Every definition must be DEFINITELY WRONG.

- Never define the word correctly.

- Never use synonyms.

- Never overlap with the correct meaning.

- Dictionary style.

- Maximum 12 words.

- Do not use the target word or any form of it.

- One definition per line.

- No numbering.

- No bullets.

- No explanations.
"""

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content":
                        "You are creating distractors for a vocabulary quiz.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.8,
        )

        text = response.choices[0].message.content or ""
        results: list[str] = []

        for line in text.splitlines():
            line = line.lstrip("-•* ").strip()

            if not line:
                continue

            line = normalize_definition(line)
            if not line:
                continue

            if line.lower() == word.lower():
                continue

            if len(line.split()) < 3:
                continue

            if line:
                results.append(line)

        return results

    except Exception as e:
        print(f"[OPENAI ERROR] {word}: {e}")
        return []


def _filter_candidates(
    word: str,
    candidates: list[str],
    existing: set[str],
) -> list[str]:

    filtered: list[str] = []
    seen: set[str] = set()

    existing_lower = {
        d.lower()
        for d in existing
    }

    for candidate in candidates:
        c = candidate.strip()

        if not is_valid_distractor(word, c):
            continue

        if c.lower() in seen:
            continue

        if c.lower() in existing_lower:
            continue

        seen.add(c.lower())
        filtered.append(c)

    return filtered


def _order_candidates(
    candidates: list[str],
) -> list[str]:

    return sorted(
        candidates,
        key=lambda s: (len(s), s.lower())
    )


def _build_objects(
    candidates: list[str],
) -> list[Distractor]:

    objects: list[Distractor] = []

    for candidate in candidates:
        objects.append({
            "text": candidate,
            "source": "openai",
            "status": "generated",
            "reviewed": False,
        })

    return objects
