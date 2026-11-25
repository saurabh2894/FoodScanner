"""indian-alias-24b: five Indian pulse names paired with the English name in the FSSAI pulses standard behave exactly like the English term (naming only; counted separately). 'chana' is NOT encoded: as a bare-word alias it broke 'chana dal'."""
import csv
from pathlib import Path
import pytest
from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
PAIRS = [(r["from"], r["to"]) for r in csv.DictReader((ROOT / "evaluation" / "indian_alias_24" / "aliases_b.csv").open(newline=""))]
FORMS = ["{}", "{}, Salt", "{} powder", "Sugar, {}", "Wheat flour, {}", "{} (5%), Water", "Rice, {}", "{}, Sunflower oil, Salt", "Dried {}", "Canned {}", "{} in brine", "Roasted {}", "Salted {}", "Hydrogenated {}", "{} flour", "Split {}"]


def grp(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


def test_five_pairs():
    assert [p[0] for p in PAIRS] == ["masur", "urd", "lobia", "matki", "matra"]


@pytest.mark.parametrize("pair", PAIRS)
@pytest.mark.parametrize("form", FORMS)
def test_alias_matches_english(pair, form):
    a, b = pair
    assert grp(form.format(a.title())) == grp(form.format(b.title()))


def test_existing_dal_rows_unchanged():
    assert grp("Chana dal") == 1 and grp("Chana dal, Salt") == 3 and grp("Masoor dal") == 1 and grp("Urad dal") == 1 and grp("Urd beans") == 1 and grp("Black gram") == 1


def test_chana_not_encoded():
    assert grp("Chana") is None
