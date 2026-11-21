# fats_rows_1: twenty culinary rows, 19 oils and lard (PROPOSAL; staging only, merge stops with the owner)

Branch claude/fats-rows-1 (off main cf06f63; main 342e662, the whole-food guard included, merged in, no rebase). Input: junior branch antigravity/class-bulk-7-fats-oils (1b015d2), senior review `evaluation/junior_reviews_4/07_fats_oils_review.md` (claude/junior-reviews-4, d016ead). Decision reference: owner instruction 2026-11-21 (narrow fats staging; nutmeg butter and ucuhuba butter excluded pending evidence of culinary identity).

## 1. Rows (existing kind `culinary`; text in the lexicon `source` column; 24 FDC records, `staged_rows.csv`)
| term | clause (FAO 2019 ca5644en Table 1 Group 2, p.11, verified verbatim) | inference level |
|---|---|---|
| almond, hazelnut, walnut, babassu, sheanut oil | "Vegetable oils crushed from seeds, nuts or fruit (notably olives)" | class-instance of vegetable oils (nuts) |
| apricot kernel, palm kernel oil | same | class-instance (oil from the kernel, the seed of the fruit) |
| avocado oil | same | class-instance (fruit) |
| canola, cupuassu, flaxseed, grapeseed, poppyseed, safflower, teaseed, tomatoseed oil | same | class-instance (seeds) |
| corn oil, wheat germ oil, oat oil | Group 2 definition: "Substances obtained directly from group 1 foods or from nature by industrial processes such as pressing, centrifuging, refining, extracting or mining. Used to prepare, season and cook group 1 foods." | class-instance of the general definition, not of the example list |
| lard | "butter and lard obtained from milk and pork"; section 2 p.9 "Processed culinary ingredients include oils, butter, lard, sugar and salt." | exact-named |
No row is purity-claiming (FDC names only 'Oil, X'); none is NAMED beyond lard. The olive-oil wording is unchanged (existing row). Excluded/held: nutmeg butter, ucuhuba butter; the five industrial/brand records (171042, 171438, 171439, 172357, 171033); synonym candidates; animal fats other than lard; fish oils. Canonical count after source-grounded dedup: 20 (19 oils + lard), as expected.

## 2. Gates (committed tree vs main 342e662; separate fresh processes)
| check | result |
|---|---|
| lexicon | 406 -> 426 (+20 culinary rows; none changed or removed); synonyms.csv, markers.csv byte-identical; no code change |
| frozen 66 | changed 0; unexplained 0; abstain->4 0 |
| out-of-sample 32 | changed 1: S01 (pasta salad label): 'canola oil' moves from the Not-assessed list to recognised, reason text changes, group stays abstain; attributed to the row `canola oil`; unexplained 0; abstain->4 0 |
| drift (556) | 0 differences |
| salted (147) / descriptor (812) / powder (558) surfaces | 0 changed |
| after-build proof | all 20 rows recognised after, none before |
| suite | **1886 passed, 5 xfailed** (earlier 1825 is stale: it predates the nut and whole-food merges) |
| parity | **807/807** identical (main 789 + 18 added entries, 0 removed; reason and driver compared; earlier 778 is stale) |

## 3. Measured forms (20 new rows vs 14 existing oil/fat rows; before = unrecognised for new rows)
| form | new rows | existing rows (unchanged) |
|---|---|---|
| X | 2 | 2 |
| hydrogenated / partially hydrogenated / fully hydrogenated / interesterified X, X (hydrogenated) | 4 | 4 |
| X spray, X blend, X (antioxidant), X (INS 319), oil, X, cooking X | abstain | abstain |
| roasted/refined/cold pressed/extra virgin X, unsalted X | 2 | 2 |
| salted X, X (salted), X (sugar), X (canned) | 2 | 2 |
| **X (XQ9)** | **2** | **2** |
| **X powder, 100% X powder** | **2** | 2 (13 of 14; one abstains) |
| Rice, almond oil; Milk, lard; Walnuts, walnut oil | 3 | n/a (food plus oil list) |
| Walnuts (walnut oil), Cashew Nuts (walnut oil), Almonds (almond oil) | 3 (before: abstain, the oil was unrecognised) | Sesame Seeds (sesame oil): 3 before and after |
| lard, salt; corn oil, canola oil; wheat flour, lard, salt | abstain | as before |
| **Corn and canola oil** | **3 (before: abstain)** | |
| nutmeg butter, ucuhuba butter, shea butter, rapeseed oil, maize oil, industrial canola oil, natreon canola oil, beef tallow, fish oil, pork fat, animal fat, shortening, margarine | unrecognised | |

## 4. Gaps widened by recognition (reported; nothing changed here, no engine edit in this batch)
1. **Unknown bracket on a culinary row answers Group 2** (`Corn Oil (XQ9)`): the unrecognised-bracket guard covers legume, vegetable, fruit, flour, whole_food and nut kinds, not `culinary`. Predates the batch (`Sunflower Oil (XQ9)` -> 2 on main) and now applies to 20 more terms.
2. **Oil powders answer Group 2** (`Corn Oil Powder`): powder routing excludes `culinary`; an oil powder is usually encapsulated on a carrier. Existing hole, now wider.
3. **'X and Y oil' is split at 'and'** (`Corn and Canola Oil` -> Group 3 'recognised whole food': corn plus canola oil, before abstain). A blend of oils is read as a food plus an oil. The same on main for 'corn and sunflower oil'; the new rows make more blends answer. Owner decision: an and-split guard for oil names, or accept.
4. `Salted X`, `X (sugar)`: Group 2 plus group 2 is Group 2 under the clause ('products consisting of group 2 items'), so these are not unsupported; `X (canned)` is not a meaningful oil form.
These three are candidates for a separate engine proposal; the rows themselves are source-supported.

## 5. Exact diff vs main 342e662
- `data/ingest/fats_rows_1.json`
- `data/ingest/whole_food_guard_1.json`
- `evaluation/fats_rows_1/README.md`
- `evaluation/fats_rows_1/applied_gate/applied_gate.json`
- `evaluation/fats_rows_1/staged_rows.csv`
- `evaluation/whole_food_guard_1/README.md`
- `evaluation/whole_food_guard_1/applied_gate/applied_gate.json`
- `evaluation/whole_food_guard_1/overlay_dairy_gate/applied_gate.json`
- `evaluation/whole_food_guard_1/overlay_five_rows_forms.json`
- `scripts/parity_check.py`
- `src/foodscan/classify.py`
- `src/foodscan/resources/lexicon.csv`
- `tests/test_dairy_abstentions.py`
- `tests/test_fats_rows_1.py`
- `tests/test_salted_grain_guard.py`
- `tests/test_sweetener_foods_note.py`
- `tests/test_thickener_emulsifying_salt_markers.py`
- `tests/test_vocab_gap_and_soybean.py`
- `tests/test_whole_food_guard_1.py`
- `web_preview/foodscan.js`
