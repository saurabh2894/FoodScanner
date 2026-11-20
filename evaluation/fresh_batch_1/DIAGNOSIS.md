# Diagnoses for the fix round (written against the frozen build 12e7226, before the fixes)

## A. Silent merges and splits (item 5): case, wrong output, general rule
| Case | Item text | Wrong output | General rule that catches it | Done |
|---|---|---|---|---|
| paste N02 | `nature identical flavouring substance and dough conditioner (223)` | one item (2 reference items merged), completeness "complete" | Pair splitting required BOTH sides to be recognised. "dough conditioner" is not an additive class word, so the side was "unrecognised". A part that ends in a bracket holding only additive codes is itself the mark of an additive item. Flavourings carry no INS numbers (CXG 36 introduction), so a trailing code is not a shared list when an earlier part is a flavouring | fixed |
| paste N13 | `thickeners - E1442, E1450` | split into `thickeners - E1442` and a bare `E1450` | an item that is only an additive code continues the previous item's code list | fixed |
| paste N13 | `nature identical and natural flavouring substances` | one item; the reference counts two | not a bug: one declared phrase with two modifiers and one head noun, nothing is lost. Convention difference in my reference | not changed (documented, test pins it) |
| paste N14 | `Dry Fruits, Nuts & Seeds (22%) {...}` | split at the comma into `Dry Fruits` and `Nuts & Seeds (22%) {...}` | in a list whose groups are separated by semicolons, a chunk shaped NAME, NAME (NN%) {sub-list} keeps its commas: the percentage belongs to the group, so everything before it is the group name | fixed (semicolon lists only) |
| paste N15 | `Roasted Peanuts (91%) Sugar` (comma missing in the source text) | one item, completeness "complete" | a closing percentage bracket followed by another word usually means a missing comma. Splitting would guess, so it is flagged: completeness "uncertain" plus a warning | detection only |
| paste N16 | `Wheat Flour (Atta) (6.5%) Milk Solids (6%)` and a stray `[`/`(` swallowing the rest | merges | same percentage rule (flagged); the unclosed bracket is already named in a warning (previous round) | flagged |
| photo N07 | OCR read only `Just two! ... cocoa nibs (45%)` | 2 reference items omitted, no warning | OCR damage (table layout with dotted leaders), not a parser rule. The abstention is correct | not changed |
| photo N08 | `Pasteurised Toned Milk J Active Lactic Cul...` | 3 reference items in one garbled item | OCR damage plus an unrecognised phrase (`probiotic culture`) | not changed |
| paste N08 | `Active Lactic Culture and Probiotic Culture (...)` | one item | `probiotic culture` is not established as a starter culture (FSSAI 2.1.13 lists "Prebiotics and Probiotics" apart from starter cultures), so the pair is not split | not changed |

## B. Photos where no list was found: which stage lost it
Evidence: OCR text of the frozen browser run (`frozen_results_12e7226/photo_results.json`), the current heading search, the current block inference, and the share of reference items that are readable in the OCR text.
| Photo | Reference items readable in the OCR text | Heading | Block inference | Stage that lost the list | General cause fixed |
|---|---|---|---|---|---|
| N01 | 9/12 | not read at all | rejected: 2 of 8 items recognised (words fused) | block inference on partial, garbled text | no |
| N02 | 6/12 | not read | rejected: one 1,568-character noisy block with no comma structure | OCR output mostly unusable | no |
| N03 | 10/14 | not read | rejected: 9.2 words per item against a limit of 6 | heading not read; inference counted the words inside brackets | YES: the length test now ignores bracket contents. The block is now found (inferred heading) and flagged uncertain |
| N10 | 3/8 | read as `Tedieniy`, beyond the tolerant match | rejected: 9.2 words per item | OCR partial; heading damaged | no |
| N14 | 4/8 | not read | rejected: no comma structure | OCR mostly unusable (curved bottle) | no |
| N15 | 0/4 | not read | none | OCR unusable | no |
| N16 | 0/14 | not read | none | OCR unusable | no |
N13 was a different failure (wrong block): the word INGREDIENTS inside a marketing line was taken as the heading. Fixed by the heading position rule; the photo now reports "no list found" instead of a wrong block marked complete.

## C. INS digit misreads on the millet puff pack (`tests/fixtures/millet_puff_label.jpg`, the printed codes are INS330, INS296, INS334, INS 508, INS 392)
| Stage | INS codes read |
|---|---|
| Browser, first reading (tesseract.js, stretch + sharpen) | 330, **236**, 334, 508, **382** (this reproduces the reported screenshot) |
| Browser, second reading (lighting-corrected), forced for this diagnosis in a scratch copy | 330, **236**, 334, 508, **392** |
| Native tesseract, plain / stretch+sharpen / lighting-corrected | 296 or 295, 392 (a different engine build: not the same errors) |
Findings: 296 became 236 in BOTH browser readings (they agree, so a two-reading comparison cannot catch it); 392 became 382 only in the first reading (the readings disagree). The second reading did not run for this label because the first looked clean (Group 4, completeness complete), so there was no disagreement signal. The second pass now also runs when the first reading holds additive codes, and a disagreement on codes is shown as a review hint, never resolved.
