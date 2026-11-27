"""Provenance completeness: an unescaped inner double quote used to split a source across extra CSV fields, so the loader (DictReader, 3-column header) kept only a truncated source. Every row must have exactly 3 fields, or 5 where the last two are a trailing id and batch tag."""
import csv
import re
from pathlib import Path

RES = Path(__file__).resolve().parents[1] / "src" / "foodscan" / "resources"


def _bad(name):
    out = []
    with (RES / name).open(newline="") as f:
        for n, r in enumerate(csv.reader(f), 1):
            if len(r) == 3:
                continue
            if len(r) == 5 and re.fullmatch(r"[\w:;.\-]+", r[3]) and re.fullmatch(r"[\w\-]+", r[4]):
                continue
            out.append((n, len(r), r[0]))
    return out


def test_lexicon_rows_not_split():
    assert _bad("lexicon.csv") == []


def test_synonyms_rows_not_split():
    assert _bad("synonyms.csv") == []


def test_repaired_sources_are_complete():
    with (RES / "lexicon.csv").open(newline="") as f:
        rows = {r["term"]: r["source"] for r in csv.DictReader(f)}
    assert rows["calamansi"].rstrip().endswith("are not placed by this row.")
    assert rows["rajma"].rstrip().endswith("plain dals as group 1")


def test_no_alias_maps_to_two_targets():
    seen = {}
    with (RES / "synonyms.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            seen.setdefault(r["from"].lower(), set()).add(r["to"])
    assert {k: v for k, v in seen.items() if len(v) > 1} == {}
