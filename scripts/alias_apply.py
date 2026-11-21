"""Build the synonyms-2 rows from the reviewed alias-1 set and append them (additions-only, text-level) to src/foodscan/resources/synonyms.csv.

Inputs (committed under evaluation/synonyms_2/inputs/): the junior alias candidates (antigravity/alias-1) and the senior per-row review status (claude/junior-reviews-1). Only the rows the owner approved
for this batch are applied (INCLUDE below); every other alias is listed as parked and gets NO entry. Every applied row is re-verified against the repo's CACHED FDC zips (id exists, description matches,
Common Name attribute present) and against the live vocabulary (alias not already recognised; target is a lexicon row). Recognition routing only: no lexicon, marker or classifier edit.
Usage: python scripts/alias_apply.py --out evaluation/synonyms_2 [--apply]
"""
from __future__ import annotations

import argparse
import csv
import io
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
csv.field_size_limit(10**9)
sys.path.insert(0, str(ROOT / "src"))

PARKED = {"badishep": "partial evidence stays unverified", "chick peas": "partial evidence stays unverified", "tumeric": "quote unverified (host unreachable)", "chili": "quote unverified (host unreachable)",
          "cane sugar": "quote unverified (host unreachable)", "yellow cherries": "held: generic phrase", "gingelly oil": "NEEDS_EQUIVALENCE_EVIDENCE", "carom seeds": "NEEDS_EQUIVALENCE_EVIDENCE",
          "desi ghee": "NEEDS_EQUIVALENCE_EVIDENCE", "maida": "NEEDS_EQUIVALENCE_EVIDENCE", "cassia": "NEEDS_EQUIVALENCE_EVIDENCE", "cassia whole": "NEEDS_EQUIVALENCE_EVIDENCE", "refined palmolien oil": "AMBIGUOUS"}
ZIPS = {"foundation": "FoodData_Central_foundation_food_csv_2026-10-29.zip", "sr_legacy": "FoodData_Central_sr_legacy_food_csv_2018-04.zip"}


def table(zp: Path, base: str) -> list[dict]:
    z = zipfile.ZipFile(zp)
    n = [i for i in z.namelist() if i.endswith("/" + base)][0]
    return list(csv.DictReader(io.TextIOWrapper(z.open(n), encoding="utf-8", newline="")))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--inputs", type=Path, default=ROOT / "evaluation" / "synonyms_2" / "inputs")
    ap.add_argument("--cache", type=Path, default=ROOT / "data" / "cache" / "fdc")
    ap.add_argument("--synonyms", type=Path, default=ROOT / "src" / "foodscan" / "resources" / "synonyms.csv")
    ap.add_argument("--only", nargs="*", default=None, help="build only these aliases (e.g. a row re-added after an engine fix)")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    from foodscan.classify import is_recognised, lookup
    from foodscan.normalise import normalise_ingredient
    cand = {r["alias"]: r for r in csv.DictReader((a.inputs / "alias_candidates.csv").open(encoding="utf-8", newline=""))}
    rev = {r["alias"]: r for r in csv.DictReader((a.inputs / "03_alias_review_status.csv").open(encoding="utf-8", newline=""))}
    include = [al for al in rev if al not in PARKED and (a.only is None or al in a.only)]
    attrs, foods = {}, {}
    for ds, zn in ZIPS.items():
        zp = a.cache / zn
        foods[ds] = {r["fdc_id"]: r for r in table(zp, "food.csv")}
        attrs[ds] = {}
        for r in table(zp, "food_attribute.csv"):
            if r.get("food_attribute_type_id") == "1000":
                attrs[ds].setdefault(r["fdc_id"], []).append((r["id"], r["value"]))
    lex = {r["term"]: r["kind"] for r in csv.DictReader((ROOT / "src" / "foodscan" / "resources" / "lexicon.csv").open(encoding="utf-8-sig", newline=""))}
    rows, table_rows, errors = [], [], []
    for al in include:
        r, c = rev[al], cand[al]
        target = (r["proposed_target"] if al != "mandarin oranges" else "tangerines").split(" / ")[0]
        if al == "pak choi":
            target = "bok choy cabbage"
        if al == "mandarin oranges":
            fid, ds = "169105", "sr_legacy"
            f = foods[ds].get(fid)
            ok = bool(f) and f["description"] == "Tangerines, (mandarin oranges), raw"
            ev = f'USDA FoodData Central (CC0 1.0) SR Legacy FDC id 169105 "Tangerines, (mandarin oranges), raw" (food.csv in {ZIPS[ds]}): the bracketed alternate name in the FDC description ties mandarin oranges to tangerines (description evidence; the record carries no Common Name attribute)'
            where = f"{ZIPS[ds]} food.csv fdc_id 169105 description bracket"
        else:
            m = re.search(r"FDC ID (\d+) \((\w+): \"([^\"]*)\"; Common Name: \"([^\"]*)\"", c["equivalence_evidence"])
            fid, dsn, desc, cn = m.groups()
            ds = "foundation" if dsn == "foundation" else "sr_legacy"
            f = foods[ds].get(fid)
            hit = [(i, v) for i, v in attrs[ds].get(fid, []) if al.lower() in v.lower()]
            ok = bool(f) and f["description"] == desc and bool(hit)
            if not ok:
                errors.append(f"{al}: FDC {fid} check failed (desc match {bool(f) and f['description'] == desc}, attr {hit})")
                continue
            attr_id, val = hit[0]
            ev = f'USDA FoodData Central (CC0 1.0) {ds} FDC id {fid} "{f["description"]}", Common Name attribute (food_attribute.csv row {attr_id}, type 1000) "{val}" in {ZIPS[ds]}'
            where = f"{ZIPS[ds]} food_attribute.csv row {attr_id} (fdc_id {fid}, Common Name '{val}')"
        if target not in lex:
            errors.append(f"{al}: target {target!r} is not a lexicon row")
            continue
        if is_recognised(normalise_ingredient(al).name):
            errors.append(f"{al}: already recognised")
            continue
        src = (f'PROVISIONAL: alias of existing lexicon row "{target}" (same food per the FDC name evidence below; recognition routing only: the canonical row\'s placement and conditions apply unchanged, '
               f"no placement of its own); {ev}; synonyms-2 (reviewed alias-1)")
        rows.append({"from": al, "to": target, "source": src})
        table_rows.append({"alias": al, "target": target, "kind_of_target": lex[target], "pinpoint_evidence": where, "senior_status": r["senior_status"][:70]})
    if errors:
        print("ERRORS:", *errors, sep="\n  ")
        return 1
    a.out.mkdir(parents=True, exist_ok=True)
    with (a.out / "synonym_rows.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["from", "to", "source"], lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    with (a.out / "row_table.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(table_rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(table_rows)
    with (a.out / "parked.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["alias", "reason_parked", "no_synonyms_entry"])
        for k, v in PARKED.items():
            w.writerow([k, v, "yes"])
    print(f"{len(rows)} rows built, {len(PARKED)} parked")
    if a.apply:
        data = a.synonyms.read_bytes()
        buf = io.StringIO()
        csv.writer(buf, lineterminator="\n").writerows([[r["from"], r["to"], r["source"]] for r in rows])
        with a.synonyms.open("ab") as fh:
            if data and not data.endswith(b"\n"):
                fh.write(b"\n")
            fh.write(buf.getvalue().encode("utf-8"))
        print("appended to", a.synonyms)
    return 0


if __name__ == "__main__":
    sys.exit(main())
