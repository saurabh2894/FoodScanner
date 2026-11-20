# foodscan

Local app: photo of an Indian packaged-food ingredient label -> OCR -> NOVA processing level.
Reports processing level only. Local only (localhost), no paid APIs, no network calls.

## Standing rules
- Output "Not enough information" plus a reason whenever evidence is weak (little OCR text,
  no ingredient list, truncated list, or uncertain classification). Never output a guessed group.
- Exception, decided by the user ("Option A"): a list that looks truncated (unclosed bracket, or cut off
  mid-word) still gets Group 4 if a STRONG marker is already present, because missing text cannot remove a
  marker. The result carries a "List may be incomplete" warning. All other truncated cases abstain.
- "Contains ..." statements count as evidence ONLY when they declare an additive class (colour, flavour,
  sweetener, emulsifier, ...). Allergen statements ("Contains soy, milk") and "May contain" never do.
  Known gap: only the first sentence after the ingredient list is read, so a later "Contains permitted colour"
  is missed (this errs on the cautious side).
- yeast extract and pea protein are NOT markers (in no research/ file; pea protein does not say concentrate or
  isolate). They stay outside the vocabulary and appear under "Not assessed". Adding either needs a cited source.
- Results list what could not be judged ("Not assessed"); unrecognised ingredients are never invisible.
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

## Browser version
web_preview/ holds a JS port of the classifier published as a single-page artifact. Python is the source of
truth. After ANY rule or table change: `python scripts/parity_check.py` (must be all identical), then
`python scripts/build_web_preview.py` (refuses to build if parity fails) and republish web_preview/dist/.

## Static hosting
`python scripts/build_web_preview.py` writes web_preview/dist/foodscan-preview.html (for the artifact host,
which adds its own document skeleton) and dist/index.html (wrapped with doctype, lang, viewport, description,
favicon for ordinary static hosts such as Vercel). Run scripts/fetch_tesseract_assets.py once first.

## Workflow
- Small commits, tests passing before each commit. One task per branch.
- OCR is behind an interface (foodscan.ocr.OcrEngine) so a vision model can replace it later.
- Tests never require the tesseract binary except those marked `ocr` (auto-skipped if absent).
