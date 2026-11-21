# provenance_fixes_1: fixes for the junior's provenance audit (branch claude/provenance-fixes-1, off main c6d8629)

Audit: evaluation/provenance_audit_1/REPORT.md on antigravity/audit-1 (179 rows: 33 verified, 29 mismatch, 117 internal-source; FAO PDF sha256 c8024c19...ceff, the document used here). Each finding gets the ID PA1-<row>. Triage is exactly one of WRONG (contradicts its cited source), INFERRED (goes beyond the source) or UNVERIFIABLE-in-scope (not touched).

## Condition scope, read per finding (ingredient vs product)
Every one of the 29 conditions is INGREDIENT-scoped (the nuts' own salt/sugar; the herb's own form; the fruit's own form) or a citation fact. None is product-scoped, so nothing is flagged back to the owner for scope.

## Findings (29) and their treatment

| ID | Row | Triage | Condition scope | Fix |
|---|---|---|---|---|
| PA1-almonds | almonds | INFERRED (dropped condition + silent class) | ingredient: the nuts' own added salt or sugar | placement KEPT; kind nut_seed; condition recorded in provenance and applied AT ITEM LEVEL by the classifier (see below); not-named note added |
| PA1-pumpkin seeds | pumpkin seeds | INFERRED (dropped condition + silent class) | ingredient: the nuts' own added salt or sugar | placement KEPT; kind nut_seed; condition recorded in provenance and applied AT ITEM LEVEL by the classifier (see below); not-named note added |
| PA1-flax seeds | flax seeds | INFERRED (dropped condition + silent class) | ingredient: the nuts' own added salt or sugar | placement KEPT; kind nut_seed; condition recorded in provenance and applied AT ITEM LEVEL by the classifier (see below); not-named note added |
| PA1-ajwain | ajwain | INFERRED (silent class-to-instance) | ingredient: its own form ('whole or powdered, fresh or dried') | provenance only: 'exact term not named by the clause (an instance of the class ...)' added; no classification change |
| PA1-bishop's seed | bishop's seed | INFERRED (silent class-to-instance) | ingredient: its own form ('whole or powdered, fresh or dried') | provenance only: 'exact term not named by the clause (an instance of the class ...)' added; no classification change |
| PA1-aniseed | aniseed | INFERRED (silent class-to-instance) | ingredient: its own form ('whole or powdered, fresh or dried') | provenance only: 'exact term not named by the clause (an instance of the class ...)' added; no classification change |
| PA1-caraway | caraway | INFERRED (silent class-to-instance) | ingredient: its own form ('whole or powdered, fresh or dried') | provenance only: 'exact term not named by the clause (an instance of the class ...)' added; no classification change |
| PA1-bay leaf | bay leaf | INFERRED (silent class-to-instance) | ingredient: its own form ('whole or powdered, fresh or dried') | provenance only: 'exact term not named by the clause (an instance of the class ...)' added; no classification change |
| PA1-capsicum powder | capsicum powder | INFERRED (silent class-to-instance) | ingredient: its own form ('whole or powdered, fresh or dried') | provenance only: 'exact term not named by the clause (an instance of the class ...)' added; no classification change |
| PA1-fennel | fennel | INFERRED (silent class-to-instance) | ingredient: its own form ('whole or powdered, fresh or dried') | provenance only: 'exact term not named by the clause (an instance of the class ...)' added; no classification change |
| PA1-fennel seeds | fennel seeds | INFERRED (silent class-to-instance) | ingredient: its own form ('whole or powdered, fresh or dried') | provenance only: 'exact term not named by the clause (an instance of the class ...)' added; no classification change |
| PA1-fenugreek | fenugreek | INFERRED (silent class-to-instance) | ingredient: its own form ('whole or powdered, fresh or dried') | provenance only: 'exact term not named by the clause (an instance of the class ...)' added; no classification change |
| PA1-nutmeg | nutmeg | INFERRED (silent class-to-instance) | ingredient: its own form ('whole or powdered, fresh or dried') | provenance only: 'exact term not named by the clause (an instance of the class ...)' added; no classification change |
| PA1-mace | mace | INFERRED (silent class-to-instance) | ingredient: its own form ('whole or powdered, fresh or dried') | provenance only: 'exact term not named by the clause (an instance of the class ...)' added; no classification change |
| PA1-mustard | mustard | INFERRED (silent class-to-instance) | ingredient: its own form ('whole or powdered, fresh or dried') | provenance only: 'exact term not named by the clause (an instance of the class ...)' added; no classification change |
| PA1-long pepper | long pepper | INFERRED (silent class-to-instance) | ingredient: its own form ('whole or powdered, fresh or dried') | provenance only: 'exact term not named by the clause (an instance of the class ...)' added; kind/cut of the named 'pepper' noted |
| PA1-white pepper | white pepper | INFERRED (silent class-to-instance) | ingredient: its own form ('whole or powdered, fresh or dried') | provenance only: 'exact term not named by the clause (an instance of the class ...)' added; kind/cut of the named 'pepper' noted |
| PA1-black pepper bits | black pepper bits | INFERRED (silent class-to-instance) | ingredient: its own form ('whole or powdered, fresh or dried') | provenance only: 'exact term not named by the clause (an instance of the class ...)' added; cut/flaked form also noted as not named by 'whole or powdered' |
| PA1-red chili | red chili | INFERRED (silent class-to-instance) | ingredient: its own form ('whole or powdered, fresh or dried') | provenance only: 'exact term not named by the clause (an instance of the class ...)' added; no classification change |
| PA1-chillies | chillies | INFERRED (silent class-to-instance) | ingredient: its own form ('whole or powdered, fresh or dried') | provenance only: 'exact term not named by the clause (an instance of the class ...)' added; no classification change |
| PA1-chilli flakes | chilli flakes | INFERRED (silent class-to-instance) | ingredient: its own form ('whole or powdered, fresh or dried') | provenance only: 'exact term not named by the clause (an instance of the class ...)' added; cut/flaked form also noted as not named by 'whole or powdered' |
| PA1-schezwan pepper | schezwan pepper | INFERRED (silent class-to-instance) | ingredient: its own form ('whole or powdered, fresh or dried') | provenance only: 'exact term not named by the clause (an instance of the class ...)' added; kind/cut of the named 'pepper' noted |
| PA1-dried curry leaves | dried curry leaves | INFERRED (silent class-to-instance) | ingredient: its own form ('whole or powdered, fresh or dried') | provenance only: 'exact term not named by the clause (an instance of the class ...)' added; no classification change |
| PA1-black raisin | black raisin | INFERRED (silent class-to-instance) | ingredient: its own form | provenance only: dried fruit instance, exact term not named |
| PA1-banana powder | banana powder | WRONG (cite) | citation fact | page corrected p.10 -> p.6: the Group 1 definition prose sits between the report footers 'Page 5 of 44' and 'Page 6 of 44' |
| PA1-strawberry powder | strawberry powder | WRONG (cite) | citation fact | page corrected p.10 -> p.6: the Group 1 definition prose sits between the report footers 'Page 5 of 44' and 'Page 6 of 44' |
| PA1-beetroot powder | beetroot powder | WRONG (cite) | citation fact | page corrected p.10 -> p.6: the Group 1 definition prose sits between the report footers 'Page 5 of 44' and 'Page 6 of 44' |
| PA1-emulsifying salt | emulsifying salt (markers.csv) | WRONG (cite) | citation fact | 'Table 1 (p. 11)' corrected to 'pp. 9-10 (prose) and Table 1 continuation (p. 12)'; the plural-in-text note added (the marker already matches singular and plural, so the singular row term is not a defect) |
| PA1-thickener | thickener (markers.csv) | WRONG (cite) | citation fact | 'Table 1 (p. 11)' corrected to 'pp. 9-10 (prose) and Table 1 continuation (p. 12)'; the plural-in-text note added (the marker already matches singular and plural, so the singular row term is not a defect) |

Also corrected (same defect, found while fixing, not in the audit's 29): `sprouted ragi` and `sprouted jowar` cited the same definition as p.10; now p.6 (lexicon rows, decisions JSON, research/07, the held_sources README, a classify.py comment). Older gate artifacts under evaluation/ keep their original text as a historical record.

## The nuts and seeds fix (the audit's flagship finding), exactly as scoped by the owner
- The FAO clause 'tree and ground nuts and other oily seeds (with no added salt or sugar)' and the Group 3 counterpart 'salted or sugared nuts and seeds' describe the NUTS themselves. The rows keep their Group 1 placement.
- New kind `nut_seed` (Python classify.py, JS port, validate_batch KINDS): behaves as a whole food, plus an item-level check on the item's OWN name and bracket text: salt, salted, sugar, sugared, sweetened, candied, caramelised, honey, glazed, jaggery or syrup adds the condition-breaking substance; 'no', 'without', 'non', 'free' near it ('no added salt', 'salt free') and 'unsalted'/'unsweetened' do not.
- Effect: 'Salted Almonds', 'Almonds (Almonds, Salt)', 'Rice, Salted Pumpkin Seeds' are Group 3 (FAO Group 3 names salted or sugared nuts), never Group 1 via the nut clause; 'Sugared Almonds' and 'Honey Roasted Almonds' are not in the vocabulary and never Group 1; a plain 'Almonds' entry in a sweetened product keeps its placement (the product's sugar is not added to the nuts); 'Unsalted Almonds', 'Almonds (no added salt)' stay Group 1. tests/test_nut_seed_condition.py pins all of it both ways.

## Not touched
- 33 verified rows; 117 internal-source rows (research/02 etc.) are UNVERIFIABLE-in-scope: no fix. Re-audit candidates if you want them checked: the 87 lexicon and 30 marker rows cite research/02 notes whose underlying sources are Monteiro et al. 2017/2018/2019 (read here as PMC copies, licence unverified) and the FAO report; a re-audit would need those documents' page-level text per row, which is a task for you to schedule.

## Gate and flips (vs main c6d8629, separate fresh processes)
Frozen 66: no change in group, status, reason, drivers, warnings, ingredients, unassessed or INS mappings. Out-of-sample 32: no change. (Provenance text changed on 29 rows and the nut rows changed kind; no frozen or out-of-sample input contains a salted or sugared nut item.) Suite 1200 passed + 5 expected failures; parity 487/487.
