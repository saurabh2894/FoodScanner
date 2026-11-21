# markers_1: five owner-approved strong markers (CLASSIFICATION-BEARING; branch claude/markers-1, off main 1eb06e0)

Rows (data/ingest/marker_rows_1.json -> src/foodscan/resources/markers.csv; class derived_substance, strength strong): fructose (exact term named), wheat gluten (instance of 'gluten'), hydrolysed vegetable protein (instance of 'hydrolysed proteins'), lemon juice concentrate and apple juice concentrate (instances of the class 'fruit juice concentrates'; class-level coverage, exact terms not named).
Each row's source quotes the clause verbatim (FAO 2019 ca5644en p.9: "include varieties of sugars (fructose, high-fructose corn syrup, ‘fruit juice concentrates’, ...) ... and sources of protein (hydrolysed proteins, soya protein isolate, gluten, casein, whey protein, and ‘mechanically separated meat’)") and cites the identification sentence as the classification basis (p.10: "The presence in the list of ingredients of one or more of these food substances identifies a product as ultra-processed."). Both quotes are checked verbatim against the report text by the gate (scripts/marker_batch.py).

## Gate: before and after builds in separate fresh processes; every changed input listed and attributed to a marker
Frozen 66: 8 inputs changed, all in `drivers` only (group 4 -> 4 and status unchanged on all 8): b1/N13 (lemon juice concentrate), b1/N16, b2/M10, dev/F07, dev/F08 (wheat gluten), neg/R4 (apple juice concentrate), neg/R5 (fructose), dev/F03 (hydrolysed vegetable protein). Out-of-sample 32: 5 changed, drivers only, group 4 -> 4 and status unchanged: S04 (hydrolysed vegetable protein), S15, S19, S22 (wheat gluten), S30 (both). Unexplained changes: 0. Group changes that are not abstain -> 4: 0. No abstaining label moved to Group 4 on either set: every input holding these terms was already Group 4 by other markers, so the new rows add drivers (evidence) and change no group.
Full listing with the new driver text per input: gate_report.md / gate_report.json.

## Not added (scope as approved; candidates for a later decision)
- 'hydrolysed protein' (FAO's own term), other fruit juice concentrates (orange, grape, pineapple), lactose, casein, whey protein, soya protein isolate (existing row: protein isolate), 'mechanically separated meat'.
- KNOWN GAP (strict xfail in tests/test_marker_rows_1.py): the z spelling 'hydrolyzed vegetable protein' does not match the approved row (dev/F07 and S13 hold it; both are Group 4 by other markers). A spelling synonym for it needs your approval.

## Tests that encoded the earlier proposal status were updated, not weakened
tests/test_lexicon_1.py::test_condition_handling_processed_forms_stay_unassessed: 'apple juice concentrate' still has no lexicon row but is now an approved marker (answers Group 4, no longer unassessed); the other four processed forms still must stay unassessed. tests/test_demand_bulk_1.py: the mixed parked list now answers Group 4 only because of the approved 'wheat gluten', the rest stays unplaced.

Suite 1092 passed + 5 expected failures; parity 429/429 (11 new synthetic texts, incl. 'gluten free', 'Contains gluten', fructooligosaccharide, orange juice concentrate as non-markers).
