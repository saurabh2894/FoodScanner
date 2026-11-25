"""indian-alias-24c: five Indian oil names paired with the English name in FSSAI Chapter 2.2 behave exactly like the English term (naming only; counted separately). 'chana' is NOT encoded: as a bare-word alias it broke 'chana dal'."""
import csv
from pathlib import Path
import pytest
from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
PAIRS = [(r["from"], r["to"]) for r in csv.DictReader((ROOT / "evaluation" / "indian_alias_24" / "aliases_c.csv").open(newline=""))]
FORMS = ["{}", "{}, Salt", "{} powder", "Sugar, {}", "Wheat flour, {}", "{} (5%), Water", "Rice, {}", "{}, Sunflower oil, Salt", "Dried {}", "Canned {}", "{} in brine", "Roasted {}", "Salted {}", "Hydrogenated {}", "{} flour", "Split {}"]


def grp(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


def test_five_pairs():
    assert [p[0] for p in PAIRS] == ["sarson ka tel", "tisi ka tel", "barrey ka tel", "gingelly oil", "til oil"]


@pytest.mark.parametrize("pair", PAIRS)
@pytest.mark.parametrize("form", FORMS)
def test_alias_matches_english(pair, form):
    a, b = pair
    assert grp(form.format(a.title())) == grp(form.format(b.title()))


def test_existing_oils_unchanged():
    assert grp("Mustard oil") == 2 and grp("Sesame oil") == 2 and grp("Linseed oil") == 2 and grp("Safflower oil") == 2


def test_rapeseed_toria_not_encoded():
    assert grp("Rapeseed oil") is None and grp("Toria oil") is None

