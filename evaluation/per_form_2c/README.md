# per_form_2c: cow milk provenance wording (ready for review; NOT merged)

Branch claude/per-form-2c off main cecccb9. Provenance/wording only. Decision reference: owner correction 2026-11-21 (a Lancet 2025 sentence could not be verified verbatim, so it cannot support a NAMED claim).

## Change
- `lexicon.csv` row `cow milk`: Lancet 2025 quote and "NAMED (as cow's milk)" removed. Placement rests on FAO 2019 Table 1 Group 1 (definition; example "fresh, powdered or pasteurized milk"; no species restriction). Inference level: class-instance of the animal milk named by FAO, the same label `goat milk` carries. One line records that the Lancet sentence was not accessible for verbatim verification and is not relied on. Exclusions kept (standardised/recombined, flavoured/sweetened, milk solids, human milk).
- `evaluation/per_form_2b/README.md`: S3 marked not relied on; `cow milk` provenance row corrected; the "S3 names" sentence removed.
- Test comments/docstring (`test_sweetener_foods_note`, `test_thickener_emulsifying_salt_markers`, `test_vocab_gap_and_soybean`, `test_dairy_abstentions`, `test_species_milk_2b`) no longer cite Lancet. `test_species_milk_2b` provenance test now asserts class-instance on both rows and no NAMED/Lancet text on `cow milk` (assertion on the removed wording replaced; no behavioural assertion weakened).
- Unchanged by design: `evaluation/per_form_2b/applied_gate/applied_gate.json` (frozen record of the 2b run) and `data/ingest/per_form_2b.json` (controls).

## Gates (committed tree vs main cecccb9; separate fresh processes)
| check | result |
|---|---|
| lexicon | 386 -> 386; only `cow milk` source_changed; none added/removed/kind-changed |
| synonyms.csv / markers.csv | byte-identical |
| frozen 66 / out-of-sample 32 | changed 0 / 0; unexplained 0; abstain->4 0 |
| drift | 536 probed, 0 differences |
| salted (147) / descriptor (772) / powder (558) surfaces | 0 changed (probe counts include the 2b rows, now base rows) |
| suite | 1620 passed, 5 xfailed |
| parity | 722/722 identical |
