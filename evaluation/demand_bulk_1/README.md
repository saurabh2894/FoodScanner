# Demand Bulk 1: Staged Candidate Batch (Generation Only)

Status: **STAGED for senior review** (nothing merged into `src/foodscan/resources/lexicon.csv` or `synonyms.csv`).
Branch: `antigravity/demand-bulk-1` branched from `origin/main` at `d1bc5d5`.
Gate verdict: **READY_FOR_REVIEW** (`evaluation/demand_bulk_1/gate/gate_report.md`).
Flip proof: **0 flips** across all 66 frozen inputs evaluated in separate fresh processes (`evaluation/demand_bulk_1/flip_check/`).

---

## 1. Executive Summary and Counts

In accordance with ANTIGRAVITY TASK: demand-bulk-1, the top 40 open unassessed ingredient terms from `evaluation/demand_inventory_1/inventory.csv` (mined by `scripts/mine_unassessed.py --force`, excluding photo-only and noise items) were researched against the two authorized sources:
1. **FAO 2019 NOVA Report**: Monteiro et al., *Ultra-processed foods, diet quality, and health using the NOVA classification system*, FAO, Rome (`ca5644en.pdf`), Table 1 (p. 11) and Group 1 definitions (pp. 10–11).
2. **USDA FoodData Central (FDC)**: Foundation Foods (2026-10-29) and SR Legacy (2018-04) normalised candidates via `scripts/fdc_ingest.py` (CC0 1.0 Universal).

Each term was assigned exactly one disposition:
- **CANDIDATE**: 2 terms (`beans`, `cabbage`)
- **CONDITIONED (LABEL_BOUND)**: 9 terms (`minerals`, `vitamins`, `vitamins & mineral`, `wheat flour`, `apple juice`, `grape juice`, `orange juice`, `pineapple juice`, `corn flakes`)
- **PARK**: 29 terms
- **Total terms researched**: 40

---

## 2. Research and Disposition of the Top 40 Open Terms

| Rank | Term | Inputs | Input IDs | Raw Label Text Variants | Disposition | Verbatim Source Clause / Rationale |
|:---:|:---|:---:|:---|:---|:---:|:---|
| 1 | `cocoa solids` | 5 | b1/N01; b1/N06; dev15/F02; dev15/F04; dev15/F06 | COCOA SOLIDS (1%); Cocoa Solids (5.3%); cocoa solids; Cocoa solids (3.8%) | **PARK** | Fraction/derivative of cocoa bean; no FAO Group 1 unconditioned clause support; substances extracted from whole foods fall under Group 4. |
| 2 | `liquid glucose` | 5 | b1/N02; b1/N12; b2/M09; b2/M15; b3/Q14 | liquid glucose; LIQUID GLUCOSE; Liquid Glucose | **PARK** | Industrial starch hydrolysate / syrup; outside FAO Group 1 (NOVA Group 4 or processed culinary ingredient). |
| 3 | `spices & condiments` | 5 | b1/N04; b1/N12; b1/N13; b3/Q14; neg/R2 | Spices & Condiments; spices & condiments | **PARK** | Collective compound category header; 'condiments' includes prepared sauces, pickles, and seasonings outside unconditioned herbs and spices. |
| 4 | `wheat gluten` | 4 | b1/N16; b2/M10; dev15/F07; dev15/F08 | Wheat gluten; wheat gluten (0.4%); wheat gluten (0.07%); Wheat Gluten | **PARK** | Explicitly listed in FAO 2019 Table 1 Group 4 as an extracted food substance ('substances extracted from whole foods, such as casein, lactose, whey, gluten'). |
| 5 | `minerals` | 3 | b1/N16; b3/Q11; dev15/F02 | Minerals | **CONDITIONED** (LABEL_BOUND) | FAO 2019 Table 1 Group 1 p.11: *"foods with vitamins and minerals added generally to replace nutrients lost during processing, such as wheat or corn flour fortified with iron and folic acid"*. Conditioned by processing-loss replacement purpose; label cannot establish purpose; marked LABEL_BOUND per repo abstention policy. |
| 6 | `starch` | 3 | b1/N12; b3/Q14; dev15/F03 | Starch; starch | **PARK** | FAO Table 1 Group 2 culinary ingredient (*"starches extracted from corn and other plants"*) or Group 4 fraction; no Group 1 whole food support. |
| 7 | `carbonated water` | 3 | b2/M13; b3/Q13; neg/R6 | CARBONATED WATER; Carbonated water; Carbonated Water | **PARK** | Water with carbonating agents; FAO Table 1 Group 4 lists carbonating agents and soft drinks; outside plain drinking water. |
| 8 | `cocoa butter` | 2 | b1/N06; b1/N07 | COCOA BUTTER; cocoa butter (10%) | **PARK** | Extracted vegetable fat (FDC Fats and Oils category); FAO Table 1 Group 2/4, no Group 1 unconditioned whole food clause. |
| 9 | `yeast extract` | 2 | b1/N05; dev15/F07 | Yeast Extract; yeast extract | **PARK** | Industrial yeast hydrolysate/extract; FAO Table 1 Group 4 (*"hydrolysed proteins... flavour enhancers"*). |
| 10 | `cocoa powder` | 2 | b1/N14; b3/Q12 | Cocoa Powder (1.5%); Cocoa Powder (7%) | **PARK** | Processed cocoa bean fraction; FAO Group 1 limits powdered forms to milk, eggs, and herbs/spices; no unconditioned Group 1 clause. |
| 11 | `banana pulp` | 2 | b2/M14; dev15/F14 | BANANA PULP; banana pulp | **PARK** | Industrial fruit pulp preparation; outside FAO Group 1 unconditioned fresh/frozen/dried whole fruit clause. |
| 12 | `caffeine` | 2 | b2/M13; b3/Q13 | caffeine (13mg/100g); Caffeine | **PARK** | Isolated chemical alkaloid / additive; no FAO food clause support. |
| 13 | `mango pulp` | 2 | b2/M14; dev15/F14 | MANGO PULP; mango pulp | **PARK** | Industrial fruit pulp preparation; outside FAO Group 1 unconditioned fresh/frozen/dried whole fruit clause. |
| 14 | `papaya pulp` | 2 | b2/M14; dev15/F14 | PAPAYA PULP; papaya pulp | **PARK** | Industrial fruit pulp preparation; outside FAO Group 1 unconditioned fresh/frozen/dried whole fruit clause. |
| 15 | `pear pulp` | 2 | b2/M14; dev15/F14 | PEAR PULP; pear pulp | **PARK** | Industrial fruit pulp preparation; outside FAO Group 1 unconditioned fresh/frozen/dried whole fruit clause. |
| 16 | `tomato puree` | 2 | b1/N12; b3/Q14 | Tomato puree (67%); Tomato Puree (67%) | **PARK** | Processed/cooked canned tomato puree; outside unconditioned fresh/dried vegetable clause; classified under Group 3 processed foods in NOVA. |
| 17 | `vitamins` | 2 | b3/Q11; dev15/F02 | Vitamins | **CONDITIONED** (LABEL_BOUND) | FAO 2019 Table 1 Group 1 p.11: *"foods with vitamins and minerals added generally to replace nutrients lost during processing, such as wheat or corn flour fortified with iron and folic acid"*. Conditioned by purpose; label cannot establish purpose; marked LABEL_BOUND. |
| 18 | `vitamins & mineral` | 2 | b2/M14; dev15/F14 | VITAMINS & MINERAL; vitamins & mineral | **CONDITIONED** (LABEL_BOUND) | FAO 2019 Table 1 Group 1 p.11: *"foods with vitamins and minerals added generally to replace nutrients lost during processing, such as wheat or corn flour fortified with iron and folic acid"*. Conditioned by purpose; marked LABEL_BOUND. |
| 19 | `wheat flour` | 2 | b2/M09; dev15/F02 | Wheat Flour (Atta) (55.8%); WHEAT FLOUR (63%) | **CONDITIONED** (LABEL_BOUND) | FAO 2019 Table 1 Group 1 p.11: *"grits, flakes or flour made from corn, wheat, oats, or cassava"*. Cereal flour clause; project policy defines kind=flour as label-bound (mixed bread-like lists abstain); marked LABEL_BOUND. |
| 20 | `whey powder` | 2 | b1/N05; dev15/F06 | WHEY POWDER; Whey Powder | **PARK** | Explicitly listed in FAO 2019 Table 1 Group 4 as an extracted food substance (*"substances extracted from whole foods, such as casein, lactose, whey, gluten"*). |
| 21 | `tapioca starch` | 2 | b1/N03; b1/N05 | Tapioca Starch; tapioca starch | **PARK** | Extracted plant starch; FAO Table 1 Group 2 culinary ingredient (*"starches extracted from corn and other plants"*). |
| 22 | `apple juice` | 2 | b2/M14; dev15/F14 | APPLE JUICE; apple juice | **CONDITIONED** (LABEL_BOUND) | FAO 2019 Table 1 Group 1 p.11: *"fresh or pasteurized fruit or vegetable juices (with no added sugar, sweeteners or flavours)"*. Explicitly conditioned; bare term does not establish fresh/pasteurized vs reconstituted from concentrate (Group 4); marked LABEL_BOUND. |
| 23 | `grape juice` | 2 | b2/M14; dev15/F14 | GRAPE JUICE; grape juice | **CONDITIONED** (LABEL_BOUND) | FAO 2019 Table 1 Group 1 p.11: *"fresh or pasteurized fruit or vegetable juices (with no added sugar, sweeteners or flavours)"*. Conditioned clause; bare label term crosses Group 1 / Group 4 concentrate boundary; marked LABEL_BOUND. |
| 24 | `orange juice` | 2 | b2/M14; dev15/F14 | ORANGE JUICE; orange juice | **CONDITIONED** (LABEL_BOUND) | FAO 2019 Table 1 Group 1 p.11: *"fresh or pasteurized fruit or vegetable juices (with no added sugar, sweeteners or flavours)"*. Conditioned clause; bare label term crosses Group 1 / Group 4 concentrate boundary; marked LABEL_BOUND. |
| 25 | `pineapple juice` | 2 | b2/M14; dev15/F14 | PINEAPPLE JUICE; pineapple juice | **CONDITIONED** (LABEL_BOUND) | FAO 2019 Table 1 Group 1 p.11: *"fresh or pasteurized fruit or vegetable juices (with no added sugar, sweeteners or flavours)"*. Conditioned clause; bare label term crosses Group 1 / Group 4 concentrate boundary; marked LABEL_BOUND. |
| 26 | `maida` | 1 | dev15/F07 | maida (refined wheat flour) (78.7%); maida (refined wheat flour) (15.9%) | **PARK** | Vernacular Indian term for refined wheat flour not named in FAO; refined flours on mixed lists abstain; no unconditioned Group 1 clause. |
| 27 | `guar gum` | 1 | b1/N03 | guar gum | **PARK** | Food additive (thickener / stabilizer, INS 412); listed under FAO Table 1 Group 4 additive classes (*"thickeners... gelling and glazing agents"*). |
| 28 | `soya flour` | 1 | b1/N05 | Soya Flour (9%) | **PARK** | Industrial defatted/roasted legume flour; outside unconditioned Group 1 food clause; flours abstain/stay unmapped. |
| 29 | `cereal product` | 1 | b3/Q11 | Cereal product (3%) | **PARK** | Non-specific compound product description with no single commodity identity or FAO clause support. |
| 30 | `coriander cinnamon` | 1 | b2/M11 | CORIANDER. CINNAMON; CORIANDER CINNAMON | **PARK** | Delimiter-loss run-together pairing of two distinct spices (*coriander* and *cinnamon*); not a single ingredient. |
| 31 | `corn flakes` | 1 | dev15/F10 | Corn Flakes (6%) | **CONDITIONED** (LABEL_BOUND) | FAO 2019 Table 1 Group 1 p.11: *"grits, flakes or flour made from corn, wheat, oats, or cassava"*. Conditioned on plain (unflavoured/unsweetened) form; commercial corn flakes are ultra-processed formulations; pinned in `tests/test_vocabulary_layer.py:55`; marked LABEL_BOUND. |
| 32 | `dried mango black salt` | 1 | dev15/F10 | Dried Mango Black Salt; Dried Mango \| Black Salt | **PARK** | OCR delimiter-loss run-together phrase combining dried mango (fruit) and black salt (culinary); not a single commodity. |
| 33 | `rice flakes` | 1 | dev15/F10 | Rice Flakes (37%) | **PARK** | Rice is not named in the FAO cereal flakes clause (*"corn, wheat, oats, or cassava"*) and no commodity candidate exists in FDC Foundation or SR Legacy. |
| 34 | `roasted gram` | 1 | dev15/F10 | Roasted Gram (25%); Roasted Gram \| (25%) | **PARK** | No matching commodity candidate record in FDC Foundation or SR Legacy; lacks supply provenance. |
| 35 | `tomato paste` | 1 | b2/M12 | TOMATO PASTE (28°B) 24.7% | **PARK** | Concentrated cooked tomato paste; classified under Group 3 processed foods in NOVA, outside Group 1 unconditioned vegetables. |
| 36 | `active lactic culture and probiotic culture` | 1 | b1/N08 | Active Lactic Culture and Probiotic Culture (Bifidobacterium lactis & Lactobacillus acidophilus) | **PARK** | Compound label description naming microbial culture strains; no matching FAO food clause or FDC candidate. |
| 37 | `anlioxidant` | 1 | dev15/F03 | Anlioxidant (320) | **PARK** | OCR misspelling for 'antioxidant' (INS 320, BHA); additive class term, not a whole food. |
| 38 | `beans` | 1 | dev15/F07 | beans (9.5%) | **CANDIDATE** | FAO 2019 Table 1 Group 1 p.11: *"legumes such as beans, lentils, and chickpeas"*; exact term IS named by the clause; FDC Foundation id 2644281 and SR Legacy id 169961. |
| 39 | `brown rice flakes` | 1 | b1/N14 | Brown Rice Flakes | **PARK** | Rice flakes are not named in the FAO cereal flakes clause (*"corn, wheat, oats, or cassava"*) and have no candidate in FDC Foundation or SR Legacy. |
| 40 | `cabbage` | 1 | dev15/F07 | cabbage (3.8%) | **CANDIDATE** | FAO 2019 Table 1 Group 1 p.11: *"Fresh, squeezed, chilled, frozen, or dried fruit and leafy and root vegetables"*; covered as leafy vegetable; FDC SR Legacy id 169975 and Foundation id 2346407. |

---

## 3. Staged Candidate Rows (evaluation/demand_bulk_1/staged_rows.csv)

The 2 candidate terms are staged in `staged_rows.csv` following the exact schema of `evaluation/herb_spice_bulk_1/`:

| term | kind | source | fdc_ids | rule_id |
|:---|:---|:---|:---|:---|
| `beans` | `whole_food` | `PROVISIONAL: FAO 2019 (ca5644en.pdf) Table 1 Group 1 p.11 "legumes such as beans, lentils, and chickpeas"; exact term IS named by the clause; name from USDA FoodData Central (CC0 1.0): foundation FDC id 2644281 "Beans, cannellini, dry"; sr_legacy FDC id 169961 "Beans, snap, green, raw"` | `fdc_foundation:2644281;fdc_sr_legacy:169961` | `tier1-demand-bulk-1` |
| `cabbage` | `whole_food` | `PROVISIONAL: FAO 2019 (ca5644en.pdf) Table 1 Group 1 p.11 "Fresh, squeezed, chilled, frozen, or dried fruit and leafy and root vegetables"; exact term not named by the clause (covered as a leafy vegetable); name from USDA FoodData Central (CC0 1.0): sr_legacy FDC id 169975 "Cabbage, raw"; foundation FDC id 2346407 "Cabbage, green, raw"` | `fdc_sr_legacy:169975;fdc_foundation:2346407` | `tier1-demand-bulk-1` |

---

## 4. Gate Verification and Harness Proof

The batch was submitted to `scripts/validate_batch.py`:
```powershell
python scripts/validate_batch.py --staged evaluation/demand_bulk_1/staged_rows.csv \
  --decisions evaluation/demand_bulk_1/decisions.csv \
  --candidates evaluation/demand_bulk_1/candidates.csv \
  --out evaluation/demand_bulk_1/gate \
  --rule data/ingest/clause_tier1_demand_bulk_1.json \
  --force
```

### Gate Verdict: READY_FOR_REVIEW
- **Staged rows**: 2
- **Schema errors**: 0
- **Provenance errors**: 0
- **Duplicates**: 0
- **Policy errors**: 0
- **Parked / ambiguity queue**: 0
- **Ready rows**: 2 (`beans`, `cabbage`)
- **Blockers**: None (`[]`)
- **Harness proof**: separate processes, lexicon rows 135 -> 137; both staged terms recognized after; 0 recognized before.

---

## 5. Flip-Check Evidence (66 Frozen Inputs)

Executed across all 66 frozen paste inputs from the 5 evaluation directories (`fresh_batch_1`, `fresh_batch_2`, `fresh_batch_3`, `negation_addendum`, `dev_regression_15`):
- `group`: **0 changed** (0 of 66)
- `status`: **0 changed** (0 of 66)
- `drivers`: **0 changed** (0 of 66)
- `reason`: **0 changed** (0 of 66)
- `warnings`: **0 changed** (0 of 66)
- `ingredients`: **0 changed** (0 of 66)
- `ins_mappings`: **0 changed** (0 of 66)
- `unexplained changes`: **0**
- `flips`: **0**
- `unassessed`: **1 input changed** (`dev/F07`)

### Attributed unassessed drop on `dev/F07`:
- On `dev/F07` (instant noodles formulation), the raw ingredients text contains:
  `dehydrated vegetables [beans (9.5%), carrot (7.1%), onion (4.6%), cabbage (3.8%)]`
- Before this batch: `carrot` and `onion` were recognised; `beans (9.5%)` and `cabbage (3.8%)` were unassessed.
- After this batch: `beans` and `cabbage` are recognized as `whole_food` and removed from unassessed.
- Classification impact: `dev/F07` remains squarely NOVA Group 4 (driven by thickeners INS 508, 412, acidity regulators INS 501(i), 500(i), stabilizer INS 339(ii), and flavour enhancer INS 635).
- Zero group, status, or driver flips occurred.

---

## 6. Source Disagreements and Boundary Observations

1. **Juice Boundary (Bare Juice vs. Concentrate)**:
   FAO Table 1 Group 1 lists *"fresh or pasteurized fruit or vegetable juices (with no added sugar, sweeteners or flavours)"*, while pp. 9–10 list *"fruit juice concentrate"* among the markers of ultra-processed foods. A bare label term like `apple juice` on product `b2/M14` / `dev15/F14` does not declare whether it is fresh/pasteurized or reconstituted from industrial concentrate. Consistent with the cranberry precedent and the senior engineer's review in Lexicon 1 (commit `03f25af`), all juice terms remain held as **CONDITIONED (LABEL_BOUND)**.

2. **Cereal Flakes Formulation**:
   FAO Table 1 Group 1 lists *"grits, flakes or flour made from corn, wheat, oats, or cassava"*. However, commercially manufactured corn flakes (seen on `dev15/F10`) are frequently ultra-processed breakfast cereal formulations containing added sugar, malt extract, and flavourings. Bare `corn flakes` cannot be assumed to be plain, and `tests/test_vocabulary_layer.py:55` explicitly asserts `assert lookup("corn flakes") is None`. Thus, `corn flakes` remains **CONDITIONED (LABEL_BOUND)**.

3. **Flour Abstention Policy**:
   Although wheat flour is named in the cereal flour clause, project architectural policy assigns `kind=flour` to trigger abstention on mixed/bread-like lists. `wheat flour` is therefore maintained as **CONDITIONED (LABEL_BOUND)**.

4. **Rice Flakes**:
   Poha / flattened rice is an everyday staple in India (`dev15/F10`), but FAO's flakes clause explicitly restricts to *"corn, wheat, oats, or cassava"* (omitting rice), and FDC has no matching commodity candidate. Parked for lack of dual-source clause fit.

5. **Fruit Pulps and Purees**:
   Industrial pulps (`banana pulp`, `mango pulp`, `papaya pulp`, `pear pulp`) and purees (`tomato puree`) are pre-processed industrial preparations that often involve thermal concentration or preservative carriers. They fall outside the unconditioned fresh/frozen/dried whole fruit clause and are consistently parked.

6. **Extracted Fractions**:
   `wheat gluten`, `whey powder`, `tapioca starch`, `starch`, `cocoa butter`, and `liquid glucose` are explicitly characterized by FAO Table 1 as Group 2 culinary ingredients or Group 4 extracted/derived food substances. Parked without Group 1 admission.

---

## 7. Artifact Manifest

| File | Content |
|:---|:---|
| `candidates.csv` | FDC commodity candidates providing provenance for the staged candidate rows |
| `decisions.csv` | Explicit ACCEPT decisions with reason codes for each candidate record |
| `staged_rows.csv` | 2 staged candidate rows (`beans`, `cabbage`) in the standard schema |
| `README.md` | Full documentation of research, 40-term dispositions, gate verdict, and flip proof |
| `gate/gate_report.md`, `.json` | Validation gate report from `scripts/validate_batch.py` (READY_FOR_REVIEW) |
| `gate/lexicon_candidate_rows.csv` | Candidate rows in `lexicon.csv` column layout |
| `gate/synonyms_candidate_rows.csv` | Synonym candidates layout (empty for this batch) |
| `gate/ambiguity_queue.csv` | Ambiguity queue layout |
| `gate/flip_before.json`, `flip_after.json` | Dump artifacts from fresh-process harness execution |
| `flip_check/before.json`, `after.json` | Frozen inputs dumps from baseline and candidate builds |
| `flip_check/diff.json` | Exact per-input field diffs (1 unassessed drop on `dev/F07`, 0 flips) |
| `flip_check/README.md` | Summary of flip-check harness results |
