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
    recorded_fields: dict[str, str]
    unrecorded_fields: list[str]
    tie_outs: list[str]
    has_tie_out_gap: bool


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
    """Combine lines separated by blank lines into coherent paragraph blocks."""
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
        for ln in err_text.splitlines():
            s = ln.strip()
            if "Erratum" in s or "denominator" in s or "re-run" in s:
                errata_notes.append(s.lstrip("#").strip())
        if not errata_notes:
            errata_notes.append("ERRATA.md present in batch directory.")

    # 1. Stated denominators in prose
    stated_ext_denom = None
    stated_cls_denom = None

    for p in header_paras:
        # Check extraction prose statements:
        m_ext1 = re.search(r"Extraction denominator:\s*([^.]+)", p)
        if m_ext1:
            stated_ext_denom = m_ext1.group(1).strip()
        else:
            m_ext2 = re.search(r"extraction uses\s*([^,;]+(?:labels and \d+ reference items|\d+ reference items))", p, re.IGNORECASE)
            if m_ext2:
                stated_ext_denom = m_ext2.group(1).strip()

        # Check classification prose statements:
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
            # Derive extraction denominator from table
            if own_item and derived_ext_denom is None:
                d_info = extract_denominator_and_count(own_item)
                if d_info:
                    derived_ext_denom = d_info[1]

        # Collect notes without doubled bullets
        for ln in ext_lines:
            s = ln.strip()
            if s and not s.startswith("|"):
                clean_s = re.sub(r"^[-*]\s*", "", s).strip()
                ext_notes.append(clean_s)

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
            # Derive classification denominator by summing outcomes
            if derived_cls_denom is None:
                c = extract_leading_int(correct or "") or 0
                w = extract_leading_int(wrong or "") or 0
                a = extract_leading_int(abstained or "") or 0
                sum_row = c + w + a
                if sum_row > 0:
                    derived_cls_denom = sum_row

        for ln in cls_lines:
            s = ln.strip()
            if s and not s.startswith("|"):
                clean_s = re.sub(r"^[-*]\s*", "", s).strip()
                cls_notes.append(clean_s)

    # Uncertainty warnings section
    warn_sec_title = next((k for k in sections if "uncertainty warnings" in k.lower()), None)
    warnings_worked: list[str] = []
    warnings_not_worked: list[str] = []

    if warn_sec_title:
        warn_lines = sections[warn_sec_title]
        # In batch 1:
        # - Worked: paste N03, N08, N16; photo N05, N11, N12...
        # - Did not work (extraction wrong...): paste N02... None of these produced a wrong confident group...
        # In batch 2:
        # Worked: paste M07, M10, M11... photo M05, M09, M11, M12... Did not work (extraction wrong...): paste M08... No wrong confident group resulted in any of them.
        for ln in warn_lines:
            s = ln.strip()
            if not s or s.startswith("#") or s.startswith("Not general accuracy"):
                continue

            # Separate by Did not work if both are on same line
            if "Did not work" in s and ("Worked:" in s or s.startswith("- Worked") or s.startswith("Worked")):
                parts = re.split(r"(?=Did not work)", s, flags=re.IGNORECASE)
                for part in parts:
                    part_str = part.strip().lstrip("-* ").strip()
                    if part_str.lower().startswith("worked"):
                        w_val = re.sub(r"^worked:\s*", "", part_str, flags=re.IGNORECASE).strip()
                        if w_val:
                            warnings_worked.append(w_val)
                    elif "did not work" in part_str.lower():
                        # Extract qualifier and text
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
                clean = re.sub(r"^[-*]\s*", "", s).strip()
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
            # Clean each line's leading bullet markers if present, but maintain items
            cleaned_lines = []
            for ln in s_lines:
                s = ln.strip()
                if not s:
                    continue
                clean_s = re.sub(r"^[-*]\s*", "", s).strip()
                cleaned_lines.append(clean_s)
            if cleaned_lines:
                other_sections[sec_name] = cleaned_lines

    # Recorded vs unrecorded analysis
    recorded_fields: dict[str, str] = {}
    unrecorded_fields: list[str] = []

    if ext_sec_title:
        recorded_fields["Extraction section"] = f"Recorded ({len(ext_rows)} rows)"
    else:
        unrecorded_fields.append("Extraction section: section not found or not parsed")

    has_split = any(r.split is not None for r in ext_rows)
    if has_split:
        recorded_fields["Extraction table: Split column"] = "Recorded"
    else:
        unrecorded_fields.append("Extraction table: Split column (not recorded in batch table)")

    if cls_sec_title:
        recorded_fields["Classification section"] = f"Recorded ({len(cls_rows)} rows)"
    else:
        unrecorded_fields.append("Classification section: section not found or not parsed")

    has_overlap_col = any("Without" in k for r in cls_rows for k in r.extra_columns)
    if has_overlap_col:
        recorded_fields["Classification table: Without overlapping labels column"] = "Recorded"
    else:
        unrecorded_fields.append("Classification table: Without overlapping labels column (not recorded in batch table)")

    if warn_sec_title:
        recorded_fields["Uncertainty warnings section"] = "Recorded"
    else:
        unrecorded_fields.append("Uncertainty warnings section: section not found or not parsed")

    for sec_name in other_sections:
        clean_name = sec_name.lstrip("#").strip()
        recorded_fields[f"Additional section: {clean_name}"] = "Recorded"

    # Tie-out checks and enforcement
    tie_outs: list[str] = []
    has_tie_out_gap = False

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
            split_cnt = extract_leading_int(r.split or "") if r.split is not None else 0

            sum_parts = own_cnt + merged_cnt + omitted_cnt + split_cnt

            denom_match_msg = ""
            if stated_ext_target is not None:
                if table_denom == stated_ext_target:
                    denom_match_msg = f"matches stated denominator ({stated_ext_target})"
                else:
                    has_tie_out_gap = True
                    denom_match_msg = f"MISMATCH with stated denominator ({stated_ext_target})"

            if sum_parts == table_denom:
                if r.split is not None:
                    tie_outs.append(
                        f"Extraction items ({mode_label}): {own_cnt} own + {merged_cnt} merged + {split_cnt} split + {omitted_cnt} omitted = {sum_parts}/{table_denom} (Ties out exactly; table denominator {denom_match_msg})"
                    )
                else:
                    tie_outs.append(
                        f"Extraction items ({mode_label}): {own_cnt} own + {merged_cnt} merged + {omitted_cnt} omitted = {sum_parts}/{table_denom} (Sum matches table denominator, assuming 0 splits as split column is not recorded; table denominator {denom_match_msg})"
                    )
            else:
                has_tie_out_gap = True
                gap = table_denom - sum_parts
                tie_outs.append(
                    f"Extraction items ({mode_label}): sum {sum_parts} != denominator {table_denom} (Gap: {gap}; table denominator {denom_match_msg})"
                )
        else:
            has_tie_out_gap = True
            tie_outs.append(f"Extraction items ({mode_label}): Missing valid fraction denominator in '{r.own_item}'")

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
                has_tie_out_gap = True
                tie_outs.append(
                    f"Classification labels ({mode_label}): {c_cnt} correct + {w_cnt} wrong + {a_cnt} abstained = {sum_cls}/{stated_cls_target} (Gap: {stated_cls_target - sum_cls})"
                )
        else:
            has_tie_out_gap = True
            tie_outs.append(
                f"Classification labels ({mode_label}): {c_cnt} correct + {w_cnt} wrong + {a_cnt} abstained = {sum_cls} (Stated denominator is missing or not parsed)"
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
        recorded_fields=recorded_fields,
        unrecorded_fields=unrecorded_fields,
        tie_outs=tie_outs,
        has_tie_out_gap=has_tie_out_gap,
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
        s_ext = b.stated_extraction_denominator or "Not found/parsed"
        d_ext = str(b.derived_extraction_denominator) if b.derived_extraction_denominator is not None else "Not derived"
        s_cls = b.stated_classification_denominator or "Not found/parsed"
        d_cls = str(b.derived_classification_denominator) if b.derived_classification_denominator is not None else "Not derived"
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
            for sec_name, sec_paras in b.other_sections.items():
                clean_sec = sec_name.lstrip("#").strip()
                out.append(f"#### {clean_sec}")
                for p in sec_paras:
                    out.append(f"- {p}")
                out.append("")

        # Recorded vs Unrecorded
        out.append("### Recorded vs. Unrecorded Inventory")
        out.append("**Recorded Fields & Sections:**")
        for k, v in b.recorded_fields.items():
            out.append(f"- {k}: {v}")
        out.append("")
        out.append("**Unrecorded / Missing in this Batch:**")
        for u in b.unrecorded_fields:
            out.append(f"- {u}")
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

    # Guard: output path must not be an existing input artifact
    input_artifacts = [
        (repo_root / "evaluation" / "fresh_batch_1" / "SCORES.md").resolve(),
        (repo_root / "evaluation" / "fresh_batch_1" / "ERRATA.md").resolve(),
        (repo_root / "evaluation" / "fresh_batch_2" / "SCORES.md").resolve(),
    ]
    if output_path in input_artifacts:
        raise ValueError(f"Refusing to write to input evaluation artifact '{output_path}'.")

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

    # Enforce tie-outs
    gaps_found = [b.name for b in rollups if b.has_tie_out_gap]
    if gaps_found:
        rendered_md = generate_rollup_markdown(rollups)
        raise ValueError(
            f"Tie-out validation failed for batch(es): {', '.join(gaps_found)}. Gaps or denominator mismatches detected."
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
