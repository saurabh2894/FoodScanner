"""A sweetener class word whose bracket names only foods ("Sweeteners (Jaggery Powder, Dates Powder)") is not an added sweetener class.
FAO 2019 pp. 9-10 lists ARTIFICIAL sweeteners for Group 4. Real additive sweeteners keep driving Group 4."""
import json
from pathlib import Path

import pytest

from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
GOOD_PRO = ("Milk Solids, Millets & Nuts Mix (49.57%) (Milk Solids, Ragi, Bajra, Foxtail Millet, Oats, Almonds, Walnuts, Cashews), Sweeteners (Jaggery Powder, "
            "Dates Powder), Fructooligosaccharides, Cocoa Powder (7%), Vitamins, Minerals, Nature Identical Flavour, Coconut Milk Powder, Algal Oil, Rock Salt, "
            "Probiotic Blend (0.1%), Dried Monk Fruit Powder.")


def a(t):
    return analyse_text(t, source="text")


def drivers(t):
    return [d.detail for d in a(t).drivers]


def test_the_reported_label_stays_group_4_through_the_flavour_only():
    r = a("Ingredients: " + GOOD_PRO)
    assert r.answered and r.group == 4
    assert [d.detail for d in r.drivers] == ['"flavour" (cosmetic_additive)']
    assert any("not counted as an added sweetener class" in w for w in r.warnings)


def test_sweetener_of_foods_alone_decides_nothing_and_says_why():
    r = a("Ingredients: Milk solids, Sweeteners (Jaggery Powder, Dates Powder), Cocoa powder.")
    assert not r.answered and "bracket names only foods" in r.reason
    assert not any("sweetener" in d.detail for d in r.drivers)


@pytest.mark.parametrize("text", [
    "Ingredients: Water, Sweeteners (Aspartame, Acesulfame K).",
    "Ingredients: Water, Sweeteners (Jaggery, Sucralose).",        # one non-food name keeps the marker
    "Ingredients: Water, Sweetener (INS 950).",
    "Ingredients: Water, Sweetener.",
    "Ingredients: Water, Sweeteners (955, 950).",
])
def test_additive_sweeteners_still_drive_group_4(text):
    r = a(text)
    assert r.answered and r.group == 4 and '"sweetener" (cosmetic_additive)' in drivers(text), text


def test_natural_sweeteners_of_foods_and_declared_contains_lines():
    r = a("Ingredients: Water, Natural sweeteners (Jaggery, Honey), Salt.")
    assert not any("sweetener" in d.detail for d in r.drivers)
    t = "Ingredients: Water, Salt. Contains Non-Caloric Sweeteners (Aspartame, Acesulfame K)."
    assert a(t).group == 4                                          # a Contains declaration of real sweeteners is untouched


def test_every_frozen_paste_input_keeps_its_group():
    before = json.loads((ROOT / "evaluation/sweetener_flip_check/groups_before.json").read_text())
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
        # without species restriction; Lancet 2025 names minimally processed cow's milk), so both move None -> Group 1. Evidence: evaluation/per_form_2b/.
        expected = 3 if key == "b3/Q03" else (None if key == "b3/Q10" else (1 if key in ("b2/M02", "b3/Q06") else group))
        assert (r.group if r.answered else None) == expected, key
