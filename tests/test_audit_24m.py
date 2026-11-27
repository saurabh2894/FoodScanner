"""audit-24m: species-identity audit. Fifteen rows were the same food as an existing row and are now RECOGNITION-ONLY (behaviour unchanged); the curly apostrophe reads as the straight one in alias matching."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


PAIRS = [("Jicama", "Yambean"), ("Waterchestnuts", "Chinese waterchestnuts"), ("Sapote", "Mamey sapote"), ("Redcurrants", "Red currants"), ("Mungobeans", "Mungo beans"),
         ("Winter squashes", "Winter squash"), ("Cress", "Garden cress"), ("Chrysanthemum leaves", "Garland chrysanthemum"), ("Bajra", "Pearl millet"), ("Jowar", "Sorghum"),
         ("Maize", "Corn"), ("Groundnut oil", "Peanut oil"), ("Chillies", "Chilli"), ("Rajma", "Kidney beans"), ("Moong", "Greengram")]
FORMS = ["{}", "{}, Salt", "Sugar, {}", "Dried {}", "{} (Sugar)", "Roasted {}", "{} powder"]


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("a,b", PAIRS)
def test_demoted_row_still_equals_its_twin(a, b, form):
    assert g(form.format(a)) == g(form.format(b)), (a, b, form)


@pytest.mark.parametrize("form", FORMS)
def test_curly_apostrophe_equals_straight(form):
    assert g(form.format("Jew\u2019s mallow")) == g(form.format("Jew's mallow")) == g(form.format("Jute"))
    assert g(form.format("Bishop\u2019s seed")) == g(form.format("Bishop's seed"))


def test_recognition_only_rows_are_excluded_from_the_count():
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
    from count_heads import counts
    c = counts()
    for t in ("jicama", "waterchestnuts", "sapote", "redcurrants", "mungobeans", "winter squashes", "cress", "chrysanthemum leaves", "bajra", "jowar", "maize", "groundnut oil", "chillies", "rajma", "moong"):
        assert t in c["recognition_only"], t
