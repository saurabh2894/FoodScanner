# per_form_2b: species-head milk recognition (ready for review; NOT merged)

Branch claude/per-form-2b off main 79e3f19. Scope: `cow milk` and `goat milk` as head names (`buffalo milk` was already a lexicon term). `cow` and `goat` stay unrecognised standalone. Decision reference: owner decision 2026-11-21: establish source identity first, then route recognition.

## 1. Source identity (quoted)

| # | source | quote (verbatim) |
|---|---|---|
| S1 | FAO 2019 (ca5644en), Table 1 Group 1 definition | "Edible parts of plants (fruit, seeds, leaves, stems, roots, tubers) or of or from animals (muscle, fat, offal, eggs, milk), and also fungi, algae, all after separation from nature." |
| S2 | FAO 2019, Table 1 Group 1 examples | "fresh, powdered or pasteurized milk" |
| S3 | Monteiro et al., Lancet 2025 | not accessible for verbatim verification; NOT relied on (correction per-form-2c) |

What they cover: S1/S2 place milk as an animal food with no species restriction. S3 is not relied on. What they do not cover: no species is named by any verified NOVA source; standardised/recombined, flavoured or sweetened milk, milk solids (a fraction), human milk.

## 2. Per-row provenance

| term | kind | clauses | inference level |
|---|---|---|---|
| cow milk | whole_food | S1, S2 | class-instance of the animal milk named by FAO; species not named by any verified NOVA source (corrected in per-form-2c; was recorded as NAMED) |
| goat milk | whole_food | S1, S2 | class-instance of the animal milk named by FAO; species not named by any NOVA source read |

Both rows are PROVISIONAL (source text in lexicon.csv).

## 3. Mechanism (and why)

Lexicon rows, not synonyms. A synonym `cow milk -> milk` would delete the species token before the bracket rule runs, so `Rice (Cow Milk)` would read as `Rice (Milk)`. Rows keep the token. `cow`/`goat` are not rows, so they stay unrecognised.
`classify.py`: `_MILK_TERMS` gains both terms; `_MILK_POWDER_ROWS` gains both and `_MILK_POWDER_WORDS` gains `cow`, `goat`, so `<fat-grade> <species> milk powder` takes the existing milk-powder outcome (S2). `bracket_residual`: a species word (cow/buffalo/goat) in a bracket is benign only when the head item is plain milk (a whole_food row in `_MILK_TERMS` minus `milk solids`); on any other head it is unrecognised content. `foodscan.js` mirrors this.

## 4. Frozen-flip attribution

| input | label text | before -> after | status | attributed to |
|---|---|---|---|---|
| b2/M02 | PASTEURISED COW MILK | abstain -> Group 1 | uncertain -> complete | row `cow milk` |
| b3/Q06 | Pasteurized Cow Milk | abstain -> Group 1 | uncertain -> complete | row `cow milk` |
| b3/Q10 | Milk solids (Pasteurized skimmed cow milk) | abstain -> abstain | unchanged | milk solids is not plain milk; stays abstain on its own evidence |

## 5. Gates (committed tree; BEFORE = worktree of main 79e3f19, separate fresh processes)

| check | result |
|---|---|
| frozen 66 | changed 2 (M02, Q06, both attributed); unexplained 0; abstain->4 0 |
| out-of-sample 32 | changed 0; unexplained 0; abstain->4 0 |
| drift (534 existing terms/synonyms) | 0 differences |
| salted surface (141 base-row forms) | 0 changed (unchanged vs 141/42/0 baseline) |
| descriptor surface (768) | 0 changed |
| powder surface (552) | 0 changed |
| lexicon / synonyms / markers | 384 -> 386 rows (+2, none changed); synonyms.csv, markers.csv byte-identical |
| suite | 1620 passed, 5 xfailed |
| parity | 722/722 identical (additions-only, +13 inputs) |

Surfaces probe the base rows so their numbers stay comparable across batches; the two new rows are reported separately (section 7).

## 6. Controls (before -> after group)

| control | before | after |
|---|---|---|
| cow milk | abstain | 1 (drivers identical to `milk`) |
| goat milk (pasteurized) | abstain | 1 |
| pasteurised cow milk / toned cow milk | abstain | 1 |
| cow milk powder | abstain | 1 (driver: "powdered milk", S2) |
| skimmed cow milk powder / goat milk powder | abstain | 1 (same driver) |
| cow milk, starter culture | abstain | 1 (culture rule) |
| milk solids (pasteurized skimmed cow milk) | abstain | abstain |
| cow / goat | abstain | abstain (unrecognised) |
| rice (cow milk), rice (goat milk), egg (cow milk), milk (cow) | abstain | abstain |
| fortified cow milk powder, cow milk solids powder, sheep milk, human milk, cow cheese, cow's milk | abstain | abstain (unassessed) |
| milk (cow milk), milk (goat milk), milk (pasteurized cow milk), buffalo milk, milk | 1 | 1 |
| rice (buffalo milk) | 1 | abstain (see below) |

**Behaviour change outside the frozen/OOS sets:** `Rice (Buffalo Milk)` 1 -> abstain. Before, buffalo was benign in any bracket containing "milk"; now the species rule is head-scoped, so a species milk inside a non-milk item is unrecognised content. Consistent with the existing `Rice (Cow Milk)` abstain. Not in the frozen or OOS inputs.

## 7. New-row forms (after-build only; flagged for decision)

| form | result |
|---|---|
| salted cow milk, roasted salted cow milk, salted goat milk, roasted salted goat milk | None -> 1, same as existing `Salted Milk` (outside the 2a 23-term grain guard; parked) |
| roasted cow milk, roasted goat milk | 1 (global `roasted` descriptor, as `roasted milk`) |
| toasted / toasted salted forms | abstain (toasted is scoped to the 23 grain terms) |
| cow/goat milk powder, 100%/whole variants | 1 (`powdered milk`) |

Decision for you: a salted-milk guard (`Salted Milk`/`Salted Egg`/these) remains parked.

## 8. Exact diff vs main 79e3f19

`data/ingest/per_form_2b.json`, `evaluation/per_form_2b/README.md`, `evaluation/per_form_2b/applied_gate/applied_gate.json`, `scripts/applied_gate.py` (surfaces probe base rows; new-rows section), `scripts/parity_check.py`, `src/foodscan/classify.py`, `src/foodscan/resources/lexicon.csv`, `tests/test_dairy_abstentions.py`, `tests/test_demand_bulk_1.py`, `tests/test_per_form_1.py`, `tests/test_species_milk_2b.py` (new), `tests/test_sweetener_foods_note.py`, `tests/test_thickener_emulsifying_salt_markers.py`, `tests/test_validate_batch.py`, `tests/test_vocab_gap_and_soybean.py`, `web_preview/foodscan.js`. Updated tests carry explanation comments; none weakened. synonyms.csv, markers.csv, descriptors.csv untouched.
