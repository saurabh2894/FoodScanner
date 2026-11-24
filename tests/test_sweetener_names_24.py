"""sweetener-names-24: named artificial sweeteners are strong cosmetic_additive markers (FAO 2019 p.10 names aspartame, cyclamate and stevia-derived compounds as examples of the sweetener class)."""
import csv
from pathlib import Path
import pytest
from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
TERMS = [r["term"] for r in csv.DictReader((ROOT / "evaluation" / "sweetener_names_24" / "markers_candidate_rows.csv").open(newline=""))]


def run(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.answered, a.group


def test_staged_terms():
    assert TERMS == ["aspartame", "cyclamate", "sodium cyclamate", "steviol glycosides", "sucralose", "acesulfame", "saccharin"]


@pytest.mark.parametrize("t", ["Wheat flour, Salt, {}", "Water, {}", "Wheat flour, Sugar, {} (Sweetener)", "Wheat flour, {} (INS 950)"])
@pytest.mark.parametrize("name", ["Aspartame", "Sodium cyclamate", "Sucralose", "Acesulfame potassium", "Saccharin", "Steviol glycosides"])
def test_named_sweetener_is_group_4(t, name):
    assert run(t.format(name)) == (True, 4)


def test_plain_foods_and_unnamed_stevia_do_not_move():
    assert run("Wheat flour, Salt") == (False, None)
    assert run("Stevia") != (True, 4)
    assert run("Jaggery") != (True, 4)
