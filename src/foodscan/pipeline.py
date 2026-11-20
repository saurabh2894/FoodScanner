"""photo -> OCR -> parse -> normalise -> classify -> abstention gate.

Single entry point shared by the CLI, the evaluation script and the web page.
Rule (CLAUDE.md): whenever evidence is weak the result is "Not enough information"
with a reason, never a guessed group.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .classify import Driver, _hits_for, classify_ingredients, is_recognised
from .normalise import Ingredient, InsUse, normalise_list
from .ocr import OcrEngine, TesseractOcr
from .parser import parse_ingredient_list

NOT_ENOUGH = "Not enough information"
GROUP_NAMES = {
    1: "unprocessed or minimally processed foods",
    2: "processed culinary ingredients",
    3: "processed foods",
    4: "ultra-processed foods",
}

MIN_CHARS = 20          # fewer non-space characters than this: OCR produced little text
MIN_ALPHA_RATIO = 0.5   # share of alphabetic characters; below this the text looks like noise


@dataclass
class Analysis:
    answered: bool
    group: int | None = None
    reason: str | None = None            # why we abstained
    ingredients: list[str] = field(default_factory=list)
    drivers: list[Driver] = field(default_factory=list)
    ins_mappings: list[InsUse] = field(default_factory=list)
    extracted_text: str = ""

    @property
    def headline(self) -> str:
        if self.answered:
            return f"NOVA group {self.group}: {GROUP_NAMES[self.group]}"
        return f"{NOT_ENOUGH}: {self.reason}"


def _abstain(reason: str, text: str, **kw) -> Analysis:
    return Analysis(answered=False, reason=reason, extracted_text=text, **kw)


def _recognisable(ing: Ingredient) -> bool:
    return is_recognised(ing.name) or bool(ing.ins) or bool(_hits_for(ing))


def analyse_text(text: str) -> Analysis:
    compact = re.sub(r"\s+", "", text)
    if len(compact) < MIN_CHARS:
        return _abstain("OCR produced little text", text)
    if sum(c.isalpha() for c in compact) / len(compact) < MIN_ALPHA_RATIO:
        return _abstain("extracted text looks like noise, not a readable label", text)

    parsed = parse_ingredient_list(text)
    if not parsed.found:
        return _abstain("no ingredient list found in the text", text)

    ings = normalise_list(parsed.items)
    uses = [u for i in ings for u in i.ins]
    common = dict(ingredients=parsed.items, ins_mappings=uses)

    # Truncation: brackets left open, or the list runs off the end of the text
    # (no full stop / stop phrase) on a word we cannot recognise ("refined wheat flo").
    if parsed.unbalanced_brackets:
        return _abstain("ingredient list looks truncated (unclosed bracket)", text, **common)
    if not parsed.terminated and not _recognisable(ings[-1]):
        return _abstain(
            f'ingredient list looks truncated (ends mid-word or unrecognised: "{parsed.items[-1]}")',
            text, **common)

    result = classify_ingredients(ings, parsed.declarations)
    if result.group is None:
        return _abstain(result.reason or "classification uncertain", text, drivers=result.drivers, **common)
    return Analysis(answered=True, group=result.group, drivers=result.drivers,
                    extracted_text=text, **common)


def analyse_image(path: str | Path, ocr: OcrEngine | None = None) -> Analysis:
    """Raises ocr.OcrUnavailable if the OCR backend cannot run (an error, not an abstention)."""
    engine = ocr or TesseractOcr()
    return analyse_text(engine.extract_text(path))
