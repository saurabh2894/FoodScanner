# Internal-Source Mapping Audit 1: Primary Evidence Behind 117 Internal Rows

## Executive Summary

During Provenance Audit 1, **117 classification-bearing rows** (87 in `lexicon.csv` and 30 in `markers.csv`) were segregated as citing internal research notes (`research/02`, `research/04`, provisional author seeds, or FSSAI dairy standards) rather than primary peer-reviewed or intergovernmental NOVA literature.

This audit maps each of the 117 internal-source rows against admissible primary authorities:
1. **FAO 2019 Report (`ca5644en.pdf`)**: Official intergovernmental NOVA standard (SHA-256 `c8024c194a8294a0355759877712ea7f61d4da62efc4dec46f3889821b19ceff`).
2. **Monteiro et al. 2019 Identification Paper** (*Public Health Nutrition* 22(5):936–941; unverified licence: paraphrased and cited only).
3. **NUPENS/USP Public Classification Pages** (University of São Paulo).
4. **WHO JECFA Additive Database** (Technological functional classes).
5. **USDA FoodData Central (Foundation & SR Legacy, CC0)**: Commodity naming and form evidence only (never classification authority).

All 117 rows have been mapped and recorded in `evaluation/internal_source_map_1/map.csv`.

---

## 1. Summary Counts by Support Type

| Support Type | Definition | Markers (`markers.csv`) | Lexicon (`lexicon.csv`) | Total Rows | Share |
|---|---|:---:|:---:|:---:|:---:|
| **verbatim clause available** | Primary source (`ca5644en.pdf`) explicitly names the exact term or a clear grammatical synonym/variant | 21 | 28 | **49** | 41.9% |
| **paraphrase-only licence** | Named in unverified-licence primary literature (Monteiro 2019, Martinez-Steele 2022, NUPENS/USP) | 3 | 1 | **4** | 3.4% |
| **naming-only** | Named in USDA FoodData Central (CC0) or JECFA, but NOVA group placement is an author inference | 4 | 31 | **35** | 29.9% |
| **NOT FOUND** | No admissible primary source or CC0 commodity database names this term | 2 | 27 | **29** | 24.8% |
| **Total** | | **30** | **87** | **117** | **100.0%** |

---

## 2. The NOT FOUND List (29 Rows — Urgent Candidates for Retirement)

These 29 terms have **no backing** in admissible primary NOVA literature, WHO JECFA, or USDA FoodData Central. They originated as provisional author seeds, unverified Indian market terms, or FSSAI regulatory imports (which cannot decide NOVA classification). They are prime candidates for deletion or re-scoping.

### A. Marker Classes (2 rows in `markers.csv`)
1. **`firming`** (`marker_class: cosmetic_additive`):
   - *Current claim*: `research/02 marker class 2 (cosmetic processing aids)`
   - *Audit Finding*: **NOT FOUND in any primary NOVA source**. FAO 2019 `ca5644en.pdf` never mentions firming agents in its 44 pages. Monteiro et al. 2019 abstract does not list firming agents among ultra-processed additive classes. Only JECFA lists "firming agent" as a technological functional class (e.g. for potassium chloride). Its status as an ultra-processing cosmetic marker is ungrounded.
2. **`humectant`** (`marker_class: cosmetic_additive`):
   - *Current claim*: `research/02 marker class 2 (cosmetic processing aids)`
   - *Audit Finding*: **NOT FOUND in any primary NOVA source**. Absent from FAO 2019 `ca5644en.pdf` and Monteiro et al. 2019. NUPENS-USP mentions "anti-humectants in salt" under Group 2 (culinary ingredients), directly contradicting a Group 4 cosmetic marker classification.

### B. Traditional Indian Dals & Pulses (7 rows in `lexicon.csv`)
1. `toor dal` (`kind: whole_food`): Pigeon pea dal. Not in FAO 2019 or USDA FDC.
2. `moong dal` (`kind: whole_food`): Mung bean dal. Not in FAO 2019 or USDA FDC.
3. `chana dal` (`kind: whole_food`): Split chickpea dal. Not in FAO 2019 or USDA FDC.
4. `masoor dal` (`kind: whole_food`): Red lentil dal. Not in FAO 2019 or USDA FDC.
5. `urad dal` (`kind: whole_food`): Black gram dal. Not in FAO 2019 or USDA FDC.
6. `rajma` (`kind: whole_food`): Kidney beans. Not in FAO 2019 or USDA FDC.
7. `moong` (`kind: whole_food`): Whole mung bean. Not in FAO 2019 or USDA FDC.

*Note*: While FAO 2019 Table 1 Group 1 names `"legumes such as beans, lentils, and chickpeas"`, these specific Indian market terms represent silent class-to-instance mappings with no primary source naming.

### C. Traditional Indian Grains & Millets (4 rows in `lexicon.csv`)
1. `ragi` (`kind: whole_food`): Finger millet. Not named in FAO 2019 or USDA FDC.
2. `jowar` (`kind: whole_food`): Sorghum grain. Not named in FAO 2019 or USDA FDC.
3. `bajra` (`kind: whole_food`): Pearl millet grain. Not named in FAO 2019 or USDA FDC.
4. `foxtail millet` (`kind: whole_food`): Not named in FAO 2019 or USDA FDC.

### D. Indian Culinary Ingredients & Oils (5 rows in `lexicon.csv`)
1. `mustard oil` (`kind: culinary`): Not named in FAO 2019 or USDA FDC.
2. `rice bran oil` (`kind: culinary`): Not named in FAO 2019 or USDA FDC.
3. `palmolein` (`kind: culinary`): Liquid fraction of palm oil. Not in FAO 2019 or USDA FDC.
4. `jaggery` (`kind: culinary`): Unrefined cane/palm sugar. Not named in FAO 2019 or USDA FDC.
5. `black salt` (`kind: culinary`): Kala namak. Not named in FAO 2019 or USDA FDC.

### E. Indian Spices (1 row in `lexicon.csv`)
1. `asafoetida` (`kind: herb_spice`): Hing. Not named in FAO 2019 or USDA FDC.

### F. Dairy Variants & Starter Cultures (8 rows in `lexicon.csv`)
1. `toned milk` (`kind: whole_food`): Standardized milk (3.0% fat / 8.5% SNF). Not in FAO 2019 or USDA FDC.
2. `double toned milk` (`kind: whole_food`): Standardized milk (1.5% fat / 9.0% SNF). Not in FAO 2019 or USDA FDC.
3. `buffalo milk` (`kind: whole_food`): Species-identified milk. Not in FAO 2019 or USDA FDC.
4. `dahi` (`kind: whole_food`): Fermented milk. Not named in FAO 2019 or USDA FDC (FAO names "plain yoghurt").
5. `starter culture` (`kind: culture`): Not named in FAO 2019 or USDA FDC.
6. `lactic culture` (`kind: culture`): Not named in FAO 2019 or USDA FDC.
7. `live culture` (`kind: culture`): Not named in FAO 2019 or USDA FDC.
8. `active culture` (`kind: culture`): Not named in FAO 2019 or USDA FDC.
9. `yoghurt culture` (`kind: culture`): Not named in FAO 2019 or USDA FDC.
10. `active lactic culture` (`kind: culture`): Not named in FAO 2019 or USDA FDC.

---

## 3. Suspected-Wrong List (Contradictions & Substantive Conflicts)

The following rows exhibit direct contradictions or substantive classification conflicts between repository rules and primary authorities:

### 1. `452(i)` — Sodium Polyphosphate (`src/foodscan/resources/ins_map.csv`)
- **Repo State**: `functional_class: stabiliser`, `strength: unlisted`
- **Repo Claim**: `"its functional classes are in no research/02 marker list, so it never decides a group"`
- **Primary Source Evidence**:
  - **WHO JECFA Database (ID 4669)**: Functional classes are `EMULSIFIER; SEQUESTRANT; TEXTURIZER; THICKENER`.
  - **Codex CXG 36-1989**: `acidity regulator; emulsifier; emulsifying salt; humectant; raising agent; sequestrant; stabilizer; thickener`.
  - **FAO 2019 Report (`ca5644en.pdf` Section 2 p. 9 & Table 1 Group 4 p. 12)**: Explicitly lists `emulsifiers`, `emulsifying salts`, and `thickeners` among the additive classes used exclusively in ultra-processed foods (Group 4).
- **Conflict**: The repository classed 452(i) as an unlisted stabilizer that never triggers Group 4, whereas both JECFA and Codex certify it as an emulsifier, emulsifying salt, and thickener. This rule actively causes ultra-processed formulations containing 452(i) to be under-classified.

### 2. `firming` & `humectant` (`src/foodscan/resources/markers.csv`)
- **Repo State**: `marker_class: cosmetic_additive` (strong Group 4 marker)
- **Repo Claim**: `research/02 marker class 2 (cosmetic processing aids)`
- **Primary Source Evidence**:
  - **FAO 2019 Report (`ca5644en.pdf`)**: Does not name `firming` or `humectant` anywhere across all 44 pages.
  - **Monteiro et al. 2019 PHN Paper**: Abstract does not list firming agents or humectants among ultra-processed additive classes.
  - **NUPENS/USP NOVA Classification**: Mentions "anti-humectants in salt" under Group 2 (culinary ingredients).
- **Conflict**: The repository elevates firming and humectant agents to strong Group 4 cosmetic markers, but no primary NOVA literature restricts them to ultra-processed foods.

### 3. `pectin` (`src/foodscan/resources/markers.csv` & `ins_map.csv`)
- **Repo State**: `marker_class: ordinary_additive`, `strength: weak_specific` (cancels cosmetic class words, consistent with Group 3)
- **Repo Claim**: `research/02 qualification: pectin in a jam is consistent with group 3`
- **Primary Source Evidence**:
  - **WHO JECFA Database (ID 3043)**: Functional classes are `EMULSIFIER; GELLING_AGENT; STABILIZER; THICKENER`.
  - **FAO 2019 Report (`ca5644en.pdf` Section 2 p. 9)**: Explicitly lists `emulsifiers`, `gelling agents`, and `thickeners` as additive classes used only in ultra-processed foods.
- **Conflict**: While artisanal jams with fruit and sugar may contain pectin, international regulatory bodies class pectin as a gelling agent, thickener, and emulsifier—all three of which FAO 2019 designates as Group 4 markers. Forcing pectin to cancel cosmetic markers creates a systematic blind spot for industrial texturized foods.

### 4. `milk solids` (`src/foodscan/resources/lexicon.csv`)
- **Repo State**: `kind: whole_food` (Group 1)
- **Repo Claim**: `Treated as dried or concentrated milk, like the other milks...`
- **Primary Source Evidence**:
  - **FAO 2019 Report (`ca5644en.pdf` Section 2 pp. 8–9)**: Ultra-processed foods are characterized by the fractioning of whole foods into substances including sugars, proteins, and starches, explicitly listing `"whey protein"`, `"casein"`, and `"lactose"` as food substances of no or rare culinary use.
  - **Dairy Technology / USDA FDC**: "Milk solids" is a composite of dehydrated/fractioned dairy components (whey solids, nonfat dry milk, milk protein concentrates).
- **Conflict**: Classifying bare `milk solids` as an unconditioned `whole_food` (Group 1) allows ultra-processed formulations containing industrial whey or casein fractions to masquerade as minimally processed foods.

### 5. `refined wheat flour` (`src/foodscan/resources/lexicon.csv`)
- **Repo State**: `kind: flour` (causes mixed bread-like ingredient lists to abstain)
- **Repo Claim**: `flour kind => bread-like lists abstain`
- **Primary Source Evidence**:
  - **FAO 2019 Report (`ca5644en.pdf` Table 1 Group 1 p. 11)**: `"grits, flakes or flour made from corn, wheat, oats, or cassava"` is explicitly placed in Group 1 (Minimally processed foods).
  - **Martinez-Steele et al. 2022 (PMC10127522 footnote 2)**: Lists `"flours"` under unprocessed or minimally processed foods.
- **Conflict**: The NOVA literature classifies plain wheat flour in Group 1. The repository's bespoke kind `flour` forces abstention on lists containing wheat flour to work around synthetic test bread cases, creating a divergence between the app's rules and published NOVA methodology.

---

## 4. Condition Preservation Analysis

In primary literature, several ingredient classes are placed in Group 1 or Group 2 **only under strict negative conditions**:
1. **Nuts & Seeds**: FAO 2019 Table 1 Group 1 specifies `"(with no added salt or sugar)"`. In Group 3, Table 1 specifies `"salted or sugared nuts and seeds"`.
2. **Fruit/Vegetable Juices**: FAO 2019 Table 1 Group 1 specifies `"(with no added sugar, sweeteners or flavours)"`.
3. **Milk**: FAO 2019 Table 1 Group 1 specifies `"fresh, powdered or pasteurized milk"`. The repository maps `toned milk`, `double toned milk`, and `buffalo milk` without verification of whether recombined or standardized milks retain Group 1 status.
4. **Fermented Milk / Dahi**: NUPENS-USP specifies `"plain yoghurt with no added sugar or artificial sweeteners"`. The repository's `dahi` row is unconditioned `whole_food`, ignoring commercial sweetened curd formulations.

---

## 5. Top 3 Most Urgent Findings for Senior Integration

1. **Retire or Re-classify `452(i)`**: Sodium polyphosphate is documented by JECFA and Codex as an emulsifier, emulsifying salt, and thickener. Its current status in `ins_map.csv` as an unlisted stabilizer that never decides a group directly violates FAO 2019 Group 4 definitions.
2. **Drop or Re-evaluate `firming` and `humectant` Markers**: Neither class appears in FAO 2019 or Monteiro 2019 ultra-processing additive lists. They originated from secondary aggregators (Open Food Facts / Siga) and currently generate unsourced Group 4 classifications.
3. **Segregate or Retire the 29 NOT FOUND Rows**: 27 lexicon entries (including traditional Indian dals, millets, and unrefined sweeteners like jaggery) and 2 markers have zero primary source backing. If retained, they must carry explicit provisional gating rather than silent authority claims.
