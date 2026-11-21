# Task 18 senior: real-label browser acceptance gate

Branch `claude/browser-acceptance-18-senior` from main 4e626f9. Junior branch `antigravity/browser-acceptance-18` pinned c3ca811458fc922265cc2ed4e8f1dfe1139908b3 reviewed, not merged. No product, classifier or data change: gate scripts, tests, fixtures and evidence only.

## What changed against the junior gate (review items 1-6)
| # | Finding | Correction |
|---|---|---|
| 1 | Windows Chrome path; always `--smoke-live` | Runner is playwright-based (bundled Chromium, or `--browser` / `$FOODSCAN_BROWSER`). Default is deterministic local only. Production is read only with `--smoke-live URL`; `--expected-parity N` compares the observed footer stamp with the stamp you expect (observed-only without it; a footer is never commit proof; production is never required to show any particular number). pytest never contacts production. |
| 2 | `isCurrentSeniorBaseline` = footer is 921 | Removed. `scripts/run_browser_acceptance_18.py` compares `web_preview/dist/{index,foodscan-preview}.html` byte for byte with a fresh in-memory build of the current template, engine and tables (`exact_rebuild_match` / `mismatch` / `unknown`), and records git HEAD, whether the source files are modified, and sha256 of served and rebuilt pages. Mismatch or unknown fails the gate (`--allow-unknown-build` is an explicit opt-in). Footer stamp is recorded as a stamp and checked only for consistency with the current parity total. No product code added. |
| 3 | `expectedDrivers` unused; only group asserted | `fixtures.json` carries item-level expectations per label and per flow: required driver / weak-evidence items, required result mentions (structural warnings, unplaced and not-in-vocabulary names, INS codes, Contains-line declaration), forbidden text. Reading completeness is a separate check, not folded into the group check. Photo flow requires status "Done", at least 20 extracted words, and label-visible items in the extracted text. |
| 4 | L01 correction could be a no-op | Real-OCR correction runs only if the real OCR output contains the artefacts (`Vitamins”`, `Minerals**`); the check asserts the corrected text differs, was exactly what was submitted, and the result changed. Otherwise it is recorded `skipped` with the reason and nothing is claimed. The edit-and-reanalyse is a separate, labelled SYNTHETIC mutation control. |
| 5 | Runner exits 0 on failure; overwrites tracked evidence; hardcoded 921/13 | Exit 1 on any failed check, missing evidence (fixture, screenshot, image hash) or wrong/unknown build; 2 for a partial run (`--skip-photo`). Output goes to `--out-dir` (default a new temp directory). No snapshot counts in tests. |
| 6 | README/JSON mismatch; native picker and pixels | README tables below are generated from the saved JSON. Junior README timings vs its own JSON: L01 photo 5.7 s vs 4164 ms saved, L02 6.2 s vs 4094 ms saved; its "13 of 13 executions" is not comparable with this gate's check count. Pixels: result card screenshots are decoded and must hold content; DOM metrics are separate. Native picker not exercised (limitation in the JSON). |

## Inventory (6 real labels; 3 with a physical photo, 3 text-only)
| Key | Source | Photo |
|---|---|---|
| L01 | multigrain pack; text transcribed by the owner | 57260-byte relay copy (607x494), sha256 beed9e93...; NOT the owner's 81439-byte original, which is not in the repository |
| L02 | millet puff pack | tests/fixtures/millet_puff_label.jpg |
| L03 | potato chips pack | tests/fixtures/chips_label.png |
| L04-L06 | Open Food Facts India negation texts R1-R3 | none in the repository (paste only) |

Reference texts for L02/L03 were extracted from the junior runner; L01 text/image copied unchanged.

## Results (generated from saved JSON, real local OCR)
Main 4e626f9 baseline: 116/116 checks, build `exact_rebuild_match`, git HEAD 4e626f9c, sources modified: False.

| Label | Paste group | Paste completeness | Photo group | Photo OCR time | Reference word recall | Photo completeness (recorded) |
|---|---|---|---|---|---|---|
| L01 | abstain | COMPLETE | abstain | 3.3 s | 1.00 | COMPLETE |
| L02 | 4 | COMPLETE | 4 | 4.2 s | 1.00 | COMPLETE |
| L03 | 4 | UNCERTAIN | 4 | 3.4 s | 0.87 | UNCERTAIN |
| L04 | abstain | COMPLETE | no photo | - | - | - |
| L05 | abstain | COMPLETE | no photo | - | - | - |
| L06 | 4 | COMPLETE | no photo | - | - | - |

Integration (Task 17 v2 template 1c793219 on the same 509-row engine, built in a separate worktree): 116/116 checks, build `exact_rebuild_match`, HEAD 1c793219. Photo timings, same order: L01 4.3 s, L02 4.9 s, L03 4.4 s.

Notes: L01 photo OCR correction status `run` (real OCR contained the footnote artefacts). L03 paste is completeness UNCERTAIN (unclosed bracket) and still Group 4 through the strong-marker exception; L04 and L05 abstain for different reasons (unlisted stabiliser code plus a cut-off item; vocabulary gap), neither driven by the negation sentence.

## Files
- `scripts/run_browser_acceptance_18.py`, `tests/js/browser_acceptance_18_senior.js`, `tests/test_browser_acceptance_18.py` (5 tests: provenance detection, wrong/unknown build fails, wrong expectations/missing evidence fail nonzero, live smoke opt-in and stamp comparison against a local fake site, full real-OCR gate).
- `fixtures.json`, `inputs/`, `evidence/main_4e626f9/` (results, provenance, 13 screenshots), `evidence/integration_task17_1c79321/` (results, provenance).
- Run: `python scripts/build_web_preview.py && python scripts/run_browser_acceptance_18.py` (add `--out-dir evaluation/browser_acceptance_18_senior/evidence/<name>` to refresh evidence on purpose).

## Not claimed
Native file picker, real mobile hardware, pixel-level correctness of every element, production state (never contacted here), cause of the owner's original failed preview.
