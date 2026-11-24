"""cocoa-powder-24 (SYNTHETIC): one `culinary` row (cocoa powder), demand-led (rank-5 open demand term; inputs b1/N14 'Cocoa Powder (7%)' and b3/Q12 'Cocoa Powder (1.5%)' now assess).
Placement: class-instance of FAO 2019 (ca5644en.pdf) Table 1 Group 2 general definition (p.11), corroborated by an exact-named PMC10127522 table footnote 5 ('cocoa powder' under 'Other processed culinary ingredients'; licence unverified: short quote only).
Conditions: plain cocoa powder only. Sweetened cocoa mixes, drinking chocolate and cocoa confectionery are not covered; ambiguous/held cocoa forms stay abstained; no alias is assumed for bare 'cocoa'."""
from __future__ import annotations

import csv
from pathlib import Path

from foodscan.pipeline import analyse_text


def g(text):
    a = analyse_text(f"Ingredients: {text}.", source="text")
    return (a.group if a.answered else None), a


def test_synthetic_plain_cocoa_powder_is_group_2_with_the_single_culinary_driver():
    group, a = g("cocoa powder")
    assert group == 2 and a.drivers[0].detail == "single processed culinary ingredient"


def test_synthetic_percentage_case_and_unsweetened_forms_are_group_2():
    for f in ("Cocoa Powder (5%)", "Cocoa Powder (1.5%)", "COCOA POWDER", "Cocoa Powder (unsweetened)"):
        assert g(f)[0] == 2, f


def test_synthetic_bracket_additions_abstain_with_the_plain_food_condition():
    # the pmc-reresearch-4 park mechanism (cocoa_powder_residual): anything in the bracket beyond a share or the
    # condition word leaves the item's composition unestablished
    for f in ("Cocoa Powder (Sugar)", "cocoa powder (alkalised)", "Cocoa Powder (Milk)"):
        group, a = g(f)
        assert group is None and "cocoa powder" in a.reason and "not established as plain cocoa powder" in a.reason, (f, a.reason)
    # an independent strong marker still decides first: a declared flavour makes the list ultra-processed
    assert g("Cocoa Powder (sugar, flavour)")[0] == 4


def test_synthetic_ambiguous_and_held_cocoa_forms_stay_abstained():
    # bare 'cocoa' is ambiguous (powder, mass or drinking cocoa: no alias assumed); cocoa solids stays held
    # (composition ambiguity, no exact-named source); cocoa nibs is a different food with no placement yet;
    # sweetened and dutch/alkalised named forms are conditioned forms outside the row's plain-only scope.
    for f in ("cocoa", "cocoa solids", "COCOA SOLIDS (1%)", "cocoa nibs", "sweetened cocoa powder", "dutch cocoa powder", "unsweetened cocoa powder", "cocoa mass"):
        assert g(f)[0] is None, f


def test_synthetic_lists_with_cocoa_powder_follow_the_existing_rules():
    assert g("cocoa powder, sugar")[0] is None  # two culinary items: existing culinary-mixture abstention
    assert g("Milk, Cocoa Powder, Sugar")[0] == 3  # whole food plus culinary ingredients: processed
    assert g("cocoa butter")[0] == 2  # existing neighbouring row unchanged


def test_synthetic_row_provenance_has_clause_and_no_purity_claim():
    root = Path(__file__).resolve().parent.parent
    rows = {r["term"]: r["source"] for r in csv.DictReader((root / "src" / "foodscan" / "resources" / "lexicon.csv").open(encoding="utf-8-sig", newline=""))}
    s = rows["cocoa powder"]
    assert s.startswith("PROVISIONAL (cocoa-powder-24)")
    assert "pressing, centrifuging, refining, extracting or mining" in s  # verbatim FAO Group 2 definition clause
    assert "PMC10127522" in s and "footnote 5" in s and '"cocoa powder"' in s
    assert "class-instance" in s and "NAMED" not in s and "pure" not in s.replace("purity", "")
    assert "NOT covered" in s and "not a strong marker" in s
