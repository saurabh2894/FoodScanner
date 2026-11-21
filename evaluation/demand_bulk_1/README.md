# demand_bulk_1: first demand-driven batch (workstream B; branch claude/demand-bulk-1, off main 6a6334f)

Input: the 110 open terms of evaluation/demand_inventory_1 (noise and photo-only terms excluded), in rank order. One decision per term in data/ingest/demand_decisions_1.json; `scripts/demand_batch.py` checks coverage (every term decided exactly once), the FAO clause verbatim in Table 1 (both pages), FDC ids and descriptions, schema, duplicates, the lexicon-1 standing exclusions, and the 66-input flip check in separate fresh processes. No branch antigravity/demand-bulk-1 exists on the remote (checked), so nothing was reviewed or integrated from it; this batch was generated here.

## Result: 110 terms decided
| Disposition | Terms | Paste-input mentions |
|---|---|---|
| ACCEPT_ROW (lexicon rows) | 4: beans, wheat flour, cabbage, peanut oil (demand term "edible peanut oil") | 5 |
| ACCEPT_SYNONYM | 1: potable water -> water | 1 |
| MARKER_PROPOSAL (classification-bearing, owner decision, not staged) | 5: wheat gluten, hydrolysed vegetable protein, fructose, lemon/apple juice concentrate | 8 |
| LABEL_BOUND (conditioned clause) | 4: apple, grape, orange, pineapple juice | 8 |
| PARK | 96 (reasons below) | 121 |

Supply is the constraint, not tooling: of 110 demand terms only 5 are supported by a source I have read (FAO Table 1 clauses; FDC for names). The rest is parked with a one-line reason each (ambiguity_queue.csv, decisions_report.csv). Park reasons by weight (terms / paste inputs): no source names the term 18/29; form not named (pulps, purees, flakes, meals) 20/25; owner decision 17/19; extraction problem, not vocabulary (items joined without a comma or cut) 13/13; held category C (vitamins, minerals, malted) 7/11; existing standing decision 7/11; blend or class phrase 3/7; additive table 6/7; typo 4/4; source conflict (corn flakes: Group 1 flakes vs Group 4 breakfast cereals) 1/1.

## What would unlock the most remaining demand (owner call, sources not read)
1. An Indian regulatory or trade source (FSSAI standards) equating maida/khand/jowar/roasted gram/Himalayan pink salt with a term already placed (about 8 terms).
2. A NOVA source naming cocoa products and glucose syrup (18 terms, 29 inputs, the biggest block). FAO Table 1 does not.
3. A decision on marker proposals (5 terms): FAO section 3 names gluten, hydrolysed proteins, fructose and fruit juice concentrate among ingredients of ultra-processed foods. Adding them as strong markers would move abstaining labels to Group 4: proposed in marker_proposals.csv, deliberately not staged.
4. The extraction block (13 terms) is parser work, not vocabulary.

## A finding while building it
My first draft accepted starch, tapioca starch and cranberry. The gate's standing-exclusion check (every string in tests/test_lexicon_1.py::test_explicit_exclusions_and_blocked_items_did_not_get_rows) and the existing test caught it: the lexicon-1 senior review had explicitly held starches and blocked cranberry. They are parked as `existing_decision` and the gate now refuses any staged term on that list.

## Gates
Flip check (66 frozen inputs, separate fresh processes): group 0, drivers 0, status 0, warnings 0; reason text changed on 1 input and 5 inputs lost an unassessed item (all attributed to the new rows, 0 unexplained). Out-of-sample set re-run from the cache vs main: group and status unchanged on 32/32; 3 labels differ in what is still unassessed: S01 loses "red cabbage", S15 and S24 lose "Wheat Flour" (group 4 stays 4). Suite 1080 passed + 4 expected failures; parity 418/418 (10 new synthetic texts).

## Junior cross-check (antigravity/demand-bulk-1, read-only reference; 38 of its 40 dispositions agree with this batch)
- Divergence, resolved: `wheat flour` is LABEL_BOUND there and a kind-`flour` row here (owner confirmed kind flour: single-item lists answer, multi-item lists abstain).
- Its quote "substances extracted from whole foods, such as casein, lactose, whey, gluten" is not in FAO Table 1. The nearest verbatim text is Monteiro et al. 2018, Public Health Nutr 21(1):5-17 (PMC10261019): "Some of these are directly extracted from foods, such as casein, lactose, whey and gluten." That is new, citable evidence naming "whey" and "lactose" (carried into the next batch as marker proposals for whey powder / whey solids, owner decision).
- Its `beans` provenance cites FDC 169961 "Beans, snap, green, raw" (a different food), its rule file's `clause.text` is the string "Table 1 Group 1 p.11" and its gate ran without --fao-text, so its verbatim-clause check was vacuous; the merged rows here quote the clauses verbatim and the clause check passes against the report text.
- Its yeast-extract rationale ("Group 4") contradicts the standing decision that yeast extract is not a marker (outcome identical: parked). Its pin of `corn flakes` at tests/test_vocabulary_layer.py:55 corroborates holding that term.
