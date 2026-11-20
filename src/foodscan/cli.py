"""Command-line entry point: the testable core. The web page calls the same pipeline."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .ocr import OcrUnavailable
from .pipeline import Analysis, analyse_image, analyse_text


def _where(d) -> str:
    return f" (section: {d.section})" if d.section else ""


def format_analysis(a: Analysis) -> str:
    lines = []
    if a.ingredients and any(label for label, _ in a.sections):
        lines.append("Ingredients found:")
        n = 0
        for label, items in a.sections:
            lines.append(f"  [{label or 'no section label'}]")
            for i in items:
                n += 1
                lines.append(f"  {n}. {i}")
    elif a.ingredients:
        lines.append("Ingredients found:")
        lines += [f"  {n}. {i}" for n, i in enumerate(a.ingredients, 1)]
    else:
        lines.append("Ingredients found: none")
    lines.append("")
    lines.append(a.headline)
    if a.answered:
        lines.append("Label-based NOVA classification from the ingredient text. It is not a safety or health finding about any ingredient or product.")
    for w in a.warnings:
        lines.append(f"Warning: {w}")
    if a.answered and a.drivers:
        lines.append("Driven by:")
        lines += [f"  - {d.ingredient}{_where(d)}: {d.detail}  [{d.source}]" for d in a.drivers]
    if not a.answered and a.drivers:
        lines.append("Weak evidence seen (not enough to decide):")
        lines += [f"  - {d.ingredient}{_where(d)}: {d.detail}" for d in a.drivers]
    c = a.completeness
    w = c["words"]
    lines.append(f"Completeness: {c['status']}. {w['in_list']} words read as ingredients ({round(c['list_share'] * 100)}% of the list region); "
                 f"{w['not_read']} not read, {w['unaccounted']} unaccounted, {w['excluded']} set aside after the list, {w['declared']} declared; "
                 f"{c['assessed']['not_assessed']} of {c['assessed']['items']} items outside the vocabulary."
                 + (" All recognised text spans accounted for. This is not a guarantee that characters, digits or the list are complete or correct."
                    if c["status"] == "complete" else ""))
    lines += [f"  - check: {r}" for r in c["reasons"]]
    if a.declared:
        lines.append("Declared on a 'Contains' line (counts as evidence; allergen statements are not shown):")
        lines += [f"  - {d['text']}  [{'also in the ingredient list' if d['in_list'] else 'NOT in the ingredient list'}]" for d in a.declared]
    if a.ignored:
        lines.append("Not read as ingredients (text after the list):")
        lines += [f"  - {t}" for t in a.ignored]
    if a.unassessed:
        lines.append("Not assessed (not in the vocabulary, or a group name whose contents were assessed):")
        lines += [f"  - {u}" for u in a.unassessed]
    if a.ins_mappings:
        lines.append("INS mappings used:")
        for u in a.ins_mappings:
            lines.append(f"  - INS {u.code} -> {u.name or '(not in local mapping)'}" + (f"  [{u.source}]" if u.source else ""))
            if u.name is None and u.ref_name:      # display only: it never decides a group
                lines.append(f"      {u.ref_name} (provisional name). Recognised code, no processing rule yet; classification treats it as unknown."
                             + (f" Source: {u.ref_url}" if u.ref_url else ""))
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="foodscan", description="Estimate NOVA processing level from a label photo.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("classify", help="classify one label photo")
    c.add_argument("path", help="image file (or text file with --text, '-' for stdin)")
    c.add_argument("--text", action="store_true", help="treat input as label text, skipping OCR")
    args = ap.parse_args(argv)

    try:
        if args.text:
            text = sys.stdin.read() if args.path == "-" else Path(args.path).read_text(encoding="utf-8")
            result = analyse_text(text, source="text")   # typed or file text: never blame OCR
        else:
            result = analyse_image(args.path)
    except OcrUnavailable as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(f"error: file not found: {exc.filename}", file=sys.stderr)
        return 2
    print(format_analysis(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
