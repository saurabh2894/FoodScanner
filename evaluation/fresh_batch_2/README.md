# Fresh batch 2: selection rule, written BEFORE any product is drawn

Frozen build under test: code commit 2eb5f39 (this README is committed before selection, references are committed before any run).

Pool: Open Food Facts products from India (countries_tags en:india), code prefix 890, English ingredients text of at least 20 characters, an ingredient-panel photo on record.
Excluded: every product code of batches P (development texts), F (development photos), N (fresh batch 1), and every code ever listed or seen during development
(the candidate lists good.json, good2.json, chosen.json). Same-brand products are skipped within a part.

Part A, plain dairy (8 labels, so that the milk-plus-culture rule can fire on real labels): products of the categories en:dairies, en:milks, en:yogurts in that order, pages 1 to 3, sorted by
scan count; the first 8 whose ingredients text has at most 6 comma-separated items, from distinct brands.
Part B, code-heavy (7 labels, to exercise the misread-hint and two-reading paths): categories en:biscuits-and-cakes, en:instant-noodles, en:salty-snacks, en:sauces, en:beverages, en:spreads,
en:chocolates, en:breakfast-cereals in that order, pages 2 and 3, sorted by scan count; the first product per category whose ingredients text holds at least 4 INS/E code occurrences, from a brand not already
chosen, until 7 are drawn.
No product is dropped or replaced after drawing, except one whose photo shows no ingredient list at all (it is then listed as excluded with the reason, before scoring).

Pasted input = the untouched Open Food Facts text. Photos are not copied into the repository (URLs in manifest.json). References (item lists, expected group or "unjudged", with basis) are written from the
photos by an LLM before anything is run, committed, and then spot-checked by the owner; they are provisional. No code change and no tuning against this batch while scoring; the batch is one frozen-build sample.
Photo timing: every browser OCR call is timed, to measure what the second reading adds.

## Drawn labels and flags (added at pre-registration, before any run)
Drawn by the rule above: M01 to M15. Excluded before scoring: M02 (the photo on record shows a nutrition table, no ingredient list). Development overlap by product family (not by code, so the
rule did not exclude them): M01 (Amul butter, P06), M04 and M05 (Smoodh, F06; M04 and M05 carry the same recipe text), M10 (Maggi, P02), M14 (Kissan jam, F14, same text). Results are reported for all scored
labels and again without these six. M13's item list is unjudged (unreadable photo); its group is judged from the readable fragments.
