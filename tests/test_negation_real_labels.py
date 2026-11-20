"""Real-label negation cases (evaluation/negation_addendum/): a false Group 4 would be visible on R1 and R2, where no code or positive marker decides the group."""
from pathlib import Path
import pytest
from foodscan.pipeline import analyse_text

D = Path(__file__).resolve().parent.parent / "evaluation" / "negation_addendum" / "inputs"


def run(r):
    return analyse_text((D / f"{r}.txt").read_text(), source="text")


@pytest.mark.parametrize("r", ["R1", "R2"])
def test_negation_only_labels_are_never_group_4(r):
    a = run(r)
    assert not (a.answered and a.group == 4)
    assert not any("declared in" in d.detail for d in a.drivers)


def test_mixed_sentence_registers_positive_span_only():
    a = run("R3")
    assert a.answered and a.group == 4
    assert [d.detail for d in a.drivers] == ['declared in "Contains" statement: "flavour"']


def test_negation_after_list_and_allergen_free_statements_add_nothing():
    for r in ("R4", "R5", "R6"):
        a = run(r)
        assert a.answered and a.group == 4, r
        assert not any("preservative" in d.detail for d in a.drivers), r
    assert len(run("R5").ingredients) == 18
    assert len(run("R6").ingredients) == 4
