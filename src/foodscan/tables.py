"""Loaders for the small CSV tables in resources/. Every row must carry a `source`."""
from __future__ import annotations

import csv
import io
from functools import lru_cache
from importlib import resources


@lru_cache(maxsize=None)
def load_table(name: str) -> tuple[dict[str, str], ...]:
    text = resources.files("foodscan.resources").joinpath(name).read_text(encoding="utf-8")
    rows = list(csv.DictReader(io.StringIO(text)))
    for r in rows:
        if not (r.get("source") or "").strip():
            raise ValueError(f"{name}: row without a source: {r}")
    return tuple(rows)


def has_table(name: str) -> bool:
    return resources.files("foodscan.resources").joinpath(name).is_file()
