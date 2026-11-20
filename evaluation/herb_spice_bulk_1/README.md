# herb_spice_bulk_1 (staged batch, NOT merged into lexicon.csv by this README's step)

Status: STAGED, revision 2 (owner review fixes applied). Gate verdict: READY_FOR_REVIEW (gate/gate_report.md).
Rule: data/ingest/clause_tier1_herbs_spices.json (tier1-herbs-and-spices-1), FAO 2019 Table 1 Group 1 unconditioned clause. Names only; no NOVA group is decided.
Variant policy: data/ingest/variant_policy_1.json (below). Inputs: FDC Foundation Foods 2026-10-29 and SR Legacy 2018-04 (CC0), hashes in scope_summary.json.

## Revision 2 changes (from the owner's review)
1. `poppy seed` moved from ready to the ambiguity queue (origin `policy`, reason `overlaps_conditioned_clause`): FAO's conditioned "tree and ground nuts and other oily seeds (with no added salt or sugar)" clause overlaps it and the boundary is unresolved.
2. Variant policy (consistent, enforced by the gate): SAME ingredient + SAME plant part + SAME form as an existing row -> synonym in synonyms.csv, not a new lexicon row; DIFFERENT plant part or species -> separate row.
   | Staged term | Disposition | Why |
   |---|---|---|
   | anise seed | synonym -> aniseed | same ingredient, part (seed), form |
   | caraway seed | synonym -> caraway | same |
   | cumin seed | synonym -> cumin | same |
   | fenugreek seed | synonym -> fenugreek | same |
   | fennel seed | already recognised (dropped as duplicate in revision 1) | consistent with the four above |
   | coriander leaf / coriander seed | separate rows | different plant parts; bare `coriander` (existing, ambiguous between parts) is left untouched, not widened |
   | dill weed / dill seed | separate rows | different plant parts; bare `dill` left untouched |
   | peppermint / spearmint | separate rows | different species from `mint` |
   The gate now BLOCKS when a ready row is a variant of an existing row that the policy neither maps nor keeps as a separate row.
3. Provenance wording: the clause literally names thyme, oregano, mint, pepper, cloves and cinnamon. `oregano` and `thyme` now say "exact term IS named by the clause" (rule file `named_terms`, checked against the clause text in code). Every other row says "exact term not named by the clause"; `peppermint` and `spearmint` add "the clause names the broader term 'mint'". Audit of existing lexicon rows: none of them makes a named/not-named claim (their sources say "exact label term seen on ..."), so none is wrong; `mint`, `pepper`, `cinnamon` and `cloves` are in fact named by the clause but their sources do not say so (not changed here).
4. Mapper hardening (no change to the 66 decisions, verified byte-identical): a Group 2 word anywhere in a candidate's name, not only in the head, now REJECTs (`group2_word`), so the series rule can never turn "Spices, garlic, salt" into a label term.

## Counts (revision 2)
37 staged = 20 new lexicon rows + 4 synonyms + 12 duplicates dropped (unchanged from revision 1) + 1 parked by policy (poppy seed). Plus 10 parked by the mapper (curry powder, chili powder, garlic powder, onion powder, pumpkin pie spice, pepper (red or cayenne), 4 vinegars). Rejected by rule: salt, prepared mustard, vanilla extracts, canned capers, seasoning mixes, poultry seasoning, prepared horseradish.
Flip check (66 frozen inputs, before/after in separate fresh processes, lexicon 115 -> 135 rows and 4 synonym rows added): 0 changes on every compared field. 0/66 means no corpus evidence either way; see out_of_sample/ for the fresh draw.

## Files
| File | Content |
|---|---|
| candidates_spices_herbs.csv | 66 FDC candidates in category "Spices and Herbs" |
| decisions.csv | one decision + reason code per candidate |
| staged_rows.csv | 37 staged terms with source text and FDC ids |
| scope_summary.json | rule/FAO/FDC hashes; decisions over all 8291 candidates |
| gate/gate_report.md, .json | verdict, counts, flip check |
| gate/lexicon_candidate_rows.csv | 20 ready rows (lexicon.csv layout) |
| gate/synonyms_candidate_rows.csv | 4 synonym candidates (synonyms.csv layout) |
| gate/ambiguity_queue.csv | 11 parked terms (never included) |
| gate/flip_before.json, flip_after.json | per-input dumps from separate fresh processes |

## Regenerate (refuses to overwrite without --force)
```
python scripts/clause_tier.py --candidates evaluation/herb_spice_bulk_1/candidates_spices_herbs.csv --out evaluation/herb_spice_bulk_1 --force
python scripts/validate_batch.py --staged evaluation/herb_spice_bulk_1/staged_rows.csv --decisions evaluation/herb_spice_bulk_1/decisions.csv \
  --candidates evaluation/herb_spice_bulk_1/candidates_spices_herbs.csv --out evaluation/herb_spice_bulk_1/gate --policy data/ingest/variant_policy_1.json \
  --fao-text <pdftotext -layout of ca5644en.pdf> --force
```
