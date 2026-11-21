# Ampersand-Split Simulation Results (ampersand_split_sim_1)

## Executive Summary

This simulation measures the exact impact of splitting '&'-joined items inside brackets into two independent items.

### Splitting Rule
- An '&'-joined item inside brackets is split into two items **ONLY** when each side, run through the current unmodified classifier standalone, is independently recognised.
- If either side is unrecognised, the compound remains **WHOLE** (e.g., `"spices & condiments"`, `"palm & palmolein"`, `"Bifidobacterium lactis & Lactobacillus acidophilus"` stay unsplit).
- Preprocessing lives entirely within the simulation harness; no parser or repository files are modified.

### Summary Totals

| Metric | Count |
|---|---|
| Total inputs evaluated | **98** |
| - Frozen corpus inputs | 66 |
| - Out-of-sample challenge set inputs | 32 |
| Inputs with ampersand splits performed | **6** |
| - Frozen inputs with splits | 2 (`b1/N11`, `b2/M12`) |
| - Out-of-sample inputs with splits | 4 (`oos/S03`, `oos/S20`, `oos/S26`, `oos/S28`) |
| Inputs completely unchanged | **92** |
| **Inputs with group or status changes** | **0** |

---

## Inputs with Group or Status Changes (0 Inputs)

**Zero inputs changed NOVA group or completeness status.**

While 6 inputs underwent ampersand splits resulting in recognised sub-items and cleaner ingredient/unassessed lists, none of them altered group classification or completeness status:
- Products that were already Group 4 (e.g. `oos/S03`, `oos/S20`, `b2/M12`) remain Group 4 because existing strong markers (colours, thickeners, flavour enhancers, preservatives) independently determine the classification.
- Products that were abstaining (e.g. `b1/N11`) continue to abstain because the split items (`INS 330`, `INS 260`) are weak or unlisted acidity regulators.
- Out-of-sample challenge labels (`oos/S26`, `oos/S28`) had items recognised without shifting overall status.

---

## Detailed Analysis of the 6 Inputs with Splits

### Input: `b1/N11`

**Splits Performed**:
- Original: `INS 330 & INS 260`
- Split Parts: `['INS 330', 'INS 260']`
- Replaced with: `INS 330, INS 260`

- **Group**: `None` -> `None` (unchanged)
- **Status**: `complete` -> `complete` (unchanged)
- **Diff Fields**: `['reason', 'ingredients']`

- **Ingredient Count**: 8 items -> 8 items

---

### Input: `b2/M12`

**Splits Performed**:
- Original: `INS 1422 & INS 415`
- Split Parts: `['INS 1422', 'INS 415']`
- Replaced with: `INS 1422, INS 415`

- **Group**: `4` -> `4` (unchanged)
- **Status**: `complete` -> `complete` (unchanged)
- **Diff Fields**: `['ingredients']`

- **Ingredient Count**: 9 items -> 9 items

---

### Input: `oos/S03`

**Splits Performed**:
- Original: `White Pepper (0.1%) & Celery Seed Powder`
- Split Parts: `['White Pepper (0.1%)', 'Celery Seed Powder']`
- Replaced with: `White Pepper (0.1%), Celery Seed Powder`

- **Group**: `4` -> `4` (unchanged)
- **Status**: `uncertain` -> `uncertain` (unchanged)
- **Diff Fields**: `['ingredients', 'unassessed_items']`

- **Unassessed Items Before**:
  `['Tomato Paste', 'Corn Starch', 'Yeast Extract', 'Paprika Oleoresin', 'Spices (White Pepper (0.1%) & Celery Seed Powder)', 'Sichuan Pepper Powder']`
- **Unassessed Items After**:
  `['Tomato Paste', 'Corn Starch', 'Yeast Extract', 'Paprika Oleoresin', 'Sichuan Pepper Powder', 'Spices (group name; its contents were assessed separately)']`

- **Ingredient Count**: 22 items -> 22 items

---

### Input: `oos/S20`

**Splits Performed**:
- Original: `INS 211 & INS 202`
- Split Parts: `['INS 211', 'INS 202']`
- Replaced with: `INS 211, INS 202`
- Original: `SAFFRON & CARDAMOM`
- Split Parts: `['SAFFRON', 'CARDAMOM']`
- Replaced with: `SAFFRON, CARDAMOM`
- Original: `INS 102 & INS 110`
- Split Parts: `['INS 102', 'INS 110']`
- Replaced with: `INS 102, INS 110`

- **Group**: `4` -> `4` (unchanged)
- **Status**: `uncertain` -> `uncertain` (unchanged)
- **Diff Fields**: `['ingredients']`

- **Ingredient Count**: 14 items -> 14 items

---

### Input: `oos/S26`

**Splits Performed**:
- Original: `Thyme & Rosemary`
- Split Parts: `['Thyme', 'Rosemary']`
- Replaced with: `Thyme, Rosemary`

- **Group**: `4` -> `4` (unchanged)
- **Status**: `uncertain` -> `uncertain` (unchanged)
- **Diff Fields**: `['ingredients', 'unassessed_items']`

- **Unassessed Items Before**:
  `['Cheese 6%', 'Chili', 'Thyme & Rosemary', 'Corn Starch', 'Seasoning (group name; its contents were assessed separately)', 'Herbs 0.5% (group name; its contents were assessed separately)']`
- **Unassessed Items After**:
  `['Cheese 6%', 'Chili', 'Corn Starch', 'Seasoning (group name; its contents were assessed separately)', 'Herbs 0.5% (group name; its contents were assessed separately)']`

- **Ingredient Count**: 6 items -> 6 items

---

### Input: `oos/S28`

**Splits Performed**:
- Original: `Garlic & Onion`
- Split Parts: `['Garlic', 'Onion']`
- Replaced with: `Garlic, Onion`

- **Group**: `4` -> `4` (unchanged)
- **Status**: `uncertain` -> `uncertain` (unchanged)
- **Diff Fields**: `['ingredients']`

- **Ingredient Count**: 1 items -> 1 items

---

## Compounds Correctly Kept Whole (Negative Verification)

The simulation verified that compounds where one or both sides are not independently recognised remain whole:
- `"Spices & Condiments"` (`b1/N04`, `b1/N12`, `b1/N13`, `dev/F07`, `dev/F10`): kept whole (neither `"spices"` nor `"condiments"` is recognised).
- `"palm & palmolein"` (`b1/N02`): kept whole (`"palm"` is not recognised standalone).
- `"Bifidobacterium lactis & Lactobacillus acidophilus"` (`b1/N08`): kept whole (bacterial strains not in lexicon).
- `"fortified with vitamin A & D"` (`b1/N13`): kept whole (`"D"` is not recognised standalone).
- `"NATURE IDENTICAL & ARTIFICIAL FLAVOURING SUBSTANCES-ROSE FLAVOUR"` (`neg/R3`): kept whole (`"NATURE IDENTICAL"` is not recognised standalone).
- `"Colouring & Spices"` (`dev/F10`): kept whole (`"Spices"` is not recognised standalone).

