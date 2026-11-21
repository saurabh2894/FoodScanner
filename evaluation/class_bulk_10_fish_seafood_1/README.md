# Batch 10 Candidate Staging: Plain Fish & Seafood (`class_bulk_10_fish_seafood_1`)

## 1. Summary & Staging Scope
- **Task**: Candidate staging for Batch 10 (plain fish and seafood) based on cached USDA FoodData Central (FDC) records and FAO 2019 NOVA definitions.
- **Role**: Generator/Researcher staging evidence and candidates for senior review (Claude). Zero changes to application source code, parser, classifier, or runtime resources (`lexicon.csv`, `synonyms.csv`, `markers.csv` untouched).
- **Branch**: `antigravity/class-bulk-10-fish-seafood`
- **Base Commit**: `46ad81c94757f92daaee0bf24c29d02f49965c07` (main HEAD)
- **Status**: COMPLETE; artifacts staged additions-only under `evaluation/class_bulk_10_fish_seafood_1/`.

## 2. Derivation & Tie-Out
All counts are strictly derived from the underlying CSV artifacts (`accept_records.csv`, `queue.csv`, `reject.csv`):

| Measure | Count | Notes |
|---|---|---|
| **Total FDC candidates in scope** | **288** | Category exactly 'Finfish and Shellfish Products' (264 SR Legacy + 24 Foundation) |
| **ACCEPT (candidate records)** | **218** | Plain whole fish, fillets, steaks, crustaceans, and mollusks (A1–A6) |
| **QUEUE (pending owner decision)** | **12** | Fish oils (defer to fats), roe/caviar, moisture-additive warnings, rare species |
| **REJECT (conditioned / out of scope)** | **58** | Canned fish, smoked fish, breaded/battered, surimi, salted fish, fish sticks, cakes |
| **Total Artifact Sum (Tie-Out)** | **288** | **EXACT TIE**: `candidates = accept (218) + queue (12) + reject (58)` |

### In-Scope Category Breakdown
- `Finfish and Shellfish Products`: 288 records (264 SR Legacy + 24 Foundation)

### Acceptance Breakdown
- **Candidate records accepted**: 218
- **Distinct canonical foods**: 67
- **Already covered in lexicon.csv**: 0 (zero fish/seafood terms currently exist in lexicon.csv)
- **NEW canonical food proposals for senior review**: 67

### Queue Breakdown (12 rows)
- `plain_form_not_stated`: 5
- `queue_fish_oil`: 1
- `queue_rare_species`: 3
- `queue_roe_special`: 3

### Reject Breakdown (58 rows)
- `breaded_battered`: 10
- `canned_preserved`: 30
- `formulated_product`: 3
- `salted_pickled`: 4
- `smoked_fish`: 7
- `surimi_imitation`: 4

## 3. Dispositions & Overlaps
- **Fish / Cod-Liver Oils**: 1 record is placed in QUEUE under `queue_fish_oil` with disposition **'defer to fats reading (Task 7 review outcome)'**.
- **Moisture Additive Warnings**: 5 records explicitly stating `(may contain additives to retain moisture)` (shrimp, cod, pollock) are placed in QUEUE under `plain_form_not_stated` because their single-ingredient status is unverified.
- **Fish Roe / Caviar**: 3 records (sturgeon caviar, mixed fish roe) are placed in QUEUE under `queue_roe_special`.
- **Rare / Non-Core Species**: 3 records (turtle, frog legs, terrestrial snail) are placed in QUEUE under `queue_rare_species`.

## 4. Proposed New Canonical Foods (67 items)
The following 67 canonical aquatic foods are plain, unconditioned commodities supported by real FDC commodity records:

| Canonical Term | Category Sub-class | FDC Record Count | Example FDC ID & Description |
|---|---|---|---|
| `abalone` | Mollusk | 2 | FDC 174212 ("Mollusks, abalone, mixed species, raw") |
| `anchovy` | Finfish | 1 | FDC 174182 ("Fish, anchovy, european, raw") |
| `bass` | Finfish | 4 | FDC 171948 ("Fish, bass, striped, raw") |
| `bluefish` | Finfish | 2 | FDC 171949 ("Fish, bluefish, raw") |
| `burbot` | Finfish | 2 | FDC 171950 ("Fish, burbot, raw") |
| `butterfish` | Finfish | 2 | FDC 171951 ("Fish, butterfish, raw") |
| `carp` | Finfish | 2 | FDC 171952 ("Fish, carp, raw") |
| `catfish` | Finfish | 5 | FDC 173714 ("Fish, catfish, channel, wild, cooked, dry heat") |
| `cisco` | Finfish | 1 | FDC 171953 ("Fish, cisco, raw") |
| `clam` | Mollusk | 2 | FDC 171975 ("Mollusks, clam, mixed species, cooked, moist heat") |
| `cod` | Finfish | 8 | FDC 171955 ("Fish, cod, Atlantic, raw") |
| `crab` | Crustacean | 10 | FDC 171968 ("Crustaceans, crab, dungeness, raw") |
| `crayfish` | Crustacean | 4 | FDC 174206 ("Crustaceans, crayfish, mixed species, wild, raw") |
| `croaker` | Finfish | 1 | FDC 174192 ("Fish, croaker, Atlantic, raw") |
| `cusk` | Finfish | 2 | FDC 171958 ("Fish, cusk, raw") |
| `cuttlefish` | Mollusk | 2 | FDC 172010 ("Mollusks, cuttlefish, mixed species, cooked, moist heat") |
| `drum` | Finfish | 2 | FDC 171960 ("Fish, drum, freshwater, raw") |
| `eel` | Finfish | 2 | FDC 174193 ("Fish, eel, mixed species, raw") |
| `flounder` | Finfish | 2 | FDC 174196 ("Fish, flatfish (flounder and sole species), raw") |
| `grouper` | Finfish | 2 | FDC 171962 ("Fish, grouper, mixed species, raw") |
| `haddock` | Finfish | 3 | FDC 171964 ("Fish, haddock, raw") |
| `halibut` | Finfish | 5 | FDC 171965 ("Fish, halibut, Greenland, raw") |
| `herring` | Finfish | 5 | FDC 173668 ("Fish, herring, Atlantic, kippered") |
| `ling` | Finfish | 2 | FDC 173670 ("Fish, ling, raw") |
| `lobster` | Crustacean | 5 | FDC 172009 ("Crustaceans, spiny lobster, mixed species, cooked, moist heat") |
| `mackerel` | Finfish | 8 | FDC 171994 ("Fish, mackerel, Pacific and jack, mixed species, cooked, dry heat") |
| `mahimahi` | Finfish | 3 | FDC 171959 ("Fish, mahimahi, raw") |
| `milkfish` | Finfish | 2 | FDC 171995 ("Fish, milkfish, cooked, dry heat") |
| `monkfish` | Finfish | 2 | FDC 171996 ("Fish, monkfish, cooked, dry heat") |
| `mullet` | Finfish | 2 | FDC 175123 ("Fish, mullet, striped, raw") |
| `mussel` | Mollusk | 2 | FDC 174216 ("Mollusks, mussel, blue, raw") |
| `octopus` | Mollusk | 2 | FDC 174218 ("Mollusks, octopus, common, raw") |
| `oyster` | Mollusk | 7 | FDC 171978 ("Mollusks, oyster, eastern, wild, raw") |
| `perch` | Finfish | 4 | FDC 173678 ("Fish, perch, mixed species, raw") |
| `pike` | Finfish | 4 | FDC 171997 ("Fish, pike, walleye, cooked, dry heat") |
| `pollock` | Finfish | 6 | FDC 173725 ("Fish, pollock, Alaska, raw") |
| `pompano` | Finfish | 2 | FDC 173682 ("Fish, pompano, florida, raw") |
| `pout` | Finfish | 2 | FDC 173677 ("Fish, pout, ocean, raw") |
| `rockfish` | Finfish | 2 | FDC 173684 ("Fish, rockfish, Pacific, mixed species, raw") |
| `roughy` | Finfish | 2 | FDC 174251 ("Fish, roughy, orange, cooked, dry heat") |
| `sablefish` | Finfish | 2 | FDC 174240 ("Fish, sablefish, cooked, dry heat") |
| `salmon` | Finfish | 19 | FDC 171998 ("Fish, salmon, Atlantic, wild, cooked, dry heat") |
| `scallop` | Mollusk | 4 | FDC 167742 ("Mollusks, scallop, (bay and sea), cooked, steamed") |
| `scup` | Finfish | 2 | FDC 174241 ("Fish, scup, cooked, dry heat") |
| `sea bass` | Finfish | 3 | FDC 173694 ("Fish, sea bass, mixed species, cooked, dry heat") |
| `shad` | Finfish | 2 | FDC 173696 ("Fish, shad, american, raw") |
| `shark` | Finfish | 1 | FDC 173697 ("Fish, shark, mixed species, raw") |
| `sheepshead` | Finfish | 2 | FDC 175144 ("Fish, sheepshead, raw") |
| `shrimp` | Crustacean | 3 | FDC 175179 ("Crustaceans, shrimp, raw") |
| `smelt` | Finfish | 2 | FDC 175146 ("Fish, smelt, rainbow, raw") |
| `snapper` | Finfish | 3 | FDC 173698 ("Fish, snapper, mixed species, raw") |
| `spot` | Finfish | 2 | FDC 173700 ("Fish, spot, raw") |
| `squid` | Mollusk | 3 | FDC 171982 ("Mollusks, squid, mixed species, cooked, fried") |
| `sturgeon` | Finfish | 2 | FDC 173701 ("Fish, sturgeon, mixed species, raw") |
| `sucker` | Finfish | 2 | FDC 172002 ("Fish, sucker, white, cooked, dry heat") |
| `sunfish` | Finfish | 2 | FDC 172003 ("Fish, sunfish, pumpkin seed, cooked, dry heat") |
| `swordfish` | Finfish | 3 | FDC 173703 ("Fish, swordfish, raw") |
| `tilapia` | Finfish | 3 | FDC 175176 ("Fish, tilapia, raw") |
| `tilefish` | Finfish | 2 | FDC 173705 ("Fish, tilefish, raw") |
| `trout` | Finfish | 9 | FDC 172004 ("Fish, trout, mixed species, cooked, dry heat") |
| `tuna` | Finfish | 7 | FDC 172005 ("Fish, tuna, skipjack, fresh, cooked, dry heat") |
| `turbot` | Finfish | 2 | FDC 173710 ("Fish, turbot, european, raw") |
| `whelk` | Mollusk | 2 | FDC 171983 ("Mollusks, whelk, unspecified, raw") |
| `whitefish` | Finfish | 2 | FDC 173711 ("Fish, whitefish, mixed species, raw") |
| `whiting` | Finfish | 2 | FDC 173713 ("Fish, whiting, mixed species, raw") |
| `wolffish` | Finfish | 2 | FDC 174247 ("Fish, wolffish, Atlantic, cooked, dry heat") |
| `yellowtail` | Finfish | 2 | FDC 174248 ("Fish, yellowtail, mixed species, cooked, dry heat") |

## 5. Canonical Deduplication Decisions (A6)
Butchering cuts (fillets, steaks, loins, whole dressed fish, shrimp tails, squid tubes), species varieties (Atlantic vs Pacific cod, chinook vs coho vs sockeye salmon), and plain cooking methods (raw, dry heat, moist heat, steamed, baked) collapse into single canonical foods:

| Candidate Variety / Variant | Collapses To Canonical | Decision Basis |
|---|---|---|
| Atlantic cod, Pacific cod | `cod` | Regional species varieties of Gadus; same culinary fish |
| Chinook, coho, sockeye, pink, chum salmon | `salmon` | Species varieties of Oncorhynchus / Salmo; same culinary fish |
| Blue, dungeness, queen, snow crab, king crab | `crab` | Regional crustacean species; same culinary shellfish |
| Northern lobster, spiny lobster | `lobster` | Homarus vs Panulirus crustacean species; same culinary shellfish |
| Eastern oyster, Pacific oyster | `oyster` | Crassostrea species; same culinary bivalve |
| Bay scallop, sea scallop | `scallop` | Pectinidae species; same culinary bivalve |
| Yellowfin, skipjack, albacore, bluefin tuna | `tuna` | Thunnus species; same culinary fish |
| Rainbow trout, lake trout | `trout` | Oncorhynchus mykiss / Salvelinus namaycush; same culinary fish |

## 6. Synonym Candidates for Review
The following synonym candidates are surfaced from FDC descriptions and commercial cut trade names (not added to synonyms.csv):
- `salmon fillet` -> `salmon`
- `cod fillet` -> `cod`
- `tuna steak` -> `tuna`
- `halibut steak` -> `halibut`
- `calamari` -> `squid`
- `prawns` -> `shrimp`
- `dungeness crab` -> `crab`
- `snow crab` -> `crab`
- `blue crab` -> `crab`
- `sea scallops` -> `scallop`
- `bay scallops` -> `scallop`
