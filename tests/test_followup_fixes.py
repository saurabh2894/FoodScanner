"""Follow-up fixes (items 1-7 of the combined prompt): every observed case AND the controls that must not change."""
import re
from pathlib import Path

import pytest

from foodscan import pipeline
from foodscan.classify import is_recognised, lookup
from foodscan.parser import parse_ingredient_list, split_top_level_and_ex, unclosed_openers
from foodscan.pipeline import analyse_image, analyse_text
from foodscan.tables import load_table

F07 = (Path(__file__).resolve().parent.parent / "evaluation/dev_regression_15/inputs/F07.txt")


def a(t):
    return analyse_text(t, source="text")


def words(s):
    return re.findall(r"[^\W_]+", s.lower())


# ============================ 1. flavour inside a colour note is not independent evidence ====================================
@pytest.mark.parametrize("note", ["colour & flavour", "colouring and flavouring", "colour & spices"])
def test_markers_inside_the_same_note_cannot_decide_group_4(note):
    r = a(f"Ingredients: Rice, salt, turmeric ({note}).")
    assert not r.answered and not r.drivers


def test_controls_for_the_note_fix():
    assert a("Ingredients: Rice, salt, turmeric (colour), added flavour.").group == 4          # separate flavour item decides
    assert a("Ingredients: Rice, salt, turmeric (colour), colour (INS 150d).").group == 4      # declared colour decides
    assert a("Ingredients: Butter, colour (INS 160b).").group == 4                             # provisional, documented


# ============================ 2. one code list shared by two additive classes =================================================
SHARED = "Ingredients: Water, sugar, emulsifiers and stabilizers [INS 460(i), INS 471, INS 466], salt."


def test_shared_trailing_code_list_is_not_split_and_codes_are_not_duplicated():
    r = a(SHARED)
    assert any(i.lower().startswith("emulsifiers and stabilizers") for i in r.ingredients)
    assert "stabilizers [INS 460(i), INS 471, INS 466]" not in r.ingredients          # codes were not pinned on the last class alone
    assert {u.code for u in r.ins_mappings} == {"460(i)", "471", "466"}
    assert len({u.ingredient for u in r.ins_mappings}) == 1                           # one item owns the whole shared list
    assert r.group == 4 and r.completeness["status"] == "complete"


def test_controls_for_shared_lists():
    assert a("Ingredients: Rice, raising agents (INS 500(ii), INS 503(ii)), salt.").ingredients[1] == "raising agents (INS 500(ii), INS 503(ii))"
    assert "Spices and Condiments" in a("Ingredients: Rice, Spices and Condiments, salt.").ingredients
    r = a("Ingredients: Sugar, emulsifier [472e] and flour treatment agent [1101(ii)], salt.")      # each side has its own codes: still split
    assert "emulsifier [472e]" in r.ingredients and "flour treatment agent [1101(ii)]" in r.ingredients


def test_a_split_that_drops_a_word_is_caught_by_the_completeness_accounting(monkeypatch):
    raw = "emulsifier [472e] and sweetener [950]"
    # a faulty split that loses the word "950" (both remaining sides are still recognisable, so the pair is split)
    monkeypatch.setattr(pipeline, "split_top_level_and_ex", lambda r: (["emulsifier [472e]", "sweetener"], ["and"]) if r == raw else split_top_level_and_ex(r))
    r = a(f"Ingredients: Sugar, {raw}, salt.")
    assert r.completeness["words"]["unaccounted"] >= 1 and r.completeness["status"] == "uncertain"
    assert any("neither read" in x for x in r.completeness["reasons"])


# ============================ 3. an unmatched bracket: nothing vanishes, the stray bracket is named ============================
@pytest.mark.parametrize("text", [
    "Ingredients: Rice, Corn (3%, salt, sugar, added flavour. Store in a cool place.",
    "Ingredients: Rice, Corn {wheat flour (3%), sugar, salt, added flavour, palm oil.",
    "Ingredients: Rice, salt, Sugar [aged, flavour enhancer (INS 627), oil. Contains milk.",
])
def test_unclosed_bracket_is_named_and_loses_nothing_silently(text):
    r = a(text)
    assert any("was never closed" in w for w in r.warnings), text
    assert r.completeness["status"] == "uncertain" and r.completeness["words"]["unaccounted"] == 0
    body = text.split("Ingredients:")[1]
    kept = " ".join(r.ingredients + r.ignored + [d["text"] for d in r.declared])
    # every ingredient word of the list region reaches an item (the stop-phrase tail is set aside, not lost)
    region = re.split(r"(?i)\bcontains\b|\bstore in\b", body)[0]
    assert all(w in words(kept) for w in words(region))
    assert r.answered is False or r.group == 4          # only a strong-marker Group 4 stands (Option A)


def test_unclosed_openers_helper():
    assert unclosed_openers("Rice, Corn {wheat flour (3%), sugar")[0].startswith("Rice, Corn {")
    assert unclosed_openers("Rice (a, b), salt") == []


def test_balanced_multi_bracket_and_multi_line_lists_are_unchanged():
    r = parse_ingredient_list("Ingredients: Rice,\nCorn (3%,\nsalt),\nsugar [a (b)], oil.")
    assert r.items == ["Rice", "Corn (3%, salt)", "sugar [a (b)]", "oil"] and not r.unbalanced_brackets
    assert not any("never closed" in w for w in a("Ingredients: Rice, Corn (3%, salt), sugar [a (b)], oil.").warnings)


# ============================ 4. later sections, repeated and qualified labels ================================================
def test_observed_label_keeps_all_three_sections_including_the_qualified_one():
    p = parse_ingredient_list(F07.read_text(), assume_list=True)
    assert [s.label for s in p.sections] == ["Instant noodles", "Seasoning: masala mix", "Sprinkler mix (topping)"]
    assert [len(s.items) for s in p.sections] == [7, 11, 6] and not p.ignored
    assert not any("masala mix:" in i for i in p.items)        # the double label is no longer left inside an item


def test_repeated_section_labels_are_all_kept():
    p = parse_ingredient_list("Ingredients: Seasoning: salt, sugar. Seasoning: chilli, cumin. Seasoning: pepper, clove.")
    assert [s.label for s in p.sections] == ["Seasoning"] * 3 and p.items == ["salt", "sugar", "chilli", "cumin", "pepper", "clove"]


def test_a_section_that_cannot_be_read_is_flagged_not_dropped():
    r = a("Ingredients: Rice, salt. Topping 2: chilli, cumin, garlic.")
    assert any("Topping 2" in x for x in r.ignored) and r.completeness["words"]["not_read"] > 0
    assert r.completeness["status"] == "uncertain"


def test_single_and_multi_section_labels_unchanged():
    assert [s.label for s in parse_ingredient_list("Ingredients: Noodles: wheat flour, salt. Masala tastemaker: sugar, flavour.").sections] == ["Noodles", "Masala tastemaker"]
    assert [s.label for s in parse_ingredient_list("Ingredients: Puff 88%: Rice, Rice Bran Oil. Seasoning 12%: Salt, Flavour.").sections] == ["Puff 88%", "Seasoning 12%"]
    assert [s.label for s in parse_ingredient_list("Ingredients: Rice, salt.").sections] == [None]


# ============================ 5. one-line complete list is not "truncated" ====================================================
def test_complete_yoghurt_list_parses_clean():
    r = a("Pasteurized Toned Milk & Active Lactic Culture")
    assert r.ingredients == ["Pasteurized Toned Milk", "Active Lactic Culture"]
    assert r.completeness["status"] == "complete" and "truncated" not in (r.reason or "")
    assert not r.unassessed


def test_a_genuinely_cut_off_list_still_flags_truncated():
    r = a("Ingredients: Sugar, refined wheat flo")
    assert not r.answered and "truncated" in r.reason and r.completeness["status"] == "uncertain"
    r = a("Ingredients: Rice, Pasteurized Toned")
    assert not r.answered and "truncated" in r.reason


# ============================ 6. vocabulary: named gaps only, with the processing distinction recorded ========================
def test_named_terms_are_recognised_with_their_kind():
    assert lookup("besan")["kind"] == "flour"                                  # milled chickpea flour: flour kind, not a whole food
    assert lookup("toned milk")["kind"] == "whole_food" and lookup("dahi")["kind"] == "whole_food"
    assert lookup("active lactic culture")["kind"] == "culture"
    for t in ("bengal gram flour", "gram flour", "chickpea flour"):
        r = a(f"Ingredients: {t}.")
        assert r.ingredients and not r.unassessed, t


def test_new_rows_follow_the_citation_rule():
    """Every new row: the cited source names that exact term, or the row stays PROVISIONAL with the missing source stated.
    The NUPENS-USP page is the NOVA METHOD source only; it never backs a term's identity."""
    lex = {r["term"]: r["source"] for r in load_table("lexicon.csv")}
    for t in ("toned milk", "double toned milk", "dahi"):                 # named in the FSSAI dairy chapter (exact term, section given)
        assert "FSSAI" in lex[t] and "2.1." in lex[t] and "SHA-256" in lex[t], t
        assert "PROVISIONAL" in lex[t] and "NOVA method only" in lex[t], t     # the NOVA step stays provisional
    assert "milled" not in lex["toned milk"] and "standardised to 3.0% fat" in lex["toned milk"]
    assert "standardised to 1.5% fat" in lex["double toned milk"] and "plain dahi" in lex["dahi"].lower()
    assert lex["besan"].startswith("PROVISIONAL, source missing") and "NUPENS" in lex["besan"] and "FSSAI" in lex["besan"]
    for t in ("active lactic culture", "lactic culture", "live culture", "active culture", "yoghurt culture"):
        assert lex[t].startswith("PROVISIONAL, exact term not in a source") and "not the phrase" in lex[t], t
    assert "curd culture" not in lex                                         # unreachable (curd is rewritten to dahi) and unsourced
    syn = {r["from"]: r["source"] for r in load_table("synonyms.csv")}
    for t in ("bengal gram flour", "gram flour", "chickpea flour"):
        assert syn[t].startswith("PROVISIONAL, source missing"), t
    assert syn["curd"].startswith("PROVISIONAL") and "omits the word (Curd)" in syn["curd"]
    assert "double toned milk" not in syn and "double-toned milk" not in syn      # double toned milk has its own entry, not a synonym of toned milk
    r = a("Ingredients: Double-Toned Milk.")
    assert r.answered and r.group == 1 and not r.unassessed        # the hyphenated spelling reaches its own entry


def test_no_broad_batch_unknown_terms_still_abstain():
    for t in ("ajwain", "compounded asafoetida", "bishop's seed", "carom seeds"):
        if t in ("ajwain", "bishop's seed"):
            # Attributed exceptions (lexicon-1): the herb_spice rows "ajwain" and "bishop's seed" (lexicon.csv) rest on FAO 2019 Table 1 Group 1 p.11, "herbs and spices used
            # in culinary preparations ... whole or powdered, fresh or dried" (PROVISIONAL: exact term not named). These two terms are recognised now.
            # "compounded asafoetida" and "carom seeds" get no row and stay pinned as unrecognised.
            assert is_recognised(t), t
        else:
            assert not is_recognised(t), t
    assert not a("Ingredients: Bengal Gram Flour (Besan), Ajwain, Edible Common Salt.").answered


# ============================ 7. OCR second pass ==============================================================================
class _Engine:
    def __init__(self, first, second=None):
        self.first, self.second, self.calls = first, second, []

    def extract_text(self, p):
        self.calls.append("first"); return self.first

    def extract_text_alt(self, p):
        self.calls.append("second"); return self.second


CLEAN = "Ingredients: Sugar, palm oil, emulsifier (INS 322), added flavour, salt."
NOISY = "Ingredients: Sug4r palm 0il emuls1fier flav0ur xx"


CLEAN_NO_CODES = "Ingredients: Sugar, palm oil, added flavour, salt."


def test_second_pass_is_skipped_when_the_first_reading_is_clean_and_has_no_codes():
    e = _Engine(CLEAN_NO_CODES, NOISY)
    assert analyse_image("x.jpg", ocr=e).group == 4 and e.calls == ["first"]


def test_second_pass_also_runs_when_the_first_reading_holds_additive_codes():
    e = _Engine(CLEAN, CLEAN)                                           # digits are what OCR confuses most
    r = analyse_image("x.jpg", ocr=e)
    assert e.calls == ["first", "second"] and r.group == 4 and not any("disagree" in w for w in r.warnings)


def test_second_pass_with_better_yield_is_used():
    e = _Engine(NOISY, CLEAN)
    r = analyse_image("x.jpg", ocr=e)
    assert e.calls == ["first", "second"] and r.group == 4 and "Sugar" in r.ingredients


def test_a_worse_or_equal_second_reading_keeps_the_first():
    e = _Engine("Ingredients: Sugar, salt, oil, flo", "Ingredients: Sugar")
    r = analyse_image("x.jpg", ocr=e)
    assert r.ingredients[0] == "Sugar" and len(r.ingredients) == 4


def test_flatten_lighting_returns_a_same_size_greyscale_image():
    np = pytest.importorskip("numpy")
    from PIL import Image

    from foodscan.ocr import flatten_lighting
    img = Image.fromarray((np.tile(np.linspace(40, 220, 300), (200, 1))).astype("uint8"))     # a lighting gradient
    out = flatten_lighting(img)
    assert out.mode == "L" and out.size == img.size
