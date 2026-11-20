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
- Declared colour marker (provisional, research/04): counts only as a declared ADDED colour ("Colour (INS 150d)", "Natural
  colour (annatto)", "Food colour - E122", a Contains line). A colour word that is only a bracketed function note on a named
  food ("Turmeric (Colouring & Spices)", "Annatto (colour)") is not read as an added colour; the result says so. Results are
  label-based NOVA classifications, never safety or health findings.
- The INS reference table (Codex CXG 36) is parked in data/pending/ and must not be shipped (licence and edition unresolved, research/05).
- Milk-plus-culture rule (research/04): a list that is recognised in full and is only milk (milk, toned milk, double toned milk) plus starter
  culture(s) is Group 1 (NUPENS-USP: plain yoghurt with no added sugar or sweeteners). Anything else keeps its existing behaviour; not keyed off product words.
- Vocabulary rows: the cited source must name that exact term, else the row stays PROVISIONAL with the missing source stated. The NUPENS-USP page is a NOVA method source only.
- Heading: the word "Ingredients" must sit in heading position or form (start of text/line/sentence, or followed by a colon or dash); marketing and attribution
  text that merely contains it is not a heading. Section labels may carry a bracketed percentage ("Noodles (88.5%):"). A text block with few recognised items
  and no code or marker on the photo path is flagged "uncertain" (it may not be an ingredient list).
- INS codes: a code is never replaced and never reclassified by a review hint. Two hints only: (1) the label's own additive name is tied to a DIFFERENT code by a page that was
  read (ins_names.csv, WHO JECFA pages read in full, research/04), (2) two photo readings that disagree on a code. The class-word versus function check was removed (it flagged
  INS 508 under "Thickeners" on a legitimate pack). ins_names.csv rows are display names only ("Recognised code, no processing rule yet"). Agreement of two readings is not
  reassurance. No Codex-derived data is used. The completeness line is text coverage, not a guarantee that characters, digits or the list are correct.
- Contains lines: negation is scoped to its exact span. "Contains no added flavours, added colour or preservatives" declares nothing; in a mixed line only the positive span is a
  declaration ("No added colours, contains preservative (INS 211)"); "free from nuts" and "may contain" are never drivers.
- Milk context: milk, toned milk, double toned milk, buffalo milk and milk solids (PROVISIONAL) plus starter culture(s) is Group 1; a trailing "Made from <milk>" provenance line is
  set aside (counted, not an ingredient). Not a general dairy matcher.
- Role phrases "emulsifying agent" and "stabilizing agent" map to their class words (PROVISIONAL). "probiotic culture" is NOT a starter culture (research/04).
- yeast extract and pea protein are NOT markers (in no research/ file; pea protein does not say concentrate or
  isolate). They stay outside the vocabulary and appear under "Not assessed". Adding either needs a cited source.
- Sweetener class word (owner decision): an entry named only "sweetener" whose bracket names only recognised foods and no INS code ("Sweeteners (Jaggery Powder, Dates Powder)") is not read as an added sweetener class (FAO 2019 lists *artificial* sweeteners); the result says so. Any non-food name or code keeps the marker. Basis in research/04; the lexicon row "dates" is PROVISIONAL.
- Vocabulary gap versus truncation: a list is called truncated only when the last item looks cut off (word fragment, start of a longer term, unclosed bracket). An unknown whole word is reported as "not in the local vocabulary" and named; groups and gating are unchanged. Soybean is a PROVISIONAL lexicon row (research/04).
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
