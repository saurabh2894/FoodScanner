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

from .normalise import Ingredient, flatten, normalise_ingredient, normalise_list
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
        out.append((re.compile(rf"(?<![a-z]){re.escape(term)}(?![a-z])"), r))
    return tuple(out)


@cache
def lexicon() -> dict[str, dict[str, str]]:
    return {flatten(r["term"]): r for r in load_table("lexicon.csv")}


@cache
def _descriptors() -> frozenset:
    return frozenset(r["word"].lower() for r in load_table("descriptors.csv"))


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
    return None


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
    toks = re.findall(r"[a-z]+", ing.text.lower())
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
_POWDER_ROUTED = ("whole_food", "legume", "vegetable", "fruit")


def powder_composition_stated(ing) -> bool:
    if re.search(r"(?<![\d.])100(?:\.0+)?\s*%", ing.raw.lower()):
        return True
    toks = re.findall(r"[a-z]+", ing.text.lower())
    row = lookup(ing.name)
    return "whole" in toks and "milk" not in toks and not (row and row["term"] in _MILK_TERMS)


# Powdered MILK is placed by the source BY NAME (owner post-merge refinement): FAO Table 1 Group 1 lists "frozen eggs; fresh, powdered or pasteurized milk" (p. 11), so unlike vegetable powders
# (clause names only 'dried') the composition of a milk powder IS source-established. An item whose whole text is "<optional fat-grade word> milk powder" (milk, toned milk, double toned milk,
# buffalo milk; grade words whole/skimmed/skim are fat grades, not composition statements) keeps its plain Group 1 placement. 'milk solids powder' / 'milk solids' (a solids fraction is not the
# named powdered-milk form) and any item with extra words (a bracket naming an additive, a blend) stay under the powder standard.
_MILK_POWDER_ROWS = frozenset({"milk", "toned milk", "double toned milk", "buffalo milk"})
_MILK_POWDER_WORDS = frozenset({"milk", "toned", "double", "buffalo", "whole", "skimmed", "skim", "powder", "powdered"})


def milk_powder_named(ing) -> bool:
    row = lookup(ing.name)
    toks = re.findall(r"[a-z]+", ing.text.lower())
    return bool(row) and row["term"] in _MILK_POWDER_ROWS and "powder" in toks + (["powder"] if "powdered" in toks else []) and set(toks) <= _MILK_POWDER_WORDS


def powder_routed(ing, kind: str) -> bool:
    if kind not in _POWDER_ROUTED or not _added(ing, _POWDER_WORDS):
        return False
    if kind == "whole_food" and milk_powder_named(ing):
        return False
    if kind in _BRINE_KINDS and (legume_added_salt_sugar_or_brine(ing) or legume_preserved_form(ing)):
        return False
    return True


# Unknown additions on the same item are never laundered (class-bulk-3, owner requirement): the guard reads the item's own bracket for salt/sugar/brine, but a bracket on a legume, vegetable or fruit
# item that names content the vocabulary does not recognise ("Dried Mango (XQ9)", "Dried Blueberries (Sunflower Oil)") used to be ignored and the item answered Group 1. Such an item now ABSTAINS: neither
# Group 1 nor Group 3 is established while part of the item is unassessed. Benign bracket parts: recognised foods, descriptors, condition words handled by the guard, negation/connector words, digits/codes.
_BRACKET_BENIGN = frozenset({"with", "without", "skin", "peel", "added", "no", "non", "free", "of", "in", "from", "as", "the", "a", "an", "natural", "cooked", "organic", "whole", "percent", "less", "than", "only", "pure", "plain", "ins", "e"})


def bracket_residual(ing) -> list:
    if not ing.inner:
        return []
    ok_tokens = _descriptors() | _BRACKET_BENIGN | _LEGUME_ADDED | _LEGUME_PRESERVED
    residual = []
    for part in re.split(r"\s*(?:,|;|&|\band\b)\s*", ing.inner):
        toks = re.findall(r"[a-z]+", part)
        if not toks or is_recognised(part.strip()) or all(t in ok_tokens for t in toks):
            continue
        residual.append(part.strip())
    return residual


def nut_added_salt_or_sugar(ing) -> bool:
    return _added(ing, _NUT_ADDED)


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
_MILK_TERMS = frozenset({"milk", "toned milk", "double toned milk", "buffalo milk", "milk solids"})      # lexicon terms that count as the milk of the milk-plus-culture rule
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


def classify_ingredients(ings: list[Ingredient], declarations: list[str] | None = None) -> Classification:
    strong: list[Driver] = []
    weak: list[Driver] = []
    for ing in ings:
        for h in _hits_for(ing):
            d = Driver(ing.raw, h.detail, h.source, ing.section)
            (strong if h.strength == "strong" else weak).append(d)
    for decl in declarations or []:
        text = normalise_ingredient(decl).text   # same spelling/plural handling as ingredients (color -> colour)
        for pat, row in _markers():
            if row["strength"] == "strong" and row["marker_class"] == "cosmetic_additive" and pat.search(text):
                strong.append(Driver(decl, f'declared in "Contains" statement: "{row["term"]}"', row["source"]))

    if strong:
        return Classification(4, drivers=strong)

    # A colour note on a named food ("Turmeric (as colourant)") leaves open whether a colour is added. Without an independent
    # marker (checked above) the result stays uncertain; it is never read as a confident group from the foods alone.
    notes = [i.raw for i in ings if colour_note_only(i)]
    if notes:
        return Classification(None, drivers=weak, reason="a colour note on a named ingredient (" + "; ".join(notes) + ") leaves open whether a colour is added, and no other marker decides the group")

    sweet = [i.raw for i in ings if sweetener_foods_only(i)]
    if sweet:
        return Classification(None, drivers=weak, reason="a sweetener entry whose bracket names only foods (" + "; ".join(sweet) + ") leaves open whether a sweetener additive is added, and no other marker decides the group")

    if weak:
        names = "; ".join(sorted({f"{d.ingredient} -> {d.detail}" for d in weak}))
        return Classification(None, drivers=weak, reason=f"only weak or unlisted markers present ({names}); not enough to call a group")

    unrecognised = [i.raw for i in ings if not is_recognised(i.name)]
    if unrecognised:
        return Classification(None, reason="ingredients not in the local vocabulary, so processing level cannot be judged: " + ", ".join(unrecognised))

    kinds = [lookup(i.name)["kind"] for i in ings]
    bracket_unknown = [(i.raw, bracket_residual(i)) for i, k in zip(ings, kinds) if k in _BRINE_KINDS and bracket_residual(i)]
    kinds = ["food_powder" if powder_routed(i, k) else k for i, k in zip(ings, kinds)]
    unplaced = [i.raw for i, k in zip(ings, kinds) if k == "unplaced"]
    if unplaced:
        # Recognised by NAME only: no source places these items, so the list can never be answered from the rest of it. This only ever ADDS an abstention (a strong
        # marker returned above); it is vocabulary, not classification, and these items are never counted as classified.
        return Classification(None, reason="recognised by name only, and no source read places " + "; ".join(unplaced) + ", so the processing level cannot be judged (recognition is vocabulary, not classification)")
    substantive = [(i, k) for i, k in zip(ings, kinds) if k not in ("neutral", "culture")]
    if bracket_unknown:
        return Classification(None, reason="a bracket on a legume, vegetable or fruit item names content the vocabulary does not recognise (" + "; ".join(f"{raw}: {', '.join(r)}" for raw, r in bracket_unknown)
                              + "), so neither Group 1 nor Group 3 is established while part of the item is unassessed")
    nut_salted = [i.raw for i, k in zip(ings, kinds) if (k == "nut_seed" and nut_added_salt_or_sugar(i)) or (k in _BRINE_KINDS and legume_added_salt_sugar_or_brine(i))]
    legume_preserved = [i.raw for i, k in zip(ings, kinds) if k in _BRINE_KINDS and legume_preserved_form(i) and not legume_added_salt_sugar_or_brine(i)]
    if legume_preserved:
        return Classification(None, reason="a canned, bottled or preserved legume, vegetable or fruit (" + "; ".join(legume_preserved) + "): FAO Group 3 names vegetables and legumes preserved in brine and fruit in syrup, but the item does not say that salt, sugar, syrup or brine is added, so neither Group 1 nor Group 3 is established")
    if len(ings) == 1 and kinds[0] in ("nut_seed", "legume", "vegetable", "fruit"):
        if nut_salted:
            what = ("nut or seed with added salt or sugar (FAO Table 1 Group 3: 'salted or sugared nuts and seeds')" if kinds[0] == "nut_seed"
                    else ("fruit with added sugar, syrup or salt (FAO Group 3: 'whole fruit preserved in syrup'; definition: adding salt or sugar to group 1 foods)" if kinds[0] == "fruit"
                          else f"{kinds[0]} with added salt, sugar or brine (FAO Group 3: 'canned or bottled vegetables or legumes (pulses) preserved in brine'; definition: adding salt or sugar to group 1 foods)"))
            return Classification(3, drivers=[Driver(ings[0].raw, what, lookup(ings[0].name)["source"], ings[0].section)])
        return Classification(1, drivers=[Driver(ings[0].raw, "single recognised unprocessed food", lookup(ings[0].name)["source"], ings[0].section)])
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
        return Classification(None, reason="a powder of a food (" + "; ".join(powders) + ") is named without its composition: the label does not say whether it is that food alone or carries carriers or anti-caking agents, so the level cannot be judged")
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
