"""plural-policy-1 synonyms as merged (SYNTHETIC unit cases: hand-written probes, not labels, never counted as coverage). Positives, then NEGATIVE CONTROLS: a plural or leaf form must
not attach to a different plant part, a different food, or a processed form."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from foodscan.classify import is_recognised
from foodscan.normalise import normalise_ingredient
from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
POLICY = json.loads((ROOT / "data" / "ingest" / "plural_policy_1.json").read_text(encoding="utf-8"))
SYN = {r["from"]: r for r in csv.DictReader((ROOT / "src" / "foodscan" / "resources" / "synonyms.csv").open(encoding="utf-8-sig", newline=""))}
LEX = {r["term"] for r in csv.DictReader((ROOT / "src" / "foodscan" / "resources" / "lexicon.csv").open(encoding="utf-8-sig", newline=""))}


def rec(t: str) -> bool:
    return bool(is_recognised(normalise_ingredient(t).name))


@pytest.mark.parametrize("r", POLICY["rows"], ids=lambda r: r["from"])
def test_synthetic_every_policy_row_is_merged_and_maps_to_its_target(r):
    assert r["from"] in SYN and SYN[r["from"]]["to"] == r["to"] and r["to"] in LEX
    assert SYN[r["from"]]["source"].startswith("PROVISIONAL: alias of existing lexicon row") and "exact term not named by any source read" in SYN[r["from"]]["source"]
    assert normalise_ingredient(r["from"]).name == r["to"] and rec(r["from"]) and rec(r["from"].upper()) and rec(f"Dried {r['from']}")


# india-24e: "fenugreek leaves" is now its own vegetable row (PROSEA Trigonella foenum-graecum id=601: leaves are a vegetable in India); it is still never mapped onto the seed row (test_fenugreek_leaves_are_not_the_seed_row).
# Current Product19330 explicitly identifies mustard leaves as mustard greens, not mustard seed.
# The historical policy JSON is unchanged and every other part/food hold remains.
@pytest.mark.parametrize("t", [t for t in POLICY["must_stay_unmapped"] if t not in ("mustard leaves", "fenugreek leaves")])
def test_synthetic_negative_control_other_part_or_food_is_not_mapped_onto_a_base_row(t):
    assert t not in SYN and normalise_ingredient(t).name == t and not rec(t)


@pytest.mark.parametrize("t", POLICY["must_stay_unrecognised"])
def test_synthetic_negative_control_processed_forms_stay_unrecognised(t):
    assert not rec(t)


def test_synthetic_the_four_part_distinctions_that_matter():
    assert rec("fenugreek seeds") and normalise_ingredient("fenugreek leaves").name != "fenugreek"   # india-24e: own vegetable row, never the seed row
    assert rec("coriander leaves") and normalise_ingredient("coriander leaves").name == "coriander leaf"
    assert normalise_ingredient("coriander seeds").name != "coriander leaf"          # seeds never become the leaf row
    assert rec("basil leaves") and not rec("basil seeds")                              # raw basil seeds are a different food
    assert normalise_ingredient("peppermint leaves").name == "peppermint"             # longest match: not "pepper" + mint
    assert normalise_ingredient("mint leaves").name == "mint"


def test_synthetic_existing_rows_are_untouched():
    for t in ("bay leaf", "dried curry leaves", "dill", "coriander", "fennel seeds", "mustard seeds", "celery seeds", "cloves"):
        assert rec(t)
    assert normalise_ingredient("dried curry leaves").name == "dried curry leaves"
    assert "curry leaves" not in SYN and "curry leaf" not in SYN            # dropped by the gate: it would rewrite the existing row's own name
    assert "coriander" not in {r["from"] for r in SYN.values()} and "dill" not in SYN


def test_synthetic_plural_forms_in_a_list_are_recognised_and_the_other_parts_stay_visibly_unassessed():
    a = analyse_text("Ingredients: Rice, cumin seeds, basil leaves, coriander leaves, fenugreek flowers, basil seeds, salt.", source="text")
    un = " | ".join(a.unassessed).lower()
    assert "fenugreek flowers" in un and "basil seeds" in un
    assert not any(x in un for x in ("cumin seeds", "basil leaves", "coriander leaves"))
