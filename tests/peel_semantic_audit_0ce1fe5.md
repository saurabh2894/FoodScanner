# Semantic audit of the fictional peel corpus

Tested `origin/main`: **`0ce1fe5d129c60efa8a567d11e979b536fea5e9c`**.
Comparison: `b88609675a3582aec1afce3be85da4c80ce44341`. Corpus and
original reporting script were read directly from git at
`d03113b52b8733251e5b7b96b7de1b02e873dd3b` on
`copilot/peel-adversarial-corpus`; see draft PR #13, "Final head 0ce1fe5".
All inputs below are fictional. No product identity, recipe, or manufacturing
process is assumed.

The original script uses `scripts/parity_check.py` for Python and JS on text
and OCR paths. For this audit the same adapter was run with the corpus
streamed from git rather than copied to a file. All 79 rows were run on both
paths; the 11 answered rows below have identical full Python/JS results and
identical text/OCR results. Output summaries show group, ingredient items,
section labels when present, drivers, not-assessed items, and completeness;
they are not the complete serialized output. "Kept" means text remains in
the displayed list, not that every word was independently assessed.

**Basis and limits.** `research/02-research-nova-and-ingredients.txt`
distinguishes group 1 foods, group 2 culinary ingredients, and group 3
combinations, identifies maltodextrin as a group 4 marker, and notes that
ingredients alone are weaker evidence at the group 1/2/3 boundary. The added
flavour class is a group 4 marker under the FAO 2019 source quoted in
`research/06-declared-roles-nova-source.txt`. Added colour is provisional
and context-sensitive, per `research/04-nova-colour-and-butter-basis.txt`.
Group 3 judgments below are **label-based**, not claims about undisclosed
processing. Under the project's completeness rule uncertain coverage blocks
group 3; a strong group 4 marker can survive uncertainty, including an
unclosed bracket, with the appropriate incomplete-list warning.

## 1. Answered rows: semantic review

Verdicts assess both the label-based group and whether the output represents
its evidence honestly: **6 correct, 3 wrong, 2 ambiguous**. An answer can
have a plausible group but still be wrong because it suppresses an ingredient
or violates the completeness gate. Each output below applies separately to
**Python and JS, both text and OCR**; neither engine output is inferred from
the other.

### alias-heading — correct

Input: `Ingredients: Seasoning : Onion, salt.`

Python output: G3; items `Onion`, `salt`; section `Seasoning`; drivers
`Onion`, `salt`; complete; not assessed: none.

JS output: G3; items `Onion`, `salt`; section `Seasoning`; drivers
`Onion`, `salt`; complete; not assessed: none.

All ingredient words are kept and assessed; `Seasoning` is moved to the
section label, not lost. Onion plus salt supports label-based G3.

### alias-double — correct

Input: `Ingredients: Seasoning: Masala: Onion, salt.`

Python output: G3; items `Onion`, `salt`; section `Seasoning: Masala`;
drivers `Onion`, `salt`; complete; not assessed: none.

JS output: G3; items `Onion`, `salt`; section `Seasoning: Masala`;
drivers `Onion`, `salt`; complete; not assessed: none.

All ingredient words are kept and assessed; the two colon-led labels are
retained as a section, not ingredients. Onion plus salt supports label-based
G3 on this nested-label reading.

### exact-maltodextrin — ambiguous

Input: `Ingredients: Rice, Maltodextrin Seasoning: Onion, salt.`

Python output: G4; items `Rice`, `Maltodextrin Seasoning: Onion`, `salt`;
driver `Maltodextrin Seasoning: Onion` (maltodextrin); uncertain completeness;
not assessed: none; colon warning.

JS output: G4; items `Rice`, `Maltodextrin Seasoning: Onion`, `salt`;
driver `Maltodextrin Seasoning: Onion` (maltodextrin); uncertain completeness;
not assessed: none; colon warning.

All words remain, with no peel, but Onion is not independently assessed or
reported as not assessed. G4 is justified if maltodextrin is an ingredient;
the wording could instead name a seasoning whose declared contents follow the
colon. Review needs the label author's intended ingredient/section boundary
and whether maltodextrin is actually a constituent, not merely a product name.

### plain-no-colon — correct

Input: `Ingredients: Rice, Garlic Powder, onion, salt.`

Python output: G3; items and drivers `Rice`, `Garlic Powder`, `onion`,
`salt`; complete; not assessed: none.

JS output: G3; items and drivers `Rice`, `Garlic Powder`, `onion`, `salt`;
complete; not assessed: none.

Every ingredient word is kept and assessed; nothing is moved or peeled.
These ordinary food ingredients plus salt support label-based G3.

### colon-class — ambiguous

Input: `Ingredients: Rice, Garlic Powder Colour: INS 150d, salt.`

Python output: G4; items `Rice`, `Garlic Powder Colour: INS 150d`, `salt`;
drivers `colour` and `INS 150d` in that item; complete; not assessed: none.

JS output: G4; items `Rice`, `Garlic Powder Colour: INS 150d`, `salt`;
drivers `colour` and `INS 150d` in that item; complete; not assessed: none.

All words and the code remain in the item, with no peel; Garlic Powder is
not separately assessed. G4 is supported if this is a declaration of added
colour, but the boundary between the food name and colour declaration is
unclear in this compressed wording. Review needs an unambiguous original
declaration showing whether colour/INS 150d is added and how Garlic Powder
relates to it; the code must not be changed by inference.

### bracket-colon — wrong

Input: `Ingredients: Rice, Garlic Powder (Seasoning: Onion), salt.`

Python output: G3; items `Rice`, `Garlic Powder (Seasoning: Onion)`, `salt`;
drivers those three items; complete; not assessed: none.

JS output: G3; items `Rice`, `Garlic Powder (Seasoning: Onion)`, `salt`;
drivers those three items; complete; not assessed: none.

Onion's text is kept inside the item, but it is neither separately assessed
nor disclosed as not assessed; it is effectively lost from the evidence.
G3 is plausible for the stated foods and salt, but the complete/fully-assessed
presentation is not justified by the output.

### bracket-square — wrong

Input: `Ingredients: Rice, Garlic Powder Seasoning: [Onion, salt].`

Python output: G3; items `Rice`, `Garlic Powder Seasoning: [Onion, salt]`;
drivers `Rice`, `Onion`, `salt`; not assessed `Garlic Powder Seasoning:
(group name; its contents were assessed separately)`; uncertain; colon warning.

JS output: G3; items `Rice`, `Garlic Powder Seasoning: [Onion, salt]`;
drivers `Rice`, `Onion`, `salt`; not assessed `Garlic Powder Seasoning:
(group name; its contents were assessed separately)`; uncertain; colon warning.

Text is retained, but `Garlic Powder` is moved into the unassessed group
name rather than assessed as a possible ingredient. G3 is plausible if it is
a food, but an uncertain-completeness G3 without a strong marker violates the
abstention rule.

### bracket-unclosed-marker — correct

Input: `Ingredients: Rice, Garlic Powder Seasoning: Maltodextrin (onion, salt.`

Python output: G4; items `Rice`, `Garlic Powder Seasoning: Maltodextrin
(onion, salt`; driver the latter item (maltodextrin); uncertain; not assessed:
none; unclosed-bracket and `List may be incomplete` warnings.

JS output: G4; items `Rice`, `Garlic Powder Seasoning: Maltodextrin
(onion, salt`; driver the latter item (maltodextrin); uncertain; not assessed:
none; unclosed-bracket and `List may be incomplete` warnings.

No words are dropped or peeled; Garlic Powder, onion and salt remain bundled
and are not separately assessed. The visible maltodextrin ingredient supports
G4 despite the unclosed list under Option A; the warning exposes incompleteness.

### bracket-curly — wrong

Input: `Ingredients: Rice, Garlic Powder Seasoning: Onion {cumin, salt}.`

Python output: G3; items `Rice`, `Garlic Powder Seasoning: Onion {cumin,
salt}`; drivers `Rice`, `cumin`, `salt`; not assessed `Garlic Powder
Seasoning: Onion (group name; its contents were assessed separately)`;
uncertain; colon warning.

JS output: G3; items `Rice`, `Garlic Powder Seasoning: Onion {cumin,
salt}`; drivers `Rice`, `cumin`, `salt`; not assessed `Garlic Powder
Seasoning: Onion (group name; its contents were assessed separately)`;
uncertain; colon warning.

Text is retained, but Garlic Powder and Onion are moved into an unassessed
group name instead of assessed as possible ingredients. G3 is plausible for
the named foods, but uncertain completeness without a strong marker requires
abstention.

### strong-marker — correct

Input: `Ingredients: Rice, Garlic Powder Seasoning: Onion, maltodextrin.`

Python output: G4; items `Rice`, `Garlic Powder Seasoning: Onion`,
`maltodextrin`; driver `maltodextrin`; not assessed `Garlic Powder
Seasoning: Onion`; uncertain; colon warning.

JS output: G4; items `Rice`, `Garlic Powder Seasoning: Onion`,
`maltodextrin`; driver `maltodextrin`; not assessed `Garlic Powder
Seasoning: Onion`; uncertain; colon warning.

All words are kept; the ambiguous composite is explicitly not assessed,
not peeled or silently lost. Separately listed maltodextrin justifies G4
despite uncertain completeness.

### contains-additive — correct

Input: `Ingredients: Rice, Garlic Powder Seasoning: Onion, salt. Contains added flavour.`

Python output: G4; items `Rice`, `Garlic Powder Seasoning: Onion`, `salt`;
driver `Contains added flavour`; declaration `added flavour` outside list;
not assessed `Garlic Powder Seasoning: Onion`; uncertain; colon warning.

JS output: G4; items `Rice`, `Garlic Powder Seasoning: Onion`, `salt`;
driver `Contains added flavour`; declaration `added flavour` outside list;
not assessed `Garlic Powder Seasoning: Onion`; uncertain; colon warning.

All ingredient words are kept; the ambiguous composite is explicitly not
assessed, and the Contains declaration is moved to declarations rather than
misrepresented as a list item. The explicit added-flavour class justifies G4.

## 2. Lost answers: 28-row triage

These are the 28 rows identified in PR #13 as answered by both engines on at
least one path at `b886096` and abstaining on that path at the tested head.
Twenty-seven changed on both paths; `no-heading` changed on text only (OCR
already abstained). A readable answer need not reproduce the old peel: a
percentage-bearing compound can instead be retained as a section heading.
The recall category assumes only the disclosed contents of that heading,
not undisclosed product ingredients or processing. A category here concerns
the decision to abstain, not whether the old ingredient extraction was correct.

**Counts:** abstention right 5; recall cost 5; unclear 18; total 28.

| Category | Row | Short reason |
|---|---|---|
| Abstention right | `alias-after-exact` | `Turmeric Masala` can be a compound name or turmeric followed by a heading. |
| Abstention right | `unknown-label` | `Garlic Powder Garnish` may be a compound name, not a separate garnish heading. |
| Abstention right | `plural-cumin-seeds` | Old peel moved `Seeds` out of `Cumin Seeds`; the boundary is unresolved. |
| Abstention right | `plural-coriander-leaves` | Old peel moved `Leaves` out of `Coriander Leaves`; the boundary is unresolved. |
| Abstention right | `percent-zero` | A declared seasoning at 0% with listed contents is internally unclear. |
| Recall cost | `percent-label` | `Garlic Powder Seasoning (12%):` is a readable percentage-bearing heading; disclosed contents are onion and salt. |
| Recall cost | `percent-bare` | `Garlic Powder Seasoning 12%:` is a readable heading and percentage without brackets. |
| Recall cost | `percent-decimal` | `Garlic Powder Seasoning (12.5%):` is a readable heading with a decimal percentage. |
| Recall cost | `percent-spaced` | Spaces within `( 12.5 % )` do not make the heading unreadable. |
| Recall cost | `percent-exact-prefix` | `Cumin Seasoning (2.5%):` is a readable percentage-bearing heading; onion and salt are disclosed. |
| Unclear | `exact-prefix` | `Rice Bran Oil Seasoning:` does not settle whether oil is a separate item or part of the name. |
| Unclear | `descriptor-prefix` | `Garlic Powder Seasoning:` can be a compound name or an item plus heading. |
| Unclear | `exact-salt` | `Salt Seasoning:` leaves salt's role and the boundary open. |
| Unclear | `exact-cumin` | `Cumin Seasoning:` leaves cumin's role and the boundary open. |
| Unclear | `descriptor-dried` | `Dried Garlic Seasoning:` admits both a product name and an item-plus-heading reading. |
| Unclear | `descriptor-ground` | `Ground Cumin Seasoning:` admits both readings. |
| Unclear | `descriptor-multiple` | `Dry Ground Ginger Seasoning:` admits both readings. |
| Unclear | `descriptor-mixed-case` | Case changes do not resolve the compound-versus-section boundary. |
| Unclear | `descriptor-spaces` | Extra spaces do not establish an ingredient boundary. |
| Unclear | `plural-onions` | `Onions Seasoning:` may name a seasoning or separate onions from its heading. |
| Unclear | `plural-garlics` | Unusual `Garlics` and the adjacent heading leave the intended phrase uncertain. |
| Unclear | `plural-chillies` | `Chillies Seasoning:` admits both boundary readings. |
| Unclear | `plural-prefix-and-label` | `Onions Toppings:` could be a compound name or onions followed by a heading. |
| Unclear | `percent-after-colon` | Onion's percentage is readable, but does not settle the preceding `Garlic Powder Seasoning` boundary. |
| Unclear | `line-break` | The line break follows the colon; it does not settle the preceding compound name. |
| Unclear | `semicolon` | Semicolons separate items, but do not settle the compound before the colon. |
| Unclear | `no-heading` | Text input has the same unresolved compound; absence of a heading is not itself a text-path defect. |
| Unclear | `contains-allergen` | `Contains milk` is an allergen line, not a driver; it does not resolve the compound. |

For the unclear cases a reviewer needs the intended component/section
boundary, and, where a compound is a product name, its disclosed composition.
Neither engine agreement nor the old G3 answer resolves that question.
