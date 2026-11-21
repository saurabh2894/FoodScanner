# class_bulk_3 / Batch 3: FDC 'Fruits and Fruit Juices' (PROPOSAL; merge stops with the owner)

Status: STAGED on branch claude/class-bulk-3 (main merged in, incl. the legume/vegetable guard, the powder standard and the milk powder exception). The branch's lexicon.csv carries the rows so the applied-state gate is real; main is NOT changed. validate_batch: **READY_FOR_REVIEW**; applied_gate: **READY_FOR_REVIEW**. Rule `data/ingest/class_fruits_1.json`; mapper `scripts/class_batch.py`; applier `scripts/class_apply.py`; gates `scripts/validate_batch.py` + `scripts/applied_gate.py`. Scope per the owner: WHOLE/SIMPLE forms only; juices, concentrates, sweetened forms are NOT this batch.

## 1. Category source rules (written BEFORE any acceptance)

FAO 2019 (ca5644en.pdf), Table 1, Group 1, p.11, verified verbatim in the report text by the gate:

> Fresh, squeezed, chilled, frozen, or dried fruit and leafy and root vegetables

Inference level: inference level: class-instance of fruit; the clause names 'fruit' without listing species, and the Group 1 definition names 'edible parts of plants (fruit, seeds, leaves, stems, roots, tubers)' (same table); botanical fruit used as vegetables or berries/drupes/pomes/tropical fruit are instances of the class, none is named

Scope: The clause is unconditioned and names the forms fresh, squeezed, chilled, frozen or dried. In THIS batch only the plain raw and the frozen-unsweetened whole/cut fruit are instances: 'squeezed' (juice) and 'dried' forms, juices, concentrates, purees, sauces, jams, canned or syrup-packed or sweetened fruit, fruit cocktails and salads, smoothies and dishes are not accepted here (juices are a CONDITIONED clause: 'fresh or pasteurized fruit or vegetable juices (with no added sugar, sweeteners or flavours)'; fruit in syrup is Group 3: 'whole fruit preserved in syrup').

Related clauses used only for the guard and for what is NOT accepted: Group 3 prose 'whole fruit preserved in syrup' (p.7, verified verbatim) and Table 1 continuation 'fruit in syrup (with or without added anti-oxidants)'; the conditioned juice clause 'fresh or pasteurized fruit or vegetable juices (with no added sugar, sweeteners or flavours)' (a different, conditioned batch).

**Acceptance criteria**

- A1. The FDC food category is exactly 'Fruits and Fruit Juices'.
- A2. The plain form is established by the name ('raw', or 'frozen' + 'unsweetened') OR by the record attribute: a Foundation record whose FoodOn item name states '(raw)' where the description does not.
- A3. The name holds no word from the word guard, no product word and no queue word.
- A4. Record attributes do not contradict the plain form (no portion descriptor holding a guard word).
- A5. The derived label term is a distinct food name: else QUEUE.
- A6. Canonical deduplication: cultivar, grade, colour-shade, region and cut variants of one fruit collapse into ONE row; the rest are synonym CANDIDATES (synonyms.csv is not touched).

**Rejection word guard** (anywhere in the name = REJECT, processed): `ade`, `applesauce`, `ascorbic`, `baked`, `blend`, `boiled`, `bottled`, `candied`, `canned`, `chutney`, `cocktail`, `commercial`, `concentrate`, `concentrated`, `cooked`, `creamed`, `cured`, `diet`, `diluted`, `drained`, `drink`, `enriched`, `extra`, `filling`, `flavored`, `flavoured`, `fortified`, `fried`, `from`, `frozen-concentrate`, `glace`, `glazed`, `grilled`, `halves`, `heated`, `heavy`, `home-prepared`, `infusion`, `instant`, `jam`, `jelly`, `juice`, `leather`, `light`, `lime-flavored`, `liquid`, `marinated`, `marmalade`, `mashed`, `microwaved`, `mix`, `mixed`, `nectar`, `paste`, `pickled`, `pie`, `pieces`, `pimiento`, `prepared`, `preserves`, `puree`, `reconstituted`, `restaurant`, `roasted`, `salad`, `salt`, `salted`, `sauce`, `sauteed`, `scalloped`, `seasoned`, `sections`, `segments`, `slices`, `smoked`, `smoothie`, `sodium`, `solids`, `soup`, `spread`, `steamed`, `stewed`, `stir-fried`, `stuffed`, `sugar`, `sulfured`, `supplement`, `sweetened`, `syrup`, `tinned`, `topping`, `uncooked`, `undiluted`, `vitamin`, `water`; phrases `baby food`, `food distribution`, `water pack`, `juice pack`, `heavy syrup`, `light syrup`, `from concentrate`, `with added`, `without added`, `added sugar`, `no sugar added`. The category-wide extension of the Spices and Herbs word guard (owner rule 3): any treatment, addition, packing medium, concentrate or product word puts the name outside a plain raw or frozen-unsweetened fruit. 'unsweetened' is NOT guarded (it is the clause-compatible frozen form; 'sweetened' is). 'Includes foods for USDA's Food Distribution Program' is a programme note and is removed before the check.

**Product words** (REJECT): `juice`, `powder`, `flour`, `starch`, `flakes`, `granules`, `applesauce`, `smoothie`, `cocktail`, `salad`, `leather`, `puree`, `sauce`, `jam`, `jelly`, `raisins`, `prunes`, `dates`. A juice, powder, flour, puree, sauce, jam, cocktail, salad or smoothie of fruit is a product, not the fruit: REJECT. Raisins, prunes and dates are DRIED fruit: dried forms are per-term only (dehydrated-policy-1), routed to the owner.

**Queue words** (QUEUE): `dried`; `dehydrated`; `peel`; `rind`; `seeds`; `stalk`; `olives`; `carob`; `roselle`; `tamarinds`; `coconut`; `pulp` (reasons in the rule file). **Portion guard**: Portion descriptors of RAW fruit legitimately say slices, sections, pieces, halves, cubes, pureed or juice (measuring units); only descriptors naming a preparation or packing medium contradict the plain form.

**Kind**: `fruit` (whole-food behaviour plus the item-level guard of section 6a and the powder standard).

## 2. Measured results

| Measure | Count |
|---|---|
| FDC candidates in the category | 430 |
| ACCEPT (candidate records) | 156 |
| canonical rows after dedupe | 76 |
| already recognised by the build (dropped as duplicates) | 1: mangos |
| NEW lexicon rows proposed | 75 |
| QUEUE | 22 |
| REJECT | 252 |
| synonym CANDIDATES (not merged) | 57 (+0 already mapped elsewhere) |
| existing rows retyped whole_food -> fruit (kind column only) | 4: mango, lemon, dates, black raisin |

Reject codes: {"processed_word": 243, "product_word": 9}  
Queue codes: {"queue_rind": 1, "queue_stalk": 1, "queue_peel": 4, "queue_tamarinds": 1, "queue_pulp": 1, "plain_form_not_stated": 5, "queue_dried": 6, "queue_roselle": 1, "dedupe_stays_out": 2}

### Proposed new rows (75)

abiyuch, acerola, apples, apricots, asian pears, avocados, bananas, black currants, blackberries, blueberries, boysenberries, breadfruit, cantaloupe melons, carambola, carissa, casaba melons, cherimoya, cherries, clementines, crabapples, custard-apple, elderberries, feijoa, figs, gooseberries, grapefruit, grapes, groundcherries, guavas, honeydew melons, jackfruit, java-plum, jujube, kiwifruit, kumquats, limes, litchis, longans, loquats, mamey sapote, mammy-apple, mandarin, mulberries, muscadine grapes, nance, nectarines, oheloberries, oranges, papayas, passion-fruit, pawpaw, pears, persimmons, pineapple, pitanga, plantains, plums, pomegranates, prickly pears, pummelo, quinces, raspberries, red currants, rhubarb, rose-apples, rowal, sapodilla, sour cherries, soursop, strawberries, strawberry guavas, sugar-apples, tangerines, watermelon, yellow peaches

## 3. Canonical deduplication decisions

Cultivar, colour-shade, ripeness and size variants collapse into one row; synonyms.csv is untouched (candidates only).

| FDC-derived term | canonical | decision basis |
|---|---|---|
| fuji apples | apples | cultivar variant of one fruit; one canonical row |
| gala apples | apples | cultivar variant of one fruit; one canonical row |
| golden delicious apples | apples | cultivar variant of one fruit; one canonical row |
| granny smith apples | apples | cultivar variant of one fruit; one canonical row |
| honeycrisp apples | apples | cultivar variant of one fruit; one canonical row |
| red delicious apples | apples | cultivar variant of one fruit; one canonical row |
| unheated apples | apples | cultivar variant of one fruit; one canonical row |
| bartlett pears | pears | cultivar variant of one fruit; one canonical row |
| bosc pears | pears | cultivar variant of one fruit; one canonical row |
| red anjou pears | pears | cultivar variant of one fruit; one canonical row |
| green anjou pears | pears | cultivar variant of one fruit; one canonical row |
| green anjou pear | pears | cultivar variant of one fruit; one canonical row |
| red grapes | grapes | colour-shade variant of one fruit; one canonical row |
| green grapes | grapes | colour-shade variant of one fruit; one canonical row |
| red or green grapes | grapes | colour-shade variant of one fruit; one canonical row |
| american type grapes | (stays out) | a grape type descriptor (slip skin) that is not a label term; stays out rather than inflating the lexicon |
| sweet cherries | cherries | FDC 'Cherries, sweet': the sweet cherry is the common cherry; one canonical row (INFERENCE: owner to confirm) |
| dark red sweet cherries | cherries | FDC 'Cherries, sweet': the sweet cherry is the common cherry; one canonical row (INFERENCE: owner to confirm) |
| red sour cherries | sour cherries | colour-shade variant of sour cherries; one canonical row |
| ataulfo mango | mangos | cultivar variant of one fruit; one canonical row (existing 'mango' row recognises the plural) |
| tommy atkins mango | mangos | cultivar variant of one fruit; one canonical row (existing 'mango' row recognises the plural) |
| hass avocado | avocados | cultivar variant of one fruit; one canonical row |
| ripe and slightly ripe bananas | bananas | ripeness grade of one fruit; one canonical row |
| green plantains | plantains | colour-shade variant of one fruit; one canonical row |
| yellow plantains | plantains | colour-shade variant of one fruit; one canonical row |
| green kiwifruit | kiwifruit | cultivar variant of one fruit; one canonical row |
| zespri sungold kiwifruit | kiwifruit | cultivar variant of one fruit; one canonical row |
| white grapefruit | grapefruit | colour-shade variant of one fruit; one canonical row |
| apricot | apricots | same fruit, singular/plural FDC entries; one canonical row |
| black plum | plums | cultivar variant of one fruit; one canonical row |
| red raspberries | raspberries | colour-shade variant of one fruit; one canonical row |
| european black currants | black currants | FDC 'Currants, european black'; label term 'black currants' |
| red and white currants | red currants | FDC 'Currants, red and white' (one record for both colours); INFERENCE: owner to confirm |
| japanese persimmons | persimmons | species variants of persimmon; one canonical row (label term 'persimmon') |
| native persimmons | persimmons | species variants of persimmon; one canonical row (label term 'persimmon') |
| purple passion-fruit | passion-fruit | colour-shade variant of one fruit; one canonical row |
| cranberries | (stays out) | STANDING EXCLUSION (lexicon-1 senior review, tests/test_lexicon_1.py): 'cranberry' on b1/N14 does not establish plain dried status (cranberries are typically sweetened when dried), so the term must st |

## 4. Representative inspection: 13 accepted rows with the FDC attributes checked

| FDC id | name | -> term | attributes checked |
|---|---|---|---|
| 325430 | Peaches, yellow, raw | yellow peaches | foundation_food; cat 'Fruits and Fruit Juices'; FoodOn 'peach (raw)'; taxon NCBITaxon_3760; portions 'NLEA |extra large (3" dia)|large (2-3/4" dia)|medi' |
| 327046 | Kiwifruit, green, raw | kiwifruit | foundation_food; cat 'Fruits and Fruit Juices'; FoodOn 'fuzzy kiwifruit (raw)'; taxon NCBITaxon_3627; portions '-' |
| 327198 | Melons, cantaloupe, raw | cantaloupe melons | foundation_food; cat 'Fruits and Fruit Juices'; FoodOn '-'; taxon -; portions 'balls|cubes|diced|large (1/8 of large melon)|large' |
| 327357 | Nectarines, raw | nectarines | foundation_food; cat 'Fruits and Fruit Juices'; FoodOn 'nectarine (raw)'; taxon NCBITaxon_3760; portions ' 2-1/2" dia| slices|2-1/3" dia|2-3/4" dia|NLEA' |
| 167789 | Nance, frozen, unsweetened | nance | sr_legacy_food; cat 'Fruits and Fruit Juices'; FoodOn '-'; taxon -; portions 'cup without pits, thawed|fruit without pits, thawe' |
| 171713 | Boysenberries, frozen, unsweetened | boysenberries | sr_legacy_food; cat 'Fruits and Fruit Juices'; FoodOn '-'; taxon -; portions 'cup, unthawed|package (10 oz)' |
| 171718 | Cherries, sour, red, frozen, unsweetened (Includes foods for USDA's Food Distribution Program) | sour cherries | sr_legacy_food; cat 'Fruits and Fruit Juices'; FoodOn '-'; taxon -; portions 'cup, unthawed|package (18 oz)' |
| 327699 | Strawberries, raw | strawberries | foundation_food; cat 'Fruits and Fruit Juices'; FoodOn '-'; taxon -; portions '-' |
| 2346398 | Pineapple, raw | pineapple | foundation_food; cat 'Fruits and Fruit Juices'; FoodOn 'pineapple (raw)'; taxon NCBITaxon_4615; portions '-' |
| 2747675 | Watermelon, seedless, flesh only, raw | watermelon | foundation_food; cat 'Fruits and Fruit Juices'; FoodOn 'watermelon (raw)'; taxon NCBITaxon_3654; portions '-' |
| 169134 | Pomegranates, raw | pomegranates | sr_legacy_food; cat 'Fruits and Fruit Juices'; FoodOn '-'; taxon -; portions 'cup arils (seed/juice sacs)|pomegranate (4" dia)' |
| 173021 | Figs, raw | figs | sr_legacy_food; cat 'Fruits and Fruit Juices'; FoodOn '-'; taxon -; portions 'large (2-1/2" dia)|medium (2-1/4" dia)|small (1-1/' |
| 174687 | Jackfruit, raw | jackfruit | sr_legacy_food; cat 'Fruits and Fruit Juices'; FoodOn '-'; taxon -; portions 'cup 1" pieces|cup, sliced' |

## 5. Representative inspection: 14 rejected and 9 queued rows with the reason

| decision | FDC id | name | reason | attributes checked |
|---|---|---|---|---|
| REJECT | 325287 | Grapefruit juice, white, canned or bottled, unsweetened | processed_word: word guard ['bottled', 'canned', 'juice']: outside a plain dry/raw seed | foundation_food; cat 'Fruits and Fruit Juices'; FoodOn 'white grapefruit juice'; taxon NCBITaxon_376 |
| REJECT | 326905 | Figs, dried, uncooked | processed_word: word guard ['uncooked']: outside a plain dry/raw seed | foundation_food; cat 'Fruits and Fruit Juices'; FoodOn '-'; taxon -; portions '-' |
| REJECT | 332791 | Olives, green, Manzanilla, stuffed with pimiento | processed_word: word guard ['pimiento', 'stuffed']: outside a plain dry/raw seed | foundation_food; cat 'Fruits and Fruit Juices'; FoodOn 'olive (stuffed with pimiento)'; taxon NCBITa |
| REJECT | 746768 | Figs, dried, uncooked | processed_word: word guard ['uncooked']: outside a plain dry/raw seed | foundation_food; cat 'Fruits and Fruit Juices'; FoodOn 'fig (dried)'; taxon NCBITaxon_3494; portions |
| REJECT | 2003590 | Apple juice, with added vitamin C, from concentrate, shelf stable | processed_word: word guard ['concentrate', 'from', 'juice', 'vitamin', 'from concentrate', 'with added']: outside a  | foundation_food; cat 'Fruits and Fruit Juices'; FoodOn 'apple juice (reconstituted)'; taxon NCBITaxo |
| REJECT | 2003591 | Orange juice, no pulp, not fortified, from concentrate, refrigerated | processed_word: word guard ['concentrate', 'fortified', 'from', 'juice', 'from concentrate']: outside a plain dry/ra | foundation_food; cat 'Fruits and Fruit Juices'; FoodOn 'reconstituted orange juice (from concentrate |
| REJECT | 2003592 | Grape juice, purple, with added vitamin C, from concentrate, shelf stable | processed_word: word guard ['concentrate', 'from', 'juice', 'vitamin', 'from concentrate', 'with added']: outside a  | foundation_food; cat 'Fruits and Fruit Juices'; FoodOn 'grape juice (reconstituted)'; taxon NCBITaxo |
| REJECT | 2758979 | Raisins, golden, seedless | product_word: product word(s) ['raisins']: a product made from a legume, not the legume | foundation_food; cat 'Fruits and Fruit Juices'; FoodOn '-'; taxon -; portions '-' |
| REJECT | 2758980 | Raisins, dark, seedless | product_word: product word(s) ['raisins']: a product made from a legume, not the legume | foundation_food; cat 'Fruits and Fruit Juices'; FoodOn '-'; taxon -; portions '-' |
| REJECT | 167806 | Baobab powder | product_word: product word(s) ['powder']: a product made from a legume, not the legume | sr_legacy_food; cat 'Fruits and Fruit Juices'; FoodOn '-'; taxon -; portions '-' |
| REJECT | 168164 | Raisins, golden, seedless | product_word: product word(s) ['raisins']: a product made from a legume, not the legume | sr_legacy_food; cat 'Fruits and Fruit Juices'; FoodOn '-'; taxon -; portions 'cup (not packed)|cup,  |
| REJECT | 168165 | Raisins, dark, seedless (Includes foods for USDA's Food Distribution Program) | product_word: product word(s) ['raisins']: a product made from a legume, not the legume | sr_legacy_food; cat 'Fruits and Fruit Juices'; FoodOn '-'; taxon -; portions 'cup (not packed)|cup,  |
| REJECT | 168166 | Raisins, seeded | product_word: product word(s) ['raisins']: a product made from a legume, not the legume | sr_legacy_food; cat 'Fruits and Fruit Juices'; FoodOn '-'; taxon -; portions 'cup (not packed)|cup,  |
| REJECT | 168191 | Dates, medjool | product_word: product word(s) ['dates']: a product made from a legume, not the legume | sr_legacy_food; cat 'Fruits and Fruit Juices'; FoodOn '-'; taxon -; portions 'date, pitted' |
| QUEUE | 2747676 | Watermelon, seedless, rind only, raw | queue_rind: a plant-part variant (rind) of a fruit. | foundation_food; cat 'Fruits and Fruit Juices'; FoodOn 'watermelon food product'; taxon NCBITaxon_36 |
| QUEUE | 2758975 | Rhubarb, stalk, raw | queue_stalk: plant-part variant. | foundation_food; cat 'Fruits and Fruit Juices'; FoodOn '-'; taxon -; portions '-' |
| QUEUE | 167746 | Lemons, raw, without peel | queue_peel: a plant-part variant (peel, rind) of a fruit: not established as a label term. | sr_legacy_food; cat 'Fruits and Fruit Juices'; FoodOn '-'; taxon -; portions 'NLEA serving|cup, sect |
| QUEUE | 167763 | Tamarinds, raw | queue_tamarinds: tamarind is a culinary pulp/sourcing ingredient on Indian labels (tamarind pulp, paste): the raw fru | sr_legacy_food; cat 'Fruits and Fruit Juices'; FoodOn '-'; taxon -; portions 'cup, pulp|fruit (3" x  |
| QUEUE | 167790 | Naranjilla (lulo) pulp, frozen, unsweetened | queue_pulp: a fruit pulp is a processed mass (a puree-like product), not the whole or cut fruit; per-item decisi | sr_legacy_food; cat 'Fruits and Fruit Juices'; FoodOn '-'; taxon -; portions 'cup thawed' |
| QUEUE | 167791 | Horned melon (Kiwano) | plain_form_not_stated: the name does not state a raw or dry seed form; the plain form is not established by the name or by  | sr_legacy_food; cat 'Fruits and Fruit Juices'; FoodOn '-'; taxon -; portions 'cup|fruit (4-2/3" long |
| QUEUE | 168152 | Jujube, Chinese, fresh, dried | queue_dried: dried forms: the clause names 'dried' but earlier owner policy (dehydrated-policy-1) keeps dried/deh | sr_legacy_food; cat 'Fruits and Fruit Juices'; FoodOn '-'; taxon -; portions '-' |
| QUEUE | 168170 | Roselle, raw | queue_roselle: calyces used as a hibiscus herb/tea; not established as a fruit term. | sr_legacy_food; cat 'Fruits and Fruit Juices'; FoodOn '-'; taxon -; portions 'cup, without refuse' |
| QUEUE | 171722 | Cranberries, raw | dedupe_stays_out: STANDING EXCLUSION (lexicon-1 senior review, tests/test_lexicon_1.py): 'cranberry' on b1/N14 does no | sr_legacy_food; cat 'Fruits and Fruit Juices'; FoodOn '-'; taxon -; portions 'cup, chopped|cup, whol |

## 6a. The fruit guard (same item-level condition, per form)

Kind `fruit` joins `legume` and `vegetable` in the guard: FAO Group 3 'whole fruit preserved in syrup' / 'fruit in syrup' and the Group 3 definition 'adding salt, oil, sugar or other group 2 ingredients to group 1 foods'. An item whose OWN name or bracket adds sugar, syrup, sweetened, honey, jaggery, candied, glazed or salt: Group 3, never Group 1 via the fruit clause. Canned / tinned / bottled / jarred / preserved / pickled without sugar, syrup or salt: ABSTAIN. Negated forms ('no added sugar', 'sugar free') keep Group 1. Roasting/boiling are not part of the guard. Frozen plain forms are unchanged (the clause names frozen). The powder standard (100%/whole only) and the milk powder exception apply to the new rows through the same routing.

Effect on the 4 existing rows: `mango (sweetened)` Group 1 -> 3; `mango (preserved)` and `lemon (pickled)` Group 1 -> abstain.

## 6. Gates (applied state)

BEFORE = a worktree of main (9feadd8); AFTER = this branch's source with the rows applied; separate fresh processes.

- After-build proof: 75 of 75 staged terms recognised after and not before; lexicon 295 -> 370 (+75, 0 removed, 0 sources changed, 4 retyped); synonyms.csv and markers.csv byte-identical.
- Frozen 66: changed 0 (), unexplained 0, abstain->4 0, abstain->1 0, other 0.
- Out-of-sample 32: changed 3 (S01 group None->None, unassessed -['diced apples']; S24 group 4->4, unassessed -['Lime']; S31 group None->None, unassessed -['Dry Grapes', 'Watermelon']), unexplained 0, abstain->4 0, abstain->1 0, other 0.
- Drift over 421 existing terms and synonyms: 0 differences. Powder surface (540 forms): bare X powder Group 1 after: 0; owner-allowed milk forms: 3; moves to another group: 0.
- Controls (applied_gate.json 'controls', 30 negative, 16 positive): salted/sugared/syrup forms -> Group 3; preserved/bottled/pickled/canned brackets -> abstain; juice, concentrate, jam, sauce, chips, cocktail unassessed; 'mango powder', 'banana powder', 'apple powder' abstain; '100% mango powder' and 'whole banana powder' Group 1; plain/negated/frozen forms Group 1.

## 6c. Dried forms and unknown additions (owner requirement; applied-state controls in applied_gate.json)
V1 names 'dried' fruit, so a bare `dried X` takes Group 1 through the existing `dried` descriptor ONLY when no condition word attaches. Measured (before on main -> after on this branch):
| form | before | after | why |
|---|---|---|---|
| dried pineapple / papaya / banana / blueberries / cherries / apricots, dry grapes | abstain | Group 1 | bare dried form, V1 'dried'; no condition word |
| dried mango, dried mango (organic) | 1 | 1 | unchanged |
| dried mango (sugar) | 1 | 3 | stated sugar: Group 3 definition |
| dried banana (honey), dried papaya (jaggery), dried cherries (syrup) | abstain | 3 | stated honey/jaggery/syrup |
| dried blueberries (sunflower oil) | abstain | 3 | a recognised Group 2 substance in the item's own bracket is an added group 2 ingredient (Group 3 definition) |
| dried mango (XQ9), dried mango (sulphur dioxide), dried pineapple (sugar, XQ9) | 1 / 1 / abstain | abstain | unknown addition on the same item is NEVER laundered (the old path ignored an unrecognised bracket and answered Group 1) |
| sweetened dried mango, candied pineapple, dried cranberries, dried cranberries (sugar), dried mango slices (glazed) | unassessed | unassessed | words outside the vocabulary; never Group 1 |
- New mechanism (classify.bracket_residual, mirrored in foodscan.js): on legume, vegetable and fruit items a bracket naming content the vocabulary does not recognise ABSTAINS; benign parts are recognised foods, descriptors, guard condition words, negation/connector words and digits/codes. This also closes the general gap that `Rice (XQ9)` answered Group 1 for these kinds. Sulphur dioxide as a preservative now abstains (it was Group 1): conservative; NUPENS accepts preservatives in Group 1, so relax this only on your word. Pre-existing and NOT changed: `Rice (XQ9)`, `Wheat Flour (XQ9, Salt)` for other kinds still answer from the plain row.
- Cranberry-shaped check: the corpus (frozen 66, out-of-sample 32, all evaluation inputs) holds no bare `dried X` item from the commonly-sweetened set whose label context fails to establish plain status: the only dried-fruit contexts are `sweetened dried cranberries (cranberries, sugar, sunflower oil)` (already unassessed, cranberries queued), `Dry Fruits ... (Black Raisin, Cranberry, ...)` (b1/N14, cranberry queued) and S31 `Dry Grapes` in a dry-fruits list (no sweetener named). No further term was queued on evidence.
- Gate re-run on this branch after the change: frozen 66 changed 0, out-of-sample 32 changed 3 (S01, S24, S31; none moves a group), 0 unexplained, 0 abstain->4, drift 421 terms 0 differences, 75/75 after-build proof.

## 7. Findings and open decisions for the owner (measured)

1. **Standing exclusion respected:** `cranberries` is QUEUED (lexicon-1 senior review: 'cranberry' on b1/N14 does not establish plain dried status). It would otherwise have been a row.
2. **Existing tests that used `jackfruit` as an unknown word** (test_extraction_completeness, test_review_unassessed) were updated to the synthetic token `XQ9` (FIXTURE INTENT: generic unknown handling, never a real food name; a named-food gap would be a separate, named test): jackfruit is now a vocabulary row (an 'X and Y' phrase of two recognised items is a list). `black raisin` kind expectations in test_lexicon_1 now expect `fruit`.
3. **'dried' / 'dry' descriptors:** `dried apricots` (and `Dry Grapes` on out-of-sample label S31) are recognised as the fruit through the existing descriptors `dried`/`dry` and answer through the plain row (FAO V1 names dried fruit). Unchanged mechanism; the batch makes it apply to the new fruit rows. If you want dried forms per-term only for fruit, say so and the descriptor path needs a decision (not changed here).
4. **Queued for decisions:** dried forms (6), peel/rind/stalk variants (6), tamarind, roselle, olives, pulp products, frozen forms that do not state 'unsweetened' (5: horned melon, durian, loganberries, melon balls, wild blueberries), cranberries.
5. Condition-record upgrades from the junior audit-2 map are NOT folded in yet (audit-2 review is queued).
