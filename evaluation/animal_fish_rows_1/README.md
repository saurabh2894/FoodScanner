# animal_fish_rows_1: 68 fish and seafood rows (PROPOSAL, stacked on claude/animal-guard-1; merge stops with the owner)

Branch claude/animal-fish-rows-1 = claude/animal-guard-1 (658c0e966672d56e2c7235b5068673de86738013, the revised dried-scope guard; base main a6cacbc) plus this work (merge commit, no rebase). It cannot merge before animal-guard-1 (the rows rely on its guard). Inputs: the owner's senior review revision 2 (68 reviewed fish/seafood candidates); decision reference: owner instruction 2026-11-22, Priority 3. Candidates are not live coverage.

## 1. Rows (68, `staged_rows.csv`; kind whole_food)
Source-stated food labels, class-instance of the continuous FAO Table 1 Group 1 example "meat, poultry, fish and seafood, whole or in the form of steaks, fillets and other cuts" (never NAMED, no taxonomic resolution, no aliases, no purity or ingredient claim). Labels follow the review: `queen crab` (not snow crab), `spot` (not spot croaker), `pumpkin seed sunfish` (source spelling); `ling` and `lingcod`, `butterfish`, `monkfish`, `bluefin tuna` stay source-stated labels. Each row names its verified raw or physical-state support count and first FDC id (naming only, never placement). Generic names and aliases are NOT rows: salmon, tuna, fish, shrimp, prawn, crab, lobster, catfish, cod, pollock, halibut, tilapia, snow crab, spot croaker, pumpkinseed sunfish.

## 1a. Dried scope (owner review of animal-guard-1 6a30fe3)
The FAO Group 3 example names dried 'meats and fish', not seafood. Each row now records its scope: 56 fish labels `DRIED-G3-SCOPE: finfish` (the label is a fish; no taxonomy claim) and 12 rows `DRIED-G3-SCOPE: none` (alaska king crab, blue crab, blue swimming crab, dungeness crab, queen crab, northern lobster, blue mussel, eastern oyster, pacific oyster, common octopus, patagonian bay scallop, sea scallop). `Dried <finfish>` is Group 3; `Dried <crab/lobster/mussel/oyster/octopus/scallop>` and `Dehydrated ...`, `Dried X, salt`, `Dried X powder` ABSTAIN (reason: dried meats and fish only; drying alone does not make it Group 1): the Group 1 grouping of seafood with fish is not extended to the dried example, and no evidence for that extension was found. Generic drying never falls back to Group 1 for these rows.

## 2. Gates (committed tree vs the stacked base 658c0e9; separate fresh processes)
| check | result |
|---|---|
| lexicon | 441 -> 509 (+68 whole_food rows; none changed or removed); synonyms, markers, descriptors untouched |
| frozen 66 / out-of-sample 32 | changed 0 / 0 (no label holds one of these words); unexplained 0; abstain->4 0 (the meat rows' own S18 change belongs to animal-guard-1) |
| drift (591) / descriptor (882) / salted (192) / powder (603) | 0 differences / 0 / 0 / 0 changed |
| suite | **2304 passed, 5 xfailed** (animal-guard-1 2082 + 222 new tests) |
| parity | **893/893** identical (animal-guard-1 875 + 18 added entries, 0 removed; reason and driver compared) |
Cumulative against main a6cacbc the stack is 433 -> 509 rows; the only frozen/out-of-sample difference of the whole stack is animal-guard-1's S18 (`Lamb (33%)`).

## 3. Measured forms (all 68 rows; before = unrecognised)
| form | result | form | result |
|---|---|---|---|
| X; ground X; roasted X; boiled X; steamed X | 1 (all 68) | dried X | 3 for the 56 fish rows; **abstain for the 12 seafood rows** |
| X powder; 100% X powder; whole X powder | abstain | chilled X; cooked X | abstain |
| salted, smoked, cured, canned, breaded, battered, fried, minced, formed X | abstain | X (XQ9); X (rice); X (milk); X (brine); X (sunflower oil); X, water | abstain |
| X, salt | 3 | hydrogenated X | 4 |
Generic and alias labels (salmon, tuna, fish, shrimp, crab, snow crab) stay unrecognised; plant, dairy and meat controls (dried chicken 3, chicken powder abstain, dried rice 1) are unchanged. `Salmon` alone abstains: only `atlantic salmon`, `chinook`, `chum`, `coho`, `pink` and `sockeye salmon` are rows.

## 4. Exact diff vs animal-guard-1 658c0e9 (7 paths, `git diff --name-only 658c0e9 HEAD` on the committed merge tree)
- `data/ingest/animal_fish_rows_1.json`
- `evaluation/animal_fish_rows_1/README.md`
- `evaluation/animal_fish_rows_1/applied_gate/applied_gate.json`
- `evaluation/animal_fish_rows_1/staged_rows.csv`
- `scripts/parity_check.py`
- `src/foodscan/resources/lexicon.csv`
- `tests/test_animal_fish_rows_1.py`
