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

### 2. Licence handling: storage MINIMIZATION, not a licence determination (the question stays OPEN)
Open Food Facts terms (https://world.openfoodfacts.org/terms-of-use, read by this session 2026-11-20): the database is available under the Open Database License (ODbL 1.0), individual contents under the Database Contents License (DbCL), product images under CC BY-SA.
ODbL obligations, per the official ODbL summary at opendatacommons.org as read by the owner on 2026-11-21 and relayed to this session (this environment could not reach opendatacommons.org, so this session did not read it itself): the obligations trigger on PUBLIC use.
Attribution for any public use of the database or works produced from it, with notices kept intact; share-alike only when an ADAPTED database is publicly used; produced works may carry another licence but need the attribution notice.
Consequence: the trigger question is the repository's intended distribution (private or public), not the mere fact of storage. A private repository holding label texts without a notice does not by itself establish a breach or a share-alike requirement.
What was chosen here is storage minimization: the texts of this challenge set are fetched by scripts/oos_draw.py into the gitignored cache `data/cache/oos_herb_spice_1/inputs/`; the repository commits the manifest (barcode, product URL, per-label licence note, retrieval date, sha256 of each text, selection counts), the scripts, and result tables with flags, counts and staged-term names (no ingredient list text). No images, ever.
This is not an exemption: the manifest and result tables can still carry database obligations if the repository or its results are publicly used. Whether the obligations are met is NOT decided here; it must be re-checked before any public distribution decision.
Re-running scripts/oos_eval.py needs the cache; it checks each text's sha256 against the manifest and stops on a mismatch (the database is live and may have changed: no replacement draw is allowed).
Attribution for this use: "Contains information from Open Food Facts, which is made available under the Open Database License (ODbL)" (also in /NOTICE).

### 3. How the frozen inputs handled this, and the remediation applied
The 66 frozen inputs ARE stored in the repository: evaluation/{fresh_batch_1,fresh_batch_2,fresh_batch_3,negation_addendum,dev_regression_15}/inputs/*.txt hold the untouched Open Food Facts texts, and each manifest.json carries the string "Open Food Facts: database ODbL, images CC BY-SA as stated by that site (not independently verified here)".
They had no notice file. Remediation, technical scope only: a NOTICE at the repository root now carries the conventional attribution and the terms URL for the stored texts. Nothing was deleted, migrated or rewritten (no history change).
A decision to distribute the repository publicly would need the ODbL obligations (attribution, notices, share-alike for an adapted database) re-checked first; anything beyond the NOTICE is a product/legal call for the owner.
This challenge set does not copy the store-the-text pattern (stricter, as above).

### 4. Reporting rules
Per label: whether each staged target term in the text was recognised or NOT (an abstention or gap on a target is reported first and prominently), anything mis-recognised, what became newly unassessed, any change of group/status/drivers between the before and after builds, what stayed unassessed. Before and after builds run in separate fresh processes (scripts/oos_eval.py). Unit probes written by hand are SYNTHETIC, live in tests/ and are never counted here.
