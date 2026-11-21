# pmc_reresearch_2: remaining parked terms re-read against PMC10127522 (branch claude/pmc-reresearch-2, off main 0463b45)

Same admissibility conditions as pmc_reresearch_1 (read-only use of the cached copy, paraphrase, identifier + "licence unverified", never sole support beyond FAO/Monteiro: then park and flag). 8 terms decided (data/ingest/pmc_decisions_2.json, gate scripts/demand_batch.py).

| Term | PMC10127522 (paraphrase) | FAO 2019 | Result |
|---|---|---|---|
| coconut fat | the Nova description lists coconut and animal fats among the processed culinary ingredients | Group 2 'Vegetable oils crushed from seeds, nuts or fruit' (class) | ROW: culinary, plain only; hydrogenated/fractionated forms are different entries and the strong `hydrogenated` marker still decides (negative test) |
| liquid glucose, glucose syrup | all syrups except 100% maple syrup are coded ultra-processed | silent on glucose syrup | PMC alone and broader than FAO: PARKED and FLAGGED (a placement would be a strong-marker proposal) |
| dehydrated onion, dehydrated vegetable, onions flakes | dried vegetables (no added sugar) coded unprocessed/minimally processed | 'dried ... vegetables' AGREES | two sources agree for 'dried', but 'dehydrated'/'flakes' are different words and a descriptor changes every recognition: PROPOSAL for the owner (a 'dehydrated' descriptor), nothing staged |
| natural vinegar | vinegar coded with the processed culinary ingredients (existing vinegar row corroborated) | silent | no source says what 'natural' means: parked |
| caster sugar | the 'Table sugar' row holds honey, molasses, maple syrup | Group 2 sugar | no source names 'caster': parked |
Not matched in PMC10127522 at all (no change): pulps, purees, pastes, bran, carbonated water, cocoa butter/solids/nibs, whey powder as a form, maida/khand/jowar names.

## Gate and flips (vs main 0463b45, separate fresh processes)
66 frozen inputs: group, drivers, status, reason, warnings, ingredients, INS 0 changes; only neg/R5 loses 'coconut fat' from "not assessed" (attributed, 0 unexplained). Out-of-sample 32: no change. Suite 1142 passed + 5 expected failures; parity 456/456.
Open for you: whether to allow a 'dehydrated' descriptor (two sources agree for 'dried'); glucose syrup stays flagged until a second admissible source lands.
