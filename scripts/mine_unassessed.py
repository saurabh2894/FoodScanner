"""WS1 demand miner: one ranked inventory of every "not assessed" (unrecognised) term in the evaluation evidence.

Read-only tooling. It never edits an evaluation file, a resource table or the classifier; it writes only the two output files
(inventory.csv, inventory.json) into --out, and refuses to overwrite them without --force. No network. Standard library plus the repo's own
`foodscan` package (used read-only, to re-analyse the frozen inputs and to ask "is this term recognised now?").

Evidence streams (kept apart, because they do not carry the same trust):
  paste_live      every evaluation/*/inputs/*.txt analysed now with this build (clean text, current vocabulary)
  paste_recorded  `unassessed` lists recorded in evaluation JSON artifacts (paste_results.json, flip-check before/after files): clean text, older builds
  photo_recorded  "NOT ASSESSED" blocks in recorded photo/browser results: OCR-damaged text, so a term seen ONLY here is flagged photo_only
                  (probably OCR damage, not a vocabulary gap) and never ranks as demand on its own.

Ranking: by distinct input IDs from the two paste streams (a photo mention of an input already counted adds nothing), then live count, then
recorded mentions. A term already recognised by this build is kept in the inventory but marked `recognised_now`, so closed gaps stay visible.
Recognition includes the vocabulary and full-phrase strong-marker routes, not merely vocabulary lookup. A Group 4 answer alone is not
recognition: unresolved content must remain visible. Recognition does not establish universal placement of conditioned or compound forms.

Exit codes: 0 ok; 1 error; 2 output exists without --force.
"""
from __future__ import annotations

import argparse
from functools import lru_cache
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR_PREFIX = {"fresh_batch_1": "b1", "fresh_batch_2": "b2", "fresh_batch_3": "b3", "negation_addendum": "neg", "dev_regression_15": "dev15"}
LETTER_PREFIX = {"N": "b1", "M": "b2", "Q": "b3", "F": "dev15", "R": "neg"}
GROUP_NAME_SUFFIX = "(group name; its contents were assessed separately)"
HEADINGS = ("ADDITIVE CODES", "COMPLETENESS", "NOT READ AS INGREDIENTS", "NOT ASSESSED", "DRIVEN BY", "WEAK EVIDENCE", "EXTRACTED INGREDIENTS", "Raw text analysed", "Raw OCR text")


# ---------------------------------------------------------------- normalisation
def term_key(raw: str) -> str:
    """Grouping key: lowercase, bracket content and percentages dropped, spacing and edge punctuation tidied. The raw form is kept elsewhere."""
    s = raw.lower()
    s = re.sub(r"\([^)]*\)|\[[^\]]*\]|\{[^}]*\}", " ", s)
    s = re.sub(r"\d+(?:\.\d+)?\s*%", " ", s)
    s = re.sub(r"[^\w&'\- ]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip(" -&'_")
    return s


def is_noise(key: str) -> bool:
    """Stray fragments ('&quot', '631)', one or two letters) that are not ingredient terms."""
    letters = re.sub(r"[^a-z]", "", key)
    return len(letters) < 3 or key.startswith("quot") or re.fullmatch(r"[\d\s]+", key) is not None


def canon_id(raw: str | None, context_dir: str | None, manifest_codes: dict[str, str]) -> str | None:
    """b1/N05 style ID from a key ('N05', 'b1/N05', 'dev/F01') or an image file name ('Q02_8908000794023.jpg', 'N_8906010090197.jpg')."""
    if not raw:
        return None
    raw = str(raw)
    if "/" in raw and not raw.endswith((".jpg", ".png", ".jpeg")) and not raw.startswith(("http", "/")):
        p, n = raw.split("/", 1)
        return f"{'dev15' if p == 'dev' else p}/{n}"
    name = Path(raw).name
    tok = name.split("_", 1)[0].split(".", 1)[0]
    m = re.fullmatch(r"([NMQFR])(\d+)", tok)
    if m:
        letter, num = m.group(1), m.group(2)
        # N/M/Q/F are batch-local letters; R belongs to the negation addendum
        prefix = LETTER_PREFIX[letter]
        return f"{prefix}/{letter}{num}"
    if tok == "N":                                   # negation addendum photo names: N_<product code>.jpg
        code = re.sub(r"\D", "", name.split("_", 1)[1]) if "_" in name else ""
        return manifest_codes.get(code)
    if context_dir in DIR_PREFIX and re.fullmatch(r"[A-Z]\d+", raw):
        return f"{DIR_PREFIX[context_dir]}/{raw}"
    return None


def context_of(path: Path, evaluation: Path) -> str | None:
    rel = path.relative_to(evaluation).parts
    return rel[0] if rel and rel[0] in DIR_PREFIX else None


# ---------------------------------------------------------------- stream readers
def parse_not_assessed(text: str) -> list[str]:
    """Items listed under a 'NOT ASSESSED' heading in a rendered result (stops at the next heading or blank-line-delimited block end)."""
    out: list[str] = []
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if ln.strip() != "NOT ASSESSED":
            continue
        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        if j < len(lines) and lines[j].strip().startswith("Not in the vocabulary"):
            j += 1                                                    # the fixed explanatory sentence
        while j < len(lines):
            s = lines[j].strip()
            if any(s == h or s.startswith(h) for h in HEADINGS):
                break
            if s and not s.endswith(GROUP_NAME_SUFFIX):
                out.append(s)
            j += 1
    return out


def walk_json_unassessed(obj, path_ids: list[str], found: list[tuple[str | None, list[str]]], key_hint: str | None = None) -> None:
    """Collect (input id hint, unassessed list) pairs from any JSON shape that carries an `unassessed` list."""
    if isinstance(obj, dict):
        # an input RECORD: its group is a number or null. (A summary dict such as `changed_inputs` also has an `unassessed` list, but of input IDs, and a list-valued group.)
        if isinstance(obj.get("unassessed"), list) and all(isinstance(x, str) for x in obj["unassessed"]) and not isinstance(obj.get("group"), list):
            found.append((key_hint or obj.get("id"), obj["unassessed"]))
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                walk_json_unassessed(v, path_ids, found, k if isinstance(k, str) else key_hint)
    elif isinstance(obj, list):
        for v in obj:
            walk_json_unassessed(v, path_ids, found, key_hint)


def photo_text_blocks(obj) -> list[tuple[str | None, str]]:
    """(id hint, rendered result text) for photo result records (`result` or `displayed_result` strings)."""
    out = []
    if isinstance(obj, list):
        for rec in obj:
            if isinstance(rec, dict):
                text = rec.get("result") if isinstance(rec.get("result"), str) else rec.get("displayed_result")
                if isinstance(text, dict):
                    text = json.dumps(text)
                if isinstance(text, str) and "NOT ASSESSED" in text:
                    out.append((rec.get("id") or rec.get("image"), text))
    return out


# ---------------------------------------------------------------- mining
class Inventory:
    def __init__(self) -> None:
        self.rows: dict[str, dict] = {}

    def add(self, raw: str, stream: str, input_id: str | None, source: str) -> None:
        key = term_key(raw)
        if not key:
            return
        r = self.rows.setdefault(key, {"term": key, "variants": defaultdict(int), "paste_live": defaultdict(int), "paste_recorded": defaultdict(int),
                                       "photo_recorded": defaultdict(int), "sources": set()})
        r["variants"][raw.strip()] += 1
        r[stream][input_id or f"?{source}"] += 1
        r["sources"].add(source)


def mine(evaluation: Path, analyse) -> Inventory:
    inv = Inventory()
    manifest_codes: dict[str, str] = {}
    neg = evaluation / "negation_addendum" / "manifest.json"
    if neg.is_file():
        for rid, rec in json.loads(neg.read_text(encoding="utf-8")).items():
            if isinstance(rec, dict) and rec.get("code"):
                manifest_codes[str(rec["code"])] = f"neg/{rid}"

    # live: every inputs/*.txt analysed now
    for f in sorted(evaluation.glob("*/inputs/*.txt")):
        d = f.relative_to(evaluation).parts[0]
        iid = f"{DIR_PREFIX.get(d, d)}/{f.stem}"
        for item in analyse(f.read_text(encoding="utf-8")):
            inv.add(item, "paste_live", iid, "live")

    # recorded artifacts
    for f in sorted(evaluation.rglob("*.json")):
        try:
            obj = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        ctx = context_of(f, evaluation)
        rel = str(f.relative_to(evaluation))
        found: list[tuple[str | None, list[str]]] = []
        walk_json_unassessed(obj, [], found)
        for hint, items in found:
            iid = canon_id(hint, ctx, manifest_codes)
            for item in items:
                if not item.endswith(GROUP_NAME_SUFFIX) and "group name" not in item.lower():
                    inv.add(item, "paste_recorded", iid, rel)
        for hint, text in photo_text_blocks(obj):
            iid = canon_id(hint, ctx, manifest_codes)
            for item in parse_not_assessed(text):
                inv.add(item, "photo_recorded", iid, rel)
    return inv


def finish(inv: Inventory, recognised) -> list[dict]:
    rows = []
    for key, r in inv.rows.items():
        paste_ids = sorted(set(r["paste_live"]) | set(r["paste_recorded"]))
        photo_ids = sorted(set(r["photo_recorded"]) - set(paste_ids))
        ids = paste_ids + [i for i in photo_ids if i not in paste_ids]
        variants = sorted(r["variants"].items(), key=lambda kv: -kv[1])
        recog = recognised(variants[0][0]) or recognised(key)
        rows.append({
            "term": key, "distinct_paste_inputs": len(paste_ids), "live_inputs": len(r["paste_live"]), "live_mentions": sum(r["paste_live"].values()),
            "recorded_paste_mentions": sum(r["paste_recorded"].values()), "photo_mentions": sum(r["photo_recorded"].values()),
            "photo_only": not paste_ids, "noise": is_noise(key), "recognised_now": bool(recog),
            "input_ids": ids, "raw_variants": [v for v, _ in variants[:5]], "sources": sorted(r["sources"])})
    rows.sort(key=lambda x: (x["recognised_now"], x["photo_only"], -x["distinct_paste_inputs"], -x["live_inputs"], -x["recorded_paste_mentions"], -x["photo_mentions"], x["term"]))
    rank = 0
    for r in rows:
        if not r["recognised_now"] and not r["photo_only"] and not r["noise"]:
            rank += 1
            r["rank_open"] = rank
        else:
            r["rank_open"] = None
    return rows


def default_analysers():
    sys.path.insert(0, str(ROOT / "src"))
    from foodscan.classify import is_recognised
    from foodscan.normalise import normalise_ingredient
    from foodscan.pipeline import analyse_text

    def unassessed_of(text: str) -> list[str]:
        a = analyse_text(text, source="text")
        return [u for u in a.unassessed if "group name" not in u]

    @lru_cache(maxsize=None)
    def recognised(raw: str) -> bool:
        if is_recognised(normalise_ingredient(raw).name):
            return True
        # The lexicon is not the only recognition route: strong derived-substance
        # markers can already account for a term. Require the full original phrase
        # to have no unresolved content, rather than treating any marker substring
        # or a Group 4 answer as proof that its whole item has been assessed.
        # Do not let an already-decisive marker conceal bracketed composition.
        # This closure route is only for a simple term, never a compound form.
        if re.search(r"[()\[\],;:&]|\band\b", raw, re.I):
            return False
        a = analyse_text("Ingredients: " + raw, source="text")
        return bool(a.drivers) and not a.unassessed and not a.unplaced

    return unassessed_of, recognised


def write_outputs(rows: list[dict], out: Path, force: bool) -> None:
    csv_path, json_path = out / "inventory.csv", out / "inventory.json"
    if (csv_path.exists() or json_path.exists()) and not force:
        raise FileExistsError(f"{out} already holds an inventory; use --force to overwrite")
    out.mkdir(parents=True, exist_ok=True)
    cols = ["rank_open", "term", "distinct_paste_inputs", "live_inputs", "live_mentions", "recorded_paste_mentions", "photo_mentions", "photo_only", "noise", "recognised_now",
            "input_ids", "raw_variants", "sources"]
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for r in rows:
            w.writerow([("; ".join(r[c]) if isinstance(r[c], list) else ("" if r[c] is None else r[c])) for c in cols])
    json_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Rank every unassessed term across the evaluation evidence (read-only).")
    ap.add_argument("--evaluation", type=Path, default=ROOT / "evaluation", help="evaluation directory to read (default: ./evaluation)")
    ap.add_argument("--out", type=Path, default=ROOT / "evaluation" / "demand_inventory_1", help="directory for inventory.csv / inventory.json")
    ap.add_argument("--force", action="store_true", help="overwrite an existing inventory in --out")
    ap.add_argument("--top", type=int, default=25, help="how many open terms to print (default 25)")
    args = ap.parse_args(argv)
    try:
        analyse, recognised = default_analysers()
        rows = finish(mine(args.evaluation, analyse), recognised)
        write_outputs(rows, args.out, args.force)
    except FileExistsError as e:
        sys.stderr.write(f"Refusing to overwrite: {e}\n")
        return 2
    except Exception as e:   # noqa: BLE001
        sys.stderr.write(f"Error: {e}\n")
        return 1
    open_rows = [r for r in rows if r["rank_open"]]
    print(f"{len(rows)} distinct terms; {len(open_rows)} open (not recognised now, seen in paste text, not noise); "
          f"{sum(r['recognised_now'] for r in rows)} recognised now; {sum(r['photo_only'] for r in rows)} photo-only; written to {args.out}")
    for r in open_rows[: args.top]:
        print(f"{r['rank_open']:3d}  {r['distinct_paste_inputs']:2d} inputs  {r['term'][:40]:40s} {', '.join(r['input_ids'][:6])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
