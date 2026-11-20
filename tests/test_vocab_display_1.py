"""Tests for Task 2: Vocabulary and Display Data Expansion 1."""
import csv
from pathlib import Path
import pytest

from foodscan.normalise import normalise_ingredient
from foodscan.pipeline import analyse_text
from foodscan.roles import declared_roles
from foodscan.tables import load_table

ROOT = Path(__file__).resolve().parent.parent


def test_package_1_spelling_synonyms():
    # US spelling variant
    assert normalise_ingredient("iodized salt").name == "iodised salt"
    # open compound variant
    assert normalise_ingredient("cotton seed oil").name == "cottonseed oil"
    # refined oil phrasing variant
    assert normalise_ingredient("refined palmolein oil").name == "palmolein"


def test_package_2_ins_display_names():
    rows = {r["ins"]: r for r in load_table("ins_names.csv")}
    added_codes = ["202", "260", "339(ii)", "407", "412", "415", "466", "476", "500(i)", "501(i)", "551", "1422"]
    for code in added_codes:
        assert code in rows, f"missing INS code {code}"
        assert "JECFA" in rows[code]["source"]
        assert "Codex" not in rows[code]["source"]
        assert "Display name only: no rule, no group effect" in rows[code]["source"]

    # Test that display names appear on unmapped codes without altering group
    a = analyse_text("Ingredients: Rice, Preservative (INS 202), salt.", source="text")
    u = next(x for x in a.ins_mappings if x.code == "202")
    assert u.ref_name == "Potassium Sorbate"
    assert u.name is None  # no marker decision row


def test_package_3_declared_roles():
    roles = {r["term"]: r for r in load_table("declared_roles.csv")}
    assert "sequestrant" in roles
    assert roles["sequestrant"]["nova_status"] == "not_named"
    assert "dough conditioner" in roles
    assert roles["dough conditioner"]["nova_status"] == "not_named"

    # Test label phrasing gets declared roles
    u = next(x for x in analyse_text("Ingredients: Rice, sequestrant - E385, salt.", source="text").ins_mappings if x.code == "385")
    assert u.declared_roles == ("sequestrant",)
    assert any("not named in the NOVA source read" in note for note in u.role_notes)
