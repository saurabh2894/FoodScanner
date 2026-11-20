"""Tests for Task 2: Vocabulary and Display Data Expansion 1."""
from pathlib import Path
import pytest

from foodscan.normalise import normalise_ingredient
from foodscan.pipeline import analyse_text
from foodscan.roles import declared_roles
from foodscan.tables import load_table

ROOT = Path(__file__).resolve().parent.parent


def test_package_1_spelling_synonyms():
    # OCR typo variants
    assert normalise_ingredient("lodised salt").name == "iodised salt"
    assert normalise_ingredient("lodized salt").name == "iodised salt"
    # US spelling variant
    assert normalise_ingredient("iodized salt").name == "iodised salt"
    # open compound variant
    assert normalise_ingredient("cotton seed oil").name == "cottonseed oil"
    # refined oil phrasing variant
    assert normalise_ingredient("refined palmolein oil").name == "palmolein"


def test_package_2_ins_display_names():
    rows = {r["ins"]: r for r in load_table("ins_names.csv")}
    added_codes = ["202", "260", "339(ii)", "412", "415", "466", "476", "500(i)", "501(i)", "551", "1422"]      # 407 withheld pending the sourced family-exception fix (BACKLOG.md)
    for code in added_codes:
        assert code in rows, f"missing INS code {code}"
        name = rows[code]["name"]
        source = rows[code]["source"]
        # Assert non-empty, single-spaced display name
        assert name and name.strip() == name, f"name for {code} is empty or unstripped"
        assert "  " not in name, f"name for {code} has double spaces: {name!r}"
        # Assert source note contains JECFA URL
        assert "https://www.fao.org/food/food-safety-quality/scientific-advice/jecfa/jecfa-additives/detail/en/c/" in source, f"source for {code} missing JECFA URL"
        assert "Display name only: no rule, no group effect" in source

    # Test that display names appear on unmapped codes without altering group
    a = analyse_text("Ingredients: Rice, Preservative (INS 202), salt.", source="text")
    u = next(x for x in a.ins_mappings if x.code == "202")
    assert u.ref_name == "Potassium Sorbate"
    assert u.name is None  # no marker decision row


def test_package_2_name_tie_hints():
    # Assert name-tie misread hint fires correctly for Guar gum (INS 415) and Xanthan gum (INS 412)
    r_guar = analyse_text("Ingredients: Water, Guar gum (INS 415).", source="text")
    assert any("Read as INS 415. The label text says Guar gum, and the source page for guar gum gives INS 412" in w for w in r_guar.warnings)

    r_xanthan = analyse_text("Ingredients: Water, Xanthan gum (INS 412).", source="text")
    assert any("Read as INS 412. The label text says Xanthan gum, and the source page for xanthan gum gives INS 415" in w for w in r_xanthan.warnings)

    # 407 (carrageenan) is withheld from ins_names.csv: without that row the name-tie hint cannot fire on the legitimate 407a family code.
    assert "407" not in {r["ins"] for r in load_table("ins_names.csv")}
    r_carr = analyse_text("Ingredients: Water, Carrageenan (INS 407a).", source="text")
    assert not any("Read as INS" in w for w in r_carr.warnings)


def test_package_3_declared_roles():
    roles = {r["term"]: r for r in load_table("declared_roles.csv")}
    assert "sequestrant" in roles
    assert roles["sequestrant"]["nova_status"] == "not_named"
    assert "dough conditioner" in roles
    assert roles["dough conditioner"]["nova_status"] == "not_named"
    assert "thickening & stabilizing agents" not in roles

    # Test label phrasing gets declared roles
    u = next(x for x in analyse_text("Ingredients: Rice, sequestrant - E385, salt.", source="text").ins_mappings if x.code == "385")
    assert u.declared_roles == ("sequestrant",)
    assert any("not named in the NOVA source read" in note for note in u.role_notes)
