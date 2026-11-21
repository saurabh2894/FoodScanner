"""culinary-guard-1 (SYNTHETIC; abstention only). (1) Bracket content on an OIL or FAT row that does not establish a culinary-only composition abstains: an unrecognised part (a suffix 'oil' or 'fat' is not an identity: 'XQ9 Oil',
'Mineral Oil', 'Essential Oil', 'Gingelly Oil') and a recognised distinct food ('Rice', 'Milk'); supported parts are recognised culinary rows (another oil, salt, sugar, starch) and the source word of a recognised oil ('palm, coconut');
(2) the powder of an oil or fat abstains unless its own name (outside any bracket) states 100%, and a 100% never overrides bracket content; (3) 'A and B oil' where 'A oil' and 'B oil' are both oil rows is kept whole (it names two oils; the composition is not established) while 'Rice and Sunflower Oil' stays food plus oil. Plain oils and lard stay Group 2,
hydrogenated and interesterified forms stay Group 4, comma lists of a food and an oil stay Group 3, other culinary rows (salt, sugar, vinegar, jaggery) are untouched."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
OILS = ["Olive Oil", "Sunflower Oil", "Soybean Oil", "Palm Oil", "Coconut Oil", "Mustard Oil", "Groundnut Oil", "Sesame Oil", "Edible Vegetable Oil", "Vegetable Oil", "Refined Oil", "Butter", "Ghee", "Cocoa Butter", "Palmolein", "Peanut Oil",
        "Cottonseed Oil", "Rice Bran Oil", "Coconut Fat", "Butter Oil"]       # all 20 oil/fat rows of the lexicon on main 625f0fa (is_fat_row)
FATS_ROWS = ["almond oil", "apricot kernel oil", "avocado oil", "babassu oil", "canola oil", "corn oil", "cupuassu oil", "flaxseed oil", "grapeseed oil", "hazelnut oil", "lard", "oat oil", "palm kernel oil", "poppyseed oil",
             "safflower oil", "sheanut oil", "teaseed oil", "tomatoseed oil", "walnut oil", "wheat germ oil"]


def g(text):
    a = analyse_text(f"Ingredients: {text}.", source="text")
    return (a.group if a.answered else None), a


@pytest.mark.parametrize("t", OILS)
def test_synthetic_plain_oils_stay_group_2_and_hydrogenated_forms_group_4(t):
    assert g(t)[0] == 2 and g("Hydrogenated " + t)[0] == 4 and g("Interesterified " + t)[0] == 4 and g(t + " (hydrogenated)")[0] == 4, t


@pytest.mark.parametrize("t", OILS)
def test_synthetic_unrecognised_bracket_content_on_an_oil_or_fat_abstains(t):
    for b in ("XQ9", "oryzanol", "XQ9 Oil", "XQ9 Carrier Oil", "Mineral Oil", "Essential Oil", "XQ9 Fat", "Gingelly Oil"):
        group, a = g(f"{t} ({b})")
        assert group is None and a.reason.startswith("a bracket on a processed culinary ingredient names content that is unrecognised or is a different food, not a culinary ingredient (") and "no group is asserted" in a.reason, (t, b)


@pytest.mark.parametrize("t", OILS)
def test_synthetic_a_recognised_distinct_food_in_the_bracket_abstains_and_culinary_only_content_stays_group_2(t):
    for b in ("Rice", "Milk", "Sugar, Rice", "Palm, Rice", "Refined (XQ9), Palm"):
        assert g(f"{t} ({b})")[0] is None, (t, b)
    for b in ("Starch", "Palm, Salt", "Refined", "Palm, Coconut"):
        assert g(f"{t} ({b})")[0] == 2, (t, b)


@pytest.mark.parametrize("t", ["Edible Vegetable Oil (palm, coconut)", "Edible Vegetable Oil (palmolein)", "Refined Oil (rice bran)", "Sunflower Oil (Refined)", "Groundnut Oil (Peanut Oil)", "Ghee (Butter)", "Sunflower Oil (Palm Oil)"])
def test_synthetic_oil_source_and_recognised_culinary_brackets_stay_group_2(t):
    assert g(t)[0] == 2, t


def test_synthetic_no_alias_is_assumed_for_gingelly_or_til_oil():
    assert g("Sesame Oil (Gingelly Oil)")[0] is None and g("Sesame Oil (Til Oil)")[0] is None


def test_synthetic_hydrogenation_marker_keeps_precedence_over_the_bracket_guard():
    assert g("Hydrogenated Sunflower Oil (XQ9)")[0] == 4 and g("Hydrogenated Sunflower Oil (Rice)")[0] == 4 and g("Sunflower Oil (hydrogenated)")[0] == 4


@pytest.mark.parametrize("t", ["Sunflower Oil", "Olive Oil", "Ghee", "Butter", "Edible Vegetable Oil", "Groundnut Oil", "Palmolein"])
def test_synthetic_oil_and_fat_powders_abstain_unless_100_percent_is_stated(t):
    group, a = g(t + " Powder")
    assert group is None and a.reason.startswith("a powder of an oil or fat is named (") and "composition is not established" in a.reason and "carrier" not in a.reason, t
    assert g("100% " + t + " Powder")[0] == 2, t
    assert g("100% " + t + " Powder (Rice)")[0] is None and g("100% " + t + " Powder (XQ9 Oil)")[0] is None and g(t + " Powder (100% Starch)")[0] is None, t


def test_synthetic_other_culinary_rows_are_untouched():
    for t in ("Jaggery Powder", "Sugar Powder", "Salt (XQ9)", "Sugar (Cane)", "Salt (Iodised)", "Vinegar (XQ9)", "Honey", "Starch"):
        assert g(t)[0] == 2 or t in ("Salt (XQ9)", "Sugar (Cane)", "Salt (Iodised)", "Vinegar (XQ9)"), t
    assert g("Salt (XQ9)")[0] == 2 and g("Sugar (Cane)")[0] == 2   # the broader culinary unknown-bracket question stays open (parked), only oils and fats are guarded here


@pytest.mark.parametrize("t", ["Soybean and Palm Oil", "Sesame and Sunflower Oil", "Groundnut and Palm Oil"])
def test_synthetic_a_phrase_naming_two_oils_is_kept_whole_and_abstains(t):
    group, a = g(t)
    assert group is None and a.ingredients == [t] and "not in the local vocabulary" in a.reason, t


def test_synthetic_food_plus_oil_lists_keep_group_3():
    assert g("Rice and Sunflower Oil")[0] == 3 and g("Rice, Sunflower Oil")[0] == 3 and g("Potato, Edible Vegetable Oil (palm, coconut), Salt")[0] == 3
    assert g("Walnuts (sunflower oil)")[0] == 3 and g("Salt and Sunflower Oil")[0] is None


def _overlay(tmp_path, texts):
    """The 20 staged fats rows (held proposal) appended to a COPY of the lexicon; the repository lexicon is untouched."""
    src = tmp_path / "src"
    shutil.copytree(ROOT / "src", src, ignore=shutil.ignore_patterns("__pycache__", "*.egg-info"))
    lex = src / "foodscan" / "resources" / "lexicon.csv"
    lex.write_text(lex.read_text(encoding="utf-8").rstrip("\n") + "\n" + "".join(f'{t},culinary,"PROVISIONAL (test overlay)"\n' for t in FATS_ROWS), encoding="utf-8")
    code = ("import json,sys; from foodscan.pipeline import analyse_text; "
            "print(json.dumps({t: (lambda a: [a.group if a.answered else None, a.ingredients])(analyse_text('Ingredients: '+t+'.', source='text')) for t in json.loads(sys.argv[1])}))")
    r = subprocess.run([sys.executable, "-c", code, json.dumps(texts)], capture_output=True, text=True, env={"PYTHONPATH": str(src), "PATH": "/usr/bin:/bin:/usr/local/bin"}, cwd=str(tmp_path))
    assert r.returncode == 0, r.stderr[-400:]
    return json.loads(r.stdout)


def test_synthetic_staged_fats_rows_overlay(tmp_path):
    new = ["Corn Oil", "Canola Oil", "Lard", "Walnut Oil", "Wheat Germ Oil", "Palm Kernel Oil"]
    texts = [f for t in new for f in (t, t + " (XQ9)", t + " Powder", "100% " + t + " Powder", "Hydrogenated " + t, "Rice, " + t, "Rice and " + t)]
    texts += ["Corn and Canola Oil", "Corn and Sunflower Oil", "Soybean and Corn Oil", "Rice and Sunflower Oil", "Walnuts (Walnut Oil)", "Edible Vegetable Oil (Corn, Canola)", "Edible Vegetable Oil (Corn, XQ9)"]
    r = _overlay(tmp_path, texts)
    for t in new:
        assert r[t][0] == 2 and r[t + " (XQ9)"][0] is None and r[t + " Powder"][0] is None and r["100% " + t + " Powder"][0] == 2 and r["Hydrogenated " + t][0] == 4 and r["Rice, " + t][0] == 3, t
    for t in ("Corn and Canola Oil", "Corn and Sunflower Oil", "Soybean and Corn Oil"):
        assert r[t][0] is None and r[t][1] == [t], t
    assert r["Rice and Sunflower Oil"][0] == 3 and r["Walnuts (Walnut Oil)"][0] == 3 and r["Edible Vegetable Oil (Corn, Canola)"][0] == 2 and r["Edible Vegetable Oil (Corn, XQ9)"][0] is None
