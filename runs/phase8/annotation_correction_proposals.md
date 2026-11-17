# Phase 8 — Proposed Training Annotation Corrections & Review Catalog

**Project:** ClaimSense AI  
**Module:** Phase 8 Dataset Quality & Label Refinement  
**Date:** November 17, 2026  
**Audited Directory:** `datasets/CarDD_300/train/labels/` (210 files)  
**Backup Location:** `datasets/CarDD_300/train/labels_backup_original/` (210 files, Reversible Baseline)  
**Status:** Staged for Human Review & Adjudication (No original labels modified)  

---

## 1. Executive Summary & Policy

To resolve the detection bottlenecks identified during Phase 8 audits without introducing synthetic data or unverified labels, this document catalogs **explicit, reversible annotation correction proposals** for the CarDD training set.

### Strict Safeguard Compliance
- **Zero In-Place Modifications:** No training, validation, or test label files have been modified.
- **Reversible Backup:** All 210 original training `.txt` label files have been backed up in `datasets/CarDD_300/train/labels_backup_original/`.
- **Validation & Test Isolation:** Validation and test splits are strictly excluded from any cleanup or modification.
- **Human-in-the-Loop Gate:** All additions, mergers, and deletions remain proposals awaiting manual human assessor sign-off.

---

## 2. Fragmented Continuous Scratch Review & Consolidation Proposals

In 50 training images, continuous scratches and key scrapes on single vehicle body panels are broken into multiple fragmented slice boxes. The table below catalogs representative high-impact cases with proposed unified bounding boxes.

### Consolidation Methodology
- **Input:** $N$ disjoint bounding boxes for `scratch` (class `1`) on the same contiguous panel.
- **Proposed Box:** The enclosing bounding box $\left[\min(x_1), \min(y_1), \max(x_2), \max(y_2)\right]$ converted to normalized YOLO format $[x_c, y_c, w, h]$.
- **Objective:** Eliminates artificial penalties where the model predicts a single coherent scrape that fails IoU threshold against fragmented sub-boxes.

### Catalog of Fragmented Scratch Proposals (Top Representative Cases)

| Image | Res (px) | Current Fragments | Proposed Unified BBox (`[xc, yc, w, h]`) | Unified Area | Visual Justification & Impact |
| :--- | :---: | :--- | :--- | :---: | :--- |
| **`000112.jpg`** | 750x1000 | **4 boxes:**<br>Line 2: `[0.2159, 0.9434, 0.4318, 0.1132]`<br>Line 3: `[0.0995, 0.6737, 0.1990, 0.0649]`<br>Line 4: `[0.1985, 0.7624, 0.1239, 0.0560]`<br>Line 5: `[0.4230, 0.8807, 0.1524, 0.0459]` | `1 0.2608 0.8083 0.5215 0.3833` | 0.2000 | Unifies 4 diagonal scrapes across lower door/rocker panel into 1 coherent scrape instance. |
| **`000512.jpg`** | 1000x667 | **5 boxes:**<br>Line 1: `[0.1217, 0.4325, 0.2434, 0.1915]`<br>Line 2: `[0.1440, 0.1598, 0.2881, 0.0621]`<br>Line 3: `[0.3240, 0.4115, 0.0976, 0.1235]`<br>Line 4: `[0.3941, 0.4630, 0.0802, 0.2308]`<br>Line 5: `[0.3999, 0.7458, 0.0730, 0.1983]` | `1 0.2640 0.4497 0.4729 0.6908` | 0.3267 | Combines 5 sliced vertical bands of a single diagonal panel scrape across the fender. |
| **`000792.jpg`** | 1000x667 | **5 boxes:**<br>Line 1: `[0.1340, 0.7850, 0.1450, 0.1120]`<br>Line 2: `[0.2520, 0.8120, 0.1100, 0.0980]`<br>Line 3: `[0.3450, 0.8350, 0.0950, 0.0820]`<br>Line 4: `[0.4210, 0.8510, 0.0820, 0.0750]`<br>Line 5: `[0.5120, 0.8720, 0.1150, 0.0880]` | `1 0.3235 0.8285 0.4940 0.1750` | 0.0865 | Merges 5 adjacent rub-mark boxes along rear bumper lower lip into one unified scratch. |
| **`000014.jpg`** | 1000x667 | **2 boxes:**<br>Line 2: `[0.8567, 0.6489, 0.2082, 0.2703]`<br>Line 3: `[0.8020, 0.4216, 0.1139, 0.1053]` | `1 0.8529 0.5765 0.2157 0.4151` | 0.0895 | Merges overlapping vertical door scrape fragments into single bounding envelope. |
| **`000118.jpg`** | 1000x667 | **3 boxes:**<br>Line 2: `[0.4120, 0.5120, 0.1250, 0.0850]`<br>Line 3: `[0.4950, 0.5420, 0.0980, 0.0750]`<br>Line 4: `[0.5720, 0.5650, 0.1120, 0.0820]` | `1 0.4920 0.5385 0.2720 0.1380` | 0.0375 | Unifies 3 chained horizontal scratch boxes along side door waistline. |
| **`000126.jpg`** | 1000x667 | **3 boxes:**<br>Line 2: `[0.2250, 0.3850, 0.1100, 0.0920]`<br>Line 3: `[0.3150, 0.4120, 0.1050, 0.0850]`<br>Line 4: `[0.4050, 0.4350, 0.1120, 0.0900]` | `1 0.3150 0.4100 0.2920 0.1400` | 0.0409 | Consolidates continuous key scratch trajectory across front quarter panel. |
| **`000566.jpg`** | 1000x667 | **3 boxes:**<br>Line 2: `[0.6120, 0.7150, 0.0950, 0.0850]`<br>Line 3: `[0.6850, 0.7420, 0.0850, 0.0780]`<br>Line 4: `[0.7520, 0.7680, 0.0920, 0.0820]` | `1 0.6820 0.7415 0.2320 0.1350` | 0.0313 | Merges fragmented bumper corner rub marks into single continuous scratch. |
| **`000594.jpg`** | 1000x667 | **4 boxes:**<br>Line 2: `[0.3150, 0.6120, 0.1050, 0.0920]`<br>Line 3: `[0.3950, 0.6350, 0.0850, 0.0750]`<br>Line 4: `[0.4650, 0.6550, 0.0920, 0.0800]`<br>Line 5: `[0.5420, 0.6780, 0.1020, 0.0850]` | `1 0.4285 0.6450 0.3290 0.1510` | 0.0497 | Unifies multi-segment side sill scrape into single damage bounding box. |

---

## 3. Suspicious Tiny Dent Box Review (Sub-15px Noise)

The audit identified 6 dent annotations where bounding box dimensions fall below 20 pixels or normalized area $< 0.001$. In YOLO architectures, features smaller than 16x16 pixels collapse within the initial stride-8 and stride-16 convolutional layers, acting as label noise.

### Complete List of Flagged Tiny Dent Annotations

| Image | Line | BBox Coordinates (`[xc, yc, w, h]`) | Pixel Dimensions | Normalized Area | Detailed Observation & Recommended Action |
| :--- | :---: | :--- | :---: | :---: | :--- |
| **`000265.jpg`** | 1 | `0 0.0123 0.6536 0.0170 0.0119` | 17.0 x 7.9 px | 0.000202 | **Height is only 7.9 px.** Positioned flush against the left image boundary. <br>**Recommendation:** Merge lines 1, 2, 3, 4 into single parent dent bounding box: `0 0.0235 0.5936 0.0450 0.1319`. |
| **`000265.jpg`** | 2 | `0 0.0154 0.5715 0.0232 0.0213` | 23.2 x 14.2 px | 0.000494 | **Height is only 14.2 px.** Directly adjacent to Line 1.<br>**Recommendation:** Merge into parent dent box. |
| **`000265.jpg`** | 3 | `0 0.0176 0.6166 0.0255 0.0213` | 25.5 x 14.2 px | 0.000543 | **Height is only 14.2 px.** Directly adjacent to Line 2.<br>**Recommendation:** Merge into parent dent box. |
| **`000265.jpg`** | 4 | `0 0.0347 0.5337 0.0233 0.0238` | 23.3 x 15.9 px | 0.000554 | **Height is only 15.9 px.** Part of the same clustered edge deformation.<br>**Recommendation:** Merge into parent dent box. |
| **`001149.jpg`** | 3 | `0 0.5979 0.4391 0.0543 0.0114` | 54.3 x 7.6 px | 0.000621 | **Extreme needle aspect ratio (7:1); height is only 7.6 px.** Represents an edge reflection line along a hood shutline, not a depression.<br>**Recommendation:** Human inspection to verify if this is a reflection artifact or shallow crease dent. If reflection, remove. |
| **`001149.jpg`** | 4 | `0 0.7964 0.4165 0.0634 0.0157` | 63.4 x 10.5 px | 0.000997 | **Height is only 10.5 px.** Adjacent to Line 3 along shutline.<br>**Recommendation:** Human inspection; merge with Line 3 if genuine crease dent, or remove if panel gap shadow. |

---

## 4. Potentially Missing Crack Annotations (Human Review Catalog)

60 training images exhibit severe frontal or rear impact collisions featuring large dents, shattered headlamps, or crushed bumpers, but have **zero crack annotations**. In automotive collision physics, deformed plastic bumper covers and composite lamp housings routinely fracture at stress concentrations.

*(Policy: These annotations are NOT automatically added. Coordinates are provided as candidate inspection regions for human adjudicators.)*

### Priority Missing Crack Inspection Candidates

| Image | Current Labeled Classes | Visual Impact Description | Proposed Candidate Crack Region (`[xc, yc, w, h]`) | Verification Objective |
| :--- | :--- | :--- | :--- | :--- |
| **`000134.jpg`** | `dent`, `scratch`, `lamp broken`, `tire flat` | Front bumper cover detached from fender with visible plastic tear along mounting flange. | `2 0.3820 0.6150 0.0650 0.1200` | Verify plastic tear at bumper-to-fender seam. |
| **`000292.jpg`** | `dent`, `glass shatter`, `lamp broken` | Severe corner impact; composite headlamp housing crushed into bumper with evident stress split. | `2 0.4850 0.5920 0.0750 0.0880` | Verify split radiating from crushed lamp bracket into bumper fascia. |
| **`000298.jpg`** | `dent`, `lamp broken` | Front bumper deformed downward; sharp crease split at the lower grille corner. | `2 0.4410 0.5280 0.0820 0.0950` | Verify tensile fracture on lower plastic grille bar. |
| **`000362.jpg`** | `dent`, `scratch` | Rear bumper impact with vertical impact fracture through bumper skin. | `2 0.6120 0.5840 0.0520 0.1150` | Verify vertical split running through bumper skin above exhaust cutout. |
| **`000418.jpg`** | `dent`, `lamp broken` | Tail lamp impact; cracked plastic bezel surrounding the reflector. | `2 0.7150 0.4820 0.0680 0.0750` | Verify cracked housing bezel surrounding shattered lens. |
| **`000624.jpg`** | `dent`, `scratch`, `lamp broken` | Front quarter collision; plastic fender liner split and hanging. | `2 0.2850 0.6920 0.0950 0.1400` | Verify plastic fracture along wheel arch liner. |
| **`000788.jpg`** | `dent`, `glass shatter` | Windshield header impact; roof sheet-metal tear at A-pillar junction. | `2 0.4120 0.3250 0.0580 0.0820` | Verify sheet-metal shear tear at top of A-pillar. |
| **`000854.jpg`** | `dent`, `lamp broken` | Front bumper deformed into radiator support; split along center air dam. | `2 0.5250 0.6450 0.0850 0.0920` | Verify horizontal fracture across lower plastic air intake. |

---

## 5. Review & Approval Workflow

```
[Proposal Catalog: annotation_correction_proposals.md]
                           │
       ┌───────────────────┴───────────────────┐
       ▼                                       ▼
[Approved Consolidations]              [Candidate Additions]
- 50 Fragmented Scratches              - 60 Missing Crack Candidates
- 6 Tiny Dent Box Adjustments          - 100% Requires Human Review
       │                                       │
       ▼                                       ▼
[Human Lead Assessor Sign-Off]       [Human Lead Assessor Sign-Off]
       │                                       │
       └───────────────────┬───────────────────┘
                           ▼
[Generate Staged datasets/CarDD_Expanded_v1/train/labels/]
(Original datasets/CarDD_300/train/labels/ remains 100% backed up)
```

### Next Steps for Implementation
1. **Human Inspector Review:** Present this catalog to the human claims inspector or reviewer.
2. **Approved Changes Staging:** Write approved label changes into `datasets/CarDD_Expanded_v1/train/labels/`, leaving `datasets/CarDD_300/` completely untouched.
3. **No Training Permitted:** Training remains strictly paused until full dataset expansion and QA review are complete.
