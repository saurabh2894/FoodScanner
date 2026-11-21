"""Class-bulk mapper: ONE reviewable rule file per FDC category (data/ingest/class_*.json) maps FDC candidate NAMES and RECORD ATTRIBUTES to candidate lexicon rows.

It maps names to a recognition kind. It never decides a NOVA group, never writes to src/foodscan/resources/, never touches synonyms.csv or markers.csv.
Each candidate gets exactly one decision with a reason code: ACCEPT / QUEUE / REJECT / OUT_OF_SCOPE. Outputs (in --out):
  decisions.csv, staged_rows.csv (canonical rows, validate_batch layout), synonym_candidates.csv (dedupe + FDC alternate names; NEVER merged here),
  queue.csv (conditional cases), attributes.csv (the FDC record attributes checked), scope_summary.json (hashes and counts).
Standard library only. Exit codes: 0 ok; 1 error; 2 refused (output exists without --force).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
csv.field_size_limit(10**9)


def words(s: str) -> list[str]:
    return re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", s.lower())


def split_parts(desc: str) -> list[str]:
    """Comma split that keeps commas inside brackets together."""
    parts, depth, cur = [], 0, ""
    for ch in desc:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        if ch == "," and depth == 0:
            parts.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur.strip())
    return [p.lower() for p in parts if p]


def read_zip_table(zpath: Path, base: str) -> list[dict]:
    with zipfile.ZipFile(zpath) as z:
        names = [n for n in z.namelist() if n.endswith("/" + base)]
        if not names:
            return []
        return list(csv.DictReader(io.TextIOWrapper(z.open(names[0]), encoding="utf-8", newline="")))


def load_attributes(cache: Path, cand: list[dict]) -> dict[str, dict]:
    """Per fdc_id: data_type, food category, SR alternate names, Foundation FoodOn name and NCBI taxon, portion descriptions/modifiers (CC0 FDC tables)."""
    ids = {c["fdc_id"] for c in cand}
    out = {i: {"alt_names": [], "foodon": "", "taxon": "", "portions": []} for i in ids}
    for z in sorted(cache.glob("FoodData_Central_*_csv_*.zip")):
        for r in read_zip_table(z, "food_attribute.csv"):
            i = r["fdc_id"]
            if i not in ids:
                continue
            if r.get("name") == "FoodOn Ontology Name For FDC Item":
                out[i]["foodon"] = r["value"]
            elif r.get("name") == "NCBI Taxon":
                out[i]["taxon"] = r["value"].rsplit("/", 1)[-1]
            elif r.get("food_attribute_type_id") == "1000" and r["value"]:
                out[i]["alt_names"].append(r["value"].lower())
        for r in read_zip_table(z, "food_portion.csv"):
            if r["fdc_id"] in ids:
                out[r["fdc_id"]]["portions"].append(" ".join(x for x in (r.get("portion_description"), r.get("modifier")) if x))
    return out


def derive_term(parts: list[str], rule: dict) -> tuple[str | None, list[str], bool]:
    """(label term, alternate names found in brackets, plain_form_seen). Form parts are removed; qualifiers are reversed in front of the head ('kidney, red' -> 'red kidney beans')."""
    forms = set(rule["form_tokens"])
    plain, kept, alts = False, [], []
    for p in parts:
        p2 = re.sub(r"\(0% moisture\)", "", p).strip()
        if p2 != p:
            plain = True
        if p2 in ("raw", "dry", "mature seeds", "mature seed", "all types"):
            plain = plain or p2 in ("raw", "dry")
            continue
        m = re.fullmatch(r"([^()]*)\((.*)\)", p2)
        if m:
            alts += [a.strip() for a in m.group(2).split(",") if a.strip()]
            p2 = m.group(1).strip()
        if p2:
            kept.append(p2)
    if not kept:
        return None, alts, plain
    head, quals = kept[0], kept[1:]
    term = " ".join(list(reversed(quals)) + [head]).strip()
    # SR/Foundation head 'beans' + variety: 'pinto' -> 'pinto beans'
    if head == "beans" and quals:
        term = " ".join(list(reversed(quals)) + ["beans"])
    return re.sub(r"\s+", " ", term), alts, plain


def decide(row: dict, attrs: dict, rule: dict) -> dict:
    out = {"decision": None, "reason_code": None, "reason": None, "term": None, "alts": []}

    def done(d, code, reason, term=None, alts=None):
        out.update(decision=d, reason_code=code, reason=reason, term=term, alts=alts or [])
        return out

    if row["food_category"] != rule["category_gate"]:
        return done("OUT_OF_SCOPE", "category", f"category '{row['food_category']}' has no rule in {rule['rule_id']}")
    desc = re.sub(r"\((?:includes|including)[^)]*\)", "", row["description"], flags=re.I)        # "(Includes foods for USDA's Food Distribution Program)" is a programme note, not a name part
    parts = split_parts(desc)
    all_words = set(words(" ".join(parts)))
    phrase = " ".join(parts)
    hit = sorted(all_words & set(rule["word_guard"]["words"])) + [p for p in rule["word_guard"].get("phrases", []) if p in phrase]
    if hit:
        return done("REJECT", "processed_word", f"word guard {hit}: outside a plain dry/raw seed")
    prod = sorted((all_words & set(rule["product_words"]["words"])) | {w for w in rule["product_words"]["words"] if " " in w and w in phrase})
    if prod:
        return done("REJECT", "product_word", f"product word(s) {prod}: a product made from a legume, not the legume")
    for w, why in rule["queue_words"].items():
        if w in all_words or (" " in w and w in phrase):
            return done("QUEUE", f"queue_{w.replace(' ', '_')}", why)
    term, alts, plain = derive_term(parts, rule)
    if term is None:
        return done("QUEUE", "no_head", "no item name after removing form parts")
    if not plain:
        return done("QUEUE", "plain_form_not_stated", "the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes")
    bad = sorted({w for p in attrs.get("portions", []) for w in words(p)} & set(rule["word_guard"]["words"]))
    if bad:
        return done("QUEUE", "attribute_contradicts_plain", f"FDC portion attribute(s) mention {bad}: the record may describe a prepared form")
    if term in rule["generic_queue"]["terms"]:
        return done("QUEUE", "generic_name", rule["generic_queue"]["why"], term, alts)
    return done("ACCEPT", "plain_seed", "plain raw/dry seed in the category; no guard, product or queue word; attributes consistent", term, alts)


def named_status(term: str, rule: dict) -> str:
    named = rule["clause"]["named_terms"]
    cw = set(words(rule["clause"]["text"]))
    assert all(n in cw for n in named)
    if term in named:
        return "exact term IS named by the clause"
    if any(w in named or w.rstrip("s") + "s" in named for w in term.split()):
        w = [w for w in term.split() if w in named or w.rstrip("s") + "s" in named][0]
        return f"exact term not named by the clause (an instance of the class 'legumes'; the clause names the broader term '{w}')"
    return "exact term not named by the clause (an instance of the class 'legumes')"


def source_text(rule: dict, recs: list[dict], term: str) -> str:
    prov = "; ".join(f"{r['dataset']} FDC id {r['fdc_id']} \"{r['description']}\"" for r in recs)
    cat = recs[0]["food_category"]
    return (f"PROVISIONAL: FAO 2019 (ca5644en.pdf) Table 1 Group 1 p.11 \"{rule['clause']['text']}\"; {named_status(term, rule)}; plain dry/raw seed form "
            f"(inference level: class-instance); FDC category '{cat}' (naming evidence only, CC0); {rule.get('condition_note', '')}{'; ' if rule.get('condition_note') else ''}name from USDA FoodData Central (CC0 1.0): {prov}")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict], cols: list[str], force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"{path} exists; use --force to overwrite")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Map one FDC category to candidate lexicon rows with one reviewable rule (names + record attributes, never a NOVA group).")
    ap.add_argument("--candidates", type=Path, required=True)
    ap.add_argument("--rule", type=Path, required=True)
    ap.add_argument("--cache", type=Path, default=ROOT / "data" / "cache" / "fdc")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)
    try:
        rule = json.loads(a.rule.read_text(encoding="utf-8"))
        rows = [r for r in csv.DictReader(a.candidates.open(encoding="utf-8", newline="")) if r["food_category"] == rule["category_gate"]]
        attrs = load_attributes(a.cache, rows)
        decisions, by_term, syn = [], defaultdict(list), []
        canon = rule.get("canonical", {})
        for r in rows:
            d = decide(r, attrs[r["fdc_id"]], rule)
            term = d["term"]
            if d["decision"] == "ACCEPT" and term in canon:
                c = canon[term]
                if c["to"] is None:
                    d = {**d, "decision": "QUEUE", "reason_code": "dedupe_stays_out", "reason": c["basis"]}
                elif c["to"] != term:
                    syn.append({"from": term, "to": c["to"], "basis": c["basis"], "origin": "dedupe", "fdc_id": r["fdc_id"]})
                    term = c["to"]
            if d["decision"] == "ACCEPT":
                by_term[term].append(r)
            elif d["reason_code"] == "dedupe_stays_out":
                term = d["term"]
            at = attrs[r["fdc_id"]]
            decisions.append({**{k: r[k] for k in ("candidate_id", "dataset", "data_type", "fdc_id", "description", "food_category")},
                              "decision": d["decision"], "reason_code": d["reason_code"], "reason": d["reason"], "term": term or "",
                              "foodon": at["foodon"], "taxon": at["taxon"], "alt_names": "|".join(at["alt_names"]), "portions": "|".join(sorted(set(at["portions"])))[:120]})
            alts = [x.strip() for a in d["alts"] + at["alt_names"] for x in a.split(",") if x.strip()]
            for alt in alts:
                if alt.lower() in rule.get("alt_name_ignore", {}):
                    continue                                               # qualifier words in brackets ('baby', 'roman', 'southern'), not names of the food
                syn.append({"from": alt.lower(), "to": term or "", "basis": "FDC bracketed/alternate name of the same record (naming evidence)", "origin": "fdc_alt_name", "fdc_id": r["fdc_id"]})
        staged = [{"term": t, "kind": rule["kind"], "source": source_text(rule, recs, t), "fdc_ids": ";".join(x["candidate_id"] for x in recs), "rule_id": rule["rule_id"]} for t, recs in sorted(by_term.items())]
        dcols = ["candidate_id", "dataset", "data_type", "fdc_id", "description", "food_category", "decision", "reason_code", "reason", "term", "foodon", "taxon", "alt_names", "portions"]
        write_csv(a.out / "decisions.csv", decisions, dcols, a.force)
        write_csv(a.out / "staged_rows.csv", staged, ["term", "kind", "source", "fdc_ids", "rule_id"], a.force)
        write_csv(a.out / "queue.csv", [d for d in decisions if d["decision"] == "QUEUE"], dcols, a.force)
        seen = set()
        uniq = [s for s in syn if not ((s["from"], s["to"]) in seen or seen.add((s["from"], s["to"]))) and s["from"] != s["to"] and s["to"]]
        res = ROOT / "src" / "foodscan" / "resources"
        existing = {}
        for fn, key, tgt in (("synonyms.csv", "from", "to"), ("lexicon.csv", "term", "term")):
            for r in csv.DictReader((res / fn).open(encoding="utf-8-sig", newline="")):
                existing[re.sub(r"[\s\-]+", " ", r[key].lower()).strip()] = (fn, r[tgt])
        fresh = [s for s in uniq if re.sub(r"[\s\-]+", " ", s["from"]).strip() not in existing]
        already = [{**s, "existing_in": existing[re.sub(r"[\s\-]+", " ", s["from"]).strip()][0], "existing_target": existing[re.sub(r"[\s\-]+", " ", s["from"]).strip()][1]} for s in uniq if re.sub(r"[\s\-]+", " ", s["from"]).strip() in existing]
        uniq = fresh
        write_csv(a.out / "synonym_candidates.csv", uniq, ["from", "to", "basis", "origin", "fdc_id"], a.force)
        write_csv(a.out / "synonym_already_mapped.csv", already, ["from", "to", "basis", "origin", "fdc_id", "existing_in", "existing_target"], a.force)
        write_csv(a.out / "candidates_category.csv", rows, list(rows[0].keys()), a.force)
        c = Counter(d["decision"] for d in decisions)
        summ = {"rule_id": rule["rule_id"], "rule_sha256": sha(a.rule), "candidates_sha256": sha(a.candidates), "category": rule["category_gate"], "candidates_in_category": len(rows),
                "decisions": dict(c), "reason_codes": dict(Counter(d["reason_code"] for d in decisions)), "staged_rows": len(staged), "synonym_candidates": len(uniq)}
        (a.out / "scope_summary.json").write_text(json.dumps(summ, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(summ))
        return 0
    except FileExistsError as e:
        sys.stderr.write(f"Refusing to overwrite: {e}\n")
        return 2
    except Exception as e:   # noqa: BLE001
        sys.stderr.write(f"Error: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
