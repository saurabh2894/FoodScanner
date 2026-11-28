"""salted-animal-27a: the FAO Table 1 Group 3 example reads "salted, dried, cured, or smoked meats and fish" (https://www.fao.org/3/ca5644en/ca5644en.pdf, p.7). Dried was already routed for meat and finfish rows
(DRIED-G3-SCOPE marker). This reverses the old test hold that made "salted X" abstain for those same scoped rows, with the clause as the reason. Smoked and cured stay abstaining (they are not descriptors; adding them
is a global parser change), crab and other unscoped animal rows still abstain, unsalted stays Group 1, a salted butter or nut keeps its own route."""
from __future__ import annotations

import pytest

from foodscan.pipeline import analyse_text

MEAT = ["beef", "lamb", "pork", "chicken", "veal", "turkey", "duck", "goose"]


def g(t):
    a = analyse_text(f"Ingredients: {t}.", source="text")
    return (a.group if a.answered else None), a


@pytest.mark.parametrize("t", MEAT)
def test_salted_meat_is_group_3_with_the_fao_example(t):
    group, a = g(f"salted {t}")
    assert group == 3 and "salted, dried, cured, or smoked meats and fish" in a.drivers[0].detail
    assert g(f"{t} (salted)")[0] == 3


@pytest.mark.parametrize("t", ["salted cod", "salted mackerel"])
def test_salted_finfish_is_group_3(t):
    assert g(t)[0] == 3


def test_edges_still_abstain_or_keep_their_own_route():
    assert g("salted chicken (brine)")[0] is None and g("salted crab")[0] is None
    assert g("smoked chicken")[0] is None and g("cured pork")[0] is None and g("chicken, salted")[0] is None
    assert g("unsalted chicken")[0] == 1 and g("chicken")[0] == 1 and g("salted butter")[0] == 2 and g("salted almonds")[0] == 3 and g("salted rice")[0] == 3
