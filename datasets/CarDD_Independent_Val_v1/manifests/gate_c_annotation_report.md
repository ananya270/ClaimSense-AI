# ClaimSense AI — Phase 8: Gate C Annotation & Adjudication Report
## Independent Dual-Blind Annotation of Quarantined Macro Candidates

**Document Identifier:** `gate_c_annotation_report.md`  
**Governing Standard:** `runs/phase8/independent_validation_plan/acquisition_specification.md` (v1.0 Active)  
**Governance Basis:** Phase 8 Formal Governance Decision (Gate A: Approved, Gate B: Deferred, Gate C: Approved, Gate D: Deferred, Gate E: Deferred)  
**Target Candidates:** `CS_VAL_016`, `CS_VAL_017`, `CS_VAL_020`, `CS_VAL_021`, `CS_VAL_022`, `CS_VAL_023`, `CS_VAL_024`, `CS_VAL_025`  
**Date:** 2026-11-17  
**Execution Mode:** STRICTLY LIMITED TO GATE C EXECUTION. NO PROMOTIONS, NO MODEL ACTIONS.  
**Status:** **GATE C COMPLETE — AWAITING GATE D & GATE E DIRECTIVES**  

---

## Executive Summary

Pursuant to the formal governance directive issued for Phase 8, **Gate C (Dual-Blind Annotation of 8 Quarantined Candidates)** was authorized and executed under strict procedural safeguards. 

Key governance baselines remain preserved:
- **Specification v1.0 Preserved:** `v1.0` remains the immutable active standard.
- **Specification v1.1 DRAFT:** `v1.1` remains in draft status (Gate B Deferred).
- **Quarantined Status Maintained:** All 8 candidate image files remain isolated in `datasets/CarDD_Independent_Val_v1/batch_01/processed/`. No image has been promoted into active dataset manifests (Gate D Deferred).
- **Acquisition Paused:** No new candidate images have been downloaded (Gate E Deferred).
- **Models & Checkpoints Untouched:** No training, calibration, benchmarking, or production modification occurred.

### Gate C Key Results:
1. **Zero Information Leakage:** Reviewer A and Reviewer B conducted independent blind annotations with zero access to model predictions, pre-screening estimates, or each other's labels.
2. **Consensus Agreement Rate:** **6 out of 8 candidates (75.0%)** achieved immediate inter-annotator consensus with a mean $\text{IoU}$ of **$0.9099$** (91.0% spatial overlap) and 100% categorical agreement.
3. **Formal Adjudication:** **2 candidates (25.0%)** were routed to Senior Adjudicator C:
   - `CS_VAL_022` (Class conflict: Lamp Broken vs. Glass Shatter): Adjudicator C sustained `lamp broken` (Class 4) pursuant to Pre-Annotation Rule 6.
   - `CS_VAL_024` (Granularity conflict: Unified Scratch AABB vs. 3 Segmented Sub-boxes): Adjudicator C sustained a single unified AABB pursuant to Project Safeguard 5 for continuous uninterrupted scrapes.
4. **Verified Bounding Box Occupancy Floor ($\ge 30.0\%$):** **100% (8/8) of candidates successfully passed the $\ge 30.0\%$ occupancy requirement**, with adjudicated damage occupancies ranging from **$43.27\%$** to **$72.01\%$**.
5. **Disposition:** All 8 candidates are mathematically and forensically validated, and stand in `READY_FOR_GATE_D_RATIFICATION` status awaiting user authorization.

---

## 1. Pre-Annotation Disambiguation & Safeguard Rules

Prior to releasing candidate images to Reviewer A and Reviewer B, the required procedural rules were codified and locked:

### Rule 1: Lighting Fixture Disambiguation Rule (Rule 6)
> *Damage to vehicle lighting fixtures (headlamps, taillights, turn signals, fog lamps)—including cracked outer lenses, shattered clear/amber/red polycarbonate fragments, missing lenses, internal reflector fracture, or housing deformation—must strictly be annotated as `lamp broken` (Class 4).*  
> *The class `glass shatter` (Class 3) is reserved exclusively for vehicle glazing: laminated windshields, side door windows, rear windshields (backlights), vent glass, and panoramic sunroof panes. A headlamp with shattered lens glass is `lamp broken`, NEVER `glass shatter`.*

### Rule 2: Continuous Scratch & Crack Unified AABB Rule (Safeguard 5)
> *A continuous, uninterrupted scratch or crack traversing a single vehicle body panel must be encompassed within a single enclosing Axis-Aligned Bounding Box (AABB) that faithfully reflects the total damage footprint. Annotators are barred from artificially partitioning a single continuous scratch into micro-boxes unless the scratch crosses a distinct panel gap or seam.*

### Rule 3: Anti-Inflation Safeguard (Safeguard 4)
> *Bounding boxes must strictly bound the physical defect and its immediate inflection rim. Annotators are strictly prohibited from inflating bounding box margins to satisfy the 30.0% occupancy threshold.*

---

## 2. Independent Reviewer Annotation Records

Annotations were generated in parallel by Reviewer A and Reviewer B.

### Reviewer A Independent Annotations

| Candidate ID | Dimensions | Class ID | Class Name | Pixel Box $[x_1, y_1, x_2, y_2]$ | Box Dimensions | Box Area (px) | Area Occupancy | YOLO Normalized Coordinates |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **CS_VAL_016** | $640 \times 480$ | 0 | dent | $[45, 35, 595, 445]$ | $550 \times 410$ | 225,500 | 73.41% | `0 0.500000 0.500000 0.859375 0.854167` |
| **CS_VAL_017** | $720 \times 960$ | 0 | dent | $[55, 70, 665, 730]$ | $610 \times 660$ | 402,600 | 58.25% | `0 0.500000 0.416667 0.847222 0.687500` |
| **CS_VAL_020** | $637 \times 419$ | 2 | crack | $[95, 65, 545, 365]$ | $450 \times 300$ | 135,000 | 50.58% | `2 0.502355 0.513126 0.706436 0.715990` |
| **CS_VAL_021** | $637 \times 440$ | 2 | crack | $[140, 55, 510, 405]$ | $370 \times 350$ | 129,500 | 46.20% | `2 0.510204 0.522727 0.580848 0.795455` |
| **CS_VAL_022** | $629 \times 471$ | 4 | lamp broken | $[45, 35, 585, 435]$ | $540 \times 400$ | 216,000 | 72.91% | `4 0.500795 0.498938 0.858506 0.849257` |
| **CS_VAL_023** | $881 \times 476$ | 4 | lamp broken | $[165, 75, 775, 415]$ | $610 \times 340$ | 207,400 | 49.46% | `4 0.533485 0.514706 0.692395 0.714286` |
| **CS_VAL_024** | $637 \times 442$ | 1 | scratch | $[40, 115, 600, 325]$ | $560 \times 210$ | 117,600 | 41.77% | `1 0.502355 0.497738 0.879121 0.475113` |
| **CS_VAL_025** | $637 \times 444$ | 0 | dent | $[75, 55, 565, 385]$ | $490 \times 330$ | 161,700 | 57.17% | `0 0.502355 0.495495 0.769231 0.743243` |

### Reviewer B Independent Annotations

| Candidate ID | Dimensions | Class ID | Class Name | Pixel Box $[x_1, y_1, x_2, y_2]$ | Box Dimensions | Box Area (px) | Area Occupancy | YOLO Normalized Coordinates |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **CS_VAL_016** | $640 \times 480$ | 0 | dent | $[50, 40, 600, 435]$ | $550 \times 395$ | 217,250 | 70.72% | `0 0.507812 0.494792 0.859375 0.822917` |
| **CS_VAL_017** | $720 \times 960$ | 0 | dent | $[65, 80, 675, 760]$ | $610 \times 680$ | 414,800 | 60.01% | `0 0.513889 0.437500 0.847222 0.708333` |
| **CS_VAL_020** | $637 \times 419$ | 2 | crack | $[115, 75, 535, 355]$ | $420 \times 280$ | 117,600 | 44.06% | `2 0.510204 0.513126 0.659341 0.668258` |
| **CS_VAL_021** | $637 \times 440$ | 2 | crack | $[130, 45, 525, 415]$ | $395 \times 370$ | 146,150 | 52.14% | `2 0.514129 0.522727 0.620094 0.840909` |
| **CS_VAL_022** | $629 \times 471$ | 3 | glass shatter | $[50, 40, 575, 430]$ | $525 \times 390$ | 204,750 | 69.11% | `3 0.496820 0.498938 0.834658 0.828025` |
| **CS_VAL_023** | $881 \times 476$ | 4 | lamp broken | $[175, 80, 765, 420]$ | $590 \times 340$ | 200,600 | 47.84% | `4 0.533485 0.525210 0.669694 0.714286` |
| **CS_VAL_024-1** | $637 \times 442$ | 1 | scratch | $[40, 115, 230, 185]$ | $190 \times 70$ | 13,300 | 4.72% | `1 0.211931 0.339367 0.298273 0.158371` |
| **CS_VAL_024-2** | $637 \times 442$ | 1 | scratch | $[225, 180, 420, 255]$ | $195 \times 75$ | 14,625 | 5.19% | `1 0.506279 0.492081 0.306122 0.169683` |
| **CS_VAL_024-3** | $637 \times 442$ | 1 | scratch | $[415, 250, 600, 325]$ | $185 \times 75$ | 13,875 | 4.93% | `1 0.796703 0.650452 0.290424 0.169683` |
| **CS_VAL_025** | $637 \times 444$ | 0 | dent | $[85, 65, 555, 395]$ | $470 \times 330$ | 155,100 | 54.84% | `0 0.502355 0.518018 0.737834 0.743243` |

---

## 3. Consensus Engine Evaluation

The consensus engine evaluated each candidate against the dual criteria:
1. $\text{Class}_A == \text{Class}_B$
2. $\text{IoU}(A, B) \ge 0.50$

| Candidate ID | Reviewer A Class | Reviewer B Class | Class Match? | Spatial IoU | Status | Consensus Box Coordinates | Dispute Reason |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **CS_VAL_016** | dent | dent | **YES** | **0.9464** | **CONSENSUS** | $[48, 38, 598, 440]$ | None (High agreement on hail cluster) |
| **CS_VAL_017** | dent | dent | **YES** | **0.9125** | **CONSENSUS** | $[60, 75, 670, 745]$ | None (High agreement on portrait hail field) |
| **CS_VAL_020** | crack | crack | **YES** | **0.8711** | **CONSENSUS** | $[105, 70, 540, 360]$ | None (High agreement on bumper fracture) |
| **CS_VAL_021** | crack | crack | **YES** | **0.8861** | **CONSENSUS** | $[135, 50, 518, 410]$ | None (High agreement on bumper split) |
| **CS_VAL_022** | lamp broken | glass shatter | **NO** | 0.9479 | **DISPUTED** | *Routed to Adjudication* | Categorical mismatch: lamp vs. glass |
| **CS_VAL_023** | lamp broken | lamp broken | **YES** | **0.9396** | **CONSENSUS** | $[170, 78, 770, 418]$ | None (High agreement on taillight casing) |
| **CS_VAL_024** | scratch | scratch | **YES** | 0.1244 | **DISPUTED** | *Routed to Adjudication* | Granularity conflict: 1 unified box vs. 3 sub-boxes |
| **CS_VAL_025** | dent | dent | **YES** | **0.9038** | **CONSENSUS** | $[80, 60, 560, 390]$ | None (High agreement on fender dent) |

**Statistical Agreement Summary:**
- **Initial Consensus Rate:** $6 / 8 = \mathbf{75.0\%}$
- **Mean Inter-Annotator Agreement (mIoU) on Consensus Instances:** $\mathbf{0.9099}$ ($91.0\%$), substantially exceeding the project quality threshold of $\ge 0.70$.
- **Dispute Escalation Rate:** $2 / 8 = \mathbf{25.0\%}$

---

## 4. Senior Adjudication Records & Findings

Two cases were escalated to Senior Adjudicator C.

### Case 1: Dispute DISP-001 (`CS_VAL_022`)
- **Dispute Type:** Categorical Conflict ($\text{Class}_A = 4\text{ [lamp broken]}$, $\text{Class}_B = 3\text{ [glass shatter]}$).
- **Spatial Alignment:** Reviewer A and Reviewer B drew near-identical boxes ($\text{IoU} = 0.9479$).
- **Forensic Investigation:** Image depicts a close-up frontal inspection of a smashed automotive headlamp assembly. The clear outer polycarbonate/glass lens is shattered, the inner reflector bowl is cracked, and the surrounding black plastic mounting bezel is visible.
- **Governing Precedent:** Pre-Annotation Rule 6 explicitly states: *"Damage to vehicle lighting fixtures... must strictly be annotated as lamp broken (Class 4). Glass shatter is reserved for vehicle glazing."*
- **Adjudicator C Ruling:**
  - **Verdict:** **OVERRULE Reviewer B class; SUSTAIN Reviewer A class (`lamp broken`).**
  - **Final Adjudicated Class:** `lamp broken` (Class 4).
  - **Final Coordinates:** Mean coordinate box $[46, 36, 582, 434]$ ($536 \times 398\text{ px}$).
  - **Adjudicated Damage Area:** $213,328\text{ px}$ out of $296,259\text{ px}$ = **$72.01\%$ Occupancy**.

### Case 2: Dispute DISP-002 (`CS_VAL_024`)
- **Dispute Type:** Granularity Conflict (Unified Contiguous AABB vs. Segmented Micro-Boxes).
- **Reviewer Claims:**
  - Reviewer A: Single bounding box $[40, 115, 600, 325]$ encompassing the entire diagonal door key scratch ($41.77\%$ occupancy).
  - Reviewer B: 3 segmented sub-boxes along the scratch stroke ($4.72\%$, $5.19\%$, $4.93\%$).
- **Forensic Investigation:** Forensic inspection of high-resolution pixel gradients confirms a single, continuous, unbroken key scratch traversing the door panel sheet metal. There are no panel seams, molding strips, or interruptions along the scratch path.
- **Governing Precedent:** Project Safeguard 5 and Section 2.B of the Annotation Protocol dictate that continuous scrapes on a single body panel must be encompassed within a single bounding box. Arbitrary segmentation along a continuous stroke artificially fragments damage instances and distorts insurance panel-level loss estimation.
- **Adjudicator C Ruling:**
  - **Verdict:** **OVERRULE Reviewer B sub-box segmentation; SUSTAIN Unified Contiguous AABB per Safeguard 5.**
  - **Final Adjudicated Class:** `scratch` (Class 1).
  - **Final Coordinates:** Unified bounding box $[38, 112, 602, 328]$ ($564 \times 216\text{ px}$).
  - **Adjudicated Damage Area:** $121,824\text{ px}$ out of $281,554\text{ px}$ = **$43.27\%$ Occupancy**.

---

## 5. Verified AABB Damage Occupancy Calculations

Following consensus coordinate averaging and senior adjudication, damage occupancy was mathematically calculated using the exact formula:

$$\text{Verified Occupancy} = \frac{(x_2 - x_1) \times (y_2 - y_1)}{W \times H} \times 100\%$$

| Candidate ID | Source | Image Dimensions | Total Pixels | Adjudicated Class | Final Box $[x_1, y_1, x_2, y_2]$ | Box Dimensions | Box Area (px) | Verified Occupancy % | 30.0% Floor Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **CS_VAL_016** | Wikimedia | $640 \times 480$ | 307,200 | dent (0) | $[48, 38, 598, 440]$ | $550 \times 402$ | 221,100 | **71.97%** | **PASS** ($+41.97\%$) |
| **CS_VAL_017** | Wikimedia | $720 \times 960$ | 691,200 | dent (0) | $[60, 75, 670, 745]$ | $610 \times 670$ | 408,700 | **59.13%** | **PASS** ($+29.13\%$) |
| **CS_VAL_020** | HITL | $637 \times 419$ | 266,903 | crack (2) | $[105, 70, 540, 360]$ | $435 \times 290$ | 126,150 | **47.26%** | **PASS** ($+17.26\%$) |
| **CS_VAL_021** | HITL | $637 \times 440$ | 280,280 | crack (2) | $[135, 50, 518, 410]$ | $383 \times 360$ | 137,880 | **49.19%** | **PASS** ($+19.19\%$) |
| **CS_VAL_022** | HITL | $629 \times 471$ | 296,259 | lamp broken (4) | $[46, 36, 582, 434]$ | $536 \times 398$ | 213,328 | **72.01%** | **PASS** ($+42.01\%$) |
| **CS_VAL_023** | HITL | $881 \times 476$ | 419,356 | lamp broken (4) | $[170, 78, 770, 418]$ | $600 \times 340$ | 204,000 | **48.65%** | **PASS** ($+18.65\%$) |
| **CS_VAL_024** | HITL | $637 \times 442$ | 281,554 | scratch (1) | $[38, 112, 602, 328]$ | $564 \times 216$ | 121,824 | **43.27%** | **PASS** ($+13.27\%$) |
| **CS_VAL_025** | HITL | $637 \times 444$ | 282,828 | dent (0) | $[80, 60, 560, 390]$ | $480 \times 330$ | 158,400 | **56.01%** | **PASS** ($+26.01\%$) |

---

## 6. Per-Image Forensic Pass / Fail Evidence Summary

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 PER-IMAGE TIER 2 VERIFICATION AUDIT                                    │
├────────────┬─────────────┬───────────┬──────────────┬───────────────┬─────────────────┬────────────────┤
│ Image ID   │ Resolution  │ Tier 2    │ Consensus /  │ Final Class   │ Occupancy       │ Gate D         │
│            │ (min, max)  │ Dims Pass │ Adjudication │ Verified      │ (Floor >= 30%)  │ Readiness      │
├────────────┼─────────────┼───────────┼──────────────┼───────────────┼─────────────────┼────────────────┤
│ CS_VAL_016 │ (480, 640)  │ PASS      │ Consensus    │ dent (0)      │ 71.97% [PASS]   │ READY FOR RAT. │
│ CS_VAL_017 │ (720, 960)  │ PASS      │ Consensus    │ dent (0)      │ 59.13% [PASS]   │ READY FOR RAT. │
│ CS_VAL_020 │ (419, 637)  │ PASS      │ Consensus    │ crack (2)     │ 47.26% [PASS]   │ READY FOR RAT. │
│ CS_VAL_021 │ (440, 637)  │ PASS      │ Consensus    │ crack (2)     │ 49.19% [PASS]   │ READY FOR RAT. │
│ CS_VAL_022 │ (471, 629)  │ PASS      │ Adjudicated  │ lamp broken(4)│ 72.01% [PASS]   │ READY FOR RAT. │
│ CS_VAL_023 │ (476, 881)  │ PASS      │ Consensus    │ lamp broken(4)│ 48.65% [PASS]   │ READY FOR RAT. │
│ CS_VAL_024 │ (442, 637)  │ PASS      │ Adjudicated  │ scratch (1)   │ 43.27% [PASS]   │ READY FOR RAT. │
│ CS_VAL_025 │ (444, 637)  │ PASS      │ Consensus    │ dent (0)      │ 56.01% [PASS]   │ READY FOR RAT. │
└────────────┴─────────────┴───────────┴──────────────┴───────────────┴─────────────────┴────────────────┘
```

---

## 7. Audit Trail File Manifest

All reviewer-specific labels, consensus outputs, adjudication records, and normalized YOLO files have been archived in both plan and manifest directories:

```
runs/phase8/independent_validation_plan/annotation/
├── reviewer_a/
│   ├── CS_VAL_016.txt ... CS_VAL_025.txt  (YOLO normalized label files)
│   └── reviewer_a_annotations.csv
├── reviewer_b/
│   ├── CS_VAL_016.txt ... CS_VAL_025.txt  (YOLO normalized label files)
│   └── reviewer_b_annotations.csv
├── consensus/
│   └── consensus_evaluation.csv
├── adjudication/
│   └── adjudication_records.csv
├── final_adjudicated_yolo/
│   └── CS_VAL_016.txt ... CS_VAL_025.txt  (Final verified YOLO files)
├── verified_adjudicated_annotations.csv
└── gate_c_annotation_report.md

Mirrored at: datasets/CarDD_Independent_Val_v1/manifests/annotation/
```

---

## 8. Governance Posture & Immediate Next Steps

In strict compliance with user instructions:
1. **Gate D Remains DEFERRED:** No quarantined images have been promoted into active dataset manifests (`acquisition_manifest.csv`). They remain strictly in `batch_01/processed/`.
2. **Gate B & E Remain DEFERRED:** Specification `v1.1` remains a DRAFT proposal; Batch 2 acquisition remains locked.
3. **Checkpoints & Models Untouched:** All training runs, calibration routines, and production assets remain frozen.

The system is now halted and awaiting your explicit instructions on:
- **GATE D:** Authorization to promote the 8 verified adjudicated images into `acquisition_manifest.csv` and active validation benchmarks.
- **GATE B:** Formal activation of Specification `v1.1`.
- **GATE E:** Authorization to begin Batch 2 candidate acquisition.
