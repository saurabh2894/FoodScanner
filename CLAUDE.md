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
  Every "Contains ..." sentence after the list is read (allergen clauses are dropped; additive clauses are shown as
  "Declared on a Contains line" and count as evidence, never as list items).
- Completeness signal: each result carries `completeness` (text-span coverage: words read as ingredients / not read /
  set aside / unaccounted, plus reasons). It is never a claim of exact completeness. Unaccounted words, a damaged
  or inferred heading, unbalanced brackets or unread ingredient-like text make it "uncertain" and block every answer
  except a strong-marker Group 4 (Option A). Photo path: a damaged heading ("REDIENTS") is matched tolerantly; with
  no heading the most list-like block is used, never a nutrition table or allergen-only line; else ask for a clearer photo.
- Colour-alone policy, decided by the user ("Option B", Amul Butter review): if the ONLY strong evidence is a
  colouring (class word, colour INS code, or a Contains colour declaration), the result is "Not enough information"
  with that reason. Any other strong marker alongside it still gives Group 4. Basis: research/02 prefers "uncertain" over
  a forced call on weak/ambiguous markers and names no butter/annatto rule. A cited source on natural colours may revisit it.
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

## Deploy flow
Production is `main` -> Vercel (project "foodscan", Git-connected). Do NOT run `vercel deploy` by hand. Work on a
branch, get approval, then push to `main`; Vercel runs the repo-root vercel.json build (fetch the photo-reader
files, run the parity check, build web_preview/dist) and publishes it. The build needs only python3, node and npm.
Preview deploys of other branches sit behind Vercel Authentication.

## Workflow
- Small commits, tests passing before each commit. One task per branch.
- OCR is behind an interface (foodscan.ocr.OcrEngine) so a vision model can replace it later.
- Tests never require the tesseract binary except those marked `ocr` (auto-skipped if absent).
