# Peel known-phrase: shared rule (claude/peel-known-phrase-1), step (a) design

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
