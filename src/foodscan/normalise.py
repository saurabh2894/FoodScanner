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
    terms = sorted({r["term"].lower() for r in load_table("markers.csv") if r["marker_class"] in _ADDITIVE_CLASSES},
                   key=len, reverse=True)
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


def _make_use(code: str, table: dict) -> "InsUse":
    row = table.get(code)
    if not row:
        ref = _ins_reference().get(code)
        if ref:
            return InsUse(code, None, None, ref_name=ref["name"], ref_partial=ref["reading"].startswith("partial"),
                          ref_classes=tuple(c.strip() for c in ref["functional_classes"].split(";") if c.strip()))
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
    """Display-only Codex data. NOT SHIPPED while its licence is unresolved (data/pending/, research/05): the table is
    read only if src/foodscan/resources/ins_reference.csv exists, so a release without the file simply shows nothing."""
    from .tables import has_table
    if not has_table("ins_reference.csv"):
        return {}
    return {canonical_code(r["ins"]): r for r in load_table("ins_reference.csv")}


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


def extract_ins(text: str) -> tuple[str, list[InsUse]]:
    """Return (text with INS references removed, mapped INS uses)."""
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


def normalise_ingredient(raw: str) -> Ingredient:
    text, uses = extract_ins(raw)
    text = re.sub(r"\d+(?:\.\d+)?\s*%", " ", text)
    text = _apply_synonyms(text)
    text = flatten(text)
    name, inner = _split_brackets(text)
    return Ingredient(raw=raw, name=name, inner=inner, ins=[replace(u, ingredient=raw) for u in uses])


def normalise_list(items: list[str]) -> list[Ingredient]:
    return [normalise_ingredient(i) for i in items]
