# Fresh batch 3: selection rule, written BEFORE any product is drawn

Frozen build under test: code commit dd13c04 (this README is committed before the draw; references are committed before any run). One batch for the whole fix round that followed batch 2:
the dairy vocabulary and provenance line of the milk-plus-culture rule, removal of the function-class hint, and negation scoped to its exact span.

Pool: Open Food Facts products from India (countries_tags en:india), code prefix 890, English ingredients text of at least 10 characters, an ingredient-panel photo on record.
Excluded: every product code of batches P, F, N, M and every code listed or seen during development. Same-brand products are skipped within a part. No product is replaced after drawing, except one whose photo shows no ingredient list at all (excluded with the reason, before scoring).

Part A, plain dairy (10 labels, to exercise the fixed rule on real labels): categories en:milks, en:yogurts, en:dairies in that order, pages 1 to 4, sorted by scan count; the first 10 whose ingredients text has at most 5 comma-separated items,
mentions milk, curd, dahi, yogurt, yoghurt or culture, and contains none of: sugar, sweetener, flavour, colour, INS or E-number codes; distinct brands.
Part B, controls (5 labels): (B1) 2 sweetened or flavoured dairy labels (same categories and order; text mentions sugar, sweetener or flavour; at most 12 items) to confirm the rule does NOT fire; (B2) 2 labels whose ingredients text holds a negation
("contains no", "no added", "free from", "does not contain") from en:dairies, en:biscuits-and-cakes, en:sauces, en:beverages, en:chocolates, en:salty-snacks in that order, pages 1 to 3; (B3) 1 code-heavy label (at least 4 INS/E codes) from en:sauces, pages 2 to 3.

Pasted input = the untouched Open Food Facts text. Photos are not copied (URLs in manifest.json). References (item lists, expected group or "unjudged", with basis) are written from the photos by an LLM before anything is run, committed, then spot-checked by the owner;
they are provisional. No code change and no tuning while scoring; one frozen-build sample, no general accuracy claim. Development overlap by product family is flagged and results are given with and without it.
