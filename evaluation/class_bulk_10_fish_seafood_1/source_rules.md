# Category Source Rules: FDC Plain Fish & Seafood (Batch 10)

## 1. Primary Source Authority & Verbatim Quotations

All classification grounding is established strictly from the primary report in the repository:  
**FAO 2019**: Carlos Augusto Monteiro, Geoffrey Cannon, Mark Lawrence, Maria Laura da Costa Louzada, Priscila Pereira Machado. *Ultra-processed foods, diet quality, and health using the NOVA classification system*. Rome: Food and Agriculture Organization of the United Nations, 2019. (Report text `ca5644en.pdf`).

---

### Verbatim Group 1 Definition Clause (Animal Foods)
> **Table 1, Group 1: Unprocessed and minimally processed foods — Definition (p. 11)**  
> *"Unprocessed (or natural) foods are the edible parts of plants (such as fruit, leaves, stems, seeds, roots) or from animals (such as muscle, offal, eggs, milk), and also fungi, algae and water, after separation from nature.*  
> *Minimally processed foods are natural foods altered by industrial processes such as removal of inedible or unwanted parts, drying, powdering, squeezing, crushing, grinding, fractioning, steaming, poaching, boiling, roasting, and pasteurization, chilling, freezing, placing in containers, vacuum packaging, non-alcoholic fermentation, and other methods that do not add salt, sugar, oils or fats or other food substances to the original food."*

---

### Verbatim Group 1 Examples Clause (Fish & Seafood)
> **Table 1, Group 1: Unprocessed and minimally processed foods — Examples (p. 11)**  
> *"...meat, poultry, fish and seafood, whole or in the form of steaks, fillets and other cuts; ..."*

---

### Verbatim Group 3 & Group 4 Modification / Marker Clauses
> **Table 1, Group 3: Processed foods — Examples (p. 12)**  
> *"salted, dried, cured, or smoked meats and fish; canned fish (with or without added preservatives); ..."*

> **Table 1, Group 4: Ultra-processed foods — Examples (p. 12)**  
> *"...poultry and fish 'nuggets' and 'sticks', sausages, burgers, hot dogs, and other reconstituted meat products; ..."*

---

## 2. Naming vs. Class-Instance Breakdown

| Category Clause / Item | Verbatim Scope in FAO 2019 | Inference Level | Status & Notes |
|---|---|---|---|
| **Fish (general class)** | Table 1 Group 1 p. 11: *"fish"* | **Exact-named** | Overarching class named verbatim |
| **Seafood (general class)** | Table 1 Group 1 p. 11: *"seafood"* | **Exact-named** | Overarching class named verbatim (covers crustaceans, mollusks) |
| **Steaks, fillets and cuts** | Table 1 Group 1 p. 11: *"steaks, fillets and other cuts"* | **Exact-named** | Physical cutting/filleting is an explicit verbatim Group 1 cut form |
| **Finfish species** (salmon, tuna, cod, trout, mackerel, etc.) | Table 1 Group 1 p. 11: *"fish"* | **Class-instance** | Individual fish species are not named in FAO 2019; they are class-instances of `fish` |
| **Crustaceans** (shrimp, crab, lobster, crayfish) | Table 1 Group 1 p. 11: *"seafood"* | **Class-instance** | Crustacean species are class-instances of `seafood` |
| **Mollusks** (clam, oyster, mussel, scallop, squid, octopus) | Table 1 Group 1 p. 11: *"seafood"* | **Class-instance** | Mollusk species are class-instances of `seafood` |
| **Canned / Tinned fish** | Table 1 Group 3 p. 12: *"canned fish"*; p. 9: *"tinned fish preserved in oil"* | **Exact-named** | Processed foods; rejected |
| **Smoked / Salted fish** | Table 1 Group 3 p. 12: *"salted... or smoked... fish"* | **Exact-named** | Processed foods; rejected |
| **Fish sticks / nuggets / surimi** | Table 1 Group 4 p. 12: *"fish 'nuggets' and 'sticks'"* | **Exact-named** | Ultra-processed formulations; rejected |

---

## 3. Silence on Specific Terms (`SOURCE-SILENT`)

Where the FAO 2019 report text does not name or define a term or category, it is recorded strictly as **SOURCE-SILENT**:
- **Specific fish species**: **SOURCE-SILENT** in the FAO text (no species like salmon, tilapia, tuna, cod, shrimp, or crab is named individually; all are class-instances).
- **Fish roe / Caviar**: **SOURCE-SILENT** in Group 1 examples (queued under `queue_roe_special`).
- **Plain dried fish**: **SOURCE-SILENT** in Group 1 examples (cured/salted dried fish is Group 3; plain unsalted dried fish is queued under `dried_form_unstated`).
- **Surimi / fish paste**: **SOURCE-SILENT** in Group 1; industrial reconstituted seafood formulation (rejected under `surimi_imitation`).
- **Seaweed as food**: **SOURCE-SILENT** in Group 1 examples (algae named in definition, but commercial dried/processed seaweed as food unstated).
- **Fish oils / cod-liver oils**: **SOURCE-SILENT** in Group 2 culinary ingredients; queued under `queue_fish_oil` (defer to fats reading).
