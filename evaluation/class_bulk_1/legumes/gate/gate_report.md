# Gate report: class-legumes-1

**Verdict: READY_FOR_REVIEW**

Nothing was merged. `lexicon_candidate_rows.csv` holds the ready rows in lexicon.csv layout and `synonyms_candidate_rows.csv` the synonym candidates in synonyms.csv layout, for review.

| Check | Result |
|---|---|
| staged rows | 26 |
| schema errors | 0 |
| provenance errors | 0 |
| duplicates (exact, synonym, already recognised) | 5 |
| variants of an existing term (informational) | 19 |
| parked in the ambiguity queue | 31 (Counter({'clause_tier': 31})) |
| ready rows (new lexicon rows) | 21 |
| synonym candidates (variant policy variant-policy-class-legumes-1) | 0 |
| policy errors | 0 |
| verbatim clause vs FAO text | PASS |
| harness proof (separate processes) | lexicon rows 160 -> 181; all 21 staged terms recognised after; 0 already recognised before |
| flip check (66 frozen inputs, before and after in separate fresh processes) | group 0, drivers 0, status 0, reason 0, warnings 0, ingredients 0, unassessed 0, ins_mappings 0 |
| group/status/driver flips | 0  |
| unexplained changes | 0 |

## Ready rows (new lexicon rows)

- `adzuki beans`: separate row because a named bean species or market class (FDC names it as its own food); the bare generic row 'beans' is left untouched and not widened
- `black beans`: separate row because a named bean species or market class (FDC names it as its own food); the bare generic row 'beans' is left untouched and not widened
- `broadbeans`
- `cannellini beans`: separate row because a named bean species or market class (FDC names it as its own food); the bare generic row 'beans' is left untouched and not widened
- `carioca beans`: separate row because a named bean species or market class (FDC names it as its own food); the bare generic row 'beans' is left untouched and not widened
- `cowpeas`
- `cranberry beans`: separate row because a named bean species or market class (FDC names it as its own food); the bare generic row 'beans' is left untouched and not widened
- `flor de mayo beans`: separate row because a named bean species or market class (FDC names it as its own food); the bare generic row 'beans' is left untouched and not widened
- `great northern beans`: separate row because a named bean species or market class (FDC names it as its own food); the bare generic row 'beans' is left untouched and not widened
- `hyacinth beans`: separate row because a named bean species or market class (FDC names it as its own food); the bare generic row 'beans' is left untouched and not widened
- `kidney beans`: separate row because a named bean species or market class (FDC names it as its own food); the bare generic row 'beans' is left untouched and not widened
- `lima beans`: separate row because a named bean species or market class (FDC names it as its own food); the bare generic row 'beans' is left untouched and not widened
- `lupins`
- `mothbeans`
- `navy beans`: separate row because a named bean species or market class (FDC names it as its own food); the bare generic row 'beans' is left untouched and not widened
- `pigeon peas`: separate row because a named pulse (red gram), not the generic 'peas' row (a vegetable-style term), which is left untouched
- `pink beans`: separate row because a named bean species or market class (FDC names it as its own food); the bare generic row 'beans' is left untouched and not widened
- `pinto beans`: separate row because a named bean species or market class (FDC names it as its own food); the bare generic row 'beans' is left untouched and not widened
- `small white beans`: separate row because a named bean species or market class (FDC names it as its own food); the bare generic row 'beans' is left untouched and not widened
- `winged beans`: separate row because a named bean species or market class (FDC names it as its own food); the bare generic row 'beans' is left untouched and not widened
- `yardlong beans`: separate row because a named bean species or market class (FDC names it as its own food); the bare generic row 'beans' is left untouched and not widened

## Synonym candidates (variant policy: same ingredient, plant part and form)


## Duplicates (excluded: already covered)

- `chickpeas`: already recognised by this build (descriptors, plurals or synonyms)
- `lentils`: already recognised by this build (descriptors, plurals or synonyms)
- `mung beans`: synonyms.csv alias of 'moong dal'
- `soybeans`: synonyms.csv alias of 'soybean'
- `split green peas`: already recognised by this build (descriptors, plurals or synonyms)

## Variants of existing terms (kept; informational)

- `adzuki beans` ~ ['beans']
- `black beans` ~ ['beans']
- `cannellini beans` ~ ['beans']
- `carioca beans` ~ ['beans']
- `cranberry beans` ~ ['beans']
- `flor de mayo beans` ~ ['beans']
- `great northern beans` ~ ['beans']
- `hyacinth beans` ~ ['beans']
- `kidney beans` ~ ['beans']
- `lima beans` ~ ['beans']
- `navy beans` ~ ['beans']
- `pigeon peas` ~ ['peas']
- `pink beans` ~ ['beans']
- `pinto beans` ~ ['beans']
- `small white beans` ~ ['beans']
- `winged beans` ~ ['beans']
- `yardlong beans` ~ ['beans']

## Ambiguity queue (parked, never included)

- `brown beans` (clause_tier, generic_name): A bare colour or pod-versus-seed name does not establish a distinct food: 'brown/tan/light tan/red/small red/medium red beans' are Foundation market-class colour labels of Phaseolus vulgaris; 'french beans' and 'yellow beans' on an Indian label usually denote the fresh pod (a vegetable); 'white beans' is a generic of cannellini/navy/great northern. QUEUE (conditional on a label that names the food).
- `tan beans` (clause_tier, generic_name): A bare colour or pod-versus-seed name does not establish a distinct food: 'brown/tan/light tan/red/small red/medium red beans' are Foundation market-class colour labels of Phaseolus vulgaris; 'french beans' and 'yellow beans' on an Indian label usually denote the fresh pod (a vegetable); 'white beans' is a generic of cannellini/navy/great northern. QUEUE (conditional on a label that names the food).
- `small red beans` (clause_tier, generic_name): A bare colour or pod-versus-seed name does not establish a distinct food: 'brown/tan/light tan/red/small red/medium red beans' are Foundation market-class colour labels of Phaseolus vulgaris; 'french beans' and 'yellow beans' on an Indian label usually denote the fresh pod (a vegetable); 'white beans' is a generic of cannellini/navy/great northern. QUEUE (conditional on a label that names the food).
- `medium red beans` (clause_tier, generic_name): A bare colour or pod-versus-seed name does not establish a distinct food: 'brown/tan/light tan/red/small red/medium red beans' are Foundation market-class colour labels of Phaseolus vulgaris; 'french beans' and 'yellow beans' on an Indian label usually denote the fresh pod (a vegetable); 'white beans' is a generic of cannellini/navy/great northern. QUEUE (conditional on a label that names the food).
- `light tan beans` (clause_tier, generic_name): A bare colour or pod-versus-seed name does not establish a distinct food: 'brown/tan/light tan/red/small red/medium red beans' are Foundation market-class colour labels of Phaseolus vulgaris; 'french beans' and 'yellow beans' on an Indian label usually denote the fresh pod (a vegetable); 'white beans' is a generic of cannellini/navy/great northern. QUEUE (conditional on a label that names the food).
- `red beans` (clause_tier, generic_name): A bare colour or pod-versus-seed name does not establish a distinct food: 'brown/tan/light tan/red/small red/medium red beans' are Foundation market-class colour labels of Phaseolus vulgaris; 'french beans' and 'yellow beans' on an Indian label usually denote the fresh pod (a vegetable); 'white beans' is a generic of cannellini/navy/great northern. QUEUE (conditional on a label that names the food).
- `medium red beans` (clause_tier, generic_name): A bare colour or pod-versus-seed name does not establish a distinct food: 'brown/tan/light tan/red/small red/medium red beans' are Foundation market-class colour labels of Phaseolus vulgaris; 'french beans' and 'yellow beans' on an Indian label usually denote the fresh pod (a vegetable); 'white beans' is a generic of cannellini/navy/great northern. QUEUE (conditional on a label that names the food).
- `red beans` (clause_tier, generic_name): A bare colour or pod-versus-seed name does not establish a distinct food: 'brown/tan/light tan/red/small red/medium red beans' are Foundation market-class colour labels of Phaseolus vulgaris; 'french beans' and 'yellow beans' on an Indian label usually denote the fresh pod (a vegetable); 'white beans' is a generic of cannellini/navy/great northern. QUEUE (conditional on a label that names the food).
- `brown beans` (clause_tier, generic_name): A bare colour or pod-versus-seed name does not establish a distinct food: 'brown/tan/light tan/red/small red/medium red beans' are Foundation market-class colour labels of Phaseolus vulgaris; 'french beans' and 'yellow beans' on an Indian label usually denote the fresh pod (a vegetable); 'white beans' is a generic of cannellini/navy/great northern. QUEUE (conditional on a label that names the food).
- `tan beans` (clause_tier, generic_name): A bare colour or pod-versus-seed name does not establish a distinct food: 'brown/tan/light tan/red/small red/medium red beans' are Foundation market-class colour labels of Phaseolus vulgaris; 'french beans' and 'yellow beans' on an Indian label usually denote the fresh pod (a vegetable); 'white beans' is a generic of cannellini/navy/great northern. QUEUE (conditional on a label that names the food).
- `light tan beans` (clause_tier, generic_name): A bare colour or pod-versus-seed name does not establish a distinct food: 'brown/tan/light tan/red/small red/medium red beans' are Foundation market-class colour labels of Phaseolus vulgaris; 'french beans' and 'yellow beans' on an Indian label usually denote the fresh pod (a vegetable); 'white beans' is a generic of cannellini/navy/great northern. QUEUE (conditional on a label that names the food).
- `small red beans` (clause_tier, generic_name): A bare colour or pod-versus-seed name does not establish a distinct food: 'brown/tan/light tan/red/small red/medium red beans' are Foundation market-class colour labels of Phaseolus vulgaris; 'french beans' and 'yellow beans' on an Indian label usually denote the fresh pod (a vegetable); 'white beans' is a generic of cannellini/navy/great northern. QUEUE (conditional on a label that names the food).
- `Flour, soy, defatted` (clause_tier, queue_flour): a flour is placed by the 'flours' class (PMC10127522 fn2, NUPENS), not by the legumes clause; kind flour belongs to the flour batch (Cereal Grains and Pasta: plain flours).
- `Flour, soy, full-fat` (clause_tier, queue_flour): a flour is placed by the 'flours' class (PMC10127522 fn2, NUPENS), not by the legumes clause; kind flour belongs to the flour batch (Cereal Grains and Pasta: plain flours).
- `Peanuts, raw` (clause_tier, queue_peanuts): same as peanut
- `Peanuts, all types, raw` (clause_tier, queue_peanuts): same as peanut
- `Peanuts, valencia, raw` (clause_tier, queue_peanuts): same as peanut
- `Peanuts, virginia, raw` (clause_tier, queue_peanuts): same as peanut
- `Soy flour, low-fat` (clause_tier, queue_flour): a flour is placed by the 'flours' class (PMC10127522 fn2, NUPENS), not by the legumes clause; kind flour belongs to the flour batch (Cereal Grains and Pasta: plain flours).
- `Soy meal, defatted, raw` (clause_tier, queue_meal): defatted/ground fraction: not established as a plain flour or a whole legume.
- `french beans` (clause_tier, generic_name): A bare colour or pod-versus-seed name does not establish a distinct food: 'brown/tan/light tan/red/small red/medium red beans' are Foundation market-class colour labels of Phaseolus vulgaris; 'french beans' and 'yellow beans' on an Indian label usually denote the fresh pod (a vegetable); 'white beans' is a generic of cannellini/navy/great northern. QUEUE (conditional on a label that names the food).
- `yellow beans` (clause_tier, generic_name): A bare colour or pod-versus-seed name does not establish a distinct food: 'brown/tan/light tan/red/small red/medium red beans' are Foundation market-class colour labels of Phaseolus vulgaris; 'french beans' and 'yellow beans' on an Indian label usually denote the fresh pod (a vegetable); 'white beans' is a generic of cannellini/navy/great northern. QUEUE (conditional on a label that names the food).
- `Carob flour` (clause_tier, queue_flour): a flour is placed by the 'flours' class (PMC10127522 fn2, NUPENS), not by the legumes clause; kind flour belongs to the flour batch (Cereal Grains and Pasta: plain flours).
- `mungo beans` (clause_tier, dedupe_stays_out): 'mungo' vs 'mung' beans: the FDC record does not establish which pulse a label word means (black gram vs green gram); stays out
- `Peanuts, spanish, raw` (clause_tier, queue_peanuts): same as peanut
- `Peanut flour, defatted` (clause_tier, queue_peanut): overlaps the CONDITIONED FAO nuts/seeds clause ('tree and ground nuts and other oily seeds (with no added salt or sugar)'); FDC files peanuts under Legumes. Boundary and kind (nut_seed) belong to the Nut and Seed batch.
- `Soy flour, full-fat, raw` (clause_tier, queue_flour): a flour is placed by the 'flours' class (PMC10127522 fn2, NUPENS), not by the legumes clause; kind flour belongs to the flour batch (Cereal Grains and Pasta: plain flours).
- `Soy flour, defatted` (clause_tier, queue_flour): a flour is placed by the 'flours' class (PMC10127522 fn2, NUPENS), not by the legumes clause; kind flour belongs to the flour batch (Cereal Grains and Pasta: plain flours).
- `Chickpea flour (besan)` (clause_tier, queue_flour): a flour is placed by the 'flours' class (PMC10127522 fn2, NUPENS), not by the legumes clause; kind flour belongs to the flour batch (Cereal Grains and Pasta: plain flours).
- `white beans` (clause_tier, generic_name): A bare colour or pod-versus-seed name does not establish a distinct food: 'brown/tan/light tan/red/small red/medium red beans' are Foundation market-class colour labels of Phaseolus vulgaris; 'french beans' and 'yellow beans' on an Indian label usually denote the fresh pod (a vegetable); 'white beans' is a generic of cannellini/navy/great northern. QUEUE (conditional on a label that names the food).
- `catjang cowpeas` (clause_tier, dedupe_stays_out): subspecies distinction (catjang) is not established as a label term; stays out rather than inflating the lexicon

## Unassessed drops attributed to ready rows

