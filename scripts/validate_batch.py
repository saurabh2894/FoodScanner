"""WS4 validation gate: an automated checker for a staged batch of candidate lexicon rows. It decides nothing about NOVA and merges nothing.

Checks (each reported PASS / FAIL / NOTE):
  schema       required columns, kind in the lexicon's kinds, a clean lowercase term, source starts PROVISIONAL, source holds the rule's verbatim clause
  provenance   every row names FDC candidate ids; each id exists in candidates.csv; the source text repeats each id and its verbatim description
  duplicates   against lexicon.csv and synonyms.csv: exact term, synonym 'from', already recognised by this build; informational: variant of an existing term
  flip         the frozen paste inputs analysed BEFORE and AFTER in two fresh processes (never one: cached tables corrupt a baseline): every changed field is listed and attributed
               to the staged row that caused it; a changed group, status or driver list is a FLIP and BLOCKS the batch
  ambiguity    uncertain terms are PARKED in ambiguity_queue.csv instead of being included: WS3 QUEUE decisions, a term that collides with an existing row of another kind,
               a term equal to a NOVA marker term
  policy       --policy (data/ingest/variant_policy_1.json): a staged term that is the same ingredient, plant part and form as an existing row becomes a SYNONYM candidate (never a new
               lexicon row); a different part or species stays a separate row; a term on a conditioned-clause boundary is PARKED. A ready row that is a variant of an existing row and is
               neither mapped nor listed as separate BLOCKS the gate (the inconsistency this policy exists to remove).
  clause       the verbatim clause is checked against the FAO report text when --fao-text is given (else NOTE: not checked)
Ready rows = schema ok, provenance ok, not a duplicate, not parked. The gate writes only into --out and never touches src/foodscan/resources/ (the 'after' build is a temporary copy).
Exit codes: 0 gate ran (verdict in the report); 1 error; 2 refused (output exists without --force); 3 gate verdict BLOCKED (with --strict).
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import clause_tier  # noqa: E402

KINDS = {"whole_food", "culinary", "flour", "herb_spice", "neutral", "culture", "food_powder", "unplaced", "nut_seed"}
REQUIRED = ["term", "kind", "source", "fdc_ids", "rule_id"]
COMPARE = ["group", "drivers", "status", "reason", "warnings", "ingredients", "unassessed", "ins_mappings"]


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def flat(term: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[-–—_/]", " ", term.lower())).strip()


# ---------------------------------------------------------------- checks
def check_schema(staged: list[dict], rule: dict) -> dict[str, list[str]]:
    errs: dict[str, list[str]] = {}
    clause = rule["clause"]["text"]
    for r in staged:
        e = [f"missing column or value: {c}" for c in REQUIRED if not (r.get(c) or "").strip()]
        t = r.get("term") or ""
        if t and (t != t.lower() or t != re.sub(r"\s+", " ", t).strip() or not re.fullmatch(r"[a-z][a-z '&\-]*[a-z]", t)):
            e.append(f"term not clean lowercase text: {t!r}")
        if r.get("kind") not in KINDS:
            e.append(f"kind {r.get('kind')!r} is not one of {sorted(KINDS)}")
        s = r.get("source") or ""
        if not s.startswith("PROVISIONAL"):
            e.append("source does not start with PROVISIONAL")
        if clause not in s:
            e.append("source does not hold the verbatim clause")
        if e:
            errs.setdefault(t or "?", []).extend(e)          # two bad rows with the same term must not hide each other
    return errs


def check_provenance(staged: list[dict], candidates: dict[str, dict]) -> dict[str, list[str]]:
    errs: dict[str, list[str]] = {}
    for r in staged:
        e = []
        ids = [i for i in (r.get("fdc_ids") or "").split(";") if i]
        if not ids:
            e.append("no FDC candidate ids")
        for i in ids:
            c = candidates.get(i)
            if c is None:
                e.append(f"{i} not in candidates.csv")
                continue
            if f"FDC id {c['fdc_id']}" not in r["source"] or f"\"{c['description']}\"" not in r["source"]:
                e.append(f"source does not repeat {i} and its verbatim description")
        if e:
            errs.setdefault(r["term"], []).extend(e)
    return errs


def check_duplicates(staged: list[dict], lexicon: list[dict], synonyms: list[dict], recognised) -> dict[str, dict]:
    lex = {flat(r["term"]): r for r in lexicon}
    syn = {flat(r["from"]): r for r in synonyms}
    out: dict[str, dict] = {}
    for r in staged:
        t = flat(r["term"])
        info: dict = {}
        if t in lex:
            info["duplicate"] = f"exact lexicon term (kind {lex[t]['kind']})"
        elif t in syn:
            info["duplicate"] = f"synonyms.csv alias of '{syn[t]['to']}'"
        elif recognised(r["term"]):
            info["duplicate"] = "already recognised by this build (descriptors, plurals or synonyms)"
        variants = sorted(k for k in lex if k != t and (t.startswith(k + " ") or t.endswith(" " + k) or k.startswith(t + " ") or k.endswith(" " + t)))
        if variants:
            info["variant_of"] = variants
        if info:
            out[r["term"]] = info
    return out


def ambiguity(staged: list[dict], decisions: list[dict], lexicon: list[dict], markers: list[dict]) -> list[dict]:
    queue = [{"term": d.get("term") or d["description"], "source_row": d["candidate_id"], "origin": "clause_tier", "reason_code": d["reason_code"], "reason": d["reason"],
              "description": d["description"]} for d in decisions if d["decision"] == "QUEUE"]
    lex = {flat(r["term"]): r for r in lexicon}
    marker_terms = {flat(r["term"]) for r in markers}
    for r in staged:
        t = flat(r["term"])
        if t in lex and lex[t]["kind"] != r["kind"]:
            queue.append({"term": r["term"], "source_row": r["fdc_ids"], "origin": "gate", "reason_code": "kind_conflict",
                          "reason": f"existing lexicon row has kind {lex[t]['kind']}, staged row says {r['kind']}", "description": ""})
        if t in marker_terms:
            queue.append({"term": r["term"], "source_row": r["fdc_ids"], "origin": "gate", "reason_code": "equals_marker_term",
                          "reason": "the term equals a NOVA marker term in markers.csv: never added automatically", "description": ""})
    return queue


def load_policy(path: Path | None) -> dict:
    empty = {"policy_id": None, "synonyms": {}, "separate_rows": {}, "parked": {}}
    return json.loads(path.read_text(encoding="utf-8")) if path else empty


def apply_policy(staged: list[dict], dups: dict, policy: dict, lexicon: list[dict], synonyms: list[dict], candidates: dict[str, dict]) -> dict:
    """Variant policy. Returns synonym candidate rows (from,to,source), policy-parked queue rows, and policy errors (each one blocks the gate)."""
    errs: list[str] = []
    by_term = {r["term"]: r for r in staged}
    lex = {flat(r["term"]) for r in lexicon}
    syn = {flat(r["from"]) for r in synonyms}
    syn_rows, queue = [], []
    for term, m in policy.get("synonyms", {}).items():
        if term not in by_term:
            errs.append(f"policy synonym '{term}' is not a staged term")
            continue
        if flat(m["to"]) not in lex:
            errs.append(f"policy synonym '{term}' -> '{m['to']}': target is not an existing lexicon row")
        if flat(term) in lex or flat(term) in syn:
            errs.append(f"policy synonym '{term}' already exists in lexicon.csv or synonyms.csv")
            continue
        recs = [candidates[i] for i in by_term[term]["fdc_ids"].split(";") if i in candidates]
        prov = "; ".join(f"{c['dataset']} FDC id {c['fdc_id']} \"{c['description']}\"" for c in recs)
        syn_rows.append({"from": term, "to": m["to"], "source": f"PROVISIONAL: alias of existing lexicon row \"{m['to']}\" ({m['basis']}); {policy['policy_id']}; name from USDA FoodData Central (CC0 1.0): {prov}"})
    for term in policy.get("separate_rows", {}):
        if term not in by_term:
            errs.append(f"policy separate row '{term}' is not a staged term")
    for term, m in policy.get("parked", {}).items():
        if term not in by_term:
            errs.append(f"policy parked term '{term}' is not a staged term")
            continue
        queue.append({"term": term, "source_row": by_term[term]["fdc_ids"], "origin": "policy", "reason_code": m["reason_code"], "reason": m["reason"], "description": ""})
    groups = [set(policy.get("synonyms", {})), set(policy.get("separate_rows", {})), set(policy.get("parked", {}))]
    for i in range(3):
        for j in range(i + 1, 3):
            for t in groups[i] & groups[j]:
                errs.append(f"policy lists '{t}' in two different dispositions")
    covered = set().union(*groups)
    for t, info in dups.items():
        if "variant_of" in info and "duplicate" not in info and t not in covered:
            errs.append(f"'{t}' is a variant of {info['variant_of']} but the policy neither maps it to a synonym nor keeps it as a separate row")
    return {"synonym_rows": syn_rows, "queue": queue, "errors": errs}


# ---------------------------------------------------------------- flip harness (two fresh processes)
def append_rows(lexicon_csv: Path, rows: list[dict]) -> None:
    data = lexicon_csv.read_bytes()
    with lexicon_csv.open("ab") as fh:
        if data and not data.endswith(b"\n"):
            fh.write(b"\n")
    import io
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    for r in rows:
        w.writerow([r["term"], r["kind"], r["source"]])
    with lexicon_csv.open("ab") as fh:
        fh.write(buf.getvalue().encode("utf-8"))


def append_synonyms(synonyms_csv: Path, rows: list[dict]) -> None:
    import io
    data = synonyms_csv.read_bytes()
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    for r in rows:
        w.writerow([r["from"], r["to"], r["source"]])
    with synonyms_csv.open("ab") as fh:
        if data and not data.endswith(b"\n"):
            fh.write(b"\n")
        fh.write(buf.getvalue().encode("utf-8"))


def run_dump(src_dir: Path, evaluation: Path, out: Path, probe_file: Path | None = None) -> None:
    env = {"PYTHONPATH": str(src_dir), "PATH": "/usr/bin:/bin:/usr/local/bin", "HOME": str(Path.home())}
    cmd = [sys.executable, str(ROOT / "scripts" / "flip_dump.py"), "--evaluation", str(evaluation), "--out", str(out)] + (["--probe-file", str(probe_file)] if probe_file else [])
    r = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=str(src_dir.parent))
    if r.returncode or str(src_dir) not in r.stderr:
        raise RuntimeError(f"flip dump failed or did not use {src_dir}: {r.stderr[-400:]}")


def flip_check(rows: list[dict], repo_src: Path, evaluation: Path, work: Path, syn_rows: list[dict] | None = None) -> dict:
    """before = a copy of the repo src as it is; after = the same copy with the rows appended to lexicon.csv. Each is analysed in its OWN fresh process."""
    before_src, after_src = work / "before" / "src", work / "after" / "src"
    for d in (before_src, after_src):
        shutil.copytree(repo_src, d, ignore=shutil.ignore_patterns("__pycache__", "*.egg-info"))
    syn_rows = syn_rows or []
    append_rows(after_src / "foodscan" / "resources" / "lexicon.csv", rows)
    if syn_rows:
        append_synonyms(after_src / "foodscan" / "resources" / "synonyms.csv", syn_rows)
    b, a = work / "before.json", work / "after.json"
    probe = work / "probe.txt"
    probe.write_text("\n".join([r["term"] for r in rows] + [r["from"] for r in syn_rows]) + "\n", encoding="utf-8")
    run_dump(before_src, evaluation, b, probe)
    run_dump(after_src, evaluation, a, probe)
    pb = json.loads((work / "before.json.probe.json").read_text(encoding="utf-8"))
    pa = json.loads((work / "after.json.probe.json").read_text(encoding="utf-8"))
    already = [t for t, v in pb.items() if v]
    missing = [t for t, v in pa.items() if not v]
    if missing:                                    # the exact failure that once invalidated a flip check: an 'after' that does not hold the change
        raise RuntimeError(f"harness invalid: the AFTER build does not recognise staged term(s) {missing}")
    n = lambda d: len(read_csv(d / "foodscan" / "resources" / "lexicon.csv"))
    return {"before": json.loads(b.read_text(encoding="utf-8")), "after": json.loads(a.read_text(encoding="utf-8")),
            "harness": {"lexicon_rows_before": n(before_src), "lexicon_rows_after": n(after_src),
                                                           "synonym_rows_added": len(syn_rows), "terms_recognised_before": already, "terms_recognised_after": len(pa)}}


def _singular(tok: str) -> str:
    if len(tok) > 3 and tok.endswith("ies"):
        return tok[:-3] + "y"
    if len(tok) > 4 and tok.endswith("oes"):
        return tok[:-2]
    if len(tok) > 3 and tok.endswith("s") and not re.search(r"(ss|us|is)$", tok):
        return tok[:-1]
    return tok


def cores(item: str, descriptors: set[str]) -> set[str]:
    """The forms an unassessed item can be recognised as: as written, and with descriptor words removed and plurals singularised ('Pasteurized Cow Milk' -> 'cow milk')."""
    base = flat(re.sub(r"\s*\([^)]*\)", "", item))
    toks = base.split()
    kept = [t for t in toks if t not in descriptors]
    return {base, " ".join(kept), " ".join(_singular(t) for t in kept)}


def attribute(before: dict, after: dict, rows: list[dict], descriptors: set[str] | None = None) -> dict:
    descriptors = descriptors or set()
    terms: dict[str, str] = {}                            # every form a staged term can take (as written, singularised) -> the staged term itself
    for r in rows:
        t = flat(r["term"])
        terms[t] = r["term"]
        terms[" ".join(_singular(x) for x in t.split())] = r["term"]
    changed = {f: [k for k in before if before[k][f] != after[k][f]] for f in COMPARE}
    drops, unexplained = {}, []
    for k in changed["unassessed"]:
        gone = [x for x in before[k]["unassessed"] if x not in after[k]["unassessed"]]
        new = [x for x in after[k]["unassessed"] if x not in before[k]["unassessed"]]
        hit = {x: sorted({terms[c] for c in cores(x, descriptors) if c in terms}) for x in gone}
        drops[k] = {"recognised_now": gone, "attributed_to_rows": sorted({t for v in hit.values() for t in v}), "newly_unassessed": new}
        if new or any(not v for v in hit.values()):
            unexplained.append(k)
    blocking = sorted(set(changed["group"]) | set(changed["status"]) | set(changed["drivers"]))
    return {"changed_counts": {f: len(v) for f, v in changed.items()}, "changed_inputs": changed, "unassessed_attribution": drops, "unexplained": unexplained,
            "flips": blocking, "group_flips": {k: [before[k]["group"], after[k]["group"]] for k in changed["group"]}}


# ---------------------------------------------------------------- the gate
def run_gate(staged_csv: Path, decisions_csv: Path, candidates_csv: Path, rule: dict, repo_src: Path, evaluation: Path, work: Path, fao_text: Path | None, policy: dict | None = None) -> dict:
    sys.path.insert(0, str(repo_src))
    from foodscan.classify import is_recognised
    from foodscan.normalise import normalise_ingredient
    res = repo_src / "foodscan" / "resources"
    staged, decisions = read_csv(staged_csv), read_csv(decisions_csv)
    candidates = {r["candidate_id"]: r for r in read_csv(candidates_csv)}
    lexicon, synonyms, markers = read_csv(res / "lexicon.csv"), read_csv(res / "synonyms.csv"), read_csv(res / "markers.csv")
    schema_err, prov_err = check_schema(staged, rule), check_provenance(staged, candidates)
    dups = check_duplicates(staged, lexicon, synonyms, lambda t: is_recognised(normalise_ingredient(t).name))
    queue = ambiguity(staged, decisions, lexicon, markers)
    policy = policy or load_policy(None)
    pol = apply_policy(staged, dups, policy, lexicon, synonyms, candidates)
    queue += pol["queue"]
    parked = {q["term"] for q in queue if q["origin"] in ("gate", "policy")}
    duplicate_terms = {t for t, i in dups.items() if "duplicate" in i}
    syn_terms = {r["from"] for r in pol["synonym_rows"]}
    ready = [r for r in staged if r["term"] not in schema_err and r["term"] not in prov_err and r["term"] not in duplicate_terms and r["term"] not in parked and r["term"] not in syn_terms]
    flip = {"skipped": "no ready rows"}
    if ready or pol["synonym_rows"]:
        runs = flip_check(ready, repo_src, evaluation, work, pol["synonym_rows"])
        descriptors = {r["word"].lower() for r in read_csv(res / "descriptors.csv")}
        flip = attribute(runs["before"], runs["after"], ready + [{"term": r["from"]} for r in pol["synonym_rows"]], descriptors)
        flip["inputs"] = len(runs["before"])
        flip["harness"] = runs["harness"]
        flip["_runs"] = runs
    clause_state = "NOT CHECKED (no --fao-text)"
    if fao_text:
        clause_state = "PASS" if clause_tier.fao_clause_present(fao_text.read_text(encoding="utf-8"), rule["clause"]["text"]) else "FAIL"
    blockers = [f"policy: {e}" for e in pol["errors"]]
    if schema_err:
        blockers.append(f"schema errors on {len(schema_err)} row(s)")
    if prov_err:
        blockers.append(f"provenance errors on {len(prov_err)} row(s)")
    if flip.get("flips"):
        blockers.append(f"flip: {len(flip['flips'])} input(s) changed group, status or drivers")
    if flip.get("unexplained"):
        blockers.append(f"{len(flip['unexplained'])} input(s) changed in a way no ready row explains")
    if clause_state == "FAIL":
        blockers.append("verbatim clause not found in the FAO text")
    return {"rule_id": rule["rule_id"], "staged": len(staged), "ready": [r["term"] for r in ready], "ready_rows": ready, "duplicates": dups, "synonym_rows": pol["synonym_rows"], "separate_rows": {t: w for t, w in policy.get("separate_rows", {}).items() if t in {r["term"] for r in ready}},
            "policy_id": policy.get("policy_id"), "policy_errors": pol["errors"], "schema_errors": schema_err,
            "provenance_errors": prov_err, "ambiguity_queue": queue, "flip": flip, "clause_check": clause_state, "blockers": blockers, "verdict": "BLOCKED" if blockers else "READY_FOR_REVIEW"}


def write_report(g: dict, out: Path, force: bool) -> None:
    targets = [out / n for n in ("gate_report.json", "gate_report.md", "ambiguity_queue.csv", "lexicon_candidate_rows.csv", "synonyms_candidate_rows.csv", "flip_before.json", "flip_after.json")]
    if any(t.exists() for t in targets) and not force:
        raise FileExistsError(f"{out} already holds gate output; use --force to overwrite")
    out.mkdir(parents=True, exist_ok=True)
    runs = g["flip"].pop("_runs", None)
    if runs:
        (out / "flip_before.json").write_text(json.dumps(runs["before"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (out / "flip_after.json").write_text(json.dumps(runs["after"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (out / "ambiguity_queue.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["term", "source_row", "origin", "reason_code", "reason", "description"], lineterminator="\n")
        w.writeheader()
        w.writerows(g["ambiguity_queue"])
    with (out / "lexicon_candidate_rows.csv").open("w", newline="", encoding="utf-8") as fh:        # lexicon.csv column layout; NOT merged
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["term", "kind", "source"])
        for r in g["ready_rows"]:
            w.writerow([r["term"], r["kind"], r["source"]])
    with (out / "synonyms_candidate_rows.csv").open("w", newline="", encoding="utf-8") as fh:      # synonyms.csv column layout; NOT merged
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["from", "to", "source"])
        for r in g["synonym_rows"]:
            w.writerow([r["from"], r["to"], r["source"]])
    slim = {k: v for k, v in g.items() if k != "ready_rows"}
    (out / "gate_report.json").write_text(json.dumps(slim, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    f = g["flip"]
    L = [f"# Gate report: {g['rule_id']}", "", f"**Verdict: {g['verdict']}**" + (": " + "; ".join(g["blockers"]) if g["blockers"] else ""), "",
         "Nothing was merged. `lexicon_candidate_rows.csv` holds the ready rows in lexicon.csv layout and `synonyms_candidate_rows.csv` the synonym candidates in synonyms.csv layout, for review.", "",
         "| Check | Result |", "|---|---|",
         f"| staged rows | {g['staged']} |", f"| schema errors | {len(g['schema_errors'])} |", f"| provenance errors | {len(g['provenance_errors'])} |",
         f"| duplicates (exact, synonym, already recognised) | {sum('duplicate' in i for i in g['duplicates'].values())} |",
         f"| variants of an existing term (informational) | {sum('variant_of' in i for i in g['duplicates'].values())} |",
         f"| parked in the ambiguity queue | {len(g['ambiguity_queue'])} ({Counter(q['origin'] for q in g['ambiguity_queue'])}) |",
         f"| ready rows (new lexicon rows) | {len(g['ready'])} |", f"| synonym candidates (variant policy {g['policy_id']}) | {len(g['synonym_rows'])} |", f"| policy errors | {len(g['policy_errors'])} |", f"| verbatim clause vs FAO text | {g['clause_check']} |"]
    if "changed_counts" in f:
        h = f.get("harness", {})
        L += [f"| harness proof (separate processes) | lexicon rows {h.get('lexicon_rows_before')} -> {h.get('lexicon_rows_after')}; all {h.get('terms_recognised_after')} staged terms recognised after; "
              f"{len(h.get('terms_recognised_before', []))} already recognised before |",
              f"| flip check ({f['inputs']} frozen inputs, before and after in separate fresh processes) | " + ", ".join(f"{k} {v}" for k, v in f["changed_counts"].items()) + " |",
              f"| group/status/driver flips | {len(f['flips'])} {f['flips'] or ''} |", f"| unexplained changes | {len(f['unexplained'])} |"]
    L += ["", "## Ready rows (new lexicon rows)", ""] + [f"- `{t}`" + (f": separate row because {g['separate_rows'][t]}" if t in g["separate_rows"] else "") for t in g["ready"]]
    L += ["", "## Synonym candidates (variant policy: same ingredient, plant part and form)", ""] + [f"- `{r['from']}` -> `{r['to']}`" for r in g["synonym_rows"]]
    dup = [(t, i) for t, i in g["duplicates"].items() if "duplicate" in i]
    L += ["", "## Duplicates (excluded: already covered)", ""] + [f"- `{t}`: {i['duplicate']}" for t, i in dup]
    var = [(t, i) for t, i in g["duplicates"].items() if "variant_of" in i and "duplicate" not in i]
    L += ["", "## Variants of existing terms (kept; informational)", ""] + [f"- `{t}` ~ {i['variant_of']}" for t, i in var]
    L += ["", "## Ambiguity queue (parked, never included)", ""] + [f"- `{q['term']}` ({q['origin']}, {q['reason_code']}): {q['reason']}" for q in g["ambiguity_queue"]]
    if "unassessed_attribution" in f:
        L += ["", "## Unassessed drops attributed to ready rows", ""]
        for k, v in f["unassessed_attribution"].items():
            L.append(f"- {k}: {v['recognised_now']} -> rows {v['attributed_to_rows']}" + (f" NEWLY UNASSESSED {v['newly_unassessed']}" if v["newly_unassessed"] else ""))
    (out / "gate_report.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validation gate for a staged batch of candidate lexicon rows (no merge).")
    ap.add_argument("--staged", type=Path, required=True, help="staged_rows.csv (scripts/clause_tier.py)")
    ap.add_argument("--decisions", type=Path, required=True, help="decisions.csv (scripts/clause_tier.py)")
    ap.add_argument("--candidates", type=Path, required=True, help="candidates.csv (scripts/fdc_ingest.py normalise)")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--rule", type=Path, default=clause_tier.RULE_PATH)
    ap.add_argument("--src", type=Path, default=ROOT / "src")
    ap.add_argument("--evaluation", type=Path, default=ROOT / "evaluation")
    ap.add_argument("--fao-text", type=Path, default=None, help="pdftotext -layout output of the FAO report, to verify the clause verbatim")
    ap.add_argument("--policy", type=Path, default=None, help="variant policy JSON (data/ingest/variant_policy_1.json)")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--strict", action="store_true", help="exit 3 when the verdict is BLOCKED")
    args = ap.parse_args(argv)
    try:
        with tempfile.TemporaryDirectory() as td:
            g = run_gate(args.staged, args.decisions, args.candidates, clause_tier.load_rule(args.rule), args.src, args.evaluation, Path(td), args.fao_text, load_policy(args.policy))
            write_report(g, args.out, args.force)
        print(f"verdict {g['verdict']}; staged {g['staged']}, ready {len(g['ready'])}, synonyms {len(g['synonym_rows'])}, parked {len(g['ambiguity_queue'])}, blockers {g['blockers']}")
        return 3 if (args.strict and g["blockers"]) else 0
    except FileExistsError as e:
        sys.stderr.write(f"Refusing to overwrite: {e}\n")
        return 2
    except Exception as e:   # noqa: BLE001
        sys.stderr.write(f"Error: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
