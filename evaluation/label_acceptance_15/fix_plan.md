# Bounded Implementation Fix Plan: Multigrain Label Resolution

## 1. Plan Overview and Scope Constraints

This plan presents ranked, modular implementation proposals for the senior reviewer (Claude) to resolve the multigrain label diagnostics without destabilizing the classifier or making unverified evidence leaps.

> [!IMPORTANT]
> In accordance with the TASK 15 boundary, **no code in `src/`, `web_preview/`, or `tests/` is modified in this task**. This plan serves as the bounded blueprint for future integration.

---

## 2. Ranked Implementation Proposals

### Proposal 1: Footnote Marker Stripping in Normalization (Rank 1 - Highest Priority)

- **Target Files**:
  - `src/foodscan/normalise.py` (`normalise_ingredient`, `_strip_footnotes`)
  - `web_preview/foodscan.js` (`normaliseIngredient`)
- **Problem**:
  - Packaging labels frequently place footnote markers (`#`, `##`, `*`, `**`, `†`) on ingredient names to reference nutrient tables or disclosures.
  - OCR also frequently reads `#` as `”` or `*`.
  - Current normalization retains these characters as part of the ingredient token (`vitamins#`, `minerals##`), causing lexicon lookups to fail and dumping valid ingredients into `unassessed`.
- **Proposed Change**:
  - Introduce a clean footnote-stripping step during token normalization:
    ```python
    # Strip trailing footnote characters from the core ingredient name
    s = re.sub(r'[\#\*\u2020\u201D\u201C]+$', '', s).strip()
    ```
- **Expected Benefit**:
  - `Vitamins# and Minerals##` normalizes to `Vitamins and Minerals`.
  - Splits at `and` into `Vitamins` and `Minerals`.
  - Both terms match the existing vocabulary in `lexicon.csv` (as kind `unplaced`).
- **Risk Assessment**: Very low. Footnote symbols are never legitimate parts of botanical or chemical ingredient names.
- **Verification Tests**:
  - Test with `Vitamins#`, `Minerals##`, `Salt*`, `Iron†`, and OCR artifact `Vitamins”`.

---

### Proposal 2: Connector Generalization in Sub-Bracket Pair Splitting (Rank 2)

- **Target Files**:
  - `src/foodscan/pipeline.py` (`_split_amp_pair`)
  - `web_preview/foodscan.js` (`_splitAmpPair`)
- **Problem**:
  - `_split_amp_pair` strictly requires the connector token to be `&`:
    ```python
    if len(parts) != 2 or any(c != "&" for c in connectors):
        return [raw], []
    ```
  - If a label or OCR uses the word `and` (`[Sprouted Ragi and Jowar (23.4%)]`), pair splitting is aborted, and the whole phrase becomes `unassessed`.
- **Proposed Change**:
  - Allow `connectors` to contain either `&` or `and`, provided both sides are independently recognizable with the shared modifier:
    ```python
    if len(parts) != 2 or any(c not in ("&", "and") for c in connectors):
        return [raw], []
    ```
- **Expected Benefit**:
  - Typographical variation between `&` and `and` in compound ingredient lists is handled uniformly.
- **Risk Assessment**: Low. Both sides are still strictly guarded by `_recognisable()` before any split is performed.
- **Verification Tests**:
  - Verify that `Sprouted Ragi & Jowar (23.4%)` and `Sprouted Ragi and Jowar (23.4%)` yield identical sub-items and pair notes.

---

### Proposal 3: Multi-Layer Transparent Reason Reporting (Rank 3)

- **Target Files**:
  - `src/foodscan/classify.py` (`classify_ingredients`)
  - `src/foodscan/pipeline.py` (`analyse_text`)
  - `web_preview/foodscan.js` (`classifyIngredients`, `analyseText`)
- **Problem**:
  - The current classifier evaluates gates in a rigid order:
    1. Strong markers (Group 4)
    2. Colour notes
    3. Sweetener foods
    4. Weak markers (Abstain)
    5. Unrecognised items (Abstain)
    6. Unplaced items (Abstain)
    7. Powder composition (Abstain)
  - Because `weak` fires at step 4, the presence of `Antioxidant (Natural Tocopherol)` triggers `only weak or unlisted markers present...` and completely suppresses disclosure of:
    - Unplaced items (`Sprouted Ragi`, `Sprouted Jowar`, `Vitamins`, `Minerals`)
    - Powder composition uncertainties (`Date Powder`, `Banana Powder`, `Strawberry Powder`, `Beetroot Powder`)
  - This misleadingly implies that if the antioxidant were removed, the label would classify.
- **Proposed Change**:
  - Structure abstention reporting so that when the classification cannot be answered, all active blocking layers are recorded:
    - Primary headline: summary of primary reason.
    - Secondary disclosures: explicitly list unplaced items, unassessed terms, and composition uncertainties under dedicated collapsible or bulleted sections.
- **Expected Benefit**:
  - Complete diagnostic transparency for end users and reviewers.
- **Risk Assessment**: Medium. Reason strings are checked across existing parity tests, so changes must be coordinated with test fixtures.
- **Verification Tests**:
  - Run full parity check across all 859 inputs to verify zero Python vs JS divergence.

---

### Proposal 4: Maintain Rigorous Evidence Boundaries (Rank 4)

- **Target Files**:
  - `src/foodscan/resources/lexicon.csv`
  - `src/foodscan/classify.py`
- **Policy**:
  - **Do NOT force a NOVA Group** for this label.
  - Keep `sprouted ragi` and `sprouted jowar` as `unplaced` until senior review and primary literature establish consensus on sprouting.
  - Keep `vitamins` and `minerals` as `unplaced` due to purpose-conditioned fortification rules.
  - Keep bare fruit/vegetable powders as `food_powder` (abstaining on multi-item lists).
- **Expected Benefit**:
  - Prevents false-negative or false-positive NOVA classifications and upholds strict scientific integrity.
- **Risk Assessment**: Zero. Prevents regression against project principles.
