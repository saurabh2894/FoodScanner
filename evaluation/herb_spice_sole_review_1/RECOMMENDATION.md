# Sole-spice question: options, risks, recommendation (design only; NO behaviour change, no resources edit)

Base ddc717e. Companion to `README.md` in this folder (which holds the exact FAO clauses, what the code does today, and the 73/73 measurement). `simulation_options_B_C_not_committed_behaviour.py` monkeypatches the classifier in a throwaway process to count effects; it edits no file. Labels are label-based NOVA readings, never health findings. Nothing here derives an absent additive from silence.

## 1. The question
All 73 `herb_spice` rows abstain as a sole item because no rule exists for the kind (README section 1). Two source readings pull in different directions:
- **FAO Table 1 Group 1** names "herbs and spices used in culinary preparations ... whole or powdered, fresh or dried" and defines the group as processes "that do not add salt, sugar, oils or fats or other food substances to the original food".
- **class-bulk-2 (owner ruling)**: an "X powder" label does not by itself establish whole-food composition (extract, starch, colour, carrier-containing powder are possible); a powder answers Group 1 only when its own text says `100%` or `whole`. The one carve-out is powdered milk, because FAO names "powdered ... milk" by name.

## 2. Options
| | Sole item answers Group 1 when | Everything else | Consistent with class-bulk-2 |
|---|---|---|---|
| **A** (today) | never | abstain | yes |
| **B** | the item is one `herb_spice` row in a form FAO names or the definition allows (whole, seeds, leaves, fresh, dried, crushed, flakes) with NO added-substance word and NO bracket; a "powder"/"powdered" form only with `100%` or `whole` in its own text | abstain | yes: spice powders are treated exactly like vegetable powders |
| **C** | B, plus a plain "X powder" of a single spice (FAO names "powdered" spices; milk-powder precedent) | abstain | no: a second named-powder carve-out, based on a class-level (not exact-term) naming |
| **D** | B or C, extended to a list of only plain spices ("two or more items in this group") | abstain | as B or C |

Measured effect of the options with the guard in place (throwaway simulation; synthetic parity corpus of the base, 37,277 pairs; "distinct texts" is the number of different item strings):
| Option | Frozen 66 | Out-of-sample 32 | Parity pairs changed (abstain -> Group 1 only) | Distinct texts | Changed texts containing a guard word or bracket |
|---|---|---|---|---|---|
| B | 0 | 0 | 264 | 104 | 0 |
| C | 0 | 0 | 414 | 151 | 0 |
For comparison, the guard-less patch measured in `README.md` moved 526 pairs and included "Salted cardamon", "Jeera (Sugar)", "Tumeric (Palm, Salt)" and "Tumeric (Milk Powder)" to Group 1. With the guard none of these changes, and the 20 current abstentions of the frozen 66 are unchanged (none is a spice-only list). Because no saved real label is a sole spice, the real-label evidence can show neither benefit nor harm for any option; the counts are synthetic controls.

## 3. The guard (required for B, C and D)
An item abstains, by the existing item-level pattern (own text and bracket, like the legume/vegetable/fruit/nut guards), when ANY of these holds:
- a bracket or sub-list is present (a bracket naming a spice-only child is a possible later extension, not part of this rule);
- an added-substance word is present: salt/salted, sugar/sugared/sweetened, oil/fat/ghee/butter/milk/starch/vinegar/sauce/honey/jaggery/syrup/brine, flavour/flavoured, colour/coloured, pickled/canned/bottled/preserved, candied, caramelised;
- a form the clause does not name: paste, extract, oleoresin, masala, mix, blend, seasoning;
- a powder form without `100%`/`whole` (option B only);
- more than one item (unless D is chosen).
Unrecognised words, INS codes, markers, Contains-line declarations and colour notes are handled upstream and keep abstaining exactly as today. The guard does not claim that an unlisted word is absent: a word it does not know simply fails to match the row term and abstains (the item is not recognised as the plain row).

## 4. Risk table
| Risk | Effect if unguarded | Mitigation | Residual |
|---|---|---|---|
| Added salt/sugar/oil/milk in a bracket or word | wrong Group 1 for what FAO excludes (Group 3 or other) | the guard above; negative controls named in section 6 | a word not in the guard list that adds a substance |
| Anticaking agents or carriers in ground spice, undeclared | wrong Group 1 | none from label text; limited to forms B allows (whole forms, or powder with `100%`/`whole`) | silence is not evidence of absence: option C accepts this risk for plain powders, B does not |
| Declared oil permitted in a standard (owner-supplied statement about chilli powder; FSSAI 2.9 not read here) | a standard-compliant "Chilli powder" could carry oil FAO excludes | keep plain powders abstaining (B) until the clause is read | open until the clause is read |
| Extracts, oleoresins, pastes, masalas, blends, mixed spices powder | FAO names none; FSSAI (recorded earlier, naming only) allows starch/salt/oil/sweeteners in masalas | guard words; abstain | none |
| Flakes, crushed | the definition names "crushing, grinding"; "flakes" is not a spice example | allowed in B; owner may prefer to hold flakes | judgement call |
| Colour note on a spice ("Turmeric (Colouring & Spices)") | colour as additive | existing upstream colour-note guard (F10) | none |
| Descriptor forms ("Roasted", "Smoked", "Dried") | roasting is a named process, smoking is not | B allows only descriptors already in `descriptors.csv` for the row and the FAO forms; "smoked" abstains | list needs review row by row |
| Row identity ("coriander" is leaf or seed, "mustard" seed or condiment, "pepper") | an ambiguous term answered as a spice | rows already exist as the owner staged them; no new row | ambiguous bare rows stay as they are |

## 5. Recommendation
**Adopt B now; hold C and D for an owner ruling.**
1. B follows the FAO clause where it is exact (whole, fresh, dried herbs and spices, named for the class) and does not widen the powder ruling the owner already made. It answers a plain "Cumin seeds", "Dried Fennel", "Cardamom", "Chilli flakes" and "100% chilli powder", and keeps "Chilli powder", "Turmeric powder" and every blend abstaining.
2. C needs one thing this review could not supply: the FSSAI 2.9 clause on permitted added oil for chilli powder (the statement was supplied, not read). If a standard-compliant "chilli powder" may carry oil, then "Chilli powder" alone cannot be taken as composition-complete, whatever FAO says of "powdered" spices. That is also why C is a second carve-out, not an application of the first.
3. D adds a list rule and a new class of interactions (spice plus unrecognised item, order, sections). It should wait until B has run on real labels.
4. Inherent abstentions stay as abstentions: anything bracketed, sweetened, salted, oiled, flavoured, extracted, blended, unrecognised, a powder without a stated composition, and any list. No group is forced for them.

## 6. Execution if B is approved (separate change, not part of this note)
- Code: one item-level branch for `kinds[0] == "herb_spice"` next to the other sole-item branches, plus the same guard in the JS port; parity corpus additions for every case below.
- Tests (each with Python and JS agreeing): positives (cumin seeds, dried fennel, chilli flakes, 100% chilli powder, whole turmeric powder); negatives that MUST stay abstentions: "Salted cardamom", "Jeera (Sugar)", "Tumeric (Palm, Salt)", "Tumeric (Milk Powder)", "Chilli powder", "Mixed spices powder", "Paprika Oleoresin", "Garam masala", "Turmeric (Colouring & Spices)", "Smoked paprika", an unknown word beside a spice.
- Gates: full suite, parity, frozen 66 and out-of-sample 32 flip dumps in fresh processes (expected 0 changes, as simulated), and a before/after over the whole parity corpus attributing every change to a sole plain-spice item.
- Failure modes to watch: an added-substance word spelled in a way the guard misses (extend the guard, never loosen the rule); a bare row that is ambiguous between a spice and a condiment answered as a spice; a descriptor that changes the product ("smoked", "pickled", "candied").
- Success criteria: 0 changed answers on any saved real label; every changed synthetic text is a plain single spice in an FAO-named form; 0 changed texts contain a guard word or bracket.

## 7. Not decided here
- The FSSAI 2.9 clauses (including the oil statement) were not read in this session; the owner or a later pass must read them before option C is considered.
- Whether "flakes" and "crushed" are in scope for B, and the exact descriptor list.
- Whether the owner accepts the anticaking-agent risk for plain powders (option C); it cannot be settled from label text.
