# pmc_reresearch_3: decision record for the remaining parked terms re-read against the three admissible PMC copies + FAO (documentation only)

DOCUMENTATION-ONLY branch (re-cut onto main a2935ed): no lexicon, synonym, marker or classifier change. Sources re-read (cached, read-only, paraphrase, licence unverified): Monteiro 2018 (PMC10261019), Monteiro 2019 (PMC10260459), Martinez Steele 2022 (PMC10127522), plus FAO 2019. 17 terms recorded in data/ingest/pmc_decisions_3.json.

## Whey: APPROVED and already merged
The two whey rows (whey powder, whey solids) were proposed here, approved by the owner on 2026-11-21 and merged into markers.csv as strong derived_substance markers via claude/markers-2 (three admissible sources name whey or whey protein: FAO p.9, Monteiro 2018, PMC10127522; the dried form is an explicit inference). See evaluation/markers_2/ for the gate (frozen 66: b1/N05, dev/F06, neg/R5 only, group 4 -> 4; out-of-sample unchanged).

## Everything else stays parked (reasons in the decisions file)
dry fruits (mixes nuts with dried fruit), roasted gram (naming), refined oil, butter oil, defatted soya, texturized soy protein, cocoa butter/solids/nibs/mass (single source or broader than FAO), carbonated water, cereal extract, malt extract, mango pieces.
