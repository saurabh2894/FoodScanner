"""Thickeners and emulsifying salts are strong cosmetic_additive markers (FAO 2019, Monteiro et al., pp. 9-10 and Table 1; research/02 addendum).
Frozen paste inputs of every existing batch must keep their group (evaluation/thickener_salt_flip_check/): no flips were found."""
import json
from pathlib import Path

import pytest

from foodscan.pipeline import analyse_text
from foodscan.tables import load_table

ROOT = Path(__file__).resolve().parent.parent


def g(t):
    a = analyse_text(t, source="text")
    return a.group if a.answered else None, a


@pytest.mark.parametrize("text", [
    "Ingredients: Rice, salt, Thickener (INS 412).",
    "Ingredients: Rice, salt, Thickeners (508, 412).",
    "Ingredients: Water, oil, salt, Thickener - E1442.",
    "Ingredients: Milk, sugar, Emulsifying salts (INS 331).",
    "Ingredients: Milk, cheese, Emulsifying salt.",
])
def test_declared_thickener_or_emulsifying_salt_is_group_4(text):
    group, a = g(text)
    assert group == 4, text
    assert any(d.detail in ('"thickener" (cosmetic_additive)', '"emulsifying salt" (cosmetic_additive)') for d in a.drivers)


def test_marker_rows_cite_the_fao_text_that_was_read():
    rows = {r["term"]: r for r in load_table("markers.csv")}
    for term in ("thickener", "emulsifying salt"):
        r = rows[term]
        assert (r["marker_class"], r["strength"]) == ("cosmetic_additive", "strong")
        assert "https://www.fao.org/3/ca5644en/ca5644en.pdf" in r["source"] and "pp. 9-10" in r["source"]


def test_pectin_qualification_still_holds_for_a_thickener_declared_with_ins_440():
    group, _ = g("Ingredients: Sugar, fruit pulp, Thickener (INS 440), Citric acid.")
    assert group != 4


def test_unrelated_classes_are_unchanged():
    assert g("Ingredients: Rice, salt, Stabilizer (INS 412).")[0] is None            # stabiliser stays unlisted
    assert g("Ingredients: Rice, salt, Guar gum.")[0] is None or g("Ingredients: Rice, salt, Guar gum.")[0] != 4   # a food name is not a class word


def test_every_frozen_paste_input_keeps_its_group():
    before = json.loads((ROOT / "evaluation/thickener_salt_flip_check/groups_before_marker_change.json").read_text())
    dirs = {"b1": "fresh_batch_1", "b2": "fresh_batch_2", "b3": "fresh_batch_3", "neg": "negation_addendum", "dev15": "dev_regression_15"}
    assert len(before) == 66
    for key, group in before.items():
        k, name = key.split("/")
        a = analyse_text((ROOT / "evaluation" / dirs[k] / "inputs" / f"{name}.txt").read_text(), source="text")
        assert (a.group if a.answered else None) == group, key
