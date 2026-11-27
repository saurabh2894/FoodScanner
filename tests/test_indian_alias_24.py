"""indian-alias-24: twelve Indian spice names paired with the English name in FSSAI Chapter 2.9 section headings behave exactly like the English term (naming only, no placement; counted separately from heads)."""
import csv
from pathlib import Path
import pytest
from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
PAIRS = [(r["from"], r["to"]) for r in csv.DictReader((ROOT / "evaluation" / "indian_alias_24" / "aliases.csv").open(newline=""))]
FORMS = ["{}", "{}, Salt", "{} powder", "Sugar, {}", "Wheat flour, {}", "{} (5%), Water", "Rice, {}", "Milk, Sugar, {}", "{}, Sunflower oil, Salt", "Dried {}", "Hydrogenated {}", "{} flavour"]


def res(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return (a.group if a.answered else None, a.reason)


def test_twelve_pairs():
    assert len(PAIRS) == 12 and len({p[0] for p in PAIRS}) == 12


@pytest.mark.parametrize("pair", PAIRS)
@pytest.mark.parametrize("form", FORMS)
def test_alias_matches_english(pair, form):
    a, b = pair
    ra, rb = res(form.format(a.title())), res(form.format(b.title()))
    assert ra[0] == rb[0]


def test_ambiguous_names_stay_unrecognised():
    # methi (seed or leaf), sarson/rai (seed, greens or oil), taj, kalonji: not encoded, leads only
    for n in ["Methi, Salt", "Sarson, Salt", "Taj, Salt", "Kalonji, Salt"]:
        assert "not in the local vocabulary" in res(n)[1]
