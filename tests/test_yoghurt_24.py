"""yoghurt-g1-1 (recognition-only): only the explicit 'plain yoghurt' is placed (Group 1, FAO 'plain yoghurt'); the bare word and every other form abstain."""
import pytest
from foodscan.pipeline import analyse_text


def run(t):
    return analyse_text(f"Ingredients: {t}.", source="text")


@pytest.mark.parametrize("t", ["Plain yoghurt", "Plain yogurt", "plain yoghurt"])
def test_explicit_plain_is_group1(t):
    a = run(t)
    assert a.answered and a.group == 1


@pytest.mark.parametrize("t", ["Yoghurt", "Yogurt", "Yoghurt, Sugar", "Sweetened plain yoghurt", "Plain yoghurt powder", "Plain yoghurt, Sugar", "Plain yoghurt (Milk)", "Milk, Plain yoghurt", "Plain Greek yoghurt", "Frozen plain yoghurt", "Flavoured yoghurt", "Fruit yoghurt", "Yogurt drink", "Plain yoghurt, Salt", "Dried plain yoghurt", "Plain yoghurt, Wheat Flour"])
def test_bare_and_other_forms_never_group1_or_3(t):
    a = run(t)
    assert not (a.answered and a.group in (1, 3))


def test_dahi_and_culture_rule_unchanged():
    assert run("Dahi").group == 1 and run("Milk, Starter culture").group == 1 and run("Curd").group == 1


def test_neighbours_unchanged():
    for n in ["Paneer", "Buttermilk", "Kefir", "Khoa", "Cream"]:
        a = run(n)
        assert not a.answered or a.group is None
