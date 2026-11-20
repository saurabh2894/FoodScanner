# Out-of-sample draw for herb_spice_bulk_1 (selection rule written BEFORE any product is drawn)

Purpose: the frozen 66 inputs contain none of the new terms (flip 0/66 is silent on coverage). This draw takes REAL public labels that contain them, so the merged-with-batch build can be run on text it has never seen.
No label is fabricated, edited or replaced. SYNTHETIC unit cases live only in tests/ (marked synthetic) and are never counted here.

Source and terms (same as the existing corpus): Open Food Facts public API (https://world.openfoodfacts.org/api/v2/search), pasted input = the untouched `ingredients_text_en` string. Terms as recorded in the earlier manifests: "Open Food Facts: database ODbL, images CC BY-SA as stated by that site (not independently verified here)".
Used for evaluation only; nothing from Open Food Facts is incorporated into vocabulary or resource tables (ODbL share-alike fit unresolved).

Selection rule (deterministic given the API snapshot; scripts/oos_draw.py implements exactly this):
1. Targets: the staged terms that would become recognised: allspice, basil, celery seed, chervil, coriander leaf, coriander seed, dill weed, dill seed, marjoram, oregano, paprika, parsley, peppermint, rosemary, saffron, sage, savory, spearmint, tarragon, thyme, anise seed, caraway seed, cumin seed, fenugreek seed. Not targeted (parked): poppy seed.
2. Pool per target: products with countries_tags en:india AND ingredients_tags containing the Open Food Facts tag for that term (en:<term with spaces as hyphens>), `ingredients_text_en` of at least 10 characters. A target whose tag returns no product in the pool is reported as "no label found"; no other tag or country is substituted.
3. Excluded: every product code used anywhere in this repository's evaluation, development or test data (66 codes found by text search of evaluation/, data/, src/, tests/, research/).
4. Order: ascending numeric product code. Take the first 2 products per target; skip a product whose brand (lower-cased) is already in the draw or whose code is already drawn for another target; a product matching several targets counts for the first target in the list above and is still scored for all.
5. No replacement after the draw. A label whose text turns out not to be an ingredient list is kept and reported (no photo check is possible in this environment: stated limit).
6. The run records the retrieval date. The corpus is a snapshot of a live database: re-running later may draw different labels.

No expected NOVA group is claimed for these labels; they measure vocabulary recognition only (what the new rows recognised, what stayed unassessed, any mis-recognition), judged by reading each pasted text.
