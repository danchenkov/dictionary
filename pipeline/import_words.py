from __future__ import annotations

import time
from typing import List

from dictionary.types import Entry, Definition, Distractor

from dictionary.yaml_store import load_yaml, save_yaml
from dictionary.services.definition_service import fetch_definitions


WORDS_FILE = "words_100.txt"


# -----------------------------
# Word loader
# -----------------------------

def load_words() -> list[str]:
    with open(WORDS_FILE, "r", encoding="utf-8") as f:
        return [w.strip() for w in f if w.strip()]


# -----------------------------
# Indexing (existing YAML lookup)
# -----------------------------

def index_words(data: list[Entry]) -> dict[str, Entry]:
    return {
        entry["word"].lower(): entry
        for entry in data
        if "word" in entry
    }


# -----------------------------
# Main pipeline
# -----------------------------

def main() -> None:
    words = load_words()
    data = load_yaml()

    word_index = index_words(data)

    print(f"Loaded words: {len(words)}")
    print(f"Existing entries: {len(data)}")

    for i, word in enumerate(words):
        key = word.lower()

        # skip already imported
        if key in word_index:
            continue

        print(f"[{i + 1}/{len(words)}] Processing: {word}")

        result = fetch_definitions(word)

        if not result.definitions:
            print("  -> No definitions found")
            continue

        entry: Entry = {
            "word": word,
            "pos": result.pos,
            "entries": result.definitions,
            "status": "imported",
            "reviewed": False,
            "distractors": [],
        }

        data.append(entry)
        save_yaml(data)

        print(
            f"  -> saved ({len(result.definitions)} definitions, "
            f"source={result.source_primary})"
        )

        time.sleep(0.25)

    print("\nDone.")


if __name__ == "__main__":
    main()