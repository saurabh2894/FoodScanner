"""general-24t: five Hindi-name aliases (kaju, akhrot, badam, kajur, ananas) of existing rows (IISc India Flora). Every alias equals its English head in every probed form."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


FORMS = ["{}", "{}, Salt", "Sugar, {}", "Wheat flour, {}", "{} (5%), Water", "Rice, {}", "Dried {}", "Roasted {}", "{} (Sugar)", "{} 100%", "{} powder", "{} extract", "Instant {}", "Decaffeinated {}", "{} flavour", "{} leaves", "{} bags", "Iced {}", "{} concentrate", "Cooked {}", "{} (Salt)", "Milk, {}", "{}, Milk"]

ALIASES = [("Kaju", "Cashew nuts"), ("Akhrot", "Walnuts"), ("Badam", "Almonds"), ("Kajur", "Dates"), ("Ananas", "Pineapple"), ("Hing", "Asafoetida")]


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name,target", ALIASES)
def test_alias_matches_head(name, target, form):
    assert g(form.format(name)) == g(form.format(target)), (name, form)


@pytest.mark.parametrize("t", ["Badam milk", "Kaju katli", "Ananas juice", "Badam oil", "Khajur"])
def test_compounds_and_unsourced_spellings_do_not_gain_a_new_placement(t):
    ans = g(t)
    assert ans is None or ans == g(t.replace("Badam", "Almond").replace("Kaju", "Cashew").replace("Ananas", "Pineapple")), t


def test_compounded_asafoetida_and_hingra_stay_unrecognised():
    for t in ["Compounded asafoetida", "Hingra", "Bandhani hing"]:
        assert g(t) is None
