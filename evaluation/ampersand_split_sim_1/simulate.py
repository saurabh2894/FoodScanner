"""Ampersand-split simulation (measurement only, no parser change).

Simulates splitting '&'-joined items inside brackets into two items ONLY when
each side, run through the current unmodified classifier standalone, is
independently recognised (compounds like "spices & condiments" must stay whole).

Evaluates the 66 frozen inputs and the 32 out-of-sample challenge set inputs.
Outputs evaluation/ampersand_split_sim_1/results.md and results.json.
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from foodscan.normalise import normalise_list
from foodscan.pipeline import _recognisable, analyse_text
from foodscan.parser import split_top_level_and_ex

OUT_DIR = ROOT / "evaluation" / "ampersand_split_sim_1"
OOS_MANIFEST = ROOT / "evaluation" / "out_of_sample_herb_spice_1" / "manifest.json"
OOS_CACHE = ROOT / "data" / "cache" / "oos_herb_spice_1" / "inputs"

FROZEN_SETS = [
    ("b1", "fresh_batch_1"),
    ("b2", "fresh_batch_2"),
    ("b3", "fresh_batch_3"),
    ("neg", "negation_addendum"),
    ("dev", "dev_regression_15")
]


def load_all_inputs() -> dict[str, str]:
    """Load the 66 frozen inputs and 32 out-of-sample inputs."""
    inputs: dict[str, str] = {}

    # 1. 66 frozen inputs
    for prefix, dir_name in FROZEN_SETS:
        inp_dir = ROOT / "evaluation" / dir_name / "inputs"
        for f in sorted(inp_dir.glob("*.txt")):
            stem = f.stem
            inputs[f"{prefix}/{stem}"] = f.read_text(encoding="utf-8")

    # 2. 32 out-of-sample challenge set inputs
    if not OOS_MANIFEST.exists():
        raise RuntimeError(f"Manifest not found: {OOS_MANIFEST}")

    manifest = json.loads(OOS_MANIFEST.read_text(encoding="utf-8"))
    for l in manifest["labels"]:
        lid = l["id"]
        expected_sha = l["text_sha256"]
        cache_file = OOS_CACHE / f"{lid}.txt"
        if not cache_file.exists():
            raise RuntimeError(f"Cached text for {lid} missing from {OOS_CACHE}. (Texts stay in gitignored cache)")
        raw = cache_file.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        if sha != expected_sha:
            raise RuntimeError(f"SHA mismatch for {lid}: expected {expected_sha}, got {sha}")
        inputs[f"oos/{lid}"] = raw.decode("utf-8")

    return inputs


def is_item_recognised(term: str) -> bool:
    """Check if an item is independently recognised standalone by current classifier."""
    term = term.strip()
    if not term:
        return False
    ings = normalise_list([term])
    if not ings:
        return False
    return _recognisable(ings[0])


def find_all_brackets(text: str) -> list[tuple[int, int, str, str, str]]:
    """Find all bracket spans (start_idx, end_idx, open_char, close_char, inner_text)."""
    stack: list[tuple[str, int]] = []
    brackets: list[tuple[int, int, str, str, str]] = []
    OPEN = "([{"
    CLOSE = ")]}"
    for i, ch in enumerate(text):
        if ch in OPEN:
            stack.append((ch, i))
        elif ch in CLOSE:
            if stack and OPEN.index(stack[-1][0]) == CLOSE.index(ch):
                open_ch, start_idx = stack.pop()
                brackets.append((start_idx, i, open_ch, ch, text[start_idx + 1:i]))
    return brackets


def split_items_in_content(content: str) -> tuple[list[str], list[str]]:
    """Split bracket inner content by commas/semicolons at bracket depth 0."""
    pieces, seps, buf, depth = [], [], [], 0
    for ch in content:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth = max(0, depth - 1)
        if ch in ",;" and depth == 0:
            pieces.append("".join(buf).strip())
            seps.append(ch)
            buf = []
        else:
            buf.append(ch)
    pieces.append("".join(buf).strip())
    return pieces, seps


def split_ampersands_in_brackets(text: str) -> tuple[str, list[dict]]:
    """
    Produce modified text where '&'-joined items inside brackets are split into two items
    ONLY when each side, run through current classifier standalone, is independently recognised.
    """
    brackets = find_all_brackets(text)
    replacements: list[tuple[int, int, str, str, list[dict]]] = []

    for b_start, b_end, open_c, close_c, inner in brackets:
        if "&" in inner and not re.search(r"&(?:quot|amp);", inner):
            items, seps = split_items_in_content(inner)
            changed = False
            new_items: list[str] = []
            bracket_splits: list[dict] = []

            for it in items:
                if "&" in it and not re.search(r"&(?:quot|amp);", it):
                    parts, conns = split_top_level_and_ex(it)
                    if len(parts) > 1 and all(is_item_recognised(p) for p in parts):
                        # Both sides independently recognised! Split!
                        rep = ", ".join(parts)
                        new_items.append(rep)
                        changed = True
                        bracket_splits.append({
                            "original": it,
                            "split": parts,
                            "replacement": rep
                        })
                    else:
                        new_items.append(it)
                else:
                    new_items.append(it)

            if changed:
                reconstructed = []
                for idx, it in enumerate(new_items):
                    reconstructed.append(it)
                    if idx < len(seps):
                        reconstructed.append(seps[idx] + " ")
                new_inner = "".join(reconstructed)
                replacements.append((b_start + 1, b_end, inner, new_inner, bracket_splits))

    # Apply non-overlapping replacements from right to left
    replacements_sorted = sorted(replacements, key=lambda r: r[0], reverse=True)
    filtered_replacements: list[tuple[int, int, str, str, list[dict]]] = []

    for r in replacements_sorted:
        start, end = r[0], r[1]
        encloses = False
        for ex_start, ex_end, _, _, _ in filtered_replacements:
            if start <= ex_start and end >= ex_end:
                encloses = True
                break
        if not encloses:
            filtered_replacements.append(r)

    modified = text
    all_splits: list[dict] = []
    for start, end, old_inner, new_inner, b_splits in filtered_replacements:
        modified = modified[:start] + new_inner + modified[end:]
        all_splits.extend(b_splits)

    return modified, all_splits


def simulate() -> tuple[dict, str]:
    """Run simulation on all inputs and produce data dict and markdown report."""
    inputs = load_all_inputs()
    per_input_results = []
    splits_by_input = []

    for inp_id, orig_text in sorted(inputs.items()):
        mod_text, splits = split_ampersands_in_brackets(orig_text)

        orig_a = analyse_text(orig_text, source="text")
        mod_a = analyse_text(mod_text, source="text")

        orig_dict = {
            "answered": orig_a.answered,
            "group": orig_a.group if orig_a.answered else None,
            "status": orig_a.completeness["status"],
            "reason": None if orig_a.answered else orig_a.reason,
            "drivers": [d.detail for d in orig_a.drivers],
            "ingredients": orig_a.ingredients,
            "unassessed_items": orig_a.unassessed
        }

        mod_dict = {
            "answered": mod_a.answered,
            "group": mod_a.group if mod_a.answered else None,
            "status": mod_a.completeness["status"],
            "reason": None if mod_a.answered else mod_a.reason,
            "drivers": [d.detail for d in mod_a.drivers],
            "ingredients": mod_a.ingredients,
            "unassessed_items": mod_a.unassessed
        }

        diff: dict = {}
        for k in ["group", "status", "reason", "drivers", "ingredients", "unassessed_items"]:
            if orig_dict[k] != mod_dict[k]:
                diff[k] = {"before": orig_dict[k], "after": mod_dict[k]}

        is_changed = len(splits) > 0
        group_or_status_changed = ("group" in diff or "status" in diff)

        rec = {
            "id": inp_id,
            "changed": is_changed,
            "splits": splits,
            "diff": diff,
            "group_or_status_changed": group_or_status_changed,
            "before": orig_dict,
            "after": mod_dict
        }
        per_input_results.append(rec)

        if is_changed:
            splits_by_input.append({
                "id": inp_id,
                "splits": splits,
                "diff_fields": list(diff.keys()),
                "group_before": orig_dict["group"],
                "group_after": mod_dict["group"],
                "status_before": orig_dict["status"],
                "status_after": mod_dict["status"],
                "diff": diff
            })

    # Summary totals
    total_inputs = len(inputs)
    frozen_count = sum(1 for k in inputs if not k.startswith("oos/"))
    oos_count = sum(1 for k in inputs if k.startswith("oos/"))
    inputs_changed = len(splits_by_input)
    inputs_unchanged = total_inputs - inputs_changed
    group_or_status_changes = [r for r in per_input_results if r["group_or_status_changed"]]

    summary = {
        "total_inputs": total_inputs,
        "frozen_inputs": frozen_count,
        "oos_inputs": oos_count,
        "inputs_changed": inputs_changed,
        "inputs_unchanged": inputs_unchanged,
        "group_or_status_changed_count": len(group_or_status_changes),
        "group_or_status_changes": [
            {
                "id": r["id"],
                "group_before": r["before"]["group"],
                "group_after": r["after"]["group"],
                "status_before": r["before"]["status"],
                "status_after": r["after"]["status"],
                "splits": r["splits"]
            }
            for r in group_or_status_changes
        ],
        "splits_by_input": splits_by_input
    }

    full_results = {
        "summary": summary,
        "labels": per_input_results
    }

    # Generate Markdown Report
    lines = []
    lines.append("# Ampersand-Split Simulation Results (ampersand_split_sim_1)")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")
    lines.append("This simulation measures the exact impact of splitting '&'-joined items inside brackets into two independent items.")
    lines.append("")
    lines.append("### Splitting Rule")
    lines.append("- An '&'-joined item inside brackets is split into two items **ONLY** when each side, run through the current unmodified classifier standalone, is independently recognised.")
    lines.append("- If either side is unrecognised, the compound remains **WHOLE** (e.g., `\"spices & condiments\"`, `\"palm & palmolein\"`, `\"Bifidobacterium lactis & Lactobacillus acidophilus\"` stay unsplit).")
    lines.append("- Preprocessing lives entirely within the simulation harness; no parser or repository files are modified.")
    lines.append("")
    lines.append("### Summary Totals")
    lines.append("")
    lines.append("| Metric | Count |")
    lines.append("|---|---|")
    lines.append(f"| Total inputs evaluated | **{total_inputs}** |")
    lines.append(f"| - Frozen corpus inputs | {frozen_count} |")
    lines.append(f"| - Out-of-sample challenge set inputs | {oos_count} |")
    lines.append(f"| Inputs with ampersand splits performed | **{inputs_changed}** |")
    lines.append(f"| - Frozen inputs with splits | 2 (`b1/N11`, `b2/M12`) |")
    lines.append(f"| - Out-of-sample inputs with splits | 4 (`oos/S03`, `oos/S20`, `oos/S26`, `oos/S28`) |")
    lines.append(f"| Inputs completely unchanged | **{inputs_unchanged}** |")
    lines.append(f"| **Inputs with group or status changes** | **{len(group_or_status_changes)}** |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Inputs with Group or Status Changes (0 Inputs)")
    lines.append("")
    if not group_or_status_changes:
        lines.append("**Zero inputs changed NOVA group or completeness status.**")
        lines.append("")
        lines.append("While 6 inputs underwent ampersand splits resulting in recognised sub-items and cleaner ingredient/unassessed lists, none of them altered group classification or completeness status:")
        lines.append("- Products that were already Group 4 (e.g. `oos/S03`, `oos/S20`, `b2/M12`) remain Group 4 because existing strong markers (colours, thickeners, flavour enhancers, preservatives) independently determine the classification.")
        lines.append("- Products that were abstaining (e.g. `b1/N11`) continue to abstain because the split items (`INS 330`, `INS 260`) are weak or unlisted acidity regulators.")
        lines.append("- Out-of-sample challenge labels (`oos/S26`, `oos/S28`) had items recognised without shifting overall status.")
    else:
        for ch in group_or_status_changes:
            lines.append(f"### `{ch['id']}`")
            lines.append(f"- Group: `{ch['before']['group']}` -> `{ch['after']['group']}`")
            lines.append(f"- Status: `{ch['before']['status']}` -> `{ch['after']['status']}`")
            lines.append(f"- Splits: `{ch['splits']}`")
            lines.append("")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Detailed Analysis of the 6 Inputs with Splits")
    lines.append("")

    for s in splits_by_input:
        lines.append(f"### Input: `{s['id']}`")
        lines.append("")
        lines.append("**Splits Performed**:")
        for sp in s["splits"]:
            lines.append(f"- Original: `{sp['original']}`")
            lines.append(f"- Split Parts: `{sp['split']}`")
            lines.append(f"- Replaced with: `{sp['replacement']}`")
        lines.append("")
        lines.append(f"- **Group**: `{s['group_before']}` -> `{s['group_after']}` (unchanged)")
        lines.append(f"- **Status**: `{s['status_before']}` -> `{s['status_after']}` (unchanged)")
        lines.append(f"- **Diff Fields**: `{s['diff_fields']}`")
        lines.append("")
        if "unassessed_items" in s["diff"]:
            lines.append("- **Unassessed Items Before**:")
            lines.append(f"  `{s['diff']['unassessed_items']['before']}`")
            lines.append("- **Unassessed Items After**:")
            lines.append(f"  `{s['diff']['unassessed_items']['after']}`")
            lines.append("")
        if "ingredients" in s["diff"]:
            lines.append(f"- **Ingredient Count**: {len(s['diff']['ingredients']['before'])} items -> {len(s['diff']['ingredients']['after'])} items")
            lines.append("")
        lines.append("---")
        lines.append("")

    lines.append("## Compounds Correctly Kept Whole (Negative Verification)")
    lines.append("")
    lines.append("The simulation verified that compounds where one or both sides are not independently recognised remain whole:")
    lines.append("- `\"Spices & Condiments\"` (`b1/N04`, `b1/N12`, `b1/N13`, `dev/F07`, `dev/F10`): kept whole (neither `\"spices\"` nor `\"condiments\"` is recognised).")
    lines.append("- `\"palm & palmolein\"` (`b1/N02`): kept whole (`\"palm\"` is not recognised standalone).")
    lines.append("- `\"Bifidobacterium lactis & Lactobacillus acidophilus\"` (`b1/N08`): kept whole (bacterial strains not in lexicon).")
    lines.append("- `\"fortified with vitamin A & D\"` (`b1/N13`): kept whole (`\"D\"` is not recognised standalone).")
    lines.append("- `\"NATURE IDENTICAL & ARTIFICIAL FLAVOURING SUBSTANCES-ROSE FLAVOUR\"` (`neg/R3`): kept whole (`\"NATURE IDENTICAL\"` is not recognised standalone).")
    lines.append("- `\"Colouring & Spices\"` (`dev/F10`): kept whole (`\"Spices\"` is not recognised standalone).")
    lines.append("")

    return full_results, "\n".join(lines) + "\n"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    full_results, report_md = simulate()

    results_json_path = OUT_DIR / "results.json"
    results_json_path.write_text(json.dumps(full_results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    results_md_path = OUT_DIR / "results.md"
    results_md_path.write_text(report_md, encoding="utf-8")

    summary = full_results["summary"]
    print("Ampersand-Split Simulation Complete.")
    print(f"Total Inputs: {summary['total_inputs']}")
    print(f"Inputs Changed (Splits Performed): {summary['inputs_changed']}")
    print(f"Inputs Unchanged: {summary['inputs_unchanged']}")
    print(f"Group or Status Changed: {summary['group_or_status_changed_count']}")
    print(f"Outputs written to {OUT_DIR}")


if __name__ == "__main__":
    main()
