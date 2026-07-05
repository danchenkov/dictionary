from __future__ import annotations

import os
from typing import Optional

from openai import OpenAI

from dictionary.types import Definition
from dictionary.normalize import normalize_definition
from dictionary.validators import is_valid_definition


OPENAI_API_KEY = os.getenv("OPENAPI_DICTIONARY_API_KEY")

client: Optional[OpenAI] = (
    OpenAI(api_key=OPENAI_API_KEY)
    if OPENAI_API_KEY
    else None
)


SYSTEM_PROMPT = "You are a precise lexicographer."


USER_PROMPT_TEMPLATE = """
You are a lexicographer.

Return ONLY valid dictionary definitions for the word: "{word}".

STRICT RULES:
- Do NOT repeat the word itself
- Do NOT return the word alone
- Do NOT return numbered lists
- Do NOT include synonyms as definitions
- Each line must be a complete definition
- Maximum 15 words per definition
- If unsure, rewrite meaningfully or omit

OUTPUT FORMAT:
One definition per line only.
"""


def fetch_openai_definitions(
    word: str,
    pos: Optional[str] = None,
    max_defs: int = 6,
) -> list[Definition]:
    """
    Fetch dictionary-style definitions from OpenAI.

    Args:
        word: target word
        pos: optional part of speech hint (not strictly enforced yet)
        max_defs: safety cap after filtering

    Returns:
        list[Definition]
    """

    if not client:
        return []

    prompt = USER_PROMPT_TEMPLATE.format(word=word)

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )

        content = response.choices[0].message.content
        if not content:
            return []

        lines: list[str] = []

        for raw in content.split("\n"):
            line = raw.strip()

            if not line:
                continue

            # remove bullets or numbering artifacts
            line = line.lstrip("-•* ").strip()
            line = normalize_definition(line)

            # reject obvious garbage
            if not line:
                continue

            if line.lower() == word.lower():
                continue

            if len(line.split()) < 3:
                continue

            if not is_valid_definition(word, line):
                continue

            lines.append(line)

        results: list[Definition] = []

        for i, definition in enumerate(lines[:max_defs]):
            results.append(
                {
                    "text": definition,
                    "source": "openai",
                }
            )

        return results

    except Exception as e:
        print(f"[OPENAI ERROR] {word}: {e}")
        return []