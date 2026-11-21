"""whole-food-guard-1 (SYNTHETIC; abstention only). A recognised whole_food item is not answered Group 1 when its own name or bracket names an added or preserving condition (salt, sugar, brine, an oil, canned/bottled/preserved),
or when its own bracket names a different food that is not explicitly the same food. The one exemption is SALT on the 23 grain/flour terms (a supported Group 3); any other observed condition on those terms still abstains.
Same-food equivalences are explicit (identical row, egg/eggs, plain milk with milk/cow/buffalo/goat milk, milk solids with the plain milk they are made from, 'dehydrated vegetable' with a vegetable row); there is no class taxonomy. No Group 3 is asserted for salted or sugared milk or eggs."""
from __future__ import annotations

from pathlib import Path

import pytest

from foodscan.pipeline import analyse_text


def g(text):
    a = analyse_text(f"Ingredients: {text}.", source="text")
    return (a.group if a.answered else None), a


WHOLE_FOODS = ["Milk", "Toned Milk", "Buffalo Milk", "Cow Milk", "Eggs", "Egg", "Dahi", "Ragi", "Oat", "Wheat", "Yeast", "Milk Solids", "Rice"]


@pytest.mark.parametrize("t", WHOLE_FOODS)
def test_synthetic_added_salt_sugar_oil_brine_or_preserved_forms_abstain(t):
    for f in ("{x} (sugar)", "{x} (sunflower oil)", "{x} (canned)", "{x} (brine)", "{x} (preserved)"):
        group, a = g(f.format(x=t))
        assert group is None and "names an added or preserving condition" in a.reason and "not denied" not in a.reason, f.format(x=t)


@pytest.mark.parametrize("t", ["Milk", "Eggs", "Dahi", "Ragi", "Oat", "Wheat", "Yeast"])
def test_synthetic_salted_forms_abstain_and_assert_no_group_3(t):
    for f in ("Salted {x}", "{x} (salted)"):
        group, a = g(f.format(x=t))
        assert group is None and a.reason, f.format(x=t)


def test_synthetic_the_23_grain_terms_keep_their_group_3_and_negations_keep_group_1():
    assert g("Salted Rice")[0] == 3 and g("Salted Wheat Flour")[0] == 3 and g("Rice (salted)")[0] == 3
    for t in ("Unsalted Milk", "Milk (no added salt)", "Eggs (no added sugar)", "Milk (Pasteurized)", "Eggs (Raw)", "Roasted Gram"):
        assert g(t)[0] == 1, t


@pytest.mark.parametrize("t", ["Rice (Egg)", "Eggs (Rice)", "Milk (Rice)", "Milk (Egg)", "Dahi (Rice)", "Wheat (Egg)", "Rice (Wheat)", "Rice (Walnuts)", "Milk (Milk Solids)", "Milk (Toned Milk)", "Dehydrated Vegetable (Peas)", "Milk Solids (Eggs)"])
def test_synthetic_a_distinct_nested_food_abstains_with_an_accurate_reason(t):
    group, a = g(t)
    assert group is None and a.reason.startswith("a bracket names a different food inside the item (") and "not recognise" not in a.reason, t
    assert "neither Group 1 nor Group 3 is asserted" in a.reason


@pytest.mark.parametrize("t", ["Milk (Buffalo Milk)", "Milk (Cow Milk)", "Toned Milk (Cow Milk)", "Buffalo Milk (Buffalo Milk)", "Eggs (Egg)", "Egg (Eggs)", "Rice (Rice)", "Dehydrated Vegetable (Onion)", "Milk (Pasteurized Cow Milk)"])
def test_synthetic_supported_same_food_and_species_brackets_stay_group_1(t):
    assert g(t)[0] == 1, t


def test_synthetic_species_milk_in_a_non_milk_head_keeps_the_existing_unrecognised_bracket_reason():
    group, a = g("Rice (Buffalo Milk)")
    assert group is None and a.reason.startswith("a bracket on a legume, vegetable, fruit or flour item names content the vocabulary does not recognise")


def test_synthetic_lists_and_other_kinds_are_unchanged():
    assert g("Milk, Sugar")[0] == 3 and g("Rice, Salt")[0] == 3 and g("Milk, Starter Culture")[0] == 1
    assert g("Salted Almonds")[0] == 3 and g("Salted Pinto Beans")[0] == 3 and g("Kidney Beans (canned)")[0] is None
    assert g("Milk (Salted), Water")[0] is None and g("Milk, Eggs (Rice)")[0] is None


def test_synthetic_condition_reasons_name_the_observed_condition_and_keep_the_general_definition():
    _, a = g("Milk (sugar)")
    assert "(Milk (sugar): sugar)" in a.reason and "the general Group 3 definition covers group 1 foods with salt, oil, sugar or other group 2 ingredients added" in a.reason
    assert "no source read" not in a.reason and "not established by the label evidence and the rules available" in a.reason and "neither Group 1 nor Group 3 is asserted" in a.reason
    assert "(Salted Milk: salted)" in g("Salted Milk")[1].reason and "(Eggs (canned): canned)" in g("Eggs (canned)")[1].reason


@pytest.mark.parametrize("t,observed", [("Rice (salt, sunflower oil)", "sunflower oil"), ("Salted Rice (canned)", "canned"), ("Rice (salt, sugar)", "sugar"), ("Salted Buckwheat (brine)", "brine"), ("Rice (Rice, Salt, Sunflower Oil)", "sunflower oil")])
def test_synthetic_scoped_grain_salt_is_exempt_but_other_conditions_still_abstain(t, observed):
    group, a = g(t)
    assert group is None and f": {observed})" in a.reason and "salt" not in a.reason.split("names an added or preserving condition (")[1].split("):")[0].replace("salted", "").replace("(salt, ", ""), t


@pytest.mark.parametrize("t", ["Salted Rice", "Salted Buckwheat", "Rice (salted)", "Rice (Rice, Salt)", "Salted Wheat Flour", "Roasted Salted Buckwheat"])
def test_synthetic_plain_salted_scoped_grains_keep_group_3(t):
    assert g(t)[0] == 3, t


def test_synthetic_same_class_distinct_foods_are_not_equated():
    # two different plants, a plant and a nut, a milk fraction in milk and a toned milk in milk are not the same food merely by class or token
    for t in ("Rice (Wheat)", "Wheat (Rice)", "Rice (Walnuts)", "Ragi (Oat)", "Milk (Milk Solids)", "Milk (Toned Milk)", "Dahi (Milk)", "Eggs (Milk)"):
        assert g(t)[0] is None, t
    for t in ("Rice (Rice)", "Rice (Brown Rice)", "Eggs (Egg)", "Egg (Eggs)", "Milk (Cow Milk)", "Buffalo Milk (Milk)", "Toned Milk (Goat Milk)", "Dehydrated Vegetable (Onion)", "Milk Solids (Toned Milk)", "Milk Solids (Milk)"):   # the solids with the milk they are made from: frozen b3/Q04
        assert g(t)[0] == 1, t


OVERLAY_ROWS = ["sheep milk", "duck eggs", "goose eggs", "quail eggs", "turkey eggs"]


def _overlay(tmp_path, texts):
    """Measure with the five rows of the held dairy proposal appended to a COPY of the lexicon (a future-rows overlay; the repository lexicon is not touched)."""
    import json
    import shutil
    import subprocess
    import sys

    src = tmp_path / "src"
    shutil.copytree(Path(__file__).resolve().parent.parent / "src", src, ignore=shutil.ignore_patterns("__pycache__", "*.egg-info"))
    lex = src / "foodscan" / "resources" / "lexicon.csv"
    lex.write_text(lex.read_text(encoding="utf-8").rstrip("\n") + "\n" + "".join(f'{t},whole_food,"PROVISIONAL (test overlay)"\n' for t in OVERLAY_ROWS), encoding="utf-8")
    code = ("import json,sys; from foodscan.pipeline import analyse_text; "
            "print(json.dumps({t: (lambda a: a.group if a.answered else None)(analyse_text('Ingredients: '+t+'.', source='text')) for t in json.loads(sys.argv[1])}))")
    r = subprocess.run([sys.executable, "-c", code, json.dumps(texts)], capture_output=True, text=True, env={"PYTHONPATH": str(src), "PATH": "/usr/bin:/bin:/usr/local/bin"}, cwd=str(tmp_path))
    assert r.returncode == 0, r.stderr[-400:]
    return json.loads(r.stdout)


def test_synthetic_future_dairy_rows_overlay(tmp_path):
    texts = ["Sheep Milk", "Duck Eggs", "Sheep Milk (Sheep Milk)", "Duck Eggs (Duck Eggs)", "Salted Sheep Milk", "Sheep Milk (sugar)", "Duck Eggs (canned)", "Duck Eggs (brine)", "Rice (Sheep Milk)", "Rice (Duck Eggs)",
             "Milk (Sheep Milk)", "Eggs (Duck Eggs)", "Duck Eggs (Eggs)", "Sheep Milk (Milk)", "Milk (Cow Milk)", "Eggs (Egg)", "Sheep Milk, Sugar", "Duck Eggs, Salt"]
    r = _overlay(tmp_path, texts)
    assert r["Sheep Milk"] == 1 and r["Duck Eggs"] == 1 and r["Sheep Milk (Sheep Milk)"] == 1 and r["Duck Eggs (Duck Eggs)"] == 1
    for t in ("Salted Sheep Milk", "Sheep Milk (sugar)", "Duck Eggs (canned)", "Duck Eggs (brine)", "Rice (Sheep Milk)", "Rice (Duck Eggs)"):
        assert r[t] is None, t
    # reported exceptions: no explicit equivalence is listed for the new species rows, so these abstain rather than being called the same food by class or token
    for t in ("Milk (Sheep Milk)", "Eggs (Duck Eggs)", "Duck Eggs (Eggs)", "Sheep Milk (Milk)"):
        assert r[t] is None, t
    assert r["Milk (Cow Milk)"] == 1 and r["Eggs (Egg)"] == 1 and r["Sheep Milk, Sugar"] == 3 and r["Duck Eggs, Salt"] == 3
