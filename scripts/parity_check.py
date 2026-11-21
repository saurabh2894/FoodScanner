"""Run the Python pipeline and the JS port on the same texts; fail on any difference.

Usage: python scripts/parity_check.py     (needs node)
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from web_tables import tables  # noqa: E402

from foodscan.pipeline import analyse_text  # noqa: E402

BISCUIT = ("Ingredients: Refined wheat flour, sugar, edible vegetable oil (palmolein), invert syrup, "
           "raising agents (INS 500(ii), INS 503(ii)), emulsifier (INS 471), salt, added flavour (vanilla).")
CORPUS = [
    BISCUIT,
    "Ingredients: Whole wheat flour.",
    "Ingredients: Cucumber, water, salt, vinegar, dill.",
    "Ingredients: Sugar, refined wheat flo",
    "Ingredients: Rice, maltodextrin.", "Ingredients: Rice, dextrose.", "Ingredients: Rice, modified starch.",
    "Ingredients: Rice, soy protein isolate.", "Ingredients: Rice, high fructose corn syrup.",
    "Ingredients: Rice, interesterified vegetable oil.", "Ingredients: Rice, edible vegetable oil (hydrogenated).",
    "Ingredients: Water, sweetener (INS 950), salt.", "Ingredients: Water, colour (INS 150d), sugar.",
    "Ingredients: Milk, flavour enhancer (INS 621).", "Ingredients: Rice, added flavour (vanilla).",
    "Ingredients: Cucumber, salt. Contains permitted natural colour.",
    "Ingredients: Sugar, cocoa. Contains permitted natural colour. May contain nuts.",
    "Ingredients: Sugar. May contain nuts and other things here.",
    "Ingredients: Mango, sugar, pectin (INS 440).", "Ingredients: Mango, sugar, gelling agent (pectin INS 440).",
    "Ingredients: Mango, sugar, gelling agent (INS 407).",
    "Ingredients: Whole wheat flour, raising agents (INS 500(ii)).",
    "Ingredients: Cucumber, salt, preservative (INS 211).", "Ingredients: Cucumber, salt, INS 999.",
    "Ingredients: Sugar, gelatin substitute (INS 171).", "Ingredients: Water, colour (E171), salt.",
    "Ingredients: Cucumber, tomato, onion, carrot, salt, vinegar, dill, turmeric, cumin, garlic, water.",
    "Ingredients: Sugar, maltodextrin.", "Ingredients: Whole wheat flour, water, salt, yeast.",
    "Ingredients: Rice, jackfruit seed paste.", "Ingredients: Salt.", "Ingredients: Salt, sugar and more things.",
    "Ingredients: Dill, turmeric, black pepper.", "Ingredients: Milk, sugar, cardamom flavouring.",
    "Ingredients: Sugar, emulsifier (INS 471, salt", "Ingredients: Sugar, emulsifier (INS 471",
    "Salt", "", "#### ~~ 1234 !!!! 5678 ---- //// 9999 ==== ++++ ",
    "Nutrition facts per 100 g: energy 450 kcal, protein 8 g, fat 20 g",
    "INGREDIENTS:\nWheat flour,\nsalt,\nsugar.\nNutrition per 100g",
    "Ingredients: Rice, salt Manufactured by XYZ Foods", "Ingredients: Sugar (12.5%), salt, rice flour.",
    "सामग्री: चावल, नमक, चीनी और अन्य सामग्री", "Ingredients:   ",
    "Ingredients: Atta, salt.", "Ingredients: Atta.", "Ingredients: Toor dal.", "Ingredients: Eggs.",
    "Ingredients: Raising agents (INS 500(ii), 503(ii)), whole wheat flour.",
    "Ingredients: Refined wheat flour, sugar, raising agent (INS 500i(ii)), salt.",
    "Ingredients: Milk, sugar, stabilizer (INS 466), thickener (INS 407).",
    "Ingredients: Sugar, Glucose-Fructose Syrup, water, carbonating agent.",
    "Ingredients: Water, sugar, acidity regulator (INS 330), antioxidant (INS 300), preservative (E211).",
    "Ingredients: Tomato, edible vegetable oil (palmolein), salt, anti-foaming agent (INS 900a).",
    "Ingredients: Mango, sugar, lemon, colour (INS 102 and 110), flavour",
    "Ingredients: Peas (60%), water, salt.", "Ingredients: Potato, sunflower oil, iodised salt, chilli, turmeric.",
    # real chips label (see tests/test_real_label.py): as printed, and as tesseract read it
    "INGREDIENTS: Potato (83%), Edible Vegetable Oil*, *Seasoning (Sugar, Iodised Salt, Milk Solids (1.2%), Spices and Condiments, Maltodextrin, Flavour (Natural and Nature Identical Flavouring Substances), Cheese Powder (0.3%), Hydrolysed Vegetable Protein, Flavour Enhancers (627, 631), Edible Vegetable Oil (Palm, Coconut). *As flavouring agent. ALLERGEN ADVICE: Contains Soy, Milk",
    'INGREDIENTS: Potato (83%), Edible Vegetable Or",\n"Seasoning (Suger, lodised Salt, Mik Solids (1.2%), Spices\nand Comiments, Maltodextrin, Flavour (Natural and Nature\nidentical Raxvouring Substances}, Cheese Powler (0.3%),\nHydrolysed Vegetable Protein, Flavour Enhancers (627,\n631), Edible Vegetadie OF (Paim, Coconut).\n\n"AS favouring agent.',
    # Option A and compound expansion
    "Ingredients: Sugar, maltodextrin, refined wheat flo", "Ingredients: Sugar, emulsifier (INS 471, salt",
    "Ingredients: Cucumber, salt (iodised, vinegar", "Ingredients: Mango, sugar, pectin (INS 440, jam",
    "Ingredients: Potato, edible vegetable oil (palm, coconut), salt.",
    "Ingredients: Potato, raising agents (INS 500(ii), INS 503(ii)), salt.",
    "Ingredients: Potato, seasoning (salt, sugar, turmeric), oil.",
    "Ingredients: Potato, seasoning (salt, sugar, colour (INS 150d)), edible vegetable oil.",
    "Ingredients: Rice, masala (spices, salt, dextrose).", "Ingredients: *(salt, sugar), rice.",
    "Ingredients: Rice, mix (a (b, c), d (e, f)), salt.",
    "Ingredients:\nBase Mix(57%)(Ragi, Rice, Pea Protein, Urad Dal), Sabudana Flour, Potato Flour, Rice Bran Oil. Seasoning : Dehydrated Vegetables(Garlic, Onion, Tomato), Iodised Salt, Khaand, Natural Citric Acid, Milk Solids, Spices & Condiments, Natural & Nature Identical Flavours, Rosemary Extract, Contains natural color extracted from Paprika",
    "Ingredients: Rice, Rice Bran Oil. Seasoning : Iodised Salt, Sugar, Flavour.",
    "Ingredients: Rice, salt. Coating: Sugar, Cocoa.", "Ingredients: Rice, salt. Note: store in a cool place, away from light.",
    "Ingredients: Potato, salt. Contains permitted color.", "Ingredients: Ragi, salt.", "Ingredients: Ragi.",
    "Ingredients: Base Mix(57%)(Ragi, Rice, Urad Dal), salt, Rice Bran Oil.",
    "Ingredients: Rice flour, Rice Bran Oil. Seasoning: Iodised Salt.",
    "Ingredients: Water, sugar, INS 102.", "Ingredients: Water, sugar, E110, salt.", "Ingredients: Water, INS 150d, sugar.",
    "Ingredients: Water, sugar, INS 950.", "Ingredients: Water, sweetener (950 and 955), sugar.",
    "Ingredients: Water, sugar, colour (INS 102, INS 110).",
    "Ingredients: Potato, flavour enhancers (627, 631), salt.", "Ingredients: Potato, Flavour Enhancer (627).",
    "Ingredients: Potato, raising agents (500(ii), 503(ii)), salt.", "Ingredients: Water, colours (102, 110), sugar.",
    "Ingredients: Potato, salt (500), sugar (1200).", "Ingredients: Water, sweeteners (950 and 955), citric acid.",
    "Ingredients: Potato, flavouring (627), salt.", "Ingredients: Water, emulsifiers (471, 472e), sugar.",
    "Ingredients: Potato, *Seasoning (Sugar, Salt, Edible Vegetable Oil (Palm, Coconut). *As flavouring agent.",
    "Ingredients: Potato, *Seasoning (Sugar, Maltodextrin, Edible Vegetable Oil (Palm, Coconut). *As flavouring agent.",
    "Ingredients: Rice, salt (iodised. Contains soy",
    # synthetic fixtures for the section / short-input regression tests (tests/test_regression_sections_and_short_input.py)
    "Ingredients: Noodles: wheat flour, palm oil, salt, stabiliser (INS 452(i)). Masala tastemaker: mixed spices, salt, sugar, flavour enhancers (INS 627, INS 631), added flavour, colour (INS 150d). Contains wheat. Manufactured by Example Foods Pvt Ltd.",
    "Ingredients: wheat flour, palm oil, salt, stabiliser (INS 452(i)), mixed spices, salt, sugar, flavour enhancers (INS 627, INS 631), added flavour, colour (INS 150d). Contains wheat. Manufactured by Example Foods Pvt Ltd.",
    "Ingredients: Noodles: wheat flour, palm oil, salt, stabiliser (INS 452(i))\nMasala tastemaker: mixed spices, salt, sugar, flavour enhancers (INS 627, INS 631), added flavour, colour (INS 150d)\nContains wheat.",
    "INGREDIENTS :\r\n  Noodles:   wheat flour ,  palm oil,\r\n\r\n salt, stabiliser (INS 452(i)).  Masala   tastemaker :  mixed spices, salt,\nsugar, flavour enhancers (INS 627, INS 631), added flavour, colour (INS 150d).  CONTAINS wheat.",
    "Ingredients: Wheat flour, palm\noil, salt", "Ingredients: Rice, salt. Tastemaker: sugar, flavour.",
    "Ingredients: Rice, salt. Directions: add hot water, stir.", "Ingredients: Rice, salt. Serving suggestion: with butter.",
    "Ingredients: Rice, salt. Enjoy hot with butter.", "Ingredients: Rice, salt. Colour: INS 150d.",
    "Ingredients: Fruit: mango. Set: sugar, pectin (INS 440).", "Ingredients: Sugar (min. 10%), salt (approx. 2%), flavour.",
    "Ingredients: Sugar (12.5%), emulsifier (INS 322), milk solids, salt.", "Ingredients: Rice: 60%, salt.",
    "Ingredients: Milk: skimmed milk, cream, salt.", "Ingredients: Spices:\nTurmeric, cumin\nSeasoning: salt, flavour",
    # review fixes: percentage labels, same-line labels, OCR "O11" (real millet puff label: tests/test_review_labels.py)
    "INGREDIENTS:\nPuff 88%: Supergrain Blend (Jowar, Foxtail Millet,\nCorn, Rice)(72%), Rice Bran Oil(16%).\nSeasoning 12%: Vegetables and Spices (Onion,\nGarlic, Tomato, Chilli, Amchur, Tamarind), Salt,\nNatural and Nature Identical Flavours, Raw Sugar,\nAcidity Regulators(INS330, INS296, INS334),\nPotassium Chloride - Salt Substitute (INS 508),\nRosemary Extract - Antioxidant (INS 392).\nTHIS PRODUCT CONTAINS 37% MILLETS",
    "INGREDIENTS: Puff 88%: Supergrain Blend (Jowar, Foxtail Millet, Corn, Rice)(72%), Rice Bran O11 (16%). Seasoning 12%: Salt, Raw Sugar.",
    "Ingredients: Base Mix(57%)(Beetroot, Carrot, Rice, Urad Dal), Sabudana Flour, Potato Flour, Rice Bran Oil Seasoning : Dehydrated Vegetables(Garlic, Onion, Tomato), Iodised Salt, Natural & Nature Identical Flavours",
    "Ingredients: Rice, Rice Bran Oil Seasoning : Onion, Garlic, Flavour.", "Ingredients: Rice, Mystery Paste Seasoning : Onion, salt.",
    "Ingredients: Rice, Rice Bran Oil Colour : INS 150d.", "Ingredients: Rice, salt. Salt 5%: sugar, flavour.",
    "Ingredients: Rice, salt. Seasoning 12.5 %: sugar, flavour.", "Ingredients: Rice, Salt Seasoning 5%: Onion, chilli.",
    "Ingredients: Edible Vegetable O11, salt.", "Ingredients: Rice Bran Oil Seasoning: Onion.",
    "Ingredients: Rice, Mystery Seasoning : Dehydrated Vegetables(Garlic, Onion, Tomato), flavour.",
    "Ingredients: Rice, jackfruit seed paste, jaggery syrup.", "Ingredients: Rice, jackfruit, jackfruit, flavour.",
    "Ingredients: Rice, preservative (INS 211), emulsifier (INS 471), maltodextrin, INS 999.",
    "Ingredients: Jaggery.", "Ingredients: Ragi, jaggery, groundnut oil.", "Ingredients: Milk, INS 322.",
    "Ingredients: Milk, stabiliser (INS 452(i)).", "Ingredients: Rice, yeast extract, salt.", "Ingredients: Rice, pea protein.",
    "Ingredients: Rice, yeast extract, pea protein, natural flavour.", "Ingredients: Rice, salt. Contains soy, milk, wheat, gluten.",
    "Ingredients: Rice, salt. Contains soy. Contains permitted colour.", "Ingredients: Rice, salt. Contains artificial sweetener.",
    "Ingredients: Rice, 10il, salt.", "Ingredients: Rice, 0ils, o111, salt.", "Ingredients: Rice Bran 0il (16%), salt.", "Ingredients: Edible Vegetable 0il, Rice Bran O11.",
    # percentage headings and silent-loss regressions (tests/test_percentage_headings_regression.py)
    "Ingredients: Seasoning 12%: Vegetables and Spices (Onion, Garlic, Tomato, Chilli, Amchur, Tamarind), Salt, Natural and Nature Identical Flavours, Raw Sugar, Acidity Regulators (INS330, INS296, INS334), Potassium Chloride - Salt Substitute (INS 508), Rosemary Extract - Antioxidant (INS 392). Puff 88%: Supergrain Blend (Jowar, Foxtail Millet, Corn, Rice)(72%), Rice Bran Oil (16%). THIS PRODUCT CONTAINS 37% MILLETS",
    "Ingredients: Puff: Supergrain Blend (Jowar, Foxtail Millet, Corn, Rice)(72%), Rice Bran Oil (16%). Seasoning: Vegetables and Spices (Onion, Garlic), Salt, Natural and Nature Identical Flavours. THIS PRODUCT CONTAINS 37% MILLETS",
    "Seasoning 12%: Salt, Raw Sugar, Natural and Nature Identical Flavours.",
    "Ingredients: Rice, salt. Sugar, natural flavour.", "Ingredients: Rice, salt. Sugar, vinegar.", "Ingredients: Rice, salt. Khaand, amchur, tamarind.",
    "Ingredients: Rice, natural flavour. Sugar, vinegar.", "Ingredients: Rice, salt. Enjoy hot with butter.",
    "Ingredients: Rice, salt. Note: store in a cool place, away from light.", "Ingredients: Rice, salt. Directions: add hot water, stir.",
    "Ingredients: Rice, salt. *As flavouring agent.", "Ingredients: Rice, salt. Serving suggestion: with butter.",
    "Ingredients: Rice. Seasoning 12%: Salt. Enjoy hot. Coating: Sugar.", "Ingredients: Rice, salt. THIS PRODUCT CONTAINS 37% MILLETS",
    "Ingredients: Rice, salt. Allergen advice: contains soy.", "Ingredients: Rice Manufactured by Example Foods",
    "Ingredients: Rice, Acidity Regulators(INS330, INS296, INS334), salt.", "Ingredients: Rice, Preservatives (INS 211), Antioxidants (INS 392).",
    "Ingredients: Rice, humectants (INS 422), salt.", "Ingredients: Rice, Stabilisers (INS 466), Thickeners (INS 415), salt.",
    "Ingredients: Rice, Anticaking Agents (INS 551), Flour Treatment Agents (INS 300).",
    # vocabulary layer (tests/test_vocabulary_layer.py): ordinary wordings of plain staples
    "Ingredients: rolled oat flakes", "Ingredients: Oats", "Ingredients: steamed rolled oats", "Ingredients: corn flakes", "Ingredients: wheat flakes",
    "Ingredients: mung bean splits, edible vegetable oil, edible common salt, black salt", "Ingredients: split green gram, refined palm oil, table salt",
    "Ingredients: bengal gram dal", "Ingredients: red lentil, kala namak", "Ingredients: butter", "Ingredients: pasteurised butter, salt",
    "Ingredients: rolled oats, sugar, salt", "Ingredients: rolled oats, maltodextrin", "Ingredients: powdered sugar", "Ingredients: Honey",
    "Ingredients: brown rice, salted butter", "Ingredients: cold pressed sesame oil", "Ingredients: edible", "Ingredients: jackfruit seed paste, oat",
    # extraction completeness (tests/test_extraction_completeness.py): and-pairs, bracket kinds, Contains lines
    "Ingredients: wheat flour, emulsifier [472e] and flour treatment agent [1101(ii)], salt.", "Ingredients: rice, salt and sugar, water.",
    "Ingredients: rice, Spices and Condiments, Natural and Nature Identical Flavours, milk and cream.", "Ingredients: rice, colour (INS 102 and INS 110), water.",
    "Ingredients: rice, antioxidant (INS 392) and acidity regulator (INS 330), water.", "Ingredients: rice, emulsifiers (471) & raising agents (500(ii)).",
    "Ingredients: Noodles: wheat flour, salt and sugar. Masala: emulsifier [472e] and flour treatment agent [1101(ii)].",
    "Ingredients: Rice, salt.\nContains added flavours (nature identical flavouring substances).", "Ingredients: Rice, natural flavour, salt.\nContains added flavours.",
    "Ingredients: Rice, salt.\nContains wheat, milk and soy.\nMay contain traces of nuts.", "Ingredients: Rice, salt. Contains wheat and milk, permitted natural colour (160c) and added flavour.",
    "Ingredients: Rice, salt. Contains soy. Contains permitted colour. Manufactured by X.", "Ingredients: Rice, salt.\nManufactured by Example Foods.\nAllergen information: Contains wheat.\nContains added flavours",
    "Ingredients: Rice. May contain traces of nuts. Contains milk.", "Ingredients: raising agents [500(ii), 503(ii)], Colour [150d], rice.",
    # peel-label guard (tests/test_peel_label_guard.py, SYNTHETIC): a descriptor or form word makes a name, never a section label
    "Ingredients: Rice flour, salt, Paprika Powder Flake(0.6%): Roasted Sesame, Roasted Seaweed.",
    "Ingredients: Rice, Rice Bran Oil Seasoning Powder : Onion, salt.", "Ingredients: Rice, Rice Bran Oil Dried Flakes (5%): Onion, salt.",
    "Ingredients: Rice, Paprika Extract (5%): Roasted Sesame, salt.", "Ingredients: Rice, Thyme Mix (10%): Roasted Sesame, salt.", "Ingredients: Rice, Oregano Blend: Roasted Sesame, salt.",
    "Ingredients: Rice, Rice Bran Oil Seasoning : Onion, salt, flavour.", "Ingredients: Rice, Rice Bran Oil Seasoning (12%): Onion, salt, flavour.",
    # plural-policy-1 synonyms (tests/test_plural_synonyms_1.py, SYNTHETIC): plural/leaf forms map, other parts and processed forms do not
    "Ingredients: Rice, cumin seeds, caraway seeds, fenugreek seeds, anise seeds, ajwain seeds, salt.", "Ingredients: Rice, basil leaves, mint leaf, peppermint leaves, coriander leaves, dill leaves, bay leaves, salt.",
    "Ingredients: Rice, fenugreek leaves, basil seeds, chilli seeds, turmeric leaves, salt.", "Ingredients: Rice, oregano leaf extract, mint leaf extract, basil leaf oil, salt.", "Ingredients: Rice, chillis, red chilis, salt.",
    # demand-bulk-1 rows (tests/test_demand_bulk_1.py, SYNTHETIC)
    "Ingredients: Starch", "Ingredients: Rice, tapioca starch, salt.", "Ingredients: Modified starch, rice.", "Ingredients: Beans, water, salt.", "Ingredients: Wheat flour.", "Ingredients: Wheat flour, salt.",
    "Ingredients: Cabbage, cranberry, sugar.", "Ingredients: Edible peanut oil.", "Ingredients: Water, potable water, sugar.", "Ingredients: Cocoa butter, wheat gluten, apple juice, yeast extract, glucose syrup.",
    # held-sources-1 (tests/test_held_sources_1.py, SYNTHETIC + the owner's acceptance label text)
    "Ingredients: Banana powder", "Ingredients: Rice, banana powder, salt.", "Ingredients: Banana powder, maltodextrin.", "Ingredients: Strawberry powder, Beetroot powder (for natural colour).", "Ingredients: Rice, vitamins and minerals.",
    "Ingredients: Multigrain Flour Blend (45.7%) [Sprouted Ragi & Jowar (23.4%), Rice & Oat (22.3%)], Whole Milk Powder (29.5%), Date Powder (9%), Banana Powder, Strawberry Powder (5%), Skimmed Milk Powder, Vitamins and Minerals, Beetroot Powder, Antioxidant (Natural Tocopherol).",
    # marker-rows-1 (tests/test_marker_rows_1.py, SYNTHETIC): approved FAO section 3 substances are strong markers; claims and look-alikes are not
    "Ingredients: Rice, wheat gluten, salt.", "Ingredients: Water, fructose.", "Ingredients: Rice, hydrolysed vegetable protein, salt.", "Ingredients: Rice, Hydrolyzed Vegetable Protein.", "Ingredients: Water, lemon juice concentrate.",
    "Ingredients: Water, apple juice concentrate, salt.", "Ingredients: Oats, gluten free.", "Ingredients: Wheat flour (gluten free), salt.", "Ingredients: Rice, fructooligosaccharide.", "Ingredients: Water, orange juice concentrate.",
    "Ingredients: Rice, salt. Contains gluten.",
    # unplaced kind (tests/test_unplaced_kind_1.py, SYNTHETIC + the owner's acceptance label text): recognised by name only, never placed, lists abstain
    "Ingredients: Rice, vitamins and minerals.", "Ingredients: Rice, salt, vitamins & minerals.", "Ingredients: Vitamins.", "Ingredients: Minerals", "Ingredients: Sprouted ragi, rice.", "Ingredients: Water, fructose, vitamins and minerals.",
    "Ingredients: Multigrain Flour Blend (45.7%) [Sprouted Ragi & Jowar (23.4%), Rice & Oat (22.3%)], Whole Milk Powder (29.5%), Date Powder (9%), Banana Powder, Strawberry Powder (5%), Skimmed Milk Powder, Vitamins and Minerals, Beetroot Powder.",
    # plain starch rows (tests/test_starch_rows.py, SYNTHETIC): plain starch is Group 2; every modified form stays the strong marker
    "Ingredients: Starch", "Ingredients: Rice, starch.", "Ingredients: Rice, Starch (Modified).", "Ingredients: Rice, starch (acid treated).", "Ingredients: Rice, Tapioca Starch (Oxidised).", "Ingredients: Rice, starch (modified) (INS 1422).",
    "Ingredients: Rice, modified corn starch.", "Ingredients: Rice, corn starch, salt.", "Ingredients: Rice, tapioca starch, salt.",
    # pmc-decisions-2 (tests/test_pmc_reresearch_2.py, SYNTHETIC)
    "Ingredients: Coconut fat", "Ingredients: Rice, coconut fat.", "Ingredients: Rice, hydrogenated coconut fat.", "Ingredients: Rice, glucose syrup.", "Ingredients: Rice, dehydrated onion, caster sugar, natural vinegar.",
    # dehydrated-policy-1 (tests/test_dehydrated_forms_1.py, SYNTHETIC)
    "Ingredients: Dehydrated onion", "Ingredients: Rice, onion flakes, salt.", "Ingredients: Rice, onions flakes.", "Ingredients: Dehydrated vegetable, rice.", "Ingredients: Dehydrated potato flakes, rice.", "Ingredients: Rice, fried onion flakes.", "Ingredients: Rice, corn flakes, chilli flakes.",
    # marker-rows-2 (tests/test_marker_rows_2.py, SYNTHETIC): whey powder / whey solids are strong markers; whey protein bars and look-alikes are not read as them
    "Ingredients: Rice, whey powder, salt.", "Ingredients: Rice, whey solids.", "Ingredients: Milk, whey.", "Ingredients: Rice, Whey Powder (from milk).", "Ingredients: Rice, whey protein.",
    # ampersand split (tests/test_ampersand_split_1.py, SYNTHETIC + the owner's acceptance label): shared modifier, shared percentage, negative controls
    "Ingredients: Multigrain Flour Blend (45.7%) [Sprouted Ragi & Jowar (23.4%), Rice & Oat (22.3%)], Whole Milk Powder (29.5%), Date Powder (9%), Banana Powder, Strawberry Powder (5%), Skimmed Milk Powder, Vitamins and Minerals, Beetroot Powder, Antioxidant (Natural Tocopherol).",
    "Ingredients: Blend [Sprouted Ragi & Jowar (23.4%), Rice & Oat (22.3%)].", "Ingredients: Blend [Sprouted Ragi & Oat, Rice].", "Ingredients: Blend [Roasted Rice & Oat, Salt].", "Ingredients: Blend [Fermented Ragi & Oat, Salt].",
    "Ingredients: Blend [Spices & Condiments, Salt].", "Ingredients: Blend [Rice & Oat (Organic), Salt].", "Ingredients: Blend [Rice & Oat & Wheat, Salt].", "Ingredients: Blend [Salted Almonds & Pumpkin Seeds, Rice].",
    # provenance-fixes-1 (tests/test_nut_seed_condition.py, SYNTHETIC): item-level salt/sugar condition on nuts and seeds
    "Ingredients: Almonds", "Ingredients: Salted Almonds", "Ingredients: Almonds (Almonds, Salt)", "Ingredients: Unsalted Almonds", "Ingredients: Almonds (no added salt)", "Ingredients: Rice, Salted Pumpkin Seeds.", "Ingredients: Wheat Flour, Sugar, Almonds, Butter.",
    "Ingredients: Rice, Sugar, Almonds.", "Ingredients: Sugared Almonds", "Ingredients: Flax Seeds, Honey.",
    # class-bulk-1 legume guard (tests/test_legume_condition_1.py, SYNTHETIC): item-level salt/sugar/brine condition and canned/bottled abstention on legume rows
    "Ingredients: Pinto Beans", "Ingredients: Salted Pinto Beans", "Ingredients: Pinto Beans (in brine)", "Ingredients: Pinto Beans (Pinto Beans, Salt)", "Ingredients: Adzuki Beans (sweetened)",
    "Ingredients: Unsalted Pinto Beans", "Ingredients: Pinto Beans (no added salt)", "Ingredients: Kidney Beans (canned)", "Ingredients: Chickpeas (pickled)", "Ingredients: Beans (bottled)",
    "Ingredients: Chickpeas (canned, salted)", "Ingredients: Roasted Soybeans", "Ingredients: Boiled Lentils", "Ingredients: Rice, Salt, Pinto Beans.", "Ingredients: Rice, Pinto Beans.",
    "Ingredients: Rice, Kidney Beans (canned).", "Ingredients: Salted Peas", "Ingredients: Moong Dal (salted)", "Ingredients: Baked Beans", "Ingredients: Sweeteners (Moong Dal, Jaggery Powder).",
    # class-bulk-2 vegetable kind (tests/test_class_bulk_2.py, SYNTHETIC): same item-level guard as the legume kind
    "Ingredients: Salted Potatoes", "Ingredients: Potatoes (in brine)", "Ingredients: Carrots (sweetened)", "Ingredients: Cucumber (pickled)", "Ingredients: Tomatoes (canned)", "Ingredients: Spinach (tinned)",
    "Ingredients: Unsalted Carrots", "Ingredients: Carrots (no added salt)", "Ingredients: Boiled Potatoes", "Ingredients: Shiitake Mushrooms", "Ingredients: Rice, Salt, Carrots.", "Ingredients: Rice, Tomatoes (canned).",
    "Ingredients: Spinach", "Ingredients: Kale (frozen)", "Ingredients: Sweeteners (Carrot, Jaggery Powder).", "Ingredients: Tomato Sauce",
    # powder standard (tests/test_powder_standard_1.py, SYNTHETIC): a bare 'X powder' abstains; '100%' and 'whole' are the only affirmative forms; unassessed co-ingredients are not laundered
    "Ingredients: Spinach Powder", "Ingredients: 100% Spinach Powder", "Ingredients: Spinach Powder (100%)", "Ingredients: Whole Spinach Powder", "Ingredients: Whole Milk Powder", "Ingredients: Milk Powder",
    "Ingredients: Rice, Spinach Powder.", "Ingredients: Rice, Spinach Powder, XQ9.", "Ingredients: Rice, Spinach Powder, Flavouring XQ9.", "Ingredients: Seasoning Blend (Spinach Powder, Salt).",
    "Ingredients: Spinach Extract Powder", "Ingredients: Beet Red Powder", "Ingredients: Spinach Powder (Maltodextrin)", "Ingredients: Spinach & Kale Powder", "Ingredients: Banana Powder", "Ingredients: 100% Date Powder",
    "Ingredients: Salted Pinto Beans Powder", "Ingredients: Rice, 100% Spinach Powder.", "Ingredients: Spinach Powder (45%)",
    # milk powder exception (tests/test_milk_powder_1.py, SYNTHETIC): FAO Group 1 names 'fresh, powdered or pasteurized milk'; only the enumerated fat-grade forms take it
    "Ingredients: Milk Powder", "Ingredients: Whole Milk Powder", "Ingredients: Skimmed Milk Powder", "Ingredients: Toned Milk Powder", "Ingredients: Buffalo Milk Powder", "Ingredients: Whole Buffalo Milk Powder",
    "Ingredients: Milk Powder (45%)", "Ingredients: Fortified Milk Powder", "Ingredients: Instant Milk Powder", "Ingredients: Milk Powder Blend", "Ingredients: Milk Powder (Vitamins Added)",
    "Ingredients: Skimmed Milk Powder (Soy Lecithin)", "Ingredients: Milk Solids Powder", "Ingredients: Rice, Milk Solids Powder.", "Ingredients: Rice, Salt, Milk Powder.", "Ingredients: Rice, Milk Powder.",
    "Ingredients: Blend (Milk Solids Powder, Salt).", "Ingredients: Milk Solids",
    # class-bulk-3 fruit kind (tests/test_class_bulk_3.py, SYNTHETIC): same item-level guard (sugar/syrup/salt -> Group 3; canned/bottled/preserved abstain) and the powder standard
    "Ingredients: Salted Plums", "Ingredients: Plums (in syrup)", "Ingredients: Mango (sweetened)", "Ingredients: Strawberries (with sugar)", "Ingredients: Mango (preserved)", "Ingredients: Apples (bottled)",
    "Ingredients: Strawberries (no added sugar)", "Ingredients: Strawberries (frozen)", "Ingredients: Rice, Apples (canned).", "Ingredients: Rice, Salt, Apples.", "Ingredients: Mango Powder", "Ingredients: 100% Mango Powder",
    "Ingredients: Whole Banana Powder", "Ingredients: Spinach & Apple Powder", "Ingredients: Canned Peaches", "Ingredients: Dried Apricots", "Ingredients: Sweeteners (Dates, Jaggery Powder).",
    # dried forms and unknown additions on the same item (tests/test_class_bulk_3.py, SYNTHETIC)
    "Ingredients: Dried Mango", "Ingredients: Dried Mango (Sugar)", "Ingredients: Dried Mango (XQ9)", "Ingredients: Dried Pineapple (Sugar, XQ9)", "Ingredients: Dried Blueberries (Sunflower Oil)",
    "Ingredients: Dried Mango (Sulphur Dioxide)", "Ingredients: Sweetened Dried Mango", "Ingredients: Candied Pineapple", "Ingredients: Dried Cranberries (Sugar)", "Ingredients: Rice, Dried Mango (XQ9).",
    "Ingredients: Pinto Beans (XQ9)", "Ingredients: Carrots (Sunflower Oil)", "Ingredients: Dried Banana (Honey)", "Ingredients: Kidney Beans (cooked)",
    # class-bulk-4 flour kind joins the unknown-bracket abstention (tests/test_class_bulk_4.py, SYNTHETIC)
    "Ingredients: Oat Flour (XQ9)", "Ingredients: Rye Flour (XQ9)", "Ingredients: Wheat Flour (XQ9)", "Ingredients: Whole Wheat Flour (Atta)", "Ingredients: Wheat Flour (Organic)", "Ingredients: Oat Flour",
    "Ingredients: Rye Flour", "Ingredients: Wild Rice", "Ingredients: Buckwheat", "Ingredients: Rice, Oat Flour.", "Ingredients: Oat Flour, XQ9.", "Ingredients: Enriched Wheat Flour",
    # synonyms-2 (tests/test_synonyms_2.py, SYNTHETIC): every applied alias alone, conditioned forms of one alias, and parked aliases that must stay unassessed
    "Ingredients: Sucrose", "Ingredients: Mandarin Oranges", "Ingredients: Chinese Gooseberry", "Ingredients: Broccoli Rabe", "Ingredients: Rapini", "Ingredients: Sunchokes", "Ingredients: Water Spinach", "Ingredients: Kangkong", "Ingredients: Christophine", "Ingredients: Moth Bean", "Ingredients: Mat Bean", "Ingredients: Lychee", "Ingredients: Horseradish Tree Pods", "Ingredients: Sweetpotato Leaves", "Ingredients: Portobello", "Ingredients: Portabello", "Ingredients: Portobella", "Ingredients: Gai-Lan", "Ingredients: Kai-Lan", "Ingredients: Mamey Colorado", "Ingredients: Marmalade Plum", "Ingredients: Garlic Pear", "Ingredients: Pak Choi",
    "Ingredients: Salted Lychee", "Ingredients: Lychee (pickled)", "Ingredients: Lychee Powder", "Ingredients: 100% Lychee Powder", "Ingredients: Rice, Lychee.", "Ingredients: Moth Bean (salted)", "Ingredients: Sucrose, Salt.",
    "Ingredients: Bok Choy", "Ingredients: Tumeric", "Ingredients: Chili", "Ingredients: Cane Sugar", "Ingredients: Maida", "Ingredients: Yellow Cherries", "Ingredients: Chick Peas", "Ingredients: Badishep",
    # engine-fixes-1 (tests/test_engine_fixes_1.py, SYNTHETIC): target-safe synonym rewrite; bok choy routes to bok choy cabbage, which is unchanged
    "Ingredients: Bok Choy", "Ingredients: Bok Choy Cabbage", "Ingredients: Pak Choi", "Ingredients: Bok Choy (raw)", "Ingredients: Salted Bok Choy", "Ingredients: Baby Bok Choy", "Ingredients: Bok Choy, Bok Choy Cabbage.",
    "Ingredients: Rice, Bok Choy.", "Ingredients: Chinese Cabbage", "Ingredients: Moong Dal", "Ingredients: Moong", "Ingredients: Jerusalem Artichokes",
    # per-form-1 (tests/test_per_form_1.py, SYNTHETIC): roasted/toasted plain grains and flours; whole_food unknown-bracket abstention; parked forms
    "Ingredients: Roasted Buckwheat", "Ingredients: Toasted Oat Flour", "Ingredients: Toasted Rice", "Ingredients: Toasted Unsalted Oat Flour", "Ingredients: Toasted Salted Oat Flour", "Ingredients: Toasted Almonds",
    "Ingredients: Rice, Toasted Oat Flour.", "Ingredients: Toasted Oat Flour, Salt.", "Ingredients: Rice (XQ9)", "Ingredients: Milk (XQ9)", "Ingredients: Wheat (XQ9)", "Ingredients: Toasted Oat Flour (XQ9)",
    "Ingredients: Rice (Basmati)", "Ingredients: Milk (Skimmed)", "Ingredients: Enriched Wheat Flour", "Ingredients: Fortified Wheat Flour", "Ingredients: Sprouted Ragi", "Ingredients: Pearled Barley", "Ingredients: Vitamins and Minerals",
    # per-form-1 round 2 (tests/test_per_form_1.py, SYNTHETIC): species-of-origin provenance in a milk bracket on a milk head item only
    "Ingredients: Milk (Pasteurized Cow Milk)", "Ingredients: Milk (Buffalo Milk)", "Ingredients: Milk (Goat Milk)", "Ingredients: Milk (Cow)", "Ingredients: Rice (Cow Milk)", "Ingredients: Rice (Cow)",
    "Ingredients: Goat Milk (Pasteurized)", "Ingredients: Toned Milk (Cow Milk)", "Ingredients: Egg (Cow Milk)", "Ingredients: Milk (Cow Milk, XQ9)", "Ingredients: Milk solids (Pasteurized skimmed cow milk)",
    # per-form-1 amendment 2 (tests/test_per_form_1.py, SYNTHETIC): 'toasted' narrowed to the 23 Batch-4 grain/flour terms, no other qualifier
    "Ingredients: Toasted Milk", "Ingredients: Toasted Egg", "Ingredients: Toasted Sweetened Oat Flour", "Ingredients: Toasted Honey Oat Flour", "Ingredients: Toasted Flavoured Oat Flour", "Ingredients: Toasted Brown Rice",
    "Ingredients: Toasted Whole Wheat Flour", "Ingredients: Toasted Oats", "Ingredients: Roasted Milk", "Ingredients: Milk Solids (Cow Milk)",
    # salted-grain guard (tests/test_salted_grain_guard.py, SYNTHETIC): 23 Batch-4 grain/flour terms with salt added take Group 3; other rows unchanged
    "Ingredients: Salted Buckwheat", "Ingredients: Roasted Salted Buckwheat", "Ingredients: Salted Rice", "Ingredients: Salted Wheat Flour", "Ingredients: Salted Oat Flour", "Ingredients: Rice (salted)",
    "Ingredients: Rice (Rice, Salt)", "Ingredients: Unsalted Rice", "Ingredients: Rice (no added salt)", "Ingredients: Salted Milk", "Ingredients: Salted Egg", "Ingredients: Rice, Salted Buckwheat.",
    "Ingredients: Salted Wheat Flour, Water.", "Ingredients: Salted Parboiled Rice", "Ingredients: Salted Almonds", "Ingredients: Salted Pinto Beans",
    # per-form-2b (tests/test_species_milk_2b.py, SYNTHETIC): species-head milk recognition (cow milk, goat milk); species words alone and milk solids stay abstained
    "Ingredients: Cow Milk", "Ingredients: Goat Milk", "Ingredients: Goat Milk (Pasteurized)", "Ingredients: Pasteurised Cow Milk", "Ingredients: Cow Milk Powder", "Ingredients: Goat Milk Powder", "Ingredients: Cow",
    "Ingredients: Rice (Cow Milk)", "Ingredients: Rice (Buffalo Milk)", "Ingredients: Milk Solids (Pasteurized Skimmed Cow Milk)", "Ingredients: Cow Milk, Starter Culture", "Ingredients: Sheep Milk", "Ingredients: Cow Milk Solids",
    # class-bulk-5 (tests/test_class_bulk_5_nuts.py, SYNTHETIC): 20 nut_seed rows; item-level salt/sugar guard; held seeds and nut forms stay unrecognised
    "Ingredients: Cashew Nuts", "Ingredients: Walnuts", "Ingredients: Sesame Seeds", "Ingredients: Chia Seeds", "Ingredients: Chestnuts", "Ingredients: Pistachio Nuts", "Ingredients: Salted Cashew Nuts",
    "Ingredients: Walnuts, Sugar", "Ingredients: Sesame Seeds, Salt", "Ingredients: Roasted Cashew Nuts", "Ingredients: Oil Roasted Cashew Nuts", "Ingredients: Lotus Seeds", "Ingredients: Breadfruit Seeds",
    "Ingredients: Almond Butter", "Ingredients: Cashew Nuts (salted)", "Ingredients: Hazelnuts, Pecans, Brazil Nuts",
    # dairy-rows-1 (tests/test_dairy_rows_1.py, SYNTHETIC): five whole_food rows (sheep milk; duck, goose, quail, turkey eggs); held and other forms stay unrecognised
    "Ingredients: Sheep Milk", "Ingredients: Duck Eggs", "Ingredients: Quail Eggs", "Ingredients: Salted Duck Eggs", "Ingredients: Duck Eggs, Salt", "Ingredients: Sheep Milk (XQ9)", "Ingredients: Duck Eggs (cow milk)",
    "Ingredients: 100% Goose Eggs Powder", "Ingredients: Turkey Eggs Powder", "Ingredients: Human Milk", "Ingredients: Sheep Milk Powder", "Ingredients: Rice (Sheep Milk)",
    # nut-guard-1 (tests/test_nut_guard_1.py, SYNTHETIC): canned/bottled/preserved, brine and unrecognised-bracket guards also apply to kind nut_seed
    "Ingredients: Almonds (canned)", "Ingredients: Almonds (brine)", "Ingredients: Almonds (XQ9)", "Ingredients: Walnuts (preserved)", "Ingredients: Walnuts (sunflower oil)", "Ingredients: Cashew Nuts (no added salt)",
    "Ingredients: Pumpkin Seeds (XQ9)", "Ingredients: Flax Seeds (bottled)", "Ingredients: Sesame Seeds (raw)", "Ingredients: Almonds (skin removed)", "Ingredients: Almonds, Cashew Nuts (XQ9)", "Ingredients: Chia Seeds (in brine)", "Ingredients: Almonds (XQ9), Rice (XQ9)", "Ingredients: Almonds (canned), Kidney Beans (canned)", "Ingredients: Kidney Beans (canned)", "Ingredients: Rice (XQ9)", "Ingredients: Walnuts (brine)", "Ingredients: Walnuts (sunflower oil)", "Ingredients: Walnuts (salted)", "Ingredients: Walnuts (sugar)", "Ingredients: Walnuts (honey)", "Ingredients: Almonds (salt, sunflower oil)",
    # fats-rows-1 (tests/test_fats_rows_1.py, SYNTHETIC): 20 culinary rows (19 oils and lard); hydrogenated forms stay Group 4; held, synonym and animal-fat terms stay unrecognised
    "Ingredients: Walnut Oil", "Ingredients: Lard", "Ingredients: Wheat Germ Oil", "Ingredients: Hydrogenated Lard", "Ingredients: Partially Hydrogenated Palm Kernel Oil", "Ingredients: Interesterified Corn Oil",
    "Ingredients: Rice, Almond Oil", "Ingredients: Walnuts (walnut oil)", "Ingredients: Corn and Canola Oil", "Ingredients: Corn Oil (XQ9)", "Ingredients: Corn Oil Powder", "Ingredients: Salted Lard", "Ingredients: Nutmeg Butter",
    "Ingredients: Shea Butter", "Ingredients: Rapeseed Oil", "Ingredients: Beef Tallow", "Ingredients: Lard, Salt", "Ingredients: Milk, Lard",
    # tea-coffee-rows-1 (tests/test_tea_coffee_rows_1.py, SYNTHETIC): two whole_food rows; held forms, aliases and conditioned forms
    "Ingredients: Tea", "Ingredients: Coffee", "Ingredients: Tea, Sugar", "Ingredients: Coffee, Milk", "Ingredients: Tea (sugar)", "Ingredients: Coffee (chicory)", "Ingredients: Instant Coffee", "Ingredients: Decaffeinated Tea",
    "Ingredients: Tea, Natural Flavour", "Ingredients: 100% Coffee Powder", "Ingredients: Coffee Powder", "Ingredients: Salted Tea", "Ingredients: Green Tea", "Ingredients: Hibiscus Tea", "Ingredients: Tea, Maltodextrin",
    # whole-food-guard-1 (tests/test_whole_food_guard_1.py, SYNTHETIC): added-substance and distinct-nested-food abstentions on whole_food rows; same-food and species brackets unchanged
    "Ingredients: Salted Milk", "Ingredients: Milk (sugar)", "Ingredients: Milk (sunflower oil)", "Ingredients: Eggs (canned)", "Ingredients: Eggs (brine)", "Ingredients: Ragi (preserved)", "Ingredients: Salted Egg",
    "Ingredients: Rice (Egg)", "Ingredients: Eggs (Rice)", "Ingredients: Milk (Rice)", "Ingredients: Milk (Buffalo Milk)", "Ingredients: Eggs (Egg)", "Ingredients: Dehydrated Vegetable (Onion)", "Ingredients: Milk (Salted), Water",
    "Ingredients: Milk, Eggs (Rice)", "Ingredients: Unsalted Milk", "Ingredients: Salted Rice", "Ingredients: Rice (sugar)", "Ingredients: Rice (salt, sunflower oil)", "Ingredients: Salted Rice (canned)", "Ingredients: Rice (salt, sugar)", "Ingredients: Salted Buckwheat (brine)", "Ingredients: Rice (Wheat)", "Ingredients: Rice (Walnuts)", "Ingredients: Milk (Milk Solids)", "Ingredients: Milk (Toned Milk)", "Ingredients: Milk solids (Toned Milk) & Active Culture", "Ingredients: Dehydrated Vegetable (Peas)", "Ingredients: Toned Milk (Goat Milk)",
    # culinary-guard-1 (tests/test_culinary_guard_1.py, SYNTHETIC): unknown brackets and powders on oil/fat rows abstain; 'A and B oil' naming two oils is kept whole; supported oil-source brackets and food+oil lists unchanged
    "Ingredients: Sunflower Oil (XQ9)", "Ingredients: Edible Vegetable Oil (palm, coconut)", "Ingredients: Edible Vegetable Oil (palm, coconut, XQ9)", "Ingredients: Sesame Oil (Gingelly Oil)", "Ingredients: Rice Bran Oil (oryzanol)",
    "Ingredients: Sunflower Oil Powder", "Ingredients: 100% Sunflower Oil Powder", "Ingredients: Ghee Powder", "Ingredients: Jaggery Powder", "Ingredients: Soybean and Palm Oil", "Ingredients: Sesame and Sunflower Oil",
    "Ingredients: Rice and Sunflower Oil", "Ingredients: Potato, Edible Vegetable Oil (palm, coconut), Salt.", "Ingredients: Salt (XQ9)", "Ingredients: Hydrogenated Sunflower Oil", "Ingredients: Walnuts (sunflower oil)", "Ingredients: Sunflower Oil (XQ9 Oil)", "Ingredients: Sunflower Oil (Mineral Oil)", "Ingredients: Sunflower Oil (Essential Oil)", "Ingredients: Sunflower Oil (Rice)", "Ingredients: Sunflower Oil (Starch)", "Ingredients: Sunflower Oil (Milk)", "Ingredients: 100% Sunflower Oil Powder (Rice)", "Ingredients: Sunflower Oil Powder (100% Starch)", "Ingredients: Hydrogenated Sunflower Oil (Rice)",
    # headline-aggregation-1 (tests/test_headline_aggregation_1.py, SYNTHETIC): an abstention headed by weak markers also names the other active blockers
    "Ingredients: Multigrain Blend (Sprouted Ragi & Jowar (23.4%), Wheat), Vitamins#, Minerals##, Antioxidant (INS 320), Edible Vegetable Oil.", "Ingredients: Wheat, Antioxidant (INS 320).", "Ingredients: Spinach Powder, Antioxidant (INS 320).",
    "Ingredients: Turmeric (Colouring & Spices), Xyzzy.", "Ingredients: Sunflower Oil Powder, Antioxidant (INS 320).", "Ingredients: Vitamins, Minerals, Antioxidant (INS 320).", "Ingredients: Rice, Colour (INS 150d).",
    # photo-path resilience (tests/test_photo_path_resilience.py)
    "REDIENTS: Wheat flour, sugar, edible vegetable oil (palm), invert sugar syrup, salt, raising agents (INS 503(ii), INS 500(ii)), emulsifier (INS 322).",
    "REDIENTS: Rice, salt, sugar, edible vegetable oil, water, turmeric, cumin, garlic.", "GREDIENTS: Rice, salt, sugar, oil, water, cumin.",
    "lNGREDlENTS: Rice, salt, sugar, maltodextrin, water.", "INGREDIEN: Rice, salt, sugar.", "INGREDIENT5: Rice, salt, sugar, water.",
    "Nutrients: energy 450 kcal, protein 8 g, fat 20 g, sugar 10 g.", "Recipients: please send the whole panel, closer.",
    "We love fine redients in our kitchen, rice, salt, sugar, oil and more.",
    "NEW! Tasty crunchy snack. Buy now and get a free gift inside, limited offer, enjoy the taste!\n\nWheat flour, sugar, edible vegetable oil (palm), invert sugar syrup, salt, raising agents (INS 503(ii), INS 500(ii)), emulsifier (INS 322).\n\nNutritional information per 100 g\nEnergy 450 kcal\nProtein 8 g\n\nContains: wheat, milk, soy.",
    "NEW! Tasty crunchy snack. Buy now and get a free gift inside, limited offer, enjoy the taste!\n\nRice, salt, sugar, edible vegetable oil, water, turmeric, cumin, garlic.\n\nNutritional information per 100 g\nEnergy 450 kcal",
    "Nutritional information per 100 g\nEnergy 450 kcal\nProtein 8 g\nCarbohydrate 60 g\nTotal fat 20 g\nSodium 600 mg",
    "Contains: wheat, milk, soy, gluten, peanuts, tree nuts.", "NEW, tasty, crunchy, buy now, free gift, limited offer, enjoy the taste",
    "Energy 450 kcal, Protein 8 g, Carbohydrate 60 g, Total fat 20 g, Sodium 600 mg, Fibre 2 g",
    "Ingredients: SUGAR, EMULSIFIER OF VEGETABLE ORIGIN [472e] AND FLOUR TREATMENT AGENT [1101(ii)]. CONTAINS: WHEAT, MILK",
    "Ingredients: Sugar, colour of natural origin (160b), SPICES AND CONDIMENTS, SALT.",
    "Ingredients: Rice, acidity regulators (330, 508), stabilizer (412), raising agent (500(i), 501(i)), emulsifier (451(i)), flavour enhancer (635), salt, colour (INS 105), preservative (INS 999).",
    # failure-1 fix: a colour that is only a function note on a named ingredient is not an added colour (tests/test_colour_note_scope.py)
    "Ingredients: Rice flakes (37%), Roasted gram (25%), Ground spices & condiments (iodised salt, red chilli, turmeric (colouring & spices), cumin), Dried curry leaves (0.5%).",
    "Ingredients: Milk fat, salt, annatto (colour).", "Ingredients: Rice, salt, beetroot powder (for natural colours).", "Ingredients: Rice, salt, turmeric (colour).",
    "Ingredients: Butter, salt, colour (INS 160b annatto).", "Ingredients: Sugar, food colour - E122.", "Ingredients: Rice, spices & condiments (salt, colour (INS 150d)).",
    "Ingredients: Rice, spices (salt, natural colour, cumin).", "Ingredients: Rice, salt, turmeric (colouring & spices). Contains permitted natural colour.",
    "Ingredients: Rice, salt, turmeric (colouring & spices), added flavour.",
    "Ingredients: Rice, salt, turmeric (as colourant).", "Ingredients: Rice, salt, turmeric (as colouring).", "Ingredients: Rice, salt, turmeric (for colour).",
    "Ingredients: Rice, salt, turmeric (colour & spices).", "Ingredients: Rice, salt, turmeric (natural colour).", "Ingredients: Rice, salt, paprika (as colorant).",
    "Ingredients: Rice, salt, turmeric (colouring agent).", "Ingredients: Rice, salt, turmeric (as colourant), added flavour.",
    "Ingredients: Rice, salt, turmeric (as colourant). Contains permitted natural colour.", "Ingredients: Rice, salt, turmeric (as colourant), colour (INS 150d).",
    "Ingredients: Rice, salt, turmeric (as colourant), raising agent (INS 500(ii)).",
    "Ingredients: Rice, salt, turmeric (colour & flavour).", "Ingredients: Rice, salt, turmeric (colouring and flavouring).", "Ingredients: Rice, salt, turmeric (flavour & colour).",
    "Ingredients: Rice, salt, turmeric (colour & flavour), added flavour.", "Ingredients: Rice, salt, turmeric (colour & flavour), colour (INS 150d).",
    "Ingredients: Rice, salt, turmeric (colour & flavour), emulsifier (INS 322).", "Ingredients: Rice, salt, turmeric (colour & flavour), flavour enhancer (INS 627).",
    "Ingredients: Rice, salt, turmeric (colour & flavour). Contains added flavour.", "Ingredients: Rice, salt, turmeric (colour & flavour). Contains permitted natural colour.",
    # combined follow-up fixes (tests/test_followup_fixes.py)
    "Ingredients: Water, sugar, emulsifiers and stabilizers [INS 460(i), INS 471, INS 466], salt.", "Ingredients: Sugar, emulsifier [472e] and flour treatment agent [1101(ii)], salt.",
    "Ingredients: Rice, Corn (3%, salt, sugar, added flavour. Store in a cool place.", "Ingredients: Rice, Corn {wheat flour (3%), sugar, salt, added flavour, palm oil.",
    "Ingredients: Rice, salt, Sugar [aged, flavour enhancer (INS 627), oil. Contains milk.", "Ingredients: Rice,\nCorn (3%,\nsalt),\nsugar [a (b)], oil.",
    "Ingredients: Rice, salt. Sprinkler Mix (Topping): chilli, cumin, garlic.", "Ingredients: Seasoning: salt, sugar. Seasoning: chilli, cumin. Seasoning: pepper, clove.",
    "Ingredients: Rice, salt. Topping 2: chilli, cumin, garlic.", "Ingredients: Noodles: wheat flour, salt. Seasoning: Masala Mix: sugar, flavour. Sprinkler Mix (Topping): chilli, cumin.",
    "Pasteurized Toned Milk & Active Lactic Culture", "Ingredients: Double Toned Milk, Active Culture.", "Ingredients: Dahi.", "Ingredients: Milk, live cultures.",
    "Ingredients: Bengal Gram Flour (Besan), Refined Palmolein Oil, Edible Common Salt.", "Ingredients: Gram flour, salt.", "Ingredients: Sugar, refined wheat flo",
    "Ingredients: Rice, salt, turmeric (colour), added flavour.", "Ingredients: Rice, salt, turmeric (colour), colour (INS 150d).", "Ingredients: Butter, colour (INS 160b).",
    "Ingredients: Milk, live cultures.", "Ingredients: Double toned milk, active culture.", "Ingredients: Toned milk, active culture, xyzgum.",
    "Ingredients: Milk, active culture, sugar.", "Ingredients: Milk, active culture, sweetener (INS 950).", "Ingredients: Milk, active culture, stabilizer (INS 440).",
    "Ingredients: Dahi, active culture.", "Ingredients: Active culture.", "Ingredients: Milk, water.", "Ingredients: Milk, yoghurt culture, lactic culture.", "Ingredients: Curd.", "Ingredients: Double-toned milk, live culture.",
    # fix round + INS-misread addendum (tests/test_round_fixes.py)
    "MFG. BY: SYMEGA FOOD INGREDIENTS LTD., KERALA\nSOURCE: EUROMONITOR, COOKING INGREDIENTS & MEALS, RETAIL VALUE RSP IN 2024\nSINGLE SERVE PACK.", "Active ingredients: caffeine, taurine, sugar, water",
    "Ingredients: retail value, single serve pack, premium quality, best offer, free gift.", "Biscuits\nINGREDIENTS REFINED WHEAT FLOUR, SUGAR, SALT, PALM OIL.",
    "Ingredients: Noodles (88.5%): Supergrain blend (whole wheat (atta), jowar) (83%), guar gum, iodised salt. Seasoning (11.5%): Mixed spices (onion, cumin), sugar, salt.",
    "Ingredients: Rice, salt, emulsifying agent.", "Ingredients: Rice, salt, emulsifying & stabilizing agent (INS 1422, INS 415).", "Ingredients: Rice, salt, stabilizing agent (INS 440).",
    "Ingredients: Pasteurized Buffalo Milk.", "Ingredients: Buffalo milk, active lactic culture.", "Ingredients: Pasteurised toned milk, active lactic culture and probiotic culture (Bifidobacterium lactis & Lactobacillus acidophilus).",
    "Ingredients: Water, thickeners - E1442, E1450, salt.", "Ingredients: Sugar, nature identical flavouring substance and dough conditioner (223).",
    "Ingredients: Whole Grains (34%) {rolled oats, ragi flakes}; Dry Fruits, Nuts & Seeds (22%) {raisin, almonds}; Organic Jaggery, Cocoa Powder (7%), Dates.",
    "Ingredients: Roasted Peanuts (91%) Sugar, Stabilizer (INS471), Iodised Salt.", "Ingredients: Sugar, nature identical and natural flavouring substances, salt.",
    "Ingredients: Seasoning 12%: Acidity Regulators (INS330, INS296, INS334), Potassium Chloride - Salt Substitute (INS 508), Rosemary Extract - Antioxidant (INS 392).",
    "Ingredients: Seasoning 12%: Acidity Regulators (INS330, INS236, INS334), Potassium Chloride - Salt Substitute (INS 508), Rosemary Extract - Antioxidant (INS 382).",
    "Ingredients: Rice, salt, acidity regulator (INS 392).", "Ingredients: Rice, salt, preservative (INS 999).", "Ingredients: Water, emulsifiers and stabilizers [INS 460(i), INS 471].",
    # dairy vocabulary + provenance line + negation scoped to its span (tests/test_dairy_negation_round.py)
    "Ingredients: Milk, starter culture.", "Ingredients: Pasteurised toned milk, milk solids, active lactic cultures.", "Ingredients: Pasteurised double toned milk, Milk Solids, Active Lactic Cultures (L.bacillus delbrueckii subsp. bulgaricus, S.thermophilus).",
    "Pasteurised Toned Milk & Active Lactic Cultures, Made from Toned Milk Allergen Information: Contains Milk", "Ingredients: Milk solids and Sugar.", "Ingredients: Rice, salt, made from rice.",
    "Ingredients: Milk, salt. Contains no added flavours, added colour or preservatives.", "Ingredients: Milk, salt. CONTAINS NO ADDED FLAVOURS,\nADDED COLOUR OR PRESERVATIVES.",
    "Ingredients: Milk, salt. Contains added flavours.", "Ingredients: Milk, salt. No added colours, contains added flavour.", "Ingredients: Milk, salt. Contains added flavour, no added colours.",
    "Ingredients: Milk, salt. No added colours, contains preservative (INS 211).", "Ingredients: Milk, salt. Does not contain added flavour.", "Ingredients: Rice, salt. Free from nuts. Contains soy, milk. May contain traces of sesame.",
    "Ingredients: Mozzarella Cheese (Pasteurized Milk, Iodised Salt, Firming Agent (INS 509), Microbial Cultures and Microbial Rennet.)\n\nCONTAINS NO ADDED FLAVOURS,\nADDED COLOUR OR PRESERVATIVES.",
    "ingredients: PEAS, WATER, SALT", "Ingredients : Rice ; salt ; sugar.", "Ingredient: Rice, salt, sugar, ghee",
]
_f07 = Path(__file__).resolve().parent.parent / 'evaluation/dev_regression_15/inputs/F07.txt'
if _f07.exists():
    CORPUS.append('Ingredients: ' + _f07.read_text())


def py_result(text, source="ocr"):
    a = analyse_text(text, source=source)
    return {
        "answered": a.answered, "group": a.group, "reason": a.reason, "headline": a.headline,
        "ingredients": a.ingredients, "warnings": a.warnings, "unassessed": a.unassessed, "unplaced": a.unplaced, "ignored": a.ignored, "declared": a.declared, "heading": a.heading, "completeness": a.completeness,
        "sections": [[label, list(items)] for label, items in a.sections],
        "drivers": [{"ingredient": d.ingredient, "detail": d.detail, "source": d.source, "section": d.section} for d in a.drivers],
        "ins": [{"code": u.code, "name": u.name, "source": u.source, "classes": list(u.classes), "strength": u.strength,
                 "ingredient": u.ingredient, "section": u.section, "ref_name": u.ref_name, "ref_classes": list(u.ref_classes), "ref_partial": u.ref_partial, "ref_source": u.ref_source,
                 "declared": u.declared, "declared_roles": list(u.declared_roles), "role_notes": u.role_notes} for u in a.ins_mappings],
    }


# pasted-text path (source="text"): the regression fixtures, plus every corpus text above, must also match
PASTE = [
    "Puff 88%: Rice, Rice Bran Oil. Seasoning 12%: Salt, Flavour.", "REDIENTS: Rice, salt, sugar, water, cumin, oil.", "Rice, Rice Bran Oil Seasoning : Onion, Garlic, Flavour",
    "Ingredients: Milk", "Milk", "milk.", "INGREDIENTS : MILK", "  ingredients:milk  ", "Ingredients: milk.", "MILK, SALT",
    "", "   ", "\n \t\n", "Ingredients:", "Ingredients:   ", "###", "#### ~~ 1234 !!!! 5678", "1234 5678",
    "Salt", "Sugar, refined wheat flo", "Ingredients: Sugar, refined wheat flo", "Rice, salt", "rice,salt,sugar",
    "Nutrition facts per 100 g: energy 450 kcal, protein 8 g, fat 20 g", "Contains soy", "Contains permitted color.",
    "Sugar, maltodextrin", "Wheat flour", "Whole wheat flour.", "Mango, sugar, pectin (INS 440).",
    "Noodles: wheat flour, salt. Masala tastemaker: sugar, flavour.",
    "Noodles: wheat flour, palm oil, salt\nMasala tastemaker: mixed spices, flavour enhancers (INS 627, INS 631)",
    "Colour (INS 150d)", "INS 150d", "Potato (83%), edible vegetable oil, salt", "Eggs", "Toor dal",
    "Ingredients: Rice, salt, Thickeners (INS 508).", "Ingredients: Rice, salt, Salt substitute (INS 508).", "Ingredients: Rice, salt, Potassium chloride (INS 508).", "Ingredients: Water, Sugar, Class II Preservative (INS 211), Antioxidant (INS 300), Acidity Regulator (INS 330).", "Ingredients: Milk, Emulsifier & Stabilizers [INS 471, INS 407, INS 412].", "Ingredients: Water, Natural and Synthetic Food Colours (INS 150d, INS 122), Emulsifying & Stabilizing Agent (INS1422, INS415).",
    "Ingredients: Rice, salt, Thickener (INS 412).", "Ingredients: Milk, sugar, Emulsifying salts (INS 331).", "Ingredients: Sugar, fruit pulp, Thickener (INS 440), Citric acid.", "Ingredients: Rice, salt, Stabilizer (INS 412).",
    "Ingredients: Milk Solids, Sweeteners (Jaggery Powder, Dates Powder), Nature Identical Flavour, Cocoa powder.", "Ingredients: Milk solids, Sweeteners (Jaggery Powder, Dates Powder), Cocoa powder.", "Ingredients: Water, Sweeteners (Aspartame, Acesulfame K).", "Ingredients: Water, Sweeteners (Jaggery, Sucralose).", "Ingredients: Water, Sweetener (INS 950).", "Ingredients: Water, Natural sweeteners (Jaggery, Honey), Salt.",
    "Soyabean Seed", "Soybean", "Soya bean", "Soyabean Seed, Salt", "Water, Sugar, Zorbium", "Rice, flavour, Zorbium", "Zorbium, Quux", "Sugar, refined wheat flo", "Rice, salt, flavou", "Soybean oil, Soya beans",
    "Ingredients: Milk & Milk Solids", "Ingredients: Toned milk, milk solids.", "Ingredients: Pasteurized Cow Milk", "Ingredients: Cow milk, active culture",
    "Ingredients: Milk, milk solids, Vitamin A.", "Ingredients: Milk, milk solids, sugar.", "Ingredients: Milk, milk solids, flavour.", "Ingredients: Milk, milk solids, stabilizer (INS 440).",
    "Rice, lodised salt", "Rice, lodized salt", "Rice, iodized salt", "Rice, cotton seed oil", "Rice, refined palmolein oil",
    "Ingredients: Water, Xanthan gum (INS 415), Guar gum (INS 412).",
    "Ingredients: Rice, sequestrant - E385, dough conditioner (INS 223).",
]
TOTAL = len(CORPUS) + len(PASTE)


NODE = """
const fs = require('fs');
const E = require(process.argv[2]).createEngine(JSON.parse(fs.readFileSync(process.argv[3], 'utf8')));
const corpus = JSON.parse(fs.readFileSync(process.argv[4], 'utf8'));  // [text, source] pairs
const pick = (a) => ({answered: a.answered, group: a.group, reason: a.reason, headline: a.headline,
  ingredients: a.ingredients, warnings: a.warnings, unassessed: a.unassessed, unplaced: a.unplaced, ignored: a.ignored, declared: a.declared, heading: a.heading, completeness: a.completeness, sections: a.sections, drivers: a.drivers, ins: a.ins});
process.stdout.write(JSON.stringify(corpus.map(([t, source]) => pick(E.analyseText(t, { source })))));
"""


PAIRS = [(t, "ocr") for t in CORPUS] + [(t, "text") for t in PASTE]


def run_js(pairs):
    """Run the browser engine (web_preview/foodscan.js, under node) on [(text, source), ...]; returns one result dict per pair. Raises RuntimeError if node fails."""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        (td / "tables.json").write_text(json.dumps(tables()))
        (td / "corpus.json").write_text(json.dumps(pairs))
        (td / "run.js").write_text(NODE)
        out = subprocess.run(
            ["node", str(td / "run.js"), str(ROOT / "web_preview" / "foodscan.js"), str(td / "tables.json"), str(td / "corpus.json")],
            capture_output=True, text=True)
        if out.returncode:
            raise RuntimeError(out.stderr)
        return json.loads(out.stdout)


def main() -> int:
    try:
        js = run_js(PAIRS)
    except RuntimeError as e:
        print(e)
        return 2
    bad = 0
    for (text, source), j in zip(PAIRS, js):
        p = py_result(text, source)
        if p != j:
            bad += 1
            print(f"MISMATCH [{source}]:", repr(text))
            for k in p:
                if p[k] != j[k]:
                    print(f"  {k}:\n    py: {p[k]!r}\n    js: {j[k]!r}")
    print(f"{TOTAL - bad}/{TOTAL} analyses identical between Python and JS ({len(CORPUS)} photo-path texts, {len(PASTE)} pasted-text texts)")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
