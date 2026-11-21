# Category Source Rules: FDC 'Beverages' Plain Forms (Batch 8)

## 1. Primary Source Authority & Verbatim Quotations

All classification grounding is established strictly from the primary report in the repository:  
**FAO 2019**: Carlos Augusto Monteiro, Geoffrey Cannon, Mark Lawrence, Maria Laura da Costa Louzada, Priscila Pereira Machado. *Ultra-processed foods, diet quality, and health using the NOVA classification system*. Rome: Food and Agriculture Organization of the United Nations, 2019. (Report text `ca5644en.pdf`).

---

### Verbatim Group 1 Definition Clause
> **Table 1, Group 1: Unprocessed and minimally processed foods — Definition (p. 11)**  
> *"Unprocessed (or natural) foods are the edible parts of plants (such as fruit, leaves, stems, seeds, roots) or from animals (such as muscle, offal, eggs, milk), and also fungi, algae and water, after separation from nature. Spring and tap water.*  
> *Minimally processed foods are natural foods altered by industrial processes such as removal of inedible or unwanted parts, drying, powdering, squeezing, crushing, grinding, fractioning, steaming, poaching, boiling, roasting, and pasteurization, chilling, freezing, placing in containers, vacuum packaging, non-alcoholic fermentation, and other methods that do not add salt, sugar, oils or fats or other food substances to the original food."*

---

### Verbatim Group 1 Examples Clause
> **Table 1, Group 1: Unprocessed and minimally processed foods — Examples (p. 11)**  
> *"...fresh or pasteurized plain yoghurt; tea, coffee, and drinking water."*

---

### Verbatim Group 4 Examples Clause
> **Table 1, Group 4: Ultra-processed foods — Examples (p. 12)**  
> *"Many ready-to-consume products such as carbonated soft drinks; ... 'energy' drinks; milk drinks, 'fruit' yoghurts and 'fruit' drinks; 'cocoa' drinks..."*

---

## 2. Naming vs. Class-Instance Breakdown

| Category Clause / Item | Verbatim Scope in FAO 2019 | Inference Level | Status & Notes |
|---|---|---|---|
| **Drinking water** | Table 1 Group 1 p. 11: *"drinking water"* | **Exact-named** | Verbatim named in Table 1 Group 1 examples |
| **Tap water** | Table 1 Group 1 p. 11: *"Spring and tap water"* | **Exact-named** | Verbatim named in Table 1 Group 1 definition |
| **Spring water** | Table 1 Group 1 p. 11: *"Spring and tap water"* | **Exact-named** | Verbatim named in Table 1 Group 1 definition |
| **Tea** | Table 1 Group 1 p. 11: *"tea, coffee, and drinking water"* | **Exact-named** | Verbatim named in Table 1 Group 1 examples |
| **Tea varieties (black, green, oolong)** | Table 1 Group 1 p. 11: *"tea"* | **Class-instance** | Specific types of Camellia sinensis infusions (`black tea`, `green tea`, `oolong tea`) are class-instances of `tea` |
| **Coffee** | Table 1 Group 1 p. 11: *"tea, coffee, and drinking water"* | **Exact-named** | Verbatim named in Table 1 Group 1 examples |
| **Coffee preparation styles (brewed, espresso)** | Table 1 Group 1 p. 11: *"coffee"* | **Class-instance** | Specific preparations (`brewed coffee`, `espresso`) are class-instances of plain coffee |
| **Carbonated / sparkling water** | Table 1 Group 1 p. 11: *"water"* (silent on carbonation) | **Class-instance** | Carbonation introduces carbonic acid / carbon dioxide gas; queued pending policy |
| **Carbonated soft drinks / colas** | Table 1 Group 4 p. 12: *"carbonated soft drinks"* | **Exact-named** | Ultra-processed formulations; rejected |
| **Energy & sports drinks** | Table 1 Group 4 p. 12: *"'energy' drinks"* | **Exact-named** | Ultra-processed formulations; rejected |
| **Fruit drinks / fruit-flavored drinks** | Table 1 Group 4 p. 12: *"'fruit' drinks"* | **Exact-named** | Formulated sweetened beverages; rejected |

---

## 3. Silence on Specific Terms (`SOURCE-SILENT`)

Where the FAO 2019 report text does not name or define a specific beverage form, it is recorded strictly as **SOURCE-SILENT**:
- **Herbal infusions (tisanes)** (e.g. chamomile, hibiscus, mint): **SOURCE-SILENT** in Table 1 Group 1 (FAO text specifies `tea`, referring botanically to Camellia sinensis; non-Camellia plant infusions are queued under `queue_herbal_infusion`).
- **Plain 100% fruit and vegetable juices**: **SOURCE-SILENT** in Table 1 Group 1 examples (juices were deliberately parked from Batch 3 fruit staging and remain queued under `roadmap_parked`).
- **Coconut water**: **SOURCE-SILENT** in Table 1 Group 1 examples (queued under `queue_coconut_water`).
- **Plant-based milks** (e.g. almond milk, oat milk, rice milk, soy milk): **SOURCE-SILENT** under Group 1; ultra-processed formulations under Group 4 (queued under `queue_plant_milk`).
- **Coffee substitutes / chicory**: **SOURCE-SILENT** in Group 1 examples (queued under `queue_coffee_substitute`).

---

## 4. Suggested Kind Taxonomy Mapping

In `src/foodscan/resources/lexicon.csv`:
- `water` is currently staged with `kind='neutral'` (defined in research/02 as carrying no processing signal).
- For `tea` and `coffee`, Table 1 Group 1 establishes them as plain unsweetened beverage infusions that carry no processing signal in isolation.
- **Mapping Option 1 (Recommended)**: Map plain unsweetened `tea` and `coffee` to `kind='neutral'` (aligning with `water` as an unsweetened liquid carrier).
- **Mapping Option 2**: Map to `kind='whole_food'` (aligning with unprocessed/minimally processed plant commodities).
- Both interpretations are preserved for senior review; `accept_records.csv` defaults to `neutral` matching the established `water` precedent.
