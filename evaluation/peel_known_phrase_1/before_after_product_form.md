# Before/after: product-form tails (third commit on claude/peel-known-phrase-1)

Old/new results are the Python engine in fresh processes (`py_result`, the parity comparison function); Python/JS agreement is checked separately by `scripts/parity_check.py`. Tooling: `ba_dump.py`, `ba_classify.py` in this folder (scratch paths inside).

## A. Base ddc717e -> this commit (includes the pre-existing same-class cases, e.g. `Rice Bran Oil Seasoning :` which was Group 3/4 on the base)

Pairs compared: 37607 (37,381 corpus pairs of the PR head + 158 Copilot pairs [81 rows x text/ocr, id/category in `copilot/peel-adversarial-corpus`] + 68 new product-form pairs). Classification: `more cautious` = an answer became an abstention, or complete became uncertain; `MORE CONFIDENT` = the reverse; `ANSWERED GROUP CHANGED` = an answered group moved.

| class | pairs |
|---|---|
| identical | 37477 |
| more cautious (answer -> abstain) | 99 |
| more cautious (complete -> uncertain) | 29 |
| same answer/status (structure only) | 2 |

**More confident / answered-group-changed pairs: 0**

| text (`Ingredients:` prefix and trailing `.` kept) | class | old (group/status) | new | sources |
|---|---|---|---|---|
| `Ingredients: Rice, Bishop's Seed Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Black pepper powder Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Cardamom powder Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Chilli powder Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Chillies Seasoning: Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Cinnamon powder Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Clove powder Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Coriander Leaves Seasoning: Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Coriander powder Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Corn Oil 12%: Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Corn Oil Seasoning (12%): Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Corn Oil Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Corn Oil: Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Cumin Base : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Cumin Coating (3%): Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Cumin Dressing : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Cumin Filling : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Cumin Glaze : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Cumin Seasoning (2.5%): Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Cumin Seasoning: Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Cumin Seeds Seasoning: Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Cumin powder Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Fennel powder Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Fenugreek powder Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Ginger powder Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Milk Solids: Skimmed Milk, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Moong Dal Seasoning (12%): Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Mustard Greens: Salt, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Mustard powder Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Nutmeg powder Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Oyster Mushrooms: Garlic, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Rice Bran Oil Fancy Zorba : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Rice Bran Oil Hot Masala Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Rice Bran Oil Masala Tastemaker : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Rice Bran Oil Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,ocr/corpus,text/copilot-81,text/corpus |
| `Ingredients: Rice, Rice Bran Oil Zorba : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Rice Flour: Rice, Water, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Rice Flours: Wheat, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Rice Noodles Soup (22.7%): Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Rice Puff Sprinkler : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Salt Seasoning 5%: Onion, chilli.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus |
| `Ingredients: Rice, Salt Seasoning: Onion, sugar.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Tomato Concentrate: Tomato, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Turmeric Garnish : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Turmeric Masala : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Turmeric Topping : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Turmeric powder Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Wheat Flour (45%): Wheat, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Wheat Flour 45%: Wheat, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Base Mix(57%)(Beetroot, Carrot, Rice, Urad Dal), Sabudana Flour, Potato Flour, Rice Bran Oil Seasoning : Dehydrated Vegetables(` | more cautious (complete -> uncertain) | G4/compl | G4/uncer | ocr/corpus |
| `Ingredients: Rice, Coriander Leaf: Fresh, salt.` | more cautious (complete -> uncertain) | abstain/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Corn Oil: Onion (Moong Dal: Roasted), salt.` | more cautious (complete -> uncertain) | abstain/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Maltodextrin Seasoning: Onion, salt.` | more cautious (complete -> uncertain) | G4/compl | G4/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Milk Solids Seasoning : Onion, salt.` | more cautious (complete -> uncertain) | abstain/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Moong Dal: Roasted, salt.` | more cautious (complete -> uncertain) | abstain/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Paprika Oleoresin (0.6%): Roasted Sesame, salt.` | more cautious (complete -> uncertain) | abstain/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Paprika Oleoresin: Roasted Sesame, salt.` | more cautious (complete -> uncertain) | abstain/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Rice Bran Oil Seasoning (12%): Onion, salt, flavour.` | more cautious (complete -> uncertain) | G4/compl | G4/uncer | ocr/corpus |
| `Ingredients: Rice, Rice Bran Oil Seasoning : Onion, Garlic, Flavour.` | more cautious (complete -> uncertain) | G4/compl | G4/uncer | ocr/corpus |
| `Ingredients: Rice, Rice Bran Oil Seasoning : Onion, salt, flavour.` | more cautious (complete -> uncertain) | G4/compl | G4/uncer | ocr/corpus |
| `Ingredients: Rice, Tomato Concentrate Base : Onion, salt.` | more cautious (complete -> uncertain) | abstain/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Vitamins and Minerals: Iron, Zinc, salt.` | more cautious (complete -> uncertain) | abstain/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Wheat Flour Premix : Onion, salt.` | more cautious (complete -> uncertain) | abstain/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Whole Wheat Flour Seasoning : Onion, salt.` | more cautious (complete -> uncertain) | abstain/compl | abstain/uncer | ocr/corpus,ocr/product-form (new),text/corpus,text/product-form (new) |
| `Rice, Rice Bran Oil Seasoning : Onion, Garlic, Flavour` | more cautious (complete -> uncertain) | G4/compl | G4/uncer | text/corpus |
| `Ingredients: Rice, Corn Oil: Onion: Garlic, salt.` | same answer/status (structure only) | abstain/uncer | abstain/uncer | ocr/corpus,text/corpus |

## B. PR head b886096 (J+W) -> this commit

Pairs compared: 37607 (37,381 corpus pairs of the PR head + 158 Copilot pairs [81 rows x text/ocr, id/category in `copilot/peel-adversarial-corpus`] + 68 new product-form pairs). Classification: `more cautious` = an answer became an abstention, or complete became uncertain; `MORE CONFIDENT` = the reverse; `ANSWERED GROUP CHANGED` = an answered group moved.

| class | pairs |
|---|---|
| identical | 37388 |
| more cautious (answer -> abstain) | 164 |
| more cautious (complete -> uncertain) | 35 |
| same answer/status (structure only) | 20 |

**More confident / answered-group-changed pairs: 0**

| text (`Ingredients:` prefix and trailing `.` kept) | class | old (group/status) | new | sources |
|---|---|---|---|---|
| `Ingredients: Rice, Bishop's Seed Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Bishop’s Seed Masala 5%: Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Bishop’s Seed Oil: Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Bishop’s Seed Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Black pepper powder Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Cardamom powder Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Chilli powder Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Chillies Seasoning: Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Cinnamon powder Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Clove powder Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Coriander Leaves Seasoning: Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Coriander powder Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Corn Oil Seasoning (12%): Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Corn Oil Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Cumin Base : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Cumin Coating (3%): Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Cumin Dressing : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Cumin Filling : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Cumin Glaze : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Cumin Seasoning (2.5%): Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Cumin Seasoning: Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Cumin Seeds Seasoning: Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Cumin powder Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Dried Coriander Leaves Seasoning 5%: Onion, Garlic, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Dried Garlic Seasoning: Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Dried Paprika Masala : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Dried Paprika Seasoning: Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Dry Ground Ginger Seasoning: Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Dry ginger powder Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Fennel powder Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Fenugreek powder Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, GARLIC POWDER SEASONING (12%): ONION, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Garlic  Powder   Seasoning  :  Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Garlic Powder Garnish: Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Garlic Powder SEASONINGS : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Garlic Powder Seasoning ( 12.5 % ): Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Garlic Powder Seasoning (12%): Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,ocr/corpus,text/copilot-81,text/corpus |
| `Ingredients: Rice, Garlic Powder Seasoning (12.5%): Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Garlic Powder Seasoning 0%: Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Garlic Powder Seasoning 12%: Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,ocr/corpus,text/copilot-81,text/corpus |
| `Ingredients: Rice, Garlic Powder Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,ocr/corpus,ocr/product-form (new),text/copilot-81,text/corpus,text/product-form (new) |
| `Ingredients: Rice, Garlic Powder Seasoning: Onion (12%), salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Garlic Powder Seasoning: Onion, salt. Contains milk.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Garlic Powder Seasoning:Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Garlics Seasoning: Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Ginger powder Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Ground Cumin Seasoning: Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Moong Dal Seasoning (12%): Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Mustard powder Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Nutmeg powder Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Onions Seasoning: Garlic, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Onions Toppings: Garlic, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Paprika Powder Seasoning: Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Powdered Sugar Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Red Chilli Powders Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Red Chilli Powders Seasonings : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Red chilli powder Sauce : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Red chilli powder Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Refined Palm Oil Sauce : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Rice Bran Oil Fancy Zorba : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Rice Bran Oil Hot Masala Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Rice Bran Oil Masala Tastemaker : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Rice Bran Oil Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,ocr/corpus,text/copilot-81,text/corpus |
| `Ingredients: Rice, Rice Bran Oil Zorba : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Rice Noodles Soup (22.7%): Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Rice Puff Sprinkler : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Roasted Rice Seasoning (12%): Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Salt Seasoning 5%: Onion, chilli.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus |
| `Ingredients: Rice, Salt Seasoning: Onion, sugar.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Toasted Rice Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Turmeric Garnish : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Turmeric Masala : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Turmeric Topping : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Turmeric powder Seasoning : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, gArLiC pOwDeR sEaSoNiNg : Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, garlic powder seasoning 5%: onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice; Garlic Powder Seasoning: Onion; salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | ocr/copilot-81,text/copilot-81 |
| `Rice, Garlic Powder Seasoning: Onion, salt.` | more cautious (answer -> abstain) | G3/compl | abstain/uncer | text/copilot-81 |
| `Ingredients: Base Mix(57%)(Beetroot, Carrot, Rice, Urad Dal), Sabudana Flour, Potato Flour, Rice Bran Oil Seasoning : Dehydrated Vegetables(` | more cautious (complete -> uncertain) | G4/compl | G4/uncer | ocr/corpus |
| `Ingredients: Rice, Garlic Powder Seasoning : Onion (Garlic, Red Chilli Powder Seasoning : Salt), salt.` | more cautious (complete -> uncertain) | abstain/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Garlic Powder Seasoning : Onion (Red Chilli Powder Sauce : Salt), salt.` | more cautious (complete -> uncertain) | abstain/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Garlic Powder Seasoning : Onion [Corn Oil Seasoning : Salt], salt.` | more cautious (complete -> uncertain) | abstain/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Garlic Powder Seasoning: Onion (spices [cumin, pepper]), salt.` | more cautious (complete -> uncertain) | abstain/compl | abstain/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Garlic Powder Seasoning: Onion {cumin, salt}.` | more cautious (complete -> uncertain) | G3/compl | G3/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Garlic Powder Seasoning: Onion, maltodextrin.` | more cautious (complete -> uncertain) | G4/compl | G4/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Garlic Powder Seasoning: Onion, salt. Contains added flavour.` | more cautious (complete -> uncertain) | G4/compl | G4/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Maltodextrin Seasoning: Onion, salt.` | more cautious (complete -> uncertain) | G4/compl | G4/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Milk Solids Seasoning : Onion, salt.` | more cautious (complete -> uncertain) | abstain/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Paprika Oleoresin (0.6%): Roasted Sesame, salt.` | more cautious (complete -> uncertain) | abstain/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Paprika Oleoresin: Roasted Sesame, salt.` | more cautious (complete -> uncertain) | abstain/compl | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Rice Bran Oil Seasoning (12%): Onion, salt, flavour.` | more cautious (complete -> uncertain) | G4/compl | G4/uncer | ocr/corpus |
| `Ingredients: Rice, Rice Bran Oil Seasoning : Onion, Garlic, Flavour.` | more cautious (complete -> uncertain) | G4/compl | G4/uncer | ocr/corpus |
| `Ingredients: Rice, Rice Bran Oil Seasoning : Onion, salt, flavour.` | more cautious (complete -> uncertain) | G4/compl | G4/uncer | ocr/corpus |
| `Ingredients: Rice, Tomato Concentrate Base : Onion, salt.` | more cautious (complete -> uncertain) | abstain/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Wheat Flour Premix : Onion, salt.` | more cautious (complete -> uncertain) | abstain/compl | abstain/uncer | ocr/product-form (new),text/product-form (new) |
| `Ingredients: Rice, Whole Wheat Flour Seasoning : Onion, salt.` | more cautious (complete -> uncertain) | abstain/compl | abstain/uncer | ocr/corpus,ocr/product-form (new),text/corpus,text/product-form (new) |
| `Rice, Rice Bran Oil Seasoning : Onion, Garlic, Flavour` | more cautious (complete -> uncertain) | G4/compl | G4/uncer | text/corpus |
| `Ingredients: Rice, Dry ginger powder Seasoning : Onion: Garlic, salt.` | same answer/status (structure only) | abstain/uncer | abstain/uncer | ocr/corpus,text/corpus |
| `Ingredients: Rice, Garlic Powder Seasoning : Onion : Garlic, salt.` | same answer/status (structure only) | abstain/uncer | abstain/uncer | ocr/corpus,ocr/product-form (new),text/corpus,text/product-form (new) |
| `Ingredients: Rice, Garlic Powder Seasoning: Maltodextrin (onion, salt.` | same answer/status (structure only) | G4/uncer | G4/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Garlic Powder Seasoning: Masala: Onion, salt.` | same answer/status (structure only) | abstain/uncer | abstain/uncer | ocr/copilot-81,ocr/product-form (new),text/copilot-81,text/product-form (new) |
| `Ingredients: Rice, Garlic Powder Seasoning: Masala: Topping: Onion, salt.` | same answer/status (structure only) | abstain/uncer | abstain/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Garlic Powder Seasoning: Onion (cumin, salt.` | same answer/status (structure only) | abstain/uncer | abstain/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Garlic Powder Seasoning: Onion: Garlic, salt.` | same answer/status (structure only) | abstain/uncer | abstain/uncer | ocr/copilot-81,text/copilot-81 |
| `Ingredients: Rice, Garlic Powder Seasoning: Sauce: Tomato, salt.` | same answer/status (structure only) | abstain/uncer | abstain/uncer | ocr/copilot-81,text/copilot-81 |

## C. The 81 Copilot rows by category (PR head -> this commit): pairs changed / pairs

| category | changed | pairs |
|---|---|---|
| alias | 2 | 14 |
| control | 10 | 16 |
| descriptor | 12 | 14 |
| compound | 0 | 22 |
| colon | 8 | 18 |
| percentage | 14 | 18 |
| synonym | 0 | 14 |
| plural | 12 | 14 |
| bracket | 8 | 16 |
| format | 5 | 6 |
| marker | 6 | 6 |
