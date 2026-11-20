"""Evaluation rollup for frozen evaluation batches.

Reads frozen evaluation artifacts (SCORES.md) for fresh_batch_1 and fresh_batch_2
and prints / writes a consolidated, honest rollup.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ExtractionRow:
    mode: str
    list_found: str | None  # e.g. "15/15 labels", "7/13 (6 no list)"
    own_item: str | None    # e.g. "92/121", "77/94"
    merged: str | None
    split: str | None
    omitted: str | None
    additions: str | None


@dataclass
class ClassificationRow:
    mode: str
    correct_confident: str | None
    wrong_confident: str | None
    abstained: str | None
    extra_columns: dict[str, str]  # any other column in the table, e.g. "Without the 5 overlapping labels (9)"


@dataclass
class WarningRow:
    category: str
    details: str


@dataclass
class BatchRollup:
    name: str
    path: Path
    title: str
    metadata_lines: list[str]
    extraction_denominator: str | None
    extraction_table: list[ExtractionRow]
    extraction_notes: list[str]
    classification_denominator: str | None
    classification_table: list[ClassificationRow]
    classification_notes: list[str]
    other_sections: dict[str, list[str]]
    warnings_worked: list[str]
    warnings_not_worked: list[str]
    recorded_fields: dict[str, str]
    unrecorded_fields: list[str]
    tie_outs: list[str]


def parse_markdown_table(lines: list[str]) -> list[dict[str, str]]:
    """Parse a markdown pipe table into a list of dicts {col_header: cell_value}."""
    table_lines = [line.strip() for line in lines if line.strip().startswith("|") and line.strip().endswith("|")]
    if len(table_lines) < 2:
        return []

    # Parse header
    headers = [c.strip() for c in table_lines[0].strip("|").split("|")]
    # Check if second row is separator
    sep_row = [c.strip() for c in table_lines[1].strip("|").split("|")]
    if not all(re.match(r"^:?-+:?$", s) for s in sep_row):
        return []

    data_rows = []
    for line in table_lines[2:]:
        cols = [c.strip() for c in line.strip("|").split("|")]
        # Pad with empty string if row has fewer columns
        if len(cols) < len(headers):
            cols.extend([""] * (len(headers) - len(cols)))
        row_dict = {headers[i]: cols[i] for i in range(len(headers))}
        data_rows.append(row_dict)
    return data_rows


def extract_denominator_and_count(s: str) -> tuple[int, int] | None:
    """Extract (count, denom) from string like '92/121', '7/13 (6 no list)', '15/15 labels'."""
    m = re.search(r"(\d+)\s*/\s*(\d+)", s)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None


def extract_leading_int(s: str) -> int | None:
    """Extract leading integer from strings like '8 (all Group 4...)', '11', '0'."""
    m = re.match(r"^(\d+)", s.strip())
    if m:
        return int(m.group(1))
    return None


def parse_batch_scores(batch_dir: Path) -> BatchRollup:
    """Parse SCORES.md of a batch directory faithfully."""
    scores_path = batch_dir / "SCORES.md"
    if not scores_path.is_file():
        raise FileNotFoundError(f"Missing SCORES.md in {batch_dir}")

    text = scores_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    title = lines[0].lstrip("#").strip() if lines else ""

    # Split lines into sections based on ## headers
    sections: dict[str, list[str]] = {}
    current_sec = "__header__"
    sections[current_sec] = []

    for line in lines[1:]:
        if line.startswith("## "):
            current_sec = line.strip()
            sections[current_sec] = []
        else:
            sections[current_sec].append(line)

    header_lines = [ln.strip() for ln in sections.get("__header__", []) if ln.strip()]

    # Extract metadata line info
    extraction_denom_stated = None
    classification_denom_stated = None

    for ln in header_lines:
        if "Extraction denominator:" in ln:
            m = re.search(r"Extraction denominator:\s*([^.]+)", ln)
            if m:
                extraction_denom_stated = m.group(1).strip()
        if "Judged for classification:" in ln:
            m = re.search(r"Judged for classification:\s*([^.]+)", ln)
            if m:
                classification_denom_stated = m.group(1).strip()

    # Find Extraction section
    ext_sec_title = next((k for k in sections if "Extraction" in k), None)
    ext_rows: list[ExtractionRow] = []
    ext_notes: list[str] = []
    if ext_sec_title:
        ext_lines = sections[ext_sec_title]
        parsed_table = parse_markdown_table(ext_lines)
        for r in parsed_table:
            # Map column variations
            mode = r.get("Mode", "")
            list_found = r.get("List found in the right place")
            own_item = r.get("Own item, recognisable") or r.get("Own item")
            merged = r.get("Merged into another item") or r.get("Merged")
            split = r.get("Split into several") or r.get("Split")
            omitted = r.get("Omitted")
            additions = r.get("Additions (app items with no reference item)") or r.get("Additions")
            ext_rows.append(ExtractionRow(
                mode=mode,
                list_found=list_found,
                own_item=own_item,
                merged=merged,
                split=split,
                omitted=omitted,
                additions=additions,
            ))
        # Non-table lines
        for ln in ext_lines:
            s = ln.strip()
            if s and not s.startswith("|"):
                ext_notes.append(s)

    # Find Classification section
    cls_sec_title = next((k for k in sections if "Classification" in k), None)
    cls_rows: list[ClassificationRow] = []
    cls_notes: list[str] = []
    if cls_sec_title:
        cls_lines = sections[cls_sec_title]
        # In batch 2, the denominator might be in the section header: "Classification (14 judged labels...)"
        if not classification_denom_stated:
            m = re.search(r"Classification\s*\(([^)]+)\)", cls_sec_title)
            if m:
                classification_denom_stated = m.group(1).strip()

        parsed_cls = parse_markdown_table(cls_lines)
        for r in parsed_cls:
            mode = r.get("Mode", "")
            correct = r.get("Correct confident group") or r.get("Correct confident")
            wrong = r.get("Wrong confident group") or r.get("Wrong confident")
            abstained = r.get("Abstained")
            known_cols = {"Mode", "Correct confident group", "Correct confident", "Wrong confident group", "Wrong confident", "Abstained"}
            extra = {k: v for k, v in r.items() if k not in known_cols}
            cls_rows.append(ClassificationRow(
                mode=mode,
                correct_confident=correct,
                wrong_confident=wrong,
                abstained=abstained,
                extra_columns=extra,
            ))
        for ln in cls_lines:
            s = ln.strip()
            if s and not s.startswith("|"):
                cls_notes.append(s)

    # Uncertainty warnings section
    warn_sec_title = next((k for k in sections if "Did uncertainty warnings work?" in k), None)
    warnings_worked: list[str] = []
    warnings_not_worked: list[str] = []
    if warn_sec_title:
        warn_lines = sections[warn_sec_title]
        # In batch 2:
        # "Worked: paste M07... Did not work (extraction wrong...): paste M08... No wrong confident group resulted in any of them."
        # In batch 1:
        # "- Worked: paste N03..."
        # "- Did not work (extraction wrong...): paste N02..."
        full_warn_text = "\n".join(warn_lines)
        # Check if there are separate lines or inline
        worked_match = re.search(r"Worked:\s*([^\n]+(?:\n[^\n]+)*?)(?=(?:Did not work|$))", full_warn_text)
        did_not_work_match = re.search(r"Did not work(?:\s*\([^)]+\))?:\s*([^\n]+(?:\n[^\n]+)*)", full_warn_text)
        if worked_match:
            w_text = worked_match.group(1).strip()
            # Clean up leading list dash or whitespace
            warnings_worked.append(w_text.strip("- ").strip())
        if did_not_work_match:
            dnw_text = did_not_work_match.group(1).strip()
            warnings_not_worked.append(dnw_text.strip("- ").strip())

    # Other sections
    other_sections: dict[str, list[str]] = {}
    known_sec_titles = {ext_sec_title, cls_sec_title, warn_sec_title, "__header__"}
    for sec_name, s_lines in sections.items():
        if sec_name not in known_sec_titles:
            non_empty = [ln.strip() for ln in s_lines if ln.strip()]
            if non_empty:
                other_sections[sec_name] = non_empty

    # Recorded vs unrecorded analysis
    recorded_fields: dict[str, str] = {}
    unrecorded_fields: list[str] = []

    if ext_sec_title:
        recorded_fields["Extraction table"] = f"Recorded ({len(ext_rows)} rows)"
    else:
        unrecorded_fields.append("Extraction table")

    # Check split column
    has_split = any(r.split is not None for r in ext_rows)
    if has_split:
        recorded_fields["Extraction: Split into several"] = "Recorded"
    else:
        unrecorded_fields.append("Extraction: Split into several (not recorded in batch)")

    if cls_sec_title:
        recorded_fields["Classification table"] = f"Recorded ({len(cls_rows)} rows)"
    else:
        unrecorded_fields.append("Classification table")

    # Extra classification breakdown (e.g. without overlap)
    has_overlap_col = any("Without" in k for r in cls_rows for k in r.extra_columns)
    if has_overlap_col:
        recorded_fields["Classification: Without overlapping labels breakdown"] = "Recorded"
    else:
        unrecorded_fields.append("Classification: Without overlapping labels breakdown (not recorded in batch)")

    # Diagnostic / Hint / Time sections
    for sec_name in other_sections:
        clean_name = sec_name.lstrip("#").strip()
        recorded_fields[f"Section: {clean_name}"] = "Recorded"

    # Specific checks across batches
    if not any("Hint, disagreement and role-phrase" in k for k in other_sections):
        unrecorded_fields.append("Section: Hint, disagreement and role-phrase paths (not recorded in batch)")
    if not any("Added time of the second OCR reading" in k for k in other_sections):
        unrecorded_fields.append("Section: Added time of the second OCR reading (not recorded in batch)")

    # Tie-out checks
    tie_outs: list[str] = []

    # 1. Extraction items tie-out
    # Items: own_item + merged + omitted (+ split?) vs denominator
    for r in ext_rows:
        mode_label = r.mode.split("(")[0].strip()
        denom_info = extract_denominator_and_count(r.own_item or "")
        if denom_info:
            own_cnt, total_denom = denom_info
            merged_cnt = extract_leading_int(r.merged or "") or 0
            omitted_cnt = extract_leading_int(r.omitted or "") or 0
            split_cnt = extract_leading_int(r.split or "") if r.split is not None else 0

            # Does it sum to total_denom?
            sum_parts = own_cnt + merged_cnt + omitted_cnt
            # In batch 1 paste: 92 + 17 + 2(split) + 10(omitted) = 121
            if r.split is not None:
                sum_with_split = sum_parts + (split_cnt or 0)
                if sum_with_split == total_denom:
                    tie_outs.append(
                        f"Extraction items ({mode_label}): {own_cnt} own + {merged_cnt} merged + {split_cnt} split + {omitted_cnt} omitted = {sum_with_split}/{total_denom} (Ties out exactly)"
                    )
                else:
                    tie_outs.append(
                        f"Extraction items ({mode_label}): {own_cnt} own + {merged_cnt} merged + {omitted_cnt} omitted (+ split {split_cnt}) = {sum_with_split}/{total_denom} (Gap: {total_denom - sum_with_split})"
                    )
            else:
                if sum_parts == total_denom:
                    tie_outs.append(
                        f"Extraction items ({mode_label}): {own_cnt} own + {merged_cnt} merged + {omitted_cnt} omitted = {sum_parts}/{total_denom} (Ties out exactly)"
                    )
                else:
                    tie_outs.append(
                        f"Extraction items ({mode_label}): {own_cnt} own + {merged_cnt} merged + {omitted_cnt} omitted = {sum_parts}/{total_denom} (Gap: {total_denom - sum_parts})"
                    )
        else:
            tie_outs.append(f"Extraction items ({mode_label}): No valid fraction denominator found in '{r.own_item}'")

    # 2. Classification labels tie-out
    # Parse denominator from classification_denominator
    cls_denom_val = None
    if classification_denom_stated:
        m = re.search(r"(\d+)\s*(?:judged)?\s*labels?", classification_denom_stated)
        if m:
            cls_denom_val = int(m.group(1))

    for r in cls_rows:
        mode_label = r.mode.split("(")[0].strip()
        c_cnt = extract_leading_int(r.correct_confident or "") or 0
        w_cnt = extract_leading_int(r.wrong_confident or "") or 0
        a_cnt = extract_leading_int(r.abstained or "") or 0
        sum_cls = c_cnt + w_cnt + a_cnt
        if cls_denom_val is not None:
            if sum_cls == cls_denom_val:
                tie_outs.append(
                    f"Classification labels ({mode_label}): {c_cnt} correct + {w_cnt} wrong + {a_cnt} abstained = {sum_cls}/{cls_denom_val} (Ties out exactly)"
                )
            else:
                tie_outs.append(
                    f"Classification labels ({mode_label}): {c_cnt} correct + {w_cnt} wrong + {a_cnt} abstained = {sum_cls}/{cls_denom_val} (Gap: {cls_denom_val - sum_cls})"
                )
        else:
            tie_outs.append(
                f"Classification labels ({mode_label}): {c_cnt} correct + {w_cnt} wrong + {a_cnt} abstained = {sum_cls} (No explicit classification denominator stated)"
            )

    return BatchRollup(
        name=batch_dir.name,
        path=batch_dir,
        title=title,
        metadata_lines=header_lines,
        extraction_denominator=extraction_denom_stated,
        extraction_table=ext_rows,
        extraction_notes=ext_notes,
        classification_denominator=classification_denom_stated,
        classification_table=cls_rows,
        classification_notes=cls_notes,
        other_sections=other_sections,
        warnings_worked=warnings_worked,
        warnings_not_worked=warnings_not_worked,
        recorded_fields=recorded_fields,
        unrecorded_fields=unrecorded_fields,
        tie_outs=tie_outs,
    )


def generate_rollup_markdown(rollups: list[BatchRollup]) -> str:
    """Generate Markdown representation of the multi-batch rollup."""
    out: list[str] = []
    out.append("# Frozen Evaluation Rollup (fresh_batch_1 & fresh_batch_2)")
    out.append("")
    out.append("This document summarizes the hand-adjudicated frozen evaluation artifacts recorded in `evaluation/fresh_batch_1` and `evaluation/fresh_batch_2`. All figures and observations are read-only extractions from each batch's respective `SCORES.md` without modification, derivation, or re-computation.")
    out.append("")

    # Overview table
    out.append("## 1. Batch Summaries & Metadata")
    out.append("")
    out.append("| Batch | Title | Stated Extraction Denominator | Stated Classification Denominator |")
    out.append("|---|---|---|---|")
    for b in rollups:
        ext_d = b.extraction_denominator or "Not stated"
        cls_d = b.classification_denominator or "Not stated"
        out.append(f"| `{b.name}` | {b.title} | {ext_d} | {cls_d} |")
    out.append("")

    # Section for each batch
    for b in rollups:
        out.append(f"## 2. Batch: `{b.name}`")
        out.append(f"**Title**: {b.title}")
        out.append("")
        if b.metadata_lines:
            out.append("**Metadata & Notes:**")
            for m in b.metadata_lines:
                out.append(f"- {m}")
            out.append("")

        # Extraction
        out.append("### Extraction Outcomes (per batch record)")
        if b.extraction_table:
            has_split = any(r.split is not None for r in b.extraction_table)
            if has_split:
                out.append("| Mode | List Found | Own Item | Merged | Split | Omitted | Additions |")
                out.append("|---|---|---|---|---|---|---|")
                for r in b.extraction_table:
                    out.append(f"| {r.mode} | {r.list_found or 'not recorded'} | {r.own_item or 'not recorded'} | {r.merged or 'not recorded'} | {r.split or 'not recorded'} | {r.omitted or 'not recorded'} | {r.additions or 'not recorded'} |")
            else:
                out.append("| Mode | List Found | Own Item | Merged | Split | Omitted | Additions |")
                out.append("|---|---|---|---|---|---|---|")
                for r in b.extraction_table:
                    out.append(f"| {r.mode} | {r.list_found or 'not recorded'} | {r.own_item or 'not recorded'} | {r.merged or 'not recorded'} | not recorded | {r.omitted or 'not recorded'} | {r.additions or 'not recorded'} |")
            out.append("")
        else:
            out.append("*No extraction table recorded.*")
            out.append("")

        if b.extraction_notes:
            out.append("**Extraction Notes & Failure Splits:**")
            for note in b.extraction_notes:
                out.append(f"- {note}")
            out.append("")

        # Classification
        out.append("### Classification Outcomes (abstentions are their own outcome)")
        if b.classification_table:
            extra_col_names = []
            for r in b.classification_table:
                for k in r.extra_columns:
                    if k not in extra_col_names:
                        extra_col_names.append(k)

            hdr = ["Mode", "Correct Confident", "Wrong Confident", "Abstained"] + extra_col_names
            out.append("| " + " | ".join(hdr) + " |")
            out.append("| " + " | ".join(["---"] * len(hdr)) + " |")
            for r in b.classification_table:
                row_vals = [
                    r.mode,
                    r.correct_confident or "not recorded",
                    r.wrong_confident or "not recorded",
                    r.abstained or "not recorded",
                ]
                for extra in extra_col_names:
                    row_vals.append(r.extra_columns.get(extra, "not recorded"))
                out.append("| " + " | ".join(row_vals) + " |")
            out.append("")
        else:
            out.append("*No classification table recorded.*")
            out.append("")

        if b.classification_notes:
            out.append("**Classification Notes:**")
            for note in b.classification_notes:
                out.append(f"- {note}")
            out.append("")

        # Uncertainty warnings
        out.append("### Uncertainty Warning Effectiveness")
        if b.warnings_worked or b.warnings_not_worked:
            if b.warnings_worked:
                out.append("- **Worked:** " + "; ".join(b.warnings_worked))
            else:
                out.append("- **Worked:** not recorded")
            if b.warnings_not_worked:
                out.append("- **Did not work:** " + "; ".join(b.warnings_not_worked))
            else:
                out.append("- **Did not work:** not recorded")
            out.append("")
        else:
            out.append("- *Uncertainty warning effectiveness not recorded in this batch.*")
            out.append("")

        # Other sections unique to this batch
        if b.other_sections:
            out.append("### Batch-Specific Additional Sections")
            for sec_name, sec_lines in b.other_sections.items():
                clean_sec = sec_name.lstrip("#").strip()
                out.append(f"#### {clean_sec}")
                for ln in sec_lines:
                    out.append(f"- {ln}")
                out.append("")

        # Recorded vs Unrecorded
        out.append("### Recorded vs. Unrecorded Inventory")
        out.append("**Recorded Fields & Sections:**")
        for k, v in b.recorded_fields.items():
            out.append(f"- {k}: {v}")
        out.append("")
        out.append("**Not Recorded in this Batch:**")
        for u in b.unrecorded_fields:
            out.append(f"- {u}")
        out.append("")

        # Tie-out checks
        out.append("### Denominator & Tie-Out Verification")
        for to in b.tie_outs:
            out.append(f"- {to}")
        out.append("")

    return "\n".join(out)


def run_rollup(repo_root: Path, force: bool = False, output_path: Path | None = None) -> tuple[str, Path]:
    """Execute rollup, print output, and write evaluation/ROLLUP.md."""
    if output_path is None:
        output_path = repo_root / "evaluation" / "ROLLUP.md"

    if output_path.exists() and not force:
        raise FileExistsError(
            f"Output file '{output_path}' already exists. Use --force to overwrite."
        )

    b1_dir = repo_root / "evaluation" / "fresh_batch_1"
    b2_dir = repo_root / "evaluation" / "fresh_batch_2"

    rollups = [
        parse_batch_scores(b1_dir),
        parse_batch_scores(b2_dir),
    ]

    rendered_md = generate_rollup_markdown(rollups)

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered_md, encoding="utf-8")

    return rendered_md, output_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Roll up frozen evaluation results from fresh_batch_1 and fresh_batch_2 into evaluation/ROLLUP.md."
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Overwrite evaluation/ROLLUP.md if it already exists.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Custom output file path (default: evaluation/ROLLUP.md).",
    )
    args = parser.parse_args(argv)

    # Repo root is directory containing pyproject.toml or evaluation/
    repo_root = Path.cwd()
    if not (repo_root / "evaluation").is_dir():
        # Try script's grandparent
        cand = Path(__file__).resolve().parent.parent
        if (cand / "evaluation").is_dir():
            repo_root = cand
        else:
            sys.stderr.write("Error: Could not locate repo root containing evaluation/ directory.\n")
            return 1

    try:
        rendered, out_file = run_rollup(repo_root, force=args.force, output_path=args.output)
        # Print the rollup to stdout
        print(rendered)
        sys.stderr.write(f"\nWrote rollup successfully to {out_file}\n")
        return 0
    except FileExistsError as e:
        sys.stderr.write(f"Refusing to overwrite: {e}\n")
        return 2
    except Exception as e:
        sys.stderr.write(f"Error during rollup: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
