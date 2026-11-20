"""Run a BEFORE build and an AFTER build (each in its OWN fresh process) on the texts of the out-of-sample challenge set and report, per label: was each staged target term in the
text recognised (or NOT), what newly became recognised, what newly became unassessed, any change of group, status or drivers, and what stayed unassessed.

This is a TARGETED OUT-OF-SAMPLE CHALLENGE SET for the staged terms, not a coverage estimate: the draw searches for the new terms, so it cannot measure general recognition.

Texts are read from a GITIGNORED cache (Open Food Facts content stays out of the repository); each text's sha256 is checked against the committed manifest. The committed report
(results.md/json) holds flags, counts and staged-term names only; the full detail (all unassessed item strings) goes to the cache. Read-only for src/. Exit codes: 0 ok; 1 error; 2 refused.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import oos_draw  # noqa: E402

TARGETS = oos_draw.TARGETS
PLURAL = {"seed": r"seeds?", "leaf": r"(?:leaf|leaves)", "weed": r"weeds?"}


def term_pattern(term: str) -> re.Pattern:
    """A mention of a staged term in a text: whole words, plural/leaves forms, any case, hyphen or space between words."""
    toks = term.split()
    parts = [PLURAL.get(t, re.escape(t)) if i == len(toks) - 1 else re.escape(t) for i, t in enumerate(toks)]
    return re.compile(r"(?<![a-z])" + r"[\s\-]+".join(parts) + r"(?![a-z])", re.I)


def dump(src: Path, inputs: Path, out: Path) -> None:
    env = {"PYTHONPATH": str(src), "PATH": "/usr/bin:/bin:/usr/local/bin", "HOME": str(Path.home())}
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "flip_dump.py"), "--inputs-dir", str(inputs), "--out", str(out)], capture_output=True, text=True, env=env, cwd=str(src.parent))
    if r.returncode or str(src) not in r.stderr:
        raise RuntimeError(f"dump failed or did not use {src}: {r.stderr[-300:]}")


def norm(s: str) -> str:
    return re.sub(r"[\s\-]+", " ", s.lower()).strip()


def judge(text: str, label_before: dict, label_after: dict) -> dict:
    """Per staged-term mention: after-build status. 'recognised' = an item read as an ingredient holds the mention and no unassessed item does; 'NOT recognised' = an unassessed item holds it;
    'inside another item' = the mention sits in text the parser did not turn into a stand-alone item (a compound, a bracket, a declared clause)."""
    mentions = []
    for t in TARGETS:
        for m in term_pattern(t).finditer(text):
            w = norm(m.group(0))
            ua = [u for u in label_after["unassessed"] if w in norm(u)]
            ing = [i for i in label_after["ingredients"] if w in norm(i)]
            ub = [u for u in label_before["unassessed"] if w in norm(u)]
            status = "NOT recognised" if ua else ("recognised" if ing else "inside another item")
            mentions.append({"target": t, "mention": w, "after": status, "was_unassessed_before": bool(ub)})
    return {"mentions": mentions}


def evaluate(manifest: dict, cache: Path, before_src: Path, after_src: Path) -> dict:
    texts = {}
    for l in manifest["labels"]:
        f = cache / l["cache_file"].split(" ")[0]
        t = f.read_text(encoding="utf-8")
        if hashlib.sha256(t.encode("utf-8")).hexdigest() != l["text_sha256"]:
            raise RuntimeError(f"{l['id']}: cached text does not match the manifest sha256 (the database changed or the cache is damaged: redraw is NOT allowed, report it)")
        texts[l["id"]] = t
    with tempfile.TemporaryDirectory() as td:
        b, a = Path(td) / "before.json", Path(td) / "after.json"
        dump(before_src, cache / "inputs", b)                  # two separate processes: cached resource tables make a one-process comparison invalid
        dump(after_src, cache / "inputs", a)
        before, after = json.loads(b.read_text(encoding="utf-8")), json.loads(a.read_text(encoding="utf-8"))
    rows = []
    for l in manifest["labels"]:
        i = l["id"]
        B, A = before[i], after[i]
        j = judge(texts[i], B, A)
        newly_rec = [x for x in B["unassessed"] if x not in A["unassessed"]]
        newly_un = [x for x in A["unassessed"] if x not in B["unassessed"]]
        changed = [f for f in ("group", "status", "drivers", "reason") if B[f] != A[f]]
        rows.append({"id": i, "code": l["code"], "target": l["target"], "mentions": j["mentions"], "newly_recognised_items": newly_rec, "newly_unassessed_items": newly_un,
                     "changed_fields": changed, "group_before": B["group"], "group_after": A["group"], "status_before": B["status"], "status_after": A["status"],
                     "unassessed_before": len(B["unassessed"]), "unassessed_after": len(A["unassessed"]), "unassessed_items_after": A["unassessed"], "ingredients_after": len(A["ingredients"])})
    return {"labels": rows}


def summarise(res: dict, manifest: dict) -> dict:
    ms = [m for r in res["labels"] for m in r["mentions"]]
    by = {}
    for m in ms:
        by.setdefault(m["after"], 0)
        by[m["after"]] += 1
    return {"labels": len(res["labels"]), "mentions_of_staged_terms": len(ms), "mentions_by_after_status": by,
            "labels_with_changed_group_status_drivers_or_reason": [r["id"] for r in res["labels"] if r["changed_fields"]],
            "labels_with_newly_unassessed_items": [r["id"] for r in res["labels"] if r["newly_unassessed_items"]]}


def report_md(res: dict, manifest: dict, summ: dict) -> str:
    L = ["# Targeted out-of-sample challenge set: results for herb_spice_bulk_1", "",
         "**This is a targeted out-of-sample challenge set for the staged terms. It is not a coverage estimate** (the draw searches for the new terms), and no figure here is a percentage of Indian foods or labels.", "",
         f"Retrieved {manifest['retrieved']}; {summ['labels']} labels; before/after builds run in separate fresh processes; texts live in a gitignored cache (see README). "
         "Detail strings (full unassessed lists) are in the cache report, not committed.", "",
         f"Mentions of staged terms: {summ['mentions_of_staged_terms']}; after-build status: {summ['mentions_by_after_status']}", "",
         "## NOT recognised (abstention or gap on a staged term): first-class results", ""]
    miss = [(r["id"], m) for r in res["labels"] for m in r["mentions"] if m["after"] != "recognised"]
    L += [f"- {i} ({next(x['code'] for x in res['labels'] if x['id'] == i)}): `{m['mention']}` (target `{m['target']}`): **{m['after']}**" for i, m in miss] or ["- none"]
    L += ["", "## Changes of group, status, drivers or reason between before and after", ""]
    ch = [r for r in res["labels"] if r["changed_fields"]]
    L += [f"- {r['id']}: {r['changed_fields']} (group {r['group_before']} -> {r['group_after']}, status {r['status_before']} -> {r['status_after']})" for r in ch] or ["- none"]
    L += ["", "## Per label", "", "| id | barcode | target | staged-term mentions (after status) | newly recognised items | newly unassessed | unassessed before -> after | group before -> after |", "|---|---|---|---|---|---|---|---|"]
    for r in res["labels"]:
        mm = "; ".join(f"{m['mention']}: {m['after']}" for m in r["mentions"]) or "none found by pattern"
        L.append(f"| {r['id']} | {r['code']} | {r['target']} | {mm} | {len(r['newly_recognised_items'])} | {len(r['newly_unassessed_items'])} | {r['unassessed_before']} -> {r['unassessed_after']} | {r['group_before']} -> {r['group_after']} |")
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", type=Path, default=ROOT / "evaluation" / "out_of_sample_herb_spice_1" / "manifest.json")
    ap.add_argument("--cache", type=Path, default=ROOT / "data" / "cache" / "oos_herb_spice_1")
    ap.add_argument("--before-src", type=Path, required=True, help="src/ of the build WITHOUT the batch (e.g. a git worktree of the commit before the merge)")
    ap.add_argument("--after-src", type=Path, default=ROOT / "src")
    ap.add_argument("--out", type=Path, default=ROOT / "evaluation" / "out_of_sample_herb_spice_1")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args(argv)
    try:
        if (args.out / "results.md").exists() and not args.force:
            sys.stderr.write("Refusing to overwrite results.md (use --force)\n")
            return 2
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        res = evaluate(manifest, args.cache, args.before_src.resolve(), args.after_src.resolve())
        summ = summarise(res, manifest)
        full = {"summary": summ, **res}
        args.cache.mkdir(parents=True, exist_ok=True)
        (args.cache / "results_full.json").write_text(json.dumps(full, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")          # cache only
        slim = {"summary": summ, "labels": [{k: v for k, v in r.items() if k not in ("unassessed_items_after", "newly_recognised_items", "newly_unassessed_items")} | {
            "newly_recognised_count": len(r["newly_recognised_items"]), "newly_unassessed_count": len(r["newly_unassessed_items"])} for r in res["labels"]]}
        (args.out / "results.json").write_text(json.dumps(slim, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        (args.out / "results.md").write_text(report_md(res, manifest, summ), encoding="utf-8")
        print(json.dumps(summ))
        return 0
    except Exception as e:   # noqa: BLE001
        sys.stderr.write(f"Error: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
