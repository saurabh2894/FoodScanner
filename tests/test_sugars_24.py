"""sugars-24: misri head (FSSAI 2.8 sole-product naming; FAO Group 2 sugar class-instance); mishri spelling alias. Golden syrup and dried glucose syrup not encoded (Group 4 markers)."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


@pytest.mark.parametrize("t", ["Misri", "Mishri"])
def test_plain_group_2(t):
    assert g(t) == 2


@pytest.mark.parametrize("f", ["{}", "{}, Salt", "Sugar, {}", "Wheat flour, {}", "{} (5%), Water", "{} powder", "{} (Sugar)", "Hydrogenated {}", "{} syrup", "{} flavour", "{} 100%", "Dried {}", "{} extract"])
def test_alias_matches_target(f):
    assert g(f.format("Mishri")) == g(f.format("Misri"))


def test_unencoded():
    assert g("Golden syrup") is None and g("Glucose syrup") == 4
