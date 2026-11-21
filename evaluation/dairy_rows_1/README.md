# dairy_rows_1: five whole_food rows (PROPOSAL; staging only, merge stops with the owner)

Branch claude/dairy-rows-1 off main 46ad81c. Input: junior branch antigravity/class-bulk-6-dairy (bbc0fb8), senior review `evaluation/junior_reviews_3/06_dairy_review.md` (branch claude/junior-reviews-3). Decision reference: owner instruction 2026-11-21 (narrow dairy proposal, exactly five rows).

## 1. Rows (kind whole_food; full text in the lexicon `source` column and `data/ingest/dairy_rows_1.json` controls)
| term | clause (FAO 2019 ca5644en Table 1 Group 1, p.11, verified verbatim) | FDC record (naming and plain-form evidence only) | inference level |
|---|---|---|---|
| sheep milk | definition "...or of or from animals (muscle, fat, offal, eggs, milk)..."; example "fresh, powdered or pasteurized milk" | sr_legacy 170882 "Milk, sheep, fluid" | class-instance of the animal milk named by FAO; species not named by any NOVA source read (same level as goat milk) |
| duck eggs | same definition; example "fresh, powdered, chilled or frozen eggs" | sr_legacy 172189 "Egg, duck, whole, fresh, raw" | class-instance of the eggs named by FAO |
| goose eggs | same | sr_legacy 172190 "Egg, goose, whole, fresh, raw" | same |
| quail eggs | same | sr_legacy 172191 "Egg, quail, whole, fresh, raw" | same |
| turkey eggs | same | sr_legacy 172192 "Egg, turkey, whole, fresh, raw" | same |

No row is NAMED. Held (not rows): human milk, instant dry milk. Not changed: milk-powder behaviour (existing route, no row), synonyms, species constants (`_MILK_TERMS`, `_MILK_POWDER_ROWS`, `_MILK_POWDER_WORDS`), milk/egg powder exceptions, yoghurt, any classifier code. The fruit/flavoured-yoghurt bookkeeping in the review is not a classifier rule and is not used here.

## 2. Gates (committed tree vs main 46ad81c; separate fresh processes)
| check | result |
|---|---|
| lexicon | 406 -> 411 (+5 whole_food rows; none changed or removed); synonyms.csv, markers.csv byte-identical; no source file changed |
| frozen 66 / out-of-sample 32 | changed 0 / 0 (no label holds these terms); unexplained 0; abstain->4 0 |
| drift (556) | 0 differences |
| salted (147) / descriptor (812) / powder (558) surfaces (base rows) | 0 changed |
| existing controls (milk, eggs, egg, buffalo/cow/goat milk, milk solids, dahi, milk powder forms) | unchanged before vs after |
| suite | 1697 passed, 5 xfailed (one species test list edited with an explanation: 'Sheep Milk' leaves the unrecognised list) |
| parity | 750/750 identical (additions-only, +12 inputs) |

## 3. Measured forms of the five new rows (identical for all five unless noted; before = unrecognised)
| form | result | form | result |
|---|---|---|---|
| X | 1 | X (cow milk) / X (sheep) / X (XQ9) | abstain |
| X, salt / X, sugar / X, salt, sugar | 3 | Rice, X / X, rice / X, milk / X, eggs | abstain |
| **salted X / X (salted)** | **1** | X, starter culture | abstain |
| **X (sugar)** | **1** | roasted X / dried X | 1 |
| sugared X / toasted X | abstain | X (pasteurized) / (raw) / (boiled) | 1 |
| **X (canned) / (brine) / (preserved) / (sunflower oil)** | **1** | X powder | abstain |
| 100% X powder | 1 | whole X powder | 1 for the four egg rows; abstain for sheep milk ('whole' is not read for milk) |
| duck egg, goose egg, quail egg, turkey egg (singular) | 1 | | |

Compared with the same forms on existing rows (milk, eggs, egg, buffalo/cow/goat milk, milk solids, dahi) the new rows behave identically; the bold cells already hold on main for `Milk` and `Eggs`, so they are existing holes now reaching five more terms: added salt through the descriptor or bracket (`Salted Milk`, `Salted Egg`: parked), sugar inside a bracket, and canned/brine/preserved/oil in a bracket (the legume/vegetable/fruit/nut guards do not apply to `whole_food`; only the 23 grain/flour terms have a salted guard).

Also measured: `rice (sheep milk)`, `egg (duck eggs)` and `milk (sheep milk)` answer **1** after the change (before: abstain, the nested name was unrecognised). A recognised food inside another item's bracket is a benign bracket part under the existing rule (`rice (egg)` and `rice (eggs)` answer 1 on main today). Reported, not changed.

## 4. Gaps and decisions for the owner (nothing changed here)
1. Salted/sugared/canned/brined/oiled whole_food forms of milk and eggs answer Group 1 or ignore the added substance (existing holes; the parked `Salted Milk`/`Salted Egg` decision and a possible whole_food condition guard).
2. A recognised food in another item's bracket is benign (`rice (sheep milk)` -> 1): existing behaviour that adding any row widens.
3. `sheep milk powder` and `milk (sheep)` abstain until the species constants are extended (separate engine item; not done).
4. Egg powder: `100% X powder` and `whole X powder` give Group 1 under the powder standard; the bare `X powder` abstains. No egg-powder exception exists.

## 5. Exact diff vs main 46ad81c
`data/ingest/dairy_rows_1.json`, `evaluation/dairy_rows_1/{README.md,applied_gate/applied_gate.json}`, `scripts/parity_check.py` (+12 inputs), `src/foodscan/resources/lexicon.csv` (+5 rows), `tests/test_dairy_rows_1.py` (new), `tests/test_species_milk_2b.py` (list edit with comment, one new test).
