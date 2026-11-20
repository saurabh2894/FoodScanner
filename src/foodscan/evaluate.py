"""Evaluate the classifier over labelled samples.

Reports TWO separate numbers, never one (research/03 "Reading the evaluation"):
  * coverage: answered / total samples
  * accuracy on answered samples vs labels.csv (provisional reference labels,
    not ground truth). Samples with status `uncertain` are excluded from
    accuracy but stay in the abstention analysis.
Lists every wrong call and every abstention.

labels.csv columns: file,nova_ref,status,notes. `file` is resolved next to
labels.csv, then in a samples/ subfolder. `.txt` files are read as label text
(skipping OCR); anything else is treated as an image.
"""
from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from .ocr import OcrEngine, OcrUnavailable, TesseractOcr
from .pipeline import Analysis, analyse_image, analyse_text


@dataclass
class Row:
    file: str
    nova_ref: int | None
    status: str
    notes: str = ""


@dataclass
class Outcome:
    row: Row
    analysis: Analysis


@dataclass
class Report:
    outcomes: list[Outcome] = field(default_factory=list)
    errors: list[tuple[Row, str]] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.outcomes)

    @property
    def answered(self) -> list[Outcome]:
        return [o for o in self.outcomes if o.analysis.answered]

    @property
    def abstained(self) -> list[Outcome]:
        return [o for o in self.outcomes if not o.analysis.answered]

    @property
    def scored(self) -> list[Outcome]:
        """Answered samples that have a confirmed reference label."""
        return [o for o in self.answered if o.row.status == "confirmed" and o.row.nova_ref is not None]

    @property
    def wrong(self) -> list[Outcome]:
        return [o for o in self.scored if o.analysis.group != o.row.nova_ref]

    @property
    def coverage(self) -> float | None:
        return len(self.answered) / self.total if self.total else None

    @property
    def accuracy(self) -> float | None:
        return (len(self.scored) - len(self.wrong)) / len(self.scored) if self.scored else None


def read_labels(path: Path) -> tuple[list[Row], list[tuple[Row, str]]]:
    rows, bad = [], []
    with path.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            status = (r.get("status") or "confirmed").strip().lower()
            ref_raw = (r.get("nova_ref") or "").strip()
            row = Row(r["file"].strip(), None, status, (r.get("notes") or "").strip())
            if ref_raw:
                if ref_raw not in {"1", "2", "3", "4"}:
                    bad.append((row, f"invalid nova_ref {ref_raw!r}"))
                    continue
                row.nova_ref = int(ref_raw)
            if status not in {"confirmed", "uncertain"}:
                bad.append((row, f"invalid status {status!r}"))
                continue
            if row.nova_ref is None and status == "confirmed":
                bad.append((row, "confirmed row needs a nova_ref (or mark it uncertain)"))
                continue
            rows.append(row)
    return rows, bad


def _resolve(base: Path, name: str) -> Path | None:
    for cand in (base / name, base / "samples" / name):
        if cand.is_file():
            return cand
    return None


def evaluate(labels_path: Path, ocr: OcrEngine | None = None) -> Report:
    rows, bad = read_labels(labels_path)
    report = Report(errors=list(bad))
    base = labels_path.parent
    for row in rows:
        path = _resolve(base, row.file)
        if path is None:
            report.errors.append((row, "file not found"))
            continue
        if path.suffix.lower() == ".txt":
            analysis = analyse_text(path.read_text(encoding="utf-8"))
        else:
            analysis = analyse_image(path, ocr or TesseractOcr())  # OcrUnavailable propagates
        report.outcomes.append(Outcome(row, analysis))
    return report


def _pct(x: float | None) -> str:
    return "n/a" if x is None else f"{x:.1%}"


def format_report(rep: Report) -> str:
    L: list[str] = []
    n_ans, n_abs = len(rep.answered), len(rep.abstained)
    excluded = len(rep.answered) - len(rep.scored)
    L.append("== foodscan evaluation (labels are provisional reference labels, not ground truth) ==")
    L.append("")
    L.append(f"Coverage:  {n_ans}/{rep.total} answered ({_pct(rep.coverage)}), {n_abs} abstained")
    L.append(
        f"Accuracy on answered:  {len(rep.scored) - len(rep.wrong)}/{len(rep.scored)} correct ({_pct(rep.accuracy)})"
        + (f"   [{excluded} answered sample(s) excluded: label uncertain]" if excluded else "")
    )
    L.append("(Two separate numbers: judge them together, never one alone.)")

    L.append("")
    L.append(f"Wrong calls ({len(rep.wrong)}):")
    for o in rep.wrong:
        drivers = "; ".join(f"{d.ingredient}: {d.detail}" for d in o.analysis.drivers) or "-"
        L.append(f"  - {o.row.file}: predicted {o.analysis.group}, reference {o.row.nova_ref}  | drivers: {drivers}")
    if not rep.wrong:
        L.append("  (none)")

    L.append("")
    L.append(f"Abstentions ({n_abs}):")
    for o in rep.abstained:
        ref = f"reference {o.row.nova_ref}" if o.row.nova_ref else "no reference"
        L.append(f"  - {o.row.file} ({ref}, label {o.row.status}): {o.analysis.reason}")
    if not rep.abstained:
        L.append("  (none)")

    if rep.errors:
        L.append("")
        L.append(f"Rows skipped ({len(rep.errors)}):")
        for row, why in rep.errors:
            L.append(f"  - {row.file}: {why}")
    return "\n".join(L)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Evaluate foodscan on labelled samples.")
    ap.add_argument("labels", type=Path, help="path to labels.csv")
    args = ap.parse_args(argv)
    try:
        rep = evaluate(args.labels)
    except OcrUnavailable as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except FileNotFoundError:
        print(f"error: labels file not found: {args.labels}", file=sys.stderr)
        return 2
    print(format_report(rep))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
