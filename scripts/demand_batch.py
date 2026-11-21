"""Demand-driven batch (workstream B): one decision per open demand term (data/ingest/demand_decisions_*.json) -> staged rows, a gate, and a reviewable report.

Dispositions: ACCEPT_ROW (a PROVISIONAL lexicon row: verbatim FAO clause + named/not-named statement + optional FDC provenance), ACCEPT_SYNONYM, LABEL_BOUND (conditioned clause: never staged),
MARKER_PROPOSAL (a marker row is classification-bearing: proposed for owner decision, never staged), PARK (one-line reason). Commodity datasets supply names only, never a group.
Gate: coverage (every open inventory term has exactly one decision), the FAO clause verbatim in Table 1, FDC ids and verbatim descriptions, schema, duplicates, 66-input flip check in two
fresh processes (validate_batch.flip_check), drift of existing terms. Merges nothing. Exit: 0 ran; 1 error; 2 refused (output exists); 3 BLOCKED with --strict.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import validate_batch as vb  # noqa: E402

KINDS = vb.KINDS


def fao_table_text(fao_text: str) -> str:
    """Right-hand EXAMPLES column of FAO Table 1 across both pages (Group 1 and Group 2 sit before the 'Cont.' header, Groups 3 and 4 after it)."""
    lines = fao_text.splitlines()
    start = next(i for i, ln in enumerate(lines) if "TABLE 1. THE NOVA" in ln)
    end = next(i for i in range(start + 1, len(lines)) if "Adapted from Monteiro" in lines[i])
    col, right = None, []
    for ln in lines[start:end]:
        if "EXAMPLES" in ln:
            col = ln.index("EXAMPLES")
        if col is not None and len(ln) > col:
            right.append(ln[col:].strip())
    return re.sub(r"\s+", " ", " ".join(right))


def standing_exclusions() -> set[str]:
    """Every string literal in tests/test_lexicon_1.py::test_explicit_exclusions_and_blocked_items_did_not_get_rows: the lexicon-1 senior review's explicit exclusions."""
    import ast
    tree = ast.parse((ROOT / "tests" / "test_lexicon_1.py").read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "test_explicit_exclusions_and_blocked_items_did_not_get_rows")
    return {n.value.lower() for n in ast.walk(fn) if isinstance(n, ast.Constant) and isinstance(n.value, str)}


def source_row(d: dict, candidates: dict, batch_id: str = "demand-decisions-1") -> str:
    fdc = "; ".join(f"{candidates[i]['dataset']} FDC id {candidates[i]['fdc_id']} \"{candidates[i]['description']}\"" for i in d["fdc"])
    return (f"PROVISIONAL: {d['group_label']} \"{d['clause']}\"; {d['named']}" + (f"; {d['corroboration']}" if d.get("corroboration") else "") + (f"; name from USDA FoodData Central (CC0 1.0): {fdc}" if fdc else "")
            + f"; demand-driven row ({batch_id})")


def run(dec: dict, inventory: Path, candidates_csv: Path, fao_text: Path, repo_src: Path, evaluation: Path, work: Path, extra_texts: dict | None = None) -> dict:
    sys.path.insert(0, str(repo_src))
    from foodscan.classify import is_recognised
    from foodscan.normalise import normalise_ingredient
    res = repo_src / "foodscan" / "resources"
    inv = [r for r in vb.read_csv(inventory) if r["noise"] == "False" and r["photo_only"] == "False" and r["recognised_now"] == "False"]
    cands = {r["candidate_id"]: r for r in vb.read_csv(candidates_csv)}
    lex = {vb.flat(r["term"]): r for r in vb.read_csv(res / "lexicon.csv")}
    syn = {vb.flat(r["from"]): r for r in vb.read_csv(res / "synonyms.csv")}
    raw = fao_text.read_text(encoding="utf-8")
    table = fao_table_text(raw)
    prose = re.sub(r"\s+", " ", raw)           # single-column prose passages (e.g. the Group 1 definition on p.10) are checked here
    errors, decisions = [], dec["decisions"]
    terms = [r["term"] for r in inv]
    got = Counter(d["term"] for d in decisions)
    errors += [f"inventory term without a decision: {t}" for t in terms if t not in got]
    errors += [f"decision for a term not in the open inventory: {t}" for t in got if t not in terms]
    errors += [f"term decided twice: {t}" for t, n in got.items() if n > 1]
    rows, syns = [], []
    held = standing_exclusions()
    for d in decisions:
        if d["disposition"] in ("ACCEPT_ROW", "ACCEPT_SYNONYM") and {d["term"].lower(), d.get("row_term", "").lower()} & held and not d.get("owner_override"):
            errors.append(f"{d['term']}: is a standing exclusion of the lexicon-1 senior review; it may not be staged without an owner decision")
        if d["disposition"] in ("ACCEPT_ROW", "ACCEPT_SYNONYM"):
            src_name = d.get("clause_source")
            if src_name:
                doc = (extra_texts or {}).get(src_name)
                if doc is None or re.sub(r"\s+", " ", d["clause"]) not in doc:
                    errors.append(f"{d['term']}: clause not found verbatim in {src_name}")
                if len(d["clause"].split()) > 40:
                    errors.append(f"{d['term']}: clause longer than 40 words (quote only the single clause relied on)")
            elif re.sub(r"\s+", " ", d["clause"]) not in table and re.sub(r"\s+", " ", d["clause"]) not in prose:
                errors.append(f"{d['term']}: clause not found verbatim in the FAO text")
            for i in d["fdc"]:
                if i not in cands:
                    errors.append(f"{d['term']}: {i} not in the FDC candidates")
        if d["disposition"] == "ACCEPT_ROW":
            term = d.get("row_term", d["term"])
            r = {"term": term, "kind": d["kind"], "source": source_row(d, cands, dec['decisions_id']), "demand_term": d["term"]}
            if d["kind"] not in KINDS:
                errors.append(f"{term}: kind {d['kind']!r} invalid")
            if not r["source"].startswith("PROVISIONAL") or d["clause"] not in r["source"]:
                errors.append(f"{term}: source is not PROVISIONAL with the verbatim clause")
            if vb.flat(term) in lex or vb.flat(term) in syn or is_recognised(normalise_ingredient(term).name):
                errors.append(f"{term}: already covered by this build")
            rows.append(r)
        elif d["disposition"] == "ACCEPT_SYNONYM":
            if vb.flat(d["to"]) not in lex:
                errors.append(f"{d['term']} -> {d['to']}: target is not an existing lexicon row")
            if vb.flat(d["term"]) in lex or vb.flat(d["term"]) in syn:
                errors.append(f"{d['term']}: already a lexicon term or synonym")
            syns.append({"from": d["term"], "to": d["to"], "source": source_row(d, cands, dec['decisions_id'])})
        elif d["disposition"] in ("PARK", "LABEL_BOUND", "MARKER_PROPOSAL", "CONFLICT"):
            if not (d.get("reason") or "").strip():
                errors.append(f"{d['term']}: no one-line reason")
        else:
            errors.append(f"{d['term']}: unknown disposition {d['disposition']}")
    flip = {"skipped": "no rows"}
    if (rows or syns) and not errors:
        runs = vb.flip_check(rows, repo_src, evaluation, work, syns) if work.mkdir(exist_ok=True) is None else None
        desc = {r["word"].lower() for r in vb.read_csv(res / "descriptors.csv")}
        flip = vb.attribute(runs["before"], runs["after"], rows + [{"term": s["from"]} for s in syns], desc)
        flip["inputs"], flip["harness"] = len(runs["before"]), runs["harness"]
        if flip["flips"]:
            errors.append(f"flip: {len(flip['flips'])} input(s) changed group, status or drivers: {flip['flips']}")
        if flip["unexplained"]:
            errors.append(f"unexplained changes: {flip['unexplained']}")
    by_inputs = Counter()
    for d in decisions:
        by_inputs[d["disposition"]] += d["paste_inputs"]
    return {"decisions_id": dec["decisions_id"], "n_terms": len(terms), "by_disposition": dict(Counter(d["disposition"] for d in decisions)), "paste_inputs_by_disposition": dict(by_inputs),
            "rows": rows, "synonyms": syns, "decisions": decisions, "flip": flip, "errors": errors, "verdict": "BLOCKED" if errors else "READY_FOR_REVIEW"}


def write(g: dict, out: Path, force: bool) -> None:
    names = ("decisions_report.csv", "lexicon_candidate_rows.csv", "synonyms_candidate_rows.csv", "marker_proposals.csv", "ambiguity_queue.csv", "gate_report.md", "gate_report.json")
    if any((out / n).exists() for n in names) and not force:
        raise FileExistsError(str(out))
    out.mkdir(parents=True, exist_ok=True)
    def w(name, header, rows):
        with (out / name).open("w", newline="", encoding="utf-8") as fh:
            c = csv.writer(fh, lineterminator="\n")
            c.writerow(header)
            c.writerows(rows)
    D = g["decisions"]
    w("decisions_report.csv", ["rank", "term", "paste_inputs", "disposition", "code_or_kind", "reason_or_clause"],
      [[d["rank"], d["term"], d["paste_inputs"], d["disposition"], d.get("code") or d.get("kind", ""), d.get("reason") or d.get("clause", "")] for d in D])
    w("lexicon_candidate_rows.csv", ["term", "kind", "source"], [[r["term"], r["kind"], r["source"]] for r in g["rows"]])
    w("synonyms_candidate_rows.csv", ["from", "to", "source"], [[s["from"], s["to"], s["source"]] for s in g["synonyms"]])
    w("marker_proposals.csv", ["rank", "term", "paste_inputs", "fao_term_named", "why"], [[d["rank"], d["term"], d["paste_inputs"], d["clause"], d["reason"]] for d in D if d["disposition"] == "MARKER_PROPOSAL"])
    w("ambiguity_queue.csv", ["rank", "term", "paste_inputs", "disposition", "code", "reason"], [[d["rank"], d["term"], d["paste_inputs"], d["disposition"], d["code"], d["reason"]] for d in D if d["disposition"] in ("PARK", "LABEL_BOUND", "CONFLICT")])
    (out / "gate_report.json").write_text(json.dumps({k: v for k, v in g.items() if k not in ("decisions",)}, indent=1, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    f = g["flip"]
    L = [f"# Gate report: {g['decisions_id']}", "", f"**Verdict: {g['verdict']}**" + (": " + "; ".join(g["errors"]) if g["errors"] else ""), "", "Nothing was merged.", "",
         "| Check | Result |", "|---|---|", f"| open demand terms decided | {g['n_terms']} |", f"| by disposition | {g['by_disposition']} |",
         f"| paste-input mentions by disposition (a term can occur in several inputs) | {g['paste_inputs_by_disposition']} |", f"| candidate lexicon rows | {len(g['rows'])} |", f"| candidate synonyms | {len(g['synonyms'])} |"]
    if "changed_counts" in f:
        L += [f"| flip check ({f['inputs']} frozen inputs, separate fresh processes) | " + ", ".join(f"{k} {v}" for k, v in f["changed_counts"].items()) + " |",
              f"| harness proof | lexicon rows {f['harness'].get('lexicon_rows_before')} -> {f['harness'].get('lexicon_rows_after')}; synonym rows {f['harness'].get('synonym_rows_added')}; all {f['harness'].get('terms_recognised_after')} terms recognised after |"]
    L += ["", "## Candidate rows", ""] + [f"- `{r['term']}` ({r['kind']}) for demand term `{r['demand_term']}`" for r in g["rows"]] + [f"- synonym `{s['from']}` -> `{s['to']}`" for s in g["synonyms"]]
    for disp, title in (("MARKER_PROPOSAL", "Marker proposals (classification-bearing: owner decision, not staged)"), ("CONFLICT", "CONFLICT between authoritative sources (flagged, not parked, not staged)"), ("LABEL_BOUND", "Label-bound (conditioned clause, never staged)"), ("PARK", "Parked")):
        L += ["", f"## {title}", ""] + [f"- #{d['rank']} `{d['term']}` ({d['paste_inputs']} inputs): {d.get('code', '')}: {d['reason']}" for d in D if d["disposition"] == disp]
    (out / "gate_report.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--decisions", type=Path, default=ROOT / "data" / "ingest" / "demand_decisions_1.json")
    ap.add_argument("--inventory", type=Path, default=ROOT / "evaluation" / "demand_inventory_1" / "inventory.csv")
    ap.add_argument("--candidates", type=Path, required=True, help="candidates.csv from scripts/fdc_ingest.py normalise")
    ap.add_argument("--fao-text", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--src", type=Path, default=ROOT / "src")
    ap.add_argument("--evaluation", type=Path, default=ROOT / "evaluation")
    ap.add_argument("--extra-text", action="append", default=[], help="NAME=path of a cached source text for clause_source checks (whitespace-normalised)")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args(argv)
    extra = {kv.split("=", 1)[0]: re.sub(r"\s+", " ", Path(kv.split("=", 1)[1]).read_text(encoding="utf-8", errors="ignore")) for kv in a.extra_text}
    try:
        with tempfile.TemporaryDirectory() as td:
            g = run(json.loads(a.decisions.read_text(encoding="utf-8")), a.inventory, a.candidates, a.fao_text, a.src, a.evaluation, Path(td), extra)
            write(g, a.out, a.force)
        print(f"verdict {g['verdict']}; {g['by_disposition']}; errors {g['errors']}")
        return 3 if (a.strict and g["errors"]) else 0
    except FileExistsError as e:
        sys.stderr.write(f"Refusing to overwrite: {e}\n")
        return 2
    except Exception as e:   # noqa: BLE001
        sys.stderr.write(f"Error: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
