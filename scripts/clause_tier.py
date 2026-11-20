"""WS3 clause-tier mapping: ONE reviewable rule (data/ingest/clause_tier1_herbs_spices.json) that maps FDC candidate names to candidate lexicon rows of kind
herb_spice, for the unconditioned Tier 1 clause of FAO 2019 Table 1 Group 1 ("herbs and spices ... whole or powdered, fresh or dried").

It maps NAMES to a recognition kind. It never decides a NOVA group, never writes to src/foodscan/resources/, and never passes a conditioned clause (nuts, juices,
plain cereals): those categories come back LABEL_BOUND. Each candidate gets exactly one decision with a reason code:
  ACCEPT       a candidate lexicon row (staged, PROVISIONAL, verbatim clause, per-row provenance)
  QUEUE        ambiguous: parked for review, never included (possible blend, unresolved qualifier, not placed by any source clause)
  REJECT       outside the clause as written (processed word, or a FAO Group 2 head)
  LABEL_BOUND  conditioned clause: only a label that declares the plain form can qualify a term
  OUT_OF_SCOPE no rule for this category in this file
Standard library only. Exit codes: 0 ok; 1 error; 2 refused (output exists without --force).
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULE_PATH = ROOT / "data" / "ingest" / "clause_tier1_herbs_spices.json"


def load_rule(path: Path = RULE_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def words(s: str) -> list[str]:
    return re.findall(r"[a-z]+", s.lower())


def decide(row: dict, rule: dict) -> dict:
    """One decision for one candidate row (see module docstring). Pure function of the row and the rule."""
    parts = json.loads(row["parts"]) if isinstance(row["parts"], str) else list(row["parts"])
    cat = row["food_category"]
    out = {"decision": None, "reason_code": None, "reason": None, "term": None}

    def done(decision, code, reason, term=None):
        out.update(decision=decision, reason_code=code, reason=reason, term=term)
        return out

    gate = rule["category_gate"]["food_category"]
    if cat != gate:
        bound = rule["label_bound_clauses"]["clauses"]
        if cat in bound:
            return done("LABEL_BOUND", "conditioned_clause", f"conditioned clause ({bound[cat]}): only a label that declares the plain form can qualify a term; no automatic pass")
        return done("OUT_OF_SCOPE", "category", f"category '{cat}' has no rule in {rule['rule_id']}")

    all_words = {w for p in parts for w in words(p)}
    hit = sorted(all_words & set(rule["processed_words"]["words"]))
    if hit:
        return done("REJECT", "processed", f"processed word(s) {hit}: outside 'whole or powdered, fresh or dried'")

    lead = set(rule["lead_words"])
    series = bool(parts) and parts[0] in lead
    rest = parts[1:] if series else parts
    if not rest:
        return done("QUEUE", "no_head", "no item name after the lead word")
    head, quals = rest[0], rest[1:]
    head_words = words(head)
    g2 = sorted(set(head_words) & set(rule["group2_heads"]["words"]))
    if g2:
        return done("REJECT", "group2_head", f"head word(s) {g2}: FAO Table 1 Group 2 example, not a herb or spice")

    forms = set(rule["form_words"])
    if len(head_words) > 1 and (set(head_words) & forms):
        return done("QUEUE", "form_embedded_in_name", f"'{head}': a form word sits inside the name, so it may be a product or blend rather than a single herb or spice")
    if len(head_words) > 1 and head_words[-1] == "spice":
        return done("QUEUE", "blend_name", f"'{head}': a multi-word name ending in 'spice' is a blend")

    left = [q for q in quals if not (set(words(q)) <= forms)]
    if not left:
        return done("ACCEPT", "clause_forms_only", "name plus only the clause forms (whole/powdered, fresh/dried)", head)
    if series and len(left) == 1 and re.fullmatch(r"[a-z]+", left[0]):
        return done("ACCEPT", "series_variety", f"FDC 'Spices, {head}, {left[0]}' order: label term is '{left[0]} {head}'", f"{left[0]} {head}")
    return done("QUEUE", "qualifier_unresolved", f"qualifier(s) {left} are not clause forms and cannot be resolved mechanically")


def source_text(rule: dict, recs: list[dict]) -> str:
    prov = "; ".join(f"{r['dataset']} FDC id {r['fdc_id']} \"{r['description']}\"" for r in recs)
    return (f"PROVISIONAL: FAO 2019 (ca5644en.pdf) Table 1 Group 1 p.11 \"{rule['clause']['text']}\"; exact term not named by the clause; "
            f"name from USDA FoodData Central (CC0 1.0): {prov}")


def map_candidates(rows: list[dict], rule: dict) -> tuple[list[dict], list[dict]]:
    """(decisions for every row, staged candidate lexicon rows). Rows mapping to the same term are merged with all their provenance."""
    decisions, by_term = [], defaultdict(list)
    for r in rows:
        d = decide(r, rule)
        decisions.append({**{k: r[k] for k in ("candidate_id", "dataset", "fdc_id", "description", "food_category")}, **d})
        if d["decision"] == "ACCEPT":
            by_term[d["term"]].append(r)
    staged = [{"term": t, "kind": rule["kind"], "source": source_text(rule, recs), "fdc_ids": ";".join(r["candidate_id"] for r in recs), "rule_id": rule["rule_id"]}
              for t, recs in sorted(by_term.items())]
    return decisions, staged


def fao_clause_present(fao_text: str, clause: str) -> bool:
    """Check a clause verbatim against the FAO report text (pdftotext -layout). Table 1 is two-column, so the right-hand 'EXAMPLES' column is rebuilt first."""
    lines = fao_text.splitlines()
    start = next((i for i, ln in enumerate(lines) if "TABLE 1. THE NOVA" in ln), None)
    if start is None:
        return False
    hdr = next((ln for ln in lines[start:start + 8] if "EXAMPLES" in ln), None)
    if hdr is None:
        return False
    col = hdr.index("EXAMPLES")
    end = next((i for i in range(start + 1, len(lines)) if "TABLE 1. Cont." in lines[i]), len(lines))
    right = " ".join(ln[col:].strip() for ln in lines[start:end] if len(ln) > col)
    norm = lambda s: re.sub(r"\s+", " ", s).strip()
    return norm(clause) in norm(right)


def write_csv(path: Path, rows: list[dict], cols: list[str], force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"{path} exists; use --force to overwrite")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Map FDC candidates to candidate herb_spice rows with one reviewable rule (names only, never a NOVA group).")
    ap.add_argument("--candidates", type=Path, required=True, help="candidates.csv from scripts/fdc_ingest.py normalise")
    ap.add_argument("--out", type=Path, required=True, help="directory for decisions.csv and staged_rows.csv")
    ap.add_argument("--rule", type=Path, default=RULE_PATH)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args(argv)
    try:
        rule = load_rule(args.rule)
        with args.candidates.open(encoding="utf-8", newline="") as fh:
            rows = [r for r in csv.DictReader(fh) if r["food_category"]]
        decisions, staged = map_candidates(rows, rule)
        write_csv(args.out / "decisions.csv", decisions, ["candidate_id", "dataset", "fdc_id", "description", "food_category", "decision", "reason_code", "reason", "term"], args.force)
        write_csv(args.out / "staged_rows.csv", staged, ["term", "kind", "source", "fdc_ids", "rule_id"], args.force)
        c = Counter(d["decision"] for d in decisions if d["food_category"] == rule["category_gate"]["food_category"])
        print(f"{len(rows)} candidates; in the Spices and Herbs category: {dict(c)}; staged rows: {len(staged)}")
        return 0
    except FileExistsError as e:
        sys.stderr.write(f"Refusing to overwrite: {e}\n")
        return 2
    except Exception as e:   # noqa: BLE001
        sys.stderr.write(f"Error: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
