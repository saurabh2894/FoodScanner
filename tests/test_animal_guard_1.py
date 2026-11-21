"""animal-guard-1 (SYNTHETIC): eight meat/poultry rows (beef, lamb, pork, chicken, veal, turkey, duck, goose) as source-stated food labels, class-instance of the FAO Group 1 example 'meat, poultry, fish and seafood, whole or in the
form of steaks, fillets and other cuts' (never NAMED, no aliases). Bounded guard: dried animal food is Group 3 (FAO Group 3 example 'salted, dried, cured, or smoked meats and fish'); the powder of an animal food abstains even with
100% in the text. Ground, roasted, boiled and steamed X stay Group 1 under the existing whole-food rules (named minimal processes; the no-added-substance condition is kept by the observed-condition guard); salted, smoked, cured,
canned, breaded, battered, fried, minced and formed forms abstain; plant, dairy, egg and fat controls are untouched."""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from foodscan.pipeline import analyse_text

ROWS = ["beef", "lamb", "pork", "chicken", "veal", "turkey", "duck", "goose"]


def g(t):
    a = analyse_text(f"Ingredients: {t}.", source="text")
    return (a.group if a.answered else None), a


@pytest.mark.parametrize("t", ROWS)
def test_synthetic_plain_and_minimal_process_forms_are_group_1(t):
    for f in ("{x}", "ground {x}", "roasted {x}", "boiled {x}", "steamed {x}"):
        assert g(f.format(x=t))[0] == 1, f.format(x=t)


@pytest.mark.parametrize("t", ROWS)
def test_synthetic_dried_animal_food_is_group_3_with_the_fao_example(t):
    group, a = g(f"dried {t}")
    assert group == 3 and "salted, dried, cured, or smoked meats and fish" in a.drivers[0].detail, t
    assert g(f"dried {t}, salt")[0] == 3


@pytest.mark.parametrize("t", ROWS)
def test_synthetic_animal_powders_abstain_whatever_the_text_states(t):
    for f in ("{x} powder", "100% {x} powder", "whole {x} powder", "{x} (powder)", "dried {x} powder", "100% {x} powder (rice)"):
        group, a = g(f.format(x=t))
        assert group is None and a.reason.startswith("a powder of an animal food is named (") and "whatever percentage the item states" in a.reason, f.format(x=t)
    assert g(f"{t} powder, rice")[0] is None


@pytest.mark.parametrize("t", ROWS)
def test_synthetic_conditioned_forms_abstain_or_follow_the_existing_guards(t):
    for f in ("salted {x}", "smoked {x}", "cured {x}", "canned {x}", "breaded {x}", "battered {x}", "fried {x}", "pan fried {x}", "minced {x}", "formed {x}", "cooked {x}", "chilled {x}",
              "{x} (XQ9)", "{x} (rice)", "{x} (milk)", "{x} (egg)", "{x} (brine)", "{x} (canned)", "{x} (preserved)", "{x} (sunflower oil)", "{x}, water", "{x}, rice"):
        assert g(f.format(x=t))[0] is None, f.format(x=t)
    assert g(f"{t}, salt")[0] == 3 and g(f"{t}, sugar")[0] == 3 and g(f"{t}, sunflower oil")[0] == 3
    assert g(f"hydrogenated {t}")[0] == 4 and g(f"{t}, flavour")[0] == 4 and g(f"{t}, maltodextrin")[0] == 4


@pytest.mark.parametrize("t", ["Mutton", "Goat", "Fish", "Chicken Meat", "Beef Extract", "Pork Fat"])
def test_synthetic_aliases_other_animals_and_held_forms_stay_unrecognised(t):
    assert g(t)[0] is None, t


def test_synthetic_plant_dairy_egg_fat_and_powder_controls_are_unchanged():
    assert g("Dried Rice")[0] == 1 and g("Dried Mango")[0] == 1 and g("Rice Powder")[0] is None and g("Banana Powder")[0] is None
    assert g("Milk")[0] == 1 and g("Sheep Milk")[0] == 1 and g("Eggs")[0] == 1 and g("Dried Egg")[0] == 1 and g("100% Egg Powder")[0] == 1 and g("Egg Powder")[0] is None
    assert g("Skimmed Milk Powder")[0] == 1 and g("Salted Milk")[0] is None and g("Milk (Rice)")[0] is None and g("Rice (Wheat)")[0] is None
    assert g("Sunflower Oil")[0] == 2 and g("Lard")[0] == 2 and g("Sunflower Oil Powder")[0] is None and g("Tea")[0] == 1 and g("Walnuts (brine)")[0] == 3


def test_synthetic_row_provenance_is_class_instance_with_the_verified_example_and_no_naming_or_purity_claim():
    root = Path(__file__).resolve().parent.parent
    rows = {r["term"]: r["source"] for r in csv.DictReader((root / "src" / "foodscan" / "resources" / "lexicon.csv").open(encoding="utf-8-sig", newline=""))}
    for t in ROWS:
        s = rows[t]
        assert s.startswith("PROVISIONAL (animal-guard-1)") and '"meat, poultry, fish and seafood, whole or in the form of steaks, fillets and other cuts"' in s, t
        assert "DRIED-G3-SCOPE: meat" in s and "class-instance" in s and "never NAMED" in s and "no taxonomic resolution" in s and "no alias" in s and "FDC id" in s and "Unprocessed (or natural)" not in s, t


def test_synthetic_dried_scope_is_meat_and_finfish_only_other_seafood_abstains_and_never_falls_back_to_group_1(tmp_path):
    """FAO Group 3 names dried 'meats and fish'. A row records its scope; an animal row with scope none (crab, mussel, ...) abstains when dried: neither Group 3 nor Group 1. Measured on a COPY of the lexicon with three test rows."""
    import json
    import shutil
    import subprocess
    import sys

    root = Path(__file__).resolve().parent.parent
    src = tmp_path / "src"
    shutil.copytree(root / "src", src, ignore=shutil.ignore_patterns("__pycache__", "*.egg-info"))
    lex = src / "foodscan" / "resources" / "lexicon.csv"
    base = 'PROVISIONAL (test overlay): ""meat, poultry, fish and seafood, whole or in the form of steaks, fillets and other cuts"" '
    lex.write_text(lex.read_text(encoding="utf-8").rstrip("\n") + "\n" + f'testfish,whole_food,"{base}DRIED-G3-SCOPE: finfish."\ntestcrab,whole_food,"{base}DRIED-G3-SCOPE: none."\ntestmeat,whole_food,"{base}DRIED-G3-SCOPE: meat."\n', encoding="utf-8")
    texts = ["testfish", "dried testfish", "dried testcrab", "dehydrated testcrab", "testcrab", "testcrab powder", "dried testcrab, salt", "dried testmeat", "dried testfish powder", "dried rice"]
    code = ("import json,sys; from foodscan.pipeline import analyse_text; "
            "print(json.dumps({t: (lambda a: a.group if a.answered else None)(analyse_text('Ingredients: '+t+'.', source='text')) for t in json.loads(sys.argv[1])}))")
    r = subprocess.run([sys.executable, "-c", code, json.dumps(texts)], capture_output=True, text=True, env={"PYTHONPATH": str(src), "PATH": "/usr/bin:/bin:/usr/local/bin"}, cwd=str(tmp_path))
    assert r.returncode == 0, r.stderr[-400:]
    out = json.loads(r.stdout)
    assert out["testfish"] == 1 and out["testcrab"] == 1 and out["dried testfish"] == 3 and out["dried testmeat"] == 3
    assert out["dried testcrab"] is None and out["dehydrated testcrab"] is None and out["dried testcrab, salt"] is None, out
    assert out["testcrab powder"] is None and out["dried testfish powder"] is None and out["dried rice"] == 1
