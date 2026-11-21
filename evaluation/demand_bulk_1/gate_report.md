# Gate report: demand-decisions-1

**Verdict: READY_FOR_REVIEW**

Nothing was merged.

| Check | Result |
|---|---|
| open demand terms decided | 110 |
| by disposition | {'PARK': 96, 'MARKER_PROPOSAL': 5, 'ACCEPT_ROW': 4, 'LABEL_BOUND': 4, 'ACCEPT_SYNONYM': 1} |
| paste-input mentions by disposition (a term can occur in several inputs) | {'PARK': 127, 'MARKER_PROPOSAL': 8, 'ACCEPT_ROW': 5, 'LABEL_BOUND': 8, 'ACCEPT_SYNONYM': 1} |
| candidate lexicon rows | 4 |
| candidate synonyms | 1 |
| flip check (66 frozen inputs, separate fresh processes) | group 0, drivers 0, status 0, reason 1, warnings 0, ingredients 0, unassessed 5, ins_mappings 0 |
| harness proof | lexicon rows 135 -> 139; synonym rows 1; all 5 terms recognised after |

## Candidate rows

- `wheat flour` (flour) for demand term `wheat flour`
- `beans` (whole_food) for demand term `beans`
- `cabbage` (whole_food) for demand term `cabbage`
- `peanut oil` (culinary) for demand term `edible peanut oil`
- synonym `potable water` -> `water`

## Marker proposals (classification-bearing: owner decision, not staged)

- #4 `wheat gluten` (4 inputs): classification_bearing: FAO names 'gluten' among ingredients of ultra-processed foods (strong marker candidate)
- #52 `hydrolysed vegetable protein` (1 inputs): classification_bearing: FAO names 'hydrolysed proteins'; 'hydrolysed vegetable protein' is a hydrolysed protein by name (strong marker candidate)
- #54 `lemon juice concentrate` (1 inputs): classification_bearing: FAO section 3 lists 'fruit juice concentrate' among ingredients of ultra-processed foods; lemon juice concentrate is covered by class only, the exact term is not named; the juice clause is conditioned and a concentrate is not 'fresh or pasteurized'
- #85 `apple juice concentrate` (1 inputs): classification_bearing: FAO section 3 lists 'fruit juice concentrate' among ingredients of ultra-processed foods; apple juice concentrate is covered by class only, the exact term is not named; the juice clause is conditioned and a concentrate is not 'fresh or pasteurized'
- #96 `fructose` (1 inputs): classification_bearing: FAO names 'fructose' among ingredients of ultra-processed foods (strong marker candidate)

## Label-bound (conditioned clause, never staged)

- #22 `apple juice` (2 inputs): conditioned_clause: conditioned clause: fresh or pasteurized juices only 'with no added sugar, sweeteners or flavours'; only a label that declares the plain form can qualify
- #23 `grape juice` (2 inputs): conditioned_clause: conditioned clause: fresh or pasteurized juices only 'with no added sugar, sweeteners or flavours'; only a label that declares the plain form can qualify
- #24 `orange juice` (2 inputs): conditioned_clause: conditioned clause: fresh or pasteurized juices only 'with no added sugar, sweeteners or flavours'; only a label that declares the plain form can qualify
- #25 `pineapple juice` (2 inputs): conditioned_clause: conditioned clause: fresh or pasteurized juices only 'with no added sugar, sweeteners or flavours'; only a label that declares the plain form can qualify

## Parked

- #1 `cocoa solids` (5 inputs): no_source_names: no source read places cocoa products: FAO Table 1 Group 4 names 'chocolate' and 'cocoa drinks' as products, not cocoa butter, mass, solids, nibs or powder as ingredients
- #2 `liquid glucose` (5 inputs): no_source_names: no source read names glucose syrup, liquid glucose or glucose powder: FAO names 'glucose-fructose syrup' (existing marker row) and 'fructose', not glucose
- #3 `spices & condiments` (5 inputs): ambiguous_blend: a blend or class phrase: 'spices and condiments' is broader than the herbs-and-spices clause; mixed or compounded forms are queued by the clause-tier rule
- #5 `minerals` (3 inputs): held_category_C: vitamins, minerals and malted/sprouted items belong to workstream C (sources not yet read)
- #6 `starch` (3 inputs): existing_decision: standing exclusion from the lexicon-1 senior review (tests/test_lexicon_1.py::test_explicit_exclusions_and_blocked_items_did_not_get_rows, evaluation/lexicon_1_flip_check/README.md): held until the owner reopens it; cranberry additionally because a label does not establish plain dried status
- #7 `carbonated water` (3 inputs): owner_decision: needs an owner decision (a new descriptor word, a vague or processed form, or no source read places the fat, protein or product)
- #8 `cocoa butter` (2 inputs): no_source_names: no source read places cocoa products: FAO Table 1 Group 4 names 'chocolate' and 'cocoa drinks' as products, not cocoa butter, mass, solids, nibs or powder as ingredients
- #9 `yeast extract` (2 inputs): existing_decision: standing decision: yeast extract is NOT a marker and stays outside the vocabulary (in no research/ file; adding needs a cited source); research/04: probiotic culture is NOT a starter culture; cow milk is not covered by the two-part dairy basis
- #10 `cocoa powder` (2 inputs): no_source_names: no source read places cocoa products: FAO Table 1 Group 4 names 'chocolate' and 'cocoa drinks' as products, not cocoa butter, mass, solids, nibs or powder as ingredients
- #11 `banana pulp` (2 inputs): form_not_named: the pulp or puree form is not named by the fruit/vegetable clause (fresh, squeezed, chilled, frozen or dried); canned or pureed forms sit in other groups by the label
- #12 `caffeine` (2 inputs): additive_table: an additive or nutrient: handled by the additive/INS tables, not by lexicon rows; no Codex-derived data may be used
- #13 `mango pulp` (2 inputs): form_not_named: the pulp or puree form is not named by the fruit/vegetable clause (fresh, squeezed, chilled, frozen or dried); canned or pureed forms sit in other groups by the label
- #14 `papaya pulp` (2 inputs): form_not_named: the pulp or puree form is not named by the fruit/vegetable clause (fresh, squeezed, chilled, frozen or dried); canned or pureed forms sit in other groups by the label
- #15 `pear pulp` (2 inputs): form_not_named: the pulp or puree form is not named by the fruit/vegetable clause (fresh, squeezed, chilled, frozen or dried); canned or pureed forms sit in other groups by the label
- #16 `tomato puree` (2 inputs): form_not_named: the pulp or puree form is not named by the fruit/vegetable clause (fresh, squeezed, chilled, frozen or dried); canned or pureed forms sit in other groups by the label
- #17 `vitamins` (2 inputs): held_category_C: vitamins, minerals and malted/sprouted items belong to workstream C (sources not yet read)
- #18 `vitamins & mineral` (2 inputs): held_category_C: vitamins, minerals and malted/sprouted items belong to workstream C (sources not yet read)
- #20 `whey powder` (2 inputs): no_source_names: FAO names 'whey protein' (and protein isolates), not whey powder or whey solids as a product form; no source read equates them
- #21 `tapioca starch` (2 inputs): existing_decision: standing exclusion from the lexicon-1 senior review (tests/test_lexicon_1.py::test_explicit_exclusions_and_blocked_items_did_not_get_rows, evaluation/lexicon_1_flip_check/README.md): held until the owner reopens it; cranberry additionally because a label does not establish plain dried status
- #26 `maida` (1 inputs): no_source_names: an Indian trade or regional name, or a form, with no source read that equates it (FSSAI or another Indian source would be needed)
- #27 `guar gum` (1 inputs): additive_table: an additive or nutrient: handled by the additive/INS tables, not by lexicon rows; no Codex-derived data may be used
- #28 `soya flour` (1 inputs): form_not_named: flour or meal of a grain or pulse not named by 'flour made from corn, wheat, oats, or cassava'
- #29 `cereal product` (1 inputs): owner_decision: needs an owner decision (a new descriptor word, a vague or processed form, or no source read places the fat, protein or product)
- #30 `coriander cinnamon` (1 inputs): extraction_not_vocabulary: two or more ingredients joined without a comma, or an item cut by the parser: an extraction problem, not a vocabulary gap
- #31 `corn flakes` (1 inputs): source_conflict: 'flakes ... made from corn' (Group 1) versus breakfast 'cereals' (Group 4): the term alone does not decide; owner decision
- #32 `dried mango black salt` (1 inputs): extraction_not_vocabulary: two or more ingredients joined without a comma, or an item cut by the parser: an extraction problem, not a vocabulary gap
- #33 `rice flakes` (1 inputs): form_not_named: flakes are named only 'made from corn, wheat, oats, or cassava'; this grain is not named, and breakfast 'cereals' are Group 4 products
- #34 `roasted gram` (1 inputs): no_source_names: an Indian trade or regional name, or a form, with no source read that equates it (FSSAI or another Indian source would be needed)
- #35 `tomato paste` (1 inputs): form_not_named: the pulp or puree form is not named by the fruit/vegetable clause (fresh, squeezed, chilled, frozen or dried); canned or pureed forms sit in other groups by the label
- #36 `active lactic culture and probiotic culture` (1 inputs): existing_decision: standing decision: yeast extract is NOT a marker and stays outside the vocabulary (in no research/ file; adding needs a cited source); research/04: probiotic culture is NOT a starter culture; cow milk is not covered by the two-part dairy basis
- #37 `anlioxidant` (1 inputs): additive_table: an additive or nutrient: handled by the additive/INS tables, not by lexicon rows; no Codex-derived data may be used
- #39 `brown rice flakes` (1 inputs): form_not_named: flakes are named only 'made from corn, wheat, oats, or cassava'; this grain is not named, and breakfast 'cereals' are Group 4 products
- #41 `caster sugar` (1 inputs): no_source_names: an Indian trade or regional name, or a form, with no source read that equates it (FSSAI or another Indian source would be needed)
- #42 `cereal extract` (1 inputs): owner_decision: needs an owner decision (a new descriptor word, a vague or processed form, or no source read places the fat, protein or product)
- #43 `citric acid` (1 inputs): additive_table: an additive or nutrient: handled by the additive/INS tables, not by lexicon rows; no Codex-derived data may be used
- #44 `cocoa nibs` (1 inputs): no_source_names: no source read places cocoa products: FAO Table 1 Group 4 names 'chocolate' and 'cocoa drinks' as products, not cocoa butter, mass, solids, nibs or powder as ingredients
- #45 `compounded asafoetida` (1 inputs): ambiguous_blend: a blend or class phrase: 'spices and condiments' is broader than the herbs-and-spices clause; mixed or compounded forms are queued by the clause-tier rule
- #46 `cranberry` (1 inputs): existing_decision: standing exclusion from the lexicon-1 senior review (tests/test_lexicon_1.py::test_explicit_exclusions_and_blocked_items_did_not_get_rows, evaluation/lexicon_1_flip_check/README.md): held until the owner reopens it; cranberry additionally because a label does not establish plain dried status
- #47 `defatted soya` (1 inputs): owner_decision: needs an owner decision (a new descriptor word, a vague or processed form, or no source read places the fat, protein or product)
- #48 `dehydrated vegetable` (1 inputs): owner_decision: needs an owner decision (a new descriptor word, a vague or processed form, or no source read places the fat, protein or product)
- #49 `fractionated vegetable fats` (1 inputs): owner_decision: needs an owner decision (a new descriptor word, a vague or processed form, or no source read places the fat, protein or product)
- #50 `glucose powder` (1 inputs): no_source_names: no source read names glucose syrup, liquid glucose or glucose powder: FAO names 'glucose-fructose syrup' (existing marker row) and 'fructose', not glucose
- #51 `himalayan pink salt` (1 inputs): no_source_names: an Indian trade or regional name, or a form, with no source read that equates it (FSSAI or another Indian source would be needed)
- #53 `jowar flakes` (1 inputs): form_not_named: flakes are named only 'made from corn, wheat, oats, or cassava'; this grain is not named, and breakfast 'cereals' are Group 4 products
- #55 `lodised salt brine` (1 inputs): extraction_not_vocabulary: two or more ingredients joined without a comma, or an item cut by the parser: an extraction problem, not a vocabulary gap
- #56 `malt extract` (1 inputs): held_category_C: vitamins, minerals and malted/sprouted items belong to workstream C (sources not yet read)
- #57 `malted barley` (1 inputs): held_category_C: vitamins, minerals and malted/sprouted items belong to workstream C (sources not yet read)
- #58 `maltodectrin` (1 inputs): ocr_or_typo: a misspelling or truncation: a typo alias to a marker is classification-bearing and no spelling policy exists; owner decision
- #59 `mango pieces` (1 inputs): form_not_named: the pulp or puree form is not named by the fruit/vegetable clause (fresh, squeezed, chilled, frozen or dried); canned or pureed forms sit in other groups by the label
- #60 `microbial cultures and microbial rennet` (1 inputs): extraction_not_vocabulary: two or more ingredients joined without a comma, or an item cut by the parser: an extraction problem, not a vocabulary gap
- #61 `milk & milk solids milk` (1 inputs): extraction_not_vocabulary: two or more ingredients joined without a comma, or an item cut by the parser: an extraction problem, not a vocabulary gap
- #62 `mixed spices powder` (1 inputs): ambiguous_blend: a blend or class phrase: 'spices and condiments' is broader than the herbs-and-spices clause; mixed or compounded forms are queued by the clause-tier rule
- #63 `natural vinegar` (1 inputs): owner_decision: needs an owner decision (a new descriptor word, a vague or processed form, or no source read places the fat, protein or product)
- #64 `onions flakes` (1 inputs): owner_decision: needs an owner decision (a new descriptor word, a vague or processed form, or no source read places the fat, protein or product)
- #65 `pasteurized buffalo milk fat min` (1 inputs): extraction_not_vocabulary: two or more ingredients joined without a comma, or an item cut by the parser: an extraction problem, not a vocabulary gap
- #66 `pasteurized cow milk` (1 inputs): existing_decision: standing decision: yeast extract is NOT a marker and stays outside the vocabulary (in no research/ file; adding needs a cited source); research/04: probiotic culture is NOT a starter culture; cow milk is not covered by the two-part dairy basis
- #67 `pipal` (1 inputs): no_source_names: an Indian trade or regional name, or a form, with no source read that equates it (FSSAI or another Indian source would be needed)
- #68 `quinoa flakes` (1 inputs): form_not_named: flakes are named only 'made from corn, wheat, oats, or cassava'; this grain is not named, and breakfast 'cereals' are Group 4 products
- #69 `ragi flakes` (1 inputs): form_not_named: flakes are named only 'made from corn, wheat, oats, or cassava'; this grain is not named, and breakfast 'cereals' are Group 4 products
- #70 `raw mango pulp` (1 inputs): form_not_named: the pulp or puree form is not named by the fruit/vegetable clause (fresh, squeezed, chilled, frozen or dried); canned or pureed forms sit in other groups by the label
- #71 `refined oil` (1 inputs): owner_decision: needs an owner decision (a new descriptor word, a vague or processed form, or no source read places the fat, protein or product)
- #72 `roasted peanuts sugar` (1 inputs): extraction_not_vocabulary: two or more ingredients joined without a comma, or an item cut by the parser: an extraction problem, not a vocabulary gap
- #73 `sorghum flour` (1 inputs): form_not_named: flour or meal of a grain or pulse not named by 'flour made from corn, wheat, oats, or cassava'
- #74 `split pulse urad flour` (1 inputs): form_not_named: flour or meal of a grain or pulse not named by 'flour made from corn, wheat, oats, or cassava'
- #75 `synthetic vinegar` (1 inputs): owner_decision: needs an owner decision (a new descriptor word, a vague or processed form, or no source read places the fat, protein or product)
- #76 `tartaric acid` (1 inputs): additive_table: an additive or nutrient: handled by the additive/INS tables, not by lexicon rows; no Codex-derived data may be used
- #77 `texturized soy protein` (1 inputs): owner_decision: needs an owner decision (a new descriptor word, a vague or processed form, or no source read places the fat, protein or product)
- #78 `tumeric` (1 inputs): ocr_or_typo: a misspelling or truncation: a typo alias to a marker is classification-bearing and no spelling policy exists; owner decision
- #79 `vitamin a and vitamin d` (1 inputs): held_category_C: vitamins, minerals and malted/sprouted items belong to workstream C (sources not yet read)
- #80 `vitamin a palmitate & vitamin d` (1 inputs): held_category_C: vitamins, minerals and malted/sprouted items belong to workstream C (sources not yet read)
- #81 `wheat bran` (1 inputs): form_not_named: flour or meal of a grain or pulse not named by 'flour made from corn, wheat, oats, or cassava'
- #82 `wheat flour milk solids` (1 inputs): extraction_not_vocabulary: two or more ingredients joined without a comma, or an item cut by the parser: an extraction problem, not a vocabulary gap
- #83 `yeast` (1 inputs): owner_decision: needs an owner decision (a new descriptor word, a vague or processed form, or no source read places the fat, protein or product)
- #84 `refined palmolien oil` (1 inputs): ocr_or_typo: a misspelling or truncation: a typo alias to a marker is classification-bearing and no spelling policy exists; owner decision
- #86 `butter oil` (1 inputs): owner_decision: needs an owner decision (a new descriptor word, a vague or processed form, or no source read places the fat, protein or product)
- #87 `cocoa butter ¹` (1 inputs): no_source_names: no source read places cocoa products: FAO Table 1 Group 4 names 'chocolate' and 'cocoa drinks' as products, not cocoa butter, mass, solids, nibs or powder as ingredients
- #88 `cocoa mass ¹` (1 inputs): no_source_names: no source read places cocoa products: FAO Table 1 Group 4 names 'chocolate' and 'cocoa drinks' as products, not cocoa butter, mass, solids, nibs or powder as ingredients
- #89 `coconut fat` (1 inputs): owner_decision: needs an owner decision (a new descriptor word, a vague or processed form, or no source read places the fat, protein or product)
- #90 `com meal` (1 inputs): form_not_named: flour or meal of a grain or pulse not named by 'flour made from corn, wheat, oats, or cassava'
- #91 `dehydrated onion` (1 inputs): owner_decision: needs an owner decision (a new descriptor word, a vague or processed form, or no source read places the fat, protein or product)
- #92 `desi khand` (1 inputs): no_source_names: an Indian trade or regional name, or a form, with no source read that equates it (FSSAI or another Indian source would be needed)
- #93 `dough conditioner` (1 inputs): additive_table: an additive or nutrient: handled by the additive/INS tables, not by lexicon rows; no Codex-derived data may be used
- #95 `exhausted vanilla bean pieces` (1 inputs): owner_decision: needs an owner decision (a new descriptor word, a vague or processed form, or no source read places the fat, protein or product)
- #97 `glucose syrup` (1 inputs): no_source_names: no source read names glucose syrup, liquid glucose or glucose powder: FAO names 'glucose-fructose syrup' (existing marker row) and 'fructose', not glucose
- #98 `gram meal` (1 inputs): form_not_named: flour or meal of a grain or pulse not named by 'flour made from corn, wheat, oats, or cassava'
- #99 `microbial cultu` (1 inputs): ocr_or_typo: a misspelling or truncation: a typo alias to a marker is classification-bearing and no spelling policy exists; owner decision
- #100 `pasteurised cow milk` (1 inputs): existing_decision: standing decision: yeast extract is NOT a marker and stays outside the vocabulary (in no research/ file; adding needs a cited source); research/04: probiotic culture is NOT a starter culture; cow milk is not covered by the two-part dairy basis
- #102 `reconstituted skimmed milk` (1 inputs): extraction_not_vocabulary: two or more ingredients joined without a comma, or an item cut by the parser: an extraction problem, not a vocabulary gap
- #103 `rice meal` (1 inputs): form_not_named: flour or meal of a grain or pulse not named by 'flour made from corn, wheat, oats, or cassava'
- #104 `skimmed milk powder or concentrate` (1 inputs): extraction_not_vocabulary: two or more ingredients joined without a comma, or an item cut by the parser: an extraction problem, not a vocabulary gap
- #105 `whey solids` (1 inputs): no_source_names: FAO names 'whey protein' (and protein isolates), not whey powder or whey solids as a product form; no source read equates them
- #106 `dry fruits` (1 inputs): no_source_names: an Indian trade or regional name, or a form, with no source read that equates it (FSSAI or another Indian source would be needed)
- #107 `flavoured` (1 inputs): owner_decision: needs an owner decision (a new descriptor word, a vague or processed form, or no source read places the fat, protein or product)
- #108 `made from toned milk` (1 inputs): extraction_not_vocabulary: two or more ingredients joined without a comma, or an item cut by the parser: an extraction problem, not a vocabulary gap
- #109 `milk solids and sugar` (1 inputs): extraction_not_vocabulary: two or more ingredients joined without a comma, or an item cut by the parser: an extraction problem, not a vocabulary gap
- #110 `pasteurized toned milk & active lactic culture` (1 inputs): extraction_not_vocabulary: two or more ingredients joined without a comma, or an item cut by the parser: an extraction problem, not a vocabulary gap
