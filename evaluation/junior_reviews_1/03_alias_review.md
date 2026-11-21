# Senior review 3: antigravity/alias-1 (evaluation/alias_1/)

Boundary (step 0): 4 files, all under evaluation/alias_1/, base 827cdcb. 37 rows. Per-row senior status: `03_alias_review_status.csv` (this directory). Nothing here touches synonyms.csv; application stays a SEPARATE gated batch.

## Method
For every row that cites an FDC id (28 rows) I looked up the id, the quoted description and the Common Name attribute (type 1000) in the repo's CACHED zips (data/cache/fdc/*, hashes in downloads.json). 27 of 28 match exactly. For every alias and target I ran the live normaliser/lookup on main: no alias is already recognised and every target is recognised (no collision today). External hosts (Merriam-Webster, Molesworth/DSAL, eCFR) are unreachable from this session (proxy 403/000), so those quotes are UNVERIFIED by me and marked so.

## Your four corrections, made directly
(a) **mandarin oranges** - junior error confirmed. FDC 169106 is 'Tangerines, (mandarin oranges), canned, juice pack' (misquoted as 'raw'); neither 169106 nor 169105 has a Common Name attribute, and no record in either cached zip has a Common Name containing mandarin/tangerine. Status: NEEDS_EQUIVALENCE_EVIDENCE for the junior target ('mandarin'). Admissible re-source: SR 169105 'Tangerines, (mandarin oranges), raw': the bracketed alternate name in the FDC description ties 'mandarin oranges' to the merged row `tangerines`, not to the Foundation row `mandarin`. Re-sourced proposal: 'mandarin oranges' -> 'tangerines'.
(b) **sucrose / chinese gooseberry** - both GENUINELY PRESENT in the cached foundation zip (FoodData_Central_foundation_food_csv_2026-10-29.zip): food_attribute.csv row 5581 (fdc 334247, Common Name 'sucrose', description 'Sugars, granulated') and row 5579 (fdc 327046, Common Name 'Chinese gooseberry', description 'Kiwifruit, green, raw'). The public archive you opened lacks these tables; the cached file has them. Both stay PROPOSED with these pinpoints.
(c) **pak choi** - re-assessed: FDC SR 170390 has ONE Common Name attribute 'pak choi, bok choy' (row 2503), so pak choi = bok choy is source-supported and 'pak choi' -> 'bok choy cabbage' is supported (status PROPOSED). **This exposed a defect on main (mine, Batch 2):** the staged and merged row `chinese cabbage` lists BOTH FDC 169979 'Cabbage, chinese (pe-tsai), raw' and FDC 170390 'Cabbage, chinese (pak-choi), raw' as its provenance, because the bracketed alternate names were dropped in dedupe. Two different vegetables sit under one row name. Group 1 placement is unaffected (both plain raw vegetables) but the row's source claim and the meaning of the label word 'chinese cabbage' are wrong. Proposed fix-forward, separate gated change on your instruction: attach 170390 to `bok choy cabbage`, keep `chinese cabbage` on 169979, record both Common Names. I have NOT changed main.
(d) **UNVERIFIED_PARTIAL rows**: `badishep` (Molesworth) and `chick peas` (Merriam-Webster) cannot be re-fetched from here. Kept UNVERIFIED_PARTIAL, not proposable. `chick peas` is a low-risk spelling variant but its only cited source is a commercial dictionary.

## Additional senior findings
- **HELD: `yellow cherries` -> `nance`.** FDC 167789 really carries that Common Name, but 'yellow cherries' also denotes ordinary yellow cherries on labels; applying it would misread them. Do not apply.
- The 6 NEEDS_EQUIVALENCE_EVIDENCE rows (gingelly oil, carom seeds, desi ghee, maida, cassia, cassia whole) and the AMBIGUOUS `refined palmolien oil` stand as the junior set them: no evidence offered, none found by me. `cassia` -> `cinnamon` should stay out regardless (cassia and cinnamon are different spices; the clause names cinnamon only).
- `cane sugar` -> `sugar` rests on 21 CFR 184.1854 ('Sucrose is the chemical name of the substance known to the consumer as cane sugar, beet sugar, or white sugar'): plausible, UNVERIFIED by me.
- `no_target_spans.csv` (240 span rows) is demand evidence only; I did not audit it row by row.

## Counts after senior review (37 rows)
- Proposable on FDC evidence verified by me in the cached zips (id, description, Common Name attribute): **23** (incl. sucrose, chinese gooseberry, pak choi, bok choy).
- Re-sourced: **1** (mandarin oranges -> tangerines, FDC 169105 description bracket).
- Dictionary / regulation quotes awaiting a lawful copy (unverified by me): **3** (tumeric, chili, cane sugar).
- UNVERIFIED_PARTIAL: **2** (badishep, chick peas). HELD: **1** (yellow cherries). NEEDS_EQUIVALENCE_EVIDENCE: **6**. AMBIGUOUS: **1** (refined palmolien oil).
- 23 + 1 + 3 + 2 + 1 + 6 + 1 = 37.
