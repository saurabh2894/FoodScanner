# Batch 10 Candidate Staging: Plain Fish & Seafood (`class_bulk_10_fish_seafood_1`)

## 1. Summary & Staging Scope
- **Task**: Candidate staging for Batch 10 (plain fish and seafood) based on cached USDA FoodData Central (FDC) records and FAO 2019 NOVA definitions, cleaned and finalized under Task 14.
- **Role**: Generator/Researcher staging evidence and candidates for senior review (Claude). Zero changes to application source code, parser, classifier, or runtime resources (`lexicon.csv`, `synonyms.csv`, `markers.csv` untouched).
- **Branch**: `antigravity/class-bulk-10-fish-seafood`
- **Original Base Commit**: `46ad81c94757f92daaee0bf24c29d02f49965c07` (main HEAD)
- **Primary Handoff Unit**: `canonical_candidates.csv` (68 candidate rows, exactly 1 row per source-stated biological species identity).
- **Complete Provenance Map**: `record_dispositions.csv` (288 rows, exactly 1 row per cached in-scope FDC record).
- **Status**: COMPLETE; artifacts staged additions-only under `evaluation/class_bulk_10_fish_seafood_1/`.

---

## 2. Derivation & Tie-Out
All counts are strictly derived from the underlying CSV artifacts (`record_dispositions.csv`, `canonical_candidates.csv`, `accept_records.csv`, `queue.csv`, `reject.csv`):

| Measure | Count | Notes |
|---|---|---|
| **Total FDC records in scope** | **288** | Category exactly 'Finfish and Shellfish Products' (264 SR Legacy + 24 Foundation) |
| **ACCEPT (candidate records)** | **149** | Plain whole fish, fillets, steaks, crustaceans, and mollusks of specific source-stated biological species |
| **QUEUE (pending owner decision)** | **80** | Mixed/unspecified species (49), generic identity unstated (18), moisture additive warnings (5), rare species (3), roe/caviar (3), fried methods (2) |
| **REJECT (conditioned / out of scope)** | **59** | Canned fish (30), breaded/battered/sticks (9), smoked/kippered (8), salted/pickled (4), surimi (4), formulated dishes (4) |
| **Total Artifact Sum (Tie-Out)** | **288** | **EXACT TIE**: `candidates = accept (149) + queue (80) + reject (59)` |

### In-Scope Category Breakdown
- `Finfish and Shellfish Products`: 288 records (264 SR Legacy + 24 Foundation)

---

## 3. Evidence Corrections (Task 14)

1. **Exact Verbatim FAO Quotations**:
   - The continuous examples clause in Table 1 Group 1 p. 11 is quoted verbatim without splicing: `"meat, poultry, fish and seafood, whole or in the form of steaks, fillets and other cuts"`.
   - Leading thermal text (*"fresh, chilled or frozen"*) and trailing offal text (*"or offal"*) have been excised from the examples quotation.
2. **Observed Descriptors vs Absence of Ingredients**:
   - Blanket assertions of "no added salt/oil/additives" have been replaced with precise statements of observed physical attributes and explicit acknowledgment that SR Legacy commodity descriptors do not publish formal ingredient declarations; absence of additive terms in a descriptor confirms no declared additives in the name, but is not an ingredient-list guarantee.
3. **Generic & Unspecified Identities Queued**:
   - In accordance with the per-species candidate unit, 18 records that only state generic family, genus, or market categories without species resolution (generic pollock, shrimp, lobster tail, catfish, halibut, snapper, squid, conch, tilapia, carp, tilefish) have been moved to QUEUE under `queue_generic_unspecified_identity`.
   - Queen crab and Snow crab (*Chionoecetes opilio*) are reconciled under `snow crab` with candidate alias `queen crab`.
   - Exactly **68 distinct source-stated biological species candidates** are staged in `canonical_candidates.csv`.

---

## 4. Proposed Canonical Species Candidates (`canonical_candidates.csv`: 68 rows)

The 149 accepted plain records collapse into exactly 68 distinct biological species candidates:

| Category Sub-class | Count | Example Species Candidates |
|---|---|---|
| **Salmonids** | 8 | `atlantic salmon`, `chinook salmon`, `coho salmon`, `sockeye salmon`, `pink salmon`, `chum salmon`, `rainbow trout`, `brook trout` |
| **Gadoids (Cods & Pollocks)** | 4 | `atlantic cod`, `pacific cod`, `atlantic pollock`, `alaska pollock` |
| **Scombroids (Tunas & Mackerels)** | 6 | `bluefin tuna`, `yellowfin tuna`, `skipjack tuna`, `atlantic mackerel`, `spanish mackerel`, `king mackerel` |
| **Clupeoids (Herrings & Anchovies)** | 4 | `atlantic herring`, `pacific herring`, `european anchovy`, `american shad` |
| **Crustaceans (Crabs, Lobsters)** | 6 | `blue crab`, `dungeness crab`, `alaska king crab`, `snow crab` (alias: `queen crab`), `blue swimming crab`, `northern lobster` |
| **Mollusks (Oysters, Mussels, Octopuses, Scallops)** | 6 | `eastern oyster`, `pacific oyster`, `blue mussel`, `common octopus`, `sea scallop`, `patagonian bay scallop` |
| **Other Freshwater & Marine Finfish** | 34 | `striped bass`, `chilean sea bass`, `bluefish`, `burbot`, `butterfish`, `channel catfish`, `cisco`, `cusk`, `freshwater drum`, `haddock`, `greenland halibut`, `ling`, `lingcod`, `mahimahi`, `milkfish`, `monkfish`, `striped mullet`, `atlantic ocean perch`, `northern pike`, `walleye pike`, `florida pompano`, `ocean pout`, `orange roughy`, `sablefish`, `scup`, `sheepshead`, `rainbow smelt`, `spot croaker`, `atlantic croaker`, `white sucker`, `pumpkinseed sunfish`, `swordfish`, `european turbot`, `atlantic wolffish` |

- **Already covered in lexicon.csv**: 0 (zero fish/seafood terms exist in `lexicon.csv`)
- **Genuinely new biological species proposals**: 68
- **Variant/synonym candidates**: Surfaced purely as candidate aliases in `canonical_candidates.csv`; `synonyms.csv` is not modified.

---

## 5. Queue Breakdown (80 rows)
- `queue_mixed_species`: **49 rows** (records explicitly stating mixed species, multiple species, or unstated biological identity; e.g. clam mixed species, grouper mixed species, flatfish flounder and sole, crayfish mixed species).
- `queue_generic_unspecified_identity`: **18 rows** (records with generic market or family terms lacking specific species resolution: generic pollock, shrimp, lobster tail, catfish, halibut, snapper, squid, conch, tilapia, carp, tilefish).
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
