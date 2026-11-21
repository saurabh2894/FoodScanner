# class_bulk_4 / Batch 4: FDC 'Cereal Grains and Pasta' (PROPOSAL; staging only, merge stops with the owner)

Status: STAGED on branch claude/class-bulk-4 (off main 827cdcb, which already holds Batches 1-3, the powder standard and the milk powder exception). Rows are applied on the branch so the applied-state gate is real; main is NOT changed. validate_batch **READY_FOR_REVIEW**, applied_gate **READY_FOR_REVIEW**. Rule `data/ingest/class_grains_1.json`. Scope per the owner: PLAIN GRAINS (kind whole_food) and PLAIN FLOURS (kind flour); pasta, noodles, cereals, enriched/fortified/bleached forms, starches and fractions are NOT this batch.

## 1. Category source rules (written BEFORE any acceptance)

| id | verbatim clause (FAO 2019 ca5644en.pdf, Table 1 Group 1, p.11; verified verbatim by the gate) | applies to | inference level |
|---|---|---|---|
| G1 | grains such as brown, parboiled or white rice, corn cob or kernel, wheat berry or grain | whole grains (kind whole_food) | inference level: class-instance of grains; the clause names rice (brown, parboiled, white), corn cob or kernel and wheat berry or grain; other cereals and pseudo-cereals (oats, barley, millets, sorghum, quinoa, buckwheat, rye) are instances of the class 'grains', not named |
| G2 | grits, flakes or flour made from corn, wheat, oats, or cassava | flours, meals, grits (kind flour) | inference level: class-instance of grits/flour; the clause names flour of corn, wheat, oats and cassava; flours of rice, rye, barley, millet, sorghum, buckwheat, quinoa, amaranth are instances of 'flour made from ... grains' (not named) |

Group 1 definition (same table, verified): "pasta, couscous and polenta made with flours, flakes or grits and water; and foods with vitamins and minerals added generally to replace nutrients lost during processing, such as wheat or corn flour fortified with iron and folic acid". The enriched/fortified forms this sentence covers are held for the owner's pending per-form decision (process-terms review P-C), so they are QUEUED/REJECTED here, not accepted.

Scope: The clause is unconditioned. A plain whole grain or a plain flour of it is an instance (flour: the next clause). Pasta, noodles, breakfast cereals, bread, starches, bran/germ fractions, enriched/fortified/bleached forms, pre-gelatinized or nixtamalized products, canned or cooked forms and mixes are not accepted here.

**Acceptance criteria**

- A1. The FDC food category is exactly 'Cereal Grains and Pasta'.
- A2. The plain form is established by the name ('raw', 'dry', 'whole grain', a flour/meal entry) or by a Foundation FoodOn '(raw)' attribute.
- A3. No word from the word guard, product word or queue word.
- A4. Record attributes do not contradict the plain form.
- A5. The derived label term is a distinct food name: else QUEUE.
- A6. Canonical deduplication: variety, grade (dark/light/medium, hard/soft, red/white), grain-length and cut variants collapse into ONE row; others are synonym CANDIDATES (synonyms.csv untouched).

**Rejection word guard**: `added`, `baked`, `blend`, `boiled`, `canned`, `commercial`, `cooked`, `drained`, `dumpling`, `egg`, `flaked`, `flavored`, `flavoured`, `fried`, `frozen`, `gluten-free`, `heated`, `instant`, `juice`, `liquid`, `marinated`, `microwaved`, `mix`, `mixed`, `pickled`, `popped`, `prepared`, `puffed`, `ready`, `restaurant`, `roasted`, `salt`, `salted`, `sauce`, `seasoned`, `smoked`, `sodium`, `soup`, `spinach`, `steamed`, `sugar`, `supplement`, `sweet`, `sweetened`, `toasted`, `tomato`, `vitamin`, `vitamins`, `with`; phrases `food distribution`, `with added`, `dry mix`, `cooking yield`. The category-wide extension of the Spices and Herbs word guard (owner rule 3). 'parboiled' is NOT guarded (the clause names parboiled rice); 'roasted' and 'toasted' are guarded (the clause does not cover them; per-form owner decision); 'unenriched' and 'unbleached' are plain-form words (not guarded).

**Product words** (REJECT): `pasta`, `noodles`, `macaroni`, `spaghetti`, `cereal`, `cereals`, `bread`, `crisp`, `crispbread`, `cake`, `tortilla`, `snack`, `chip`, `pilaf`, `starch`, `gluten`, `pre-gelatinized`, `gelatinized`, `tapioca`, `hominy`, `masa`, `dough`, `pretzel`, `cracker`, `pie`, `pizza`, `fortified`, `enriched`, `bleached`, `bran`, `germ`, `degermed`, `self-rising`, `pearl`. A pasta, noodle, cereal, bread, starch, gluten, pre-gelatinized, nixtamalized (hominy, masa), degermed, enriched, fortified or bleached item is a product, a fraction or a treated form, not the plain grain or flour: REJECT. 'enriched/fortified/bleached' forms follow the owner's pending per-form decision (process-terms review P-C); 'bran'/'germ' are milling fractions.

**Queue words** (QUEUE): `sprouted`; `chia`; `wheat gluten`; `arrowroot`; `00`; `kernza`; `khorasan`; `fonio`; `einkorn`; `triticale`; `pearled`; `bulgur`; `couscous`; `rolled`; `steel`; `corn`; `uncle`; `debranned`; `malt` (reasons in the rule file).

## 2. Measured results

| Measure | Count |
|---|---|
| FDC candidates in the category | 254 |
| ACCEPT (candidate records) | 50 |
| canonical rows after dedupe | 23 |
| already recognised (dropped as duplicates) | 9: barley, millet, parboiled rice, red rice, rice, rice flour, sorghum flour, wheat flour, whole wheat flour |
| NEW lexicon rows proposed | 14 |
| QUEUE | 42 |
| REJECT | 162 |
| synonym CANDIDATES (not merged) | 6 |

Reject codes: {"product_word": 75, "processed_word": 87}  
Queue codes: {"queue_00": 1, "queue_rolled": 1, "queue_steel": 1, "queue_chia": 1, "queue_bulgur": 2, "queue_einkorn": 1, "queue_pearled": 4, "queue_fonio": 1, "queue_khorasan": 2, "plain_form_not_stated": 15, "queue_uncle": 1, "queue_triticale": 2, "queue_corn": 5, "queue_couscous": 1, "queue_sprouted": 1, "queue_malt": 1, "queue_debranned": 1, "queue_arrowroot": 1}

### Proposed new rows (14)

amaranth flour (flour), barley flour (flour), black rice (whole_food), buckwheat (whole_food), buckwheat flour (flour), cornmeal (flour), millet flour (flour), oat flour (flour), quinoa flour (flour), rye flour (flour), semolina (flour), sorghum (whole_food), spelt flour (flour), wild rice (whole_food)

## 3. Canonical deduplication decisions

| FDC-derived term | canonical | decision basis |
|---|---|---|
| barley flour or meal | barley flour | same FDC food ('Barley flour or meal'); one canonical row |
| long grain rice | rice | grain-length variant of rice; the existing 'rice' row recognises it; one canonical row |
| pastry flour | wheat flour | grade variant of wheat flour (FDC 'Flour, pastry'); one canonical row (INFERENCE: pastry flour is a wheat flour grade) |
| semolina flour | semolina | FDC 'Flour, semolina' and 'Semolina': one food; one canonical row |
| whole-groat buckwheat flour | buckwheat flour | cut/grade variant; one canonical row |
| refined sorghum flour | sorghum flour | grade variant (refined vs whole-grain) of sorghum flour; the existing 'sorghum flour' row recognises it; one canonical row |
| whole wheat flour | whole wheat flour | same as the existing row (duplicate) |

Grade (dark/light/medium), grain-length, wheat class (hard/soft, red/white) and cut variants collapse; separate rows next to untouched existing rows (barley, rice, millet, oat, quinoa, sorghum flour) per `variant_policy_class_grains_1.json`.

## 4. Representative inspection: 14 accepted rows with the FDC attributes checked

| FDC id | name | -> term | attributes checked |
|---|---|---|---|
| 790018 | Flour, wheat, all-purpose, unenriched, unbleached | wheat flour | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn 'flour (unenriched, unbleached)'; taxon NCBITaxon_4564; portions '-' |
| 790085 | Flour, whole wheat, unenriched | whole wheat flour | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn 'whole wheat flour'; taxon NCBITaxon_4564; portions '-' |
| 790214 | Flour, rice, white, unenriched | rice flour | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn 'white rice flour'; taxon NCBITaxon_4530; portions '-' |
| 2003587 | Flour, spelt, whole grain | spelt flour | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn 'spelt flour'; taxon NCBITaxon_58933; portions '-' |
| 2003588 | Flour, semolina, coarse and semi-coarse | semolina | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn 'semolina flour (durum wheat)'; taxon NCBITaxon_4564; portions '-' |
| 2261421 | Flour, oat, whole grain | oat flour | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn 'oat flour'; taxon NCBITaxon_4498; portions '-' |
| 2512371 | Flour, amaranth | amaranth flour | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn 'amaranth flour'; taxon NCBITaxon_3564; portions '-' |
| 2512372 | Flour, quinoa | quinoa flour | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn 'quinoa flour'; taxon NCBITaxon_63459; portions '-' |
| 2512373 | Flour, sorghum | sorghum flour | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn 'sorghum flour'; taxon NCBITaxon_4557; portions '-' |
| 2512374 | Flour, buckwheat | buckwheat flour | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn 'buckwheat flour'; taxon NCBITaxon_3617; portions '-' |
| 2512375 | Flour, rye | rye flour | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn 'rye flour'; taxon NCBITaxon_4550; portions '-' |
| 2512376 | Flour, barley | barley flour | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn 'barley flour'; taxon NCBITaxon_4513; portions '-' |
| 2512378 | Buckwheat, whole grain | buckwheat | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn 'buckwheat seed'; taxon NCBITaxon_3617; portions '-' |
| 2512379 | Millet, whole grain | millet | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn 'millet seed (dried)'; taxon NCBITaxon_4479; portions '-' |

## 5. Representative inspection: 12 rejected and 18 queued rows with the reason

| decision | FDC id | name | reason | attributes checked |
|---|---|---|---|---|
| REJECT | 789890 | Flour, wheat, all-purpose, enriched, bleached | product_word: product word(s) ['bleached', 'enriched']: a product made from a legume, not the legume | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn 'flour (all purpose)'; taxon NCBITaxon_4564;  |
| REJECT | 789951 | Flour, wheat, all-purpose, enriched, unbleached | product_word: product word(s) ['enriched']: a product made from a legume, not the legume | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn 'white wheat flour (unbleached, enriched)'; t |
| REJECT | 790146 | Flour, bread, white, enriched, unbleached | product_word: product word(s) ['bread', 'enriched']: a product made from a legume, not the legume | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn 'white bread flour'; taxon NCBITaxon_4564; po |
| REJECT | 790276 | Flour, corn, yellow, fine meal, enriched | product_word: product word(s) ['enriched']: a product made from a legume, not the legume | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn 'yellow corn flour'; taxon NCBITaxon_4577; po |
| REJECT | 2710835 | Corn flour, masa harina, white or yellow, dry, raw | product_word: product word(s) ['masa']: a product made from a legume, not the legume | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn 'masa'; taxon NCBITaxon_4577; portions '-' |
| REJECT | 2710839 | Sorghum bran, white, unenriched, dry, raw | product_word: product word(s) ['bran']: a product made from a legume, not the legume | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn 'sorghum food product'; taxon NCBITaxon_4557; |
| REJECT | 2779240 | Sorghum, puffed, organic | processed_word: word guard ['puffed']: outside a plain dry/raw seed | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn '-'; taxon -; portions '-' |
| REJECT | 2779241 | Quinoa, puffed, organic | processed_word: word guard ['puffed']: outside a plain dry/raw seed | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn '-'; taxon -; portions '-' |
| REJECT | 2779242 | Mushroom corn, puffed, organic | processed_word: word guard ['puffed']: outside a plain dry/raw seed | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn '-'; taxon -; portions '-' |
| REJECT | 2779243 | Millet, puffed, organic | processed_word: word guard ['puffed']: outside a plain dry/raw seed | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn '-'; taxon -; portions '-' |
| REJECT | 2779244 | Khorasan, puffed, organic | processed_word: word guard ['puffed']: outside a plain dry/raw seed | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn '-'; taxon -; portions '-' |
| REJECT | 2779245 | Kamut, puffed, organic | processed_word: word guard ['puffed']: outside a plain dry/raw seed | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn '-'; taxon -; portions '-' |
| QUEUE | 2003586 | Flour, 00 | queue_00: a flour grade name; no label word established. | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn '00 wheat flour'; taxon NCBITaxon_4564; porti |
| QUEUE | 2346396 | Oats, whole grain, rolled, old fashioned | queue_rolled: rolled oats are flaked (process); the clause names 'flakes' of oats: per-term decision (existing 'oa | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn 'rolled oats'; taxon NCBITaxon_4498; portions |
| QUEUE | 2346397 | Oats, whole grain, steel cut | queue_steel: steel cut oats: per-term decision. | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn 'steel cut oats'; taxon NCBITaxon_4498; porti |
| QUEUE | 2710819 | Chia seeds, dry, raw | queue_chia: a seed (nut_seed batch). | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn 'chia seed'; taxon NCBITaxon_49212; portions  |
| QUEUE | 2710820 | Bulgur, dry, raw | queue_bulgur: parboiled cracked wheat: the clause names 'parboiled' rice; per-term decision. | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn 'bulgur'; taxon NCBITaxon_4564; portions '-' |
| QUEUE | 2710827 | Einkorn, grain, dry, raw | queue_einkorn: rare grain; QUEUE per-term. | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn 'einkorn wheat grain'; taxon NCBITaxon_4568;  |
| QUEUE | 2710828 | Farro, pearled, dry, raw | queue_pearled: pearled grains are polished (a milling step beyond the clause's whole grain); QUEUE per-term. | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn 'farro kernel'; taxon NCBITaxon_4564; portion |
| QUEUE | 2710829 | Fonio, grain, dry, raw | queue_fonio: rare grain; QUEUE per-term. | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn 'fonio food product'; taxon NCBITaxon_1010633 |
| QUEUE | 2710830 | Khorasan, grain, dry, raw | queue_khorasan: a trademarked wheat (Kamut); rare; QUEUE. | foundation_food; cat 'Cereal Grains and Pasta'; FoodOn 'khorasan wheat kernel (raw)'; taxon NCBITaxo |
| QUEUE | 168874 | Quinoa, uncooked | plain_form_not_stated: the name does not state a raw or dry seed form; the plain form is not established by the name or by  | sr_legacy_food; cat 'Cereal Grains and Pasta'; FoodOn '-'; taxon -; portions 'cup' |
| QUEUE | 168876 | Rice, brown, parboiled, dry, UNCLE BEN'S | queue_uncle: a brand-name record (Uncle Ben's), not a food term. | sr_legacy_food; cat 'Cereal Grains and Pasta'; FoodOn '-'; taxon -; portions 'cup' |
| QUEUE | 168888 | Triticale flour, whole-grain | queue_triticale: hybrid grain; rare; QUEUE per-term. | sr_legacy_food; cat 'Cereal Grains and Pasta'; FoodOn '-'; taxon -; portions 'cup' |
| QUEUE | 168920 | Corn grain, white | queue_corn: corn overlaps vegetables (sweet corn, queued in Batch 2) and cereal; QUEUE for an owner decision on  | sr_legacy_food; cat 'Cereal Grains and Pasta'; FoodOn '-'; taxon -; portions 'cup' |
| QUEUE | 169699 | Couscous, dry | queue_couscous: couscous is named in the Group 1 DEFINITION ('pasta, couscous and polenta made with flours, flakes o | sr_legacy_food; cat 'Cereal Grains and Pasta'; FoodOn '-'; taxon -; portions 'cup' |
| QUEUE | 169725 | Wheat, sprouted | queue_sprouted: sprouted grains: process-terms review proposes per-term inference rows from the general method claus | sr_legacy_food; cat 'Cereal Grains and Pasta'; FoodOn '-'; taxon -; portions 'cup' |
| QUEUE | 169740 | Barley malt flour | queue_malt: malted product: malt forms are parked/unplaced in this project (malt extract PARK); QUEUE. | sr_legacy_food; cat 'Cereal Grains and Pasta'; FoodOn '-'; taxon -; portions 'cup' |
| QUEUE | 169741 | Oat flour, partially debranned | queue_debranned: a milling fraction (bran partly removed): not the plain whole flour. | sr_legacy_food; cat 'Cereal Grains and Pasta'; FoodOn '-'; taxon -; portions 'cup' |
| QUEUE | 170684 | Arrowroot flour | queue_arrowroot: arrowroot flour is a starch product (FAO Group 2 starch example), not a grain flour. | sr_legacy_food; cat 'Cereal Grains and Pasta'; FoodOn '-'; taxon -; portions 'cup' |

## 6. Gates (applied state)

BEFORE = a worktree of main at staging; AFTER = this branch's source with the rows applied; separate fresh processes.

- After-build proof: 14 of 14 staged terms recognised after and not before; lexicon 370 -> 384 (+14, 0 removed, 0 sources changed); synonyms.csv and markers.csv byte-identical.
- Frozen 66: changed 0, unexplained 0. Out-of-sample 32: changed 1 (S30 group 4->4, unassessed -['Barley Flour']), unexplained 0; abstain->4 0; abstain->1 0.
- Drift over 496 existing terms/synonyms: 0 differences. Powder surface (552 forms): bare X powder Group 1 after 0; moves to another group 0.
- Controls (applied_gate.json 'controls', 21 negative, 17 positive): enriched/bleached/fortified/pre-gelatinized/arrowroot/pasta/noodles/masa/hominy unassessed; wheat gluten Group 4 (existing marker); flour in any list abstains; plain grains and flours Group 1 as the sole item; 'Oat Flour (XQ9)' / 'Rye Flour (XQ9)' abstain.

## 7. Findings and open decisions for the owner (measured)

1. **Flour kind joins the unknown-bracket abstention (classification-bearing, this branch).** Before: `Oat Flour (XQ9)` and every flour row answered Group 1 with an unknown bracket ignored. Now `classify.py`/`foodscan.js` treat kind `flour` like legume/vegetable/fruit for `bracket_residual` (parity 603/603). Existing flour rows (wheat flour etc.) are affected only when a bracket names content the vocabulary does not recognise (`Whole Wheat Flour (Atta)` and `Wheat Flour (Organic)` stay Group 1). Whole grains (kind whole_food: `Rice (XQ9)`) are NOT changed: owner decision P-D.
2. **`roasted buckwheat` becomes Group 1** through the existing `roasted` descriptor (FAO's Group 1 definition names roasting): unchanged mechanism; the batch makes it apply to the new buckwheat row. The FDC record 'Buckwheat groats, roasted' itself is QUEUED (the clause does not cover roasting).
   **Aligned in per-form-1 (owner ruling):** roasting is exact-named in the FAO p.6 minimal-processing methods clause, so plain roasted grains and flours are Group 1 at runtime by design and 'toasted' joins them (kind-scoped descriptor, inference). The staging guard for 'roasted'/'toasted' FDC records is a staging-scope note, not a placement judgement; see evaluation/per_form_1/README.md.
3. **Held for owner decisions:** enriched/fortified/bleached flours and rices (FAO names fortified flours in the Group 1 definition: P-C), sprouted wheat (P-A), pearled barley, bulgur, couscous, rolled/steel-cut oats, corn (overlaps Batch 2), rare grains (einkorn, fonio, khorasan, triticale, kernza), `masa harina`/hominy (nixtamalized), vital wheat gluten (FAO Group 4 substance), arrowroot flour (a starch).
4. The 9 terms already recognised (rice, millet, barley, wheat flour, whole wheat flour, rice flour, sorghum flour, red rice, parboiled rice) created no duplicate row.
5. Condition-record upgrades from audit-2 (dals/millets class-instance wording) are folded in as the inference levels recorded per row here; the standing NOT FOUND rows are untouched.
