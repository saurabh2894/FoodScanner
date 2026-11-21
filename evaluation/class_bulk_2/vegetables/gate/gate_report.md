# Gate report: class-vegetables-1

**Verdict: READY_FOR_REVIEW**

Nothing was merged. `lexicon_candidate_rows.csv` holds the ready rows in lexicon.csv layout and `synonyms_candidate_rows.csv` the synonym candidates in synonyms.csv layout, for review.

| Check | Result |
|---|---|
| staged rows | 122 |
| schema errors | 0 |
| provenance errors | 0 |
| duplicates (exact, synonym, already recognised) | 8 |
| variants of an existing term (informational) | 10 |
| parked in the ambiguity queue | 114 (Counter({'clause_tier': 111, 'gate': 3})) |
| ready rows (new lexicon rows) | 114 |
| synonym candidates (variant policy variant-policy-class-vegetables-1) | 0 |
| policy errors | 0 |
| verbatim clause vs FAO text | PASS |
| harness proof (separate processes) | lexicon rows 181 -> 295; all 114 staged terms recognised after; 0 already recognised before |
| flip check (66 frozen inputs, before and after in separate fresh processes) | group 0, drivers 0, status 0, reason 0, warnings 0, ingredients 0, unassessed 0, ins_mappings 0 |
| group/status/driver flips | 0  |
| unexplained changes | 0 |

## Ready rows (new lexicon rows)

- `acorn squash`
- `amaranth leaves`
- `arrowhead`
- `artichokes`
- `arugula`
- `asparagus`
- `balsam-pear`
- `bamboo shoots`
- `banana peppers`
- `beet greens`
- `bell peppers`
- `bok choy cabbage`: separate row because a named cabbage type kept as its own food name next to the untouched generic 'cabbage' row
- `borage`
- `broccoli`
- `broccoli raab`
- `brussels sprouts`
- `burdock root`
- `butterbur`
- `butterhead lettuce`
- `butternut squash`
- `cardoon`
- `cassava`
- `cauliflower`
- `celeriac`
- `celtuce`
- `chanterelle mushrooms`
- `chayote`
- `chicory greens`
- `chicory roots`
- `chinese broccoli`
- `chinese cabbage`: separate row because a named cabbage type (pe-tsai) next to the generic 'cabbage' row
- `chinese waterchestnuts`
- `chrysanthemum leaves`
- `collards`
- `cornsalad`
- `crimini mushrooms`
- `dandelion greens`
- `dishcloth gourd`
- `dock`
- `drumstick leaves`
- `drumstick pods`
- `eggplant`
- `endive`
- `enoki mushrooms`
- `eppaw`
- `garden cress`
- `garland chrysanthemum`
- `grape leaves`
- `hawaii mountain yam`
- `hot chili peppers`
- `hubbard squash`
- `iceberg lettuce`
- `jalapeno peppers`
- `jerusalem-artichokes`
- `jew's ear`
- `jute`
- `kale`
- `kohlrabi`
- `lambsquarters`
- `leaf lettuce`
- `leeks`
- `lotus root`
- `maitake mushrooms`
- `morel mushrooms`
- `mustard greens`: separate row because the leaf vegetable; 'mustard' is the seed spice, a different plant part, left untouched
- `mustard spinach`: separate row because a leaf vegetable (tendergreen); 'mustard' is the seed spice, left untouched
- `napa cabbage`: separate row because a named cabbage type next to the generic 'cabbage' row (whether napa and chinese cabbage are one food is not stated by FDC; both kept)
- `new zealand spinach`
- `nopales`
- `okra`
- `oriental radishes`
- `oyster mushrooms`
- `parsnips`
- `poblano peppers`
- `pokeberry shoots`
- `portabella mushrooms`
- `pumpkin`: separate row because the fruit-vegetable; 'pumpkin seeds' is a different plant part (nut_seed row), left untouched
- `pumpkin leaves`
- `purslane`
- `radicchio`
- `radishes`
- `romaine lettuce`
- `rutabagas`
- `salsify`
- `savoy cabbage`: separate row because a named cabbage type next to the generic 'cabbage' row
- `serrano peppers`
- `shallots`
- `shiitake mushrooms`
- `snap beans`: separate row because a named bean pod vegetable next to the untouched generic 'beans' legume row
- `spaghetti squash`
- `spinach`
- `summer squash`
- `sweet peppers`
- `sweet potato leaves`
- `sweet potatoes`
- `swiss chard`
- `taro`
- `taro leaves`
- `taro shoots`
- `tomatillos`
- `turnip greens`
- `turnips`
- `vinespinach`
- `water convolvulus`: separate row because a leaf vegetable; the shared word 'water' with the existing 'water' row is incidental (false variant match)
- `watercress`
- `waxgourd`
- `white mushrooms`
- `white-flowered gourd`
- `winter squash`
- `witloof chicory`
- `yam`
- `yambean`
- `yautia`
- `zucchini`

## Synonym candidates (variant policy: same ingredient, plant part and form)


## Duplicates (excluded: already covered)

- `cabbage`: exact lexicon term (kind whole_food)
- `carrots`: already recognised by this build (descriptors, plurals or synonyms)
- `cucumber`: exact lexicon term (kind whole_food)
- `fennel`: exact lexicon term (kind herb_spice)
- `green onions`: already recognised by this build (descriptors, plurals or synonyms)
- `onions`: already recognised by this build (descriptors, plurals or synonyms)
- `potatoes`: already recognised by this build (descriptors, plurals or synonyms)
- `tomatoes`: already recognised by this build (descriptors, plurals or synonyms)

## Variants of existing terms (kept; informational)

- `bok choy cabbage` ~ ['cabbage']
- `chinese cabbage` ~ ['cabbage']
- `mustard greens` ~ ['mustard']
- `mustard spinach` ~ ['mustard']
- `napa cabbage` ~ ['cabbage']
- `pumpkin` ~ ['pumpkin seeds']
- `savoy cabbage` ~ ['cabbage']
- `snap beans` ~ ['beans']
- `water convolvulus` ~ ['water']

## Ambiguity queue (parked, never included)

- `Garlic, raw` (clause_tier, queue_garlic): an herb or spice per FDC in other records; kept out of this batch until the owner decides garlic's class (existing label vocabulary).
- `Mushroom, lion's mane` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Mushroom, oyster` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Mushrooms, shiitake` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Mushrooms, white button` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Spinach, baby` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Spinach, mature` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Tomato, roma` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Mushroom, lion's mane` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Mushrooms, shiitake` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Mushrooms, white button` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Spinach, baby` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Mushroom, portabella` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Mushroom, king oyster` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Mushroom, enoki` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Mushroom, crimini` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Mushroom, maitake` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Mushroom, beech` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Mushroom, pioppini` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `celery` (clause_tier, dedupe_stays_out): NAME COLLISION (observed in out-of-sample label S12 'Celery Powder'): 'powder' is a descriptor, so a celery powder (used as a curing/nitrite source) would be read as the plain vegetable celery and leave the unassessed list; QUEUED for an owner decision on the powder descriptor.
- `beets` (clause_tier, dedupe_stays_out): NAME COLLISION (observed in out-of-sample label S30 'Beet Red Powder'): 'red' and 'powder' are descriptors, so 'beet red powder' (the beetroot red colour, E162) would be read as the vegetable beets and leave the unassessed list; QUEUED for an owner decision on descriptor handling. 'beet greens' is unaffected.
- `Corn, sweet, yellow and white kernels,  fresh, raw` (clause_tier, queue_corn): sweet corn overlaps the cereal-grain clause ('corn cob or kernel'): the Cereal batch owns it.
- `Seaweed, Canadian Cultivated EMI-TSUNOMATA, dry` (clause_tier, queue_seaweed): algae are named only in the Group 1 DEFINITION ('fungi, algae'), not in an example; kind and placement need an owner decision.
- `Seaweed, Canadian Cultivated EMI-TSUNOMATA, rehydrated` (clause_tier, queue_seaweed): algae are named only in the Group 1 DEFINITION ('fungi, algae'), not in an example; kind and placement need an owner decision.
- `Hearts of palm, raw` (clause_tier, queue_hearts_of_palm): stem of a palm: the plant-part basis is not named by the clause; QUEUE.
- `Yeast extract spread` (clause_tier, queue_yeast): not a vegetable.
- `Alfalfa seeds, sprouted, raw` (clause_tier, queue_sprouted): germinated seeds (sprouts) are not named by the clause; the plant-part basis is not established.
- `leafy tips balsam-pear` (clause_tier, dedupe_stays_out): plant-part variant of a food (leaves, stalks, tips): not established as a label term; stays out rather than inflating the lexicon
- `Lima beans, immature seeds, raw` (clause_tier, queue_immature): immature legume seeds overlap the legume rows (Batch 1).
- `Corn, sweet, yellow, frozen, kernels cut off cob, unprepared (Includes foods for USDA's Food Distribution Program)` (clause_tier, queue_corn): sweet corn overlaps the cereal-grain clause ('corn cob or kernel'): the Cereal batch owns it.
- `Corn, sweet, yellow, frozen, kernels on cob, unprepared` (clause_tier, queue_corn): sweet corn overlaps the cereal-grain clause ('corn cob or kernel'): the Cereal batch owns it.
- `Cowpeas (blackeyes), immature seeds, frozen, unprepared` (clause_tier, queue_immature): immature legume seeds overlap the legume rows (Batch 1).
- `Cowpeas, young pods with seeds, raw` (clause_tier, queue_cowpeas): legume overlap (Batch 1).
- `Edamame, frozen, unprepared` (clause_tier, queue_edamame): legume overlap (Batch 1).
- `Pepeao, dried` (clause_tier, queue_dried): dried forms: the clause names 'dried' but earlier owner policy (dehydrated-policy-1) keeps dried/dehydrated forms per-term only; QUEUE for per-term decisions.
- `Lentils, sprouted, raw` (clause_tier, queue_sprouted): germinated seeds (sprouts) are not named by the clause; the plant-part basis is not established.
- `Mushrooms, shiitake, dried` (clause_tier, queue_dried): dried forms: the clause names 'dried' but earlier owner policy (dehydrated-policy-1) keeps dried/dehydrated forms per-term only; QUEUE for per-term decisions.
- `Radishes, oriental, dried` (clause_tier, queue_dried): dried forms: the clause names 'dried' but earlier owner policy (dehydrated-policy-1) keeps dried/dehydrated forms per-term only; QUEUE for per-term decisions.
- `Seaweed, irishmoss, raw` (clause_tier, queue_seaweed): algae are named only in the Group 1 DEFINITION ('fungi, algae'), not in an example; kind and placement need an owner decision.
- `Seaweed, kelp, raw` (clause_tier, queue_seaweed): algae are named only in the Group 1 DEFINITION ('fungi, algae'), not in an example; kind and placement need an owner decision.
- `Seaweed, laver, raw` (clause_tier, queue_seaweed): algae are named only in the Group 1 DEFINITION ('fungi, algae'), not in an example; kind and placement need an owner decision.
- `Sesbania flower, raw` (clause_tier, queue_flower): an edible flower is not established as a vegetable by the clause; QUEUE.
- `arrowroot` (clause_tier, dedupe_stays_out): NAME COLLISION (measured): 'powder' is a descriptor, so 'arrowroot powder' (a starch extracted from the root, a FAO Group 2 'starch' example) would be read as the plain root and answer Group 1; QUEUED for an owner decision on descriptor handling.
- `Corn, sweet, white, raw` (clause_tier, queue_corn): sweet corn overlaps the cereal-grain clause ('corn cob or kernel'): the Cereal batch owns it.
- `Corn, sweet, white, frozen, kernels cut off cob, unprepared` (clause_tier, queue_corn): sweet corn overlaps the cereal-grain clause ('corn cob or kernel'): the Cereal batch owns it.
- `Tomatoes, sun-dried` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Peppers, hot chile, sun-dried` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Lemon grass (citronella), raw` (clause_tier, queue_lemon_grass): an herb or spice (Spices and Herbs clause), not a vegetable; routed to that category's rule.
- `Beans, fava, in pod, raw` (clause_tier, queue_fava): legume overlap (Batch 1).
- `Peppers, pasilla, dried` (clause_tier, queue_dried): dried forms: the clause names 'dried' but earlier owner policy (dehydrated-policy-1) keeps dried/dehydrated forms per-term only; QUEUE for per-term decisions.
- `Fungi, Cloud ears, dried` (clause_tier, queue_dried): dried forms: the clause names 'dried' but earlier owner policy (dehydrated-policy-1) keeps dried/dehydrated forms per-term only; QUEUE for per-term decisions.
- `Wasabi, root, raw` (clause_tier, queue_wasabi): a condiment root (Spices and Herbs clause).
- `Fiddlehead ferns, frozen, unprepared` (clause_tier, queue_fiddlehead): fern shoots: not named by the clause; QUEUE.
- `Beans, navy, mature seeds, sprouted, raw` (clause_tier, queue_sprouted): germinated seeds (sprouts) are not named by the clause; the plant-part basis is not established.
- `beets` (clause_tier, dedupe_stays_out): NAME COLLISION (observed in out-of-sample label S30 'Beet Red Powder'): 'red' and 'powder' are descriptors, so 'beet red powder' (the beetroot red colour, E162) would be read as the vegetable beets and leave the unassessed list; QUEUED for an owner decision on descriptor handling. 'beet greens' is unaffected.
- `Beans, kidney, mature seeds, sprouted, raw` (clause_tier, queue_sprouted): germinated seeds (sprouts) are not named by the clause; the plant-part basis is not established.
- `Cowpeas (blackeyes), immature seeds, raw` (clause_tier, queue_immature): immature legume seeds overlap the legume rows (Batch 1).
- `Yardlong bean, raw` (clause_tier, queue_yardlong): legume overlap (Batch 1).
- `Cowpeas, leafy tips, raw` (clause_tier, queue_cowpeas): legume overlap (Batch 1).
- `Garlic, raw` (clause_tier, queue_garlic): an herb or spice per FDC in other records; kept out of this batch until the owner decides garlic's class (existing label vocabulary).
- `Ginger root, raw` (clause_tier, queue_ginger): an herb or spice (Spices and Herbs clause), not a vegetable.
- `Hyacinth-beans, immature seeds, raw` (clause_tier, queue_immature): immature legume seeds overlap the legume rows (Batch 1).
- `Kanpyo, (dried gourd strips)` (clause_tier, queue_dried): dried forms: the clause names 'dried' but earlier owner policy (dehydrated-policy-1) keeps dried/dehydrated forms per-term only; QUEUE for per-term decisions.
- `Pumpkin flowers, raw` (clause_tier, queue_flowers): an edible flower is not established as a vegetable by the clause; QUEUE.
- `Seaweed, agar, raw` (clause_tier, queue_seaweed): algae are named only in the Group 1 DEFINITION ('fungi, algae'), not in an example; kind and placement need an owner decision.
- `Soybeans, green, raw` (clause_tier, queue_soybeans): legume overlap (Batch 1).
- `Soybeans, mature seeds, sprouted, raw` (clause_tier, queue_sprouted): germinated seeds (sprouts) are not named by the clause; the plant-part basis is not established.
- `leaves broccoli` (clause_tier, dedupe_stays_out): plant-part variant of a food (leaves, stalks, tips): not established as a label term; stays out rather than inflating the lexicon
- `Broccoli, flower clusters, raw` (clause_tier, queue_flower): an edible flower is not established as a vegetable by the clause; QUEUE.
- `stalks broccoli` (clause_tier, dedupe_stays_out): plant-part variant of a food (leaves, stalks, tips): not established as a label term; stays out rather than inflating the lexicon
- `Corn, sweet, white, frozen, kernels on cob, unprepared` (clause_tier, queue_corn): sweet corn overlaps the cereal-grain clause ('corn cob or kernel'): the Cereal batch owns it.
- `Peppers, sweet, red, freeze-dried` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Peppers, ancho, dried` (clause_tier, queue_dried): dried forms: the clause names 'dried' but earlier owner policy (dehydrated-policy-1) keeps dried/dehydrated forms per-term only; QUEUE for per-term decisions.
- `Epazote, raw` (clause_tier, queue_epazote): an herb (Spices and Herbs clause).
- `leaves fireweed` (clause_tier, dedupe_stays_out): plant-part variant of a food (leaves, stalks, tips): not established as a label term; stays out rather than inflating the lexicon
- `Fiddlehead ferns, raw` (clause_tier, queue_fiddlehead): fern shoots: not named by the clause; QUEUE.
- `Lima beans, immature seeds, frozen, fordhook, unprepared` (clause_tier, queue_immature): immature legume seeds overlap the legume rows (Batch 1).
- `Lima beans, immature seeds, frozen, baby, unprepared` (clause_tier, queue_immature): immature legume seeds overlap the legume rows (Batch 1).
- `Mung beans, mature seeds, sprouted, raw` (clause_tier, queue_sprouted): germinated seeds (sprouts) are not named by the clause; the plant-part basis is not established.
- `Beans, pinto, immature seeds, frozen, unprepared` (clause_tier, queue_immature): immature legume seeds overlap the legume rows (Batch 1).
- `celery` (clause_tier, dedupe_stays_out): NAME COLLISION (observed in out-of-sample label S12 'Celery Powder'): 'powder' is a descriptor, so a celery powder (used as a curing/nitrite source) would be read as the plain vegetable celery and leave the unassessed list; QUEUED for an owner decision on the powder descriptor.
- `Chives, raw` (clause_tier, queue_chives): an herb (Spices and Herbs clause).
- `Coriander (cilantro) leaves, raw` (clause_tier, queue_coriander): an herb (Spices and Herbs clause).
- `Corn, sweet, yellow, raw` (clause_tier, queue_corn): sweet corn overlaps the cereal-grain clause ('corn cob or kernel'): the Cereal batch owns it.
- `Onions, young green, tops only` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Peas, edible-podded, raw` (clause_tier, queue_peas): peas and pea pods overlap the legume rows (Batch 1); the existing 'peas' row is already a legume.
- `Peas, edible-podded, frozen, unprepared` (clause_tier, queue_peas): peas and pea pods overlap the legume rows (Batch 1); the existing 'peas' row is already a legume.
- `Peas, green, frozen, unprepared (Includes foods for USDA's Food Distribution Program)` (clause_tier, queue_peas): peas and pea pods overlap the legume rows (Batch 1); the existing 'peas' row is already a legume.
- `Peas and onions, frozen, unprepared` (clause_tier, queue_peas): peas and pea pods overlap the legume rows (Batch 1); the existing 'peas' row is already a legume.
- `Pigeonpeas, immature seeds, raw` (clause_tier, queue_immature): immature legume seeds overlap the legume rows (Batch 1).
- `Turnips, frozen, unprepared` (clause_tier, attribute_contradicts_plain): FDC portion attribute(s) mention ['mashed']: the record may describe a prepared form
- `Winged bean tuber, raw` (clause_tier, queue_winged): legume overlap (Batch 1).
- `Chives, freeze-dried` (clause_tier, queue_chives): an herb (Spices and Herbs clause).
- `Shallots, freeze-dried` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Beans, pinto, mature seeds, sprouted, raw` (clause_tier, queue_sprouted): germinated seeds (sprouts) are not named by the clause; the plant-part basis is not established.
- `Seaweed, agar, dried` (clause_tier, queue_seaweed): algae are named only in the Group 1 DEFINITION ('fungi, algae'), not in an example; kind and placement need an owner decision.
- `Seaweed, spirulina, raw` (clause_tier, queue_seaweed): algae are named only in the Group 1 DEFINITION ('fungi, algae'), not in an example; kind and placement need an owner decision.
- `Radish seeds, sprouted, raw` (clause_tier, queue_sprouted): germinated seeds (sprouts) are not named by the clause; the plant-part basis is not established.
- `Broadbeans, immature seeds, raw` (clause_tier, queue_immature): immature legume seeds overlap the legume rows (Batch 1).
- `Parsley, fresh` (clause_tier, queue_parsley): an herb (Spices and Herbs clause).
- `Peas, green, raw` (clause_tier, queue_peas): peas and pea pods overlap the legume rows (Batch 1); the existing 'peas' row is already a legume.
- `Peas, mature seeds, sprouted, raw` (clause_tier, queue_sprouted): germinated seeds (sprouts) are not named by the clause; the plant-part basis is not established.
- `Peas and carrots, frozen, unprepared` (clause_tier, queue_peas): peas and pea pods overlap the legume rows (Batch 1); the existing 'peas' row is already a legume.
- `Turnip greens and turnips, frozen, unprepared` (clause_tier, queue_turnip_greens_and_turnips): a mixture of two foods in one record (a head naming two foods with 'and'): not a single ingredient.
- `Winged beans, immature seeds, raw` (clause_tier, queue_immature): immature legume seeds overlap the legume rows (Batch 1).
- `Winged bean leaves, raw` (clause_tier, queue_winged): legume overlap (Batch 1).
- `Leeks, (bulb and lower-leaf portion), freeze-dried` (clause_tier, plain_form_not_stated): the name does not state a raw or dry seed form; the plain form is not established by the name or by the attributes
- `Parsley, freeze-dried` (clause_tier, queue_parsley): an herb (Spices and Herbs clause).
- `Seaweed, spirulina, dried` (clause_tier, queue_seaweed): algae are named only in the Group 1 DEFINITION ('fungi, algae'), not in an example; kind and placement need an owner decision.
- `Seaweed, wakame, raw` (clause_tier, queue_seaweed): algae are named only in the Group 1 DEFINITION ('fungi, algae'), not in an example; kind and placement need an owner decision.
- `Carrot, dehydrated` (clause_tier, queue_dehydrated): dehydrated forms: per-term only (dehydrated-policy-1).
- `cabbage` (gate, kind_conflict): existing lexicon row has kind whole_food, staged row says vegetable
- `cucumber` (gate, kind_conflict): existing lexicon row has kind whole_food, staged row says vegetable
- `fennel` (gate, kind_conflict): existing lexicon row has kind herb_spice, staged row says vegetable

## Unassessed drops attributed to ready rows

