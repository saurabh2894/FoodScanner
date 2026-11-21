# class_bulk_1 / Batch 1: FDC 'Legumes and Legume Products' (OWNER-APPROVED; legume guard added before merge)

Status: rows APPROVED 2026-11-21; the merge was HELD by the owner for the legume guard (section 6a) and applied-state gate proof (section 6). 21 new rows of kind `legume` + 12 existing legume rows retyped to `legume`; synonyms.csv and markers.csv untouched; synonym candidates stay candidates.
Rule: `data/ingest/class_legumes_1.json` (class-legumes-1). Mapper: `scripts/class_batch.py`. FDC: Foundation 2026-10-29 + SR Legacy 2018-04 (CC0, hashes in scope_summary.json). FDC supplies NAMING and record attributes only; placement comes from the FAO clause.

## 1. Category source rules (written BEFORE any acceptance)

**FAO clause this category maps to** (verbatim; FAO 2019 ca5644en.pdf, Table 1, Group 1 examples, p.11; verified verbatim in the PDF text by the gate: PASS):

> legumes such as beans, lentils, and chickpeas

Scope of the clause: The clause is unconditioned and names a CLASS (legumes) with three examples. It places legumes as foods of the first group: the Group 1 definition (FAO p.6) covers dried, ground, cracked, roasted, boiled and similar minimal processing, but adds no salt, sugar, oil, fat or other substance. A plain dry or raw legume is an instance of the class. Anything that is a product made from a legume (tofu, tempeh, miso, milk, butter, sauce, flour, protein fraction, canned in brine, cooked with sauce) is not an instance of this clause.

**Acceptance criteria**

- A1. The FDC food category is exactly 'Legumes and Legume Products'.
- A2. The name states a PLAIN seed form: a form part 'raw', 'dry' or 'mature seeds, raw' (SR Legacy), or the Foundation pattern 'Beans, Dry, <variety> (0% moisture)'.
- A3. The name holds no word from the word guard (below), no product word and no queue word.
- A4. The record attributes do not contradict the plain form: no portion description/modifier of the record holds a guard word (a record named 'raw' whose portions say 'cooked' goes to QUEUE).
- A5. The derived label term is a distinct food name (not a bare colour or a pod-vs-seed ambiguity): else QUEUE.
- A6. Canonical deduplication: preparation, cut, grade and cultivar-shade variants of one food collapse into ONE row (table 'canonical' below); the others are reported as synonym CANDIDATES (synonyms.csv is not touched in this workstream).

**Rejection word guard** (any of these anywhere in the name = REJECT, processed): `canned`, `pickled`, `salted`, `salt`, `sweetened`, `sugar`, `cooked`, `boiled`, `fried`, `roasted`, `dry-roasted`, `oil-roasted`, `dried-frozen`, `flavored`, `flavoured`, `fortified`, `enhanced`, `seasoned`, `marinated`, `smoked`, `cured`, `concentrate`, `concentrated`, `juice`, `sauce`, `soup`, `mix`, `blend`, `prepared`, `supplement`, `sodium`, `vitamin`, `vitamins`, `drained`, `rinsed`, `liquid`, `solids`, `frozen`, `stewed`, `baked`, `refried`, `home-prepared`, `commercial`, `fermented`, `unfortified`, `pork`, `beef`, `franks`, `tomato`, `sweet`, `chili`, `barbecue`, `vegetarian`, `meatless`, `unprepared`, `low`, `reduced`, `lite`, `nigari`, `calcium`, `sulfate`, `extra`, `silken`, `firm`, `soft`, `creamy`, `chunky`, `smooth`, `chunk`, `vanilla`, `chocolate`, `plain`, `original`, `organic`, `sprouted`  ; phrases: `baby food`, `food distribution`. 'light' is NOT guarded: in this category it is a colour shade of a bean ('Light Red Kidney', 'Light Tan'); the reduced-fat sense is caught by 'lite', 'low' and 'reduced'.

**Product words** (REJECT, a product made from a legume or a brand series): `tofu`, `tempeh`, `miso`, `natto`, `soymilk`, `okara`, `hummus`, `falafel`, `butter`, `spread`, `papad`, `noodles`, `vermicelli`, `yokan`, `yogurt`, `creamer`, `luncheon`, `bacon`, `sausage`, `frankfurter`, `meatballs`, `fillets`, `chicken`, `extender`, `burger`, `burgers`, `soyburgers`, `patties`, `meatloaf`, `sandwich`, `isolate`, `protein`, `soy sauce`, `shoyu`, `tamari`, `silk`, `mori-nu`, `vitasoy`, `nasoya`, `azumaya`, `house`, `fuyu`, `koyadofu`, `curd`, `cheese`, `milk`

**Queue words** (QUEUE, conditional): `peanut` (overlaps the CONDITIONED FAO nuts/seeds clause ('tree and ground nuts and other oily seeds...); `peanuts` (same as peanut...); `flour` (a flour is placed by the 'flours' class (PMC10127522 fn2, NUPENS), not by the legumes clau...); `meal` (defatted/ground fraction: not established as a plain flour or a whole legume....); `defatted` (a fractionated (defatted) form: composition changed by an industrial step; not an instance...); `carob` (carob is not a Group 1 legume example of the clause (a pod used as a cocoa substitute); no...); `soy` ('soy' forms other than the plain raw seed are products; see the product words....)

**Kind**: `legume` for every accepted row (a plain legume seed): whole-food behaviour everywhere plus the item-level condition of section 6a. Inference level of every row: class-instance of the class 'legumes' (the clause names beans, lentils and chickpeas; other legumes are instances of the class, not named).

## 2. Measured results

| Measure | Count |
|---|---|
| FDC candidates in the category | 351 |
| ACCEPT (candidate records) | 55 |
| canonical rows after dedupe | 26 |
| of which already recognised or aliased by the build (dropped as duplicates) | 5: chickpeas, lentils, mung beans, soybeans, split green peas |
| NEW lexicon rows proposed | 21 |
| QUEUE (conditional, never accepted) | 31 |
| REJECT | 265 |
| synonym CANDIDATES (not merged; synonyms.csv untouched) | 17 (+2 already mapped elsewhere, below) |

Reject reason codes: {"processed_word": 237, "product_word": 28}  
Queue reason codes: {"generic_name": 15, "queue_flour": 7, "queue_peanuts": 5, "queue_meal": 1, "dedupe_stays_out": 2, "queue_peanut": 1}

### Proposed new rows (21)

| term | kind | FDC records (canonical row merges all) |
|---|---|---|
| adzuki beans | whole_food | SR:173727 |
| black beans | whole_food | F:335912;F:747444;SR:173734;SR:175186 |
| broadbeans | whole_food | SR:175205 |
| cannellini beans | whole_food | F:2644281 |
| carioca beans | whole_food | F:335433;F:747436 |
| cowpeas | whole_food | F:2644284;SR:173758 |
| cranberry beans | whole_food | F:335782;F:747437;SR:175189 |
| flor de mayo beans | whole_food | F:335428;F:747432 |
| great northern beans | whole_food | F:336067;F:747446;SR:175190 |
| hyacinth beans | whole_food | SR:175210 |
| kidney beans | whole_food | F:335245;F:335422;F:747438;F:747440;SR:173742;SR:173744;SR:175193;SR:175196 |
| lima beans | whole_food | SR:174252;SR:174255 |
| lupins | whole_food | SR:172423 |
| mothbeans | whole_food | SR:172425 |
| navy beans | whole_food | F:335419;F:747441;SR:173745 |
| pigeon peas | whole_food | SR:172436 |
| pink beans | whole_food | F:335306;F:747439;SR:173748 |
| pinto beans | whole_food | F:335695;F:747445;SR:175199 |
| small white beans | whole_food | F:335927;F:747442;SR:173749 |
| winged beans | whole_food | SR:174283 |
| yardlong beans | whole_food | SR:174281 |

## 3. Canonical deduplication decisions

Two FDC records with the same name (Foundation 335xxx and 747xxx pairs) are one food: their provenance is merged into one row. Cultivar-shade, size-grade and alternate-name variants collapse into one canonical row; the variant is a synonym CANDIDATE only.

| FDC-derived term | canonical | decision basis |
|---|---|---|
| dark red kidney beans | kidney beans | cultivar-shade variant of the FDC umbrella record 'Beans, kidney, all types'; one canonical row |
| red kidney beans | kidney beans | cultivar-shade variant of 'Beans, kidney, all types'; one canonical row |
| california red kidney beans | kidney beans | cultivar variant of 'Beans, kidney, all types'; one canonical row |
| royal red kidney beans | kidney beans | cultivar variant of 'Beans, kidney, all types'; one canonical row |
| black turtle beans | black beans | INFERENCE (owner to confirm): black turtle is a black-bean cultivar group; FDC files both as plain dry black beans; one canonical row |
| large lima beans | lima beans | size-grade variant of lima beans (FDC 'large' vs 'thin seeded (baby)'); one canonical row |
| thin seeded lima beans | lima beans | size-grade variant of lima beans; one canonical row |
| common cowpeas | cowpeas | FDC record 'Cowpeas, common (blackeyes, crowder, southern)': 'common' is the species group qualifier; one canonical row |
| blackeye pea | cowpeas | FDC lists 'blackeyes' as an alternate name of 'Cowpeas, common' (record attribute); same food, one canonical row |
| catjang cowpeas | (stays out) | subspecies distinction (catjang) is not established as a label term; stays out rather than inflating the lexicon |
| mungo beans | (stays out) | 'mungo' vs 'mung' beans: the FDC record does not establish which pulse a label word means (black gram vs green gram); stays out |
| pink or red lentils | lentils | market-grade variant of lentils (existing term); duplicate semantics |
| light red kidney beans | kidney beans | cultivar-shade variant of 'Beans, kidney, all types'; one canonical row |

Named species/market classes kept as separate rows next to the untouched generic `beans` and `peas` rows (variant policy `variant_policy_class_legumes_1.json`): adzuki beans, black beans, cannellini beans, carioca beans, cranberry beans, flor de mayo beans, great northern beans, hyacinth beans, kidney beans, lima beans, navy beans, pink beans, pinto beans, small white beans, winged beans, yardlong beans, pigeon peas.

Possible overlap NOT collapsed (no source read states equivalence, so both stay): `small white beans` / `navy beans`, `carioca beans` / `pinto beans`.

### Synonym candidates (for a later owner-approved synonym step; NOT staged)

| from | to | origin | basis |
|---|---|---|---|
| dark red kidney beans | kidney beans | dedupe | cultivar-shade variant of the FDC umbrella record 'Beans, kidney, all types'; one canonical row |
| light red kidney beans | kidney beans | dedupe | cultivar-shade variant of 'Beans, kidney, all types'; one canonical row |
| garbanzo beans | chickpeas | fdc_alt_name | FDC bracketed/alternate name of the same record (naming evidence) |
| blackeye pea | cowpeas | dedupe | FDC lists 'blackeyes' as an alternate name of 'Cowpeas, common' (record attribute); same food, one canonical row |
| mat bean | mothbeans | fdc_alt_name | FDC bracketed/alternate name of the same record (naming evidence) |
| moth bean | mothbeans | fdc_alt_name | FDC bracketed/alternate name of the same record (naming evidence) |
| california red kidney beans | kidney beans | dedupe | cultivar variant of 'Beans, kidney, all types'; one canonical row |
| red kidney beans | kidney beans | dedupe | cultivar-shade variant of 'Beans, kidney, all types'; one canonical row |
| common cowpeas | cowpeas | dedupe | FDC record 'Cowpeas, common (blackeyes, crowder, southern)': 'common' is the species group qualifier; one canonical row |
| blackeyes | cowpeas | fdc_alt_name | FDC bracketed/alternate name of the same record (naming evidence) |
| crowder | cowpeas | fdc_alt_name | FDC bracketed/alternate name of the same record (naming evidence) |
| large lima beans | lima beans | dedupe | size-grade variant of lima beans (FDC 'large' vs 'thin seeded (baby)'); one canonical row |
| thin seeded lima beans | lima beans | dedupe | size-grade variant of lima beans; one canonical row |
| pink or red lentils | lentils | dedupe | market-grade variant of lentils (existing term); duplicate semantics |
| black turtle beans | black beans | dedupe | INFERENCE (owner to confirm): black turtle is a black-bean cultivar group; FDC files both as plain dry black beans; one canonical row |
| royal red kidney beans | kidney beans | dedupe | cultivar variant of 'Beans, kidney, all types'; one canonical row |
| fava beans | broadbeans | fdc_alt_name | FDC bracketed/alternate name of the same record (naming evidence) |

**Already mapped in synonyms.csv (not re-proposed; flagged):** `bengal gram` -> existing `chana dal` (FDC says it names `chickpeas`); `red gram` -> existing `toor dal` (FDC says it names `pigeon peas`). Both targets are whole_food Group 1 pulses, so the NOVA placement does not differ; the existing mapping is the split dal form and is left untouched.

## 4. Representative inspection: 16 accepted rows with the FDC attributes checked

| FDC id | name | -> term | attributes checked |
|---|---|---|---|
| 335245 | Beans, Dry, Dark Red Kidney (0% moisture) | kidney beans | foundation_food; cat 'Legumes and Legume Products'; FoodOn '-'; taxon -; alt names '-'; portions '-' |
| 335306 | Beans, Dry, Pink (0% moisture) | pink beans | foundation_food; cat 'Legumes and Legume Products'; FoodOn '-'; taxon -; alt names '-'; portions '-' |
| 335419 | Beans, Dry, Navy (0% moisture) | navy beans | foundation_food; cat 'Legumes and Legume Products'; FoodOn '-'; taxon -; alt names '-'; portions '-' |
| 335428 | Beans, Dry, Flor de Mayo (0% moisture) | flor de mayo beans | foundation_food; cat 'Legumes and Legume Products'; FoodOn '-'; taxon -; alt names '-'; portions '-' |
| 335433 | Beans, Dry, Carioca (0% moisture) | carioca beans | foundation_food; cat 'Legumes and Legume Products'; FoodOn '-'; taxon -; alt names '-'; portions '-' |
| 335695 | Beans, Dry, Pinto (0% moisture) | pinto beans | foundation_food; cat 'Legumes and Legume Products'; FoodOn '-'; taxon -; alt names '-'; portions '-' |
| 335782 | Beans, Dry, Cranberry (0% moisture) | cranberry beans | foundation_food; cat 'Legumes and Legume Products'; FoodOn '-'; taxon -; alt names '-'; portions '-' |
| 335912 | Beans, Dry, Black (0% moisture) | black beans | foundation_food; cat 'Legumes and Legume Products'; FoodOn '-'; taxon -; alt names '-'; portions '-' |
| 335927 | Beans, Dry, Small White (0% moisture) | small white beans | foundation_food; cat 'Legumes and Legume Products'; FoodOn '-'; taxon -; alt names '-'; portions '-' |
| 336067 | Beans, Dry, Great Northern (0% moisture) | great northern beans | foundation_food; cat 'Legumes and Legume Products'; FoodOn '-'; taxon -; alt names '-'; portions '-' |
| 2644281 | Beans, cannellini, dry | cannellini beans | foundation_food; cat 'Legumes and Legume Products'; FoodOn 'white kidney bean'; taxon NCBITaxon_3885; alt names '-'; portions '-' |
| 2644282 | Chickpeas, (garbanzo beans, bengal gram), dry | chickpeas | foundation_food; cat 'Legumes and Legume Products'; FoodOn 'chickpea (dried)'; taxon NCBITaxon_3827; alt names '-'; portions '-' |
| 2644283 | Lentils, dry | lentils | foundation_food; cat 'Legumes and Legume Products'; FoodOn 'lentil (dried)'; taxon NCBITaxon_3864; alt names '-'; portions '-' |
| 2644284 | Blackeye pea, dry | cowpeas | foundation_food; cat 'Legumes and Legume Products'; FoodOn 'blackeyed pea (raw)'; taxon NCBITaxon_3917; alt names '-'; portions '-' |
| 172423 | Lupins, mature seeds, raw | lupins | sr_legacy_food; cat 'Legumes and Legume Products'; FoodOn '-'; taxon -; alt names '-'; portions 'cup' |
| 172425 | Mothbeans, mature seeds, raw | mothbeans | sr_legacy_food; cat 'Legumes and Legume Products'; FoodOn '-'; taxon -; alt names 'mat bean, moth bean'; portions 'cup' |

## 5. Representative inspection: 12 rejected and 10 queued rows with the reason

| decision | FDC id | name | reason | attributes checked |
|---|---|---|---|---|
| REJECT | 321358 | Hummus, commercial | processed_word: word guard ['commercial']: outside a plain dry/raw seed | foundation_food; cat 'Legumes and Legume Products'; FoodOn 'hummus'; taxon NCBITaxon_3827; alt names '-'; port |
| REJECT | 324860 | Peanut butter, smooth style, with salt | processed_word: word guard ['salt', 'smooth']: outside a plain dry/raw seed | foundation_food; cat 'Legumes and Legume Products'; FoodOn '-'; taxon -; alt names '-'; portions '-' |
| REJECT | 1750337 | Soy milk, unsweetened, plain, shelf stable | processed_word: word guard ['plain']: outside a plain dry/raw seed | foundation_food; cat 'Legumes and Legume Products'; FoodOn '-'; taxon -; alt names '-'; portions '-' |
| REJECT | 2257044 | Soy milk, sweetened, plain, refrigerated | processed_word: word guard ['plain', 'sweetened']: outside a plain dry/raw seed | foundation_food; cat 'Legumes and Legume Products'; FoodOn 'soybean milk'; taxon NCBITaxon_3847; alt names '-' |
| REJECT | 2262072 | Peanut butter, creamy | processed_word: word guard ['creamy']: outside a plain dry/raw seed | foundation_food; cat 'Legumes and Legume Products'; FoodOn 'peanut butter (creamy)'; taxon NCBITaxon_3818; alt |
| REJECT | 2644285 | Beans, black, canned, sodium added, drained and rinsed | processed_word: word guard ['canned', 'drained', 'rinsed', 'sodium']: outside a plain dry/raw seed | foundation_food; cat 'Legumes and Legume Products'; FoodOn 'black turtle bean'; taxon NCBITaxon_3885; alt name |
| REJECT | 167722 | Tofu yogurt | product_word: product word(s) ['tofu', 'yogurt']: a product made from a legume, not the legume | sr_legacy_food; cat 'Legumes and Legume Products'; FoodOn '-'; taxon -; alt names '-'; portions 'cup' |
| REJECT | 168106 | Papad | product_word: product word(s) ['papad']: a product made from a legume, not the legume | sr_legacy_food; cat 'Legumes and Legume Products'; FoodOn '-'; taxon -; alt names '-'; portions '-' |
| REJECT | 169083 | Soybean, curd cheese | product_word: product word(s) ['cheese', 'curd']: a product made from a legume, not the legume | sr_legacy_food; cat 'Legumes and Legume Products'; FoodOn '-'; taxon -; alt names '-'; portions 'cup' |
| REJECT | 169884 | Vermicelli, made from soy | product_word: product word(s) ['vermicelli']: a product made from a legume, not the legume | sr_legacy_food; cat 'Legumes and Legume Products'; FoodOn '-'; taxon -; alt names '-'; portions 'cup' |
| REJECT | 172442 | Miso | product_word: product word(s) ['miso']: a product made from a legume, not the legume | sr_legacy_food; cat 'Legumes and Legume Products'; FoodOn '-'; taxon -; alt names '-'; portions 'cup|tbsp' |
| REJECT | 172443 | Natto | product_word: product word(s) ['natto']: a product made from a legume, not the legume | sr_legacy_food; cat 'Legumes and Legume Products'; FoodOn '-'; taxon -; alt names '-'; portions 'cup' |
| QUEUE | 335425 | Beans, Dry, Brown (0% moisture) | generic_name: A bare colour or pod-versus-seed name does not establish a distinct food: 'brown/tan/light tan/red/small red/m | foundation_food; cat 'Legumes and Legume Products'; FoodOn '-'; taxon -; alt names '-'; portions '-' |
| QUEUE | 335442 | Beans, Dry, Tan (0% moisture) | generic_name: A bare colour or pod-versus-seed name does not establish a distinct food: 'brown/tan/light tan/red/small red/m | foundation_food; cat 'Legumes and Legume Products'; FoodOn '-'; taxon -; alt names '-'; portions '-' |
| QUEUE | 1104705 | Flour, soy, defatted | queue_flour: a flour is placed by the 'flours' class (PMC10127522 fn2, NUPENS), not by the legumes clause; kind flour belon | foundation_food; cat 'Legumes and Legume Products'; FoodOn 'soybean flour (defatted)'; taxon NCBITaxon_3847; a |
| QUEUE | 1104766 | Flour, soy, full-fat | queue_flour: a flour is placed by the 'flours' class (PMC10127522 fn2, NUPENS), not by the legumes clause; kind flour belon | foundation_food; cat 'Legumes and Legume Products'; FoodOn 'soybean flour'; taxon NCBITaxon_3847; alt names '- |
| QUEUE | 2515376 | Peanuts, raw | queue_peanuts: same as peanut | foundation_food; cat 'Legumes and Legume Products'; FoodOn 'peanut (raw)'; taxon NCBITaxon_3818; alt names '-' |
| QUEUE | 172430 | Peanuts, all types, raw | queue_peanuts: same as peanut | sr_legacy_food; cat 'Legumes and Legume Products'; FoodOn '-'; taxon -; alt names '-'; portions 'cup|oz' |
| QUEUE | 172445 | Soy meal, defatted, raw | queue_meal: defatted/ground fraction: not established as a plain flour or a whole legume. | sr_legacy_food; cat 'Legumes and Legume Products'; FoodOn '-'; taxon -; alt names '-'; portions 'cup' |
| QUEUE | 174259 | Mungo beans, mature seeds, raw | dedupe_stays_out: 'mungo' vs 'mung' beans: the FDC record does not establish which pulse a label word means (black gram vs green | sr_legacy_food; cat 'Legumes and Legume Products'; FoodOn '-'; taxon -; alt names '-'; portions 'cup' |
| QUEUE | 174267 | Peanut flour, defatted | queue_peanut: overlaps the CONDITIONED FAO nuts/seeds clause ('tree and ground nuts and other oily seeds (with no added salt | sr_legacy_food; cat 'Legumes and Legume Products'; FoodOn '-'; taxon -; alt names '-'; portions 'cup|oz' |
| QUEUE | 175208 | Cowpeas, catjang, mature seeds, raw | dedupe_stays_out: subspecies distinction (catjang) is not established as a label term; stays out rather than inflating the lexic | sr_legacy_food; cat 'Legumes and Legume Products'; FoodOn '-'; taxon -; alt names '-'; portions 'cup' |

Attribute use: Foundation records give a FoodOn name and NCBI taxon; SR records give 'alternate names' (used only as synonym candidates and to confirm dedupe, e.g. 'blackeyes' for cowpeas); portion descriptors are checked for guard words (a record named raw whose portions say cooked would be QUEUED; 0 such cases here). Where the name alone could not establish the plain form (colour-only market classes, pod versus seed, subspecies), the case was QUEUED, not accepted.

## 6a. The legume guard (item-level condition), per form, against the quoted clauses
Why: `descriptors.csv` drops salted/sugared words, so `salted soybeans` answered Group 1 (pre-existing). Adding 21 legume rows would have extended that. The guard is NOT the nut rule copied: each form is reasoned against the quoted clauses.
- FAO Group 3 definition (Table 1, p.12): "Products made by adding salt, oil, sugar or other group 2 ingredients to group 1 foods". Example (p.12; prose p.7 'canned or bottled vegetables or legumes (pulses) preserved in brine'): "Canned or bottled vegetables and legumes in brine".
- Item's OWN name or bracket says salt / salted / sugar / sugared / sweetened / candied / honey / glazed / jaggery / syrup / brine / brined: a group 1 legume with a group 2 ingredient added = Group 3 (definition); brine = the Group 3 example. Single item or in a list, the item is read as Group 3 material; it is NEVER Group 1 via the legume clause.
- Negated forms (`no added salt`, `unsalted`, `salt free`, `without salt`): condition met, Group 1 kept.
- canned / tinned / bottled / jarred / preserved / pickled WITHOUT salt, sugar or brine: the clause names legumes in brine only, and a plain-legume Group 1 is not supported either, so the item ABSTAINS (never an invented Group 3).
- Items outside the vocabulary (`canned kidney beans`, `baked beans`, `kidney beans in brine`, `sweetened adzuki beans`) stay unassessed: no row reads them.
- Roasted and boiled/cooked plain forms: UNCHANGED. FAO Group 1 definition (p.6) names roasting and boiling among the minimal processes, so the existing descriptors.csv behaviour (`roasted soybeans`, `boiled lentils` -> Group 1) has source fit for plain legumes.
- Applies to 33 rows: the 21 new rows and 12 existing rows retyped from `whole_food` to `legume` (beans, peas, chickpea, lentil, rajma, moong, soybean, toor dal, moong dal, chana dal, masoor dal, urad dal). Only the `kind` column changed on those 12; their `source` text is unchanged (no row removed, no source changed: gate-checked).
- Observed effect on EXISTING rows (before -> after): `salted soybeans` 1->3, `chickpeas (canned, salted)` 1->3, `moong dal (salted)` 1->3, `salted peas` 1->3 (guard), `chickpeas (pickled)`, `beans (bottled)`, `lentils (tinned)` 1->abstain.

## 6. Gates (applied state)
BEFORE = a worktree of main (646ba5b, no legume rows, old classifier); AFTER = the COMMITTED branch source; each analysed in a SEPARATE fresh process (`scripts/applied_gate.py`; the same result was reproduced on the clean committed tree).
- (a) After-build proof: 21 of 21 staged terms are recognised after and were NOT recognised before; lexicon rows 160 -> 181 (+21 added, 0 removed, 0 sources changed, 12 kinds retyped); synonyms.csv and markers.csv byte-identical.
- (b) Frozen 66: changed inputs 0, unexplained 0, abstain->4 0, abstain->1 0, other group changes 0. Out-of-sample 32: changed 0, unexplained 0, abstain->4 0, abstain->1 0, other 0. (0 changes = no corpus evidence either way: none of the 98 inputs holds a staged or retyped legume term; these rows are not corpus-validated.)
- Drift over 286 existing lexicon terms and synonyms analysed alone: 0 differences.
- (c) Controls (label order, as the item would appear). Negative: never Group 1 via the new rows; positive: the placement is kept.

| control | group before | group after | row kind after | driver / reason |
|---|---|---|---|---|
| salted pinto beans | None | 3 | legume | legume with added salt, sugar or brine (FAO Gr |
| pinto beans (salted) | None | 3 | legume | legume with added salt, sugar or brine (FAO Gr |
| pinto beans (in brine) | None | 3 | legume | legume with added salt, sugar or brine (FAO Gr |
| kidney beans in brine | None | None | - | ingredients not in the local vocabulary, so pr |
| canned kidney beans | None | None | - | ingredients not in the local vocabulary, so pr |
| kidney beans (canned) | None | None | legume | a canned, bottled or preserved legume (kidney  |
| baked beans | None | None | - | ingredients not in the local vocabulary, so pr |
| refried beans | None | None | - | ingredients not in the local vocabulary, so pr |
| sweetened adzuki beans | None | None | - | ingredients not in the local vocabulary, so pr |
| adzuki beans (sweetened) | None | 3 | legume | legume with added salt, sugar or brine (FAO Gr |
| salted soybeans | 1 | 3 | legume | legume with added salt, sugar or brine (FAO Gr |
| chickpeas (canned, salted) | 1 | 3 | legume | legume with added salt, sugar or brine (FAO Gr |
| chickpeas (pickled) | 1 | None | legume | a canned, bottled or preserved legume (chickpe |
| beans (bottled) | 1 | None | legume | a canned, bottled or preserved legume (beans ( |
| lentils (tinned) | 1 | None | legume | a canned, bottled or preserved legume (lentils |
| moong dal (salted) | 1 | 3 | legume | legume with added salt, sugar or brine (FAO Gr |
| salted peas | 1 | 3 | legume | legume with added salt, sugar or brine (FAO Gr |
| pinto beans (pinto beans, salt) | None | 3 | legume | legume with added salt, sugar or brine (FAO Gr |
| rice, salted pinto beans | None | 3 | - | recognised whole food |
| hummus | None | None | - | ingredients not in the local vocabulary, so pr |
| pinto beans | None | 1 | legume | single recognised unprocessed food |
| kidney beans | None | 1 | legume | single recognised unprocessed food |
| chickpeas | 1 | 1 | legume | single recognised unprocessed food |
| lentils | 1 | 1 | legume | single recognised unprocessed food |
| unsalted pinto beans | None | 1 | legume | single recognised unprocessed food |
| pinto beans (no added salt) | None | 1 | legume | single recognised unprocessed food |
| pinto beans (salt free) | None | 1 | legume | single recognised unprocessed food |
| kidney beans (cooked) | None | 1 | legume | single recognised unprocessed food |
| roasted soybeans | 1 | 1 | legume | single recognised unprocessed food |
| boiled lentils | 1 | 1 | legume | single recognised unprocessed food |
| soybeans (roasted) | 1 | 1 | legume | single recognised unprocessed food |
| rice, salt, pinto beans | None | 3 | - | recognised whole food |
| beans, salt | 3 | 3 | - | recognised whole food |
| moong dal | 1 | 1 | legume | single recognised unprocessed food |
| split green peas | 1 | 1 | legume | single recognised unprocessed food |
| mung beans | 1 | 1 | legume | single recognised unprocessed food |
| black beans | None | 1 | legume | single recognised unprocessed food |
| peas | 1 | 1 | legume | single recognised unprocessed food |

- validate_batch (rows against the pre-batch build): schema 0 errors, provenance 0 errors, FAO clause verbatim: PASS, 21 ready rows, 5 already-covered terms dropped. Suite and parity: see the status line at the stop.

## 7. Open points for the owner

1. `mothbeans`, `broadbeans`, `lupins`, `winged beans`, `yardlong beans` follow the FDC spelling; label spellings (`moth beans`, `broad beans`) are synonym candidates only.
2. `black turtle beans` -> `black beans` is an INFERENCE (cultivar group), flagged for confirmation.
3. Flours (soy, peanut, carob, besan) and peanuts are QUEUED to the flour and Nut/Seed batches (different clause or conditioned clause).
4. The 'Soy' products (tofu, tempeh, miso, natto, milk, protein fractions) are REJECTED here: they are products, not instances of the legumes clause.

## Regenerate (refuses to overwrite without --force)
```
python scripts/class_batch.py --candidates <fdc candidates.csv> --rule data/ingest/class_legumes_1.json --out evaluation/class_bulk_1/legumes
python scripts/validate_batch.py --staged evaluation/class_bulk_1/legumes/staged_rows.csv --decisions evaluation/class_bulk_1/legumes/decisions.csv --candidates evaluation/class_bulk_1/legumes/candidates_category.csv --rule data/ingest/class_legumes_1.json --policy data/ingest/variant_policy_class_legumes_1.json --fao-text <pdftotext -layout FAO> --out evaluation/class_bulk_1/legumes/gate
python scripts/class_gate.py --gate evaluation/class_bulk_1/legumes/gate --rule data/ingest/class_legumes_1.json --out evaluation/class_bulk_1/legumes/class_gate --force
```
