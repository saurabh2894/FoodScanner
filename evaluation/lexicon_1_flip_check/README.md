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


---

## Senior revision: fb28575-anchored flip check (26 rows; the four plain-juice rows held)

The section above is the junior's analysis as submitted (anchored at 8a4e2e7, 30 rows). It is kept unchanged. After PR #2 was released (main = fb28575) and after the senior review, the evidence below supersedes the counts above for the row set that will actually be merged.

### What changed after review
1. **Four juice rows held** (apple, grape, orange, pineapple juice; removed from `lexicon.csv`; `tests/test_lexicon_1.py` adjusted; a test pins that they stay unassessed). Reason, from the sources: FAO 2019 Table 1, Group 1, p. 11 lists "fresh or pasteurized fruit or vegetable juices (with no added sugar, sweeteners or flavours)", while pp. 9-10 list "fruit juice concentrate" among the substances of ultra-processed foods. The bare term "juice" does not say which. The item-level condition (no additions on the item) is met on b2/M14 and dev15/F14, but the unmet condition (fresh/pasteurized versus from concentrate) crosses the Group 1 / Group 4 boundary, unlike the unknowns the endorsed nuts rows leave open (roasted versus raw stays inside Group 1). The corpus shows concentrates declared as "concentrate" (b1/N13, neg/R4), which supports a label convention but is two labels from two products, and the two labels carrying the juice rows are one product family. Benefit if kept: cosmetic only (8 unassessed item slots on those two Group 4 labels, no group change). Same discipline as cranberry. To restore them, source the label convention first (for example the FSSAI fruit-juice standard's labelling clause).
2. **Pin repair** in `tests/test_followup_fixes.py::test_no_broad_batch_unknown_terms_still_abstain`: attributed exceptions for `ajwain` and `bishop's seed` only (rows added by this PR, FAO spice clause); `carom seeds` and `compounded asafoetida` stay pinned as unrecognised. The besan/ajwain/salt assertion in the same test still holds: the list still abstains, now through the flour rule instead of the vocabulary gap.

### fb28575-anchored results (66 frozen paste inputs; before and after produced in separate, fresh processes)
- Files: `before_fb28575.json`, `after_fb28575.json`, `groups_before_fb28575.json`, `groups_after_fb28575.json`, `diff_summary_fb28575.json`.
- **group 0, drivers 0, status 0, warnings 0, ingredients 0, additive display 0 changed.**
- **reason: 2** (b1/N10: Mustard, Fenugreek recognised, still abstains on other items; dev15/F09: Ajwain recognised, the flour-list rule now gives the reason, still an abstention).
- **unassessed: 11 inputs, 38 item slots**, removals only; every dropped term is one of the 26 added rows. As submitted (30 rows) it was 13 inputs and 46 slots: the four juice rows account for the difference (b2/M14 and dev15/F14, 4 slots each).
- The junior's 8a4e2e7 before-artifact was checked and is valid (equal to a fresh 8a4e2e7 run on group, reason, warnings, status, unassessed and ingredients in 66/66 inputs).
- Schema note: the fb28575 files use the same serialisation as `evaluation/vocab_display_1_flip_check/` (detail strings for drivers, `dev/` key prefix); the junior's files use a repr of the driver objects and `dev15/` keys.
- These 66 inputs are the frozen evidence set that the vocabulary was drawn from: they cannot measure generalisation. The new rows are PROVISIONAL.
