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
# Synthetic exact-source water form controls, not real-label validation.
WATER_CONTROLS = ["Ingredients: " + f.format(t="Carbonated Water") + "." for f in ['{t}', 'Plain {t}', 'Salted {t}', 'Sugared {t}', 'Sweetened {t}', 'Flavoured {t}', 'Flavored {t}', 'Powdered {t}', 'Dried {t}', 'Refined {t}', 'Fresh {t}', '100% {t}', '{t} (100%)', '{t} (Water)', '{t} (Sugar)', '{t} (Rice)', '{t}, Sugar', '{t}, Water', '{t}, Rice', '{t}, Flavour', '{t}, Maltodextrin', '{t}, INS 999', '{t}, Preservative (INS 211)', 'Milk ({t})', 'Mango ({t})', 'Rice ({t})', 'Rice (Milk ({t}))', 'Sugar ({t})', '{t} concentrate', '{t} powder']]
import csv
with (ROOT / "src/foodscan/resources/descriptors.csv").open() as _fh:
    WATER_CONTROLS += ["Ingredients: " + text + "." for row in csv.DictReader(_fh) for d in [next(iter(row.values()))] for text in [d + " Carbonated Water", "Carbonated Water " + d]]
CORPUS = ['Ingredients: Mixed Spices (Clove, Cinnamon, Chilli) Preservative (INS 211).', 'Ingredients: Rice (Rice) Colour (INS 102).', 'Ingredients: Spices [Clove, Cinnamon] preservative (INS 211).', 'Ingredients: Rice (Rice), Preservative (INS 211).', 'Ingredients: Spices (Pepper Preservative (INS 211)).', 'Ingredients: Stabilizer (INS 414) Preservative (INS 211).', 'Ingredients: Stabiliser (INS 414) Preservative (INS 211).', 'Ingredients: Emulsifying Agent (INS 322) Preservative (INS 211).', 'Ingredients: Rice (Rice) (100%).', 'Ingredients: Rice (Rice) as colouring.', 'Ingredients: Mixed Spices (Clove, Cinnamon, Chilli).', 'Ingredients: Rice (Rice) with salt (1%).', 'Ingredients: Rice (Rice) and Preservative (INS 211).', 'Ingredients: Rice (Rice) Preservative free (claim).', 'Ingredients: Rice (Rice) Natural Flavour (vanilla).'] + WATER_CONTROLS + [
    BISCUIT,
    "Ingredients: Whole wheat flour.",
    (ROOT / "tests/fixtures/native_n08_readings/second.txt").read_text(),
    "Ingredients: Pasteurized Buffalo Milk Fat 6.00% Min., SNF 9.00% Min. Allergen Information: Contains Milk",
    "Ingredients: Pasteurized Buffalo Milk Fat 6.00% Min., SNF 9.00% Min., Vitamin A",
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
    # label-parser-16 senior correction (tests/test_label_parser_16_senior.py, SYNTHETIC): footnote marks inside a multi-word phrase are not removed; boundary marks still are
    "Ingredients: Rice\u201d Flour.", "Ingredients: Sunflower\u201d Oil.", "Ingredients: Skimmed\u201d Milk Powder.", "Ingredients: Rice# Flour.", "Ingredients: Rice* Flour.", "Ingredients: Vitamins# and Minerals##.",
    "Ingredients: Vitamins\u201d and Minerals**.", "Ingredients: Vitamins\u201d & Minerals**.", "Ingredients: Rice* (23%).", "Ingredients: Rice#, Sugar.", "Ingredients: Rice \u201cand\u201d Flour.", "Ingredients: Sugar\u2020, Salt\u2021.",
    # headline-aggregation-1 (tests/test_headline_aggregation_1.py, SYNTHETIC): an abstention headed by weak markers also names the other active blockers
    "Ingredients: Multigrain Blend (Sprouted Ragi & Jowar (23.4%), Wheat), Vitamins#, Minerals##, Antioxidant (INS 320), Edible Vegetable Oil.", "Ingredients: Wheat, Antioxidant (INS 320).", "Ingredients: Spinach Powder, Antioxidant (INS 320).",
    "Ingredients: Turmeric (Colouring & Spices), Xyzzy.", "Ingredients: Sunflower Oil Powder, Antioxidant (INS 320).", "Ingredients: Vitamins, Minerals, Antioxidant (INS 320).", "Ingredients: Rice, Colour (INS 150d).", "Ingredients: Multigrain Blend (Sprouted Ragi & Jowar (23.4%), Wheat), Vitamins, Minerals, Date Powder, Banana Powder, Strawberry Powder, Beetroot Powder, Antioxidant (INS 320), Edible Vegetable Oil.", "Ingredients: Banana Powder, Antioxidant.", "Ingredients: Vitamins, Banana Powder.", "Ingredients: Vitamins, XQ9.", "Ingredients: XQ9, Vitamins, Banana Powder.", "Ingredients: 100% Banana Powder, Antioxidant.", "Ingredients: 100% Banana Powder.", "Ingredients: Banana Powder, Rice.", "Ingredients: Beetroot Powder, Strawberry Powder.",
    # animal-guard-1 (tests/test_animal_guard_1.py, SYNTHETIC): eight meat rows; dried animal food is Group 3, animal powders abstain, other conditioned forms follow the existing guards
    "Ingredients: Chicken.", "Ingredients: Beef.", "Ingredients: Dried Beef.", "Ingredients: Dried Chicken, Salt.", "Ingredients: Beef Powder.", "Ingredients: 100% Beef Powder.", "Ingredients: Chicken Powder, Rice.", "Ingredients: Ground Beef.",
    "Ingredients: Roasted Chicken.", "Ingredients: Salted Beef.", "Ingredients: Smoked Chicken.", "Ingredients: Breaded Chicken.", "Ingredients: Chicken (XQ9).", "Ingredients: Beef (Rice).", "Ingredients: Chicken, Salt.", "Ingredients: Dried Mango.",
    # animal-fish-rows-1 (tests/test_animal_fish_rows_1.py, SYNTHETIC): 68 fish/seafood rows on the animal guard
    "Ingredients: Haddock.", "Ingredients: Dried Haddock.", "Ingredients: Haddock Powder.", "Ingredients: 100% Haddock Powder.", "Ingredients: Salted Haddock.", "Ingredients: Atlantic Salmon.", "Ingredients: Queen Crab.", "Ingredients: Snow Crab.",
    "Ingredients: Spot.", "Ingredients: Sea Scallop, Salt.", "Ingredients: Dried Blue Crab.", "Ingredients: Dried Sea Scallop.", "Ingredients: Dehydrated Blue Mussel.", "Ingredients: Dried Queen Crab, Salt.", "Ingredients: Dried Chilean Sea Bass.", "Ingredients: Haddock (Rice).", "Ingredients: Fried Haddock.", "Ingredients: Salmon.",
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
                 "declaration_only": u.declaration_only, "class_conflict": u.class_conflict, "declared": u.declared, "declared_roles": list(u.declared_roles), "role_notes": u.role_notes} for u in a.ins_mappings],
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
# direct-culinary-2: source-scoped forms, not a measured accuracy sample.
_DIRECT_CULINARY_NAMES = ["corn starch", "baking powder", "baking soda", "cornstarch", "maize starch"]
_DIRECT_CULINARY_FORMS = ["{t}", "{t} (salt)", "{t} (sugar)", "{t} (XQ9)", "{t} (Rice)",
    "{t} (Mango, Sugar)", "{t} (Milk)", "100% {t} (Rice)", "{t}, Maltodextrin",
    "Wheat Flour ({t})", "Refined Wheat Flour ({t})", "Corn Oil ({t})", "{t} (Corn Oil)",
    "{t} (no added salt)", "Modified {t}", "{t} (modified)", "{t} (pregelatinized)",
    "{t} flour", "{t} milk", "{t} oil"]
_DIRECT_CULINARY_TEXTS = ["Ingredients: " + form.format(t=t) + "."
    for t in _DIRECT_CULINARY_NAMES for form in _DIRECT_CULINARY_FORMS]
_DIRECT_CULINARY_TEXTS += [f"Ingredients: {t} ({origin})."
    for t in ["corn starch", "cornstarch", "maize starch"] for origin in ["corn", "maize"]]
for _texts in (CORPUS, PASTE):
    _texts.extend(t for t in _DIRECT_CULINARY_TEXTS if t not in _texts)

# scoped-nested-3: synthetic regression controls, not a measured accuracy sample.
_NESTED_3_TEXTS = [
    "Ingredients: Semolina (Sprouted Ragi).",
    "Ingredients: Suji (Sprouted Ragi).",
    "Ingredients: Rawa (Sprouted Ragi).",
    "Ingredients: Chickpea (Sprouted Ragi).",
    "Ingredients: Cashew Nuts (Sprouted Ragi).",
    "Ingredients: Pistachio Nuts (Sprouted Ragi).",
    "Ingredients: Sugar Apples (Sprouted Ragi).",
    "Ingredients: Milk (Sprouted Ragi).",
    "Ingredients: Cilantro (Sprouted Ragi).",
    "Ingredients: Baking Powder (Sprouted Ragi).",
    "Ingredients: Corn Oil (Sprouted Ragi).",
    "Ingredients: Semolina (Sprouted Jowar).",
    "Ingredients: Suji (Sprouted Jowar).",
    "Ingredients: Rawa (Sprouted Jowar).",
    "Ingredients: Chickpea (Sprouted Jowar).",
    "Ingredients: Cashew Nuts (Sprouted Jowar).",
    "Ingredients: Pistachio Nuts (Sprouted Jowar).",
    "Ingredients: Sugar Apples (Sprouted Jowar).",
    "Ingredients: Milk (Sprouted Jowar).",
    "Ingredients: Cilantro (Sprouted Jowar).",
    "Ingredients: Baking Powder (Sprouted Jowar).",
    "Ingredients: Corn Oil (Sprouted Jowar).",
    "Ingredients: Semolina (Sprouted Ragi), Maltodextrin.",
    "Ingredients: Suji (Sprouted Ragi), Maltodextrin.",
    "Ingredients: Cashew Nuts (Sprouted Ragi), Maltodextrin.",
    "Ingredients: Sugar Apples (Sprouted Ragi), Maltodextrin.",
    "Ingredients: Semolina (Sprouted Jowar), Maltodextrin.",
    "Ingredients: Suji (Sprouted Jowar), Maltodextrin.",
    "Ingredients: Cashew Nuts (Sprouted Jowar), Maltodextrin.",
    "Ingredients: Sugar Apples (Sprouted Jowar), Maltodextrin.",
    "Ingredients: Sugar Apples.",
    "Ingredients: Sugar Apple.",
    "Ingredients: Raw Sugar Apples.",
    "Ingredients: Sugar-apples (Rice).",
    "Ingredients: Sugar-apples (Milk).",
    "Ingredients: Sugar-apples (Cashew Nuts).",
    "Ingredients: Sugar-apples (Suji).",
    "Ingredients: 100% Sugar-apples powder.",
    "Ingredients: Salted Sugar Apples.",
    "Ingredients: Sugar-apples (salt).",
    "Ingredients: Sugar-apples (sugar).",
    "Ingredients: Sugar-apples (corn oil).",
    "Ingredients: Sugar-apples (no added salt, sugar).",
    "Ingredients: Sugar-apples (salt free, sugar).",
    "Ingredients: Sugar-apples (sugar apples, sugar).",
    "Ingredients: Sugar-apples powder.",
    "Ingredients: Sugar-apples (canned).",
    "Ingredients: Sugar-apples (XQ9).",
    "Ingredients: Sugar Applesauce.",
    "Ingredients: Sugar Apple Juice.",
    "Ingredients: Cashew Nuts (Rice).",
    "Ingredients: Chickpea (Rice).",
    "Ingredients: Sugar Apples (Rice).",
    "Ingredients: Cashew Nuts (Milk).",
    "Ingredients: Chickpea (Milk).",
    "Ingredients: Sugar Apples (Milk).",
    "Ingredients: Cashew Nuts (Cashew Nuts).",
    "Ingredients: Chickpea (Cashew Nuts).",
    "Ingredients: Sugar Apples (Cashew Nuts).",
    "Ingredients: Cashew Nuts (Vitamins).",
    "Ingredients: Chickpea (Vitamins).",
    "Ingredients: Sugar Apples (Vitamins).",
    "Ingredients: Cashew Nuts (Minerals).",
    "Ingredients: Chickpea (Minerals).",
    "Ingredients: Sugar Apples (Minerals).",
    "Ingredients: Cashew Nuts (Vitamins and Minerals).",
    "Ingredients: Chickpea (Vitamins and Minerals).",
    "Ingredients: Sugar Apples (Vitamins and Minerals).",
    "Ingredients: Milk (Starter Culture).",
    # cocoa-powder-24: the plain-food bracket condition on the new culinary row (Py/JS must agree on every form)
    "Ingredients: Cocoa Powder.",
    "Ingredients: Cocoa Powder (5%).",
    "Ingredients: Cocoa Powder (unsweetened).",
    "Ingredients: Cocoa Powder (Sugar).",
    "Ingredients: cocoa powder (alkalised).",
    "Ingredients: Milk, Cocoa Powder, Sugar.",
    "Ingredients: cocoa.",
    "Ingredients: cocoa solids.",
    # pool-a-24: the generalised plain-food condition on the four new culinary rows
    "Ingredients: Coconut Cream.",
    "Ingredients: Milk Cream (4%).",
    "Ingredients: Unsweetened Baking Chocolate.",
    "Ingredients: Gelatin Powder (unsweetened).",
    "Ingredients: Coconut Cream (Sugar).",
    "Ingredients: Milk Cream (sugar, flavour).",
    "Ingredients: baking chocolate.",
    "Ingredients: Milk, Milk Cream, Sugar."
]
for _texts in (CORPUS, PASTE):
    _texts.extend(t for t in _NESTED_3_TEXTS if t not in _texts)

# scoped-flour-4: synthetic regression controls, not a measured accuracy sample.
_FLOUR_4_TEXTS = [
    "Ingredients: whole wheat flour (sugar).",
    "Ingredients: refined wheat flour (sugar).",
    "Ingredients: rice flour (sugar).",
    "Ingredients: potato flour (sugar).",
    "Ingredients: besan (sugar).",
    "Ingredients: wheat flour (sugar).",
    "Ingredients: sorghum flour (sugar).",
    "Ingredients: soya flour (sugar).",
    "Ingredients: split pulse urad flour (sugar).",
    "Ingredients: amaranth flour (sugar).",
    "Ingredients: barley flour (sugar).",
    "Ingredients: buckwheat flour (sugar).",
    "Ingredients: cornmeal (sugar).",
    "Ingredients: millet flour (sugar).",
    "Ingredients: oat flour (sugar).",
    "Ingredients: quinoa flour (sugar).",
    "Ingredients: rye flour (sugar).",
    "Ingredients: semolina (sugar).",
    "Ingredients: spelt flour (sugar).",
    "Ingredients: whole wheat flour (sunflower oil).",
    "Ingredients: refined wheat flour (sunflower oil).",
    "Ingredients: rice flour (sunflower oil).",
    "Ingredients: potato flour (sunflower oil).",
    "Ingredients: besan (sunflower oil).",
    "Ingredients: wheat flour (sunflower oil).",
    "Ingredients: sorghum flour (sunflower oil).",
    "Ingredients: soya flour (sunflower oil).",
    "Ingredients: split pulse urad flour (sunflower oil).",
    "Ingredients: amaranth flour (sunflower oil).",
    "Ingredients: barley flour (sunflower oil).",
    "Ingredients: buckwheat flour (sunflower oil).",
    "Ingredients: cornmeal (sunflower oil).",
    "Ingredients: millet flour (sunflower oil).",
    "Ingredients: oat flour (sunflower oil).",
    "Ingredients: quinoa flour (sunflower oil).",
    "Ingredients: rye flour (sunflower oil).",
    "Ingredients: semolina (sunflower oil).",
    "Ingredients: spelt flour (sunflower oil).",
    "Ingredients: whole wheat flour (Mango, Sugar).",
    "Ingredients: refined wheat flour (Mango, Sugar).",
    "Ingredients: rice flour (Mango, Sugar).",
    "Ingredients: potato flour (Mango, Sugar).",
    "Ingredients: besan (Mango, Sugar).",
    "Ingredients: wheat flour (Mango, Sugar).",
    "Ingredients: sorghum flour (Mango, Sugar).",
    "Ingredients: soya flour (Mango, Sugar).",
    "Ingredients: split pulse urad flour (Mango, Sugar).",
    "Ingredients: amaranth flour (Mango, Sugar).",
    "Ingredients: barley flour (Mango, Sugar).",
    "Ingredients: buckwheat flour (Mango, Sugar).",
    "Ingredients: cornmeal (Mango, Sugar).",
    "Ingredients: millet flour (Mango, Sugar).",
    "Ingredients: oat flour (Mango, Sugar).",
    "Ingredients: quinoa flour (Mango, Sugar).",
    "Ingredients: rye flour (Mango, Sugar).",
    "Ingredients: semolina (Mango, Sugar).",
    "Ingredients: spelt flour (Mango, Sugar).",
    "Ingredients: whole wheat flour (canned).",
    "Ingredients: refined wheat flour (canned).",
    "Ingredients: rice flour (canned).",
    "Ingredients: potato flour (canned).",
    "Ingredients: besan (canned).",
    "Ingredients: wheat flour (canned).",
    "Ingredients: sorghum flour (canned).",
    "Ingredients: soya flour (canned).",
    "Ingredients: split pulse urad flour (canned).",
    "Ingredients: amaranth flour (canned).",
    "Ingredients: barley flour (canned).",
    "Ingredients: buckwheat flour (canned).",
    "Ingredients: cornmeal (canned).",
    "Ingredients: millet flour (canned).",
    "Ingredients: oat flour (canned).",
    "Ingredients: quinoa flour (canned).",
    "Ingredients: rye flour (canned).",
    "Ingredients: semolina (canned).",
    "Ingredients: spelt flour (canned).",
    "Ingredients: whole wheat flour (preserved).",
    "Ingredients: refined wheat flour (preserved).",
    "Ingredients: rice flour (preserved).",
    "Ingredients: potato flour (preserved).",
    "Ingredients: besan (preserved).",
    "Ingredients: wheat flour (preserved).",
    "Ingredients: sorghum flour (preserved).",
    "Ingredients: soya flour (preserved).",
    "Ingredients: split pulse urad flour (preserved).",
    "Ingredients: amaranth flour (preserved).",
    "Ingredients: barley flour (preserved).",
    "Ingredients: buckwheat flour (preserved).",
    "Ingredients: cornmeal (preserved).",
    "Ingredients: millet flour (preserved).",
    "Ingredients: oat flour (preserved).",
    "Ingredients: quinoa flour (preserved).",
    "Ingredients: rye flour (preserved).",
    "Ingredients: semolina (preserved).",
    "Ingredients: spelt flour (preserved).",
    "Ingredients: whole wheat flour (honey).",
    "Ingredients: refined wheat flour (honey).",
    "Ingredients: rice flour (honey).",
    "Ingredients: potato flour (honey).",
    "Ingredients: besan (honey).",
    "Ingredients: wheat flour (honey).",
    "Ingredients: sorghum flour (honey).",
    "Ingredients: soya flour (honey).",
    "Ingredients: split pulse urad flour (honey).",
    "Ingredients: amaranth flour (honey).",
    "Ingredients: barley flour (honey).",
    "Ingredients: buckwheat flour (honey).",
    "Ingredients: cornmeal (honey).",
    "Ingredients: millet flour (honey).",
    "Ingredients: oat flour (honey).",
    "Ingredients: quinoa flour (honey).",
    "Ingredients: rye flour (honey).",
    "Ingredients: semolina (honey).",
    "Ingredients: spelt flour (honey).",
    "Ingredients: whole wheat flour (brine).",
    "Ingredients: refined wheat flour (brine).",
    "Ingredients: rice flour (brine).",
    "Ingredients: potato flour (brine).",
    "Ingredients: besan (brine).",
    "Ingredients: wheat flour (brine).",
    "Ingredients: sorghum flour (brine).",
    "Ingredients: soya flour (brine).",
    "Ingredients: split pulse urad flour (brine).",
    "Ingredients: amaranth flour (brine).",
    "Ingredients: barley flour (brine).",
    "Ingredients: buckwheat flour (brine).",
    "Ingredients: cornmeal (brine).",
    "Ingredients: millet flour (brine).",
    "Ingredients: oat flour (brine).",
    "Ingredients: quinoa flour (brine).",
    "Ingredients: rye flour (brine).",
    "Ingredients: semolina (brine).",
    "Ingredients: spelt flour (brine).",
    "Ingredients: Salted refined wheat flour.",
    "Ingredients: Salted potato flour.",
    "Ingredients: Salted besan.",
    "Ingredients: Salted soya flour.",
    "Ingredients: Salted split pulse urad flour.",
    "Ingredients: refined wheat flour (salt).",
    "Ingredients: potato flour (salt).",
    "Ingredients: besan (salt).",
    "Ingredients: soya flour (salt).",
    "Ingredients: split pulse urad flour (salt).",
    "Ingredients: refined wheat flour (Sea Salt).",
    "Ingredients: potato flour (Sea Salt).",
    "Ingredients: besan (Sea Salt).",
    "Ingredients: soya flour (Sea Salt).",
    "Ingredients: split pulse urad flour (Sea Salt).",
    "Ingredients: whole wheat flour.",
    "Ingredients: refined wheat flour.",
    "Ingredients: rice flour.",
    "Ingredients: potato flour.",
    "Ingredients: besan.",
    "Ingredients: wheat flour.",
    "Ingredients: sorghum flour.",
    "Ingredients: soya flour.",
    "Ingredients: split pulse urad flour.",
    "Ingredients: amaranth flour.",
    "Ingredients: barley flour.",
    "Ingredients: buckwheat flour.",
    "Ingredients: cornmeal.",
    "Ingredients: millet flour.",
    "Ingredients: oat flour.",
    "Ingredients: quinoa flour.",
    "Ingredients: rye flour.",
    "Ingredients: semolina.",
    "Ingredients: spelt flour.",
    "Ingredients: Unsalted whole wheat flour.",
    "Ingredients: Unsalted refined wheat flour.",
    "Ingredients: Unsalted rice flour.",
    "Ingredients: Unsalted potato flour.",
    "Ingredients: Unsalted besan.",
    "Ingredients: Unsalted wheat flour.",
    "Ingredients: Unsalted sorghum flour.",
    "Ingredients: Unsalted soya flour.",
    "Ingredients: Unsalted split pulse urad flour.",
    "Ingredients: Unsalted amaranth flour.",
    "Ingredients: Unsalted barley flour.",
    "Ingredients: Unsalted buckwheat flour.",
    "Ingredients: Unsalted cornmeal.",
    "Ingredients: Unsalted millet flour.",
    "Ingredients: Unsalted oat flour.",
    "Ingredients: Unsalted quinoa flour.",
    "Ingredients: Unsalted rye flour.",
    "Ingredients: Unsalted semolina.",
    "Ingredients: Unsalted spelt flour.",
    "Ingredients: whole wheat flour (no added salt).",
    "Ingredients: refined wheat flour (no added salt).",
    "Ingredients: rice flour (no added salt).",
    "Ingredients: potato flour (no added salt).",
    "Ingredients: besan (no added salt).",
    "Ingredients: wheat flour (no added salt).",
    "Ingredients: sorghum flour (no added salt).",
    "Ingredients: soya flour (no added salt).",
    "Ingredients: split pulse urad flour (no added salt).",
    "Ingredients: amaranth flour (no added salt).",
    "Ingredients: barley flour (no added salt).",
    "Ingredients: buckwheat flour (no added salt).",
    "Ingredients: cornmeal (no added salt).",
    "Ingredients: millet flour (no added salt).",
    "Ingredients: oat flour (no added salt).",
    "Ingredients: quinoa flour (no added salt).",
    "Ingredients: rye flour (no added salt).",
    "Ingredients: semolina (no added salt).",
    "Ingredients: spelt flour (no added salt).",
    "Ingredients: whole wheat flour (no added sugar).",
    "Ingredients: refined wheat flour (no added sugar).",
    "Ingredients: rice flour (no added sugar).",
    "Ingredients: potato flour (no added sugar).",
    "Ingredients: besan (no added sugar).",
    "Ingredients: wheat flour (no added sugar).",
    "Ingredients: sorghum flour (no added sugar).",
    "Ingredients: soya flour (no added sugar).",
    "Ingredients: split pulse urad flour (no added sugar).",
    "Ingredients: amaranth flour (no added sugar).",
    "Ingredients: barley flour (no added sugar).",
    "Ingredients: buckwheat flour (no added sugar).",
    "Ingredients: cornmeal (no added sugar).",
    "Ingredients: millet flour (no added sugar).",
    "Ingredients: oat flour (no added sugar).",
    "Ingredients: quinoa flour (no added sugar).",
    "Ingredients: rye flour (no added sugar).",
    "Ingredients: semolina (no added sugar).",
    "Ingredients: spelt flour (no added sugar).",
    "Ingredients: whole wheat flour (Rice).",
    "Ingredients: refined wheat flour (Rice).",
    "Ingredients: rice flour (Rice).",
    "Ingredients: potato flour (Rice).",
    "Ingredients: besan (Rice).",
    "Ingredients: wheat flour (Rice).",
    "Ingredients: sorghum flour (Rice).",
    "Ingredients: soya flour (Rice).",
    "Ingredients: split pulse urad flour (Rice).",
    "Ingredients: amaranth flour (Rice).",
    "Ingredients: barley flour (Rice).",
    "Ingredients: buckwheat flour (Rice).",
    "Ingredients: cornmeal (Rice).",
    "Ingredients: millet flour (Rice).",
    "Ingredients: oat flour (Rice).",
    "Ingredients: quinoa flour (Rice).",
    "Ingredients: rye flour (Rice).",
    "Ingredients: semolina (Rice).",
    "Ingredients: spelt flour (Rice).",
    "Ingredients: whole wheat flour (Mango).",
    "Ingredients: refined wheat flour (Mango).",
    "Ingredients: rice flour (Mango).",
    "Ingredients: potato flour (Mango).",
    "Ingredients: besan (Mango).",
    "Ingredients: wheat flour (Mango).",
    "Ingredients: sorghum flour (Mango).",
    "Ingredients: soya flour (Mango).",
    "Ingredients: split pulse urad flour (Mango).",
    "Ingredients: amaranth flour (Mango).",
    "Ingredients: barley flour (Mango).",
    "Ingredients: buckwheat flour (Mango).",
    "Ingredients: cornmeal (Mango).",
    "Ingredients: millet flour (Mango).",
    "Ingredients: oat flour (Mango).",
    "Ingredients: quinoa flour (Mango).",
    "Ingredients: rye flour (Mango).",
    "Ingredients: semolina (Mango).",
    "Ingredients: spelt flour (Mango).",
    "Ingredients: whole wheat flour (Milk).",
    "Ingredients: refined wheat flour (Milk).",
    "Ingredients: rice flour (Milk).",
    "Ingredients: potato flour (Milk).",
    "Ingredients: besan (Milk).",
    "Ingredients: wheat flour (Milk).",
    "Ingredients: sorghum flour (Milk).",
    "Ingredients: soya flour (Milk).",
    "Ingredients: split pulse urad flour (Milk).",
    "Ingredients: amaranth flour (Milk).",
    "Ingredients: barley flour (Milk).",
    "Ingredients: buckwheat flour (Milk).",
    "Ingredients: cornmeal (Milk).",
    "Ingredients: millet flour (Milk).",
    "Ingredients: oat flour (Milk).",
    "Ingredients: quinoa flour (Milk).",
    "Ingredients: rye flour (Milk).",
    "Ingredients: semolina (Milk).",
    "Ingredients: spelt flour (Milk).",
    "Ingredients: whole wheat flour (Sugar Apples).",
    "Ingredients: refined wheat flour (Sugar Apples).",
    "Ingredients: rice flour (Sugar Apples).",
    "Ingredients: potato flour (Sugar Apples).",
    "Ingredients: besan (Sugar Apples).",
    "Ingredients: wheat flour (Sugar Apples).",
    "Ingredients: sorghum flour (Sugar Apples).",
    "Ingredients: soya flour (Sugar Apples).",
    "Ingredients: split pulse urad flour (Sugar Apples).",
    "Ingredients: amaranth flour (Sugar Apples).",
    "Ingredients: barley flour (Sugar Apples).",
    "Ingredients: buckwheat flour (Sugar Apples).",
    "Ingredients: cornmeal (Sugar Apples).",
    "Ingredients: millet flour (Sugar Apples).",
    "Ingredients: oat flour (Sugar Apples).",
    "Ingredients: quinoa flour (Sugar Apples).",
    "Ingredients: rye flour (Sugar Apples).",
    "Ingredients: semolina (Sugar Apples).",
    "Ingredients: spelt flour (Sugar Apples).",
    "Ingredients: whole wheat flour (Vitamins, Minerals).",
    "Ingredients: refined wheat flour (Vitamins, Minerals).",
    "Ingredients: rice flour (Vitamins, Minerals).",
    "Ingredients: potato flour (Vitamins, Minerals).",
    "Ingredients: besan (Vitamins, Minerals).",
    "Ingredients: wheat flour (Vitamins, Minerals).",
    "Ingredients: sorghum flour (Vitamins, Minerals).",
    "Ingredients: soya flour (Vitamins, Minerals).",
    "Ingredients: split pulse urad flour (Vitamins, Minerals).",
    "Ingredients: amaranth flour (Vitamins, Minerals).",
    "Ingredients: barley flour (Vitamins, Minerals).",
    "Ingredients: buckwheat flour (Vitamins, Minerals).",
    "Ingredients: cornmeal (Vitamins, Minerals).",
    "Ingredients: millet flour (Vitamins, Minerals).",
    "Ingredients: oat flour (Vitamins, Minerals).",
    "Ingredients: quinoa flour (Vitamins, Minerals).",
    "Ingredients: rye flour (Vitamins, Minerals).",
    "Ingredients: semolina (Vitamins, Minerals).",
    "Ingredients: spelt flour (Vitamins, Minerals).",
    "Ingredients: whole wheat flour powder.",
    "Ingredients: refined wheat flour powder.",
    "Ingredients: rice flour powder.",
    "Ingredients: potato flour powder.",
    "Ingredients: besan powder.",
    "Ingredients: wheat flour powder.",
    "Ingredients: sorghum flour powder.",
    "Ingredients: soya flour powder.",
    "Ingredients: amaranth flour powder.",
    "Ingredients: barley flour powder.",
    "Ingredients: buckwheat flour powder.",
    "Ingredients: cornmeal powder.",
    "Ingredients: millet flour powder.",
    "Ingredients: oat flour powder.",
    "Ingredients: quinoa flour powder.",
    "Ingredients: rye flour powder.",
    "Ingredients: semolina powder.",
    "Ingredients: spelt flour powder.",
    "Ingredients: 100% whole wheat flour powder.",
    "Ingredients: 100% refined wheat flour powder.",
    "Ingredients: 100% rice flour powder.",
    "Ingredients: 100% potato flour powder.",
    "Ingredients: 100% besan powder.",
    "Ingredients: 100% wheat flour powder.",
    "Ingredients: 100% sorghum flour powder.",
    "Ingredients: 100% soya flour powder.",
    "Ingredients: 100% amaranth flour powder.",
    "Ingredients: 100% barley flour powder.",
    "Ingredients: 100% buckwheat flour powder.",
    "Ingredients: 100% cornmeal powder.",
    "Ingredients: 100% millet flour powder.",
    "Ingredients: 100% oat flour powder.",
    "Ingredients: 100% quinoa flour powder.",
    "Ingredients: 100% rye flour powder.",
    "Ingredients: 100% semolina powder.",
    "Ingredients: 100% spelt flour powder.",
    "Ingredients: split pulse urad flour powder.",
    "Ingredients: 100% split pulse urad flour powder.",
    "Ingredients: Salted whole wheat flour.",
    "Ingredients: Salted rice flour.",
    "Ingredients: Salted wheat flour.",
    "Ingredients: Salted sorghum flour.",
    "Ingredients: Salted amaranth flour.",
    "Ingredients: Salted barley flour.",
    "Ingredients: Salted buckwheat flour.",
    "Ingredients: Salted cornmeal.",
    "Ingredients: Salted millet flour.",
    "Ingredients: Salted oat flour.",
    "Ingredients: Salted quinoa flour.",
    "Ingredients: Salted rye flour.",
    "Ingredients: Salted semolina.",
    "Ingredients: Salted spelt flour.",
    "Ingredients: whole wheat flour (salt).",
    "Ingredients: rice flour (salt).",
    "Ingredients: wheat flour (salt).",
    "Ingredients: sorghum flour (salt).",
    "Ingredients: amaranth flour (salt).",
    "Ingredients: barley flour (salt).",
    "Ingredients: buckwheat flour (salt).",
    "Ingredients: cornmeal (salt).",
    "Ingredients: millet flour (salt).",
    "Ingredients: oat flour (salt).",
    "Ingredients: quinoa flour (salt).",
    "Ingredients: rye flour (salt).",
    "Ingredients: semolina (salt).",
    "Ingredients: spelt flour (salt).",
    "Ingredients: whole wheat flour (Sea Salt).",
    "Ingredients: rice flour (Sea Salt).",
    "Ingredients: wheat flour (Sea Salt).",
    "Ingredients: sorghum flour (Sea Salt).",
    "Ingredients: amaranth flour (Sea Salt).",
    "Ingredients: barley flour (Sea Salt).",
    "Ingredients: buckwheat flour (Sea Salt).",
    "Ingredients: cornmeal (Sea Salt).",
    "Ingredients: millet flour (Sea Salt).",
    "Ingredients: oat flour (Sea Salt).",
    "Ingredients: quinoa flour (Sea Salt).",
    "Ingredients: rye flour (Sea Salt).",
    "Ingredients: semolina (Sea Salt).",
    "Ingredients: spelt flour (Sea Salt).",
    "Ingredients: whole wheat flour (Rice, Salt).",
    "Ingredients: rice flour (Rice, Salt).",
    "Ingredients: wheat flour (Rice, Salt).",
    "Ingredients: sorghum flour (Rice, Salt).",
    "Ingredients: amaranth flour (Rice, Salt).",
    "Ingredients: barley flour (Rice, Salt).",
    "Ingredients: buckwheat flour (Rice, Salt).",
    "Ingredients: cornmeal (Rice, Salt).",
    "Ingredients: millet flour (Rice, Salt).",
    "Ingredients: oat flour (Rice, Salt).",
    "Ingredients: quinoa flour (Rice, Salt).",
    "Ingredients: rye flour (Rice, Salt).",
    "Ingredients: semolina (Rice, Salt).",
    "Ingredients: spelt flour (Rice, Salt).",
    "Ingredients: whole wheat flour (Salt, Sugar).",
    "Ingredients: rice flour (Salt, Sugar).",
    "Ingredients: wheat flour (Salt, Sugar).",
    "Ingredients: sorghum flour (Salt, Sugar).",
    "Ingredients: amaranth flour (Salt, Sugar).",
    "Ingredients: barley flour (Salt, Sugar).",
    "Ingredients: buckwheat flour (Salt, Sugar).",
    "Ingredients: cornmeal (Salt, Sugar).",
    "Ingredients: millet flour (Salt, Sugar).",
    "Ingredients: oat flour (Salt, Sugar).",
    "Ingredients: quinoa flour (Salt, Sugar).",
    "Ingredients: rye flour (Salt, Sugar).",
    "Ingredients: semolina (Salt, Sugar).",
    "Ingredients: spelt flour (Salt, Sugar).",
    "Ingredients: whole wheat flour (Rice, Salt, Sugar).",
    "Ingredients: rice flour (Rice, Salt, Sugar).",
    "Ingredients: wheat flour (Rice, Salt, Sugar).",
    "Ingredients: sorghum flour (Rice, Salt, Sugar).",
    "Ingredients: amaranth flour (Rice, Salt, Sugar).",
    "Ingredients: barley flour (Rice, Salt, Sugar).",
    "Ingredients: buckwheat flour (Rice, Salt, Sugar).",
    "Ingredients: cornmeal (Rice, Salt, Sugar).",
    "Ingredients: millet flour (Rice, Salt, Sugar).",
    "Ingredients: oat flour (Rice, Salt, Sugar).",
    "Ingredients: quinoa flour (Rice, Salt, Sugar).",
    "Ingredients: rye flour (Rice, Salt, Sugar).",
    "Ingredients: semolina (Rice, Salt, Sugar).",
    "Ingredients: spelt flour (Rice, Salt, Sugar).",
    "Ingredients: whole wheat flour (XQ9).",
    "Ingredients: refined wheat flour (XQ9).",
    "Ingredients: rice flour (XQ9).",
    "Ingredients: potato flour (XQ9).",
    "Ingredients: besan (XQ9).",
    "Ingredients: wheat flour (XQ9).",
    "Ingredients: sorghum flour (XQ9).",
    "Ingredients: soya flour (XQ9).",
    "Ingredients: split pulse urad flour (XQ9).",
    "Ingredients: amaranth flour (XQ9).",
    "Ingredients: barley flour (XQ9).",
    "Ingredients: buckwheat flour (XQ9).",
    "Ingredients: cornmeal (XQ9).",
    "Ingredients: millet flour (XQ9).",
    "Ingredients: oat flour (XQ9).",
    "Ingredients: quinoa flour (XQ9).",
    "Ingredients: rye flour (XQ9).",
    "Ingredients: semolina (XQ9).",
    "Ingredients: spelt flour (XQ9).",
    "Ingredients: whole wheat flour (Sugar, XQ9).",
    "Ingredients: refined wheat flour (Sugar, XQ9).",
    "Ingredients: rice flour (Sugar, XQ9).",
    "Ingredients: potato flour (Sugar, XQ9).",
    "Ingredients: besan (Sugar, XQ9).",
    "Ingredients: wheat flour (Sugar, XQ9).",
    "Ingredients: sorghum flour (Sugar, XQ9).",
    "Ingredients: soya flour (Sugar, XQ9).",
    "Ingredients: split pulse urad flour (Sugar, XQ9).",
    "Ingredients: amaranth flour (Sugar, XQ9).",
    "Ingredients: barley flour (Sugar, XQ9).",
    "Ingredients: buckwheat flour (Sugar, XQ9).",
    "Ingredients: cornmeal (Sugar, XQ9).",
    "Ingredients: millet flour (Sugar, XQ9).",
    "Ingredients: oat flour (Sugar, XQ9).",
    "Ingredients: quinoa flour (Sugar, XQ9).",
    "Ingredients: rye flour (Sugar, XQ9).",
    "Ingredients: semolina (Sugar, XQ9).",
    "Ingredients: spelt flour (Sugar, XQ9).",
    "Ingredients: whole wheat flour (Sprouted Ragi).",
    "Ingredients: refined wheat flour (Sprouted Ragi).",
    "Ingredients: rice flour (Sprouted Ragi).",
    "Ingredients: potato flour (Sprouted Ragi).",
    "Ingredients: besan (Sprouted Ragi).",
    "Ingredients: wheat flour (Sprouted Ragi).",
    "Ingredients: sorghum flour (Sprouted Ragi).",
    "Ingredients: soya flour (Sprouted Ragi).",
    "Ingredients: split pulse urad flour (Sprouted Ragi).",
    "Ingredients: amaranth flour (Sprouted Ragi).",
    "Ingredients: barley flour (Sprouted Ragi).",
    "Ingredients: buckwheat flour (Sprouted Ragi).",
    "Ingredients: cornmeal (Sprouted Ragi).",
    "Ingredients: millet flour (Sprouted Ragi).",
    "Ingredients: oat flour (Sprouted Ragi).",
    "Ingredients: quinoa flour (Sprouted Ragi).",
    "Ingredients: rye flour (Sprouted Ragi).",
    "Ingredients: semolina (Sprouted Ragi).",
    "Ingredients: spelt flour (Sprouted Ragi).",
    "Ingredients: whole wheat flour (Corn Starch).",
    "Ingredients: refined wheat flour (Corn Starch).",
    "Ingredients: rice flour (Corn Starch).",
    "Ingredients: potato flour (Corn Starch).",
    "Ingredients: besan (Corn Starch).",
    "Ingredients: wheat flour (Corn Starch).",
    "Ingredients: sorghum flour (Corn Starch).",
    "Ingredients: soya flour (Corn Starch).",
    "Ingredients: split pulse urad flour (Corn Starch).",
    "Ingredients: amaranth flour (Corn Starch).",
    "Ingredients: barley flour (Corn Starch).",
    "Ingredients: buckwheat flour (Corn Starch).",
    "Ingredients: cornmeal (Corn Starch).",
    "Ingredients: millet flour (Corn Starch).",
    "Ingredients: oat flour (Corn Starch).",
    "Ingredients: quinoa flour (Corn Starch).",
    "Ingredients: rye flour (Corn Starch).",
    "Ingredients: semolina (Corn Starch).",
    "Ingredients: spelt flour (Corn Starch).",
    "Ingredients: whole wheat flour (Salt, Corn Starch).",
    "Ingredients: refined wheat flour (Salt, Corn Starch).",
    "Ingredients: rice flour (Salt, Corn Starch).",
    "Ingredients: potato flour (Salt, Corn Starch).",
    "Ingredients: besan (Salt, Corn Starch).",
    "Ingredients: wheat flour (Salt, Corn Starch).",
    "Ingredients: sorghum flour (Salt, Corn Starch).",
    "Ingredients: soya flour (Salt, Corn Starch).",
    "Ingredients: split pulse urad flour (Salt, Corn Starch).",
    "Ingredients: amaranth flour (Salt, Corn Starch).",
    "Ingredients: barley flour (Salt, Corn Starch).",
    "Ingredients: buckwheat flour (Salt, Corn Starch).",
    "Ingredients: cornmeal (Salt, Corn Starch).",
    "Ingredients: millet flour (Salt, Corn Starch).",
    "Ingredients: oat flour (Salt, Corn Starch).",
    "Ingredients: quinoa flour (Salt, Corn Starch).",
    "Ingredients: rye flour (Salt, Corn Starch).",
    "Ingredients: semolina (Salt, Corn Starch).",
    "Ingredients: spelt flour (Salt, Corn Starch).",
    "Ingredients: whole wheat flour, Salt.",
    "Ingredients: refined wheat flour, Salt.",
    "Ingredients: rice flour, Salt.",
    "Ingredients: potato flour, Salt.",
    "Ingredients: besan, Salt.",
    "Ingredients: wheat flour, Salt.",
    "Ingredients: sorghum flour, Salt.",
    "Ingredients: soya flour, Salt.",
    "Ingredients: split pulse urad flour, Salt.",
    "Ingredients: amaranth flour, Salt.",
    "Ingredients: barley flour, Salt.",
    "Ingredients: buckwheat flour, Salt.",
    "Ingredients: cornmeal, Salt.",
    "Ingredients: millet flour, Salt.",
    "Ingredients: oat flour, Salt.",
    "Ingredients: quinoa flour, Salt.",
    "Ingredients: rye flour, Salt.",
    "Ingredients: semolina, Salt.",
    "Ingredients: spelt flour, Salt.",
    "Ingredients: whole wheat flour, Sugar.",
    "Ingredients: refined wheat flour, Sugar.",
    "Ingredients: rice flour, Sugar.",
    "Ingredients: potato flour, Sugar.",
    "Ingredients: besan, Sugar.",
    "Ingredients: wheat flour, Sugar.",
    "Ingredients: sorghum flour, Sugar.",
    "Ingredients: soya flour, Sugar.",
    "Ingredients: split pulse urad flour, Sugar.",
    "Ingredients: amaranth flour, Sugar.",
    "Ingredients: barley flour, Sugar.",
    "Ingredients: buckwheat flour, Sugar.",
    "Ingredients: cornmeal, Sugar.",
    "Ingredients: millet flour, Sugar.",
    "Ingredients: oat flour, Sugar.",
    "Ingredients: quinoa flour, Sugar.",
    "Ingredients: rye flour, Sugar.",
    "Ingredients: semolina, Sugar.",
    "Ingredients: spelt flour, Sugar.",
    "Ingredients: whole wheat flour (sugar), Maltodextrin.",
    "Ingredients: refined wheat flour (sugar), Maltodextrin.",
    "Ingredients: rice flour (sugar), Maltodextrin.",
    "Ingredients: potato flour (sugar), Maltodextrin.",
    "Ingredients: besan (sugar), Maltodextrin.",
    "Ingredients: wheat flour (sugar), Maltodextrin.",
    "Ingredients: sorghum flour (sugar), Maltodextrin.",
    "Ingredients: soya flour (sugar), Maltodextrin.",
    "Ingredients: split pulse urad flour (sugar), Maltodextrin.",
    "Ingredients: amaranth flour (sugar), Maltodextrin.",
    "Ingredients: barley flour (sugar), Maltodextrin.",
    "Ingredients: buckwheat flour (sugar), Maltodextrin.",
    "Ingredients: cornmeal (sugar), Maltodextrin.",
    "Ingredients: millet flour (sugar), Maltodextrin.",
    "Ingredients: oat flour (sugar), Maltodextrin.",
    "Ingredients: quinoa flour (sugar), Maltodextrin.",
    "Ingredients: rye flour (sugar), Maltodextrin.",
    "Ingredients: semolina (sugar), Maltodextrin.",
    "Ingredients: spelt flour (sugar), Maltodextrin.",
    "Ingredients: whole wheat flour (canned), Maltodextrin.",
    "Ingredients: refined wheat flour (canned), Maltodextrin.",
    "Ingredients: rice flour (canned), Maltodextrin.",
    "Ingredients: potato flour (canned), Maltodextrin.",
    "Ingredients: besan (canned), Maltodextrin.",
    "Ingredients: wheat flour (canned), Maltodextrin.",
    "Ingredients: sorghum flour (canned), Maltodextrin.",
    "Ingredients: soya flour (canned), Maltodextrin.",
    "Ingredients: split pulse urad flour (canned), Maltodextrin.",
    "Ingredients: amaranth flour (canned), Maltodextrin.",
    "Ingredients: barley flour (canned), Maltodextrin.",
    "Ingredients: buckwheat flour (canned), Maltodextrin.",
    "Ingredients: cornmeal (canned), Maltodextrin.",
    "Ingredients: millet flour (canned), Maltodextrin.",
    "Ingredients: oat flour (canned), Maltodextrin.",
    "Ingredients: quinoa flour (canned), Maltodextrin.",
    "Ingredients: rye flour (canned), Maltodextrin.",
    "Ingredients: semolina (canned), Maltodextrin.",
    "Ingredients: spelt flour (canned), Maltodextrin.",
    "Ingredients: Maida.",
    "Ingredients: Cashew.",
    "Ingredients: Pistachio.",
    "Ingredients: Garbanzo Bean."
]
for _texts in (CORPUS, PASTE):
    _texts.extend(t for t in _FLOUR_4_TEXTS if t not in _texts)

# scoped-powder-5: synthetic name/form controls, not a measured accuracy sample.
_POWDER_5_TEXTS = ["Ingredients: almonds powder.","Ingredients: pumpkin seeds powder.","Ingredients: flax seeds powder.","Ingredients: acorns powder.","Ingredients: beechnuts powder.","Ingredients: brazil nuts powder.","Ingredients: butternuts powder.","Ingredients: cashew nuts powder.","Ingredients: chestnuts powder.","Ingredients: chia seeds powder.","Ingredients: ginkgo nuts powder.","Ingredients: hazelnuts powder.","Ingredients: hickory nuts powder.","Ingredients: macadamia nuts powder.","Ingredients: pecans powder.","Ingredients: pili nuts powder.","Ingredients: pine nuts powder.","Ingredients: pistachio nuts powder.","Ingredients: safflower seeds powder.","Ingredients: sesame seeds powder.","Ingredients: sunflower seeds powder.","Ingredients: walnuts powder.","Ingredients: watermelon seeds powder.","Ingredients: almonds (powder).","Ingredients: pumpkin seeds (powder).","Ingredients: flax seeds (powder).","Ingredients: acorns (powder).","Ingredients: beechnuts (powder).","Ingredients: brazil nuts (powder).","Ingredients: butternuts (powder).","Ingredients: cashew nuts (powder).","Ingredients: chestnuts (powder).","Ingredients: chia seeds (powder).","Ingredients: ginkgo nuts (powder).","Ingredients: hazelnuts (powder).","Ingredients: hickory nuts (powder).","Ingredients: macadamia nuts (powder).","Ingredients: pecans (powder).","Ingredients: pili nuts (powder).","Ingredients: pine nuts (powder).","Ingredients: pistachio nuts (powder).","Ingredients: safflower seeds (powder).","Ingredients: sesame seeds (powder).","Ingredients: sunflower seeds (powder).","Ingredients: walnuts (powder).","Ingredients: watermelon seeds (powder).","Ingredients: Whole almonds (Banana Powder).","Ingredients: Whole pumpkin seeds (Banana Powder).","Ingredients: Whole flax seeds (Banana Powder).","Ingredients: Whole acorns (Banana Powder).","Ingredients: Whole beechnuts (Banana Powder).","Ingredients: Whole brazil nuts (Banana Powder).","Ingredients: Whole butternuts (Banana Powder).","Ingredients: Whole cashew nuts (Banana Powder).","Ingredients: Whole chestnuts (Banana Powder).","Ingredients: Whole chia seeds (Banana Powder).","Ingredients: Whole ginkgo nuts (Banana Powder).","Ingredients: Whole hazelnuts (Banana Powder).","Ingredients: Whole hickory nuts (Banana Powder).","Ingredients: Whole macadamia nuts (Banana Powder).","Ingredients: Whole pecans (Banana Powder).","Ingredients: Whole pili nuts (Banana Powder).","Ingredients: Whole pine nuts (Banana Powder).","Ingredients: Whole pistachio nuts (Banana Powder).","Ingredients: Whole safflower seeds (Banana Powder).","Ingredients: Whole sesame seeds (Banana Powder).","Ingredients: Whole sunflower seeds (Banana Powder).","Ingredients: Whole walnuts (Banana Powder).","Ingredients: Whole watermelon seeds (Banana Powder).","Ingredients: 100% almonds (Banana Powder).","Ingredients: 100% pumpkin seeds (Banana Powder).","Ingredients: 100% flax seeds (Banana Powder).","Ingredients: 100% acorns (Banana Powder).","Ingredients: 100% beechnuts (Banana Powder).","Ingredients: 100% brazil nuts (Banana Powder).","Ingredients: 100% butternuts (Banana Powder).","Ingredients: 100% cashew nuts (Banana Powder).","Ingredients: 100% chestnuts (Banana Powder).","Ingredients: 100% chia seeds (Banana Powder).","Ingredients: 100% ginkgo nuts (Banana Powder).","Ingredients: 100% hazelnuts (Banana Powder).","Ingredients: 100% hickory nuts (Banana Powder).","Ingredients: 100% macadamia nuts (Banana Powder).","Ingredients: 100% pecans (Banana Powder).","Ingredients: 100% pili nuts (Banana Powder).","Ingredients: 100% pine nuts (Banana Powder).","Ingredients: 100% pistachio nuts (Banana Powder).","Ingredients: 100% safflower seeds (Banana Powder).","Ingredients: 100% sesame seeds (Banana Powder).","Ingredients: 100% sunflower seeds (Banana Powder).","Ingredients: 100% walnuts (Banana Powder).","Ingredients: 100% watermelon seeds (Banana Powder).","Ingredients: almonds (Banana Powder, 100% Rice).","Ingredients: pumpkin seeds (Banana Powder, 100% Rice).","Ingredients: flax seeds (Banana Powder, 100% Rice).","Ingredients: acorns (Banana Powder, 100% Rice).","Ingredients: beechnuts (Banana Powder, 100% Rice).","Ingredients: brazil nuts (Banana Powder, 100% Rice).","Ingredients: butternuts (Banana Powder, 100% Rice).","Ingredients: cashew nuts (Banana Powder, 100% Rice).","Ingredients: chestnuts (Banana Powder, 100% Rice).","Ingredients: chia seeds (Banana Powder, 100% Rice).","Ingredients: ginkgo nuts (Banana Powder, 100% Rice).","Ingredients: hazelnuts (Banana Powder, 100% Rice).","Ingredients: hickory nuts (Banana Powder, 100% Rice).","Ingredients: macadamia nuts (Banana Powder, 100% Rice).","Ingredients: pecans (Banana Powder, 100% Rice).","Ingredients: pili nuts (Banana Powder, 100% Rice).","Ingredients: pine nuts (Banana Powder, 100% Rice).","Ingredients: pistachio nuts (Banana Powder, 100% Rice).","Ingredients: safflower seeds (Banana Powder, 100% Rice).","Ingredients: sesame seeds (Banana Powder, 100% Rice).","Ingredients: sunflower seeds (Banana Powder, 100% Rice).","Ingredients: walnuts (Banana Powder, 100% Rice).","Ingredients: watermelon seeds (Banana Powder, 100% Rice).","Ingredients: 100% almonds powder.","Ingredients: 100% pumpkin seeds powder.","Ingredients: 100% flax seeds powder.","Ingredients: 100% acorns powder.","Ingredients: 100% beechnuts powder.","Ingredients: 100% brazil nuts powder.","Ingredients: 100% butternuts powder.","Ingredients: 100% cashew nuts powder.","Ingredients: 100% chestnuts powder.","Ingredients: 100% chia seeds powder.","Ingredients: 100% ginkgo nuts powder.","Ingredients: 100% hazelnuts powder.","Ingredients: 100% hickory nuts powder.","Ingredients: 100% macadamia nuts powder.","Ingredients: 100% pecans powder.","Ingredients: 100% pili nuts powder.","Ingredients: 100% pine nuts powder.","Ingredients: 100% pistachio nuts powder.","Ingredients: 100% safflower seeds powder.","Ingredients: 100% sesame seeds powder.","Ingredients: 100% sunflower seeds powder.","Ingredients: 100% walnuts powder.","Ingredients: 100% watermelon seeds powder.","Ingredients: Whole almonds powder.","Ingredients: Whole pumpkin seeds powder.","Ingredients: Whole flax seeds powder.","Ingredients: Whole acorns powder.","Ingredients: Whole beechnuts powder.","Ingredients: Whole brazil nuts powder.","Ingredients: Whole butternuts powder.","Ingredients: Whole cashew nuts powder.","Ingredients: Whole chestnuts powder.","Ingredients: Whole chia seeds powder.","Ingredients: Whole ginkgo nuts powder.","Ingredients: Whole hazelnuts powder.","Ingredients: Whole hickory nuts powder.","Ingredients: Whole macadamia nuts powder.","Ingredients: Whole pecans powder.","Ingredients: Whole pili nuts powder.","Ingredients: Whole pine nuts powder.","Ingredients: Whole pistachio nuts powder.","Ingredients: Whole safflower seeds powder.","Ingredients: Whole sesame seeds powder.","Ingredients: Whole sunflower seeds powder.","Ingredients: Whole walnuts powder.","Ingredients: Whole watermelon seeds powder.","Ingredients: almonds (100% powder).","Ingredients: pumpkin seeds (100% powder).","Ingredients: flax seeds (100% powder).","Ingredients: acorns (100% powder).","Ingredients: beechnuts (100% powder).","Ingredients: brazil nuts (100% powder).","Ingredients: butternuts (100% powder).","Ingredients: cashew nuts (100% powder).","Ingredients: chestnuts (100% powder).","Ingredients: chia seeds (100% powder).","Ingredients: ginkgo nuts (100% powder).","Ingredients: hazelnuts (100% powder).","Ingredients: hickory nuts (100% powder).","Ingredients: macadamia nuts (100% powder).","Ingredients: pecans (100% powder).","Ingredients: pili nuts (100% powder).","Ingredients: pine nuts (100% powder).","Ingredients: pistachio nuts (100% powder).","Ingredients: safflower seeds (100% powder).","Ingredients: sesame seeds (100% powder).","Ingredients: sunflower seeds (100% powder).","Ingredients: walnuts (100% powder).","Ingredients: watermelon seeds (100% powder).","Ingredients: almonds (Milk Powder).","Ingredients: pumpkin seeds (Milk Powder).","Ingredients: flax seeds (Milk Powder).","Ingredients: acorns (Milk Powder).","Ingredients: beechnuts (Milk Powder).","Ingredients: brazil nuts (Milk Powder).","Ingredients: butternuts (Milk Powder).","Ingredients: cashew nuts (Milk Powder).","Ingredients: chestnuts (Milk Powder).","Ingredients: chia seeds (Milk Powder).","Ingredients: ginkgo nuts (Milk Powder).","Ingredients: hazelnuts (Milk Powder).","Ingredients: hickory nuts (Milk Powder).","Ingredients: macadamia nuts (Milk Powder).","Ingredients: pecans (Milk Powder).","Ingredients: pili nuts (Milk Powder).","Ingredients: pine nuts (Milk Powder).","Ingredients: pistachio nuts (Milk Powder).","Ingredients: safflower seeds (Milk Powder).","Ingredients: sesame seeds (Milk Powder).","Ingredients: sunflower seeds (Milk Powder).","Ingredients: walnuts (Milk Powder).","Ingredients: watermelon seeds (Milk Powder).","Ingredients: almonds (100% Banana Powder).","Ingredients: pumpkin seeds (100% Banana Powder).","Ingredients: flax seeds (100% Banana Powder).","Ingredients: acorns (100% Banana Powder).","Ingredients: beechnuts (100% Banana Powder).","Ingredients: brazil nuts (100% Banana Powder).","Ingredients: butternuts (100% Banana Powder).","Ingredients: cashew nuts (100% Banana Powder).","Ingredients: chestnuts (100% Banana Powder).","Ingredients: chia seeds (100% Banana Powder).","Ingredients: ginkgo nuts (100% Banana Powder).","Ingredients: hazelnuts (100% Banana Powder).","Ingredients: hickory nuts (100% Banana Powder).","Ingredients: macadamia nuts (100% Banana Powder).","Ingredients: pecans (100% Banana Powder).","Ingredients: pili nuts (100% Banana Powder).","Ingredients: pine nuts (100% Banana Powder).","Ingredients: pistachio nuts (100% Banana Powder).","Ingredients: safflower seeds (100% Banana Powder).","Ingredients: sesame seeds (100% Banana Powder).","Ingredients: sunflower seeds (100% Banana Powder).","Ingredients: walnuts (100% Banana Powder).","Ingredients: watermelon seeds (100% Banana Powder).","Ingredients: almonds (Banana Powder (100%)).","Ingredients: pumpkin seeds (Banana Powder (100%)).","Ingredients: flax seeds (Banana Powder (100%)).","Ingredients: acorns (Banana Powder (100%)).","Ingredients: beechnuts (Banana Powder (100%)).","Ingredients: brazil nuts (Banana Powder (100%)).","Ingredients: butternuts (Banana Powder (100%)).","Ingredients: cashew nuts (Banana Powder (100%)).","Ingredients: chestnuts (Banana Powder (100%)).","Ingredients: chia seeds (Banana Powder (100%)).","Ingredients: ginkgo nuts (Banana Powder (100%)).","Ingredients: hazelnuts (Banana Powder (100%)).","Ingredients: hickory nuts (Banana Powder (100%)).","Ingredients: macadamia nuts (Banana Powder (100%)).","Ingredients: pecans (Banana Powder (100%)).","Ingredients: pili nuts (Banana Powder (100%)).","Ingredients: pine nuts (Banana Powder (100%)).","Ingredients: pistachio nuts (Banana Powder (100%)).","Ingredients: safflower seeds (Banana Powder (100%)).","Ingredients: sesame seeds (Banana Powder (100%)).","Ingredients: sunflower seeds (Banana Powder (100%)).","Ingredients: walnuts (Banana Powder (100%)).","Ingredients: watermelon seeds (Banana Powder (100%)).","Ingredients: almonds (Rice).","Ingredients: pumpkin seeds (Rice).","Ingredients: flax seeds (Rice).","Ingredients: acorns (Rice).","Ingredients: beechnuts (Rice).","Ingredients: brazil nuts (Rice).","Ingredients: butternuts (Rice).","Ingredients: cashew nuts (Rice).","Ingredients: chestnuts (Rice).","Ingredients: chia seeds (Rice).","Ingredients: ginkgo nuts (Rice).","Ingredients: hazelnuts (Rice).","Ingredients: hickory nuts (Rice).","Ingredients: macadamia nuts (Rice).","Ingredients: pecans (Rice).","Ingredients: pili nuts (Rice).","Ingredients: pine nuts (Rice).","Ingredients: pistachio nuts (Rice).","Ingredients: safflower seeds (Rice).","Ingredients: sesame seeds (Rice).","Ingredients: sunflower seeds (Rice).","Ingredients: walnuts (Rice).","Ingredients: watermelon seeds (Rice).","Ingredients: almonds (Vitamins, Minerals).","Ingredients: pumpkin seeds (Vitamins, Minerals).","Ingredients: flax seeds (Vitamins, Minerals).","Ingredients: acorns (Vitamins, Minerals).","Ingredients: beechnuts (Vitamins, Minerals).","Ingredients: brazil nuts (Vitamins, Minerals).","Ingredients: butternuts (Vitamins, Minerals).","Ingredients: cashew nuts (Vitamins, Minerals).","Ingredients: chestnuts (Vitamins, Minerals).","Ingredients: chia seeds (Vitamins, Minerals).","Ingredients: ginkgo nuts (Vitamins, Minerals).","Ingredients: hazelnuts (Vitamins, Minerals).","Ingredients: hickory nuts (Vitamins, Minerals).","Ingredients: macadamia nuts (Vitamins, Minerals).","Ingredients: pecans (Vitamins, Minerals).","Ingredients: pili nuts (Vitamins, Minerals).","Ingredients: pine nuts (Vitamins, Minerals).","Ingredients: pistachio nuts (Vitamins, Minerals).","Ingredients: safflower seeds (Vitamins, Minerals).","Ingredients: sesame seeds (Vitamins, Minerals).","Ingredients: sunflower seeds (Vitamins, Minerals).","Ingredients: walnuts (Vitamins, Minerals).","Ingredients: watermelon seeds (Vitamins, Minerals).","Ingredients: Salted almonds powder.","Ingredients: Salted pumpkin seeds powder.","Ingredients: Salted flax seeds powder.","Ingredients: Salted acorns powder.","Ingredients: Salted beechnuts powder.","Ingredients: Salted brazil nuts powder.","Ingredients: Salted butternuts powder.","Ingredients: Salted cashew nuts powder.","Ingredients: Salted chestnuts powder.","Ingredients: Salted chia seeds powder.","Ingredients: Salted ginkgo nuts powder.","Ingredients: Salted hazelnuts powder.","Ingredients: Salted hickory nuts powder.","Ingredients: Salted macadamia nuts powder.","Ingredients: Salted pecans powder.","Ingredients: Salted pili nuts powder.","Ingredients: Salted pine nuts powder.","Ingredients: Salted pistachio nuts powder.","Ingredients: Salted safflower seeds powder.","Ingredients: Salted sesame seeds powder.","Ingredients: Salted sunflower seeds powder.","Ingredients: Salted walnuts powder.","Ingredients: Salted watermelon seeds powder.","Ingredients: almonds powder (Salt).","Ingredients: pumpkin seeds powder (Salt).","Ingredients: flax seeds powder (Salt).","Ingredients: acorns powder (Salt).","Ingredients: beechnuts powder (Salt).","Ingredients: brazil nuts powder (Salt).","Ingredients: butternuts powder (Salt).","Ingredients: cashew nuts powder (Salt).","Ingredients: chestnuts powder (Salt).","Ingredients: chia seeds powder (Salt).","Ingredients: ginkgo nuts powder (Salt).","Ingredients: hazelnuts powder (Salt).","Ingredients: hickory nuts powder (Salt).","Ingredients: macadamia nuts powder (Salt).","Ingredients: pecans powder (Salt).","Ingredients: pili nuts powder (Salt).","Ingredients: pine nuts powder (Salt).","Ingredients: pistachio nuts powder (Salt).","Ingredients: safflower seeds powder (Salt).","Ingredients: sesame seeds powder (Salt).","Ingredients: sunflower seeds powder (Salt).","Ingredients: walnuts powder (Salt).","Ingredients: watermelon seeds powder (Salt).","Ingredients: almonds powder (Sugar).","Ingredients: pumpkin seeds powder (Sugar).","Ingredients: flax seeds powder (Sugar).","Ingredients: acorns powder (Sugar).","Ingredients: beechnuts powder (Sugar).","Ingredients: brazil nuts powder (Sugar).","Ingredients: butternuts powder (Sugar).","Ingredients: cashew nuts powder (Sugar).","Ingredients: chestnuts powder (Sugar).","Ingredients: chia seeds powder (Sugar).","Ingredients: ginkgo nuts powder (Sugar).","Ingredients: hazelnuts powder (Sugar).","Ingredients: hickory nuts powder (Sugar).","Ingredients: macadamia nuts powder (Sugar).","Ingredients: pecans powder (Sugar).","Ingredients: pili nuts powder (Sugar).","Ingredients: pine nuts powder (Sugar).","Ingredients: pistachio nuts powder (Sugar).","Ingredients: safflower seeds powder (Sugar).","Ingredients: sesame seeds powder (Sugar).","Ingredients: sunflower seeds powder (Sugar).","Ingredients: walnuts powder (Sugar).","Ingredients: watermelon seeds powder (Sugar).","Ingredients: Cashew Nuts (Banana Powder).","Ingredients: 100% Cashew Nuts (Banana Powder).","Ingredients: Pistachio Nuts (Banana Powder).","Ingredients: 100% Pistachio Nuts (Banana Powder).","Ingredients: Chickpea (Banana Powder).","Ingredients: 100% Chickpea (Banana Powder).","Ingredients: Semolina (Banana Powder).","Ingredients: 100% Semolina (Banana Powder).","Ingredients: Suji (Banana Powder).","Ingredients: 100% Suji (Banana Powder).","Ingredients: Mango (Banana Powder).","Ingredients: 100% Mango (Banana Powder).","Ingredients: Cashew Nuts (Spinach Powder).","Ingredients: 100% Cashew Nuts (Spinach Powder).","Ingredients: Pistachio Nuts (Spinach Powder).","Ingredients: 100% Pistachio Nuts (Spinach Powder).","Ingredients: Chickpea (Spinach Powder).","Ingredients: 100% Chickpea (Spinach Powder).","Ingredients: Semolina (Spinach Powder).","Ingredients: 100% Semolina (Spinach Powder).","Ingredients: Suji (Spinach Powder).","Ingredients: 100% Suji (Spinach Powder).","Ingredients: Mango (Spinach Powder).","Ingredients: 100% Mango (Spinach Powder).","Ingredients: Cashew Nuts (Cashew Nuts Powder).","Ingredients: 100% Cashew Nuts (Cashew Nuts Powder).","Ingredients: Pistachio Nuts (Cashew Nuts Powder).","Ingredients: 100% Pistachio Nuts (Cashew Nuts Powder).","Ingredients: Chickpea (Cashew Nuts Powder).","Ingredients: 100% Chickpea (Cashew Nuts Powder).","Ingredients: Semolina (Cashew Nuts Powder).","Ingredients: 100% Semolina (Cashew Nuts Powder).","Ingredients: Suji (Cashew Nuts Powder).","Ingredients: 100% Suji (Cashew Nuts Powder).","Ingredients: Mango (Cashew Nuts Powder).","Ingredients: 100% Mango (Cashew Nuts Powder).","Ingredients: Cashew Nuts (100% Banana Powder).","Ingredients: Pistachio Nuts (100% Banana Powder).","Ingredients: Chickpea (100% Banana Powder).","Ingredients: Semolina (100% Banana Powder).","Ingredients: Suji (100% Banana Powder).","Ingredients: Mango (100% Banana Powder).","Ingredients: Cashew Nuts (Whole Spinach Powder).","Ingredients: Pistachio Nuts (Whole Spinach Powder).","Ingredients: Chickpea (Whole Spinach Powder).","Ingredients: Semolina (Whole Spinach Powder).","Ingredients: Suji (Whole Spinach Powder).","Ingredients: Mango (Whole Spinach Powder).","Ingredients: Cashew Nuts (100% Cashew Nuts Powder).","Ingredients: Pistachio Nuts (100% Cashew Nuts Powder).","Ingredients: Chickpea (100% Cashew Nuts Powder).","Ingredients: Semolina (100% Cashew Nuts Powder).","Ingredients: Suji (100% Cashew Nuts Powder).","Ingredients: Mango (100% Cashew Nuts Powder).","Ingredients: Cashew Nuts (Milk Powder).","Ingredients: Cashew Nuts (Whole Milk Powder).","Ingredients: Pistachio Nuts (Milk Powder).","Ingredients: Pistachio Nuts (Whole Milk Powder).","Ingredients: Semolina (Milk Powder).","Ingredients: Semolina (Whole Milk Powder).","Ingredients: Suji (Milk Powder).","Ingredients: Suji (Whole Milk Powder).","Ingredients: Cashew Nuts Powder (XQ9).","Ingredients: Semolina (Banana Powder, XQ9).","Ingredients: Cashew Nuts (Sprouted Ragi).","Ingredients: 100% Cashew Nuts (Banana Powder, Whole Rice).","Ingredients: Cashew Nuts (Banana Powder), Maltodextrin.","Ingredients: Cashew Nuts Powder (Maltodextrin).","Ingredients: Semolina (Banana Powder), Maltodextrin.","Ingredients: Cashew Nuts (Sunflower Oil Powder (100%)).","Ingredients: Cashew Nuts (100% Mango (Banana Powder)).","Ingredients: Cashew Nuts (Whole Mango (Banana Powder)).","Ingredients: Semolina (Whole Mango (Banana Powder)).","Ingredients: Cashew Nuts (Banana Powder (Salt), 100% Rice).","Ingredients: Semolina (Banana Powder (Salt), Whole Rice).","Ingredients: Cashew Nuts [Banana Powder {Salt}, 100% Rice].","Ingredients: Cashew Nuts (Banana Powder and 100% Rice).","Ingredients: Cashew Nuts (Banana Powder & Whole Rice).","Ingredients: Cashew Nuts (Banana Powder; 100% Rice).","Ingredients: Cashew Nuts (Banana Powder (100%)).","Ingredients: Cashew Nuts [Banana Powder {100%}].","Ingredients: Cashew Nuts (Whole Mango (100% Banana Powder)).","Ingredients: almonds Powder (100% Rice).","Ingredients: pumpkin seeds Powder (100% Rice).","Ingredients: flax seeds Powder (100% Rice).","Ingredients: acorns Powder (100% Rice).","Ingredients: beechnuts Powder (100% Rice).","Ingredients: brazil nuts Powder (100% Rice).","Ingredients: butternuts Powder (100% Rice).","Ingredients: cashew nuts Powder (100% Rice).","Ingredients: chestnuts Powder (100% Rice).","Ingredients: chia seeds Powder (100% Rice).","Ingredients: ginkgo nuts Powder (100% Rice).","Ingredients: hazelnuts Powder (100% Rice).","Ingredients: hickory nuts Powder (100% Rice).","Ingredients: macadamia nuts Powder (100% Rice).","Ingredients: pecans Powder (100% Rice).","Ingredients: pili nuts Powder (100% Rice).","Ingredients: pine nuts Powder (100% Rice).","Ingredients: pistachio nuts Powder (100% Rice).","Ingredients: safflower seeds Powder (100% Rice).","Ingredients: sesame seeds Powder (100% Rice).","Ingredients: sunflower seeds Powder (100% Rice).","Ingredients: walnuts Powder (100% Rice).","Ingredients: watermelon seeds Powder (100% Rice).","Ingredients: Banana Powder (100% Rice).","Ingredients: Spinach Powder (100% Rice).","Ingredients: Chickpea Powder (100% Rice).","Ingredients: almonds Powder (Whole Rice).","Ingredients: pumpkin seeds Powder (Whole Rice).","Ingredients: flax seeds Powder (Whole Rice).","Ingredients: acorns Powder (Whole Rice).","Ingredients: beechnuts Powder (Whole Rice).","Ingredients: brazil nuts Powder (Whole Rice).","Ingredients: butternuts Powder (Whole Rice).","Ingredients: cashew nuts Powder (Whole Rice).","Ingredients: chestnuts Powder (Whole Rice).","Ingredients: chia seeds Powder (Whole Rice).","Ingredients: ginkgo nuts Powder (Whole Rice).","Ingredients: hazelnuts Powder (Whole Rice).","Ingredients: hickory nuts Powder (Whole Rice).","Ingredients: macadamia nuts Powder (Whole Rice).","Ingredients: pecans Powder (Whole Rice).","Ingredients: pili nuts Powder (Whole Rice).","Ingredients: pine nuts Powder (Whole Rice).","Ingredients: pistachio nuts Powder (Whole Rice).","Ingredients: safflower seeds Powder (Whole Rice).","Ingredients: sesame seeds Powder (Whole Rice).","Ingredients: sunflower seeds Powder (Whole Rice).","Ingredients: walnuts Powder (Whole Rice).","Ingredients: watermelon seeds Powder (Whole Rice).","Ingredients: Banana Powder (Whole Rice).","Ingredients: Spinach Powder (Whole Rice).","Ingredients: Chickpea Powder (Whole Rice).","Ingredients: almonds Powder (100% Milk Powder).","Ingredients: pumpkin seeds Powder (100% Milk Powder).","Ingredients: flax seeds Powder (100% Milk Powder).","Ingredients: acorns Powder (100% Milk Powder).","Ingredients: beechnuts Powder (100% Milk Powder).","Ingredients: brazil nuts Powder (100% Milk Powder).","Ingredients: butternuts Powder (100% Milk Powder).","Ingredients: cashew nuts Powder (100% Milk Powder).","Ingredients: chestnuts Powder (100% Milk Powder).","Ingredients: chia seeds Powder (100% Milk Powder).","Ingredients: ginkgo nuts Powder (100% Milk Powder).","Ingredients: hazelnuts Powder (100% Milk Powder).","Ingredients: hickory nuts Powder (100% Milk Powder).","Ingredients: macadamia nuts Powder (100% Milk Powder).","Ingredients: pecans Powder (100% Milk Powder).","Ingredients: pili nuts Powder (100% Milk Powder).","Ingredients: pine nuts Powder (100% Milk Powder).","Ingredients: pistachio nuts Powder (100% Milk Powder).","Ingredients: safflower seeds Powder (100% Milk Powder).","Ingredients: sesame seeds Powder (100% Milk Powder).","Ingredients: sunflower seeds Powder (100% Milk Powder).","Ingredients: walnuts Powder (100% Milk Powder).","Ingredients: watermelon seeds Powder (100% Milk Powder).","Ingredients: Banana Powder (100% Milk Powder).","Ingredients: Spinach Powder (100% Milk Powder).","Ingredients: Chickpea Powder (100% Milk Powder).","Ingredients: almonds Powder (Whole Milk Powder).","Ingredients: pumpkin seeds Powder (Whole Milk Powder).","Ingredients: flax seeds Powder (Whole Milk Powder).","Ingredients: acorns Powder (Whole Milk Powder).","Ingredients: beechnuts Powder (Whole Milk Powder).","Ingredients: brazil nuts Powder (Whole Milk Powder).","Ingredients: butternuts Powder (Whole Milk Powder).","Ingredients: cashew nuts Powder (Whole Milk Powder).","Ingredients: chestnuts Powder (Whole Milk Powder).","Ingredients: chia seeds Powder (Whole Milk Powder).","Ingredients: ginkgo nuts Powder (Whole Milk Powder).","Ingredients: hazelnuts Powder (Whole Milk Powder).","Ingredients: hickory nuts Powder (Whole Milk Powder).","Ingredients: macadamia nuts Powder (Whole Milk Powder).","Ingredients: pecans Powder (Whole Milk Powder).","Ingredients: pili nuts Powder (Whole Milk Powder).","Ingredients: pine nuts Powder (Whole Milk Powder).","Ingredients: pistachio nuts Powder (Whole Milk Powder).","Ingredients: safflower seeds Powder (Whole Milk Powder).","Ingredients: sesame seeds Powder (Whole Milk Powder).","Ingredients: sunflower seeds Powder (Whole Milk Powder).","Ingredients: walnuts Powder (Whole Milk Powder).","Ingredients: watermelon seeds Powder (Whole Milk Powder).","Ingredients: Banana Powder (Whole Milk Powder).","Ingredients: Spinach Powder (Whole Milk Powder).","Ingredients: Chickpea Powder (Whole Milk Powder).","Ingredients: Mango (Milk Powder).","Ingredients: Chickpea (Milk Powder).","Ingredients: Carrot (Milk Powder).","Ingredients: Mango (Whole Milk Powder).","Ingredients: Chickpea (Whole Milk Powder).","Ingredients: Carrot (Whole Milk Powder).","Ingredients: Mango (100% Milk Powder).","Ingredients: Chickpea (100% Milk Powder).","Ingredients: Carrot (100% Milk Powder).","Ingredients: Cashew Nuts (100% Milk Powder).","Ingredients: Pistachio Nuts (100% Milk Powder).","Ingredients: Semolina (100% Milk Powder).","Ingredients: Mango (Milk Powder (100%)).","Ingredients: Chickpea (Milk Powder (100%)).","Ingredients: Carrot (Milk Powder (100%)).","Ingredients: Cashew Nuts (Milk Powder (100%)).","Ingredients: Pistachio Nuts (Milk Powder (100%)).","Ingredients: Semolina (Milk Powder (100%)).","Ingredients: Whole almonds Powder (Milk).","Ingredients: Whole pumpkin seeds Powder (Milk).","Ingredients: Whole flax seeds Powder (Milk).","Ingredients: Whole acorns Powder (Milk).","Ingredients: Whole beechnuts Powder (Milk).","Ingredients: Whole brazil nuts Powder (Milk).","Ingredients: Whole butternuts Powder (Milk).","Ingredients: Whole cashew nuts Powder (Milk).","Ingredients: Whole chestnuts Powder (Milk).","Ingredients: Whole chia seeds Powder (Milk).","Ingredients: Whole ginkgo nuts Powder (Milk).","Ingredients: Whole hazelnuts Powder (Milk).","Ingredients: Whole hickory nuts Powder (Milk).","Ingredients: Whole macadamia nuts Powder (Milk).","Ingredients: Whole pecans Powder (Milk).","Ingredients: Whole pili nuts Powder (Milk).","Ingredients: Whole pine nuts Powder (Milk).","Ingredients: Whole pistachio nuts Powder (Milk).","Ingredients: Whole safflower seeds Powder (Milk).","Ingredients: Whole sesame seeds Powder (Milk).","Ingredients: Whole sunflower seeds Powder (Milk).","Ingredients: Whole walnuts Powder (Milk).","Ingredients: Whole watermelon seeds Powder (Milk).","Ingredients: Whole almonds Powder (Milk Powder).","Ingredients: Whole pumpkin seeds Powder (Milk Powder).","Ingredients: Whole flax seeds Powder (Milk Powder).","Ingredients: Whole acorns Powder (Milk Powder).","Ingredients: Whole beechnuts Powder (Milk Powder).","Ingredients: Whole brazil nuts Powder (Milk Powder).","Ingredients: Whole butternuts Powder (Milk Powder).","Ingredients: Whole cashew nuts Powder (Milk Powder).","Ingredients: Whole chestnuts Powder (Milk Powder).","Ingredients: Whole chia seeds Powder (Milk Powder).","Ingredients: Whole ginkgo nuts Powder (Milk Powder).","Ingredients: Whole hazelnuts Powder (Milk Powder).","Ingredients: Whole hickory nuts Powder (Milk Powder).","Ingredients: Whole macadamia nuts Powder (Milk Powder).","Ingredients: Whole pecans Powder (Milk Powder).","Ingredients: Whole pili nuts Powder (Milk Powder).","Ingredients: Whole pine nuts Powder (Milk Powder).","Ingredients: Whole pistachio nuts Powder (Milk Powder).","Ingredients: Whole safflower seeds Powder (Milk Powder).","Ingredients: Whole sesame seeds Powder (Milk Powder).","Ingredients: Whole sunflower seeds Powder (Milk Powder).","Ingredients: Whole walnuts Powder (Milk Powder).","Ingredients: Whole watermelon seeds Powder (Milk Powder).","Ingredients: Banana Powder (100%).","Ingredients: Banana Powder (100.0%).","Ingredients: Banana Powder [100%].","Ingredients: Banana Powder (whole).","Ingredients: Whole Banana Powder.","Ingredients: 100% Banana Powder (Rice).","Ingredients: almonds Powder (100% almonds).","Ingredients: pumpkin seeds Powder (100% pumpkin seeds).","Ingredients: flax seeds Powder (100% flax seeds).","Ingredients: acorns Powder (100% acorns).","Ingredients: beechnuts Powder (100% beechnuts).","Ingredients: brazil nuts Powder (100% brazil nuts).","Ingredients: butternuts Powder (100% butternuts).","Ingredients: cashew nuts Powder (100% cashew nuts).","Ingredients: chestnuts Powder (100% chestnuts).","Ingredients: chia seeds Powder (100% chia seeds).","Ingredients: ginkgo nuts Powder (100% ginkgo nuts).","Ingredients: hazelnuts Powder (100% hazelnuts).","Ingredients: hickory nuts Powder (100% hickory nuts).","Ingredients: macadamia nuts Powder (100% macadamia nuts).","Ingredients: pecans Powder (100% pecans).","Ingredients: pili nuts Powder (100% pili nuts).","Ingredients: pine nuts Powder (100% pine nuts).","Ingredients: pistachio nuts Powder (100% pistachio nuts).","Ingredients: safflower seeds Powder (100% safflower seeds).","Ingredients: sesame seeds Powder (100% sesame seeds).","Ingredients: sunflower seeds Powder (100% sunflower seeds).","Ingredients: walnuts Powder (100% walnuts).","Ingredients: watermelon seeds Powder (100% watermelon seeds).","Ingredients: Banana Powder (100% Banana).","Ingredients: Spinach Powder (100% Spinach).","Ingredients: Chickpea Powder (100% Chickpea).","Ingredients: almonds Powder (Whole almonds).","Ingredients: pumpkin seeds Powder (Whole pumpkin seeds).","Ingredients: flax seeds Powder (Whole flax seeds).","Ingredients: acorns Powder (Whole acorns).","Ingredients: beechnuts Powder (Whole beechnuts).","Ingredients: brazil nuts Powder (Whole brazil nuts).","Ingredients: butternuts Powder (Whole butternuts).","Ingredients: cashew nuts Powder (Whole cashew nuts).","Ingredients: chestnuts Powder (Whole chestnuts).","Ingredients: chia seeds Powder (Whole chia seeds).","Ingredients: ginkgo nuts Powder (Whole ginkgo nuts).","Ingredients: hazelnuts Powder (Whole hazelnuts).","Ingredients: hickory nuts Powder (Whole hickory nuts).","Ingredients: macadamia nuts Powder (Whole macadamia nuts).","Ingredients: pecans Powder (Whole pecans).","Ingredients: pili nuts Powder (Whole pili nuts).","Ingredients: pine nuts Powder (Whole pine nuts).","Ingredients: pistachio nuts Powder (Whole pistachio nuts).","Ingredients: safflower seeds Powder (Whole safflower seeds).","Ingredients: sesame seeds Powder (Whole sesame seeds).","Ingredients: sunflower seeds Powder (Whole sunflower seeds).","Ingredients: walnuts Powder (Whole walnuts).","Ingredients: watermelon seeds Powder (Whole watermelon seeds).","Ingredients: Banana Powder (Whole Banana).","Ingredients: Spinach Powder (Whole Spinach).","Ingredients: Chickpea Powder (Whole Chickpea).","Ingredients: almonds Powder (almonds 100%).","Ingredients: pumpkin seeds Powder (pumpkin seeds 100%).","Ingredients: flax seeds Powder (flax seeds 100%).","Ingredients: acorns Powder (acorns 100%).","Ingredients: beechnuts Powder (beechnuts 100%).","Ingredients: brazil nuts Powder (brazil nuts 100%).","Ingredients: butternuts Powder (butternuts 100%).","Ingredients: cashew nuts Powder (cashew nuts 100%).","Ingredients: chestnuts Powder (chestnuts 100%).","Ingredients: chia seeds Powder (chia seeds 100%).","Ingredients: ginkgo nuts Powder (ginkgo nuts 100%).","Ingredients: hazelnuts Powder (hazelnuts 100%).","Ingredients: hickory nuts Powder (hickory nuts 100%).","Ingredients: macadamia nuts Powder (macadamia nuts 100%).","Ingredients: pecans Powder (pecans 100%).","Ingredients: pili nuts Powder (pili nuts 100%).","Ingredients: pine nuts Powder (pine nuts 100%).","Ingredients: pistachio nuts Powder (pistachio nuts 100%).","Ingredients: safflower seeds Powder (safflower seeds 100%).","Ingredients: sesame seeds Powder (sesame seeds 100%).","Ingredients: sunflower seeds Powder (sunflower seeds 100%).","Ingredients: walnuts Powder (walnuts 100%).","Ingredients: watermelon seeds Powder (watermelon seeds 100%).","Ingredients: Banana Powder (Banana 100%).","Ingredients: Spinach Powder (Spinach 100%).","Ingredients: Chickpea Powder (Chickpea 100%).","Ingredients: Banana Powder (100% Banana Powder).","Ingredients: Date Powder (100% Date Powder).","Ingredients: Strawberry Powder (100% Strawberry Powder).","Ingredients: Beetroot Powder (100% Beetroot Powder).","Ingredients: Banana Powder (Whole Banana Powder).","Ingredients: Date Powder (Whole Date Powder).","Ingredients: Strawberry Powder (Whole Strawberry Powder).","Ingredients: Beetroot Powder (Whole Beetroot Powder).","Ingredients: Banana Powder (Banana Powder 100%).","Ingredients: Date Powder (Date Powder 100%).","Ingredients: Strawberry Powder (Strawberry Powder 100%).","Ingredients: Beetroot Powder (Beetroot Powder 100%).","Ingredients: maida.","Ingredients: garbanzo bean.","Ingredients: garbanzo beans.","Ingredients: cashew.","Ingredients: cashews.","Ingredients: pistachio.","Ingredients: pistachios.","Ingredients: refined wheat flour.","Ingredients: chickpea.","Ingredients: cashew nuts.","Ingredients: pistachio nuts.","Ingredients: Raw maida.","Ingredients: Raw refined wheat flour.","Ingredients: Raw garbanzo bean.","Ingredients: Raw chickpea.","Ingredients: Raw garbanzo beans.","Ingredients: Raw cashew.","Ingredients: Raw cashew nuts.","Ingredients: Raw cashews.","Ingredients: Raw pistachio.","Ingredients: Raw pistachio nuts.","Ingredients: Raw pistachios.","Ingredients: Roasted maida.","Ingredients: Roasted refined wheat flour.","Ingredients: Roasted garbanzo bean.","Ingredients: Roasted chickpea.","Ingredients: Roasted garbanzo beans.","Ingredients: Roasted cashew.","Ingredients: Roasted cashew nuts.","Ingredients: Roasted cashews.","Ingredients: Roasted pistachio.","Ingredients: Roasted pistachio nuts.","Ingredients: Roasted pistachios.","Ingredients: Boiled maida.","Ingredients: Boiled refined wheat flour.","Ingredients: Boiled garbanzo bean.","Ingredients: Boiled chickpea.","Ingredients: Boiled garbanzo beans.","Ingredients: Boiled cashew.","Ingredients: Boiled cashew nuts.","Ingredients: Boiled cashews.","Ingredients: Boiled pistachio.","Ingredients: Boiled pistachio nuts.","Ingredients: Boiled pistachios.","Ingredients: Salted maida.","Ingredients: Salted refined wheat flour.","Ingredients: Salted garbanzo bean.","Ingredients: Salted chickpea.","Ingredients: Salted garbanzo beans.","Ingredients: Salted cashew.","Ingredients: Salted cashew nuts.","Ingredients: Salted cashews.","Ingredients: Salted pistachio.","Ingredients: Salted pistachio nuts.","Ingredients: Salted pistachios.","Ingredients: Sugared maida.","Ingredients: Sugared refined wheat flour.","Ingredients: Sugared garbanzo bean.","Ingredients: Sugared chickpea.","Ingredients: Sugared garbanzo beans.","Ingredients: Sugared cashew.","Ingredients: Sugared cashew nuts.","Ingredients: Sugared cashews.","Ingredients: Sugared pistachio.","Ingredients: Sugared pistachio nuts.","Ingredients: Sugared pistachios.","Ingredients: maida (salt).","Ingredients: refined wheat flour (salt).","Ingredients: garbanzo bean (salt).","Ingredients: chickpea (salt).","Ingredients: garbanzo beans (salt).","Ingredients: cashew (salt).","Ingredients: cashew nuts (salt).","Ingredients: cashews (salt).","Ingredients: pistachio (salt).","Ingredients: pistachio nuts (salt).","Ingredients: pistachios (salt).","Ingredients: maida (sugar).","Ingredients: refined wheat flour (sugar).","Ingredients: garbanzo bean (sugar).","Ingredients: chickpea (sugar).","Ingredients: garbanzo beans (sugar).","Ingredients: cashew (sugar).","Ingredients: cashew nuts (sugar).","Ingredients: cashews (sugar).","Ingredients: pistachio (sugar).","Ingredients: pistachio nuts (sugar).","Ingredients: pistachios (sugar).","Ingredients: maida (honey).","Ingredients: refined wheat flour (honey).","Ingredients: garbanzo bean (honey).","Ingredients: chickpea (honey).","Ingredients: garbanzo beans (honey).","Ingredients: cashew (honey).","Ingredients: cashew nuts (honey).","Ingredients: cashews (honey).","Ingredients: pistachio (honey).","Ingredients: pistachio nuts (honey).","Ingredients: pistachios (honey).","Ingredients: maida (brine).","Ingredients: refined wheat flour (brine).","Ingredients: garbanzo bean (brine).","Ingredients: chickpea (brine).","Ingredients: garbanzo beans (brine).","Ingredients: cashew (brine).","Ingredients: cashew nuts (brine).","Ingredients: cashews (brine).","Ingredients: pistachio (brine).","Ingredients: pistachio nuts (brine).","Ingredients: pistachios (brine).","Ingredients: maida (corn oil).","Ingredients: refined wheat flour (corn oil).","Ingredients: garbanzo bean (corn oil).","Ingredients: chickpea (corn oil).","Ingredients: garbanzo beans (corn oil).","Ingredients: cashew (corn oil).","Ingredients: cashew nuts (corn oil).","Ingredients: cashews (corn oil).","Ingredients: pistachio (corn oil).","Ingredients: pistachio nuts (corn oil).","Ingredients: pistachios (corn oil).","Ingredients: maida (XQ9).","Ingredients: refined wheat flour (XQ9).","Ingredients: garbanzo bean (XQ9).","Ingredients: chickpea (XQ9).","Ingredients: garbanzo beans (XQ9).","Ingredients: cashew (XQ9).","Ingredients: cashew nuts (XQ9).","Ingredients: cashews (XQ9).","Ingredients: pistachio (XQ9).","Ingredients: pistachio nuts (XQ9).","Ingredients: pistachios (XQ9).","Ingredients: maida (sugar, XQ9).","Ingredients: refined wheat flour (sugar, XQ9).","Ingredients: garbanzo bean (sugar, XQ9).","Ingredients: chickpea (sugar, XQ9).","Ingredients: garbanzo beans (sugar, XQ9).","Ingredients: cashew (sugar, XQ9).","Ingredients: cashew nuts (sugar, XQ9).","Ingredients: cashews (sugar, XQ9).","Ingredients: pistachio (sugar, XQ9).","Ingredients: pistachio nuts (sugar, XQ9).","Ingredients: pistachios (sugar, XQ9).","Ingredients: maida (no added salt, sugar).","Ingredients: refined wheat flour (no added salt, sugar).","Ingredients: garbanzo bean (no added salt, sugar).","Ingredients: chickpea (no added salt, sugar).","Ingredients: garbanzo beans (no added salt, sugar).","Ingredients: cashew (no added salt, sugar).","Ingredients: cashew nuts (no added salt, sugar).","Ingredients: cashews (no added salt, sugar).","Ingredients: pistachio (no added salt, sugar).","Ingredients: pistachio nuts (no added salt, sugar).","Ingredients: pistachios (no added salt, sugar).","Ingredients: maida (Rice).","Ingredients: refined wheat flour (Rice).","Ingredients: garbanzo bean (Rice).","Ingredients: chickpea (Rice).","Ingredients: garbanzo beans (Rice).","Ingredients: cashew (Rice).","Ingredients: cashews (Rice).","Ingredients: pistachio (Rice).","Ingredients: pistachios (Rice).","Ingredients: maida (Milk).","Ingredients: refined wheat flour (Milk).","Ingredients: garbanzo bean (Milk).","Ingredients: chickpea (Milk).","Ingredients: garbanzo beans (Milk).","Ingredients: cashew (Milk).","Ingredients: cashew nuts (Milk).","Ingredients: cashews (Milk).","Ingredients: pistachio (Milk).","Ingredients: pistachio nuts (Milk).","Ingredients: pistachios (Milk).","Ingredients: maida (Milk Powder).","Ingredients: refined wheat flour (Milk Powder).","Ingredients: garbanzo bean (Milk Powder).","Ingredients: chickpea (Milk Powder).","Ingredients: garbanzo beans (Milk Powder).","Ingredients: cashew (Milk Powder).","Ingredients: cashews (Milk Powder).","Ingredients: pistachio (Milk Powder).","Ingredients: pistachios (Milk Powder).","Ingredients: maida (Whole Milk Powder).","Ingredients: refined wheat flour (Whole Milk Powder).","Ingredients: garbanzo bean (Whole Milk Powder).","Ingredients: chickpea (Whole Milk Powder).","Ingredients: garbanzo beans (Whole Milk Powder).","Ingredients: cashew (Whole Milk Powder).","Ingredients: cashew nuts (Whole Milk Powder).","Ingredients: cashews (Whole Milk Powder).","Ingredients: pistachio (Whole Milk Powder).","Ingredients: pistachio nuts (Whole Milk Powder).","Ingredients: pistachios (Whole Milk Powder).","Ingredients: maida (Cashew Nuts).","Ingredients: refined wheat flour (Cashew Nuts).","Ingredients: garbanzo bean (Cashew Nuts).","Ingredients: chickpea (Cashew Nuts).","Ingredients: garbanzo beans (Cashew Nuts).","Ingredients: cashew (Cashew Nuts).","Ingredients: cashew nuts (Cashew Nuts).","Ingredients: cashews (Cashew Nuts).","Ingredients: pistachio (Cashew Nuts).","Ingredients: pistachio nuts (Cashew Nuts).","Ingredients: pistachios (Cashew Nuts).","Ingredients: maida powder.","Ingredients: refined wheat flour powder.","Ingredients: garbanzo bean powder.","Ingredients: chickpea powder.","Ingredients: garbanzo beans powder.","Ingredients: cashew powder.","Ingredients: cashews powder.","Ingredients: pistachio powder.","Ingredients: pistachios powder.","Ingredients: 100% maida powder.","Ingredients: 100% refined wheat flour powder.","Ingredients: 100% garbanzo bean powder.","Ingredients: 100% chickpea powder.","Ingredients: 100% garbanzo beans powder.","Ingredients: 100% cashew powder.","Ingredients: 100% cashews powder.","Ingredients: 100% pistachio powder.","Ingredients: 100% pistachios powder.","Ingredients: Whole maida powder.","Ingredients: Whole refined wheat flour powder.","Ingredients: Whole garbanzo bean powder.","Ingredients: Whole chickpea powder.","Ingredients: Whole garbanzo beans powder.","Ingredients: Whole cashew powder.","Ingredients: Whole cashews powder.","Ingredients: Whole pistachio powder.","Ingredients: Whole pistachios powder.","Ingredients: maida powder (100% Rice).","Ingredients: refined wheat flour powder (100% Rice).","Ingredients: garbanzo bean powder (100% Rice).","Ingredients: chickpea powder (100% Rice).","Ingredients: garbanzo beans powder (100% Rice).","Ingredients: cashew powder (100% Rice).","Ingredients: cashew nuts powder (100% Rice).","Ingredients: cashews powder (100% Rice).","Ingredients: pistachio powder (100% Rice).","Ingredients: pistachio nuts powder (100% Rice).","Ingredients: pistachios powder (100% Rice).","Ingredients: maida powder (Whole Rice).","Ingredients: refined wheat flour powder (Whole Rice).","Ingredients: garbanzo bean powder (Whole Rice).","Ingredients: chickpea powder (Whole Rice).","Ingredients: garbanzo beans powder (Whole Rice).","Ingredients: cashew powder (Whole Rice).","Ingredients: cashew nuts powder (Whole Rice).","Ingredients: cashews powder (Whole Rice).","Ingredients: pistachio powder (Whole Rice).","Ingredients: pistachio nuts powder (Whole Rice).","Ingredients: pistachios powder (Whole Rice).","Ingredients: maida (Banana Powder).","Ingredients: refined wheat flour (Banana Powder).","Ingredients: garbanzo bean (Banana Powder).","Ingredients: chickpea (Banana Powder).","Ingredients: garbanzo beans (Banana Powder).","Ingredients: cashew (Banana Powder).","Ingredients: cashew nuts (Banana Powder).","Ingredients: cashews (Banana Powder).","Ingredients: pistachio (Banana Powder).","Ingredients: pistachio nuts (Banana Powder).","Ingredients: pistachios (Banana Powder).","Ingredients: 100% maida (Banana Powder).","Ingredients: 100% refined wheat flour (Banana Powder).","Ingredients: 100% garbanzo bean (Banana Powder).","Ingredients: 100% chickpea (Banana Powder).","Ingredients: 100% garbanzo beans (Banana Powder).","Ingredients: 100% cashew (Banana Powder).","Ingredients: 100% cashews (Banana Powder).","Ingredients: 100% pistachio (Banana Powder).","Ingredients: 100% pistachios (Banana Powder).","Ingredients: maida (100% Banana Powder).","Ingredients: refined wheat flour (100% Banana Powder).","Ingredients: garbanzo bean (100% Banana Powder).","Ingredients: chickpea (100% Banana Powder).","Ingredients: garbanzo beans (100% Banana Powder).","Ingredients: cashew (100% Banana Powder).","Ingredients: cashews (100% Banana Powder).","Ingredients: pistachio (100% Banana Powder).","Ingredients: pistachios (100% Banana Powder).","Ingredients: maida (dried).","Ingredients: refined wheat flour (dried).","Ingredients: garbanzo bean (dried).","Ingredients: chickpea (dried).","Ingredients: garbanzo beans (dried).","Ingredients: cashew (dried).","Ingredients: cashew nuts (dried).","Ingredients: cashews (dried).","Ingredients: pistachio (dried).","Ingredients: pistachio nuts (dried).","Ingredients: pistachios (dried).","Ingredients: maida (canned).","Ingredients: refined wheat flour (canned).","Ingredients: garbanzo bean (canned).","Ingredients: chickpea (canned).","Ingredients: garbanzo beans (canned).","Ingredients: cashew (canned).","Ingredients: cashew nuts (canned).","Ingredients: cashews (canned).","Ingredients: pistachio (canned).","Ingredients: pistachio nuts (canned).","Ingredients: pistachios (canned).","Ingredients: maida (no added salt).","Ingredients: refined wheat flour (no added salt).","Ingredients: garbanzo bean (no added salt).","Ingredients: chickpea (no added salt).","Ingredients: garbanzo beans (no added salt).","Ingredients: cashew (no added salt).","Ingredients: cashew nuts (no added salt).","Ingredients: cashews (no added salt).","Ingredients: pistachio (no added salt).","Ingredients: pistachio nuts (no added salt).","Ingredients: pistachios (no added salt).","Ingredients: maida milk.","Ingredients: refined wheat flour milk.","Ingredients: garbanzo bean milk.","Ingredients: chickpea milk.","Ingredients: garbanzo beans milk.","Ingredients: cashew milk.","Ingredients: cashew nuts milk.","Ingredients: cashews milk.","Ingredients: pistachio milk.","Ingredients: pistachio nuts milk.","Ingredients: pistachios milk.","Ingredients: maida oil.","Ingredients: refined wheat flour oil.","Ingredients: garbanzo bean oil.","Ingredients: chickpea oil.","Ingredients: garbanzo beans oil.","Ingredients: cashew oil.","Ingredients: cashew nuts oil.","Ingredients: cashews oil.","Ingredients: pistachio oil.","Ingredients: pistachio nuts oil.","Ingredients: pistachios oil.","Ingredients: maida butter.","Ingredients: refined wheat flour butter.","Ingredients: garbanzo bean butter.","Ingredients: chickpea butter.","Ingredients: garbanzo beans butter.","Ingredients: cashew butter.","Ingredients: cashew nuts butter.","Ingredients: cashews butter.","Ingredients: pistachio butter.","Ingredients: pistachio nuts butter.","Ingredients: pistachios butter.","Ingredients: maida apple.","Ingredients: refined wheat flour apple.","Ingredients: garbanzo bean apple.","Ingredients: chickpea apple.","Ingredients: garbanzo beans apple.","Ingredients: cashew apple.","Ingredients: cashew nuts apple.","Ingredients: cashews apple.","Ingredients: pistachio apple.","Ingredients: pistachio nuts apple.","Ingredients: pistachios apple.","Ingredients: maida tree.","Ingredients: refined wheat flour tree.","Ingredients: garbanzo bean tree.","Ingredients: chickpea tree.","Ingredients: garbanzo beans tree.","Ingredients: cashew tree.","Ingredients: cashew nuts tree.","Ingredients: cashews tree.","Ingredients: pistachio tree.","Ingredients: pistachio nuts tree.","Ingredients: pistachios tree.","Ingredients: maida sprout.","Ingredients: refined wheat flour sprout.","Ingredients: garbanzo bean sprout.","Ingredients: chickpea sprout.","Ingredients: garbanzo beans sprout.","Ingredients: cashew sprout.","Ingredients: cashew nuts sprout.","Ingredients: cashews sprout.","Ingredients: pistachio sprout.","Ingredients: pistachio nuts sprout.","Ingredients: pistachios sprout.","Ingredients: xmaida.","Ingredients: xrefined wheat flour.","Ingredients: xgarbanzo bean.","Ingredients: xchickpea.","Ingredients: xgarbanzo beans.","Ingredients: xcashew.","Ingredients: xcashew nuts.","Ingredients: xcashews.","Ingredients: xpistachio.","Ingredients: xpistachio nuts.","Ingredients: xpistachios.","Ingredients: maidax.","Ingredients: refined wheat flourx.","Ingredients: garbanzo beanx.","Ingredients: chickpeax.","Ingredients: garbanzo beansx.","Ingredients: cashewx.","Ingredients: cashew nutsx.","Ingredients: cashewsx.","Ingredients: pistachiox.","Ingredients: pistachio nutsx.","Ingredients: pistachiosx.","Ingredients: Rice, maida.","Ingredients: Rice, refined wheat flour.","Ingredients: Rice, garbanzo bean.","Ingredients: Rice, chickpea.","Ingredients: Rice, garbanzo beans.","Ingredients: Rice, cashew.","Ingredients: Rice, cashew nuts.","Ingredients: Rice, cashews.","Ingredients: Rice, pistachio.","Ingredients: Rice, pistachio nuts.","Ingredients: Rice, pistachios.","Ingredients: maida, Maltodextrin.","Ingredients: refined wheat flour, Maltodextrin.","Ingredients: garbanzo bean, Maltodextrin.","Ingredients: chickpea, Maltodextrin.","Ingredients: garbanzo beans, Maltodextrin.","Ingredients: cashew, Maltodextrin.","Ingredients: cashew nuts, Maltodextrin.","Ingredients: cashews, Maltodextrin.","Ingredients: pistachio, Maltodextrin.","Ingredients: pistachio nuts, Maltodextrin.","Ingredients: pistachios, Maltodextrin.","Ingredients: Milk (maida).","Ingredients: Milk (refined wheat flour).","Ingredients: Milk (garbanzo bean).","Ingredients: Milk (chickpea).","Ingredients: Milk (garbanzo beans).","Ingredients: Milk (cashew).","Ingredients: Milk (cashew nuts).","Ingredients: Milk (cashews).","Ingredients: Milk (pistachio).","Ingredients: Milk (pistachio nuts).","Ingredients: Milk (pistachios).","Ingredients: Almonds (maida).","Ingredients: Almonds (refined wheat flour).","Ingredients: Almonds (garbanzo bean).","Ingredients: Almonds (chickpea).","Ingredients: Almonds (garbanzo beans).","Ingredients: Almonds (cashew).","Ingredients: Almonds (cashew nuts).","Ingredients: Almonds (cashews).","Ingredients: Almonds (pistachio).","Ingredients: Almonds (pistachio nuts).","Ingredients: Almonds (pistachios).","Ingredients: maida (modified).","Ingredients: refined wheat flour (modified).","Ingredients: garbanzo bean (modified).","Ingredients: chickpea (modified).","Ingredients: garbanzo beans (modified).","Ingredients: cashew (modified).","Ingredients: cashew nuts (modified).","Ingredients: cashews (modified).","Ingredients: pistachio (modified).","Ingredients: pistachio nuts (modified).","Ingredients: pistachios (modified).","Ingredients: maida (pregelatinized).","Ingredients: refined wheat flour (pregelatinized).","Ingredients: garbanzo bean (pregelatinized).","Ingredients: chickpea (pregelatinized).","Ingredients: garbanzo beans (pregelatinized).","Ingredients: cashew (pregelatinized).","Ingredients: cashew nuts (pregelatinized).","Ingredients: cashews (pregelatinized).","Ingredients: pistachio (pregelatinized).","Ingredients: pistachio nuts (pregelatinized).","Ingredients: pistachios (pregelatinized).","Ingredients: maida (flavour).","Ingredients: refined wheat flour (flavour).","Ingredients: garbanzo bean (flavour).","Ingredients: chickpea (flavour).","Ingredients: garbanzo beans (flavour).","Ingredients: cashew (flavour).","Ingredients: cashew nuts (flavour).","Ingredients: cashews (flavour).","Ingredients: pistachio (flavour).","Ingredients: pistachio nuts (flavour).","Ingredients: pistachios (flavour).","Ingredients: maida powder (maltodextrin).","Ingredients: refined wheat flour powder (maltodextrin).","Ingredients: garbanzo bean powder (maltodextrin).","Ingredients: chickpea powder (maltodextrin).","Ingredients: garbanzo beans powder (maltodextrin).","Ingredients: cashew powder (maltodextrin).","Ingredients: cashew nuts powder (maltodextrin).","Ingredients: cashews powder (maltodextrin).","Ingredients: pistachio powder (maltodextrin).","Ingredients: pistachio nuts powder (maltodextrin).","Ingredients: pistachios powder (maltodextrin).","Ingredients: maida (salt free, sugar).","Ingredients: refined wheat flour (salt free, sugar).","Ingredients: garbanzo bean (salt free, sugar).","Ingredients: chickpea (salt free, sugar).","Ingredients: garbanzo beans (salt free, sugar).","Ingredients: cashew (salt free, sugar).","Ingredients: cashew nuts (salt free, sugar).","Ingredients: cashews (salt free, sugar).","Ingredients: pistachio (salt free, sugar).","Ingredients: pistachio nuts (salt free, sugar).","Ingredients: pistachios (salt free, sugar).","Ingredients: Protein Rich maida.","Ingredients: Protein Rich refined wheat flour.","Ingredients: Protein Rich garbanzo bean.","Ingredients: Protein Rich chickpea.","Ingredients: Protein Rich garbanzo beans.","Ingredients: Protein Rich cashew.","Ingredients: Protein Rich cashew nuts.","Ingredients: Protein Rich cashews.","Ingredients: Protein Rich pistachio.","Ingredients: Protein Rich pistachio nuts.","Ingredients: Protein Rich pistachios.","Ingredients: Durum maida.","Ingredients: Durum refined wheat flour.","Ingredients: Durum garbanzo bean.","Ingredients: Durum chickpea.","Ingredients: Durum garbanzo beans.","Ingredients: Durum cashew.","Ingredients: Durum cashew nuts.","Ingredients: Durum cashews.","Ingredients: Durum pistachio.","Ingredients: Durum pistachio nuts.","Ingredients: Durum pistachios.","Ingredients: garbanzo bean flour.","Ingredients: garbanzo beans flour.","Ingredients: cashew flour.","Ingredients: pistachio flour.","Ingredients: Protein Rich Maida.","Ingredients: Protein Prachur Maida.","Ingredients: Durum Maida.","Ingredients: Salted Almonds & Cashews."]
for _texts in (CORPUS, PASTE):
    _texts.extend(t for t in _POWDER_5_TEXTS if t not in _texts)

# nalt-names-6: synthetic source/form controls, not a measured label or OCR accuracy sample.
_NALT_6_NAMES = ["mushroom", "lettuce", "mangosteen", "durian", "rambutan", "aubergine", "aubergines", "brinjal", "brinjals", "filbert", "filberts", "hazel nut", "hazel nuts", "soy bean", "soy beans", "chick pea", "chick peas", "linseed", "linseeds", "flaxseeds", "sunflowerseed", "sunflowerseeds", "blackcurrant", "blackcurrants", "sweetpotato", "sweetpotatoes", "passionfruit", "passionfruits", "kiwi fruit", "kiwi fruits", "water cress"]
_NALT_6_FORMS = ["{t}", "Fresh {t}", "Dried {t}", "Salted {t}", "{t} (Salt)", "{t} (Sugar)", "Canned {t}", "{t} juice", "{t} extract", "{t} puree", "{t} powder", "100% {t} powder", "Whole {t} powder", "{t} powder (100% Rice)", "{t} (Banana Powder)", "100% {t} (Banana Powder)", "{t} (Milk Powder)", "Mango ({t} Powder)", "Mango (100% {t} Powder)", "Cashew Nuts ({t} Powder)", "Cashew Nuts (100% {t} Powder)"]
_NALT_6_TEXTS = ["Ingredients: " + f.format(t=t) + "." for t in _NALT_6_NAMES for f in _NALT_6_FORMS]
_NALT_6_TEXTS += ["Ingredients: Flaxseed Oil.", "Ingredients: Cranberry.", "Ingredients: Dried Cranberries (Sugar).", "Ingredients: Tamarind.", "Ingredients: Coconut.", "Ingredients: Celery Powder."]
for _texts in (CORPUS, PASTE):
    _texts.extend(t for t in _NALT_6_TEXTS if t not in _texts)


# nalt-names-7: current-source naming/forms. Synthetic, not image or label accuracy.
_NALT_7_MANIFEST = json.loads((ROOT / "evaluation" / "nalt_names_7" / "admission.json").read_text())
_NALT_7_NAMES = [x["name"] for x in _NALT_7_MANIFEST["aliases"]] + ["peanut"]
_NALT_7_FORMS = ["{t}", "Raw {t}", "Dried {t}", "Roasted {t}", "Salted {t}", "Sugared {t}", "{t} (Salt)", "{t} (Sugar)", "{t} (Brine)", "{t} (XQ9)", "{t} powder", "100% {t} powder", "Whole {t} powder", "{t} powder (100% Rice)", "{t} powder (Sugar)", "{t} butter", "{t} flour", "{t} oil", "{t} extract", "{t} juice", "{t} solids", "{t} protein isolate", "Mango ({t} Powder)", "Mango (100% {t} Powder)", "Cashew Nuts ({t} Powder)", "Cashew Nuts (100% {t} Powder)", "{t} (Milk Powder)", "{t} (Banana Powder)", "{t} (100% Rice, Banana Powder)", "Hydrogenated {t}", "Interesterified {t}", "{t} (Rice)", "{t} (Palm, Salt)"]
_NALT_7_TEXTS = ["Ingredients: " + f.format(t=t) + "." for t in _NALT_7_NAMES for f in _NALT_7_FORMS]
_NALT_7_TEXTS += ["Ingredients: " + t + "." for t in ["Swiss Chard", "Groundnut Oil", "Flaxseed Oil", "Bovine Milk Solids", "Chard", "Star Anise", "Winter Melon", "Haricot Beans", "Catjang Peas", "Cranberry", "Tamarind", "Coconut", "Celery"]]
for _texts in (CORPUS, PASTE):
    _texts.extend(t for t in _NALT_7_TEXTS if t not in _texts)


# nalt-names-8: source-reviewed food/name/form controls, synthetic not OCR accuracy.
_NALT_8_MANIFEST = json.loads((ROOT / "evaluation" / "nalt_names_8" / "admission.json").read_text())
_NALT_8_NAMES = [a["name"] for a in _NALT_8_MANIFEST["aliases"]] + [r["term"] for r in _NALT_8_MANIFEST["new_foods"]]
_NALT_8_FORMS = ['{t}', 'Raw {t}', 'Fresh {t}', 'Frozen {t}', 'Dried {t}', 'Roasted {t}', 'Salted {t}', 'Sugared {t}', '{t} (Salt)', '{t} (Sugar)', '{t} (Brine)', '{t} (XQ9)', '{t} powder', '100% {t} powder', 'Whole {t} powder', '{t} powder (100% Rice)', '{t} powder (Sugar)', '{t} butter', '{t} flour', '{t} oil', '{t} extract', '{t} juice', '{t} solids', '{t} protein isolate', 'Mango ({t} Powder)', 'Mango (100% {t} Powder)', 'Cashew Nuts ({t} Powder)', 'Cashew Nuts (100% {t} Powder)', '{t} (Milk Powder)', '{t} (Banana Powder)', '{t} (100% Rice, Banana Powder)', 'Hydrogenated {t}', 'Interesterified {t}', '{t} (Rice)', '{t} (Palm, Salt)']
_NALT_8_TEXTS = ["Ingredients: " + f.format(t=t) + "." for t in _NALT_8_NAMES for f in _NALT_8_FORMS]
_NALT_8_TEXTS += ["Ingredients: " + t + "." for t in _NALT_8_MANIFEST["held"]]
for _texts in (CORPUS, PASTE):
    _texts.extend(t for t in _NALT_8_TEXTS if t not in _texts)


# nalt-names-9: current-source names and forms, synthetic not OCR-image accuracy.
_NALT_9_MANIFEST = json.loads((ROOT / "evaluation" / "nalt_names_9" / "admission.json").read_text())
_NALT_9_NAMES = [a["name"] for a in _NALT_9_MANIFEST["aliases"]] + [r["term"] for r in _NALT_9_MANIFEST["new_foods"]]
_NALT_9_TEXTS = ["Ingredients: " + f.format(t=t) + "." for t in _NALT_9_NAMES for f in _NALT_8_FORMS]
_NALT_9_TEXTS += ["Ingredients: " + t + "." for t in _NALT_9_MANIFEST["held"]]
for _texts in (CORPUS, PASTE):
    _texts.extend(t for t in _NALT_9_TEXTS if t not in _texts)


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


# nalt-names-10: synthetic category/form controls, not measured label accuracy.
_m10 = json.loads((ROOT / 'evaluation/nalt_names_10/admission.json').read_text())
_f10 = ['{t}', 'Raw {t}', 'Fresh {t}', 'Frozen {t}', 'Dried {t}', 'Roasted {t}', 'Salted {t}', '{t} (Salt)', '{t} (Sugar)', '{t} powder', '100% {t} powder', 'Whole {t} powder', '{t} powder (Sugar)', '{t} extract', 'Mango ({t} Powder)', 'Mango (100% {t} Powder)']
_t10 = [r['term'] for r in _m10['new_foods']] + [r['name'] for r in _m10['aliases']]
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=n) + '.' for n in _t10 for f in _f10)
# cheese-g3-1 parity: every staged cheese term in sole, listed, bracketed and conditioned forms.
import csv as _csv
_CHEESE_TERMS = [r["term"] for r in _csv.DictReader((ROOT / "evaluation" / "cheese_rows_24" / "staged_rows.csv").open(newline=""))]
_fc = ['{t}', '{t}, Salt', 'Salt, {t}', '{t} (Salt)', '{t} powder', 'Smoked {t}', 'Grated {t}', 'Processed {t}', '{t} (Cheddar)', 'Milk, {t}', '{t}, Wheat Flour', 'Dried {t}', 'Salted {t}']
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for t in _CHEESE_TERMS for f in _fc)
# cured-meat-g3-1 parity: staged cured-meat terms in sole, listed, bracketed and conditioned forms.
_CURED_TERMS = [r["term"] for r in _csv.DictReader((ROOT / "evaluation" / "cured_meat_24" / "staged_rows.csv").open(newline=""))]
_fcm = ['{t}', '{t}, Salt', 'Salt, {t}', '{t} (Pork)', '{t} powder', 'Smoked {t}', 'Raw {t}', '{t} bits', 'Meatless {t}', 'Turkey {t}', 'Milk, {t}', '{t}, Wheat Flour', 'Dried {t}', 'Salted {t}']
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for t in _CURED_TERMS for f in _fcm)
# yoghurt-g1-1 parity.
_YOG_TERMS = [r["term"] for r in _csv.DictReader((ROOT / "evaluation" / "yoghurt_24" / "staged_rows.csv").open(newline=""))] + ["plain yogurt"]
_fyg = ['{t}', '{t}, Salt', '{t}, Sugar', '{t} (Milk)', '{t} powder', 'Fruit {t}', 'Frozen {t}', '{t}, Plain yoghurt', 'Greek {t}', 'Milk, {t}', '{t} flavour', 'Sweetened {t}', '{t} drink', 'Dried {t}', 'Yoghurt', 'Yogurt', 'Yoghurt, Sugar']
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for t in _YOG_TERMS for f in _fyg)
# smoked-fish-g3-1 parity.
_SF_TERMS = [r["term"] for r in _csv.DictReader((ROOT / "evaluation" / "smoked_fish_24" / "staged_rows.csv").open(newline=""))]
_fsf = ['{t}', '{t}, Salt', 'Salt, {t}', '{t} (Atlantic)', '{t} powder', 'Canned {t}', 'Salted {t}', '{t} pate', '{t} flavour', 'Raw {t}', 'Milk, {t}', '{t}, Dill']
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for t in _SF_TERMS for f in _fsf)
# indian-alias-24 parity: each alias and its English term in sole, listed and conditioned forms.
_IA = [(r["from"], r["to"]) for r in _csv.DictReader((ROOT / "evaluation" / "indian_alias_24" / "aliases.csv").open(newline=""))]
_fia = ['{t}', '{t}, Salt', '{t} powder', 'Sugar, {t}', 'Wheat flour, {t}', '{t} (5%), Water', 'Milk, Sugar, {t}', 'Dried {t}']
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for a, b in _IA for t in (a.title(), b.title()) for f in _fia)
# indian-alias-24b parity (pulses).
_IAB = [(r["from"], r["to"]) for r in _csv.DictReader((ROOT / "evaluation" / "indian_alias_24" / "aliases_b.csv").open(newline=""))]
_fiab = ['{t}', '{t}, Salt', 'Sugar, {t}', 'Wheat flour, {t}', '{t} (5%), Water', 'Dried {t}', 'Canned {t}', '{t} in brine', 'Roasted {t}', '{t} flour']
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for a, b in _IAB for t in (a.title(), b.title()) for f in _fiab)
    _target.extend('Ingredients: ' + t + '.' for t in ['Chana dal', 'Chana dal, Salt', 'Chana', 'Urd dal', 'Masur dal'])
# indian-alias-24c parity (oils).
_IAC = [(r["from"], r["to"]) for r in _csv.DictReader((ROOT / "evaluation" / "indian_alias_24" / "aliases_c.csv").open(newline=""))]
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for a, b in _IAC for t in (a.title(), b.title()) for f in _fiab)
    _target.extend('Ingredients: ' + t + '.' for t in ['Rapeseed oil', 'Toria oil', 'Til ka tel', 'Sesame seed oil'])
# tamarind-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + t + '.' for t in ['Tamarind', 'Tamarinds', 'Dried tamarind', 'Seedless tamarind', 'Tamarind, Salt', 'Tamarind, Sugar', 'Tamarind and Jaggery', 'Tamarind pulp', 'Tamarind paste', 'Tamarind puree', 'Tamarind concentrate', 'Tamarind (pulp)', 'Tamarind juice', 'Tamarind powder', 'Tamarind extract', 'Tamarind seed powder', 'Tamarind kernel powder', 'Tamarind gum', 'Tamarind nectar', 'Tamarind chutney', 'Sweetened tamarind', 'Tamarind in brine', 'Tamarind (E412)', 'Roasted tamarind'])
# indian-alias-24d parity (moongphali).
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for t in ('Moongphali', 'Peanuts') for f in _fiab + ['{t} oil', '{t} butter', 'Roasted {t}', 'Salted {t}', '{t} powder'])
# flour-24 parity.
_fl = ['{t}', '{t}, Salt', 'Salted {t}', '{t} (Salt)', 'Sugar, {t}', 'Wheat flour, {t}', '{t} (5%), Water', 'Dried {t}', 'Roasted {t}', '{t} powder', '{t} starch', 'Bleached {t}', 'Chutney ({t}, Chilli)', '{t} 100%', 'Hydrogenated {t}']
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for t in ('Cassava flour', 'Tapioca flour', 'Pearl millet flour', 'Bajra flour', 'Ragi flour', 'Jowar flour', 'Sorghum flour') for f in _fl)
# grits-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for t in ('Corn grits', 'Maize grits', 'Cornmeal') for f in _fl + ['Instant {t}', 'Enriched {t}', 'Cooked {t}', '{t} (Butter flavour)', 'White {t}'])
# millets-24 parity.
_ml = ['{t}', '{t}, Salt', 'Sugar, {t}', 'Dried {t}', 'Roasted {t}', '{t} flour', 'Puffed {t}', 'Cooked {t}', '{t} (Salt)', 'Instant {t}', '{t} 100%']
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for t in ('Teff', 'Amaranth grain', 'Amaranth', 'Kodo millet', 'Kodo', 'Little millet', 'Kutki', 'Barnyard millet', 'Sanwa', 'Jhangora', 'Proso millet', 'Cheena', 'Mandua', 'Kangni', 'Kakun', 'Kuttu', 'Kabuli chana', 'Arhar') for f in _ml)
    _target.extend('Ingredients: ' + t + '.' for t in ['Arhar dal', 'Arhar dal, Salt', 'Split arhar', 'Arhar flour'])
# pulses-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for t in ('Horse gram', 'Kulthi', 'Moth bean') for f in _ml)
# oils-24 parity.
_ol = ['{t}', '{t}, Salt', 'Hydrogenated {t}', '{t} (antioxidant)', '{t} blend', '{t} spray', 'Refined {t}', 'Cold pressed {t}', '{t} (Sugar)', 'Sugar, {t}']
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for t in ('Mahua oil', 'Watermelon seed oil', 'Chia oil', 'Chia seeds') for f in _ol)
# sugars-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for t in ('Misri', 'Mishri', 'Golden syrup') for f in _ol)
# oils-24b parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for t in ('Taramira oil', 'Niger seed oil', 'Shea butter', 'Kokum fat', 'Mango kernel fat', 'Illipe butter', 'Shea stearin', 'Kokum', 'Niger seed', 'Mango kernel', 'Cocoa butter') for f in _ol)
# shrimp-24 parity.
_sh = ['{t}', '{t}, Salt', 'Dried {t}', '{t} powder', 'Smoked {t}', 'Canned {t}', 'Salted {t}', 'Breaded {t}', 'Fried {t}', '{t} (5%), Water', '{t} flavour', '{t} paste', '{t} sauce', '{t} extract', '{t} cracker', 'Freeze dried {t}', 'Frozen {t}', 'Cooked {t}', 'Hydrogenated {t}']
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for t in ('Shrimp', 'Shrimps', 'Prawn', 'Prawns', 'Squid') for f in _sh)
# tea-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for t in ('Black tea', 'Oolong tea', 'Kangra tea', 'Tea') for f in _sh)
# milk-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for t in ('Camel milk', 'Sheep milk', 'Goat milk') for f in _sh + ['Pasteurised {t}', 'Skimmed {t}', '{t} solids', 'Milk ({t})'])
# veg-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for t in ('Cress', 'Pumpkin flowers', 'Sesbania flower', 'Winged bean leaves', 'Winged bean tuber', 'Mountain yam', 'Roselle', 'Bitter gourd', 'Fava beans', 'Broad beans') for f in _sh + ['Dried {t}', '{t} powder', 'Salted {t}', '{t} (Sugar)'])
# gourds-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for t in ('Snake gourd', 'Ridged gourd', 'Ridge gourd', 'Ivy gourd', 'Tindori', 'Tinda', 'Bottle gourd', 'Calabash gourd', 'Bitter melon', 'Karela', 'Calabash') for f in _sh + ['Dried {t}', '{t} powder', 'Salted {t}', '{t} (Sugar)'])
# names-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for t in ('Brinjal', 'Aubergine', 'Radish', 'Mooli', 'Daikon', "Lady's finger", 'Ash gourd', 'Wax gourd', 'Dasheen', 'Eddoe', 'Amla', 'Aonla', 'Emblic myrobalan', 'Cocoyam', 'Winter melon') for f in _sh + ['Dried {t}', '{t} powder', 'Salted {t}', '{t} (Sugar)'])
# names-24b parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for t in ('Lablab', 'Wing bean', 'Goa bean', 'Black-eyed peas', 'Black-eye pea', 'Ceylon spinach', 'Malabar nightshade', 'Water chestnuts', 'Vine spinach', 'Basella', 'Indian spinach') for f in _sh + ['Dried {t}', '{t} powder', 'Salted {t}', '{t} (Sugar)', 'Canned {t}'])
# india-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for t in ('Pointed gourd', 'Parwal', 'Palwal', 'Cluster beans', 'Cluster bean', 'Bael', 'Bengal quince', 'Guar', 'Guar gum', 'Wood apple') for f in _sh + ['Dried {t}', '{t} powder', 'Salted {t}', '{t} (Sugar)', 'Canned {t}'])
# tomato-g3-1 parity: staged tomato concentrate terms in stated, unstated, bracketed and conditioned forms.
_TOMATO_TERMS = [r["term"] for r in _csv.DictReader((ROOT / "evaluation" / "tomato_rows_24" / "staged_rows.csv").open(newline=""))]
_ft = ['{t}', '{t}, Salt', '{t}, Sugar', '{t}, Sugar, Salt', '{t} (Salt)', '{t} (Tomato, Salt)', '{t} (28°B)', '{t}, Salt, Water', '{t}, Salt, Citric Acid', '{t} powder', 'Dried {t}, Salt', '{t}, {t}, Salt', '{t} (Tomato)', '{t}, Salt, Wheat Flour', 'Salt, {t}', 'Milk, {t}']
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for t in _TOMATO_TERMS for f in _ft)
# canned-fish-g3-1 parity.
_CANNED_TERMS = [r["term"] for r in _csv.DictReader((ROOT / "evaluation" / "canned_fish_rows_24" / "staged_rows.csv").open(newline=""))]
_fcf = ['{t}', '{t}, Water, Salt', '{t}, Sunflower Oil', '{t} (in Oil)', '{t} (Water, Salt)', '{t}, Tomato Sauce', '{t}, Soy Protein', '{t} powder', '{t}, {t}', '{t} (Tuna, Salt)', 'Smoked {t}', '{t}, Milk', 'Salt, {t}', '{t}, Colour (102)']
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for t in _CANNED_TERMS for f in _fcf)
# wheat-semolina alias parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Wheat semolina', 'Wheat semolina (75%)', 'Wheat Semolina, Salt', 'Wheat semolina, Maltodextrin', 'Wheat semolina (Salt)', 'Wheat semolina powder'])
# curry-leaves-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Curry leaves', 'Curry leaves, Salt', 'Dried curry leaves', 'Curry leaves powder', 'Curry leaves (Colour)', 'Curry leaves, Maltodextrin', 'Wheat semolina (75%), Curry leaves, Mustard', 'Salt, Curry leaves'])
# chives-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Chives', 'Chives, Salt', 'Dried chives', 'Chives powder', 'Chives (Colour)', 'Chives, Maltodextrin', 'Wheat semolina (75%), Chives, Mustard', 'Salt, Chives'])
# grains-rare-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Einkorn', 'Einkorn, Salt', 'Einkorn flour', 'Einkorn, Maltodextrin', 'Fonio', 'Fonio, Salt', 'Fonio flour', 'Fonio, Maltodextrin', 'Khorasan', 'Khorasan, Salt', 'Khorasan flour', 'Khorasan, Maltodextrin', 'Farro', 'Farro, Salt', 'Farro flour', 'Farro, Maltodextrin', 'Bulgur', 'Bulgur, Salt', 'Bulgur flour', 'Bulgur, Maltodextrin', 'Wheat semolina (75%), Bulgur, Mustard', 'Salt, Farro'])
# clause-named-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Pasta', 'Pasta, Salt', 'Pasta, Maltodextrin', 'Pasta (Salted)', 'Couscous', 'Couscous, Salt', 'Couscous, Maltodextrin', 'Couscous (Salted)', 'Polenta', 'Polenta, Salt', 'Polenta, Maltodextrin', 'Polenta (Salted)', 'Rye', 'Rye, Salt', 'Rye, Maltodextrin', 'Rye (Salted)', 'Poppy seeds', 'Poppy seeds, Salt', 'Poppy seeds, Maltodextrin', 'Poppy seeds (Salted)', 'Caraway seeds', 'Caraway seeds, Salt', 'Caraway seeds, Maltodextrin', 'Caraway seeds (Salted)', 'Hemp seeds', 'Hemp seeds, Salt', 'Hemp seeds, Maltodextrin', 'Hemp seeds (Salted)', 'Lotus seeds', 'Lotus seeds, Salt', 'Lotus seeds, Maltodextrin', 'Lotus seeds (Salted)', 'Pasta (Egg, Wheat flour)', 'Cheese pasta', 'Pasta sauce', 'Wheat semolina (75%), Couscous, Mustard'])
# group2-named-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Molasses', 'Molasses, Salt', 'Molasses, Maltodextrin', 'Molasses (Colour)', 'Dried molasses', 'Molasses, Flavour', 'Maple syrup', 'Maple syrup, Salt', 'Maple syrup, Maltodextrin', 'Maple syrup (Colour)', 'Dried maple syrup', 'Maple syrup, Flavour', 'Wheat flour, Maple syrup, Mustard', 'Maple flavoured syrup', 'Maple'])
# sweetener-names-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Wheat flour, Salt, Aspartame', 'Water, Aspartame', 'Aspartame (INS 950)', 'Wheat flour, Salt, Sodium cyclamate', 'Water, Sodium cyclamate', 'Sodium cyclamate (INS 950)', 'Wheat flour, Salt, Sucralose', 'Water, Sucralose', 'Sucralose (INS 950)', 'Wheat flour, Salt, Acesulfame potassium', 'Water, Acesulfame potassium', 'Acesulfame potassium (INS 950)', 'Wheat flour, Salt, Saccharin', 'Water, Saccharin', 'Saccharin (INS 950)', 'Wheat flour, Salt, Steviol glycosides', 'Water, Steviol glycosides', 'Steviol glycosides (INS 950)', 'Stevia', 'Water, Sweeteners (Jaggery, Sucralose)', 'Wheat flour, Salt'])
# fao-named-substances-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Wheat flour, Salt, Casein', 'Water, Casein', 'Casein (Stabiliser)', 'Wheat flour, Salt, Whey protein concentrate', 'Water, Whey protein isolate', 'Whey protein concentrate (Milk)', 'Wheat flour, Mechanically separated meat', 'Mechanically separated meat, Salt', 'Wheat flour, Fruit juice concentrate', 'Water, Lemon juice concentrate', 'Fruit juice concentrate (Apple)', 'Tomato paste', 'Orange juice from concentrate', 'Whey', 'Milk protein', 'Lactose free milk', 'Gluten free oats', 'Lactose', 'Wheat flour, Gluten', 'Milk (lactose free)', 'Gluten-free wheat flour', 'Without gluten', 'Free from gluten', 'No added lactose', 'Casein free', 'Non gluten flour'])
# hydrolysed-protein-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Wheat flour, Hydrolysed protein', 'Water, Hydrolyzed protein', 'Hydrolysed proteins, Salt', 'Wheat flour, Hydrolysed soy protein', 'Wheat flour, Hydrolyzed vegetable protein (Soy)', 'Wheat flour, Hydrolysed milk protein', 'Wheat flour, Hydrolysed protein free', 'Wheat flour, Hydrolysed collagen', 'Wheat flour, Soy protein', 'Wheat flour, Without hydrolysed protein'])
# game-meat-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Deer', 'Deer, Salt', 'Dried deer', 'Smoked deer', 'Deer powder', 'Deer sausage', 'Rabbit', 'Rabbit, Salt', 'Dried rabbit', 'Smoked rabbit', 'Rabbit powder', 'Rabbit sausage', 'Bison', 'Bison, Salt', 'Dried bison', 'Smoked bison', 'Bison powder', 'Bison sausage', 'Boar', 'Boar, Salt', 'Dried boar', 'Smoked boar', 'Boar powder', 'Boar sausage', 'Moose', 'Moose, Salt', 'Dried moose', 'Smoked moose', 'Moose powder', 'Moose sausage', 'Caribou', 'Caribou, Salt', 'Dried caribou', 'Smoked caribou', 'Caribou powder', 'Caribou sausage', 'Antelope', 'Antelope, Salt', 'Dried antelope', 'Smoked antelope', 'Antelope powder', 'Antelope sausage', 'Wild boar', 'Reindeer'])
# lemon-grass-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Lemon grass', 'Lemon grass, Salt', 'Rice, Lemon grass', 'Lemon grass (5%), Rice', 'Dried lemon grass, Rice', 'Lemon grass powder, Rice', 'Lemon grass paste, Rice', 'Lemon grass flavour', 'Lemongrass', 'Lemongrass, Salt', 'Rice, Lemongrass', 'Lemongrass (5%), Rice', 'Dried lemongrass, Rice', 'Lemongrass powder, Rice', 'Lemongrass paste, Rice', 'Lemongrass flavour'])
# algae-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Kelp, Salt', 'Dried kelp, Salt', 'Kelp powder, Salt', 'Kelp extract, Salt', 'Colour (Kelp)', 'Kelp flavour', 'Laver, Salt', 'Dried laver, Salt', 'Laver powder, Salt', 'Laver extract, Salt', 'Colour (Laver)', 'Laver flavour', 'Wakame, Salt', 'Dried wakame, Salt', 'Wakame powder, Salt', 'Wakame extract, Salt', 'Colour (Wakame)', 'Wakame flavour', 'Spirulina, Salt', 'Dried spirulina, Salt', 'Spirulina powder, Salt', 'Spirulina extract, Salt', 'Colour (Spirulina)', 'Spirulina flavour'])
# dried-fruit-24 and produce-gaps-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Raisins', 'Raisins, Salt', 'Raisins, Sugar', 'Dried raisins', 'Raisins powder', 'Raisins flavour', 'Rice, Raisins', 'Prunes', 'Prunes, Salt', 'Prunes, Sugar', 'Dried prunes', 'Prunes powder', 'Prunes flavour', 'Rice, Prunes', 'Jicama', 'Jicama, Salt', 'Jicama, Sugar', 'Dried jicama', 'Jicama powder', 'Jicama flavour', 'Rice, Jicama', 'Water chestnuts, Salt', 'Water chestnuts, Sugar', 'Dried water chestnuts', 'Water chestnuts powder', 'Water chestnuts flavour', 'Rice, Water chestnuts', 'Cloud ears', 'Cloud ears, Salt', 'Cloud ears, Sugar', 'Dried cloud ears', 'Cloud ears powder', 'Cloud ears flavour', 'Rice, Cloud ears', 'Goji berries', 'Goji berries, Salt', 'Goji berries, Sugar', 'Dried goji berries', 'Goji berries powder', 'Goji berries flavour', 'Rice, Goji berries', 'Sapote', 'Sapote, Salt', 'Sapote, Sugar', 'Dried sapote', 'Sapote powder', 'Sapote flavour', 'Rice, Sapote', 'Hearts of palm', 'Hearts of palm, Salt', 'Hearts of palm, Sugar', 'Dried hearts of palm', 'Hearts of palm powder', 'Hearts of palm flavour', 'Rice, Hearts of palm', 'Fiddlehead ferns', 'Fiddlehead ferns, Salt', 'Fiddlehead ferns, Sugar', 'Dried fiddlehead ferns', 'Fiddlehead ferns powder', 'Fiddlehead ferns flavour', 'Rice, Fiddlehead ferns', 'Raisin, Salt', 'Prune, Salt'])
# fardet-markers-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Wheat flour, Glucose syrup', 'Water, Liquid glucose', 'Wheat flour, Malt extract', 'Wheat flour, Barley malt extract', 'Wheat flour, Dried glucose syrup', 'Wheat flour, Glucose', 'Wheat flour, Sugar syrup', 'Wheat flour, Malted barley', 'Wheat flour, Without malt extract', 'Wheat flour, Glucose syrup-free', 'Wheat flour, Free from glucose syrup'])
# game-meat-24b parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Emu', 'Emu, Salt', 'Dried emu', 'Smoked emu', 'Emu powder', 'Emu sausage', 'Elk', 'Elk, Salt', 'Dried elk', 'Smoked elk', 'Elk powder', 'Elk sausage', 'Horse', 'Horse, Salt', 'Dried horse', 'Smoked horse', 'Horse powder', 'Horse sausage', 'Beaver', 'Beaver, Salt', 'Dried beaver', 'Smoked beaver', 'Beaver powder', 'Beaver sausage', 'Squirrel', 'Squirrel, Salt', 'Dried squirrel', 'Smoked squirrel', 'Squirrel powder', 'Squirrel sausage', 'Muskrat', 'Muskrat, Salt', 'Dried muskrat', 'Smoked muskrat', 'Muskrat powder', 'Muskrat sausage', 'Mutton', 'Goat milk', 'Goat', 'Milk (Goat)', 'Goat cheese'])
# beetroot-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Beetroot', 'Beetroot, Salt', 'Dried beetroot', 'Beetroot red', 'Beet red powder', 'Beetroot colour', 'Beetroot (5%), Water', 'Wheat flour, Beetroot red', 'Beets'])
# cofid-fish-fruit-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Plaice', 'Plaice, Salt', 'Dried Plaice', 'Plaice powder', 'Smoked Plaice', 'Plaice flavour', 'Hake', 'Hake, Salt', 'Dried Hake', 'Hake powder', 'Smoked Hake', 'Hake flavour', 'Bream', 'Bream, Salt', 'Dried Bream', 'Bream powder', 'Smoked Bream', 'Bream flavour', 'Coley', 'Coley, Salt', 'Dried Coley', 'Coley powder', 'Smoked Coley', 'Coley flavour', 'Sprats', 'Sprats, Salt', 'Dried Sprats', 'Sprats powder', 'Smoked Sprats', 'Sprats flavour', 'Skate', 'Skate, Salt', 'Dried Skate', 'Skate powder', 'Smoked Skate', 'Skate flavour', 'Rohu', 'Rohu, Salt', 'Dried Rohu', 'Rohu powder', 'Smoked Rohu', 'Rohu flavour', 'Katla', 'Katla, Salt', 'Dried Katla', 'Katla powder', 'Smoked Katla', 'Katla flavour', 'Hilsa', 'Hilsa, Salt', 'Dried Hilsa', 'Hilsa powder', 'Smoked Hilsa', 'Hilsa flavour', 'Redcurrants', 'Redcurrants, Salt', 'Dried Redcurrants', 'Redcurrants powder', 'Smoked Redcurrants', 'Redcurrants flavour', 'Whitecurrants', 'Whitecurrants, Salt', 'Dried Whitecurrants', 'Whitecurrants powder', 'Smoked Whitecurrants', 'Whitecurrants flavour', 'Damsons', 'Damsons, Salt', 'Dried Damsons', 'Damsons powder', 'Smoked Damsons', 'Damsons flavour', 'Greengages', 'Greengages, Salt', 'Dried Greengages', 'Greengages powder', 'Smoked Greengages', 'Greengages flavour', 'Swede', 'Salmon'])
# culinary-gaps-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Potato starch', 'Potato starch, Salt', 'Modified Potato starch', 'Hydrogenated Potato starch', 'Potato starch powder', 'Potato starch, Emulsifier', 'Rice starch', 'Rice starch, Salt', 'Modified Rice starch', 'Hydrogenated Rice starch', 'Rice starch powder', 'Rice starch, Emulsifier', 'Wheat starch', 'Wheat starch, Salt', 'Modified Wheat starch', 'Hydrogenated Wheat starch', 'Wheat starch powder', 'Wheat starch, Emulsifier', 'Pink salt', 'Cassava starch', 'Himalayan salt', 'Kosher salt', 'Hemp seed oil', 'Pumpkin seed oil'])
# generic-fish-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Cod', 'Cod, Salt', 'Dried cod', 'Smoked cod', 'Cod powder', 'Cod stick', 'Halibut', 'Halibut, Salt', 'Dried halibut', 'Smoked halibut', 'Halibut powder', 'Halibut stick', 'Pollock', 'Pollock, Salt', 'Dried pollock', 'Smoked pollock', 'Pollock powder', 'Pollock stick', 'Flounder', 'Flounder, Salt', 'Dried flounder', 'Smoked flounder', 'Flounder powder', 'Flounder stick', 'Crab', 'Crab, Salt', 'Dried crab', 'Smoked crab', 'Crab powder', 'Crab stick', 'Lobster', 'Lobster, Salt', 'Dried lobster', 'Smoked lobster', 'Lobster powder', 'Lobster stick'])
# claim-wording abstention parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Rice, Salt (source of lactose)', 'Rice, Sugar (high in fructose)', 'Oats (source of soluble fibre), Maltodextrin', 'Oats (rich in casein), Lactose', 'Wheat flour, Milk solids (source of lactose)', 'Rice, Salt (lactose free)', 'Rice, Salt (source of Lactose free)'])
# fibre-marker-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Wheat flour, soluble fibre', 'Water, Insoluble fiber', 'Oats (source of soluble fibre), Salt', 'Oats (rich in lactose), Salt', 'Oats (high in insoluble fibre)', 'Oat fibre, Salt', 'Wheat flour, dietary fibre'])
# triticale-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Triticale', 'Triticale, Salt', 'Triticale flour', 'Roasted triticale', 'Triticale flakes', 'Triticale flavour'])
# poultry-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Quail', 'Quail, Salt', 'Dried quail', 'Smoked quail', 'Quail powder', 'Quail sausage', 'Quail flavour', 'Pheasant', 'Pheasant, Salt', 'Dried pheasant', 'Smoked pheasant', 'Pheasant powder', 'Pheasant sausage', 'Pheasant flavour', 'Ostrich', 'Ostrich, Salt', 'Dried ostrich', 'Smoked ostrich', 'Ostrich powder', 'Ostrich sausage', 'Ostrich flavour', 'Guinea hen', 'Guinea hen, Salt', 'Dried guinea hen', 'Smoked guinea hen', 'Guinea hen powder', 'Guinea hen sausage', 'Guinea hen flavour'])
PAIRS = [(t, 'ocr') for t in CORPUS] + [(t, 'text') for t in PASTE]
TOTAL = len(PAIRS)

# nalt-names-11: synthetic food-name/form controls, not measured label accuracy.
_m11 = json.loads((ROOT / 'evaluation/nalt_names_11/admission.json').read_text())
_f11 = ['{t}', 'Raw {t}', 'Fresh {t}', 'Frozen {t}', 'Dried {t}', 'Roasted {t}', 'Salted {t}', '{t} (Salt)', '{t} (Sugar)', '{t} powder', '100% {t} powder', 'Whole {t} powder', '{t} powder (Sugar)', '{t} extract', '{t} butter', '{t} oil', 'Mango ({t} Powder)', 'Mango (100% {t} Powder)']
_t11 = [r['term'] for r in _m11['new_foods']] + [r['name'] for r in _m11['aliases']]
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=n) + '.' for n in _t11 for f in _f11)
# cheese-g3-1 parity: every staged cheese term in sole, listed, bracketed and conditioned forms.
import csv as _csv
_CHEESE_TERMS = [r["term"] for r in _csv.DictReader((ROOT / "evaluation" / "cheese_rows_24" / "staged_rows.csv").open(newline=""))]
_fc = ['{t}', '{t}, Salt', 'Salt, {t}', '{t} (Salt)', '{t} powder', 'Smoked {t}', 'Grated {t}', 'Processed {t}', '{t} (Cheddar)', 'Milk, {t}', '{t}, Wheat Flour', 'Dried {t}', 'Salted {t}']
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for t in _CHEESE_TERMS for f in _fc)
# tomato-g3-1 parity: staged tomato concentrate terms in stated, unstated, bracketed and conditioned forms.
_TOMATO_TERMS = [r["term"] for r in _csv.DictReader((ROOT / "evaluation" / "tomato_rows_24" / "staged_rows.csv").open(newline=""))]
_ft = ['{t}', '{t}, Salt', '{t}, Sugar', '{t}, Sugar, Salt', '{t} (Salt)', '{t} (Tomato, Salt)', '{t} (28°B)', '{t}, Salt, Water', '{t}, Salt, Citric Acid', '{t} powder', 'Dried {t}, Salt', '{t}, {t}, Salt', '{t} (Tomato)', '{t}, Salt, Wheat Flour', 'Salt, {t}', 'Milk, {t}']
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for t in _TOMATO_TERMS for f in _ft)
# canned-fish-g3-1 parity.
_CANNED_TERMS = [r["term"] for r in _csv.DictReader((ROOT / "evaluation" / "canned_fish_rows_24" / "staged_rows.csv").open(newline=""))]
_fcf = ['{t}', '{t}, Water, Salt', '{t}, Sunflower Oil', '{t} (in Oil)', '{t} (Water, Salt)', '{t}, Tomato Sauce', '{t}, Soy Protein', '{t} powder', '{t}, {t}', '{t} (Tuna, Salt)', 'Smoked {t}', '{t}, Milk', 'Salt, {t}', '{t}, Colour (102)']
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for t in _CANNED_TERMS for f in _fcf)
# wheat-semolina alias parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Wheat semolina', 'Wheat semolina (75%)', 'Wheat Semolina, Salt', 'Wheat semolina, Maltodextrin', 'Wheat semolina (Salt)', 'Wheat semolina powder'])
# curry-leaves-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Curry leaves', 'Curry leaves, Salt', 'Dried curry leaves', 'Curry leaves powder', 'Curry leaves (Colour)', 'Curry leaves, Maltodextrin', 'Wheat semolina (75%), Curry leaves, Mustard', 'Salt, Curry leaves'])
# chives-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Chives', 'Chives, Salt', 'Dried chives', 'Chives powder', 'Chives (Colour)', 'Chives, Maltodextrin', 'Wheat semolina (75%), Chives, Mustard', 'Salt, Chives'])
# grains-rare-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Einkorn', 'Einkorn, Salt', 'Einkorn flour', 'Einkorn, Maltodextrin', 'Fonio', 'Fonio, Salt', 'Fonio flour', 'Fonio, Maltodextrin', 'Khorasan', 'Khorasan, Salt', 'Khorasan flour', 'Khorasan, Maltodextrin', 'Farro', 'Farro, Salt', 'Farro flour', 'Farro, Maltodextrin', 'Bulgur', 'Bulgur, Salt', 'Bulgur flour', 'Bulgur, Maltodextrin', 'Wheat semolina (75%), Bulgur, Mustard', 'Salt, Farro'])
# clause-named-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Pasta', 'Pasta, Salt', 'Pasta, Maltodextrin', 'Pasta (Salted)', 'Couscous', 'Couscous, Salt', 'Couscous, Maltodextrin', 'Couscous (Salted)', 'Polenta', 'Polenta, Salt', 'Polenta, Maltodextrin', 'Polenta (Salted)', 'Rye', 'Rye, Salt', 'Rye, Maltodextrin', 'Rye (Salted)', 'Poppy seeds', 'Poppy seeds, Salt', 'Poppy seeds, Maltodextrin', 'Poppy seeds (Salted)', 'Caraway seeds', 'Caraway seeds, Salt', 'Caraway seeds, Maltodextrin', 'Caraway seeds (Salted)', 'Hemp seeds', 'Hemp seeds, Salt', 'Hemp seeds, Maltodextrin', 'Hemp seeds (Salted)', 'Lotus seeds', 'Lotus seeds, Salt', 'Lotus seeds, Maltodextrin', 'Lotus seeds (Salted)', 'Pasta (Egg, Wheat flour)', 'Cheese pasta', 'Pasta sauce', 'Wheat semolina (75%), Couscous, Mustard'])
# group2-named-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Molasses', 'Molasses, Salt', 'Molasses, Maltodextrin', 'Molasses (Colour)', 'Dried molasses', 'Molasses, Flavour', 'Maple syrup', 'Maple syrup, Salt', 'Maple syrup, Maltodextrin', 'Maple syrup (Colour)', 'Dried maple syrup', 'Maple syrup, Flavour', 'Wheat flour, Maple syrup, Mustard', 'Maple flavoured syrup', 'Maple'])
# sweetener-names-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Wheat flour, Salt, Aspartame', 'Water, Aspartame', 'Aspartame (INS 950)', 'Wheat flour, Salt, Sodium cyclamate', 'Water, Sodium cyclamate', 'Sodium cyclamate (INS 950)', 'Wheat flour, Salt, Sucralose', 'Water, Sucralose', 'Sucralose (INS 950)', 'Wheat flour, Salt, Acesulfame potassium', 'Water, Acesulfame potassium', 'Acesulfame potassium (INS 950)', 'Wheat flour, Salt, Saccharin', 'Water, Saccharin', 'Saccharin (INS 950)', 'Wheat flour, Salt, Steviol glycosides', 'Water, Steviol glycosides', 'Steviol glycosides (INS 950)', 'Stevia', 'Water, Sweeteners (Jaggery, Sucralose)', 'Wheat flour, Salt'])
# fao-named-substances-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Wheat flour, Salt, Casein', 'Water, Casein', 'Casein (Stabiliser)', 'Wheat flour, Salt, Whey protein concentrate', 'Water, Whey protein isolate', 'Whey protein concentrate (Milk)', 'Wheat flour, Mechanically separated meat', 'Mechanically separated meat, Salt', 'Wheat flour, Fruit juice concentrate', 'Water, Lemon juice concentrate', 'Fruit juice concentrate (Apple)', 'Tomato paste', 'Orange juice from concentrate', 'Whey', 'Milk protein', 'Lactose free milk', 'Gluten free oats', 'Lactose', 'Wheat flour, Gluten', 'Milk (lactose free)', 'Gluten-free wheat flour', 'Without gluten', 'Free from gluten', 'No added lactose', 'Casein free', 'Non gluten flour'])
# hydrolysed-protein-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Wheat flour, Hydrolysed protein', 'Water, Hydrolyzed protein', 'Hydrolysed proteins, Salt', 'Wheat flour, Hydrolysed soy protein', 'Wheat flour, Hydrolyzed vegetable protein (Soy)', 'Wheat flour, Hydrolysed milk protein', 'Wheat flour, Hydrolysed protein free', 'Wheat flour, Hydrolysed collagen', 'Wheat flour, Soy protein', 'Wheat flour, Without hydrolysed protein'])
# game-meat-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Deer', 'Deer, Salt', 'Dried deer', 'Smoked deer', 'Deer powder', 'Deer sausage', 'Rabbit', 'Rabbit, Salt', 'Dried rabbit', 'Smoked rabbit', 'Rabbit powder', 'Rabbit sausage', 'Bison', 'Bison, Salt', 'Dried bison', 'Smoked bison', 'Bison powder', 'Bison sausage', 'Boar', 'Boar, Salt', 'Dried boar', 'Smoked boar', 'Boar powder', 'Boar sausage', 'Moose', 'Moose, Salt', 'Dried moose', 'Smoked moose', 'Moose powder', 'Moose sausage', 'Caribou', 'Caribou, Salt', 'Dried caribou', 'Smoked caribou', 'Caribou powder', 'Caribou sausage', 'Antelope', 'Antelope, Salt', 'Dried antelope', 'Smoked antelope', 'Antelope powder', 'Antelope sausage', 'Wild boar', 'Reindeer'])
# lemon-grass-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Lemon grass', 'Lemon grass, Salt', 'Rice, Lemon grass', 'Lemon grass (5%), Rice', 'Dried lemon grass, Rice', 'Lemon grass powder, Rice', 'Lemon grass paste, Rice', 'Lemon grass flavour', 'Lemongrass', 'Lemongrass, Salt', 'Rice, Lemongrass', 'Lemongrass (5%), Rice', 'Dried lemongrass, Rice', 'Lemongrass powder, Rice', 'Lemongrass paste, Rice', 'Lemongrass flavour'])
# algae-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Kelp, Salt', 'Dried kelp, Salt', 'Kelp powder, Salt', 'Kelp extract, Salt', 'Colour (Kelp)', 'Kelp flavour', 'Laver, Salt', 'Dried laver, Salt', 'Laver powder, Salt', 'Laver extract, Salt', 'Colour (Laver)', 'Laver flavour', 'Wakame, Salt', 'Dried wakame, Salt', 'Wakame powder, Salt', 'Wakame extract, Salt', 'Colour (Wakame)', 'Wakame flavour', 'Spirulina, Salt', 'Dried spirulina, Salt', 'Spirulina powder, Salt', 'Spirulina extract, Salt', 'Colour (Spirulina)', 'Spirulina flavour'])
# dried-fruit-24 and produce-gaps-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Raisins', 'Raisins, Salt', 'Raisins, Sugar', 'Dried raisins', 'Raisins powder', 'Raisins flavour', 'Rice, Raisins', 'Prunes', 'Prunes, Salt', 'Prunes, Sugar', 'Dried prunes', 'Prunes powder', 'Prunes flavour', 'Rice, Prunes', 'Jicama', 'Jicama, Salt', 'Jicama, Sugar', 'Dried jicama', 'Jicama powder', 'Jicama flavour', 'Rice, Jicama', 'Water chestnuts, Salt', 'Water chestnuts, Sugar', 'Dried water chestnuts', 'Water chestnuts powder', 'Water chestnuts flavour', 'Rice, Water chestnuts', 'Cloud ears', 'Cloud ears, Salt', 'Cloud ears, Sugar', 'Dried cloud ears', 'Cloud ears powder', 'Cloud ears flavour', 'Rice, Cloud ears', 'Goji berries', 'Goji berries, Salt', 'Goji berries, Sugar', 'Dried goji berries', 'Goji berries powder', 'Goji berries flavour', 'Rice, Goji berries', 'Sapote', 'Sapote, Salt', 'Sapote, Sugar', 'Dried sapote', 'Sapote powder', 'Sapote flavour', 'Rice, Sapote', 'Hearts of palm', 'Hearts of palm, Salt', 'Hearts of palm, Sugar', 'Dried hearts of palm', 'Hearts of palm powder', 'Hearts of palm flavour', 'Rice, Hearts of palm', 'Fiddlehead ferns', 'Fiddlehead ferns, Salt', 'Fiddlehead ferns, Sugar', 'Dried fiddlehead ferns', 'Fiddlehead ferns powder', 'Fiddlehead ferns flavour', 'Rice, Fiddlehead ferns', 'Raisin, Salt', 'Prune, Salt'])
# poultry-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Quail', 'Quail, Salt', 'Dried quail', 'Smoked quail', 'Quail powder', 'Quail sausage', 'Quail flavour', 'Pheasant', 'Pheasant, Salt', 'Dried pheasant', 'Smoked pheasant', 'Pheasant powder', 'Pheasant sausage', 'Pheasant flavour', 'Ostrich', 'Ostrich, Salt', 'Dried ostrich', 'Smoked ostrich', 'Ostrich powder', 'Ostrich sausage', 'Ostrich flavour', 'Guinea hen', 'Guinea hen, Salt', 'Dried guinea hen', 'Smoked guinea hen', 'Guinea hen powder', 'Guinea hen sausage', 'Guinea hen flavour'])
PAIRS = [(t, 'ocr') for t in CORPUS] + [(t, 'text') for t in PASTE]
TOTAL = len(PAIRS)

# nalt-names-12: separately reviewed fruit names/categories, synthetic controls only.
_m12 = json.loads((ROOT / 'evaluation/nalt_names_12/admission.json').read_text())
_f12 = ['{t}', 'Raw {t}', 'Fresh {t}', 'Frozen {t}', 'Dried {t}', 'Roasted {t}', 'Salted {t}', '{t} (Salt)', '{t} (Sugar)', '{t} powder', '100% {t} powder', 'Whole {t} powder', '{t} powder (Sugar)', '{t} extract', '{t} juice', 'Mango ({t} Powder)', 'Mango (100% {t} Powder)']
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=r['term']) + '.' for r in _m12['new_foods'] for f in _f12)
# cheese-g3-1 parity: every staged cheese term in sole, listed, bracketed and conditioned forms.
import csv as _csv
_CHEESE_TERMS = [r["term"] for r in _csv.DictReader((ROOT / "evaluation" / "cheese_rows_24" / "staged_rows.csv").open(newline=""))]
_fc = ['{t}', '{t}, Salt', 'Salt, {t}', '{t} (Salt)', '{t} powder', 'Smoked {t}', 'Grated {t}', 'Processed {t}', '{t} (Cheddar)', 'Milk, {t}', '{t}, Wheat Flour', 'Dried {t}', 'Salted {t}']
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for t in _CHEESE_TERMS for f in _fc)
# tomato-g3-1 parity: staged tomato concentrate terms in stated, unstated, bracketed and conditioned forms.
_TOMATO_TERMS = [r["term"] for r in _csv.DictReader((ROOT / "evaluation" / "tomato_rows_24" / "staged_rows.csv").open(newline=""))]
_ft = ['{t}', '{t}, Salt', '{t}, Sugar', '{t}, Sugar, Salt', '{t} (Salt)', '{t} (Tomato, Salt)', '{t} (28°B)', '{t}, Salt, Water', '{t}, Salt, Citric Acid', '{t} powder', 'Dried {t}, Salt', '{t}, {t}, Salt', '{t} (Tomato)', '{t}, Salt, Wheat Flour', 'Salt, {t}', 'Milk, {t}']
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for t in _TOMATO_TERMS for f in _ft)
# canned-fish-g3-1 parity.
_CANNED_TERMS = [r["term"] for r in _csv.DictReader((ROOT / "evaluation" / "canned_fish_rows_24" / "staged_rows.csv").open(newline=""))]
_fcf = ['{t}', '{t}, Water, Salt', '{t}, Sunflower Oil', '{t} (in Oil)', '{t} (Water, Salt)', '{t}, Tomato Sauce', '{t}, Soy Protein', '{t} powder', '{t}, {t}', '{t} (Tuna, Salt)', 'Smoked {t}', '{t}, Milk', 'Salt, {t}', '{t}, Colour (102)']
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for t in _CANNED_TERMS for f in _fcf)
# wheat-semolina alias parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Wheat semolina', 'Wheat semolina (75%)', 'Wheat Semolina, Salt', 'Wheat semolina, Maltodextrin', 'Wheat semolina (Salt)', 'Wheat semolina powder'])
# curry-leaves-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Curry leaves', 'Curry leaves, Salt', 'Dried curry leaves', 'Curry leaves powder', 'Curry leaves (Colour)', 'Curry leaves, Maltodextrin', 'Wheat semolina (75%), Curry leaves, Mustard', 'Salt, Curry leaves'])
# chives-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Chives', 'Chives, Salt', 'Dried chives', 'Chives powder', 'Chives (Colour)', 'Chives, Maltodextrin', 'Wheat semolina (75%), Chives, Mustard', 'Salt, Chives'])
# grains-rare-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Einkorn', 'Einkorn, Salt', 'Einkorn flour', 'Einkorn, Maltodextrin', 'Fonio', 'Fonio, Salt', 'Fonio flour', 'Fonio, Maltodextrin', 'Khorasan', 'Khorasan, Salt', 'Khorasan flour', 'Khorasan, Maltodextrin', 'Farro', 'Farro, Salt', 'Farro flour', 'Farro, Maltodextrin', 'Bulgur', 'Bulgur, Salt', 'Bulgur flour', 'Bulgur, Maltodextrin', 'Wheat semolina (75%), Bulgur, Mustard', 'Salt, Farro'])
# clause-named-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Pasta', 'Pasta, Salt', 'Pasta, Maltodextrin', 'Pasta (Salted)', 'Couscous', 'Couscous, Salt', 'Couscous, Maltodextrin', 'Couscous (Salted)', 'Polenta', 'Polenta, Salt', 'Polenta, Maltodextrin', 'Polenta (Salted)', 'Rye', 'Rye, Salt', 'Rye, Maltodextrin', 'Rye (Salted)', 'Poppy seeds', 'Poppy seeds, Salt', 'Poppy seeds, Maltodextrin', 'Poppy seeds (Salted)', 'Caraway seeds', 'Caraway seeds, Salt', 'Caraway seeds, Maltodextrin', 'Caraway seeds (Salted)', 'Hemp seeds', 'Hemp seeds, Salt', 'Hemp seeds, Maltodextrin', 'Hemp seeds (Salted)', 'Lotus seeds', 'Lotus seeds, Salt', 'Lotus seeds, Maltodextrin', 'Lotus seeds (Salted)', 'Pasta (Egg, Wheat flour)', 'Cheese pasta', 'Pasta sauce', 'Wheat semolina (75%), Couscous, Mustard'])
# group2-named-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Molasses', 'Molasses, Salt', 'Molasses, Maltodextrin', 'Molasses (Colour)', 'Dried molasses', 'Molasses, Flavour', 'Maple syrup', 'Maple syrup, Salt', 'Maple syrup, Maltodextrin', 'Maple syrup (Colour)', 'Dried maple syrup', 'Maple syrup, Flavour', 'Wheat flour, Maple syrup, Mustard', 'Maple flavoured syrup', 'Maple'])
# sweetener-names-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Wheat flour, Salt, Aspartame', 'Water, Aspartame', 'Aspartame (INS 950)', 'Wheat flour, Salt, Sodium cyclamate', 'Water, Sodium cyclamate', 'Sodium cyclamate (INS 950)', 'Wheat flour, Salt, Sucralose', 'Water, Sucralose', 'Sucralose (INS 950)', 'Wheat flour, Salt, Acesulfame potassium', 'Water, Acesulfame potassium', 'Acesulfame potassium (INS 950)', 'Wheat flour, Salt, Saccharin', 'Water, Saccharin', 'Saccharin (INS 950)', 'Wheat flour, Salt, Steviol glycosides', 'Water, Steviol glycosides', 'Steviol glycosides (INS 950)', 'Stevia', 'Water, Sweeteners (Jaggery, Sucralose)', 'Wheat flour, Salt'])
# fao-named-substances-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Wheat flour, Salt, Casein', 'Water, Casein', 'Casein (Stabiliser)', 'Wheat flour, Salt, Whey protein concentrate', 'Water, Whey protein isolate', 'Whey protein concentrate (Milk)', 'Wheat flour, Mechanically separated meat', 'Mechanically separated meat, Salt', 'Wheat flour, Fruit juice concentrate', 'Water, Lemon juice concentrate', 'Fruit juice concentrate (Apple)', 'Tomato paste', 'Orange juice from concentrate', 'Whey', 'Milk protein', 'Lactose free milk', 'Gluten free oats', 'Lactose', 'Wheat flour, Gluten', 'Milk (lactose free)', 'Gluten-free wheat flour', 'Without gluten', 'Free from gluten', 'No added lactose', 'Casein free', 'Non gluten flour'])
# hydrolysed-protein-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Wheat flour, Hydrolysed protein', 'Water, Hydrolyzed protein', 'Hydrolysed proteins, Salt', 'Wheat flour, Hydrolysed soy protein', 'Wheat flour, Hydrolyzed vegetable protein (Soy)', 'Wheat flour, Hydrolysed milk protein', 'Wheat flour, Hydrolysed protein free', 'Wheat flour, Hydrolysed collagen', 'Wheat flour, Soy protein', 'Wheat flour, Without hydrolysed protein'])
# game-meat-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Deer', 'Deer, Salt', 'Dried deer', 'Smoked deer', 'Deer powder', 'Deer sausage', 'Rabbit', 'Rabbit, Salt', 'Dried rabbit', 'Smoked rabbit', 'Rabbit powder', 'Rabbit sausage', 'Bison', 'Bison, Salt', 'Dried bison', 'Smoked bison', 'Bison powder', 'Bison sausage', 'Boar', 'Boar, Salt', 'Dried boar', 'Smoked boar', 'Boar powder', 'Boar sausage', 'Moose', 'Moose, Salt', 'Dried moose', 'Smoked moose', 'Moose powder', 'Moose sausage', 'Caribou', 'Caribou, Salt', 'Dried caribou', 'Smoked caribou', 'Caribou powder', 'Caribou sausage', 'Antelope', 'Antelope, Salt', 'Dried antelope', 'Smoked antelope', 'Antelope powder', 'Antelope sausage', 'Wild boar', 'Reindeer'])
# lemon-grass-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Lemon grass', 'Lemon grass, Salt', 'Rice, Lemon grass', 'Lemon grass (5%), Rice', 'Dried lemon grass, Rice', 'Lemon grass powder, Rice', 'Lemon grass paste, Rice', 'Lemon grass flavour', 'Lemongrass', 'Lemongrass, Salt', 'Rice, Lemongrass', 'Lemongrass (5%), Rice', 'Dried lemongrass, Rice', 'Lemongrass powder, Rice', 'Lemongrass paste, Rice', 'Lemongrass flavour'])
# algae-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Kelp, Salt', 'Dried kelp, Salt', 'Kelp powder, Salt', 'Kelp extract, Salt', 'Colour (Kelp)', 'Kelp flavour', 'Laver, Salt', 'Dried laver, Salt', 'Laver powder, Salt', 'Laver extract, Salt', 'Colour (Laver)', 'Laver flavour', 'Wakame, Salt', 'Dried wakame, Salt', 'Wakame powder, Salt', 'Wakame extract, Salt', 'Colour (Wakame)', 'Wakame flavour', 'Spirulina, Salt', 'Dried spirulina, Salt', 'Spirulina powder, Salt', 'Spirulina extract, Salt', 'Colour (Spirulina)', 'Spirulina flavour'])
# dried-fruit-24 and produce-gaps-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Raisins', 'Raisins, Salt', 'Raisins, Sugar', 'Dried raisins', 'Raisins powder', 'Raisins flavour', 'Rice, Raisins', 'Prunes', 'Prunes, Salt', 'Prunes, Sugar', 'Dried prunes', 'Prunes powder', 'Prunes flavour', 'Rice, Prunes', 'Jicama', 'Jicama, Salt', 'Jicama, Sugar', 'Dried jicama', 'Jicama powder', 'Jicama flavour', 'Rice, Jicama', 'Water chestnuts, Salt', 'Water chestnuts, Sugar', 'Dried water chestnuts', 'Water chestnuts powder', 'Water chestnuts flavour', 'Rice, Water chestnuts', 'Cloud ears', 'Cloud ears, Salt', 'Cloud ears, Sugar', 'Dried cloud ears', 'Cloud ears powder', 'Cloud ears flavour', 'Rice, Cloud ears', 'Goji berries', 'Goji berries, Salt', 'Goji berries, Sugar', 'Dried goji berries', 'Goji berries powder', 'Goji berries flavour', 'Rice, Goji berries', 'Sapote', 'Sapote, Salt', 'Sapote, Sugar', 'Dried sapote', 'Sapote powder', 'Sapote flavour', 'Rice, Sapote', 'Hearts of palm', 'Hearts of palm, Salt', 'Hearts of palm, Sugar', 'Dried hearts of palm', 'Hearts of palm powder', 'Hearts of palm flavour', 'Rice, Hearts of palm', 'Fiddlehead ferns', 'Fiddlehead ferns, Salt', 'Fiddlehead ferns, Sugar', 'Dried fiddlehead ferns', 'Fiddlehead ferns powder', 'Fiddlehead ferns flavour', 'Rice, Fiddlehead ferns', 'Raisin, Salt', 'Prune, Salt'])
# poultry-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Quail', 'Quail, Salt', 'Dried quail', 'Smoked quail', 'Quail powder', 'Quail sausage', 'Quail flavour', 'Pheasant', 'Pheasant, Salt', 'Dried pheasant', 'Smoked pheasant', 'Pheasant powder', 'Pheasant sausage', 'Pheasant flavour', 'Ostrich', 'Ostrich, Salt', 'Dried ostrich', 'Smoked ostrich', 'Ostrich powder', 'Ostrich sausage', 'Ostrich flavour', 'Guinea hen', 'Guinea hen, Salt', 'Dried guinea hen', 'Smoked guinea hen', 'Guinea hen powder', 'Guinea hen sausage', 'Guinea hen flavour'])
PAIRS = [(t, 'ocr') for t in CORPUS] + [(t, 'text') for t in PASTE]
TOTAL = len(PAIRS)

# nalt-names-13: separately sourced pulse names/categories, synthetic controls only.
_m13 = json.loads((ROOT / 'evaluation/nalt_names_13/admission.json').read_text())
_f13 = ['{t}', 'Raw {t}', 'Dried {t}', 'Roasted {t}', 'Boiled {t}', 'Salted {t}', '{t} (Salt)', '{t} (Sugar)', '{t} powder', '100% {t} powder', 'Whole {t} powder', '{t} powder (Rice)', '{t} powder (Sugar)', '{t} flour', '{t} extract', '{t} leaves', '{t} straw', '100% {t} hulls powder', '{t} forage', '{t} hay', '{t} silage', 'Mango ({t} Powder)', 'Mango (100% {t} Powder)']
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=n) + '.' for n in [r['term'] for r in _m13['new_foods']] + [a['name'] for a in _m13['aliases']] for f in _f13)
# cheese-g3-1 parity: every staged cheese term in sole, listed, bracketed and conditioned forms.
import csv as _csv
_CHEESE_TERMS = [r["term"] for r in _csv.DictReader((ROOT / "evaluation" / "cheese_rows_24" / "staged_rows.csv").open(newline=""))]
_fc = ['{t}', '{t}, Salt', 'Salt, {t}', '{t} (Salt)', '{t} powder', 'Smoked {t}', 'Grated {t}', 'Processed {t}', '{t} (Cheddar)', 'Milk, {t}', '{t}, Wheat Flour', 'Dried {t}', 'Salted {t}']
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for t in _CHEESE_TERMS for f in _fc)
# tomato-g3-1 parity: staged tomato concentrate terms in stated, unstated, bracketed and conditioned forms.
_TOMATO_TERMS = [r["term"] for r in _csv.DictReader((ROOT / "evaluation" / "tomato_rows_24" / "staged_rows.csv").open(newline=""))]
_ft = ['{t}', '{t}, Salt', '{t}, Sugar', '{t}, Sugar, Salt', '{t} (Salt)', '{t} (Tomato, Salt)', '{t} (28°B)', '{t}, Salt, Water', '{t}, Salt, Citric Acid', '{t} powder', 'Dried {t}, Salt', '{t}, {t}, Salt', '{t} (Tomato)', '{t}, Salt, Wheat Flour', 'Salt, {t}', 'Milk, {t}']
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for t in _TOMATO_TERMS for f in _ft)
# canned-fish-g3-1 parity.
_CANNED_TERMS = [r["term"] for r in _csv.DictReader((ROOT / "evaluation" / "canned_fish_rows_24" / "staged_rows.csv").open(newline=""))]
_fcf = ['{t}', '{t}, Water, Salt', '{t}, Sunflower Oil', '{t} (in Oil)', '{t} (Water, Salt)', '{t}, Tomato Sauce', '{t}, Soy Protein', '{t} powder', '{t}, {t}', '{t} (Tuna, Salt)', 'Smoked {t}', '{t}, Milk', 'Salt, {t}', '{t}, Colour (102)']
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for t in _CANNED_TERMS for f in _fcf)
# wheat-semolina alias parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Wheat semolina', 'Wheat semolina (75%)', 'Wheat Semolina, Salt', 'Wheat semolina, Maltodextrin', 'Wheat semolina (Salt)', 'Wheat semolina powder'])
# curry-leaves-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Curry leaves', 'Curry leaves, Salt', 'Dried curry leaves', 'Curry leaves powder', 'Curry leaves (Colour)', 'Curry leaves, Maltodextrin', 'Wheat semolina (75%), Curry leaves, Mustard', 'Salt, Curry leaves'])
# chives-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Chives', 'Chives, Salt', 'Dried chives', 'Chives powder', 'Chives (Colour)', 'Chives, Maltodextrin', 'Wheat semolina (75%), Chives, Mustard', 'Salt, Chives'])
# grains-rare-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Einkorn', 'Einkorn, Salt', 'Einkorn flour', 'Einkorn, Maltodextrin', 'Fonio', 'Fonio, Salt', 'Fonio flour', 'Fonio, Maltodextrin', 'Khorasan', 'Khorasan, Salt', 'Khorasan flour', 'Khorasan, Maltodextrin', 'Farro', 'Farro, Salt', 'Farro flour', 'Farro, Maltodextrin', 'Bulgur', 'Bulgur, Salt', 'Bulgur flour', 'Bulgur, Maltodextrin', 'Wheat semolina (75%), Bulgur, Mustard', 'Salt, Farro'])
# clause-named-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Pasta', 'Pasta, Salt', 'Pasta, Maltodextrin', 'Pasta (Salted)', 'Couscous', 'Couscous, Salt', 'Couscous, Maltodextrin', 'Couscous (Salted)', 'Polenta', 'Polenta, Salt', 'Polenta, Maltodextrin', 'Polenta (Salted)', 'Rye', 'Rye, Salt', 'Rye, Maltodextrin', 'Rye (Salted)', 'Poppy seeds', 'Poppy seeds, Salt', 'Poppy seeds, Maltodextrin', 'Poppy seeds (Salted)', 'Caraway seeds', 'Caraway seeds, Salt', 'Caraway seeds, Maltodextrin', 'Caraway seeds (Salted)', 'Hemp seeds', 'Hemp seeds, Salt', 'Hemp seeds, Maltodextrin', 'Hemp seeds (Salted)', 'Lotus seeds', 'Lotus seeds, Salt', 'Lotus seeds, Maltodextrin', 'Lotus seeds (Salted)', 'Pasta (Egg, Wheat flour)', 'Cheese pasta', 'Pasta sauce', 'Wheat semolina (75%), Couscous, Mustard'])
# group2-named-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Molasses', 'Molasses, Salt', 'Molasses, Maltodextrin', 'Molasses (Colour)', 'Dried molasses', 'Molasses, Flavour', 'Maple syrup', 'Maple syrup, Salt', 'Maple syrup, Maltodextrin', 'Maple syrup (Colour)', 'Dried maple syrup', 'Maple syrup, Flavour', 'Wheat flour, Maple syrup, Mustard', 'Maple flavoured syrup', 'Maple'])
# sweetener-names-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Wheat flour, Salt, Aspartame', 'Water, Aspartame', 'Aspartame (INS 950)', 'Wheat flour, Salt, Sodium cyclamate', 'Water, Sodium cyclamate', 'Sodium cyclamate (INS 950)', 'Wheat flour, Salt, Sucralose', 'Water, Sucralose', 'Sucralose (INS 950)', 'Wheat flour, Salt, Acesulfame potassium', 'Water, Acesulfame potassium', 'Acesulfame potassium (INS 950)', 'Wheat flour, Salt, Saccharin', 'Water, Saccharin', 'Saccharin (INS 950)', 'Wheat flour, Salt, Steviol glycosides', 'Water, Steviol glycosides', 'Steviol glycosides (INS 950)', 'Stevia', 'Water, Sweeteners (Jaggery, Sucralose)', 'Wheat flour, Salt'])
# fao-named-substances-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Wheat flour, Salt, Casein', 'Water, Casein', 'Casein (Stabiliser)', 'Wheat flour, Salt, Whey protein concentrate', 'Water, Whey protein isolate', 'Whey protein concentrate (Milk)', 'Wheat flour, Mechanically separated meat', 'Mechanically separated meat, Salt', 'Wheat flour, Fruit juice concentrate', 'Water, Lemon juice concentrate', 'Fruit juice concentrate (Apple)', 'Tomato paste', 'Orange juice from concentrate', 'Whey', 'Milk protein', 'Lactose free milk', 'Gluten free oats', 'Lactose', 'Wheat flour, Gluten', 'Milk (lactose free)', 'Gluten-free wheat flour', 'Without gluten', 'Free from gluten', 'No added lactose', 'Casein free', 'Non gluten flour'])
# hydrolysed-protein-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Wheat flour, Hydrolysed protein', 'Water, Hydrolyzed protein', 'Hydrolysed proteins, Salt', 'Wheat flour, Hydrolysed soy protein', 'Wheat flour, Hydrolyzed vegetable protein (Soy)', 'Wheat flour, Hydrolysed milk protein', 'Wheat flour, Hydrolysed protein free', 'Wheat flour, Hydrolysed collagen', 'Wheat flour, Soy protein', 'Wheat flour, Without hydrolysed protein'])
# game-meat-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Deer', 'Deer, Salt', 'Dried deer', 'Smoked deer', 'Deer powder', 'Deer sausage', 'Rabbit', 'Rabbit, Salt', 'Dried rabbit', 'Smoked rabbit', 'Rabbit powder', 'Rabbit sausage', 'Bison', 'Bison, Salt', 'Dried bison', 'Smoked bison', 'Bison powder', 'Bison sausage', 'Boar', 'Boar, Salt', 'Dried boar', 'Smoked boar', 'Boar powder', 'Boar sausage', 'Moose', 'Moose, Salt', 'Dried moose', 'Smoked moose', 'Moose powder', 'Moose sausage', 'Caribou', 'Caribou, Salt', 'Dried caribou', 'Smoked caribou', 'Caribou powder', 'Caribou sausage', 'Antelope', 'Antelope, Salt', 'Dried antelope', 'Smoked antelope', 'Antelope powder', 'Antelope sausage', 'Wild boar', 'Reindeer'])
# lemon-grass-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Lemon grass', 'Lemon grass, Salt', 'Rice, Lemon grass', 'Lemon grass (5%), Rice', 'Dried lemon grass, Rice', 'Lemon grass powder, Rice', 'Lemon grass paste, Rice', 'Lemon grass flavour', 'Lemongrass', 'Lemongrass, Salt', 'Rice, Lemongrass', 'Lemongrass (5%), Rice', 'Dried lemongrass, Rice', 'Lemongrass powder, Rice', 'Lemongrass paste, Rice', 'Lemongrass flavour'])
# algae-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Kelp, Salt', 'Dried kelp, Salt', 'Kelp powder, Salt', 'Kelp extract, Salt', 'Colour (Kelp)', 'Kelp flavour', 'Laver, Salt', 'Dried laver, Salt', 'Laver powder, Salt', 'Laver extract, Salt', 'Colour (Laver)', 'Laver flavour', 'Wakame, Salt', 'Dried wakame, Salt', 'Wakame powder, Salt', 'Wakame extract, Salt', 'Colour (Wakame)', 'Wakame flavour', 'Spirulina, Salt', 'Dried spirulina, Salt', 'Spirulina powder, Salt', 'Spirulina extract, Salt', 'Colour (Spirulina)', 'Spirulina flavour'])
# dried-fruit-24 and produce-gaps-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Raisins', 'Raisins, Salt', 'Raisins, Sugar', 'Dried raisins', 'Raisins powder', 'Raisins flavour', 'Rice, Raisins', 'Prunes', 'Prunes, Salt', 'Prunes, Sugar', 'Dried prunes', 'Prunes powder', 'Prunes flavour', 'Rice, Prunes', 'Jicama', 'Jicama, Salt', 'Jicama, Sugar', 'Dried jicama', 'Jicama powder', 'Jicama flavour', 'Rice, Jicama', 'Water chestnuts, Salt', 'Water chestnuts, Sugar', 'Dried water chestnuts', 'Water chestnuts powder', 'Water chestnuts flavour', 'Rice, Water chestnuts', 'Cloud ears', 'Cloud ears, Salt', 'Cloud ears, Sugar', 'Dried cloud ears', 'Cloud ears powder', 'Cloud ears flavour', 'Rice, Cloud ears', 'Goji berries', 'Goji berries, Salt', 'Goji berries, Sugar', 'Dried goji berries', 'Goji berries powder', 'Goji berries flavour', 'Rice, Goji berries', 'Sapote', 'Sapote, Salt', 'Sapote, Sugar', 'Dried sapote', 'Sapote powder', 'Sapote flavour', 'Rice, Sapote', 'Hearts of palm', 'Hearts of palm, Salt', 'Hearts of palm, Sugar', 'Dried hearts of palm', 'Hearts of palm powder', 'Hearts of palm flavour', 'Rice, Hearts of palm', 'Fiddlehead ferns', 'Fiddlehead ferns, Salt', 'Fiddlehead ferns, Sugar', 'Dried fiddlehead ferns', 'Fiddlehead ferns powder', 'Fiddlehead ferns flavour', 'Rice, Fiddlehead ferns', 'Raisin, Salt', 'Prune, Salt'])
# poultry-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Quail', 'Quail, Salt', 'Dried quail', 'Smoked quail', 'Quail powder', 'Quail sausage', 'Quail flavour', 'Pheasant', 'Pheasant, Salt', 'Dried pheasant', 'Smoked pheasant', 'Pheasant powder', 'Pheasant sausage', 'Pheasant flavour', 'Ostrich', 'Ostrich, Salt', 'Dried ostrich', 'Smoked ostrich', 'Ostrich powder', 'Ostrich sausage', 'Ostrich flavour', 'Guinea hen', 'Guinea hen, Salt', 'Dried guinea hen', 'Smoked guinea hen', 'Guinea hen powder', 'Guinea hen sausage', 'Guinea hen flavour'])
PAIRS = [(t, 'ocr') for t in CORPUS] + [(t, 'text') for t in PASTE]
TOTAL = len(PAIRS)

# nalt-names-14: independent vegetable food parts, synthetic controls only.
_m14 = json.loads((ROOT / 'evaluation/nalt_names_14/admission.json').read_text())
_f14 = ['{t}', 'Raw {t}', 'Dried {t}', 'Roasted {t}', 'Salted {t}', '{t} (Salt)', '{t} (Sugar)', '{t} powder', '100% {t} powder', 'Whole {t} powder', '{t} powder (Rice)', '{t} powder (Sugar)', '{t} flour', '{t} extract', '{t} juice', '{t} oil', 'Mango ({t} Powder)', 'Mango (100% {t} Powder)']
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: '+f.format(t=n)+'.' for n in [r['term'] for r in _m14['new_foods']]+[a['name'] for a in _m14['aliases']] for f in _f14)
# cheese-g3-1 parity: every staged cheese term in sole, listed, bracketed and conditioned forms.
import csv as _csv
_CHEESE_TERMS = [r["term"] for r in _csv.DictReader((ROOT / "evaluation" / "cheese_rows_24" / "staged_rows.csv").open(newline=""))]
_fc = ['{t}', '{t}, Salt', 'Salt, {t}', '{t} (Salt)', '{t} powder', 'Smoked {t}', 'Grated {t}', 'Processed {t}', '{t} (Cheddar)', 'Milk, {t}', '{t}, Wheat Flour', 'Dried {t}', 'Salted {t}']
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for t in _CHEESE_TERMS for f in _fc)
# tomato-g3-1 parity: staged tomato concentrate terms in stated, unstated, bracketed and conditioned forms.
_TOMATO_TERMS = [r["term"] for r in _csv.DictReader((ROOT / "evaluation" / "tomato_rows_24" / "staged_rows.csv").open(newline=""))]
_ft = ['{t}', '{t}, Salt', '{t}, Sugar', '{t}, Sugar, Salt', '{t} (Salt)', '{t} (Tomato, Salt)', '{t} (28°B)', '{t}, Salt, Water', '{t}, Salt, Citric Acid', '{t} powder', 'Dried {t}, Salt', '{t}, {t}, Salt', '{t} (Tomato)', '{t}, Salt, Wheat Flour', 'Salt, {t}', 'Milk, {t}']
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for t in _TOMATO_TERMS for f in _ft)
# canned-fish-g3-1 parity.
_CANNED_TERMS = [r["term"] for r in _csv.DictReader((ROOT / "evaluation" / "canned_fish_rows_24" / "staged_rows.csv").open(newline=""))]
_fcf = ['{t}', '{t}, Water, Salt', '{t}, Sunflower Oil', '{t} (in Oil)', '{t} (Water, Salt)', '{t}, Tomato Sauce', '{t}, Soy Protein', '{t} powder', '{t}, {t}', '{t} (Tuna, Salt)', 'Smoked {t}', '{t}, Milk', 'Salt, {t}', '{t}, Colour (102)']
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f.format(t=t) + '.' for t in _CANNED_TERMS for f in _fcf)
# wheat-semolina alias parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Wheat semolina', 'Wheat semolina (75%)', 'Wheat Semolina, Salt', 'Wheat semolina, Maltodextrin', 'Wheat semolina (Salt)', 'Wheat semolina powder'])
# curry-leaves-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Curry leaves', 'Curry leaves, Salt', 'Dried curry leaves', 'Curry leaves powder', 'Curry leaves (Colour)', 'Curry leaves, Maltodextrin', 'Wheat semolina (75%), Curry leaves, Mustard', 'Salt, Curry leaves'])
# chives-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Chives', 'Chives, Salt', 'Dried chives', 'Chives powder', 'Chives (Colour)', 'Chives, Maltodextrin', 'Wheat semolina (75%), Chives, Mustard', 'Salt, Chives'])
# grains-rare-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Einkorn', 'Einkorn, Salt', 'Einkorn flour', 'Einkorn, Maltodextrin', 'Fonio', 'Fonio, Salt', 'Fonio flour', 'Fonio, Maltodextrin', 'Khorasan', 'Khorasan, Salt', 'Khorasan flour', 'Khorasan, Maltodextrin', 'Farro', 'Farro, Salt', 'Farro flour', 'Farro, Maltodextrin', 'Bulgur', 'Bulgur, Salt', 'Bulgur flour', 'Bulgur, Maltodextrin', 'Wheat semolina (75%), Bulgur, Mustard', 'Salt, Farro'])
# clause-named-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Pasta', 'Pasta, Salt', 'Pasta, Maltodextrin', 'Pasta (Salted)', 'Couscous', 'Couscous, Salt', 'Couscous, Maltodextrin', 'Couscous (Salted)', 'Polenta', 'Polenta, Salt', 'Polenta, Maltodextrin', 'Polenta (Salted)', 'Rye', 'Rye, Salt', 'Rye, Maltodextrin', 'Rye (Salted)', 'Poppy seeds', 'Poppy seeds, Salt', 'Poppy seeds, Maltodextrin', 'Poppy seeds (Salted)', 'Caraway seeds', 'Caraway seeds, Salt', 'Caraway seeds, Maltodextrin', 'Caraway seeds (Salted)', 'Hemp seeds', 'Hemp seeds, Salt', 'Hemp seeds, Maltodextrin', 'Hemp seeds (Salted)', 'Lotus seeds', 'Lotus seeds, Salt', 'Lotus seeds, Maltodextrin', 'Lotus seeds (Salted)', 'Pasta (Egg, Wheat flour)', 'Cheese pasta', 'Pasta sauce', 'Wheat semolina (75%), Couscous, Mustard'])
# group2-named-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Molasses', 'Molasses, Salt', 'Molasses, Maltodextrin', 'Molasses (Colour)', 'Dried molasses', 'Molasses, Flavour', 'Maple syrup', 'Maple syrup, Salt', 'Maple syrup, Maltodextrin', 'Maple syrup (Colour)', 'Dried maple syrup', 'Maple syrup, Flavour', 'Wheat flour, Maple syrup, Mustard', 'Maple flavoured syrup', 'Maple'])
# sweetener-names-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Wheat flour, Salt, Aspartame', 'Water, Aspartame', 'Aspartame (INS 950)', 'Wheat flour, Salt, Sodium cyclamate', 'Water, Sodium cyclamate', 'Sodium cyclamate (INS 950)', 'Wheat flour, Salt, Sucralose', 'Water, Sucralose', 'Sucralose (INS 950)', 'Wheat flour, Salt, Acesulfame potassium', 'Water, Acesulfame potassium', 'Acesulfame potassium (INS 950)', 'Wheat flour, Salt, Saccharin', 'Water, Saccharin', 'Saccharin (INS 950)', 'Wheat flour, Salt, Steviol glycosides', 'Water, Steviol glycosides', 'Steviol glycosides (INS 950)', 'Stevia', 'Water, Sweeteners (Jaggery, Sucralose)', 'Wheat flour, Salt'])
# fao-named-substances-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Wheat flour, Salt, Casein', 'Water, Casein', 'Casein (Stabiliser)', 'Wheat flour, Salt, Whey protein concentrate', 'Water, Whey protein isolate', 'Whey protein concentrate (Milk)', 'Wheat flour, Mechanically separated meat', 'Mechanically separated meat, Salt', 'Wheat flour, Fruit juice concentrate', 'Water, Lemon juice concentrate', 'Fruit juice concentrate (Apple)', 'Tomato paste', 'Orange juice from concentrate', 'Whey', 'Milk protein', 'Lactose free milk', 'Gluten free oats', 'Lactose', 'Wheat flour, Gluten', 'Milk (lactose free)', 'Gluten-free wheat flour', 'Without gluten', 'Free from gluten', 'No added lactose', 'Casein free', 'Non gluten flour'])
# hydrolysed-protein-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Wheat flour, Hydrolysed protein', 'Water, Hydrolyzed protein', 'Hydrolysed proteins, Salt', 'Wheat flour, Hydrolysed soy protein', 'Wheat flour, Hydrolyzed vegetable protein (Soy)', 'Wheat flour, Hydrolysed milk protein', 'Wheat flour, Hydrolysed protein free', 'Wheat flour, Hydrolysed collagen', 'Wheat flour, Soy protein', 'Wheat flour, Without hydrolysed protein'])
# game-meat-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Deer', 'Deer, Salt', 'Dried deer', 'Smoked deer', 'Deer powder', 'Deer sausage', 'Rabbit', 'Rabbit, Salt', 'Dried rabbit', 'Smoked rabbit', 'Rabbit powder', 'Rabbit sausage', 'Bison', 'Bison, Salt', 'Dried bison', 'Smoked bison', 'Bison powder', 'Bison sausage', 'Boar', 'Boar, Salt', 'Dried boar', 'Smoked boar', 'Boar powder', 'Boar sausage', 'Moose', 'Moose, Salt', 'Dried moose', 'Smoked moose', 'Moose powder', 'Moose sausage', 'Caribou', 'Caribou, Salt', 'Dried caribou', 'Smoked caribou', 'Caribou powder', 'Caribou sausage', 'Antelope', 'Antelope, Salt', 'Dried antelope', 'Smoked antelope', 'Antelope powder', 'Antelope sausage', 'Wild boar', 'Reindeer'])
# lemon-grass-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Lemon grass', 'Lemon grass, Salt', 'Rice, Lemon grass', 'Lemon grass (5%), Rice', 'Dried lemon grass, Rice', 'Lemon grass powder, Rice', 'Lemon grass paste, Rice', 'Lemon grass flavour', 'Lemongrass', 'Lemongrass, Salt', 'Rice, Lemongrass', 'Lemongrass (5%), Rice', 'Dried lemongrass, Rice', 'Lemongrass powder, Rice', 'Lemongrass paste, Rice', 'Lemongrass flavour'])
# algae-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Kelp, Salt', 'Dried kelp, Salt', 'Kelp powder, Salt', 'Kelp extract, Salt', 'Colour (Kelp)', 'Kelp flavour', 'Laver, Salt', 'Dried laver, Salt', 'Laver powder, Salt', 'Laver extract, Salt', 'Colour (Laver)', 'Laver flavour', 'Wakame, Salt', 'Dried wakame, Salt', 'Wakame powder, Salt', 'Wakame extract, Salt', 'Colour (Wakame)', 'Wakame flavour', 'Spirulina, Salt', 'Dried spirulina, Salt', 'Spirulina powder, Salt', 'Spirulina extract, Salt', 'Colour (Spirulina)', 'Spirulina flavour'])
# dried-fruit-24 and produce-gaps-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Raisins', 'Raisins, Salt', 'Raisins, Sugar', 'Dried raisins', 'Raisins powder', 'Raisins flavour', 'Rice, Raisins', 'Prunes', 'Prunes, Salt', 'Prunes, Sugar', 'Dried prunes', 'Prunes powder', 'Prunes flavour', 'Rice, Prunes', 'Jicama', 'Jicama, Salt', 'Jicama, Sugar', 'Dried jicama', 'Jicama powder', 'Jicama flavour', 'Rice, Jicama', 'Water chestnuts, Salt', 'Water chestnuts, Sugar', 'Dried water chestnuts', 'Water chestnuts powder', 'Water chestnuts flavour', 'Rice, Water chestnuts', 'Cloud ears', 'Cloud ears, Salt', 'Cloud ears, Sugar', 'Dried cloud ears', 'Cloud ears powder', 'Cloud ears flavour', 'Rice, Cloud ears', 'Goji berries', 'Goji berries, Salt', 'Goji berries, Sugar', 'Dried goji berries', 'Goji berries powder', 'Goji berries flavour', 'Rice, Goji berries', 'Sapote', 'Sapote, Salt', 'Sapote, Sugar', 'Dried sapote', 'Sapote powder', 'Sapote flavour', 'Rice, Sapote', 'Hearts of palm', 'Hearts of palm, Salt', 'Hearts of palm, Sugar', 'Dried hearts of palm', 'Hearts of palm powder', 'Hearts of palm flavour', 'Rice, Hearts of palm', 'Fiddlehead ferns', 'Fiddlehead ferns, Salt', 'Fiddlehead ferns, Sugar', 'Dried fiddlehead ferns', 'Fiddlehead ferns powder', 'Fiddlehead ferns flavour', 'Rice, Fiddlehead ferns', 'Raisin, Salt', 'Prune, Salt'])
# poultry-24 parity.
for _target in (CORPUS, PASTE):
    _target.extend('Ingredients: ' + f + '.' for f in ['Quail', 'Quail, Salt', 'Dried quail', 'Smoked quail', 'Quail powder', 'Quail sausage', 'Quail flavour', 'Pheasant', 'Pheasant, Salt', 'Dried pheasant', 'Smoked pheasant', 'Pheasant powder', 'Pheasant sausage', 'Pheasant flavour', 'Ostrich', 'Ostrich, Salt', 'Dried ostrich', 'Smoked ostrich', 'Ostrich powder', 'Ostrich sausage', 'Ostrich flavour', 'Guinea hen', 'Guinea hen, Salt', 'Dried guinea hen', 'Smoked guinea hen', 'Guinea hen powder', 'Guinea hen sausage', 'Guinea hen flavour'])
PAIRS = [(t, 'ocr') for t in CORPUS] + [(t, 'text') for t in PASTE]
TOTAL = len(PAIRS)

# Existing class aliases and item-level absence claims. Synthetic controls only.
_alias_code_controls = [
    "Ingredients: Milk, " + shape.format(t) + "."
    for t in ["Color", "Colour", "Stabilizer", "Stabiliser", "Emulsifiers", "Flavor Enhancers"]
    for shape in ["{} (102)", "no added {} (102)", "without {} (102)", "free from {} (102)",
                  "{} (102) free", "{} (102) not used", "no added {} (INS 102)",
                  "no added {} (102), maltodextrin", "{} (102), no added Color (110)"]
]
PAIRS += [(t, source) for t in _alias_code_controls for source in ["ocr", "text"]]
_conflict_controls = ["Ingredients: Milk, " + term + " (" + prefix + code + ")" + suffix + "."
    for term,code in [("Stabilizer","102"),("Stabiliser","102"),("Color","211"),("Colour","211"),("Colour","102"),("Stabilizer","414"),("Flavour Enhancer","627")]
    for prefix in ["", "INS ", "E"] for suffix in ["", ", maltodextrin"]]
PAIRS += [(t,s)for t in _conflict_controls for s in ["ocr","text"]]
PAIRS += [(t.replace("Milk, ","Milk. Contains "),s)for t in _conflict_controls for s in ["ocr","text"]]
TOTAL = len(PAIRS)


_declaration_controls = ["Ingredients: Milk. " + claim + "."
    for claim in ["Contains Stabilizer (INS 999)","Contains INS 999","Contains Raising Agent (INS 500(ii))",
                  "Contains Preservative (INS 211)","Contains INS 102","Contains Color (102)",
                  "Contains no Stabilizer (999)","May contain INS 999","Contains milk","Contains wheat",
                  "Contains no Color (102), contains Stabilizer (999)"]]
PAIRS += [(t,s)for t in _declaration_controls for s in ["ocr","text"]]
TOTAL = len(PAIRS)



# Source-conditioned fruit forms. Synthetic controls, not accuracy evidence.
_juice_names = ["apple juice", "grape juice", "orange juice", "pineapple juice"]
_juice_forms = ["{}", "Fresh {}", "100% {}", "100% Fresh {}", "Fresh 100% {}", "100% Pasteurized {}", "100% Pasteurised {}", "{} (100%)", "100% Fresh {} (Sugar)", "100% Fresh {} powder", "{} concentrate", "{} nectar", "Milk ({})", "Mango ({})", "Mango (100% Fresh {})", "100% Fresh {}, Sugar", "{}, Maltodextrin", "{}, Flavour", "{}, INS 999"]
PAIRS += [("Ingredients: " + form.format(name) + ".", source) for name in _juice_names for form in _juice_forms for source in ["ocr","text"]]
TOTAL = len(PAIRS)


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
    print(f"{TOTAL - bad}/{TOTAL} analyses identical between Python and JS ({len(CORPUS)} photo-path texts, {len(PASTE)} pasted-text texts, plus {len(PAIRS) - len(CORPUS) - len(PASTE)} focused alias/claim pairs)")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
