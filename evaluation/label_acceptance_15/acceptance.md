# Acceptance Specification: Multigrain Label End-to-End Resolution

This document specifies the exact acceptance criteria that any future implementation must satisfy to resolve the original multigrain ingredient label:
```text
Ingredients: Multigrain Flour Blend (45.7%) [Sprouted Ragi & Jowar (23.4%), Rice & Oat (22.3%)], Whole Milk Powder (29.5%), Date Powder (9%), Banana Powder, Strawberry Powder (5%), Skimmed Milk Powder, Vitamins# and Minerals##, Beetroot Powder, Antioxidant (Natural Tocopherol).
```

---

## 1. Acceptance Pillars Overview

A complete and valid implementation must prove correctness across four distinct stages:
1. **OCR Correctness**: Faithful text extraction of typography, percentages, brackets, and footnote marks.
2. **Parser Correctness**: Faithful syntactic representation of compounds, shared modifiers, shared percentages, and non-ingredient boundaries.
3. **Honest Classification**: Rigorous grounding in primary NOVA evidence without forced group assignments.
4. **Transparent Reason Reporting**: Explaining all unresolved evidence layers instead of masking them behind a single arbitrary gate.

```
       [ Packaging Image ]
               │
               ▼
   [ 1. OCR Correctness ] ───────► Accurately extract brackets, %, and footnote marks
               │
               ▼
  [ 2. Parser Correctness ] ─────► Expand blend, distribute shared qualifier & %, strip footnote marks
               │
               ▼
 [ 3. Honest Classification ] ───► Abstain on genuine evidence gaps (sprouting, fortification, powders)
               │
               ▼
[ 4. Transparent Reporting ] ────► Expose all contributing reasons, never mask behind a weak marker
```

---

## 2. Pillar 1: OCR Correctness

| Requirement ID | Requirement Description | Verification Method | Acceptance Pass Threshold |
| :--- | :--- | :--- | :--- |
| **OCR-REQ-01** | **Character Fidelity on Numerical Values** | Extract `45.7%`, `23.4%`, `22.3%`, `29.5%`, `9%`, `5%` without digit substitution or omission. | 100% exact match across all 6 percentages. |
| **OCR-REQ-02** | **Delimiter and Enclosure Fidelity** | Extract outer parentheses around percentages and inner square brackets `[...]` around sub-ingredients. | Zero mismatched or dropped enclosures. |
| **OCR-REQ-03** | **Footnote Symbol Resilience** | Tolerate printed footnote marks (`#`, `##`, `*`, `**`, `”`) attached to ingredient names without corrupting the ingredient base token. | Ingredient tokens resolve to canonical vocabulary without being treated as unknown words. |
| **OCR-REQ-04** | **Boundary Discrimination** | Distinguish between the ingredient list box and external declarations (`THIS PRODUCT CONTAINS 23% MILLETS`, `Contains Milk & Oats...`). | Zero marketing or allergen phrases injected into the parsed ingredient array. |

---

## 3. Pillar 2: Parser Correctness

| Requirement ID | Requirement Description | Verification Method | Acceptance Pass Threshold |
| :--- | :--- | :--- | :--- |
| **PARSE-REQ-01** | **Compound Blend Expansion** | The parent item `Multigrain Flour Blend (45.7%)` must expand into its constituent sub-items while preserving the group name in metadata. | Parent marked as assessed via contents; sub-items extracted into active evaluation. |
| **PARSE-REQ-02** | **Shared Qualifier Distribution** | The qualifier `Sprouted` in `[Sprouted Ragi & Jowar (23.4%)]` must apply to both `Ragi` and `Jowar`. | Emits `Sprouted Ragi` and `Sprouted Jowar`; emits warning noting `Sprouted` was read as shared. |
| **PARSE-REQ-03** | **Shared Percentage Attribution** | The percentage `(23.4%)` belongs to the pair `Sprouted Ragi & Jowar`, NOT 23.4% each. | Percentage is recorded as pair context, not duplicated onto individual ingredient instances. |
| **PARSE-REQ-04** | **Connector Robustness (`&` and `and`)** | Sub-bracket item pairs joined by either `&` or `and` must split when both sides are recognizable ingredients. | Changing `&` to `and` must not cause sub-brackets to fail parsing into `unassessed`. |
| **PARSE-REQ-05** | **Footnote Stripping in Normalization** | Trailing footnote markers (`#`, `##`, `*`, `†`) attached to words must be cleanly stripped during item normalization. | `Vitamins# and Minerals##` normalizes to `Vitamins` and `Minerals` and splits at `and`. |

---

## 4. Pillar 3: Honest Classification & Evidence Boundaries

> [!WARNING]
> An implementation must **NEVER** force this label into NOVA Group 1, Group 3, or Group 4 simply to make it "pass". The label contains four genuine evidence gaps documented in primary NOVA sources:

### A. Sprouting Evidence Gap
- **Primary Source**: FAO 2019 (*ca5644en*), p. 6 (Group 1 definition process list).
- **Evidence Reality**: The exhaustive process list includes *"drying, crushing, grinding, powdering, fractioning, filtering, roasting, boiling, non-alcoholic fermentation, pasteurization, chilling, freezing, placing in containers, and vacuum packaging"*. Germination/sprouting is **not** named anywhere in FAO 2019, Monteiro 2018, or Monteiro 2019.
- **Requirement**: `Sprouted Ragi` and `Sprouted Jowar` must remain `unplaced` unless explicit, reviewed primary evidence establishes that sprouting is a Group 1 process.

### B. Fortification Purpose Gap
- **Primary Source**: FAO 2019 (*ca5644en*), Table 1, Group 1, p. 11.
- **Evidence Reality**: Fortification with vitamins and minerals is strictly purpose-conditioned: *"foods with vitamins and minerals added generally to replace nutrients lost during processing, such as wheat or corn flour fortified with iron and folic acid"*. Conversely, Monteiro 2018 lists *"powdered or fortified meal and dish substitutes"* in Group 4. Label declarations cannot prove industrial purpose.
- **Requirement**: `Vitamins` and `Minerals` must remain `unplaced` (or explicitly conditioned) unless a verified rule policy is adopted by senior review.

### C. Food Powder Composition Gap
- **Primary Source**: FAO 2019 (*ca5644en*), p. 6.
- **Evidence Reality**: Powdering of a single whole food is covered under minimal processing, but commercial fruit/vegetable powders (`Banana Powder`, `Strawberry Powder`, `Date Powder`, `Beetroot Powder`) frequently contain carriers (maltodextrin) or anti-caking agents not declared on commodity-style ingredient lists.
- **Requirement**: Single-item bare food powders must continue to flag composition uncertainty in multi-ingredient formulations.

### D. Antioxidant / Tocopherol Identity
- **Primary Source**: Monteiro et al. 2019; Codex GSFA INS 307.
- **Evidence Reality**: The label declares `Antioxidant (Natural Tocopherol)`. "Antioxidant" is an unlisted additive in current research rules; tocopherol is not in the decision map.
- **Requirement**: Must not be treated as a strong cosmetic marker (Group 4) or ignored as culinary (Group 2).

---

## 5. Pillar 4: Transparent Reason Reporting

### The Masking Problem on Current Main
On current main (`a6cacbc`), the classification gate evaluates weak markers before unplaced items:
```python
if weak:
    return Classification(None, drivers=weak, reason=f"only weak or unlisted markers present ({names}); not enough to call a group")
```
This causes the user-facing output to state:
> *"Not enough information: only weak or unlisted markers present (Antioxidant (Natural Tocopherol) -> "antioxidant" (unlisted_additive)); not enough to call a group"*

This misleadingly implies that if the antioxidant were absent, the label would be classified. In reality, removing the antioxidant still results in abstention due to `Sprouted Ragi`, `Sprouted Jowar`, `Vitamins`, `Minerals`, and powder composition uncertainty.

### Acceptance Criterion for Reporting
The explanation must transparently aggregate and report all unresolved dimensions:
1. **Unlisted Additives**: Report unlisted role of `Antioxidant`.
2. **Unplaced Ingredients**: Report lack of source placement for `Sprouted Ragi`, `Sprouted Jowar`, `Vitamins`, and `Minerals`.
3. **Composition Uncertainties**: Report composition caveats on fruit/vegetable powders.
4. **No Single-Gate Obscuration**: Never suppress unplaced or unassessed disclosures when an abstention reason is rendered.
