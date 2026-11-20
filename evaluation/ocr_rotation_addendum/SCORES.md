# OCR rotation fallback and retake guidance: before/after on the existing failure sets

Our own benchmark evidence on the photos already used in this project (batches 1-3 and the negation addendum), not independently validated accuracy. No new label was drawn. 22 photos were no-list in the frozen results of their batch (batch 1: 7, batch 2: 7, batch 3: 6, negation addendum: 2).
References for the batches are LLM-prepared and still need the owner's spot-check; this table counts only whether an ingredient list was found, and how many items were extracted, not whether they are correct.

What changed (build after 78d99e9, same OCR engines, nothing paid): when the first reading and the lighting-corrected second reading find no ingredient list, retry with the photo turned 90, 270, then 180 degrees clockwise (browser: tesseract.js; Python: tesseract). A rotated reading is used only if it finds a list;
the first with 3 or more recognised items stops the retries. If no list is found even then, the result carries concrete retake guidance (flat surface, even light, straight-on and close, text upright) or the option to paste the text.
"Before" is the previous build (78d99e9) run now on the same photos, so improvements made to the parser since each freeze are not credited to rotation. Browser runs are headless Chromium with tesseract.js on this container's CPU; absolute seconds are slower than a phone would be, ratios are the point.

## Per photo (browser): previously no-list, now found or not, items recovered, added OCR time
| Photo | Frozen result from | Frozen | Before (no rotation, current parser) | After (with rotation) | Items recovered by rotation | Added OCR time (before to after total) | Native tesseract (Python): items without to with rotation |
|---|---|---|---|---|---|---|---|
| N01 | batch 1 (12e7226) | no list | no list | no list | +0 | 4.3 s (3.3 to 7.6) | 4 to 4 |
| N02 | batch 1 (12e7226) | no list | no list | no list | +0 | 24.4 s (16.4 to 40.8) | 12 to 12 |
| N03 | batch 1 (12e7226) | no list | list (4 items) | list (4 items) | +0 | 0.0 s (6.9 to 7.1) | 0 to 4 |
| N10 | batch 1 (12e7226) | no list | no list | no list | +0 | 3.0 s (2.1 to 5.0) | 0 to 0 |
| N14 | batch 1 (12e7226) | no list | no list | no list | +0 | 25.6 s (11.9 to 37.5) | 0 to 0 |
| N15 | batch 1 (12e7226) | no list | no list | no list | +0 | 65.8 s (22.0 to 87.8) | 0 to 0 |
| N16 | batch 1 (12e7226) | no list | no list | no list | +0 | 195.1 s (56.3 to 251.4) | 0 to 0 |
| M03 | batch 2 (2eb5f39) | no list | list (3 items) | list (3 items) | +0 | 0.0 s (2.4 to 2.1) | 3 to 3 |
| M06 | batch 2 (2eb5f39) | no list | no list | no list | +0 | 18.4 s (11.5 to 29.9) | 0 to 0 |
| M08 | batch 2 (2eb5f39) | no list | no list | no list | +0 | 16.6 s (8.4 to 24.9) | 0 to 0 |
| M10 | batch 2 (2eb5f39) | no list | no list | no list | +0 | 11.8 s (4.4 to 16.1) | 7 to 7 |
| M13 | batch 2 (2eb5f39) | no list | no list | no list | +0 | 138.8 s (57.4 to 196.2) | 0 to 0 |
| M14 | batch 2 (2eb5f39) | no list | no list | no list | +0 | 45.9 s (23.3 to 69.2) | 0 to 0 |
| M15 | batch 2 (2eb5f39) | no list | no list | no list | +0 | 117.0 s (53.7 to 170.7) | 0 to 5 |
| Q02 | batch 3 (dd13c04) | no list | no list | no list | +0 | 34.9 s (16.8 to 51.7) | 0 to 0 |
| Q05 | batch 3 (dd13c04) | no list | no list | no list | +0 | 10.1 s (5.3 to 15.5) | 0 to 0 |
| Q09 | batch 3 (dd13c04) | no list | no list | no list | +0 | 8.9 s (3.7 to 12.7) | 0 to 0 |
| Q10 | batch 3 (dd13c04) | no list | no list | no list | +0 | 0.7 s (1.6 to 2.3) | 0 to 0 |
| Q13 | batch 3 (dd13c04) | no list | no list | no list | +0 | 7.1 s (5.4 to 12.5) | 0 to 0 |
| Q14 | batch 3 (dd13c04) | no list | no list | no list | +0 | 24.2 s (13.2 to 37.5) | 4 to 4 |
| R1 | negation addendum (dd13c04) | no list | no list | no list | +0 | 49.2 s (19.5 to 68.7) | 0 to 0 |
| R3 | negation addendum (dd13c04) | no list | no list | no list | +0 | 2.9 s (2.9 to 5.8) | 0 to 0 |
## Totals
- Found by rotation in the browser: **0 of 22**. The only two photos that now show a list (N03, M03) show it without rotation too, so that is the parser changes since the freeze, not rotation.
- The fallback ran on 20 photos (not on N03 and M03, which now read a list on the first two readings). Added OCR time on those 20: **804.8 s in total, median 21.3 s, mean 40.2 s, range 0.7 s to 195.1 s per photo**. The retries add three more recognitions per failed photo, roughly tripling the time of the photos that were already slow.
- Python with the native tesseract binary: rotation gave a partly read list on 2 photos (N03: 4 items, M15: 5 items; both garbled, mostly outside the vocabulary, still "Not enough information: ingredient list looks truncated"). Added time on the 17 photos whose native first readings found no list (including those two): 106.7 s in total.
- Orientation as the cause: counting ingredient-vocabulary words per reading, a rotated reading beat the best unrotated reading on 3 of the 20 photos (M13, Q09, Q13) by 1 to 2 words, which is not enough for a list. Q13's 270-degree reading does recover garbled fragments of the sideways bottle text ("COMPARED 10 MOUNTAIN DEW", "330, 331) FLAVOUR", "PRESERVATIVE (11, COLOR 10)", "SWEENEY"), but with no Ingredients heading and a damaged layout the parser still finds no list. In the other 17 the text was upright and damaged (blur, size, glare), which rotation cannot fix.

## Regression checks (browser, same photos before and after)
| Photo | Result before | Result after | Extra OCR calls |
|---|---|---|---|
| Appy (negation R4) | Group 4 | Group 4, identical | 0 |
| Bovonto (R6) | not enough information (truncated bracket) | identical | 0 |
| Budhani wafers (R2) | not enough information (text after a full stop not read) | identical | 0 |
| millet puff fixture (tests/fixtures) | Group 4 | Group 4, identical | 0 |
Negation paste results are covered by tests/test_negation_real_labels.py (unchanged) and the full test suite (532 tests); rotation never ran on a photo where a list was found.

## Reading
The measured benefit of the rotated retries on our failure sets is nil in the browser and marginal (two garbled partial lists, no classification change) with the native binary, at a cost of roughly 3x OCR time on failed photos. The retake guidance costs nothing and is the part that helps a user act.
`ROTATIONS = ()` in src/foodscan/pipeline.py (and `rots` in web_preview/template.html) switches the retries off while keeping the guidance; the guidance sentence would then need its "even after trying it turned..." clause dropped.
