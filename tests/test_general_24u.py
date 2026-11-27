"""general-24u: seven Hindi-name aliases (lichi, kalimirch, mandva, til) of existing rows (IISc India Flora). Every alias equals its English head in every probed form."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


FORMS = ["{}", "{}, Salt", "Sugar, {}", "Wheat flour, {}", "{} (5%), Water", "Rice, {}", "Dried {}", "Roasted {}", "{} (Sugar)", "{} 100%", "{} powder", "{} extract", "Instant {}", "Decaffeinated {}", "{} flavour", "{} leaves", "{} bags", "Iced {}", "{} concentrate", "Cooked {}", "{} (Salt)", "Milk, {}", "{}, Milk"]

ALIASES = [("Chana", "Chickpea"), ("Imli", "Tamarind"), ("Jeera", "Cumin"), ("Lichi", "Litchis"), ("Kalimirch", "Black pepper"), ("Mandva", "Ragi"), ("Til", "Sesame seeds")]


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name,target", ALIASES)
def test_alias_matches_head(name, target, form):
    assert g(form.format(name)) == g(form.format(target)), (name, form)


@pytest.mark.parametrize("t", ["Til oil", "Imli chutney", "Kala chana", "Til laddu"])
def test_compounds_do_not_gain_a_new_placement(t):
    ans = g(t)
    assert ans is None or ans == g(t.replace("Chana", "Chickpea").replace("Til", "Sesame").replace("Imli", "Tamarind").replace("Jeera", "Cumin")), t



def test_chana_alias_leaves_chana_dal_rows_alone():
    # general-24u3: an engine guard stops a bare alias from rewriting the first word of an existing "<term> dal" row.
    assert g("Chana") == g("Chickpea") == 1
    assert g("Chana dal") == 1 and g("Chana dal, Salt") == 3 and g("Bengal gram dal") == 1
    assert g("Roasted chana") == g("Roasted chickpea")


@pytest.mark.parametrize("t", ["Kala jeera", "Shahi jeera", "Jeera powder", "Imli chutney"])
def test_imli_jeera_compounds_abstain(t):
    assert g(t) is None
