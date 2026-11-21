# engine_fixes_1: two recorded defects (ready for review; NOT merged)

Branch claude/engine-fixes-1 off main 38e85f1.

## Defect 1: prefix-of-target alias rewrite (fix: target-safe rewrite)
Cause: `normalise._apply_synonyms` applies every alias as a word-bounded substring rewrite, so an alias that is a strict word-prefix of its own target fired INSIDE the target's name: `bok choy` -> `bok choy cabbage` turned the canonical `bok choy cabbage` into `bok choy cabbage cabbage`.
Fix (explicit guard, mirrors the existing 'dal' tail): when a target starts with `<alias> `, the alias pattern also absorbs the remaining target words if they follow (`(?:\s+cabbage(?![a-z]))?`), so the canonical name is matched once and left alone. Chosen over longest-match because the tail is local to the one pattern (no ordering dependence, no change for any other alias); no existing synonym row has a prefix-of-target shape, so no existing row changes. Mirrored in `web_preview/foodscan.js` (parity below).
The previously excluded row `bok choy -> bok choy cabbage` is re-added to synonyms.csv with the exact provenance built by `scripts/alias_apply.py --only "bok choy"` (FDC 170390 Common Name row 2503). Proof: `bok choy cabbage` Group 1 -> Group 1 unchanged; `bok choy` None -> Group 1 routed to it; `pak choi`, `Bok Choy (raw)` route to it; `Salted Bok Choy` Group 3 (the canonical row's condition applies through the alias).
## Defect 2: chinese cabbage provenance (text only)
The `chinese cabbage` lexicon row cited FDC 169979 (pe-tsai) AND 170390 (pak-choi). The 170390 citation is replaced by a CORRECTION note: that record's Common Name is 'pak choi, bok choy' (the food of row `bok choy cabbage`, alias `pak choi`); the row now cites its own record only (169979). Kind, source clause, placement, conditions and recognition are unchanged (gate: chinese cabbage Group 1 -> Group 1).

## Gate evidence (committed tree, re-run on the clean tree: both JSON files identical)
| gate | BEFORE | rows/diffs | frozen 66 changed | OOS 32 changed | unexplained | abstain->4 | drift probes / differences | alias==target compared / mismatches | powder-surface changes |
|---|---|---|---|---|---|---|---|---|---|
| `applied_gate_vs_main` | main 38e85f1 | 1 synonym row (bok choy), 1 provenance string | 0 | 0 | 0 | 0 | 533 / 0 | 12 / 0 | 0 |
| `applied_gate_alias_surface` | d27faee (pre synonyms-2) | the full 24-alias set (23 + bok choy), 1 provenance string | 0 | 2 (S01, S24: the synonyms-2 recognition-only changes, no group/status move) | 0 | 0 | 510 / 0 | 288 / 0 | 0 |
Also: synonyms.csv additions-only (150 -> 151 lines vs main; 127 -> 151 vs d27faee, base lines kept in order); lexicon.csv: 0 added, 0 removed, 0 kind changes, source changed for exactly one term (chinese cabbage); markers.csv untouched; after-build proof 1/1 and 24/24.
## Exact diff vs main 38e85f1 (14 files, including this README)
`data/ingest/engine_fixes_1.json` (controls), `evaluation/engine_fixes_1/{applied_gate_alias_surface,applied_gate_vs_main}/applied_gate.json`, `evaluation/engine_fixes_1/synonym_rows_24.csv`, `scripts/alias_apply.py` (bok choy un-parked; `--only`), `scripts/applied_gate.py` (`--allow-source-change`), `scripts/parity_check.py` (+3 lines = 12 new inputs, 0 lines removed), `src/foodscan/normalise.py` (+5), `src/foodscan/resources/lexicon.csv` (1 line), `src/foodscan/resources/synonyms.csv` (+1 line), `tests/test_engine_fixes_1.py` (new), `tests/test_synonyms_2.py` (3 tests updated: bok choy leaves the parked list), `web_preview/foodscan.js` (+4/-1), `evaluation/engine_fixes_1/README.md`.
Suite 1494 passed, 5 xfailed; parity 653/653 (641 + 12 additions, 0 removed).
