# Scoped powder ownership and seven food names

Reviewed 22 November 2026. Base: `b6ac07c8a10df9fc00c0a1970eac73da7e17c502` (PR7).

## Scope

Seven naming aliases, not seven new canonical ingredients: maida; garbanzo bean/beans; cashew/cashews; pistachio/pistachios. Counts become 512 canonical entries and 163 aliases. `aliases.csv` gives each identity source and limits. Names do not independently establish NOVA placement and do not place plant parts, oils, milks, butters, extracts, qualified protein-rich flour or durum flour. Existing canonical placements remain provisional where previously provisional.

Powder forms need the same composition evidence as other powders already handled by the application. Nut/seed rows no longer bypass that check. A powder's own 100% or whole declaration is distinguished from a declaration about a named child. Descriptor-only claims such as `Banana Powder (100%)`, and explicit same-food compositions such as `Cashew Nuts Powder (100% Cashew Nuts)`, remain supported. A named different food cannot supply that claim. A named milk-powder child does not turn its parent fruit, vegetable, legume or nut into a powder. Nested powders are checked at their own bracket depth without borrowing a parent or sibling's wording.

The 100%/whole test is the application's conservative identification policy, not a claim that FAO requires those exact words on every powder label. Powdering is not inherently ultra-processing. An unresolved powder abstains; it is not assigned Group 4. Named milk powders, strong-marker precedence, ordinary flour identities, raw-food mixtures, fortification, unknown-content checks and supported same-item salted/sugared forms remain covered.

## Source basis

- FAO, *Ultra-processed foods, diet quality, and health using the NOVA classification system*, 2019, Table 1: https://www.fao.org/4/ca5644en/ca5644en.pdf . Re-read for this review. Group 1 names powdering among minimal processes, conditional on no added salt, sugar, oils, fats or other food substances. It explicitly includes "fresh, powdered or pasteurized milk" and foods made from two or more Group 1 items. This supports retaining a raw food plus named milk powder, rather than misreading the raw parent as a powder.
- The same table defines Group 3 through adding Group 2 ingredients to Group 1 foods. An unidentified oil powder has not been established as an ordinary Group 2 oil. Bare nut powder has not been established as the whole-food composition required by the current powder policy. Those cases cannot take a prior positive merely from the base noun. This is uncertainty, not proof of a particular industrial carrier.
- FSSAI cereal standards, section 2.4.2: https://fssai.gov.in/docs/food-law/regulations/compendium/food-products-standards/Chapter%202_4_Cereals_and_Cereal_products.pdf . Names Maida (Refined Wheat Flour); protein-rich and durum forms are separately qualified. Naming only. The canonical flour's existing conditions still apply.
- USDA NALT chickpeas, https://lod.nal.usda.gov/nalt/en/page/16207 , explicitly lists garbanzo beans. Singular is the corresponding food-name form.
- USDA NALT cashew nuts, https://lod.nal.usda.gov/nalt/en/page/8335 , gives a qualified cashews (nuts) synonym. TAMU Extension's food-context nut list supports the ordinary food use: https://howdyhealth.tamu.edu/do-plants-have-protein/ . This does not identify every cashew plant part or derivative as nuts.
- USDA NALT pistachios, https://lod.nal.usda.gov/nalt/en/page/55473 , identifies the product under nuts. USDA MyPlate food guidance also names pistachios as nuts: https://myplate-prd.kwaps.platform.usda.gov/eat-healthy/protein-foods . Naming, not separate NOVA evidence.

These are seven short food-name mappings, not a bulk import of the source databases. No claim of a general source-database licence is made. Restricted pending Codex/GSFA material was not used.

## Prior positives were reviewed, not automatically removed

`review.json` groups every changed case in the 11,419-case differential matrix by exact template, original/result group and head term, so the set is reproducible without treating a large count as a verdict.

- 533 Group 3 to abstention: 510 are 255 heads with either a bare nested sunflower-oil powder or an oil powder whose 100% sits only inside its own bracket. Neither establishes the existing oil-powder rule's required own-name composition. The other 23 are bare nut/seed powder plus a separate Salt item. The powder itself lacks whole-food composition evidence. Same-item salted/sugared nut powders remain Group 3 under the existing guarded route. No source read names bare nut-powder-plus-salt as an unconditional exception to the composition policy, so that exception is not invented to keep a test green.
- 127 Group 2 to abstention: a culinary head previously ignored an unresolved nested powder. This is not a confirmed mixture consisting entirely of Group 2 ingredients.
- 1,310 Group 1 to abstention: unresolved nested/own powder composition, with the exact cases recorded.
- 464 abstention to Group 1: 232 existing raw-food heads with either Milk Powder or Whole Milk Powder. FAO explicitly names powdered milk and permits Group 1 mixtures. Whole milk's fat grade is not used as a composition claim about the parent.
- 1,387 abstention-to-abstention changes are reasons only.

The older 6,108-case conditioned corpus changes only 23 bare nut/seed powders, Group 1 to abstention. All 703 flour-form cases and all 512 canonical normalisations remain unchanged. This review does not claim every possible canonical form is resolved.

## Historical expectations and retained negatives

Historical decision files, frozen results and historical applied-gate JSON are not rewritten.

- The maida parked assertions in `test_demand_bulk_1.py` and `test_synonyms_2.py` now defer only this exact food identity to FSSAI2.4.2. The other parked names remain negative; qualified maida forms remain negative in the new tests.
- `test_class_bulk_1.py` permits only the two later garbanzo names from the old candidate set, backed by NALT16207. Other candidate aliases remain excluded.
- `test_ampersand_split_1.py` retains an unrecognised-derivative negative, Salted Almonds & Cashew Milk. The formerly unknown Cashews food name now has its own positive test: the shared Salted modifier is copied to both recognised nut sides, never silently dropped. This uses the named salted-nuts rule, not a new parser rule.
- The previous release's pending-name check in `test_scoped_flour_4.py` is replaced by explicit unplaced-derivative controls. Plain-name positives are tested separately with their sources.
- Two garbanzo-flour forms remain honest abstentions. The older chickpea-flour to besan alias has separate unresolved provenance; no new chain is added merely to force alias/target equality.

## Validation and limits

- 1,074 new synthetic pytest controls pass, not 1,074 ingredients or measured product accuracy.
- Allowed full suite: 4,206 passed, 2 failed, 2 skipped, 1 deselected, 5 xfailed. The same two baseline failures are the Puff photo's missing section heading and absent historical fenugreek evidence. The same restricted-reference test exclusions remain. No new failure is relabelled as baseline.
- Committed-corpus full-field Python/JS parity: 4,969/4,969, including 2,867 OCR-text-path and 2,102 paste-path analyses. This is not a new photograph OCR accuracy measurement.
- Additional private full-field parity: 22,203/22,203. Alias/canonical comparisons across 512 heads and three child forms: 10,752/10,752, no mismatches.
- All 66 frozen paste headlines/groups remain unchanged. Exactly one full-field projection changes: existing development label F07 no longer leaves its two `maida (refined wheat flour)` mentions unassessed. Its Group 4 and all other projected fields remain unchanged except the corresponding assessed counter, which drops from four unassessed items to two.
- Local previews were built and the maida positive, borrowed-composition abstention and named-milk mixture were visually inspected. Saved remote files and deployed production must still be independently checked during publication; local tests alone are not proof of publication.
- Original-photo/OCR assets, the unavailable out-of-sample32 cache and all possible labels are not revalidated by this slice. No deployment settings, marker table, INS mapping or OCR implementation is changed.
