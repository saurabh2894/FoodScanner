# culinary_guard_1: bracket-content and powder abstentions for oil and fat rows, and 'A and B oil' (PROPOSAL, revision 2; merge stops with the owner)

Branch claude/culinary-guard-1 (off main 0810267; main 625f0fa merged in, no rebase). Decision reference: owner review 2026-11-21 of 2be1c41 (four corrections); fats-rows-1 3bf0ed2 stays held and untouched. Abstention only: no group is guessed; no row, synonym, marker or lexicon change.

## 1. Change (`classify.py`, `pipeline.py`, mirrored in `foodscan.js`)
Oil/fat rows (`is_fat_row`): `culinary` rows whose last word is oil, fat, butter, ghee, lard, palmolein or olein, or the generic rows `refined oil`, `edible vegetable oil`, `vegetable oil`. On main 625f0fa the lexicon holds exactly **20** such rows (edible vegetable oil, ghee, mustard oil, sunflower oil, groundnut oil, coconut oil, rice bran oil, butter, palm oil, palmolein, soybean oil, sesame oil, olive oil, cottonseed oil, vegetable oil, peanut oil, coconut fat, cocoa butter, refined oil, butter oil); the revision-1 tests covered 16 of them, revision 2 covers all 20.
1. **Bracket content must establish a culinary-only composition.** Revision 1 exempted any part ending in 'oil' or 'fat'; that is removed (a suffix is not an identity, and no alias is assumed). A bracket part is supported only if it is (a) the source word of a recognised oil ('palm', 'coconut', 'corn' when 'corn oil' is a row: checked first, so a bare word that is also a food row still counts as an oil source), (b) a recognised culinary row (another oil, salt, sugar, a starch: group 2 items), or (c) a descriptor, condition, negation, connector or code word already benign for every kind. Everything else abstains: unrecognised parts (`XQ9`, `XQ9 Oil`, `XQ9 Carrier Oil`, `Mineral Oil`, `Essential Oil`, `XQ9 Fat`, `Gingelly Oil`, `oryzanol`), **and recognised parts that are not culinary rows** (`Rice`, `Milk`, `Sugar, Rice`), which revision 1 ignored. Nested or mixed content (`Refined (XQ9), Palm`) abstains. Reason: "a bracket on a processed culinary ingredient names content that is unrecognised or is a different food, not a culinary ingredient (...), so what the item contains is not established and no group is asserted while part of the item is unassessed".
2. **Oil and fat powders.** A named powder abstains: "a powder of an oil or fat is named (...): a powder is named but its composition is not established, so no group is asserted unless the item's own name states 100%" (the unsupported carrier claim of revision 1 is removed). `powder_composition_stated` reads a 100% anywhere in the item, so it is not used here: `fat_powder_stated` reads the 100% only OUTSIDE any bracket. Bracket content is evaluated first, so a 100% never overrides it: `100% X Powder (Rice)` and `100% X Powder (XQ9 Oil)` abstain; `X Powder (100% Starch)` abstains (the 100% belongs to the bracket).
3. **'A and B oil'** (unchanged from revision 1): when the second part is an oil/fat row and the first part plus 'oil' or 'fat' is also an oil/fat row, the phrase is kept whole and abstains; `Rice and Sunflower Oil` stays food plus oil (Group 3). The disclosed limit stands and is held conservatively: `Corn and Sunflower Oil` is a wrong Group 3 on main until the fats rows add 'corn oil'; no food identity is invented.
Marker precedence is untouched: `Hydrogenated X`, `X (hydrogenated)`, interesterified forms stay Group 4 even with unknown or distinct-food brackets.

## 2. Gates (committed tree vs main 625f0fa; separate fresh processes)
| check | result |
|---|---|
| lexicon / synonyms / markers / descriptors | 413 -> 413, nothing changed |
| frozen 66 / out-of-sample 32 | changed 0 / 0; unexplained 0; abstain->4 0 |
| drift (563) | 0 differences |
| salted (168) / descriptor (826) / powder (579) surfaces | 0 changed |
| overlay: this branch + the 20 staged fats rows (`overlay_fats_gate/`) | frozen 66 changed 0; out-of-sample 32 changed 1: S01 (canola oil unassessed -> recognised, group stays abstain; attributed to the row); drift 0; surfaces 0 changed |
| suite | **1966 passed, 5 xfailed** (main 1884 + 82 new tests; one existing harness test updated, section 5) |
| parity | **841/841** identical (main 816 + 25 added entries, 0 removed; reason and driver compared) |

## 3. Measured before -> after (`applied_gate.json` controls, 29 forms; existing 20 rows, then the overlay with the 20 staged rows added; before = main, unrecognised for staged rows)
| form | existing 20 rows | overlay, +20 staged rows |
|---|---|---|
| X | 2 -> 2 | 2 |
| X (XQ9), (oryzanol), (XQ9 oil), (XQ9 carrier oil), (mineral oil), (essential oil), (XQ9 fat), (gingelly oil) | **2 -> abstain** (all 20) | abstain |
| X (rice), X (milk), X (sugar, rice), X (refined (XQ9), palm) | **2 -> abstain** | abstain |
| X (corn) | **2 -> abstain** ('corn oil' is not a row on main) | 2 (corn oil is a staged row) |
| X (starch), X (palm, salt), X (palm, coconut), X (sugar) | 2 -> 2 (culinary-only content) | 2 |
| X powder; X (powder) | **2 -> abstain** (19 rows; one already abstained) | abstain |
| 100% X powder; 100% X powder (palm) | 2 -> 2 | 2 |
| 100% X powder (rice); 100% X powder (XQ9 oil); X powder (100% starch); X powder (starch) | **2 -> abstain** | abstain |
| hydrogenated X; hydrogenated X (rice); hydrogenated X (XQ9); X (hydrogenated) | 4 -> 4 | 4 |
Existing rows keep Group 2 only where the bracket is supported culinary content (a starch, salt, sugar, an oil source). `X (starch)` and `X (sugar)` stay Group 2 because starch and sugar are group 2 items (clause: 'products consisting of group 2 items'); the owner's examples with a distinct food (`Rice`, `Milk`, `Sugar, Rice`) now abstain.
Phrases and lists (unchanged from revision 1): `Soybean and Palm Oil` 3 -> abstain; `Corn and Canola Oil` abstain (overlay); `Corn and Sunflower Oil` 3 -> 3 on main, 3 -> abstain with the fats rows; `Rice and Sunflower Oil`, `Rice, Sunflower Oil`, `Potato, Edible Vegetable Oil (palm, coconut), Salt`, `Walnuts (Sunflower Oil)` stay Group 3; `Edible Vegetable Oil (palm, coconut)` stays 2; `Edible Vegetable Oil (corn, canola)` 2 -> abstain on main, 2 with the fats rows; `Sesame Oil (Gingelly Oil)` 2 -> abstain (no alias is known); `Jaggery Powder`, `Sugar Powder`, `Salt (Iodised)`, `Sugar (Cane)`, `Salt (XQ9)`, `Vinegar (XQ9)` unchanged (Group 2).

## 4. Attribution
Every flip is Group 2 (or Group 3 for blends) -> abstain, none to a new group: unrecognised bracket content, recognised distinct-food bracket content, named oil powders, and the two-oil phrase. S01 in the overlay is the staged row `canola oil`, not this guard. No frozen label contains one of these forms.

## 5. Tests
`tests/test_culinary_guard_1.py` (82 cases): all 20 existing oil/fat rows plain and hydrogenated; unrecognised and `oil`/`fat`-suffix brackets abstain; recognised distinct foods abstain and culinary-only content stays 2; no alias for gingelly or til oil; marker precedence; powders with 100% inside and outside brackets; other culinary rows untouched; two-oil phrases; food plus oil lists; and a subprocess overlay of the 20 staged fats rows on a copy of the lexicon. `tests/test_validate_batch.py::test_flip_harness_detects_and_blocks_a_group_flip` is updated with an explanation: the frozen b1/N10 list holds `Sesame Oil (Gingelly Oil)`, which now needs 'gingelly oil' staged as well as 'synthetic vinegar' to flip None -> 3 (the harness purpose is unchanged).

## 6. Exact diff vs main 625f0fa (10 paths, `git diff --name-only main HEAD` on the committed tree)
- `data/ingest/culinary_guard_1.json`
- `evaluation/culinary_guard_1/README.md`
- `evaluation/culinary_guard_1/applied_gate/applied_gate.json`
- `evaluation/culinary_guard_1/overlay_fats_gate/applied_gate.json`
- `scripts/parity_check.py`
- `src/foodscan/classify.py`
- `src/foodscan/pipeline.py`
- `tests/test_culinary_guard_1.py`
- `tests/test_validate_batch.py`
- `web_preview/foodscan.js`
