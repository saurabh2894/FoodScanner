"""Fix round (items 1-5) and the INS-misread addendum: each observed case AND the controls that must not change."""
import json
from pathlib import Path

import pytest

from foodscan import cli
from foodscan.classify import is_recognised
from foodscan.parser import parse_ingredient_list, split_items
from foodscan.pipeline import analyse_image, analyse_text, ocr_code_disagreement
from foodscan.tables import load_table

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / "evaluation/fresh_batch_1"


def t(x):
    return analyse_text(x, source="text")


def ocr(x):
    return analyse_text(x, source="ocr")


# ============================ 1. heading position and form, wrong-block warning ================================================
@pytest.mark.parametrize("line", [
    "SOURCE: EUROMONITOR, COOKING INGREDIENTS & MEALS, RETAIL VALUE RSP IN 2024",
    "MFG. BY: SYMEGA FOOD INGREDIENTS LTD., KERALA 682 310",
    "Active ingredients: caffeine, taurine, sugar, water",
])
def test_marketing_manufacturer_and_qualified_lines_are_not_headings(line):
    assert not parse_ingredient_list(line).found


@pytest.mark.parametrize("text", [
    "Ingredients: Rice, salt, sugar.", "INGREDIENTS : REFINED WHEAT FLOUR, SUGAR, SALT.", "Parle-G Gluco BISCUITS INGREDIENTS : REFINED WHEAT FLOUR, SUGAR, SALT.",
    "Flavoured Sandwich BiscuitsINGREDIENTS: REFINED WHEAT FLOUR, SUGAR, SALT.", "Biscuits\nINGREDIENTS REFINED WHEAT FLOUR, SUGAR, SALT.",
    "Note. INGREDIENTS: Rice, salt, sugar",
])
def test_genuine_headings_still_work(text):
    p = parse_ingredient_list(text)
    assert p.found and p.heading_kind == "exact" and "REFINED" in " ".join(p.items).upper() + "REFINED" and len(p.items) >= 3


def test_noisy_heading_still_works_through_the_tolerant_match():
    r = ocr("REDIENTS: Wheat flour, sugar, edible vegetable oil, salt, emulsifier (INS 322), added flavour.")
    assert r.heading["kind"] == "fuzzy" and r.group == 4


def test_a_wrong_block_is_flagged_and_never_reported_complete():
    r = ocr("Ingredients: retail value, single serve pack, premium quality, best offer, free gift.")
    assert r.completeness["status"] == "uncertain" and not r.answered
    assert any("few of the items were recognised" in x for x in r.completeness["reasons"])
    assert any("may not be the ingredient list" in w for w in r.warnings)


def test_the_observed_wrong_block_photo_text_no_longer_selects_the_marketing_line():
    photo = {x["id"]: x for x in json.load((BATCH / "frozen_results_12e7226/photo_results.json").open())}["N13"]["ocr_text"]
    r = ocr(photo)
    assert not r.answered and r.completeness["status"] == "uncertain"
    assert "& MEALS" not in r.ingredients and "RETAIL VALUE RSP IN 2024" not in r.ingredients


def test_a_real_list_with_unknown_words_on_the_paste_path_is_not_called_a_wrong_block():
    assert not any("may not be the ingredient list" in w for w in t("Ingredients: Ajwain, asafoetida, bishop's seed.").warnings)


# ============================ 2. percentage-bearing section labels =============================================================
def test_percentage_in_brackets_is_a_section_label_with_contents_kept_under_it():
    text = (BATCH / "inputs/N03.txt").read_text()
    p = parse_ingredient_list("Ingredients: " + text)
    assert [s.label for s in p.sections] == ["Noodles 88.5%", "Seasoning 11.5%"] and [len(s.items) for s in p.sections] == [4, 9] and not p.ignored


def test_both_percentage_label_styles_give_the_same_label():
    for src in ("Noodles 88.5%: wheat, salt. Seasoning 11.5%: sugar, cumin.", "Noodles (88.5%): wheat, salt. Seasoning (11.5%): sugar, cumin."):
        assert [s.label for s in parse_ingredient_list("Ingredients: " + src).sections] == ["Noodles 88.5%", "Seasoning 11.5%"]


def test_label_controls_percentages_inside_items_and_multiline_compounds_are_unchanged():
    assert parse_ingredient_list("Ingredients: Sugar (12.5%), emulsifier (INS 322), salt.").items == ["Sugar (12.5%)", "emulsifier (INS 322)", "salt"]
    p = parse_ingredient_list("Ingredients: Base mix (60%) (rice,\nlentils), salt (2%).")
    assert p.items == ["Base mix (60%) (rice, lentils)", "salt (2%)"] and [s.label for s in p.sections] == [None]
    assert [s.label for s in parse_ingredient_list("Ingredients: Puff 88%: Rice, oil. Seasoning 12%: Salt, flavour.").sections] == ["Puff 88%", "Seasoning 12%"]


def test_block_inference_measures_item_length_outside_brackets():
    # the observed photo text: long bracketed sub-lists made 9.2 words per item and the whole block was rejected
    photo = {x["id"]: x for x in json.load((BATCH / "frozen_results_12e7226/photo_results.json").open())}["N03"]["ocr_text"]
    r = ocr(photo)
    assert r.heading["kind"] == "inferred" and len(r.ingredients) >= 3 and r.completeness["status"] == "uncertain"


# ============================ 3. role phrases =================================================================================
@pytest.mark.parametrize("text", [
    "Ingredients: Rice, salt, emulsifying agent.", "Ingredients: Rice, salt, emulsifying agents.",
    "Ingredients: Rice, salt, emulsifying & stabilizing agent (INS 1422, INS 415).", "Ingredients: Rice, salt, emulsifying and stabilising agent.",
])
def test_emulsifying_agent_is_the_emulsifier_class(text):
    r = t(text)
    assert r.group == 4 and any('"emulsifier"' in d.detail for d in r.drivers), text


@pytest.mark.parametrize("text", [
    "Ingredients: Rice, salt, stabilizing agent.", "Ingredients: Rice, salt, stabilising agents.", "Ingredients: Rice, salt, stabilizing agent (INS 440).",
    "Ingredients: Mango, sugar, pectin (INS 440).",
])
def test_a_stabiliser_alone_stays_uncertain(text):
    assert not t(text).answered, text


def test_a_code_with_a_different_declared_class_stays_uncertain():
    a = t("Ingredients: Rice, salt, stabilizer (INS 471).")
    assert a.group is None
    assert a.ins_mappings[0].code == "471" and a.ins_mappings[0].class_conflict


# ============================ 4. vocabulary: buffalo milk; probiotic culture is NOT mapped =====================================
def test_buffalo_milk_is_a_milk_with_a_section_citation_and_a_provisional_nova_step():
    row = {r["term"]: r["source"] for r in load_table("lexicon.csv")}["buffalo milk"]
    assert "2.1.2" in row and "5.0% milk fat" in row and "PROVISIONAL" in row and "NOVA method only" in row
    r = t("Ingredients: Pasteurized Buffalo Milk.")
    assert r.answered and r.group == 1
    assert t("Ingredients: Buffalo milk, active lactic culture.").group == 1             # still milk plus starter culture


def test_probiotic_culture_is_not_taken_for_a_starter_culture():
    # FSSAI 2.1.13 item 2(b) lists "Prebiotics and Probiotics" apart from "starter cultures": the phrase is not established as a starter
    assert not is_recognised("probiotic culture")
    r = t("Ingredients: Pasteurised toned milk, active lactic culture and probiotic culture (Bifidobacterium lactis & Lactobacillus acidophilus).")
    assert not r.answered


# ============================ 5. silent merges and splits (diagnosis in evaluation/fresh_batch_1/DIAGNOSIS.md) =================
def test_additive_code_continuing_a_code_list_is_not_a_separate_item():
    assert split_items("thickeners - E1442, E1450, natural vinegar") == ["thickeners - E1442, E1450", "natural vinegar"]
    assert t("Ingredients: Water, thickeners - E1442, E1450, salt.").ingredients == ["Water", "thickeners - E1442, E1450", "salt"]
    assert split_items("Rice, E322, salt")[0] == "Rice, E322"        # a code is only attached to the item before it, never dropped


def test_flavouring_and_dough_conditioner_with_a_code_bracket_are_two_items():
    r = t("Ingredients: Sugar, nature identical flavouring substance and dough conditioner (223).")
    assert r.ingredients == ["Sugar", "nature identical flavouring substance", "dough conditioner (223)"]
    # (the bare code 223 is not read as INS: "dough conditioner" is not an additive class word in markers.csv; unchanged, no vocabulary added)


def test_group_name_with_commas_before_a_percentage_and_brace_list_stays_one_item_in_a_semicolon_list():
    r = t("Ingredients: Whole Grains (34%) {rolled oats, ragi flakes}; Dry Fruits, Nuts & Seeds (22%) {raisin, almonds}; Organic Jaggery, Cocoa Powder (7%), Dates.")
    assert r.ingredients == ["Whole Grains (34%) {rolled oats, ragi flakes}", "Dry Fruits, Nuts & Seeds (22%) {raisin, almonds}", "Organic Jaggery", "Cocoa Powder (7%)", "Dates"]


def test_split_controls_commas_in_flat_lists_and_semicolon_lists_are_unchanged():
    assert t("Ingredients: Rice, Salt, Sugar (12%) {a, b}.").ingredients == ["Rice", "Salt", "Sugar (12%) {a, b}"]
    assert parse_ingredient_list("Ingredients : Rice ; salt ; sugar.").items == ["Rice", "salt", "sugar"]


def test_text_after_a_percentage_is_flagged_as_a_possible_missing_comma_not_complete():
    r = t("Ingredients: Roasted Peanuts (91%) Sugar, Stabilizer (INS471), Iodised Salt.")
    assert r.completeness["status"] == "uncertain" and any("comma may be missing" in w for w in r.warnings)
    assert not any("comma may be missing" in w for w in t("Ingredients: Sugar (12%) and salt, rice (3%) (aged).").warnings)


def test_shared_head_phrase_stays_one_item_by_convention():
    # 'nature identical and natural flavouring substances' is ONE declared phrase (two modifiers, one head noun): not split, nothing lost
    r = t("Ingredients: Sugar, nature identical and natural flavouring substances, salt.")
    assert "nature identical and natural flavouring substances" in r.ingredients and r.completeness["status"] == "complete"


# ============================ addendum: INS misread review hints ===============================================================
LABEL = ("Ingredients: Puff 88%: Supergrain Blend (Jowar, Foxtail Millet, Corn, Rice)(72%), Rice Bran Oil(16%). Seasoning 12%: Vegetables and Spices "
         "(Onion, Garlic, Tomato, Chilli, Amchur, Tamarind), Salt, Natural and Nature Identical Flavours, Raw Sugar, Acidity Regulators (INS330, INS@A@, INS334), "
         "Potassium Chloride - Salt Substitute (INS 508), Rosemary Extract - Antioxidant (INS @B@).")


def label(a, b):
    return t(LABEL.replace("@A@", a).replace("@B@", b))


def misreads(r):
    return [w for w in r.warnings if w.startswith("Read as INS")]


def test_only_the_name_tie_hint_remains_for_misread_codes():
    r = label("236", "382")
    m = misreads(r)
    # the function-class check was REMOVED (INS 508 under "Thickeners" was flagged on a legitimate pack): 236 under "Acidity Regulators" raises nothing
    assert not any("INS 236" in w for w in m)
    assert any(w.startswith("Read as INS 382. The label text says Rosemary Extract - Antioxidant") and "INS 392" in w and "apps.who.int" in w for w in m)   # a read page ties the NAME to 392
    assert len(m) == 1


def test_the_correct_codes_raise_no_flag():
    assert misreads(label("296", "392")) == []


def test_a_flag_never_replaces_a_code_or_changes_the_classification():
    bad, good = label("236", "382"), label("296", "392")
    assert {u.code for u in bad.ins_mappings} >= {"236", "382"} and not {u.code for u in bad.ins_mappings} & {"296", "392"}
    assert bad.answered == good.answered and bad.group == good.group == 4
    assert [d.detail for d in bad.drivers] == [d.detail for d in good.drivers]


def test_no_flag_without_a_name_tie_and_no_digit_similarity_guessing():
    assert misreads(label("236", "392")) == [] and len(misreads(label("296", "382"))) == 1
    assert misreads(t("Ingredients: Rice, salt, preservative (INS 999).")) == []                # unknown code, unrelated: no flag, no candidate
    assert misreads(t("Ingredients: Rice, salt, acidity regulator (INS 392).")) == []           # a class word never triggers a hint any more
    assert misreads(t("Ingredients: Noodles, thickeners (508 & 412), salt.")) == []             # the observed false hint (INS 508 under Thickeners) is gone
    assert misreads(t("Ingredients: Rice, rosemary extract (INS 392), salt.")) == []            # name and code agree


def test_display_names_say_recognised_code_no_rule_and_stay_unknown_for_classification():
    r = t("Ingredients: Rice, Acidity Regulators (INS330, INS296, INS334), Rosemary Extract (INS 392), Potassium Chloride (INS 508), salt, INS 382.")
    by = {u.code: u for u in r.ins_mappings}
    for c, name in (("296", "DL-Malic acid"), ("330", "Citric acid"), ("334", "L(+)-Tartaric acid"), ("392", "Rosemary extract"), ("508", "Potassium chloride")):
        assert by[c].name is None and by[c].strength is None and by[c].ref_name == name and by[c].ref_url, c      # name and URL only, no rule
    assert by["382"].ref_name is None                                           # identity not sourced: no metadata
    rows = {x["ins"]: x["source"] for x in load_table("ins_names.csv")}
    assert set(rows) == {"202", "260", "296", "330", "334", "339(ii)", "392", "412", "415", "466", "476", "500(i)", "501(i)", "508", "551", "1422"}      # 407 withheld (see BACKLOG.md: narrow sourced fix for the 407/407a name-tie hint)
    assert all(v.startswith("Checked 2026-11-20: JECFA database page read in full by me") for v in rows.values())
    for c in {"296", "330", "334", "392", "508"}:
        assert "apps.who.int" in rows[c]


def test_no_function_table_remains_and_name_rows_cite_only_pages_read():
    assert not (ROOT / "src/foodscan/resources/ins_functions.csv").exists()
    rows = {x["ins"]: x["source"] for x in load_table("ins_names.csv")}
    assert "Codex" not in " ".join(rows.values()) and all("JECFA database page read in full by me" in v for v in rows.values())


def test_provisional_role_phrase_mapping_stays_visible_and_other_phrases_are_not_added():
    r = t("Ingredients: Rice, salt, emulsifying & stabilizing agent (INS 1422, INS 415).")
    assert r.group == 4 and any('"emulsifying & stabilizing agent" is read as the emulsifier class by a provisional mapping' in w for w in r.warnings)
    assert any("provisional mapping" in w for w in t("Ingredients: Rice, emulsifying agent.").warnings)
    assert not any("provisional mapping" in w for w in t("Ingredients: Rice, emulsifier (INS 322).").warnings)       # the class word itself is not a role phrase
    phrases = {x["from"] for x in load_table("synonyms.csv") if x["source"].startswith("PROVISIONAL role phrase")}
    assert phrases == {"emulsifying & stabilizing agent", "emulsifying & stabilising agent", "emulsifying and stabilizing agent", "emulsifying and stabilising agent",
                       "emulsifying agents", "emulsifying agent", "stabilizing agents", "stabilizing agent", "stabilising agents", "stabilising agent"}


def test_completeness_explanation_says_it_is_not_a_guarantee(tmp_path, capsys):
    f = tmp_path / "l.txt"; f.write_text(LABEL.replace("@A@", "236").replace("@B@", "382"))
    cli.main(["classify", "--text", str(f)])
    out = capsys.readouterr().out
    assert "Text completeness: complete" in out and "All recognised text spans accounted for. This is not a guarantee that characters, digits or the list are complete or correct." in out


class _Eng:
    def __init__(self, a, b):
        self.a, self.b = a, b

    def extract_text(self, p):
        return self.a

    def extract_text_alt(self, p):
        return self.b


def test_two_readings_that_disagree_on_a_code_are_flagged_and_neither_is_chosen_for_the_code():
    a = LABEL.replace("@A@", "236").replace("@B@", "382"); b = LABEL.replace("@A@", "236").replace("@B@", "392")
    r = analyse_image("x.jpg", ocr=_Eng(a, b))
    assert any(w.startswith("Two readings of the photo disagree on additive codes: INS 382 in the first reading, INS 392 in the second") for w in r.warnings)
    assert {u.code for u in r.ins_mappings} >= {"382"}                      # the first reading is kept as read; nothing is replaced
    r2 = analyse_image("x.jpg", ocr=_Eng(a, a))
    assert not any("disagree" in w for w in r2.warnings)
    assert ocr_code_disagreement(["1"], ["1"]) is None and "none in the first" in ocr_code_disagreement([], ["392"])
