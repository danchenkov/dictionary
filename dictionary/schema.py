from __future__ import annotations
from dictionary.types import Entry

from dictionary.distractor_store import get_distractors,set_distractors


def migrate_entry(
    entry: Entry
) -> Entry:
    """
    Upgrade a single YAML entry to the latest schema.

    Safe to call repeatedly.
    """

    # --------------------------------------------------
    # Migration 1
    # distractors:
    #   generated: []
    #   approved: []
    #
    # ->
    #
    # distractors: []
    # --------------------------------------------------

    distractors = entry.get("distractors")

    if isinstance(distractors, dict):

        generated = distractors.get("generated", [])
        approved = set(distractors.get("approved", []))

        new = []

        for item in generated:

            if isinstance(item, str):
                new.append({
                    "text": item,
                    "source": "unknown",
                    "status": (
                        "approved"
                        if item in approved
                        else "generated"
                    ),
                })

            elif isinstance(item, dict):

                if "status" not in item:
                    item["status"] = "generated"

                new.append(item)

        set_distractors(entry, new)

    elif distractors is None:
        set_distractors(entry, [])

    return entry


def migrate_dataset(
    data: list[Entry],
) -> list[Entry]:

    for entry in data:
        migrate_entry(entry)

    return data