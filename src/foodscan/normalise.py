"""Normalise raw ingredient strings.

Steps: extract INS / E numbers (both spellings), drop percentages, unify
spelling/plural variants through synonyms.csv, flatten hyphens, split the
name from bracketed detail. Every INS mapping used is reported with its source.
"""
from __future__ import annotations

import re
from functools import cache
from dataclasses import dataclass, field, replace

from .tables import load_table

_CODE = r"\d{3,4}(?:\s*\(\s*[ivx]+\s*\))?(?:[a-z](?![a-z]))?"
# "INS 471", "E171", "e-171", "INS 500(ii), 503(ii)" (bare continuation codes)
_INS = re.compile(
    rf"(?<![a-z0-9])(?:ins|e)\s*[-:.]?\s*(?P<codes>{_CODE}(?:\s*(?:,|and|&|/)\s*{_CODE})*)",
)
_CODE_RE = re.compile(_CODE)


_ADDITIVE_CLASSES = {"cosmetic_additive", "ordinary_additive", "unlisted_additive"}


@cache
def _bare_codes_re() -> re.Pattern:
    """"Flavour Enhancers (627, 631)": codes with no INS/E prefix, but only right after an
    additive class word taken from markers.csv, so "Salt (500)" is never read as a code."""
    classes = {r["term"].lower() for r in load_table("markers.csv") if r["marker_class"] in _ADDITIVE_CLASSES}
    # Existing direct class aliases only. Do not rewrite the input or extend mappings.
    aliases = {r["from"].lower() for r in load_table("synonyms.csv") if r["to"].lower() in classes}
    terms = sorted(classes | aliases, key=len, reverse=True)
    alt = "|".join(re.escape(t) for t in terms)
    return re.compile(
        rf"(?<![a-z])(?:{alt})(?:s|ing|ings)?(?:\s+of\s+[a-z]+(?:\s+[a-z]+){{0,2}})?\s*[(\[{{]\s*(?P<codes>{_CODE}(?:\s*(?:,|and|&|/)\s*{_CODE})*)\s*[)\]}}]")


@dataclass(frozen=True)
class InsUse:
    code: str
    name: str | None      # None: code not in ins_map.csv
    source: str | None
    classes: tuple[str, ...] = ()      # functional classes from the table ("emulsifier"); () when unknown
    strength: str | None = None        # decision strength from the table: strong / weak / weak_specific / unlisted
    ingredient: str | None = None      # the raw ingredient text the code was found in
    section: str | None = None         # list section that ingredient belongs to, if any
    # Display only (ins_reference.csv, Codex CXG 36 2026): for a code absent from ins_map.csv. It never feeds a decision;
    # the code still counts as "not in local mapping" and cannot decide a group.
    ref_name: str | None = None
    ref_classes: tuple[str, ...] = ()
    ref_partial: bool = False
    ref_source: str | None = None
    # Declared role (roles.py): the class the SCANNED label names for the entry this code sits in ("Acidity Regulator (INS 330)" -> acidity regulator).
    # Read from the label text only, never from the code. Display only: it never feeds a decision.
    declaration_only: bool = False  # positive statement outside the ingredient list
    entry_conflict: bool = False  # another code in this same declaration may disagree
    declared: str | None = None            # the label's own wording for the entry
    declared_roles: tuple[str, ...] = ()   # canonical roles read from it; () when the label names no class

    @property
    def class_conflict(self) -> bool:
        # A mismatch with this limited local mapping, not proof a role is impossible.
        return self.entry_conflict or bool(self.classes and self.declared_roles and not set(self.classes).intersection(self.declared_roles))

    @property
    def role_notes(self) -> list[str]:
        if self.class_conflict:
            return [f'This entry declares {" & ".join(self.declared_roles)}, but at least one code has a different class in this project mapping. The mismatch is unresolved, not proof the label is wrong or that a code has no other function. No marker evidence from this entry is used.']
        return role_notes(self.declared_roles, self.declared or "")

    @property
    def role_label(self) -> str | None:
        return role_label(self.declared_roles)

    @property
    def ref_url(self) -> str | None:
        m = re.search(r"https?://\S+", self.ref_source or "")
        return m.group(0) if m else None


from .roles import declared_roles as _declared_roles, label_phrase, role_label, role_notes  # noqa: E402


def _make_use(code: str, table: dict) -> "InsUse":
    row = table.get(code)
    if not row:
        ref = _ins_reference().get(code)
        if ref:
            return InsUse(code, None, None, ref_name=ref["name"], ref_partial=(ref.get("reading") or "").startswith("partial"),
                          ref_classes=tuple(c.strip() for c in (ref.get("functional_classes") or "").split(";") if c.strip()),
                          ref_source=ref.get("source"))
        return InsUse(code, None, None)
    classes = tuple(c.strip() for c in (row.get("functional_class") or "").split(";") if c.strip())
    return InsUse(code, row["name"], row["source"], classes, row["strength"])


@dataclass
class Ingredient:
    raw: str
    name: str                      # normalised text outside brackets
    inner: str                     # normalised text inside brackets
    ins: list[InsUse] = field(default_factory=list)
    section: str | None = None     # label of the list section it came from ("Masala tastemaker"), if any

    @property
    def text(self) -> str:
        return f"{self.name} {self.inner}".strip()


def canonical_code(code: str) -> str:
    return re.sub(r"\s+", "", code.lower())


@cache
def _ins_map() -> dict[str, dict[str, str]]:
    return {canonical_code(r["ins"]): r for r in load_table("ins_map.csv")}


@cache
def _ins_reference() -> dict[str, dict[str, str]]:
    """Display-only names (ins_names.csv): "Recognised code, no processing rule yet". They never feed a decision. The bulk Codex
    table stays parked in data/pending/ (licence and edition unresolved, research/05)."""
    return {canonical_code(r["ins"]): r for r in load_table("ins_names.csv")}


@cache
def _synonyms() -> list[tuple[re.Pattern, str]]:
    rows = sorted(load_table("synonyms.csv"), key=lambda r: -len(r["from"]))
    def boundary(term: str) -> tuple[str, str]:
        # a term that starts or ends with a digit ("0il", "o11") must not match inside a longer alphanumeric run
        return ("(?<![a-z0-9])" if term[0].isdigit() else "(?<![a-z])",
                "(?![a-z0-9])" if term[-1].isdigit() else "(?![a-z])")

    out = []
    for r in rows:
        term = r["from"].lower()
        left, right = boundary(term)
        # an alias for a "... dal" term also absorbs a following "dal" ("bengal gram dal" -> "chana dal", not "chana dal dal")
        tail = r"(?:\s+dal(?![a-z]))?" if r["to"].lower().endswith(" dal") and not term.endswith(" dal") else ""
        # target-safe rewrite (engine-fixes-1): an alias that is a strict word-prefix of its OWN target absorbs the remaining target words when they follow, so the canonical name is never
        # rewritten twice ("bok choy" -> "bok choy cabbage" must leave "bok choy cabbage" alone, not make "bok choy cabbage cabbage")
        to_flat = flatten(r["to"])
        if to_flat.startswith(term + " "):
            tail = r"(?:\s+" + re.escape(to_flat[len(term) + 1:]).replace(r"\ ", r"\s+") + r"(?![a-z]))?"
        out.append((re.compile(f"{left}{re.escape(term)}{right}{tail}"), r["to"].lower()))
    return out



def flatten(text: str) -> str:
    """Lowercase, hyphens/slashes to spaces, collapse whitespace."""
    text = re.sub(r"[-–—_/]", " ", text.lower())
    return re.sub(r"\s+", " ", text).strip()


def _apply_synonyms(text: str) -> str:
    for pat, to in _synonyms():
        text = pat.sub(to, text)
    return text


def _split_brackets(text: str) -> tuple[str, str]:
    outside, inside, depth = [], [], 0
    for ch in text:
        if ch in "([{":
            depth += 1
            inside.append(" ")
        elif ch in ")]}":
            depth = max(depth - 1, 0)
            inside.append(" ")
        elif depth:
            inside.append(ch)
        else:
            outside.append(ch)
    clean = lambda parts: re.sub(r"\s+", " ", "".join(parts)).strip(" ,;.:")
    return clean(outside), clean(inside)


@cache
def _additive_claim_class_re() -> re.Pattern:
    classes = {r["term"].lower() for r in load_table("markers.csv") if r["marker_class"] in _ADDITIVE_CLASSES}
    aliases = {r["from"].lower() for r in load_table("synonyms.csv") if r["to"].lower() in classes}
    alt = "|".join(re.escape(t) for t in sorted(classes | aliases, key=len, reverse=True))
    return re.compile(r"(?<![a-z])(?:" + alt + r")(?:s|ing|ings)?(?![a-z])")


def is_additive_absence_claim(raw: str) -> bool:
    """An item claiming an additive is absent is not positive ingredient evidence.

    Keep the item visible and unresolved, rather than asserting a plain-food group.
    Only claim-leading or claim-trailing wording is covered, not food conditions.
    """
    low = raw.lower().strip(" ,;:.")
    if not (re.match(r"^(?:no|not|without|free\s+(?:from|of)|does\s+not\s+contain|do\s+not\s+contain)\b", low)
            or re.search(r"\b(?:free|absent|not\s+(?:added|used|present))$", low)):
        return False
    return bool(_additive_claim_class_re().search(low))


def extract_ins(text: str) -> tuple[str, list[InsUse]]:
    """Return (text with INS references removed, mapped INS uses)."""
    if is_additive_absence_claim(text):
        return text.lower(), []
    table = _ins_map()
    uses: list[InsUse] = []
    low = text.lower()

    def repl(m: re.Match) -> str:
        for c in _CODE_RE.findall(m.group("codes")):
            uses.append(_make_use(canonical_code(c), table))
        return " "

    def repl_bare(m: re.Match) -> str:
        # keep the class word, drop only the bracketed codes
        for c in _CODE_RE.findall(m.group("codes")):
            uses.append(_make_use(canonical_code(c), table))
        return m.group(0)[: m.start("codes") - m.start(0)].rstrip("([{ \t") + " "

    low = _bare_codes_re().sub(repl_bare, low)
    stripped = _INS.sub(repl, low)
    # tidy brackets emptied by the removal, e.g. "emulsifier ( )"
    for _ in range(3):
        stripped = re.sub(r"[(\[{]\s*[,;/&]*\s*[)\]}]", " ", stripped)
    return stripped, uses


# A footnote mark is removed only where it sits at a well-defined boundary of an item or sub-item: the end of the text, before a closing bracket, a comma, semicolon, colon or full stop, before an opening
# bracket (a percentage or sub-list follows), before '&' or the connector words 'and' / 'or'. A mark inside a multi-word phrase ("Rice# Flour", "Sunflower<closing quote> Oil", "Skimmed<closing quote> Milk Powder")
# is NOT a footnote: removing it would join separate words into a phrase that was never written, so the text is left untouched and abstains as before. The raw input is never changed.
_FOOT_MARKS = r"(?:#{1,3}|\*{1,3}|[\u2020\u2021]|\u201D)"
_FOOT_BOUNDARY = r"(?=\s*(?:$|[)\]},;:.]|&|\(|\b(?:and|or)\b))"
_FOOTNOTE_RE = re.compile(r"(?<=[a-zA-Z0-9)\]}])\s*" + _FOOT_MARKS + _FOOT_BOUNDARY, re.UNICODE)
_FOOTNOTE_NO_QUOTE_RE = re.compile(r"(?<=[a-zA-Z0-9)\]}])\s*(?:#{1,3}|\*{1,3}|[\u2020\u2021])" + _FOOT_BOUNDARY, re.UNICODE)


def strip_footnotes(text: str) -> str:
    """Narrow removal of footnote marks (#, ##, *, **, dagger, double dagger and the observed OCR closing quote U+201D) at item, sub-item, connector, percentage and bracket boundaries only (see above).
    A text that holds a quoted phrase (an opening and a closing quote) keeps its closing quote."""
    if "\u201D" in text and ("\u201C" in text or '"' in text):
        return _FOOTNOTE_NO_QUOTE_RE.sub("", text)
    return _FOOTNOTE_RE.sub("", text)


def normalise_ingredient(raw: str) -> Ingredient:
    text, uses = extract_ins(raw)
    text = re.sub(r"\d+(?:\.\d+)?\s*%", " ", text)
    text = strip_footnotes(text)
    text = _apply_synonyms(text)
    text = flatten(text)
    name, inner = _split_brackets(text)
    name = strip_footnotes(name)
    inner = strip_footnotes(inner)
    roles = _declared_roles(name)
    phrase = label_phrase(raw) if roles else None
    uses = [replace(u, ingredient=raw, declared=phrase, declared_roles=roles) for u in uses]
    if any(u.class_conflict for u in uses):
        uses = [replace(u, entry_conflict=True) for u in uses]
    return Ingredient(raw=raw, name=name, inner=inner, ins=uses)


def normalise_list(items: list[str]) -> list[Ingredient]:
    return [normalise_ingredient(i) for i in items]
