# Item-level references (fresh batch 3), written BEFORE any app run

Hand-prepared by an LLM from the photos, not ground truth: spot-check against the photos (links in manifest.json). Conventions as in batches 1 and 2 (errata v1): a pair joined by 'and' or '&' naming two ingredients is two items; one declared phrase is one item. Expected NOVA is provisional with its basis. Q01 is excluded under the selection rule. Q13 and Q14: item lists unjudged, group judged from the readable fragments.

## Q01 - Amul Taaza toned milk (EXCLUDED before scoring)
- Expected NOVA (provisional): **excluded**. Basis: EXCLUDED under the selection rule: the photo shows the product name, an allergen line and a nutrition table, no ingredient list
- Traps: 
- Top-level items (0):

## Q02 - Gokul pasteurised full cream milk
- Expected NOVA (provisional): **1**. Basis: provisional: a single dairy ingredient (milk, pasteurised or powdered, NUPENS-USP Group 1); 'milk solids' is itself a PROVISIONAL vocabulary row
- Traps: sideways bag photo with water drops and tiny text; the Ingredients line is one short line among many
- Top-level items (1):
  1. Milk solids

## Q03 - Katraj pasteurised buttermilk
- Expected NOVA (provisional): **3**. Basis: provisional: Group 1 foods (curd, water) with a Group 2 substance (salt) (NUPENS-USP Group 3 description)
- Traps: very small crop; 'CONTAINS MILK' follows with no separator
- Top-level items (3):
  1. Water
  2. Curd
  3. Iodised salt

## Q04 - Nandini curd
- Expected NOVA (provisional): **1**. Basis: milk (as solids) fermented with a culture, nothing else (NUPENS-USP: fermentation of milk to make yoghurt; plain yoghurt with no added sugar)
- Traps: '&' joins the two items; 'Allergen Advice: contains Milk' below; the milk-plus-culture rule should fire (milk solids and culture are in the rule)
- Top-level items (2):
  1. Milk solids (toned milk)
  2. Active culture

## Q05 - Heritage Daily Health toned milk
- Expected NOVA (provisional): **1**. Basis: provisional: milk with added vitamins (NUPENS-USP: foods with vitamins and minerals added to replace lost nutrients stay in their group)
- Traps: 'Vitamin A Palmitate & Vitamin D (Ergocalciferol)' joins two items with '&'; vitamins are outside the vocabulary, so an abstention is possible
- Development overlap: family of M06 Heritage curd
- Top-level items (3):
  1. Milk solids (toned milk)
  2. Vitamin A palmitate
  3. Vitamin D (ergocalciferol)

## Q06 - Country Delight cow milk
- Expected NOVA (provisional): **1**. Basis: pasteurised milk (NUPENS-USP Group 1)
- Traps: 'Fat 3.50% Min., SNF 8.50% Min.' is a composition note on the same line; a two-panel photo with a nutrition table
- Development overlap: family of N09 Country Delight buffalo milk
- Top-level items (1):
  1. Pasteurized cow milk

## Q07 - Arokya toned milk
- Expected NOVA (provisional): **1**. Basis: provisional: milk and its solids, nothing else (NUPENS-USP: milk, pasteurised or powdered)
- Traps: 'Milk & Milk Solids' with '&'; no culture, so the milk-plus-culture rule does not apply
- Top-level items (2):
  1. Milk
  2. Milk solids

## Q08 - Dodla toned milk
- Expected NOVA (provisional): **1**. Basis: provisional: milk with added vitamins (NUPENS-USP: fortified foods stay in their group)
- Traps: 'Vitamin A (...) and Vitamin D(...)' joins two items; tiny text on a large crumpled pouch; fat/SNF line below; allergen line
- Top-level items (3):
  1. Milk solids
  2. Vitamin A (retinyl palmitate)
  3. Vitamin D (ergocalciferol)

## Q09 - Aavin Delite toned milk
- Expected NOVA (provisional): **1**. Basis: provisional: milk and its solids (NUPENS-USP: milk, pasteurised or powdered)
- Traps: the text runs SIDEWAYS in the photo (rotated 90 degrees): OCR of rotated text is likely to fail
- Top-level items (2):
  1. Milk
  2. Milk solids

## Q10 - Akshayakalpa high protein milk
- Expected NOVA (provisional): **1**. Basis: provisional: milk solids of skimmed milk (NUPENS-USP: milk, pasteurised or powdered)
- Traps: the heading is singular 'INGREDIENT:'; 'Fat: 0.5% maximum / S.N.F: 8.7% minimum' lines follow and are composition notes; blurred photo
- Top-level items (1):
  1. Milk solids (pasteurized skimmed cow milk)

## Q11 - Boost milk shake (dairy based drink)
- Expected NOVA (provisional): **4**. Basis: provisional: stabilisers are on the NUPENS-USP list of Group 4 additive classes; 'milk drinks' are on its Group 4 examples. Control: this list must NOT fire the milk-plus-culture rule (it holds sugar and stabilisers)
- Traps: 'Dairy Based Drink (Proprietary Food)' line above; the code bracket '(INS 339 (ii))' nests a bracket; the stabiliser class is 'unlisted' in the app, so an abstention is possible
- Development overlap: brand Boost (N16, a different product)
- Top-level items (9):
  1. Toned milk (60%)
  2. Water
  3. Sugar
  4. Cereal product (3%)
  5. Milk solids
  6. Minerals
  7. Acidity regulator (INS 339 (ii))
  8. Stabilizers (INS 418, INS 407)
  9. Vitamins

## Q12 - Epigamia chocolate milk shake
- Expected NOVA (provisional): **4**. Basis: emulsifier and flavour (NUPENS-USP Group 4 classes). Control: this list must NOT fire the milk-plus-culture rule
- Traps: 'Emulsifier & Stabilizers [codes]' is ONE declared phrase with a shared code list; 'Vitamin A & Vitamin D' joins two items; square brackets; nested bracket in '[INS 339 (iii)]'
- Top-level items (11):
  1. Skimmed milk (80%)
  2. Sugar
  3. Water
  4. Milk solids
  5. Cocoa powder (1.5%)
  6. Emulsifier & Stabilizers [INS 471, INS 407, INS 412]
  7. Flavour (natural flavouring substances)
  8. Acidity regulator [INS 339 (iii)]
  9. Edible common salt
  10. Vitamin A
  11. Vitamin D

## Q13 - Mountain Dew (bottle)
- Expected NOVA (provisional): **4**. Basis: classification only: the readable fragments show acidity regulators (330, 331), flavour, preservative (211), colour and a line 'CONTAINS NON-CALORIC SWEETENERS' (NUPENS-USP: colourings, flavourings, sweeteners are Group 4 classes); the full list cannot be read at this resolution, so extraction is UNJUDGED
- Traps: bottle photographed sideways with tiny curved text and a sweeteners sentence; chosen as the negation control (the record's text holds a negation), which the photo cannot show
- Top-level items (0):

## Q14 - Tomato ketchup pouch (code-heavy control)
- Expected NOVA (provisional): **4**. Basis: classification only: the readable part lists 'Emulsifying & Stabilizing Agent (INS1422, INS415)' (a provisional role phrase: emulsifier class; INS 1422 is a modified starch), acidity regulator, preservative: Group 4 by the NUPENS-USP classes. The TOP of the ingredient list is cut off in the photo, so the item list is UNJUDGED
- Traps: the list starts above the frame; the Contains line and an allergy statement that mentions milk solids, wheat and soya as processing facts (never ingredients) follow; codes without spaces (INS1422)
- Development overlap: same recipe family as the ketchups of N12 and M12
- Top-level items (0):
- Declared on a Contains/other line:
  - permitted class II preservative (INS211)
