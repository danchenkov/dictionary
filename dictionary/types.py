from __future__ import annotations

from typing import TypedDict


class Definition(TypedDict):
    text: str
    source: str
    sense: int
    primary: bool


class Distractor(TypedDict):
    text: str
    source: str
    status: str
    reviewed: bool


class Entry(TypedDict):
    word: str
    canonical: Definition
    entries: list[Definition]
    pos: str | None
    status: str
    reviewed: bool
    distractors: list[Distractor]