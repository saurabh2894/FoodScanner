"""Gate for a batch of SYNONYM rows (data/ingest/plural_policy_*.json): plural, leaf-form and plural-spelling aliases of existing lexicon rows.

Checks: schema (from clean, to is an existing lexicon row, PROVISIONAL source), duplicates (from already a lexicon term, a synonym, or recognised), conflicts, SHADOWING AND DRIFT (the
normalised name of every existing lexicon term and synonym must be identical before and after: an alias must never rewrite an existing term), POSITIVES (every from becomes its `to`, was
not recognised before), NEGATIVE CONTROLS (policy.must_stay_unmapped: the same normalised name before and after, never mapped onto a base row), and the 66-input flip check in two
fresh processes (validate_batch.flip_check). Writes only into --out; merges nothing. Exit: 0 gate ran; 1 error; 2 refused (output exists); 3 BLOCKED with --strict.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import validate_batch as vb  # noqa: E402


def source_for(r: dict, policy_id: str = "plural-policy-1") -> str:
    named = f"; the plant part is named by USDA FoodData Central (CC0 1.0): {r['part_named_by']}" if r.get("part_named_by") else ""
    named_term = r.get("exact_named_by") or "exact term not named by any source read"
    return (f"PROVISIONAL: alias of existing lexicon row \"{r['to']}\" ({r['basis']}); {policy_id} rule {r['rule']}; {named_term}; "
            f"the row it points to carries the FAO clause and its own provenance{named}")


def probe(src: Path, terms: list[str], work: Path, tag: str) -> dict:
    tf, out = work / f"{tag}_terms.txt", work / f"{tag}_probe.json"
    tf.write_text("\n".join(terms) + "\n", encoding="utf-8")
    env = {"PYTHONPATH": str(src), "PATH": "/usr/bin:/bin:/usr/local/bin", "HOME": str(Path.home())}
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "synonym_probe.py"), str(tf), str(out)], capture_output=True, text=True, env=env, cwd=str(src.parent))
    if r.returncode or str(src) not in r.stderr:
        raise RuntimeError(f"probe failed or did not use {src}: {r.stderr[-300:]}")
    return json.loads(out.read_text(encoding="utf-8"))


def run_gate(policy: dict, repo_src: Path, evaluation: Path, work: Path) -> dict:
    res = repo_src / "foodscan" / "resources"
    lex = {vb.flat(r["term"]): r for r in vb.read_csv(res / "lexicon.csv")}
    syn = {vb.flat(r["from"]): r for r in vb.read_csv(res / "synonyms.csv")}
    rows = [{**r, "source": source_for(r, policy["policy_id"])} for r in policy["rows"]]
    errors, dropped = [], []
    froms = [r["from"] for r in rows]
    for r in rows:
        f = r["from"]
        if f != f.lower() or f != " ".join(f.split()) or not f.replace(" ", "").isalpha():
            errors.append(f"'{f}': not a clean lowercase alphabetic term")
        if vb.flat(r["to"]) not in lex:
            errors.append(f"'{f}' -> '{r['to']}': target is not an existing lexicon row")
        if f == r["to"]:
            errors.append(f"'{f}' maps to itself")
        if froms.count(f) > 1:
            errors.append(f"'{f}' listed twice")
        if vb.flat(r["to"]) in syn:
            errors.append(f"'{f}' -> '{r['to']}': the target is itself a synonym alias")
    keep = []
    for r in rows:
        k = vb.flat(r["from"])
        if k in lex or k in syn:
            dropped.append({"from": r["from"], "why": "already a lexicon term" if k in lex else "already a synonym"})
        else:
            keep.append(r)
    probe_terms = sorted({*(r["from"] for r in keep), *policy["must_stay_unmapped"], *policy.get("must_stay_unrecognised", []), *lex, *syn, *(r["from"] for r in vb.read_csv(res / "synonyms.csv")), *(r["to"] for r in vb.read_csv(res / "synonyms.csv"))})
    before_src, after_src = work / "pb" / "src", work / "pa" / "src"
    for d in (before_src, after_src):
        shutil.copytree(repo_src, d, ignore=shutil.ignore_patterns("__pycache__", "*.egg-info"))
    vb.append_synonyms(after_src / "foodscan" / "resources" / "synonyms.csv", keep)
    B, A = probe(before_src, probe_terms, work, "b"), probe(after_src, probe_terms, work, "a")
    already = [r["from"] for r in keep if B[r["from"]]["recognised"]]
    positives_bad = [r["from"] for r in keep if A[r["from"]]["name"] != vb.flat(r["to"]) or not A[r["from"]]["recognised"]]
    own = {r["from"] for r in keep}
    drift = [t for t in probe_terms if t not in own and t not in policy["must_stay_unmapped"] and t not in policy.get("must_stay_unrecognised", []) and B[t] != A[t]]
    neg_bad = [t for t in policy["must_stay_unmapped"] if B[t] != A[t]]
    proc_bad = [t for t in policy.get("must_stay_unrecognised", []) if A[t]["recognised"] or B[t]["recognised"]]
    for t in already:
        errors.append(f"'{t}' is already recognised before the batch (it would be a no-op)")
    if positives_bad:
        errors.append(f"positives not mapped to their target after the batch: {positives_bad}")
    if drift:
        errors.append(f"existing terms whose normalised name or recognition changed: {drift}")
    if proc_bad:
        errors.append(f"processed-form controls became recognised: {proc_bad}")
    if neg_bad:
        errors.append(f"negative controls changed: {neg_bad}")
    flip = {"skipped": "no rows"}
    if keep and any("target is not an existing lexicon row" in e or "listed twice" in e or "itself" in e for e in errors):
        flip = {"skipped": "invalid rows: the flip harness refuses a change its after-build cannot hold"}
    elif keep:
        runs = vb.flip_check([], repo_src, evaluation, work / "flip", keep) if (work / "flip").mkdir(exist_ok=True) is None else None
        descriptors = {r["word"].lower() for r in vb.read_csv(res / "descriptors.csv")}
        flip = vb.attribute(runs["before"], runs["after"], [{"term": r["from"]} for r in keep], descriptors)
        flip["inputs"], flip["harness"] = len(runs["before"]), runs["harness"]
        if flip["flips"]:
            errors.append(f"flip: {flip['flips']}")
        if flip["unexplained"]:
            errors.append(f"unexplained changes: {flip['unexplained']}")
    return {"policy_id": policy["policy_id"], "rows": keep, "dropped": dropped, "errors": errors, "probe_terms": len(probe_terms),
            "negative_controls": {t: {"before": B[t], "after": A[t]} for t in policy["must_stay_unmapped"] + policy.get("must_stay_unrecognised", [])}, "flip": flip,
            "verdict": "BLOCKED" if errors else "READY_FOR_REVIEW"}


def write(g: dict, out: Path, force: bool) -> None:
    import csv
    files = [out / n for n in ("gate_report.json", "gate_report.md", "synonyms_candidate_rows.csv")]
    if any(f.exists() for f in files) and not force:
        raise FileExistsError(str(out))
    out.mkdir(parents=True, exist_ok=True)
    with (out / "synonyms_candidate_rows.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["from", "to", "source"])
        for r in g["rows"]:
            w.writerow([r["from"], r["to"], r["source"]])
    (out / "gate_report.json").write_text(json.dumps({k: v for k, v in g.items()}, indent=1, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    f = g["flip"]
    L = [f"# Gate report: {g['policy_id']}", "", f"**Verdict: {g['verdict']}**" + (": " + "; ".join(g["errors"]) if g["errors"] else ""), "",
         "Nothing was merged. `synonyms_candidate_rows.csv` is in synonyms.csv layout.", "", "| Check | Result |", "|---|---|",
         f"| candidate synonyms | {len(g['rows'])} |", f"| dropped (already covered) | {len(g['dropped'])} |", f"| terms probed before/after for drift (all lexicon terms and synonyms) | {g['probe_terms']} |",
         f"| negative controls (identity, or unrecognised for processed forms) | {len(g['negative_controls'])} checked, {len([e for e in g['errors'] if 'control' in e])} failing |"]
    if "changed_counts" in f:
        L += [f"| flip check ({f['inputs']} frozen inputs, separate fresh processes) | " + ", ".join(f"{k} {v}" for k, v in f["changed_counts"].items()) + " |",
              f"| harness proof | synonym rows {f['harness'].get('synonym_rows_added')}; all {f['harness'].get('terms_recognised_after')} terms recognised after; {len(f['harness'].get('terms_recognised_before', []))} before |"]
    L += ["", "## Candidate synonyms", ""] + [f"- `{r['from']}` -> `{r['to']}` ({r['rule']})" for r in g["rows"]]
    L += ["", "## Dropped", ""] + [f"- `{d['from']}`: {d['why']}" for d in g["dropped"]]
    L += ["", "## Negative controls (must stay exactly as before the batch)", ""] + [f"- `{t}`: before {v['before']} / after {v['after']}" for t, v in g["negative_controls"].items()]
    (out / "gate_report.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--policy", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--src", type=Path, default=ROOT / "src")
    ap.add_argument("--evaluation", type=Path, default=ROOT / "evaluation")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args(argv)
    try:
        with tempfile.TemporaryDirectory() as td:
            g = run_gate(json.loads(a.policy.read_text(encoding="utf-8")), a.src, a.evaluation, Path(td))
            write(g, a.out, a.force)
        print(f"verdict {g['verdict']}; candidates {len(g['rows'])}, dropped {len(g['dropped'])}, errors {g['errors']}")
        return 3 if (a.strict and g["errors"]) else 0
    except FileExistsError as e:
        sys.stderr.write(f"Refusing to overwrite: {e}\n")
        return 2
    except Exception as e:   # noqa: BLE001
        sys.stderr.write(f"Error: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
