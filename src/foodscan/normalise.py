"""Normalise raw ingredient strings.

Steps: extract INS / E numbers (both spellings), drop percentages, unify
spelling/plural variants through synonyms.csv, flatten hyphens, split the
name from bracketed detail. Every INS mapping used is reported with its source.
"""
from __future__ import annotations

import re
from functools import cache
from dataclasses import dataclass, field

from .tables import load_table

_CODE = r"\d{3,4}(?:\s*\(\s*[ivx]+\s*\))?(?:[a-z](?![a-z]))?"
# "INS 471", "E171", "e-171", "INS 500(ii), 503(ii)" (bare continuation codes)
_INS = re.compile(
    rf"(?<![a-z0-9])(?:ins|e)\s*[-:.]?\s*(?P<codes>{_CODE}(?:\s*(?:,|and|&|/)\s*{_CODE})*)",
)
_CODE_RE = re.compile(_CODE)


@dataclass(frozen=True)
class InsUse:
    code: str
    name: str | None      # None: code not in ins_map.csv
    source: str | None


@dataclass
class Ingredient:
    raw: str
    name: str                      # normalised text outside brackets
    inner: str                     # normalised text inside brackets
    ins: list[InsUse] = field(default_factory=list)

    @property
    def text(self) -> str:
        return f"{self.name} {self.inner}".strip()


def canonical_code(code: str) -> str:
    return re.sub(r"\s+", "", code.lower())


@cache
def _ins_map() -> dict[str, dict[str, str]]:
    return {canonical_code(r["ins"]): r for r in load_table("ins_map.csv")}


@cache
def _synonyms() -> list[tuple[re.Pattern, str]]:
    rows = sorted(load_table("synonyms.csv"), key=lambda r: -len(r["from"]))
    return [
        (re.compile(rf"(?<![a-z]){re.escape(r['from'].lower())}(?![a-z])"), r["to"].lower())
        for r in rows
    ]



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
            code = canonical_code(c)
            row = table.get(code)
            uses.append(InsUse(code, row["name"] if row else None, row["source"] if row else None))
        return " "

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
    return Ingredient(raw=raw, name=name, inner=inner, ins=uses)


def normalise_list(items: list[str]) -> list[Ingredient]:
    return [normalise_ingredient(i) for i in items]
