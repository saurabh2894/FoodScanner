"""Report integrity issues in the food lexicon and synonym tables, read-only."""

import argparse
import csv
import io
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


def is_metadata_row(values, columns):
    """Intentional shape: the 3 table columns plus a trailing source id and batch tag, nothing else."""
    return (
        len(values) == len(columns) + 2
        and re.fullmatch(r"[\w:;.\-]+", values[-2]) is not None
        and re.fullmatch(r"[\w\-]+", values[-1]) is not None
    )


def read_table(path, columns, issues, metadata):
    rows = []
    with path.open(encoding="utf-8-sig", newline="") as file:
        record_lines = []

        def lines():
            for line in file:
                record_lines.append(line)
                yield line

        reader = csv.reader(lines())
        try:
            record_lines.clear()
            header = next(reader, None)
            if header != list(columns):
                issues.append(f"{path.name}: malformed header {header!r}; expected {list(columns)!r}")
                return rows
            while True:
                record_lines.clear()
                try:
                    values = next(reader)
                except StopIteration:
                    break
                line = reader.line_num
                try:
                    list(csv.reader(io.StringIO("".join(record_lines)), strict=True))
                except csv.Error as error:
                    issues.append(f"{path.name}:{line}: malformed CSV: {error}")
                if len(values) != len(columns):
                    if is_metadata_row(values, columns):
                        metadata.append(f"{path.name}:{line}: {values[0]!r} has trailing id and batch columns ({values[-2]!r}, {values[-1]!r}); ignored by the 3-column loader")
                        values = values[:len(columns)]
                    else:
                        issues.append(f"{path.name}:{line}: expected {len(columns)} fields, got {len(values)} (a split or malformed row, the loader would keep a truncated source)")
                row = dict(zip(columns, (values + [""] * len(columns))[:len(columns)]))
                for field, value in row.items():
                    if not value.strip():
                        issues.append(f"{path.name}:{line}: empty {field}")
                    elif value != value.strip():
                        issues.append(f"{path.name}:{line}: surrounding whitespace in {field}")
                rows.append((line, row))
        except csv.Error as error:
            issues.append(f"{path.name}:{reader.line_num}: malformed CSV: {error}")
    return rows


def same_target(rows, key_field, term):
    """True when every row for this exact synonym source term maps to the same normalised target."""
    return len({flatten(row["to"]) for _, row in rows if row[key_field] == term}) == 1


def audit(directory):
    """Return sections of findings; missing/unreadable files raise an error."""
    findings = {
        "Duplicate entries": [],
        "Normalised key collisions": [],
        "Empty or malformed fields": [],
        "Inconsistent categories": [],
        "Info: trailing id/batch metadata columns (intentional, not errors)": [],
        "Info: same-target duplicate aliases (harmless repeats)": [],
        "Info: same-target normalised spelling variants (harmless)": [],
    }
    metadata = findings["Info: trailing id/batch metadata columns (intentional, not errors)"]
    all_keys = defaultdict(list)
    for filename, columns in TABLES.items():
        rows = read_table(directory / filename, columns, findings["Empty or malformed fields"], metadata)
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
            all_keys[key].append((filename, line, term))
            if filename == "lexicon.csv" and row["kind"].strip() not in KINDS:
                findings["Inconsistent categories"].append(
                    f"{filename}:{line}: {term!r} has unknown kind {row['kind']!r}"
                )
        for term, lines in sorted(exact.items()):
            if len(lines) > 1:
                if filename == "synonyms.csv" and same_target(rows, key_field, term):
                    findings["Info: same-target duplicate aliases (harmless repeats)"].append(f"{filename}: {term!r} at lines {lines}")
                else:
                    findings["Duplicate entries"].append(f"{filename}: {term!r} at lines {lines}")
        for key, group in sorted(normalised.items()):
            terms = sorted({row[key_field] for _, row in group})
            if len(terms) > 1:
                locations = ", ".join(f"{row[key_field]!r} (line {line})" for line, row in group)
                if filename == "synonyms.csv" and len({flatten(r["to"]) for _, r in group}) == 1:
                    findings["Info: same-target normalised spelling variants (harmless)"].append(f"{filename}: {key!r}: {locations}")
                else:
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
    for key, group in sorted(all_keys.items()):
        if len({filename for filename, _, _ in group}) < 2:
            continue
        locations = ", ".join(f"{term!r} ({filename}:{line})" for filename, line, term in group)
        if len({term for _, _, term in group}) > 1:
            findings["Normalised key collisions"].append(f"across tables: {key!r}: {locations}")
        for term in sorted({term for _, _, term in group}):
            matches = [(filename, line) for filename, line, value in group if value == term]
            if len({filename for filename, _ in matches}) > 1:
                places = ", ".join(f"{filename}:{line}" for filename, line in matches)
                findings["Duplicate entries"].append(f"across tables: {term!r}: {places}")
    return findings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="exit 1 when any non-info finding exists")
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
    errors = sum(len(items) for heading, items in findings.items() if not heading.startswith("Info:"))
    print(f"\nErrors (non-info findings): {errors}")
    return 1 if args.strict and errors else 0


if __name__ == "__main__":
    sys.exit(main())
