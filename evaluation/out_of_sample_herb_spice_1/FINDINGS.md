# Findings: targeted out-of-sample challenge set for the staged terms of herb_spice_bulk_1

Not a coverage estimate. The draw searched for labels containing the staged terms, so it cannot measure general recognition, and no figure here is a share of Indian foods or labels. Texts are in a gitignored cache (README section 2); this file holds counts and term names only.
Builds: BEFORE = commit 6cf9a99~1 (without the batch), AFTER = 6cf9a99 plus later non-resource commits; each analysed in its own fresh process (scripts/oos_eval.py); every text matched its manifest sha256.

## Selection picture (details per target in manifest.json `per_target` and results.md)
- Rule: README (pre-registered in 66195ea). 24 targets; Open Food Facts API snapshot retrieved 2026-11-20; exclusion list = 66 repository product codes (1 of them removed one rosemary product from the pool).
- Exclusions applied: short or missing text (8 products across targets), used codes (1), same-brand or already-drawn skips (15 skips). 32 labels drawn (2 per target where possible).
- No label drawn for 7 of 24 targets: allspice, chervil, dill weed, marjoram, savory, anise seed (the API returned 0 products for the target's ingredient tag in the India pool; this cannot tell "no such product" from "tag not used") and tarragon (1 eligible product, skipped by the same-brand rule). These targets are UNTESTED by this set, not passed.
- Several drawn labels carry non-890 barcodes (imported products sold in India). No photo check was possible: whether a text is a complete ingredient list is unverified.

## Results (66 mentions of staged terms in 32 labels)
- recognised 40; NOT recognised 24; inside another item 2. Per target: results.md.
- The 24 NOT recognised, by cause (my reading of each text; list per label in results.md):
  - 11: plural or leaf form of a term that is in the vocabulary only in the singular ("cumin seeds", "fenugreek seeds", "caraway seeds", "coriander leaves", "Fenugreek Seeds Whole"). Synonyms match the singular only: this is the known gap pinned by the xfail tests in tests/test_herb_spice_bulk_1.py, now seen on real labels.
  - 4: correct abstentions on a different part or processed form: raw basil seeds, paprika oleoresin, coriander leaf extract, spice extract (paprika).
  - 9: the term sits in a compound the parser keeps as one item: "A & B" pairs ("Thyme & Rosemary"), a full-stop join ("Basil. Parsley"), an item with an unknown word ("Shepa (Dill Seeds)"), a bracketed sub-list ("Spices (White Pepper & Celery Seed Powder)"), an asterisk or trailing weight ("peppermint* (9%)", "... powder (Latin name) 0.18 g").
- No mis-recognition found: every newly recognised item is a plain herb or spice name (with powder, seed or seeds), and no extract, oleoresin or different-part form was recognised.
- Changes between the builds: group unchanged on all 32 labels. 6 labels changed only the abstention reason text (it lists the shorter unassessed set). 1 label (S19) changed status uncertain -> complete with group 4 unchanged; one item "X (0.6%): Y" was split after the recognition, leaving the second half newly unassessed (existing parser behaviour exposed by the recognition; no tuning done). Under the flip discipline this is a status change attributable to the staged rows paprika and rosemary: reported, for owner judgement.

## Decisions for the owner (nothing tuned on this set)
1. Plural and leaf forms (11 of 24 misses): add plural synonyms (cumin seeds, caraway seeds, fenugreek seeds, anise seeds) and "leaves" forms, or a general plural rule for synonyms? Either is a new reviewed change with its own flip check; not made here, because the set was pre-registered for no tuning.
2. Compound items (9 of 24): parser behaviour, outside this batch.
3. S19 status change: accept as an attributable, group-neutral effect, or hold the rows back.
4. Untested targets (7): a different tag or country pool would be a new pre-registered draw.
