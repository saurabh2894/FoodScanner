"""Report-only rerun of the fictional adversarial peel corpus.

The corpus is read from git, not copied into the current branch.
"""

import csv
import io
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS_REF = "origin/copilot/peel-adversarial-corpus"
CORPUS_PATH = "tests/corpus_adversarial_peel.csv"


def load_corpus():
    text = subprocess.run(
        ["git", "show", f"{CORPUS_REF}:{CORPUS_PATH}"],
        cwd=ROOT, check=True, capture_output=True, text=True, encoding="utf-8",
    ).stdout
    rows = list(csv.DictReader(io.StringIO(text, newline=""), strict=True))
    ids = set()
    for row in rows:
        if not all(row.get(key) for key in ("id", "category", "text")):
            raise ValueError(f"Incomplete corpus row: {row!r}")
        if row["id"] in ids:
            raise ValueError(f"Duplicate corpus id: {row['id']}")
        ids.add(row["id"])
    return rows


if __name__ == "__main__":
    print(f"{len(load_corpus())} fictional corpus rows loaded from {CORPUS_REF}.")
