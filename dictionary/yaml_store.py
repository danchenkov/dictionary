from __future__ import annotations
from dictionary.types import Entry

import yaml
from pathlib import Path

YAML_FILE = "definitions.yaml"

# -----------------------------
# YAML helpers
# -----------------------------

def load_yaml() -> list[Entry]:
    path = Path(YAML_FILE)
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data if data else []


def save_yaml(
    data: list[Entry],
) -> None:
    with open(YAML_FILE, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)


