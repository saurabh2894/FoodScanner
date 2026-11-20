"""photo -> OCR -> parse -> normalise -> classify -> abstention gate.

Single entry point shared by the CLI, the evaluation script and the web page.
Rule (CLAUDE.md): whenever evidence is weak the result is "Not enough information"
with a reason, never a guessed group.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field, replace
from pathlib import Path

from .classify import Driver, _hits_for, classify_ingredients, colour_note_only, ingredient_marker_terms, is_colour_note, is_recognised, marker_terms
from .normalise import Ingredient, InsUse, normalise_list
from .ocr import OcrEngine, TesseractOcr
from .parser import (count_words, parse_ingredient_list, split_compound, split_items, split_top_level_and, split_top_level_and_ex, starts_with_denied_label,
                     suspect_section_items, unclosed_openers)

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
    heading: dict = field(default_factory=lambda: {"kind": "none", "text": ""})   # how the list was located
    # Completeness signal. Text-span coverage over the words after the heading plus explicit reasons for doubt; it never
    # claims exact completeness (the true item count is unknown): {"status": complete|uncertain, "heading", "words":
    # {region, in_list, declared, excluded, not_read, unaccounted}, "list_share", "assessed": {items, not_assessed}, "reasons"}
    completeness: dict = field(default_factory=lambda: {
        "status": "uncertain", "heading": "none", "reasons": ["no ingredient list was read"], "list_share": 0.0,
        "words": {"region": 0, "in_list": 0, "declared": 0, "excluded": 0, "not_read": 0, "unaccounted": 0},
        "assessed": {"items": 0, "not_assessed": 0}})

    @property
    def headline(self) -> str:
        if self.answered:
            return f"NOVA group {self.group}: {GROUP_NAMES[self.group]}"
        return f"{NOT_ENOUGH}: {self.reason}"


def _abstain(reason: str, text: str, **kw) -> Analysis:
    return Analysis(answered=False, reason=reason, extracted_text=text, **kw)


def _recognisable(ing: Ingredient) -> bool:
    return is_recognised(ing.name) or bool(ing.ins) or bool(_hits_for(ing))


_CODE_ONLY = re.compile(
    r"^\s*(?:(?:ins|e)\s*[-:.]?\s*)?\d{3,4}[a-z]?(?:\([ivxl]+\))*"
    r"(?:\s*(?:,|;|and|&|/)\s*(?:(?:ins|e)\s*[-:.]?\s*)?\d{3,4}[a-z]?(?:\([ivxl]+\))*)*\s*$", re.IGNORECASE)


def _shared_code_list(parts: list[str]) -> bool:
    """"emulsifiers and stabilizers [INS 460(i), INS 471]": ONE code list at the end that belongs to both classes. Which class a
    code belongs to is not stated, so the item is not split (splitting would pin every code on the last class)."""
    last = parts[-1].rstrip()
    if len(parts) < 2 or not last or last[-1] not in ")]}" or any(c in p for p in parts[:-1] for c in "([{"):
        return False
    depth = 0
    for i in range(len(last) - 1, -1, -1):
        depth += last[i] in ")]}"
        depth -= last[i] in "([{"
        if depth == 0:
            return bool(_CODE_ONLY.match(last[i + 1:-1]))
    return False


def _split_pairs_ex(raw: str) -> tuple[list[str], int]:
    """"emulsifier [472e] and flour treatment agent [1101(ii)]" -> two items, but only when EVERY side is a recognisable
    ingredient, so "Spices and Condiments" or "Natural and Nature Identical Flavours" stay whole. One shared trailing code list
    keeps the item whole (see _shared_code_list). Also returns how many words were the joiners ("and"), so the completeness
    accounting counts only those as removed."""
    parts, connectors = split_top_level_and_ex(raw)
    if len(parts) > 1 and not _shared_code_list(parts) and all(_recognisable(normalise_list([p])[0]) for p in parts):
        return parts, sum(count_words(c) for c in connectors)
    return [raw], 0


def _split_pairs(raw: str) -> list[str]:
    return _split_pairs_ex(raw)[0]


def _declared_additives(declarations: list[str], ings: list[Ingredient]) -> list[dict]:
    """Additive/flavour clauses of the "Contains ..." lines, each marked as present in or missing from the list.
    A clause with no additive class word and no INS code (an allergen, "37% millets") is not an additive: dropped."""
    list_terms = set().union(*[ingredient_marker_terms(i) for i in ings]) if ings else set()
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


_NUTRITION = ("kcal", "energy", "carbohydrate", "per 100", "serving size", "cholesterol", "nutrition", "rda", "calories", "total fat", "trans fat")
_MARKETING = ("buy", "offer", "free", "mrp", "enjoy", "tasty", "crunchy", "delicious", "limited", "new!", "gift", "price", "taste", "extra")
RETAKE = 'retake the photo with the ingredient panel (and its "Ingredients" heading) in frame'


def _infer_block(text: str) -> str | None:
    """No heading was found: the most plausible ingredient text block, or None. Never a nutrition table, marketing copy
    or an allergen statement, and it must look like a list (four or more short items, mostly recognisable)."""
    best, best_score = None, 0
    for block in re.split(r"\n\s*\n", text.replace("\r\n", "\n")):
        flat = re.sub(r"\s+", " ", block).strip()
        low = flat.lower()
        if not flat or re.match(r"(?:may\s+)?contains?\b|allerg", low):
            continue
        if sum(k in low for k in _NUTRITION) >= 2 or sum(k in low for k in _MARKETING) >= 2:
            continue
        parts = split_items(flat)
        if len(parts) < 4 or sum(len(x.split()) for x in parts) / len(parts) > 6:
            continue
        ings = normalise_list(parts)
        recognised = sum(_recognisable(i) for i in ings)
        marked = sum(bool(i.ins) or bool(_hits_for(i)) for i in ings)
        score = recognised + 2 * marked
        if recognised / len(parts) >= 0.4 and score >= 3 and score > best_score:
            best, best_score = flat, score
    return best


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
        if split and len(split[1]) == 1 and is_colour_note(normalise_list([split[1][0]])[0].text):
            split = None          # "Annatto (colour)": a function note on a named food, not a colour ingredient: keep whole
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
            return _abstain("OCR produced little text; retake the photo closer and in focus", text)
        if sum(c.isalpha() for c in compact) / len(compact) < MIN_ALPHA_RATIO:
            return _abstain("extracted text looks like noise, not a readable label; retake a clearer photo", text)
        parsed = parse_ingredient_list(text)
        if not parsed.found:
            block = _infer_block(text)
            parsed = parse_ingredient_list(block, assume_list=True) if block else None
            if parsed is None or not parsed.found:
                return _abstain(f"no ingredient list found in the text; {RETAKE}", text)
            parsed.heading_kind = "inferred"

    split = [[(raw, *_split_pairs_ex(raw)) for raw in sec.items] for sec in parsed.sections]
    sections = [(sec.label, [p for _, parts, _j in grp for p in parts]) for sec, grp in zip(parsed.sections, split)]
    items = [raw for _, its in sections for raw in its]
    joiners = sum(j for grp in split for _raw, _parts, j in grp)       # only the joiner words; any other word a split dropped stays "unaccounted"
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
    section_warnings += [f'"{i.raw}": a colour note on a named ingredient is not counted as an added colour' for i in ings if colour_note_only(i)]
    if parsed.unbalanced_brackets:
        # No auto-close: any close point would be a guess. The text after the stray bracket stays together, in the item that holds it.
        section_warnings += [f'A bracket near "{snip}" was never closed, so the text after it was kept together as one item instead of being split (where it should close cannot be known)'
                             for it in items for snip in unclosed_openers(it)]
    common = dict(ingredients=items, ins_mappings=uses, warnings=list(section_warnings), unassessed=unassessed,
                  ignored=list(parsed.ignored), declared=declared, heading={"kind": parsed.heading_kind, "text": parsed.heading_text},
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
    heading_risk = None
    if source == "ocr" and parsed.heading_kind == "fuzzy":
        heading_risk = (f'the "Ingredients" heading was read as "{parsed.heading_text}" (the photo may be cut off at the left edge), '
                        f"so the start of the list may be missing; {RETAKE}")
    elif source == "ocr" and parsed.heading_kind == "inferred":
        heading_risk = f'no "Ingredients" heading was found, so the text block used may not be the ingredient list; {RETAKE}'
    blocking = truncation or unread or heading_risk

    in_list = sum(count_words(label or "") + sum(count_words(i) for i in its) for label, its in sections) + joiners
    not_read = sum(count_words(x) for x in parsed.ignored)
    declared_w = sum(count_words(d) for d in parsed.declarations)
    unaccounted = max(0, parsed.kept_words - in_list - not_read)
    reasons = []
    if source == "ocr" and parsed.heading_kind == "fuzzy":
        reasons.append(f'the heading was read as "{parsed.heading_text}": the photo may be cut off at the left edge')
    if source == "ocr" and parsed.heading_kind == "inferred":
        reasons.append('no "Ingredients" heading was found: the most list-like text block was used')
    if parsed.unbalanced_brackets:
        reasons.append("brackets are not balanced: text may be cut off or misread")
    if truncation:
        reasons.append("the list looks truncated")
    if unread_like:
        reasons.append("text after a full stop looks like more ingredients and was not read")
    if unaccounted:
        reasons.append(f"{unaccounted} word(s) after the heading were neither read as ingredients nor set aside")
    if suspect_section_items(items):
        reasons.append("a section label may not have been split from an ingredient")
    denom = in_list + not_read + unaccounted
    completeness = {
        "status": "uncertain" if reasons else "complete", "heading": parsed.heading_kind, "reasons": reasons,
        "list_share": round(in_list / denom, 3) if denom else 0.0,
        "words": {"region": parsed.region_words, "in_list": in_list, "declared": declared_w,
                  "excluded": max(0, parsed.tail_words - declared_w), "not_read": not_read, "unaccounted": unaccounted},
        "assessed": {"items": len(ings), "not_assessed": sum(1 for i in ings if not _recognisable(i))}}
    common["completeness"] = completeness
    if unaccounted:                                           # lost text: like truncation, only a strong-marker Group 4 stands
        blocking = blocking or f"{unaccounted} word(s) after the heading were neither read nor set aside, so text may have been lost"

    result = classify_ingredients(ings, parsed.declarations)

    # Option A (decided by the user): missing text can never remove a marker, so a
    # strong-marker Group 4 call stands on a possibly incomplete list, with a warning.
    # Every other truncated case abstains.
    if blocking and result.group != 4:
        return _abstain(blocking, text, drivers=result.drivers, **common)
    if result.group is None:
        return _abstain(result.reason or "classification uncertain", text, drivers=result.drivers, **common)
    warnings = list(section_warnings)
    if heading_risk:
        warnings.append(heading_risk[0].upper() + heading_risk[1:].split("; retake")[0] + ". Group 4 stands because the markers found are already enough.")
    if truncation:
        warnings.append("List may be incomplete (" + truncation.removeprefix("ingredient list looks truncated ").strip("()") +
                        "). Group 4 stands because the markers found are already enough.")
    return Analysis(answered=True, group=result.group, drivers=result.drivers,
                    extracted_text=text, **{**common, "warnings": warnings})


def analyse_image(path: str | Path, ocr: OcrEngine | None = None) -> Analysis:
    """Raises ocr.OcrUnavailable if the OCR backend cannot run (an error, not an abstention)."""
    engine = ocr or TesseractOcr()
    first = analyse_text(engine.extract_text(path), source="ocr")
    alt = getattr(engine, "extract_text_alt", None)
    if alt is None or (first.answered and first.completeness["status"] == "complete"):
        return first
    # One bounded second pass for photos that did not read cleanly. The better yield is kept; ties keep the first reading.
    second = analyse_text(alt(path), source="ocr")
    return second if _ocr_yield(second) > _ocr_yield(first) else first


def _ocr_yield(a: Analysis) -> int:
    """Ingredients found minus those outside the vocabulary; 0 when no list was found."""
    return max(0, len(a.ingredients) - len(a.unassessed)) if a.ingredients else 0
