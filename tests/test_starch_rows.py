"""Plain starch rows (owner lift, pmc-decisions-1): ONLY plain/unmodified starch; modified forms are never captured (SYNTHETIC cases, hard condition negative tests)."""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from foodscan.classify import is_recognised
from foodscan.normalise import normalise_ingredient
from foodscan.pipeline import analyse_text

ROOT = Path(__file__).resolve().parent.parent
LEX = {r["term"]: r for r in csv.DictReader((ROOT / "src" / "foodscan" / "resources" / "lexicon.csv").open(encoding="utf-8-sig", newline=""))}


def g(text):
    a = analyse_text(f"Ingredients: {text}.", source="text")
    return (a.group if a.answered else None), a


@pytest.mark.parametrize("t", ["starch", "tapioca starch"])
def test_synthetic_plain_starch_rows_quote_the_fao_clause_and_cite_pmc_as_licence_unverified_paraphrase(t):
    s = LEX[t]["source"]
    assert LEX[t]["kind"] == "culinary" and "starches extracted from corn and other plants" in s and "PMC10127522" in s and "licence unverified" in s and "paraphrase" in s


def test_synthetic_plain_starch_behaves_as_a_group_2_ingredient():
    assert g("Starch")[0] == 2 and g("Rice, starch")[0] == 3 and g("Rice, tapioca starch, salt")[0] == 3


@pytest.mark.parametrize("t", ["Starch (Modified)", "starch (acid treated)", "Tapioca Starch (Oxidised)", "Starch (pregelatinised)", "Starch (cross-linked)", "starch (modified) (INS 1422)", "Modified Starch (INS 1420)", "modified starch"])
def test_synthetic_negative_modified_forms_are_never_captured_by_the_plain_rows_they_stay_the_strong_group_4_marker(t):
    group, a = g(f"Rice, {t}")
    assert group == 4 and any("modified starch" in d.detail for d in a.drivers), (t, group)
    assert not any(d.detail == "single processed culinary ingredient" for d in a.drivers)


@pytest.mark.parametrize("t", ["modified corn starch", "modified tapioca starch", "pregelatinised starch", "acid treated starch", "oxidised starch", "corn starch", "maize starch", "potato starch", "starch, modified"])
def test_synthetic_negative_other_starch_names_retain_holds_except_source_reviewed_corn(t):
    if t in {'corn starch', 'maize starch'}:
        # direct-culinary-2: exact corn-starch class + corn/maize identity; not a
        # generic starch-name lift. Modified and potato controls below stay held.
        assert normalise_ingredient(t).name == 'corn starch'
        assert g(t)[0] == 2
        assert 'starches extracted from corn and other plants' in LEX['corn starch']['source']
    else:
        assert not is_recognised(normalise_ingredient(t).name)


def test_synthetic_the_modified_starch_marker_row_is_unchanged():
    m = {r["term"]: r for r in csv.DictReader((ROOT / "src" / "foodscan" / "resources" / "markers.csv").open(encoding="utf-8-sig", newline=""))}["modified starch"]
    assert m["strength"] == "strong" and m["marker_class"] == "derived_substance"
