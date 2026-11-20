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
    parse_batch_scores,
    parse_markdown_table,
    run_rollup,
)


def test_parse_real_fresh_batches(tmp_path: Path):
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
    assert rollup_b1.extraction_denominator == "121 reference items in 15 labels"
    assert "13 labels" in (rollup_b1.classification_denominator or "")
    assert len(rollup_b1.extraction_table) == 2
    assert len(rollup_b1.classification_table) == 2
    # Batch 1 has 'Split into several'
    assert any(r.split is not None for r in rollup_b1.extraction_table)

    # Batch 2 checks
    assert rollup_b2.name == "fresh_batch_2"
    assert "2eb5f39" in rollup_b2.title
    assert "14 judged labels" in (rollup_b2.classification_denominator or "")
    assert len(rollup_b2.extraction_table) == 2
    assert len(rollup_b2.classification_table) == 2
    # Batch 2 does NOT have split column
    assert all(r.split is None for r in rollup_b2.extraction_table)
    # Batch 2 has extra column 'Without the 5 overlapping labels (9)'
    assert any("Without" in k for r in rollup_b2.classification_table for k in r.extra_columns)


def test_tie_outs_real_batches():
    """Verify tie-out checks on the real batches."""
    repo_root = Path(__file__).resolve().parent.parent

    b1_dir = repo_root / "evaluation" / "fresh_batch_1"
    b2_dir = repo_root / "evaluation" / "fresh_batch_2"

    b1 = parse_batch_scores(b1_dir)
    b2 = parse_batch_scores(b2_dir)

    # Fresh batch 1 tie outs
    assert any("Extraction items (Paste): 92 own + 17 merged + 2 split + 10 omitted = 121/121 (Ties out exactly)" in to for to in b1.tie_outs)
    assert any("Extraction items (Photo): 18 own + 10 merged + 0 split + 93 omitted = 121/121 (Ties out exactly)" in to for to in b1.tie_outs)
    assert any("Classification labels (Paste): 8 correct + 0 wrong + 5 abstained = 13/13 (Ties out exactly)" in to for to in b1.tie_outs)
    assert any("Classification labels (Photo): 2 correct + 0 wrong + 11 abstained = 13/13 (Ties out exactly)" in to for to in b1.tie_outs)

    # Fresh batch 2 tie outs
    assert any("Extraction items (Paste): 77 own + 6 merged + 11 omitted = 94/94 (Ties out exactly)" in to for to in b2.tie_outs)
    assert any("Extraction items (Photo): 27 own + 23 merged + 44 omitted = 94/94 (Ties out exactly)" in to for to in b2.tie_outs)
    assert any("Classification labels (Paste): 11 correct + 0 wrong + 3 abstained = 14/14 (Ties out exactly)" in to for to in b2.tie_outs)
    assert any("Classification labels (Photo): 4 correct + 0 wrong + 10 abstained = 14/14 (Ties out exactly)" in to for to in b2.tie_outs)


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
    # The table fails separator check so it returns empty table without raising an unhandled exception
    assert rollup.extraction_table == []


def test_synthetic_missing_sections(tmp_path: Path):
    """Test honest handling when sections are completely missing."""
    batch_dir = tmp_path / "sparse_batch"
    batch_dir.mkdir()
    scores_md = batch_dir / "SCORES.md"
    scores_md.write_text(
        "# Sparse Batch\n\n"
        "Only text notes here, no markdown tables at all.\n",
        encoding="utf-8",
    )

    rollup = parse_batch_scores(batch_dir)
    assert "Extraction table" in rollup.unrecorded_fields
    assert "Classification table" in rollup.unrecorded_fields
    assert rollup.extraction_table == []
    assert rollup.classification_table == []
    assert rollup.warnings_worked == []
    assert rollup.warnings_not_worked == []


def test_synthetic_tie_out_gap_detection(tmp_path: Path):
    """Test that arithmetic gaps in denominators are detected and reported honestly."""
    batch_dir = tmp_path / "gap_batch"
    batch_dir.mkdir()
    scores_md = batch_dir / "SCORES.md"
    scores_md.write_text(
        "# Gap Batch\n\n"
        "Judged for classification: 20 labels.\n\n"
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

    # Extraction gap: 10 + 5 + 5 = 20 / 50 -> Gap of 30
    assert any("Gap: 30" in to for to in rollup.tie_outs)
    # Classification gap: 5 + 2 + 3 = 10 / 20 -> Gap of 10
    assert any("Gap: 10" in to for to in rollup.tie_outs)


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
