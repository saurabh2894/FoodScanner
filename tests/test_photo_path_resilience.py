"""Priority 2 of the first unseen-label evaluation: a photo cropped at the left edge must not lose the whole panel.

SYNTHETIC OCR texts of my own. The photo path (source="ocr") is stricter than the paste path: a heading that had to be
guessed, or a list found without any heading, may only produce a Group 4 call that a strong marker already supports;
everything else asks for a clearer photo. Nothing is ever invented.
"""
import pytest

from foodscan.parser import parse_ingredient_list
from foodscan.pipeline import analyse_text

LIST_UPF = "Wheat flour, sugar, edible vegetable oil (palm), invert sugar syrup, salt, raising agents (INS 503(ii), INS 500(ii)), emulsifier (INS 322)."
LIST_PLAIN = "Rice, salt, sugar, edible vegetable oil, water, turmeric, cumin, garlic."


# ---- tolerant heading ---------------------------------------------------------------------------------------
@pytest.mark.parametrize("heading", ["REDIENTS:", "GREDIENTS:", "NGREDIENTS:", "INGREDIEN:", "lNGREDlENTS:", "INGREDIENTS:", "Ingredients -", "INGREDlENTS:"])
def test_damaged_headings_are_still_found(heading):
    p = parse_ingredient_list(f"{heading} {LIST_UPF}")
    assert p.found and p.items[0] == "Wheat flour", (heading, p.items[:2])
    assert not any(":" in i for i in p.items)


def test_heading_kind_is_reported():
    assert parse_ingredient_list(f"INGREDIENTS: {LIST_UPF}").heading_kind == "exact"
    cut = parse_ingredient_list(f"REDIENTS: {LIST_UPF}")
    assert cut.heading_kind == "fuzzy" and cut.heading_text.lower().startswith("redients")


@pytest.mark.parametrize("not_a_heading", ["Nutrients: energy 450 kcal, protein 8 g, fat 20 g, sugar 10 g.",
                                           "Recipients: please send the whole panel, closer.", "Gradients: 1, 2, 3, 4, 5, 6.",
                                           "Experience the crunch, taste the joy, enjoy every bite."])
def test_look_alike_words_are_not_headings(not_a_heading):
    assert not parse_ingredient_list(not_a_heading).found


def test_a_heading_word_inside_a_sentence_is_not_a_heading():
    assert not parse_ingredient_list("We love fine redients in our kitchen, rice, salt, sugar, oil and more.").found


# ---- policy on the photo path -------------------------------------------------------------------------------
def test_cut_heading_with_a_strong_marker_still_gives_group4_with_a_warning():
    a = analyse_text(f"REDIENTS: {LIST_UPF}", source="ocr")
    assert a.answered and a.group == 4
    assert any("REDIENTS" in w and "cut off" in w for w in a.warnings)
    assert a.heading["kind"] == "fuzzy"


def test_cut_heading_without_a_marker_asks_for_a_clearer_photo():
    a = analyse_text(f"REDIENTS: {LIST_PLAIN}", source="ocr")
    assert not a.answered and "retake" in a.reason and "cut off" in a.reason


def test_same_text_pasted_is_not_held_to_the_photo_rule():
    a = analyse_text(f"REDIENTS: {LIST_PLAIN}", source="text")
    assert a.answered and a.group == 3 and a.heading["kind"] == "fuzzy"


def test_exact_heading_on_the_photo_path_is_unchanged():
    a = analyse_text(f"INGREDIENTS: {LIST_PLAIN}", source="ocr")
    assert a.answered and a.group == 3 and a.heading["kind"] == "exact"


# ---- no heading: the most plausible block, never a nutrition table / marketing / allergen statement -----------------
MARKETING = "NEW! Tasty crunchy snack. Buy now and get a free gift inside, limited offer, enjoy the taste!"
NUTRITION = "Nutritional information per 100 g\nEnergy 450 kcal\nProtein 8 g\nCarbohydrate 60 g\nTotal fat 20 g\nSodium 600 mg"
ALLERGEN = "Contains: wheat, milk, soy, gluten, peanuts, tree nuts."


def test_an_unheaded_list_among_other_blocks_is_found_and_flagged():
    text = f"{MARKETING}\n\n{LIST_UPF}\n\n{NUTRITION}\n\n{ALLERGEN}"
    a = analyse_text(text, source="ocr")
    assert a.answered and a.group == 4
    assert a.heading["kind"] == "inferred"
    assert a.ingredients[0] == "Wheat flour" and not any("energy" in i.lower() or "gift" in i.lower() for i in a.ingredients)
    assert any('no "ingredients" heading' in w.lower() for w in a.warnings)


def test_an_unheaded_plain_list_is_not_answered():
    a = analyse_text(f"{MARKETING}\n\n{LIST_PLAIN}\n\n{NUTRITION}", source="ocr")
    assert not a.answered and "retake" in a.reason and "heading" in a.reason


@pytest.mark.parametrize("blocks", [NUTRITION, MARKETING, ALLERGEN, f"{NUTRITION}\n\n{ALLERGEN}", f"{MARKETING}\n\n{NUTRITION}\n\n{ALLERGEN}",
                                    "Energy 450 kcal, Protein 8 g, Carbohydrate 60 g, Total fat 20 g, Sodium 600 mg, Fibre 2 g",
                                    "NEW, tasty, crunchy, buy now, free gift, limited offer, enjoy the taste"])
def test_nothing_is_invented_from_non_ingredient_text(blocks):
    a = analyse_text(blocks, source="ocr")
    assert not a.answered and a.ingredients == []
    assert "no ingredient list found" in a.reason and "retake" in a.reason


def test_garbled_ocr_asks_for_a_clearer_photo():
    for text in ["", "#### ~~ 1234 !!!!", "Sa lt", "xx xx xx xx xx xx xx xx xx xx xx xx"]:
        a = analyse_text(text, source="ocr")
        assert not a.answered and ("photo" in a.reason or "text" in a.reason), text


def test_no_heading_in_pasted_text_still_treats_the_text_as_the_list():
    a = analyse_text("Rice, salt, sugar", source="text")
    assert a.answered and a.group == 3 and a.heading["kind"] == "assumed"
