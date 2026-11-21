# fats_rows_1: twenty culinary rows, 19 oils and lard (PROPOSAL; staging only, merge stops with the owner)

Branch claude/fats-rows-1 (off main cf06f63; main bbc54e3, with the whole-food guard, dairy, tea/coffee rows and the culinary guard, merged in, no rebase). Refreshed after the culinary guard merged; no merge until reviewed. Input: junior branch antigravity/class-bulk-7-fats-oils (1b015d2), senior review `evaluation/junior_reviews_4/07_fats_oils_review.md` (claude/junior-reviews-4, d016ead). Decision reference: owner instruction 2026-11-21 (narrow fats staging; nutmeg butter and ucuhuba butter excluded pending evidence of culinary identity).

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

## 2. Gates (committed tree vs main bbc54e3, the whole-food and culinary guards included; separate fresh processes)
| check | result |
|---|---|
| lexicon | 413 -> 433 (+20 culinary rows; none changed or removed); synonyms.csv, markers.csv, descriptors.csv byte-identical; no code change |
| frozen 66 | changed 0; unexplained 0; abstain->4 0 |
| out-of-sample 32 | changed 1: S01 (pasta salad label): 'canola oil' moves from the Not-assessed list to recognised, reason text changes, group stays abstain; attributed to the row `canola oil` |
| drift (563) | 0 differences |
| salted (168) / descriptor (826) / powder (579) surfaces | 0 changed |
| after-build proof | all 20 rows recognised after, none before |
| suite | **2042 passed, 5 xfailed** (main 1966 + 76 fats tests; one fats test updated, explained) |
| parity | **859/859** identical (main 841 + 18 added entries, 0 removed; reason and driver compared) |

## 3. Measured forms of the 20 new rows (before = unrecognised; the culinary guard is now in the base; identical for all 20 unless noted)
| form | result | form | result |
|---|---|---|---|
| X; roasted/refined/cold pressed/extra virgin/unsalted X | 2 | hydrogenated, partially or fully hydrogenated, interesterified X; X (hydrogenated) | 4 |
| salted X; X (salted); X (sugar); X (canned) | 2 (group 2 plus group 2 items; unchanged rule) | X spray; X blend; X (antioxidant); X (INS 319); oil, X; cooking X | abstain |
| **X (XQ9)** | **abstain** (was 2 before the guard) | **X powder** | **abstain** (was 2) |
| 100% X powder | 2 | Rice, X; Rice and X; Milk, lard; Walnuts (walnut oil); Rice, almond oil | 3 |
| **Corn and Canola Oil** | **abstain** (was 3) | Corn and Sunflower Oil | abstain (was 3 on main until these rows) |
| nutmeg butter, ucuhuba butter, shea butter, rapeseed oil, maize oil, industrial or Natreon canola oil, beef tallow, fish oil, pork fat, animal fat, shortening, margarine | unrecognised | | |
The three holes the first version of this proposal reported (unknown bracket on a culinary row, oil powders, 'X and Y oil' read as food plus oil) are closed by the merged culinary guard for these rows; they do not widen. Salted, sugared and canned oils stay Group 2 by the 'products consisting of group 2 items' clause.

## 4. Remaining notes
1. Other culinary rows (salt, sugar, vinegar, jaggery) keep their unknown-bracket behaviour (parked, not a blanket fix).
2. `Corn and Sunflower Oil`-style blends are withheld only when both halves are oil rows.

## 5. Exact diff vs main bbc54e3 (7 paths, `git diff --name-only main HEAD` on the committed merge tree)
- `data/ingest/fats_rows_1.json`
- `evaluation/fats_rows_1/README.md`
- `evaluation/fats_rows_1/applied_gate/applied_gate.json`
- `evaluation/fats_rows_1/staged_rows.csv`
- `scripts/parity_check.py`
- `src/foodscan/resources/lexicon.csv`
- `tests/test_fats_rows_1.py`
