"""fssai-names-26h: five generic Group 1 heads named verbatim by the sources (wheat grits, cassava grits, oat grits: FAO Table 1 Group 1 "grits, flakes or flour made from corn, wheat, oats, or cassava"; dried fruit: FAO "dried fruit"; herbal infusion: Brazilian Guidelines and Martinez Steele 2023 "tea, herbal infusions, coffee") plus three aliases. The old synthetic hold on "Herbal Tea" is reversed here with the evidence stated in the row; named herbs (chamomile, hibiscus) stay unrecognised."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


FORMS = ["{}", "Potato, {}, Salt", "Potato, {}, Flavour", "{}, colour (150d)", "{} powder", "Smoked {}", "Canned {}", "Wheat flour, {}, Salt", "{} (Salt)", "{}, Sugar", "{}, Milk"]


@pytest.mark.parametrize("t,ref", [("Wheat grits", "Corn grits"), ("Cassava grits", "Corn grits"), ("Oat grits", "Corn grits"), ("Dried fruit", "Dried apricots"), ("Dried fruits", "Dried apricots"), ("Herbal infusion", "Tea"), ("Herbal tea", "Tea"), ("Long-life milk", "Milk")])
def test_follows_template(t, ref):
    for f in FORMS:
        assert g(f.format(t)) == g(f.format(ref)), f


@pytest.mark.parametrize("t", ["Wheat grits", "Cassava grits", "Oat grits", "Dried fruit", "Herbal infusion", "Herbal tea", "Long-life milk"])
def test_plain_forms_group_1(t):
    assert g(t) == 1


@pytest.mark.parametrize("t", ["Chamomile tea", "Hibiscus tea", "Instant herbal tea", "Herbal infusion powder", "Sweetened dried fruit", "Candied dried fruit", "Dried fruit and nuts", "Tapioca flour", "Fruit juice"])
def test_neighbours_stay_unrecognised(t):
    assert g(t) is None
