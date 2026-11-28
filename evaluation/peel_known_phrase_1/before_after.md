# Before/after, base ddc717e vs this branch (J+W), separate fresh processes

## 1. Whole parity corpus (37,277 pairs of the base)
Changed pairs: **0**. (The 37,277 existing texts contain no item whose peel decision differs under J or W.)

## 2. The 61 multi-word lexicon terms, `<Term>: Roasted Sesame`
Old = `_peel_label` result before (item / label / rest). All 61 are a recognised whole name split into a shorter name plus a phantom section label; all 61 are kept whole now (and flagged by `suspect_section_items`, so the status is uncertain and no group is guessed).

| Term | Old split | New |
|---|---|---|
| barley flour | Barley / Flour / Roasted Sesame | kept whole |
| black pepper bits | Black Pepper / Bits / Roasted Sesame | kept whole |
| broccoli raab | Broccoli / Raab / Roasted Sesame | kept whole |
| buckwheat flour | Buckwheat / Flour / Roasted Sesame | kept whole |
| buckwheat sprouts | Buckwheat / Sprouts / Roasted Sesame | kept whole |
| butter oil | Butter / Oil / Roasted Sesame | kept whole |
| cassava flour | Cassava / Flour / Roasted Sesame | kept whole |
| celery leaves | Celery / Leaves / Roasted Sesame | kept whole |
| celery seed | Celery / Seed / Roasted Sesame | kept whole |
| celery stalks | Celery / Stalks / Roasted Sesame | kept whole |
| coriander leaf | Coriander / Leaf / Roasted Sesame | kept whole |
| coriander seed | Coriander / Seed / Roasted Sesame | kept whole |
| corn grits | Corn / Grits / Roasted Sesame | kept whole |
| corn oil | Corn / Oil / Roasted Sesame | kept whole |
| dill seed | Dill / Seed / Roasted Sesame | kept whole |
| dill weed | Dill / Weed / Roasted Sesame | kept whole |
| fennel seeds | Fennel / Seeds / Roasted Sesame | kept whole |
| fenugreek leaves | Fenugreek / Leaves / Roasted Sesame | kept whole |
| horse gram | Horse / Gram / Roasted Sesame | kept whole |
| lemon grass | Lemon / Grass / Roasted Sesame | kept whole |
| mango kernel fat | Mango / Kernel Fat / Roasted Sesame | kept whole |
| milk cream | Milk / Cream / Roasted Sesame | kept whole |
| milk solids | Milk / Solids / Roasted Sesame | kept whole |
| millet flour | Millet / Flour / Roasted Sesame | kept whole |
| moong dal | Moong / Dal / Roasted Sesame | kept whole |
| mustard greens | Mustard / Greens / Roasted Sesame | kept whole |
| mustard oil | Mustard / Oil / Roasted Sesame | kept whole |
| mustard seed | Mustard / Seed / Roasted Sesame | kept whole |
| oat bran | Oat / Bran / Roasted Sesame | kept whole |
| oat flour | Oat / Flour / Roasted Sesame | kept whole |
| oat oil | Oat / Oil / Roasted Sesame | kept whole |
| oyster mushrooms | Oyster / Mushrooms / Roasted Sesame | kept whole |
| peanut oil | Peanut / Oil / Roasted Sesame | kept whole |
| pearl millet flour | Pearl Millet / Flour / Roasted Sesame | kept whole |
| pineapple juice | Pineapple / Juice / Roasted Sesame | kept whole |
| potato flour | Potato / Flour / Roasted Sesame | kept whole |
| pumpkin flowers | Pumpkin / Flowers / Roasted Sesame | kept whole |
| pumpkin leaves | Pumpkin / Leaves / Roasted Sesame | kept whole |
| pumpkin seed sunfish | Pumpkin / Seed Sunfish / Roasted Sesame | kept whole |
| pumpkin seeds | Pumpkin / Seeds / Roasted Sesame | kept whole |
| quinoa flour | Quinoa / Flour / Roasted Sesame | kept whole |
| ragi flour | Ragi / Flour / Roasted Sesame | kept whole |
| rice bran | Rice / Bran / Roasted Sesame | kept whole |
| rice bran oil | Rice Bran / Oil / Roasted Sesame | kept whole |
| rice flour | Rice / Flour / Roasted Sesame | kept whole |
| rye flour | Rye / Flour / Roasted Sesame | kept whole |
| scallop squash | Scallop / Squash / Roasted Sesame | kept whole |
| sorghum flour | Sorghum / Flour / Roasted Sesame | kept whole |
| soybean oil | Soybean / Oil / Roasted Sesame | kept whole |
| taro leaves | Taro / Leaves / Roasted Sesame | kept whole |
| taro shoots | Taro / Shoots / Roasted Sesame | kept whole |
| tomato concentrate | Tomato / Concentrate / Roasted Sesame | kept whole |
| vitamins & minerals | Vitamins / & Minerals / Roasted Sesame | kept whole |
| vitamins and minerals | Vitamins / And Minerals / Roasted Sesame | kept whole |
| water apple | Water / Apple / Roasted Sesame | kept whole |
| water convolvulus | Water / Convolvulus / Roasted Sesame | kept whole |
| watermelon seed oil | Watermelon / Seed Oil / Roasted Sesame | kept whole |
| watermelon seeds | Watermelon / Seeds / Roasted Sesame | kept whole |
| wheat bran | Wheat / Bran / Roasted Sesame | kept whole |
| wheat flour | Wheat / Flour / Roasted Sesame | kept whole |
| wheat germ oil | Wheat / Germ Oil / Roasted Sesame | kept whole |

## 3. New synthetic cases (Python result, status / group)
Columns: before = ddc717e, after = this branch. `Rice, <item>, salt.` pasted text.

| Item | | before | after |
|---|---|---|---|
| Dried Paprika Seasoning: Onion | CHANGED | uncertain / abstain | complete / 3 |
| Paprika Powder Seasoning: Onion | CHANGED | uncertain / abstain | complete / 3 |
| Garlic Powder Seasoning : Onion | CHANGED | uncertain / abstain | complete / 3 |
| Red chilli powder Seasoning : Onion | CHANGED | uncertain / abstain | complete / 3 |
| Dry ginger powder Seasoning : Onion | CHANGED | uncertain / abstain | complete / 3 |
| Bishop’s Seed Seasoning : Onion | CHANGED | uncertain / abstain | complete / 3 |
| Bishop's Seed Seasoning : Onion | same | complete / 3 | complete / 3 |
| Red Chilli Powders Seasoning : Onion | CHANGED | uncertain / abstain | complete / 3 |
| Roasted Rice Seasoning (12%): Onion | CHANGED | uncertain / abstain | complete / 3 |
| Dried Coriander Leaves Seasoning 5%: Onion, Garlic | CHANGED | uncertain / abstain | complete / 3 |
| Refined Palm Oil Sauce : Onion | CHANGED | uncertain / abstain | complete / 3 |
| Mystery Powder Seasoning : Onion | same | uncertain / abstain | uncertain / abstain |
| Mystery Dried Paprika Seasoning : Onion | same | uncertain / abstain | uncertain / abstain |
| Garlic Powder Seasoning : Onion : Garlic | CHANGED | uncertain / abstain | uncertain / abstain |
| Garlic Powder Seasoning : Onion (Garlic, Red Chilli Powder Seasoning : Salt) | CHANGED | uncertain / abstain | complete / abstain |
| Garlic Powder Seasoning (12%): Onion | CHANGED | uncertain / abstain | complete / 3 |
| Garlic Powder Seasoning 12%: Onion | CHANGED | uncertain / abstain | complete / 3 |
| Garlic Powder Flavour : Onion | same | complete / 4 | complete / 4 |
| Garlic Powder Note: Onion | same | uncertain / abstain | uncertain / abstain |
| Toasted Rice Seasoning : Onion | CHANGED | uncertain / abstain | complete / 3 |
| Toasted Milk Seasoning : Onion | same | uncertain / abstain | uncertain / abstain |
| Powdered Sugar Seasoning : Onion | CHANGED | uncertain / abstain | complete / 3 |
| Whole Wheat Flour Seasoning : Onion | same | complete / abstain | complete / abstain |
| Dry ginger powder Seasoning : Onion: Garlic | CHANGED | uncertain / abstain | uncertain / abstain |
| Dried Paprika Seasoning : 12% | same | uncertain / abstain | uncertain / abstain |
| Dried Paprika Seasoning : | same | uncertain / abstain | uncertain / abstain |
| Corn Oil: Onion | CHANGED | complete / 3 | uncertain / abstain |
| Moong Dal: Roasted | CHANGED | complete / abstain | uncertain / abstain |
| Milk Solids: Skimmed Milk | CHANGED | complete / 3 | uncertain / abstain |
| Rice Flour: Rice, Water | CHANGED | complete / 3 | uncertain / abstain |
| Roasted Barley Flour: Wheat | same | uncertain / abstain | uncertain / abstain |
| Coriander Leaf: Fresh | CHANGED | complete / abstain | uncertain / abstain |
| Oyster Mushrooms: Garlic | CHANGED | complete / 3 | uncertain / abstain |
| Mustard Greens: Salt | CHANGED | complete / 3 | uncertain / abstain |
| Wheat Flour (45%): Wheat | CHANGED | complete / 3 | uncertain / abstain |
| Wheat Flour 45%: Wheat | CHANGED | complete / 3 | uncertain / abstain |
| Vitamins and Minerals: Iron, Zinc | CHANGED | complete / abstain | uncertain / abstain |
| Tomato Concentrate: Tomato | CHANGED | complete / 3 | uncertain / abstain |
| Rice Flours: Wheat | CHANGED | complete / 3 | uncertain / abstain |
| Corn Oil: Onion: Garlic | CHANGED | uncertain / abstain | uncertain / abstain |
| Corn Oil: Onion (Moong Dal: Roasted) | CHANGED | complete / abstain | uncertain / abstain |
| Mystery Corn Oil: Onion | same | uncertain / abstain | uncertain / abstain |
| Corn Oil 12%: Onion | CHANGED | complete / 3 | uncertain / abstain |
| Dried Moong Dal: Roasted | same | uncertain / abstain | uncertain / abstain |
| Bishop’s Seed Oil: Onion | CHANGED | uncertain / abstain | complete / 3 |
| Corn Oil Seasoning : Onion | same | complete / 3 | complete / 3 |
| Milk Solids Seasoning : Onion | same | complete / abstain | complete / abstain |
| Moong Dal Seasoning (12%): Onion | same | complete / 3 | complete / 3 |
| Rice Bran Oil Seasoning : Onion | same | complete / 3 | complete / 3 |
| Invert syrup Seasoning : Onion | same | uncertain / 4 | uncertain / 4 |
| Paprika Oleoresin (0.6%): Roasted Sesame | same | complete / abstain | complete / abstain |
| Paprika Oleoresin: Roasted Sesame | same | complete / abstain | complete / abstain |
