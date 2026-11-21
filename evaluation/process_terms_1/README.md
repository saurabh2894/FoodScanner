# Process and Declaration Words: Evidence-Gap Research (`process_terms_1`)

## 1. Context and Non-Goals
Foodscan reads Indian ingredient labels and assigns NOVA groups from evidence-backed rules. Some condition and processing words already have verified handling (e.g. `salted`, `dried`, `roasted`, `pasteurised`, `refined`, `hydrogenated`, `hydrolysed`). However, real Indian labels—including the user-supplied multigrain label (Appendix A)—carry process and declaration words whose evidence position in the primary NOVA literature is unresolved, forcing honest abstentions:
- `'sprouted'` (e.g. `Sprouted Ragi`, `Sprouted Jowar`)
- `'vitamins and minerals'` / `'fortified'` / `'premix'`

**CRITICAL NON-GOAL**: This task is **RESEARCH ONLY**. It does **NOT** make classification verdicts, assign NOVA groups, express placement opinions, or propose classification rules. Its sole deliverable is resolving what the admissible primary evidence establishes about each unresolved word, and documenting exactly where that evidence runs out.

## 2. Base Commit and Branch Information
- **Branch**: `antigravity/process-terms-1`
- **Base commit SHA**: `827cdcbf99010b22a94dcbb01bcd924ed9c9ff50`
- **Working tree boundary**: Additions strictly isolated under `evaluation/process_terms_1/`. No modification of any existing file in the repository.

## 3. Methodology & Admissible Sources
Demand was extracted directly from real labels across the FoodScanner repository:
1. All label files under `evaluation/*/inputs/*.txt` and `data/cache/oos_herb_spice_1/inputs/*.txt` (98 files total).
2. The user-supplied multigrain cereal label (**Appendix A**):
   `"Sprouted Ragi, Sprouted Jowar, Rolled Oats, Foxtail Millet, Moong Dal, Dehydrated Fruit Powder, Vitamins and Minerals"`

### Admissible Sources Consulted
- **FAO 2019 report**: *Ultra-processed foods, diet quality, and health using the NOVA classification system* by Carlos Augusto Monteiro, Geoffrey Cannon, Mark Lawrence, Maria Laura da Costa Louzada, and Priscila Pereira Machado (Rome: FAO, 2019, ISBN 978-92-5-131707-5, `ca5644en.pdf`).
- **Primary NOVA Literature**: Monteiro et al. 2016 (*World Nutrition*), Monteiro et al. 2018 (*Public Health Nutrition* 21(1): 5-17), Monteiro et al. 2019 (*Public Health Nutrition* 22(5): 936-941).
- **Statutory Standards & Regulations**:
  - US Code of Federal Regulations (eCFR): 21 CFR §104.20 (Nutritional quality guidelines for foods), 21 CFR §137 (Cereal flours and related products), 21 CFR §184.1445 (Malt).
  - US FDA Whole Grain Label Statements Guidance (2006).
  - Food Safety and Standards Authority of India (FSSAI): Food Safety and Standards (Fortification of Foods) Regulations, 2018; Food Safety and Standards (Food Products Standards and Food Additives) Regulations, 2011.

## 4. Candidate Word List and Classification Status
A total of 23 words / word pairs were evaluated:
- **16 Deep-Researched Words (with Evidence Gaps)**:
  1. `sprouted / germinated`
  2. `vitamins and minerals`
  3. `fortified / enriched`
  4. `premix`
  5. `malted`
  6. `extract`
  7. `flaked / flakes`
  8. `puffed / popped`
  9. `toasted`
  10. `bleached`
  11. `deodorised / deodorized`
  12. `reconstituted`
  13. `defatted`
  14. `fractionated`
  15. `compounded`
  16. `fermented`
- **7 Already-Handled Reference Baseline Words in FoodScanner**:
  17. `iodised / iodized` (Group 2, author seed variant of salt)
  18. `roasted` (Group 1, descriptors.csv)
  19. `pasteurised / pasteurized` (Group 1, descriptors.csv)
  20. `homogenised` (Group 1, descriptors.csv)
  21. `refined` (Group 2, descriptors.csv)
  22. `hydrogenated` (Group 4, markers.csv)
  23. `hydrolysed` (Group 4, markers.csv)

## 5. Synthetic Probe Measurements
To establish how the current pipeline handles each process/declaration word in minimal spans, synthetic probes were analysed through `foodscan.pipeline.analyse_text(span, source='text')`:

| Minimal Probe Span | Pipeline Status | Pipeline Details |
|---|---|---|
| `sprouted ragi` | **abstains** | `group=None, reason: recognised by name only, and no source read places sprouted ragi, so the processing level cannot be judged` |
| `vitamins and minerals` | **abstains** | `group=None, reason: recognised by name only, and no source read places vitamins; minerals, so the processing level cannot be judged` |
| `fortified wheat flour` | **unrecognised** | `unassessed: ['fortified wheat flour']` |
| `malted barley` | **unrecognised** | `unassessed: ['malted barley']` |
| `corn flakes` | **unrecognised** | `unassessed: ['corn flakes']` |
| `vanilla extract` | **unrecognised** | `unassessed: ['vanilla extract']` |
| `puffed rice` | **unrecognised** | `unassessed: ['puffed rice']` |
| `toasted oats` | **unrecognised** | `unassessed: ['toasted oats']` |
| `bleached wheat flour` | **unrecognised** | `unassessed: ['bleached wheat flour']` |
| `deodorised edible vegetable oil` | **unrecognised** | `unassessed: ['deodorised edible vegetable oil']` |
| `reconstituted skimmed milk` | **unrecognised** | `unassessed: ['reconstituted skimmed milk']` |
| `defatted soya flour` | **unrecognised** | `unassessed: ['defatted soya flour']` |
| `fractionated palm oil` | **unrecognised** | `unassessed: ['fractionated palm oil']` |
| `compounded asafoetida` | **unrecognised** | `unassessed: ['compounded asafoetida']` |
| `fermented milk` | **unrecognised** | `unassessed: ['fermented milk']` |
| `iodised salt` | **recognised: Group 2** | `single processed culinary ingredient (PROVISIONAL author seed variant of salt)` |
| `roasted gram` | **recognised: Group 1** | `single recognised unprocessed food (FAO 2019 Table 1 p.11; roasted in descriptors.csv)` |
| `pasteurised milk` | **recognised: Group 1** | `single recognised unprocessed food (pasteurised in descriptors.csv)` |
| `homogenised milk` | **recognised: Group 1** | `single recognised unprocessed food (homogenised in descriptors.csv)` |
| `refined sunflower oil` | **recognised: Group 2** | `single processed culinary ingredient (refined in descriptors.csv)` |
| `hydrogenated vegetable oil` | **recognised: Group 4** | `"hydrogenated" (markers.csv marker class 1)` |
| `hydrolysed vegetable protein` | **recognised: Group 4** | `"hydrolysed vegetable protein" (markers.csv marker class 1)` |

## 6. Summary of Key Evidence Gaps

### Priority 1: `sprouted` / `germinated`
- **Finding**: Complete silence across FAO 2019 and primary Monteiro et al. literature. Neither word appears in any table, text, or example.
- **Evidence Gap**: While germination is a biological transformation without added substances, NOVA does not explicitly list it under Group 1 minimal processes. Foodscan currently abstains when sprouted grains are encountered.

### Priority 2: `vitamins and minerals` / `fortified`
- **Finding**: FAO 2019 Table 1 (p. 11) explicitly places foods with added vitamins and minerals in Group 1 ("foods with vitamins and minerals added generally to replace nutrients lost during processing, such as wheat or corn flour fortified with iron and folic acid") and Group 2 ("group 2 items with added vitamins or minerals, such as iodised salt"). Vitamins and minerals are omitted from Group 4 marker substances (p. 9) and cosmetic additives (pp. 9-10).
- **Evidence Gap**: NOVA texts establish that vitamins and minerals do not make a food Group 4 on their own, but are silent on how to classify a standalone declaration `"Vitamins and Minerals"` appearing on multi-ingredient formulated products. Foodscan currently abstains on `"vitamins and minerals"`.

### Industrial Extracts vs Culinary Concentrates (`extract`)
- **Finding**: Dual nature in FAO 2019: extraction is cited as a Group 2 culinary process (p. 11), while industrial extracts ("meat, yeast and other extracts", p. 9) and flavor extracts are Group 4 markers.
- **Evidence Gap**: Absence of explicit classification boundaries for botanical/spice extracts vs flavor extracts.

### Physical Grains (`flaked`, `puffed`, `toasted`)
- **Finding**: FAO 2019 explicitly lists plain flakes in Group 1 (p. 11: "flakes or rolled grains"; p. 10: "plain corn flakes (Group 1), but with added sugar they are Group 3, and with flavouring or colour they are Group 4"). Popping/toasting are thermal physical processes equivalent to roasting.

## 7. Deliverable Files Summary
- `process_terms.csv`: 107 real demand spans extracted from 98 ingest files and Appendix A, with measured pipeline handling and held-term exclusion flags (<= 120 cap).
- `process_evidence.csv`: 23 evidence rows addressing 16 researched process words + 7 reference baseline words with exact quotes, citations, absence analyses, and residual gaps (<= 25 cap).
- `STATUS.md`: Machine-readable completion status.
