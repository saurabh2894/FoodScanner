# TASK 15: Original Multigrain Label Diagnostics & Acceptance Pack

## 1. Overview and Base Repository State

- **Branch**: `antigravity/label-acceptance-15`
- **Base Commit**: `a6cacbc00fe3f8543a78f002b952a9a64375c4fd` (origin/main)
- **Repository Inventory at Base**:
  - 433 canonical lexicon rows (`src/foodscan/resources/lexicon.csv`)
  - 150 synonym lines (`src/foodscan/resources/synonyms.csv`)
  - 859 parity test cases (859/859 identical between Python and JS: 781 photo-path, 78 pasted-text)
- **Live Comparison Deployment**:
  - Target URL: `https://foodscan-nine.vercel.app/`
  - Live Footer Stamp: `816 of 816 matched at build time`
  - Observation: The live site reflects an earlier build (816 parity cases) than local main (859 parity cases), but its core classification rules for this label behave identically.

---

## 2. Environment and Execution Summary

| Runtime / Engine | Execution Platform | Status | Observed Result / Headline |
| :--- | :--- | :--- | :--- |
| **In-Browser OCR (Live Site)** | Tesseract.js v5.1.1 in Headless Chrome via CDP | **COMPLETED** | `Not enough information: only weak or unlisted markers present (Antioxidant (Natural Tocopherol) -> "antioxidant" (unlisted_additive)); not enough to call a group` |
| **Local CLI Photo Flow** | Python 3.12 `foodscan.cli classify` | **BLOCKED** | `OcrUnavailable: Tesseract OCR is not installed or not on PATH` |
| **Live Site Pasted Literal** | Web UI `FoodScan.createEngine` | **COMPLETED** | Identical abstention headline; `Vitamins# and Minerals##` unassessed |
| **Live Site Pasted Normalized** | Web UI `FoodScan.createEngine` | **COMPLETED** | Identical abstention headline; `Vitamins` and `Minerals` recognized but unplaced |
| **Local Main Pasted Literal** | Python `foodscan.pipeline.analyse_text` | **COMPLETED** | 100% parity with Live Site Pasted Literal |
| **Local Main Pasted Normalized** | Python `foodscan.pipeline.analyse_text` | **COMPLETED** | 100% parity with Live Site Pasted Normalized |
| **Local Main Replay OCR Text** | Python `foodscan.pipeline.analyse_text` | **COMPLETED** | 100% parity with In-Browser OCR run |

---

## 3. Key Findings and Diagnostic Insights

1. **OCR Precision on Core Typography**:
   - Every single numerical percentage (`45.7%`, `23.4%`, `22.3%`, `29.5%`, `9%`, `5%`) was extracted with 100% accuracy.
   - All enclosures (outer parentheses, inner square brackets `[...]`) and joiners (`&`) were extracted with 100% accuracy.
   - Character Error Rate (CER) on the ingredient body was **1.51%** (4 edits across 265 characters).
2. **Footnote Symbol Failure**:
   - The printed footnote marks (`Vitamins# and Minerals##`) were read by OCR as `Vitamins” and Minerals**`.
   - In both cases (literal `#`/`##` or OCR `”`/`**`), the punctuation attached to the token caused vocabulary lookup to fail, leaving the items unassessed.
   - Normalizing only the hashes (`Vitamins and Minerals`) splits the pair into `Vitamins` and `Minerals`, which are recognized in the vocabulary as kind `unplaced`.
3. **Compound Blend and Shared Attributes**:
   - The parser successfully expanded `Multigrain Flour Blend (45.7%) [...]` into sub-items.
   - The modifier `Sprouted` was successfully distributed to both sides: `Sprouted Ragi` and `Sprouted Jowar`.
   - The shared percentage `23.4%` was accurately captured as pair context with explicit warning notes, rather than duplicated onto each item.
   - However, `_split_amp_pair` strictly requires `&`; substituting `and` inside sub-brackets completely aborted splitting (documented in synthetic matrix).
4. **Obscured Multi-Layered Abstentions**:
   - The classifier currently halts at the `weak` marker gate (`Antioxidant`), displaying:
     `only weak or unlisted markers present (Antioxidant (Natural Tocopherol) -> "antioxidant" (unlisted_additive)); not enough to call a group`.
   - Diagnostic ablation (removing the antioxidant) proved that this reason masks two deeper abstention layers:
     - **Layer 2 (Unplaced Items)**: `Sprouted Ragi` and `Sprouted Jowar` (and `Vitamins`/`Minerals` when hashes are removed) are unplaced because primary NOVA sources do not place sprouting or commercial fortification.
     - **Layer 3 (Powder Composition)**: Bare fruit and vegetable powders (`Date Powder`, `Banana Powder`, `Strawberry Powder`, `Beetroot Powder`) abstain on multi-ingredient lists due to lack of carrier/anti-caking disclosures.

---

## 4. Deliverables in this Directory

- `inputs/original_label.jpg`: The frozen, unmodified original label image (SHA-256: `beed9e9324b246295fa74e729161640e448ff2afdf0f045577e38fc53eff5f18`).
- `inputs/original_label.txt`: Literal transcription with footnote hashes.
- `inputs/normalized_no_hashes.txt`: Transcribed text with footnote hashes stripped.
- `inputs/provenance.json`: Cryptographic hashes, dimensions, and provenance metadata.
- `inputs/live_site_photo_run.json` & `live_site_photo_run.png`: Captured live browser run artifacts.
- `runs.csv` & `runs.json`: Full accounting of all 7 real execution runs across engines and platforms.
- `ocr_diff.md`: Character and word error rate analysis against the frozen label photo.
- `synthetic_matrix.csv`: 23 controlled diagnostic variants isolating features one at a time.
- `acceptance.md`: Strict acceptance specification across OCR, parser, classification, and explanation.
- `fix_plan.md`: Modular, ranked implementation plan for the senior review team.
- `STATUS.md`: Machine-readable branch status.

---

## 5. Reproducible Commands

### Parity Check on Local Main
```powershell
python -B scripts/parity_check.py
```

### Run Pipeline Analysis on Literal Input
```powershell
python -B -c "from foodscan.pipeline import analyse_text; print(analyse_text(open('evaluation/label_acceptance_15/inputs/original_label.txt', encoding='utf-8').read(), source='text'))"
```

### Run Pipeline Analysis on Normalized Input
```powershell
python -B -c "from foodscan.pipeline import analyse_text; print(analyse_text(open('evaluation/label_acceptance_15/inputs/normalized_no_hashes.txt', encoding='utf-8').read(), source='text'))"
```
