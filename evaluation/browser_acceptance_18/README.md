# Task 18 Evaluation: Repeatable Real-Label Browser Acceptance Gate

## 1. Executive Summary & Baselines
- **Branch**: `antigravity/browser-acceptance-18`
- **Base Commit**: `4e626f9cc4775bed7ff4426c10eedcc6c93eb3ae` (merged `claude/integration-1` senior integration `3ff84b5` on `origin/main`)
- **State**: READY FOR SENIOR REVIEW
- **Task Goal**: Build a lightweight, repeatable browser acceptance gate that deterministically distinguishes:
  1. Current `main` baseline from a stale served deployment.
  2. The Photo UI flow (canvas preview + Tesseract WASM OCR) from the Paste text flow.
  3. Reading / OCR completeness from classification logic.
  4. A real end-to-end browser execution from an offline parity check report.
- **Independence & Scope**:
  - Independent of Task 17 (`antigravity/photo-preview-17`, `6796e56`): Task 17's preview fix remains an unmerged branch awaiting senior review. Task 18 does not duplicate its preview code or import unverified claims regarding mobile hardware constraints.
  - No changes made to classifier rules, lexicon resources, marker files, or product code.
  - Zero merges from unreviewed branches (`16` or `17`).

---

## 2. Real User-Label Inventory & Negative Controls

Every test fixture is accounted for below with exact path, SHA-256 hash, physical presence, provenance limitations, and why it is included:

| ID | Name | Repo Path | Real Photo? | SHA-256 | Provenance & Limitations | Role & Diagnostic Value |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- |
| **L01** | Original Multigrain Flour Blend | `evaluation/browser_acceptance_18/inputs/original_multigrain_label.jpg` & `.txt` | **YES** | `beed9e9324b246295fa74e729161640e448ff2afdf0f045577e38fc53eff5f18` | User photograph uploaded via web chat; 57 KB JFIF relay artifact, not camera RAW. | Bracketed blend splitting (`Sprouted Ragi & Jowar`, `Rice & Oat`), footnote mark stripping (`#`, `##`), honest abstention on sprouted grains & powder uncertainty. |
| **L02** | Millet Puff Snack Pack | `tests/fixtures/millet_puff_label.jpg` | **YES** | `0befae618d66bf8c5c78e5eda12db9d1fe3da8b00976eefc3737c36edf3902fb` | Real packaged food photo cropped to label area; stored in repo fixtures. | Section headers with percentages (`Puff 88%:`, `Seasoning 12%:`), INS codes (330, 296, 334, 508, 392), unassessed ingredient (`Amchur`), NOVA Group 4 classification. |
| **L03** | Potato Chips Pack | `tests/fixtures/chips_label.png` | **YES** | `f434a7bf97d5271abeb4db1c51f4d5013575245ab76318319a820aab811eaac9` | Real packaged potato chips photo, small/low-res; in repo fixtures. | Structural warning on unclosed parenthesis (`*Seasoning (`), multiple UPF drivers (`Maltodextrin`, `Flavour Enhancers`), NOVA Group 4 classification. |
| **L04** | D'Lecta Cheese / Milk (Negation R1) | `evaluation/negation_addendum/inputs/R1.txt` | **NO** (Text only) | `e3034aafb1e3400ecd991a005bfbaeacbd458f80657852cd8bde753adc665847` | Open Food Facts India (barcode prefix 890); physical image not retained in git tree. | Verifies negation scoping: `CONTAINS NO ADDED FLAVOUR` does not trigger false Group 4 classification; honest abstention. |
| **L05** | Potato Snack (Negation R2) | `evaluation/negation_addendum/inputs/R2.txt` | **NO** (Text only) | `ec2e141976206803b5e4d56ad06f46d807e3361b2280951ee4d693cbde89cf9e` | Open Food Facts India; physical image not retained in git tree. | Verifies multi-term negation: `No artificial colours, flavours or preservatives` does not trigger false Group 4. |
| **L06** | Flavoured Curd (Mixed R3) | `evaluation/negation_addendum/inputs/R3.txt` | **NO** (Text only) | `251ea3a17682ef5b9f81b80285ad8a3289aa5a5e334cf550cc4974e6beab5036` | Open Food Facts India; physical image not retained in git tree. | Verifies mixed positive + negative clause: `CONTAINS ADDED FLAVOUR(S)` correctly drives Group 4, while `NO PRESERVATIVES` is properly ignored. |

### Strictly Segregated Synthetic Controls
- **NC01 (Empty Input)**: Empty string `""`. Verifies that clearing input and clicking Analyse replaces previous classifications with the honest abstention prompt `"No text to analyse"` and leaves no stale group visible.
- **NC02 (Unknown Synthetic Compounds)**: `Ingredients: SyntheticChemicalX999, FakeCompoundZ404.`. Verifies that an ingredient list composed entirely of unknown words abstains honestly without assigning an arbitrary NOVA group.

---

## 3. Stale-Client Confusion Detection

The gate explicitly inspects and contrasts the local build against the served production deployment:

| Metric / Dimension | Local Build (`main` `4e626f9`) | Live Deployed Site (`https://foodscan-nine.vercel.app/`) | Audit Assessment |
| :--- | :--- | :--- | :--- |
| **URL** | `http://127.0.0.1:<port>/index.html` | `https://foodscan-nine.vercel.app/` | Separate isolated origins |
| **Parity Footer** | `921 of 921 matched at build time` | `859 of 859 matched at build time` | **Stale build detected live** (production lacks 62 recent parity cases) |
| **Lexicon Size** | 509 canonical rows | 433 canonical rows | Production is missing recent meat/fish & senior integrations |
| **HTML Payload** | 586,854 bytes (573 KB) | 509,361 bytes (498 KB) | Confirms older deployed bundle |
| **Fresh Context** | Fresh headless Chrome instance, ephemeral user-data-dir | Inspected in single read-only pass (no looping or hammering) | Isolated, repeatable telemetry |

> [!IMPORTANT]
> The parity footer number (`921 of 921`) is a **build-time static artifact stamp**, not a commit identity or proof of production deployment. A local test run must never claim that a fix is live on production.

---

## 4. Gate Architecture & Runner

### Test Runner Implementation
- **Node.js CDP Driver**: `tests/js/browser_acceptance_18_runner.js`
  - Drives Google Chrome via Chrome DevTools Protocol WebSocket.
  - Exercises **real DOM controls**: sets textarea value, fires standard `input` and `change` events, clicks `#analyse` / `#photo-analyse`, switches tabs via `#tab-text` / `#tab-photo`.
  - Never calls internal private helper functions or `window.FoodScan` directly.
- **Pytest Integration**: `tests/test_browser_acceptance_18.py`
  - Spawns local HTTP server on `web_preview/dist/`.
  - Spawns headless Chrome with isolated temporary user data directory.
  - Executes gate runner, validates 100% pass rate, asserts real-vs-synthetic distinction, verifies mobile viewport metrics, and confirms stale-client audit.
- **Documented Standalone CLI**:
  ```bash
  # Run full deterministic acceptance gate on local build
  python scripts/run_browser_acceptance_18.py

  # Run gate with single-pass live production smoke inspection
  python scripts/run_browser_acceptance_18.py --smoke-live
  ```

---

## 5. Execution Matrix & Test Results

**13 of 13 test executions PASSED cleanly (0 failures) in 24.3 seconds.**

| # | Case | Flow / Action | Input | Viewport | Expected Result | Observed Result | Status |
| :-: | :--- | :--- | :--- | :---: | :--- | :--- | :-: |
| 1 | **L01** | Paste | Multigrain literal text | 1280×720 | Honest abstention, group null | "Not enough information to give a NOVA group", group: null | **PASS** |
| 2 | **L01** | Edit & Reanalyse | Appended `, Sugar, Maltodextrin.` | 1280×720 | NOVA group 4, driver Maltodextrin | "NOVA group 4: ultra-processed foods", driver: Maltodextrin | **PASS** |
| 3 | **L01** | Photo Flow | `original_multigrain_label.jpg` | 1280×720 | OCR completes, honest abstention | OCR done (5.7s), honest abstention, group: null | **PASS** |
| 4 | **L01** | OCR Correction | Fixed OCR quote to `#` in Paste | 1280×720 | Reanalysis completes, group null | Reanalysis done, group: null | **PASS** |
| 5 | **L02** | Paste | Millet puff packaging text | 1280×720 | Group 4, Seasoning flavours driver | "NOVA group 4", driver: Flavours in Seasoning 12% | **PASS** |
| 6 | **L02** | Photo Flow | `millet_puff_label.jpg` | 1280×720 | OCR completes, Group 4 | OCR done (6.2s), "NOVA group 4", group: 4 | **PASS** |
| 7 | **L03** | Paste | Chips packaging text | 1280×720 | Group 4, unclosed bracket warning | "NOVA group 4", warning: unclosed bracket | **PASS** |
| 8 | **L03** | Photo Flow | `chips_label.png` | 1280×720 | OCR completes, Group 4 | OCR done (4.1s), "NOVA group 4", group: 4 | **PASS** |
| 9 | **L04** | Paste | Real Negation R1 | 1280×720 | Honest abstention, no false Grp 4 | "Not enough information...", group: null | **PASS** |
| 10 | **L05** | Paste | Real Negation R2 | 1280×720 | Honest abstention, no false Grp 4 | "Not enough information...", group: null | **PASS** |
| 11 | **L06** | Paste | Real Negation R3 | 1280×720 | Group 4 from positive flavours | "NOVA group 4", driver: ADDED FLAVOUR(S) | **PASS** |
| 12 | **NC01** | Paste | Empty string `""` | 1280×720 | "No text to analyse", group null | "No text to analyse", group: null, no stale card | **PASS** |
| 13 | **NC02** | Paste | Synthetic chemicals | 1280×720 | Honest abstention, group null | "Not enough information...", group: null | **PASS** |

Structured JSON data is persisted at `evaluation/browser_acceptance_18/test_results.json`.

---

## 6. Pixel & Layout Inspection

Captured across both desktop (1280×720) and mobile (390×844) viewports:

- **Desktop (1280×720)**:
  - `clientWidth`: 1280px, `scrollWidth`: 1280px (`hasHorizontalOverflow: false`).
  - `#analyse` button: width 78.4px, height 36px, visible, not clipped.
  - Result card: fully within viewport boundaries.
- **Mobile (390×844)**:
  - `clientWidth`: 390px, `scrollWidth`: 390px (`hasHorizontalOverflow: false`).
  - Strict horizontal containment verified: no content or button causes horizontal scroll.
  - `#analyse` button: visible, contained, fully clickable.
- **Key Screenshots in `screenshots/`**:
  - `viewport_desktop_1280x720_multigrain.png`
  - `viewport_mobile_390x844_multigrain.png`
  - `live_production_desktop_1280x720.png`
  - `paste_l01_1280x720.png` through `paste_l06_1280x720.png`
  - `photo_l01_complete_1280x720.png`, `photo_l02_complete_1280x720.png`, `photo_l03_complete_1280x720.png`
  - `l01_multigrain_edited_reanalyse_1280x720.png`
  - `l01_multigrain_ocr_corrected_paste_1280x720.png`
  - `nc01_empty_input_1280x720.png`, `nc02_unknown_chemical_1280x720.png`

---

## 7. Safety, Parity & Invariance Checks

- **Parity Check**:
  ```bash
  $ .venv\Scripts\python.exe scripts/parity_check.py
  921/921 analyses identical between Python and JS (843 photo-path texts, 78 pasted-text texts)
  ```
- **Boundary Verification**:
  - Zero edits to `src/foodscan/` Python backend.
  - Zero edits to `lexicon.csv`, `synonyms.csv`, or `markers.csv`.
  - Zero edits to `web_preview/template.html` (Task 17 preview work unmerged and untouched).
  - All additions strictly scoped to `tests/js/browser_acceptance_18_runner.js`, `tests/test_browser_acceptance_18.py`, `scripts/run_browser_acceptance_18.py`, and `evaluation/browser_acceptance_18/`.
