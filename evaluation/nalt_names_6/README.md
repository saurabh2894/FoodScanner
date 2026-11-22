# NALT naming intake 6

2026-11-22. Base: `17641ff075b8e4d811ff8a1eae653f4733971619`.

This slice adds five plain-food heads (mushroom, lettuce, mangosteen, durian and rambutan) and 26 reviewed names for eleven foods already supported. That is 517 canonical rows and 189 aliases, not 31 new foods. There are no new strong markers and no Python or JavaScript classification-rule changes.

## Two separate evidence jobs

USDA National Agricultural Library's Agricultural Thesaurus (NALT) supplies English food identity and category evidence. It does not assign NOVA. The five admitted foods use current Product-concept pages, not organism/taxon synonyms. FAO's NOVA Table 1 separately supplies placement: the mushroom example is named; fruit and edible leaf instances are class-instance evidence, not exact-named foods. The exact clauses, concept URLs, scope and decisions are in `admission.json` and the new rows' source fields.

- NOVA source: https://www.fao.org/4/ca5644en/ca5644en.pdf
- NALT vocabulary and licence: https://lod.nal.usda.gov/en/
- NALT download actually served: https://lod.nal.usda.gov/downloads/nalt-full_dwn.rdf.zip

Current individual pages were checked on 2026-11-22 for the five new heads and eleven existing-food alias concepts. All ordinary singular/plural additions were reviewed, not automatically admitted by a morphology rule. The archive member is `nalt-full_dwn_20240716.rdf`: despite newer website metadata, the bulk download is a July 2024 archive. It is discovery evidence only. The download metadata and archive hash are retained in the ledgers.

NALT attribution: USDA National Agricultural Library, NAL Agricultural Thesaurus, CC BY 4.0. Naming selections and reviewed singular/plural variants are adaptations. No USDA endorsement is implied. This repository stores selected naming facts, provenance and short classification clauses, not a copy of the full vocabulary or FAO report.

## Repeatable intake, not an automatic importer

Run:

```sh
PYTHONPATH=src python scripts/ingest_nalt_names.py --rdf /path/to/nalt-full_dwn.rdf.zip --out /tmp/nalt-review.json
```

The script parses Product concepts, checks food-class ancestry or existing-head hints and emits a review-only JSON queue. It does not assign a NOVA group, write runtime CSVs or generate singular forms. The checked archive run left 196 verbatim naming candidates after this slice. Those are proposals, not 196 usable foods. Source concepts can aggregate different foods: generic mushrooms must not be mapped to one species, star anise is not aniseed, and local winter-melon names need care. An existing-head hint is not proof of identity. `discovery_queue.json` records this run; `admission.json` records the separate reviewed subset and unresolved cases.

## Form scope and retained holds

For each new head, plain/fresh/raw/dried forms and explicitly whole/pure same-item powders were checked against FAO's relevant examples and named minimal processes. Bare powder stays uncertain. A child's powder or 100% claim does not qualify its parent. Juice, milk, extract, puree, pulp, starch, sauce and concentrate forms are not established by these rows. Existing item-own salt/sugar/brine and unknown-composition guards remain, and supported milk-powder mixtures retain their route. Five-food dried/whole-powder review does not approve new forms for unrelated foods.

The repository's existing unresolved cranberry, tamarind, coconut and celery cases are not lifted. Current thesaurus category evidence alone does not settle their prior form/identity concerns. A proposed singular `flaxseed` alias was also rejected: global substitution would rewrite the supported `flaxseed oil` into an unmatched name. That established Group 2 route is explicitly protected. The other reviewed linseed/plural spellings do not change existing heads.

Historical source/evaluation files are unchanged. The old parked `chick peas` proposal is superseded only by current NALT Product 16207's exact same-food naming evidence. Its qualified forms are tested against the supported chickpea target. All other old parked controls remain. Historical class-row set tests now name the separately sourced five additions explicitly; they do not rewrite old gate results.

## Validation

- 545 new synthetic tests. These are form and integration controls, not real-label accuracy measurements.
- Allowed suite: 4,750 passed, the same two failures on a fresh unchanged-base run, two skipped, one restricted-reference test deselected and five xfailed. The unchanged base had 4,206 passes and the same two failures.
- The two remaining failures concern OCR section extraction on the cached millet-puff image and missing historical fenugreek demand evidence. They remain validation gaps, not acceptable new failures.
- 6,283 full-field Python/JavaScript parity cases: 3,524 OCR-text-path and 2,759 pasted-text cases. This checks the text path, not fresh image recognition.
- 675 existing canonical/alias names: zero normalisation, target, group, status or unassessed-item drift.
- 40,326 alias/parent interactions: zero target-route mismatches.
- 51,745 additional full-field Python/JavaScript comparisons, including the preceding release's wide interaction surface: zero mismatches.
- Frozen 66 labels: no group or other compared-field changes.
- Build completed from the candidate sources. Actual local UI pixels were inspected separately before release.

Original-photo assets and the separate out-of-sample 32 have not been newly validated. No claim of general ingredient coverage, photo-OCR accuracy or completion of the broader expansion follows from this slice.
