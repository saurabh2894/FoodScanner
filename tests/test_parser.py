from foodscan.parser import parse_ingredient_list

# Example lists from research/02-research-nova-and-ingredients.txt (synthetic).
BISCUIT = (
    "Ingredients: Refined wheat flour, sugar, edible vegetable oil (palmolein), "
    "invert syrup, raising agents (INS 500(ii), INS 503(ii)), emulsifier "
    "(INS 471), salt, added flavour (vanilla)."
)


def test_simple_single_ingredient():
    p = parse_ingredient_list("Ingredients: Whole wheat flour.")
    assert p.found and p.items == ["Whole wheat flour"] and p.terminated


def test_brackets_keep_nested_commas_together():
    p = parse_ingredient_list(BISCUIT)
    assert p.items == [
        "Refined wheat flour",
        "sugar",
        "edible vegetable oil (palmolein)",
        "invert syrup",
        "raising agents (INS 500(ii), INS 503(ii))",
        "emulsifier (INS 471)",
        "salt",
        "added flavour (vanilla)",
    ]
    assert not p.unbalanced_brackets and p.terminated


def test_pickle_list():
    p = parse_ingredient_list("Ingredients: Cucumber, water, salt, vinegar, dill.")
    assert p.items == ["Cucumber", "water", "salt", "vinegar", "dill"]


def test_truncated_text_is_not_terminated():
    p = parse_ingredient_list("Ingredients: Sugar, refined wheat flo")
    assert p.found and p.items[-1] == "refined wheat flo" and not p.terminated


def test_unbalanced_brackets_flagged():
    p = parse_ingredient_list("Ingredients: Sugar, emulsifier (INS 471")
    assert p.unbalanced_brackets


def test_no_heading_means_not_found():
    assert not parse_ingredient_list("Nutrition facts: energy 450 kcal").found
    assert not parse_ingredient_list("").found
    assert not parse_ingredient_list("Ingredients:   ").found


def test_ocr_line_breaks_and_case():
    p = parse_ingredient_list("INGREDIENTS:\nWheat flour,\nsalt,\nsugar.\nNutrition per 100g")
    assert p.items == ["Wheat flour", "salt", "sugar"]


def test_stops_at_stop_phrase_without_full_stop():
    p = parse_ingredient_list("Ingredients: Rice, salt Manufactured by XYZ Foods")
    assert p.items == ["Rice", "salt"] and p.terminated


def test_decimal_point_is_not_terminator():
    p = parse_ingredient_list("Ingredients: Sugar (12.5%), salt.")
    assert p.items == ["Sugar (12.5%)", "salt"]


def test_contains_statement_kept_as_declaration_may_contain_ignored():
    p = parse_ingredient_list(
        "Ingredients: Sugar, cocoa. Contains permitted natural colour. May contain nuts."
    )
    assert p.items == ["Sugar", "cocoa"]
    assert p.declarations == ["Contains permitted natural colour"]
    p2 = parse_ingredient_list("Ingredients: Sugar. May contain nuts.")
    assert p2.declarations == []


def test_hindi_heading():
    assert parse_ingredient_list("सामग्री: चावल, नमक").found
