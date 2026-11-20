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
    assert row["kind"] == "whole_food" and row["source"].startswith("PROVISIONAL")
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
        expected = 3 if key == "b3/Q03" else group
        assert (r.group if r.answered else None) == expected, key
