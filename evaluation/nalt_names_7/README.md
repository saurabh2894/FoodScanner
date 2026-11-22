# NALT naming slice 7

2026-11-22. Base main: `e4bb96fb73a746095c522ee7b0eb0b2f53f0dfee`.

One new plain-food head, peanut, and 60 reviewed naming aliases for 32 existing foods plus that head. Proposed totals: 518 canonical rows and 249 aliases. These are 61 new naming routes, not 61 new foods. Tumeric and cardamon are recognition-only aliases and keep the current standalone-spice abstention. No Python/JavaScript classifier or strong-marker rule changes.

## Independent identity and placement

Current USDA NALT Product pages supply exact English naming/category evidence, not NOVA. `aliases.csv` records each admitted name, target and current page. `admission.json` records inherited target scope, the new food, source corrections and holds. Only reviewed current preferred/synonym labels enter this slice. Ordinary singular peanut is a reviewed adaptation of peanuts, not an automated singularisation rule.

Current Martinez Steele et al., J Nutr, Table 1 explicitly names "Nuts, peanuts, and other oilseeds without salt or sugar". FAO Table 1 separately names "tree and ground nuts and other oily seeds (with no added salt or sugar)". The new peanut row keeps the nut/seed item-own salt/sugar/brine, unknown-content and form guards. Plain roasting and explicitly whole/pure same-item grinding/powdering are separate named minimal processes. Peanut butter, flour, oil-roasted forms, an unspecified powder or a borrowed child's 100% claim are not established by the name. The existing protein-isolates Group 4 marker remains separate. Sugared-prefix wording still abstains; explicit salt/sugar item brackets take Group 3. This slice does not add a parser rule for that prefix.

Two existing source fields are corrected, without classification changes. Barley flour uses the currently verified broader cereal-grain flour class, rather than pretending FAO's narrower corn/wheat/oats/cassava example literally covers barley. Soya flour uses the currently verified ground-legume definition. The earlier flours/tapioca footnote did not appear in the current retrieval and is not relied on or repeated as evidence here. Kind `flour` still keeps its existing single-item/mixed-list behavior.

- https://pmc.ncbi.nlm.nih.gov/articles/PMC10127522/
- https://www.fao.org/4/ca5644en/ca5644en.pdf
- https://lod.nal.usda.gov/nalt/en/page/11693
- https://lod.nal.usda.gov/nalt/en/page/40636
- https://lod.nal.usda.gov/nalt/en/page/15860
- https://lod.nal.usda.gov/en/

NALT: USDA National Agricultural Library, NAL Agricultural Thesaurus, CC BY 4.0. Selections and the reviewed singular adaptation are not a USDA endorsement. The July 2024 bulk archive remains discovery only. No full vocabulary or article is redistributed.

## Holds and historical expectations

The proposed short chard alias was rejected because global substitution corrupted Swiss Chard into Swiss Swiss Chard. Spinach beets maps directly to the existing edible-leaf target, without that short alias. Bovine milk was rejected because a generic substitution would extend the broad existing Milk Solids route outside the reviewed milk scope. Species-qualified ewe/ovine/caprine milk names keep their own target guards. Singular groundnut and flaxseed remain out, preserving established oil normalisations. Star anise, winter melon, haricot beans, catjang peas, ambiguous mungo/black-gram names, and the existing cranberry/tamarind/coconut/celery holds are not lifted.

Old source/evaluation ledgers remain unchanged. Specific current-source tests supersede only the prior Peanuts and salted-roasted Peanuts, Maize Oil, Tumeric, Mustard Leaves and selected pulse-name abstentions. Current Product 19330 binds mustard leaves to edible mustard greens, not mustard seed. Entire Linseed Oil and Sunflowerseed Oil names now have separate oil evidence; those longer phrases take precedence over an older short seed alias. All other historical negative controls remain.

## Validation scope

The final allowed suite has 6,783 passes and the same two independently reproduced unchanged-baseline failures, two skipped, one restricted-reference deselected and five xfailed. The baseline had 4,750 passes and those same two failures. New synthetic naming/form controls are not a real-label or image-recognition accuracy sample. The two failures are cached millet-puff OCR section extraction and missing historical fenugreek demand evidence; neither is claimed fixed or acceptable as a new failure.

10,327 full-field Python/JavaScript parity cases match, including 5,546 OCR-text-path and 4,781 pasted-text cases. An additional 104,659 full-field comparisons match; 93,240 alias/parent comparisons have no target-route mismatch. All 706 existing names preserve normalisation, target, group, status and other non-provenance fields. Only barley/soya flour driver source text changes for the documented source corrections. Frozen 66 headline groups are unchanged; dev/F03 Tumeric leaves unassessed, with its Group 4, uncertain status, warnings, drivers and all other compared fields unchanged.

Original-photo and out-of-sample-32 assets are not newly validated. Existing mixture rules can still abstain. No general ingredient-coverage or photo-OCR completion claim follows from this slice.
