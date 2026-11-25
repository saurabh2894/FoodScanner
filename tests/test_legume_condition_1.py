"""class-bulk-1 legume guard (SYNTHETIC cases; both directions). Kind `legume` = whole-food behaviour plus an item-level condition read from the item's OWN name and bracket.
Sources: FAO 2019 Group 3 'canned or bottled vegetables or legumes (pulses) preserved in brine' (p.7 prose; Table 1 Group 3, p.12) and the Group 3 definition 'Products made by adding salt, oil,
sugar or other group 2 ingredients to group 1 foods'. A salt/sugar/brine-conditioned item is Group 3 (definition or brine example), never Group 1 via the legume clause; a canned/bottled/
preserved item that does not say salt, sugar or brine ABSTAINS (not established either way). Roasted and boiled plain forms are NOT in scope (FAO Group 1 definition p.6 names roasting and boiling)."""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from foodscan.classify import legume_added_salt_sugar_or_brine, legume_preserved_form
from foodscan.normalise import normalise_ingredient
from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
LEX = {r["term"]: r for r in csv.DictReader((ROOT / "src" / "foodscan" / "resources" / "lexicon.csv").open(encoding="utf-8-sig", newline=""))}
LEGUME_ROWS = ["beans", "peas", "chickpea", "lentil", "rajma", "moong", "soybean", "toor dal", "moong dal", "chana dal", "masoor dal", "urad dal",
               "adzuki beans", "black beans", "broadbeans", "cannellini beans", "carioca beans", "cowpeas", "cranberry beans", "flor de mayo beans", "great northern beans", "hyacinth beans",
               "kidney beans", "lima beans", "lupins", "mothbeans", "navy beans", "pigeon peas", "pink beans", "pinto beans", "small white beans", "winged beans", "yardlong beans"]

# Slice13: separately source-reviewed seed/pod food-name heads. The original33 are retained.
LEGUME_ROWS += ['greengram', 'blackgram', 'mungo beans', 'mungobeans', 'catjang peas', 'haricot beans']
# pulses-24: horse gram (FSSAI 2.4.6(2)(VI) naming + FAO legumes class-instance), added additively.
LEGUME_ROWS += ['horse gram']


def g(text):
    a = analyse_text(f"Ingredients: {text}.", source="text")
    return (a.group if a.answered else None), a


def test_synthetic_exactly_the_39_source_reviewed_legume_rows_have_the_legume_kind():
    assert {t for t, r in LEX.items() if r["kind"] == "legume"} == set(LEGUME_ROWS)


@pytest.mark.parametrize("t", ["Salted Pinto Beans", "Pinto Beans (salted)", "Pinto Beans (in brine)", "Pinto Beans (Pinto Beans, Salt)", "Adzuki Beans (sweetened)", "Salted Soybeans",
                               "Chickpeas (canned, salted)", "Moong Dal (salted)", "Salted Peas", "Lentils (with sugar)", "Rajma (brined)"])
def test_synthetic_negative_an_item_whose_own_name_or_bracket_adds_salt_sugar_or_brine_never_takes_group_1_via_the_legume_clause(t):
    group, a = g(t)
    assert group == 3 and not any(d.detail == "single recognised unprocessed food" for d in a.drivers), (t, group)
    assert any("FAO Group 3" in d.detail for d in a.drivers)


@pytest.mark.parametrize("t", ["Pinto Beans", "Unsalted Pinto Beans", "Pinto Beans (no added salt)", "Pinto Beans (salt free)", "Pinto Beans (without salt)", "Chickpeas", "Lentils", "Soybeans", "Moong Dal", "Split Green Peas", "Kidney Beans (Organic)"])
def test_synthetic_plain_and_negated_forms_keep_group_1(t):
    group, a = g(t)
    assert group == 1, (t, group)


@pytest.mark.parametrize("t", ["Roasted Soybeans", "Soybeans (Roasted)", "Boiled Lentils", "Kidney Beans (cooked)", "Chickpeas (boiled)"])
def test_synthetic_roasting_and_boiling_are_unchanged_and_keep_group_1(t):
    assert g(t)[0] == 1                                                         # FAO Group 1 definition (p.6) names roasting and boiling; not part of this guard


@pytest.mark.parametrize("t", ["Kidney Beans (canned)", "Chickpeas (pickled)", "Beans (bottled)", "Lentils (tinned)", "Pigeon Peas (preserved)", "Rice, Kidney Beans (canned)"])
def test_synthetic_negative_a_canned_bottled_or_preserved_legume_that_does_not_say_salt_sugar_or_brine_abstains(t):
    group, a = g(t)
    assert group is None and "canned, bottled or preserved legume" in (a.reason or ""), t


@pytest.mark.parametrize("t", ["Canned Kidney Beans", "Kidney Beans in Brine", "Baked Beans", "Refried Beans", "Sweetened Adzuki Beans", "Hummus", "Tofu", "Soy Milk", "Peanut Butter", "Black Beans with Salt"])
def test_synthetic_negative_forms_outside_the_vocabulary_never_get_group_1(t):
    group, a = g(t)
    assert group != 1 and group is None and t.lower() in " ".join(u.lower() for u in a.unassessed), t


def test_synthetic_the_condition_is_read_from_the_items_own_text_never_from_a_neighbour():
    assert not legume_added_salt_sugar_or_brine(normalise_ingredient("Pinto Beans"))
    assert legume_added_salt_sugar_or_brine(normalise_ingredient("Salted Pinto Beans"))
    assert not legume_added_salt_sugar_or_brine(normalise_ingredient("Unsalted Pinto Beans"))
    assert legume_preserved_form(normalise_ingredient("Kidney Beans (canned)")) and not legume_preserved_form(normalise_ingredient("Kidney Beans"))
    group, a = g("Rice, Salt, Pinto Beans")
    assert group == 3 and any(d.ingredient == "Pinto Beans" and d.detail == "recognised whole food" for d in a.drivers)
    assert g("Rice, Pinto Beans")[0] is None                                   # plain beans in a two-food list: existing abstention, unchanged
