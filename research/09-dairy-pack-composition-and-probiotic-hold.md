# Dairy source-pack decision, 23 November 2026

## N09, bounded engineering correction
Actual archived pack image inspected, SHA256 993b73b3d72aa7c434b34aaeb04a86fe6a2049ed11b088b75b0627c9443d4a6a:
https://images.openfoodfacts.org/images/products/890/611/736/0353/ingredients_en.13.full.jpg

Country Delight buffalo milk panel has an ingredient heading, one pasteurized buffalo milk line, then a separate paired fat/SNF minimum composition line. Archived text flattens the lines. Restoring a line break alone does not fix the parser. Existing parser reads the first minimum's abbreviation period as a list end, leaving the SNF portion ignored, and treats the first fat figure as part of an unrecognised ingredient.

Identity/composition source freshly read:
https://www.fssai.gov.in/upload/uploadfiles/files/2_%20Chapter%202_1%20(Dairy%20products%20and%20analogues).pdf
Section2.1.2 describes buffalo milk as species-identified milk and fat/SNF as composition. No inference of added milk-fat ingredients from those composition figures. The fetched text covers that section; fetch truncates before fermented milk and direct PDF download returned502. It is not treated as proof of current full regulatory compliance or the exact historical pack's date. The pack's6%floor need not equal the standard's5%floor.

Method sources freshly read:
https://www.fsp.usp.br/nupens/en/learn-how-to-classify-foods/
https://www.fao.org/4/ca5644en/ca5644en.pdf
Both cover milk/pasteurized milk in Group1. This change does not add a vocabulary row or promote the provisional buffalo-milk mapping. Its existing provenance/limitations remain visible under source evidence.

Scope: only whole pre-stop list regions consisting of a supported plain milk name (optionally pasteurized spelling) followed by a complete fat%minimum, SNF%minimum pair qualify. Both figures remain verbatim in a visible composition warning; original analysed text stays unchanged. No general nutrient/percent cutoff. Separate milk fat, milk with added solids, fortification, other ingredients, incomplete pairs, brackets or unknown names do not qualify. Numeric typography tolerance covers the actual pack without requiring invented commas. Figures are displayed, not checked for regulatory compliance.

## N08, no semantic change
Actual pack image inspected, SHA256 29c9aa629d0a68d85c85346da2c15e669084455dafb91527b719ce8df09b1c86:
https://images.openfoodfacts.org/images/products/890/408/330/5071/ingredients_en.8.full.jpg
The recorded text is faithful: active lactic culture and probiotic culture with Bifidobacterium lactis/Lactobacillus acidophilus bracket. No source justifies stripping the probiotic phrase or treating the combined item automatically as starter culture.
Manufacturer product page and dated2021 manufacturer article confirm probiotic curd/live-bacteria marketing, not starter purpose:
https://www.milkymist.com/curd
https://www.milkymist.com/post/probiotics-for-a-healthy-gut
Independent retailer exact-product ingredients agree with pack:
https://www.zeptonow.com/pn/milky-mist-probiotic-curd-cup/pvid/fa890e06-e218-445a-9a0d-c42f6c73ecd7
FSSAI probiotic document freshly read:
https://www.fssai.gov.in/upload/uploadfiles/files/Direction_New_compressed.pdf
It distinguishes probiotic properties from merely being commonly used starter cultures. This is an identity/scope distinction, not NOVA placement. Plain-yoghurt/fermentation clauses do not independently establish that the separate probiotic addition is covered. N08 remains unresolved under the existing research04 hold. No claim that probiotic cultures are ultra-processed or unsafe.

Q07 and cutoff wording remain transcription leads only. No new dairy inheritance, synthetic source admissions or nutrient/fortification exemptions.

## Private validation and limits, 23 November2026
- 68deduplicated recorded texts:49answered becomes50; exactly N09changes. N08 and remaining18abstentions unchanged. This is coverage, not measured accuracy.
- 15853/15853Python/browser parity, includes actual N09 and fortification tail counterexample.
- Focused14checks pass, including native template count/metadata role.
- Broader suite excluding separately run browser-gate module:10575passed,5expected-fail,1known native millet failure, before the final additional template regression check. Browser-gate module separately5passed. Actual browser fresh OCR gate116/116,0missing,exact rebuild.
- Browser390/1280actual pixels and native template replay pixels inspected. Native template dictionary-items display collision discovered visually, corrected with bracket access and regression check; no classifier change from this display correction.
- Critical limit: fresh native Tesseract on original N09.jpg still loses the Ingredients heading and mangles buffalo/fat/SNF, so it abstains. This is not an OCR fix or a promise that the original photo will now answer. Native template screenshot uses corpus text as a rendered result, explicitly not a fresh OCR success. The real native OCR output remains separately saved.
- Milk-composition word count is now a separate metadata role, not after-list text. Figures shown unchanged, original text retained, existing provisional mapping made visible above driver.
- Authority: research04's asserted owner decisions and pasted Claude report are not approvals. Genuine user's20Nov17:32:29delegation of technical decisions except spending is the operative scope, subject to subsequent parent limits. No publication authorized by this source note.
