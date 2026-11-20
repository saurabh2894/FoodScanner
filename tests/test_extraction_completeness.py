"""Priority 3 of the first unseen-label evaluation: nothing should hide inside a merged or unread line.

Fixtures are SYNTHETIC wordings of my own (the evaluated labels are not used for development).
"""
import pytest

from foodscan.normalise import normalise_ingredient
from foodscan.parser import parse_ingredient_list, split_top_level_and
from foodscan.pipeline import analyse_text


def items(text, **kw):
    return analyse_text(text, **kw).ingredients


# ---- "and" pairs ------------------------------------------------------------------------------------------------
def test_two_additives_joined_by_and_become_two_items():
    a = analyse_text("Ingredients: wheat flour, emulsifier [472e] and flour treatment agent [1101(ii)], salt.")
    assert a.ingredients == ["wheat flour", "emulsifier [472e]", "flour treatment agent [1101(ii)]", "salt"]
    assert {"472e", "1101(ii)"} <= {u.code for u in a.ins_mappings}


def test_square_bracket_codes_after_a_class_word_are_read():
    codes = [u.code for u in normalise_ingredient("raising agents [500(ii), 503(ii)]").ins]
    assert codes == ["500(ii)", "503(ii)"]
    assert [u.code for u in normalise_ingredient("Colour [150d]").ins] == ["150d"]


@pytest.mark.parametrize("pair, expected", [
    ("salt and sugar", ["salt", "sugar"]),
    ("sugar & salt", ["sugar", "salt"]),
    ("antioxidant (INS 392) and acidity regulator (INS 330)", ["antioxidant (INS 392)", "acidity regulator (INS 330)"]),
    ("emulsifiers (471) & raising agents (500(ii))", ["emulsifiers (471)", "raising agents (500(ii))"]),
])
def test_pairs_of_ingredients_are_split(pair, expected):
    assert items(f"Ingredients: rice, {pair}, water.")[1:-1] == expected


@pytest.mark.parametrize("not_a_pair", [
    "Spices and Condiments", "Natural and Nature Identical Flavours", "Vegetables and Spices (Onion, Garlic)", "milk and cream",
    "Spices & Condiments", "mono and diglycerides of fatty acids", "salt and jackfruit",
])
def test_phrases_that_are_not_two_ingredients_are_kept_whole(not_a_pair):
    assert not_a_pair in items(f"Ingredients: rice, {not_a_pair}, water.")


def test_and_inside_brackets_is_not_a_pair():
    got = items("Ingredients: rice, colour (INS 102 and INS 110), water.")
    assert got == ["rice", "colour (INS 102 and INS 110)", "water"]


def test_split_top_level_and_ignores_brackets():
    assert split_top_level_and("a (b and c) and d") == ["a (b and c)", "d"]
    assert split_top_level_and("plain") == ["plain"]
    assert split_top_level_and("x & y and z") == ["x", "y", "z"]


def test_split_pairs_keep_their_section():
    a = analyse_text("Ingredients: Noodles: wheat flour, salt and sugar. Masala: emulsifier [472e] and flour treatment agent [1101(ii)].")
    assert [(label, its) for label, its in a.sections] == [
        ("Noodles", ["wheat flour", "salt", "sugar"]), ("Masala", ["emulsifier [472e]", "flour treatment agent [1101(ii)]"])]


# ---- Contains lines ---------------------------------------------------------------------------------------------
def test_every_contains_sentence_is_read_not_only_the_first():
    p = parse_ingredient_list("Ingredients: Rice, salt. Contains soy. Contains permitted colour. Manufactured by X.")
    assert p.declarations == ["Contains soy", "Contains permitted colour"]


def test_contains_after_an_allergen_label_and_on_its_own_line():
    p = parse_ingredient_list("Ingredients: Rice, salt.\nManufactured by Example Foods.\nAllergen information: Contains wheat.\nContains added flavours")
    assert p.declarations == ["Contains wheat", "Contains added flavours"]


def test_may_contain_is_never_a_declaration():
    assert parse_ingredient_list("Ingredients: Rice. May contain traces of nuts. Contains milk.").declarations == ["Contains milk"]


def test_declared_additive_missing_from_the_list_is_surfaced():
    a = analyse_text("Ingredients: Rice, salt.\nContains added flavours (nature identical flavouring substances).")
    assert [(d["text"], d["in_list"]) for d in a.declared] == [("added flavours (nature identical flavouring substances)", False)]
    assert a.group == 4 and a.ingredients == ["Rice", "salt"]            # evidence counts, but is NOT unioned into the list


def test_declared_additive_already_in_the_list_is_marked_so():
    a = analyse_text("Ingredients: Rice, natural flavour, salt.\nContains added flavours.")
    assert [(d["text"], d["in_list"]) for d in a.declared] == [("added flavours", True)]


def test_allergen_statements_are_not_ingredients_and_not_declared_additives():
    a = analyse_text("Ingredients: Rice, salt.\nContains wheat, milk and soy.\nMay contain traces of nuts.")
    assert a.ingredients == ["Rice", "salt"] and a.declared == []
    assert a.group == 3


def test_mixed_contains_line_keeps_only_the_additive_clauses():
    a = analyse_text("Ingredients: Rice, salt. Contains wheat and milk, permitted natural colour (160c) and added flavour.")
    assert [d["text"] for d in a.declared] == ["permitted natural colour (160c)", "added flavour"]
    assert all(not d["in_list"] for d in a.declared)
    assert a.ingredients == ["Rice", "salt"]


def test_declarations_are_shown_in_the_cli(tmp_path, capsys):
    from foodscan import cli

    f = tmp_path / "l.txt"
    f.write_text("Ingredients: Rice, salt.\nContains wheat and added flavours.")
    cli.main(["classify", "--text", str(f)])
    out = capsys.readouterr().out
    assert "Declared on a 'Contains' line" in out and "added flavours" in out and "NOT in the ingredient list" in out
    assert "wheat" not in out.split("Declared on a 'Contains' line")[1].split("INS")[0]
