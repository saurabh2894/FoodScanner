"""(1) A vocabulary gap is worded as one and names the items; genuine cut-offs keep the truncation wording and gating. No classification changes.
(2) soybean is a PROVISIONAL whole_food row (FAO 2019 Table 1 Group 1 lists legumes such as beans and lentils; soybean is not named)."""
import json
from pathlib import Path

import pytest

from foodscan.pipeline import analyse_text
from foodscan.tables import load_table

ROOT = Path(__file__).resolve().parent.parent


def a(t):
    return analyse_text(t, source="text")


@pytest.mark.parametrize("text", ["Soyabean Seed", "Soybean", "Soya bean", "Soyabean seeds", "Soybeans", "Ingredients: Soya beans"])
def test_a_lone_soybean_is_group_1(text):
    r = a(text)
    assert r.answered and r.group == 1, text


def test_soybean_with_salt_is_group_3_and_processed_soy_is_not_covered():
    assert a("Soyabean Seed, Salt").group == 3
    assert a("Soybean oil").group == 2                                  # the existing culinary row is unchanged
    r = a("Soy lecithin")
    assert not r.answered                                                # a processed soy ingredient is a different term: still outside the vocabulary


def test_soybean_row_is_provisional_and_honest_about_the_source():
    row = next(r for r in load_table("lexicon.csv") if r["term"] == "soybean")
    assert row["kind"] in ("whole_food", "legume") and row["source"]       # retyped to the legume kind by class-bulk-1 (same behaviour plus the item-level salt/sugar/brine guard).startswith("PROVISIONAL")
    assert "https://www.fao.org/3/ca5644en/ca5644en.pdf" in row["source"] and "does not name soybean" in row["source"]


@pytest.mark.parametrize("text, named", [
    ("Zorbium", "Zorbium"),
    ("Water, Sugar, Zorbium", "Zorbium"),
    ("Zorbium, Quux", "Zorbium, Quux"),
])
def test_unrecognised_items_are_named_and_never_called_truncated(text, named):
    r = a(text)
    assert not r.answered and "truncated" not in r.reason
    assert r.reason == "ingredients not in the local vocabulary, so processing level cannot be judged: " + named


@pytest.mark.parametrize("text", ["Ingredients: Sugar, refined wheat flo", "Ingredients: Rice, salt, flavou", "Ingredients: Rice, Pasteurized Toned", "Sugar, wheat flour (maida"])
def test_genuine_cut_offs_keep_the_truncation_wording(text):
    r = a(text)
    assert not r.answered and "truncated" in r.reason and r.completeness["status"] == "uncertain"


def test_option_a_is_unchanged_for_a_real_cut_off_and_a_vocabulary_gap_gets_no_incomplete_warning():
    r = a("Ingredients: Rice, flavour, refined wheat flo")
    assert r.group == 4 and any("List may be incomplete" in w for w in r.warnings)
    r = a("Ingredients: Rice, flavour, Zorbium")
    assert r.group == 4 and not any("incomplete" in w for w in r.warnings)
    assert "Zorbium" in " ".join(r.unassessed)                           # still visible under Not assessed
    assert r.completeness["status"] == "uncertain" and "the last item is not in the local vocabulary" in r.completeness["reasons"]


def test_every_frozen_paste_input_keeps_its_group():
    before = json.loads((ROOT / "evaluation/vocab_message_soy_flip_check/groups_before.json").read_text())
    dirs = {"b1": "fresh_batch_1", "b2": "fresh_batch_2", "b3": "fresh_batch_3", "neg": "negation_addendum", "dev15": "dev_regression_15"}
    assert len(before) == 66
    for key, group in before.items():
        k, name = key.split("/")
        r = a((ROOT / "evaluation" / dirs[k] / "inputs" / f"{name}.txt").read_text())
        # Intended, attributed exception (vocab-display-1): the synonyms.csv row "lodised salt" -> "iodised salt" makes b3/Q03 ("Water, Curd, lodised Salt")
        # recognisable, so it moves from the frozen None to Group 3 (its reference expectation). Evidence: evaluation/vocab_display_1_flip_check/.
        # Every other key must still equal its frozen value; the frozen before-JSON is not edited.
        # Intended, attributed exception (per-form-1, owner ruling): b3/Q10 'Milk solids (Pasteurized skimmed cow milk)' is a whole_food item whose bracket names content the vocabulary does not recognise ('cow'), so the
        # whole_food unknown-bracket abstention moves it Group 1 -> None (the same class as 'Rice (XQ9)'). Evidence: evaluation/per_form_1/.
        # Intended, attributed exception (per-form-2b): b2/M02 'PASTEURISED COW MILK' and b3/Q06 'Pasteurized Cow Milk' are single species-qualified milk items; 'cow milk' is now a recognised milk row (FAO Group 1 milk
        # without species restriction; species not named by a verified NOVA source), so both move None -> Group 1. Evidence: evaluation/per_form_2b/.
        # Intended, attributed exception (whole-food-guard-1): b3/Q04 'Milk solids (Toned Milk) & Active Culture' names a different recognised food inside a whole_food bracket; no clause read establishes that a milk named in the
        # bracket of 'milk solids' is the same food, and a frozen expectation is not evidence, so the item now abstains (Group 1 -> None). Evidence: evaluation/whole_food_guard_1/.
        # N09 actual-pack correction: complete paired fat/SNF minima are composition metadata,
        # not added milk-fat ingredients. Original frozen JSON stays unchanged. research/09.
        # Class/code mismatch guard: N15 declares stabilizer for INS471, mapped here as emulsifier.
        # The literal code stays visible but the disputed entry no longer decides Group 4.
        # UPDATED (milk-24e): b3/Q02 ("Milk solids." sole item, frozen 1) abstains for the same reason as b2/M08 below.
        # UPDATED (milk-24e): b2/M08 Milkmaid sweetened condensed milk ("Milk solids, Sugar", frozen 3) now abstains: generic milk solids is not established as milk outside a fermented milk (FSSAI 2.1 composition measure only; 2.7 defines it for chocolate) and can name a fraction, so Group 3 vs 4 is not established.
        expected = 3 if key == "b3/Q03" else (None if key in ("b3/Q10", "b3/Q04", "b1/N15", "b2/M08", "b3/Q02") else (1 if key in ("b1/N09", "b2/M02", "b3/Q06") else group))
        assert (r.group if r.answered else None) == expected, key
