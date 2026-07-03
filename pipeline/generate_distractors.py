from __future__ import annotations

from dictionary.types import Entry
from dictionary.schema import migrate_dataset
from dictionary.yaml_store import load_yaml, save_yaml
from dictionary.distractors import generate_distractors
from dictionary.distractor_store import set_distractors


def should_skip(
    entry: Entry,
) -> bool:
    distractors = entry.get("distractors")

    # Case 1: new schema (list of objects)
    if isinstance(distractors, list):
        return any(
            d.get("status") == "approved"
            for d in distractors
            if isinstance(d, dict)
        )

    # Case 2: old schema (dict)
    if isinstance(distractors, dict):
        approved = distractors.get("approved", [])
        return len(approved) > 0

    # Case 3: missing or corrupted
    return False


def main() -> None:
    data: list[Entry] = load_yaml()
    data = migrate_dataset(data)

    total = len(data)
    generated_total = 0

    for i, entry in enumerate(data):
        word = entry["word"]

        print(f"[{i+1}/{total}] {word}")

        if should_skip(entry):
            print("    already processed")
            continue

        generated = generate_distractors(entry)
        set_distractors(entry, generated)
        generated_total += len(generated)

    save_yaml(data)
    print(f"    generated {generated_total} distractors total")


if __name__ == "__main__":
    main()