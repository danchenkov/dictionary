import os
import time
import requests
import yaml
from pathlib import Path


WORDS_FILE = "words_100.txt"
YAML_FILE = "definitions.yaml"

API_KEY = os.getenv("MERRIAM_WEBSTER_API_KEY")
API_URL = "https://www.dictionaryapi.com/api/v3/references/collegiate/json/"


# -----------------------------
# YAML helpers
# -----------------------------

def load_yaml():
    path = Path(YAML_FILE)
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f)
            return data if data else []
        except yaml.YAMLError:
            return []


def save_yaml(data):
    with open(YAML_FILE, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)


def already_imported(words_set):
    existing = load_yaml()
    for entry in existing:
        if "word" in entry:
            words_set.add(entry["word"].lower())
    return existing, words_set


# -----------------------------
# Word loader
# -----------------------------

def load_words():
    with open(WORDS_FILE, "r", encoding="utf-8") as f:
        return [w.strip() for w in f if w.strip()]


# -----------------------------
# Merriam-Webster lookup
# -----------------------------

def fetch_definition(word):
    if not API_KEY:
        raise RuntimeError("Missing MERRIAM_WEBSTER_API_KEY")

    url = f"{API_URL}{word}"
    params = {"key": API_KEY}

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        # MW sometimes returns suggestions instead of entries
        if not isinstance(data, list) or len(data) == 0:
            return None

        entry = data[0]

        # If suggestion list returned (strings instead of dicts)
        if isinstance(entry, str):
            return None

        # Try to extract shortdef
        if "shortdef" in entry and entry["shortdef"]:
            return entry["shortdef"][0]

        # fallback: deeper structure
        if "def" in entry:
            return str(entry["def"][0])

        return None

    except Exception as e:
        print(f"[ERROR] {word}: {e}")
        return None


# -----------------------------
# Main importer
# -----------------------------

def main():
    words = load_words()

    existing, imported_set = already_imported(set())

    print(f"Loaded words: {len(words)}")
    print(f"Already imported: {len(imported_set)}")

    new_entries = []

    for i, word in enumerate(words):
        w = word.lower()

        if w in imported_set:
            continue

        print(f"[{i+1}/{len(words)}] Fetching: {word}")

        definition = fetch_definition(word)

        if not definition:
            print(f"  -> No definition found")
            continue

        entry = {
            "word": word,
            "definition": definition,
            "source": "merriam-webster",
            "reviewed": False,
            "distractors": {
                "generated": [],
                "approved": []
            }
        }

        new_entries.append(entry)
        imported_set.add(w)

        # incremental save (important for long runs)
        save_yaml(existing + new_entries)

        print(f"  -> OK")

        # light rate limiting (safe default)
        time.sleep(0.25)

    print("\nDone.")
    print(f"New entries added: {len(new_entries)}")


if __name__ == "__main__":
    main()