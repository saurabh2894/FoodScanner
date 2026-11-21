# Batch 6 Candidate Staging: FDC 'Dairy and Egg Products' (`class_bulk_6_dairy_1`)

## 1. Summary & Staging Scope
- **Task**: Candidate staging for Batch 6 ('Dairy and Egg Products') based on cached USDA FoodData Central (FDC) records and FAO 2019 NOVA definitions.
- **Role**: Generator/Researcher staging evidence and candidates for senior review (Claude). Zero changes to application source code, parser, classifier, or runtime resources (`lexicon.csv`, `synonyms.csv`, `markers.csv` untouched).
- **Branch**: `antigravity/class-bulk-6-dairy`
- **Base Commit**: `22966c812b499ec470521afc2406cfced5862ba6` (main HEAD)
- **Status**: COMPLETE; artifacts staged additions-only under `evaluation/class_bulk_6_dairy_1/`.

## 2. Derivation & Tie-Out
All counts are strictly derived from the underlying CSV artifacts (`accept_records.csv`, `queue.csv`, `reject.csv`):

| Measure | Count | Notes |
|---|---|---|
| **Total FDC candidates in category** | **341** | Category exactly 'Dairy and Egg Products' (291 SR Legacy + 50 Foundation) |
| **ACCEPT (candidate records)** | **19** | Plain unconditioned fluid/powdered milk and whole fresh/frozen eggs |
| **QUEUE (pending owner decision)** | **223** | Cheeses (Gr 3), butter/cream (Gr 2), yogurts, buttermilk, paneer, whey/casein, egg fractions, fortified milk |
| **REJECT (conditioned / out of scope)** | **99** | Ice cream, desserts/puddings, flavored dairy, sweetened, imitation/substitutes, cooked eggs |
| **Total Artifact Sum (Tie-Out)** | **341** | **EXACT TIE**: `candidates = accept (19) + queue (223) + reject (99)` |

### Acceptance Breakdown
- **Candidate records accepted**: 19 (11 dairy + 8 egg)
- **Distinct canonical foods**: 10
- **Already covered in lexicon.csv / exceptions**: 4 (`milk`, `eggs`, `buffalo milk`, and `milk powder` via `classify.milk_powder_named`)
- **NEW canonical food proposals for senior review**: 6

### Queue Breakdown (223 rows)
- `queue_butter_ghee_cream`: 19
- `queue_buttermilk`: 5
- `queue_cheese`: 111
- `queue_condensed_evaporated`: 4
- `queue_egg_fraction`: 16
- `queue_fermented_dairy`: 35
- `queue_fortified_milk`: 26
- `queue_powdered_eggs`: 3
- `queue_whey_casein`: 4

### Reject Breakdown (99 rows)
- `cooked_egg`: 6
- `dessert_pudding_shake`: 7
- `flavored_dairy`: 32
- `ice_cream`: 14
- `imitation_substitute`: 17
- `salted`: 4
- `spread_dip_sauce`: 7
- `supplement_protein_isolate`: 3
- `sweetened_condensed`: 3
- `whipped_spray_topping`: 6

## 3. Proposed New Canonical Foods (6 items)
The following 6 canonical foods are plain, unconditioned animal milks and whole eggs supported by real FDC commodity records:

| Canonical Term | Category Sub-class | FDC Record Count | Example FDC ID & Description |
|---|---|---|---|
| `duck eggs` | Egg | 1 | FDC 172189 ("Egg, duck, whole, fresh, raw") |
| `goose eggs` | Egg | 1 | FDC 172190 ("Egg, goose, whole, fresh, raw") |
| `human milk` | Dairy | 1 | FDC 171279 ("Milk, human, mature, fluid") |
| `quail eggs` | Egg | 1 | FDC 172191 ("Egg, quail, whole, fresh, raw") |
| `sheep milk` | Dairy | 1 | FDC 170882 ("Milk, sheep, fluid") |
| `turkey eggs` | Egg | 1 | FDC 172192 ("Egg, turkey, whole, fresh, raw") |

## 4. Canonical Deduplication Decisions (A6)
Fat grade (whole, reduced fat 2%, lowfat 1%, nonfat/skim), drying cuts (regular vs instant dry milk), and egg sizing collapse into single canonical foods:

| Candidate Variety / Variant | Collapses To Canonical | Decision Basis |
|---|---|---|
| Whole, 2%, 1%, nonfat unfortified fluid milk | `milk` | Fat-level standardization does not alter commodity food identity |
| Regular nonfat dry milk, instant nonfat dry milk, whole dry milk | `milk powder` | Physical moisture removal (spray drying); composition source-established |
| Whole fresh chicken eggs, Grade A Large eggs, frozen pasteurized eggs | `eggs` | Whole egg without fractionation; pasteurization/freezing allowed |
| Duck eggs, goose eggs, quail eggs, turkey eggs | Separate avian egg species rows | Distinct whole avian egg commodities |
| Sheep milk, human milk | Separate mammalian milk species rows | Distinct mammalian fluid milk commodities |

## 5. Synonym Candidates for Review
The following synonym candidates are surfaced from FDC alternate names and variety records (not added to synonyms.csv):
- `fluid milk` -> `milk`
- `skim milk` -> `milk`
- `fat free milk` -> `milk`
- `nonfat dry milk` -> `milk powder`
- `dried milk` -> `milk powder`
- `chicken eggs` -> `eggs`
- `whole eggs` -> `eggs`
