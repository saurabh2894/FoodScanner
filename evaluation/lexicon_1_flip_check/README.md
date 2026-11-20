# Lexicon 1: Sourced Ingredient Vocabulary Expansion Flip-Check

## Summary of Changes to `src/foodscan/resources/lexicon.csv`

30 new exact-term rows added, sourced directly from FAO 2019 Table 1 Group 1 (Monteiro et al., `ca5644en.pdf`, p. 11):

1. **Package A — Nuts and Seeds (`kind=whole_food`)**:
   - Added: `almonds` (seen on `neg/R5`, `b1/N14`), `pumpkin seeds` (`b1/N14`), `flax seeds` (`b1/N14`).
   - Blocked: `roasted peanuts` (`b1/N15`) — blocked under the Condition Rule ("with no added salt or sugar"). On cited label `b1/N15` (peanut butter), the product formulation has added sugar and iodised salt, and the extracted label token is conjoined `Roasted Peanuts (91%) Sugar`.

2. **Package B — Herbs and Spices (`kind=herb_spice`)**:
   - Added 22 missing herbs and spices: `ajwain` (`dev15/F09`), `bishop's seed` (`dev15/F10`), `aniseed` (`b1/N03`, `dev15/F07`), `caraway` (`dev15/F07`), `bay leaf` (`b1/N05`), `capsicum powder` (`b1/N05`), `fennel` (`b1/N05`), `fennel seeds` (`dev15/F10`), `fenugreek` (`b1/N10`, `b1/N03`, `dev15/F03`, `dev15/F07`, `dev15/F10`, `dev15/F11`), `nutmeg` (`b1/N05`, `b1/N03`, `dev15/F03`, `dev15/F07`, `dev15/F10`), `mace` (`dev15/F10`), `mint` (`dev15/F10`), `mustard` (`b1/N10`, `dev15/F11`), `pepper` (`dev15/F03`), `long pepper` (`dev15/F10`), `white pepper` (`dev15/F15`), `black pepper bits` (`dev15/F07`), `red chili` (`dev15/F03`), `chillies` (`dev15/F07`), `chilli flakes` (`dev15/F07`), `schezwan pepper` (`dev15/F15`), `dried curry leaves` (`dev15/F10`).
   - Note: existing terms `black pepper`, `chilli`, and `mustard seed` were already present and left untouched.

3. **Package C — Cereal Forms (`kind=whole_food`)**:
   - Blocked: `corn flakes` (`dev15/F10`) — blocked under the Condition Rule ("plain corn flakes"). On `dev15/F10`, the bare term `Corn Flakes (6%)` inside a savoury mixture does not establish that the ingredient is plain (unflavoured/unsweetened), and commercial flakes typically contain sugar and malt. Furthermore, `tests/test_vocabulary_layer.py:55` explicitly asserts `assert lookup("corn flakes") is None`.
   - Flours: No flour rows added, per explicit instruction.

4. **Package D — Dried Fruit (`kind=whole_food`)**:
   - Added: `black raisin` (`b1/N14`) — raisin is dried grape (plain dried fruit).
   - Blocked: `cranberry` (`b1/N14`) — blocked under the Condition Rule. The bare term `Cranberry` does not establish a dried, plain, unsweetened form.

5. **Package E — Plain Juices (`kind=whole_food`)**:
   - Added: `apple juice`, `grape juice`, `orange juice`, `pineapple juice` (seen on `dev15/F14`, `b2/M14`).
   - Covered under FAO clause "fresh or pasteurized fruit or vegetable juices (with no added sugar, sweeteners or flavours)". Declared as plain juice ingredients within a 60% fruit blend. Concentrates excluded per explicit instructions.

### Explicit Exclusions Honored
No rows added for: milk/milk solids/whey/vitamins/minerals, pulps/purees (`papaya pulp`, `pear pulp`, `banana pulp`, `mango pulp`), starches (`tapioca starch`, `starch`), cocoa forms, liquid glucose, concentrates (`apple juice concentrate`), extracts (`yeast extract`, `malt extract`), `pipal`, typos, or terms held for senior decision.

---

## Evaluation Inputs and True Baseline
Evaluated across all 66 frozen paste inputs from 5 evaluation directories:
- `fresh_batch_1`: 16 inputs
- `fresh_batch_2`: 15 inputs
- `fresh_batch_3`: 14 inputs
- `negation_addendum`: 6 inputs
- `dev_regression_15`: 15 inputs

True baseline: commit `8a4e2e7` (origin/main), generated in a clean, isolated process.

---

## Comparison Results and Attributions

- `group`: **0 changed** (0 of 66)
- `answered`: **0 changed** (0 of 66)
- `status`: **0 changed** (0 of 66)
- `drivers`: **0 changed** (0 of 66)
- `warnings`: **0 changed** (0 of 66)
- `ingredients`: **0 changed** (0 of 66)
- `ins_mappings`: **0 changed** (0 of 66)
- `reason`: **2 changed** (2 of 66)
  - `b1/N10`: Reason text dropped unrecognised terms `Mustard, Fenugreek` (leaving `Mango Pieces, Synthetic Vinegar`). Attributed to Package B rows `mustard` and `fenugreek`.
  - `dev15/F09`: Reason text dropped unrecognised term `Ajwain` (leaving `Refined Palmolein Oil`). Attributed to Package B row `ajwain`.
- `unassessed`: **13 changed** (13 of 66)
  - `b1/N03`: Dropped `aniseed`, `fenugreek`, `nutmeg`. Attributed to Package B spice rows.
  - `b1/N05`: Dropped `Fennel`, `Bay Leaf`, `Nutmeg`, `Capsicum Powder`. Attributed to Package B spice rows.
  - `b1/N10`: Dropped `Mustard`, `Fenugreek`. Attributed to Package B spice rows.
  - `b1/N14`: Dropped `Almonds`, `Flax Seeds`, `Pumpkin Seeds` (Package A) and `Black Raisin` (Package D). `Cranberry` remains unassessed (blocked by Condition Rule).
  - `b2/M14`: Dropped `apple juice`, `pineapple juice`, `orange juice`, `grape juice`. Attributed to Package E juice rows. Pulps remain unassessed (explicit exclusions).
  - `neg/R5`: Dropped `ALMONDS`. Attributed to Package A row `almonds`.
  - `dev15/F03`: Dropped `Pepper`, `Fenugreek`, `Nutmeg`, `Red Chili`. Attributed to Package B spice rows.
  - `dev15/F07`: Dropped `chillies`, `aniseed`, `fenugreek`, `nutmeg`, `caraway`, `chilli flakes`, `black pepper bits`. Attributed to Package B spice rows.
  - `dev15/F09`: Dropped `Ajwain`. Attributed to Package B row `ajwain`.
  - `dev15/F10`: Dropped `Nutmeg`, `Long Pepper`, `Mace`, `Mint`, `Fenugreek`, `Fennel Seeds`, `Bishop's Seed`, `Dried Curry Leaves (0.5%)`. Attributed to Package B spice rows.
  - `dev15/F11`: Dropped `mustard`, `fenugreek`. Attributed to Package B spice rows.
  - `dev15/F14`: Dropped `APPLE JUICE`, `PINEAPPLE JUICE`, `ORANGE JUICE`, `GRAPE JUICE`. Attributed to Package E juice rows. Pulps remain unassessed.
  - `dev15/F15`: Dropped `White Pepper`, `Schezwan Pepper`. Attributed to Package B spice rows.

---

## Generalization Disclaimer
These 66 inputs represent a frozen evidence sample from historical evaluation batches. Zero flips on this evidence sample confirms non-regression on known test vectors, but does not assert that no other unseen packaged-food label flips.
