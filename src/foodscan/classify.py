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
    kept = " ".join(t for t in name.split() if t not in _descriptors())
    if kept and kept != name:
        if kept in lex:
            return lex[kept]
        if _singular_phrase(kept) in idx:
            return idx[_singular_phrase(kept)]
    return None


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


def ingredient_marker_terms(ing: Ingredient) -> set[str]:
    """marker_terms for an ingredient in the list. When its bracket is only a function note, nothing in it is a marker."""
    return set() if colour_note_only(ing) else marker_terms(ing.text)


def marker_terms(text: str) -> set[str]:
    """The marker terms (markers.csv) found in a normalised text."""
    return {row["term"] for pat, row in _markers() if pat.search(text)}


def _hits_for(ing: Ingredient) -> list[_Hit]:
    hits: list[_Hit] = []
    note_only = colour_note_only(ing)
    for pat, row in _markers():
        if note_only:
            break          # the name has no marker and the bracket is only a function note: its words ("colour & flavour") decide nothing
        if pat.search(ing.text):
            hits.append(_Hit(row["strength"], row["marker_class"], f'"{row["term"]}" ({row["marker_class"]})', row["source"]))
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

    if weak:
        names = "; ".join(sorted({f"{d.ingredient} -> {d.detail}" for d in weak}))
        return Classification(None, drivers=weak, reason=f"only weak or unlisted markers present ({names}); not enough to call a group")

    unrecognised = [i.raw for i in ings if not is_recognised(i.name)]
    if unrecognised:
        return Classification(None, reason="ingredients not in the local vocabulary, so processing level cannot be judged: " + ", ".join(unrecognised))

    kinds = [lookup(i.name)["kind"] for i in ings]
    substantive = [(i, k) for i, k in zip(ings, kinds) if k != "neutral"]
    if len(ings) == 1 and kinds[0] in ("whole_food", "flour"):
        return Classification(1, drivers=[Driver(ings[0].raw, "single recognised unprocessed food", lookup(ings[0].name)["source"], ings[0].section)])
    if len(ings) == 1 and kinds[0] == "culinary":
        return Classification(2, drivers=[Driver(ings[0].raw, "single processed culinary ingredient", lookup(ings[0].name)["source"], ings[0].section)])
    if "flour" in kinds:
        return Classification(None, reason="flour-based list: bakery-fresh versus industrial formulation cannot be told from the ingredient list")
    has_food = any(k == "whole_food" for _, k in substantive)
    has_culinary = any(k == "culinary" for _, k in substantive)
    if has_food and has_culinary:
        drv = [Driver(i.raw, f"recognised {k.replace('_', ' ')}", lookup(i.name)["source"], i.section) for i, k in substantive]
        return Classification(3, drivers=drv)
    return Classification(None, reason="recognised ingredients, but the combination does not match a group 1, 2 or 3 pattern")


def classify_items(items: list[str], declarations: list[str] | None = None) -> Classification:
    return classify_ingredients(normalise_list(items), declarations)
