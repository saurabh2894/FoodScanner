# Peel-label sweep and repair (claude/peel-label-guard-1)

Release-EXPOSED regression: `parser._peel_label` (a heuristic that was already in main) became newly active for the 20 new lexicon rows of herb_spice_bulk_1, because the heuristic splits "KNOWN TERM + 1-4 label words + colon + text" and the only evidence it asks for is that the term before the label words is a lexicon term. The batch made 20 more terms (plus the 4 rows its synonyms point to) such prefixes. The out-of-sample label S19 showed it: "PAPRIKA POWDER FLAKE(0.6%): ROASTED SESAME" became the ingredient "PAPRIKA" plus a phantom section "POWDER FLAKE 0.6%", and the status moved uncertain -> complete on a mis-split.

## Repair (bounded)
A candidate label holding a descriptor or form word is never a section label; the check runs for every candidate the loop tries (shortest label first), in Python (`parser._label_has_form_word`) and in the JS port. Guard words, exactly: every word in descriptors.csv; flake, flakes; and from the rule file's processed_words: extract(s), paste(s), mix(es), blend(s), syrup, cooked, canned, pickled, prepared. Not included on purpose: seasoning, sauce (genuine headers), imitation, flavor, flavour (class words already block).

## Sweep (scripts/peel_sweep.py; SYNTHETIC "<term> <suffix>: Roasted Sesame"; summary in sweep_summary.json)
Builds compared in separate fresh processes: BEFORE the batch (6cf9a99~1), main (5ce13fa), main + guard.
- On main, every known term x every alphabetic suffix peels: all 22 suffix patterns peel for 20 of 20 new rows and 115 of 115 older rows (100% of the grid). Before the batch the 20 new rows were not known terms, so none of those items peeled (0 of 20 newly-exposed prefixes); the 4 rows the synonyms point to (aniseed, caraway, cumin, fenugreek) are among the 115 older rows.
- The same is true for the 115 pre-existing lexicon terms: `RICE POWDER FLAKE (0.6%): ...` style phantom peels existed before the batch. The batch did not create the heuristic, it multiplied its reach.
- With the guard: the 13 name/form patterns (POWDER FLAKE (0.6%), POWDER FLAKE, FLAKE, FLAKES (2%), POWDER (3%), DRIED, EXTRACT (5%), EXTRACT, MIX (10%), MIX, BLEND, BLEND (2%), PASTE) peel for 0 of 135 prefixes. Genuine headers (SEASONING, SEASONING (12%), SOUP (22.7%), SAUCE) still peel for 135 of 135.

## Failure modes found, NOT guarded (scoped; owner decides)
1. Suffixes that are neither descriptors nor form words still peel after any known term: OLEORESIN, OIL, MASALA, TOPPING, GARNISH (135/135). "Paprika Oleoresin (0.6%): ..." would still become "Paprika" + a section "Oleoresin". A closed list cannot cover this; the generic fix is a different evidence rule (for example require the label to be a known section word), which is a parser design change.
2. The guard turns a peel into "item stays whole and is flagged by suspect_section_items", which makes status uncertain, not wrong.
3. Python and JS differ in `known phrase`: Python accepts exact lexicon/marker terms only; JS accepts anything `isRecognised` (descriptor-stripped, plural and synonym aware). Probe: "Rice, Garlic Powder Seasoning : Onion, salt" -> Python leaves the colon item whole, JS peels it ("Garlic Powder" + section "Seasoning"). The parity corpus has no such text (found by 4 temporary probe texts, 400/404 identical, not added). JS is the production artifact and is the more eager one.
4. Class-word exemption: an item whose pre-colon text holds an additive class word is never flagged by suspect_section_items ("GREEN TEA FLAVOUR (NATURE-IDENTICAL) SOUP(22.7%): WATER" in S19 stays whole in both builds and status is complete). Independent of this batch.

## Gates
Suite and parity are in the commit message and status line. Frozen 66 inputs: 0 changed on every compared field (main vs repaired, separate fresh processes). Out-of-sample set re-run from the cache: see ../out_of_sample_herb_spice_1/results_peel_guard_1.md.
