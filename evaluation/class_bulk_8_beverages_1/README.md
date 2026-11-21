# Batch 8 Candidate Staging: FDC 'Beverages' Plain Forms (`class_bulk_8_beverages_1`)

## 1. Summary & Staging Scope
- **Task**: Candidate staging for Batch 8 ('Beverages' plain forms) based on cached USDA FoodData Central (FDC) records and FAO 2019 NOVA definitions.
- **Role**: Generator/Researcher staging evidence and candidates for senior review (Claude). Zero changes to application source code, parser, classifier, or runtime resources (`lexicon.csv`, `synonyms.csv`, `markers.csv` untouched).
- **Branch**: `antigravity/class-bulk-8-beverages`
- **Base Commit**: `cecccb9cb9512782d8c427944c34ef4c857d72df` (main HEAD)
- **Status**: COMPLETE; artifacts staged additions-only under `evaluation/class_bulk_8_beverages_1/`.

## 2. Derivation & Tie-Out
All counts are strictly derived from the underlying CSV artifacts (`accept_records.csv`, `queue.csv`, `reject.csv`):

| Measure | Count | Notes |
|---|---|---|
| **Total FDC candidates in category** | **370** | Category exactly 'Beverages' (366 SR Legacy + 4 Foundation; 'Alcoholic Beverages' = 0 in both archives) |
| **ACCEPT (candidate records)** | **22** | Plain drinking water, brewed tea, and brewed coffee meeting criteria A1–A6 |
| **QUEUE (pending owner decision)** | **34** | Decaf/instant variants (synonym candidates), plant milks, coffee substitutes, juices (parked), sparkling water, herbal teas |
| **REJECT (conditioned / out of scope)** | **314** | Alcoholic beverages, carbonated soft drinks, juice drinks, cocktails, mixes/powders, sweetened/diet, shakes/smoothies |
| **Total Artifact Sum (Tie-Out)** | **370** | **EXACT TIE**: `candidates = accept (22) + queue (34) + reject (314)` |

### Acceptance Breakdown
- **Candidate records accepted**: 22
- **Distinct canonical foods**: 3
- **Already covered in lexicon.csv**: 1 (`water`)
- **NEW canonical food proposals for senior review**: 2 (`coffee`, `tea`)

### Queue Breakdown (34 rows)
- `queue_carbonated_water`: 3
- `queue_coconut_water`: 1
- `queue_coffee_substitute`: 4
- `queue_herbal_infusion`: 3
- `queue_plant_milk`: 6
- `roadmap_parked`: 4
- `synonym_candidates`: 13

### Reject Breakdown (314 rows)
- `alcoholic_beverage`: 82
- `carbonated_soft_drink`: 55
- `conditioned_with`: 4
- `dairy_shake_mix`: 21
- `energy_sports_drink`: 17
- `flavoured_infused`: 1
- `formulated_beverage`: 21
- `fortified_supplement`: 6
- `juice_drink_cocktail`: 58
- `mix_powder_syrup`: 25
- `sweetened_diet`: 24

## 3. Cached Category Enumeration & Dairy Overlap
- **Cached Categories Enumerated**:
  - `Beverages` (ID 14): 366 SR Legacy records + 4 Foundation records = 370 records.
  - `Alcoholic Beverages` (ID 28): 0 records present in cached SR Legacy and Foundation archives. (Alcoholic items in FDC are classified under ID 14 'Beverages', and are rejected under `alcoholic_beverage`).
- **Dairy Overlap Disposition**:
  - No plain buttermilk, lassi, or fluid dairy milk records are present in FDC 'Beverages' (dairy commodities were classified under 'Dairy and Egg Products' and queued in Batch 6).
  - One chocolate malt powder record (FDC 174864, Ovaltine Classic Malt) is rejected under `dairy_shake_mix` / `mix_powder_syrup`.

## 4. Proposed New Canonical Foods (2 items)
The following 2 canonical foods are plain, unconditioned beverages supported by real FDC commodity records and verbatim named in FAO 2019 Table 1 Group 1 (p. 11):

| Canonical Term | Category Sub-class | FDC Record Count | Example FDC ID & Description |
|---|---|---|---|
| `tea` | Plant Infusion | 7 | FDC 173227 ("Beverages, tea, black, brewed, prepared with tap water") |
| `coffee` | Plant Infusion | 3 | FDC 171890 ("Beverages, coffee, brewed, prepared with tap water") |

*(Note: `water` is supported by 12 commodity records and already exists in `lexicon.csv` with `kind='neutral'`.)*

## 5. Canonical Deduplication Decisions (A6)
Water sourcing/packaging (tap, well, municipal, spring, bottled), tea leaf types (black, green, oolong), and coffee brewing styles (brewed, espresso) collapse into single canonical foods:

| Candidate Variety / Variant | Collapses To Canonical | Decision Basis |
|---|---|---|
| Tap, well, municipal, bottled spring, purified water | `water` | Water source / containment variation; same neutral carrier commodity |
| Black tea, green tea, oolong tea | `tea` | Fermentation/oxidation grades of Camellia sinensis; same botanical tea infusion |
| Brewed breakfast blend, brewed coffee, espresso | `coffee` | Roast / extraction variation of Coffea arabica / canephora; same brewed coffee beverage |

## 6. Synonym Candidates for Review
The following synonym candidates are surfaced from FDC descriptions, processing variants, and decaf/instant forms (queued under `synonym_candidates`, not added to synonyms.csv):
- `black tea` -> `tea`
- `green tea` -> `tea`
- `oolong tea` -> `tea`
- `brewed tea` -> `tea`
- `brewed coffee` -> `coffee`
- `espresso` -> `coffee`
- `decaf coffee` / `decaffeinated coffee` -> `coffee`
- `instant coffee` -> `coffee`
- `decaf tea` / `decaffeinated tea` -> `tea`
- `instant tea` -> `tea`
- `tap water` -> `water`
- `well water` -> `water`
- `bottled water` -> `water`
- `spring water` -> `water`
