# headline_aggregation_1: complete one-line abstention reasons (PROPOSAL, revision 2; reason text only; merge stops with the owner)

Branch claude/headline-aggregation-1 off main a6cacbc (independent of claude/label-parser-16-senior; the two touch different regions and merge cleanly). Decision reference: owner instruction 2026-11-22, Priority 2.

## 0. Revision 2 (owner review of 324ac6f)
Revision 1 missed the explicit `food_powder` rows (banana, strawberry, beetroot powder) because its helper checked only newly routed powders, and it ran only on the weak-marker, colour-note and sweetener exits. Now: (a) the powder condition is the classifier's own: any item whose final kind is food_powder (routed or an explicit row) is named unless it is the sole item and states its composition; the powder of an oil or fat unless its own name states 100%; a 100% inside a list does not resolve it; (b) the helper also runs on the not-in-vocabulary, recognised-by-name-only and powder exits, so `Vitamins, XQ9`, `Vitamins, Banana Powder` and `XQ9, Vitamins, Banana Powder` show every layer without any antioxidant. Wording of the powder item: "a powder is named and its composition is not established" (no carrier-frequency claim). The original normalised multigrain headline now names Date, Banana, Strawberry and Beetroot Powder and the unplaced items.

## 1. Change (`classify.py` `other_open_items`, mirrored in `foodscan.js` `otherOpenItems`)
When an abstention is headed by weak or unlisted markers, a colour note or a sweetener-foods entry, the reason now ends with `; other open items: ...` naming the other ACTIVE blockers: items not in the vocabulary, recognised-by-name-only items that no source places (vitamins, minerals, sprouted grains), and the powder of a food or an oil/fat without a stated composition. The item the headline already names is not repeated. Nothing is appended when there is nothing else. No group changes; strong markers still return first (precedence untouched); no placement change. The UI already lists the unplaced and unassessed items below the headline; this only completes the one-line reason. Set-aside group names ('Multigrain Blend (group name; its contents were assessed separately)') are metadata and are not blockers.
Example (pasted text, a6cacbc plus this change): `Multigrain Blend (Sprouted Ragi & Jowar (23.4%), Wheat), Vitamins, Minerals, Antioxidant (INS 320), Edible Vegetable Oil` -> "only weak or unlisted markers present (Antioxidant (INS 320) ...); not enough to call a group; other open items: recognised by name only, no source read places Sprouted Ragi, Sprouted Jowar, Vitamins, Minerals".

## 2. Gates (committed tree vs main a6cacbc; separate fresh processes)
| check | result |
|---|---|
| lexicon / synonyms / markers | 433 -> 433, nothing changed |
| frozen 66 | changed 6, reason text only, group and status unchanged (b1/N07, b1/N11, b3/Q11, neg/R1, dev/F10, dev/F11); unexplained 0; abstain->4 0 |
| out-of-sample 32 | changed 2 (S08, S11), reason text only, group unchanged |
| drift (583) / descriptor (866) / salted (168) / powder (579) | 0 differences / 0 / 0 / 0 changed |
| suite | **2051 passed, 5 xfailed** |
| parity | **875/875** identical (main 859 + 16 added entries, 0 removed; reason and driver compared; earlier 866 is stale) |

## 3. Tests
`tests/test_headline_aggregation_1.py` (new): the multigrain headline names the unplaced items beside the weak marker; nothing appended when no other blocker; powders and vocabulary gaps named; the weak-marker item is not repeated as unrecognised; strong marker (Group 4) and plain abstentions keep their reasons. No existing assertion was changed.

## 4. Exact diff vs main a6cacbc (6 paths, `git diff --name-only a6cacbc HEAD` on the committed tree)
- `evaluation/headline_aggregation_1/README.md`
- `evaluation/headline_aggregation_1/applied_gate/applied_gate.json`
- `scripts/parity_check.py`
- `src/foodscan/classify.py`
- `tests/test_headline_aggregation_1.py`
- `web_preview/foodscan.js`
