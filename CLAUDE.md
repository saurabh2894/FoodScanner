# foodscan

Local app: photo of an Indian packaged-food ingredient label -> OCR -> NOVA processing level.
Reports processing level only. Local only (localhost), no paid APIs, no network calls.

## Standing rules
- Output "Not enough information" plus a reason whenever evidence is weak (little OCR text,
  no ingredient list, truncated list, or uncertain classification). Never output a guessed group.
- Never output health judgements ("healthy", "unhealthy", "should not be eaten").
- No ingredient-count rules. Short lists can be UPF; long lists of foods can be group 3.
- Every rule or mapping entry cites its source (research/ file or external reference).
  If research is ambiguous, ask before inventing a rule.
- Evaluation reports coverage and accuracy-on-answered as separate numbers. labels.csv is
  provisional reference data, not ground truth. "uncertain" labels are excluded from accuracy.

## Layout
src/foodscan/ (ocr, parser, normalise, classify, pipeline, cli, evaluate, web), tests/, data/, research/
Resource tables (src/foodscan/resources/*.csv) each carry a `source` column.

## Commands
- Install: pip install -e ".[dev]"   (needs the tesseract binary: brew / apt / UB Mannheim installer)
- Test: pytest
- Classify one photo: foodscan classify path/to/label.jpg   (add --text to pass raw text instead)
- Evaluate: python -m foodscan.evaluate data/labels.csv
- Web app: python -m foodscan.web.app   (127.0.0.1 only)

## Workflow
- Small commits, tests passing before each commit. One task per branch.
- OCR is behind an interface (foodscan.ocr.OcrEngine) so a vision model can replace it later.
- Tests never require the tesseract binary except those marked `ocr` (auto-skipped if absent).
