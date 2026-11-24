import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from count_heads import counts, norm


def test_variants_collapse():
    assert norm("tinned sardines") == norm("canned sardine")
    assert norm("eggs") == norm("egg")


def test_canonical_never_exceeds_placed_rows():
    c = counts()
    assert c["canonical_placed"] <= c["placed_rows"] <= c["rows"]


def test_wheat_semolina_is_an_alias_not_a_head():
    import csv
    from foodscan.pipeline import analyse_text
    root = Path(__file__).resolve().parent.parent / "src" / "foodscan" / "resources"
    assert "wheat semolina" not in {r["term"] for r in csv.DictReader((root / "lexicon.csv").open(newline=""))}
    for t in ["Wheat semolina", "Wheat semolina (75%)", "Wheat Semolina"]:
        a = analyse_text(f"Ingredients: {t}.", source="text")
        assert a.answered and a.group == 1
    a = analyse_text("Ingredients: Wheat semolina (75%), Maltodextrin.", source="text")
    assert a.answered and a.group == 4
