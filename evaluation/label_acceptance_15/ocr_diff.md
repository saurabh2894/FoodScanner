# OCR Extraction Diff and Error Analysis: Multigrain Ingredient Panel

## 1. Overview and Test Setup

This document provides a character-level and word-level error audit for the optical character recognition (OCR) performed on the user's original multigrain label photo:
- **Frozen Image**: `evaluation/label_acceptance_15/inputs/original_label.jpg`
- **SHA-256**: `beed9e9324b246295fa74e729161640e448ff2afdf0f045577e38fc53eff5f18`
- **Dimensions**: 607 × 494 px (RGB JPEG, 57,260 bytes)
- **OCR Engine**: Tesseract.js v5.1.1 (running client-side in Headless Chrome on https://foodscan-nine.vercel.app/)
- **Reference Ground Truth**: `evaluation/label_acceptance_15/inputs/original_label.txt` (literal transcription visually verified against the label packaging).

> [!IMPORTANT]
> This analysis evaluates OCR performance on this single frozen label image only. It is a diagnostic error audit for label acceptance, not a general OCR benchmark.

---

## 2. Text Comparison: Literal Ground Truth vs OCR Extracted

### Literal Transcription (Ground Truth)
```text
Ingredients: Multigrain Flour Blend (45.7%) [Sprouted Ragi & Jowar (23.4%), Rice & Oat (22.3%)], Whole Milk Powder (29.5%), Date Powder (9%), Banana Powder, Strawberry Powder (5%), Skimmed Milk Powder, Vitamins# and Minerals##, Beetroot Powder, Antioxidant (Natural Tocopherol).
```

### OCR Extracted Text (In-Browser Tesseract.js)
```text
INGREDIENTS

Multigrain Flour Blend (45.7%) [Sprouted Ragi &
Jowar (23.4%), Rice & Oat (22.3%)], Whole Milk
Powder (29.5%), Date Powder (9%), Banana
Powder, Strawberry Powder (5%), Skimmed Milk
Powder, Vitamins” and Minerals** , Beetroot
Powder, Antioxidant (Natural Tocopherol).

THIS PRODUCT CONTAINS 23% MILLETS
Contains Milk & Oats. Made in a facility that
also processes Soy, Wheat & Nuts. May contain
trace elements.
```

---

## 3. Quantitative Error Metrics (Ingredient List Region)

Comparing the normalized ingredient list body (excluding leading heading tokens and whitespace wrapping):

| Metric | Measured Value | Denominator | Percentage |
| :--- | :--- | :--- | :--- |
| **Character Length (Reference)** | 265 chars | 265 | — |
| **Character Levenshtein Distance** | 4 edits | 265 | **1.51% CER** |
| **Word Count (Reference)** | 36 words | 36 | — |
| **Word Levenshtein Distance** | 3 word edits | 36 | **8.33% WER** |

### Breakdown of the 4 Character Edits
1. **Substituted `#`**: The single footnote hash `#` in `Vitamins#` was read as `”` (Unicode U+201D right double quotation mark).
2. **Substituted `##`**: The double footnote hash `##` in `Minerals##` was read as `**` (two asterisks).
3. **Space Insertion before Comma**: In the literal text `Minerals##, Beetroot`, the comma is adjacent to the hash. The OCR captured `Minerals** , Beetroot` (an inserted space before the comma). *Note: Visual inspection of the physical packaging shows that a printed space actually precedes the comma on the printed packaging (`Minerals## , Beetroot`), so the OCR faithfully captured the printed typography.*

---

## 4. Key Feature Verification Matrix

| Feature / Pattern | Expected Literal Form | OCR Output Form | Match Status | Classification Impact |
| :--- | :--- | :--- | :--- | :--- |
| **Composite Percentage** | `(45.7%)` | `(45.7%)` | **EXACT (100%)** | Correctly parsed as compound blend percentage |
| **Paired Percentage 1** | `(23.4%)` | `(23.4%)` | **EXACT (100%)** | Correctly attached to Sprouted Ragi & Jowar pair |
| **Paired Percentage 2** | `(22.3%)` | `(22.3%)` | **EXACT (100%)** | Correctly attached to Rice & Oat pair |
| **Single Item Percentage 1** | `(29.5%)` | `(29.5%)` | **EXACT (100%)** | Correctly attached to Whole Milk Powder |
| **Single Item Percentage 2** | `(9%)` | `(9%)` | **EXACT (100%)** | Correctly attached to Date Powder |
| **Single Item Percentage 3** | `(5%)` | `(5%)` | **EXACT (100%)** | Correctly attached to Strawberry Powder |
| **Nested Brackets** | `(...) [...] (...)` | `(...) [...] (...)` | **EXACT (100%)** | Outer square brackets and inner parentheses intact |
| **Ampersands** | `&` (two instances) | `&` (two instances) | **EXACT (100%)** | Enabled `_split_amp_pair` to trigger |
| **Leading Shared Qualifier** | `Sprouted` | `Sprouted` | **EXACT (100%)** | Distributed to both Ragi and Jowar |
| **Additive Class & Compound** | `Antioxidant (Natural Tocopherol)` | `Antioxidant (Natural Tocopherol)` | **EXACT (100%)** | Recognized as unlisted additive marker |
| **Footnote Hashes** | `Vitamins# and Minerals##` | `Vitamins” and Minerals**` | **MISREAD** | Symbol misread causes unassessed failure |

---

## 5. Non-Ingredient Text Handling (Allergens & Marketing Claims)

The packaging image includes non-ingredient text beneath the red ingredient container:
1. **Marketing Claim**: `THIS PRODUCT CONTAINS 23% MILLETS`
2. **Allergen Header & Statement**:
   - Packaging: `ALLERGEN NOTE\nContains Milk & Oats. Made in a facility that also processes Soy, Wheat & Nuts. May contain trace elements.`
   - OCR output: The phrase `ALLERGEN NOTE` was omitted by OCR, but the text `Contains Milk & Oats...` was extracted.

### Parser Boundary Behavior
- The `foodscan` parser detects the full stop terminating `Antioxidant (Natural Tocopherol).`.
- All text following the full stop was excluded from the ingredient list.
- In completeness metrics, this non-ingredient text was accounted for as:
  - `16 words set aside after the list`
  - `0 unaccounted words`
  - `list_share: 100%` of the ingredient list region.
- The allergen text did **not** contaminate or pollute the parsed ingredients.

---

## 6. Execution Engine Differences

1. **In-Browser Tesseract.js (Live Site & Local Browser)**:
   - Extracted all text, punctuation, percentages, and brackets with 98.5% character accuracy.
   - Only failure was mapping printed footnote hashes `#` and `##` to `”` and `**`.
2. **Local Python CLI (`foodscan.cli`)**:
   - Failed immediately with `OcrUnavailable: Tesseract OCR is not installed or not on PATH`.
   - Reason: The host environment does not have the UB-Mannheim Tesseract binary installed on Windows PATH.
