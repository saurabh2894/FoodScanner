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


def split_compound(raw: str) -> tuple[str, list[str]] | None:
    """Split "Seasoning (Sugar, Salt, Maltodextrin)" into ("Seasoning", [sub-items]).

    Returns None when the bracket holds no comma-separated list. An unclosed
    bracket (a printing slip seen on a real pack) runs to the end of the string.
    """
    idx = raw.find("(")
    if idx <= 0:
        return None
    depth, end = 0, len(raw)
    for i in range(idx, len(raw)):
        if raw[i] in _OPEN:
            depth += 1
        elif raw[i] in _CLOSE:
            depth -= 1
            if depth == 0:
                end = i
                break
    subs, _ = _split_top_level(raw[idx + 1:end])
    if len(subs) < 2:
        return None
    return raw[:idx].strip(" *"), subs
