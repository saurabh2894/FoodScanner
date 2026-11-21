# pmc_reresearch_1: PMC10127522-first re-research of the strongest parked terms (branch claude/source-survey-1)

## Owner decision applied (2026-11-21)
1. The lexicon-1 hold is LIFTED for plain `starch` and `tapioca starch` ONLY: kind culinary rows in lexicon.csv, PROVISIONAL, the FAO Group 2 clause verbatim, PMC10127522 cited as corroboration (licence-unverified paraphrase). `modified starch` stays a separate strong Group 4 marker (markers.csv unchanged).
2. cocoa powder, yeast, sorghum flour, soya flour, split pulse urad flour STAY PARKED; standing reason recorded in the decisions file: 'single admissible source or broader than FAO'. No further action until a second admissible source lands.
3. Boundary guard (small classify.py + JS change, found necessary by the negative test): an entry named starch/tapioca starch whose BRACKET says the starch is modified (modified, pregelatinised, acid treated, oxidised, cross-linked, bleached, hydroxypropyl, acetylated, phosphated, thermally/enzymatically) is read as the strong 'modified starch' marker, never as plain starch. Without it `Starch (Modified)` was recognised as plain starch and answered Group 3. Names such as modified corn starch, corn starch, maize starch, potato starch, pregelatinised starch stay unrecognised (abstain). tests/test_starch_rows.py pins all of it.
4. Gate, final state vs main 95546b9 in separate fresh processes: 66 frozen inputs: only `unassessed` changes (b1/N03 and b1/N05 tapioca starch, b1/N12, b3/Q14 and dev/F03 starch left 'not assessed'), group/status/drivers/reason 0 changes, all attributed to the two rows; out-of-sample 32: only S28 and S30 lose 'Tapioca Starch' from unassessed, group 4 stays 4, status unchanged. Suite 1139 passed + 5 expected failures, parity 451/451.


Conditions applied (owner decision): corroborating source only, paraphrase, identifier + "licence unverified" in provenance, never sole support beyond FAO 2019 / Monteiro (then park and flag), label-context conditions unchanged. Row labels confirmed from the table markup: footnote 2 = "Other unprocessed or minimally processed foods", footnote 5 = "Other processed culinary ingredients" (research/08).

| Term | PMC10127522 (paraphrase) | FAO 2019 / Monteiro status | Result |
|---|---|---|---|
| starch, tapioca starch | coded with "Other processed culinary ingredients" | FAO Table 1 Group 2 "starches extracted from corn and other plants": AGREES | corroborated; staged as a PROPOSAL only because the lexicon-1 senior review holds both terms: flip evidence below, NOT in lexicon.csv, needs your lift of the hold |
| cocoa powder | unsweetened baking chocolate and cocoa powder coded with processed culinary ingredients | FAO/Monteiro silent (cocoa only in products) | PMC alone, extends beyond FAO: PARKED and FLAGGED for you; its coding concerns unsweetened cocoa powder |
| yeast | coded with unprocessed or minimally processed foods | silent (FAO names fresh or dried mushrooms as fungi) | PMC alone: PARKED and FLAGGED; distinct from yeast extract (standing non-marker decision) |
| sorghum flour, soya flour, split pulse urad flour | generic "flours" coded with unprocessed or minimally processed foods | FAO names flour from corn, wheat, oats or cassava only: PMC is broader | extends beyond FAO for these flours: PARKED and FLAGGED (wheat flour is already a kind-flour row) |

## Flip evidence for the starch proposal (gate scripts/demand_batch.py with an explicit PROPOSED-ONLY override; nothing merged)
66 frozen inputs, separate fresh processes: group, drivers, status, reason, warnings, ingredients, INS 0 changes; `unassessed` on 5 inputs (b1/N03, b1/N05, b1/N12, b3/Q14, dev/F03: starch and tapioca starch leave "not assessed"), all attributed, 0 unexplained. Out-of-sample 32: no change. Effect if you lift the hold: kind culinary, so a single-item "Starch" list becomes Group 2 and starch + a whole food becomes Group 3; the existing `modified starch` strong marker keeps priority.

## What this batch did NOT do
No row was added to lexicon.csv or markers.csv; the decisions are in data/ingest/pmc_decisions_1.json. Open decisions for you: lift the starch hold (flip evidence ready); say whether cocoa powder, yeast and the three flours should stay parked until a second source agrees.
