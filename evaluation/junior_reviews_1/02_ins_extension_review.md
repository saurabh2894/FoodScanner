# Senior review 2: antigravity/ins-extension-1 (evaluation/ins_extension_1/)

Boundary (step 0): 3 files, all under evaluation/ins_extension_1/, base 9feadd8. 66 rows (65 OK, 1 EVIDENCE-MISSING: INS 196), none of the 66 codes is already in ins_map.csv or ins_names.csv. No classification content in the artifact (verified: it contains codes, names, quoted classes, flags only).
**Verification limit (stated plainly):** the INCHEM host (www.inchem.org) is blocked by this session's egress proxy (observed HTTP 403 from the proxy), so I could NOT re-fetch any INCHEM quote. I rely on your 4/4 verbatim spot-check; the review below is of classification relevance and internal consistency, and every class string is a LEAD until a lawful copy is read. Not circumvented.

## 1. What the artifact is (and is not) evidence of
Each row quotes the functional-class wording of an INCHEM JECFA *evaluation* document (older monographs, e.g. 'SWEETENING AGENT', 'THICKENING AGENT', 'FOOD COLOUR'), not the current JECFA technological-function vocabulary the standing policy names. FAO's list of UPF-only additive classes (p.9, verified verbatim): flavours, flavour enhancers, colours, emulsifiers, emulsifying salts, artificial sweeteners, thickeners, and foaming, anti-foaming, bulking, carbonating, gelling and glazing agents. Any decision rule needs an explicit vocabulary map (INCHEM wording -> FAO class), cited per code.

## 2. Triage of the 65 OK rows against the standing policy
(Policy: a listed class is possible-use evidence, not proof of function in a product. Candidates = ONLY cosmetic classes listed; multifunctional or code variants = flagged with both citations, never automatic Group 4.)
| Tier | Codes | Senior reading |
|---|---|---|
| A. Cosmetic-only, single class (candidate rows for a gated rule batch) | colours 122, 123, 124, 133, 150a, 150c, 160b, 161h; flavour enhancers 621, 635; sweetener 955 (sucralose); emulsifiers 442, 472e, 492 | Strongest candidates. Each maps to an FAO class by name. Row-level caveats below. |
| A-caveat. Cosmetic-only in the listing but real-world non-cosmetic use | 100 curcumin (also the spice turmeric), 101 riboflavin (also vitamin B2 fortification), 160a carotenes (also provitamin A), 640 glycine (also a plain amino-acid ingredient) | Do NOT make code-only markers: the code can be a fortificant or a food. Keep for label-declared role only. |
| B. All listed classes are cosmetic though more than one | 160(ci) and 160c paprika oleoresin (colour; flavouring), 951 aspartame (sweetening; flavour enhancer), 436 polysorbate (emulsifier; dispersing agent) | Candidates; the quoted classes need the vocabulary map. 951 is already caught by name. |
| C. Mixed cosmetic + non-cosmetic (multifunctional) | 407, 414, 418 (thickener/gelling/stabilizer/emulsifier), 422 glycerol (humectant; flavouring; solvent), 452, 451, 450(iii), 460(i), 472c, 903, 904, 1420, 1442, 1450, 170, 331, 338, 339(iii), 340, 341, 450(i), 501(ii), 503, 516 | Flag with both citations; label-declared role decides; no code-only Group 4. 414 gum arabic and 418 gellan are also traditional/food ingredients. |
| D. Non-cosmetic only | antioxidants 300, 306, 307, 307b, 319, 320; preservatives/antioxidants 223, 236 (formic: preservative+flavouring), 262(i), 385; alkalis 500, 501; anticaking 552; firming 509 | Never markers. (Note 236 and 297 list 'flavouring agent' next to a technical role: multifunctional, flag.) |

## 3. Does any code deserve a decision-rule proposal? YES: two, both as SEPARATE gated batches (nothing now)
**P1. Cosmetic-only INS codes (Tier A + B):** a code-level rule for codes whose cited classes are ONLY FAO-listed UPF classes, with: the INCHEM quote, an explicit vocabulary map, a negative-control set (the A-caveat codes stay label-declared-role only), and the flip gate (frozen 66 + out-of-sample 32, 0 unexplained). Owner policy per code: confirm the quote at a lawful primary copy first (INCHEM unreachable for me).
**P2. Chemically modified starch codes 1420, 1442, 1450 (and siblings):** 'modified starches' are named as a Group 4 substance on the NUPENS Nova page (read in full: "protein isolates or concentrates, interesterified oils, hydrogenated fat, modified starches"), and the repo already has a strong `modified starch` marker. A code-to-marker equivalence needs the Codex INS class-name table (range and definition of 'modified starch'), which is not an admissible shipped source (parked, research/05). So: PROPOSAL ONLY, blocked on an admissible INS class-name source.
**No proposal** for Tier C/D (policy: flagged, role-declared only).

## 4. Data-hygiene findings (junior errors or ambiguities)
- INS 196: 'Not found in JECFA/INCHEM' is plausible (no such INS code is known to me) but is a negative claim I cannot verify; keep EVIDENCE-MISSING, never a row.
- Duplicate/variant pairs with identical quoted classes: 331 and 331(iii) (both trisodium citrate), 451 and 451(i) (pentasodium triphosphate), 306 and 307b (both mixed tocopherols concentrate), 160(ci) and 160c (paprika oleoresin). These are the 'code variants' the policy flags; they must not become two independent rules.
- **Cross-artifact inconsistency:** audit-2's `452(i)` lists JECFA classes 'EMULSIFIER; SEQUESTRANT; TEXTURIZER; THICKENER (ID 4669)'; this artifact's INS 452 ('sodium polyphosphates, glassy') lists 'EMULSIFIER; SEQUESTRANT; TEXTURIZER' with NO thickener; the owner's live GSFA check lists acidity regulator, emulsifier, humectant, raising agent, sequestrant, stabilizer, thickener. Three sources, three class sets for the same substance: exactly why code-level Group 4 is not source-supported and role-declared handling is the standard.
- 'multifunctional=yes' is 37 of 66 (56%): a code-only rule would be wrong more often than right for this set.

## 5. Contradictions with rows on main
None. No row on main is touched or contradicted by this artifact.
