"""Rules-only NOVA classifier (marker-ingredient approach).

Source for every rule: research/02-research-nova-and-ingredients.txt.
  * Group 4 needs >= 1 STRONG marker (marker class 1 derived substances, or
    marker class 2 cosmetic additive classes). Rule from "Marker classes".
  * Weak / ambiguous markers alone (pectin, raising agents) and additive
    classes not named in the research (preservative, ...) never decide a group:
    result is uncertain ("Important qualifications").
  * No ingredient-count rules anywhere ("What an ingredient list can and cannot tell you").
  * Groups 1-3 are only called for lists made entirely of recognised foods
    (resources/lexicon.csv). Flour-based multi-ingredient lists are uncertain
    because bakery-fresh vs industrial is not decidable from the label
    (research/02: bread example).
  * Anything else -> group None with a reason. Never a guess.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import cache

from .normalise import Ingredient, flatten, normalise_ingredient, normalise_list, _split_brackets, is_additive_absence_claim
from .tables import load_table


@dataclass(frozen=True)
class Driver:
    ingredient: str       # raw ingredient text
    detail: str           # what about it drove the decision
    source: str
    section: str | None = None   # list section the ingredient came from, if the label had sections


@dataclass
class Classification:
    group: int | None
    drivers: list[Driver] = field(default_factory=list)
    reason: str | None = None   # set when group is None (why uncertain)


@cache
def _markers() -> tuple[tuple[re.Pattern, dict], ...]:
    out = []
    for r in load_table("markers.csv"):
        term = flatten(r["term"])
        out.append((re.compile(rf"(?<![a-z])(?<!no )(?<!no added )(?<!non )(?<!non-)(?<!without )(?<!free from )(?<!free of )(?<!source of )(?<!rich in )(?<!high in ){re.escape(term)}(?![a-z])(?![ -]free(?![a-z]))"), r))
    return tuple(out)


@cache
def _claim_markers() -> tuple[tuple[re.Pattern, dict], ...]:
    """A marker term directly after "source of", "rich in" or "high in". The wording can describe a natural content or an added isolated ingredient, so on its own it neither proves nor disproves the marker: it is read as an abstention (weak hit), never as a lower group and never as Group 4."""
    return tuple((re.compile(rf"(?<![a-z])(?:source of|rich in|high in) {re.escape(flatten(r['term']))}(?![a-z])(?![ -]free(?![a-z]))"), r) for r in load_table("markers.csv") if r["strength"] == "strong")


@cache
def lexicon() -> dict[str, dict[str, str]]:
    return {flatten(r["term"]): r for r in load_table("lexicon.csv")}


@cache
def _descriptors() -> frozenset:
    """Global descriptors: rows with no 'kinds' value. Kind-scoped rows (e.g. 'toasted': whole_food;flour) are in _scoped_descriptors()."""
    return frozenset(r["word"].lower() for r in load_table("descriptors.csv") if not (r.get("kinds") or "").strip())


@cache
def _scoped_descriptors() -> dict:
    return {r["word"].lower(): frozenset(k.strip() for k in r["kinds"].split(";") if k.strip()) for r in load_table("descriptors.csv") if (r.get("kinds") or "").strip()}


def _singular(tok: str) -> str:
    if len(tok) > 3 and tok.endswith("ies"):
        return tok[:-3] + "y"
    if len(tok) > 4 and tok.endswith("oes"):
        return tok[:-2]
    if len(tok) > 3 and tok.endswith("s") and not tok.endswith(("ss", "us", "is")):
        return tok[:-1]
    return tok


def _singular_phrase(phrase: str) -> str:
    return " ".join(_singular(t) for t in phrase.split())


@cache
def _lexicon_index() -> dict[str, dict[str, str]]:
    idx: dict[str, dict[str, str]] = {}
    for term, row in lexicon().items():
        idx.setdefault(_singular_phrase(term), row)
    return idx


# 'toasted' (per-form-1, owner amendment 2): source-fit plain grain forms ONLY. The word is dropped only when the remaining name resolves to one of the 23 terms Batch 4 placed (9 grain whole_food rows + 14 flour
# rows, enumerated in evaluation/per_form_1/README.md and asserted by tests/test_per_form_1.py), and the name carries NO other qualifier: the only other words allowed are benign condition/provenance words below.
# 'Toasted Salted Oat Flour', 'Toasted Sweetened Oat Flour', toasted milk/egg/anything else: not recognised (abstain). Global descriptors are NOT stripped on this path.
_SCOPED_TERMS = {"toasted": frozenset({"barley", "black rice", "buckwheat", "millet", "parboiled rice", "red rice", "rice", "sorghum", "wild rice",
                                       "amaranth flour", "barley flour", "buckwheat flour", "cornmeal", "millet flour", "oat flour", "quinoa flour", "rice flour", "rye flour", "semolina", "sorghum flour",
                                       "spelt flour", "wheat flour", "whole wheat flour"})}
_SCOPED_BENIGN = frozenset({"unsalted", "organic", "whole", "plain", "pure", "white", "brown", "red", "common", "edible"})


def _scoped_lookup(name: str, scoped: dict, lex: dict, idx: dict):
    words = {t for t in name.split() if t in scoped}
    others = [t for t in name.split() if t not in scoped]
    for cand in (" ".join(others), " ".join(t for t in others if t not in _SCOPED_BENIGN)):
        row = lex.get(cand) or idx.get(_singular_phrase(cand))
        if row and all(row["kind"] in scoped[w] and row["term"] in _SCOPED_TERMS.get(w, frozenset()) for w in words):
            return row
    return None


def lookup(name: str) -> dict[str, str] | None:
    """The lexicon row for an ingredient name, tolerant of ordinary wording.

    Order: exact term, singular form, then the same two after dropping descriptor words (descriptors.csv: edible,
    common, rolled, split, refined, powdered, ...). Used ONLY for recognising plain ingredients and their kind;
    markers are matched separately and always win. "flakes" is deliberately not a descriptor (corn flakes and wheat
    flakes are processed cereals), so oat flakes is an explicit synonym of oat instead."""
    lex, idx = lexicon(), _lexicon_index()
    if name in lex:
        return lex[name]
    if _singular_phrase(name) in idx:
        return idx[_singular_phrase(name)]
    toks = name.split()
    while toks and toks[0] in _descriptors():               # leading descriptors first: "pasteurised double toned milk" -> "double toned milk"
        toks = toks[1:]
        lead = " ".join(toks)
        if lead in lex:
            return lex[lead]
        if _singular_phrase(lead) in idx:
            return idx[_singular_phrase(lead)]
    kept = " ".join(t for t in name.split() if t not in _descriptors())
    if kept and kept != name:
        if kept in lex:
            return lex[kept]
        if _singular_phrase(kept) in idx:
            return idx[_singular_phrase(kept)]
    scoped = _scoped_descriptors()
    if any(t in scoped for t in name.split()):               # kind- and TERM-scoped descriptor ('toasted'): see _scoped_lookup
        return _scoped_lookup(name, scoped, lex, idx)
    return None


def named_water_unresolved(ing, sole=False) -> list[str]:
    """Exact dietary-water scope only; descriptor stripping is not form evidence."""
    out = []
    row = lookup(ing.name)
    if row and row["kind"] == "named_water":
        raw = ing.raw.lower().strip(" ,;:.")
        if not (sole and raw in ("carbonated water", "plain carbonated water")):
            out.append(ing.raw)
    for part in raw_bracket_parts(ing.raw):
        out.extend(named_water_unresolved(normalise_ingredient(part)))
    return out


def plain_juice_stated(ing) -> bool:
    """Narrow FAO fresh/pasteurized juice clause, no descriptor stripping as proof."""
    row = lookup(ing.name)
    if not row or row["kind"] != "fruit_juice":
        return False
    # An explicit 100% is about this item, not a bracket child or a product claim.
    term = re.escape(row["term"])
    quality = r"(?:fresh|pasteuri[sz]ed)"
    pct = r"100(?:\.0+)?\s*%"
    raw = ing.raw.lower().strip(" ,;:.")
    return bool(re.fullmatch(rf"(?:{pct}\s+{quality}|{quality}\s+{pct})\s+{term}", raw))


def nested_juice_unresolved(ing) -> list[str]:
    out = []
    for part in raw_bracket_parts(ing.raw):
        child = normalise_ingredient(part)
        row = lookup(child.name)
        if row and row["kind"] == "fruit_juice":
            out.append(part + " (inside " + ing.raw + ")")
        out.extend(nested_juice_unresolved(child))
    return out


# Item-level condition for the nut/seed rows (kind nut_seed): FAO Table 1 Group 1 covers tree and ground nuts and other oily seeds "(with no added salt or sugar)" and Group 3 covers
# "salted or sugared nuts and seeds". The condition is about the nuts themselves, so it is read from the item's OWN name and bracket ("salted almonds", "almonds (almonds, salt)"),
# never from the rest of the product (a plain "almonds" entry in a sweetened biscuit list keeps the placement). provenance_audit_1 dropped-condition finding.
_NUT_ADDED = frozenset({"salt", "salted", "sugar", "sugared", "sweetened", "candied", "caramelised", "caramelized", "honey", "glazed", "jaggery", "syrup"})


# Same item-level condition for LEGUME rows (kind legume, class-bulk-1): FAO Group 3 covers "canned or bottled vegetables or legumes (pulses) preserved in brine" (p. 7 prose;
# Table 1 continuation p. 12, Group 3 "Canned or bottled vegetables and legumes in brine") and its definition is "adding salt, oil, sugar or other group 2 ingredients to group 1 foods". Salt, sugar and brine are
# read from the item's OWN name and bracket, never from the rest of the product. Roasting and boiling are NOT part of this guard (minimal processing, separate source treatment).
_BRINE_KINDS = ("legume", "vegetable", "fruit")      # FAO Group 3: "Canned or bottled vegetables and legumes in brine" and "whole fruit preserved in syrup" / "fruit in syrup" (class-bulk-2 adds vegetable, class-bulk-3 fruit)
_LEGUME_ADDED = _NUT_ADDED | frozenset({"brine", "brined"})


def _added(ing, words) -> bool:
    # scoped-nested-3: the existing fruit name sugar-apples is not added sugar.
    # Keep two tokens so the existing negation window is not shortened.
    text = re.sub(r"\bsugar\s+(apples?)\b", r"fruit \1", ing.text.lower())
    toks = re.findall(r"[a-z]+", text)
    for i, t in enumerate(toks):
        if t in words:
            if any(x in ("no", "without", "non", "free") for x in toks[max(0, i - 2):i]) or (i + 1 < len(toks) and toks[i + 1] == "free"):
                continue                                           # "no added salt", "salt free": the condition is met, not broken
            return True
    return False


# A canned/bottled/preserved legume that does NOT say salt, sugar or brine: FAO Group 3 names such legumes only "in brine", so Group 3 is not established, and the plain-legume Group 1
# answer is not supported either. The item abstains (class-bulk-1; never an invented rule).
_LEGUME_PRESERVED = frozenset({"canned", "tinned", "bottled", "jarred", "preserved", "pickled"})


def legume_preserved_form(ing) -> bool:
    return _added(ing, _LEGUME_PRESERVED)


# Descriptor "powder" routing (class-bulk-2; owner rulings, the second one supersedes the first): descriptors.csv drops "powder"/"powdered", so "spinach powder" resolves to the plain row. A
# whole_food, legume or vegetable item carrying the word is treated as a food_powder: an "X powder" label does NOT by itself establish whole-food composition (it may be an extract, a starch,
# a colour or a carrier-containing powder), and FAO's named drying/crushing/grinding (Group 1 definition, p.6; V1 "dried" vegetables) cannot be generalised into proof that every powder is a
# whole food. So the item NEVER takes Group 1 from the powder reading alone; it takes Group 1 (sole item only) when its OWN text states whole-food composition, in exactly these two forms:
#   (1) "100%" in the item ("100% spinach powder", "spinach powder (100%)"): the label itself says nothing but the food is in it;
#   (2) "whole" ("whole spinach powder"): the whole food, not a fraction; NOT read for milk ("whole milk powder": 'whole' is the fat grade, not a composition statement).
# Every other reading abstains, alone or in a list; unrecognised co-ingredients are reported before this point and are never laundered by the abstention. A salted/brined/preserved legume or
# vegetable keeps its guard (not routed).
_POWDER_WORDS = frozenset({"powder", "powdered"})
_POWDER_ROUTED = ("whole_food", "legume", "vegetable", "fruit", "nut_seed")
# nut-guard-1 (owner decision): the canned/bottled/preserved, brine and unrecognised-bracket guards of the legume, vegetable and fruit kinds also apply to kind nut_seed. Measured before the change: almonds (brine), almonds (canned) and
# almonds (XQ9) answered Group 1. Same item-level reading (the item's own name and bracket); no new source: FAO Group 3 "using preservation methods such as canning and bottling" with added salt, oil, sugar. Inference level: class-instance of that rule.
_GUARDED_KINDS = _BRINE_KINDS + ("nut_seed",)


def powder_composition_stated(ing) -> bool:
    # A named child's percentage or 'whole' describes that child, not this food.
    # Descriptor-only claims such as (100%) still describe this powder itself.
    own_raw = _split_brackets(ing.raw)[0]
    own_toks = re.findall(r"[a-z]+", own_raw.lower())
    row = lookup(ing.name)
    claims = [own_raw]
    base = lookup(flatten(re.sub(r"\b(?:powder|powdered)\b", " ", ing.name)))
    quality_words = {"whole", "pure", "plain", "powder", "powdered", "percent", "natural", "organic", "only"}
    for part in raw_bracket_parts(ing.raw):
        toks = re.findall(r"[a-z]+", part.lower())
        if set(toks) <= quality_words:
            claims.append(part)
            continue
        # An explicit composition of the very same food is not a borrowed claim.
        child = normalise_ingredient(part)
        child_row = lookup(child.name)
        if child_row and ((base and child_row["term"] == base["term"]) or (row and child_row["term"] == row["term"])):
            child_own = _split_brackets(part)[0]
            child_toks = re.findall(r"[a-z]+", child_own.lower())
            if re.search(r"(?<![\d.])100(?:\.0+)?\s*%", child_own.lower()):
                return True
            if "whole" in child_toks and "milk" not in child_toks and child_row["term"] not in _MILK_TERMS:
                return True
    if any(re.search(r"(?<![\d.])100(?:\.0+)?\s*%", part.lower()) for part in claims):
        return True
    toks = re.findall(r"[a-z]+", " ".join(claims).lower())
    return "whole" in toks and "milk" not in own_toks and not (row and row["term"] in _MILK_TERMS)


# Powdered MILK is placed by the source BY NAME (owner post-merge refinement): FAO Table 1 Group 1 lists "frozen eggs; fresh, powdered or pasteurized milk" (p. 11), so unlike vegetable powders
# (clause names only 'dried') the composition of a milk powder IS source-established. An item whose whole text is "<optional fat-grade word> milk powder" (milk, toned milk, double toned milk,
# buffalo milk; grade words whole/skimmed/skim are fat grades, not composition statements) keeps its plain Group 1 placement. 'milk solids powder' / 'milk solids' (a solids fraction is not the
# named powdered-milk form) and any item with extra words (a bracket naming an additive, a blend) stay under the powder standard.
_MILK_POWDER_ROWS = frozenset({"milk", "toned milk", "double toned milk", "buffalo milk", "cow milk", "goat milk"})
_MILK_POWDER_WORDS = frozenset({"milk", "toned", "double", "buffalo", "cow", "goat", "whole", "skimmed", "skim", "powder", "powdered"})


def milk_powder_named(ing) -> bool:
    row = lookup(ing.name)
    toks = re.findall(r"[a-z]+", ing.text.lower())
    return bool(row) and row["term"] in _MILK_POWDER_ROWS and "powder" in toks + (["powder"] if "powdered" in toks else []) and set(toks) <= _MILK_POWDER_WORDS


# culinary-guard-1 (owner proposal; abstention only): the powder of an OIL or FAT row (a recognised culinary row whose last word is oil, fat, butter, ghee, lard, palmolein or olein, or the generic oil rows) is not read as
# the oil itself: a powder is named, its composition is not established, no group is guessed. A "100%" in the item's own name (outside any bracket) keeps the item an oil (Group 2); bracket content that is unassessed or a distinct food
# abstains first, so a 100% never overrides it.
_FAT_LAST_WORDS = frozenset({"oil", "fat", "butter", "ghee", "lard", "palmolein", "olein"})
_FAT_ROWS = frozenset({"refined oil", "edible vegetable oil", "vegetable oil"})


def is_fat_row(row) -> bool:
    return bool(row) and row["kind"] == "culinary" and (row["term"].split()[-1] in _FAT_LAST_WORDS or row["term"] in _FAT_ROWS)


def fat_powder(ing, kind: str) -> bool:
    return kind == "culinary" and is_fat_row(lookup(ing.name)) and _added(ing, _POWDER_WORDS) and not fat_powder_stated(ing)


# animal-guard-1 (owner Priority 3): rows of ANIMAL foods (a whole_food row whose source records the class-instance placement under the FAO Group 1 example below) get bounded rules. (1) DRIED, scoped: 'dried' or 'dehydrated' is
# Group 3 ONLY for a row whose source records 'DRIED-G3-SCOPE: meat' or 'DRIED-G3-SCOPE: finfish', because the FAO Group 3 example names "salted, dried, cured, or smoked meats and fish" (meats and fish, not seafood). A dried form of
# any other animal row (scope none: crab, lobster, mussel, oyster, octopus, scallop) ABSTAINS and never falls back to Group 1; see animal_dried / animal_dried_unscoped below. (2) The powder of an animal food abstains whatever else the
# item states (a 100% in the text cannot establish form or composition: powdered meat or fish is named by no source read). Every other form is untouched: ground, roasted, boiled and steamed X stay under the existing whole-food rules
# (grinding, steaming, boiling and roasting are named minimal processes WITH their no-added-substance condition, which the observed-condition guard keeps); salted, smoked, cured, canned, breaded, fried and generic cooked forms
# abstain as before; plant, dairy and fat rows are not animal rows.
_ANIMAL_MARK = "meat, poultry, fish and seafood, whole or in the form of steaks, fillets and other cuts"
_ANIMAL_DRIED = frozenset({"dried", "dehydrated"})


def is_animal_row(row) -> bool:
    return bool(row) and row["kind"] == "whole_food" and _ANIMAL_MARK in row["source"]


# The FAO Group 3 example names "meats and fish". The row records its scope: 'DRIED-G3-SCOPE: meat' (meat and poultry rows) or 'DRIED-G3-SCOPE: finfish' (a fish label); every other animal row (crab, lobster, mussel, oyster,
# octopus, scallop) carries 'DRIED-G3-SCOPE: none': the Group 1 example groups seafood with fish, but the dried example does not, so a dried form of such a row neither takes Group 3 nor falls back to Group 1: it abstains.
_DRIED_SCOPES = ("DRIED-G3-SCOPE: meat", "DRIED-G3-SCOPE: finfish")


def animal_dried(ing, kind: str) -> bool:
    row = lookup(ing.name)
    return kind == "whole_food" and is_animal_row(row) and any(m in row["source"] for m in _DRIED_SCOPES) and _added(ing, _ANIMAL_DRIED)


def animal_dried_unscoped(ing, kind: str) -> bool:
    row = lookup(ing.name)
    return kind == "whole_food" and is_animal_row(row) and not any(m in row["source"] for m in _DRIED_SCOPES) and _added(ing, _ANIMAL_DRIED)


# cheese-g3-1: a row whose source records 'CHEESE-G3' is a cheese. Brazil Dietary Guidelines Group 3 names "cheeses" and FAO Table 1 Group 3 names "simple cheeses to which salt is added". A sole, plain cheese item is Group 3;
# a cheese inside a longer list, with a bracket, or with a powder, processed, smoked, spread, sauce, flavoured or analogue word abstains (no rule or source here places those forms).
_CHEESE_MARK = "CHEESE-G3"
_CHEESE_ABSTAIN = frozenset({"powder", "powdered", "processed", "smoked", "spread", "sauce", "flavour", "flavor", "flavoured", "flavored", "analogue", "analog", "substitute", "dip", "grated", "shredded", "dried", "dehydrated", "canned", "tinned", "pickled", "breaded", "fried", "baked", "melted", "sliced", "blend"})


def is_cheese_row(row) -> bool:
    return bool(row) and row["kind"] == "whole_food" and _CHEESE_MARK in row["source"]


# cured-meat-g3-1: a row whose source records 'CURED-MEAT-G3' is a named cured pork or beef item (bacon, ham, pastrami). FAO Table 1 Group 3 prose (p.7): "some types of processed animal foods such as ham, bacon, pastrami, and smoked fish";
# identity is USDA FDC SR Legacy ('Pork, cured, bacon', 'Pork, cured, ham', 'Beef, cured, pastrami'). A sole, plain item is Group 3; any list, bracket, form word or plant/other-species word abstains.
_CURED_MARK = "CURED-MEAT-G3"
_CURED_ABSTAIN = _CHEESE_ABSTAIN | frozenset({"raw", "uncooked", "bits", "bit", "meatless", "vegan", "vegetarian", "plant", "turkey", "chicken", "beef", "pork", "style", "salad", "loaf", "sausage", "stick", "sticks", "cured", "brined", "honey", "water", "added"})


def is_cured_meat_row(row) -> bool:
    return bool(row) and row["kind"] == "whole_food" and _CURED_MARK in row["source"]


# yoghurt-g1-1: a row whose source records 'YOGHURT-G1' is plain yoghurt. FAO Table 1 Group 1 prose: "fresh or pasteurized plain yoghurt"; identity FSSAI Chapter 2.1 item 1(f)(xvii) 'yoghurt' and USDA FDC SR Legacy 'Yogurt, plain'.
# A sole, plain item is Group 1; any list, bracket, sweetened, flavoured, fruit, frozen, drinking, powder or other stated form abstains (the clause names only plain yoghurt).
_YOGHURT_MARK = "YOGHURT-G1"
_YOGHURT_ABSTAIN = _CHEESE_ABSTAIN | frozenset({"sweetened", "sugar", "sugared", "fruit", "fruity", "low", "fat", "drinking", "drink", "frozen", "probiotic", "greek", "strawberry", "mango", "vanilla", "honey", "dried", "freeze"})


def is_yoghurt_row(row) -> bool:
    return bool(row) and row["kind"] == "whole_food" and _YOGHURT_MARK in row["source"]


# smoked-fish-g3-1: a row whose source records 'SMOKED-FISH-G3' is an explicitly named smoked fish (smoked salmon, smoked haddock, kippered herring). FAO Table 1 Group 3 prose p.7: "processed animal foods such as ham, bacon,
# pastrami, and smoked fish"; identity USDA FDC SR Legacy 'Fish, X, smoked' / 'kippered'. The smoked word is part of the row name, so it is not a stated form here. A sole plain item is Group 3; a list, bracket, canned, salted,
# pâté, spread, powder, flavoured, raw or other stated form abstains.
_SMOKED_FISH_MARK = "SMOKED-FISH-G3"
_SMOKED_FISH_ABSTAIN = (_CHEESE_ABSTAIN - {"smoked"}) | frozenset({"raw", "uncooked", "salted", "brined", "pate", "mousse", "cakes", "cake", "sauce", "pie", "salad", "soup", "paste", "fillet", "fillets"})


def is_smoked_fish_row(row) -> bool:
    return bool(row) and row["kind"] == "whole_food" and _SMOKED_FISH_MARK in row["source"]


# tomato-g3-1: a row whose source records 'TOMATO-CONC-G3' is a tomato concentrate. Brazil Dietary Guidelines Group 3: "tomato extract or concentrates (with salt and/or sugar)". Group 3 ONLY when salt or sugar is stated
# (a sibling salt or sugar item, or salt/sugar in the item's own bracket) and nothing else is in the list or bracket; unstated, other additives or other foods abstain (a concentrate with no salt or sugar stated is not placed by the clause).
_TOMATO_MARK = "TOMATO-CONC-G3"
_TOMATO_OK_TERMS = frozenset({"salt", "sugar", "iodised salt"})
_TOMATO_INNER_OK = frozenset({"tomato", "tomatoes", "salt", "sugar"})


def is_tomato_conc_row(row) -> bool:
    return bool(row) and row["kind"] == "whole_food" and _TOMATO_MARK in row["source"]


def tomato_conc_verdict(ings):
    """None when no tomato concentrate row is present; otherwise (group, detail) with group 3 or None (abstain)."""
    idx = [n for n, i in enumerate(ings) if is_tomato_conc_row(lookup(i.name))]
    if not idx:
        return None
    if len(idx) != 1:
        return (None, "more than one tomato concentrate item is listed, so the combination is not established")
    t = ings[idx[0]]
    others = [i for n, i in enumerate(ings) if n != idx[0]]
    if any((lookup(o.name) or {}).get("term") not in _TOMATO_OK_TERMS or o.inner for o in others):
        return (None, "the list holds something besides the tomato concentrate and salt or sugar, so no source read here places the combination")
    parts = [p.strip().lower() for p in re.split(r"\s*(?:,|;|&|\band\b)\s*", t.inner or "") if p.strip()]
    if any(p not in _TOMATO_INNER_OK for p in parts) or _added(t, _CHEESE_ABSTAIN):
        return (None, "the concentrate's bracket or wording holds something besides tomato, salt or sugar, so no source read here places it")
    stated = bool(others) or any(p in ("salt", "sugar") for p in parts)
    if not stated:
        return (None, "salt or sugar is not stated, and the Brazil Group 3 clause covers tomato concentrates only 'with salt and/or sugar'")
    return (3, "tomato concentrate with stated salt or sugar (Brazil Dietary Guidelines Group 3: 'tomato extract or concentrates (with salt and/or sugar)')")


# canned-fish-g3-1: Brazil Dietary Guidelines Group 3 "canned sardine and tuna" and PAHO NP Model Panel A "canned sardine and tuna" name the CANNED form exactly. Rows carry 'CANNED-FISH-G3' and exist only for the canned/tinned names;
# bare tuna and sardine stay unrecognised (a bare word would be read as raw). Group 3 when the item stands alone, with only water, salt or a plain oil as siblings, and no other bracket content or form word; anything else abstains.
_CANNED_MARK = "CANNED-FISH-G3"
_CANNED_SIBLINGS = frozenset({"water", "salt", "olive oil", "sunflower oil", "vegetable oil", "soybean oil", "refined oil", "edible vegetable oil"})
_CANNED_INNER_OK = frozenset({"oil", "olive oil", "sunflower oil", "vegetable oil", "salt", "water", "brine"})
_CANNED_ABSTAIN = _CHEESE_ABSTAIN - {"canned", "tinned"}


def is_canned_fish_row(row) -> bool:
    return bool(row) and row["kind"] == "whole_food" and _CANNED_MARK in row["source"]


def canned_fish_verdict(ings):
    idx = [n for n, i in enumerate(ings) if is_canned_fish_row(lookup(i.name))]
    if not idx:
        return None
    if len(idx) != 1:
        return (None, "more than one canned fish item is listed, so the combination is not established")
    t = ings[idx[0]]
    others = [i for n, i in enumerate(ings) if n != idx[0]]
    if any((lookup(o.name) or {}).get("term") not in _CANNED_SIBLINGS or o.inner for o in others):
        return (None, "the list holds something besides the canned fish and water, salt or a plain oil, so no source read here places the combination")
    parts = [p.strip().lower() for p in re.split(r"\s*(?:,|;|&|\band\b)\s*", re.sub(r"^\s*(?:in|packed in)\s+", "", t.inner or "", flags=re.I)) if p.strip()]
    if any(p not in _CANNED_INNER_OK for p in parts) or _added(t, _CANNED_ABSTAIN):
        return (None, "the item's bracket or wording holds something besides oil, salt, water or brine, or a stated form, so no source read here places it")
    return (3, "canned fish (Brazil Dietary Guidelines Group 3 and PAHO NP Model Panel A: 'canned sardine and tuna')")


def animal_powder(ing, kind: str) -> bool:
    return kind == "whole_food" and is_animal_row(lookup(ing.name)) and _added(ing, _POWDER_WORDS)


# direct-culinary-2: scoped to the three newly source-placed culinary identities.
# Existing non-fat culinary rows and raw-food mixture policy are unchanged.
_SOURCE_PLACED_CULINARY = frozenset({"corn starch", "baking powder", "baking soda"})


def fat_bracket_residual(ing) -> list:
    """Bracket content on an OIL or FAT row that does not establish a culinary-only composition (culinary-guard-1). Supported parts: (a) a recognised culinary row (another oil, salt, sugar, a starch: group 2 items),
    (b) the source word of a recognised oil ('palm', 'coconut': palm oil and coconut oil are rows), (c) descriptor, condition, negation, connector and code words already benign for every kind. Everything else is residual:
    an unrecognised part ('XQ9', 'Gingelly Oil', 'Mineral Oil', 'Essential Oil': a suffix 'oil' or 'fat' is not an identity and no alias is assumed) and a RECOGNISED part that is not a culinary row ('Rice', 'Milk': a distinct
    food or carrier). direct-culinary-2 also applies this composition check to corn starch, baking powder and baking soda only; other non-fat culinary rows stay outside the check."""
    head = lookup(ing.name)
    if not head or not (is_fat_row(head) or head["term"] in _SOURCE_PLACED_CULINARY) or not ing.inner:
        return []
    ok_tokens = _descriptors() | _BRACKET_BENIGN | _LEGUME_ADDED | _LEGUME_PRESERVED
    out = []
    for part in re.split(r"\s*(?:,|;|&|\band\b)\s*", ing.inner):
        p = part.strip()
        toks = re.findall(r"[a-z]+", p.lower())
        if not toks:
            continue
        if is_fat_row(head) and any(is_fat_row(lookup(f"{p.lower()} {w}")) for w in ("oil", "fat")):
            continue                                  # the source word of a recognised oil ('corn' when 'corn oil' is a row), even where the bare word is also a food row
        if head["term"] == "corn starch" and p.lower() in {"corn", "maize"}:
            continue                                  # closed corn/maize starch source identity, USDA NALT29170
        row = lookup(p)
        if row:
            if row["kind"] != "culinary":
                out.append(p)
        elif not all(t in ok_tokens for t in toks):
            out.append(p)
    return out


# plain-condition culinary rows: the source names the plain food only. cocoa-powder-24 established the pattern (the pmc-reresearch-4 park
# mechanism); pool-a-24 adds the two creams, unsweetened baking chocolate (the condition word is part of its row term) and gelatin powder.
_PLAIN_CONDITION_CULINARY = frozenset({"cocoa powder", "coconut cream", "milk cream", "unsweetened baking chocolate", "gelatin powder"})


def plain_culinary_residual(ing) -> list:
    """cocoa-powder-24 / pool-a-24: item-level plain-food condition on the _PLAIN_CONDITION_CULINARY rows. PMC10127522 table footnote 5
    places these items as other processed culinary ingredients as plain foods; the row covers the plain food only. Its bracket must add
    nothing: a percentage or quantity is the item's share, and the word 'unsweetened' restates the condition. Every other bracket part
    (sugar, flavours, alkalising agents, another food) leaves the item's composition unestablished, so the item abstains rather than
    take the Group 2 placement."""
    head = lookup(ing.name)
    if not head or head["term"] not in _PLAIN_CONDITION_CULINARY or not ing.inner:
        return []
    out = []
    for part in re.split(r"\s*(?:,|;|&|\band\b)\s*", ing.inner):
        p = part.strip()
        toks = re.findall(r"[a-z]+", p.lower())
        if not toks:
            continue                                # a percentage or quantity share
        if toks == ["unsweetened"]:
            continue                                # the condition word restated
        out.append(p)
    return out


# The four nutrient labels remain outside this check: FAO Table 1 expressly
# includes Group 1 foods with vitamins/minerals added. Recognition-only grain
# forms have no equivalent placement and must not disappear inside brackets.
_NUTRIENT_LABELS = frozenset({"vitamins and minerals", "vitamins & minerals", "vitamins", "minerals"})


def nested_unplaced(ing) -> list[str]:
    out = []
    for part in re.split(r"\s*(?:,|;|&|\band\b)\s*", ing.inner or ""):
        row = lookup(part.strip())
        if row and row["kind"] == "unplaced" and row["term"] not in _NUTRIENT_LABELS:
            out.append(f"{part.strip()} (inside {ing.raw})")
    return list(dict.fromkeys(out))


def fat_powder_stated(ing) -> bool:
    """A '100%' that sits in the item's own name, outside any bracket; a '100%' inside a bracket belongs to the bracket content and does not describe the oil."""
    return bool(re.search(r"(?<![\d.])100(?:\.0+)?\s*%", re.sub(r"[(\[{][^)\]}]*[)\]}]", "", ing.raw.lower())))


def powder_routed(ing, kind: str) -> bool:
    if kind not in _POWDER_ROUTED:
        return False
    # A named child such as Milk Powder is not a powder form of its parent.
    powder_named = _added(Ingredient(ing.raw, ing.name, ""), _POWDER_WORDS)
    for part in re.split(r"\s*(?:,|;|&|\band\b)\s*", ing.inner or ""):
        toks = re.findall(r"[a-z]+", part)
        if not lookup(part.strip()) and toks and all(t in _descriptors() | _BRACKET_BENIGN for t in toks):
            powder_named = powder_named or _added(Ingredient(part, part, ""), _POWDER_WORDS)
    if not powder_named:
        return False
    if kind == "whole_food" and milk_powder_named(ing):
        return False
    if kind in _GUARDED_KINDS and (legume_added_salt_sugar_or_brine(ing) or legume_preserved_form(ing)):
        return False
    return True


def raw_bracket_parts(raw: str) -> list[str]:
    """Immediate children, retaining each child's own nested brackets."""
    groups, depth, start = [], 0, 0
    for n, ch in enumerate(raw):
        if ch in "([{":
            if depth == 0:
                start = n + 1
            depth += 1
        elif ch in ")]}":
            if depth == 1:
                groups.append(raw[start:n])
            depth = max(depth - 1, 0)
    if depth:
        groups.append(raw[start:])
    parts = []
    for group in groups:
        depth, start = 0, 0
        for m in re.finditer(r"[()\[\]{},;&]|\band\b", group, re.I):
            token = m.group()
            if token in "([{":
                depth += 1
            elif token in ")]}":
                depth = max(depth - 1, 0)
            elif depth == 0:
                parts.append(group[start:m.start()].strip())
                start = m.end()
        parts.append(group[start:].strip())
    return [p for p in parts if p]


def nested_powder_unresolved(ing) -> list[str]:
    """A child's own composition must be established at every bracket depth."""
    if not ing.inner:
        return []
    out = []
    for part in raw_bracket_parts(ing.raw):
        child = normalise_ingredient(part)
        row = lookup(child.name)
        unresolved = bool(nested_powder_unresolved(child))
        if row:
            kind = row["kind"]
            unresolved = unresolved or animal_powder(child, kind) or fat_powder(child, kind)
            if kind == "food_powder" or powder_routed(child, kind):
                unresolved = unresolved or not powder_composition_stated(child)
        if unresolved:
            out.append(f"{part} (inside {ing.raw})")
    return list(dict.fromkeys(out))


# Unknown additions on the same item are never laundered (class-bulk-3, owner requirement): the guard reads the item's own bracket for salt/sugar/brine, but a bracket on a legume, vegetable or fruit
# item that names content the vocabulary does not recognise ("Dried Mango (XQ9)", "Dried Blueberries (Sunflower Oil)") used to be ignored and the item answered Group 1. Such an item now ABSTAINS: neither
# Group 1 nor Group 3 is established while part of the item is unassessed. Benign bracket parts: recognised foods, descriptors, condition words handled by the guard, negation/connector words, digits/codes.
_RESIDUAL_EXTRA_KINDS = ("flour", "whole_food")       # class-bulk-4 added flour (a flour row must not launder 'Oat Flour (XQ9)'); per-form-1 adds whole_food (owner ruling: 'Rice (XQ9)' Group 1 -> abstain)
_BRACKET_BENIGN = frozenset({"with", "without", "skin", "peel", "added", "no", "non", "free", "of", "in", "from", "as", "the", "a", "an", "natural", "cooked", "organic", "whole", "percent", "less", "than", "only", "pure", "plain", "ins", "e"})


# Species-of-origin provenance (per-form-1, owner decision): a species word from the CLOSED set {cow, buffalo, goat} is benign ONLY inside a bracket that also holds the word 'milk', and ONLY when the head item
# is itself a plain milk item (head row kind whole_food and head term in milk, toned milk, double toned milk, buffalo milk; NOT 'milk solids': owner amendment, a solids fraction is not established as
# identical to milk, so 'Milk solids (... cow milk)' stays abstained). It is resolved here, in the bracket check: no lexicon row, no
# synonym, no globally recognised word ('cow milk' as an ingredient name stays unrecognised). 'Rice (Cow Milk)', 'Milk (Cow)' (no milk word in the bracket) and any other head keep the abstention.
_SPECIES_WORDS = frozenset({"cow", "buffalo", "goat"})
_MILK_PROVENANCE_WORDS = frozenset({"milk", "toned", "double", "solids"})


def bracket_residual(ing) -> list:
    if not ing.inner:
        return []
    ok_tokens = _descriptors() | _BRACKET_BENIGN | _LEGUME_ADDED | _LEGUME_PRESERVED
    head = lookup(ing.name)
    head_is_milk = bool(head) and head["kind"] == "whole_food" and head["term"] in (_MILK_TERMS - {"milk solids"})
    residual = []
    for part in re.split(r"\s*(?:,|;|&|\band\b)\s*", ing.inner):
        toks = re.findall(r"[a-z]+", part)
        if set(toks) & _SPECIES_WORDS and not head_is_milk:         # per-form-2b: 'cow milk'/'goat milk'/'buffalo milk' are recognised names now, but a species-milk part is benign ONLY on a plain milk head item
            residual.append(part.strip())
            continue
        if not toks or is_recognised(part.strip()) or all(t in ok_tokens for t in toks):
            continue
        if head_is_milk and "milk" in toks and set(toks) & _SPECIES_WORDS and all(t in ok_tokens or t in _SPECIES_WORDS or t in _MILK_PROVENANCE_WORDS for t in toks):
            continue
        residual.append(part.strip())
    return residual


# whole-food-guard-1 (owner proposal; abstention only, no new group): a recognised whole_food item is no longer answered Group 1 when (a) its OWN name or bracket names an added or preserving condition (salt, sugar, honey,
# syrup, brine, a recognised culinary substance such as an oil, or a canned/bottled/preserved form), or (b) its own bracket names a different food that is not explicitly known to be the same food. The one exemption inside (a) is the
# positively supported case: for the 23 grain/flour terms of the per-form-2a guard, SALT alone keeps its Group 3 answer; any other observed condition on such an item still abstains. No source read or rule states the final group
# for salted or sugared milk or eggs (an open owner decision), so none is asserted. The general Group 3 definition ("adding salt, oil, sugar or other group 2 ingredients to group 1 foods") is not denied: what is not established is
# this item's form and composition from the label evidence.
# Same-food equivalences (explicit, not a taxonomy): the identical row; egg and eggs; a plain milk row with milk, cow milk, buffalo milk or goat milk (the species-milk brackets of per-form-1 and per-form-2b); and the class-phrase row
# 'dehydrated vegetable' with a vegetable row (its source names dried vegetables as a class). Everything else, including two different plants, a milk fraction IN milk, or a species milk not listed, stays distinct.
_SAME_MILK_PARTS = frozenset({"milk", "cow milk", "buffalo milk", "goat milk"})



def whole_food_observed(ing, kind: str) -> list:
    # scoped-flour-4: an added/preserving condition cannot borrow plain-flour
    # Group 1. Keep the existing salt-only placement for its bounded grain set.
    if kind not in ("whole_food", "flour"):
        return []
    if kind == "flour" and grain_added_salt(ing, kind):
        # Preserve existing positive salted-grain routes, including another
        # Group 2 ingredient. This patch removes unsupported plain Group 1;
        # it does not expand or remove an established Group 3 route.
        return [p.strip().lower() for p in re.split(r"\s*(?:,|;|&|\band\b)\s*", ing.inner or "")
                if lookup(p.strip()) and lookup(p.strip())["term"] in _SOURCE_PLACED_CULINARY]
    obs = nut_added_observed(ing) + [w for w in sorted(_LEGUME_PRESERVED) if _added(ing, {w})]
    obs = list(dict.fromkeys(obs))
    if grain_added_salt(ing, kind):                                  # per-form-2a: salt on these 23 terms is a supported Group 3; only salt itself (the words 'salt'/'salted' or a lexicon salt row) is exempt
        salt_rows = {r["term"] for r in load_table("lexicon.csv") if r["kind"] == "culinary" and (r["term"] == "salt" or r["term"].endswith(" salt"))}
        obs = [o for o in obs if o not in ("salt", "salted") and not ((lookup(o) or {}).get("term") in salt_rows)]
    return obs


def whole_food_nested(ing, kind: str) -> list:
    head = lookup(ing.name)
    if kind != "whole_food" or not head or not ing.inner:
        return []
    out = []
    for part in re.split(r"\s*(?:,|;|&|\band\b)\s*", ing.inner):
        row = lookup(part.strip()) if part.strip() else None
        if not row or row["kind"] in ("neutral", "culture", "culinary"):
            continue
        ht, pt = head["term"], row["term"]
        if pt == ht or {ht, pt} <= {"egg", "eggs"} or (ht in (_MILK_TERMS - {"milk solids"}) and pt in _SAME_MILK_PARTS) or (ht == "dehydrated vegetable" and row["kind"] == "vegetable"):
            continue
        out.append(part.strip())
    return out


# Salted grain guard (per-form-2a): the 23 Batch-4 grain/flour terms (the _SCOPED_TERMS set) with salt added in the item's OWN name or bracket take Group 3, never Group 1 through the global 'salted' descriptor.
# Source (FAO 2019 ca5644en, quoted in evaluation/per_form_2a/README.md): "They are made by adding salt, oil, sugar or other substances from group 2 to group 1 foods." (p.7 prose); "Some of what are now
# ultra-processed foods were originally manufactured only with group 1 foods and salt or sugar or other substances from group 2, and thus would be classed in NOVA group 3 as processed foods." (p.9). INFERENCE
# LEVEL: class-instance of that stated rule; no clause names a salted grain (the named analogues are salted nuts and seeds, and bread of wheat flour, water, salt and yeast). Salt only (not sugar, oil): the
# batch scope. Negated forms ("unsalted", "no added salt", "salt free") are not matched.
_GRAIN_SALT_WORDS = frozenset({"salt", "salted"})


def grain_added_salt(ing, kind: str) -> bool:
    if kind not in ("whole_food", "flour") or not _added(ing, _GRAIN_SALT_WORDS):
        return False
    row = lookup(ing.name)
    return bool(row) and row["term"] in _SCOPED_TERMS["toasted"]


def nut_added_salt_or_sugar(ing) -> bool:
    return _added(ing, _NUT_ADDED)


# nut-guard-1 (owner review): the Group 3 driver for a nut or seed names the OBSERVED added substance. Salt or sugar only: the example "salted or sugared nuts and seeds" fits and is quoted. Brine, honey, syrup or a recognised
# culinary substance such as an oil in the item's own bracket: the general Group 3 definition is quoted (class-instance; no FAO example names that form).
_NUT_OBSERVED_ORDER = ("salt", "salted", "sugar", "sugared", "sweetened", "candied", "caramelised", "caramelized", "honey", "glazed", "jaggery", "syrup", "brine", "brined")


def nut_added_observed(ing) -> list:
    seen = [w for w in _NUT_OBSERVED_ORDER if _added(ing, {w})]
    seen += [p.strip().lower() for p in re.split(r"\s*(?:,|;|&|\band\b)\s*", ing.inner or "") if p.strip() and is_recognised(p.strip()) and lookup(p.strip())["kind"] == "culinary"]
    return list(dict.fromkeys(seen))


def nut_group3_driver(ing) -> str:
    obs = nut_added_observed(ing)
    if not obs or set(obs) <= {"salt", "salted", "sugar", "sugared"}:
        return "nut or seed with added salt or sugar (FAO Table 1 Group 3: 'salted or sugared nuts and seeds')"
    return ("nut or seed with added " + ", ".join(obs) + " (FAO Table 1 Group 3 definition: 'Products made by adding salt, oil, sugar or other group 2 ingredients to group 1 foods'; "
            "class-instance of that rule, no FAO example names this form)")


def legume_added_salt_sugar_or_brine(ing) -> bool:
    if _added(ing, _LEGUME_ADDED):
        return True
    # a recognised culinary (Group 2) substance named in the item's own bracket ("Dried Blueberries (Sunflower Oil)") is an addition of a group 2 ingredient: the Group 3 definition
    return any(is_recognised(p.strip()) and lookup(p.strip())["kind"] == "culinary" for p in re.split(r"\s*(?:,|;|&|\band\b)\s*", ing.inner or "") if p.strip())


def is_recognised(name: str) -> bool:
    return lookup(name) is not None


@dataclass
class _Hit:
    strength: str
    marker_class: str
    detail: str
    source: str


# A colour word that is only a bracketed function note on a named ingredient ("Turmeric (Colouring & Spices)",
# "Beetroot powder (for natural colour)") says what the food is used for. It is not a declared ADDED colour, so it
# is not a marker (research/04). An added colour is declared as the ingredient itself: "Colour (INS 150d)",
# "Natural colour (annatto)", "Food colour - E122", or a "Contains ... colour" line.
_MILK_TERMS = frozenset({"milk", "toned milk", "double toned milk", "buffalo milk", "milk solids", "cow milk", "goat milk"})      # lexicon terms that count as the milk of the milk-plus-culture rule
_NOTE_PREFIX = r"(?:(?:for|as|used|a|an|the|to|give|added|natural|permitted|food|synthetic|artificial) )*"
_NOTE_COLOUR = r"colou?r(?:ant)?(?: agent)?"
_NOTE_OTHER = r"(?:spices?|seasoning|flavou?rs?)"
_COLOUR_NOTE = re.compile(rf"^{_NOTE_PREFIX}(?:{_NOTE_COLOUR}(?: (?:and|&) {_NOTE_OTHER})?|{_NOTE_OTHER} (?:and|&) {_NOTE_COLOUR})$")


def is_colour_note(inner: str) -> bool:
    return bool(_COLOUR_NOTE.match(inner.strip()))


def colour_note_only(ing: Ingredient) -> bool:
    """The only colour wording on this ingredient is a short bracketed note, and its own name is no additive class."""
    if not ing.name or not is_colour_note(ing.inner):
        return False
    return not any(pat.search(ing.name) for pat, _ in _markers())


def sweetener_foods_only(ing: Ingredient) -> bool:
    """The entry's own name is only the class word "sweetener" and its bracket names only recognised foods, no INS code ("Sweeteners (Jaggery
    Powder, Dates Powder)"). The NOVA source lists ARTIFICIAL sweeteners as a Group 4 class (FAO 2019 pp. 9-10); named sugars are foods, so the word
    alone is not read as an added sweetener class. Any name or code that is not a recognised food keeps the marker (aspartame, "stevia", INS 950)."""
    if ing.ins or not ing.inner or ing.name not in ("sweetener", "natural sweetener"):
        return False
    parts = [p.strip() for p in re.split(r"\s*(?:,|;|&|\band\b)\s*", ing.inner) if p.strip()]
    return bool(parts) and all(is_recognised(p) and lookup(p)["kind"] in ("whole_food", "legume", "vegetable", "fruit", "culinary") for p in parts)


def ingredient_marker_terms(ing: Ingredient) -> set[str]:
    """marker_terms for an ingredient in the list. When its bracket is only a function note, nothing in it is a marker."""
    if colour_note_only(ing):
        return set()
    terms = marker_terms(ing.text)
    return terms - {"sweetener"} if sweetener_foods_only(ing) else terms


def marker_terms(text: str) -> set[str]:
    """The marker terms (markers.csv) found in a normalised text."""
    return {row["term"] for pat, row in _markers() if pat.search(text)}


# The plain starch rows (starch, tapioca starch) cover ONLY plain/unmodified starch (owner decision 2026-11-21). An entry whose bracket says the starch is modified
# ("Starch (Modified)", "Starch (Acid Treated)") is the FAO marker 'modified starches', not plain starch: it is read as the strong 'modified starch' marker so the plain row can never capture it.
_PLAIN_STARCH_ROWS = frozenset({"starch", "tapioca starch"})
_STARCH_MODIFIED = re.compile(r"modif|pregelatini[sz]ed|acid[- ]?treated|oxidi[sz]ed|cross[- ]?linked|bleached|hydroxypropyl|acetylated|phosphated|thermally|enzymatically")


def _hits_for(ing: Ingredient) -> list[_Hit]:
    if is_additive_absence_claim(ing.raw):
        return []
    if any(u.class_conflict for u in ing.ins):
        return [_Hit("unlisted", "unlisted_additive", "declared class and local code mapping differ; entry unresolved", "label wording versus existing project mapping; no source resolves this mismatch")]
    hits: list[_Hit] = []
    note_only = colour_note_only(ing)
    sweet_foods = sweetener_foods_only(ing)
    for pat, row in _markers():
        if note_only:
            break          # the name has no marker and the bracket is only a function note: its words ("colour & flavour") decide nothing
        if sweet_foods and row["term"] == "sweetener":
            continue       # "Sweeteners (Jaggery Powder, Dates Powder)": the bracket names foods, so the class word is not counted
        if pat.search(ing.text):
            hits.append(_Hit(row["strength"], row["marker_class"], f'"{row["term"]}" ({row["marker_class"]})', row["source"]))
    if not note_only:
        for pat, row in _claim_markers():
            if pat.search(ing.text) and not any(h.detail == f'"{row["term"]}" ({row["marker_class"]})' for h in hits):
                hits.append(_Hit("weak", "claim_wording", f'"{row["term"]}" named only in claim wording ("source of" / "rich in" / "high in")', "claim wording alone neither shows an added isolated ingredient nor shows it absent; abstains"))
    if ing.name in _PLAIN_STARCH_ROWS and ing.inner and _STARCH_MODIFIED.search(ing.inner.lower()) and not any(h.detail == '"modified starch" (derived_substance)' for h in hits):
        mrow = next((row for _, row in _markers() if row["term"] == "modified starch"), None)
        if mrow is not None:
            hits.append(_Hit(mrow["strength"], mrow["marker_class"], f'"modified starch" ({mrow["marker_class"]})', mrow["source"]))
    ins_table = {r["ins"].lower(): r for r in load_table("ins_map.csv")}
    for use in ing.ins:
        row = ins_table.get(use.code)
        if row is None:
            hits.append(_Hit("unlisted", "unlisted_additive", f"INS {use.code} (not in local mapping)", "no source: code absent from ins_map.csv"))
        else:
            hits.append(_Hit(row["strength"], "ins", f"INS {use.code} ({row['name']})", row["source"]))
    # research/02: pectin (INS 440) is consistent with group 3 even though it can be
    # declared as a "gelling agent": a weak_specific hit cancels cosmetic class-word hits
    # in the same ingredient. Derived-substance hits are never cancelled.
    if any(h.strength == "weak_specific" for h in hits):
        hits = [h for h in hits if not (h.strength == "strong" and h.marker_class == "cosmetic_additive")]
    return hits


def other_open_items(ings, skip=()) -> str:
    """Headline aggregation (owner Priority 2): when an abstention is headed by weak or unlisted markers, a colour note or a sweetener-foods entry, the other ACTIVE blockers are named as well, so the headline does not look like the
    only open point: items not in the vocabulary, recognised-by-name-only items that no source places, and the powder of a food or of an oil or fat whose composition is not stated. Group names set aside as metadata are not
    ingredients here. Returns '' when there is nothing else; it never changes a group and is only appended to an abstention that already exists."""
    parts = []
    ings0 = ings
    ings = [i for i in ings if i.raw not in skip]                 # an item already named by the headline (the weak marker, the colour note, the sweetener entry) is not repeated
    unrec = [i.raw for i in ings if not is_recognised(i.name)]
    if unrec:
        parts.append("not in the local vocabulary: " + ", ".join(unrec))
    rec = [(i, lookup(i.name)["kind"]) for i in ings if is_recognised(i.name)]
    unpl = [i.raw for i, k in rec if k == "unplaced"]
    if unpl:
        parts.append("recognised by name only, no source read places " + ", ".join(unpl))
    juices = [i.raw for i, k in rec if k == "fruit_juice" and not (len(ings0) == 1 and plain_juice_stated(i))]
    juices += [name for i in ings for name in nested_juice_unresolved(i)]
    if juices:
        parts.append("a named juice's processing and composition are not established: " + ", ".join(juices))
    waters = [p for i in ings for p in named_water_unresolved(i, len(ings0) == 1)]
    if waters:
        parts.append("a named water's plain form or standalone scope is not established: " + ", ".join(waters))
    # the powder condition is the classifier's own: an item whose FINAL kind is food_powder (routed by the word 'powder' or an explicit food_powder row such as banana, strawberry or beetroot powder) is uncertain unless it is the
    # sole item and states its composition; the powder of an oil or fat is uncertain unless its own name states 100%. A 100% inside a multi-item list does not resolve it.
    pw = [i.raw for i, k in rec if fat_powder(i, k) or ((k == "food_powder" or powder_routed(i, k)) and not (len(ings0) == 1 and powder_composition_stated(i)))]
    if pw:
        parts.append("a powder is named and its composition is not established: " + ", ".join(pw))
    return ("; other open items: " + "; ".join(parts)) if parts else ""


def classify_ingredients(ings: list[Ingredient], declarations: list[str] | None = None) -> Classification:
    strong: list[Driver] = []
    weak: list[Driver] = []
    for ing in ings:
        for h in _hits_for(ing):
            d = Driver(ing.raw, h.detail, h.source, ing.section)
            (strong if h.strength == "strong" else weak).append(d)
    from .parser import split_items
    for decl in declarations or []:
        for clause in split_items(re.sub(r"^contains?\s*:?[ ]*", "", decl, flags=re.IGNORECASE)):
            ing = normalise_ingredient(clause)
            if any(u.class_conflict for u in ing.ins):
                weak.append(Driver(clause, "declared class and local code mapping differ; entry unresolved", "label wording versus existing project mapping; no source resolves this mismatch"))
                continue
            # Keep existing positive cosmetic declarations. Other additive/code
            # evidence blocks an unsupported lower-group answer, not a new Group 4 route.
            for h in _hits_for(ing):
                if h.strength != "strong":
                    weak.append(Driver(clause, h.detail, h.source))
                elif h.marker_class == "ins":
                    weak.append(Driver(clause, "code stated outside ingredient list; verify declaration before using its mapped marker", h.source))
            for pat, row in _markers():
                if row["strength"] == "strong" and row["marker_class"] == "cosmetic_additive" and pat.search(ing.text):
                    strong.append(Driver(decl, f'declared in "Contains" statement: "{row["term"]}"', row["source"]))

    if strong:
        return Classification(4, drivers=strong)

    # A colour note on a named food ("Turmeric (as colourant)") leaves open whether a colour is added. Without an independent
    # marker (checked above) the result stays uncertain; it is never read as a confident group from the foods alone.
    notes = [i.raw for i in ings if colour_note_only(i)]
    if notes:
        return Classification(None, drivers=weak, reason="a colour note on a named ingredient (" + "; ".join(notes) + ") leaves open whether a colour is added, and no other marker decides the group" + other_open_items(ings, set(notes) | {d.ingredient for d in weak}))

    sweet = [i.raw for i in ings if sweetener_foods_only(i)]
    if sweet:
        return Classification(None, drivers=weak, reason="a sweetener entry whose bracket names only foods (" + "; ".join(sweet) + ") leaves open whether a sweetener additive is added, and no other marker decides the group" + other_open_items(ings, set(sweet) | {d.ingredient for d in weak}))

    if weak:
        names = "; ".join(sorted({f"{d.ingredient} -> {d.detail}" for d in weak}))
        return Classification(None, drivers=weak, reason=f"only weak or unlisted markers present ({names}); not enough to call a group" + other_open_items(ings, {d.ingredient for d in weak}))

    unrecognised = [i.raw for i in ings if not is_recognised(i.name)]
    if unrecognised:
        return Classification(None, reason="ingredients not in the local vocabulary, so processing level cannot be judged: " + ", ".join(unrecognised) + other_open_items(ings, set(unrecognised)))

    kinds = [lookup(i.name)["kind"] for i in ings]
    cv = canned_fish_verdict(ings)
    if cv is not None:
        if cv[0] == 3:
            c0 = next(i for i in ings if is_canned_fish_row(lookup(i.name)))
            return Classification(3, drivers=[Driver(c0.raw, cv[1], lookup(c0.name)["source"], c0.section)])
        return Classification(None, reason="a canned fish is named: " + cv[1] + ", so no group is asserted")
    tv = tomato_conc_verdict(ings)
    if tv is not None:
        if tv[0] == 3:
            t0 = next(i for i in ings if is_tomato_conc_row(lookup(i.name)))
            return Classification(3, drivers=[Driver(t0.raw, tv[1], lookup(t0.name)["source"], t0.section)])
        return Classification(None, reason="a tomato concentrate is named: " + tv[1] + ", so no group is asserted")
    bracket_unknown = [(i.raw, fat_bracket_residual(i) or plain_culinary_residual(i) if k == "culinary" else bracket_residual(i), k) for i, k in zip(ings, kinds) if (k in _GUARDED_KINDS + _RESIDUAL_EXTRA_KINDS and bracket_residual(i)) or (k == "culinary" and (fat_bracket_residual(i) or plain_culinary_residual(i)))]
    fat_powders = [i.raw for i, k in zip(ings, kinds) if fat_powder(i, k)]
    animal_powders = [i.raw for i, k in zip(ings, kinds) if animal_powder(i, k)]
    animal_dry = [i.raw for i, k in zip(ings, kinds) if animal_dried(i, k)]
    animal_dry_unscoped = [i.raw for i, k in zip(ings, kinds) if animal_dried_unscoped(i, k)]
    wf_condition = [(i.raw, whole_food_observed(i, k)) for i, k in zip(ings, kinds) if whole_food_observed(i, k)]
    wf_nested = [(i.raw, whole_food_nested(i, k)) for i, k in zip(ings, kinds) if whole_food_nested(i, k)]
    kinds = ["food_powder" if powder_routed(i, k) else k for i, k in zip(ings, kinds)]
    unplaced = [i.raw for i, k in zip(ings, kinds) if k == "unplaced"]
    unplaced += [name for i in ings for name in nested_unplaced(i)]
    if unplaced:
        # Recognised by NAME only: no source places these items, so the list can never be answered from the rest of it. This only ever ADDS an abstention (a strong
        # marker returned above); it is vocabulary, not classification, and these items are never counted as classified.
        return Classification(None, reason="recognised by name only, and no source read places " + "; ".join(unplaced) + ", so the processing level cannot be judged (recognition is vocabulary, not classification)" + other_open_items(ings, set(unplaced)))
    juices = [i.raw for i, k in zip(ings, kinds) if k == "fruit_juice"]
    nested_juices = [p for i in ings for p in nested_juice_unresolved(i)]
    if juices or nested_juices:
        if len(ings) == 1 and not nested_juices and plain_juice_stated(ings[0]):
            return Classification(1, drivers=[Driver(ings[0].raw, "single explicitly 100% fresh or pasteurized fruit juice; FAO Table 1 Group 1 conditioned juice example", lookup(ings[0].name)["source"], ings[0].section)])
        return Classification(None, reason="a named fruit juice (" + "; ".join(juices + nested_juices) + "): FAO Group 1 covers fresh or pasteurized juice with no added sugar, sweeteners or flavours; the item's processing and composition are not established by this list, so no group is asserted")
    waters = [p for i in ings for p in named_water_unresolved(i, len(ings) == 1)]
    if waters:
        return Classification(None, reason="a named water's plain form or standalone scope is not established: " + "; ".join(waters) + "; the source names plain or carbonated water as a dietary item, not treated forms or mixtures, so no group is asserted")
    if len(ings) == 1 and kinds[0] == "named_water":
        return Classification(1, drivers=[Driver(ings[0].raw, "single plain carbonated water; exact-named Group 1 dietary-water example (Khandpur et al. 2021 Table 3)", lookup(ings[0].name)["source"], ings[0].section)])
    substantive = [(i, k) for i, k in zip(ings, kinds) if k not in ("neutral", "culture")]
    if bracket_unknown:
        # nut-guard-1: the item kind is named accurately. Only non-nut items: the original text, unchanged. Only nut/seed items: a nut-specific text. A mix: kind-neutral text.
        nut_flags = [k == "nut_seed" for _, _, k in bracket_unknown]
        cul_flags = [k == "culinary" for _, _, k in bracket_unknown]
        what = "a bracket on a legume, vegetable, fruit or flour item" if not any(nut_flags) else ("a bracket on a nut or seed item" if all(nut_flags) else "a bracket on a food item")
        tail = "), so neither Group 1 nor Group 3 is established while part of the item is unassessed"
        names = " names content the vocabulary does not recognise ("
        plain_cul = {i.raw: lookup(i.name)["term"] for i in ings if plain_culinary_residual(i)}
        if any(raw in plain_cul for raw, _, _ in bracket_unknown):   # cocoa-powder-24 / pool-a-24: the plain-food condition, not a culinary-composition check
            terms = {plain_cul[raw] for raw, _, _ in bracket_unknown if raw in plain_cul}
            what = f"a bracket on {sorted(terms)[0]}" if len(terms) == 1 and all(raw in plain_cul for raw, _, _ in bracket_unknown) else "a bracket on a food item"
            names = " adds content beyond the plain food the source names ("
            tail = f"), so the item is not established as plain {sorted(terms)[0]} and no group is asserted" if len(terms) == 1 else "), so the items are not established as the plain foods the sources name and no group is asserted"
        elif any(cul_flags):      # culinary-guard-1: an oil or fat item (Group 2 at stake); its bracket part may be unrecognised OR a recognised food that is not a culinary ingredient
            what = "a bracket on a processed culinary ingredient" if all(cul_flags) else "a bracket on a food item"
            names = " names content that is unrecognised or is a different food, not a culinary ingredient ("
            tail = "), so what the item contains is not established and no group is asserted while part of the item is unassessed"
        return Classification(None, reason=what + names + "; ".join(f"{raw}: {', '.join(r)}" for raw, r, _ in bracket_unknown) + tail)
    if animal_powders:
        return Classification(None, reason="a powder of an animal food is named (" + "; ".join(animal_powders) + "): no source read names powdered meat, poultry, fish or seafood, so its form and composition are not established and no group is asserted, whatever percentage the item states")
    if animal_dry_unscoped:
        return Classification(None, reason="a dried form of an animal food is named (" + "; ".join(animal_dry_unscoped) + "): the FAO Group 3 example names dried meats and fish only, so whether a dried form of this food is processed that way is not established, and drying alone does not make it Group 1")
    if fat_powders:
        return Classification(None, reason="a powder of an oil or fat is named (" + "; ".join(fat_powders) + "): a powder is named but its composition is not established, so no group is asserted unless the item's own name states 100%")
    if wf_nested:
        return Classification(None, reason="a bracket names a different food inside the item (" + "; ".join(f"{raw}: {', '.join(r)}" for raw, r in wf_nested)
                              + "): no rule or source available here establishes that it is the same food or how the two combine, so what the item is made of is not established and neither Group 1 nor Group 3 is asserted")
    if wf_condition:
        return Classification(None, reason="an item whose own text names an added or preserving condition (" + "; ".join(f"{raw}: {', '.join(o)}" for raw, o in wf_condition)
                              + "): the general Group 3 definition covers group 1 foods with salt, oil, sugar or other group 2 ingredients added, but this food's form and composition are not established by the label evidence and the rules available, so neither Group 1 nor Group 3 is asserted")
    nested_powders = [p for i in ings for p in nested_powder_unresolved(i)]
    if nested_powders:
        return Classification(None, reason="a nested powder's form or composition is not established (" + "; ".join(nested_powders) + "), so it cannot inherit the outer food's plain placement and no group is asserted")
    cheese_names = [i.raw for i, k in zip(ings, kinds) if k == "whole_food" and is_cheese_row(lookup(i.name))]
    if cheese_names:
        if len(ings) == 1 and not ings[0].inner and not _added(ings[0], _CHEESE_ABSTAIN):
            return Classification(3, drivers=[Driver(ings[0].raw, "cheese (Brazil Dietary Guidelines Group 3: 'cheeses'; FAO Table 1 Group 3: 'simple cheeses to which salt is added'); a sole plain cheese item", lookup(ings[0].name)["source"], ings[0].section)])
        return Classification(None, reason="a cheese is named (" + "; ".join(cheese_names) + ") inside a longer list, with a bracket, or with a stated form (powder, processed, smoked, spread, sauce, flavoured, grated, sliced): no source read here places that form or combination, so no group is asserted")
    yoghurt_names = [i.raw for i, k in zip(ings, kinds) if k == "whole_food" and is_yoghurt_row(lookup(i.name))]
    if yoghurt_names:
        if len(ings) == 1 and not ings[0].inner and not _added(ings[0], _YOGHURT_ABSTAIN):
            return Classification(1, drivers=[Driver(ings[0].raw, "plain yoghurt (FAO Table 1 Group 1: 'fresh or pasteurized plain yoghurt'); a sole plain item, identity FSSAI Chapter 2.1 and USDA FDC SR Legacy", lookup(ings[0].name)["source"], ings[0].section)])
        return Classification(None, reason="yoghurt is named (" + "; ".join(yoghurt_names) + ") inside a longer list, with a bracket, or with a stated form (sweetened, flavoured, fruit, frozen, drinking, powder): the FAO clause names only plain yoghurt, so no group is asserted")
    smoked_fish_names = [i.raw for i, k in zip(ings, kinds) if k == "whole_food" and is_smoked_fish_row(lookup(i.name))]
    if smoked_fish_names:
        if len(ings) == 1 and not ings[0].inner and not _added(ings[0], _SMOKED_FISH_ABSTAIN - {"kippered"}):
            return Classification(3, drivers=[Driver(ings[0].raw, "smoked fish (FAO Table 1 Group 3 prose: 'processed animal foods such as ham, bacon, pastrami, and smoked fish'); a sole plain item, identity USDA FDC SR Legacy", lookup(ings[0].name)["source"], ings[0].section)])
        return Classification(None, reason="a smoked fish is named (" + "; ".join(smoked_fish_names) + ") inside a longer list, with a bracket, or with a stated form (canned, salted, pate, spread, powder, flavoured): no source read here places that form or combination, so no group is asserted")
    cured_names = [i.raw for i, k in zip(ings, kinds) if k == "whole_food" and is_cured_meat_row(lookup(i.name))]
    if cured_names:
        if len(ings) == 1 and not ings[0].inner and not _added(ings[0], _CURED_ABSTAIN):
            return Classification(3, drivers=[Driver(ings[0].raw, "cured meat (FAO Table 1 Group 3 prose: 'processed animal foods such as ham, bacon, pastrami'); a sole plain item, identity USDA FDC SR Legacy", lookup(ings[0].name)["source"], ings[0].section)])
        return Classification(None, reason="a cured meat is named (" + "; ".join(cured_names) + ") inside a longer list, with a bracket, or with a stated form or other-species word: no source read here places that form or combination, so no group is asserted")
    nut_salted = animal_dry + [i.raw for i, k in zip(ings, kinds) if (k == "nut_seed" and nut_added_salt_or_sugar(i)) or (k in _GUARDED_KINDS and legume_added_salt_sugar_or_brine(i)) or grain_added_salt(i, k)]
    legume_preserved = [i.raw for i, k in zip(ings, kinds) if k in _GUARDED_KINDS and legume_preserved_form(i) and not legume_added_salt_sugar_or_brine(i)]
    if legume_preserved:
        preserved_nut = [k == "nut_seed" for i, k in zip(ings, kinds) if k in _GUARDED_KINDS and legume_preserved_form(i) and not legume_added_salt_sugar_or_brine(i)]
        if not any(preserved_nut):
            return Classification(None, reason="a canned, bottled or preserved legume, vegetable or fruit (" + "; ".join(legume_preserved) + "): FAO Group 3 names vegetables and legumes preserved in brine and fruit in syrup, but the item does not say that salt, sugar, syrup or brine is added, so neither Group 1 nor Group 3 is established")
        # nut-guard-1: no FAO example names a canned nut, so the general Group 3 definition is cited, not an example
        return Classification(None, reason="a canned, bottled or preserved " + ("nut or seed" if all(preserved_nut) else "food") + " (" + "; ".join(legume_preserved) + "): the FAO Group 3 definition covers group 1 foods with salt, oil, sugar or other group 2 ingredients added, using preservation methods such as canning and bottling, but the item does not say that any such substance is added, so added substances are not established and neither Group 1 nor Group 3 is established")
    if len(ings) == 1 and kinds[0] in ("nut_seed", "legume", "vegetable", "fruit"):
        if nut_salted:
            what = (nut_group3_driver(ings[0]) if kinds[0] == "nut_seed"
                    else ("fruit with added sugar, syrup or salt (FAO Group 3: 'whole fruit preserved in syrup'; definition: adding salt or sugar to group 1 foods)" if kinds[0] == "fruit"
                          else f"{kinds[0]} with added salt, sugar or brine (FAO Group 3: 'canned or bottled vegetables or legumes (pulses) preserved in brine'; definition: adding salt or sugar to group 1 foods)"))
            return Classification(3, drivers=[Driver(ings[0].raw, what, lookup(ings[0].name)["source"], ings[0].section)])
        return Classification(1, drivers=[Driver(ings[0].raw, "single recognised unprocessed food", lookup(ings[0].name)["source"], ings[0].section)])
    if len(ings) == 1 and animal_dry:
        return Classification(3, drivers=[Driver(ings[0].raw, "dried meat, poultry, fish or seafood (FAO Table 1 Group 3 example: 'salted, dried, cured, or smoked meats and fish'); class-instance of that example", lookup(ings[0].name)["source"], ings[0].section)])
    if len(ings) == 1 and kinds[0] in ("whole_food", "flour") and nut_salted:            # only the salted-grain guard can fill nut_salted for these kinds
        return Classification(3, drivers=[Driver(ings[0].raw, "grain or grain flour with added salt (FAO: group 1 foods with salt added are classed in NOVA group 3 as processed foods; inference: no clause names a salted grain)", lookup(ings[0].name)["source"], ings[0].section)])
    if len(ings) == 1 and kinds[0] in ("whole_food", "flour"):
        what = "powdered milk (FAO Table 1 Group 1: 'fresh, powdered or pasteurized milk')" if milk_powder_named(ings[0]) else "single recognised unprocessed food"
        return Classification(1, drivers=[Driver(ings[0].raw, what, lookup(ings[0].name)["source"], ings[0].section)])
    if len(ings) == 1 and kinds[0] == "food_powder" and powder_composition_stated(ings[0]):
        # owner ruling (class-bulk-2): a powder of one food is Group 1 ONLY when the item's own text states whole-food composition ("100%", "whole"); the bare term "X powder" abstains
        # below (held-sources-1 had answered Group 1 for any sole powder item; superseded).
        return Classification(1, drivers=[Driver(ings[0].raw, "single recognised powder of one food whose own text states whole-food composition ('100%' or 'whole'); nothing else listed", lookup(ings[0].name)["source"], ings[0].section)])
    if len(ings) == 1 and kinds[0] == "culinary":
        return Classification(2, drivers=[Driver(ings[0].raw, "single processed culinary ingredient", lookup(ings[0].name)["source"], ings[0].section)])
    rows = [lookup(i.name) for i in ings]
    if any(r["kind"] == "culture" for r in rows) and any(r["term"] in _MILK_TERMS for r in rows) \
            and all(r["kind"] == "culture" or r["term"] in _MILK_TERMS for r in rows):
        # Narrow rule (research/04): the WHOLE list is recognised and is only milk plus starter culture(s): fermented milk with nothing
        # else in it (no sugar, sweetener, flavour or other marker: those returned above or fall outside this rule). Not keyed off product words.
        return Classification(1, drivers=[Driver(i.raw, "milk fermented with a starter culture, nothing else listed (NUPENS-USP: plain yoghurt with no added sugar or "
                                                 "artificial sweeteners; fermentation of milk to make yoghurt)", "NUPENS-USP classification page (research/04)", i.section) for i in ings])
    powders = [i.raw for i, k in zip(ings, kinds) if k == "food_powder"]
    if powders:
        return Classification(None, reason="a powder of a food (" + "; ".join(powders) + ") is named without its composition: the label does not say whether it is that food alone or carries carriers or anti-caking agents, so the level cannot be judged" + other_open_items(ings, set(powders)))
    if "flour" in kinds:
        return Classification(None, reason="flour-based list: bakery-fresh versus industrial formulation cannot be told from the ingredient list")
    has_food = any(k in ("whole_food", "nut_seed", "legume", "vegetable", "fruit") for _, k in substantive)
    has_culinary = any(k == "culinary" for _, k in substantive) or bool(nut_salted)           # salt or sugar added to the nuts themselves is a Group 2 substance on a Group 1 food: Group 3
    if has_food and has_culinary:
        drv = [Driver(i.raw, f"recognised {'whole food' if k in ('nut_seed', 'legume', 'vegetable', 'fruit') else k.replace('_', ' ')}", lookup(i.name)["source"], i.section) for i, k in substantive]
        return Classification(3, drivers=drv)
    return Classification(None, reason="recognised ingredients, but the combination does not match a group 1, 2 or 3 pattern")


def classify_items(items: list[str], declarations: list[str] | None = None) -> Classification:
    return classify_ingredients(normalise_list(items), declarations)
