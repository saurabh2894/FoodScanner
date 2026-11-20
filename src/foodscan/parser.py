"""Locate the ingredient list in OCR text and split it into ingredients.

Structural facts only (no classification). Whether the list *looks truncated*
is decided in the pipeline, because it also needs the vocabulary; the parser
reports the structural evidence: was the list closed by a full stop or a
stop-phrase, and are brackets balanced.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

# English plus the Hindi headings common on Indian packs (research/02 "Indian label specifics").
_HEADING = re.compile(r"(?:ingredients?|सामग्री|अवयव)\s*[:\-–—]?\s*", re.IGNORECASE)

# Phrases that end the list. "contains" statements are kept separately (see below).
_STOP = re.compile(
    r"\b(?:may\s+contain|contains|allergen(?:s)?(?:\s+information)?|nutrition(?:al)?|"
    r"manufactured|manufacturer|mfd|marketed|packed\s+by|best\s+before|use\s+by|"
    r"net\s+(?:wt|weight|qty|quantity)|storage|store\s+in|fssai|customer\s+care)\b",
    re.IGNORECASE,
)

_OPEN, _CLOSE = "([{", ")]}"

# Packs often split the list into labelled sections after a full stop:
# "... Rice Bran Oil. Seasoning : Iodised Salt, ..." The section is still part of the ingredient
# list. Only these section labels are absorbed, so "Note: store cool." still ends the list.
_SECTION = re.compile(
    r"\s*(?:seasoning|coating|filling|topping|sauce|masala|dressing|marinade|glaze|base|premix|spice\s+mix|tadka|chutney)"
    r"(?:\s+(?:mix|powder|blend))?\s*:\s*", re.IGNORECASE)


@dataclass
class ParsedList:
    found: bool
    items: list[str] = field(default_factory=list)
    list_text: str = ""
    terminated: bool = False          # closed by full stop or stop-phrase
    unbalanced_brackets: bool = False
    declarations: list[str] = field(default_factory=list)  # "Contains ..." sentences after the list


def _collapse(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _split_top_level(text: str) -> tuple[list[str], bool]:
    """Split on commas/semicolons outside brackets. Returns (items, unbalanced)."""
    items, buf, depth = [], [], 0
    for ch in text:
        if ch in _OPEN:
            depth += 1
        elif ch in _CLOSE:
            depth = max(depth - 1, 0) if depth else 0
        if ch in ",;" and depth == 0:
            items.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    items.append("".join(buf))
    unbalanced = _bracket_depth(text) != 0
    return [i.strip(" .") for i in items if i.strip(" .")], unbalanced


def _bracket_depth(text: str) -> int:
    depth = 0
    for ch in text:
        if ch in _OPEN:
            depth += 1
        elif ch in _CLOSE:
            if depth == 0:
                return -1  # stray closer: also unbalanced
            depth -= 1
    return depth


def _find_terminator(text: str) -> int | None:
    """Index of the first full stop at bracket depth 0 that is not a decimal point."""
    depth = 0
    for i, ch in enumerate(text):
        if ch in _OPEN:
            depth += 1
        elif ch in _CLOSE:
            depth = max(depth - 1, 0)
        elif ch == "." and depth == 0:
            prev_digit = i > 0 and text[i - 1].isdigit()
            next_digit = i + 1 < len(text) and text[i + 1].isdigit()
            if not (prev_digit and next_digit):
                return i
    return None


def _join_sections(body: str) -> str:
    while True:
        end = _find_terminator(body)
        if end is None:
            return body
        m = _SECTION.match(body, end + 1)
        if not m:
            return body
        body = body[:end] + ", " + body[m.end():]


def parse_ingredient_list(text: str) -> ParsedList:
    flat = _collapse(text)
    m = _HEADING.search(flat)
    if not m:
        return ParsedList(found=False)
    body = flat[m.end():]

    terminated = False
    declarations: list[str] = []

    stop = _STOP.search(body)
    if stop:
        tail = body[stop.start():]
        body = body[: stop.start()]
        terminated = True
        # Keep "Contains ..." statements: they can declare additive classes
        # (e.g. "Contains added flavour") that are classification evidence.
        # "may contain" (allergen cross-contact) is not an ingredient declaration.
        if re.match(r"contains\b", tail, re.IGNORECASE):
            end = _find_terminator(tail)
            declarations.append(tail[:end] if end is not None else tail)

    body = _join_sections(body)
    end = _find_terminator(body)
    if end is None and _bracket_depth(body) > 0:
        # A bracket the pack never closes (seen on a real label) hides the full stop from the
        # depth-0 scan, so footnotes would be absorbed into the last ingredient. Fall back to
        # the first full stop that directly follows a closing bracket.
        m = re.search(r"[)\]}]\.(?=\s|$)", body)
        end = m.end() - 1 if m else None
    if end is not None:
        body = body[:end]
        terminated = True

    items, unbalanced = _split_top_level(body)
    if not items:
        return ParsedList(found=False)
    return ParsedList(
        found=True,
        items=items,
        list_text=body.strip(),
        terminated=terminated,
        unbalanced_brackets=unbalanced,
        declarations=declarations,
    )


def _bracket_groups(raw: str):
    """Yield (open_index, close_index_or_len, content) for each top-level bracket group."""
    i = 0
    while i < len(raw):
        if raw[i] in _OPEN:
            depth, end = 0, len(raw)
            for j in range(i, len(raw)):
                if raw[j] in _OPEN:
                    depth += 1
                elif raw[j] in _CLOSE:
                    depth -= 1
                    if depth == 0:
                        end = j
                        break
            yield i, end, raw[i + 1:end]
            i = end + 1
        else:
            i += 1


def split_compound(raw: str) -> tuple[str, list[str]] | None:
    """Split "Seasoning (Sugar, Salt, Maltodextrin)" into ("Seasoning", [sub-items]).

    Returns None when no bracket holds a comma-separated list. Brackets with no letters
    ("(57%)") are skipped, so "Base Mix(57%)(Ragi, Rice)" splits on the second one. An
    unclosed bracket (a printing slip seen on a real pack) runs to the end of the string.
    """
    for idx, end, content in _bracket_groups(raw):
        if not re.search(r"[A-Za-z]", content):
            continue
        if idx <= 0:
            return None
        subs, _ = _split_top_level(content)
        if len(subs) < 2:
            return None
        return raw[:idx].strip(" *"), subs
    return None
