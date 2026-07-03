from __future__ import annotations

import time

from dictionary.yaml_store import load_yaml, save_yaml
from dictionary.schema import migrate_dataset

from dictionary.services.distractor_service import generate_distractors


def should_skip(entry: dict) -> bool:
    """
    Skip if already has approved distractors.
    """

    distractors = entry.get("distractors", [])

    if isinstance(distractors, list):
        return any(
            d.get("status") == "approved"
            for d in distractors
            if isinstance(d, dict)
        )

    return False


def main() -> None:
    data = load_yaml()
    data = migrate_dataset(data)

    total = len(data)

    print(f"Loaded entries: {total}")

    for i, entry in enumerate(data):
        word = entry.get("word", "<unknown>")

        print(f"[{i + 1}/{total}] {word}")

        if should_skip(entry):
            print("  -> already approved, skipping")
            continue

        distractors = generate_distractors(entry)

        entry["distractors"] = distractors

        print(f"  -> generated {len(distractors)} distractors")

        time.sleep(0.2)

    save_yaml(data)
    print("\nDone.")


if __name__ == "__main__":
    main()