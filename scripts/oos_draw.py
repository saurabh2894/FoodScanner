"""Draw real Open Food Facts labels for an out-of-sample check, by the rule pre-registered in evaluation/out_of_sample_herb_spice_1/README.md.

Network: read-only HTTPS GET to world.openfoodfacts.org (public API). The untouched ingredients_text_en strings go to a GITIGNORED cache (data/cache/oos_herb_spice_1/inputs/, never committed:
Open Food Facts database content stays out of the repository); the committed manifest.json holds barcodes, record URLs, a per-label licence note, retrieval date, sha256 of each text and the full
selection picture. No images. Refuses to overwrite.
Exit codes: 0 ok; 1 error; 2 refused (output exists).
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGETS = ["allspice", "basil", "celery seed", "chervil", "coriander leaf", "coriander seed", "dill weed", "dill seed", "marjoram", "oregano", "paprika", "parsley",
           "peppermint", "rosemary", "saffron", "sage", "savory", "spearmint", "tarragon", "thyme", "anise seed", "caraway seed", "cumin seed", "fenugreek seed"]
TERMS = "Open Food Facts: database ODbL, images CC BY-SA as stated by that site (not independently verified here)"
API = "https://world.openfoodfacts.org/api/v2/search"
PER_TARGET = 2


def used_codes() -> set[str]:
    out = subprocess.run(["grep", "-rhoE", r"\b[0-9]{8,14}\b", "evaluation", "data", "src", "tests", "research", "--exclude-dir=out_of_sample_herb_spice_1", "--exclude=*.zip"],
                         capture_output=True, text=True, cwd=ROOT).stdout.split()
    return {c for c in out if c.startswith("890")}


def get(url: str, tries: int = 8) -> dict:
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "foodscan-eval/1.0"}), timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception:   # noqa: BLE001  (the API answers 503 under load: back off and retry)
            time.sleep(10 + 10 * i)
    raise RuntimeError(f"no usable answer after {tries} tries: {url}")


def pool(term: str) -> tuple[list[dict], dict]:
    tag = "en:" + term.replace(" ", "-")
    page, out, api_count, short, capped = 1, [], 0, 0, False
    while True:
        q = urllib.parse.urlencode({"ingredients_tags": tag, "countries_tags": "en:india", "page_size": 100, "page": page, "fields": "code,product_name,brands,ingredients_text_en"})
        d = get(f"{API}?{q}")
        api_count = d.get("count", 0)
        for p in d.get("products", []):
            if len(p.get("ingredients_text_en") or "") >= 10:
                out.append(p)
            else:
                short += 1
        if page * 100 >= api_count or page >= 10:
            capped = page * 100 < api_count
            return out, {"api_count": api_count, "fetched_with_text": len(out), "excluded_short_or_missing_text": short, "pool_capped_at_1000": capped}
        page += 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=ROOT / "evaluation" / "out_of_sample_herb_spice_1", help="committed manifest goes here")
    ap.add_argument("--cache", type=Path, default=ROOT / "data" / "cache" / "oos_herb_spice_1", help="gitignored: the untouched texts go here")
    args = ap.parse_args(argv)
    if (args.out / "manifest.json").exists():
        sys.stderr.write("Refusing to overwrite: manifest.json exists\n")
        return 2
    try:
        used = used_codes()
        drawn, brands, notes = [], set(), {}
        for t in TARGETS:
            raw, stats = pool(t)
            cand = sorted((p for p in raw if p["code"] not in used), key=lambda p: int(p["code"]))
            notes[t] = {**stats, "excluded_used_codes": len(raw) - len(cand), "eligible_pool": len(cand), "skipped_same_brand_or_already_drawn": 0}
            print(t, notes[t], flush=True)
            took = 0
            for p in cand:
                brand = (p.get("brands") or "").split(",")[0].strip().lower()
                if took >= PER_TARGET:
                    break
                if p["code"] in {d["code"] for d in drawn} or (brand and brand in brands):
                    notes[t]["skipped_same_brand_or_already_drawn"] += 1
                    continue
                drawn.append({"code": p["code"], "product": p.get("product_name") or "", "brand": brand, "target": t, "text": p["ingredients_text_en"]})
                brands.add(brand)
                took += 1
            notes[t]["drawn"] = took
        (args.cache / "inputs").mkdir(parents=True, exist_ok=True)
        args.out.mkdir(parents=True, exist_ok=True)
        manifest = []
        for i, d in enumerate(drawn, 1):
            lid = f"S{i:02d}"
            (args.cache / "inputs" / f"{lid}.txt").write_text(d["text"], encoding="utf-8")
            manifest.append({"id": lid, "code": d["code"], "product": d["product"], "brand": d["brand"], "target": d["target"], "record": f"https://in.openfoodfacts.org/product/{d['code']}",
                             "cache_file": f"inputs/{lid}.txt (gitignored, not in the repository)", "text_sha256": hashlib.sha256(d["text"].encode("utf-8")).hexdigest(), "terms": TERMS})
        (args.out / "manifest.json").write_text(json.dumps({"retrieved": datetime.date.today().isoformat(), "api": API, "used_codes_in_exclusion_list": len(used), "label_count": len(drawn), "per_target": notes, "labels": manifest},
                                                           indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"drawn {len(drawn)} labels; used codes excluded {len(used)}; targets without a label: {[t for t, n in notes.items() if not n['drawn']]}")
        return 0
    except Exception as e:   # noqa: BLE001
        sys.stderr.write(f"Error: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
