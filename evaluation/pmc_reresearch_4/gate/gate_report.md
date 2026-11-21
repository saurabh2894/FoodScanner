# Gate report: pmc-decisions-4

**Verdict: READY_FOR_REVIEW**

Nothing was merged.

| Check | Result |
|---|---|
| open demand terms decided | 24 |
| by disposition | {'ACCEPT_ROW': 11, 'ACCEPT_SYNONYM': 3, 'MARKER_PROPOSAL': 3, 'CONFLICT': 1, 'PARK': 6} |
| paste-input mentions by disposition (a term can occur in several inputs) | {'ACCEPT_ROW': 11, 'ACCEPT_SYNONYM': 3, 'MARKER_PROPOSAL': 3, 'CONFLICT': 1, 'PARK': 6} |
| candidate lexicon rows | 11 |
| candidate synonyms | 3 |
| flip check (66 frozen inputs, separate fresh processes) | group 0, drivers 0, status 0, reason 2, warnings 0, ingredients 0, unassessed 15, ins_mappings 0 |
| harness proof | lexicon rows 151 -> 162; synonym rows 3; all 14 terms recognised after |

## Candidate rows

- `yeast` (whole_food) for demand term `yeast`
- `sorghum flour` (flour) for demand term `sorghum flour`
- `soya flour` (flour) for demand term `soya flour`
- `split pulse urad flour` (flour) for demand term `split pulse urad flour`
- `cocoa powder` (culinary) for demand term `cocoa powder`
- `cocoa butter` (culinary) for demand term `cocoa butter`
- `dry fruits` (nut_seed) for demand term `dry fruits`
- `roasted gram` (whole_food) for demand term `roasted gram`
- `refined oil` (culinary) for demand term `refined oil`
- `butter oil` (culinary) for demand term `butter oil`
- `dehydrated vegetable` (whole_food) for demand term `dehydrated vegetable`
- synonym `caster sugar` -> `sugar`
- synonym `natural vinegar` -> `vinegar`
- synonym `mango pieces` -> `mango`

## Marker proposals (classification-bearing: owner decision, not staged)

- #15 `liquid glucose` (1 inputs): classification_bearing: FAO 2019 (ca5644en.pdf) p.9 names 'varieties of sugars' (class) among ultra-processed ingredients and PMC10127522 (Martinez Steele et al., J Nutr 2022;153(1):225-241) (table footnote 12, 'Other ultraprocessed foods') codes 'all syrups (excluding 100% maple syrup)' as ultra-processed: class-instance (glucose syrup in liquid form); FAO Group 2 names only maple syrup among syrups, so no conflict. STRONG marker proposal for the owner.
- #16 `glucose syrup` (1 inputs): classification_bearing: FAO 2019 (ca5644en.pdf) p.9 names 'varieties of sugars' (class) among ultra-processed ingredients and PMC10127522 (Martinez Steele et al., J Nutr 2022;153(1):225-241) (table footnote 12, 'Other ultraprocessed foods') codes 'all syrups (excluding 100% maple syrup)' as ultra-processed: class-instance (a syrup); FAO Group 2 names only maple syrup among syrups, so no conflict. STRONG marker proposal for the owner.
- #17 `texturized soy protein` (1 inputs): classification_bearing: NUPENS 'Food classification Nova' page (nupens.fsp.usp.br/en/food-classification-nova/) (group 4) lists 'protein isolates or concentrates' among the substances of ultra-processed formulations and Monteiro et al., Lancet 2025 'Ultra-processed foods and human health: the main thesis and the evidence' (fsp.usp.br PDF) names 'plant protein isolates'; FAO p.9 names 'soya protein isolate' (existing marker 'protein isolate'). Texturized soy protein as an instance of that class is an INFERENCE (extruded product of soy protein concentrate or flour). STRONG marker proposal for the owner.

## CONFLICT between authoritative sources (flagged, not parked, not staged)

- #18 `defatted soya` (1 inputs): authoritative_sources_conflict: PMC10127522 (Martinez Steele et al., J Nutr 2022;153(1):225-241) (footnote 2) places generic 'flours' with the unprocessed or minimally processed foods, while Monteiro et al., Lancet 2025 'Ultra-processed foods and human health: the main thesis and the evidence' (fsp.usp.br PDF) describes ultra-processed foods as made from soy and other crops fractioned into starches, fibre, sugars, oils and fats, and proteins, and NUPENS 'Food classification Nova' page (nupens.fsp.usp.br/en/food-classification-nova/) lists protein isolates or concentrates among group 4 substances: a defatted soy fraction is placed differently depending on which statement applies. FLAGGED, not parked and not staged.

## Label-bound (conditioned clause, never staged)


## Parked

- #19 `cocoa solids` (1 inputs): no_authoritative_source_covers_it: none of FAO 2019, Monteiro 2018/2019, Lancet 2025, NUPENS pages or PMC10127522 (Martinez Steele et al., J Nutr 2022;153(1):225-241) names or places cocoa solids; PMC10127522 (Martinez Steele et al., J Nutr 2022;153(1):225-241) places 'unsweetened baking chocolate' and 'cocoa powder' (cocoa mass or solids as the same thing is an unstated equivalence); FDC names cocoa products (naming only)
- #20 `cocoa nibs` (1 inputs): no_authoritative_source_covers_it: none of FAO 2019, Monteiro 2018/2019, Lancet 2025, NUPENS pages or PMC10127522 (Martinez Steele et al., J Nutr 2022;153(1):225-241) names or places cocoa nibs; PMC10127522 (Martinez Steele et al., J Nutr 2022;153(1):225-241) places 'unsweetened baking chocolate' and 'cocoa powder' (cocoa mass or solids as the same thing is an unstated equivalence); FDC names cocoa products (naming only)
- #21 `cocoa mass` (1 inputs): no_authoritative_source_covers_it: none of FAO 2019, Monteiro 2018/2019, Lancet 2025, NUPENS pages or PMC10127522 (Martinez Steele et al., J Nutr 2022;153(1):225-241) names or places cocoa mass; PMC10127522 (Martinez Steele et al., J Nutr 2022;153(1):225-241) places 'unsweetened baking chocolate' and 'cocoa powder' (cocoa mass or solids as the same thing is an unstated equivalence); FDC names cocoa products (naming only)
- #22 `carbonated water` (1 inputs): no_authoritative_source_covers_it: the sources place carbonated SOFT DRINKS (products) and 'carbonating agents' (an additive class), not plain carbonated water as an ingredient; FDC names bottled non-carbonated waters (naming only)
- #23 `cereal extract` (1 inputs): no_authoritative_source_covers_it: no authoritative source places a cereal or malt extract; PMC10127522 mentions malt flavour and malt syrup only inside ultra-processed corn-flake ingredient lists; FDC names 'Syrups, malt' (naming only)
- #24 `malt extract` (1 inputs): no_authoritative_source_covers_it: no authoritative source places a cereal or malt extract; PMC10127522 mentions malt flavour and malt syrup only inside ultra-processed corn-flake ingredient lists; FDC names 'Syrups, malt' (naming only)
