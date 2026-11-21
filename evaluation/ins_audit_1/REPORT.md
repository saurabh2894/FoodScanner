# INS Additive Resource & Classification Audit 1

## Executive Summary

Following the senior review finding on **INS 500(ii)** (Sodium hydrogen carbonate classed as a weak ordinary additive without checking for cosmetic functional classes), this audit evaluates every additive rule currently shipped in the repository across:
- `src/foodscan/resources/ins_map.csv` (14 active classification rules)
- `src/foodscan/resources/ins_names.csv` (16 display-only references)
- **Total codes audited: 30**

Each code was cross-referenced against:
1. **WHO JECFA Additive Database** (`apps.who.int/food-additives-contaminants-jecfa-database/`): Monograph evaluations and registered technological functional classes.
2. **Codex CXG 36-1989 (Class Names and the International Numbering System for Food Additives)**: Multi-functional class registrations.
3. **FAO 2019 Report (`ca5644en.pdf` Section 2 pp. 9–10 & Table 1 pp. 11–12)**: Additive classes designated as exclusive to ultra-processed foods (Group 4).

All 30 audited codes and verdicts are recorded in `evaluation/ins_audit_1/audit.csv`.

---

## 1. Audit Summary Totals

| Category | Active Rules (`ins_map.csv`) | Display Only (`ins_names.csv`) | Total Codes | Share |
|---|:---:|:---:|:---:|:---:|
| **Clean Rules / Entries** | 8 | 4 | **12** | 40.0% |
| **Dual-Function Risks** | 3 | 5 | **8** | 26.7% |
| **Severe Mismatches (Missed Group 4)** | 2 | 0 | **2** | 6.7% |
| **Unlisted Cosmetic Risks (if ruled)** | 1 | 7 | **8** | 26.7% |
| **Total Audited** | **14** | **16** | **30** | **100.0%** |

---

## 2. Detailed Analysis of Active Rules (`ins_map.csv` — 14 Codes)

### A. Clean Rules (8 codes)
These rules have claimed functional classes confirmed verbatim by JECFA, with no conflicting unrepresented cosmetic or non-cosmetic roles:
- **`171` (Titanium dioxide)**: Claimed `colour`. JECFA confirms `COLOUR`. Group 4 marker in FAO 2019.
- **`211` (Sodium benzoate)**: Claimed `preservative` (`unlisted`). JECFA confirms `PRESERVATIVE`. Permitted in Group 3 (FAO Table 1 p. 12); repo strength `unlisted` correctly prevents forced Group 4.
- **`627` (Disodium 5'-guanylate)**: Claimed `flavour enhancer`. JECFA confirms `FLAVOUR_ENHANCER`. Group 4 marker in FAO 2019.
- **`631` (Disodium 5'-inosinate)**: Claimed `flavour enhancer`. JECFA confirms `FLAVOUR_ENHANCER`. Group 4 marker in FAO 2019.
- **`102` (Tartrazine)**: Claimed `colour`. JECFA confirms `COLOUR`. Group 4 marker in FAO 2019.
- **`110` (Sunset yellow FCF)**: Claimed `colour`. JECFA confirms `COLOUR`. Group 4 marker in FAO 2019.
- **`150d` (Caramel IV)**: Claimed `colour`. JECFA confirms `COLOUR`. Group 4 marker in FAO 2019.
- **`950` (Acesulfame potassium)**: Claimed `sweetener`. JECFA confirms `SWEETENER` and `FLAVOUR_ENHANCER`. Both functions are Group 4 markers in FAO 2019; no misclassification risk.

### B. The Senior-Identified INS 500(ii) Issue & Codes with Identical Risk (3 codes)

#### 1. **`500(ii)` (Sodium hydrogen carbonate / baking soda)**
- **Repo State**: `functional_class: raising agent`, `strength: weak`
- **JECFA Functional Classes**: `ACIDITY_REGULATOR; LEAVENING_AGENT; RAISING_AGENT`
- **Codex CXG 36-1989**: `acidity regulator; anticaking agent; raising agent; stabilizer; thickener`
- **FAO 2019 Definition**: Neither raising agents nor acidity regulators are listed as Group 4 markers (plain bread made with raising agents is consistent with Group 3). However, `thickeners` are explicitly listed in FAO 2019 pp. 9–10 as exclusive Group 4 markers.
- **The Core Problem**: The repository's rule hardcodes INS 500(ii) to `raising agent` (`ordinary_additive`), treating it as a weak Group 3 marker. However, an ingredient label on packaged food may declare INS 500(ii) under a cosmetic function (e.g., *"Thickener (INS 500(ii))"*) or as an acidity regulator. Because the classifier maps the INS code directly to `raising agent`, it forces an ordinary additive classification, overriding the manufacturer's declared technological purpose.

#### 2. **`322` (Lecithin)**
- **Repo State**: `functional_class: emulsifier`, `strength: strong`
- **JECFA Functional Classes**: `ANTIOXIDANT; EMULSIFIER`
- **Codex CXG 36-1989**: `antioxidant; emulsifier; flour treatment agent`
- **FAO 2019 Definition**: `emulsifiers` are Group 4 markers; `antioxidants` are permitted in Group 2 (vegetable oils) and Group 3 (canned fish/fruit).
- **The Conflict**: The repo hardcodes code 322 as an emulsifier (driving automatic Group 4). If a manufacturer uses lecithin as an antioxidant (e.g. in cooking oil or artisanal chocolate), the hardcoded code forces Group 4, ignoring the declared antioxidant role.

#### 3. **`503(ii)` (Ammonium hydrogen carbonate)**
- **Repo State**: `functional_class: raising agent`, `strength: weak`
- **JECFA Functional Classes**: `RAISING_AGENT` (Codex adds `acidity regulator`)
- **Status**: Clean for raising agent, but shares the dual-role characteristic if declared as an acidity regulator.

### C. Severe Mismatches & Missed Group 4 Markers (2 codes)

#### 1. **`452(i)` (Sodium polyphosphate)** — *Most Critical Additive Bug*
- **Repo State**: `functional_class: stabiliser`, `strength: unlisted`
- **Repo Justification**: `"its functional classes are in no research/02 marker list, so it never decides a group"`
- **JECFA Functional Classes (ID 4669)**: `EMULSIFIER; SEQUESTRANT; TEXTURIZER; THICKENER`
- **Codex CXG 36-1989**: `acidity regulator; emulsifier; emulsifying salt; humectant; raising agent; sequestrant; stabilizer; thickener`
- **FAO 2019 Evidence (pp. 9–10)**:
  > *"Classes of additives used only in the manufacture of ultra-processed foods, are flavours, flavour enhancers, colours, emulsifiers, emulsifying salts, artificial sweeteners, thickeners..."*
- **Impact**: The repository classed 452(i) as an unlisted stabilizer that never decides a group. In reality, JECFA and Codex certify 452(i) as an **emulsifier**, **emulsifying salt**, and **thickener**—all three of which are primary Group 4 ultra-processing markers. Ultra-processed products containing 452(i) (processed meats, cheeses, noodles) currently evade Group 4 classification.

#### 2. **`440` (Pectins)**
- **Repo State**: `functional_class: ""`, `strength: weak_specific` (acts as ordinary additive / Group 3 exception)
- **JECFA Functional Classes (ID 3043)**: `EMULSIFIER; GELLING_AGENT; STABILIZER; THICKENER`
- **FAO 2019 Evidence (pp. 9–10)**: `emulsifiers`, `gelling agents`, and `thickeners` are exclusive Group 4 markers.
- **Impact**: Research/02 carved out an exception for pectin in artisanal fruit jams. However, in industrial foods (confectionery, dairy desserts, sauces), pectin is deployed as an industrial gelling agent and thickener. Treating 440 as an unconditional Group 3 qualifier creates an open false-negative hole.

---

## 3. Analysis of Display-Only Additives (`ins_names.csv` — 16 Codes)

The 16 display-only codes currently carry no classification rules. If classification rules are authored in future rounds, the following risks must be accounted for:

### A. High-Risk Latent Group 4 Markers (7 codes)
These codes are currently display-only, but their JECFA functional classes include major Group 4 cosmetic markers:
1. **`339(ii)` (Disodium hydrogen phosphate)**: JECFA lists `EMULSIFIER; THICKENER; TEXTURIZER; ACIDITY_REGULATOR`. Identical risk profile to `452(i)`.
2. **`412` (Guar gum)**: JECFA lists `EMULSIFIER; STABILIZER; THICKENER`. Emulsifier and thickener are Group 4 markers.
3. **`415` (Xanthan gum)**: JECFA lists `EMULSIFIER; FOAMING_AGENT; STABILIZER; THICKENER`. Three Group 4 cosmetic classes.
4. **`466` (Sodium carboxymethyl cellulose)**: JECFA lists `EMULSIFIER; STABILIZER; THICKENER`. Codex adds `bulking, gelling, glazing`.
5. **`476` (Polyglycerol polyricinoleate / PGPR)**: JECFA lists `EMULSIFIER`. Universal confectionery emulsifier; strong Group 4 marker.
6. **`508` (Potassium chloride)**: JECFA lists `FLAVOUR_ENHANCER; GELLING_AGENT; YEAST_FOOD`. Flavour enhancer and gelling agent are Group 4 markers.
7. **`1422` (Acetylated distarch adipate)**: JECFA lists `EMULSIFIER; STABILIZER; THICKENER`. Chemically modified starch and cosmetic thickener.

### B. Dual-Function Acids / Flavorings (4 codes)
JECFA lists `FLAVOURING_AGENT` alongside technological acid/preservative roles:
1. **`260` (Acetic acid)**: `ACIDITY_REGULATOR; PRESERVATIVE; FLAVOURING_AGENT`
2. **`296` (Malic acid)**: `ACIDITY_REGULATOR; FLAVOURING_AGENT; ACID`
3. **`330` (Citric acid)**: `ACID; ANTIOXIDANT_SYNERGIST; FLAVOURING_AGENT`
4. **`334` (Tartaric acid)**: `ACID; ANTIOXIDANT_SYNERGIST; FLAVOURING_AGENT`

*Policy Recommendation*: In consumer packaged goods, these organic acids are overwhelmingly used for pH regulation or sourness rather than cosmetic flavour imitation. Rules should only trigger Group 4 if the label explicitly declares the functional class as *"Flavouring"* or *"Flavour"*.

---

## 4. Architectural Summary: The Core Vulnerability of Single-Class INS Mapping

The fundamental design flaw identified by this audit is **forcing an INS code into a single hardcoded functional class**:
```
INS Code  --->  Hardcoded Class in ins_map.csv  --->  Classifier Group Decision
```
In real food manufacturing and under Codex/JECFA standards, additives are **multi-functional**:
- `500(ii)` can function as a raising agent (Group 3) OR a thickener (Group 4).
- `322` can function as an antioxidant (Group 2/3) OR an emulsifier (Group 4).
- `452(i)` can function as a stabilizer OR an emulsifying salt (Group 4).

### Recommended Remediation Architecture
1. **Role-Aware Code Resolution**: If the scanned label explicitly declares a functional class for an INS code (e.g. *"Acidity Regulator (INS 500(ii))"* vs *"Thickener (INS 500(ii))"*), the **label-declared functional class must take precedence** over the default class in `ins_map.csv`.
2. **Dual-Function Gating**: When a code has both cosmetic (Group 4) and ordinary (Group 2/3) functions, and the label declares no functional class, the system should treat the code as ambiguous/uncertain rather than forcing a false-negative Group 3 or false-positive Group 4.
3. **Immediate Correction of `452(i)`**: Update `452(i)` to register `emulsifying salt` / `emulsifier` / `thickener` as active strong cosmetic markers.
