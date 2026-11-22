# Scoped nested-vocabulary reliability fixes

Reviewed 22 November 2026 against main `3928b359a84d5f57ba1408c29d53c39516a9680c`.

This changes two classifier edge cases. It adds no canonical foods or aliases. Counts remain 512 canonical rows and 156 aliases. The six proposed nut/legume aliases and the earlier broad guard experiment are not included.

## Changes and evidence

1. The word sugar in the existing fruit name sugar-apples is intrinsic to that name, not evidence of added sugar. USDA FoodData Central SR Legacy food 168175 names the raw fruit, with sweetsop as an alternate name. This is historical naming evidence only. FAO Table 1 places fresh fruit in Group 1, a class-instance placement for this fruit. The added-substance check masks only that exact fruit phrase, without shortening its token count or changing the negation window. Separate sugar, salt, oil and other added-substance declarations still count.
2. Recognition-only sprouted ragi and sprouted jowar must not acquire a placement by sitting inside a bracket on a placed food. Their existing rows remain unplaced. They now appear in the unplaced display and count as not fully assessed. The completeness text uses that wording rather than incorrectly calling recognized-but-unplaced content outside the vocabulary. A strong Group 4 marker can still decide the product while those terms remain visible. This is an unresolved placement, not a claim that sprouting itself establishes any NOVA group.

FAO Table 1 expressly includes mixtures of two or more Group 1 foods and foods with vitamins/minerals added. Those source-supported routes are retained. The four generic nutrient labels are not treated as unresolved grain forms when nested. No blanket rejection of different raw foods or minimal processing is added.

Sources:

- FAO, Monteiro et al., 2019, *Ultra-processed foods, diet quality, and health using the NOVA classification system*, Table 1, printed pages 11-12: https://www.fao.org/4/ca5644en/ca5644en.pdf
- USDA FoodData Central downloads, SR Legacy April 2018 archive, `food.csv`, food 168175, published in FoodData Central on 2019-04-01: https://fdc.nal.usda.gov/download-datasets/

## Validation

- 69 new synthetic regression tests pass.
- Python/browser full-field parity: 1,271/1,271, comprising 1,018 OCR-text-path inputs and 253 paste-path inputs. This is implementation agreement, not measured accuracy or new original-photo OCR validation.
- Frozen 66 paste inputs: no compared fields change.
- Of 6,108 old conditioned inputs, exactly five sugar-apples results change. All are recorded in `review.json`: plain fruit, a raw-rice mixture and pure powder become Group 1; bare powder and an unspecified canned form abstain rather than falsely claiming added sugar and Group 3.
- Existing canonical-name normalization is unchanged for all 512 canonical rows.
- Full available test run: 2,520 passed, 2 failed, 2 skipped, 1 deselected, 5 expected failures. The two failures are unchanged baseline gaps: the millet-puff photo section heading and the fenugreek demand-evidence fixture.

The restricted reference test module is excluded, and the additive-display reference case is deselected. The pending reference was not fetched or used. The absent out-of-sample-32 cache remains a disclosed validation gap. This is not an all-green claim.

Commands:

```text
PYTHONPATH=src python -m pytest -q tests/test_scoped_nested_3.py
PYTHONPATH=src python -m pytest -q --ignore=tests/test_ins_reference.py -k 'not additive_codes_are_grouped_with_plain_effect_labels'
PYTHONPATH=src python scripts/parity_check.py
```
