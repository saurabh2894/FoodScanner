"""fssai-names-26e: two FSSAI 2.9 spice heads (cassia, ajowan) and two FSSAI 2.5 species meat heads (goat meat, buffalo meat) follow their template rows (allspice, beef); ten FSSAI/FDC same-product names are aliases. Held: tapioca flour (existing hold: main naming check treats it as starch-ambiguous), mutton, goat, buffalo (bare), mineral water, poppy seed, curry powder, onion powder, amchur."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


FORMS = ["{}", "Potato, {}, Salt", "Potato, {}, Flavour", "{}, colour (150d)", "Dried {}", "{} powder", "Smoked {}", "Canned {}", "Wheat flour, {}, Salt", "{} (Salt)"]
HEADS = [("Cassia", "Allspice"), ("Ajowan", "Allspice"), ("Goat meat", "Beef"), ("Buffalo meat", "Beef")]
ALIASES = [("Pimento", "Allspice"), ("Dried laurel", "Bay leaf"), ("Sweet basil", "Basil"), ("Sweet marjoram", "Marjoram"), ("Dehydrated tarragon", "Tarragon"), ("Bishop's weed", "Ajowan"), ("Rabbit meat", "Rabbit"), ("Drinking water", "Water"), ("Packaged drinking water", "Water"), ("Purified drinking water", "Water"), ("Pearl barley", "Barley")]


@pytest.mark.parametrize("t,ref", HEADS + ALIASES)
def test_follows_template(t, ref):
    for f in FORMS:
        assert g(f.format(t)) == g(f.format(ref)), f


@pytest.mark.parametrize("t", ["Goat meat", "Buffalo meat"])
def test_meat_rows_group_1_and_dried_group_3(t):
    assert g(t) == 1 and g("Dried " + t) == 3


@pytest.mark.parametrize("t", ["Mutton", "Goat", "Buffalo", "Curry powder", "Onion powder", "Amchur", "Meat", "Poultry"])
def test_held_names_stay_unrecognised(t):
    assert g(t) is None
