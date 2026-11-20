"""ins_reference.csv (Codex CXG 36 2026): display data for codes ins_map.csv does not decide on. It never changes a group."""
import csv
from pathlib import Path

from foodscan.normalise import normalise_ingredient
from foodscan.pipeline import analyse_text

import pytest

from foodscan import normalise
from foodscan.tables import has_table

REF = Path(__file__).resolve().parent.parent / "data/pending/ins_reference.csv"   # not shipped while its licence is unresolved


@pytest.fixture
def with_reference(monkeypatch):
    """Use the pending table for display tests; a release without it must behave as if it did not exist."""
    data = {normalise.canonical_code(r["ins"]): r for r in csv.DictReader(REF.open(encoding="utf-8"))}
    monkeypatch.setattr(normalise, "_ins_reference", lambda: data)


def test_reference_table_is_not_shipped_while_its_licence_is_unresolved():
    assert not has_table("ins_reference.csv")
    (u,) = normalise_ingredient("stabilizer (INS 412)").ins
    assert u.name is None and u.ref_name is None and u.strength is None


def rows():
    return list(csv.DictReader(REF.open(encoding="utf-8")))


def test_every_row_carries_source_and_reading():
    for r in rows():
        assert r["source"].startswith("Codex CXG 36-1989") and r["reading"] and r["functional_classes"]


def test_unmapped_code_gets_display_name_but_no_decision_strength(with_reference):
    (u,) = normalise_ingredient("stabilizer (INS 412)").ins
    assert u.name is None and u.strength is None and u.ref_name == "Guar gum" and "thickener" in u.ref_classes


def test_partial_reading_is_flagged(with_reference):
    (u,) = normalise_ingredient("raising agent (INS 500(i))").ins
    assert u.ref_name == "Sodium carbonate" and u.ref_partial


def test_mapped_code_keeps_its_decision_row():
    (u,) = normalise_ingredient("colour (INS 102)").ins
    assert u.name == "tartrazine" and u.ref_name is None


def test_reference_data_cannot_make_a_group(with_reference):
    # INS 412 (guar gum) is listed in the reference but not mapped: stays "not in local mapping", so no Group 4 from it
    a = analyse_text("Ingredients: Rice, stabilizer (INS 412), salt.")
    assert a.group != 4


def test_unknown_code_has_no_reference(with_reference):
    (u,) = normalise_ingredient("preservative (INS 7777)").ins
    assert u.ref_name is None
