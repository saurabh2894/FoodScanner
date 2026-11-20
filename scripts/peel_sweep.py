"""Sweep of parser._peel_label: every known prefix (each lexicon term) x label-like suffix patterns, in the build on PYTHONPATH.

One run = one process = one build (resource tables are cached per process). Read-only. Usage:
  PYTHONPATH=<src> python scripts/peel_sweep.py dump --out sweep.json
  python scripts/peel_sweep.py compare --before a.json --main b.json --guard c.json [--new-prefixes terms.txt]
Every item is SYNTHETIC ("<known term> <suffix>: Roasted Sesame"); it probes the heuristic, it is not a label and not evidence.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

# (suffix, class): GENUINE = real section-header wording that must still peel; NAME = a form/product word that belongs to the ingredient name; OTHER = neither (reported, not guarded)
SUFFIXES = [("POWDER FLAKE (0.6%)", "NAME"), ("POWDER FLAKE", "NAME"), ("FLAKE", "NAME"), ("FLAKES (2%)", "NAME"), ("POWDER (3%)", "NAME"), ("DRIED", "NAME"),
            ("EXTRACT (5%)", "NAME"), ("EXTRACT", "NAME"), ("MIX (10%)", "NAME"), ("MIX", "NAME"), ("BLEND", "NAME"), ("BLEND (2%)", "NAME"), ("PASTE", "NAME"),
            ("OLEORESIN", "OTHER"), ("OIL", "OTHER"), ("MASALA", "OTHER"), ("TOPPING", "OTHER"), ("GARNISH", "OTHER"),
            ("SEASONING", "GENUINE"), ("SEASONING (12%)", "GENUINE"), ("SOUP (22.7%)", "GENUINE"), ("SAUCE", "GENUINE")]


def dump(out: str) -> int:
    import foodscan
    from foodscan.parser import _peel_label
    sys.stderr.write(f"foodscan from {foodscan.__file__}\n")
    res = Path(foodscan.__file__).parent / "resources" / "lexicon.csv"
    terms = [r["term"] for r in csv.DictReader(res.open(encoding="utf-8-sig", newline=""))]
    rows = {}
    for t in terms:
        for suf, cls in SUFFIXES:
            item = f"{t.upper()} {suf}: Roasted Sesame"
            rows[f"{t}|{suf}"] = {"term": t, "suffix": suf, "class": cls, "peeled": _peel_label(item)}
    Path(out).write_text(json.dumps({"terms": terms, "rows": rows}, indent=1, ensure_ascii=False), encoding="utf-8")
    return 0


def compare(args) -> int:
    B, M, G = (json.loads(Path(p).read_text(encoding="utf-8")) for p in (args.before, args.main, args.guard))
    new = [t for t in M["terms"] if t not in set(B["terms"])]
    def peeled(D, k):
        return bool(D["rows"].get(k, {}).get("peeled"))
    out = {"new_prefixes": new, "n_old_prefixes": len(B["terms"])}
    for label, keys in (("new_prefixes", [k for k in M["rows"] if M["rows"][k]["term"] in new]), ("old_prefixes", [k for k in M["rows"] if M["rows"][k]["term"] not in new])):
        grid = {}
        for k in keys:
            r = M["rows"][k]
            g = grid.setdefault(f"{r['class']}|{r['suffix']}", {"main_peels": 0, "newly_peels_vs_before": 0, "guard_peels": 0, "n": 0})
            g["n"] += 1
            g["main_peels"] += peeled(M, k)
            g["guard_peels"] += peeled(G, k)
            g["newly_peels_vs_before"] += peeled(M, k) and not peeled(B, k)
        out[label] = grid
    print(json.dumps(out, indent=1))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("dump"); d.add_argument("--out", required=True)
    c = sub.add_parser("compare")
    for n in ("before", "main", "guard"):
        c.add_argument(f"--{n}", required=True)
    a = ap.parse_args()
    return dump(a.out) if a.cmd == "dump" else compare(a)


if __name__ == "__main__":
    sys.exit(main())
