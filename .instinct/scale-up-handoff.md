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
- OFF texts never enter the repo from new draws (gitignored cache); OFF is evaluation material only. Git: push only claude/scale-ingest-1 (status lines go to claude/great-mendel-rx6aek via /tmp/status_line.sh pattern: append one line to .instinct/session-status.md there, commit that file alone, push that branch only). No PR creation, no merge to main, no GitHub comments, no Vercel/artifact actions.
- Staged batches never merge into src/foodscan/resources/lexicon.csv without owner verification and a senior review pass.
- After each step: full suite + `python scripts/parity_check.py` (must be all identical), commit, push, status line.
- Flip check: before/after in SEPARATE fresh processes; any group/status/driver flip -> stop and report.

## 3. Checkpoint
Branch base: main 3df79d7. Suite 777 passed + 6 xfailed (known plural gap, strict xfail), parity 395/395.
- [x] WS1 demand miner: 8ae89bf. [x] WS2 supply ingest: 1365b49. [x] WS3 clause-tier rule: 7a4394f. [x] WS4 validation gate: 3c6def3.
- [x] Batch 1 staged, then revision 2 (dc3babf): poppy seed parked, variant policy data/ingest/variant_policy_1.json (4 synonyms, 6 separate rows), oregano/thyme "IS named" provenance, Group-2 word anywhere in a name rejects, mapper exclusion tests. Gate READY_FOR_REVIEW: 20 rows + 4 synonyms, flip 0/66.
- [x] Out-of-sample tooling (scripts/oos_draw.py, scripts/oos_eval.py): texts in gitignored cache data/cache/oos_herb_spice_1/ (NOT in repo), manifest + results + FINDINGS committed. Licence status: storage MINIMIZED, not resolved; NOTICE added; OFF never appears in production source columns.
- [x] Integration prep on the feature branch: gate rows merged into lexicon.csv/synonyms.csv (6cf9a99), tests/test_herb_spice_bulk_1.py (synthetic), research/07 held-category note (sources and clause fit only, no rows).
- [x] Challenge-set results: 32 labels, 7 of 24 targets with no label; 40 recognised / 24 not / 2 inside another item; see evaluation/out_of_sample_herb_spice_1/FINDINGS.md.

- [x] Peel-label guard (branch claude/peel-label-guard-1, off main 5ce13fa): release-exposed regression repair in parser._peel_label + JS port; sweep in evaluation/peel_label_sweep_1/. Awaiting owner verification; NOT merged.

- [x] Cycle 2 workstream A (branch claude/plural-synonyms-1, off main d1bc5d5): 37 plural/leaf/plural-spelling synonyms via data/ingest/plural_policy_1.json + scripts/synonym_batch.py; evaluation/plural_synonyms_1/. Awaiting owner verification; NOT merged. Next: B (demand-driven bulk batches from evaluation/demand_inventory_1), then C (held-category sources).

- [x] Cycle 2 B1 (branch claude/demand-bulk-1, off main 6a6334f): 4 rows + 1 synonym from the 110 open demand terms, 5 marker proposals for owner decision, 96 parks; evaluation/demand_bulk_1/. Awaiting owner verification; NOT merged. A and the 3.12 fix are merged (6a6334f). C (held-category sources) next. Acceptance probe still needs the owner's label text.

- [x] Cycle 2 C (branch claude/held-sources-1, off main 1eb06e0): research/07 reading pass 2, 3 fruit/vegetable powder rows, acceptance label unassessed 6 -> 3 and group still abstains; photo-preview hardening on claude/photo-preview-1 and markers on claude/markers-1 await verification. Next: B2 (cocoa/glucose block; include the Monteiro 2018 'whey/lactose' evidence as marker proposals), then typo policy. Open owner decision: an 'unplaced' recognition-only kind (code change).
- [x] Cycle 2: demand-bulk-1 merged (1eb06e0). Acceptance probe run on the merged build: no change vs d1bc5d5, group honestly abstains. Branch claude/markers-1 (off main 1eb06e0): 5 owner-approved strong markers, evaluation/markers_1/. Awaiting owner verification; NOT merged. Next: B2 (cocoa/glucose source read + admissible-source survey, report before using), then typo policy, then C.

- [x] main d7e225d: markers-1, photo-preview-1 and corrected held-sources-1 merged. Branch claude/unplaced-kind-1 (off d7e225d): the 'unplaced' recognition-only kind (code change), rows for vitamins/minerals and sprouted ragi/jowar; awaiting owner verification, NOT merged. Pending: senior review of antigravity/audit-1 when it lands (triage WRONG / INFERRED / UNVERIFIABLE-in-scope; no row changes before the owner reviews the evidence; proposed fixes held at merge-stop); the '&' split measurement is owned by the junior (antigravity/audit-1, evaluation/ampersand_split_sim_1/). Demand inventory fully decided: next growth = re-research of parked terms against NEW admissible sources.

- [x] main 95546b9: unplaced-kind merged. Branch claude/source-survey-1: research/08 admissible-source survey (report only; PMC throttles bulk reads; new candidate PMC10127522 partly read; FSSAI 502). Standing protocol: EVERY stop ends with a pushed status line.

- [x] main 0463b45: source-survey-1 merged (starch/tapioca starch rows, modified-starch guard, research/08). Branch claude/pmc-reresearch-2: coconut fat row + parks/proposals (evaluation/pmc_reresearch_2); awaiting owner verification, NOT merged.

- [x] main ac6ead1: pmc-reresearch-2 merged (coconut fat). Branch claude/dehydrated-forms-1: 3 term-level synonyms (dehydrated onion, onion flakes, onions flakes -> onion); no 'dehydrated' or 'flakes' descriptor (owner); awaiting verification, NOT merged.

- [x] main de86733: dehydrated-forms-1 merged. Branch claude/pmc-reresearch-3: re-read of the remaining parks; one proposal (whey powder / whey solids strong markers, NOT in markers.csv); everything else stays parked; awaiting owner decision.

## 4. Remaining steps (in order)
- [ ] Owner verification of the branch (they verify independently), then a bounded merge instruction. STOP before any merge to main.
- [ ] Owner decisions listed in FINDINGS.md (plural/leaf synonyms, S19 status change, untested targets).
- [ ] Only on instruction: next staged batch (held categories per research/07 need sources first); conditioned clauses stay label-bound.

## 5. Fresh-session resume
1. Read this file and .instinct/session-status.md (on claude/great-mendel-rx6aek).
2. `git checkout claude/scale-ingest-1`; `pip install -e ".[dev]"`; run `pytest` and `python scripts/parity_check.py` to confirm the checkpoint.
3. Read evaluation/herb_spice_bulk_1/README.md and gate/gate_report.md.
4. Continue from the first unchecked step in section 4.
