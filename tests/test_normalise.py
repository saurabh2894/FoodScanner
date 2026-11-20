from foodscan.normalise import extract_ins, normalise_ingredient


def codes(raw):
    return [u.code for u in normalise_ingredient(raw).ins]


def test_ins_and_e_number_spellings():
    assert codes("Colour (INS 171)") == ["171"]
    assert codes("Colour (E171)") == ["171"]
    assert codes("colour (e-171)") == ["171"]
    assert codes("Colour (ins171)") == ["171"]


def test_ins_with_roman_suffix_and_continuation_codes():
    assert codes("raising agents (INS 500(ii), INS 503(ii))") == ["500(ii)", "503(ii)"]
    assert codes("raising agents (INS 500(ii), 503(ii))") == ["500(ii)", "503(ii)"]
    assert codes("Colour (INS 150d)") == ["150d"]


def test_mapped_ins_records_name_and_source():
    ing = normalise_ingredient("Emulsifier (INS 471)")
    (use,) = ing.ins
    assert use.name == "emulsifier" and "research/02" in use.source
    assert ing.name == "emulsifier" and ing.inner == ""


def test_unmapped_ins_has_no_name_and_no_invented_source():
    (use,) = normalise_ingredient("Preservative (INS 202)").ins
    assert use.code == "202" and use.name is None and use.source is None


def test_user_approved_ins_entries_carry_their_source():
    (u171,) = normalise_ingredient("Colour (E171)").ins
    (u211,) = normalise_ingredient("Preservative (INS 211)").ins
    assert u171.name == "titanium dioxide" and "USER-APPROVED" in u171.source
    assert u211.name == "sodium benzoate" and "USER-APPROVED" in u211.source


def test_synonyms_and_spelling():
    assert normalise_ingredient("Invert Syrup").name == "invert sugar"
    assert normalise_ingredient("High Fructose Corn Syrup").name == "glucose fructose syrup"
    assert normalise_ingredient("Atta").name == "whole wheat flour"
    assert normalise_ingredient("Added Flavours (nature identical)").name == "added flavour"
    assert normalise_ingredient("Permitted Colors").name == "permitted colour"


def test_name_inner_split_and_percent_removed():
    ing = normalise_ingredient("Edible Vegetable Oil (Palmolein) (12%)")
    assert ing.name == "edible vegetable oil" and ing.inner == "palmolein"
    assert normalise_ingredient("Sugar (12.5%)").name == "sugar"


def test_words_starting_with_e_are_not_codes():
    assert codes("Eggs 3 pieces") == []
    assert codes("Edible 500 g oil") == []


def test_extract_ins_strips_text():
    text, uses = extract_ins("Emulsifier (INS 471)")
    assert "471" not in text and len(uses) == 1


def test_bare_codes_after_additive_class_word():
    ing = normalise_ingredient("Flavour Enhancers (627, 631)")
    assert [u.code for u in ing.ins] == ["627", "631"]
    assert ing.name == "flavour enhancer" and ing.inner == ""
    assert [u.name for u in ing.ins] == ["disodium guanylate", "disodium inosinate"]
    assert all("USER-APPROVED" in u.source for u in ing.ins)


def test_bare_codes_with_roman_suffix_and_plural_class_word():
    assert [u.code for u in normalise_ingredient("Raising agents (500(ii), 503(ii))").ins] == ["500(ii)", "503(ii)"]
    assert [u.code for u in normalise_ingredient("Colours (102, 110)").ins] == ["102", "110"]


def test_bare_numbers_without_class_word_are_not_codes():
    assert normalise_ingredient("Salt (500)").ins == []
    assert normalise_ingredient("Sugar (1200)").ins == []
    assert normalise_ingredient("Potato (83)").ins == []
