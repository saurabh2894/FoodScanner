# Batch 9 Candidate Staging: Plain Meat & Poultry (`class_bulk_9_meat_poultry_1`)

## 1. Summary & Staging Scope
- **Task**: Candidate staging for Batch 9 (plain meat and poultry) based on cached USDA FoodData Central (FDC) records and FAO 2019 NOVA definitions, repaired under Task 13.
- **Role**: Generator/Researcher staging evidence and candidates for senior review (Claude). Zero changes to application source code, parser, classifier, or runtime resources (`lexicon.csv`, `synonyms.csv`, `markers.csv` untouched).
- **Branch**: `antigravity/class-bulk-9-meat-poultry`
- **Original Base Commit**: `c0ece2b55f3b968598c889edc6b7d07e1dfd2b58` (main HEAD)
- **Primary Handoff Unit**: `canonical_candidates.csv` (8 candidate rows, exactly 1 row per distinct domestic meat food).
- **Complete Provenance Map**: `record_dispositions.csv` (2,179 rows, exactly 1 row per cached in-scope FDC record).
- **Status**: COMPLETE; artifacts staged additions-only under `evaluation/class_bulk_9_meat_poultry_1/`.

---

## 2. Derivation & Tie-Out
All counts are strictly derived from the underlying CSV artifacts (`record_dispositions.csv`, `canonical_candidates.csv`, `accept_records.csv`, `queue.csv`, `reject.csv`):

| Measure | Count | Notes |
|---|---|---|
| **Total FDC records in scope** | **2,179** | 4 commodity categories (2,137 SR Legacy + 42 Foundation) |
| **ACCEPT (candidate records)** | **1,650** | Plain whole muscle cuts and natural offal of domestic livestock & poultry |
| **QUEUE (pending owner decision)** | **241** | Game/rare species (115), fried/pan-fried methods (60), separable fat/skin-only (50), unstated ground meat (16) |
| **REJECT (conditioned / out of scope)** | **288** | Cured/smoked meats (122), seasoned/formulated (71), injected/enhanced/basted (65), breaded/battered (19), mechanically deboned (7), added broth/gravy (4) |
| **Total Artifact Sum (Tie-Out)** | **2,179** | **EXACT TIE**: `candidates = accept (1650) + queue (241) + reject (288)` |

### In-Scope Category Breakdown
- `Beef Products`: 975 records (954 SR Legacy + 21 Foundation)
- `Lamb, Veal, and Game Products`: 466 records (464 SR Legacy + 2 Foundation)
- `Poultry Products`: 395 records (383 SR Legacy + 12 Foundation)
- `Pork Products`: 343 records (336 SR Legacy + 7 Foundation)
- **Total in-scope**: 2,179 records (2,137 SR Legacy + 42 Foundation)

### Skipped Category Recorded
- `Sausages and Luncheon Meats`: **185 records** skipped entirely (167 SR Legacy + 18 Foundation). All items are cured, formulated, or ultra-processed sausages/luncheon meats.

---

## 3. Task 13 Staging Repairs & Guard Enforcements

1. **Primary Review Handoff**: `canonical_candidates.csv` is now the concise primary review artifact (8 candidate rows). `accept_records.csv` (1,650 rows) is retained for full transparency as a record-level mapping, and `record_dispositions.csv` (2,179 rows) provides a single deterministic map of every in-scope category record.
2. **Separable Animal Fats Isolated**: 50 records representing pure animal backfat (`Pork, fresh, backfat, raw`), seam fat, external fat, subcutaneous fat, intermuscular fat, suet, leaf fat, or skin-only (`Chicken, skin only`, `Turkey, skin`) were isolated to QUEUE under `queue_animal_fat` and deferred to the fats review.
3. **Cooking Methods with Added Fat**: 60 records where the cooking method states `pan-fried`, `fried`, or `deep-fried` were isolated to QUEUE under `queue_cooking_added_fat`. Because the source name states frying without establishing whether added cooking oil/fat was used, plain status cannot be established from the name alone.
4. **Enhanced / Injected / Seasoned Formulations**: 65 injected/enhanced records (e.g. `Pork, fresh, enhanced`, `Turkey breast, pre-basted`, `Hormel Always Tender`) and 71 seasoned/formulated records (e.g. `rotisserie, original seasoning`) were moved to REJECT.
5. **Mechanically Deboned Meat**: 7 records of mechanically separated/deboned poultry and beef were moved to REJECT.

---

## 4. Proposed Canonical Candidates (`canonical_candidates.csv`: 8 rows)

The 1,650 accepted plain meat records collapse into exactly 8 distinct domestic food candidates:

| Canonical Label | Suggested Kind | Supporting FDC Count | Existing Lexicon Match | Example Supporting FDC IDs | Variant / Synonym Candidates |
|---|---|---|---|---|---|
| `beef` | `whole_food` | 911 | NONE | 170809, 168607, 174013 | `ground beef; beef steak; beef roast; beef brisket; beef chuck; beef ribeye; beef sirloin; beef tenderloin; beef shank; beef round; beef liver; beef heart; beef tongue; beef kidney; beef tripe` |
| `lamb` | `whole_food` | 264 | NONE | 172479, 172573, 172605 | `ground lamb; lamb chop; lamb leg; lamb shoulder; lamb loin; lamb rib; lamb shank; lamb liver; lamb heart; lamb tongue; lamb kidney` |
| `pork` | `whole_food` | 190 | NONE | 167818, 168249, 168376 | `ground pork; pork chop; pork loin; pork tenderloin; pork shoulder; pork spareribs; pork ribs; pork liver; pork heart; pork tongue; pork kidney` |
| `chicken` | `whole_food` | 113 | NONE | 171047, 171051, 171062 | `chicken cut; chicken breast; chicken thigh; chicken drumstick; chicken wing; chicken leg; chicken meat; chicken giblets; chicken liver; chicken heart; chicken gizzard; ground chicken` |
| `veal` | `whole_food` | 91 | NONE | 172478, 172640, 172644 | `ground veal; veal cutlet; veal chop; veal loin; veal rib; veal shank; veal breast; veal liver; veal heart; veal tongue; veal kidney; sweetbread` |
| `turkey` | `whole_food` | 67 | NONE | 171081, 171480, 171485 | `turkey cut; turkey breast; turkey thigh; turkey drumstick; turkey wing; turkey meat; turkey giblets; turkey liver; turkey heart; ground turkey` |
| `duck` | `whole_food` | 9 | NONE | 171112, 171113, 172408 | `duck cut; duck breast; duck leg; duck meat; duck liver` |
| `goose` | `whole_food` | 5 | NONE | 172412, 172413, 172414 | `goose cut; goose meat; goose breast; goose liver` |

- **Already covered in lexicon.csv**: 0 (zero meat/poultry terms exist in `lexicon.csv`)
- **Genuinely new canonical food proposals**: 8
- **Variant/synonym candidates**: Surfaced purely as candidate aliases in `canonical_candidates.csv`; `synonyms.csv` is not modified.

---

## 5. Queue Breakdown (241 rows)
- `queue_game_rare_species`: **115 rows** (bison, venison/deer, elk, moose, antelope, bear, beaver, horse, rabbit, hare, muskrat, opossum, squirrel, raccoon, goat, pheasant, quail, squab, wild duck, wild turkey, ostrich, emu, rhea, grouse, Canada goose).
- `queue_cooking_added_fat`: **60 rows** (pan-fried, fried, deep-fried cuts where added cooking fat cannot be ruled out from source description alone).
- `queue_animal_fat`: **50 rows** (pure animal backfat, seam fat, external fat, subcutaneous fat, intermuscular fat, suet, leaf fat, skin-only; deferred to fats and oils review).
- `ground_form_unstated`: **16 rows** (ground meat where lean/fat ratio and processing details are unstated).

---

## 6. Reject Breakdown (288 rows)
- `cured_smoked_processed`: **122 rows** (bacon, Canadian bacon, breakfast strips, salt pork, cured ham, pastrami, corned beef, dried beef, smoked meats).
- `seasoned_formulated`: **71 rows** (rotisserie seasoned chicken, frankfurters, bologna, salami, sausages, patties, nuggets, loaves, barbecue).
- `injected_enhanced_solution`: **65 rows** (enhanced pork, pre-basted turkey, injected water/phosphate solutions, Hormel Always Tender).
- `breaded_battered`: **19 rows** (breaded, battered, or floured meat/poultry cuts).
- `mechanically_separated`: **7 rows** (mechanically separated or mechanically deboned poultry/meat).
- `added_broth_gravy`: **4 rows** (cuts packed with added broth or gravy).
