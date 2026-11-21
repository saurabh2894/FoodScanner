# Gate report: pmc-decisions-4

**Verdict: READY_FOR_REVIEW**

Nothing was merged.

| Check | Result |
|---|---|
| open demand terms decided | 24 |
| by disposition | {'ACCEPT_ROW': 9, 'PARK': 8, 'ACCEPT_SYNONYM': 3, 'HELD': 3, 'CONFLICT': 1} |
| paste-input mentions by disposition (a term can occur in several inputs) | {'ACCEPT_ROW': 9, 'PARK': 8, 'ACCEPT_SYNONYM': 3, 'HELD': 3, 'CONFLICT': 1} |
| candidate lexicon rows | 9 |
| candidate synonyms | 3 |
| flip check (66 frozen inputs, separate fresh processes) | group 0, drivers 0, status 0, reason 2, warnings 0, ingredients 0, unassessed 13, ins_mappings 0 |
| harness proof | lexicon rows 151 -> 160; synonym rows 3; all 12 terms recognised after |

## Candidate rows

- `yeast` (whole_food) for demand term `yeast`
- `sorghum flour` (flour) for demand term `sorghum flour`
- `soya flour` (flour) for demand term `soya flour`
- `split pulse urad flour` (flour) for demand term `split pulse urad flour`
- `cocoa butter` (culinary) for demand term `cocoa butter`
- `roasted gram` (whole_food) for demand term `roasted gram`
- `refined oil` (culinary) for demand term `refined oil`
- `butter oil` (culinary) for demand term `butter oil`
- `dehydrated vegetable` (whole_food) for demand term `dehydrated vegetable`
- synonym `caster sugar` -> `sugar`
- synonym `natural vinegar` -> `vinegar`
- synonym `mango pieces` -> `mango`

## Marker proposals (classification-bearing: owner decision, not staged)


## CONFLICT between authoritative sources (flagged, not parked, not staged)

- #18 `defatted soya` (1 inputs): authoritative_sources_conflict: PMC10127522 (Martinez Steele et al., J Nutr 2022;153(1):225-241) (footnote 2) places generic 'flours' with the unprocessed or minimally processed foods, while Monteiro et al., Lancet 2025 'Ultra-processed foods and human health: the main thesis and the evidence' (fsp.usp.br PDF) describes ultra-processed foods as made from soy and other crops fractioned into starches, fibre, sugars, oils and fats, and proteins, and NUPENS 'Food classification Nova' page (nupens.fsp.usp.br/en/food-classification-nova/) lists protein isolates or concentrates among group 4 substances: a defatted soy fraction is placed differently depending on which statement applies. FLAGGED, not parked and not staged.

## HELD by the owner (not parked, not staged; exact gap stated)

- #15 `liquid glucose` (1 inputs): owner_held_gap: OWNER AMENDMENT (2026-11-21): HELD (not parked, not staged). Gap: no ingredient-level naming in an admissible source; product-level coding alone insufficient. FAO p.9 names specific sugar varieties (fructose, HFCS, 'fruit juice concentrates', invert sugar, maltodextrin, dextrose, lactose), a named list, not 'all sugars'; Monteiro 2019 (PMC10260459) repeats it; PMC10127522 fn12 'all syrups (excluding 100% maple syrup)' is product-level NHANES coding, corroboration only when a source applies it to ingredients. Bring back only as a fresh proposal if an admissible primary clause names the ingredient form itself.
- #16 `glucose syrup` (1 inputs): owner_held_gap: OWNER AMENDMENT (2026-11-21): HELD (not parked, not staged). Gap: no ingredient-level naming in an admissible source; product-level coding alone insufficient. FAO p.9 names specific sugar varieties (fructose, HFCS, 'fruit juice concentrates', invert sugar, maltodextrin, dextrose, lactose), a named list, not 'all sugars'; Monteiro 2019 (PMC10260459) repeats it; PMC10127522 fn12 'all syrups (excluding 100% maple syrup)' is product-level NHANES coding, corroboration only when a source applies it to ingredients. Bring back only as a fresh proposal if an admissible primary clause names the ingredient form itself.
- #17 `texturized soy protein` (1 inputs): owner_held_gap: OWNER AMENDMENT (2026-11-21): HELD (not parked, not staged). Gap: class membership not established for the texturized form. NUPENS and Lancet 2025 name 'protein isolates or concentrates', but texturizing does not establish an isolate or concentrate (common TVP is texturized soy flour, ~50% protein); no reachable admissible source names texturized/textured protein. Bring back only as a fresh proposal if an admissible primary clause names the ingredient form itself.

## Label-bound (conditioned clause, never staged)


## Parked

- #5 `cocoa powder` (1 inputs): owner_park_pending_mechanism: OWNER DECISION (2026-11-21): PARK until an item-level 'unsweetened' condition mechanism exists for this kind (like nut_seed). PMC10127522 fn5 places 'unsweetened baking chocolate, cocoa powder and gelatin powder' (exact-named, condition 'unsweetened'). Do not stage the row without the mechanism.
- #7 `dry fruits` (1 inputs): owner_park_pending_mechanism: OWNER DECISION (2026-11-21): PARK. The clause covers 'dried fruits (without added sugars)', a dried-FRUIT class with a sugar condition; kind nut_seed is a stretch and there is no dried-fruit condition mechanism. Revisit together with the cocoa powder mechanism.
- #19 `cocoa solids` (1 inputs): no_authoritative_source_covers_it: none of FAO 2019, Monteiro 2018/2019, Lancet 2025, NUPENS pages or PMC10127522 (Martinez Steele et al., J Nutr 2022;153(1):225-241) names or places cocoa solids; PMC10127522 (Martinez Steele et al., J Nutr 2022;153(1):225-241) places 'unsweetened baking chocolate' and 'cocoa powder' (cocoa mass or solids as the same thing is an unstated equivalence); FDC names cocoa products (naming only)
- #20 `cocoa nibs` (1 inputs): no_authoritative_source_covers_it: none of FAO 2019, Monteiro 2018/2019, Lancet 2025, NUPENS pages or PMC10127522 (Martinez Steele et al., J Nutr 2022;153(1):225-241) names or places cocoa nibs; PMC10127522 (Martinez Steele et al., J Nutr 2022;153(1):225-241) places 'unsweetened baking chocolate' and 'cocoa powder' (cocoa mass or solids as the same thing is an unstated equivalence); FDC names cocoa products (naming only)
- #21 `cocoa mass` (1 inputs): no_authoritative_source_covers_it: none of FAO 2019, Monteiro 2018/2019, Lancet 2025, NUPENS pages or PMC10127522 (Martinez Steele et al., J Nutr 2022;153(1):225-241) names or places cocoa mass; PMC10127522 (Martinez Steele et al., J Nutr 2022;153(1):225-241) places 'unsweetened baking chocolate' and 'cocoa powder' (cocoa mass or solids as the same thing is an unstated equivalence); FDC names cocoa products (naming only)
- #22 `carbonated water` (1 inputs): no_authoritative_source_covers_it: the sources place carbonated SOFT DRINKS (products) and 'carbonating agents' (an additive class), not plain carbonated water as an ingredient; FDC names bottled non-carbonated waters (naming only)
- #23 `cereal extract` (1 inputs): no_authoritative_source_covers_it: no authoritative source places a cereal or malt extract; PMC10127522 mentions malt flavour and malt syrup only inside ultra-processed corn-flake ingredient lists; FDC names 'Syrups, malt' (naming only)
- #24 `malt extract` (1 inputs): no_authoritative_source_covers_it: no authoritative source places a cereal or malt extract; PMC10127522 mentions malt flavour and malt syrup only inside ultra-processed corn-flake ingredient lists; FDC names 'Syrups, malt' (naming only)
