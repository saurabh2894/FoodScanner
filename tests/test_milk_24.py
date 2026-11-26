"""milk-24: camel milk head (FSSAI 2.1.2(1)(a) species identified milk; FAO Group 1 milk class-instance), same behaviour as goat milk and sheep milk in every probed form."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


FORMS = ["{}", "{}, Salt", "{}, Sugar", "Sugar, {}", "Wheat flour, {}", "{} (5%), Water", "Dried {}", "Pasteurised {}", "Flavoured {}", "{} (Sugar)", "{} 100%", "Skimmed {}", "Toned {}", "{} solids", "{} protein", "{} extract", "Hydrogenated {}", "Fermented {}", "{} (Salt)", "Milk, {}", "{} fat"]


@pytest.mark.parametrize("form", FORMS)
def test_matches_sheep_and_goat_milk(form):
    c = g(form.format("Camel milk"))
    assert c == g(form.format("Sheep milk")) == g(form.format("Goat milk")), (form, c)


def test_plain_group_1():
    assert g("Camel milk") == 1


def test_sheep_camel_milk_powder_follow_the_powder_rule():
    # CORRECTION: only goat (and cow, buffalo, plain) milk powder is routed through the milk powder rule (group 1); sheep milk powder (pinned in test_dairy_rows_1) and camel milk powder both abstain.
    assert g("Camel milk powder") == 1 and g("Sheep milk powder") == 1 and g("Goat milk powder") == 1
    for suffix in ["", " solids", " powder (maltodextrin)", " powder, sugar", " cheese"]:
        goat = g("Goat milk" + suffix)
        assert g("Camel milk" + suffix) == goat and g("Sheep milk" + suffix) == goat, suffix


def test_skim_milk_spelling_matches_skimmed_milk():
    # milk-24c: "skim" is a spelling variant of the existing descriptor "skimmed" (FSSAI 2.1 text says skimmed milk).
    for a, b in [("Skim milk", "Skimmed milk"), ("Skim milk powder", "Skimmed milk powder"), ("Skim milk, sugar", "Skimmed milk, sugar")]:
        assert g(a) == g(b), a
    assert g("Skim milk") == 1


def test_milk_solids_abstains_outside_fermented_milk():
    # milk-24e: identity-to-placement gap. FSSAI 2.1 uses milk solids only as a composition measure; 2.7 defines it for chocolate only; 2.1.13 2(a)(ii) lists dried and concentrated milk as fermented-milk raw materials (the milk plus culture rule).
    from foodscan.pipeline import analyse_text
    a = lambda x: analyse_text("Ingredients: " + x, source="text").group
    for x in ["Milk solids", "Skim milk solids", "Skimmed milk solids", "Milk solids, sugar", "Milk solids and Sugar", "Milk solids, palm oil, sugar", "Milk, milk solids", "Milk solids, Vitamin A", "Milk solids (Toned Milk)"]:
        assert a(x) is None, x
    assert a("Milk solids, Active Culture") == 1 and a("Pasteurised double toned milk, Milk solids, Active lactic cultures") == 1
    assert a("Whey protein concentrate, milk solids") == 4
