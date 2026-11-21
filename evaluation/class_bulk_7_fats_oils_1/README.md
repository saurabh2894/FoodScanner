# Batch 7 Candidate Staging: FDC 'Fats and Oils' (`class_bulk_7_fats_oils_1`)

## 1. Summary & Staging Scope
- **Task**: Candidate staging for Batch 7 ('Fats and Oils') based on cached USDA FoodData Central (FDC) records and FAO 2019 NOVA definitions.
- **Role**: Generator/Researcher staging evidence and candidates for senior review (Claude). Zero changes to application source code, parser, classifier, or runtime resources (`lexicon.csv`, `synonyms.csv`, `markers.csv` untouched).
- **Branch**: `antigravity/class-bulk-7-fats-oils`
- **Base Commit**: `79e3f1981ed18536cdf6b61205f12dfedaf99eb0` (main HEAD)
- **Status**: COMPLETE; artifacts staged additions-only under `evaluation/class_bulk_7_fats_oils_1/`.

## 2. Derivation & Tie-Out
All counts are strictly derived from the underlying CSV artifacts (`accept_records.csv`, `queue.csv`, `reject.csv`):

| Measure | Count | Notes |
|---|---|---|
| **Total FDC candidates in category** | **228** | Category exactly 'Fats and Oils' (216 SR Legacy + 12 Foundation) |
| **ACCEPT (candidate records)** | **50** | Plain single-ingredient vegetable oils and plant butters meeting criteria A1–A6 |
| **QUEUE (pending owner decision)** | **16** | Dairy butter (owned here), animal fats, fish oils, fat fractions |
| **REJECT (conditioned / out of scope)** | **162** | Standing rule (hydrogenated/interesterified), margarines, shortenings, dressings, spreads, blends |
| **Total Artifact Sum (Tie-Out)** | **228** | **EXACT TIE**: `candidates = accept (50) + queue (16) + reject (162)` |

### Acceptance Breakdown
- **Candidate records accepted**: 50
- **Distinct canonical foods**: 32
- **Already covered in lexicon.csv**: 11 (`cocoa butter`, `coconut oil`, `cottonseed oil`, `mustard oil`, `olive oil`, `palm oil`, `peanut oil`, `rice bran oil`, `sesame oil`, `soybean oil`, `sunflower oil`)
- **NEW canonical food proposals for senior review**: 21

### Queue Breakdown (16 rows)
- `queue_animal_fat`: 6
- `queue_dairy_fat`: 2
- `queue_fish_oil`: 5
- `queue_fraction`: 3

### Reject Breakdown (162 rows)
- `blended_oil`: 2
- `conditioned_with`: 2
- `dressing_mayo`: 69
- `imitation_substitute`: 1
- `industrial_oil_mix`: 2
- `margarine`: 37
- `modified_oil`: 1
- `shortening`: 5
- `spread`: 2
- `standing_rule`: 39
- `whipped_spray`: 2

## 3. Dairy Queue Overlap Disposition
- **Context**: In Task 8 ('Dairy and Egg Products'), 19 dairy butter, ghee, and cream records were placed in queue under `queue_butter_ghee_cream` because they are fats/culinary ingredients.
- **Batch 7 Ownership**: Batch 7 ('Fats and Oils') **OWNS** the fats reading.
- **Disposition**: The 2 dairy butter records present in the FDC 'Fats and Oils' category (FDC 172344 "Butter, light, stick, without salt" and FDC 173581 "Butter, light, stick, with salt") are queued here under `queue_dairy_fat` with disposition **'owned here, dairy queue defers'**. Senior review can integrate both sets from Batch 7's definitive fats evidence.

## 4. Proposed New Canonical Foods (21 items)
The following 21 canonical culinary oils and plant fats are plain, single-ingredient commodities supported by real FDC commodity records:

| Canonical Term | Category Sub-class | FDC Record Count | Example FDC ID & Description |
|---|---|---|---|
| `almond oil` | Vegetable Oil / Fat | 1 | FDC 171031 ("Oil, almond") |
| `apricot kernel oil` | Vegetable Oil / Fat | 1 | FDC 171032 ("Oil, apricot kernel") |
| `avocado oil` | Vegetable Oil / Fat | 1 | FDC 173573 ("Oil, avocado") |
| `babassu oil` | Vegetable Oil / Fat | 1 | FDC 171428 ("Oil, babassu") |
| `canola oil` | Vegetable Oil / Fat | 4 | FDC 171033 ("Oil, vegetable, Natreon canola, high stability, non trans, high oleic (70%)") |
| `corn oil` | Vegetable Oil / Fat | 2 | FDC 171029 ("Oil, corn, industrial and retail, all purpose salad or cooking") |
| `cupuassu oil` | Vegetable Oil / Fat | 1 | FDC 173563 ("Oil, cupu assu") |
| `flaxseed oil` | Vegetable Oil / Fat | 1 | FDC 167702 ("Oil, flaxseed, cold pressed") |
| `grapeseed oil` | Vegetable Oil / Fat | 1 | FDC 171028 ("Oil, grapeseed") |
| `hazelnut oil` | Vegetable Oil / Fat | 1 | FDC 171427 ("Oil, hazelnut") |
| `nutmeg butter` | Vegetable Oil / Fat | 1 | FDC 172335 ("Oil, nutmeg butter") |
| `oat oil` | Vegetable Oil / Fat | 1 | FDC 173576 ("Oil, oat") |
| `palm kernel oil` | Vegetable Oil / Fat | 1 | FDC 171422 ("Vegetable oil, palm kernel") |
| `poppyseed oil` | Vegetable Oil / Fat | 1 | FDC 171423 ("Oil, poppyseed") |
| `safflower oil` | Vegetable Oil / Fat | 3 | FDC 171026 ("Oil, safflower, salad or cooking, linoleic, (over 70%)") |
| `sheanut oil` | Vegetable Oil / Fat | 1 | FDC 171429 ("Oil, sheanut") |
| `teaseed oil` | Vegetable Oil / Fat | 1 | FDC 171425 ("Oil, teaseed") |
| `tomatoseed oil` | Vegetable Oil / Fat | 1 | FDC 171424 ("Oil, tomatoseed") |
| `ucuhuba butter` | Vegetable Oil / Fat | 1 | FDC 173570 ("Oil, ucuhuba butter") |
| `walnut oil` | Vegetable Oil / Fat | 1 | FDC 171030 ("Oil, walnut") |
| `wheat germ oil` | Vegetable Oil / Fat | 1 | FDC 171014 ("Oil, wheat germ") |

## 5. Canonical Deduplication Decisions (A6)
Fat cultivars, processing cuts (cold pressed, refined, extra virgin, extra light), fatty acid profiles (high oleic, linoleic), and retail/industrial cuts collapse into single canonical foods:

| Candidate Variety / Variant | Collapses To Canonical | Decision Basis |
|---|---|---|
| High oleic, mid-oleic, linoleic (65%, <60%) sunflower oil | `sunflower oil` | Fatty acid cultivar variations of Helianthus annuus; same culinary oil |
| Extra virgin, extra light, salad or cooking olive oil | `olive oil` | Pressing and grading cuts of Olea europaea; same culinary oil |
| High oleic, linoleic (>70%) safflower oil | `safflower oil` | Fatty acid cultivar variations of Carthamus tinctorius |
| Cold pressed flaxseed oil | `flaxseed oil` | Mechanical extraction method does not alter food identity |
| Refined, low linolenic, ultra low linolenic soybean oil | `soybean oil` | Refining and seed cultivar variations of Glycine max |
| Industrial, retail, all purpose corn oil | `corn oil` | Commercial packaging/distribution cuts of Zea mays oil |
| Nutmeg butter, ucuhuba butter | Distinct plant fat rows | Pure vegetable fats pressed from distinct botanical seeds |
| Palm oil vs palm kernel oil | Distinct vegetable oils | Oil pressed from mesocarp (fruit) vs seed (kernel) of Elaeis guineensis |

## 6. Synonym Candidates for Review
The following synonym candidates are surfaced from FDC descriptions and commodity trade names (not added to synonyms.csv):
- `flax seed oil` -> `flaxseed oil`
- `cold pressed flaxseed oil` -> `flaxseed oil`
- `extra virgin olive oil` -> `olive oil`
- `extra light olive oil` -> `olive oil`
- `virgin olive oil` -> `olive oil`
- `maize oil` -> `corn oil`
- `rapeseed oil` -> `canola oil`
- `tea seed oil` -> `teaseed oil`
- `shea butter` -> `sheanut oil`
- `shea nut oil` -> `sheanut oil`
- `cupuacu oil` -> `cupuassu oil`
