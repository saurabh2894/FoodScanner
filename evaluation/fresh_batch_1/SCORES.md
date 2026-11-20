# Fresh batch 1: scores for ONE frozen build (code commit 12e7226)

Frozen build: code at `12e7226`; the reference commit `608fc6c` adds only evaluation files (no change under src/, web_preview/, scripts/, tests/ between them). No code was changed while scoring and nothing was tuned to this batch. One sample, 15 labels scored (16 drawn; N04 excluded before scoring as a variant of a development product): not a general accuracy figure. References were written by an LLM from the photos before any run and have not been spot-checked by the owner. Item adjudication for OCR-garbled items counts an item as present when a human can recognise it; those counts are approximate. All numbers are from `frozen_results_12e7226/`.

Judged for classification: 13 labels (N07 and N10 unjudged). Extraction denominator: 121 reference items in 15 labels.

## A. Extraction (items; each reference item counted once)
| Mode | List found in the right place | Own item, recognisable | Merged into another item | Split into several | Omitted | Additions (app items with no reference item) |
|---|---|---|---|---|---|---|
| Paste (untouched Open Food Facts text) | 15/15 labels | 92/121 | 17 | 2 | 10 | 0 (stray text glued into an item on N03 and N09) |
| Photo (browser OCR, with second pass when needed) | 7/15 labels (1 wrong block, 7 no list) | 18/121 | 10 | 0 | 93 (72 of them in the 7 no-list photos) | 8 |

- Paste merges: N02 (flavouring + dough conditioner), N08 (two cultures), N13 (nature-identical + natural flavouring), N15 (missing comma), N16 (missing comma, then an unclosed bracket swallows 7 items). Splits: N13 (thickeners + code), N14 (the group name 'Dry Fruits, Nuts & Seeds'). Omitted: N03's whole second section (10 items), set aside under "not read" and flagged.
- Photo: OCR read error versus parser error. No heading text was read on N01, N02, N03, N10, N14, N15 and N16, so no list was found. On N01, N03 and N14 the list text was partly read, so block inference could not recover them; on N02, N10, N15 and N16 the OCR was mostly garbage. N13 is a parser error: the word INGREDIENTS inside a marketing line ('COOKING INGREDIENTS & MEALS') was taken as the heading, giving the wrong block, with completeness reported "complete".

## B. Classification (judged labels only, 13)
| Mode | Correct confident group | Wrong confident group | Abstained |
|---|---|---|---|
| Paste | 8 (all Group 4: N01, N02, N05, N06, N13, N14, N15, N16) | 0 | 5 (N03 section unread, N08 and N09 vocabulary, N11 weak/unlisted only, N12 emulsifying agent not recognised as an emulsifier) |
| Photo | 2 (N05, N06) | 0 | 11 |
- Unjudged (excluded): N07 and N10, abstained in both modes. Abstentions are their own outcome, not counted as failures or successes.
- The milk-plus-culture rule fired on 0 of 15 labels (N08's 'probiotic culture' and N09's 'buffalo milk' are not in the vocabulary).

## C. Did uncertainty warnings work?
- Worked: paste N03, N08, N16; photo N05, N11, N12 (completeness uncertain with reasons or warnings); every Group 4 given on an incomplete reading carried a warning.
- Did not work (extraction wrong, completeness "complete", no warning): paste N02, N13, N14, N15; photo N07 (2 items omitted), N08 (3 items merged), N13 (wrong block). None of these produced a wrong confident group (paste answers were correct; the photo cases abstained).

Not general accuracy. Not validation. A later independent check needs another fresh batch.
