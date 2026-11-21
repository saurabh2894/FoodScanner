# Batch 10 Candidate Staging: Plain Fish & Seafood (`class_bulk_10_fish_seafood_1`)

## 1. Summary & Staging Scope
- **Task**: Candidate staging for Batch 10 (plain fish and seafood) based on cached USDA FoodData Central (FDC) records and FAO 2019 NOVA definitions, repaired under Task 13.
- **Role**: Generator/Researcher staging evidence and candidates for senior review (Claude). Zero changes to application source code, parser, classifier, or runtime resources (`lexicon.csv`, `synonyms.csv`, `markers.csv` untouched).
- **Branch**: `antigravity/class-bulk-10-fish-seafood`
- **Original Base Commit**: `46ad81c94757f92daaee0bf24c29d02f49965c07` (main HEAD)
- **Primary Handoff Unit**: `canonical_candidates.csv` (80 candidate rows, exactly 1 row per source-stated species identity).
- **Complete Provenance Map**: `record_dispositions.csv` (288 rows, exactly 1 row per cached in-scope FDC record).
- **Status**: COMPLETE; artifacts staged additions-only under `evaluation/class_bulk_10_fish_seafood_1/`.

---

## 2. Derivation & Tie-Out
All counts are strictly derived from the underlying CSV artifacts (`record_dispositions.csv`, `canonical_candidates.csv`, `accept_records.csv`, `queue.csv`, `reject.csv`):

| Measure | Count | Notes |
|---|---|---|
| **Total FDC records in scope** | **288** | Category exactly 'Finfish and Shellfish Products' (264 SR Legacy + 24 Foundation) |
| **ACCEPT (candidate records)** | **167** | Plain whole fish, fillets, steaks, crustaceans, and mollusks of specific source-stated species |
| **QUEUE (pending owner decision)** | **62** | Mixed/unspecified species (49), moisture additive warnings (5), rare species (3), roe/caviar (3), fried methods (2) |
| **REJECT (conditioned / out of scope)** | **59** | Canned fish (30), breaded/battered/sticks (9), smoked/kippered (8), salted/pickled (4), surimi (4), formulated dishes (4) |
| **Total Artifact Sum (Tie-Out)** | **288** | **EXACT TIE**: `candidates = accept (167) + queue (62) + reject (59)` |

### In-Scope Category Breakdown
- `Finfish and Shellfish Products`: 288 records (264 SR Legacy + 24 Foundation)

---

## 3. Task 13 Staging Repairs & Guard Enforcements

1. **Primary Review Handoff**: `canonical_candidates.csv` is now the concise primary review artifact (80 candidate rows). `accept_records.csv` (167 rows) is retained for full transparency as a record-level mapping, and `record_dispositions.csv` (288 rows) provides a single deterministic map of every in-scope category record.
2. **Species Identity as Candidate Unit**: Biologically distinct fish are no longer collapsed under broad culinary buckets. For instance, Pacific and Atlantic species (Atlantic salmon, Chinook salmon, Coho salmon, Sockeye salmon, Pink salmon, Chum salmon) are staged as distinct species candidates rather than merged into a single generic "salmon" label.
3. **Explicit Mixed Species Preserved in Queue**: 49 records where the FDC description explicitly states `mixed species` or multiple species (e.g. `Fish, grouper, mixed species`, `Mollusks, clam, mixed species`, `Fish, flatfish (flounder and sole species)`) are preserved explicitly and placed in QUEUE under `queue_mixed_species`. No species identity is invented or collapsed from generic group names.
4. **Smoked & Kippered Isolation**: `Fish, herring, Atlantic, kippered` (FDC 173668) and 7 smoked fish records are rejected under `smoked_cured`.
5. **Cooking Methods with Added Fat**: `Mollusks, squid, mixed species, cooked, fried` (FDC 171982) and `Mollusks, abalone, mixed species, cooked, fried` (FDC 174213) are isolated to QUEUE under `queue_cooking_added_fat`.
6. **Preformed / Breaded Products**: Preformed frozen fish sticks (FDC 174195) and breaded/batter-dipped cuts are rejected under `breaded_battered_fried`.

---

## 4. Proposed Canonical Species Candidates (`canonical_candidates.csv`: 80 rows)

The 167 accepted plain records collapse into exactly 80 distinct biological species candidates:

| Category Sub-class | Count | Example Species Candidates |
|---|---|---|
| **Salmonids** | 8 | `atlantic salmon`, `chinook salmon`, `coho salmon`, `sockeye salmon`, `pink salmon`, `chum salmon`, `rainbow trout`, `brook trout` |
| **Gadoids (Cods & Pollocks)** | 5 | `atlantic cod`, `pacific cod`, `atlantic pollock`, `alaska pollock`, `pollock` |
| **Scombroids (Tunas & Mackerels)** | 6 | `bluefin tuna`, `yellowfin tuna`, `skipjack tuna`, `atlantic mackerel`, `spanish mackerel`, `king mackerel` |
| **Clupeoids (Herrings & Anchovies)** | 4 | `atlantic herring`, `pacific herring`, `european anchovy`, `american shad` |
| **Crustaceans (Crabs, Lobsters, Shrimps)** | 9 | `blue crab`, `dungeness crab`, `alaska king crab`, `queen crab`, `snow crab`, `blue swimming crab`, `northern lobster`, `lobster`, `shrimp` |
| **Mollusks (Oysters, Mussels, Octopuses, Scallops)** | 9 | `eastern oyster`, `pacific oyster`, `blue mussel`, `common octopus`, `sea scallop`, `patagonian bay scallop`, `conch`, `squid` |
| **Other Freshwater & Marine Finfish** | 39 | `striped bass`, `chilean sea bass`, `bluefish`, `burbot`, `butterfish`, `common carp`, `cisco`, `cusk`, `freshwater drum`, `haddock`, `greenland halibut`, `halibut`, `ling`, `lingcod`, `mahimahi`, `milkfish`, `monkfish`, `striped mullet`, `atlantic ocean perch`, `northern pike`, `walleye pike`, `florida pompano`, `ocean pout`, `orange roughy`, `sablefish`, `scup`, `sheepshead`, `rainbow smelt`, `spot croaker`, `atlantic croaker`, `white sucker`, `pumpkinseed sunfish`, `swordfish`, `tilapia`, `tilefish`, `european turbot`, `atlantic wolffish`, `snapper`, `catfish`, `channel catfish` |

- **Already covered in lexicon.csv**: 0 (zero fish/seafood terms exist in `lexicon.csv`)
- **Genuinely new species proposals**: 80
- **Variant/synonym candidates**: Surfaced purely as candidate aliases in `canonical_candidates.csv`; `synonyms.csv` is not modified.

---

## 5. Queue Breakdown (62 rows)
- `queue_mixed_species`: **49 rows** (records explicitly stating mixed species, multiple species, or unstated biological identity; e.g. clam mixed species, grouper mixed species, flatfish flounder and sole, crayfish mixed species, snapper mixed species, trout mixed species).
- `plain_form_not_stated`: **5 rows** (explicit warning: `may contain additives to retain moisture`).
- `queue_rare_species`: **3 rows** (green turtle, frog legs, terrestrial snail).
- `queue_roe_special`: **3 rows** (sturgeon caviar, mixed fish roe).
- `queue_cooking_added_fat`: **2 rows** (fried squid, fried abalone).

---

## 6. Reject Breakdown (59 rows)
- `canned_fish`: **30 rows** (tuna canned in water/oil, canned salmon, sardines in oil/tomato sauce, canned shrimp/clams/crab).
- `breaded_battered_fried`: **9 rows** (breaded fish cuts, croaker, fish sticks, portions).
- `smoked_cured`: **8 rows** (kippered herring, smoked salmon lox, smoked cisco, smoked whitefish, smoked haddock, smoked sturgeon).
- `salted_pickled`: **4 rows** (salted jellyfish, salted mackerel, pickled herring, cod in brine).
- `surimi_imitation`: **4 rows** (imitation shrimp, imitation king crab, imitation blue crab, surimi block).
- `formulated_prepared`: **4 rows** (gefilte fish sweet recipe, crab cakes, tuna salad, salmon nuggets).
