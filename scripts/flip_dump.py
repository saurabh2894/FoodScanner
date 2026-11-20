"""Dump the analysis of every frozen paste input (all fields the flip checks compare) from the build on PYTHONPATH, as JSON.

One run = one process = one set of resource tables: run it once per build (the resource tables are cached inside a process, so a before/after comparison made in
ONE process is invalid). Read-only. Usage: PYTHONPATH=<src dir> python scripts/flip_dump.py --evaluation evaluation --out dump.json
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

SETS = [("b1", "fresh_batch_1"), ("b2", "fresh_batch_2"), ("b3", "fresh_batch_3"), ("neg", "negation_addendum"), ("dev", "dev_regression_15")]


def dump_dir(inputs_dir: str) -> dict:
    """Same fields for every *.txt in one directory, keyed by file stem (used for the out-of-sample set, whose texts live in a gitignored cache)."""
    from foodscan.pipeline import analyse_text
    out = {}
    for f in sorted(glob.glob(os.path.join(inputs_dir, "*.txt"))):
        with open(f, encoding="utf-8") as fh:
            out[os.path.basename(f)[:-4]] = _fields(analyse_text(fh.read(), source="text"))
    return out


def _fields(a) -> dict:
    return {"answered": a.answered, "group": a.group if a.answered else None, "reason": None if a.answered else a.reason, "warnings": a.warnings,
            "status": a.completeness["status"], "drivers": [d_.detail for d_ in a.drivers], "ingredients": a.ingredients, "unassessed": a.unassessed,
            "ins_mappings": [{"code": u.code, "name": u.name, "ref_name": u.ref_name, "declared": u.declared, "declared_roles": list(u.declared_roles), "role_notes": u.role_notes}
                             for u in a.ins_mappings]}


def dump(evaluation: str) -> dict:
    from foodscan.pipeline import analyse_text
    out = {}
    for prefix, d in SETS:
        for f in sorted(glob.glob(os.path.join(evaluation, d, "inputs", "*.txt"))):
            with open(f, encoding="utf-8") as fh:
                a = analyse_text(fh.read(), source="text")
            out[f"{prefix}/{os.path.basename(f)[:-4]}"] = {
                "answered": a.answered, "group": a.group if a.answered else None, "reason": None if a.answered else a.reason, "warnings": a.warnings,
                "status": a.completeness["status"], "drivers": [d_.detail for d_ in a.drivers], "ingredients": a.ingredients, "unassessed": a.unassessed,
                "ins_mappings": [{"code": u.code, "name": u.name, "ref_name": u.ref_name, "declared": u.declared, "declared_roles": list(u.declared_roles), "role_notes": u.role_notes}
                                 for u in a.ins_mappings]}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--evaluation", default="evaluation")
    ap.add_argument("--inputs-dir", default=None, help="dump every *.txt in this directory instead of the frozen sets")
    ap.add_argument("--out", required=True)
    ap.add_argument("--probe-file", default=None, help="text file, one term per line: also write <out>.probe.json saying whether THIS build recognises each term")
    args = ap.parse_args(argv)
    import foodscan
    sys.stderr.write(f"foodscan from {foodscan.__file__}\n")
    if args.probe_file:
        from foodscan.classify import is_recognised
        from foodscan.normalise import normalise_ingredient
        with open(args.probe_file, encoding="utf-8") as fh:
            terms = [ln.strip() for ln in fh if ln.strip()]
        with open(args.out + ".probe.json", "w", encoding="utf-8") as fh:
            json.dump({t: bool(is_recognised(normalise_ingredient(t).name)) for t in terms}, fh, indent=2)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(dump_dir(args.inputs_dir) if args.inputs_dir else dump(args.evaluation), fh, indent=2, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
