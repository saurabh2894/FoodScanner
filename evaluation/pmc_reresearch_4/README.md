# pmc-reresearch-4 (OWNER-APPROVED PART MERGED)

**Merged (owner decision 2026-11-21): 9 rows + 3 synonyms. NOT merged: the 3 marker proposals (amended to HELD: glucose syrup / liquid glucose 'no ingredient-level naming in an admissible source; product-level coding alone insufficient'; texturized soy protein 'class membership not established for the texturized form'), cocoa powder and dry fruits (PARK until an item-level condition mechanism exists), defatted soya (CONFLICT stands). markers.csv unchanged.** The marker_gate_a/b directories and data/ingest/marker_proposals_4a/4b.json are kept only as the record of the withdrawn proposals. Rule update applied: any authoritative NOVA source may place a term on its own; naming-only sources (FDC, WHO JECFA) never place; conflicts are flagged, not parked; park only when no authoritative source covers the term.

Sources used (details in `data/ingest/pmc_decisions_4.json` -> `sources_used`): FAO 2019 ca5644en; PMC10127522 (cached); NUPENS Nova page (fetched, 200); USP-hosted Lancet 2025 PDF (fetched, 200, pdftotext); FDC naming only; WHO JECFA home reachable but no per-term monograph. Each row quotes one clause, verified verbatim by the gate (`--extra-text`).

## Per-term triage
| Term | Disposition | Placement source | Inference level | Condition / note |
|---|---|---|---|---|
| yeast | row, whole_food | PMC10127522 fn2 | exact-named | "yeast extract" stays unplaced (not a marker, not this row) |
| sorghum flour, soya flour, split pulse urad flour | rows, flour | PMC10127522 fn2 "flours" | class-instance | Group 1 flour behaviour already in kind `flour` |
| cocoa powder | row, culinary | PMC10127522 fn5 | exact-named | **Condition "unsweetened"**: no item-level mechanism for this kind yet; needs one (like nut_seed) BEFORE merge. Classification-bearing |
| cocoa butter | row, culinary | NUPENS Group 2 definition | class-instance (fat extracted by pressing) | |
| dry fruits | row, nut_seed | PMC10127522 fn2 "dried fruits (without added sugars)" | class-instance | Owner to confirm nut_seed as the kind: its sugar condition matches "without added sugars"; salt condition is incidental |
| roasted gram | row, whole_food | FAO Group 1 legumes | inference (roasted pulse) | |
| refined oil | row, culinary | FAO Group 2 vegetable oils | inference (refined form) | |
| butter oil | row, culinary | FAO Group 2 butter | inference | |
| dehydrated vegetable | row, whole_food | FAO Group 1 dried vegetables | class-instance | per-term only, as decided |
| caster sugar / natural vinegar / mango pieces | synonyms | FAO / PMC10127522 fn5 / Lancet 2025 | form variants | |
| glucose syrup, liquid glucose | MARKER proposal (strong) | FAO p.9 'varieties of sugars' + PMC fn12 | class-instance | Classification-bearing, separate gate |
| texturized soy protein | MARKER proposal (strong) | NUPENS Group 4 'protein isolates or concentrates' | **inference** | Classification-bearing, separate gate |
| defatted soya | **CONFLICT** | PMC10127522 fn2 (generic 'flours' with minimally processed) vs Lancet 2025 (soy fractioned into proteins etc.) and NUPENS Group 4 ('protein isolates or concentrates') | - | Both citations in the decisions file; not parked, not staged |
| cocoa solids, cocoa nibs, cocoa mass | PARK | none covers the term | - | |
| carbonated water | PARK | sources place soft drinks / carbonating agents, not the water | - | |
| cereal extract, malt extract | PARK | none | - | |

## Gates (fresh-process before/after, every change attributed)
- Rows + synonyms (`gate/`): READY_FOR_REVIEW; group changes 0, drivers 0, status 0, reason 2, unassessed 15 (all attributed to staged rows), unexplained 0, 66 frozen + 32 out-of-sample.
- Marker proposals (`marker_gate_a/` sugars, `marker_gate_b/` texturized soy protein): READY_FOR_REVIEW. Frozen: 6 and 1 changes; OOS: 2 and 0. All are 4 -> 4 with only a new driver; no abstain->4 and no other group change; unexplained 0.

## Needed before merge
1. Owner decision on each marker proposal (classification-bearing).
2. Cocoa powder needs an item-level "unsweetened" mechanism (or park until built).
3. Owner decision on dry fruits kind, and on the defatted soya CONFLICT.

## Final staged gate (after the owner's decisions)
- Rows + synonyms (`gate/`, run on the pre-staging tables): group 0, drivers 0, status 0, reason 2, unassessed 13 (frozen 66), every change attributed to a staged row, 0 unexplained.
- Post-staging repo vs the pre-merge build in separate fresh processes: frozen 66 and out-of-sample 32 show group/status/drivers unchanged; the only changes are unassessed/reason (frozen 13; OOS S11, S15, S22, attributed to yeast and dehydrated vegetable). 0 abstain->4.
