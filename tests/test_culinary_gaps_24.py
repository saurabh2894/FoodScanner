"""culinary-gaps-24: potato, rice and wheat starch (identity: USDA NALT concepts 59403, 61521, 64114; placement: FAO Group 2 starches clause) behave like the tapioca starch row. Himalayan salt, kosher salt, hemp seed oil and pumpkin seed oil were withdrawn for lack of an identity source."""
import pytest
from foodscan.pipeline import analyse_text


def res(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


FORMS = ["{}", "{}, Salt", "{}, Sugar", "Dried {}", "{} powder", "Modified {}", "Hydrogenated {}", "Smoked {}", "{} flavour", "Rice, {}", "{} (5%), Water", "Organic {}", "{} (antioxidant)", "{}, Emulsifier"]
CASES = [("Potato starch", "Tapioca starch"), ("Rice starch", "Tapioca starch"), ("Wheat starch", "Tapioca starch")]


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name,ref", CASES)
def test_matches_nearest_row(form, name, ref):
    assert res(form.format(name)) == res(form.format(ref))


def test_plain_forms_group_2():
    for n, _ in CASES:
        assert res(n) == 2


def test_neighbours_unchanged():
    assert res("Pink salt") is None and res("Cassava starch") is None and res("Sago starch") is None
    for n in ["Himalayan salt", "Kosher salt", "Hemp seed oil", "Pumpkin seed oil"]:
        assert res(n) is None, n  # withdrawn: no admissible identity source
