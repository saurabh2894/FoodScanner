# Peel known-phrase: shared rule (claude/peel-known-phrase-1)

Steps: (a) design (below, approved as J+W), (b) implemented as two commits (then a third commit, product-form tails, see the last section): **J** (shared known-prefix rule + flatten fix, commit f87d04f) and **W** (whole-phrase guard, separate commit so it can be dropped). Results are at the end of this file.

Base reliability/demand-truth-23 at ddc717e. No data table is edited. Scripts here (`survey.py`, `real.py`, `sweep2.py`) are read-only probes; paths inside them are scratch paths and were run from the repository root.

## What differs today
`parser._peel_label` splits "<known prefix> <1-4 label words>: <rest>" into the prefix item plus a section label. "Known prefix" is:
- Python `parser._known_phrase(_flat(prefix))`: exact lexicon term or exact marker term.
- JS `knownPhrase(flatten(prefix))`: `isRecognised` = `lookup()` (exact, singular form, leading-descriptor strip, all-descriptor strip, kind-scoped descriptors such as `toasted`) or marker term.
Two further differences found while reading:
1. **Flattening**: JS `flatten` and `normalise.flatten` map the curly apostrophes to a straight one; `parser._flat` does not. "Bishop’s Seed Seasoning : Onion" diverges (JS peels, Python keeps whole) although "bishop's seed" is an exact term. This is not among the five pinned probes.
2. The pinned docstring calls the JS rule "synonym-aware". It is not: `lookup()` has no synonym path in either engine ("Invert syrup Seasoning : Onion" agrees: neither peels). Only plural and descriptor stripping widen the JS rule.
All five pinned probes still diverge on ddc717e (the base already moved "Chilli powder Seasoning : Onion" and the other 12 single-spice heads into exact terms).

## A pre-existing false peel, in BOTH engines, found while evaluating compounds
The loop tries the shortest label first, so the whole pre-colon text is never checked as a name: "Corn Oil: x" becomes "Corn" + section "Oil", "Moong Dal: x" becomes "Moong" + "Dal", "Milk Solids: x", "Rice Flour: x", "Coriander Leaf: x". 61 of the 423 multi-word lexicon terms peel this way today when followed by a colon and text. Under the JS rule the same happens for descriptor/plural forms ("Roasted Barley Flour: x"; Python keeps it whole today, JS peels): 790 of the synthetic prefix-form x tail combinations in `sweep2.py`.

## Options
| Option | Rule | False peel (name split into item + label) | Missed peel (label kept inside an item) | Divergence |
|---|---|---|---|---|
| E | exact term/marker only, both engines | as today: all 61 exact compounds above; every known term x any non-form tail (OIL, MASALA, TOPPING ... peel 135/135 in the earlier sweep) | grows: every "Dried X", "X powder", plural form keeps the label glued to the item; item stays whole, `suspect_section_items` flags it, status uncertain (fail-closed) | none, but needs JS change in production |
| J | `lookup()` or marker, both engines | same 61, plus descriptor/plural forms of them; reach grows (8,018 prefixes recognised by stripping only) | shrinks | none |
| J+W (recommended) | J, plus: if the whole pre-colon text (percent value removed) is itself a known phrase, never peel | the 61 exact compounds and the 790 descriptor-form compounds stop peeling; remaining false peels are the documented parked class (known prefix + non-form tail that is part of a product name, e.g. "Paprika Oleoresin (0.6%):") | as J | none |
| Section-word list | peel only when the label is a known section word | lowest | highest (unknown labels are never peeled) | none, but a new data table and a behaviour change beyond this task (parked in the peel-label sweep README) |

Why J+W and not E: E keeps today's false peels and turns the common label shapes of the five probes ("Red chilli powder Seasoning : Onion") into uncertain results. Why not plain J: it widens the false-peel reach without protecting compounds, which is the risk named in the task. J+W changes only two things: more prefixes qualify (descriptor/plural forms of known foods) and recognised whole names are protected. It weakens no existing guard (form-word, descriptor, class-word, lexicon-term, deny-list, digit/bracket checks all stay in front).

## Evidence on real labels (honest: it cannot discriminate)
- 30,546 distinct texts (the parity corpus plus every saved input): the Python exact rule and the JS rule differ on **0** peel decisions. The corpus holds 17 peeled items in total, all synthetic ("Rice Bran Oil Seasoning : Onion" and the single-spice heads).
- 100 real saved label texts (frozen 66 + out-of-sample 32 + others): **2** items have a depth-0 colon at all ("GREEN TEA FLAVOUR (NATURE-IDENTICAL) SOUP(22.7%): WATER" and "PAPRIKA POWDER FLAKE(0.6%): ROASTED SESAME"); neither peels under E, J or J+W.
So the saved label sets cannot show which rule is better; the decision rests on the structural analysis above, and the flip run in step (b) can only confirm that no saved label changes.

## Step (b) plan
1. `parser._known_phrase(text)`: flatten with `normalise.flatten`, then `lookup(flat) is not None or flat in marker terms` (lazy import of `classify.lookup`; no import cycle at load time). JS keeps `knownPhrase`.
2. Whole-phrase guard in `_peel_label` and `peelLabel`: after the percent value is removed, if `_known_phrase(" ".join(words))` then no peel. Both engines identical.
3. Move the five probes (and the curly-apostrophe probe) into the parity corpus, remove the strict xfail test file, add adversarial cases: compounds that must not peel (corn oil, moong dal, milk solids, rice flour, roasted barley flour, coriander leaf), several colons, bracketed sub-lists, unknown first words, percent values before the colon, plurals, descriptor forms, curly apostrophes, label words that are descriptors/class words.
4. Full suite, parity (37,277 today plus the new cases), frozen-66 + out-of-sample flip dump in separate fresh processes, parity-wide before/after diff of every field.

## What I cannot decide here
- Whether the owner wants the whole-phrase guard in this change (it fixes 61 existing false peels and is a behaviour change of the Python source of truth; without it, J alone would extend the false-peel class to JS-only forms). I recommend it; it is a separate commit so it can be dropped.
- Whether "Paprika Oleoresin (0.6%): ..." style false peels (known prefix + non-form tail) should get a data-driven evidence rule; out of scope.


## Step (b) results (J+W)
Changed: `parser._flat` (curly apostrophes), `parser._known_phrase` (lookup or marker, lazy import of `classify.lookup`), the whole-phrase guard in `parser._peel_label` and `peelLabel` in `web_preview/foodscan.js`; tests, `scripts/parity_check.py` corpus, this note. No data table, no classifier code. Existing guards (form-word, descriptor, class-word, lexicon-term label, deny list, digit/bracket checks) are untouched and still run first; W only adds a non-peel condition.

| Gate | Result |
|---|---|
| Parity | 37,381/37,381 identical (37,277 existing + 52 J cases + 52 W cases, each in `ocr` and `text`) |
| Full suite | 18,937 passed (the five strict-xfail probes are now ordinary passing parity cases) |
| Frozen 66 labels (flip dump, fresh processes, base vs branch) | 0 fields changed on any label (group, status, reason, drivers, ingredients, unassessed, INS) |
| Out-of-sample 32 labels (same method) | 0 fields changed |
| Whole base parity corpus (37,277 pairs, py_result, fresh processes) | 0 pairs changed |
| 61 multi-word terms that peeled before | 61 -> kept whole (list in `before_after.md`); each was a recognised whole name split into a shorter name plus a phantom label ("Corn Oil: x" -> "Corn" + "Oil", "Wheat Flour: x", "Moong Dal: x"...) |

Behaviour change worth reading (`before_after.md` section 3):
- **J (more peels, what the five probes ask for):** "Garlic Powder Seasoning : Onion" and the other descriptor/plural/curly forms now peel; the result moves from uncertain/abstain to complete/Group 3 in the synthetic list (the same answer the straight-apostrophe and exact-term shapes already gave).
- **W (fewer peels):** a colon after a recognised whole name now keeps the item whole and flagged, so synthetic "Rice, Corn Oil: Onion, salt." moves from an answered Group 3 (built on the phantom split "Corn" + section "Oil") to uncertain/abstain. This turns invented structure into an abstention; it does not remove a right peel, because in every case the whole pre-colon text is itself a recognised ingredient name. "Vitamins and Minerals: Iron, Zinc" is the one with a plausible heading reading; it was split into "Vitamins" + "And Minerals" before, which is not a correct reading either, and is now kept whole and flagged.
- **Curly apostrophe side effect:** "Bishop\u2019s Seed Oil: Onion" now peels like the straight-apostrophe form always did (Python and JS agree); this is the open item below, not a new class.

## OPEN ITEM (documented, not fixed): known prefix + non-form tail that belongs to a product name
"Paprika Oleoresin (0.6%): Roasted Sesame" still peels to "Paprika" + section "Oleoresin 0.6%" in both engines (pinned by `test_open_item_known_prefix_plus_non_form_tail_still_peels` and in the parity corpus, so any future rule change shows up). Same class: OIL, MASALA, TOPPING, GARNISH, OLEORESIN tails after a known prefix. Neither W nor J can see it, because the phrase as a whole is not a recognised name. A fix needs evidence that is not in the tables today (a known-section-word list or a recognised-compound list) and is a data decision for the owner.

## Could not decide
- Real label evidence is thin: only 2 items with a depth-0 colon in 100 saved real labels, neither peels under any rule. The rule choice is structural, the flip run only confirms that no saved label moves.
- Whether a colon after a recognised name should instead open a nested sub-list (e.g. "Wheat Flour: Wheat 80%, Barley"). W keeps such items whole and flagged (abstain), which is the conservative reading.


## Product-form tails (third commit; review finding on b886096 accepted)
Finding: with J+W, "Garlic Powder Seasoning : Onion" became the item "Garlic Powder" + "Onion" and the word "Seasoning" was dropped, so an unrecognised item (abstain on the base) turned into a confident Group 3. A seasoning, sauce or blend can hold things the label does not list. Parity agreement was never evidence of correctness: it only shows both engines do the same thing.
Replacement design (parser and JS identical; replaces nothing from J or W, which still decide WHAT counts as a known prefix):
- a section label glued after an ingredient on the same line is peeled only when EVERY tail word is a known plain label word; a tail containing a product-form word is never peeled (the whole text stays ONE flagged item, so the result abstains);
- product-form words come from the data, not from review examples alone (`product_form_words.md`): the clause file's processed words, the section labels in the saved real labels and the parity corpus, and the reviewer-listed words the data does not contain;
- the allowlist of known plain label words is EMPTY by evidence (every same-line label in the data is a product form or a food name), so a same-line glued label is never peeled today. Lines that start a section ("Seasoning : Onion" at the start of a line or sentence, "Rice Bran Oil. Seasoning : Onion") are a different path and are unchanged.
Evidence (`before_after_product_form.md`): 37,381 corpus pairs + 158 Copilot pairs + 68 new product-form pairs, three builds in fresh processes. Against the base ddc717e: 0 more-confident pairs, 0 answered-group changes; 99 answer -> abstain, 29 complete -> uncertain, 2 structure-only. Against the PR head b886096: 0 more-confident pairs. The pre-existing same-class cases moved the cautious way too ("Rice Bran Oil Seasoning :" was Group 3/4 complete on the base; it is abstain/uncertain now, and Group 4 where a flavour marker is present stays Group 4 through the strong-marker exception, status uncertain). Frozen 66 and out-of-sample 32: 0 fields changed. Copilot corpus (79 rows by its own report script): 0 divergent rows, 0/158 divergent analyses. Parity 37,449/37,449, suite 18,982 passed.
Tests changed with this commit (all more cautious, each explained in a comment): the "still peels" positive controls in test_peel_label_guard.py, test_peel_whole_phrase.py and test_peel_known_phrase.py now expect the whole text to stay one item; test_review_labels.py's same-line case expects uncertain + the suspect-section warning. No test was weakened to meet parity.

## Open item status after the third commit
"Paprika Oleoresin (0.6%):" no longer peels: "oleoresin" is a product-form word and no tail word is allowed to peel, so it stays one item and abstains (pinned by test, parity case). The general class "known prefix + unlisted tail" is closed the same way. What stays open is a data decision: which plain label words, if any, may ever be peeled (the allowlist), and the nested-sub-list reading of a colon after a recognised name.
