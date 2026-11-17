# ClaimSense AI — Independent Validation Dataset: Class Coverage Analysis

**Document Version:** 1.0  
**Audit Date:** 2026-11-17  
**Scope:** Feasibility analysis and class-instance distribution across approved candidate sources  
**Target Independent Dataset:** `CarDD_Independent_Val_v1` (Target: 220–250 authentic images)  
**Execution Restriction:** Audit only. No image downloads, no scraping, no model fine-tuning.

---

## 1. Class-Wise Target Instance Requirements

To establish a statistically robust, independent validation benchmark for ClaimSense AI, the target dataset must provide sufficient support across all six canonical damage categories. Target instance counts are defined independently of image counts:

| Damage Class ID | Class Name | Phase 8 Baseline Training Instances (`CarDD_Expanded_v1/train`) | Proposed Target Validation Instances | Minimum Validation Quota | Rarity / Difficulty Classification |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **0** | **Dent** | 269 | **90+** | 90 | Abundant / High Feasibility |
| **1** | **Scratch** | 260 | **100+** | 100 | Abundant / High Feasibility |
| **2** | **Crack** | 169 | **60+** | 60 | **Moderate / High Precision Required** |
| **3** | **Glass shatter** | 45 | **40+** | 40 | Rare / High Impact |
| **4** | **Lamp broken** | 64 | **45+** | 45 | Moderate / Multi-Component |
| **5** | **Tire flat** | 22 | **30+** | 30 | **Extreme Bottleneck / Critical Focus** |
| **Total** | *All Classes* | 829 | **365+** | 365 | Estimated ~450–520 Total Instances |

---

## 2. Source-to-Class Availability Mapping

The six **APPROVED** open-source repositories identified in `licensing_matrix.md` exhibit differing strengths and category distributions:

| Source ID | Source Name | Primary License | Dent (90+) | Scratch (100+) | Crack (60+) | Glass Shatter (40+) | Lamp Broken (45+) | Tire Flat (30+) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **SRC-01** | **Roboflow Car Damage V5** | CC BY 4.0 | ★★★ | ★★★ | ★★☆ | ★★☆ | ★★☆ | ☆☆☆ |
| **SRC-02** | **DrBimmer / Hugging Face** | MIT | ★★★ | ★★★ | ★★★ | ★☆☆ | ★★★ | ☆☆☆ |
| **SRC-03** | **Kaggle COCO Car Damage** | CC0 | ★★★ | ★★★ | ★☆☆ | ★★☆ | ★★★ | ☆☆☆ |
| **SRC-04** | **Kaggle Car Damage Assessment** | CC0 | ★★★ | ★★★ | ★★☆ | ★★☆ | ★★☆ | ★★☆ |
| **SRC-05** | **Kaggle Insurance Claims** | Apache 2.0 | ★★★ | ★★☆ | ★★☆ | ★★★ | ★★☆ | ☆☆☆ |
| **SRC-06** | **Wikimedia Commons Collections** | CC-BY / CC0 | ★★★ | ★★☆ | ★☆☆ | ★★★ | ★★☆ | ★★★ |

*Rating Scale: ★★★ = Abundant primary provider; ★★☆ = Moderate / Secondary provider; ★☆☆ = Low / Incidental provider; ☆☆☆ = Negligible / Absent.*

---

## 3. In-Depth Class-by-Class Feasibility Analysis

### Class 0: Dent (Target: 90+ instances)
- **Feasibility:** **Extremely High (Over-Indexed)**
- **Source Contribution:** Dents are the most frequent mechanical deformity in collision, parking, and weather events. Available across all six approved sources.
- **Key Subtypes to Ingest:**
  1. *Panel creases / body lines:* Deep creases along door panels, quarter panels, and fenders (SRC-01, SRC-02, SRC-05).
  2. *Shallow blunt dents:* Parking lot door dings, basketball/shopping cart impacts (SRC-01, SRC-03).
  3. *Hail damage:* Multiple high-frequency shallow dimples per panel (SRC-06 `Category:Automobile_hail_damage`). A single hail damage photograph can supply 4–8 distinct ground-truth dent instances.
- **Quality Safeguards:** Exclude natural body contours, aerodynamic stamped grooves, and specular reflection artifacts misidentified as dents.

### Class 1: Scratch (Target: 100+ instances)
- **Feasibility:** **Extremely High (Over-Indexed)**
- **Source Contribution:** Present in substantial quantities across SRC-01, SRC-02, SRC-03, and SRC-04.
- **Key Subtypes to Ingest:**
  1. *Clearcoat abrasions:* Superficial surface scuffs along bumper corners and mirrors.
  2. *Deep primer / metal scratches:* Key scratches, curb gouges, scraped rocker panels.
  3. *Cluster scuffs:* Multi-line parallel scratches from wall or guardrail contact.
- **Quality Safeguards:** Scratches must have visible paint displacement or white/gray clearcoat fracturing. Avoid lighting glare, road grime streaks, and water drying marks.

### Class 2: Crack (Target: 60+ instances)
- **Feasibility:** **Moderate (Requires Targeted Filtering)**
- **Historical Problem:** In CarDD training, crack was severely confused with deep scratches, resulting in an operational mAP50 of only 1.99% in Session 2 and Session 4. Bumper fascias are predominantly thermoplastic (polypropylene/polyurethane) that tear and split rather than denting.
- **Source Contribution:**
  - **SRC-02 (DrBimmer)** is the primary high-yield source: professional body shop intake photos focus specifically on cracked front/rear bumper fascias, fractured splitters, and snapped mounting tabs.
  - **SRC-01 (Roboflow V5)** provides bumper tears and grille fractures.
  - **SRC-05 (Insurance Claims)** provides severe structural fractures in composite panels.
- **Target Ingestion Strategy:** Select 40–45 images featuring clear plastic tears, bumper splits, and grille fractures to yield **65–75 verified crack instances**.

### Class 3: Glass Shatter (Target: 40+ instances)
- **Feasibility:** **High (Readily Achieved via Focused Categories)**
- **Source Contribution:**
  - **SRC-06 (Wikimedia Commons)** contains dedicated categories (`Category:Broken_car_windows`, `Category:Broken_windshields`) containing hundreds of authentic, high-resolution photographs.
  - **SRC-05 (Insurance Claims)** and **SRC-01 (Roboflow V5)** contribute severe windshield impact stars, bullseyes, and laminated crack lines.
- **Key Subtypes to Ingest:**
  1. *Laminated glass cracking (Windshield):* Spiderweb crack patterns, circular impact blooms, edge-to-edge stress fractures.
  2. *Tempered glass shattering (Side & Rear windows):* Granular fractured mosaic, completely missing pane with remaining perimeter glass granules.
- **Target Ingestion Strategy:** Select 25–30 images to yield **45–55 verified instances**.

### Class 4: Lamp Broken (Target: 45+ instances)
- **Feasibility:** **High**
- **Source Contribution:** Headlamps and tail lamps are fragile polycarbonate housings located at the vehicle perimeter, making them present in nearly all frontal and rear-end collisions.
- **Primary Sources:** SRC-02 (DrBimmer intake), SRC-03 (Kaggle COCO), SRC-04 (Kaggle Damage Assessment).
- **Key Subtypes to Ingest:**
  1. *Cracked outer lens:* Transparent plastic fractured but internal reflector intact.
  2. *Shattered lens with missing housing:* Bulb and internal wiring exposed.
  3. *Detached / knocked-out assembly:* Entire headlamp dislodged from mounting bracket.
- **Target Ingestion Strategy:** Select 35–40 images to yield **50–60 verified instances**.

### Class 5: Tire Flat (Target: 30+ instances)
- **Feasibility:** **Achievable with Dedicated Ingestion Quota (Critical Bottleneck)**
- **Historical Problem:** CarDD expanded dataset contains only 22 training instances (2.6% of training dataset). Most collision datasets ignore tire deflation, creating an extreme data scarcity bottleneck.
- **Targeted Source Solution:**
  - **SRC-06 (Wikimedia Commons `Category:Flat_tires`):** Contains over 200 distinct, verified high-resolution photographs of authentic flat tires on passenger cars, sedans, pickup trucks, and commercial vans.
  - **SRC-04 (Kaggle Car Damage Assessment):** Contains a dedicated categorical folder of flat tire claims.
- **Key Subtypes to Ingest:**
  1. *Deflated sidewall on rim:* Bottom bead collapsed onto pavement/rim flange.
  2. *Blowout / tread separation:* Shredded rubber with visible internal steel belts.
  3. *Punctured standing tire:* Completely depressurized tire parked on street.
- **Target Ingestion Strategy:** Reserve a dedicated acquisition quota of **25–28 images** featuring flat tires to guarantee **32–38 verified tire flat instances**.

---

## 4. Multi-Label Damage Co-Occurrence Model

Real-world vehicle accidents rarely produce single-class isolated damage. Selecting realistic collision and claim images enables natural multi-label yield:

```
┌────────────────────────────────────────────────────────────────────────┐
│               Typical Damage Co-Occurrence Patterns                    │
├────────────────────────────────┬───────────────────────────────────────┤
│ Collision Scenario             │ Expected Damage Classes Co-Occurring   │
├────────────────────────────────┼───────────────────────────────────────┤
│ 1. Frontal Corner Impact       │ Dent (fender) + Scratch + Lamp broken │
│                                │ + Plastic bumper Crack                │
├────────────────────────────────┼───────────────────────────────────────┤
│ 2. Side T-Bone Impact          │ Dent (doors) + Scratch + Glass shatter│
│                                │ (side window)                         │
├────────────────────────────────┼───────────────────────────────────────┤
│ 3. Severe Curb / Pothole Strike│ Tire flat + Rim dent/scratch + Lower  │
│                                │ bumper Crack                          │
├────────────────────────────────┼───────────────────────────────────────┤
│ 4. Severe Hail Storm Event     │ Multiple Dents (hood/roof/trunk) +    │
│                                │ Glass shatter (windshield star)       │
├────────────────────────────────┼───────────────────────────────────────┤
│ 5. Rear-End Impact             │ Dent (tailgate) + Lamp broken +       │
│                                │ Bumper crack + Scratch                │
└────────────────────────────────┴───────────────────────────────────────┘
```

Because of this multi-label distribution, an intake of **235 curated authentic images** is projected to yield:
$$\text{Projected Total Instances} \approx 235 \times 2.05 \approx 482 \text{ ground-truth annotations}$$
comfortably surpassing the cumulative minimum threshold of 365 instances across all six classes.

---

## 5. Synthesis: Target Instance vs Projected Yield Matrix

| Damage Class | Minimum Target | Target Portfolio Images | Projected Yield Rate (inst/img) | Projected Instance Yield | Safety Margin Above Target |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Dent** | 90 | 110 (co-occurring) | 1.25 | **135** | **+50.0%** |
| **Scratch** | 100 | 105 (co-occurring) | 1.35 | **142** | **+42.0%** |
| **Crack** | 60 | 50 (targeted) | 1.40 | **70** | **+16.7%** |
| **Glass shatter** | 40 | 32 (targeted) | 1.50 | **48** | **+20.0%** |
| **Lamp broken** | 45 | 40 (targeted) | 1.30 | **52** | **+15.5%** |
| **Tire flat** | 30 | 28 (dedicated) | 1.20 | **34** | **+13.3%** |
| **Overall Dataset** | **365** | **235 images** | **~2.05** | **481 instances** | **+31.8%** |

**Conclusion:** All six target classes are statistically viable using exclusively the six **APPROVED** open-license sources, with zero reliance on synthetic datasets or prohibited web scraping.
