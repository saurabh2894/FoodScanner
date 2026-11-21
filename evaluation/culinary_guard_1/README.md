# culinary_guard_1: unknown-bracket, oil-powder and 'A and B oil' abstentions for oil and fat rows (PROPOSAL; merge stops with the owner)

Branch claude/culinary-guard-1 (off main 0810267; main 625f0fa, with the tea and coffee rows, merged in, no rebase). Decision reference: owner instruction 2026-11-21 (conservative scoped proposal before fats integration; fats-rows-1 3bf0ed2 stays held and untouched). Abstention only: no group is guessed for carrier-containing oil powders or ambiguous blends; no row, synonym, marker or lexicon change.

## 1. Change (`classify.py`, `pipeline.py`, mirrored in `foodscan.js`)
1. **Unknown bracket on an oil or fat row.** An oil/fat row is a `culinary` row whose last word is oil, fat, butter, ghee, lard, palmolein or olein, or one of the generic rows `refined oil`, `edible vegetable oil`, `vegetable oil` (`is_fat_row`). A bracket part that is unrecognised abstains ("a bracket on a processed culinary ingredient names content the vocabulary does not recognise (...), so what the item contains is not established and no group is asserted while part of the item is unassessed"; kind-neutral wording in a mixed list; existing texts for other kinds unchanged). Supported, so not residual: a part that names the source of a recognised oil (`Edible Vegetable Oil (palm, coconut)`: palm oil and coconut oil are rows) and a part that itself ends in 'oil' or 'fat' (`Sesame Oil (Gingelly Oil)`: any oil is a group 2 substance, nothing but another oil can hide there; hydrogenation is read by the markers). Other culinary rows (salt, sugar, vinegar, jaggery, honey, starch) are NOT touched: `Salt (XQ9)` and `Sugar (Cane)` still answer Group 2 (the broader culinary question stays parked).
2. **Oil and fat powders.** `X powder` / `X (powder)` on an oil or fat row abstains ("a powder of an oil or fat is named (...): oil powders are commonly made on a carrier such as a starch or maltodextrin, so the composition is not established and no group is asserted unless the item states 100%"). A stated `100% X powder` stays Group 2. Jaggery, sugar and other non-fat powders are unchanged.
3. **'A and B oil'.** `Corn and Canola Oil` splits at 'and' into the food corn plus the oil canola oil (Group 3). When the second part is an oil/fat row and the first part followed by 'oil' or 'fat' is also an oil/fat row, the phrase names two oils and the positive composition is not established: it is kept whole and abstains ("not in the local vocabulary", as any unrecognised item). `Rice and Sunflower Oil` ('rice oil' is no row) remains food plus oil (Group 3); comma lists are untouched.
Source: none new; Group 2 placement of a plain oil is unchanged. The proposal withholds answers, it adds none.

## 2. Gates (committed tree vs main 625f0fa; separate fresh processes)
| check | result |
|---|---|
| lexicon / synonyms / markers / descriptors | 413 -> 413, nothing changed |
| frozen 66 / out-of-sample 32 | changed 0 / 0; unexplained 0; abstain->4 0 |
| drift (563) | 0 differences |
| salted (168) / descriptor (826) / powder (579) surfaces | 0 changed |
| overlay: this branch + the 20 staged fats rows (`overlay_fats_gate/`) | frozen 66 changed 0; out-of-sample 32 changed 1: S01 (canola oil unassessed -> recognised, group stays abstain, attributed to the row); drift 0; surfaces 0 changed |
| suite | **1938 passed, 5 xfailed** (main 1884 + 54 new tests) |
| parity | **832/832** identical (main 816 + 16 added entries, 0 removed; reason and driver compared) |

## 3. Measured behaviour (`applied_gate.json` controls; before -> after; committed tree, 20 existing oil/fat rows, then the overlay with 20 more)
| form | existing 20 rows | overlay: +20 staged rows (before = unrecognised) |
|---|---|---|
| X; refined/cold pressed X; salted X; X (sugar); X (canned) | 2 -> 2 | 2 |
| X (palm, coconut); X (gingelly oil) | 2 -> 2 | 2 |
| **X (XQ9); X (oryzanol)** | **2 -> abstain** | abstain |
| X (INS 319); X (antioxidant); X spray; X blend | abstain -> abstain | abstain |
| hydrogenated, partially hydrogenated, interesterified X; X (hydrogenated) | 4 -> 4 | 4 |
| **X powder; X (powder)** | **2 -> abstain** (19 rows; the 20th already abstained) | abstain |
| 100% X powder | 2 -> 2 | 2 |
| Rice, X; X, rice; Rice and X; Potato, X, salt; Walnuts (X); Almonds, X; Sesame Seeds (X); Milk, X; Eggs and X | 3 -> 3 | 3 |
| **Soybean and X** (soybean oil is a row) | **3 -> abstain** | abstain |
| **Corn and X** | 3 -> 3 (corn oil is not a row on main) | **3 -> abstain** |
| X and Palm Oil; Sunflower Oil and X; Salt and X; Wheat Flour and X; Rice (X) | abstain -> abstain | abstain |
Phrases: `Corn and Canola Oil` abstain (overlay) ; `Corn and Sunflower Oil` 3 -> 3 on main, 3 -> abstain with the fats rows; `Soybean and Palm Oil` 3 -> abstain; `Sesame and Sunflower Oil` abstain; `Rice and Sunflower Oil` 3 -> 3; `Edible Vegetable Oil (palm, coconut)` 2 -> 2; `Edible Vegetable Oil (corn, canola)` 2 -> abstain on main (corn and canola are not rows yet), 2 -> 2 with the fats rows; `Jaggery Powder`, `Sugar Powder`, `Salt (Iodised)`, `Sugar (Cane)`, `Salt (XQ9)`, `Vinegar (XQ9)` unchanged (Group 2).

## 4. Explained changes and limits
1. Every flip is Group 2 or 3 -> abstain, none to a new group. Unknown or additive-like brackets on oils (`XQ9`, `oryzanol`) and oil powders are the withheld answers; 'A and B oil' blends are the third.
2. `Sunflower Oil (XQ9 Oil)` still answers Group 2 (an unknown oil is an oil). A bracket mixing a source word and unknown content abstains.
3. The and-split guard keys on rows: on main today it covers blends whose first word already has an oil row (soybean, sunflower, sesame, mustard, coconut, palm, peanut, groundnut, olive, cottonseed, rice bran); `Corn and Sunflower Oil` stays a wrong Group 3 on main until the fats rows (corn oil and the others) land, and is then withheld.
4. Not changed: salt, sugar, vinegar, jaggery and other culinary rows; `X (sugar)` and `Salted X` on oils (Group 2 plus group 2 is Group 2 under the clause 'products consisting of group 2 items'); powder routing for other kinds; the word guard for oil words.
5. Genuine food plus oil (comma lists, `Rice and Sunflower Oil`) and explicit hydrogenation remain as before.

## 5. Tests
`tests/test_culinary_guard_1.py` (new, 54 cases): the 16 existing oil/fat rows plain, hydrogenated and interesterified; unknown brackets; supported source and oil-name brackets; powders and 100%; other culinary rows untouched; two-oil phrases kept whole; food plus oil lists; and a subprocess overlay of the 20 staged fats rows on a copy of the lexicon.

## 6. Exact diff vs main 625f0fa (9 paths, `git diff --name-only main HEAD` on the committed merge tree)
- `data/ingest/culinary_guard_1.json`
- `evaluation/culinary_guard_1/README.md`
- `evaluation/culinary_guard_1/applied_gate/applied_gate.json`
- `evaluation/culinary_guard_1/overlay_fats_gate/applied_gate.json`
- `scripts/parity_check.py`
- `src/foodscan/classify.py`
- `src/foodscan/pipeline.py`
- `tests/test_culinary_guard_1.py`
- `web_preview/foodscan.js`
