# Targeted out-of-sample challenge set for the staged terms of herb_spice_bulk_1 (selection rule written BEFORE any product is drawn)

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


## Amendments (written after the rule above was committed in 66195ea, before any product text was read or any result produced)
### 1. What this set is, and is not
A TARGETED out-of-sample challenge set for the 24 staged terms. The draw searches for labels that contain the new terms, so it cannot estimate general recognition: pre-registration fixes the rule, it does not remove that selection bias.
No result here is a percentage of Indian foods or labels, and none may be quoted as coverage. Every claim uses the words "targeted out-of-sample challenge set for the staged terms".
The full selection picture is recorded in manifest.json (`per_target`): per target the API count, products fetched with text, exclusions (short or missing text; codes already used in this repository), the eligible pool, same-brand/already-drawn skips and the number drawn; targets with no eligible label are listed as such.

### 2. Licence boundary: texts are NOT stored in the repository
Open Food Facts terms (https://world.openfoodfacts.org/terms-of-use, read 2026-11-20): the database is available under the Open Database License (ODbL 1.0), individual contents under the Database Contents License (DbCL), product images under CC BY-SA.
Obligations of ODbL 1.0 as I understand them (my reading, not legal advice; the licence text at opendatacommons.org was not reachable from this environment and should be read before any reliance):
- Attribution: credit the source in any public use of a database or work based on it (conventionally "Contains information from Open Food Facts, which is made available under the Open Database License (ODbL)"), keep the licence notice and give its location.
- Share-alike: a Derivative Database (a database built from a substantial extraction of the contents) that is publicly used must be offered under ODbL. A repository holding a corpus of extracted ingredient texts with annotations, if published, is a candidate Derivative Database; whether the rest of the repository is reached is exactly the "fit unresolved" status in data/ingest/SOURCES.md.
- Produced Works (reports built from the data) may carry another licence but must carry the attribution notice.
The repository does not satisfy these cleanly for stored texts (no notice file, no decision on the share-alike reach). Therefore this set follows the reference-only boundary: the texts are fetched by scripts/oos_draw.py into the gitignored cache `data/cache/oos_herb_spice_1/inputs/`, and the repository commits only the manifest (barcode, product URL, per-label licence note, retrieval date, sha256 of each text, selection counts), the scripts, and result tables that hold flags, counts and staged-term names (no ingredient list text). No images, ever.
Re-running scripts/oos_eval.py needs the cache; it checks each text's sha256 against the manifest and stops on a mismatch (the database is live and may have changed: no replacement draw is allowed).
Attribution for this use: "Contains information from Open Food Facts, which is made available under the Open Database License (ODbL)".

### 3. How the frozen inputs handled this (for consistency)
The 66 frozen inputs ARE stored in the repository: evaluation/{fresh_batch_1,fresh_batch_2,fresh_batch_3,negation_addendum,dev_regression_15}/inputs/*.txt hold the untouched Open Food Facts texts, and each manifest.json carries the string "Open Food Facts: database ODbL, images CC BY-SA as stated by that site (not independently verified here)"; data/ingest/SOURCES.md describes them as "already in the repo under their stated terms". There is no ODbL notice file, no attribution statement and no share-alike decision in the repository for them. That is an open inconsistency with the reference-only wording, found while writing this note; it is not changed here. Owner decision needed: add a NOTICE and a licence decision, or move those texts to the same cache pattern.
This challenge set deliberately does NOT copy that pattern (stricter), per the boundary above.

### 4. Reporting rules
Per label: whether each staged target term in the text was recognised or NOT (an abstention or gap on a target is reported first and prominently), anything mis-recognised, what became newly unassessed, any change of group/status/drivers between the before and after builds, what stayed unassessed. Before and after builds run in separate fresh processes (scripts/oos_eval.py). Unit probes written by hand are SYNTHETIC, live in tests/ and are never counted here.
