"""Marker batch gate (CLASSIFICATION-BEARING): rows for src/foodscan/resources/markers.csv from data/ingest/marker_rows_*.json.

Checks: both FAO quotes verbatim in the report text; schema and class/strength vocabulary; no duplicate marker term; then the BEFORE build (repo src) and the AFTER build (a temp copy with the
rows appended) are run in separate fresh processes over the 66 frozen inputs and, when given, an out-of-sample cache directory. EVERY input whose group, status, reason or drivers changed is
listed and attributed to a specific marker row + clause (a new driver that names a staged term); a change with no such driver is UNEXPLAINED and blocks the gate. Group changes that are not
abstain -> 4 are reported separately. Merges nothing. Exit: 0 ran; 1 error; 2 refused; 3 BLOCKED with --strict.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import oos_eval  # noqa: E402
import validate_batch as vb  # noqa: E402

CLASSES = {"derived_substance"}
STRENGTHS = {"strong"}


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"-\s+", "-", s)).strip()


def source_for(spec: dict, row: dict) -> str:
    c, b = spec["clause"], spec["basis"]
    return (f"PROVISIONAL: {c['where']} \"{c['text']}\"; classification basis {b['where']} \"{b['text']}\"; {row['coverage']}")


def append_markers(path: Path, rows: list[dict]) -> None:
    data = path.read_bytes()
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    for r in rows:
        w.writerow([r["term"], r["marker_class"], r["strength"], r["source"]])
    with path.open("ab") as fh:
        if data and not data.endswith(b"\n"):
            fh.write(b"\n")
        fh.write(buf.getvalue().encode("utf-8"))


def attribute_changes(before: dict, after: dict, rows: list[dict]) -> dict:
    terms = [r["term"] for r in rows]
    listed, unexplained, other_group = [], [], []
    for k in before:
        b, a = before[k], after[k]
        ch = [f for f in ("group", "status", "reason", "drivers") if b[f] != a[f]]
        if not ch:
            continue
        new = [d for d in a["drivers"] if d not in b["drivers"]]
        hit = sorted({t for t in terms for d in new if t in d.lower()})
        entry = {"input": k, "changed": ch, "group": [b["group"], a["group"]], "status": [b["status"], a["status"]], "new_drivers": new, "markers": hit}
        listed.append(entry)
        if not hit:
            unexplained.append(k)
        if b["group"] != a["group"] and b["group"] is not None:
            other_group.append(k)
    return {"changed": listed, "unexplained": unexplained, "group_changes_not_from_abstain": other_group}


def run(spec: dict, fao_text: Path, repo_src: Path, evaluation: Path, work: Path, oos_cache: Path | None) -> dict:
    res = repo_src / "foodscan" / "resources"
    errors = []
    text = norm(fao_text.read_text(encoding="utf-8"))
    for key in ("clause", "basis"):
        if norm(spec[key]["text"]) not in text:
            errors.append(f"{key} quote not found verbatim in the FAO text")
    existing = {vb.flat(r["term"]) for r in vb.read_csv(res / "markers.csv")}
    rows = []
    for r in spec["rows"]:
        row = {"term": r["term"], "marker_class": spec["marker_class"], "strength": spec["strength"], "coverage": r["coverage"]}
        row["source"] = source_for(spec, r)
        if row["marker_class"] not in CLASSES or row["strength"] not in STRENGTHS:
            errors.append(f"{r['term']}: class or strength outside the approved vocabulary")
        if not re.fullmatch(r"[a-z][a-z \-]*[a-z]", r["term"]):
            errors.append(f"{r['term']}: not a clean lowercase term")
        if vb.flat(r["term"]) in existing:
            errors.append(f"{r['term']}: already a marker row")
        rows.append(row)
    out = {"batch_id": spec["batch_id"], "rows": rows, "errors": errors}
    if errors:
        out.update(verdict="BLOCKED")
        return out
    b_src, a_src = work / "b" / "src", work / "a" / "src"
    for d in (b_src, a_src):
        shutil.copytree(repo_src, d, ignore=shutil.ignore_patterns("__pycache__", "*.egg-info"))
    append_markers(a_src / "foodscan" / "resources" / "markers.csv", rows)
    sets = {"frozen_66": None}
    results = {}
    for name in sets:
        bf, af = work / f"{name}_b.json", work / f"{name}_a.json"
        vb.run_dump(b_src, evaluation, bf)
        vb.run_dump(a_src, evaluation, af)
        results[name] = attribute_changes(json.loads(bf.read_text()), json.loads(af.read_text()), rows)
    if oos_cache and (oos_cache / "inputs").exists():
        bf, af = work / "oos_b.json", work / "oos_a.json"
        oos_eval.dump(b_src, oos_cache / "inputs", bf)
        oos_eval.dump(a_src, oos_cache / "inputs", af)
        results["out_of_sample_32"] = attribute_changes(json.loads(bf.read_text()), json.loads(af.read_text()), rows)
    for name, r in results.items():
        if r["unexplained"]:
            errors.append(f"{name}: unexplained change(s): {r['unexplained']}")
    out.update(results=results, verdict="BLOCKED" if errors else "READY_FOR_REVIEW", errors=errors)
    return out


def write(g: dict, spec: dict, out: Path, force: bool) -> None:
    names = ("gate_report.md", "gate_report.json", "markers_candidate_rows.csv")
    if any((out / n).exists() for n in names) and not force:
        raise FileExistsError(str(out))
    out.mkdir(parents=True, exist_ok=True)
    with (out / "markers_candidate_rows.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["term", "marker_class", "strength", "source"])
        for r in g["rows"]:
            w.writerow([r["term"], r["marker_class"], r["strength"], r["source"]])
    (out / "gate_report.json").write_text(json.dumps(g, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    L = [f"# Gate report: {g['batch_id']} (CLASSIFICATION-BEARING markers)", "", f"**Verdict: {g['verdict']}**" + (": " + "; ".join(g["errors"]) if g["errors"] else ""), "",
         "Nothing was merged. Clause (p. 9) and classification basis (p. 10) are quoted verbatim in every row's source.", "", "## Rows", ""]
    L += [f"- `{r['term']}` ({r['marker_class']}, {r['strength']}): {r['coverage']}" for r in g["rows"]]
    for name, r in g.get("results", {}).items():
        L += ["", f"## {name}: every changed input", ""]
        L += [f"- `{c['input']}`: group {c['group'][0]} -> {c['group'][1]}, status {c['status'][0]} -> {c['status'][1]}, changed {c['changed']}; marker(s) {c['markers'] or 'UNEXPLAINED'}; new drivers {c['new_drivers']}" for c in r["changed"]] or ["- none"]
        L += [f"- unexplained: {r['unexplained'] or 'none'}; group changes not from abstain: {r['group_changes_not_from_abstain'] or 'none'}"]
    (out / "gate_report.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rows", type=Path, default=ROOT / "data" / "ingest" / "marker_rows_1.json")
    ap.add_argument("--fao-text", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--oos-cache", type=Path, default=ROOT / "data" / "cache" / "oos_herb_spice_1")
    ap.add_argument("--src", type=Path, default=ROOT / "src")
    ap.add_argument("--evaluation", type=Path, default=ROOT / "evaluation")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args(argv)
    try:
        spec = json.loads(a.rows.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as td:
            g = run(spec, a.fao_text, a.src, a.evaluation, Path(td), a.oos_cache)
            write(g, spec, a.out, a.force)
        print(f"verdict {g['verdict']}; errors {g['errors']}")
        return 3 if (a.strict and g["errors"]) else 0
    except FileExistsError as e:
        sys.stderr.write(f"Refusing to overwrite: {e}\n")
        return 2
    except Exception as e:   # noqa: BLE001
        sys.stderr.write(f"Error: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
