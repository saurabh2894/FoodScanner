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


# ---- focused coverage added after the flip check (no frozen input contains "emulsifying salt") ----
def drivers(text):
    return [d.detail for d in analyse_text(text, source="text").drivers]


@pytest.mark.parametrize("text", [
    "Ingredients: Milk, cheese, Emulsifying Salt (INS 339).",
    "Ingredients: Milk, cheese, Emulsifying Salts (INS 339, INS 331).",
])
def test_emulsifying_salt_by_class_word_singular_and_plural_gives_group_4_with_its_driver(text):
    group, a = g(text)
    assert group == 4 and '"emulsifying salt" (cosmetic_additive)' in drivers(text)


def test_negated_emulsifying_salt_is_not_a_driver():
    t = "Ingredients: Milk, cheese, salt. Contains no emulsifying salts."
    group, a = g(t)
    assert group is None and a.drivers == []
    assert not any("emulsifying salt" in d for d in drivers(t))


def test_mixed_line_keeps_only_the_positive_marker():
    t = "Ingredients: Milk, cheese, salt. Contains no emulsifying salts, contains added flavour."
    group, a = g(t)
    assert group == 4
    assert drivers(t) == ['declared in "Contains" statement: "flavour"']                      # the negated emulsifying salt is not registered
    t2 = "Ingredients: Milk, cheese, salt. Contains no emulsifying salts, contains preservative (INS 211)."
    assert g(t2)[0] is None and not any("emulsifying salt" in d for d in drivers(t2))      # preservative is not a marker: nothing decides
    t3 = "Ingredients: Milk, cheese, salt. No emulsifying salts, contains emulsifying salt (INS 339)."
    assert g(t3)[0] == 4 and drivers(t3) == ['declared in "Contains" statement: "emulsifying salt"']   # the positive half of a mixed line still registers


def test_thickener_with_pectin_code_does_not_drive_group_4_but_another_code_does():
    assert g("Ingredients: Sugar, fruit pulp, Thickener (INS 440).")[0] is None
    assert g("Ingredients: Sugar, fruit pulp, Thickener (INS 412).")[0] == 4
    assert '"thickener" (cosmetic_additive)' in drivers("Ingredients: Sugar, fruit pulp, Thickener (INS 412).")
    # separate entries: the pectin qualification is per ingredient entry, so a second thickener entry with another code still counts
    assert g("Ingredients: Sugar, fruit pulp, Thickener (INS 440), Thickener (INS 412).")[0] == 4
