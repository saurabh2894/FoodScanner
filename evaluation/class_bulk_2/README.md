# class_bulk_2 / Batch 2: FDC 'Vegetables and Vegetable Products' (PROPOSAL; merge HELD behind the legume guard)

Status: STAGED on branch claude/class-bulk-2 (off main a66aae1, which already holds the legume guard). The branch's lexicon.csv carries the rows so the applied-state gate is real; main is NOT changed. validate_batch: **READY_FOR_REVIEW**; applied_gate: **READY_FOR_REVIEW**. Rule: `data/ingest/class_vegetables_1.json` (class-vegetables-1). Mapper `scripts/class_batch.py`, applier `scripts/class_apply.py`, gates `scripts/validate_batch.py` + `scripts/applied_gate.py`. FDC supplies NAMING and record attributes only.

## 1. Category source rules (written BEFORE any acceptance)

FAO 2019 (ca5644en.pdf), Table 1, Group 1, p.11. Verified verbatim in the report text by the gate. Three clauses, routed by head word:

| id | verbatim clause | applies to | inference level |
|---|---|---|---|
| V1 | Fresh, squeezed, chilled, frozen, or dried fruit and leafy and root vegetables | default: leafy, root, stem, flower, bulb and fruit vegetables | inference level: class-instance of vegetables; the clause names 'leafy and root vegetables'; stem, flower, bulb and fruit-vegetables (tomato, cauliflower, onion, courgette) are instances of the Group 1 definition 'edible parts of plants (fruit, seeds, leaves, stems, roots, tubers)' (same table), not named by the example |
| V2 | starchy roots and tubers such as potatoes, sweet potatoes and cassava | head words: potato, potatoes, cassava, yam, yams, taro, yautia, arrowroot, arrowhead, jicama, yambean, rutabaga... | inference level: class-instance of starchy roots and tubers (the clause names potatoes, sweet potatoes and cassava) |
| V3 | fungi such as fresh or dried mushrooms | head words: mushroom, mushrooms, shiitake, chanterelle, morel, enoki, maitake, portabella, crimini, oyster, pioppini, jew... | inference level: class-instance of fungi (the clause names fresh or dried mushrooms) |

Group 1 definition (same table): "Edible parts of plants (fruit, seeds, leaves, stems, roots, tubers) ... and also fungi, algae, all after separation from nature." Group 3 (Table 1 continuation): "Canned or bottled vegetables and legumes in brine"; definition "Products made by adding salt, oil, sugar or other group 2 ingredients to group 1 foods".

Scope: The clause is unconditioned and names the forms fresh, squeezed, chilled, frozen or dried. A plain raw or frozen-unprepared vegetable is an instance. Cooked, canned, pickled, salted, sauced, fried, mashed or otherwise prepared forms, vegetable products (sauce, juice, puree, chips, fries, flour, powder, dishes) and mixtures are not instances of this clause.

**Acceptance criteria**

- A1. The FDC food category is exactly 'Vegetables and Vegetable Products'.
- A2. The plain form is established by the name ('raw', or 'frozen' + 'unprepared', both forms the clause names) OR by the record attribute: a Foundation record whose FoodOn item name states '(raw)' where the description does not.
- A3. The name holds no word from the word guard, no product word and no queue word; the head is a single food (a head naming two foods with 'and' is a mixture: QUEUE).
- A4. Record attributes do not contradict the plain form (no portion descriptor holding a guard word).
- A5. The derived label term is a distinct food name: else QUEUE.
- A6. Canonical deduplication: cut, grade, colour-shade and cultivar variants of one food collapse into ONE row (table 'canonical' and the collapse-word rule); the rest are synonym CANDIDATES (synonyms.csv is not touched).

**Rejection word guard** (anywhere in the name = REJECT, processed): `canned`, `pickled`, `salted`, `salt`, `sweetened`, `sugar`, `cooked`, `boiled`, `fried`, `stir-fried`, `roasted`, `grilled`, `sauteed`, `steamed`, `microwaved`, `baked`, `mashed`, `creamed`, `scalloped`, `stuffed`, `glazed`, `candied`, `flavored`, `flavoured`, `fortified`, `seasoned`, `marinated`, `smoked`, `cured`, `concentrate`, `concentrated`, `juice`, `sauce`, `soup`, `mix`, `mixed`, `blend`, `prepared`, `supplement`, `drained`, `solids`, `liquid`, `sodium`, `low`, `reduced`, `regular`, `pack`, `home-prepared`, `commercial`, `restaurant`, `instant`, `butter`, `cheese`, `cream`, `oil`, `dressing`, `gravy`, `pork`, `bacon`, `sausage`, `egg`, `milk`, `ultraviolet`, `hash`, `o'brien`, `wedges`, `sticks`, `patties`, `pancakes`, `fries`, `puffs`, `tots`, `chips`, `souffle`, `pudding`, `salsa`, `succotash`, `tempura`, `relish`, `catsup`, `ketchup`, `paste`, `puree`, `salad`, `kimchi`, `sauerkraut`, `pickles`, `jam`, `chutney`, `poi`, `unsalted`; phrases `baby food`, `food distribution`, `french fried`, `par fried`, `home prepared`, `no salt added`, `with salt`, `without salt`, `o'brien`. The category-wide extension of the Spices and Herbs word guard (owner rule 3): any treatment, addition, cooking/canning liquid, product or dish word puts the name outside a plain raw or frozen-unprepared vegetable. 'baby' is NOT guarded (baby carrots are a plain cut); 'unprepared' is the clause-compatible frozen form (tokenised separately from 'prepared'); UV-exposed mushrooms (a treatment) are rejected.

**Product words** (REJECT): `flour`, `starch`, `powder`, `flakes`, `granules`, `tomato products`. **Queue words** (QUEUE, conditional): `sprouted`; `seaweed`; `corn`; `immature`; `mature seeds`; `soybeans`; `edamame`; `cowpeas`; `peas`; `fava`; `yardlong`; `winged`; `dried`; `dehydrated`; `hearts of palm`; `fiddlehead`; `lemon grass`; `ginger`; `garlic`; `parsley`; `coriander`; `epazote`; `chives`; `wasabi`; `yeast`; `turnip greens and turnips`; `peas and`; `flowers`; `flower` (each with its reason in the rule file).

**Kind**: `vegetable` (whole-food behaviour plus the item-level guard of section 6a). Mushrooms and tubers use the same kind: FAO Group 3 names vegetables in brine and the guard is the same.

## 2. Measured results

| Measure | Count |
|---|---|
| FDC candidates in the category | 913 |
| ACCEPT (candidate records) | 229 |
| canonical rows after dedupe | 122 |
| already recognised by the build (dropped as duplicates) | 8: cabbage, carrots, cucumber, fennel, green onions, onions, potatoes, tomatoes |
| NEW lexicon rows proposed | 114 |
| QUEUE (conditional, never accepted) | 111 |
| REJECT | 573 |
| synonym CANDIDATES (not merged) | 99 (+0 already mapped elsewhere) |
| existing rows retyped whole_food -> vegetable (kind column only) | 6: cucumber, tomato, potato, onion, carrot, cabbage |

Reject codes: {"processed_word": 568, "product_word": 5}  
Queue codes: {"queue_garlic": 2, "plain_form_not_stated": 24, "dedupe_stays_out": 9, "queue_corn": 7, "queue_seaweed": 10, "queue_hearts_of_palm": 1, "queue_yeast": 1, "queue_sprouted": 9, "queue_immature": 10, "queue_cowpeas": 2, "queue_edamame": 1, "queue_dried": 7, "queue_flower": 2, "queue_lemon_grass": 1, "queue_fava": 1, "queue_wasabi": 1, "queue_fiddlehead": 2, "queue_yardlong": 1, "queue_ginger": 1, "queue_flowers": 1, "queue_soybeans": 1, "queue_epazote": 1, "queue_chives": 2, "queue_coriander": 1, "queue_peas": 6, "attribute_contradicts_plain": 1, "queue_winged": 2, "queue_parsley": 2, "queue_turnip_greens_and_turnips": 1, "queue_dehydrated": 1}

### Proposed new rows (114)

acorn squash, amaranth leaves, arrowhead, artichokes, arugula, asparagus, balsam-pear, bamboo shoots, banana peppers, beet greens, bell peppers, bok choy cabbage, borage, broccoli, broccoli raab, brussels sprouts, burdock root, butterbur, butterhead lettuce, butternut squash, cardoon, cassava, cauliflower, celeriac, celtuce, chanterelle mushrooms, chayote, chicory greens, chicory roots, chinese broccoli, chinese cabbage, chinese waterchestnuts, chrysanthemum leaves, collards, cornsalad, crimini mushrooms, dandelion greens, dishcloth gourd, dock, drumstick leaves, drumstick pods, eggplant, endive, enoki mushrooms, eppaw, garden cress, garland chrysanthemum, grape leaves, hawaii mountain yam, hot chili peppers, hubbard squash, iceberg lettuce, jalapeno peppers, jerusalem-artichokes, jew's ear, jute, kale, kohlrabi, lambsquarters, leaf lettuce, leeks, lotus root, maitake mushrooms, morel mushrooms, mustard greens, mustard spinach, napa cabbage, new zealand spinach, nopales, okra, oriental radishes, oyster mushrooms, parsnips, poblano peppers, pokeberry shoots, portabella mushrooms, pumpkin, pumpkin leaves, purslane, radicchio, radishes, romaine lettuce, rutabagas, salsify, savoy cabbage, serrano peppers, shallots, shiitake mushrooms, snap beans, spaghetti squash, spinach, summer squash, sweet peppers, sweet potato leaves, sweet potatoes, swiss chard, taro, taro leaves, taro shoots, tomatillos, turnip greens, turnips, vinespinach, water convolvulus, watercress, waxgourd, white mushrooms, white-flowered gourd, winter squash, witloof chicory, yam, yambean, yautia, zucchini

Existing-term collisions NOT added: `fennel` (the existing row is the seed spice; the FDC record is the bulb, a different plant part: bare 'fennel' left untouched). `celery`, `beets`, `arrowroot`: see section 7.

## 3. Canonical deduplication decisions

Colour shades, size, cut and cultivar-shade variants collapse into one row; named cultivars that carry their own food name (butternut, acorn, hubbard, spaghetti squash; savoy, napa, bok choy cabbage) stay separate; plant-part variants (leaves, stalks, tips) stay out. Variant policy `variant_policy_class_vegetables_1.json` keeps separate rows next to the untouched generic rows (cabbage, beans, celery seed, mustard, pumpkin seeds, water).

| FDC-derived term | canonical | decision basis |
|---|---|---|
| green bell peppers | bell peppers | colour-shade variant of one food; one canonical row |
| red bell peppers | bell peppers | colour-shade variant of one food; one canonical row |
| yellow bell peppers | bell peppers | colour-shade variant of one food; one canonical row |
| orange bell peppers | bell peppers | colour-shade variant of one food; one canonical row |
| green sweet peppers | sweet peppers | colour-shade variant of one food; one canonical row |
| red sweet peppers | sweet peppers | colour-shade variant of one food; one canonical row |
| yellow sweet peppers | sweet peppers | colour-shade variant of one food; one canonical row |
| green hot chili peppers | hot chili peppers | colour-shade variant of one food; one canonical row |
| red hot chili peppers | hot chili peppers | colour-shade variant of one food; one canonical row |
| banana pepper | banana peppers | FDC names banana, Hungarian wax and Hungarian peppers in the same 'Peppers' series; cultivar variants of one food; one canonical row (INFERENCE: owner to confirm) |
| banana or hungarian wax peppers | banana peppers | FDC names banana, Hungarian wax and Hungarian peppers in the same 'Peppers' series; cultivar variants of one food; one canonical row (INFERENCE: owner to confirm) |
| hungarian peppers | banana peppers | FDC names banana, Hungarian wax and Hungarian peppers in the same 'Peppers' series; cultivar variants of one food; one canonical row (INFERENCE: owner to confirm) |
| green leaf lettuce | leaf lettuce | colour-shade variant of one food; one canonical row |
| green lettuce | leaf lettuce | colour-shade variant of one food; one canonical row |
| red leaf lettuce | leaf lettuce | colour-shade variant of one food; one canonical row |
| red lettuce | leaf lettuce | colour-shade variant of one food; one canonical row |
| cos or romaine lettuce | romaine lettuce | FDC 'Lettuce, cos or romaine': cos and romaine are one lettuce; one canonical row |
| green romaine lettuce | romaine lettuce | FDC 'Lettuce, cos or romaine': cos and romaine are one lettuce; one canonical row |
| red tomatoes | tomatoes | cultivar/size/cut variant of one food; one canonical row |
| green tomatoes | tomatoes | cultivar/size/cut variant of one food; one canonical row |
| yellow tomatoes | tomatoes | cultivar/size/cut variant of one food; one canonical row |
| orange tomatoes | tomatoes | cultivar/size/cut variant of one food; one canonical row |
| roma tomato | tomatoes | cultivar/size/cut variant of one food; one canonical row |
| grape tomatoes | tomatoes | cultivar/size/cut variant of one food; one canonical row |
| gold potatoes | potatoes | cultivar/size/cut variant of one food; one canonical row |
| red potatoes | potatoes | cultivar/size/cut variant of one food; one canonical row |
| russet potatoes | potatoes | cultivar/size/cut variant of one food; one canonical row |
| white potatoes | potatoes | cultivar/size/cut variant of one food; one canonical row |
| sweet potato | sweet potatoes | same food (FDC singular/plural and flesh-colour entries); one canonical row |
| orange flesh sweet potatoes | sweet potatoes | same food (FDC singular/plural and flesh-colour entries); one canonical row |
| red onions | onions | cultivar/size/cut variant of one food; one canonical row |
| white onions | onions | cultivar/size/cut variant of one food; one canonical row |
| yellow onions | onions | cultivar/size/cut variant of one food; one canonical row |
| sweet onions | onions | cultivar/size/cut variant of one food; one canonical row |
| welsh onions | onions | cultivar/size/cut variant of one food; one canonical row |
| spring or scallions onions | green onions | FDC 'Onions, spring or scallions' and 'Green onion, (scallion)': one food; one canonical row |
| green onion | green onions | FDC 'Onions, spring or scallions' and 'Green onion, (scallion)': one food; one canonical row |
| green cabbage | cabbage | colour-shade variant of one food; one canonical row |
| red cabbage | cabbage | colour-shade variant of one food; one canonical row |
| red radishes | radishes | colour-shade variant of one food; one canonical row |
| white icicle radishes | radishes | cultivar variant of radishes; one canonical row |
| rutabaga | rutabagas | same food, singular/plural FDC entries; one canonical row |
| green asparagus | asparagus | colour-shade variant of one food; one canonical row |
| green cauliflower | cauliflower | colour-shade variant of one food; one canonical row |
| baby arugula | arugula | size variant; one canonical row |
| baby carrots | carrots | size/cut variant (a plain cut); one canonical row |
| baby zucchini squash | zucchini | size variant; one canonical row |
| zucchini summer squash | zucchini | FDC 'Squash, summer, zucchini'; one canonical row |
| zucchini green summer squash | zucchini | FDC 'Squash, summer, zucchini'; one canonical row |
| yellow summer squash | summer squash | FDC 'Squash, summer' series; cultivar variants of one food; one canonical row |
| crookneck and straightneck summer squash | summer squash | FDC 'Squash, summer' series; cultivar variants of one food; one canonical row |
| scallop summer squash | summer squash | FDC 'Squash, summer' series; cultivar variants of one food; one canonical row |
| acorn winter squash | acorn squash | named winter squash, kept as its own food name |
| butternut winter squash | butternut squash | named winter squash |
| hubbard winter squash | hubbard squash | named winter squash |
| spaghetti winter squash | spaghetti squash | same food as 'Squash, spaghetti' |
| pie pumpkin squash | pumpkin | FDC 'Squash, pie pumpkin' and 'Pumpkin, raw'; one canonical row (INFERENCE: owner to confirm) |
| green snap beans | snap beans | colour-shade variant of one food; one canonical row |
| yellow snap beans | snap beans | colour-shade variant of one food; one canonical row |
| oyster mushroom | oyster mushrooms | same food, singular/plural FDC entries |
| or crimini italian brown mushrooms | crimini mushrooms | FDC 'Mushrooms, brown, italian, or crimini': crimini is the label name; one canonical row |
| leaves broccoli | (stays out) | plant-part variant of a food (leaves, stalks, tips): not established as a label term; stays out rather than inflating the lexicon |
| stalks broccoli | (stays out) | plant-part variant of a food (leaves, stalks, tips): not established as a label term; stays out rather than inflating the lexicon |
| leaves fireweed | (stays out) | plant-part variant of a food (leaves, stalks, tips): not established as a label term; stays out rather than inflating the lexicon |
| leafy tips balsam-pear | (stays out) | plant-part variant of a food (leaves, stalks, tips): not established as a label term; stays out rather than inflating the lexicon |
| pods balsam-pear | balsam-pear | FDC 'Balsam-pear (bitter gourd), pods'; the bracketed alternate 'bitter gourd' is a synonym candidate |
| potherb jute | jute | FDC 'Jute, potherb' (a leafy vegetable); one canonical row |
| fruit chayote | chayote | FDC 'Chayote, fruit' |
| tahitian taro | taro | cultivar variant of taro; one canonical row |
| beets | (stays out) | NAME COLLISION (observed in out-of-sample label S30 'Beet Red Powder'): 'red' and 'powder' are descriptors, so 'beet red powder' (the beetroot red colour, E162) would be read as the vegetabl |
| celery | (stays out) | NAME COLLISION (observed in out-of-sample label S12 'Celery Powder'): 'powder' is a descriptor, so a celery powder (used as a curing/nitrite source) would be read as the plain vegetable cele |
| arrowroot | (stays out) | NAME COLLISION (measured): 'powder' is a descriptor, so 'arrowroot powder' (a starch extracted from the root, a FAO Group 2 'starch' example) would be read as the plain root and answer Group |

Synonym candidates (not staged): see `vegetables/synonym_candidates.csv` (99 rows: dedupe variants and FDC alternate names, e.g. 'bitter gourd' for balsam-pear, 'scallion' for green onions).

## 4. Representative inspection: 13 accepted rows with the FDC attributes checked

| FDC id | name | -> term | route | attributes checked |
|---|---|---|---|---|
| 321360 | Tomatoes, grape, raw | tomatoes | V1 | foundation_food; cat 'Vegetables and Vegetable Products'; FoodOn 'grape tomato (raw)'; taxon NCBITaxon_4081; portions '-' |
| 321900 | Broccoli, raw | broccoli | V1 | foundation_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions 'chopped' |
| 323505 | Kale, raw | kale | V1 | foundation_food; cat 'Vegetables and Vegetable Products'; FoodOn 'kale leaf (raw)'; taxon NCBITaxon_3712; portions 'pieces of ~1"' |
| 326458 | Carrots, frozen, unprepared (Includes foods for USDA's Food Distribution Program) | carrots | V1 | foundation_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions '-' |
| 168387 | Artichokes, (globe or french), frozen, unprepared | artichokes | V1 | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions 'package|package (9 oz)' |
| 168547 | Peppers, sweet, red, frozen, chopped, unprepared | sweet peppers | V1 | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions 'package (10 oz)' |
| 2258588 | Peppers, bell, green, raw | bell peppers | V1 | foundation_food; cat 'Vegetables and Vegetable Products'; FoodOn 'sweet green pepper (raw)'; taxon NCBITaxon_4072; portions '-' |
| 2346404 | Sweet potatoes, orange flesh, without skin, raw | sweet potatoes | V2 | foundation_food; cat 'Vegetables and Vegetable Products'; FoodOn 'sweet potato (raw)'; taxon NCBITaxon_4120; portions '-' |
| 2727584 | Leeks, bulb and greens, root removed, raw | leeks | V1 | foundation_food; cat 'Vegetables and Vegetable Products'; FoodOn 'leek (raw)'; taxon NCBITaxon_4681; portions '-' |
| 169242 | Mushrooms, shiitake, raw | shiitake mushrooms | V3 | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions 'piece whole' |
| 169260 | Okra, raw | okra | V1 | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions 'cup|pods (3" long)' |
| 169308 | Taro, raw | taro | V2 | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions 'cup, sliced' |
| 169985 | Cassava, raw | cassava | V2 | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions 'cup|root' |

## 5. Representative inspection: 12 rejected and 30 queued rows with the reason

| decision | FDC id | name | reason | attributes checked |
|---|---|---|---|---|
| REJECT | 321611 | Beans, snap, green, canned, regular pack, drained solids | processed_word: word guard ['canned', 'drained', 'pack', 'regular', 'solids']: outside a plain dry/raw seed | foundation_food; cat 'Vegetables and Vegetable Products'; FoodOn 'green bean (canned)'; taxon NCBITa |
| REJECT | 324317 | Onion rings, breaded, par fried, frozen, prepared, heated in oven | processed_word: word guard ['fried', 'prepared', 'par fried']: outside a plain dry/raw seed | foundation_food; cat 'Vegetables and Vegetable Products'; FoodOn 'onion ring (breaded, frozen)'; tax |
| REJECT | 324653 | Pickles, cucumber, dill or kosher dill | processed_word: word guard ['pickles']: outside a plain dry/raw seed | foundation_food; cat 'Vegetables and Vegetable Products'; FoodOn 'dill pickle'; taxon NCBITaxon_3659 |
| REJECT | 326196 | Kale, frozen, cooked, boiled, drained, without salt | processed_word: word guard ['boiled', 'cooked', 'drained', 'salt', 'without salt']: outside a plain dry/raw seed | foundation_food; cat 'Vegetables and Vegetable Products'; FoodOn 'kale (frozen)'; taxon NCBITaxon_37 |
| REJECT | 333281 | Tomatoes, canned, red, ripe, diced | processed_word: word guard ['canned']: outside a plain dry/raw seed | foundation_food; cat 'Vegetables and Vegetable Products'; FoodOn 'tomato (diced, canned)'; taxon NCB |
| REJECT | 747693 | Ketchup, restaurant | processed_word: word guard ['ketchup', 'restaurant']: outside a plain dry/raw seed | foundation_food; cat 'Vegetables and Vegetable Products'; FoodOn 'tomato catsup'; taxon NCBITaxon_40 |
| REJECT | 2003596 | Tomato juice, with added ingredients, from concentrate, shelf stable | processed_word: word guard ['concentrate', 'juice']: outside a plain dry/raw seed | foundation_food; cat 'Vegetables and Vegetable Products'; FoodOn 'tomato juice'; taxon NCBITaxon_408 |
| REJECT | 2261422 | Flour, potato | product_word: product word(s) ['flour']: a product made from a legume, not the legume | foundation_food; cat 'Vegetables and Vegetable Products'; FoodOn 'potato flour'; taxon NCBITaxon_411 |
| REJECT | 2512377 | Flour, cassava | product_word: product word(s) ['flour']: a product made from a legume, not the legume | foundation_food; cat 'Vegetables and Vegetable Products'; FoodOn 'cassava flour'; taxon NCBITaxon_39 |
| REJECT | 168446 | Potato flour | product_word: product word(s) ['flour']: a product made from a legume, not the legume | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions 'cup' |
| REJECT | 170002 | Onions, dehydrated flakes | product_word: product word(s) ['flakes']: a product made from a legume, not the legume | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions 'cup|tbsp' |
| REJECT | 170461 | Tomato powder | product_word: product word(s) ['powder']: a product made from a legume, not the legume | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions '-' |
| QUEUE | 1104647 | Garlic, raw | queue_garlic: an herb or spice per FDC in other records; kept out of this batch until the owner decides garlic's c | foundation_food; cat 'Vegetables and Vegetable Products'; FoodOn 'garlic bulb (raw)'; taxon NCBITaxo |
| QUEUE | 1750344 | Mushroom, lion's mane | plain_form_not_stated: the name does not state a raw or dry seed form; the plain form is not established by the name or by  | foundation_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions '-' |
| QUEUE | 2346405 | Celery, raw | dedupe_stays_out: NAME COLLISION (observed in out-of-sample label S12 'Celery Powder'): 'powder' is a descriptor, so a | foundation_food; cat 'Vegetables and Vegetable Products'; FoodOn 'celery stalk (raw)'; taxon NCBITax |
| QUEUE | 2710826 | Corn, sweet, yellow and white kernels,  fresh, raw | queue_corn: sweet corn overlaps the cereal-grain clause ('corn cob or kernel'): the Cereal batch owns it. | foundation_food; cat 'Vegetables and Vegetable Products'; FoodOn 'sweet corn kernel'; taxon NCBITaxo |
| QUEUE | 167602 | Seaweed, Canadian Cultivated EMI-TSUNOMATA, dry | queue_seaweed: algae are named only in the Group 1 DEFINITION ('fungi, algae'), not in an example; kind and placeme | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions 'cup' |
| QUEUE | 167714 | Hearts of palm, raw | queue_hearts_of_palm: stem of a palm: the plant-part basis is not named by the clause; QUEUE. | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions '-' |
| QUEUE | 167717 | Yeast extract spread | queue_yeast: not a vegetable. | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions 'tsp' |
| QUEUE | 168384 | Alfalfa seeds, sprouted, raw | queue_sprouted: germinated seeds (sprouts) are not named by the clause; the plant-part basis is not established. | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions 'cup|tbsp' |
| QUEUE | 168396 | Lima beans, immature seeds, raw | queue_immature: immature legume seeds overlap the legume rows (Batch 1). | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions 'cup' |
| QUEUE | 168405 | Cowpeas, young pods with seeds, raw | queue_cowpeas: legume overlap (Batch 1). | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions 'cup|pod' |
| QUEUE | 168410 | Edamame, frozen, unprepared | queue_edamame: legume overlap (Batch 1). | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions 'cup|package' |
| QUEUE | 168418 | Pepeao, dried | queue_dried: dried forms: the clause names 'dried' but earlier owner policy (dehydrated-policy-1) keeps dried/deh | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions 'cup' |
| QUEUE | 168459 | Sesbania flower, raw | queue_flower: an edible flower is not established as a vegetable by the clause; QUEUE. | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions 'cup flowers| |
| QUEUE | 168573 | Lemon grass (citronella), raw | queue_lemon_grass: an herb or spice (Spices and Herbs clause), not a vegetable; routed to that category's rule. | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions 'cup|tbsp' |
| QUEUE | 168574 | Beans, fava, in pod, raw | queue_fava: legume overlap (Batch 1). | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions 'cup|pod' |
| QUEUE | 168583 | Wasabi, root, raw | queue_wasabi: a condiment root (Spices and Herbs clause). | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions 'cup, sliced| |
| QUEUE | 168584 | Fiddlehead ferns, frozen, unprepared | queue_fiddlehead: fern shoots: not named by the clause; QUEUE. | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions '-' |
| QUEUE | 169222 | Yardlong bean, raw | queue_yardlong: legume overlap (Batch 1). | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions 'cup slices|p |
| QUEUE | 169231 | Ginger root, raw | queue_ginger: an herb or spice (Spices and Herbs clause), not a vegetable. | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions 'cup slices ( |
| QUEUE | 169270 | Pumpkin flowers, raw | queue_flowers: an edible flower is not established as a vegetable by the clause; QUEUE. | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions 'cup|flower' |
| QUEUE | 169282 | Soybeans, green, raw | queue_soybeans: legume overlap (Batch 1). | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions 'cup' |
| QUEUE | 169398 | Epazote, raw | queue_epazote: an herb (Spices and Herbs clause). | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions 'sprig|tbsp' |
| QUEUE | 169994 | Chives, raw | queue_chives: an herb (Spices and Herbs clause). | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions 'tbsp chopped |
| QUEUE | 169997 | Coriander (cilantro) leaves, raw | queue_coriander: an herb (Spices and Herbs clause). | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions 'cup|sprigs' |
| QUEUE | 170010 | Peas, edible-podded, raw | queue_peas: peas and pea pods overlap the legume rows (Batch 1); the existing 'peas' row is already a legume. | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions 'cup, chopped |
| QUEUE | 170059 | Turnips, frozen, unprepared | attribute_contradicts_plain: FDC portion attribute(s) mention ['mashed']: the record may describe a prepared form | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions 'package, mas |
| QUEUE | 170070 | Winged bean tuber, raw | queue_winged: legume overlap (Batch 1). | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions '-' |
| QUEUE | 170416 | Parsley, fresh | queue_parsley: an herb (Spices and Herbs clause). | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions 'cup chopped| |
| QUEUE | 170470 | Turnip greens and turnips, frozen, unprepared | queue_turnip_greens_and_turnips: a mixture of two foods in one record (a head naming two foods with 'and'): not a single ingredient. | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions 'package (10  |
| QUEUE | 170500 | Carrot, dehydrated | queue_dehydrated: dehydrated forms: per-term only (dehydrated-policy-1). | sr_legacy_food; cat 'Vegetables and Vegetable Products'; FoodOn '-'; taxon -; portions 'cup' |

Attribute use: Foundation FoodOn names stating '(raw)' establish the plain form where the description does not (e.g. 'Spinach, mature' -> 'spinach leaf (raw)'); Foundation records with no such statement ('Mushroom, enoki') are QUEUED. SR 'alternate names' feed synonym candidates; portion descriptors are checked for guard words.

## 6a. The vegetable guard (same condition as the legume guard, per form)

Kind `vegetable` shares the item-level condition of kind `legume` (merged in class-bulk-1): FAO Group 3 "Canned or bottled vegetables and legumes in brine" and the Group 3 definition. An item whose OWN name or bracket adds salt, sugar or brine: Group 3, never Group 1 via the vegetable clause. Canned / tinned / bottled / jarred / preserved / pickled without salt, sugar or brine: ABSTAIN. Negated forms keep Group 1. Roasted, boiled, cooked and frozen plain forms are unchanged (FAO Group 1 definition p.6 names roasting and boiling; V1 names frozen). Classifier change in this branch: `classify.py` and `foodscan.js` treat kind `vegetable` like `legume` (one tuple); parity 523/523.

Effect on the 6 existing rows (before -> after): `cucumber (pickled)`, `onions (pickled)`, `tomatoes (canned)`, `cabbage (preserved)` Group 1 -> abstain; `potatoes (salted)`, `potatoes (in brine)`, `carrots (in brine)`, `carrots (sweetened)` Group 1 -> Group 3.

## 6. Gates (applied state)

BEFORE = a worktree of main (a66aae1); AFTER = this branch's source with the rows applied; separate fresh processes (`scripts/applied_gate.py`).

- After-build proof: 114 of 114 staged terms recognised after and not before; lexicon 181 -> 295 (+114, 0 removed, 0 sources changed, 6 retyped); synonyms.csv and markers.csv byte-identical.
- Frozen 66: changed 0, unexplained 0, abstain->4 0, abstain->1 0, other 0.
- Out-of-sample 32: changed 3 (all attributed to a staged term; none changes a group: S01 [None, None] unassessed -['arugula', 'shallots']; S18 [4, 4] unassessed -['Leek']; S31 [None, None] unassessed -['Pumpkin']), unexplained 0, abstain->4 0, abstain->1 0, other 0.
- Drift over 307 existing terms and synonyms analysed alone: 0 differences.
- Controls (label order): see `vegetables/applied_gate/applied_gate.json` 'controls' (27 negative, 22 positive). Negatives never Group 1 via the vegetable clause: salted/brined/sweetened forms -> Group 3; pickled/canned/tinned/preserved bracket forms -> abstain; products (puree, sauce, chips, fries, mashed, sauerkraut, kimchi, juice, ketchup) unassessed.

## 7. Findings and open decisions for the owner (measured)

1. **Descriptor `powder` broadens recognition to every vegetable row (pre-existing mechanism, larger surface).** `descriptors.csv` drops `powder`, so `<vegetable> powder` is read as the vegetable and answers Group 1 as the sole item. Measured: of the 115 proposed terms, 113 of '<term> powder' forms answer Group 1 on this branch vs 0 on main. (Pre-existing for carrot/onion/tomato powder.) Proposal for a separate classification-bearing step: route a descriptor-`powder` on a whole-food/legume/vegetable row through the existing food_powder behaviour (Group 1 only as sole item; multi-item lists abstain). Not implemented here.
2. **Name collisions QUEUED (evidence, not guesses):** `beets` (out-of-sample S30 'Beet Red Powder': 'red' and 'powder' are descriptors, so the E162 colour would read as the vegetable), `celery` (S12 'Celery Powder', a curing source), `arrowroot` ('arrowroot powder' is a starch, FAO Group 2 example). All three need your decision on descriptor handling before the vegetable rows are staged for them.
3. Overlaps routed to other batches: corn (cereal clause), peas/edamame/cowpeas/fava/yardlong/winged/immature seeds (legume rows), garlic/ginger/parsley/coriander/chives/wasabi/lemon grass/epazote (Spices and Herbs), seaweed (algae are named only in the Group 1 definition: needs a kind decision), dried/dehydrated forms (per-term policy), sprouts, flowers, hearts of palm, fiddleheads.
4. Inference levels: stem, flower, bulb and fruit-vegetables (tomato, cauliflower, onion, courgette, aubergine) are instances of the Group 1 definition's plant parts, not named by the example clause V1; recorded per row.
5. Condition-record upgrades from the junior audit-2 map are NOT folded in yet (audit-2 review is queued).
