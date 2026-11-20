"""Declared role of an additive code: the class the SCANNED label itself names for the ingredient entry the code sits in.

Never a per-code assumption: the same code can be declared as different classes on different packs. A role is read only when the whole
outside-bracket text of the ingredient entry is a role phrase (class words plus filler such as "class II", "permitted", "natural").
The wording about what a role means for Group 4 comes from declared_roles.csv and cites the NOVA method text that was read (FAO 2019).
Display only: nothing here feeds a classification."""
from __future__ import annotations

import re
from functools import cache

from .tables import load_table

_FILLER = {"contains", "contain", "permitted", "natural", "synthetic", "artificial", "nature", "identical", "added", "food", "class", "i", "ii", "iii",
           "1", "2", "substance", "substances", "and", "&", "the", "of"}


@cache
def _roles() -> list[tuple[re.Pattern, dict]]:
    rows = sorted(load_table("declared_roles.csv"), key=lambda r: -len(r["term"]))
    return [(re.compile(r"(?<![a-z])" + re.escape(r["term"]) + r"s?(?![a-z])"), r) for r in rows]


def declared_roles(name: str) -> tuple[str, ...]:
    """Canonical roles when the ingredient's outside-bracket text (normalised) is only role words and filler; else ()."""
    text = re.sub(r"[,;&/]", " ", name.lower())
    found: list[str] = []
    for pat, row in _roles():
        m = pat.search(text)
        if m:
            found.append(row["role"])
            text = text[:m.start()] + " " + text[m.end():]
    left = [t for t in re.findall(r"[a-z0-9]+", text) if t not in _FILLER]
    if left or not found:
        return ()
    return tuple(dict.fromkeys(found))


def label_phrase(raw: str) -> str:
    """The label's own wording for the entry: the raw text outside brackets, without a leading 'Contains'."""
    out, depth = [], 0
    for ch in raw:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth = max(depth - 1, 0)
        elif not depth:
            out.append(ch)
    s = re.sub(r"\s+", " ", "".join(out)).strip(" ,;.:*-")
    return re.sub(r"^contains\s*:?\s*", "", s, flags=re.IGNORECASE).strip()


@cache
def _marker_patterns() -> list[tuple[re.Pattern, str]]:
    flat = lambda t: re.sub(r"\s+", " ", re.sub(r"[-–—_/]", " ", t.lower())).strip()
    return [(re.compile(r"(?<![a-z])" + re.escape(flat(r["term"])) + r"(?![a-z])"), r["strength"]) for r in load_table("markers.csv")]


def _counted_as_marker(role: str) -> bool:
    """True when this tool's marker table counts the class word as a strong marker (same patterns classify uses on the label text)."""
    text = re.sub(r"[-–—_/]", " ", role.lower())
    return any(p.search(text) and strength == "strong" for p, strength in _marker_patterns())


def _row(role: str) -> dict:
    return next(r for _, r in _roles() if r["role"] == role)


def role_notes(roles: tuple[str, ...], phrase: str) -> list[str]:
    """Role-scoped sentences for a code whose label declares a class. Empty when no class is declared (the bare wording stays)."""
    if not roles:
        return []
    notes = [f'Declared on the label as: "{phrase}".']
    if re.search(r"(?:emulsifying|stabili[sz]ing)\s+(?:&\s*)?(?:and\s+)?(?:stabili[sz]ing\s+)?agent", phrase, re.IGNORECASE):
        notes.append("That wording is mapped to the class by a provisional role-phrase mapping (no source names the phrase).")
    if len(roles) > 1:
        notes.append("The codes listed with it share this entry, so the label does not say which code has which of these roles.")
    for role in roles:
        r = _row(role)
        src = r["cite"]
        if r["nova_status"] == "group4_listed":
            counted = _counted_as_marker(role)
            notes.append(f"Declared as {role}: the NOVA source lists {r['source_wording']} among the additive classes of ultra-processed foods ({src}). "
                         + ("This tool counts that class on the label as a Group 4 marker." if counted else
                            "This tool does not count this class as a marker yet, so it leaves the result uncertain."))
        elif r["nova_status"] == "group3_allowed":
            notes.append(f"Declared as {role}: no Group 4 marker detected for this role per {src}: it is not among the additive classes the source says are used only in "
                         f"ultra-processed foods. The source says processed (Group 3) foods may contain such additives ({r['source_wording']}) and also mentions them in its "
                         "Group 4 definition, so this role does not by itself separate the groups.")
        else:
            counted = _counted_as_marker(role)
            notes.append(f"Declared as {role}: this class is not named in the NOVA source read ({src}); "
                         + ("this tool counts it as a marker on the basis of research/02, not of that source." if counted else "this tool does not use it to decide a group."))
    return notes


def role_label(roles: tuple[str, ...]) -> str | None:
    """Short pill text replacing the bare 'No decision rule' for a row whose label declares a class."""
    if not roles:
        return None
    return "Declared as " + " & ".join(roles)
