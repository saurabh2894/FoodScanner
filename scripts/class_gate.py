"""Class-bulk gate extras (after scripts/validate_batch.py): the checks the owner requires per class batch, on the READY rows of a validate_batch gate.

  1. Frozen 66 + out-of-sample 32: BEFORE (repo src copy) and AFTER (copy with the ready rows appended to lexicon.csv) analysed in SEPARATE fresh processes;
     every changed input is attributed to a staged term (a staged term in an added/removed unassessed item or a new driver); 0 unexplained is required;
     group moves are listed by kind (abstain->4 must be 0; abstain->1/other are listed separately and attributed).
  2. Drift: every existing lexicon term and synonym, analysed alone as 'Ingredients: <term>' before/after: 0 differences required.
  3. Negative controls (from the rule file 'negative_controls'): conditioned/processed forms that were REJECTED or QUEUED must not be recognised as a staged term after the change.
Read-only; merges nothing. Exit 0 ran; 1 error.
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import oos_eval  # noqa: E402
import validate_batch as vb  # noqa: E402

PROBE = r'''
import json, sys
from foodscan.pipeline import analyse_text
out = {}
for line in open(sys.argv[1], encoding="utf-8").read().splitlines():
    if not line.strip():
        continue
    a = analyse_text("Ingredients: " + line, source="text")
    out[line] = {"group": a.group if a.answered else None, "answered": a.answered, "ingredients": a.ingredients, "unassessed": a.unassessed, "status": a.completeness["status"],
                 "drivers": [d.detail for d in a.drivers], "reason": None if a.answered else a.reason}
json.dump(out, open(sys.argv[2], "w"), indent=0)
sys.stderr.write(sys.argv[3])
'''


def probe(src: Path, lines: list[str], out: Path, work: Path) -> dict:
    f = work / "lines.txt"
    f.write_text("\n".join(lines) + "\n", encoding="utf-8")
    s = work / "probe_run.py"
    s.write_text(PROBE, encoding="utf-8")
    env = {"PYTHONPATH": str(src), "PATH": "/usr/bin:/bin:/usr/local/bin", "HOME": str(Path.home())}
    r = subprocess.run([sys.executable, str(s), str(f), str(out), str(src)], capture_output=True, text=True, env=env, cwd=str(src.parent))
    if r.returncode or str(src) not in r.stderr:
        raise RuntimeError(f"probe failed or did not use {src}: {r.stderr[-300:]}")
    return json.loads(out.read_text(encoding="utf-8"))


def compare_sets(B: dict, A: dict, terms: list[str]) -> dict:
    fields = ("group", "status", "reason", "drivers", "warnings", "ingredients", "unassessed", "ins_mappings")
    listed, unexplained, kinds = [], [], {"abstain_to_4": [], "abstain_to_1": [], "abstain_to_2_3": [], "other_group_change": []}
    def variants(t):
        t = t.lower()
        v = {t, t.rstrip("s")}
        if t.endswith("ies"):
            v.add(t[:-3] + "y")                       # cranberries -> cranberry
        if t.endswith("oes") or t.endswith("ches") or t.endswith("shes") or t.endswith("sses"):
            v.add(t[:-2])
        return v
    low = sorted({x for t in terms for x in variants(t)})
    for k in B:
        ch = [f for f in fields if B[k].get(f) != A[k].get(f)]
        if not ch:
            continue
        txt = json.dumps([B[k].get(f) for f in ("unassessed", "ingredients", "drivers", "reason")] + [A[k].get(f) for f in ("unassessed", "ingredients", "drivers", "reason")]).lower()
        diff_unassessed = [u for u in B[k]["unassessed"] if u not in A[k]["unassessed"]] + [u for u in A[k]["unassessed"] if u not in B[k]["unassessed"]]
        hay = diff_unassessed + [d for d in A[k]["drivers"] if d not in B[k]["drivers"]] + ([A[k]["reason"]] if A[k].get("reason") != B[k].get("reason") and A[k].get("reason") else [])
        hit = sorted({t for t in low for u in hay if t in u.lower()})
        e = {"input": k, "changed": ch, "group": [B[k]["group"], A[k]["group"]], "status": [B[k]["status"], A[k]["status"]], "unassessed_diff": diff_unassessed, "staged_terms": hit}
        listed.append(e)
        if not hit:
            unexplained.append(k)
        g0, g1 = B[k]["group"], A[k]["group"]
        if g0 != g1:
            if g0 is None and g1 == 4:
                kinds["abstain_to_4"].append(k)
            elif g0 is None and g1 == 1:
                kinds["abstain_to_1"].append(k)
            elif g0 is None:
                kinds["abstain_to_2_3"].append(k)
            else:
                kinds["other_group_change"].append(k)
    return {"changed": listed, "unexplained": unexplained, **kinds}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--gate", type=Path, required=True, help="validate_batch gate directory (gate_report.json, lexicon_candidate_rows.csv)")
    ap.add_argument("--rule", type=Path, required=True)
    ap.add_argument("--oos-cache", type=Path, default=ROOT / "data" / "cache" / "oos_herb_spice_1")
    ap.add_argument("--src", type=Path, default=ROOT / "src")
    ap.add_argument("--evaluation", type=Path, default=ROOT / "evaluation")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)
    if a.out.exists() and not a.force:
        sys.stderr.write(f"Refusing to overwrite: {a.out}\n")
        return 2
    rule = json.loads(a.rule.read_text(encoding="utf-8"))
    rows = vb.read_csv(a.gate / "lexicon_candidate_rows.csv")
    terms = [r["term"] for r in rows]
    res = a.src / "foodscan" / "resources"
    drift_terms = [r["term"] for r in vb.read_csv(res / "lexicon.csv")] + [r["from"] for r in vb.read_csv(res / "synonyms.csv")]
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        bs, as_ = td / "b" / "src", td / "a" / "src"
        for d in (bs, as_):
            shutil.copytree(a.src, d, ignore=shutil.ignore_patterns("__pycache__", "*.egg-info"))
        vb.append_rows(as_ / "foodscan" / "resources" / "lexicon.csv", rows)
        out = {"rule_id": rule["rule_id"], "rows": terms}
        # 1. frozen 66 and out-of-sample 32, separate fresh processes
        vb.run_dump(bs, a.evaluation, td / "fb.json")
        vb.run_dump(as_, a.evaluation, td / "fa.json")
        out["frozen_66"] = compare_sets(json.loads((td / "fb.json").read_text()), json.loads((td / "fa.json").read_text()), terms)
        inputs = a.oos_cache / "inputs"
        if inputs.exists():
            oos_eval.dump(bs, inputs, td / "ob.json")
            oos_eval.dump(as_, inputs, td / "oa.json")
            B, A = json.loads((td / "ob.json").read_text()), json.loads((td / "oa.json").read_text())
            out["out_of_sample"] = {"inputs": len(B), **compare_sets(B, A, terms)}
        # 2. drift over every existing term and synonym
        db = probe(bs, drift_terms, td / "db.json", td)
        da = probe(as_, drift_terms, td / "da.json", td)
        diff = [t for t in db if db[t] != da[t]]
        out["drift"] = {"probed": len(db), "differences": diff}
        # 3. negative controls
        neg = rule.get("negative_controls", [])
        nb = probe(bs, neg, td / "nb.json", td)
        na = probe(as_, neg, td / "na.json", td)
        low = [t.lower() for t in terms]
        res_neg = {}
        for n in neg:
            rec_after = [i for i in na[n]["ingredients"] if any(i.lower() == t or i.lower().rstrip("s") == t.rstrip("s") for t in low)]
            res_neg[n] = {"group_before": nb[n]["group"], "group_after": na[n]["group"], "unassessed_after": na[n]["unassessed"], "ingredients_after": na[n]["ingredients"],
                          "ingredients_before": nb[n]["ingredients"], "read_as_staged_term": rec_after, "changed": nb[n] != na[n]}
        out["negative_controls"] = res_neg
    blockers = []
    for k in ("frozen_66", "out_of_sample"):
        if k in out:
            if out[k]["unexplained"]:
                blockers.append(f"{k}: unexplained {out[k]['unexplained']}")
            if out[k]["abstain_to_4"]:
                blockers.append(f"{k}: abstain->4 {out[k]['abstain_to_4']}")
    if out["drift"]["differences"]:
        blockers.append(f"drift: {len(out['drift']['differences'])} existing term(s) changed")
    bad = [n for n, v in out["negative_controls"].items() if v["read_as_staged_term"] or v["group_after"] not in (None, v["group_before"])]
    if bad:
        blockers.append(f"negative controls recognised or newly placed: {bad}")
    out["blockers"], out["verdict"] = blockers, "BLOCKED" if blockers else "READY_FOR_REVIEW"
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "class_gate.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("verdict", out["verdict"], blockers)
    for k in ("frozen_66", "out_of_sample"):
        if k in out:
            print(k, "changed", len(out[k]["changed"]), "unexplained", out[k]["unexplained"], "abstain->4", out[k]["abstain_to_4"], "abstain->1", out[k]["abstain_to_1"], "other", out[k]["other_group_change"])
    print("drift", out["drift"]["probed"], out["drift"]["differences"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
