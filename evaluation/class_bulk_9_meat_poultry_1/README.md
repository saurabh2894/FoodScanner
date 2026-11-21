# Batch 9 Candidate Staging: Plain Meat & Poultry (`class_bulk_9_meat_poultry_1`)

## 1. Summary & Staging Scope
- **Task**: Candidate staging for Batch 9 (plain meat and poultry) based on cached USDA FoodData Central (FDC) records and FAO 2019 NOVA definitions.
- **Role**: Generator/Researcher staging evidence and candidates for senior review (Claude). Zero changes to application source code, parser, classifier, or runtime resources (`lexicon.csv`, `synonyms.csv`, `markers.csv` untouched).
- **Branch**: `antigravity/class-bulk-9-meat-poultry`
- **Base Commit**: `c0ece2b55f3b968598c889edc6b7d07e1dfd2b58` (main HEAD)
- **Status**: COMPLETE; artifacts staged additions-only under `evaluation/class_bulk_9_meat_poultry_1/`.

## 2. Derivation & Tie-Out
All counts are strictly derived from the underlying CSV artifacts (`accept_records.csv`, `queue.csv`, `reject.csv`):

| Measure | Count | Notes |
|---|---|---|
| **Total FDC candidates in scope** | **2179** | 4 commodity categories (2137 SR Legacy + 42 Foundation) |
| **ACCEPT (candidate records)** | **1691** | Plain whole muscle, cuts, and offal of domestic livestock & poultry (A1–A6) |
| **QUEUE (pending owner decision)** | **186** | Game & rare species, ground/minced forms unstated, separable animal fats |
| **REJECT (conditioned / out of scope)** | **302** | Cured/smoked meats, bacon, ham, breaded/battered, injected with solution, patties |
| **Total Artifact Sum (Tie-Out)** | **2179** | **EXACT TIE**: `candidates = accept (1691) + queue (186) + reject (302)` |

### In-Scope Category Breakdown
- `Beef Products`: 975 records (954 SR Legacy + 21 Foundation)
- `Lamb, Veal, and Game Products`: 466 records (464 SR Legacy + 2 Foundation)
- `Poultry Products`: 395 records (383 SR Legacy + 12 Foundation)
- `Pork Products`: 343 records (336 SR Legacy + 7 Foundation)
- **Total in-scope**: 2179 records (2137 SR Legacy + 42 Foundation)

### Skipped Category Recorded
- `Sausages and Luncheon Meats`: **185 records** skipped entirely (167 SR Legacy + 18 Foundation). All items are cured, formulated, or ultra-processed sausages/luncheon meats.

### Acceptance Breakdown
- **Candidate records accepted**: 1691
- **Distinct canonical foods**: 8 (`beef`, `chicken`, `duck`, `goose`, `lamb`, `pork`, `turkey`, `veal`)
- **Already covered in lexicon.csv**: 0 (zero meat/poultry terms currently exist in lexicon.csv)
- **NEW canonical food proposals for senior review**: 8

### Queue Breakdown (186 rows)
- `ground_form_unstated`: 71
- `queue_animal_fat`: 21
- `queue_game_rare_species`: 94

### Reject Breakdown (302 rows)
- `breaded_battered`: 31
- `canned_meat`: 3
- `conditioned_with`: 67
- `cured_pork_products`: 130
- `formulated_restructured`: 40
- `mechanically_separated`: 7
- `seasoned_marinated`: 19
- `smoked_meat`: 5

## 3. Dispositions & Overlaps
- **Separable Animal Fats**: 21 animal fat records (suet, fatback, separable fat, poultry skin) are placed in QUEUE under `queue_animal_fat` with disposition **'defer to fats reading (Task 7 review outcome)'**.
- **Ground / Minced Forms**: 71 ground/minced records are placed in QUEUE under `ground_form_unstated` pending policy resolution on single-ingredient verification for comminuted meats.
- **Game & Rare Species**: 94 records representing wild game (venison, elk, bison, rabbit, wild boar) and rare species (goat, pheasant, quail, squab, ostrich, emu) are placed in QUEUE under `queue_game_rare_species` as SOURCE-SILENT in FAO 2019 Table 1 Group 1.

## 4. Proposed New Canonical Foods (8 items)
The following 8 canonical domestic livestock and poultry foods are plain, unconditioned commodities supported by real FDC commodity records:

| Canonical Term | Category Sub-class | FDC Record Count | Example FDC ID & Description |
|---|---|---|---|
| `beef` | Mammalian Meat | 912 | FDC 168607 ("Beef, brisket, whole, separable lean only, all grades, raw") |
| `chicken` | Poultry | 142 | FDC 171047 ("Chicken, broilers or fryers, meat and skin and giblets and neck, raw") |
| `duck` | Poultry | 9 | FDC 171112 ("Duck, young duckling, domesticated, White Pekin, leg, meat and skin, bone in, cooked, roasted") |
| `goose` | Poultry | 6 | FDC 172412 ("Goose, domesticated, meat and skin, cooked, roasted") |
| `lamb` | Mammalian Meat | 279 | FDC 172479 ("Lamb, composite of trimmed retail cuts, separable lean and fat, trimmed to 1/4" fat, choice, raw") |
| `pork` | Mammalian Meat | 184 | FDC 167811 ("Pork, fresh, backfat, raw") |
| `turkey` | Poultry | 62 | FDC 171081 ("Turkey, whole, meat and skin, raw") |
| `veal` | Mammalian Meat | 97 | FDC 172478 ("Veal, Australian, rib, rib roast, separable lean only, raw") |

## 5. Canonical Deduplication Decisions (A6)
Butchering cuts (steaks, roasts, chops, cutlets, breasts, drumsticks, wings), fat trim levels (separable lean only, separable lean and fat, 1/8" trim, 0" trim), USDA commercial grades (Choice, Select, Prime), plain offal (liver, heart, kidney, tongue, tripe, gizzard), and plain cooking methods (raw, roasted, broiled, braised, pan-broiled, simmered, stewed) collapse into single canonical foods:

| Candidate Variety / Variant | Collapses To Canonical | Decision Basis |
|---|---|---|
| Ribeye, tenderloin, sirloin, chuck, brisket, round steaks/roasts, liver, heart | `beef` | Cuts and offal of cattle (Bos taurus); same commodity food |
| Chops, loin, tenderloin, spareribs, shoulder butt, belly, liver, kidney | `pork` | Cuts and offal of domestic swine (Sus domesticus) |
| Loin chops, leg of lamb, shoulder roasts, shank, lamb liver, heart | `lamb` | Cuts and offal of domestic sheep (Ovis aries) |
| Veal cutlet, chops, breast, rib, shoulder, veal liver, sweetbreads | `veal` | Cuts and offal of young cattle |
| Chicken breast, thigh, drumstick, wing, back, chicken liver, heart, gizzard | `chicken` | Parts, cuts, and giblets of Gallus gallus domesticus |
| Turkey breast, drumstick, wing, thigh, turkey liver, heart, gizzard | `turkey` | Parts, cuts, and giblets of Meleagris gallopavo |
| Duck breast, meat only, meat and skin, duck liver | `duck` | Parts and offal of domestic duck (Anas platyrhynchos) |
| Goose meat only, meat and skin, goose liver | `goose` | Parts and offal of domestic goose (Anser anser) |

## 6. Synonym Candidates for Review
The following synonym candidates are surfaced from FDC descriptions and commercial cut trade names (not added to synonyms.csv):
- `beef steak` -> `beef`
- `beef roast` -> `beef`
- `beef brisket` -> `beef`
- `beef liver` -> `beef`
- `pork chop` -> `pork`
- `pork loin` -> `pork`
- `pork tenderloin` -> `pork`
- `pork liver` -> `pork`
- `lamb chop` -> `lamb`
- `leg of lamb` -> `lamb`
- `chicken breast` -> `chicken`
- `chicken thigh` -> `chicken`
- `chicken drumstick` -> `chicken`
- `chicken wings` -> `chicken`
- `chicken liver` -> `chicken`
- `turkey breast` -> `turkey`
- `turkey drumstick` -> `turkey`
- `duck meat` -> `duck`
- `goose meat` -> `goose`
