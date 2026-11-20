"""Scope of the provisional declared-colour marker (research/04). No rule is added: these pin down existing behaviour."""
from foodscan.pipeline import analyse_text


def a(t):
    return analyse_text(t, source="text")


def test_declared_natural_colour_is_still_a_marker_provisionally():
    r = a("Ingredients: Milk fat, salt, natural colour (annatto).")
    assert r.group == 4 and any('"colour"' in d.detail for d in r.drivers)


def test_plain_and_salted_butter_do_not_trigger_the_colour_marker():
    for t in ("Ingredients: Butter.", "Ingredients: Milk fat, salt.", "Ingredients: Butter, salt."):
        r = a(t)
        assert not any("colour" in d.detail for d in r.drivers), t
        assert r.group != 4, t


def test_coloured_whole_ingredients_are_never_read_as_an_additive():
    for t in ("Ingredients: Milk fat, salt, annatto.", "Ingredients: Rice, turmeric, beetroot powder, saffron."):
        r = a(t)
        assert not any("colour" in d.detail for d in r.drivers) and r.group != 4, t


def test_undeclared_function_stays_visible_as_not_assessed():
    r = a("Ingredients: Milk fat, salt, annatto extract.")
    assert not r.answered and "annatto extract" in r.unassessed
