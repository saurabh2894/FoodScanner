"""general-24o: eight plain heads (fruit: calamondin, marula, kiwano, rambai, yuzu, rangpur lime; vegetable: tatsoi, spiny gourd) and six English alias names, each from a named source. Every probed form equals the comparison row; every alias equals its head."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


FORMS = ["{}", "{}, Salt", "Sugar, {}", "Wheat flour, {}", "{} (5%), Water", "Rice, {}", "Dried {}", "Roasted {}", "{} (Sugar)", "{} 100%", "{} powder", "{} extract", "Instant {}", "Decaffeinated {}", "{} flavour", "{} leaves", "{} bags", "Iced {}", "{} concentrate", "Cooked {}", "{} (Salt)", "Milk, {}", "{}, Milk"]

VEGS = ["Tatsoi", "Spiny gourd"]
FRUITS = ["Calamondin", "Marula", "Kiwano", "Rambai", "Yuzu", "Rangpur lime"]
ALIASES = [("Horned melon", "Kiwano"), ("Jelly melon", "Kiwano"), ("African horned cucumber", "Kiwano"), ("Tat soi", "Tatsoi"), ("Rosette pak choi", "Tatsoi"), ("Teasel gourd", "Spiny gourd")]


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name", VEGS)
def test_veg_head_matches_okra(name, form):
    assert g(form.format(name)) == g(form.format("Okra")), (name, form)


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name", FRUITS)
def test_fruit_head_matches_guava(name, form):
    assert g(form.format(name)) == g(form.format("Guavas")), (name, form)


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name,target", ALIASES)
def test_alias_matches_head(name, target, form):
    assert g(form.format(name)) == g(form.format(target)), (name, form)


@pytest.mark.parametrize("name", VEGS + FRUITS + [a for a, _ in ALIASES])
def test_plain_group_1(name):
    assert g(name) == 1


def test_unaliased_names_stay_unrecognised():
    for t in ["Golden lime", "Spinach mustard", "Hedged gourd", "Kakrol", "Key lime"]:
        assert g(t) is None


# A word that merely ends in "no" must not read as the negation "no <marker>" (kiwano flavour, jalapeno flavour); real negations keep abstaining.
@pytest.mark.parametrize("t", ["Kiwano flavour", "Jalapeno flavour", "Casino flavour"])
def test_word_ending_in_no_is_not_a_negation(t):
    assert g(t) == g(t.replace("Kiwano", "Marula").replace("Jalapeno", "Marula").replace("Casino", "Marula")) == 4


@pytest.mark.parametrize("t", ["No flavour", "Kiwano, no flavour", "Sugar, no added flavour", "Salt, non flavour"])
def test_real_negations_still_abstain(t):
    assert g(t) is None
