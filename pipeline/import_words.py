from __future__ import annotations
from dictionary.types import Entry, Definition, Distractor

import os
import requests
import time

from openai import OpenAI

from dictionary.yaml_store import load_yaml, save_yaml
from dictionary.normalize import normalize_definition, normalize_mw_definition
from dictionary.validators import is_valid_definition


WORDS_FILE = "words_100.txt"

MW_API_KEY = os.getenv("MERRIAM_WEBSTER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAPI_DICTIONARY_API_KEY")

MW_URL = "https://www.dictionaryapi.com/api/v3/references/collegiate/json/"

client: OpenAI | None = (
    OpenAI(api_key=OPENAI_API_KEY)
    if OPENAI_API_KEY
    else None
)

def index_words(
    data: list[Entry],
) -> dict[str, Entry]:
    return {entry["word"].lower(): entry for entry in data if "word" in entry}


# -----------------------------
# Word loader
# -----------------------------

def load_words() -> list[str]:
    with open(WORDS_FILE, "r", encoding="utf-8") as f:
        return [w.strip() for w in f if w.strip()]


# -----------------------------
# Merriam-Webster
# -----------------------------

def fetch_mw(
    word: str,
) -> list[Definition]:
    if not MW_API_KEY:
        return []

    url = f"{MW_URL}{word}"

    try:
        r = requests.get(url, params={"key": MW_API_KEY}, timeout=10)
        r.raise_for_status()
        data = r.json()

        if not isinstance(data, list):
            return []

        entry = data[0]

        if isinstance(entry, str):
            return []

        results: list[Definition] = []
        pos = entry.get("fl")

        if "shortdef" in entry:
            for i, d in enumerate(entry.get("shortdef", [])):
                cleaned = normalize_mw_definition(word, d)
                if is_valid_definition(word, cleaned):
                    results.append({
                        "text": cleaned,
                        "source": "merriam-webster",
                        "sense": i + 1,
                        "primary": i == 0,
                        "pos": pos,
                    })

        return results

    except Exception as e:
        print(f"[MW ERROR] {word}: {e}")
        return []


# -----------------------------
# OpenAI fallback
# -----------------------------

def fetch_openai(
    word: str,
) -> list[Definition]:
    if not client:
        return []

    try:
        prompt = f"""
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

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a precise lexicographer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )

        content = response.choices[0].message.content
        if content is None:
            return []
        text = content.strip()

        lines: list[str] = []

        for l in text.split("\n"):
            l = l.strip()

            if not l:
                continue

            # remove bullet markers
            l = l.lstrip("-• ").strip()

            # remove numbering (NEW)
            l = normalize_definition(l)

            # remove invalid artifacts
            if l.strip() in {"[THING]", "THING", ""}:
                continue

            if l.strip().lower() == word.lower():
                continue

            if len(l.split()) < 3:
                continue

            if l:
                if is_valid_definition(word, l):
                    lines.append(l)

        results: list[Definition] = []

        for i, line in enumerate(lines):
            results.append({
                "text": line,
                "source": "openai",
                "sense": i + 1,
                "primary": False,
                "pos": None,
            })

        return results

    except Exception as e:
        print(f"[OPENAI ERROR] {word}: {e}")
        return []


# -----------------------------
# Merge logic
# -----------------------------

def merge_entries(
    existing_entries: list[Definition],
    new_entries: list[Definition],
) -> list[Definition]:
    seen = set(e["text"].lower() for e in existing_entries)

    for e in new_entries:
        if e["text"].lower() not in seen:
            existing_entries.append(e)
            seen.add(e["text"].lower())

    return existing_entries


# -----------------------------
# Choose canonical
# -----------------------------

def choose_canonical(
    mw_entries: list[Definition],
    ai_entries: list[Definition],
) -> Definition | None:
    """
    Priority:
    1. Merriam-Webster primary
    2. first MW entry
    3. first AI entry
    """

    if mw_entries:
        return mw_entries[0]

    if ai_entries:
        return ai_entries[0]

    return None


# -----------------------------
# Main
# -----------------------------

def main() -> None:
    words: list[str] = load_words()
    data: list[Entry] = load_yaml()
    word_index: dict[str, Entry] = index_words(data)

    print(f"Loaded words: {len(words)}")
    print(f"Existing entries: {len(data)}")

    for i, word in enumerate(words):
        key = word.lower()

        if key in word_index:
            continue

        print(f"[{i+1}/{len(words)}] Processing: {word}")

        mw_entries = fetch_mw(word)

        if mw_entries:
            print("  -> Merriam-Webster OK")
            ai_entries = fetch_openai(word)
        else:
            print("  -> MW missing, using OpenAI fallback")
            mw_entries = []
            ai_entries = fetch_openai(word)

        entries = mw_entries + ai_entries

        if not entries:
            print("  -> No definitions found")
            continue

        canonical = choose_canonical(mw_entries, ai_entries)

        if not canonical:
            continue

        distractors: list[Distractor] = []
        entry: Entry = {
            "word": word,
            "pos": canonical.get("pos"),
            "canonical": canonical,
            "entries": entries,
            "status": "imported",
            "reviewed": False,
            "distractors": distractors,
        }

        data.append(entry)
        save_yaml(data)

        print(f"  -> saved ({len(entries)} entries)")

        time.sleep(0.25)

    print("\nDone.")


if __name__ == "__main__":
    main()