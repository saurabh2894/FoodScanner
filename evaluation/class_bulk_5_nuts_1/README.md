# Batch 5 Candidate Staging: FDC 'Nut and Seed Products' (`class_bulk_5_nuts_1`)

## 1. Summary & Staging Scope
- **Task**: Candidate staging for Batch 5 ('Nut and Seed Products') based on cached USDA FoodData Central (FDC) records and FAO 2019 NOVA definitions.
- **Role**: Generator/Researcher staging evidence and candidates for senior review (Claude). Zero changes to application source code, parser, classifier, or runtime resources (`lexicon.csv`, `synonyms.csv`, `markers.csv` untouched).
- **Branch**: `antigravity/class-bulk-5-nuts`
- **Base Commit**: `38e85f1b43b8bf9e7d443c1f20de5f9beddbebcc` (main HEAD)
- **Status**: COMPLETE; artifacts staged additions-only under `evaluation/class_bulk_5_nuts_1/`.

## 2. Derivation & Tie-Out
All counts are strictly derived from the underlying CSV artifacts (`accept_records.csv`, `queue.csv`, `reject.csv`):

| Measure | Count | Notes |
|---|---|---|
| **Total FDC candidates in category** | **156** | Category exactly 'Nut and Seed Products' (137 SR Legacy + 19 Foundation) |
| **ACCEPT (candidate records)** | **52** | Plain unconditioned seeds and nuts meeting criteria A1–A6 |
| **QUEUE (pending owner decision)** | **59** | Plain roasted, flours/meals, butters/pastes, coconut, mixed, unstated |
| **REJECT (conditioned / out of scope)** | **45** | Salted, oil-roasted, boiled/steamed, sweetened, formulated, canned |
| **Total Artifact Sum (Tie-Out)** | **156** | **EXACT TIE**: `candidates = accept (52) + queue (59) + reject (45)` |

### Acceptance Breakdown
- **Candidate records accepted**: 52
- **Distinct canonical foods**: 27
- **Already covered in lexicon.csv**: 3 (`almonds`, `pumpkin seeds`, `flax seeds`)
- **NEW canonical food proposals for senior review**: 24

### Queue Breakdown (59 rows)
- `plain_form_not_stated`: 4
- `queue_butter_paste`: 11
- `queue_coconut`: 14
- `queue_flour_meal`: 12
- `queue_mixed`: 1
- `queue_roasted_plain`: 17

### Reject Breakdown (45 rows)
- `boiled_steamed`: 4
- `canned`: 1
- `flavored_seasoned`: 1
- `formulated`: 2
- `oil_roasted`: 15
- `salted`: 20
- `sweetened`: 2

## 3. Proposed New Canonical Foods (24 items)
The following 24 canonical foods are plain, unconditioned nuts and seeds supported by real FDC commodity records:

| Canonical Term | Category Sub-class | FDC Record Count | Example FDC ID & Description |
|---|---|---|---|
| `acorns` | Tree Nuts | 2 | FDC 170157 ("Nuts, acorns, raw") |
| `beechnuts` | Tree Nuts | 1 | FDC 170161 ("Nuts, beechnuts, dried") |
| `brazil nuts` | Tree Nuts | 2 | FDC 170569 ("Nuts, brazilnuts, dried, unblanched") |
| `breadfruit seeds` | Seeds | 1 | FDC 170144 ("Seeds, breadfruit seeds, raw") |
| `breadnut seeds` | Tree Nuts | 2 | FDC 170552 ("Seeds, breadnut tree seeds, raw") |
| `butternuts` | Tree Nuts | 1 | FDC 170570 ("Nuts, butternuts, dried") |
| `cashew nuts` | Tree Nuts | 2 | FDC 170162 ("Nuts, cashew nuts, raw") |
| `chestnuts` | Tree Nuts | 8 | FDC 169408 ("Nuts, chestnuts, japanese, dried") |
| `chia seeds` | Seeds | 1 | FDC 170554 ("Seeds, chia seeds, dried") |
| `ginkgo nuts` | Tree Nuts | 2 | FDC 170175 ("Nuts, ginkgo nuts, dried") |
| `hazelnuts` | Tree Nuts | 2 | FDC 170581 ("Nuts, hazelnuts or filberts") |
| `hickory nuts` | Tree Nuts | 1 | FDC 170177 ("Nuts, hickorynuts, dried") |
| `lotus seeds` | Seeds | 2 | FDC 168591 ("Seeds, lotus seeds, raw") |
| `macadamia nuts` | Tree Nuts | 2 | FDC 170178 ("Nuts, macadamia nuts, raw") |
| `pecans` | Tree Nuts | 1 | FDC 2346395 ("Nuts, pecans, halves, raw") |
| `pili nuts` | Tree Nuts | 1 | FDC 170590 ("Nuts, pilinuts, dried") |
| `pine nuts` | Tree Nuts | 3 | FDC 170591 ("Nuts, pine nuts, dried") |
| `pistachio nuts` | Tree Nuts | 2 | FDC 170184 ("Nuts, pistachio nuts, raw") |
| `safflower seeds` | Seeds | 1 | FDC 170558 ("Seeds, safflower seed kernels, dried") |
| `sesame seeds` | Seeds | 2 | FDC 169412 ("Seeds, sesame seed kernels, dried (decorticated)") |
| `sisymbrium seeds` | Seeds | 1 | FDC 168587 ("Seeds, sisymbrium sp. seeds, whole, dried") |
| `sunflower seeds` | Seeds | 2 | FDC 170562 ("Seeds, sunflower seed kernels, dried") |
| `walnuts` | Tree Nuts | 3 | FDC 170186 ("Nuts, walnuts, black, dried") |
| `watermelon seeds` | Seeds | 1 | FDC 169407 ("Seeds, watermelon seed kernels, dried") |

## 4. Canonical Deduplication Decisions (A6)
Variety, species, form cut, and size variants collapse into single canonical foods:

| Candidate Variety / Variant | Collapses To Canonical | Decision Basis |
|---|---|---|
| Black walnuts, English walnuts | `walnuts` | Botanical varieties of Juglans; same culinary tree nut food |
| Japanese, Chinese, European chestnuts | `chestnuts` | Regional/species varieties of Castanea; collapsed to single whole food |
| Whole, blanched almonds | `almonds` | Physical skin removal (blanching) does not alter food identity |
| Whole, peeled chestnuts | `chestnuts` | Physical shell/pellicle removal |
| Pinyon pine nuts | `pine nuts` | Regional North American pine nut variety |
| Decorticated sesame seed kernels | `sesame seeds` | Dehulled seed kernels |
| Pepitas | `pumpkin seeds` | Dehulled pumpkin seed kernels |
| Filberts | `hazelnuts` | Botanical/culinary synonym for Corylus avellana |

## 5. Synonym Candidates for Review
The following synonym candidates are surfaced from FDC alternate names and variety records (not added to synonyms.csv):
- `filberts` -> `hazelnuts`
- `pepitas` -> `pumpkin seeds`
- `pinyon pine nuts` -> `pine nuts`
- `black walnuts` -> `walnuts`
- `english walnuts` -> `walnuts`
- `japanese chestnuts` -> `chestnuts`
- `chinese chestnuts` -> `chestnuts`
- `european chestnuts` -> `chestnuts`
