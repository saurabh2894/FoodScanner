"""Locate the ingredient list in text and split it into ingredients, keeping section boundaries.

Structural facts only (no classification). Whether the list *looks truncated*
is decided in the pipeline, because it also needs the vocabulary; the parser
reports the structural evidence: was the list closed by a full stop or a
stop-phrase, and are brackets balanced.

A full stop is NOT the end of the list by itself. Labels often split a list into sections
("Noodles: ... . Masala tastemaker: ..."), and a line break can do the same. After a full stop the
list continues when the next text starts with a section label ("Label:", at most four words), unless
the label names non-ingredient text (Note, Directions, ...). Unlabelled text after a full stop still
ends the list, as do the stop phrases (Contains, Allergen, Manufactured, Best before, Nutrition, ...).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import cache

from .tables import load_table

# English plus the Hindi headings common on Indian packs (research/02 "Indian label specifics").
_HEADING = re.compile(r"(?:ingredient[s5]?|सामग्री|अवयव)\s*[:\-–—]?\s*", re.IGNORECASE)
_HEADING_WORDS = ("ingredients", "ingredient")
_OCR_DIGITS = str.maketrans("5103", "sioe")      # digits OCR often puts where letters are


def _lev(a: str, b: str) -> int:
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def _heading_like(tok: str) -> bool:
    """A damaged "INGREDIENTS": cropped at an edge ("REDIENTS", "INGREDIEN") or off by up to two OCR letters."""
    t = tok.lower().translate(_OCR_DIGITS)
    if len(t) < 6:
        return False
    if any(w.endswith(t) or w.startswith(t) for w in _HEADING_WORDS):
        return True
    return len(t) >= 8 and any(_lev(t, w) <= 2 for w in _HEADING_WORDS)


_HEAD_QUALIFIER = re.compile(r"(?:^|[\s(])(?:active|inactive|cooking)\s*$", re.IGNORECASE)


def _heading_position_ok(norm: str, m: re.Match) -> bool:
    """The word must sit in heading position and form: at the start of the text, a line or a sentence, or followed by a colon or
    dash. "COOKING INGREDIENTS & MEALS" and "SYMEGA FOOD INGREDIENTS LTD." are text that merely contains the word."""
    before = norm[: m.start()]
    if _HEAD_QUALIFIER.search(before):
        return False                       # "Active ingredients:", "Cooking ingredients:"
    at_start = re.search(r"(?:^|\n)[\s*\u2022|\-]*$", before) is not None or re.search(r"[.!?]\s*$", before) is not None
    has_separator = re.search(r"[:\-\u2013\u2014]", m.group()) is not None
    return at_start or has_separator


def _find_heading(norm: str) -> tuple[int, str, str] | None:
    """(end of heading, kind, heading text). kind "exact", or "fuzzy" for a damaged heading. A fuzzy heading must
    sit at the start of a line or be followed by a colon or dash, so a look-alike word inside a sentence is not one."""
    for m in _HEADING.finditer(norm):
        if _heading_position_ok(norm, m):
            return m.end(), "exact", m.group().strip(" :-–—")
    for t in re.finditer(r"[A-Za-z0-9]{6,}", norm):
        if not _heading_like(t.group()) or t.group().lower() in _HEADING_WORDS:
            continue                       # the exact word was already judged by its position (_heading_position_ok)
        before, after = norm[: t.start()], norm[t.end():]
        if re.match(r"\s*[:\-–—]", after) or re.search(r"(?:^|\n)[\s*•\-]*$", before):
            end = t.end() + len(re.match(r"\s*[:\-–—]?\s*", after).group())
            return end, "fuzzy", t.group()
    return None

class _Cut:
    def __init__(self, i): self._i = i
    def start(self): return self._i


_NEG_CLAIM = re.compile(r"(?:^|[.\n])\s*((?:no|nil|without|free\s+from)\s+(?:added|artificial|preservatives?|colou?rs?|flavou?rs?|sweeteners?)\b)", re.IGNORECASE)

# Phrases that end the list. "contains" statements are kept separately (see below).
_STOP = re.compile(
    r"\b(?:may\s+contain|(?:does|do)\s+not\s+contain|contains|allergen(?:s)?(?:\s+information)?|nutrition(?:al)?|"
    r"manufactured|manufacturer|mfd|marketed|packed\s+by|best\s+before|use\s+by|"
    r"net\s+(?:wt|weight|qty|quantity)|storage|store\s+in|fssai|customer\s+care)\b",
    re.IGNORECASE,
)

_OPEN, _CLOSE = "([{", ")]}"

# What may sit between the end of the list and a stop phrase without being ingredients.
_LEAD_IN = re.compile(
    r"(?:^|[.\n])\s*((?:this\s+|the\s+|our\s+)?product|allerg(?:en|y)\s+advice|[A-Za-z][A-Za-z &'\u2019/\-]{0,40}:)\s*$",
    re.IGNORECASE)

# "Label:" at the start of a section: 1 to 4 words, then a colon, then more text.
_LABEL = re.compile(
    r"\s*(?P<label>[A-Za-z][A-Za-z&'\u2019/\-]*(?:[ ][A-Za-z&'\u2019/\-]+){0,3})"
    r"(?P<qual>\s*\([A-Za-z][A-Za-z ]{0,18}\))?"
    r"(?:\s+(?P<pct>\d+(?:\.\d+)?\s*%)|\s*\(\s*(?P<pctb>\d+(?:\.\d+)?\s*%)\s*\))?\s*:\s*(?=\S)")
# Labels that introduce non-ingredient text: the list ends before them.
_DENY = re.compile(
    r"(?:notes?|directions?|instructions?|cooking instructions|preparation|how to \w+(?: \w+)?|"
    r"serving suggestions?|warning|caution|tips?|usage|mrp|price|address|batch(?: no)?)", re.IGNORECASE)
_ADDITIVE_CLASSES = {"cosmetic_additive", "ordinary_additive", "unlisted_additive"}


@dataclass
class Section:
    label: str | None      # e.g. "Noodles", "Masala tastemaker"; None when the list has no label
    items: list[str]


@dataclass
class ParsedList:
    found: bool
    items: list[str] = field(default_factory=list)       # all sections, flat
    list_text: str = ""
    terminated: bool = False          # closed by full stop or stop-phrase
    unbalanced_brackets: bool = False
    declarations: list[str] = field(default_factory=list)  # "Contains ..." sentences after the list
    sections: list[Section] = field(default_factory=list)
    # Text after the list that was NOT read as ingredients (unlabelled text after a full stop). Never dropped
    # silently: it is kept here so the result can show it and, if it looks like more ingredients, say so.
    ignored: list[str] = field(default_factory=list)
    heading_kind: str = "none"        # exact / fuzzy (damaged heading) / assumed (pasted list, no heading) / inferred (set by the pipeline)
    heading_text: str = ""
    region_words: int = 0             # words after the heading
    kept_words: int = 0               # of those, words in the part kept as the list region (before any stop phrase)
    tail_words: int = 0               # words set aside after the list: stop-phrase tail and its lead-in


def _flat(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[-\u2013\u2014_/]", " ", s.lower())).strip()


@cache
def _class_word_re() -> re.Pattern:
    terms = sorted({r["term"].lower() for r in load_table("markers.csv") if r["marker_class"] in _ADDITIVE_CLASSES},
                   key=len, reverse=True)
    return re.compile(r"(?<![a-z])(?:" + "|".join(re.escape(t) for t in terms) + r")(?:s|ing|ings)?(?![a-z])")


@cache
def _lexicon_terms() -> frozenset:
    return frozenset(_flat(r["term"]) for r in load_table("lexicon.csv"))


def _label_info(seg: str) -> tuple[str, int, bool] | None:
    """If `seg` starts with a section label: (label, offset where the content starts, strip_label).

    Not a label: non-ingredient labels (Note, Directions, ...), labels that are themselves a recognised
    food, and labels followed by a digit or bracket ("Rice: 60%"). A label that contains an additive class
    word ("Colour:", "Sweetener:") continues the list but is kept in the text, so its marker is not lost.
    """
    m = _LABEL.match(seg)
    if not m:
        return None
    label = m.group("label").strip()
    if _DENY.fullmatch(label):
        return None
    if not seg[m.end():m.end() + 1].isalpha():
        return None
    flat = _flat(label)
    if flat in _lexicon_terms():
        return None
    shown = label + (" " + m.group("qual").strip() if m.group("qual") else "")                 # "Sprinkler Mix (Topping)"
    pct = m.group("pct") or m.group("pctb")
    shown += " " + re.sub(r"\s+", "", pct) if pct else ""                                        # "Seasoning 12%", "Noodles (88.5%):" -> "Noodles 88.5%"
    return shown, m.end(), not _class_word_re().search(flat)


@cache
def _marker_terms() -> frozenset:
    return frozenset(_flat(r["term"]) for r in load_table("markers.csv"))


def _known_phrase(flat: str) -> bool:
    return flat in _lexicon_terms() or flat in _marker_terms()


_LABEL_WORD = re.compile(r"[A-Za-z&'\u2019/\-]+")


def _colon_at_depth0(item: str) -> int:
    depth = 0
    for i, ch in enumerate(item):
        if ch in _OPEN:
            depth += 1
        elif ch in _CLOSE:
            depth = max(depth - 1, 0)
        elif ch == ":" and depth == 0:
            return i
    return -1


def _peel_label(item: str) -> tuple[str, str, str] | None:
    """Split an item where a section label sits on the same line as the ingredient before it.

    "Rice Bran Oil Seasoning : Onion" -> ("Rice Bran Oil", "Seasoning", "Onion"). The label is the
    last 1 to 4 words before the colon, and what precedes it must be a recognised ingredient (longest
    recognised prefix wins). If the prefix is not recognised nothing is guessed: the item is left whole
    (and flagged by suspect_section_items).
    """
    colon = _colon_at_depth0(item)
    if colon <= 0:
        return None
    left, rest = item[:colon], item[colon + 1:].strip()
    if not rest[:1].isalpha():
        return None
    pct = ""
    mp = re.search(r"\s+(\d+(?:\.\d+)?\s*%)\s*$", left) or re.search(r"\s*\(\s*(\d+(?:\.\d+)?\s*%)\s*\)\s*$", left)
    if mp:
        pct, left = re.sub(r"\s+", "", mp.group(1)), left[:mp.start()]
    words = left.split()
    for k in range(len(words) - 1, 0, -1):
        label_words = words[k:]
        if len(label_words) > 4 or not all(_LABEL_WORD.fullmatch(w) for w in label_words):
            continue
        label = " ".join(label_words)
        flat = _flat(label)
        if _DENY.fullmatch(label) or flat in _lexicon_terms() or _class_word_re().search(flat):
            continue
        prefix = " ".join(words[:k])
        if _known_phrase(_flat(prefix)):
            return prefix, label + (" " + pct if pct else ""), rest
    return None


def suspect_section_items(items: list[str]) -> list[str]:
    """Items that still contain a colon at depth 0 after splitting: a section label may be glued in.
    Items whose pre-colon text holds an additive class word ("Colour : INS 150d") are not suspect."""
    out = []
    for it in items:
        c = _colon_at_depth0(it)
        if c > 0 and not _class_word_re().search(_flat(it[:c])):
            out.append(it)
    return out


def _normalise_ws(text: str) -> str:
    """Collapse spaces but KEEP line breaks (they can separate sections)."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out = "\n".join(re.sub(r"[ \t\u00a0]+", " ", ln).strip() for ln in lines)
    return re.sub(r"\n{2,}", "\n", out).strip()


def count_words(text: str) -> int:
    return len(re.findall(r"[^\W_]+", text))


def _collapse(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


_CODE_ITEM = re.compile(r"^(?:(?:ins|e)\s*[-:.]?\s*)?\d{3,4}[a-z]?(?:\([ivxl]+\))*$", re.IGNORECASE)
# "NAME (22%) {a, b, c}": a percentage then a bracket holding letters, ending the chunk
_PCT_GROUP = re.compile(r"\(\s*\d+(?:\.\d+)?\s*%\s*\)\s*[\[{(].*[A-Za-z].*[\]})]\s*$")


def _split_top_level(text: str) -> tuple[list[str], bool]:
    """Split on commas/semicolons outside brackets. Returns (items, unbalanced).

    Two general rules on top of the plain split:
    - in a list whose groups are separated by semicolons, a chunk shaped "NAME, NAME (22%) {a, b}" keeps its commas: the
      percentage belongs to the group, so everything before it is the group's name ("Dry Fruits, Nuts & Seeds");
    - an item that is only an additive code ("E1450", "INS 415") continues the previous item's code list
      ("thickeners - E1442, E1450")."""
    pieces, seps, buf, depth = [], [], [], 0
    for ch in text:
        if ch in _OPEN:
            depth += 1
        elif ch in _CLOSE:
            depth = max(depth - 1, 0) if depth else 0
        if ch in ",;" and depth == 0:
            pieces.append("".join(buf))
            seps.append(ch)
            buf = []
        else:
            buf.append(ch)
    pieces.append("".join(buf))
    if ";" in seps:
        merged, cur = [], [pieces[0]]
        for sep, piece in zip(seps, pieces[1:]):
            if sep == ";":
                merged.append(cur)
                cur = [piece]
            else:
                cur.append(piece)
        merged.append(cur)
        pieces = []
        for chunk in merged:
            head = chunk[:-1]
            if len(chunk) >= 2 and _PCT_GROUP.search(chunk[-1]) and all(not re.search(r"[(\[{]", p) for p in head) \
                    and sum(len(p.split()) for p in head) <= 6:
                pieces.append(",".join(chunk))
            else:
                pieces.extend(chunk)
    items: list[str] = []
    for p in pieces:
        p = p.strip(" .")
        if not p:
            continue
        if items and _CODE_ITEM.match(p):
            items[-1] += ", " + p
        else:
            items.append(p)
    return items, _bracket_depth(text) != 0


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


def _next_boundary(body: str, start: int) -> tuple[int, str]:
    """First section boundary at bracket depth 0 after `start`: ("stop" = full stop, "break" = line
    break before a section label) or (len(body), "end")."""
    depth = 0
    for i in range(start, len(body)):
        ch = body[i]
        if ch in _OPEN:
            depth += 1
        elif ch in _CLOSE:
            depth = max(depth - 1, 0)
        elif depth == 0:
            if ch == ".":
                prev_digit = i > 0 and body[i - 1].isdigit()
                next_digit = i + 1 < len(body) and body[i + 1].isdigit()
                if not (prev_digit and next_digit):
                    return i, "stop"
            elif ch == "\n" and _label_info(body[i + 1:]) is not None:
                return i, "break"
    if depth > 0:
        # A bracket the pack never closes (seen on a real label) hides the full stop from the depth-0
        # scan, so footnotes would be absorbed into the last ingredient. Fall back to the first full
        # stop that directly follows a closing bracket.
        m = re.search(r"[)\]}]\.(?=\s|$)", body[start:])
        if m:
            return start + m.end() - 1, "stop"
    return len(body), "end"


def _read_sections(body: str) -> tuple[list[tuple[str | None, str]], bool, str]:
    """Cut the body into (label, text) sections. Returns (sections, ended_by_full_stop, unread_text)."""
    sections: list[tuple[str | None, str]] = []
    pos, ended, unread = 0, False, ""
    while True:
        info = _label_info(body[pos:])
        label, seg_start = None, pos
        if info:
            lab, off, strip = info
            if strip:
                label, seg_start = lab, pos + off
                while True:             # "Seasoning: Masala Mix: ...": a second label right after the first names the same section
                    nxt = _label_info(body[seg_start:])
                    if not nxt or not nxt[2]:
                        break
                    label, seg_start = f"{label}: {nxt[0]}", seg_start + nxt[1]
        end, kind = _next_boundary(body, seg_start)
        sections.append((label, body[seg_start:end]))
        if kind == "end":
            break
        if kind == "break":
            pos = end + 1
            continue
        rest = body[end + 1:]
        if not rest.strip() or _label_info(rest) is None:
            ended = True            # trailing full stop, or unlabelled text after it: the list is over
            unread = rest.strip()   # whatever follows is kept, not dropped
            break
        pos = end + 1
    return sections, ended, unread


_ALLERGEN_LABEL = re.compile(r"^(?:allerg(?:en|y)[a-z ]*|note)\s*:\s*", re.IGNORECASE)


def _contains_sentences(tail: str) -> list[str]:
    """The "Contains ..." sentences of the text after the list: sentences end at a full stop outside brackets or at a
    line break; a leading "Allergen information:" label is dropped; "May contain" does not match."""
    out, buf, depth = [], [], 0
    for i, ch in enumerate(tail):
        if ch in _OPEN:
            depth += 1
        elif ch in _CLOSE:
            depth = max(depth - 1, 0)
        is_stop = (ch == "." and depth == 0 and not (i > 0 and tail[i - 1].isdigit() and i + 1 < len(tail) and tail[i + 1].isdigit()))
        if is_stop or (ch == "\n" and depth == 0):
            out.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    out.append("".join(buf))
    found = []
    for seg in out:
        found.extend(_positive_spans(_ALLERGEN_LABEL.sub("", _collapse(seg))))
    return found


# One keyword at a time: a NEGATOR opens a negated span, "contains" opens a positive one, "may contain" opens a span that is never read.
_POLARITY = re.compile(
    r"(?P<maybe>\bmay\s+contain\b)"
    r"|(?P<neg>\b(?:does\s+not\s+contain|do\s+not\s+contain|contains?\s+(?:no|nil|none|without)|free\s+(?:from|of)|without|nil|none|no|not)\b)"
    r"|(?P<pos>\bcontains?\b)", re.IGNORECASE)


def _positive_spans(seg: str) -> list[str]:
    """A sentence that opens with "contains" or a negator is read as alternating spans. Only the POSITIVE spans are declarations
    ("Contains <span>"): "Contains no added flavours, added colour or preservatives" declares nothing; "No added colours, contains
    preservative (INS 211)" declares the preservative only; "free from nuts" is never a driver in either direction. Scoped to the
    span, never to the whole line or input."""
    ms = list(_POLARITY.finditer(seg))
    if not ms or ms[0].start() != 0 or ms[0].group("maybe"):
        return []
    out = []
    for k, m in enumerate(ms):
        if not m.group("pos"):
            continue
        end = ms[k + 1].start() if k + 1 < len(ms) else len(seg)
        text = seg[m.end():end].strip(" ,;:-")
        if text:
            out.append(m.group(0) + " " + text)          # the label's own keyword and casing
    return out


def unclosed_openers(text: str) -> list[str]:
    """Snippets (from the opening bracket, 45 characters) of brackets that are opened and never closed."""
    stack = []
    for i, ch in enumerate(text):
        if ch in _OPEN:
            stack.append(i)
        elif ch in _CLOSE and stack:
            stack.pop()
    return [re.sub(r"\s+", " ", text[max(0, i - 15): i + 45]).strip() for i in stack]


def split_top_level_and(raw: str) -> list[str]:
    """Split "a and b" / "a & b" at bracket depth 0. Always returns at least [raw]; whether both sides are really
    ingredients is for the caller to decide (it needs the vocabulary)."""
    return split_top_level_and_ex(raw)[0]


def split_top_level_and_ex(raw: str) -> tuple[list[str], list[str]]:
    """As split_top_level_and, also returning the connector text that was removed ("and", "&")."""
    cuts, depth = [], 0
    for m in re.finditer(r"[(\[{)\]}]|\s+(?:and|&)\s+", raw, re.IGNORECASE):
        tok = m.group()
        if tok in _OPEN:
            depth += 1
        elif tok in _CLOSE:
            depth = max(depth - 1, 0)
        elif depth == 0:
            cuts.append((m.start(), m.end()))
    parts, last, connectors = [], 0, []
    for a, b in cuts:
        parts.append(raw[last:a].strip())
        connectors.append(raw[a:b].strip())
        last = b
    parts.append(raw[last:].strip())
    keep = [p for p in parts if p]
    return (keep, connectors) if len(keep) > 1 and len(keep) == len(parts) else ([raw], [])


def parse_ingredient_list(text: str, *, assume_list: bool = False) -> ParsedList:
    norm = _normalise_ws(text)
    found = _find_heading(norm)
    if found:
        body, heading_kind, heading_text = norm[found[0]:], found[1], found[2]
    elif assume_list:
        body, heading_kind, heading_text = norm, "assumed", ""      # pasted text with no heading: the whole text is the list
    else:
        return ParsedList(found=False)

    terminated = False
    declarations: list[str] = []
    region_words = count_words(body)

    stop = _STOP.search(body)
    claim = _NEG_CLAIM.search(body)
    if claim and (not stop or claim.start(1) < stop.start()):
        stop = _Cut(claim.start(1))                 # "No added colours, ..." opening a sentence after the list: a claim, not an ingredient
    body_with_tail = body[stop.start():] if stop else ""
    if stop:
        tail = _collapse(body[stop.start():])
        # The stop phrase takes its own lead-in with it: a label right before it ("Note: store in ...") or a
        # claim opener ("THIS PRODUCT contains ..."), so those fragments are not left behind as unread text.
        lead = _LEAD_IN.search(body[: stop.start()])
        body = body[: lead.start(1) if lead else stop.start()]
        terminated = True
        # "Contains ..." statements can declare additive classes (e.g. "Contains added flavour"): classification
        # evidence. Every such sentence in the text after the list is kept, not only the first one. "May contain"
        # (allergen cross-contact) is never a declaration.
        declarations = _contains_sentences(body_with_tail)

    kept_words = count_words(body)
    raw_sections, ended, unread = _read_sections(body)
    terminated = terminated or ended
    ignored = [_collapse(unread)] if unread else []

    sections: list[Section] = []
    items: list[str] = []
    unbalanced = False
    for label, content in raw_sections:
        its, unb = _split_top_level(_collapse(content))
        unbalanced = unbalanced or unb
        cur_label, cur = label, []
        for it in its:
            peeled = _peel_label(it)
            if peeled:                          # "Rice Bran Oil Seasoning : Onion": a new section starts mid-line
                prefix, lab, rest = peeled
                cur.append(prefix)
                sections.append(Section(cur_label, cur))
                items.extend(cur)
                cur_label, cur = lab, [rest]
            else:
                cur.append(it)
        if cur:
            sections.append(Section(cur_label, cur))
            items.extend(cur)
    if not items:
        return ParsedList(found=False)
    return ParsedList(
        found=True,
        items=items,
        list_text=_collapse(body),
        terminated=terminated,
        unbalanced_brackets=unbalanced,
        declarations=declarations,
        sections=sections,
        ignored=ignored,
        heading_kind=heading_kind,
        heading_text=heading_text,
        region_words=region_words,
        kept_words=kept_words,
        tail_words=region_words - kept_words,
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


def starts_with_denied_label(seg: str) -> bool:
    """True for text that opens with a non-ingredient label such as "Note:" or "Directions:"."""
    m = _LABEL.match(seg)
    return bool(m) and bool(_DENY.fullmatch(m.group("label").strip()))


def split_items(text: str) -> list[str]:
    return _split_top_level(_collapse(text))[0]
