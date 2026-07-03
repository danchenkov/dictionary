import os
import re
import requests
import time
import yaml
from pathlib import Path
from openai import OpenAI

from normalize import (
    normalize_definition,
    normalize_mw_definition,
)

WORDS_FILE = "words_100.txt"
YAML_FILE = "definitions.yaml"

MW_API_KEY = os.getenv("MERRIAM_WEBSTER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAPI_DICTIONARY_API_KEY")

MW_URL = "https://www.dictionaryapi.com/api/v3/references/collegiate/json/"

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


# -----------------------------
# YAML helpers
# -----------------------------

def load_yaml():
    path = Path(YAML_FILE)
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data if data else []


def save_yaml(data):
    with open(YAML_FILE, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)


def index_words(data):
    return {entry["word"].lower(): entry for entry in data if "word" in entry}


# -----------------------------
# Word loader
# -----------------------------

def load_words():
    with open(WORDS_FILE, "r", encoding="utf-8") as f:
        return [w.strip() for w in f if w.strip()]


# -----------------------------
# Merriam-Webster
# -----------------------------

def fetch_mw(word):
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

        results = []

        if "shortdef" in entry:
            for i, d in enumerate(entry["shortdef"]):
                cleaned = normalize_mw_definition(word, d)
                results.append({
                    "text": cleaned,
                    "source": "merriam-webster",
                    "sense": i + 1,
                    "primary": i == 0
                })

        return results

    except Exception as e:
        print(f"[MW ERROR] {word}: {e}")
        return []


# -----------------------------
# OpenAI fallback
# -----------------------------

def fetch_openai(word):
    if not client:
        return []

    try:
        prompt = f"""
Provide dictionary definitions for the word: "{word}"

Rules:
- one meaning per line
- max 12 words per definition
- no synonyms
- no examples
- dictionary style only
- if multiple meanings exist, list them separately
"""
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a precise lexicographer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )

        text = response.choices[0].message.content.strip()

        lines = []
        for l in text.split("\n"):
            l = l.strip()

            if not l:
                continue

            # remove bullet markers
            l = l.lstrip("-• ").strip()

            l = normalize_definition(normalize_mw_definition(word, l))

            if l:
                lines.append(l)

        results = []

        for i, line in enumerate(lines):
            results.append({
                "text": line,
                "source": "openai",
                "sense": i + 1,
                "primary": False
            })

        return results

    except Exception as e:
        print(f"[OPENAI ERROR] {word}: {e}")
        return []


# -----------------------------
# Merge logic
# -----------------------------

def merge_entries(existing_entries, new_entries):
    seen = set(e["text"].lower() for e in existing_entries)

    for e in new_entries:
        if e["text"].lower() not in seen:
            existing_entries.append(e)
            seen.add(e["text"].lower())

    return existing_entries


# -----------------------------
# Choose canonical
# -----------------------------

def choose_canonical(mw_entries, ai_entries):
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

def main():
    words = load_words()
    data = load_yaml()
    word_index = index_words(data)

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
            ai_entries = fetch_openai(word)  # optional enrichment
        else:
            print("  -> MW missing, using OpenAI fallback")
            mw_entries = []
            ai_entries = fetch_openai(word)

        entries = mw_entries + ai_entries

        if not entries:
            print("  -> No definitions found")
            continue

        canonical = choose_canonical(mw_entries, ai_entries)

        if not entries:
            print("  -> No definitions found")
            continue

        entry = {
            "word": word,
            "canonical": canonical,
            "entries": entries,
            "status": "imported",
            "reviewed": False,
            "distractors": {
                "generated": [],
                "approved": []
            }
        }

        data.append(entry)
        save_yaml(data)

        print(f"  -> saved ({len(entries)} entries)")

        time.sleep(0.25)

    print("\nDone.")


if __name__ == "__main__":
    main()