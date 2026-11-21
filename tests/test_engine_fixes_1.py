"""engine-fixes-1 (SYNTHETIC): the synonym rewrite is target-safe. An alias that is a strict word-prefix of its OWN target must not fire inside the target's name; elsewhere the rewrite is unchanged."""
from __future__ import annotations

import foodscan.normalise as nm
from foodscan.normalise import normalise_ingredient
from foodscan.pipeline import analyse_text


def with_rows(monkeypatch, rows):
    monkeypatch.setattr(nm, "load_table", lambda name: rows if name == "synonyms.csv" else nm.load_table.__wrapped__(name) if hasattr(nm.load_table, "__wrapped__") else [])
    nm._synonyms.cache_clear()


def test_synthetic_prefix_alias_rewrites_once_and_leaves_its_own_target_alone(monkeypatch):
    with_rows(monkeypatch, [{"from": "bok choy", "to": "bok choy cabbage", "source": "t"}, {"from": "jerusalem", "to": "jerusalem artichokes", "source": "t"}, {"from": "moong", "to": "moong dal", "source": "t"}])
    try:
        assert nm._apply_synonyms("bok choy") == "bok choy cabbage"
        assert nm._apply_synonyms("bok choy cabbage") == "bok choy cabbage"                 # the defect: used to become 'bok choy cabbage cabbage'
        assert nm._apply_synonyms("jerusalem artichokes") == "jerusalem artichokes"
        assert nm._apply_synonyms("jerusalem") == "jerusalem artichokes"
        assert nm._apply_synonyms("moong dal") == "moong dal" and nm._apply_synonyms("moong") == "moong dal"
        assert nm._apply_synonyms("bok choy, bok choy cabbage") == "bok choy cabbage, bok choy cabbage"
        assert nm._apply_synonyms("baby bok choy") == "baby bok choy cabbage"              # a longer phrase that merely contains the alias still expands (unchanged behaviour)
    finally:
        monkeypatch.undo()
        nm._synonyms.cache_clear()


def test_synthetic_a_non_prefix_alias_is_unchanged(monkeypatch):
    with_rows(monkeypatch, [{"from": "pak choi", "to": "bok choy cabbage", "source": "t"}, {"from": "rapini", "to": "broccoli raab", "source": "t"}])
    try:
        assert nm._apply_synonyms("pak choi") == "bok choy cabbage" and nm._apply_synonyms("rapini rapini") == "broccoli raab broccoli raab"
    finally:
        monkeypatch.undo()
        nm._synonyms.cache_clear()


def test_synthetic_the_shipped_bok_choy_row_routes_and_the_canonical_row_is_unchanged():
    assert normalise_ingredient("bok choy").name == "bok choy cabbage" and normalise_ingredient("bok choy cabbage").name == "bok choy cabbage"
    assert normalise_ingredient("pak choi").name == "bok choy cabbage"
    for t in ("Bok Choy Cabbage", "Bok Choy", "Pak Choi", "Bok Choy (raw)"):
        a = analyse_text(f"Ingredients: {t}.", source="text")
        assert a.answered and a.group == 1 and a.unassessed == [], t
    assert analyse_text("Ingredients: Salted Bok Choy.", source="text").group == 3                 # the canonical row's conditions apply through the alias


def test_synthetic_the_chinese_cabbage_row_cites_pe_tsai_only_and_says_why():
    import csv
    from pathlib import Path
    rows = {r["term"]: r for r in csv.DictReader((Path(__file__).resolve().parent.parent / "src" / "foodscan" / "resources" / "lexicon.csv").open(encoding="utf-8-sig", newline=""))}
    s = rows["chinese cabbage"]["source"]
    assert rows["chinese cabbage"]["kind"] == "vegetable" and 'FDC id 169979 "Cabbage, chinese (pe-tsai), raw"' in s
    assert "CORRECTION (engine-fixes-1)" in s and "pak choi, bok choy" in s and s.count("FDC id 170390") == 1             # the one mention is the correction note, not a citation of the pak-choi record
    assert "FDC id 170390" in rows["chinese cabbage"]["source"] and "in error" in s
