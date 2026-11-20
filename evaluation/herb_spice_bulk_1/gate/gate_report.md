# Gate report: tier1-herbs-and-spices-1

**Verdict: READY_FOR_REVIEW**

Nothing was merged. `lexicon_candidate_rows.csv` holds the ready rows in lexicon.csv layout and `synonyms_candidate_rows.csv` the synonym candidates in synonyms.csv layout, for review.

| Check | Result |
|---|---|
| staged rows | 37 |
| schema errors | 0 |
| provenance errors | 0 |
| duplicates (exact, synonym, already recognised) | 12 |
| variants of an existing term (informational) | 11 |
| parked in the ambiguity queue | 11 (Counter({'clause_tier': 10, 'policy': 1})) |
| ready rows (new lexicon rows) | 20 |
| synonym candidates (variant policy variant-policy-1) | 4 |
| policy errors | 0 |
| verbatim clause vs FAO text | PASS |
| harness proof (separate processes) | lexicon rows 115 -> 135; all 24 staged terms recognised after; 0 already recognised before |
| flip check (66 frozen inputs, before and after in separate fresh processes) | group 0, drivers 0, status 0, reason 0, warnings 0, ingredients 0, unassessed 0, ins_mappings 0 |
| group/status/driver flips | 0  |
| unexplained changes | 0 |

## Ready rows (new lexicon rows)

- `allspice`
- `basil`
- `celery seed`
- `chervil`
- `coriander leaf`: separate row because different plant part from coriander seed
- `coriander seed`: separate row because different plant part from coriander leaf; the existing bare row 'coriander' is ambiguous between parts and is left untouched (not widened)
- `dill seed`: separate row because different plant part (seed) from dill weed; the existing bare row 'dill' is left untouched (not widened)
- `dill weed`: separate row because different plant part (leaf) from dill seed; the existing bare row 'dill' is left untouched (not widened)
- `marjoram`
- `oregano`
- `paprika`
- `parsley`
- `peppermint`: separate row because different species from 'mint' (bare mint is an existing row)
- `rosemary`
- `saffron`
- `sage`
- `savory`
- `spearmint`: separate row because different species from 'mint' (bare mint is an existing row)
- `tarragon`
- `thyme`

## Synonym candidates (variant policy: same ingredient, plant part and form)

- `anise seed` -> `aniseed`
- `caraway seed` -> `caraway`
- `cumin seed` -> `cumin`
- `fenugreek seed` -> `fenugreek`

## Duplicates (excluded: already covered)

- `bay leaf`: exact lexicon term (kind herb_spice)
- `black pepper`: exact lexicon term (kind herb_spice)
- `cardamom`: exact lexicon term (kind herb_spice)
- `cinnamon`: exact lexicon term (kind herb_spice)
- `cloves`: already recognised by this build (descriptors, plurals or synonyms)
- `fennel seed`: already recognised by this build (descriptors, plurals or synonyms)
- `ginger`: exact lexicon term (kind herb_spice)
- `mace`: exact lexicon term (kind herb_spice)
- `mustard seed`: exact lexicon term (kind herb_spice)
- `nutmeg`: exact lexicon term (kind herb_spice)
- `turmeric`: exact lexicon term (kind herb_spice)
- `white pepper`: exact lexicon term (kind herb_spice)

## Variants of existing terms (kept; informational)

- `caraway seed` ~ ['caraway']
- `coriander leaf` ~ ['coriander']
- `coriander seed` ~ ['coriander']
- `cumin seed` ~ ['cumin']
- `dill seed` ~ ['dill']
- `dill weed` ~ ['dill']
- `fenugreek seed` ~ ['fenugreek']

## Ambiguity queue (parked, never included)

- `Spices, curry powder` (clause_tier, form_embedded_in_name): 'curry powder': a form word sits inside the name, so it may be a product or blend rather than a single herb or spice
- `Spices, pepper, red or cayenne` (clause_tier, qualifier_unresolved): qualifier(s) ['red or cayenne'] are not clause forms and cannot be resolved mechanically
- `Spices, chili powder` (clause_tier, form_embedded_in_name): 'chili powder': a form word sits inside the name, so it may be a product or blend rather than a single herb or spice
- `Spices, garlic powder` (clause_tier, form_embedded_in_name): 'garlic powder': a form word sits inside the name, so it may be a product or blend rather than a single herb or spice
- `Spices, onion powder` (clause_tier, form_embedded_in_name): 'onion powder': a form word sits inside the name, so it may be a product or blend rather than a single herb or spice
- `Spices, pumpkin pie spice` (clause_tier, blend_name): 'pumpkin pie spice': a multi-word name ending in 'spice' is a blend
- `Vinegar, distilled` (clause_tier, qualifier_unresolved): qualifier(s) ['distilled'] are not clause forms and cannot be resolved mechanically
- `Vinegar, red wine` (clause_tier, qualifier_unresolved): qualifier(s) ['red wine'] are not clause forms and cannot be resolved mechanically
- `Vinegar, balsamic` (clause_tier, qualifier_unresolved): qualifier(s) ['balsamic'] are not clause forms and cannot be resolved mechanically
- `Vinegar, cider` (clause_tier, qualifier_unresolved): qualifier(s) ['cider'] are not clause forms and cannot be resolved mechanically
- `poppy seed` (policy, overlaps_conditioned_clause): FAO Table 1 Group 1 also lists 'tree and ground nuts and other oily seeds (with no added salt or sugar)': a conditioned clause. Poppy seed sits on the boundary between that clause and the unconditioned herbs-and-spices clause; the boundary is unresolved, so it is parked (same discipline as the juice rows).

## Unassessed drops attributed to ready rows

