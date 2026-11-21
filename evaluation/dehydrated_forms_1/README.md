# dehydrated_forms_1: term-level 'dehydrated X' and 'X flakes' mappings (branch claude/dehydrated-forms-1, off main ac6ead1)

Owner decision (2026-11-21): the free-floating 'dehydrated' descriptor is REJECTED, and so is any generic 'flakes' descriptor. Each form gets its own sourced mapping to a source-supported dried form, or stays unassessed. Policy: data/ingest/dehydrated_policy_1.json; gate: scripts/synonym_batch.py (drift over 303 existing terms, positives, negative controls, 66-input flip check in separate fresh processes).

## Three synonyms, each its own decision, all to the existing `onion` row
`dehydrated onion`, `onions flakes`, `onion flakes` -> `onion`. Dried vegetables are source-supported twice: FAO 2019 Table 1 Group 1 "Fresh, squeezed, chilled, frozen, or dried fruit and leafy and root vegetables" and PMC10127522 (licence unverified; paraphrase: dried vegetables without added sugars coded unprocessed/minimally processed). FDC (CC0) names "Onions, dehydrated flakes" (sr_legacy 170002). That 'dehydrated' means dried is a definitional step, stated in each row's provenance and not claimed from a source. Behaviour equals `dried onion` exactly (already recognised through the existing descriptor), so no new exposure: a single-item list is Group 1, with salt it is Group 3.

## Stays unassessed (no sourced single dried-form row)
`dehydrated vegetable` (a class with unstated contents; no row to map to); other forms are controls that must NOT map: dehydrated vegetables, dehydrated potato flakes (a mashed-potato product in FDC), dehydrated garlic, dehydrated milk, dehydrated mango, corn flakes, rice flakes, chilli flakes (existing row, unchanged); fried onion flakes and fried dehydrated onion must stay unrecognised. `dehydrated carrot` is a further candidate (FDC 'Carrot, dehydrated') but not a demand term, so it is not added.

## Flip evidence vs main ac6ead1
66 frozen inputs: group, drivers, status, reason, warnings, ingredients, INS 0 changes; unassessed on 2 inputs, both attributed (dev/F03 'Onions Flakes (1.15%)', dev/F07 'dehydrated onion'), 0 unexplained. Out-of-sample 32: only S32 changes: 'Dehydrated Onion' leaves the unassessed list and the abstention reason text lists one item fewer; group (abstains) and status unchanged. Drift: 0 existing terms changed. Suite 1159 passed + 5 expected failures; parity 463/463.
