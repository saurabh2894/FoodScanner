# dairy_rows_1: five whole_food rows (PROPOSAL, refreshed onto main 342e662; staging only, merge stops with the owner)

Branch claude/dairy-rows-1 (originally off 46ad81c; main merged in, no rebase, no force-push). Input: junior branch antigravity/class-bulk-6-dairy (bbc0fb8), senior review `evaluation/junior_reviews_3/06_dairy_review.md` (claude/junior-reviews-3). Decision reference: owner instruction 2026-11-21 (narrow dairy proposal, exactly five rows; refresh after the whole-food guard).

## 1. Rows (kind whole_food; text in the lexicon `source` column; controls in `data/ingest/dairy_rows_1.json`)
| term | clause (FAO 2019 ca5644en Table 1 Group 1, p.11, verified verbatim) | FDC record (naming and plain-form evidence only) | inference level |
|---|---|---|---|
| sheep milk | definition "...or of or from animals (muscle, fat, offal, eggs, milk)..."; example "fresh, powdered or pasteurized milk" | sr_legacy 170882 "Milk, sheep, fluid" | class-instance of the animal milk named by FAO; species not named by any NOVA source read (same level as goat milk) |
| duck, goose, quail, turkey eggs | same definition; example "fresh, powdered, chilled or frozen eggs" | sr_legacy 172189, 172190, 172191, 172192 ("Egg, <species>, whole, fresh, raw") | class-instance of the eggs named by FAO |
No row is NAMED. Held, not rows: human milk, instant dry milk. Not changed: milk-powder behaviour, synonyms, species constants (`_MILK_TERMS`, `_MILK_POWDER_ROWS`, `_MILK_POWDER_WORDS`), milk/egg powder exceptions, yoghurt, any classifier code. The fruit/flavoured-yoghurt bookkeeping in the review is not used.

## 2. Gates (committed tree vs main 342e662, the whole-food guard included; separate fresh processes)
| check | result |
|---|---|
| lexicon | 406 -> 411 (+5 whole_food rows; none changed or removed); synonyms.csv, markers.csv byte-identical; no source file changed |
| frozen 66 / out-of-sample 32 | changed 0 / 0; unexplained 0; abstain->4 0 |
| drift (556) | 0 differences |
| salted (147) / descriptor (812) / powder (558) surfaces (base rows) | 0 changed |
| existing controls (milk, eggs, egg, buffalo/cow/goat milk, milk solids, dahi, milk powder forms) | unchanged before vs after |
| suite | **1833 passed, 5 xfailed** (main 1810 + 23 new dairy tests; one species test list edited with an explanation) |
| parity | **801/801** identical (main 789 + 12 added entries, 0 removed; reason and driver compared). The earlier figures 1697 and 750 are stale (they predate the guard and the nut merge) and are withdrawn |

## 3. Measured forms of the five new rows (identical for all five unless noted; before = unrecognised; the whole-food guard is now in the base)
| form | result | form | result |
|---|---|---|---|
| X; roasted X; dried X; unsalted X; X (pasteurized) / (raw) / (boiled) | 1 | X (cow milk), X (sheep), X (XQ9) | abstain |
| X, salt; X, sugar; X, salt, sugar | 3 | Rice, X; X, rice; X, milk; X, eggs; X, cow milk; X, starter culture | abstain |
| salted X; X (salted); sugared X | abstain | X (sugar); X (canned); X (brine); X (preserved); X (sunflower oil) | abstain |
| toasted X; X powder | abstain | 100% X powder | 1 |
| duck egg, goose egg, quail egg, turkey egg (singular) | 1 | whole X powder | 1 for the four egg rows; abstain for sheep milk |
Distinct-food and held forms: `rice (sheep milk)`, `egg (duck eggs)`, `milk (sheep milk)` abstain (before: abstain for the unrecognised name; the pre-guard run had shown them answering Group 1). Human milk, instant skimmed milk powder, sheep, duck, egg powder, plain yoghurt, sheep cheese, duck egg yolk, sheep milk solids, fortified sheep milk powder stay unrecognised or abstain.
With the guard in the base, the holes the earlier version of this proposal reported (salted, sugared, canned, brined, oiled forms and a recognised nested food answering Group 1) do not widen: they abstain. The full five-row x 40-form measurement (including `Milk (X)`, `Eggs (X)`, `Rice (X)`) is `evaluation/whole_food_guard_1/overlay_five_rows_forms.json`, Python and JS identical.

## 4. Remaining items for the owner (nothing changed here)
1. `Salted Milk`/`Salted Egg` Group 3 stays an open decision (the guard abstains).
2. `sheep milk powder` and `milk (sheep)` abstain until the species constants are extended (separate engine item); `Milk (Sheep Milk)` and `Eggs (Duck Eggs)` abstain (no listed equivalence).
3. Egg powder: `100% X powder` and `whole X powder` give Group 1 under the powder standard; the bare `X powder` abstains. No egg-powder exception exists.

## 5. Exact diff vs main 342e662
- `data/ingest/dairy_rows_1.json`
- `evaluation/dairy_rows_1/README.md`
- `evaluation/dairy_rows_1/applied_gate/applied_gate.json`
- `scripts/parity_check.py`
- `src/foodscan/resources/lexicon.csv`
- `tests/test_dairy_rows_1.py`
- `tests/test_species_milk_2b.py`
