"""Tests for the frozen-evaluation rollup tool (scripts/eval_rollup.py)."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure repo root is in sys.path so scripts can be imported cleanly
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pytest

from scripts.eval_rollup import (
    BatchRollup,
    generate_rollup_markdown,
    main,
    parse_batch_scores,
    parse_markdown_table,
    run_rollup,
)


def test_parse_real_fresh_batches():
    """Test parsing real fresh_batch_1 and fresh_batch_2 read-only."""
    repo_root = Path(__file__).resolve().parent.parent

    b1_dir = repo_root / "evaluation" / "fresh_batch_1"
    b2_dir = repo_root / "evaluation" / "fresh_batch_2"

    assert b1_dir.is_dir()
    assert b2_dir.is_dir()

    rollup_b1 = parse_batch_scores(b1_dir)
    rollup_b2 = parse_batch_scores(b2_dir)

    # Batch 1 checks
    assert rollup_b1.name == "fresh_batch_1"
    assert "12e7226" in rollup_b1.title
    assert rollup_b1.stated_extraction_denominator == "121 reference items in 15 labels"
    assert rollup_b1.derived_extraction_denominator == 121
    assert "13 labels" in (rollup_b1.stated_classification_denominator or "")
    assert rollup_b1.derived_classification_denominator == 13
    assert len(rollup_b1.extraction_table) == 2
    assert len(rollup_b1.classification_table) == 2
    assert any(r.split is not None for r in rollup_b1.extraction_table)
    # Errata captured whole
    assert rollup_b1.errata_markdown is not None
    assert "121" in rollup_b1.errata_markdown
    assert "120" in rollup_b1.errata_markdown
    # Warnings parsed and qualifier preserved
    assert len(rollup_b1.warnings_worked) > 0
    assert len(rollup_b1.warnings_not_worked) > 0
    assert any('(extraction wrong, completeness "complete", no warning)' in w for w in rollup_b1.warnings_not_worked)
    assert not rollup_b1.has_real_tie_out_gap

    # Batch 2 checks
    assert rollup_b2.name == "fresh_batch_2"
    assert "2eb5f39" in rollup_b2.title
    # Prose extraction denominator found
    assert rollup_b2.stated_extraction_denominator == "13 labels and 94 reference items"
    assert rollup_b2.derived_extraction_denominator == 94
    assert "14 judged labels" in (rollup_b2.stated_classification_denominator or "")
    assert rollup_b2.derived_classification_denominator == 14
    assert len(rollup_b2.extraction_table) == 2
    assert len(rollup_b2.classification_table) == 2
    assert all(r.split is None for r in rollup_b2.extraction_table)
    assert any("Without" in k for r in rollup_b2.classification_table for k in r.extra_columns)
    # Warnings parsed and qualifier preserved
    assert len(rollup_b2.warnings_worked) > 0
    assert len(rollup_b2.warnings_not_worked) > 0
    assert any('(extraction wrong, completeness "complete", no warning)' in w for w in rollup_b2.warnings_not_worked)
    assert not rollup_b2.has_real_tie_out_gap


def test_tie_outs_real_batches():
    """Verify tie-out checks on the real batches."""
    repo_root = Path(__file__).resolve().parent.parent

    b1_dir = repo_root / "evaluation" / "fresh_batch_1"
    b2_dir = repo_root / "evaluation" / "fresh_batch_2"

    b1 = parse_batch_scores(b1_dir)
    b2 = parse_batch_scores(b2_dir)

    # Fresh batch 1 tie outs
    assert any("Extraction items (Paste): 92 own + 17 merged + 2 split + 10 omitted = 121/121 (Ties out exactly with stated denominator; table denominator matches)" in to for to in b1.tie_outs)
    assert any("Extraction items (Photo): 18 own + 10 merged + 0 split + 93 omitted = 121/121 (Ties out exactly with stated denominator; table denominator matches)" in to for to in b1.tie_outs)
    assert any("Classification labels (Paste): 8 correct + 0 wrong + 5 abstained = 13/13 (Ties out exactly with stated denominator)" in to for to in b1.tie_outs)
    assert any("Classification labels (Photo): 2 correct + 0 wrong + 11 abstained = 13/13 (Ties out exactly with stated denominator)" in to for to in b1.tie_outs)

    # Fresh batch 2 tie outs (Partial tie out assuming 0 splits)
    assert any("Partial tie-out: matches stated denominator under the assumption of 0 splits" in to for to in b2.tie_outs)
    assert any("Classification labels (Paste): 11 correct + 0 wrong + 3 abstained = 14/14 (Ties out exactly with stated denominator)" in to for to in b2.tie_outs)


def test_errata_rendering_whole():
    """Regression test for Change 1: Errata section contains the complete N13 sentence (both halves)
    and the re-run table's header and separator rows."""
    repo_root = Path(__file__).resolve().parent.parent
    b1_dir = repo_root / "evaluation" / "fresh_batch_1"
    b2_dir = repo_root / "evaluation" / "fresh_batch_2"

    rollup_b1 = parse_batch_scores(b1_dir)
    rollup_b2 = parse_batch_scores(b2_dir)
    rendered = generate_rollup_markdown([rollup_b1, rollup_b2])

    # Check complete N13 explanation sentence is present without truncation
    expected_fragment_1 = (
        "The original reference counted it as two items (Nature identical flavouring substances; "
        "Natural flavouring substances). It is one declared phrase (two modifiers,"
    )
    expected_fragment_2 = (
        "one head noun), and keeping it whole loses nothing. N13's reference therefore has **11** "
        "items instead of 12 and the batch has **120** instead of 121."
    )
    assert expected_fragment_1 in rendered
    assert expected_fragment_2 in rendered

    # Check reference.errata-v1.json line is present
    assert "`reference.errata-v1.json` holds the corrected N13 entry." in rendered

    # Check table header row and separator are present
    assert "| Mode | Own item | Merged | Split | Omitted | Total |" in rendered
    assert "|---|---|---|---|---|---|" in rendered


def test_synthetic_malformed_table():
    """Test handling of malformed or incomplete markdown table without unused tmp_path."""
    lines = [
        "| Mode | List found |",
        "| not a separator |",
        "| Paste | 15/15 |",
    ]
    parsed = parse_markdown_table(lines)
    assert parsed == []


def test_synthetic_missing_sections(tmp_path: Path):
    """Test honest handling with three distinct labels: section absent, section found but not parsed, uncertain."""
    batch_dir = tmp_path / "sparse_batch"
    batch_dir.mkdir()
    scores_md = batch_dir / "SCORES.md"
    scores_md.write_text(
        "# Sparse Batch\n\n"
        "Only text notes here, no markdown tables at all.\n\n"
        "## A. Extraction\n"
        "No table format here, just text description.\n",
        encoding="utf-8",
    )

    rollup = parse_batch_scores(batch_dir)
    inv_dict = dict(rollup.inventory_items)
    assert inv_dict.get("Extraction table") == "section found but not parsed"
    assert inv_dict.get("Classification table") == "section absent"
    assert inv_dict.get("Uncertainty warnings section") == "section absent"


def test_rendering_and_bullet_formatting():
    """Test output rendering: section numbering (## 1., ## 2., ## 3.), no doubled bullets."""
    repo_root = Path(__file__).resolve().parent.parent
    b1_dir = repo_root / "evaluation" / "fresh_batch_1"
    b2_dir = repo_root / "evaluation" / "fresh_batch_2"

    b1 = parse_batch_scores(b1_dir)
    b2 = parse_batch_scores(b2_dir)

    rendered = generate_rollup_markdown([b1, b2])

    assert "## 1. Batch Summaries & Denominator Overview" in rendered
    assert "## 2. Batch: `fresh_batch_1`" in rendered
    assert "## 3. Batch: `fresh_batch_2`" in rendered
    assert "## 2. Batch: `fresh_batch_2`" not in rendered
    assert "- - " not in rendered


def test_tie_out_exit_cases_all_four(tmp_path: Path):
    """Assert exit behaviour for all four tie-out cases:
    (a) batch states a denominator and parts do not sum -> exit non-zero (case a)
    (b) no denominator stated anywhere -> report 'not stated' and exit 0 (case b)
    (c) only a table-derived denominator exists -> label derived, exit 0 (case c)
    (d) component needed for sum is not recorded -> report partial tie-out with named assumption, exit 0 (case d)
    """
    mock_repo = tmp_path / "mock_repo"
    b1 = mock_repo / "evaluation" / "fresh_batch_1"
    b2 = mock_repo / "evaluation" / "fresh_batch_2"
    b1.mkdir(parents=True)
    b2.mkdir(parents=True)

    # --- Case (a): Stated denominator with real gap -> must raise ValueError / exit non-zero
    (b1 / "SCORES.md").write_text(
        "# Batch 1\n\nExtraction denominator: 50 reference items.\nJudged for classification: 20 labels.\n\n"
        "## A. Extraction\n| Mode | Own item | Merged | Split | Omitted |\n|---|---|---|---|---|\n| Paste | 10/50 | 5 | 0 | 5 |\n\n"
        "## B. Classification (20 judged labels)\n| Mode | Correct confident | Wrong confident | Abstained |\n|---|---|---|---|\n| Paste | 5 | 0 | 5 |\n",
        encoding="utf-8",
    )
    (b2 / "SCORES.md").write_text(
        "# Batch 2\n\nExtraction denominator: 20 reference items.\nJudged for classification: 10 labels.\n\n"
        "## A. Extraction\n| Mode | Own item | Merged | Split | Omitted |\n|---|---|---|---|---|\n| Paste | 10/20 | 5 | 0 | 5 |\n\n"
        "## B. Classification (10 judged labels)\n| Mode | Correct confident | Wrong confident | Abstained |\n|---|---|---|---|\n| Paste | 5 | 0 | 5 |\n",
        encoding="utf-8",
    )
    rollup_a = parse_batch_scores(b1)
    assert rollup_a.has_real_tie_out_gap is True
    with pytest.raises(ValueError, match="Tie-out validation failed"):
        run_rollup(repo_root=mock_repo, force=True)

    # --- Case (b): No denominator is stated anywhere -> exit 0, reports 'not stated'
    (b1 / "SCORES.md").write_text(
        "# Batch 1\n\n"
        "## A. Extraction\n| Mode | Own item | Merged | Split | Omitted |\n|---|---|---|---|---|\n| Paste | 10 | 5 | 0 | 5 |\n\n"
        "## B. Classification\n| Mode | Correct confident | Wrong confident | Abstained |\n|---|---|---|---|\n| Paste | 5 | 0 | 5 |\n",
        encoding="utf-8",
    )
    (b2 / "SCORES.md").write_text(
        "# Batch 2\n\n"
        "## A. Extraction\n| Mode | Own item | Merged | Split | Omitted |\n|---|---|---|---|---|\n| Paste | 10 | 5 | 0 | 5 |\n\n"
        "## B. Classification\n| Mode | Correct confident | Wrong confident | Abstained |\n|---|---|---|---|\n| Paste | 5 | 0 | 5 |\n",
        encoding="utf-8",
    )
    rollup_b = parse_batch_scores(b1)
    assert rollup_b.has_real_tie_out_gap is False
    assert rollup_b.stated_extraction_denominator is None
    assert rollup_b.stated_classification_denominator is None
    rendered_b, _ = run_rollup(repo_root=mock_repo, force=True)
    assert "not stated" in rendered_b

    # --- Case (c): Only a table-derived denominator exists -> exit 0, labeled derived
    (b1 / "SCORES.md").write_text(
        "# Batch 1\n\n"
        "## A. Extraction\n| Mode | Own item | Merged | Split | Omitted |\n|---|---|---|---|---|\n| Paste | 10/20 | 5 | 0 | 5 |\n\n"
        "## B. Classification\n| Mode | Correct confident | Wrong confident | Abstained |\n|---|---|---|---|\n| Paste | 5 | 0 | 5 |\n",
        encoding="utf-8",
    )
    (b2 / "SCORES.md").write_text(
        "# Batch 2\n\n"
        "## A. Extraction\n| Mode | Own item | Merged | Split | Omitted |\n|---|---|---|---|---|\n| Paste | 10/20 | 5 | 0 | 5 |\n\n"
        "## B. Classification\n| Mode | Correct confident | Wrong confident | Abstained |\n|---|---|---|---|\n| Paste | 5 | 0 | 5 |\n",
        encoding="utf-8",
    )
    rollup_c = parse_batch_scores(b1)
    assert rollup_c.has_real_tie_out_gap is False
    assert rollup_c.derived_extraction_denominator == 20
    assert any("Ties out exactly with table-derived denominator" in to for to in rollup_c.tie_outs)
    rendered_c, _ = run_rollup(repo_root=mock_repo, force=True)
    assert "Table (Derived) Ext Denom" in rendered_c

    # --- Case (d): Component needed for sum is not recorded -> partial tie-out with named assumption, exit 0
    (b1 / "SCORES.md").write_text(
        "# Batch 1\n\nExtraction denominator: 20 reference items.\nJudged for classification: 10 labels.\n\n"
        "## A. Extraction\n| Mode | Own item | Merged | Omitted |\n|---|---|---|---|\n| Paste | 10/20 | 5 | 5 |\n\n"
        "## B. Classification (10 judged labels)\n| Mode | Correct confident | Wrong confident | Abstained |\n|---|---|---|---|\n| Paste | 5 | 0 | 5 |\n",
        encoding="utf-8",
    )
    (b2 / "SCORES.md").write_text(
        "# Batch 2\n\nExtraction denominator: 20 reference items.\nJudged for classification: 10 labels.\n\n"
        "## A. Extraction\n| Mode | Own item | Merged | Omitted |\n|---|---|---|---|\n| Paste | 10/20 | 5 | 5 |\n\n"
        "## B. Classification (10 judged labels)\n| Mode | Correct confident | Wrong confident | Abstained |\n|---|---|---|---|\n| Paste | 5 | 0 | 5 |\n",
        encoding="utf-8",
    )
    rollup_d = parse_batch_scores(b1)
    assert rollup_d.has_real_tie_out_gap is False
    assert any("assumption of 0 splits" in to for to in rollup_d.tie_outs)
    rendered_d, _ = run_rollup(repo_root=mock_repo, force=True)
    assert "Partial tie-out" in rendered_d


def test_protect_input_paths(tmp_path: Path):
    """Refuse to write over existing source/input files even with --force, while allowing new paths."""
    repo_root = Path(__file__).resolve().parent.parent
    scores_file = repo_root / "evaluation" / "fresh_batch_1" / "SCORES.md"
    errata_file = repo_root / "evaluation" / "fresh_batch_1" / "ERRATA.md"

    # Existing files cannot be overwritten
    with pytest.raises(ValueError, match="Refusing to write to protected existing file"):
        run_rollup(repo_root=repo_root, force=True, output_path=scores_file)

    with pytest.raises(ValueError, match="Refusing to write to protected existing file"):
        run_rollup(repo_root=repo_root, force=True, output_path=errata_file)

    # New custom path outside evaluation is allowed
    new_out = tmp_path / "subdir" / "new_rollup.md"
    rendered, out_path = run_rollup(repo_root=repo_root, force=False, output_path=new_out)
    assert out_path.is_file()
    assert "# Frozen Evaluation Rollup (fresh_batch_1 & fresh_batch_2)" in rendered


def test_run_rollup_refuse_overwrite_without_force():
    """Test that existing evaluation/ROLLUP.md is not overwritten without --force."""
    repo_root = Path(__file__).resolve().parent.parent
    rollup_file = repo_root / "evaluation" / "ROLLUP.md"
    assert rollup_file.is_file()

    with pytest.raises(FileExistsError, match="already exists"):
        run_rollup(repo_root=repo_root, force=False)


def test_main_cli_exit_codes(tmp_path: Path):
    """Test CLI return codes for normal execution, overwrite collision, and validation failure."""
    repo_root = Path(__file__).resolve().parent.parent

    # 1. Normal run with --force returns 0
    ret0 = main(["--force"])
    assert ret0 == 0

    # 2. Overwrite collision without --force returns 2
    ret2 = main([])
    assert ret2 == 2

    # 3. Protected existing file collision returns 3 (Validation Error)
    input_scores = repo_root / "evaluation" / "fresh_batch_1" / "SCORES.md"
    ret3 = main(["--output", str(input_scores), "--force"])
    assert ret3 == 3
