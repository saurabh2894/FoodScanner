# unplaced_kind_1: recognition-only handling (branch claude/unplaced-kind-1, off main d7e225d)

Owner-approved follow-up: recognise vitamins/minerals and sprouted-grain forms BY NAME without classifying them. Recognition is vocabulary, not classification.

## Kind `unplaced`: the three hard constraints
1. Never suppresses a list-level abstention: any list holding an unplaced item abstains ("recognised by name only, and no source read places X, so the processing level cannot be judged (recognition is vocabulary, not classification)"). The rest of the list can never override it; a strong marker still returns Group 4 first (the kind only ever ADDS an abstention). The baby-food label still abstains overall.
2. Never a classification or classified coverage: not a driver; not in `unassessed`; counted as NOT assessed in `completeness.assessed.not_assessed`; excluded from the OCR yield used to pick the better reading; the evaluation coverage figure is answered/total, so such lists count as abstentions.
3. Rendered distinctly: Python `Analysis.unplaced`, the CLI section "Recognised by name only, NOT placed", and the page section "Recognised by name, not placed" with its own hint, separate from "Not assessed"; the result keeps "No level assigned".
Each row's provenance carries the abstention reason. Code: classify.py, pipeline.py, cli.py, web_preview/foodscan.js, template.html (a small, conservative change); parity covers the new `unplaced` field.

## Rows (data/ingest/unplaced_decisions_1.json, gate scripts/demand_batch.py)
vitamins and minerals, vitamins & minerals, vitamins, minerals (FAO Table 1 Group 1 fortification clause quoted verbatim, purpose-conditioned), sprouted ragi, sprouted jowar (no source names sprouting: 0 mentions in FAO 2019, Monteiro 2018/2019, NUPENS; the Group 1 process list is quoted and does not include it). The '&'-joined pair "Sprouted Ragi & Jowar" is NOT added as a phrase (that would be per-label hardcoding); the pair split stays an open parser decision owned by the junior simulation, so on the owner's label that item remains visibly unassessed.
Standing exclusion: the lexicon-1 hold on "vitamins and minerals" is superseded for the unplaced kind ONLY by the owner's decision (recorded as `owner_override` in the decisions file; tests/test_lexicon_1.py now requires such rows to be kind unplaced).
"Vitamins and Minerals" is split by the existing and-pair rule into two items, so the result lists "vitamins" and "minerals".

## Gate and flips
66 frozen inputs (separate fresh processes): group, drivers, status, reason, warnings, ins_mappings 0 changes; `ingredients` changed on 2 inputs (b2/M14, dev/F14: "VITAMINS & MINERAL" now splits into two recognised items) and `unassessed` on 5 inputs (b1/N16, b2/M14, b3/Q11, dev/F02, dev/F14: the vitamins/minerals items moved from "not assessed" to "unplaced"); 0 unexplained. Out-of-sample 32: no change in any compared field.
Owner acceptance label: still abstains ("only weak or unlisted markers present: antioxidant"); unplaced section lists Vitamins and Minerals; Sprouted Ragi & Jowar and Rice & Oat stay unassessed (pair unsplit). Without the antioxidant item the abstention reason is the unplaced one.
Tests: tests/test_unplaced_kind_1.py (constraints 1-4), tests/test_unplaced_render.py (browser render, skipped without node/playwright). Suite 1115 passed + 5 expected failures; parity 442/442.
