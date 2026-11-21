# integration_1: reviewed parser, headline and animal changes on one tree (READY FOR REVIEW; NOT merged to main, not deployed)

Branch claude/integration-1 from origin/main a6cacbc00fe3f8543a78f002b952a9a64375c4fd (verified unchanged at the start). Merged, in this order, with no other branch: label-parser-16-senior 0c482d19ea173a7a99e5f8dfa50a028a7a18720d, headline-aggregation-1 6820a5c0413770910d6c9419c223dcff89a0789b, animal-fish-rows-1 e43601ef774f49d0b156a78a3958ad42ce940875 (which includes animal-guard-1 658c0e966672d56e2c7235b5068673de86738013). NOT included: Task 17 photo-UI branch, Task 15 prose, junior branches. Tip SHA: see the git log of this branch (the README is committed before the final status commit).

## 1. Conflicts and how they were resolved
- `scripts/parity_check.py` (corpus additions at the same anchor, twice): resolved by keeping both sides. Verified on the ACTUAL texts, not the count: the integration CORPUS is the multiset union of origin/main plus each branch's additions (12 parser + 16 headline + 34 animal/fish entries, 841 entries, no missing, no extra; PASTE list identical to main). Parity entries 859 + 62 = 921.
- `classify.py` and `foodscan.js` merged without textual conflict; the headline aggregation (`other_open_items`) and the scoped animal guard (`animal_dried`, `animal_dried_unscoped`, `animal_powder`) are both present and exercised by the tests and parity.
- `lexicon.csv`: git reports 76 insertions and 0 deletions against main; `synonyms.csv`, `markers.csv`, `descriptors.csv` show no diff.

## 2. Gates (fresh processes; committed tree vs main a6cacbc)
| check | result |
|---|---|
| lexicon | 433 -> 509 = old 433 rows unchanged + the 76 reviewed candidates (8 meat + 68 fish; labels equal the review table, no duplicates); synonyms, markers, descriptors unchanged |
| suite | **2357 passed, 5 xfailed** (full suite, no test weakened or removed; every assertion change is explained in the branch it came from) |
| parity | **921/921** identical (reason and driver compared; 843 photo-path texts, 78 pasted-text texts) |
| frozen 66 | changed 6, all reason text only (b1/N07, b1/N11, b3/Q11, neg/R1, dev/F10, dev/F11: headline aggregation), group and status unchanged; unexplained 0; abstain->4 0 |
| out-of-sample 32 | changed 5, no group change: S08, S11 (headline reason), S13 and S16 (parser: bracket `and` pair and organic-asterisk items recognised), S18 (`Lamb (33%)`: lamb recognised, group 4 unchanged); unexplained 0 |
| drift (583) / descriptor (866) / salted (168) / powder (579) | 0 differences / 0 / 0 / 0 changed |
This is exactly the union of the attributed changes of the three reviewed proposals; no unexplained group flip.

## 4. Measurements on the integrated tree (Python; JS parity covers the same inputs)
**Multigrain blend (a reconstruction of the owner's label text, not the photo):** `Multigrain Blend (Sprouted Ragi & Jowar (23.4%), Wheat), Vitamins, Minerals, Date Powder, Banana Powder, Strawberry Powder, Beetroot Powder, Antioxidant (INS 320), Edible Vegetable Oil`: abstains in all three readings (literal `Vitamins#`/`Minerals##`, OCR `Vitamins<closing quote>`/`Minerals**`, marks removed). The unplaced list is Sprouted Ragi, Sprouted Jowar, Vitamins, Minerals (marks kept in the entries when literal, kept as separate entries, never merged); the group name is set aside as metadata. The headline names every active blocker: the weak antioxidant, "recognised by name only, no source read places Sprouted Ragi, Sprouted Jowar, Vitamins, Minerals" and "a powder is named and its composition is not established: Date Powder, Banana Powder, Strawberry Powder, Beetroot Powder". A real-photo end-to-end retest through the photo UI is NOT done here.
**Internal punctuation:** `Rice<closing quote> Flour`, `Sunflower<closing quote> Oil`, `Skimmed<closing quote> Milk Powder`, `Rice# Flour` abstain; `Rice* (23%)` 1; `Rice#, Sugar` 3.
**Oil blends and oils:** `Corn and Canola Oil` and `Soybean and Palm Oil` abstain; `Rice and Sunflower Oil` 3; `Sunflower Oil (XQ9)`, `Sunflower Oil (Rice)`, `Sunflower Oil Powder`, `100% Sunflower Oil Powder (Rice)` abstain.
**Animal:** `Dried Atlantic Cod`, `Dried Chilean Sea Bass`, `Dried Beef` 3; `Dried Queen Crab`, `Dried Queen Crab, Salt`, `Dried Blue Mussel, Salt`, `Dehydrated Blue Mussel` abstain (never Group 1); `Chicken Powder`, `100% Chicken Powder`, `100% Haddock Powder` abstain; `Beef (Rice)`, `Beef (Milk)`, `Salted Haddock` abstain; `Haddock, Sunflower Oil` and `Chicken, Salt` 3; `Chicken, Flavour` and `Hydrogenated Beef` 4; `Ground Beef` and `Roasted Chicken` 1; held aliases and generics (`Snow Crab`, `Spot Croaker`, `Mutton`, `Salmon`, `Fish`) unrecognised (abstain). `evaluation/integration_1/applied_gate/applied_gate.json` holds the 2267-form control measurement (old and new rows, conditioned and nested forms).

## 5. Housekeeping done here (behaviour neutral)
- The animal-guard comment in `classify.py` described every dried animal food as Group 3; it now states the scoped rule (meat and finfish rows only; other animal rows abstain).
- Branch READMEs carried a wrong date for the instruction reference; corrected to 2026-11-21.
- The gate artifact uses `data/ingest/integration_1.json` (rule_id integration-1). The earlier gates' rule_id fats-rows-1 was a harness label only, not a scientific policy; no staged rule is implied.
- The junior's stale STATUS SHA (cccb3e98, not in the repository) is reconciled in `evaluation/label_parser_16_senior/README.md`; the junior STATUS file keeps its historical text.

## 6. Exact changed paths and SHAs
Base: a6cacbc00fe3f8543a78f002b952a9a64375c4fd. Changed paths vs the base (30 paths, `git diff --name-only a6cacbc HEAD` on the committed tree before this README commit):
- `data/ingest/animal_fish_rows_1.json`
- `data/ingest/animal_guard_1.json`
- `data/ingest/integration_1.json`
- `evaluation/animal_fish_rows_1/README.md`
- `evaluation/animal_fish_rows_1/applied_gate/applied_gate.json`
- `evaluation/animal_fish_rows_1/staged_rows.csv`
- `evaluation/animal_guard_1/README.md`
- `evaluation/animal_guard_1/applied_gate/applied_gate.json`
- `evaluation/animal_guard_1/staged_rows.csv`
- `evaluation/headline_aggregation_1/README.md`
- `evaluation/headline_aggregation_1/applied_gate/applied_gate.json`
- `evaluation/integration_1/applied_gate/applied_gate.json`
- `evaluation/label_parser_16/README.md`
- `evaluation/label_parser_16/STATUS.md`
- `evaluation/label_parser_16/matrix_comparison.json.txt`
- `evaluation/label_parser_16_senior/README.md`
- `evaluation/label_parser_16_senior/applied_gate/applied_gate.json`
- `scripts/parity_check.py`
- `src/foodscan/classify.py`
- `src/foodscan/normalise.py`
- `src/foodscan/pipeline.py`
- `src/foodscan/resources/lexicon.csv`
- `tests/test_ampersand_split_1.py`
- `tests/test_animal_fish_rows_1.py`
- `tests/test_animal_guard_1.py`
- `tests/test_dairy_rows_1.py`
- `tests/test_headline_aggregation_1.py`
- `tests/test_label_parser_16.py`
- `tests/test_label_parser_16_senior.py`
- `web_preview/foodscan.js`
