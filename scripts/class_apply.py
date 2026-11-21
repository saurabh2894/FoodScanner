"""Apply a validated class batch to src/foodscan/resources/lexicon.csv: retype listed existing rows (kind column ONLY, source untouched) and append the gate's ready rows.
Only lexicon.csv is written; synonyms.csv and markers.csv are never touched. Text-level edits (the file is not re-quoted). Refuses when a ready term is already present.
Usage: python scripts/class_apply.py --rows <gate>/lexicon_candidate_rows.csv --from-kind whole_food --to-kind vegetable --retype cucumber tomato ...
"""
from __future__ import annotations

import argparse
import csv
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--rows", type=Path, required=True)
    ap.add_argument("--lexicon", type=Path, default=ROOT / "src" / "foodscan" / "resources" / "lexicon.csv")
    ap.add_argument("--from-kind", default="whole_food")
    ap.add_argument("--to-kind", required=True)
    ap.add_argument("--retype", nargs="*", default=[])
    a = ap.parse_args(argv)
    text = a.lexicon.read_bytes().decode("utf-8")
    present = {r[0] for r in csv.reader(io.StringIO(text, newline=""))}
    new = list(csv.reader(a.rows.open(encoding="utf-8", newline="")))[1:]
    dup = [r[0] for r in new if r[0] in present]
    if dup:
        print("Refusing: already present:", dup)
        return 2
    lines, done = text.split("\n"), set()
    for i, ln in enumerate(lines):
        for t in a.retype:
            if ln.startswith(f"{t},{a.from_kind},"):
                lines[i] = ln.replace(f",{a.from_kind},", f",{a.to_kind},", 1)
                done.add(t)
    missing = [t for t in a.retype if t not in done]
    if missing:
        print("Refusing: no row of kind", a.from_kind, "for", missing)
        return 2
    out = "\n".join(lines)
    if not out.endswith("\n"):
        out += "\n"
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\n").writerows(new)
    a.lexicon.write_bytes((out + buf.getvalue()).encode("utf-8"))
    print(f"retyped {len(done)} rows, appended {len(new)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
