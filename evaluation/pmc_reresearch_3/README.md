# pmc_reresearch_3 (UPDATE: the whey marker proposal was APPROVED and is merged on main via claude/markers-2; the 15 parks below are what this branch adds): remaining parked terms re-read against the three admissible PMC copies (documentation-only; re-cut onto main a2935ed)

Sources re-read (cached, read-only, paraphrase, licence unverified): Monteiro 2018 (PMC10261019), Monteiro 2019 (PMC10260459), Martinez Steele 2022 (PMC10127522), plus FAO 2019. 17 terms decided in data/ingest/pmc_decisions_3.json. NO lexicon, synonym, marker or classifier change on this branch.

## Whey: proposed here, then APPROVED by the owner (2026-11-21) and MERGED into markers.csv via claude/markers-2 (historical record of the proposal)
FAO p.9 names "whey protein" among the substances that identify ultra-processed food; Monteiro 2018 names whey ("directly extracted from foods, such as casein, lactose, whey and gluten"); PMC10127522 lists whey among non-culinary substances that make a bread ultra-processed. Three admissible sources, so `whey powder` and `whey solids` (instances of the named class; the dried form is an inference) were proposed, and are now, as strong derived-substance markers. The proposal files this branch originally carried were superseded by data/ingest/marker_rows_2.json and evaluation/markers_2/ (scripts/marker_batch.py gate) on main; the rows are IN markers.csv.
Flip evidence from the proposal gate, confirmed by the merged gate (before/after in separate fresh processes): frozen 66: b1/N05, neg/R5, dev/F06 change DRIVERS only, group 4 -> 4, status unchanged, each attributed to its marker; out-of-sample 32: no change; 0 unexplained; 0 abstain -> 4 moves.

## Everything else stays parked (reasons in the decisions file)
dry fruits (mixes nuts with dried fruit), roasted gram (naming), refined oil, butter oil, defatted soya, texturized soy protein, cocoa butter/solids/nibs/mass (single source or broader than FAO), carbonated water, cereal extract, malt extract, mango pieces.
Decision status: the whey rows were approved and merged via claude/markers-2; nothing is open for the owner on this branch.
