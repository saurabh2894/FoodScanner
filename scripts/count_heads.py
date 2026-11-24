"""Count head terms three ways: lexicon rows, strict placed rows, and canonical placed heads.

Canonical means spelling, singular/plural and canned/tinned variants of one food collapse into one head (they are recognised phrasings, not distinct foods).
Name-only (unplaced), culture and neutral rows never count as placed.
"""
import collections
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NON_PLACED = {"unplaced", "culture", "neutral"}


def norm(t: str) -> str:
    t = t.lower().replace("tinned", "canned").replace("-", " ")
    t = re.sub(r"ise\b", "ize", t).replace("colour", "color").replace("flavour", "flavor").replace("yoghurt", "yogurt")

    def sing(x):
        if x.endswith("ies") and len(x) > 4:
            return x[:-3] + "y"
        if x.endswith("oes"):
            return x[:-2]
        if x.endswith("ss") or x.endswith("us"):
            return x
        if x.endswith("s") and len(x) > 3:
            return x[:-1]
        return x
    return " ".join(sing(x) for x in t.split())


def counts():
    rows = list(csv.DictReader((ROOT / "src/foodscan/resources/lexicon.csv").open(newline="")))
    placed = [r for r in rows if r["kind"] not in NON_PLACED]
    groups = collections.defaultdict(list)
    for r in placed:
        groups[norm(r["term"])].append(r["term"])
    return {"rows": len(rows), "placed_rows": len(placed), "canonical_placed": len(groups), "variant_clusters": {k: v for k, v in groups.items() if len(v) > 1}}


if __name__ == "__main__":
    c = counts()
    print(f"lexicon rows {c['rows']}; strict placed rows {c['placed_rows']}; canonical placed heads {c['canonical_placed']}")
    for k, v in sorted(c["variant_clusters"].items()):
        print(f"  {k}: {', '.join(v)}")
    sys.exit(0)
