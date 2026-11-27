"""general-24p: ackee (fruit, PROTA identity, FAO Group 1 fruit clause). Plain and plain-form variants equal the guava row; canned, brined and sweetened forms are asserted separately against guava as well."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


FORMS = ["{}", "{}, Salt", "Sugar, {}", "Wheat flour, {}", "{} (5%), Water", "Rice, {}", "Dried {}", "Roasted {}", "{} (Sugar)", "{} 100%", "{} powder", "{} extract", "Instant {}", "Decaffeinated {}", "{} flavour", "{} leaves", "{} bags", "Iced {}", "{} concentrate", "Cooked {}", "{} (Salt)", "Milk, {}", "{}, Milk"]

FRUITS = ["Ackee", "Lingonberry", "Medlar"]


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name", FRUITS)
def test_head_matches_guava(name, form):
    assert g(form.format(name)) == g(form.format("Guavas")), (name, form)


@pytest.mark.parametrize("t", ["Ackee", "Ackee, Salt", "Canned ackee", "Ackee in brine", "Sweetened ackee", "Ackee (Sugar)"])
def test_ackee_separate_forms_equal_guava_forms(t):
    assert g(t) == g(t.replace("ackee", "guavas").replace("Ackee", "Guavas")), t


@pytest.mark.parametrize("name", FRUITS)
def test_plain_group_1(name):
    assert g(name) == 1


def test_unaliased_names_stay_unrecognised():
    for t in ["Akee", "Mountain cranberry", "Cowberry", "Japanese medlar"]:
        assert g(t) is None


@pytest.mark.parametrize("form", FORMS)
def test_pineapple_guava_alias_matches_feijoa(form):
    assert g(form.format("Pineapple guava")) == g(form.format("Feijoa")), form


def test_pineapple_and_guava_separate_words_stay_unrecognised():
    assert g("Pineapple, Guava") is None
