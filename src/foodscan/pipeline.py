"""photo -> OCR -> parse -> normalise -> classify -> abstention gate.

Single entry point shared by the CLI, the evaluation script and the web page.
Rule (CLAUDE.md): whenever evidence is weak the result is "Not enough information"
with a reason, never a guessed group.
"""
from __future__ import annotations

import re
from functools import cache
from dataclasses import dataclass, field, replace
from pathlib import Path

from .classify import _MILK_TERMS, is_fat_row, lookup as _lookup, Driver, _hits_for, classify_ingredients, nested_unplaced, colour_note_only, ingredient_marker_terms, sweetener_foods_only, is_colour_note, is_recognised, marker_terms
from .normalise import Ingredient, InsUse, normalise_list
from .ocr import OcrEngine, TesseractOcr
from .normalise import _ins_reference, is_additive_absence_claim
from .tables import load_table
from .parser import (_class_word_re, count_words, parse_ingredient_list, split_compound, split_items, split_top_level_and, split_top_level_and_ex, starts_with_denied_label,
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
    reading_conflict: dict | None = None  # photo-only, alternatives remain separate and never alter the chosen result
    warnings: list[str] = field(default_factory=list)   # answered, but with a caveat
    sections: list[tuple[str | None, list[str]]] = field(default_factory=list)   # (label, items) per list section
    # What the classifier could not judge (not in the vocabulary, no marker, no INS code), plus compound
    # group names that were expanded. Shown so nothing is invisible once a strong marker is found.
    unassessed: list[str] = field(default_factory=list)
    # Items recognised BY NAME ONLY (kind "unplaced"): in the vocabulary, but no source places them. They are shown apart from classified items and from "unassessed",
    # never counted as classified coverage, and the list that holds one cannot be answered (recognition is vocabulary, not classification).
    unplaced: list[str] = field(default_factory=list)
    ignored: list[str] = field(default_factory=list)    # text after the list that was not read as ingredients
    # additive / flavour declarations from "Contains ..." lines: [{"text", "in_list"}]. in_list False: stated there but
    # missing from the ingredient list. They count as evidence but are never added to the list; allergens are dropped.
    declared: list[dict] = field(default_factory=list)
    heading: dict = field(default_factory=lambda: {"kind": "none", "text": ""})   # how the list was located
    # Completeness signal. Text-span coverage over the words after the heading plus explicit reasons for doubt; it never
    # claims exact completeness (the true item count is unknown): {"status": complete|uncertain, "heading", "words":
    # {region, in_list, declared, excluded, not_read, unaccounted}, "list_share", "assessed": {items, not_assessed}, "reasons"}
    retake: str | None = None            # photo path only: concrete retake guidance when no list could be read even after the rotated retries
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


@cache
def _vocab() -> tuple[frozenset[str], frozenset[str], frozenset[str]]:
    """(words, phrases, descriptor words) of the vocabulary tables (lexicon, synonyms, markers, descriptors): for telling a cut-off fragment from an unknown whole word."""
    words: set[str] = set()
    phrases: set[str] = set()
    for table, cols in (("lexicon.csv", ("term",)), ("synonyms.csv", ("from", "to")), ("markers.csv", ("term",)), ("descriptors.csv", ("word",))):
        for r in load_table(table):
            for c in cols:
                text = (r.get(c) or "").lower()
                words.update(re.findall(r"[a-z]+", text))
                phrases.add(" ".join(re.findall(r"[a-z]+", text)))
    return frozenset(words), frozenset(phrases), frozenset(r["word"].lower() for r in load_table("descriptors.csv"))


def _looks_cut_off(ing: Ingredient) -> bool:
    """The item looks cut off: its last word is a strict prefix of a vocabulary word and not itself one ("refined wheat flo"), or the whole item (without
    leading descriptors) is the start of a longer vocabulary phrase ("pasteurized toned" -> "toned milk"). An unknown whole word is not a cut-off."""
    words, phrases, descriptors = _vocab()
    toks = re.findall(r"[a-z]+", ing.name.lower())
    if not toks:
        return False
    last = toks[-1]
    if len(last) >= 3 and last not in words and any(w.startswith(last) for w in words):
        return True
    for k in range(len(toks)):            # drop leading words one at a time: "pasteurized toned" -> "toned" is the start of "toned milk"
        if k == 0 or toks[k - 1] in descriptors:
            if any(p.startswith(" ".join(toks[k:]) + " ") for p in phrases):
                return True
    return False


_CODE_ONLY = re.compile(
    r"^\s*(?:(?:ins|e)\s*[-:.]?\s*)?\d{3,4}[a-z]?(?:\([ivxl]+\))*"
    r"(?:\s*(?:,|;|and|&|/)\s*(?:(?:ins|e)\s*[-:.]?\s*)?\d{3,4}[a-z]?(?:\([ivxl]+\))*)*\s*$", re.IGNORECASE)


def _shared_code_list(parts: list[str]) -> bool:
    """"emulsifiers and stabilizers [INS 460(i), INS 471]": ONE code list at the end that belongs to both classes. Which class a
    code belongs to is not stated, so the item is not split (splitting would pin every code on the last class)."""
    last = parts[-1].rstrip()
    if len(parts) < 2 or not last or last[-1] not in ")]}" or any(c in p for p in parts[:-1] for c in "([{"):
        return False
    if any(re.search(r"flavou?r", p, re.IGNORECASE) for p in parts[:-1]):
        return False          # flavourings have no INS numbers (CXG 36 introduction), so a trailing code belongs to the other item
    depth = 0
    for i in range(len(last) - 1, -1, -1):
        depth += last[i] in ")]}"
        depth -= last[i] in "([{"
        if depth == 0:
            return bool(_CODE_ONLY.match(last[i + 1:-1]))
    return False


def _ends_in_code_bracket(part: str) -> bool:
    """"dough conditioner (223)": the item ends in a bracket holding only additive codes, which is itself the mark of an additive item."""
    s = part.rstrip()
    if not s or s[-1] not in ")]}":
        return False
    depth = 0
    for i in range(len(s) - 1, -1, -1):
        depth += s[i] in ")]}"
        depth -= s[i] in "([{"
        if depth == 0:
            return i > 0 and bool(_CODE_ONLY.match(s[i + 1:-1]))
    return False


_SUSPECT_PCT = re.compile(r"\(\s*\d+(?:\.\d+)?\s*%\s*\)\s+(?!and\b|or\b|with\b|of\b|in\b|&|\(|\[|\{)[A-Za-z]", re.IGNORECASE)
def _role_phrase_notes(ings) -> list[str]:
    """A role phrase ("emulsifying agent") read as its class word is a PROVISIONAL mapping (no source names the phrase): keep that visible."""
    out = []
    for i in ings:
        low = i.raw.lower()
        for r in load_table("synonyms.csv"):
            if r["source"].startswith("PROVISIONAL role phrase") and re.search(rf"(?<![a-z]){re.escape(r['from'])}(?![a-z])", low):
                out.append(f'"{_short(i.raw)}": "{r["from"]}" is read as the {r["to"].split(" & ")[0]} class by a provisional mapping (no source names the phrase)')
                break
    return out


def _implausible(ings) -> bool:
    """Few recognised items and no additive code or marker at all: the block may not be an ingredient list (photo path)."""
    if not ings:
        return False
    if any(i.ins or _hits_for(i) for i in ings):
        return False
    return sum(_recognisable(i) for i in ings) / len(ings) < 1 / 3


def _possible_misreads(ings) -> list[str]:
    """REVIEW HINT ONLY. A code is never replaced and no alternative is used in classification. One check, from a source row: the label's
    own additive name is tied to a DIFFERENT code by a page that was read (ins_names.csv). No candidate is ever guessed from digit
    similarity. (The class-word versus function check was removed: a legitimate pack was flagged, e.g. INS 508 under "Thickeners".)"""
    out, seen = [], set()
    names = _ins_reference()
    for ing in ings:
        if not ing.ins:
            continue
        head = re.split(r"[\[({]", ing.raw, maxsplit=1)[0].strip(" ,;:*-") or ing.raw
        codes = {u.code for u in ing.ins}
        for u in ing.ins:
            key = (ing.raw, u.code)
            if key in seen:
                continue
            tied = next((c for c, r in names.items() if len(r["name"]) >= 5 and r["name"].lower() in ing.name and c not in codes), None)
            if tied:
                seen.add(key)
                url = re.search(r"https?://\S+", names[tied]["source"])
                out.append(f'Read as INS {u.code}. The label text says {head}, and the source page for {names[tied]["name"].lower()} gives INS {tied}'
                           f'{" (" + url.group(0) + ")" if url else ""}. Possible misread, check the pack.')
                continue
    return out


def _names_two_oils(parts: list[str]) -> bool:
    """'Corn and Canola Oil' splits at 'and' into the food 'Corn' and the oil 'Canola Oil'. When the second part is an oil or fat row and the first part followed by 'oil' (or 'fat') is also an oil row, the phrase names TWO oils
    (a blend), not a food plus an oil, and the positive composition is not established: it stays whole and abstains. 'Rice and Sunflower Oil' ('rice oil' is no row) is still a food plus an oil."""
    if len(parts) != 2:
        return False
    first, second = (normalise_list([p])[0] for p in parts)
    if not is_fat_row(_lookup(second.name)) or not _lookup(first.name) or _lookup(first.name)["kind"] == "culinary":
        return False
    return any(is_fat_row(_lookup(f"{first.name} {w}")) for w in ("oil", "fat"))


def _split_pairs_ex(raw: str) -> tuple[list[str], int]:
    """"emulsifier [472e] and flour treatment agent [1101(ii)]" -> two items, but only when EVERY side is a recognisable
    ingredient, so "Spices and Condiments" or "Natural and Nature Identical Flavours" stay whole. One shared trailing code list
    keeps the item whole (see _shared_code_list). Also returns how many words were the joiners ("and"), so the completeness
    accounting counts only those as removed."""
    parts, connectors = split_top_level_and_ex(raw)
    if len(parts) > 1 and not _shared_code_list(parts) and all(_recognisable(normalise_list([p])[0]) or _ends_in_code_bracket(p) for p in parts):
        if _names_two_oils(parts):
            return [raw], 0           # culinary-guard-1: kept whole, so it abstains as unrecognised instead of reading 'Corn and Canola Oil' as the food corn plus the oil canola
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


_PROVENANCE = re.compile(r"^made\s+(?:from|with|using)\s+(.+)$", re.IGNORECASE)


def _strip_provenance(parsed) -> int:
    """A trailing provenance line ("Made from Toned Milk") names the milk the product is made from: part of the milk context, not a
    separate ingredient. It is removed from the items only when what follows is a milk term, and its words are counted as set aside
    (never silently lost). Returns the number of words set aside."""
    words = 0
    for sec in parsed.sections:
        while len(sec.items) > 1:
            m = _PROVENANCE.match(sec.items[-1])
            row = _lookup(normalise_list([m.group(1)])[0].name) if m else None
            if not row or row["term"] not in _MILK_TERMS:
                break
            words += count_words(sec.items.pop())
    parsed.items = [i for sec in parsed.sections for i in sec.items]
    return words


def _outside_brackets(s: str) -> str:
    """The item without its bracketed contents ("Mixed spices (onion, cumin, ...)" -> "Mixed spices"): a long sub-list is not a long item."""
    prev = None
    while prev != s:
        prev, s = s, re.sub(r"[(\[{][^(\[{)\]}]*[)\]}]", "", s)
    return s


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
        if len(parts) < 4 or sum(len(_outside_brackets(x).split()) for x in parts) / len(parts) > 6:
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
    # Actual N08 second OCR inserts a stop before a combined, unplaced culture
    # phrase. Recognising the word as ingredient-like is NOT mapping its role or
    # placing probiotics. Never classify unread text; it only blocks Group1-3.
    if re.search(r"\bcultures?\b", seg, re.IGNORECASE):
        return True
    parts = split_items(seg)
    return len(parts) >= 2 or any(_recognisable(normalise_list([part])[0]) for part in parts)


def _split_amp_pair(raw: str) -> tuple[list[str], list[str]]:
    """An '&'- or 'and'-joined pair INSIDE a bracket ("Sprouted Ragi & Jowar (23.4%)", "Rice and Oat (22.3%)") becomes two items ONLY when each side is independently recognised WITH its shared modifier attached
    (a leading modifier of the left side applies to both: 'sprouted ragi' AND 'sprouted jowar', never bare 'jowar'). Anything else stays whole: an unrecognised side or modified form, a bracket
    other than a shared trailing percentage, more than two parts, or an unsupported connector. Culinary blends ('Corn and Canola Oil') and shared code lists stay whole.
    The shared percentage is NOT copied onto the items: it is returned as a note (the pair's context, not a measurement of each item). Preserves the actual connector in notes. A split of recognised-but-unplaced sides is recognition only: classification stays unresolved because those items still abstain."""
    parts, connectors = split_top_level_and_ex(raw)
    if len(parts) != 2 or len(connectors) != 1 or connectors[0].lower() not in ("&", "and"):
        return [raw], []
    if _shared_code_list(parts):
        return [raw], []
    left, right = parts
    pct = None
    m = re.fullmatch(r"(.*?)\s*\(\s*(\d+(?:\.\d+)?\s*%)\s*\)", right)
    if m:
        right, pct = m.group(1).strip(), re.sub(r"\s+", "", m.group(2))
    if not left or not right or re.search(r"[(\[{)\]}]", left + right):
        return [raw], []
    toks = left.split()
    mod = ""
    for k in range(1, len(toks)):                                  # smallest leading modifier whose removal leaves a recognised term
        if _recognisable(normalise_list([" ".join(toks[k:])])[0]):
            mod = " ".join(toks[:k])
            break
    right_full = f"{mod} {right}" if mod and not right.lower().startswith(mod.lower() + " ") else right
    if not (_recognisable(normalise_list([left])[0]) and _recognisable(normalise_list([right_full])[0])):
        return [raw], []
    if _names_two_oils([left, right_full]):
        return [raw], []
    conn = connectors[0]
    notes = []
    if mod:
        notes.append(f'"{mod}" was read as shared by both sides of "{left} {conn} {right}"')
    if pct:
        notes.append(f'The {pct} after "{left} {conn} {right}" applies to the pair, not to each item separately')
    return [left, right_full], notes


def _expand(items: list[tuple[str, str | None]], depth: int = 0, heads: list[str] | None = None, notes: list[str] | None = None) -> list[Ingredient]:
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
        split = split_compound(raw) if depth < 3 and not is_additive_absence_claim(raw) else None
        if split and len(split[1]) == 1 and is_colour_note(normalise_list([split[1][0]])[0].text):
            split = None          # "Annatto (colour)": a function note on a named food, not a colour ingredient: keep whole
        if split and not _recognisable(normalise_list([split[0]])[0]):
            if heads is not None:
                heads.append(split[0])          # the group name itself is not classified: keep it visible
            subs: list[str] = []
            for sub in split[1]:
                pieces, pair_notes = _split_amp_pair(sub)
                subs.extend(pieces)
                if notes is not None:
                    notes.extend(n for n in pair_notes if n not in notes)
            out.extend(_expand([(sub, section) for sub in subs], depth + 1, heads, notes))
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

    provenance_words = _strip_provenance(parsed)
    split = [[(raw, *_split_pairs_ex(raw)) for raw in sec.items] for sec in parsed.sections]
    sections = [(sec.label, [p for _, parts, _j in grp for p in parts]) for sec, grp in zip(parsed.sections, split)]
    items = [raw for _, its in sections for raw in its]
    joiners = sum(j for grp in split for _raw, _parts, j in grp)       # only the joiner words; any other word a split dropped stays "unaccounted"
    heads: list[str] = []
    amp_notes: list[str] = []
    ings = _expand([(raw, label) for label, its in sections for raw in its], heads=heads, notes=amp_notes)
    declared = _declared_additives(parsed.declarations, ings)
    unassessed = list(dict.fromkeys(
        [i.raw for i in ings if not _recognisable(i)]
        + [f"{h} (group name; its contents were assessed separately)" for h in heads]))
    unplaced = list(dict.fromkeys(
        [i.raw for i in ings if (_lookup(i.name) or {}).get("kind") == "unplaced"]
        + [name for i in ings for name in nested_unplaced(i)]))
    declaration_conflicts = [i for decl in parsed.declarations for i in normalise_list(split_items(re.sub(r"^contains?\s*:?[ ]*", "", decl, flags=re.IGNORECASE))) if any(u.class_conflict for u in i.ins)]
    uses = [u for i in ings + declaration_conflicts for u in i.ins]
    section_warnings = [f'"{it}" contains a colon, so a section label may not have been split from the ingredient before it'
                        for it in suspect_section_items(items)] + amp_notes
    section_warnings += [f'Milk composition declaration (not an added ingredient): "{seg}". No vitamin, added-solid or milk-fat ingredient was inferred.' for seg in parsed.composition]
    unread_like = [seg for seg in parsed.ignored if _looks_like_more_ingredients(seg)]
    unread_warnings = [f'Text after a full stop was not read as ingredients but looks like more of the list: "{_short(seg)}"'
                       for seg in unread_like]
    section_warnings += unread_warnings
    section_warnings += [f'"{i.raw}": a colour note on a named ingredient is not counted as an added colour' for i in ings if colour_note_only(i)]
    section_warnings += [f'"{i.raw}": the bracket names foods, so the word "sweeteners" is not counted as an added sweetener class' for i in ings if sweetener_foods_only(i)]
    section_warnings += [f'"{i.raw}": additive-absence wording is not treated as a positive ingredient or code declaration; the entry stays unresolved' for i in ings if is_additive_absence_claim(i.raw)]
    section_warnings += [f'"{i.raw}": declared class and local code mapping differ; codes remain visible, but marker evidence from this entry is not used' for i in ings + declaration_conflicts if any(u.class_conflict for u in i.ins)]
    section_warnings += _role_phrase_notes(ings)
    pct_suspects = [it for it in items if _SUSPECT_PCT.search(it)]
    section_warnings += [f'"{_short(it)}" has text after a percentage; a comma may be missing between two ingredients' for it in pct_suspects]
    implausible = source == "ocr" and _implausible(ings)
    if implausible:
        section_warnings.append("Few of the items were recognised, so this text may not be the ingredient list")
    misreads = _possible_misreads(ings)
    section_warnings += misreads
    if parsed.unbalanced_brackets:
        # No auto-close: any close point would be a guess. The text after the stray bracket stays together, in the item that holds it.
        section_warnings += [f'A bracket near "{snip}" was never closed, so the text after it was kept together as one item instead of being split (where it should close cannot be known)'
                             for it in items for snip in unclosed_openers(it)]
    common = dict(ingredients=items, ins_mappings=uses, warnings=list(section_warnings), unassessed=unassessed, unplaced=unplaced,
                  ignored=list(parsed.ignored), declared=declared, heading={"kind": parsed.heading_kind, "text": parsed.heading_text},
                  sections=[(label, list(its)) for label, its in sections])

    # Truncation: brackets left open, or the list runs off the end of the text
    # (no full stop / stop phrase) on a word we cannot recognise ("refined wheat flo").
    truncation = None
    vocab_last = False      # the list runs on and its last item is not in the vocabulary, but that item does not look cut off: a vocabulary gap, not a truncation
    if parsed.unbalanced_brackets:
        truncation = "ingredient list looks truncated (unclosed bracket)"
    elif not parsed.terminated and not _recognisable(ings[-1]):
        if _looks_cut_off(ings[-1]):
            truncation = f'ingredient list looks truncated (ends mid-word: "{items[-1]}")'
        else:
            vocab_last = True
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
    unaccounted = max(0, parsed.kept_words - in_list - not_read - provenance_words)
    reasons = []
    if source == "ocr" and parsed.heading_kind == "fuzzy":
        reasons.append(f'the heading was read as "{parsed.heading_text}": the photo may be cut off at the left edge')
    if source == "ocr" and parsed.heading_kind == "inferred":
        reasons.append('no "Ingredients" heading was found: the most list-like text block was used')
    if parsed.unbalanced_brackets:
        reasons.append("brackets are not balanced: text may be cut off or misread")
    if truncation:
        reasons.append("the list looks truncated")
    elif vocab_last:
        reasons.append("the last item is not in the local vocabulary")
    if unread_like:
        reasons.append("text after a full stop looks like more ingredients and was not read")
    if unaccounted:
        reasons.append(f"{unaccounted} word(s) after the heading were neither read as ingredients nor set aside")
    if suspect_section_items(items):
        reasons.append("a section label may not have been split from an ingredient")
    if pct_suspects:
        reasons.append("an item has text after a percentage: a comma may be missing between two ingredients")
    if implausible:
        reasons.append("few of the items were recognised: this text may not be an ingredient list")
    denom = in_list + not_read + unaccounted
    completeness = {
        "status": "uncertain" if reasons else "complete", "heading": parsed.heading_kind, "reasons": reasons,
        "list_share": round(in_list / denom, 3) if denom else 0.0,
        "words": {"region": parsed.region_words, "in_list": in_list, "declared": declared_w,
                  "excluded": max(0, parsed.tail_words - declared_w) + provenance_words, "not_read": not_read, "unaccounted": unaccounted},
        "assessed": {"items": len(ings), "not_assessed": sum(1 for i in ings if not _recognisable(i) or any(u.class_conflict for u in i.ins) or (_lookup(i.name) or {}).get("kind") == "unplaced" or nested_unplaced(i))}}
    if parsed.composition:
        composition_words = sum(count_words(x) for x in parsed.composition)
        completeness["words"]["composition"] = composition_words
        completeness["words"]["excluded"] -= composition_words
        section_warnings.append("Existing milk mappings may be PROVISIONAL: NOVA names milk, not each species or standardised class. The composition note supplies no new placement evidence; see full source evidence.")
        common["warnings"] = list(section_warnings)
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


ROTATIONS = ()                  # clockwise degrees to retry when no list was found. OFF: the measurement (evaluation/ocr_rotation_addendum) recovered 0 of 22 photos in the browser path; set (90, 270, 180) to enable
GOOD_ENOUGH_ITEMS = 3           # a rotated reading with at least this many recognised items stops the retries

RETAKE_GUIDANCE = ("No ingredient list could be read from this photo. Retake it: put the pack on a flat surface (or hold it still), use good even light with no glare "
                   "or shadow across the text, shoot straight-on and close so the ingredients panel fills the frame with the text upright. Or paste the label text instead.")


def analyse_image(path: str | Path, ocr: OcrEngine | None = None) -> Analysis:
    """Raises ocr.OcrUnavailable if the OCR backend cannot run (an error, not an abstention)."""
    result = _read_image(path, ocr or TesseractOcr())
    if not result.ingredients:
        result.retake = RETAKE_GUIDANCE      # no list read: tell the user how to retake the photo (never attached to a found list or to pasted text)
    return result


def _read_image(path, engine) -> Analysis:
    first = analyse_text(engine.extract_text(path), source="ocr")
    alt = getattr(engine, "extract_text_alt", None)
    clean = first.answered and first.completeness["status"] == "complete" and not first.ins_mappings
    if alt is None or clean:
        return first
    # One bounded second pass for photos that did not read cleanly, and for any reading that holds additive codes (digits are the
    # characters OCR confuses most). The better yield is kept; ties keep the first reading. Codes, section labels and extracted ingredient items are compared for review only.
    second = analyse_text(alt(path), source="ocr")
    chosen = second if _ocr_yield(second) > _ocr_yield(first) else first
    note = ocr_code_disagreement([u.code for u in first.ins_mappings], [u.code for u in second.ins_mappings])
    if note:
        chosen.warnings.append(note)
    items_differ = _reading_items(first) != _reading_items(second)
    if note or [s[0] for s in first.sections] != [s[0] for s in second.sections] or items_differ:
        chosen.reading_conflict = {
            "chosen": "second" if chosen is second else "first",
            "items_differ": items_differ,
            "selection": "Higher existing recognised-item yield; ties keep the first reading. Not chosen for code identity or classification group.",
            "readings": [{"label": label, "text": a.extracted_text,
                "sections": [sec[0] or "No section label" for sec in a.sections],
                "codes": sorted(set(u.code for u in a.ins_mappings)),
                "ingredients": list(a.ingredients),
                "heading": a.heading["kind"], "completeness": a.completeness["status"]}
                for label, a in (("first", first), ("second", second))]}
        chosen.warnings.append("Photo readings differ. The result uses the " + chosen.reading_conflict["chosen"] + " reading only; compare both readings with the pack. Text accounting does not prove correct characters or codes.")
    if not chosen.ingredients and ROTATIONS:
        chosen = _rotated_fallback(path, engine, chosen)
    return chosen


def _rotated_fallback(path, engine, chosen: Analysis) -> Analysis:
    """Fallback only when the readings so far found no ingredient list: the same OCR engine on the photo turned 90, 270, 180 degrees.
    A rotated reading is used only when it finds a list (yield above the current one); the first such reading with enough items stops the retries."""
    rotated = getattr(engine, "extract_text_rotated", None)
    if rotated is None:
        return chosen
    best, best_deg = chosen, 0
    for deg in ROTATIONS:
        a = analyse_text(rotated(path, deg), source="ocr")
        if _ocr_yield(a) > _ocr_yield(best):
            best, best_deg = a, deg
            if _ocr_yield(a) >= GOOD_ENOUGH_ITEMS:
                break
    if best_deg:
        best.warnings.append(f"The text was read after turning the photo {best_deg} degrees clockwise (sideways or upside-down text). Check the extracted ingredients against the pack.")
    return best


def _reading_items(a: Analysis) -> list[str]:
    """Review-only signatures. Ignore case/spacing/punctuation, not item order or digits.

    Never edit either reading or use this comparison to select or classify it.
    """
    return [re.sub(r"[^a-z0-9]+", " ", item.lower()).strip() for item in a.ingredients]


def ocr_code_disagreement(first: list[str], second: list[str]) -> str | None:
    """Two readings of the same photo that disagree on additive codes: a review hint. Neither reading is chosen for the codes and
    no alternative is used in classification."""
    a, b = sorted(set(first) - set(second)), sorted(set(second) - set(first))
    if not a and not b:
        return None
    return ("Two readings of the photo disagree on additive codes: " + ("INS " + ", INS ".join(a) if a else "none") + " in the first reading, "
            + ("INS " + ", INS ".join(b) if b else "none") + " in the second. Possible misread, check the pack.")


def _ocr_yield(a: Analysis) -> int:
    """Ingredients found minus those outside the vocabulary; 0 when no list was found."""
    return max(0, len(a.ingredients) - len(a.unassessed) - len(a.unplaced)) if a.ingredients else 0
