# Scoped flour conditions, 22 November 2026

This is a reliability correction, not a vocabulary expansion. The existing 512 canonical entries and 156 aliases are unchanged. Maida, garbanzo bean(s), cashew(s), pistachio(s), and all new canonical rows remain outside this release.

## Scope

A flour item whose own text names added sugar, honey, brine, a recognised culinary ingredient, or an unresolved preserved form must not inherit the plain flour Group 1 answer. The existing whole-food added-condition check now also protects flour. No different-food bracket ban is added. Plain flour, existing minimal-form readings, raw Group 1 mixtures, vitamin/mineral additions, and strong Group 4 markers retain their prior behavior.

Existing source-supported salted-grain Group 3 routes are retained, including a salt-plus-sugar form. The prior narrow exclusions for corn starch, baking powder and baking soda also remain. An early experimental version would have removed 28 positive salted-flour answers in the wider matrix. Those were reviewed against the general Group 3 definition and retained, not called automatic safety improvements. This release adds no Group 3 placement and does not revise the historical salted-grain scope.

## Source clauses and inference level

FAO, *Ultra-processed foods, diet quality, and health using the NOVA classification system*, 2019: https://www.fao.org/4/ca5644en/ca5644en.pdf

- Table 1, Group 1 minimal-processing definition: "other methods that do not add salt, sugar, oils or fats or other food substances to the original food."
- Table 1, Group 1 examples: "grits, flakes or flour made from corn, wheat, oats, or cassava".
- Table 1, Group 1 mixtures: "Also includes foods made up from two or more items in this group".
- Table 1, Group 3 definition: "Products made by adding salt, oil, sugar or other group 2 ingredients to group 1 foods".

The addition guard is a class-instance application of the minimal-processing condition, not an exact-named placement of every flour derivative. The 67 changed added-substance cases cannot borrow the unconditional plain Group 1 route. The 19 changed canned-form cases are uncertainty controls: an unspecified preserved flour does not establish the plain form or the conditions of a Group 3 product. They abstain, not become Group 3. Placing a food in a container is a named minimal process, but this does not by itself establish every unspecified preserved formulation. No source claims that every canned flour must be Group 3.

Existing flour rows and their source strengths are not upgraded by these checks. In particular, provisional or unsourced historical rows remain provisional or unsourced. The raw-mixture tests preserve behavior under the explicit mixture clause; they do not equate distinct foods as synonyms.

## Validation

- 613 new synthetic tests pass. These are regression controls, not measured real-label accuracy or 613 newly supported ingredients.
- Full supported local suite: 3,133 passed, 2 failed, 2 skipped, 1 deselected, 5 xfailed. Failures are unchanged baseline gaps: the puff-photo section heading and the missing historical fenugreek evidence fixture.
- The pending restricted reference was not fetched or used. `tests/test_ins_reference.py` and `test_additive_codes_are_grouped_with_plain_effect_labels` remain excluded/deselected as before.
- 2,503/2,503 full-field Python/JS comparisons pass: 1,634 OCR-text-path and 869 paste-path texts. This does not verify original-photo OCR assets or OOS32.
- All 66 frozen paste inputs remain identical in the full-field parity projection.
- All 512 canonical name normalizations are unchanged.
- Exactly 86 of 6,108 legacy conditioned inputs change headline, all Group 1 to abstention. The complete list and the category rationale are in `review.json`. There are no new positive answers in that corpus and no changes outside flour. Every retained negative control remains in the tests.
- A wider 703-case flour matrix has 130 Group 1 to abstention changes and no removed Group 3 answers. The additional cases include explicit separate added-substance declarations and negation boundary controls.

No historical frozen gate or source evidence was rewritten. No marker, INS mapping, OCR, deployment setting, broad raw-mixture guard, or alias file is changed. The unrelated nested powder/form review remains open; this release does not claim all canonical conditioned forms are safe.
