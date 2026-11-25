"""yoghurt-g1-1: sole plain yoghurt is Group 1 (FAO 'fresh or pasteurized plain yoghurt'; identity FSSAI 2.1 and FDC SR Legacy); every other form abstains."""
import pytest
from foodscan.pipeline import analyse_text


def run(t):
    return analyse_text(f"Ingredients: {t}.", source="text")


@pytest.mark.parametrize("t", ["Yoghurt", "Yogurt", "yoghurt"])
def test_sole_plain_is_group1(t):
    a = run(t)
    assert a.answered and a.group == 1


@pytest.mark.parametrize("t", ["Sweetened yoghurt", "Fruit yoghurt", "Yoghurt powder", "Yoghurt, Sugar", "Yoghurt (Milk)", "Milk, Yoghurt", "Greek yoghurt", "Frozen yoghurt", "Flavoured yoghurt", "Yoghurt, Strawberry", "Yogurt drink", "Yoghurt, Salt", "Dried yoghurt", "Yoghurt coating", "Yoghurt, Wheat Flour"])
def test_other_forms_never_group1_or_3(t):
    a = run(t)
    assert not (a.answered and a.group in (1, 3))


def test_dahi_and_culture_rule_unchanged():
    assert run("Dahi").group == 1 and run("Milk, Starter culture").group == 1 and run("Curd").group == 1


def test_neighbours_unchanged():
    for n in ["Paneer", "Buttermilk", "Kefir", "Khoa", "Cream"]:
        a = run(n)
        assert not a.answered or a.group is None
