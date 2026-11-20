"""photo -> OCR -> parse -> normalise -> classify -> abstention gate.

Single entry point shared by the CLI, the evaluation script and the web page.
Rule (CLAUDE.md): whenever evidence is weak the result is "Not enough information"
with a reason, never a guessed group.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field, replace
from pathlib import Path

from .classify import Driver, _hits_for, classify_ingredients, is_recognised, marker_terms
from .normalise import Ingredient, InsUse, normalise_list
from .ocr import OcrEngine, TesseractOcr
from .parser import (parse_ingredient_list, split_compound, split_items, split_top_level_and, starts_with_denied_label,
                     suspect_section_items)

NOT_ENOUGH = "Not enough information"
GROUP_NAMES = {
    1: "unprocessed or minimally processed foods",
    2: "processed culinary ingredients",
    3: "processed foods",
    4: "ultra-processed foods",
}

MIN_CHARS = 20          # fewer non-space characters than this: OCR produced little text
MIN_ALPHA_RATIO = 0.5   # share of alphabetic characters; below this the text looks like noise
NO_TEXT = "No text to analyse"                         # pasted text: nothing there
NO_INGREDIENTS = "No ingredients found in this text"   # pasted text: no readable ingredient list


@dataclass
class Analysis:
    answered: bool
    group: int | None = None
    reason: str | None = None            # why we abstained
    ingredients: list[str] = field(default_factory=list)
    drivers: list[Driver] = field(default_factory=list)
    ins_mappings: list[InsUse] = field(default_factory=list)
    extracted_text: str = ""
    warnings: list[str] = field(default_factory=list)   # answered, but with a caveat
    sections: list[tuple[str | None, list[str]]] = field(default_factory=list)   # (label, items) per list section
    # What the classifier could not judge (not in the vocabulary, no marker, no INS code), plus compound
    # group names that were expanded. Shown so nothing is invisible once a strong marker is found.
    unassessed: list[str] = field(default_factory=list)
    ignored: list[str] = field(default_factory=list)    # text after the list that was not read as ingredients
    # additive / flavour declarations from "Contains ..." lines: [{"text", "in_list"}]. in_list False: stated there but
    # missing from the ingredient list. They count as evidence but are never added to the list; allergens are dropped.
    declared: list[dict] = field(default_factory=list)

    @property
    def headline(self) -> str:
        if self.answered:
            return f"NOVA group {self.group}: {GROUP_NAMES[self.group]}"
        return f"{NOT_ENOUGH}: {self.reason}"


def _abstain(reason: str, text: str, **kw) -> Analysis:
    return Analysis(answered=False, reason=reason, extracted_text=text, **kw)


def _recognisable(ing: Ingredient) -> bool:
    return is_recognised(ing.name) or bool(ing.ins) or bool(_hits_for(ing))


def _split_pairs(raw: str) -> list[str]:
    """"emulsifier [472e] and flour treatment agent [1101(ii)]" -> two items, but only when EVERY side is a recognisable
    ingredient, so "Spices and Condiments" or "Natural and Nature Identical Flavours" stay whole."""
    parts = split_top_level_and(raw)
    if len(parts) > 1 and all(_recognisable(normalise_list([p])[0]) for p in parts):
        return parts
    return [raw]


def _declared_additives(declarations: list[str], ings: list[Ingredient]) -> list[dict]:
    """Additive/flavour clauses of the "Contains ..." lines, each marked as present in or missing from the list.
    A clause with no additive class word and no INS code (an allergen, "37% millets") is not an additive: dropped."""
    list_terms = set().union(*[marker_terms(i.text) for i in ings]) if ings else set()
    list_codes = {u.code for i in ings for u in i.ins}
    out: list[dict] = []
    for decl in declarations:
        body = re.sub(r"^contains\s*:?\s*", "", decl, flags=re.IGNORECASE)
        for part in split_items(body):
            for clause in split_top_level_and(part):
                ing = normalise_list([clause])[0]
                terms, codes = marker_terms(ing.text), {u.code for u in ing.ins}
                if not terms and not codes:
                    continue
                entry = {"text": clause.strip(" ."), "in_list": terms <= list_terms and codes <= list_codes}
                if entry not in out:
                    out.append(entry)
    return out


def _short(text: str, limit: int = 100) -> str:
    return text if len(text) <= limit else text[: limit - 3] + "..."


def _looks_like_more_ingredients(seg: str) -> bool:
    """Unread text after a full stop that could be the rest of the list: it is list-shaped (two or more
    comma-separated items) or holds a recognised ingredient, marker or INS code. Footnotes (*, #) and
    non-ingredient labels (Note:, Directions:, ...) are not."""
    if seg.lstrip().startswith(("*", "\u2020", "#")) or starts_with_denied_label(seg):
        return False
    parts = split_items(seg)
    return len(parts) >= 2 or any(_recognisable(normalise_list([part])[0]) for part in parts)


def _expand(items: list[tuple[str, str | None]], depth: int = 0, heads: list[str] | None = None) -> list[Ingredient]:
    """Normalise (item, section label) pairs, expanding unknown compound ingredients into their sub-items.

    "Seasoning (Sugar, Maltodextrin, ...)" is judged by its contents, so drivers
    name the specific ingredient. A compound whose head is already recognised
    ("edible vegetable oil (palm, coconut)") or carries a marker/INS code
    ("raising agents (INS 500(ii), INS 503(ii))") is left whole. Sub-items keep the
    section label of the item they came from.
    """
    out: list[Ingredient] = []
    for raw, section in items:
        ing = normalise_list([raw])[0]
        ing.section = section
        ing.ins = [replace(u, section=section) for u in ing.ins]
        split = split_compound(raw) if depth < 3 else None
        if split and not _recognisable(normalise_list([split[0]])[0]):
            if heads is not None:
                heads.append(split[0])          # the group name itself is not classified: keep it visible
            out.extend(_expand([(sub, section) for sub in split[1]], depth + 1, heads))
        else:
            out.append(ing)
    return out


def analyse_text(text: str, *, source: str = "ocr") -> Analysis:
    """Analyse label text.

    source="ocr": text came from reading a photo. Short or noisy text is blamed on OCR, and the
        "Ingredients" heading is required (otherwise a nutrition table could be taken for a list).
        This is the default so the photo path keeps its existing behaviour.
    source="text": text was typed or pasted. There is no length gate (a one-ingredient list is valid),
        a list without an "Ingredients" heading is accepted as the whole text, and messages talk about
        the text, never about OCR.
    """
    if source not in ("ocr", "text"):
        raise ValueError(f"source must be 'ocr' or 'text', not {source!r}")
    compact = re.sub(r"\s+", "", text)

    if source == "text":
        if not compact:
            return _abstain(NO_TEXT, text)
        if sum(c.isalpha() for c in compact) / len(compact) < MIN_ALPHA_RATIO:
            return _abstain(NO_INGREDIENTS, text)
        parsed = parse_ingredient_list(text, assume_list=True)
        if not parsed.found:
            return _abstain(NO_INGREDIENTS, text)
    else:
        if len(compact) < MIN_CHARS:
            return _abstain("OCR produced little text", text)
        if sum(c.isalpha() for c in compact) / len(compact) < MIN_ALPHA_RATIO:
            return _abstain("extracted text looks like noise, not a readable label", text)
        parsed = parse_ingredient_list(text)
        if not parsed.found:
            return _abstain("no ingredient list found in the text", text)

    sections = [(sec.label, [p for raw in sec.items for p in _split_pairs(raw)]) for sec in parsed.sections]
    items = [raw for _, its in sections for raw in its]
    heads: list[str] = []
    ings = _expand([(raw, label) for label, its in sections for raw in its], heads=heads)
    declared = _declared_additives(parsed.declarations, ings)
    unassessed = list(dict.fromkeys(
        [i.raw for i in ings if not _recognisable(i)]
        + [f"{h} (group name; its contents were assessed separately)" for h in heads]))
    uses = [u for i in ings for u in i.ins]
    section_warnings = [f'"{it}" contains a colon, so a section label may not have been split from the ingredient before it'
                        for it in suspect_section_items(items)]
    unread_like = [seg for seg in parsed.ignored if _looks_like_more_ingredients(seg)]
    unread_warnings = [f'Text after a full stop was not read as ingredients but looks like more of the list: "{_short(seg)}"'
                       for seg in unread_like]
    section_warnings += unread_warnings
    common = dict(ingredients=items, ins_mappings=uses, warnings=list(section_warnings), unassessed=unassessed,
                  ignored=list(parsed.ignored), declared=declared,
                  sections=[(label, list(its)) for label, its in sections])

    # Truncation: brackets left open, or the list runs off the end of the text
    # (no full stop / stop phrase) on a word we cannot recognise ("refined wheat flo").
    truncation = None
    if parsed.unbalanced_brackets:
        truncation = "ingredient list looks truncated (unclosed bracket)"
    elif not parsed.terminated and not _recognisable(ings[-1]):
        truncation = f'ingredient list looks truncated (ends mid-word or unrecognised: "{items[-1]}")'
    # Unlabelled text after a full stop that looks like more of the list was not read (never dropped silently:
    # it is in `ignored` and in the warnings). Like truncation, it can only be answered when a strong marker
    # already decides (Group 4); otherwise a Group 1-3 call could hide a missing ingredient or marker.
    unread = (f'text after a full stop looks like more ingredients and was not read: "{_short(unread_like[0])}"'
              if unread_like else None)
    blocking = truncation or unread

    result = classify_ingredients(ings, parsed.declarations)

    # Option A (decided by the user): missing text can never remove a marker, so a
    # strong-marker Group 4 call stands on a possibly incomplete list, with a warning.
    # Every other truncated case abstains.
    if blocking and result.group != 4:
        return _abstain(blocking, text, drivers=result.drivers, **common)
    if result.group is None:
        return _abstain(result.reason or "classification uncertain", text, drivers=result.drivers, **common)
    warnings = list(section_warnings)
    if truncation:
        warnings.append("List may be incomplete (" + truncation.removeprefix("ingredient list looks truncated ").strip("()") +
                        "). Group 4 stands because the markers found are already enough.")
    return Analysis(answered=True, group=result.group, drivers=result.drivers,
                    extracted_text=text, **{**common, "warnings": warnings})


def analyse_image(path: str | Path, ocr: OcrEngine | None = None) -> Analysis:
    """Raises ocr.OcrUnavailable if the OCR backend cannot run (an error, not an abstention)."""
    engine = ocr or TesseractOcr()
    return analyse_text(engine.extract_text(path), source="ocr")
