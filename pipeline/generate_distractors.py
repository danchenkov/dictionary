from __future__ import annotations

import time

from dictionary.yaml_store import load_yaml, save_yaml
from dictionary.schema import migrate_dataset
from dictionary.types import Entry

from dictionary.services.distractor_service import generate_distractors
from dictionary.distractor_store import has_approved_distractors


def main() -> None:
    data = load_yaml()
    data = migrate_dataset(data)

    total = len(data)

    print(f"Loaded entries: {total}")

    for i, entry in enumerate(data):
        word = entry.get("word", "<unknown>")

        print(f"[{i + 1}/{total}] {word}")

        if has_approved_distractors(entry):
            print("    already processed")
            continue

        distractors = generate_distractors(entry)

        entry["distractors"] = distractors

        print(f"  -> generated {len(distractors)} distractors")

        time.sleep(0.2)

    save_yaml(data)
    print("\nDone.")


if __name__ == "__main__":
    main()