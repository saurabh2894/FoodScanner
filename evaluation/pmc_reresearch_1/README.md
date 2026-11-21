# pmc_reresearch_1: PMC10127522-first re-research of the strongest parked terms (branch claude/source-survey-1)

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
