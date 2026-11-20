from foodscan.classify import classify_items
from foodscan.parser import parse_ingredient_list


def cls(text):
    p = parse_ingredient_list(text)
    return classify_items(p.items, p.declarations)


# --- research/02 synthetic examples -------------------------------------------------
def test_group1_whole_wheat_flour():
    r = cls("Ingredients: Whole wheat flour.")
    assert r.group == 1


def test_group4_biscuit_example_drivers():
    r = cls(
        "Ingredients: Refined wheat flour, sugar, edible vegetable oil (palmolein), "
        "invert syrup, raising agents (INS 500(ii), INS 503(ii)), emulsifier "
        "(INS 471), salt, added flavour (vanilla)."
    )
    assert r.group == 4
    driven = " | ".join(d.ingredient + d.detail for d in r.drivers)
    assert "invert syrup" in driven and "emulsifier" in driven and "added flavour" in driven
    # weak markers (raising agents) are not reported as drivers of a group 4 call
    assert not any("raising" in d.ingredient for d in r.drivers)
    assert all(d.source for d in r.drivers)


def test_group3_pickle_example():
    assert cls("Ingredients: Cucumber, water, salt, vinegar, dill.").group == 3


# --- group 4 markers ---------------------------------------------------------------
def test_each_class1_substance_is_group4():
    for ing in ["maltodextrin", "dextrose", "modified starch", "soy protein isolate",
                "high fructose corn syrup", "interesterified vegetable oil",
                "edible vegetable oil (hydrogenated)"]:
        assert cls(f"Ingredients: Rice, {ing}.").group == 4, ing


def test_cosmetic_classes_group4_even_with_unmapped_ins():
    assert cls("Ingredients: Water, sweetener (INS 950), salt.").group == 4
    assert cls("Ingredients: Water, colour (INS 150d), sugar.").group == 4
    assert cls("Ingredients: Milk, flavour enhancer (INS 621).").group == 4


def test_single_flavour_is_enough_for_group4():
    assert cls("Ingredients: Rice, added flavour (vanilla).").group == 4


def test_contains_statement_marker_counts():
    r = cls("Ingredients: Cucumber, salt. Contains permitted natural colour.")
    assert r.group == 4 and "Contains" in r.drivers[0].detail


# --- weak / unlisted markers -> uncertain -----------------------------------------
def test_pectin_alone_is_uncertain_not_group4():
    r = cls("Ingredients: Mango, sugar, pectin (INS 440).")
    assert r.group is None and "weak" in r.reason


def test_pectin_declared_as_gelling_agent_not_cosmetic():
    assert cls("Ingredients: Mango, sugar, gelling agent (pectin INS 440).").group is None


def test_other_gelling_agent_is_cosmetic_strong():
    assert cls("Ingredients: Mango, sugar, gelling agent (INS 407).").group == 4


def test_raising_agents_only_uncertain():
    assert cls("Ingredients: Whole wheat flour, raising agents (INS 500(ii)).").group is None


def test_unlisted_additive_class_uncertain():
    assert cls("Ingredients: Cucumber, salt, preservative (INS 211).").group is None


def test_unknown_ins_without_class_word_uncertain():
    assert cls("Ingredients: Cucumber, salt, INS 999.").group is None


# --- limits of ingredient lists ----------------------------------------------------
def test_no_ingredient_count_rule_long_list_of_foods_not_forced_to_4():
    r = cls("Ingredients: Cucumber, tomato, onion, carrot, salt, vinegar, dill, turmeric, cumin, garlic, water.")
    assert r.group == 3


def test_short_list_can_be_group4():
    assert cls("Ingredients: Sugar, maltodextrin.").group == 4


def test_flour_based_list_without_markers_is_uncertain():
    r = cls("Ingredients: Whole wheat flour, water, salt, yeast.")
    assert r.group is None


def test_unrecognised_ingredient_is_uncertain():
    r = cls("Ingredients: Rice, jackfruit seed paste.")
    assert r.group is None and "jackfruit" in r.reason


def test_single_culinary_is_group2():
    assert cls("Ingredients: Salt.").group == 2


def test_herbs_only_uncertain():
    assert cls("Ingredients: Dill, turmeric.").group is None


def test_never_returns_a_health_word():
    for t in ["Ingredients: Salt.", "Ingredients: Sugar, maltodextrin.", "Ingredients: Dill."]:
        r = cls(t)
        blob = (r.reason or "") + " ".join(d.detail for d in r.drivers)
        assert not any(w in blob.lower() for w in ("healthy", "unhealthy", "unsafe", "should not"))


def test_ins171_titanium_dioxide_is_strong_marker():
    r = cls("Ingredients: Sugar, gelatin substitute (INS 171).")
    assert r.group == 4 and any("171" in d.detail for d in r.drivers)


def test_ins211_alone_stays_uncertain():
    r = cls("Ingredients: Cucumber, salt, preservative (INS 211).")
    assert r.group is None and "211" in r.reason


def test_approved_colour_and_sweetener_codes_are_strong_markers_without_class_word():
    for code in ("102", "110", "150d", "950"):
        r = cls(f"Ingredients: Water, sugar, INS {code}.")
        assert r.group == 4, code
        assert any(code in d.detail for d in r.drivers)


def test_approved_codes_carry_names_and_sources():
    from foodscan.normalise import normalise_ingredient

    names = {c: normalise_ingredient(f"INS {c}").ins[0] for c in ("102", "110", "150d", "950")}
    assert names["102"].name == "tartrazine" and names["110"].name == "sunset yellow FCF"
    assert names["150d"].name.startswith("caramel IV") and names["950"].name == "acesulfame potassium"
    assert all("Project decision" in u.source for u in names.values())
