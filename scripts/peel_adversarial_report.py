"""Report Python/JS differences on fictional peel probes; never fail on differences.

Run from any directory: python scripts/peel_adversarial_report.py
Requires Node.js and the Python dependencies used by foodscan.
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import parity_check as pc  # noqa: E402


def main():
    with (ROOT / "tests" / "corpus_adversarial_peel.csv").open(
        encoding="utf-8", newline=""
    ) as f:
        rows = list(csv.DictReader(f))

    pairs = [(row["text"], source) for row in rows for source in ("text", "ocr")]
    js_results = pc.run_js(pairs)
    if len(js_results) != len(pairs):
        raise RuntimeError("JS engine returned a different number of results")

    differing_rows = set()
    differences = 0
    for index, ((text, source), js) in enumerate(zip(pairs, js_results)):
        row = rows[index // 2]
        py = pc.py_result(text, source)
        if py != js:
            differing_rows.add(row["id"])
            differences += 1
            print(f"\n{row['id']} [{row['category']}, {source}]: {text}")
            for key in py:
                if py[key] != js[key]:
                    print(f"  {key}:\n    Python: {py[key]!r}\n    JS: {js[key]!r}")
    print(f"\n{len(rows)} rows; {len(differing_rows)} divergent rows; "
          f"{differences}/{len(pairs)} divergent analyses (text and OCR paths).")


if __name__ == "__main__":
    main()
