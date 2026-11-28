"""Completeness signal: a correct-looking verdict must not be able to hide lost text.

In production the true item count is unknown, so this is expressed as text-span coverage over the words after the heading
(read as ingredients / set aside after the list / declared / explicitly not read / unaccounted) plus explicit reasons for
doubt. It does not claim exact completeness. SYNTHETIC inputs of my own.
"""
import random

import pytest

from foodscan import cli
from foodscan.pipeline import analyse_text

CLEAN = "Ingredients: Noodles: wheat flour, salt and sugar. Masala: emulsifier [472e] and flour treatment agent [1101(ii)], flavour. Contains wheat. Manufactured by Example Foods."


def words(a):
    return a.completeness["words"]


def test_clean_input_is_complete_with_every_word_accounted():
    a = analyse_text(CLEAN, source="text")
    c = a.completeness
    assert c["status"] == "complete" and c["reasons"] == [] and c["heading"] == "exact"
    w = c["words"]
    assert w["unaccounted"] == 0 and w["not_read"] == 0
    assert w["in_list"] > 0 and w["excluded"] > 0 and w["declared"] > 0         # manufacturer text set aside, Contains declared
    assert c["list_share"] == 1.0


def test_unread_text_is_counted_and_makes_the_read_uncertain():
    a = analyse_text("Ingredients: Rice, salt. Sugar, vinegar, oil.", source="text")
    c = a.completeness
    assert words(a)["not_read"] == 3 and c["status"] == "uncertain"
    assert any("not read" in r for r in c["reasons"]) and c["list_share"] < 1.0


def test_prose_after_the_list_is_counted_but_does_not_make_it_uncertain():
    a = analyse_text("Ingredients: Rice, salt. Enjoy hot with butter.", source="text")
    assert words(a)["not_read"] == 4 and a.completeness["status"] == "complete"


@pytest.mark.parametrize("text, reason_part", [
    ("Ingredients: Rice, emulsifier (INS 471, salt", "bracket"),
    ("Ingredients: Sugar, refined wheat flo", "truncated"),
    ("Ingredients: Rice, Mystery Paste Seasoning : Onion, salt.", "section label"),
])
def test_known_risks_are_stated_as_reasons(text, reason_part):
    c = analyse_text(text, source="text").completeness
    assert c["status"] == "uncertain" and any(reason_part in r for r in c["reasons"]), c


def test_photo_path_cut_heading_and_inferred_block_are_uncertain():
    cut = analyse_text("REDIENTS: Wheat flour, sugar, invert sugar syrup, salt, emulsifier (INS 322).", source="ocr").completeness
    assert cut["status"] == "uncertain" and cut["heading"] == "fuzzy" and any("heading" in r for r in cut["reasons"])
    inferred = analyse_text("NEW tasty snack\n\nWheat flour, sugar, invert sugar syrup, salt, emulsifier (INS 322), milk.\n\nEnergy 450 kcal per 100 g", source="ocr").completeness
    assert inferred["status"] == "uncertain" and inferred["heading"] == "inferred"


def test_assessed_share_is_reported_separately_from_completeness():
    a = analyse_text("Ingredients: Rice, jackfruit seed paste, emulsifier (INS 471).", source="text")
    assert a.completeness["assessed"] == {"items": 3, "not_assessed": 1}
    assert a.completeness["status"] == "complete"          # everything was read; one item is just outside the vocabulary


def test_abstentions_carry_the_signal_too():
    a = analyse_text("Ingredients: Rice, jackfruit seed paste.", source="text")
    assert not a.answered and a.completeness["status"] == "complete" and a.completeness["words"]["in_list"] == 4


def test_no_list_found_has_no_signal_to_trust():
    a = analyse_text("Nutrition facts only: energy 450 kcal", source="ocr")
    assert a.completeness["status"] == "uncertain" and a.completeness["words"]["in_list"] == 0


def test_cli_prints_the_signal(tmp_path, capsys):
    f = tmp_path / "l.txt"
    f.write_text("Ingredients: Rice, salt. Sugar, vinegar.")
    cli.main(["classify", "--text", str(f)])
    out = capsys.readouterr().out
    assert "Text completeness: uncertain" in out and "not read" in out


def test_span_property_nothing_is_unaccounted_over_generated_inputs():
    """SYNTHETIC: 400 random label shapes; every word after the heading is read, declared, set aside or explicitly not read."""
    rng = random.Random(7)
    labels = ["", "", "Seasoning: ", "Puff 88%: ", "Noodles: ", "Masala tastemaker: ", "Note: ", "Coating 12.5%: "]
    bodies = ["Rice, salt", "sugar and salt", "Wheat flour, palm oil (palmolein), stabiliser (INS 452(i))", "Enjoy hot with butter",
              "emulsifier [472e] and flour treatment agent [1101(ii)], flavour", "Milk", "Khaand, amchur, tamarind", "Spices and Condiments, Natural and Nature Identical Flavours"]
    tails = ["", " Contains wheat.", " Contains wheat and added flavours. Manufactured by Example Foods.", " THIS PRODUCT CONTAINS 37% MILLETS", "\nNutrition per 100 g: Energy 450 kcal"]
    for _ in range(400):
        segs = [rng.choice(labels) + rng.choice(bodies) for _ in range(rng.randint(1, 4))]
        text = "Ingredients: " + rng.choice([". ", ".\n", "\n"]).join(segs) + rng.choice([".", ""]) + rng.choice(tails)
        a = analyse_text(text, source="text")
        assert a.completeness["words"]["unaccounted"] == 0, (text, a.completeness)
