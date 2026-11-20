"""WS3 clause-tier mapping (scripts/clause_tier.py + data/ingest/clause_tier1_herbs_spices.json): names to recognition kind only, never a NOVA group."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pytest

from scripts import clause_tier as ct

RULE = ct.load_rule()


def row(desc: str, cat: str = "Spices and Herbs", fdc: str = "1", dataset: str = "sr_legacy") -> dict:
    parts = [p.strip() for p in desc.lower().split(",")]
    return {"candidate_id": f"fdc_{dataset}:{fdc}", "dataset": dataset, "fdc_id": fdc, "description": desc, "parts": json.dumps(parts), "food_category": cat}


def test_rule_is_the_verbatim_unconditioned_clause_with_its_source():
    c = RULE["clause"]
    assert c["text"] == "herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried"
    assert "(" not in c["text"]                                           # unconditioned: no parenthetical condition
    assert c["url"] == "https://www.fao.org/3/ca5644en/ca5644en.pdf" and "p. 11" in c["where"] and len(c["pdf_sha256"]) == 64
    assert RULE["kind"] == "herb_spice" and RULE["category_gate"]["food_category"] == "Spices and Herbs"


@pytest.mark.parametrize("desc, decision, code, term", [
    ("Spices, bay leaf", "ACCEPT", "clause_forms_only", "bay leaf"),
    ("Spices, ginger, ground", "ACCEPT", "clause_forms_only", "ginger"),
    ("Spices, coriander leaf, dried", "ACCEPT", "clause_forms_only", "coriander leaf"),
    ("Spices, cloves, ground", "ACCEPT", "clause_forms_only", "cloves"),
    ("Basil, fresh", "ACCEPT", "clause_forms_only", "basil"),
    ("Spearmint, dried", "ACCEPT", "clause_forms_only", "spearmint"),
    ("Spices, pepper, black", "ACCEPT", "series_variety", "black pepper"),
    ("Spices, pepper, white", "ACCEPT", "series_variety", "white pepper"),
    ("Spices, pepper, red or cayenne", "QUEUE", "qualifier_unresolved", None),
    ("Spices, curry powder", "QUEUE", "form_embedded_in_name", None),
    ("Spices, garlic powder", "QUEUE", "form_embedded_in_name", None),
    ("Spices, pumpkin pie spice", "QUEUE", "blend_name", None),
    ("Vinegar, distilled", "QUEUE", "qualifier_unresolved", None),
    ("Mustard, prepared, yellow", "REJECT", "processed", None),
    ("Capers, canned", "REJECT", "processed", None),
    ("Vanilla extract, imitation, alcohol", "REJECT", "processed", None),
    ("Seasoning mix, dry, taco, original", "REJECT", "processed", None),
    ("Spices, poultry seasoning", "REJECT", "processed", None),
    ("Salt, table, iodized", "REJECT", "group2_head", None),
])
def test_decisions_for_every_branch(desc, decision, code, term):
    d = ct.decide(row(desc), RULE)
    assert (d["decision"], d["reason_code"], d["term"]) == (decision, code, term), d


@pytest.mark.parametrize("cat", ["Nut and Seed Products", "Fruits and Fruit Juices", "Cereal Grains and Pasta"])
def test_conditioned_clauses_are_label_bound_and_never_pass(cat):
    for desc in ["Almonds", "Nuts, almonds", "Apple juice", "Corn flakes", "Oats"]:        # plain-looking single-word terms get no automatic pass
        d = ct.decide(row(desc, cat), RULE)
        assert d["decision"] == "LABEL_BOUND" and d["term"] is None, (cat, desc)
        assert "plain form" in d["reason"]


def test_no_category_other_than_spices_and_herbs_is_ever_accepted():
    cats = ["Dairy and Egg Products", "Baby Foods", "Fats and Oils", "Vegetables and Vegetable Products", "Legumes and Legume Products", "Snacks", "Beverages",
            "Nut and Seed Products", "Fruits and Fruit Juices", "Cereal Grains and Pasta", "Sweets", ""]
    for cat in cats:
        for desc in ["Spices, bay leaf", "Basil, fresh", "Almonds"]:
            assert ct.decide(row(desc, cat), RULE)["decision"] in ("LABEL_BOUND", "OUT_OF_SCOPE"), (cat, desc)


def test_staged_rows_are_names_only_provisional_with_the_verbatim_clause_and_merged_provenance():
    rows = [row("Spices, thyme, dried", fdc="10"), row("Thyme, fresh", fdc="11"), row("Spices, curry powder", fdc="12"), row("Salt, table", fdc="13")]
    decisions, staged = ct.map_candidates(rows, RULE)
    assert [s["term"] for s in staged] == ["thyme"]                                   # queued and rejected rows are not staged
    s = staged[0]
    assert s["kind"] == "herb_spice" and s["fdc_ids"] == "fdc_sr_legacy:10;fdc_sr_legacy:11" and s["rule_id"] == RULE["rule_id"]
    assert s["source"].startswith("PROVISIONAL: FAO 2019 (ca5644en.pdf) Table 1 Group 1 p.11 \"" + RULE["clause"]["text"] + "\"")
    assert "FDC id 10" in s["source"] and "FDC id 11" in s["source"] and "CC0 1.0" in s["source"]
    assert set(s) == {"term", "kind", "source", "fdc_ids", "rule_id"}                  # no NOVA group, no group field of any kind
    assert len(decisions) == 4 and all(d["decision"] and d["reason_code"] for d in decisions)


def test_fao_clause_check_rebuilds_the_two_column_table():
    text = ("TABLE 1. THE NOVA FOOD CLASSIFICATION SYSTEM\n"
            " NOVA GROUP     DEFINITION             EXAMPLES\n"
            " |GROUP 1|      Unprocessed            legumes such as beans; herbs and\n"
            "                Edible parts           spices used in culinary preparations, such as thyme,\n"
            "                of plants              oregano, mint, pepper, cloves and cinnamon, whole or\n"
            "                                       powdered, fresh or dried; tea\n"
            "TABLE 1. Cont.\n")
    assert ct.fao_clause_present(text, RULE["clause"]["text"])
    assert not ct.fao_clause_present(text.replace("fresh or dried", "fresh or tinned"), RULE["clause"]["text"])
    assert not ct.fao_clause_present("no table here", RULE["clause"]["text"])


def test_cli_writes_decisions_and_staged_rows_and_refuses_to_overwrite(tmp_path, capsys):
    cand = tmp_path / "c.csv"
    import csv
    with cand.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["candidate_id", "dataset", "fdc_id", "description", "parts", "food_category"], lineterminator="\n")
        w.writeheader()
        for r in [row("Spices, bay leaf", fdc="1"), row("Salt, table", fdc="2"), row("Almonds", "Nut and Seed Products", fdc="3")]:
            w.writerow({k: r[k] for k in w.fieldnames})
    out = tmp_path / "o"
    assert ct.main(["--candidates", str(cand), "--out", str(out)]) == 0
    assert sorted(p.name for p in out.iterdir()) == ["decisions.csv", "staged_rows.csv"]
    assert "ACCEPT': 1" in capsys.readouterr().out
    assert ct.main(["--candidates", str(cand), "--out", str(out)]) == 2
    assert ct.main(["--candidates", str(cand), "--out", str(out), "--force"]) == 0
