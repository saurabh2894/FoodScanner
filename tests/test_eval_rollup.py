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
    # Errata captured
    assert any("121" in e or "120" in e for e in rollup_b1.errata_notes)
    # Warnings parsed
    assert len(rollup_b1.warnings_worked) > 0
    assert len(rollup_b1.warnings_not_worked) > 0
    assert not rollup_b1.has_tie_out_gap

    # Batch 2 checks
    assert rollup_b2.name == "fresh_batch_2"
    assert "2eb5f39" in rollup_b2.title
    assert rollup_b2.stated_extraction_denominator == "13 labels and 94 reference items"
    assert rollup_b2.derived_extraction_denominator == 94
    assert "14 judged labels" in (rollup_b2.stated_classification_denominator or "")
    assert rollup_b2.derived_classification_denominator == 14
    assert len(rollup_b2.extraction_table) == 2
    assert len(rollup_b2.classification_table) == 2
    assert all(r.split is None for r in rollup_b2.extraction_table)
    assert any("Without" in k for r in rollup_b2.classification_table for k in r.extra_columns)
    assert len(rollup_b2.warnings_worked) > 0
    assert len(rollup_b2.warnings_not_worked) > 0
    assert not rollup_b2.has_tie_out_gap


def test_tie_outs_real_batches():
    """Verify tie-out checks on the real batches."""
    repo_root = Path(__file__).resolve().parent.parent

    b1_dir = repo_root / "evaluation" / "fresh_batch_1"
    b2_dir = repo_root / "evaluation" / "fresh_batch_2"

    b1 = parse_batch_scores(b1_dir)
    b2 = parse_batch_scores(b2_dir)

    # Fresh batch 1 tie outs
    assert any("Extraction items (Paste): 92 own + 17 merged + 2 split + 10 omitted = 121/121 (Ties out exactly; table denominator matches stated denominator (121))" in to for to in b1.tie_outs)
    assert any("Extraction items (Photo): 18 own + 10 merged + 0 split + 93 omitted = 121/121 (Ties out exactly; table denominator matches stated denominator (121))" in to for to in b1.tie_outs)
    assert any("Classification labels (Paste): 8 correct + 0 wrong + 5 abstained = 13/13 (Ties out exactly with stated denominator)" in to for to in b1.tie_outs)
    assert any("Classification labels (Photo): 2 correct + 0 wrong + 11 abstained = 13/13 (Ties out exactly with stated denominator)" in to for to in b1.tie_outs)

    # Fresh batch 2 tie outs
    assert any("Extraction items (Paste): 77 own + 6 merged + 11 omitted = 94/94 (Sum matches table denominator, assuming 0 splits as split column is not recorded; table denominator matches stated denominator (94))" in to for to in b2.tie_outs)
    assert any("Extraction items (Photo): 27 own + 23 merged + 44 omitted = 94/94 (Sum matches table denominator, assuming 0 splits as split column is not recorded; table denominator matches stated denominator (94))" in to for to in b2.tie_outs)
    assert any("Classification labels (Paste): 11 correct + 0 wrong + 3 abstained = 14/14 (Ties out exactly with stated denominator)" in to for to in b2.tie_outs)
    assert any("Classification labels (Photo): 4 correct + 0 wrong + 10 abstained = 14/14 (Ties out exactly with stated denominator)" in to for to in b2.tie_outs)


def test_synthetic_malformed_table(tmp_path: Path):
    """Test handling of malformed or incomplete markdown table."""
    batch_dir = tmp_path / "malformed_batch"
    batch_dir.mkdir()
    scores_md = batch_dir / "SCORES.md"
    scores_md.write_text(
        "# Malformed Batch\n\n"
        "## A. Extraction\n"
        "| Mode | List found |\n"
        "| not a separator |\n"
        "| Paste | 15/15 |\n",
        encoding="utf-8",
    )

    rollup = parse_batch_scores(batch_dir)
    assert rollup.extraction_table == []


def test_synthetic_missing_sections(tmp_path: Path):
    """Test honest handling when sections are completely missing or unparsed."""
    batch_dir = tmp_path / "sparse_batch"
    batch_dir.mkdir()
    scores_md = batch_dir / "SCORES.md"
    scores_md.write_text(
        "# Sparse Batch\n\n"
        "Only text notes here, no markdown tables at all.\n",
        encoding="utf-8",
    )

    rollup = parse_batch_scores(batch_dir)
    assert "Extraction section: section not found or not parsed" in rollup.unrecorded_fields
    assert "Classification section: section not found or not parsed" in rollup.unrecorded_fields
    assert "Uncertainty warnings section: section not found or not parsed" in rollup.unrecorded_fields
    assert rollup.extraction_table == []
    assert rollup.classification_table == []
    assert rollup.warnings_worked == []
    assert rollup.warnings_not_worked == []


def test_synthetic_tie_out_gap_enforcement(tmp_path: Path):
    """Test that arithmetic gaps in denominators cause has_tie_out_gap and run_rollup failure."""
    batch_dir = tmp_path / "fresh_batch_1"
    batch_dir.mkdir()
    scores_md = batch_dir / "SCORES.md"
    scores_md.write_text(
        "# Gap Batch\n\n"
        "Judged for classification: 20 labels.\n"
        "Extraction denominator: 50 reference items in 20 labels.\n\n"
        "## A. Extraction\n"
        "| Mode | Own item | Merged | Omitted |\n"
        "|---|---|---|---|\n"
        "| Paste | 10/50 | 5 | 5 |\n\n"
        "## B. Classification (20 judged labels)\n"
        "| Mode | Correct confident | Wrong confident | Abstained |\n"
        "|---|---|---|---|\n"
        "| Paste | 5 | 2 | 3 |\n",
        encoding="utf-8",
    )

    rollup = parse_batch_scores(batch_dir)
    assert rollup.has_tie_out_gap is True
    assert any("Gap: 30" in to for to in rollup.tie_outs)
    assert any("Gap: 10" in to for to in rollup.tie_outs)

    # run_rollup with mock repo holding gap batch
    fake_repo = tmp_path / "mock_repo"
    (fake_repo / "evaluation" / "fresh_batch_1").mkdir(parents=True)
    (fake_repo / "evaluation" / "fresh_batch_2").mkdir(parents=True)
    (fake_repo / "evaluation" / "fresh_batch_1" / "SCORES.md").write_text(
        scores_md.read_text(encoding="utf-8"), encoding="utf-8"
    )
    (fake_repo / "evaluation" / "fresh_batch_2" / "SCORES.md").write_text(
        scores_md.read_text(encoding="utf-8"), encoding="utf-8"
    )

    with pytest.raises(ValueError, match="Tie-out validation failed"):
        run_rollup(repo_root=fake_repo, force=True)


def test_refuse_output_equal_to_input_artifact(tmp_path: Path):
    """Refuse to overwrite an input artifact file even with --force."""
    repo_root = Path(__file__).resolve().parent.parent
    scores_file = repo_root / "evaluation" / "fresh_batch_1" / "SCORES.md"

    with pytest.raises(ValueError, match="Refusing to write to input evaluation artifact"):
        run_rollup(repo_root=repo_root, force=True, output_path=scores_file)


def test_run_rollup_refuse_overwrite_without_force(tmp_path: Path):
    """Test that existing output file is not overwritten without --force."""
    out_file = tmp_path / "ROLLUP.md"
    out_file.write_text("Existing content", encoding="utf-8")

    repo_root = Path(__file__).resolve().parent.parent

    with pytest.raises(FileExistsError, match="already exists"):
        run_rollup(repo_root=repo_root, force=False, output_path=out_file)

    assert out_file.read_text(encoding="utf-8") == "Existing content"

    # With force=True, it succeeds
    run_rollup(repo_root=repo_root, force=True, output_path=out_file)
    content = out_file.read_text(encoding="utf-8")
    assert "# Frozen Evaluation Rollup (fresh_batch_1 & fresh_batch_2)" in content


def test_main_cli_exit_codes(tmp_path: Path):
    """Test CLI return codes for normal execution, overwrite collision, and validation failure."""
    repo_root = Path(__file__).resolve().parent.parent

    # 1. Normal run to custom output path returns 0
    custom_out = tmp_path / "test_out.md"
    ret0 = main(["--output", str(custom_out)])
    assert ret0 == 0
    assert custom_out.is_file()

    # 2. Overwrite collision without --force returns 2
    ret2 = main(["--output", str(custom_out)])
    assert ret2 == 2

    # 3. Input collision returns 3 (Validation Error)
    input_scores = repo_root / "evaluation" / "fresh_batch_1" / "SCORES.md"
    ret3 = main(["--output", str(input_scores), "--force"])
    assert ret3 == 3
