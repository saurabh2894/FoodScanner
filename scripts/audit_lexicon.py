"""Report integrity issues in the food lexicon and synonym tables, read-only."""

import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

RESOURCES = Path(__file__).resolve().parent.parent / "src" / "foodscan" / "resources"
KINDS = {
    "whole_food", "culinary", "flour", "herb_spice", "neutral", "culture",
    "food_powder", "unplaced", "nut_seed", "legume", "vegetable", "fruit",
    "fruit_juice", "named_water",
}
TABLES = {
    "lexicon.csv": ("term", "kind", "source"),
    "synonyms.csv": ("from", "to", "source"),
}


def flatten(text):
    """Match foodscan.normalise.flatten without importing the application."""
    text = re.sub(r"[-–—_/]", " ", text.lower().replace("’", "'").replace("‘", "'"))
    return re.sub(r"\s+", " ", text).strip()


def read_table(path, columns, issues):
    rows = []
    with path.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file, strict=True)
        try:
            header = next(reader, None)
            if header != list(columns):
                issues.append(f"{path.name}: malformed header {header!r}; expected {list(columns)!r}")
                return rows
            for values in reader:
                line = reader.line_num
                if len(values) != len(columns):
                    issues.append(f"{path.name}:{line}: expected {len(columns)} fields, got {len(values)}")
                    continue
                row = dict(zip(columns, values))
                for field, value in row.items():
                    if not value.strip():
                        issues.append(f"{path.name}:{line}: empty {field}")
                    elif value != value.strip():
                        issues.append(f"{path.name}:{line}: surrounding whitespace in {field}")
                rows.append((line, row))
        except csv.Error as error:
            issues.append(f"{path.name}:{reader.line_num}: malformed CSV: {error}")
    return rows


def audit(directory):
    """Return sections of findings; missing/unreadable files raise an error."""
    findings = {
        "Duplicate entries": [],
        "Normalised key collisions": [],
        "Empty or malformed fields": [],
        "Inconsistent categories": [],
    }
    for filename, columns in TABLES.items():
        rows = read_table(directory / filename, columns, findings["Empty or malformed fields"])
        key_field = columns[0]
        exact = defaultdict(list)
        normalised = defaultdict(list)
        for line, row in rows:
            term = row[key_field]
            key = flatten(term)
            if not key:
                continue
            exact[term].append(line)
            normalised[key].append((line, row))
            if filename == "lexicon.csv" and row["kind"].strip() not in KINDS:
                findings["Inconsistent categories"].append(
                    f"{filename}:{line}: {term!r} has unknown kind {row['kind']!r}"
                )
        for term, lines in sorted(exact.items()):
            if len(lines) > 1:
                findings["Duplicate entries"].append(f"{filename}: {term!r} at lines {lines}")
        for key, group in sorted(normalised.items()):
            terms = sorted({row[key_field] for _, row in group})
            if len(terms) > 1:
                locations = ", ".join(f"{row[key_field]!r} (line {line})" for line, row in group)
                findings["Normalised key collisions"].append(f"{filename}: {key!r}: {locations}")
            if filename == "lexicon.csv":
                kinds = sorted({row["kind"].strip() for _, row in group if row["kind"].strip()})
                if len(kinds) > 1:
                    locations = ", ".join(f"{row['kind']!r} (line {line})" for line, row in group)
                    findings["Inconsistent categories"].append(f"{filename}: {key!r}: {locations}")
            else:
                targets = {flatten(row["to"]) for _, row in group if row["to"].strip()}
                if len(targets) > 1:
                    locations = ", ".join(f"{row['to']!r} (line {line})" for line, row in group)
                    findings["Inconsistent categories"].append(
                        f"{filename}: {key!r} has conflicting targets: {locations}"
                    )
    return findings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resources", type=Path, default=RESOURCES, help="directory containing the two CSV tables")
    args = parser.parse_args(argv)
    try:
        findings = audit(args.resources)
    except (OSError, UnicodeError) as error:
        print(f"Cannot read lexicon: {error}", file=sys.stderr)
        return 1
    print(f"Food lexicon audit: {args.resources}")
    for heading, items in findings.items():
        print(f"\n{heading}: {len(items)}")
        for item in items:
            print(f"  {item}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
