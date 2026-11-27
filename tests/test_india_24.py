"""india-24 (India-relevant): pointed gourd, cluster beans and bael heads (FAO Group 1 placement; Purdue NewCROP and PROSEA identity) and aliases parwal, palwal, parmal, cluster bean, bengal quince. Every probed form equals the comparison row."""
import pytest
from foodscan.pipeline import analyse_text


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


FORMS = ["{}", "{}, Salt", "Sugar, {}", "Wheat flour, {}", "{} (5%), Water", "Rice, {}", "Dried {}", "Roasted {}", "{} (Sugar)", "{} 100%", "{} powder", "{} extract", "Instant {}", "Decaffeinated {}", "{} flavour", "{} leaves", "{} bags", "Iced {}", "{} concentrate", "Cooked {}", "{} (Salt)", "Milk, {}", "{}, Milk"]


ALIASES = [('Parwal', 'Pointed gourd'), ('Palwal', 'Pointed gourd'), ('Parmal', 'Pointed gourd'), ('Cluster bean', 'Cluster beans'), ('Bengal quince', 'Bael'), ('Star fruit', 'Carambola'), ('Starfruit', 'Carambola'), ('Karonda', 'Karanda'), ('Karaunda', 'Karanda'), ('Sweetsop', 'Sugar apples'), ('Sweetsops', 'Sugar apples'), ('Pomelo', 'Pummelo')]


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name,target", ALIASES)
def test_alias_matches_target(name, target, form):
    assert g(form.format(name)) == g(form.format(target)), (name, form)


@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("name", ["Pointed gourd", "Cluster beans", "Elephant yam", "Fenugreek leaves"])
def test_new_vegetable_head_matches_okra(name, form):
    assert g(form.format(name)) == g(form.format("Okra")), (name, form)


@pytest.mark.parametrize("form", FORMS)
def test_bael_matches_a_plain_fruit_row(form):
    assert g(form.format("Bael")) == g(form.format("Cantaloupe melons")), form
    assert g(form.format("Karanda")) == g(form.format("Cantaloupe melons")), form
    assert g(form.format("Indian jujube")) == g(form.format("Cantaloupe melons")), form
    assert g(form.format("Citron")) == g(form.format("Cantaloupe melons")), form
    assert g(form.format("Phalsa")) == g(form.format("Cantaloupe melons")), form


@pytest.mark.parametrize("name", ["Pointed gourd", "Cluster beans", "Bael", "Karanda", "Phalsa", "Elephant yam", "Fenugreek leaves", "Indian jujube", "Citron"] + [a for a, _ in ALIASES])
def test_plain_group_1(name):
    assert g(name) == 1


@pytest.mark.parametrize("name", ["Guar", "Guar gum", "Wood apple", "Sirphal", "Elephant foot yam", "Konjac", "Konjac flour"])
def test_deliberately_unaliased_names_do_not_take_group_1(name):
    assert g(name) != 1


def test_bare_fenugreek_is_unchanged_by_the_leaf_row():
    # india-24e: the seed and spice row keeps its prior behaviour
    assert g("Fenugreek") is None
    assert g("Fenugreek seeds") == g("Fenugreek seed")


def test_fenugreek_leaves_are_not_the_seed_row():
    from foodscan.normalise import normalise_ingredient
    assert normalise_ingredient("fenugreek leaves").name == "fenugreek leaves"
    assert normalise_ingredient("fenugreek seeds").name == "fenugreek"


def test_indian_jujube_is_its_own_row_and_ber_is_aliased_to_it_from_general_24k():
    from foodscan.normalise import normalise_ingredient
    assert normalise_ingredient("indian jujube").name == "indian jujube"
    assert normalise_ingredient("jujube").name != "indian jujube"
    # general-24k: the old pin (ber not aliased) predates a naming source. IISc India Flora Online (https://indiaflora-ces.iisc.ac.in/herbsheet.php?cat=13&id=12608) gives "Ber (Hindi)" for Ziziphus mauritiana, common names Common Jujube, Indian Jujube. Plain fruit either way (both rows Group 1).
    assert g("Ber") == g("Indian jujube") == 1


@pytest.mark.parametrize("form", FORMS)
def test_star_anise_behaves_like_the_other_spice_rows(form):
    # india-24h: recognition-level spice row; every form equals the existing aniseed row, and star anise is not aniseed
    assert g(form.format("Star anise")) == g(form.format("Aniseed")), form
    assert g(form.format("Chinese star anise")) == g(form.format("Star anise")), form


def test_star_anise_is_recognised_and_not_the_aniseed_row():
    from foodscan.normalise import normalise_ingredient
    assert normalise_ingredient("star anise").name == "star anise"
    assert normalise_ingredient("aniseed").name == "aniseed"
    assert normalise_ingredient("chinese star anise").name == "star anise"
