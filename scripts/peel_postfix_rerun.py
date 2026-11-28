"""Report-only rerun of the fictional adversarial peel corpus.

Run: python scripts/peel_postfix_rerun.py [--json]
Requires git, Node.js, tar, and the dependencies used by foodscan. Fetch
origin/copilot/peel-adversarial-corpus first. Differences never cause failure.
Both engine revisions are run from temporary git archives.
"""

import argparse
import csv
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS_REF = "origin/copilot/peel-adversarial-corpus"
CORPUS_COMMIT = "d03113b52b8733251e5b7b96b7de1b02e873dd3b"
CORPUS_PATH = "tests/corpus_adversarial_peel.csv"
BEFORE = "ddc717e72fc8c3b52f5479cb252d22db04e55aa2"
AFTER = "b88609675a3582aec1afce3be85da4c80ce44341"
SOURCES = ("text", "ocr")
REVIEW_FLAGS = {
    "plural-cumin-seeds": (
        "Likely false peel: 'Seeds' is moved from 'Cumin Seeds' into the "
        "section label, changing the ingredient."
    ),
    "plural-coriander-leaves": (
        "Likely false peel: 'Leaves' is moved from 'Coriander Leaves' into "
        "the section label, changing the ingredient."
    ),
    "alias-after-exact": (
        "Possible false peel: 'Turmeric Masala' could be one product name, "
        "but 'Masala' is treated as a section label."
    ),
    "unknown-label": (
        "Possible false peel: 'Garlic Powder Garnish' could be one product "
        "name, but 'Garnish' is treated as a section label."
    ),
}


def load_corpus():
    text = subprocess.run(
        ["git", "show", f"{CORPUS_COMMIT}:{CORPUS_PATH}"],
        cwd=ROOT, check=True, capture_output=True, text=True, encoding="utf-8",
    ).stdout
    rows = list(csv.DictReader(io.StringIO(text, newline=""), strict=True))
    ids = set()
    for row in rows:
        if not all(row.get(key) for key in ("id", "category", "text")):
            raise ValueError(f"Incomplete corpus row: {row!r}")
        if row["id"] in ids:
            raise ValueError(f"Duplicate corpus id: {row['id']}")
        ids.add(row["id"])
    return rows


def worker(root):
    sys.path[:0] = [str(root / "src"), str(root / "scripts")]
    import parity_check

    rows = json.load(sys.stdin)
    pairs = [(row["text"], source) for row in rows for source in SOURCES]
    js = parity_check.run_js(pairs)
    if len(js) != len(pairs):
        raise RuntimeError("JS engine returned a different number of results")
    results = [
        {"python": parity_check.py_result(text, source), "js": result}
        for (text, source), result in zip(pairs, js)
    ]
    json.dump(results, sys.stdout)


def run_engine(root, rows):
    result = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--worker", str(root)],
        cwd=root, input=json.dumps(rows), text=True, capture_output=True,
    )
    if result.returncode:
        raise RuntimeError(f"Engine worker failed in {root}:\n{result.stderr}")
    results = json.loads(result.stdout)
    if len(results) != len(rows) * len(SOURCES):
        raise RuntimeError("Engine returned a different number of results")
    return [
        dict(zip(SOURCES, results[i:i + len(SOURCES)]))
        for i in range(0, len(results), len(SOURCES))
    ]


def results_at(revision, rows):
    with tempfile.TemporaryDirectory(prefix="peel-engine-") as directory:
        archive = subprocess.run(
            ["git", "archive", revision], cwd=ROOT, check=True, capture_output=True,
        )
        subprocess.run(["tar", "-xf", "-", "-C", directory],
                       input=archive.stdout, check=True)
        return run_engine(Path(directory), rows)


def divergent(result):
    return any(pair["python"] != pair["js"] for pair in result.values())


def changed_rows(rows, before, after):
    changed = []
    for row, old, new in zip(rows, before, after):
        old_divergent, new_divergent = divergent(old), divergent(new)
        if old_divergent and not new_divergent:
            status = "now agree"
        elif not old_divergent and new_divergent:
            status = "now diverge"
        elif old_divergent and new_divergent and old != new:
            status = "still diverge, output changed"
        else:
            continue
        changed.append((row, old, new, status))
    return changed


def summary(result):
    return {
        source: {
            engine: {
                "answered": pair[engine]["answered"],
                "group": pair[engine]["group"],
                "ingredients": pair[engine]["ingredients"],
                "sections": pair[engine]["sections"],
            }
            for engine in ("python", "js")
        }
        for source, pair in result.items()
    }


def cell(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace(
        "|", "\\|"
    ).replace("\n", " ")


def report(rows, before, after):
    changes = changed_rows(rows, before, after)
    print(f"Corpus: {CORPUS_REF} at {CORPUS_COMMIT} (fictional inputs).")
    print(f"Before: reliability/demand-truth-23 at {BEFORE}.")
    print(f"Tested engine: claude/peel-known-phrase-1 at {AFTER}.")
    print("Both text and OCR paths; agreement compares the full parity result, "
          "not just the fields displayed below.")
    print(f"Rows: {len(rows)}; analyses per revision: {len(rows) * len(SOURCES)}.")
    for label, results in (("Before", before), ("After", after)):
        count = sum(divergent(result) for result in results)
        analyses = sum(pair["python"] != pair["js"]
                       for result in results for pair in result.values())
        print(f"{label}: {count}/{len(rows)} divergent rows; "
              f"{analyses}/{len(rows) * len(SOURCES)} divergent analyses.")
    print(f"Changed rows: {len(changes)}.")
    print("Output cells show answered, group, ingredients and sections per path "
          "and engine; --json emits the full results.")
    print("\n| ID | Change | Before | After |")
    print("|---|---|---|---|")
    for row, old, new, status in changes:
        print(f"| {row['id']} | {status} | {cell(summary(old))} | {cell(summary(new))} |")

    print("\n### Agreed outputs needing review")
    print("Manual flags include rows that already agreed before the fix. "
          "Possible false peels are ambiguous, not established errors. "
          "Outputs below show both engines and paths.")
    for row, result in zip(rows, after):
        if row["id"] in REVIEW_FLAGS and not divergent(result):
            print(f"\n**{row['id']}**: {REVIEW_FLAGS[row['id']]}")
            print(f"\nInput: {cell(row['text'])}")
            print(f"\nOutputs: {cell(summary(result))}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--json", action="store_true", help="emit full results as JSON")
    args = parser.parse_args()
    if args.worker:
        worker(args.worker)
        return
    rows = load_corpus()
    before = results_at(BEFORE, rows)
    after = results_at(AFTER, rows)
    if args.json:
        json.dump({"corpus_commit": CORPUS_COMMIT, "before_commit": BEFORE,
                   "after_commit": AFTER, "rows": rows, "before": before,
                   "after": after}, sys.stdout)
        print()
    else:
        report(rows, before, after)


if __name__ == "__main__":
    main()
