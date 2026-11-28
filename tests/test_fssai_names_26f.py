"""fssai-names-26f: poppy seed is a spice-class head (FAO Group 1 herbs and spices, FSSAI 2.9.16 identity) that follows the allspice template; mineral water recognises as plain water (Martinez Steele 2023 Table 1 Group 1, FSSAI 2.10.7); asafoetida and iodised salt got real sources with placement unchanged."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


FORMS = ["{}", "Potato, {}, Salt", "Potato, {}, Flavour", "{}, colour (150d)", "Dried {}", "{} powder", "Smoked {}", "Canned {}", "Wheat flour, {}, Salt", "{} (Salt)"]


@pytest.mark.parametrize("t,ref", [("Poppy seed", "Allspice"), ("Poppy seeds", "Allspice"), ("Khas khas", "Allspice"), ("Mineral water", "Water"), ("Natural mineral water", "Water")])
def test_follows_template(t, ref):
    for f in FORMS:
        assert g(f.format(t)) == g(f.format(ref)), f


@pytest.mark.parametrize("t", ["Carbonated mineral water", "Flavoured mineral water", "Mineral water, sugar, flavour"])
def test_mineral_water_forms_never_exceed_water_forms(t):
    # abstaining is allowed (the alias does not rewrite inside "carbonated mineral water"); a different group is not
    assert g(t) in (None, g(t.replace("mineral water", "water").replace("Mineral water", "Water")))


def test_poppy_alone_abstains_and_oil_unchanged():
    assert g("Poppy seed") is None and g("Poppy seed oil") == 2


def test_compounded_asafoetida_stays_unrecognised_and_salt_unchanged():
    assert g("Compounded asafoetida") is None and g("Iodised salt") == 2 and g("Rice, asafoetida, salt") == 3
