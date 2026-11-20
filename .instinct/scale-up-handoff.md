# Scale-up execution handoff (repo: FoodScanner, branch claude/scale-ingest-1)

Keep this file current: tick a step and update section 3 whenever a step completes.

## 1. Goal and approved scope
Scale vocabulary recognition from open, citable sources in four workstreams, branched from main 3df79d7:
- WS1 demand miner: read-only ranked inventory of unassessed terms across evaluation artifacts. No classification change.
- WS2 supply ingest: USDA FoodData Central (CC0) downloader + normaliser with per-row provenance.
- WS3 clause-tier mapping: one reviewable rule mapping FDC names to candidate herb_spice rows (names -> recognition kind only).
- WS4 validation gate: schema, provenance, duplicates, 66-input flip check (fresh before/after processes), ambiguity queue.
- Staged batches go to evaluation/<batch>/ with candidate rows + gate report. First batch: herb_spice_bulk_1.

## 2. Standing limits
- Sources: FDC CC0 only. IFCT 2017: documented hook only until licence verified. Open Food Facts: reference-only, nothing incorporated. No Codex-derived data (INS Codex table stays parked in data/pending/).
- No paid APIs, no spending, no network calls in the shipped app.
- No classification-rule changes in this work; commodity datasets never decide NOVA groups; no blanket additive-to-NOVA mapping; no per-product hardcoding; keep OCR/extraction/classification separation.
- Conditioned clauses (nuts, juices, plain cereals) stay label-bound; no auto-pass for plain-looking terms.
- Every candidate row: PROVISIONAL, verbatim source clause, per-row provenance.
- Git: push only claude/scale-ingest-1 (status lines go to claude/great-mendel-rx6aek via /tmp/status_line.sh pattern: append one line to .instinct/session-status.md there, commit that file alone, push that branch only). No PR creation, no merge to main, no GitHub comments, no Vercel/artifact actions.
- Staged batches never merge into src/foodscan/resources/lexicon.csv without owner verification and a senior review pass.
- After each step: full suite + `python scripts/parity_check.py` (must be all identical), commit, push, status line.
- Flip check: before/after in SEPARATE fresh processes; any group/status/driver flip -> stop and report.

## 3. Checkpoint
Branch base: main 3df79d7. Suite 658 passed, parity 395/395.
- [x] WS1 demand miner: 8ae89bf (evaluation/demand_inventory_1/)
- [x] WS2 supply ingest: 1365b49 (scripts/fdc_ingest.py, data/ingest/SOURCES.md, fdc_downloads_1.json)
- [x] WS3 clause-tier rule: 7a4394f (data/ingest/clause_tier1_herbs_spices.json, scripts/clause_tier.py)
- [x] WS4 validation gate: 3c6def3 (scripts/validate_batch.py, scripts/flip_dump.py)
- [x] Batch 1 staged herb_spice_bulk_1: gate READY_FOR_REVIEW (25 ready, 12 duplicates, 10 parked, flip 0/66). Commit sha: 4b519ea.
- [x] Test hardened (end-to-end gate test uses absent term; merge probe passes 658).

## 4. Remaining steps (in order)
- [ ] Report all workstreams + batch to the owner in-session; wait for owner verification of herb_spice_bulk_1 (do not merge).
- [ ] On owner instruction only: next staged batch via the same pipeline (candidate categories for the next tier chosen by owner; conditioned clauses stay label-bound).
- [ ] On owner verification + senior review only: merge ready rows into lexicon.csv in a separate commit, rerun suite, parity, 66-input flip check, then build_web_preview (never push main without explicit release decision).

## 5. Fresh-session resume
1. Read this file and .instinct/session-status.md (on claude/great-mendel-rx6aek).
2. `git checkout claude/scale-ingest-1`; `pip install -e ".[dev]"`; run `pytest` and `python scripts/parity_check.py` to confirm the checkpoint.
3. Read evaluation/herb_spice_bulk_1/README.md and gate/gate_report.md.
4. Continue from the first unchecked step in section 4.
