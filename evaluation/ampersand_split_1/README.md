# ampersand_split_1: '&' pairs inside brackets (branch claude/ampersand-split-1, off main de86733)

Owner-approved candidate (evidence: the junior's evaluation/ampersand_split_sim_1, run on d7e225d). Implemented in parser/pipeline (`_split_amp_pair` in pipeline.py, used when a bracketed group is expanded) and mirrored in web_preview/foodscan.js. Run here against CURRENT main de86733.

## Rule (with the owner's scope corrections)
- Only an '&'-joined pair of exactly two parts inside a bracket; a connector other than '&', three parts, or any other bracket content keeps the item WHOLE.
- Both sides must be recognised WITH the shared modifier attached: a leading modifier of the left side applies to both ("Sprouted Ragi & Jowar" tests "sprouted ragi" and "sprouted jowar", never bare "jowar"); if either modified form is unrecognised the pair stays whole ("Sprouted Ragi & Oat", "Fermented Ragi & Oat").
- A shared trailing percentage is kept as shared context: a result note says it applies to the pair, and it is NOT copied onto the items.
- Recognition only: a pair whose sides are recognised-but-unplaced (kind unplaced) splits for RECOGNITION; the items still abstain, so the list still abstains and the split is never described as resolving classification.
- Conditions stay on both sides ("Salted Almonds & Pumpkin Seeds" -> "Salted Almonds", "Salted Pumpkin Seeds").
- Recorded deviation from the owner's example: "Roasted Rice & Oat" DOES split, because 'roasted' is a descriptor so "roasted oat" is recognised in the current vocabulary; the unrecognised-modified-form control uses "Sprouted/Fermented Ragi & Oat" instead.

## Flip evidence vs main de86733 (before/after in separate fresh processes)
- Frozen 66: no field changes at all on current main (the junior's two frozen splits, INS-code pairs, are not affected here).
- Out-of-sample 32: only S26 changes: "Thyme & Rosemary" leaves the unassessed list (both recognised); group 4 stays 4, status unchanged.
- Owner acceptance label (exact text): still ABSTAINS (reason: only the weak antioxidant marker); unassessed is now only "Multigrain Flour Blend (45.7%) (group name; its contents were assessed separately)"; unplaced = Sprouted Ragi, Sprouted Jowar, Vitamins, Minerals; notes: "Sprouted" read as shared, 23.4% and 22.3% apply to their pairs. Without the antioxidant item the abstention reason is the unplaced one.
- Controls (texts_before_after.json): sprouted ragi & oat, fermented ragi & oat, spices & condiments, rice & oat (organic), three-part pair, palm & palmolein stay whole and unchanged; salted almonds & pumpkin seeds splits with the condition kept on both (still abstains); "Rice & Oat (22.3%), Salt" and "Roasted Rice & Oat, Salt" go from abstaining to Group 3 because two placed foods are now seen as two foods (expected, attributed to the split).
Tests: tests/test_ampersand_split_1.py; two older tests that pinned the unsplit state were updated (tests/test_held_sources_1.py, tests/test_unplaced_kind_1.py). Suite 1175 passed + 5 expected failures; parity 472/472.
