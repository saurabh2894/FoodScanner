"""oils-24: mahua oil, watermelon seed oil, chia oil (FSSAI 2.2.1(5), (18), (30) sole-product naming; FAO Group 2 vegetable oils class-instance). Same guards as fats-rows-1."""
import pytest
from foodscan.pipeline import analyse_text

ROWS = ["mahua oil", "watermelon seed oil", "chia oil", "taramira oil", "niger seed oil", "kokum fat", "mango kernel fat", "illipe butter"]  # oils-24b adds the last five (FSSAI 2.2.1(11),(13); 2.2.4 items 7, 8, 13); shea butter held: prior NALT holds pinned in four test files


def g(t):
    a = analyse_text("Ingredients: " + t + ".", source="text")
    return a.group if a.answered else None


@pytest.mark.parametrize("t", ROWS)
def test_plain_oil_group_2(t):
    assert g(t.title()) == 2


@pytest.mark.parametrize("t", ROWS)
def test_hydrogenated_group_4(t):
    for f in ("Hydrogenated {x}", "Partially Hydrogenated {x}", "Interesterified {x}", "{x} (hydrogenated)"):
        assert g(f.format(x=t)) == 4


@pytest.mark.parametrize("t", ROWS)
def test_sprays_blends_additives_abstain(t):
    for f in ("{x} spray", "{x} blend", "{x} (antioxidant)", "{x} (INS 319)", "oil, {x}", "cooking {x}"):
        assert g(f.format(x=t)) is None


@pytest.mark.parametrize("t", ["Shea stearin", "Shea olein", "Fractionated shea butter", "Mango kernel", "Kokum", "Taramira", "Niger seed"])
def test_fractions_and_bare_seed_do_not_take_the_oil_group(t):
    assert g(t) != 2
