"""Evaluation rollup for frozen evaluation batches.

Reads frozen evaluation artifacts (SCORES.md, ERRATA.md) for fresh_batch_1 and fresh_batch_2
and prints / writes a consolidated, honest rollup.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ExtractionRow:
    mode: str
    list_found: str | None
    own_item: str | None
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
    extra_columns: dict[str, str]


@dataclass
class BatchRollup:
    name: str
    path: Path
    title: str
    metadata_paragraphs: list[str]
    stated_extraction_denominator: str | None
    stated_classification_denominator: str | None
    derived_extraction_denominator: int | None
    derived_classification_denominator: int | None
    errata_notes: list[str]
    extraction_table: list[ExtractionRow]
    extraction_notes: list[str]
    classification_table: list[ClassificationRow]
    classification_notes: list[str]
    other_sections: dict[str, list[str]]
    warnings_worked: list[str]
    warnings_not_worked: list[str]
    inventory_items: list[tuple[str, str]]  # list of (item_label, status_category)
    tie_outs: list[str]
    has_real_tie_out_gap: bool  # True ONLY for case (a): stated denominator vs sum mismatch


def parse_markdown_table(lines: list[str]) -> list[dict[str, str]]:
    """Parse a markdown pipe table into a list of dicts {col_header: cell_value}."""
    table_lines = [line.strip() for line in lines if line.strip().startswith("|") and line.strip().endswith("|")]
    if len(table_lines) < 2:
        return []

    headers = [c.strip() for c in table_lines[0].strip("|").split("|")]
    sep_row = [c.strip() for c in table_lines[1].strip("|").split("|")]
    if not all(re.match(r"^:?-+:?$", s) for s in sep_row):
        return []

    data_rows = []
    for line in table_lines[2:]:
        cols = [c.strip() for c in line.strip("|").split("|")]
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


def parse_paragraphs(lines: list[str]) -> list[str]:
    """Combine wrapped lines separated by blank lines into coherent paragraph blocks."""
    paras: list[str] = []
    curr: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if curr:
                paras.append(" ".join(curr))
                curr = []
        else:
            curr.append(stripped)
    if curr:
        paras.append(" ".join(curr))
    return paras


def parse_batch_scores(batch_dir: Path) -> BatchRollup:
    """Parse SCORES.md and any ERRATA.md of a batch directory faithfully."""
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

    header_paras = parse_paragraphs(sections.get("__header__", []))

    # Read ERRATA.md if present
    errata_notes: list[str] = []
    errata_path = batch_dir / "ERRATA.md"
    if errata_path.is_file():
        err_text = errata_path.read_text(encoding="utf-8")
        err_lines = [ln.strip() for ln in err_text.splitlines() if ln.strip()]
        for ln in err_lines:
            if "Erratum" in ln or "denominator" in ln or "re-run" in ln or "121" in ln or "120" in ln:
                errata_notes.append(re.sub(r"^[-*#]+\s*", "", ln).strip())
        if not errata_notes:
            errata_notes.append("ERRATA.md present in batch directory.")

    # 1. Stated denominators in prose or prefix form
    stated_ext_denom = None
    stated_cls_denom = None

    for p in header_paras:
        m_ext1 = re.search(r"Extraction denominator:\s*([^.]+)", p)
        if m_ext1:
            stated_ext_denom = m_ext1.group(1).strip()
        else:
            m_ext2 = re.search(r"extraction uses\s*([^,;]+(?:labels and \d+ reference items|\d+ reference items))", p, re.IGNORECASE)
            if m_ext2:
                stated_ext_denom = m_ext2.group(1).strip()

        m_cls1 = re.search(r"Judged for classification:\s*([^.]+)", p)
        if m_cls1:
            stated_cls_denom = m_cls1.group(1).strip()
        else:
            m_cls2 = re.search(r"classification uses\s*([^,;]+judged labels?)", p, re.IGNORECASE)
            if m_cls2:
                stated_cls_denom = m_cls2.group(1).strip()

    # Find Extraction section
    ext_sec_title = next((k for k in sections if "Extraction" in k), None)
    ext_rows: list[ExtractionRow] = []
    ext_notes: list[str] = []
    derived_ext_denom: int | None = None

    if ext_sec_title:
        ext_lines = sections[ext_sec_title]
        parsed_table = parse_markdown_table(ext_lines)
        for r in parsed_table:
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
            if own_item and derived_ext_denom is None:
                d_info = extract_denominator_and_count(own_item)
                if d_info:
                    derived_ext_denom = d_info[1]

        # Process notes line by line, joining wrapped bullet lines
        curr_bullet: list[str] = []
        for ln in ext_lines:
            s = ln.strip()
            if not s or s.startswith("|"):
                continue
            if s.startswith("- ") or s.startswith("* "):
                if curr_bullet:
                    ext_notes.append(" ".join(curr_bullet))
                    curr_bullet = []
                curr_bullet.append(re.sub(r"^[-*]\s*", "", s).strip())
            else:
                if curr_bullet:
                    curr_bullet.append(s)
                else:
                    curr_bullet.append(s)
        if curr_bullet:
            ext_notes.append(" ".join(curr_bullet))

    # Find Classification section
    cls_sec_title = next((k for k in sections if "Classification" in k), None)
    cls_rows: list[ClassificationRow] = []
    cls_notes: list[str] = []
    derived_cls_denom: int | None = None

    if cls_sec_title:
        cls_lines = sections[cls_sec_title]
        if not stated_cls_denom:
            m = re.search(r"Classification\s*\(([^)]+)\)", cls_sec_title)
            if m:
                stated_cls_denom = m.group(1).strip()

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
            if derived_cls_denom is None:
                c = extract_leading_int(correct or "") or 0
                w = extract_leading_int(wrong or "") or 0
                a = extract_leading_int(abstained or "") or 0
                sum_row = c + w + a
                if sum_row > 0:
                    derived_cls_denom = sum_row

        curr_bullet = []
        for ln in cls_lines:
            s = ln.strip()
            if not s or s.startswith("|"):
                continue
            if s.startswith("- ") or s.startswith("* "):
                if curr_bullet:
                    cls_notes.append(" ".join(curr_bullet))
                    curr_bullet = []
                curr_bullet.append(re.sub(r"^[-*]\s*", "", s).strip())
            else:
                if curr_bullet:
                    curr_bullet.append(s)
                else:
                    curr_bullet.append(s)
        if curr_bullet:
            cls_notes.append(" ".join(curr_bullet))

    # Find Uncertainty Warnings section
    warn_sec_title = next((k for k in sections if "uncertainty warnings" in k.lower()), None)
    warnings_worked: list[str] = []
    warnings_not_worked: list[str] = []

    if warn_sec_title:
        warn_lines = sections[warn_sec_title]
        for ln in warn_lines:
            s = ln.strip()
            if not s or s.startswith("#") or s.startswith("Not general accuracy"):
                continue

            # In batch 2, Worked and Did not work are on the same line:
            # "Worked: paste M07... Did not work (extraction wrong...): paste M08..."
            if "Did not work" in s and ("Worked:" in s or s.startswith("- Worked") or s.startswith("Worked")):
                parts = re.split(r"(?=Did not work)", s, flags=re.IGNORECASE)
                for part in parts:
                    part_str = part.strip()
                    if part_str.startswith("- ") or part_str.startswith("* "):
                        part_str = part_str[2:].strip()
                    if part_str.lower().startswith("worked"):
                        w_val = re.sub(r"^worked:\s*", "", part_str, flags=re.IGNORECASE).strip()
                        if w_val:
                            warnings_worked.append(w_val)
                    elif "did not work" in part_str.lower():
                        m_dnw = re.match(r"^did not work\s*(\([^)]+\))?:\s*(.*)", part_str, flags=re.IGNORECASE)
                        if m_dnw:
                            qual = m_dnw.group(1) or ""
                            val = m_dnw.group(2).strip()
                            if qual:
                                warnings_not_worked.append(f"{qual}: {val}")
                            else:
                                warnings_not_worked.append(val)
                        else:
                            warnings_not_worked.append(part_str)
            elif s.lower().startswith("- worked:") or s.lower().startswith("worked:"):
                clean = re.sub(r"^[-*]\s*worked:\s*", "", s, flags=re.IGNORECASE).strip()
                if clean:
                    warnings_worked.append(clean)
            elif "did not work" in s.lower() and not s.lower().startswith("worked:"):
                clean = s
                if clean.startswith("- ") or clean.startswith("* "):
                    clean = clean[2:].strip()
                m_dnw = re.match(r"^did not work\s*(\([^)]+\))?:\s*(.*)", clean, flags=re.IGNORECASE)
                if m_dnw:
                    qual = m_dnw.group(1) or ""
                    val = m_dnw.group(2).strip()
                    if qual:
                        warnings_not_worked.append(f"{qual}: {val}")
                    else:
                        warnings_not_worked.append(val)
                else:
                    warnings_not_worked.append(clean)

    # Other sections unique to this batch
    other_sections: dict[str, list[str]] = {}
    known_sec_titles = {ext_sec_title, cls_sec_title, warn_sec_title, "__header__"}
    for sec_name, s_lines in sections.items():
        if sec_name not in known_sec_titles:
            cleaned_lines = []
            curr_item: list[str] = []
            for ln in s_lines:
                s = ln.strip()
                if not s:
                    continue
                if s.startswith("- ") or s.startswith("* "):
                    if curr_item:
                        cleaned_lines.append(" ".join(curr_item))
                        curr_item = []
                    curr_item.append(re.sub(r"^[-*]\s*", "", s).strip())
                else:
                    if curr_item:
                        curr_item.append(s)
                    else:
                        curr_item.append(s)
            if curr_item:
                cleaned_lines.append(" ".join(curr_item))
            if cleaned_lines:
                other_sections[sec_name] = cleaned_lines

    # Honest Inventory Classification
    inventory_items: list[tuple[str, str]] = []

    # Extraction
    if ext_sec_title:
        if ext_rows:
            inventory_items.append(("Extraction table", f"Recorded ({len(ext_rows)} rows)"))
        else:
            inventory_items.append(("Extraction table", "section found but not parsed"))
    else:
        # Check if heading exists partially
        cand_ext = any("extraction" in k.lower() for k in sections)
        if cand_ext:
            inventory_items.append(("Extraction table", "uncertain whether recorded"))
        else:
            inventory_items.append(("Extraction table", "section absent"))

    # Split column
    has_split = any(r.split is not None for r in ext_rows)
    if has_split:
        inventory_items.append(("Extraction table: Split column", "Recorded"))
    else:
        inventory_items.append(("Extraction table: Split column", "not recorded in batch table"))

    # Classification
    if cls_sec_title:
        if cls_rows:
            inventory_items.append(("Classification table", f"Recorded ({len(cls_rows)} rows)"))
        else:
            inventory_items.append(("Classification table", "section found but not parsed"))
    else:
        cand_cls = any("classif" in k.lower() for k in sections)
        if cand_cls:
            inventory_items.append(("Classification table", "uncertain whether recorded"))
        else:
            inventory_items.append(("Classification table", "section absent"))

    # Overlapping column
    has_overlap_col = any("Without" in k for r in cls_rows for k in r.extra_columns)
    if has_overlap_col:
        inventory_items.append(("Classification table: Without overlapping labels column", "Recorded"))
    else:
        inventory_items.append(("Classification table: Without overlapping labels column", "not recorded in batch table"))

    # Uncertainty warnings
    if warn_sec_title:
        if warnings_worked or warnings_not_worked:
            inventory_items.append(("Uncertainty warnings section", "Recorded"))
        else:
            inventory_items.append(("Uncertainty warnings section", "section found but not parsed"))
    else:
        cand_warn = any("warning" in k.lower() or "uncertain" in k.lower() for k in sections)
        if cand_warn:
            inventory_items.append(("Uncertainty warnings section", "uncertain whether recorded"))
        else:
            inventory_items.append(("Uncertainty warnings section", "section absent"))

    # Additional sections
    for sec_name in other_sections:
        clean_name = sec_name.lstrip("#").strip()
        inventory_items.append((f"Additional section ({clean_name})", "Recorded"))

    # Tie-out checks and enforcement
    tie_outs: list[str] = []
    has_real_tie_out_gap = False

    stated_ext_target = None
    if stated_ext_denom:
        m = re.search(r"(\d+)\s+reference items", stated_ext_denom)
        if m:
            stated_ext_target = int(m.group(1))

    # 1. Extraction items tie-out
    for r in ext_rows:
        mode_label = r.mode.split("(")[0].strip()
        denom_info = extract_denominator_and_count(r.own_item or "")
        if denom_info:
            own_cnt, table_denom = denom_info
            merged_cnt = extract_leading_int(r.merged or "") or 0
            omitted_cnt = extract_leading_int(r.omitted or "") or 0
            split_cnt = extract_leading_int(r.split or "") if r.split is not None else None

            # Compare table denominator with stated target if available
            target_denom = stated_ext_target if stated_ext_target is not None else table_denom
            is_stated = stated_ext_target is not None

            # Check components
            if split_cnt is not None:
                # All components recorded
                sum_parts = own_cnt + merged_cnt + omitted_cnt + split_cnt
                if sum_parts == target_denom:
                    if is_stated and table_denom == stated_ext_target:
                        tie_outs.append(
                            f"Extraction items ({mode_label}): {own_cnt} own + {merged_cnt} merged + {split_cnt} split + {omitted_cnt} omitted = {sum_parts}/{stated_ext_target} (Ties out exactly with stated denominator; table denominator matches)"
                        )
                    elif is_stated:
                        has_real_tie_out_gap = True
                        tie_outs.append(
                            f"Extraction items ({mode_label}): sum {sum_parts} != stated denominator {stated_ext_target} (Gap: {stated_ext_target - sum_parts}; table denominator is {table_denom})"
                        )
                    else:
                        tie_outs.append(
                            f"Extraction items ({mode_label}): {own_cnt} own + {merged_cnt} merged + {split_cnt} split + {omitted_cnt} omitted = {sum_parts}/{table_denom} (Ties out exactly with table-derived denominator; stated denominator not stated)"
                        )
                else:
                    if is_stated:
                        has_real_tie_out_gap = True
                        gap = target_denom - sum_parts
                        tie_outs.append(
                            f"Extraction items ({mode_label}): sum {sum_parts} != stated denominator {target_denom} (Gap: {gap}; table denominator is {table_denom})"
                        )
                    else:
                        gap = target_denom - sum_parts
                        tie_outs.append(
                            f"Extraction items ({mode_label}): sum {sum_parts} != table-derived denominator {target_denom} (Table-derived gap: {gap}; stated denominator not stated)"
                        )
            else:
                # Component (Split) is not recorded -> Partial tie-out with named assumption
                sum_without_split = own_cnt + merged_cnt + omitted_cnt
                if sum_without_split == target_denom:
                    if is_stated:
                        tie_outs.append(
                            f"Extraction items ({mode_label}): {own_cnt} own + {merged_cnt} merged + {omitted_cnt} omitted = {sum_without_split}/{stated_ext_target} (Partial tie-out: matches stated denominator under the assumption of 0 splits, as the Split column is not recorded; table denominator matches)"
                        )
                    else:
                        tie_outs.append(
                            f"Extraction items ({mode_label}): {own_cnt} own + {merged_cnt} merged + {omitted_cnt} omitted = {sum_without_split}/{table_denom} (Partial tie-out: matches table-derived denominator under the assumption of 0 splits, as the Split column is not recorded; stated denominator not stated)"
                        )
                else:
                    if is_stated:
                        has_real_tie_out_gap = True
                        gap = target_denom - sum_without_split
                        tie_outs.append(
                            f"Extraction items ({mode_label}): sum {sum_without_split} != stated denominator {target_denom} (Gap: {gap}; partial tie-out assuming 0 splits; table denominator is {table_denom})"
                        )
                    else:
                        gap = target_denom - sum_without_split
                        tie_outs.append(
                            f"Extraction items ({mode_label}): sum {sum_without_split} != table-derived denominator {target_denom} (Table-derived gap: {gap}; partial tie-out assuming 0 splits; stated denominator not stated)"
                        )
        else:
            if stated_ext_target is not None:
                has_real_tie_out_gap = True
                tie_outs.append(f"Extraction items ({mode_label}): Missing table fraction denominator; stated denominator is {stated_ext_target}")
            else:
                tie_outs.append(f"Extraction items ({mode_label}): Missing table fraction denominator and stated denominator not stated")

    stated_cls_target = None
    if stated_cls_denom:
        m = re.search(r"(\d+)\s*(?:judged)?\s*labels?", stated_cls_denom)
        if m:
            stated_cls_target = int(m.group(1))

    # 2. Classification labels tie-out
    for r in cls_rows:
        mode_label = r.mode.split("(")[0].strip()
        c_cnt = extract_leading_int(r.correct_confident or "") or 0
        w_cnt = extract_leading_int(r.wrong_confident or "") or 0
        a_cnt = extract_leading_int(r.abstained or "") or 0
        sum_cls = c_cnt + w_cnt + a_cnt

        if stated_cls_target is not None:
            if sum_cls == stated_cls_target:
                tie_outs.append(
                    f"Classification labels ({mode_label}): {c_cnt} correct + {w_cnt} wrong + {a_cnt} abstained = {sum_cls}/{stated_cls_target} (Ties out exactly with stated denominator)"
                )
            else:
                has_real_tie_out_gap = True
                tie_outs.append(
                    f"Classification labels ({mode_label}): {c_cnt} correct + {w_cnt} wrong + {a_cnt} abstained = {sum_cls}/{stated_cls_target} (Gap: {stated_cls_target - sum_cls})"
                )
        else:
            # Stated denominator not stated
            tie_outs.append(
                f"Classification labels ({mode_label}): {c_cnt} correct + {w_cnt} wrong + {a_cnt} abstained = {sum_cls} (Stated denominator not stated; matches summed total of {sum_cls})"
            )

    return BatchRollup(
        name=batch_dir.name,
        path=batch_dir,
        title=title,
        metadata_paragraphs=header_paras,
        stated_extraction_denominator=stated_ext_denom,
        stated_classification_denominator=stated_cls_denom,
        derived_extraction_denominator=derived_ext_denom,
        derived_classification_denominator=derived_cls_denom,
        errata_notes=errata_notes,
        extraction_table=ext_rows,
        extraction_notes=ext_notes,
        classification_table=cls_rows,
        classification_notes=cls_notes,
        other_sections=other_sections,
        warnings_worked=warnings_worked,
        warnings_not_worked=warnings_not_worked,
        inventory_items=inventory_items,
        tie_outs=tie_outs,
        has_real_tie_out_gap=has_real_tie_out_gap,
    )


def generate_rollup_markdown(rollups: list[BatchRollup]) -> str:
    """Generate Markdown representation of the multi-batch rollup."""
    out: list[str] = []
    out.append("# Frozen Evaluation Rollup (fresh_batch_1 & fresh_batch_2)")
    out.append("")
    out.append("This document summarizes the hand-adjudicated frozen evaluation artifacts recorded in `evaluation/fresh_batch_1` and `evaluation/fresh_batch_2`. Stated figures and notes are extracted read-only from each batch's respective `SCORES.md` and `ERRATA.md`. The tie-out verification computes category sums and compares them directly against stated and table denominators to verify integrity.")
    out.append("")

    # Overview table
    out.append("## 1. Batch Summaries & Denominator Overview")
    out.append("")
    out.append("| Batch | Title | Stated Extraction Denom | Table (Derived) Ext Denom | Stated Classif Denom | Summed (Derived) Classif Denom |")
    out.append("|---|---|---|---|---|---|")
    for b in rollups:
        s_ext = b.stated_extraction_denominator or "not stated"
        d_ext = str(b.derived_extraction_denominator) if b.derived_extraction_denominator is not None else "not derived"
        s_cls = b.stated_classification_denominator or "not stated"
        d_cls = str(b.derived_classification_denominator) if b.derived_classification_denominator is not None else "not derived"
        out.append(f"| `{b.name}` | {b.title} | {s_ext} | {d_ext} | {s_cls} | {d_cls} |")
    out.append("")

    # Section for each batch
    sec_idx = 2
    for b in rollups:
        out.append(f"## {sec_idx}. Batch: `{b.name}`")
        sec_idx += 1
        out.append(f"**Title**: {b.title}")
        out.append("")

        if b.errata_notes:
            out.append("**Errata Notice:**")
            for e in b.errata_notes:
                out.append(f"- {e}")
            out.append("")

        if b.metadata_paragraphs:
            out.append("**Metadata & Context:**")
            for p in b.metadata_paragraphs:
                out.append(f"- {p}")
            out.append("")

        # Extraction
        out.append("### Extraction Outcomes")
        if b.extraction_table:
            hdr = ["Mode", "List Found", "Own Item", "Merged", "Split", "Omitted", "Additions"]
            out.append("| " + " | ".join(hdr) + " |")
            out.append("| " + " | ".join(["---"] * len(hdr)) + " |")
            for r in b.extraction_table:
                row_vals = [
                    r.mode,
                    r.list_found or "not recorded",
                    r.own_item or "not recorded",
                    r.merged or "not recorded",
                    r.split if (r.split is not None) else "not recorded in batch table",
                    r.omitted or "not recorded",
                    r.additions or "not recorded",
                ]
                out.append("| " + " | ".join(row_vals) + " |")
            out.append("")
        else:
            out.append("*No extraction table found or parsed.*")
            out.append("")

        if b.extraction_notes:
            out.append("**Extraction Notes:**")
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
            out.append("*No classification table found or parsed.*")
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
                out.append("- **Worked:** not recorded or not parsed")
            if b.warnings_not_worked:
                out.append("- **Did not work:** " + "; ".join(b.warnings_not_worked))
            else:
                out.append("- **Did not work:** not recorded or not parsed")
            out.append("")
        else:
            out.append("- *Uncertainty warning section not found or not parsed.*")
            out.append("")

        # Other sections
        if b.other_sections:
            out.append("### Additional Recorded Sections")
            for sec_name, sec_lines in b.other_sections.items():
                clean_sec = sec_name.lstrip("#").strip()
                out.append(f"#### {clean_sec}")
                for ln in sec_lines:
                    out.append(f"- {ln}")
                out.append("")

        # Honest Inventory
        out.append("### Recorded vs. Unrecorded Inventory")
        for item_label, status_cat in b.inventory_items:
            out.append(f"- {item_label}: {status_cat}")
        out.append("")

        # Tie-outs
        out.append("### Denominator & Tie-Out Verification")
        for to in b.tie_outs:
            out.append(f"- {to}")
        out.append("")

    return "\n".join(out)


def run_rollup(repo_root: Path, force: bool = False, output_path: Path | None = None) -> tuple[str, Path]:
    """Execute rollup, enforce tie-outs, print output, and write output file."""
    if output_path is None:
        output_path = repo_root / "evaluation" / "ROLLUP.md"

    output_path = output_path.resolve()

    # Refuse to write over any existing file that is not the tool's previous ROLLUP.md output
    default_rollup_path = (repo_root / "evaluation" / "ROLLUP.md").resolve()
    if output_path.exists():
        if output_path != default_rollup_path:
            raise ValueError(
                f"Refusing to write to protected path '{output_path}'. The tool may only write to evaluation/ROLLUP.md."
            )
        if not force:
            raise FileExistsError(
                f"Output file '{output_path}' already exists. Use --force to overwrite."
            )

    b1_dir = repo_root / "evaluation" / "fresh_batch_1"
    b2_dir = repo_root / "evaluation" / "fresh_batch_2"

    rollups = [
        parse_batch_scores(b1_dir),
        parse_batch_scores(b2_dir),
    ]

    # Enforce case (a): exit non-zero if a batch states a denominator and parts do not sum to it
    gaps_found = [b.name for b in rollups if b.has_real_tie_out_gap]
    if gaps_found:
        rendered_md = generate_rollup_markdown(rollups)
        raise ValueError(
            f"Tie-out validation failed for batch(es): {', '.join(gaps_found)}. Stated denominator mismatch or arithmetic gap detected."
        )

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

    repo_root = Path.cwd()
    if not (repo_root / "evaluation").is_dir():
        cand = Path(__file__).resolve().parent.parent
        if (cand / "evaluation").is_dir():
            repo_root = cand
        else:
            sys.stderr.write("Error: Could not locate repo root containing evaluation/ directory.\n")
            return 1

    try:
        rendered, out_file = run_rollup(repo_root, force=args.force, output_path=args.output)
        print(rendered)
        sys.stderr.write(f"\nWrote rollup successfully to {out_file}\n")
        return 0
    except FileExistsError as e:
        sys.stderr.write(f"Refusing to overwrite: {e}\n")
        return 2
    except ValueError as e:
        sys.stderr.write(f"Validation Error: {e}\n")
        return 3
    except Exception as e:
        sys.stderr.write(f"Error during rollup: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
