# pmc_reresearch_3: remaining parked terms re-read against the three admissible PMC copies (branch claude/pmc-reresearch-3, off main de86733)

Sources re-read (cached, read-only, paraphrase, licence unverified): Monteiro 2018 (PMC10261019), Monteiro 2019 (PMC10260459), Martinez Steele 2022 (PMC10127522), plus FAO 2019. 17 terms decided in data/ingest/pmc_decisions_3.json. NO lexicon, synonym or marker change on this branch.

## The one stageable finding: whey (a marker PROPOSAL, classification-bearing, needs your approval)
FAO p.9 names "whey protein" among the substances that identify ultra-processed food; Monteiro 2018 names whey ("directly extracted from foods, such as casein, lactose, whey and gluten"); PMC10127522 lists whey among non-culinary substances that make a bread ultra-processed. Three admissible sources, so `whey powder` and `whey solids` (instances of the named class; the dried form is an inference) are proposed as strong derived-substance markers. data/ingest/marker_rows_2_proposal.json + evaluation/pmc_reresearch_3/markers_proposal_gate/ (scripts/marker_batch.py): rows NOT in markers.csv.
Flip evidence if approved (before/after in separate fresh processes): frozen 66: b1/N05, neg/R5, dev/F06 change DRIVERS only, group 4 -> 4, status unchanged, each attributed to its marker; out-of-sample 32: no change; 0 unexplained; 0 abstain -> 4 moves.

## Everything else stays parked (reasons in the decisions file)
dry fruits (mixes nuts with dried fruit), roasted gram (naming), refined oil, butter oil, defatted soya, texturized soy protein, cocoa butter/solids/nibs/mass (single source or broader than FAO), carbonated water, cereal extract, malt extract, mango pieces.
Open for you: approve (or not) the two whey marker rows.
