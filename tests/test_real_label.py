"""A real label (potato chips, photographed small) found while testing: regression cases.

Text below is the list as printed, typed by hand from the photo. The pack's own
brackets do not balance: "*Seasoning (" is opened and never closed.
"""
import shutil
from pathlib import Path

import pytest

from foodscan.ocr import prepare_image
from foodscan.pipeline import analyse_image, analyse_text

FIXTURE = Path(__file__).parent / "fixtures" / "chips_label.png"

AS_PRINTED = (
    "INGREDIENTS: Potato (83%), Edible Vegetable Oil*, *Seasoning (Sugar, Iodised Salt, "
    "Milk Solids (1.2%), Spices and Condiments, Maltodextrin, Flavour (Natural and Nature "
    "Identical Flavouring Substances), Cheese Powder (0.3%), Hydrolysed Vegetable Protein, "
    "Flavour Enhancers (627, 631), Edible Vegetable Oil (Palm, Coconut). "
    "*As flavouring agent. ALLERGEN ADVICE: Contains Soy, Milk"
)
# what tesseract actually returns after upscaling, slips included
AS_OCR = (
    'INGREDIENTS: Potato (83%), Edible Vegetable Or",\n"Seasoning (Suger, lodised Salt, Mik Solids (1.2%), '
    "Spices\nand Comiments, Maltodextrin, Flavour (Natural and Nature\nidentical Raxvouring Substances}, "
    "Cheese Powler (0.3%),\nHydrolysed Vegetable Protein, Flavour Enhancers (627,\n631), "
    "Edible Vegetadie OF (Paim, Coconut).\n\n\"AS favouring agent."
)


def test_as_printed_is_group4_with_incomplete_warning():
    a = analyse_text(AS_PRINTED)
    assert a.answered and a.group == 4
    assert any("unclosed bracket" in w for w in a.warnings)


def test_drivers_name_specific_ingredients_not_the_seasoning_blob():
    a = analyse_text(AS_PRINTED)
    drivers = {d.ingredient for d in a.drivers}
    assert "Maltodextrin" in drivers
    assert any(d.startswith("Flavour Enhancers") for d in drivers)
    assert not any(d.startswith("*Seasoning") for d in drivers)


def test_enhancer_codes_mapped_with_source():
    a = analyse_text(AS_PRINTED)
    mapped = {u.code: u for u in a.ins_mappings}
    assert mapped["627"].name == "disodium guanylate" and mapped["631"].name == "disodium inosinate"
    assert "Project decision" in mapped["627"].source


def test_footnote_after_unclosed_bracket_is_not_a_driver():
    a = analyse_text(AS_PRINTED)
    assert not any("As flavouring agent" in d.ingredient for d in a.drivers)
    assert all("*As" not in i for i in a.ingredients)


def test_ocr_text_with_slips_still_group4():
    assert analyse_text(AS_OCR).group == 4


def test_recognised_compound_heads_stay_whole():
    # "edible vegetable oil (palm, coconut)" must not be split into unknown sub-items
    a = analyse_text("Ingredients: Potato, edible vegetable oil (palm, coconut), salt.")
    assert a.answered and a.group == 3


def test_additive_compound_heads_stay_whole():
    a = analyse_text("Ingredients: Potato, raising agents (INS 500(ii), INS 503(ii)), salt.")
    assert not a.answered and "weak" in a.reason


def test_prepare_image_upscales_small_and_leaves_large():
    from PIL import Image

    small = prepare_image(Image.new("RGB", (239, 167), "white"))
    assert small.mode == "L" and small.width == 239 * 4
    large = prepare_image(Image.new("RGB", (1300, 200), "white"))
    assert large.width == 1300


@pytest.mark.ocr
@pytest.mark.skipif(shutil.which("tesseract") is None, reason="tesseract not installed")
def test_real_photo_end_to_end():
    a = analyse_image(FIXTURE)
    assert a.answered and a.group == 4
    assert any("altodextrin" in d.ingredient for d in a.drivers)


REFERENCE_2 = (
    "Ingredients:\nBase Mix(57%)(Ragi, Rice, Pea Protein, Urad Dal), Sabudana Flour, Potato Flour, Rice Bran Oil. "
    "Seasoning : Dehydrated Vegetables(Garlic, Onion, Tomato), Iodised Salt, Khaand, Natural Citric Acid, Milk Solids, "
    "Spices & Condiments, Natural & Nature Identical Flavours, Rosemary Extract, "
    "Contains natural color extracted from Paprika"
)


def test_reference_example_with_seasoning_section_is_group4():
    a = analyse_text(REFERENCE_2)
    assert a.answered and a.group == 4 and a.warnings == []
    assert len(a.ingredients) == 12            # the seasoning section is part of the list
    details = " | ".join(d.ingredient + " " + d.detail for d in a.drivers)
    assert "Flavours" in details                # named ingredient, not the whole section
    assert "Contains" in details and "colour" in details   # US spelling "color" is recognised


def test_us_spelling_in_contains_statement():
    a = analyse_text("Ingredients: Potato, salt. Contains permitted color.")
    assert a.group is None and "colouring" in a.reason          # US spelling is read as a colour; alone it abstains (option B)
    assert analyse_text("Ingredients: Potato, salt. Contains permitted color and added flavor.").group == 4
