from __future__ import annotations

import os
import requests
from typing import Optional

from dictionary.types import Definition
from dictionary.normalize import normalize_mw_definition
from dictionary.validators import is_valid_definition


MW_API_KEY = os.getenv("MERRIAM_WEBSTER_API_KEY")

MW_URL = "https://www.dictionaryapi.com/api/v3/references/collegiate/json/"


def fetch_mw_definitions(word: str) -> list[Definition]:
    """
    Fetch definitions from Merriam-Webster Collegiate API.

    Returns normalized list of Definition objects.
    """

    if not MW_API_KEY:
        return []

    url = f"{MW_URL}{word}"

    try:
        response = requests.get(
            url,
            params={"key": MW_API_KEY},
            timeout=10,
        )
        response.raise_for_status()

        data = response.json()

        if not isinstance(data, list):
            return []

        entry = data[0]

        if isinstance(entry, str):
            return []

        pos: Optional[str] = entry.get("fl")

        shortdefs = entry.get("shortdef", [])
        if not isinstance(shortdefs, list):
            return []

        results: list[Definition] = []

        for i, raw_def in enumerate(shortdefs):
            cleaned = normalize_mw_definition(word=word, text=raw_def)

            if not cleaned:
                continue

            if not is_valid_definition(word, cleaned):
                continue

            results.append(
                {
                    "text": cleaned,
                    "source": "merriam-webster",
                    "sense": i + 1,
                    "primary": i == 0,
                    "pos": pos,
                }
            )

        return results

    except Exception as e:
        print(f"[MW ERROR] {word}: {e}")
        return []