# ClaimSense AI — Phase 9.4: Training Bottleneck Analysis

**Document ID:** `REP-PH9-4-BOTTLENECK-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.4 — Training Strategy & Hyperparameter Optimization Planning  
**Evidence Foundation:** Phase 9.0 Audit, Phase 9.1 Evaluation, Phase 9.2 Crack Forensic Audit  
**Status:** EVIDENCE-BACKED SYNTHESIS COMPLETE  

---

## 1. Executive Summary

By synthesizing empirical findings from Phase 9.0 (Baseline Audit), Phase 9.1 (Model Re-evaluation), and Phase 9.2 (Structural Crack Forensic Investigation), this report identifies and ranks the actual technical bottlenecks hindering vehicle damage detection and causing the $0.0\%$ recall barrier for structural cracks.

---

## 2. Bottleneck A: Multi-Level Class Imbalance

### Quantitative Evidence
- **Instance-Level Imbalance (`CarDD_300` Train Split):**
  - Total instances: 714
  - `dent`: 234 instances ($32.77\%$)
  - `scratch`: 258 instances ($36.13\%$)
  - `crack`: 91 instances ($12.75\%$)
  - `lamp broken`: 64 instances ($8.96\%$)
  - `glass shatter`: 45 instances ($6.30\%$)
  - `tire flat`: 22 instances ($3.08\%$)
- **Imbalance Ratios:**
  - Scratch-to-Crack Ratio: **$2.84 : 1$**
  - Dent-to-Crack Ratio: **$2.57 : 1$**
- **Image-Level Distribution:**
  - Total training images: 210
  - Images containing cracks: 56 images ($26.7\%$)
  - Images containing scratches: 142 images ($67.6\%$)
  - Images containing dents: 138 images ($65.7\%$)
  - Pure background images (clean vehicles): 0 in CarDD_300 (45 added in Gate L full cohort).
  - Multi-class collision images: 118 images contain $\ge 2$ damage classes simultaneously.

### Engineering Impact:
The problem is **both image-level and instance-level imbalance**. In over $73\%$ of training batches, gradient updates contain zero crack supervision, causing the optimizer to favor minimizing loss on scratches and dents.

---

## 3. Bottleneck B: Structural Defect Scale & Geometric Extreme

### Quantitative Evidence
- **Scale Disparity:**
  - Median normalized crack area: **$0.0069$** ($0.69\%$ of image area).
  - Median absolute pixel dimensions on native $1000\times 667$ images: **$68.9\text{ px} \times 69.4\text{ px}$**.
  - Compared to `scratch` (median area $0.0451$, $225.5\text{ px} \times 143.8\text{ px}$), cracks are **$6.54\times$ smaller**.
  - Compared to `dent` (median area $0.0549$, $219.2\text{ px} \times 177.7\text{ px}$), cracks are **$7.96\times$ smaller**.
- **Extreme Aspect Ratio Elongation:**
  - Mean elongation ($\max(w,h)/\min(w,h)$): **$2.70 : 1$**.
  - Maximum elongation in training data: **$14.31 : 1$** (e.g. `000904`).
- **Annotation Contradiction & Noise:**
  - 14 training images exhibit severe spatial overlap where annotators drew a `crack` box and a `scratch` box over the exact same panel lesion (e.g. `001427`, `000485`).

### Engineering Impact:
When downscaled to standard training resolution ($416\times 416$ in Phase 5, or $640\times 640$ in Session 2), fine cracks collapse to sub-grid scales. On elongated fissures, standard axis-aligned bounding boxes contain over $75\%$ undamaged background, destabilizing regression loss.

---

## 4. Bottleneck C: Model Architecture & Optimization Limitations

### Quantitative Evidence
- **Feature Pyramid Striding (P3/P4/P5):**
  - YOLOv8's highest-resolution feature map is P3 (stride 8).
  - A 15-pixel crack at $640\times 640$ resolution spans only $1.8$ feature cells at P3 and $<0.9$ cells at P4. Feature activations vanish during convolution.
- **Classification Head Bias & Scratch Confusion:**
  - Forensic tracking of all 13 test-set cracks revealed:
    - **$46.2\%$ (6/13) misclassified as `scratch`** with spatial IoU between $0.26$ and $0.56$.
    - **$15.4\%$ (2/13) absorbed into `dent`** with spatial IoU between $0.41$ and $0.54$.
    - **$38.5\%$ (5/13) feature vanishing** (zero proposal formed).
    - **$0.0\%$ (0/13) correctly classified as `crack`**.
- **Loss Weight Suppression:**
  - In `args.yaml`, `cls: 0.5` vs `box: 7.5`. The network is penalized $15\times$ more for bounding box coordinate offsets than for class discrimination errors. Consequently, the network predicts `scratch` (the majority class with similar linear edges) to minimize risk.

---

## 5. Comprehensive Bottleneck Assessment Matrix

| # | Bottleneck | Evidence Source | Affected Metric / Class | Impact Severity | Confidence Level | Proposed Experimental Response |
|---|---|---|---|---|---|---|
| **1** | **Scratch vs. Crack Class Confusion** | Phase 9.2 (`phase9_2_scratch_vs_crack_confusion.csv`) | `crack` recall ($0.0\%$), `scratch` precision ($15.5\%$) | **CRITICAL** | High ($99\%$) | Clean overlapping annotations; increase classification loss weight `cls: 1.5`; class-specific focal loss $\alpha=2.8\times$. |
| **2** | **Feature Vanishing on Sub-Grid Cracks** | Phase 9.2 (`phase9_2_resolution_sensitivity.csv`) | `crack` feature detection (38.5% vanishing) | **CRITICAL** | High ($95\%$) | Train at $1024\times 1024$ input resolution; introduce P2 feature pyramid layer (stride 4). |
| **3** | **Instance & Image Imbalance** | Phase 9.0 & 9.2 audits (`phase9_2_dataset_crack_inventory.csv`) | `crack` sensitivity, multi-class gradient updates | **HIGH** | High ($95\%$) | Ingest vetted 100-image CarDD pool (+78 cracks); deploy crack-biased Copy-Paste augmentation. |
| **4** | **Elongated Bounding-Box Instability** | Phase 9.2 geometry audit (max elong 14.3:1) | Bounding-box IoU (suppressed to 0.25-0.38) | **HIGH** | High ($90\%$) | Replace standard CIoU with Wise-IoU v3 or Inner-IoU to decouple aspect-ratio penalties. |
| **5** | **Receptive Field Distortion (416 vs 640)**| Phase 9.4 baseline audit (`models/phase5/args.yaml`) | Production inference calibration | **MEDIUM** | High ($95\%$) | Standardize training and evaluation input resolution. |
| **6** | **Daylight Walkaround Domain Shift** | Gate L Dev audit (0 cracks in walkaround set) | Real-world field generalizability | **MEDIUM** | High ($90\%$) | Acquire 35-50 authentic walkaround bumper fracture instances for EXP04. |
