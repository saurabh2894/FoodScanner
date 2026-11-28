"""Audit source lexicon rows and the generated browser tables without changing them.

Run: python scripts/audit_lexicon.py [--json]
NOVA groups are not fields in the lexicon; classification depends on context.
"""
import argparse
import csv
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESOURCES = ROOT / "src" / "foodscan" / "resources"
KINDS = {
    "whole_food", "vegetable", "fruit", "culinary", "herb_spice", "legume",
    "nut_seed", "flour", "culture", "unplaced", "fruit_juice", "food_powder",
    "neutral", "named_water",
}


def key(text):
    return " ".join(re.sub(r"[^\w\s]", " ", text.lower()).split())


def variant_key(text):
    # Candidate heuristic, adapted from scripts/count_heads.py; not an equivalence rule.
    text = key(text).replace("tinned", "canned").replace("colour", "color")
    text = text.replace("flavour", "flavor").replace("yoghurt", "yogurt")
    text = re.sub(r"ise\b", "ize", text)

    def singular(word):
        if word.endswith("ies") and len(word) > 4:
            return word[:-3] + "y"
        if word.endswith("oes"):
            return word[:-2]
        if word.endswith(("ss", "us")):
            return word
        if word.endswith("s") and len(word) > 3:
            return word[:-1]
        return word

    return " ".join(singular(word) for word in text.split())


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
            raise ValueError(f"{path}: missing or duplicate CSV headers")
        return list(reader)


def browser_tables():
    # The build inserts the output of this same generator into template.html.
    env = dict(os.environ, PYTHONPATH=str(ROOT / "src"), PYTHONDONTWRITEBYTECODE="1")
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "web_tables.py")],
        capture_output=True, text=True, env=env, check=True,
    )
    return json.loads(result.stdout)


def audit(heads, aliases, browser):
    issues = []
    for label, rows, fields in (
        ("lexicon", heads, ("term", "kind", "source")),
        ("synonyms", aliases, ("from", "to", "source")),
    ):
        for line, row in enumerate(rows, 2):
            for field in fields:
                if not isinstance(row.get(field), str) or not row[field].strip():
                    issues.append(f"{label} row {line}: missing or empty {field}")
            if None in row:
                issues.append(f"{label} row {line}: extra CSV fields {row[None]!r}")
            for field in fields:
                value = row.get(field)
                if isinstance(value, str) and value and (value != value.strip() or
                                                          (field != "source" and not key(value))):
                    issues.append(f"{label} row {line}: malformed {field}: {value!r}")
            if label == "lexicon" and row.get("kind") and row["kind"] not in KINDS:
                issues.append(f"{label} row {line}: unknown kind {row['kind']!r}")

    names = [r.get("term") for r in heads if isinstance(r.get("term"), str) and r["term"].strip()]
    exact = Counter(names)
    duplicates = [f"{name}: {count} rows" for name, count in sorted(exact.items()) if count > 1]
    normalized, variants, categories = defaultdict(set), defaultdict(set), defaultdict(set)
    for row in heads:
        name, kind = row.get("term"), row.get("kind")
        if not isinstance(name, str) or not name.strip():
            continue
        normalized[key(name)].add(name)
        variants[variant_key(name)].add(name)
        if isinstance(kind, str) and kind.strip():
            categories[key(name)].add(kind)
    normalized_heads = [f"{k}: {', '.join(sorted(v))}" for k, v in sorted(normalized.items()) if len(v) > 1]
    candidate_heads = [f"{k}: {', '.join(sorted(v))}" for k, v in sorted(variants.items()) if len(v) > 1]
    inconsistent = [f"{k}: {', '.join(sorted(v))}" for k, v in sorted(categories.items()) if len(v) > 1]

    targets, spellings = defaultdict(set), defaultdict(set)
    for row in aliases:
        source, target = row.get("from"), row.get("to")
        if isinstance(source, str) and source.strip() and isinstance(target, str) and target.strip():
            targets[key(source)].add(target)
            spellings[key(source)].add(source)
    duplicate_aliases = Counter((r.get("from"), r.get("to")) for r in aliases
                                if isinstance(r.get("from"), str) and isinstance(r.get("to"), str))
    duplicates += [f"alias {a} -> {b}: {n} rows" for (a, b), n in sorted(duplicate_aliases.items()) if n > 1]
    collisions = []
    for alias, destinations in sorted(targets.items()):
        if len({key(t) for t in destinations}) > 1:
            collisions.append(f"{alias} -> {', '.join(sorted(destinations))} (multiple targets)")
        other_heads = sorted(n for n in normalized.get(alias, ()) if key(n) not in {key(t) for t in destinations})
        if other_heads:
            collisions.append(f"{alias} -> {', '.join(sorted(destinations))}; also head: {', '.join(other_heads)}")
    normalized_aliases = [f"{k}: {', '.join(sorted(v))}" for k, v in sorted(spellings.items()) if len(v) > 1]

    differences = []
    for label, python_rows, js_rows, fields in (
        ("heads", heads, browser["lexicon"], ("term",)),
        ("aliases", aliases, browser["synonyms"], ("from", "to")),
    ):
        py = {tuple(r.get(f) or "" for f in fields) for r in python_rows}
        js = {tuple(r.get(f) or "" for f in fields) for r in js_rows}
        for side, missing in (("Python only", py - js), ("browser only", js - py)):
            differences.extend(f"{label} {side}: {' -> '.join(entry)}" for entry in sorted(missing))

    return {
        "scope": ["Browser tables are generated from the Python CSVs by scripts/web_tables.py; "
                  "this compares generator output, not a deployed artifact.",
                  "NOVA group counts unavailable: lexicon rows have no group field; classification is contextual."],
        "counts_per_category": dict(sorted(Counter(r.get("kind") or "(missing)" for r in heads).items())),
        "counts_per_nova_group": None,
        "duplicate_entries": duplicates,
        "normalised_head_keys": normalized_heads,
        "normalised_alias_keys": normalized_aliases,
        "alias_collisions": collisions,
        "near_duplicate_head_candidates": candidate_heads,
        "inconsistent_categories": inconsistent,
        "missing_or_malformed_fields": issues,
        "python_browser_differences": differences,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit JSON instead of plain text")
    args = parser.parse_args()
    report = audit(read_csv(RESOURCES / "lexicon.csv"),
                   read_csv(RESOURCES / "synonyms.csv"), browser_tables())
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        for section, value in report.items():
            print(f"{section.replace('_', ' ').capitalize()}:")
            if isinstance(value, dict):
                for name, count in value.items():
                    print(f"  {name}: {count}")
            elif isinstance(value, list):
                for item in value:
                    print(f"  {item}")
                if not value:
                    print("  None")
            else:
                print("  Not available")


if __name__ == "__main__":
    main()
