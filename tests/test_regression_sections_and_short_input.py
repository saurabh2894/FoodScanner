"""Regression tests for two observed bugs.

ALL FIXTURES HERE ARE SYNTHETIC: invented for these tests. They are NOT the captured original inputs
(those were lost), only inputs shaped like the reported failures.

Bug 1: a label written as separate sections ("Noodles: ... . Masala tastemaker: ...") lost every
       section after the first full stop, including the flavour/colour markers.
Bug 2: very short input ("Ingredients: Milk") produced no ingredients and an OCR error message,
       although the text had been pasted, not photographed.
"""
import pytest

from foodscan import cli
from foodscan.ocr import OcrUnavailable  # noqa: F401  (documents which error belongs to the photo path)
from foodscan.parser import parse_ingredient_list
from foodscan.pipeline import analyse_image, analyse_text

# --- synthetic fixture 1: compound label (two sections, then Contains / Manufactured) -----------
COMPOUND = (
    "Ingredients: Noodles: wheat flour, palm oil, salt, stabiliser (INS 452(i)). "
    "Masala tastemaker: mixed spices, salt, sugar, flavour enhancers (INS 627, INS 631), "
    "added flavour, colour (INS 150d). Contains wheat. Manufactured by Example Foods Pvt Ltd."
)
# --- synthetic fixture 2: the same ingredients as one flat comma list ----------------------------
FLAT = (
    "Ingredients: wheat flour, palm oil, salt, stabiliser (INS 452(i)), mixed spices, salt, sugar, "
    "flavour enhancers (INS 627, INS 631), added flavour, colour (INS 150d). "
    "Contains wheat. Manufactured by Example Foods Pvt Ltd."
)
# --- synthetic fixture 5: sections separated by a line break instead of a full stop --------------
LINE_BREAK = (
    "Ingredients: Noodles: wheat flour, palm oil, salt, stabiliser (INS 452(i))\n"
    "Masala tastemaker: mixed spices, salt, sugar, flavour enhancers (INS 627, INS 631), "
    "added flavour, colour (INS 150d)\nContains wheat."
)

ALL_ITEMS = [
    "wheat flour", "palm oil", "salt", "stabiliser (INS 452(i))",
    "mixed spices", "salt", "sugar", "flavour enhancers (INS 627, INS 631)", "added flavour", "colour (INS 150d)",
]


def text(t):
    """Pasted-text path."""
    return analyse_text(t, source="text")


def driver_set(a):
    return {(d.ingredient, d.detail) for d in a.drivers}


# ============================ Bug 1: compound declarations ======================================
def test_compound_label_extracts_both_sections():
    p = parse_ingredient_list(COMPOUND)
    assert p.items == ALL_ITEMS
    assert p.declarations == ["Contains wheat"]
    joined = " ".join(p.items).lower()
    assert "contains" not in joined and "manufactured" not in joined and "example foods" not in joined


def test_compound_label_keeps_ins_codes_with_bracketed_suffix():
    a = analyse_text(COMPOUND)
    codes = {u.code for u in a.ins_mappings}
    assert {"452(i)", "627", "631", "150d"} <= codes


def test_compound_label_matches_flat_version():
    c, f = analyse_text(COMPOUND), analyse_text(FLAT)
    assert c.answered and f.answered
    assert c.group == f.group == 4
    assert c.ingredients == f.ingredients == ALL_ITEMS
    assert {u.code for u in c.ins_mappings} == {u.code for u in f.ins_mappings}
    assert driver_set(c) == driver_set(f)


def test_flat_version_baseline():
    f = analyse_text(FLAT)
    assert f.group == 4 and {u.code for u in f.ins_mappings} == {"452(i)", "627", "631", "150d"}


def test_section_boundaries_are_preserved():
    p = parse_ingredient_list(COMPOUND)
    assert [s.label for s in p.sections] == ["Noodles", "Masala tastemaker"]
    assert p.sections[0].items == ["wheat flour", "palm oil", "salt", "stabiliser (INS 452(i))"]
    assert p.sections[1].items[0] == "mixed spices"
    a = analyse_text(COMPOUND)
    sections_by_ingredient = {d.ingredient: d.section for d in a.drivers}
    assert sections_by_ingredient["flavour enhancers (INS 627, INS 631)"] == "Masala tastemaker"
    assert all(d.section == "Masala tastemaker" for d in a.drivers)


def test_line_break_between_sections():
    p = parse_ingredient_list(LINE_BREAK)
    assert p.items == ALL_ITEMS                       # not glued into one item
    assert [s.label for s in p.sections] == ["Noodles", "Masala tastemaker"]
    assert analyse_text(LINE_BREAK).group == 4


def test_extra_spaces_crlf_and_blank_lines():
    t = ("INGREDIENTS :\r\n  Noodles:   wheat flour ,  palm oil,\r\n\r\n salt, stabiliser (INS 452(i)).  "
         "Masala   tastemaker :  mixed spices, salt,\nsugar, flavour enhancers (INS 627, INS 631), added flavour, "
         "colour (INS 150d).  CONTAINS wheat.")
    assert parse_ingredient_list(t).items == ALL_ITEMS
    assert analyse_text(t).group == 4


def test_ocr_line_wrap_inside_a_list_is_not_a_section():
    p = parse_ingredient_list("Ingredients: Wheat flour, palm\noil, salt")
    assert p.items == ["Wheat flour", "palm oil", "salt"]
    assert [s.label for s in p.sections] == [None]


def test_full_stop_does_not_end_list_before_a_labelled_section():
    p = parse_ingredient_list("Ingredients: Rice, salt. Tastemaker: sugar, flavour.")   # label not on the old allow-list
    assert p.items == ["Rice", "salt", "sugar", "flavour"]


def test_non_ingredient_labels_still_end_the_list():
    for tail in ("Note: store in a cool place, away from light.", "Directions: add hot water, stir.",
                 "Serving suggestion: with butter."):
        p = parse_ingredient_list("Ingredients: Rice, salt. " + tail)
        assert p.items == ["Rice", "salt"] and p.terminated, tail


def test_unlabelled_text_after_full_stop_still_ends_the_list():
    p = parse_ingredient_list("Ingredients: Rice, salt. Enjoy hot with butter.")
    assert p.items == ["Rice", "salt"] and p.terminated


def test_additive_class_label_after_full_stop_keeps_its_marker():
    # "Colour:" is an additive class word, so it is kept as part of the item, never stripped as a label
    a = analyse_text("Ingredients: Rice, salt. Colour: INS 150d.")
    assert "150d" in [u.code for u in a.ins_mappings] and not a.answered       # read as evidence; a colour alone abstains (option B)
    assert analyse_text("Ingredients: Rice, salt. Colour: INS 150d. Flavour: vanilla.").group == 4


def test_weak_single_additive_still_leads_to_uncertain():
    a = analyse_text("Ingredients: Fruit: mango. Set: sugar, pectin (INS 440).")
    assert not a.answered and "weak" in a.reason


# ============================ decimals, abbreviations inside the list ===========================
def test_decimal_and_emulsifier_do_not_cut_the_list():
    p = parse_ingredient_list("Ingredients: Sugar (12.5%), emulsifier (INS 322), milk solids, salt.")
    assert p.items == ["Sugar (12.5%)", "emulsifier (INS 322)", "milk solids", "salt"]


def test_abbreviation_inside_brackets_does_not_cut_the_list():
    p = parse_ingredient_list("Ingredients: Sugar (min. 10%), salt (approx. 2%), flavour.")
    assert p.items == ["Sugar (min. 10%)", "salt (approx. 2%)", "flavour"]


# ============================ Bug 2: very short input ==========================================
def test_single_ingredient_without_full_stop_parses():
    p = parse_ingredient_list("Ingredients: Milk")
    assert p.found and p.items == ["Milk"]


@pytest.mark.parametrize("pasted", ["Ingredients: Milk", "Milk", "milk.", "INGREDIENTS : MILK", "  ingredients:milk  "])
def test_short_pasted_list_is_analysed_not_rejected(pasted):
    a = text(pasted)
    assert a.answered, a.reason
    assert [i.lower() for i in a.ingredients] == ["milk"]
    # documented behaviour: research/02 lists milk as a group 1 example and the rule is
    # "single recognised unprocessed food => group 1" (tests/test_classify.py, lexicon.csv)
    assert a.group == 1


def test_heading_less_text_is_a_list_only_on_the_pasted_path():
    assert parse_ingredient_list("Milk", assume_list=True).items == ["Milk"]
    assert not parse_ingredient_list("Milk").found            # photo path still needs the heading


def test_short_list_ending_in_unrecognised_word_still_abstains_honestly():
    a = text("Ingredients: Sugar, refined wheat flo")
    assert not a.answered and "truncated" in a.reason


def test_pasted_text_with_no_ingredients_says_so_about_the_text():
    a = text("#### ~~ 1234 !!!! 5678")
    assert not a.answered and a.reason == "No ingredients found in this text"


# ============================ empty input ======================================================
@pytest.mark.parametrize("pasted", ["", "   ", "\n \t\n"])
def test_empty_pasted_text_gets_a_text_message_not_an_ocr_message(pasted):
    a = text(pasted)
    assert not a.answered and a.group is None
    assert "OCR" not in a.reason and a.reason.startswith("No text")


# ============================ OCR wording only on the photo path ================================
class _Fake:
    def __init__(self, t):
        self.t = t

    def extract_text(self, p):
        return self.t


def test_ocr_wording_comes_only_from_the_photo_path():
    # photo path: OCR wording is correct
    assert "OCR produced little text" in analyse_image("x.jpg", ocr=_Fake("Salt")).reason
    assert "OCR produced little text" in analyse_image("x.jpg", ocr=_Fake("")).reason
    # pasted path: never
    for pasted in ["", " ", "Salt", "Milk", "###", "Nutrition facts only: energy 450 kcal", "Ingredients:"]:
        a = text(pasted)
        if a.reason:
            assert "OCR" not in a.reason and "extracted" not in a.reason, (pasted, a.reason)


def test_default_source_keeps_the_existing_photo_wording():
    # existing behaviour that older tests rely on (decision: default source stays "ocr")
    assert "little text" in analyse_text("Salt").reason


def test_cli_text_mode_never_prints_ocr_wording(tmp_path, capsys):
    f = tmp_path / "short.txt"
    f.write_text("Ingredients: Milk")
    assert cli.main(["classify", "--text", str(f)]) == 0
    out = capsys.readouterr().out
    assert "NOVA group 1" in out and "OCR" not in out
    g = tmp_path / "empty.txt"
    g.write_text("   ")
    cli.main(["classify", "--text", str(g)])
    assert "OCR" not in capsys.readouterr().out


def test_cli_shows_section_for_drivers(tmp_path, capsys):
    f = tmp_path / "compound.txt"
    f.write_text(COMPOUND)
    cli.main(["classify", "--text", str(f)])
    out = capsys.readouterr().out
    assert "NOVA group 4" in out and "Masala tastemaker" in out
