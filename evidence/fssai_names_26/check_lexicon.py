"""Read-only checker comparing evidence/fssai_names_26/candidates.csv against lexicon.csv and synonyms.csv."""

import collections
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CANDIDATES = ROOT / "evidence" / "fssai_names_26" / "candidates.csv"
LEXICON = ROOT / "src" / "foodscan" / "resources" / "lexicon.csv"
SYNONYMS = ROOT / "src" / "foodscan" / "resources" / "synonyms.csv"


def main() -> None:
    with LEXICON.open(encoding="utf-8", newline="") as f:
        lex_terms = {r["term"].strip().lower() for r in csv.DictReader(f) if r.get("term")}
    with SYNONYMS.open(encoding="utf-8", newline="") as f:
        syn_from = {r["from"].strip().lower() for r in csv.DictReader(f) if r.get("from")}

    by_ch = collections.defaultdict(collections.Counter)
    total = collections.Counter()
    with CANDIDATES.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            name = row["name"].strip().lower()
            if name in lex_terms:
                status = "exact"
            elif name in syn_from:
                status = "alias"
            else:
                status = "no"
            by_ch[row["chapter"]][status] += 1
            total[status] += 1

    print(f"Total candidates: {sum(total.values())}")
    print(f"Overall counts: exact={total['exact']} alias={total['alias']} no={total['no']}")
    for ch in sorted(by_ch):
        c = by_ch[ch]
        print(f"Chapter {ch}: total={sum(c.values())} exact={c['exact']} alias={c['alias']} no={c['no']}")


if __name__ == "__main__":
    main()
