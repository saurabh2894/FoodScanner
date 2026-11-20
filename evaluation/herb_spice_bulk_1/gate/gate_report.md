# Gate report: tier1-herbs-and-spices-1

**Verdict: READY_FOR_REVIEW**

Nothing was merged. `lexicon_candidate_rows.csv` holds the ready rows in lexicon.csv layout for review.

| Check | Result |
|---|---|
| staged rows | 37 |
| schema errors | 0 |
| provenance errors | 0 |
| duplicates (exact, synonym, already recognised) | 12 |
| variants of an existing term (informational) | 11 |
| parked in the ambiguity queue | 10 (Counter({'clause_tier': 10})) |
| ready rows | 25 |
| verbatim clause vs FAO text | PASS |
| harness proof (separate processes) | lexicon rows 115 -> 140; all 25 staged terms recognised after; 0 already recognised before |
| flip check (66 frozen inputs, before and after in separate fresh processes) | group 0, drivers 0, status 0, reason 0, warnings 0, ingredients 0, unassessed 0, ins_mappings 0 |
| group/status/driver flips | 0  |
| unexplained changes | 0 |

## Ready rows

- `allspice`
- `anise seed`
- `basil`
- `caraway seed`
- `celery seed`
- `chervil`
- `coriander leaf`
- `coriander seed`
- `cumin seed`
- `dill seed`
- `dill weed`
- `fenugreek seed`
- `marjoram`
- `oregano`
- `paprika`
- `parsley`
- `peppermint`
- `poppy seed`
- `rosemary`
- `saffron`
- `sage`
- `savory`
- `spearmint`
- `tarragon`
- `thyme`

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

## Unassessed drops attributed to ready rows

