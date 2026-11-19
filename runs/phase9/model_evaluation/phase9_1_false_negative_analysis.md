# ClaimSense AI — Phase 9.1: False-Negative & Missed Defect Forensic Analysis

**Document ID:** `REP-PH9-1-FN-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.1 — Model Performance Re-evaluation  
**Date:** 2026-11-19  
**Governing Standard:** `acquisition_specification.md` v1.1-ACTIVE  
**Audit Scope:** Deep-Dive Forensic Investigation of False-Negative Patterns, Missed Damage, and Localization Failures

---

## 1. Executive Summary

In auto insurance claims verification, false negatives (missed damage) carry critical underwriting and fraud risk. An undetected structural crack or compromised light assembly can result in denied legitimate payouts, policyholder dissatisfaction, or safety hazards from un-repaired vehicle frames.

This audit examines the **113 false negatives** recorded by the Production Baseline (`models/phase5/best.pt`) on the CarDD_300 Test Cohort (148 ground-truth defects).

---

## 2. Class-Wise False-Negative Breakdown

| Defect Class | Ground Truth Instances | False Negatives (Missed) | Operational Recall ($\tau=0.25$) | Miss Rate (%) | Core Failure Mechanism |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **0: Dent** | 49 | 34 | 30.6% | **69.4%** | Subtle, low-contrast depression contours; large diffuse boundaries |
| **1: Scratch** | 53 | 45 | 15.1% | **84.9%** | Hairline clear-coat scratches; spatial attenuation at low resolutions |
| **2: Crack** | 13 | 13 | **0.0%** | **100.0%** | Complete failure to localize structural fractures and panel splits |
| **3: Glass Shatter** | 12 | 7 | 41.7% | **58.3%** | Small spiderweb fractures outside central windshield area |
| **4: Lamp Broken** | 15 | 6 | 60.0% | **40.0%** | Cracked lens covers with intact reflector housing |
| **5: Tire Flat** | 6 | 2 | 66.7% | **33.3%** | Partially deflated tires lacking pronounced rim contact |
| **Total Micro Cohort** | **148** | **113** | **23.65%** | **76.35%** | **Overall 3 out of 4 defects missed at $\tau=0.25$** |

---

## 3. Detailed Failure Case Studies

### Case 1: `000042.jpg` (12 Missed Defects)
* **Image Context:** Severe multi-impact side collision showing side doors, rocker panel, and quarter panel.
* **Ground Truth:** 14 genuine defect annotations (multiple complex dents, deep scratches, and fractured door seams).
* **Model Output:** Detected only 2 primary dents; missed **12 distinct damage instances** (9 scratches, 2 dents, 1 crack).
* **Failure Mechanism:** When multiple defects co-occur on a single distorted panel, the anchor grid assigns feature capacity to the largest dominant deformation, suppressing adjacent smaller scratches and seam cracks.
* **Visualization Artifact:** [`runs/phase9/model_evaluation/visual_failure_cases/eval_vis_000042.jpg`](file:///c:/Users/ydvan/Desktop/ClaimSense%20Ai/ClaimSense-AI/runs/phase9/model_evaluation/visual_failure_cases/eval_vis_000042.jpg)

### Case 2: `002707.jpg` (7 Missed Defects)
* **Image Context:** Front bumper scrape with paint transfer and diffuse hairline scratches.
* **Ground Truth:** 8 annotated scratches and surface abrasions across the bumper fascia.
* **Model Output:** Successfully localized 1 central scratch; missed 7 peripheral scratches.
* **Failure Mechanism:** Low optical contrast between scraped paint flakes and the vehicle base coat. The predicted confidence scores hovered between $0.11$ and $0.19$, which were discarded by the $\tau=0.25$ threshold.
* **Visualization Artifact:** [`runs/phase9/model_evaluation/visual_failure_cases/eval_vis_002707.jpg`](file:///c:/Users/ydvan/Desktop/ClaimSense%20Ai/ClaimSense-AI/runs/phase9/model_evaluation/visual_failure_cases/eval_vis_002707.jpg)

### Case 3: `001799.jpg` (6 Missed Defects)
* **Image Context:** Rear fender impact with panel buckling and structural cracking.
* **Ground Truth:** 7 defect instances including bumper crack and dent.
* **Model Output:** Detected 1 large dent; completely failed on structural cracks.
* **Visualization Artifact:** [`runs/phase9/model_evaluation/visual_failure_cases/eval_vis_001799.jpg`](file:///c:/Users/ydvan/Desktop/ClaimSense%20Ai/ClaimSense-AI/runs/phase9/model_evaluation/visual_failure_cases/eval_vis_001799.jpg)

---

## 4. Root Causes of High False-Negative Rates

1. **Resolution Downsampling (Optical Attenuation):**
   Standard model input resolution ($416 \times 416$ or $640 \times 640$) resizes high-resolution photographic evidence by a factor of 4x to 8x. Sub-millimeter features such as hairline scratches and structural cracks are degraded below the spatial resolution required for activation.
2. **Class Imbalance in Feature Learning:**
   Because dents represent nearly 50% of the training data, detection heads preferentially predict dent bounding boxes for ambiguous damaged areas rather than identifying specific crack or scratch categories.
3. **Rigid Operating Point Threshold:**
   A single global threshold of $\tau=0.25$ suppresses subtle but authentic damage instances whose confidence falls in the $0.12–0.24$ range.

---

## 5. False-Negative Mitigation Recommendations for Phase 9.2

1. **High-Resolution Sliced Inference (SAHI):** Partition high-resolution images into overlapping $640 \times 640$ patches during evaluation to preserve native optical resolution for hairline cracks and scratches.
2. **Dynamic Per-Class Thresholding:** Lower operational thresholds for rare and fine-grained classes:
   - Cracks: $\tau = 0.15$
   - Scratches: $\tau = 0.18$
   - Dents: $\tau = 0.30$
3. **Class-Weighted Focal Loss:** Apply focal loss ($\gamma=2.5$) with inverse frequency weighting to force backpropagation gradients onto missed defect categories.
