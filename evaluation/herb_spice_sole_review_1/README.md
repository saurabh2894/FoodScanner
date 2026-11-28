# Task 2 (review only, NO behaviour change): sole herb/spice abstention and `_POWDER_ROUTED`

Base ddc717e. Nothing in `src/`, `web_preview/` or any table is changed by this note. `simulation_not_committed_behaviour.py` is a throwaway monkeypatch used for the counts below (it never edits a file); it reads the out-of-sample cache from the main checkout.

## 1. What the code does today (measured, not assumed)
- `classify.py` `_POWDER_ROUTED = ("whole_food", "legume", "vegetable", "fruit", "nut_seed")`: "X powder" on those kinds is routed to the food_powder rule (Group 1 only if the item's own text says `100%` or `whole`, else abstain). `herb_spice` is not in that tuple.
- A sole item reaches Group 1 only through the `whole_food`/`flour` branch, the stated-composition `food_powder` branch (and the plain-yoghurt / culture branches). There is no branch for kind `herb_spice`, and `has_food` does not include it either, so a sole herb/spice item falls to the last return: "recognised ingredients, but the combination does not match a group 1, 2 or 3 pattern".
- Measured: all **73** `herb_spice` rows (including the 13 single-spice powder heads added in general-25e) abstain as a sole item, with that reason. So "chilli powder", "cumin" (seeds) and "chilli flakes" abstain because no rule exists for the kind, not because a guard fired. The abstention is a gap, not a decision recorded against a clause.

## 2. The source clauses (read in this session unless stated)
FAO 2019, "Ultra-processed foods, diet quality, and health using the NOVA classification system" (https://www.fao.org/3/ca5644en/ca5644en.pdf; downloaded 2026-11-28, sha256 `c8024c194a8294a0355759877712ea7f61d4da62efc4dec46f3889821b19ceff`), Table 1, Group 1 (PDF page 13; the lexicon rows cite "p.11", which I take to be the printed page number and did not verify):
- Definition, minimally processed: "Unprocessed foods altered by industrial processes such as removal of inedible or unwanted parts, drying, powdering, squeezing, crushing, grinding, fractioning, steaming, poaching, boiling, roasting, and pasteurization, chilling, freezing, placing in containers, vacuum packaging, non-alcoholic fermentation, and other methods that do not add salt, sugar, oils or fats or other food substances to the original food."
- Examples: "... herbs and spices used in culinary preparations, such as thyme, oregano, mint, pepper, cloves and cinnamon, whole or powdered, fresh or dried; ..."
- Same cell: "Infrequently, minimally processed foods contain additives that prolong product duration, protect original properties or prevent proliferation of microorganisms." It names no anticaking agent; I do not read silence as permission or as absence.
- Same cell: "Also includes foods made up from two or more items in this group, ..." (supports a list of several plain spices; its examples are fruit, cereal and flour mixtures, no spice blend is named).

FSSAI Food Product Standards, Chapter 2 clause 2.9 (spices): **not re-read in this session** (my one attempt at a Chapter 2.9 URL returned 404; the notes in research/08 say FSSAI is a naming source only, never placement). What the repository already records from earlier reads:
- 2.9.3(2) chillies and capsicum powder: "powder obtained by grinding clean ripe fruits or pods of Capsicum annum L and Capsicum frutescens L" (quoted in the lexicon row for `chilli powder`).
- 2.9.18(2) turmeric powder: "powder obtained by grinding dried rhizomes or bulbous roots of Curcuma longa L".
- 2.9.7(2) coriander powder: "powder obtained by grinding dried mature fruits, free from added colour, starch, bleach or preservative".
- research/10: 2.9.20 mixed masala powder "may contain" edible starches, edible salt, edible vegetable oil and fats, nutritive sweeteners; 2.9.29 compounded asafoetida is asafoetida with gum arabic, edible starches or edible cereal flour.
- The statement supplied with this task, that chilli powder may contain up to 2% edible oil with declaration, is **not in any repository note and was not verified here**. If it is right, it is the clause that matters most: it would mean a standard-compliant "chilli powder" can carry added oil that FAO Group 1 excludes.
Not used as authority: Steele 2023 table readings and Codex snippets.

## 3. What the rule would be if it followed the clauses
A single narrow rule, in the style of the milk-powder carve-out (the clause names the powdered form of the class):
- the list holds only `herb_spice` items (one item, or several under "two or more items in this group"), each item's own text is the row term plus at most the FAO-named forms (whole, powdered / powder, fresh, dried, ground), no bracket, and no word that adds a substance;
- the result is Group 1, driver cites FAO Table 1 Group 1 (class-instance, not NAMED except thyme, oregano, mint, pepper, cloves, cinnamon), and the clause's own condition "no added salt, sugar, oils or fats or other food substances" is stated as the condition the label is taken at face value for;
- everything else keeps abstaining: any bracket, any added-substance word, blends/masalas/seasonings/mixes, extracts, oleoresins, pastes, "salted", "flavoured", "in oil".
Open choice for the owner, because the powder ruling (class-bulk-2) says an "X powder" label does not by itself establish whole-food composition, while FAO names powdered spices:
| Option | Sole item answers Group 1 when | Consistent with class-bulk-2? |
|---|---|---|
| A (today) | never | yes |
| B | whole/fresh/dried forms only; any powder needs "100%"/"whole" | yes (spices treated like vegetables) |
| C | plus plain "X powder" (FAO names "powdered" spices; milk-powder precedent) | no, a second named-powder carve-out |
| D | B or C extended to lists of several plain spices | as B or C |

## 4. Risks (each must be a guard or a stated limit if any option other than A is chosen)
| Risk | Why it matters | Evidence from the simulation |
|---|---|---|
| Declared oil, salt, sugar, milk in a bracket | The clause excludes added salt/sugar/oils/fats; `herb_spice` has none of the guards the legume/vegetable/fruit/nut kinds have | A naive "all items are herb_spice -> Group 1" patch answered Group 1 for synthetic "Salted cardamon", "Jeera (Sugar)", "Fenugreek seeds (Sugar)", "Aniseed (Sugar)", "Tumeric (Palm, Salt)", "Tumeric (Milk Powder)": a guard is not optional |
| Anticaking agents / carriers in a ground spice | Not declared on many packs; the label cannot show absence. Silence is not evidence of absence | Cannot be tested from label text; this is the same limit that put vegetable powders under class-bulk-2 |
| Extracts, oleoresins, pastes | Not named by the clause; an oleoresin is not "whole or powdered" | The row list has none staged as herb_spice; the open peel item "Paprika Oleoresin (0.6%):" shows the vocabulary edge |
| Blends and masalas ("mixed spices powder", curry powder) | FSSAI 2.9.20 allows starch, salt, oil, sweeteners; FAO's "two or more items" examples do not name a spice blend | stay abstain |
| Declared oil permitted in the standard (owner-supplied, unverified) | If chilli powder may legitimately carry up to 2% oil, "Chilli powder" alone cannot be taken as composition-complete | decision for the owner after the clause is read |
| Whole versus ground | FAO says "whole or powdered, fresh or dried": both forms are named; grinding itself is allowed, adding is not | none |
| Colour notes on a spice | "Turmeric (Colouring & Spices)" must keep its existing colour-note guard (F10) | unchanged, upstream of this rule |

## 5. Which of the 20 current abstentions would change
The 20 abstentions are the dev/fresh/negation inputs of the frozen 66. Under every option above the answer is **0 of 20**: none of the 20 is a list of herb/spice items only. Five of them contain spices and each has another blocker that stays: N10 (class II preservative marker), R2 (unrecognised "Refined Palmolien Oil", "Spices & Condiments"), F09 (flour-based list), F10 (colour note on turmeric), F11 (acidity regulator marker). Frozen 66: 0 changes; out-of-sample 32: 0 changes (simulation of option C+D, naive). The synthetic parity corpus would move **526 of 37,381** pairs from abstain to Group 1 under the naive sole-item patch (530 with lists), every one an abstain -> Group 1; 194 distinct texts, 32 of them with a bracket and at least 21 naming salt/sugar/oil-type words, which is the guard-less failure list above. So the real-label evidence cannot show any benefit or harm either way: no saved real label is a sole spice.

## 6. What I could not decide
- Whether the owner wants spice powders to follow FAO's "whole or powdered" (option C) or the class-bulk-2 powder ruling (option B).
- The FSSAI 2% oil statement and the exact FSSAI clauses were not read; the repository's quoted fragments are used for naming only.
- The printed page of the FAO table (11 versus PDF page 13) was not reconciled.
- Whether anticaking-agent risk is acceptable for ground spices when the label is silent; that is a policy decision, not a source reading.
