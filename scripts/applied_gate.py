"""Applied-state gate: BEFORE = a base source tree (e.g. a worktree of main), AFTER = the COMMITTED repo source. Both are analysed in SEPARATE fresh processes.
It proves the after build actually contains the batch (every staged term recognised after and not before), then compares the frozen 66 and the out-of-sample 32 (every changed input
attributed to a staged or retyped term; 0 unexplained; 0 abstain->4), the drift over every term/synonym of the base build, and named controls (negative and positive).
Read-only. Controls come from the rule JSON ('negative_controls', 'positive_controls', list of strings). Exit 0 ran; 1 error; 2 refused.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import class_gate as cg  # noqa: E402
import oos_eval  # noqa: E402
import validate_batch as vb  # noqa: E402

KINDS_PROBE = r'''
import json, sys
from foodscan.pipeline import analyse_text
from foodscan.classify import lookup, is_recognised
from foodscan.normalise import normalise_ingredient
out = {}
for line in open(sys.argv[1], encoding="utf-8").read().splitlines():
    if not line.strip():
        continue
    a = analyse_text("Ingredients: " + line, source="text")
    nm = normalise_ingredient(line).name
    r = lookup(nm) if is_recognised(nm) else None
    out[line] = {"group": a.group if a.answered else None, "ingredients": a.ingredients, "unassessed": a.unassessed, "drivers": [d.detail for d in a.drivers], "reason": None if a.answered else a.reason,
                 "row": None if r is None else {"term": r["term"], "kind": r["kind"]}}
json.dump(out, open(sys.argv[2], "w"), indent=0)
sys.stderr.write(sys.argv[3])
'''


def run_probe(src: Path, lines: list[str], work: Path, tag: str) -> dict:
    import subprocess
    f, s, o = work / f"{tag}.txt", work / f"{tag}_run.py", work / f"{tag}.json"
    f.write_text("\n".join(lines) + "\n", encoding="utf-8")
    s.write_text(KINDS_PROBE, encoding="utf-8")
    env = {"PYTHONPATH": str(src), "PATH": "/usr/bin:/bin:/usr/local/bin", "HOME": str(Path.home())}
    r = subprocess.run([sys.executable, str(s), str(f), str(o), str(src)], capture_output=True, text=True, env=env, cwd=str(src.parent))
    if r.returncode or str(src) not in r.stderr:
        raise RuntimeError(f"probe failed or did not use {src}: {r.stderr[-300:]}")
    return json.loads(o.read_text(encoding="utf-8"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--base-src", type=Path, required=True)
    ap.add_argument("--after-src", type=Path, default=ROOT / "src")
    ap.add_argument("--rule", type=Path, required=True)
    ap.add_argument("--rows", type=Path, required=True, help="the batch's lexicon_candidate_rows.csv (the rows that must be present after)")
    ap.add_argument("--retyped", nargs="*", default=[], help="existing terms whose kind changed (attribution only)")
    ap.add_argument("--expected-drift", nargs="*", default=[], help="existing terms whose sole-item behaviour change is an OWNER-RULED change (reported as attributed, not a blocker)")
    ap.add_argument("--powder-allow", nargs="*", default=[], help="exact '<term> powder' forms that an owner ruling allows to answer Group 1 without a stated composition (e.g. 'milk powder')")
    ap.add_argument("--attribute-words", nargs="*", default=[], help="phrases that attribute a changed input to an OWNER-RULED behaviour change (e.g. 'powdered milk')")
    ap.add_argument("--powder-surface", action="store_true", help="also probe '<term> powder' / '100% <term> powder' for every whole_food/legume/vegetable/food_powder row of the base and after builds and report every change")
    ap.add_argument("--oos-cache", type=Path, default=ROOT / "data" / "cache" / "oos_herb_spice_1")
    ap.add_argument("--evaluation", type=Path, default=ROOT / "evaluation")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)
    if a.out.exists() and not a.force:
        sys.stderr.write(f"Refusing to overwrite: {a.out}\n")
        return 2
    rule = json.loads(a.rule.read_text(encoding="utf-8"))
    terms = [r["term"] for r in vb.read_csv(a.rows)]
    attributed = terms + list(a.retyped) + list(a.attribute_words)
    res_b, res_a = a.base_src / "foodscan" / "resources", a.after_src / "foodscan" / "resources"
    base_terms = [r["term"] for r in vb.read_csv(res_b / "lexicon.csv")] + [r["from"] for r in vb.read_csv(res_b / "synonyms.csv")]
    out = {"rule_id": rule["rule_id"], "base_src": str(a.base_src), "after_src": str(a.after_src)}
    lex_b = {r["term"]: r for r in vb.read_csv(res_b / "lexicon.csv")}
    lex_a = {r["term"]: r for r in vb.read_csv(res_a / "lexicon.csv")}
    out["lexicon_rows"] = {"before": len(lex_b), "after": len(lex_a), "added": sorted(set(lex_a) - set(lex_b)), "removed": sorted(set(lex_b) - set(lex_a)),
                           "kind_changed": {t: [lex_b[t]["kind"], lex_a[t]["kind"]] for t in lex_b if t in lex_a and lex_b[t]["kind"] != lex_a[t]["kind"]},
                           "source_changed": [t for t in lex_b if t in lex_a and lex_b[t]["source"] != lex_a[t]["source"]]}
    out["synonyms_markers_untouched"] = {f: (res_b / f).read_bytes() == (res_a / f).read_bytes() for f in ("synonyms.csv", "markers.csv")}
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        neg, pos = rule.get("negative_controls", []), rule.get("positive_controls", [])
        pb = run_probe(a.base_src, terms + base_terms + neg + pos, td, "b")
        pa = run_probe(a.after_src, terms + base_terms + neg + pos, td, "a")
        out["after_build_proof"] = {t: {"recognised_before": pb[t]["row"] is not None, "recognised_after": pa[t]["row"] is not None, "row_after": pa[t]["row"]} for t in terms}
        vb.run_dump(a.base_src, a.evaluation, td / "fb.json")
        vb.run_dump(a.after_src, a.evaluation, td / "fa.json")
        out["frozen_66"] = cg.compare_sets(json.loads((td / "fb.json").read_text()), json.loads((td / "fa.json").read_text()), attributed)
        inputs = a.oos_cache / "inputs"
        oos_eval.dump(a.base_src, inputs, td / "ob.json")
        oos_eval.dump(a.after_src, inputs, td / "oa.json")
        B, A = json.loads((td / "ob.json").read_text()), json.loads((td / "oa.json").read_text())
        out["out_of_sample"] = {"inputs": len(B), **cg.compare_sets(B, A, attributed)}
        diff = {t: [pb[t]["group"], pa[t]["group"]] for t in base_terms if (pb[t]["group"], pb[t]["ingredients"], pb[t]["unassessed"], pb[t]["drivers"]) != (pa[t]["group"], pa[t]["ingredients"], pa[t]["unassessed"], pa[t]["drivers"])}
        expected = {t: v for t, v in diff.items() if t in set(a.expected_drift)}
        diff = {t: v for t, v in diff.items() if t not in set(a.expected_drift)}
        out["drift"] = {"probed": len(base_terms), "differences": diff, "expected_owner_ruled": expected}
        if a.powder_surface:
            kinds = {"whole_food", "legume", "vegetable", "food_powder"}
            names = sorted({r["term"] for r in vb.read_csv(res_a / "lexicon.csv") if r["kind"] in kinds})
            lines = [n + " powder" for n in names] + ["100% " + n + " powder" for n in names] + ["whole " + n + " powder" for n in names]
            sb, sa = run_probe(a.base_src, lines, td, "sb"), run_probe(a.after_src, lines, td, "sa")
            ch = {l: [sb[l]["group"], sa[l]["group"]] for l in lines if (sb[l]["group"], sb[l]["unassessed"]) != (sa[l]["group"], sa[l]["unassessed"])}
            out["powder_surface"] = {"probed": len(lines), "group1_before": sum(1 for l in lines if sb[l]["group"] == 1), "group1_after": sum(1 for l in lines if sa[l]["group"] == 1),
                                     "changed": ch, "group1_after_forms_not_stated": [l for l in lines if sa[l]["group"] == 1 and not (l.startswith("100% ") or l.startswith("whole ") or l in set(a.powder_allow))],
                                     "owner_allowed_group1_forms": [l for l in lines if sa[l]["group"] == 1 and l in set(a.powder_allow)],
                                     "newly_group4_or_other": {l: v for l, v in ch.items() if v[1] not in (None, 1)}}
        out["controls"] = {n: {"group_before": pb[n]["group"], "group_after": pa[n]["group"], "row_after": pa[n]["row"], "drivers_after": pa[n]["drivers"], "reason_after": pa[n]["reason"], "unassessed_after": pa[n]["unassessed"]} for n in neg + pos}
    blockers = []
    if not all(v["recognised_after"] and not v["recognised_before"] for v in out["after_build_proof"].values()):
        blockers.append("after-build proof: a staged term is not recognised after, or was already recognised before")
    for k in ("frozen_66", "out_of_sample"):
        if out[k]["unexplained"]:
            blockers.append(f"{k}: unexplained {out[k]['unexplained']}")
        if out[k]["abstain_to_4"]:
            blockers.append(f"{k}: abstain->4")
    if out["drift"]["differences"]:
        blockers.append(f"drift: {out['drift']['differences']}")
    ps = out.get("powder_surface")
    if ps and (ps["group1_after_forms_not_stated"] or ps["newly_group4_or_other"]):
        blockers.append("powder surface: a bare 'X powder' still answers Group 1, or a powder form moved to another group")
    if not all(out["synonyms_markers_untouched"].values()):
        blockers.append("synonyms.csv or markers.csv changed")
    if out["lexicon_rows"]["removed"] or out["lexicon_rows"]["source_changed"]:
        blockers.append("a lexicon row was removed or its source changed")
    out["blockers"], out["verdict"] = blockers, "BLOCKED" if blockers else "READY_FOR_REVIEW"
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "applied_gate.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("verdict", out["verdict"], blockers)
    for k in ("frozen_66", "out_of_sample"):
        print(k, "changed", len(out[k]["changed"]), "unexplained", out[k]["unexplained"], "abstain->4", out[k]["abstain_to_4"], "abstain->1", out[k]["abstain_to_1"], "other", out[k]["other_group_change"])
    print("drift", out["drift"]["probed"], len(out["drift"]["differences"]), "| lexicon", out["lexicon_rows"]["before"], "->", out["lexicon_rows"]["after"], "kind_changed", len(out["lexicon_rows"]["kind_changed"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
