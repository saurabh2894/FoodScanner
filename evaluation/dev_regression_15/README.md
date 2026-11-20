# Development regression batch: 15 products (NOT validation)

Status: this batch has been used in development (failures were found on it and reported), so it is **regression material only**. Any
final independent check needs a fresh batch of labels not seen during development.

- Candidate commit under test: `c91be3f` (frozen before scoring; no code changed while scoring). Frozen outputs: `frozen_results_c91be3f/`.
- Inputs: `inputs/Fnn.txt` = the untouched Open Food Facts `ingredients_text` used as the paste input. Photos: URLs in `manifest.json`
  (Open Food Facts; terms as stated by that site: database ODbL, images CC BY-SA; not independently verified here). Photos are not copied into this repository.
- References: `references.md` (item-level, hand-prepared by an LLM from the photos, to be spot-checked by the project owner).
- Not claimed: accuracy, validation, or that the two modes are comparable. 13 judged products (F10, F13 unjudged) is a smoke test.

## Known limitations recorded here
- **Photo OCR coverage (failure 5):** the in-browser OCR found no ingredient list on 5 of 15 real photos and read others with heavy noise
  (list located on 10/15; 48 of 104 items recognisable). The app abstains rather than guess; that behaviour is correct and no change is planned.
- Headless-list case and colour-only Group 4 (failure 8): documented, no rule change.
- Follow-up fixes on a separate branch (not in the corrective release): failures 2 (one joint "X and Y [codes]" phrase split in two),
  3 (a stray bracket swallows the list), 4 (a third list section not read; double section label), 6 (misleading "truncated" wording for a
  one-line list), 7 (vocabulary coverage: besan, toned milk, pickles).
