# class_bulk_5: Nuts and Seeds (PROPOSAL; staging only, merge stops with the owner)

Branch claude/class-bulk-5-nuts off main c0ece2b. Input: junior branch antigravity/class-bulk-5-nuts (0fcdcd5), senior-reviewed in `evaluation/junior_reviews_2/05_nuts_review.md` (branch claude/junior-reviews-2). Decision reference: owner instruction 2026-11-21 (stage the accepted nut rows; no merge).

## 1. Source and rule
FAO 2019 (ca5644en) Table 1 Group 1 example, verified verbatim: "tree and ground nuts and other oily seeds (with no added salt or sugar)". Group 3 example: "salted or sugared nuts and seeds". The existing kind `nut_seed` guard applies the salt/sugar condition at item level (the item's own name or bracket); no classifier, parser, normaliser, synonym, marker or descriptor change.
Inference level per row: class-instance (tree nuts or oily seeds); nothing is NAMED. Chestnuts and ginkgo nuts carry a caveat in the row (starchy, low-fat; the clause names tree nuts without the 'oily' qualifier). FDC (CC0) is naming and form evidence only.

## 2. Rows staged (20 new `nut_seed` rows; `staged_rows.csv` has the full source text and FDC IDs)
acorns, beechnuts, brazil nuts, butternuts, cashew nuts, chestnuts (8 FDC records kept in provenance, incl. 169408 dried and 169413 raw), chia seeds, ginkgo nuts, hazelnuts, hickory nuts, macadamia nuts, pecans, pili nuts, pine nuts, pistachio nuts, safflower seeds, sesame seeds, sunflower seeds, walnuts, watermelon seeds. 40 FDC accept records stand behind them.
Not staged: almonds, pumpkin seeds, flax seeds (already rows, unchanged); lotus seeds, breadfruit seeds, breadnut seeds, sisymbrium seeds (held by the review: oily-seed membership unsupported).

## 3. Gates (committed tree; BEFORE = worktree of main c0ece2b, AFTER = this branch; separate fresh processes)
| check | result |
|---|---|
| lexicon | 386 -> 406 (+20 nut_seed rows; none changed or removed); synonyms.csv, markers.csv, descriptors.csv byte-identical |
| frozen 66 | changed 0; unexplained 0; abstain->4 0 |
| out-of-sample 32 | changed 4 (S06, S08, S27: 'Sesame Seeds'; S30: 'Cashew Nuts'); each only moves that item from the Not-assessed list to recognised; group and status unchanged; unexplained 0; abstain->4 0 |
| drift (536 existing terms/synonyms) | 0 differences |
| salted surface (49 base rows, 147 forms) | 0 changed |
| descriptor surface (`roasted`, `toasted`; 772) | 0 changed |
| powder surface (558) | 0 changed (the five milk-powder Group 1 forms are the owner-allowed ones) |
| after-build proof | all 20 rows recognised after, none before (3 forms each) |
| suite | 1674 passed, 5 xfailed |
| parity | 738/738 identical (additions-only, +16 inputs) |

## 4. New-row surface (after-build, all 20 rows; same result for every row)
| form | group | form | group |
|---|---|---|---|
| X | 1 | X (sugar) | 3 |
| roasted X / dry roasted X | 1 | X, salt | 3 |
| unsalted X / X (no added salt) | 1 | salted X / roasted salted X | 3 |
| X powder / 100% X powder / whole X powder | 1 | oil roasted X / honey roasted X / sugared X | abstain |
| toasted X / toasted salted X | abstain | X flour / X butter / X oil / Rice, X | abstain |
| X (canned) | **1** | X (XQ9) | **1** |

Controls (`data/ingest/class_nuts_5.json`): the singular forms hazelnut, walnut and pecan already resolve to the plural rows (existing engine behaviour); cashew, cashews, pistachios, sesame, peanuts, coconut, butters, flours and the four held seeds stay unrecognised or abstain; `mixed nuts` abstains; `almonds, cashew nuts, walnuts` abstains (combination rule).

## 5. Decisions and gaps for the owner (not changed here)
1. **Pre-existing gap now wider.** The `nut_seed` kind has no canned/bottled/brine abstain and no unrecognised-bracket guard (the legume, vegetable, fruit and flour kinds do). Measured on main: `almonds (canned)`, `almonds (brine)`, `almonds (XQ9)` already answer Group 1. After this batch the same holds for all 20 new rows (`walnuts (brine)`, `walnuts (canned)`, `walnuts (XQ9)` -> 1). FAO Group 3 names canning/bottling with added salt, oil or sugar; whether to extend the guard to nut_seed before or after this batch merges is your call (small, separate engine item).
2. `oil roasted X` and `honey roasted X` abstain (the words are unrecognised, so nothing is placed); salted/sugared forms take Group 3 via the existing guard. No oil guard exists.
3. Synonym candidates (filberts, pepitas, pinyon pine nuts, black/english walnuts, chestnut varieties; singular/plural label forms such as cashew, cashews, pistachios) are parked.
4. Queue groups (butters, flours, coconut, roasted plain, mixed) remain per-form decisions.

## 6. Exact diff vs main c0ece2b
`data/ingest/class_nuts_5.json`, `evaluation/class_bulk_5_nuts/{README.md,staged_rows.csv,applied_gate/applied_gate.json}`, `scripts/applied_gate.py` (new-rows forms extended), `scripts/parity_check.py` (+16 inputs), `src/foodscan/resources/lexicon.csv` (+20 rows), `tests/test_class_bulk_5_nuts.py` (new).
