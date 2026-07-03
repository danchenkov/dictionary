from __future__ import annotations
from dictionary.types import Entry, Distractor

def get_distractors(
    entry: Entry,
) -> list[Distractor]:
    """
    Always returns distractors as a list (normalized view).
    """
    d = entry.get("distractors")

    if isinstance(d, list):
        return d

    if isinstance(d, dict):
        # old schema fallback (optional migration point)
        generated = d.get("generated", [])
        approved = d.get("approved", [])
        return generated + approved

    return []


def set_distractors(
    entry: Entry,
    distractors: list[Distractor],
) -> None:
    """
    Always writes new schema format.
    """
    entry["distractors"] = distractors


def has_approved_distractors(
    entry: Entry,
) -> bool:
    return any(
        d.get("status") == "approved"
        for d in get_distractors(entry)
        if isinstance(d, dict)
    )