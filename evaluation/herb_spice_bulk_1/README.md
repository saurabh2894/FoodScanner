# herb_spice_bulk_1 (staged batch, NOT merged)

Status: STAGED for review. Nothing here is in `src/foodscan/resources/lexicon.csv`. Gate verdict: READY_FOR_REVIEW (see gate/gate_report.md).

Rule: data/ingest/clause_tier1_herbs_spices.json (tier1-herbs-and-spices-1), FAO 2019 Table 1 Group 1 unconditioned clause. Names only; no NOVA group is decided.
Inputs: FDC Foundation Foods 2026-10-29 and SR Legacy 2018-04 (CC0), hashes in scope_summary.json and data/ingest/fdc_downloads_1.json.

## Files
| File | Content |
|---|---|
| candidates_spices_herbs.csv | 66 FDC candidates in category "Spices and Herbs" (unchanged from normaliser output) |
| decisions.csv | one decision + reason code for every candidate in scope of the rule file |
| staged_rows.csv | 37 staged terms with source text and FDC ids |
| scope_summary.json | rule/FAO/FDC hashes; decisions over all 8291 candidates (ACCEPT 42, QUEUE 10, REJECT 14, LABEL_BOUND 840, OUT_OF_SCOPE 7385) |
| gate/gate_report.md, .json | verdict, counts, flip check (0/66 on all compared fields) |
| gate/lexicon_candidate_rows.csv | 25 ready rows in lexicon.csv layout, PROVISIONAL, verbatim clause |
| gate/ambiguity_queue.csv | 10 parked terms (never included) |
| gate/flip_before.json, flip_after.json | per-input dumps from separate fresh processes |

## Review points
1. `kind` is classification-bearing: a merge needs owner verification + senior review.
2. 0/66 flips means no corpus evidence either way: none of the 25 terms occurs in the frozen inputs. Coverage benefit is unmeasured; needs a fresh draw.
3. poppy seed overlaps FAO's conditioned "oily seeds (with no added salt or sugar)" clause: confirm it belongs under the unconditioned herbs/spices clause.
4. 11 rows are variants of existing terms (e.g. caraway seed ~ caraway): confirm they should be separate rows or synonyms.
5. Parked: curry powder, chili powder, garlic powder, onion powder, pumpkin pie spice, pepper (red or cayenne), 4 vinegars.
6. Rejected by rule: salt, prepared mustard, vanilla extracts, canned capers, seasoning mixes, poultry seasoning, prepared horseradish.
7. Merge probe (25 rows appended in a throwaway worktree): 658 passed, parity 395/395.

## Regenerate (refuses to overwrite without --force)
```
python scripts/clause_tier.py --candidates evaluation/herb_spice_bulk_1/candidates_spices_herbs.csv --out evaluation/herb_spice_bulk_1
python scripts/validate_batch.py --staged evaluation/herb_spice_bulk_1/staged_rows.csv --decisions evaluation/herb_spice_bulk_1/decisions.csv --out evaluation/herb_spice_bulk_1/gate --fao-text <pdftotext -layout of ca5644en.pdf>
```
