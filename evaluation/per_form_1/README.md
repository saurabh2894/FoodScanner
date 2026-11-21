# per_form_1: roasted/toasted plain grains and the whole_food unknown-bracket safeguard (ready for review; NOT merged)

Branch claude/per-form-1 off main 22966c8 (after engine-fixes-1). Owner evidence rulings applied; ONLY the two supported cases are implemented.

## 1. Per-row provenance (single row-level table)

| item | table / code | status | source (verbatim) | inference level | condition kept |
|---|---|---|---|---|---|
| `roasted` | descriptors.csv (existing global row, UNCHANGED) | exact-named method | FAO 2019 ca5644en p.6 (printed): "Minimally processed foods are natural foods altered by methods that include removal of inedible or unwanted parts, and also processes that include drying, crushing, grinding, powdering, fractioning, filtering, roasting, boiling, non-alcoholic fermentation, pasteurization, chilling, freezing, placing in containers, and vacuum packaging." | exact-named ('roasting') | plain form only; salted/sugared nut guards and every marker keep priority |
| `toasted` | descriptors.csv NEW row, kind-scoped (`kinds` = whole_food;flour) | PROVISIONAL | the same p.6 sentence | INFERENCE: toasting read as the same dry-heat method as the named 'roasting' (not named by the clause) | scoped to whole_food and flour rows only (`classify._scoped_descriptors`, mirrored in `foodscan.js`); never applied when the name holds `salted`; never overrides a marker, a list rule or the powder standard |
| unknown-bracket abstention | `classify._RESIDUAL_EXTRA_KINDS` = (flour, whole_food) (was flour) | code rule, no table row | owner ruling: an item with a bracket naming content the vocabulary does not recognise cannot be answered Group 1 | intended attributed change class: 'Rice (XQ9)' Group 1 -> abstain | benign bracket parts unchanged: recognised foods, descriptors, condition words, negations, connectors, digits/codes |

`toasted` surface (measured, '<word> <term>' for every one of the 384 lexicon rows, before/after): 44 forms change, all None -> Group 1: toasted / flour: 18, toasted / whole_food: 26; changes outside whole_food/flour: []; 'roasted' surface: 0 changes; group moves other than None->1: 0.

## 2. Parked (NOT implemented; recognition/abstention stands; no rows)

| term | state at runtime | park reason (owner ruling) |
|---|---|---|
| `enriched flour` / `fortified X` | unrecognised, abstains (Enriched/Fortified Wheat Flour: 'not in the local vocabulary') | a US standard of identity (21 CFR 137.165) does not establish compliance or an identical meaning for an unqualified term on an Indian or unknown-jurisdiction label, and composition alone does not establish the replacement purpose FAO's fortification sentence conditions on; unresolved |
| sprouted anything | recognised by name only (kind unplaced), no placement | no positive placement evidence (identity unverified at primary sources) |
| `pearled barley` | unrecognised, abstains | no applicable grain-processing clause |
| `Vitamins and Minerals` standalone | recognised by name only, abstains | unresolved; abstention stands (marker-list absence alone does not establish neutral handling in composite foods) |

## 3. Gate evidence (committed tree; BEFORE = worktree of main 22966c8; separate fresh processes)

| check | result |
|---|---|
| frozen 66 | changed 1: b3/Q10 only, attributed (see below); unexplained 0; abstain->4 0 |
| out-of-sample 32 | changed 0; unexplained 0; abstain->4 0 |
| drift (534 existing terms/synonyms alone) | 0 differences |
| powder surface (552 forms) | changed 0; bare X powder Group 1 after 0 (unchanged-clean) |
| lexicon / synonyms / markers | 384 -> 384 rows, 0 added, 0 source-changed; synonyms.csv and markers.csv byte-identical |
| suite | 1533 passed, 5 xfailed |
| parity | 672/672 identical (additions-only: 653 + 19 inputs, 0 lines removed) |

**The one attributed frozen change:** b3/Q10 `Milk solids (Pasteurized skimmed cow milk)`: Group 1 -> None (status unchanged). It is a whole_food item whose bracket holds the word `cow`, which the vocabulary does not recognise, so the new whole_food abstention applies (same class as `Rice (XQ9)`). Four frozen-input tests (`test_sweetener_foods_note`, `test_thickener_emulsifying_salt_markers`, `test_vocab_gap_and_soybean` and `test_validate_batch::flip harness`) were updated with an explanation of this exception, not weakened. Proposal for you (NOT implemented): a bracket naming a source species (cow, buffalo) on a milk item is a plain provenance note; treat it as benign by an explicit decision if you want Q10 back.

## 4. Controls (applied_gate.json 'controls'; before -> after group)

| control | before | after |
|---|---|---|
| roasted buckwheat | 1 | 1 |
| toasted oat flour | None | 1 |
| toasted buckwheat | None | 1 |
| toasted rice | None | 1 |
| enriched wheat flour | None | None |
| fortified wheat flour | None | None |
| enriched flour | None | None |
| fortified rice | None | None |
| sprouted ragi | None | None |
| pearled barley | None | None |
| vitamins and minerals | None | None |
| rice (xq9) | 1 | None |
| wheat (xq9) | 1 | None |
| milk (xq9) | 1 | None |
| oat flour (xq9) | None | None |
| toasted oat flour (xq9) | None | None |
| toasted salted oat flour | None | None |
| toasted almonds | None | None |
| rice, toasted oat flour | None | None |
| mango powder | None | None |
| 100% mango powder | 1 | 1 |
| milk powder | 1 | 1 |

Notes: `Roasted Salted Buckwheat` is Group 1 and was before this branch (the existing global descriptor `salted`, 'a form word that does not change what the ingredient is', has no guard for grains); this branch does not change it and the new `toasted` path refuses a salted name, so `Toasted Salted Oat Flour` abstains. Owner decision if you want salted grains guarded like nuts and legumes.

## 5. Batch-4 staging note aligned
The staging guard for 'roasted'/'toasted' in `data/ingest/class_grains_1.json` (word_guard.why) and finding 2 of `evaluation/class_bulk_4/README.md` now state that the guard is a staging-scope note and that runtime Group 1 for plain roasted/toasted grains rests on the FAO p.6 methods clause (legume precedent). No rows, decisions or hashes of staged outputs were changed (the rule file hash differs from scope_summary.json by design; decisions are unchanged).

## 6. Exact diff vs main 22966c8 (17 files incl. this README and the gate artifact)
`data/ingest/class_grains_1.json` (note), `data/ingest/per_form_1.json` (controls), `evaluation/class_bulk_4/README.md` (note), `evaluation/per_form_1/{README.md,fao_p6_quote.txt,applied_gate/applied_gate.json}`, `scripts/applied_gate.py` (--descriptor-surface), `scripts/class_gate.py` (reason text counts for attribution), `scripts/parity_check.py` (+4 lines, 0 removed), `src/foodscan/classify.py` (+15/-2), `src/foodscan/resources/descriptors.csv` (+1 row, header gains `kinds`), `tests/test_per_form_1.py` (new) and the four updated tests, `web_preview/foodscan.js` (+10/-2). normalise.py, lexicon.csv, synonyms.csv, markers.csv: untouched.

