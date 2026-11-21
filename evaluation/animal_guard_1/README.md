# animal_guard_1: bounded animal-food guard and eight meat/poultry rows (PROPOSAL; merge stops with the owner)

Branch claude/animal-guard-1 off main a6cacbc00fe3f8543a78f002b952a9a64375c4fd. Inputs: the owner's completed senior review revision 2 (reviewed candidate table; 76 plain candidates, 8 meat + 68 fish) and its overlay acceptance handoff. Decision reference: owner instruction 2026-11-22, Priority 3. The 68 fish rows are a separate stacked proposal (claude/animal-fish-rows-1). Candidates are not live coverage.

## 1. Guard (classify.py, mirrored in foodscan.js; animal row = a whole_food row whose source records the class-instance placement under the FAO example 'meat, poultry, fish and seafood, whole or in the form of steaks, fillets and other cuts')
1. **Dried or dehydrated animal food -> Group 3, scoped to meat, poultry and fish (owner review of 6a30fe3).** The FAO Group 3 example says 'meats and fish', not seafood; the Group 1 example groups seafood with fish but the dried example does not. Each row records `DRIED-G3-SCOPE: meat` (the 8 meat/poultry rows here) or `DRIED-G3-SCOPE: finfish` (fish labels, in the fish proposal) or `DRIED-G3-SCOPE: none` (crab, lobster, mussel, oyster, octopus, scallop, in the fish proposal). A dried form of a row with scope none abstains ("a dried form of an animal food is named (...): the FAO Group 3 example names dried meats and fish only ... and drying alone does not make it Group 1"): neither Group 3 nor the generic-drying Group 1. No evidence for extending the example to crustaceans or molluscs was found, so none is assumed. This proposal has no such row; the rule is tested on a lexicon copy with test rows. Original wording:  The overlay showed `Dried X` Group 1 for all 76; FAO Table 1 Group 3 names "salted, dried, cured, or smoked meats and fish". Only the word `dried` reaches the rule (a descriptor already resolved by lookup); `dehydrated X` stays unrecognised (abstains). In a list a dried animal item counts as a Group 3 item (`Dried Chicken, Salt` Group 3).
2. **Animal powders abstain.** `X powder`, `100% X powder`, `whole X powder`, `X (powder)`, `dried X powder`, and powders with other content abstain with "a powder of an animal food is named (...): no source read names powdered meat, poultry, fish or seafood, so its form and composition are not established and no group is asserted, whatever percentage the item states". The overlay's 74 Group 1 answers for `100% X powder` are withdrawn; a 100% in the text cannot establish an unsupported form.
3. **Deliberately not changed:** ground, roasted, boiled and steamed X stay Group 1 (grinding, steaming, boiling and roasting are named minimal processes WITH their no-added-substance condition; the whole-food observed-condition guard keeps that condition: `Roasted Chicken (sunflower oil)` and salted forms abstain); salted, smoked, cured, canned, breaded, battered, fried, pan-fried, minced, formed and generic cooked X abstain as before; unknown brackets and distinct nested foods (`Beef (Rice)`, `Beef (Milk)`) abstain; `Chilled X` still abstains (a possible narrow recognition improvement, not done here); plant, dairy, egg, fat and tea controls are untouched.

## 2. Rows (8, `staged_rows.csv`; kind whole_food; class-instance of the quoted example; never NAMED; no aliases, taxonomy, purity or ingredient claim; support counts are verified raw/physical-state records, cooked-name records are naming only)
beef (395 verified records, first FDC 168607), lamb (118, 172479), pork (70, 167810), chicken (47, 171047), veal (38, 172478), turkey (28, 171081), duck (3, 172408), goose (3, 172413). Quotation used: the continuous Table 1 Group 1 example only (the table cell breaks after 'fish' and 'steaks,'); no spliced definition.

## 3. Gates (committed tree vs main a6cacbc; separate fresh processes)
| check | result |
|---|---|
| lexicon | 433 -> 441 (+8 whole_food rows; none changed or removed); synonyms, markers, descriptors untouched |
| frozen 66 | changed 0; unexplained 0; abstain->4 0 |
| out-of-sample 32 | changed 1: S18 (`Lamb (33%)`) lamb moves from unassessed to recognised, group 4 unchanged; attributed to the row `lamb` |
| drift (583) / descriptor (866) / salted (168) / powder (579) | 0 differences / 0 / 0 / 0 changed |
| suite | **SUITE_TBD** (main 2046 + new tests; one dairy test list edited with an explanation: 'Duck' is now a row) |
| parity | **875/875** identical (main 859 + 16 added entries, 0 removed; reason and driver compared) |

## 4. Measured forms of the 8 rows (before = unrecognised; identical for all 8)
| form | result | form | result |
|---|---|---|---|
| X; ground X; roasted X; boiled X; steamed X | 1 | dried X | 3 |
| X powder; 100% X powder; whole X powder; dried X powder | abstain | chilled X; generic cooked X | abstain |
| salted, smoked, cured, canned, breaded, battered, fried, pan fried, minced, formed X | abstain | X (XQ9); X (rice); X (milk); X (egg); X, water; X, rice | abstain |
| X, salt; X, sugar; X, sunflower oil | 3 | hydrogenated X; X, flavour; X, maltodextrin | 4 |
Aliases and held labels stay unrecognised: mutton, goat, fish, chicken meat, beef extract, pork fat. Plant, dairy, egg, fat and tea controls (dried rice, dried mango, rice powder, banana powder, milk, sheep milk, eggs, dried egg, 100% egg powder, egg powder, skimmed milk powder, salted milk, milk (rice), rice (wheat), sunflower oil, lard, walnuts (brine)) are unchanged.

## 5. Open
Egg powder keeps its existing rule (`100% Egg Powder` Group 1, bare abstain): not an animal row, out of scope. `Dried Egg` Group 1 is the existing egg row behaviour (the FAO dried-meats example names meats and fish, not eggs).

## 6. Exact diff vs main a6cacbc (10 paths, `git diff --name-only a6cacbc HEAD` on the committed tree)
- `data/ingest/animal_guard_1.json`
- `evaluation/animal_guard_1/README.md`
- `evaluation/animal_guard_1/applied_gate/applied_gate.json`
- `evaluation/animal_guard_1/staged_rows.csv`
- `scripts/parity_check.py`
- `src/foodscan/classify.py`
- `src/foodscan/resources/lexicon.csv`
- `tests/test_animal_guard_1.py`
- `tests/test_dairy_rows_1.py`
- `web_preview/foodscan.js`
