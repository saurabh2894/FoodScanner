# Senior review: antigravity/class-bulk-5-nuts (FDC 'Nut and Seed Products'); docs-only

Reviewed head 0fcdcd5 (one commit on base 38e85f1). Decision reference: owner instruction 2026-11-21 (senior review, then staging proposal; no merge).

## 0. Boundary check

| check | result |
|---|---|
| merge-base with stated base | 38e85f1 (equal); branch is a single commit on it |
| `git diff --name-only 38e85f1...0fcdcd5` | 6 paths, all under `evaluation/class_bulk_5_nuts_1/`: `README.md`, `STATUS.md`, `accept_records.csv`, `queue.csv`, `reject.csv`, `source_rules.md`; no ingest file declared; no path outside the folder |
| `accept_records.csv` sha256 (raw blob bytes) | `a42793e2579d6c15348cd9ba8fea55487457687aa576a2f3b5ef6d19622e2c9e` (18429 bytes) |

Hash convention: pin the sha256 of the raw blob bytes with no added trailing newline (an extra newline makes 18430 bytes and a different hash). Resolved with the owner; the pin is the value above.

## 1. Counts reproduced

| measure | reproduced |
|---|---|
| FDC candidates, category exactly 'Nut and Seed Products' | 156 (137 SR Legacy + 19 Foundation); equal, key for key, to the category filter of the cached FDC files; no duplicates, none missing, none extra |
| accept / queue / reject (junior) | 52 / 59 / 45 = 156 |
| record names vs raw FDC `food.csv` description | 156/156 identical |
| accept split | 27 canonical foods: 3 already in lexicon (almonds 3 records, pumpkin seeds 2, flax seeds 1 = 6 records) + 24 new canonical (46 records) |
| queue / reject reason codes | match the junior README breakdowns exactly |

## 2. Evidence re-verified

**FAO ca5644en (local text, Table 1; columns rebuilt from the layout).** Verbatim matches: Group 1 example "tree and ground nuts and other oily seeds (with no added salt or sugar)"; Group 1 minimal-processing definition (full sentence, "...do not add salt, sugar, oils or fats or other food substances to the original food."); Group 3 example "salted or sugared nuts and seeds"; Group 2 example "Vegetable oils crushed from seeds, nuts or fruit (notably olives)". All 52 accept rows cite the same Group 1 clause, which passes.

**Defect (prose only, no row affected).** `source_rules.md` puts in quotation marks "other methods that do not add salt, sugar, oils or fats to the original food". That is not verbatim: the source reads "...oils or fats or other food substances to the original food". It does not pass as a quote; use the full sentence.

**FDC names and IDs.** 52/52 accept record names equal the cached FDC description. 'name states X' claims: all true. Portion claims ('whole', 'in shell'): present in `food_portion.csv`, but a portion word is a measure, not a form statement. Records resting on portion words alone: 169414 (flaxseed), 170187 (walnuts, english), 170567 and 170568 (almonds), 170581 (hazelnuts). They are kept as supporting records, not as plain-form evidence; every staged canonical still has at least one record whose name or FoodOn attribute states the form (walnuts 170186/2346394, hazelnuts 2515375). Note the inconsistency this exposes: 170581 'Nuts, hazelnuts or filberts' accepted on portions while 170182 'Nuts, pecans' was queued as form-not-stated.

**Inference level, oily seeds.** The clause says "tree and ground nuts and other oily seeds"; 'oily' qualifies seeds. FDC total fat (g/100 g, measured from the cached files; recorded as a measurement, not as placement): breadfruit seeds 5.6, breadnut seeds 1.0-1.7, lotus seeds 0.5-2.0, sisymbrium seeds 4.6, against 24-80 for every other accepted nut or seed. For those four canonicals (6 records) 'oily seed' membership is not supported by any source read, so they are held (queue), not staged. Chestnuts (0.5-4.5) and ginkgo nuts (1.7-2.0) stay: their FDC names are 'Nuts' and the clause names tree nuts without the 'oily' qualifier; inference level class-instance of tree nuts, caveat recorded.

## 3. Chestnuts dedup

Eight records map to one canonical `chestnuts` (169408 japanese dried, 169413 japanese raw, 170164/170165 chinese raw/dried, 170167 european dried peeled, 170574/170575/170576 european raw/dried, peeled/unpeeled). All eight IDs are kept in the row provenance; none dropped.

## 4. Reject/queue overlap words

Words in both lists: roasted, toasted, salt, without, butter, canned. One deterministic rule, applied in order (coconut rows are queue first, standing hold):
1. positive added salt ('salt added', 'lightly salted', 'salted'; not 'without salt') -> reject
2. 'oil roasted', 'honey roasted', 'glazed', flavoured, formulated -> reject (added oil, sugar or other substances)
3. roasted/toasted with 'without salt' or no salt statement -> queue
4. canning alone, or boiling/steaming alone, with no added salt, sugar or brine stated -> queue (the repository guard abstains on 'canned' without stated brine; boiling and steaming are FAO-listed minimal processes)

The rule reproduces the junior disposition on every record it fires for except five, all moved reject -> queue: 168589, 170166, 170168 (chestnuts boiled and steamed), 170145 (breadfruit seeds boiled), 170176 (ginkgo nuts canned). The junior treated roasting (queue) and boiling (reject) differently although the junior's own quoted clause lists both as minimal processes.

| measure | junior | senior |
|---|---|---|
| accept: stage (new rows) | 46 records / 24 canonical | 40 records / 20 canonical |
| accept: already in lexicon, no row change | 6 | 6 |
| queue | 59 | 70 (59 + 5 moved + 6 held records) |
| reject | 45 | 40 |
| total | 156 | 156 |

Per-record dispositions: `05_nuts_dispositions.csv`.

## 5. Parked from this review (not implemented)

- Synonym candidates in the junior README (filberts, pepitas, pinyon pine nuts, black/english walnuts, japanese/chinese/european chestnuts) are naming-only and not staged. Singular and plural label forms (cashew, cashews, pistachios, walnut, sesame, chia seed) are likewise not staged; a label that uses them stays 'not in the local vocabulary' (abstain).
- Queue groups (butters, flours/meals, coconut, roasted plain, mixed, unstated) need per-form decisions; untouched.
