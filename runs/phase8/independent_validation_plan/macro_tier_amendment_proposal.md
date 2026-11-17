# Proposal for Formal Specification Amendment: Dual-Tier Resolution Architecture (v1.1-DRAFT)

**Document Identifier:** `macro_tier_amendment_proposal.md`  
**Governing Standard Being Amended:** `runs/phase8/independent_validation_plan/acquisition_specification.md` (v1.0) & `stage_1_preparation/acquisition_pipeline_spec.md` (v1.0)  
**Proposed Version:** `v1.1-DRAFT` (For Formal Evaluation & User Authorization)  
**Current Active Version:** `v1.0-FROZEN` (Immutable; remains in full effect until ratified)  
**Target Independent Dataset:** `CarDD_Independent_Val_v1` (Target: 220–250 authentic images)  
**Date:** 2026-11-17  
**Status:** **PROPOSAL ONLY — STRICTLY READ-ONLY / AWAITING AUTHORIZATION**  

---

## 1. Executive Summary & Problem Statement

Following the completion of the Phase 8 Batch 1 forensic audit, an irreconcilable conflict was uncovered between the single-tier resolution gate codified in `v1.0` and the physical realities of authentic vehicle damage photography:

1. **The v1.0 Single-Tier Standard:**
   Codified in `acquisition_pipeline_spec.md` (Stage 2) as:
   $$\text{Width} \ge 800\text{ px} \quad \text{AND} \quad \text{Height} \ge 600\text{ px}$$
2. **The Resulting Class Wipeout:**
   Applying this single-tier gate disqualified all 6 candidate images from the institutional CC0 Humans in the Loop repository (`CS_VAL_020` through `CS_VAL_025`) because their native bounding-box crops range between $629 \times 419$ and $881 \times 476$.
3. **Severe Distributional Distortion:**
   As a direct consequence, Batch 1 was reduced to 15 images with **strictly zero representation** for **Crack (0)**, **Lamp Broken (0)**, and **Scratch (0)**, defeating the primary objective of Batch 1 to establish baseline multi-class representation.

This document formally proposes amending the acquisition specification to a **Dual-Tier Resolution Architecture (v1.1)** that establishes rigorous, scientifically grounded standards for both **Full-Vehicle Walkaround Imagery** and **Macro Component Inspection Imagery**.

---

## 2. Proposed Dual-Tier Specification Architecture (v1.1-DRAFT)

Under the proposed `v1.1` specification, candidate images are categorized into one of two mutually exclusive tiers upon ingestion, each subject to distinct, verifiable geometric and contextual gates:

```
┌────────────────────────────────────────────────────────────────────────┐
│             PROPOSED DUAL-TIER RESOLUTION ARCHITECTURE (v1.1)          │
├──────────────────────────────────┬─────────────────────────────────────┤
│ TIER 1: Full-Vehicle Walkaround  │ TIER 2: Macro Component Inspection  │
├──────────────────────────────────┼─────────────────────────────────────┤
│ • Role: Global vehicle context,  │ • Role: Localized fracture, scratch │
│   multi-panel damage, alignment. │   depth, shattered lens textures.   │
│ • Minimum Resolution:            │ • Minimum Resolution:               │
│   Width >= 800 px AND            │   Width >= 600 px AND               │
│   Height >= 600 px               │   Height >= 400 px                  │
│ • Aspect Ratio: Free (>= 0.5)    │ • Aspect Ratio: Free (>= 0.5)       │
│ • Context Coverage: Vehicle body │ • Damage Occupancy Rule: Localized  │
│   must occupy >= 60% of frame.   │   damage bbox must occupy >= 30%    │
│ • Permitted Share of Dataset:    │   of the total image area.          │
│   Minimum 70% of total dataset.  │ • Permitted Share of Dataset:       │
│                                  │   Maximum 30% of total dataset.     │
└──────────────────────────────────┴─────────────────────────────────────┘
```

### Detailed Tier Criteria:

#### Tier 1 — Full-Vehicle Walkaround Standard
- **Resolution Floor:** $\text{Width} \ge 800\text{ px}$ AND $\text{Height} \ge 600\text{ px}$ (Total pixels $\ge 480,000$).
- **Visual Stance:** Camera distance 2.0m to 5.0m; captures the full vehicle silhouette, complete body assemblies (front clip, rear quarter, full side profile), or multiple contiguous panels.
- **Orientation:** Landscape or Portrait, provided $\min(w, h) \ge 600\text{ px}$ and $\max(w, h) \ge 800\text{ px}$.
- **Dataset Allocation Quota:** $\ge 70\%$ of the final 200+ image dataset must belong to Tier 1.

#### Tier 2 — Macro Component Inspection Standard
- **Resolution Floor:** $\text{Width} \ge 600\text{ px}$ AND $\text{Height} \ge 400\text{ px}$ (Total pixels $\ge 240,000$).
- **Damage Occupancy Ceiling Rule:** Localized vehicle damage (defined by the bounding box enclosing the primary defect) must occupy **at least 30.0% of the total image area**:
  $$\frac{\text{Area}(\text{BBox}_{\text{damage}})}{\text{Width} \times \text{Height}} \ge 0.30$$
- **Visual Stance:** Camera distance 0.3m to 1.2m; dedicated macro inspection of an isolated vehicle component (e.g. cracked plastic bumper lip, smashed headlamp housing, deep key scratch across door panel, hail-dimpled hood section).
- **Orientation Rule:** Orientation-agnostic. Evaluated as $\min(w, h) \ge 400\text{ px}$ AND $\max(w, h) \ge 600\text{ px}$, explicitly permitting vertical component crops (e.g., A/B pillar cracks, vertical door seam scratches).
- **Dataset Allocation Ceiling:** Strictly capped at **$\le 30\%$ of the final 200+ image dataset** to prevent macro-bias.

---

## 3. Mathematical & Empirical Comparison: $600 \times 400$ vs. $640 \times 400$

During initial discussions, a threshold of $640 \times 400$ (matching standard 16:10 or $640\text{-scale}$ VGA) was contemplated. A forensic comparison reveals why $600 \times 400$ is mathematically superior:

| Evaluation Metric | Threshold A: $640 \times 400$ | Threshold B: $600 \times 400$ (Proposed) | Practical Impact on Humans in the Loop (HITL) Sourcing |
| :--- | :---: | :---: | :--- |
| **Minimum Pixel Area** | $256,000\text{ px}$ | $240,000\text{ px}$ | Difference of only $16,000\text{ px}$ (6.25%). |
| **CS_VAL_020 ($637 \times 419$)** | **FAIL** ($-3\text{ px}$ on width) | **PASS** ($+37\text{ px}$ width, $+19\text{ px}$ height) | Disqualified by 3 pixels under 640; qualified under 600. |
| **CS_VAL_021 ($637 \times 440$)** | **FAIL** ($-3\text{ px}$ on width) | **PASS** ($+37\text{ px}$ width, $+40\text{ px}$ height) | Disqualified by 3 pixels under 640; qualified under 600. |
| **CS_VAL_022 ($629 \times 471$)** | **FAIL** ($-11\text{ px}$ on width) | **PASS** ($+29\text{ px}$ width, $+71\text{ px}$ height) | Disqualified by 11 pixels under 640; qualified under 600. |
| **CS_VAL_023 ($881 \times 476$)** | **PASS** ($+241\text{ px}$ width) | **PASS** ($+281\text{ px}$ width, $+76\text{ px}$ height) | Passes both thresholds comfortably. |
| **CS_VAL_024 ($637 \times 442$)** | **FAIL** ($-3\text{ px}$ on width) | **PASS** ($+37\text{ px}$ width, $+42\text{ px}$ height) | Disqualified by 3 pixels under 640; qualified under 600. |
| **CS_VAL_025 ($637 \times 444$)** | **FAIL** ($-3\text{ px}$ on width) | **PASS** ($+37\text{ px}$ width, $+44\text{ px}$ height) | Disqualified by 3 pixels under 640; qualified under 600. |
| **HITL Survival Rate** | **16.7% (1 of 6 images)** | **100.0% (6 of 6 images)** | **640x400 arbitrarily wipes out 5 authentic CC0 images.** |

### The "Effective Damage Resolution" Paradox:
A common misconception is that a $1920 \times 1080$ full-vehicle image always provides higher damage resolution than a $637 \times 419$ macro crop. Empirically, the opposite is true:
- In a full-vehicle walkaround ($1920 \times 1080 = 2,073,600\text{ px}$), a $20\text{ cm}$ bumper crack typically occupies less than $0.5\%$ of the total image area:
  $$\text{Damage Pixels}_{\text{Walkaround}} \approx 2,073,600 \times 0.005 \approx \mathbf{10,368\text{ px}}$$
- In a Tier 2 macro inspection crop ($637 \times 419 = 266,903\text{ px}$), the same crack fills $55\%$ of the frame:
  $$\text{Damage Pixels}_{\text{Macro}} \approx 266,903 \times 0.55 \approx \mathbf{146,796\text{ px}}$$
**Conclusion:** The Tier 2 macro crop delivers **over $14\times$ greater pixel density directly on the defect itself**, providing superior visual evidence for crack propagation and scratch depth without introducing interpolation artifacts.

---

## 4. Multi-Attribute Eligibility Recalculation for Candidates `CS_VAL_020` to `CS_VAL_025`

Resolution eligibility is necessary but not sufficient. Candidate images must satisfy all quality, occupancy, provenance, privacy, and licensing criteria to earn final certification:

| Candidate ID | Stated Class | Dimensions | Damage Area Occupancy | Lap. Blur Var ($\ge 50.0$) | License Status | PII & Privacy Status | EXIF Decoupling | Proposed v1.1 Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `CS_VAL_020` | Crack | $637 \times 419$ | **59.3%** ($\ge 30\%$) | **914.6** (Sharp) | CC0 Institutional | 0 Plates, 0 Faces | Purged (0 Tags) | **QUALIFIED (Tier 2)** |
| `CS_VAL_021` | Crack | $637 \times 440$ | **51.4%** ($\ge 30\%$) | **301.7** (Sharp) | CC0 Institutional | 0 Plates, 0 Faces | Purged (0 Tags) | **QUALIFIED (Tier 2)** |
| `CS_VAL_022` | Lamp Broken | $629 \times 471$ | **76.1%** ($\ge 30\%$) | **1298.2** (Sharp) | CC0 Institutional | 0 Plates, 0 Faces | Purged (0 Tags) | **QUALIFIED (Tier 2)** |
| `CS_VAL_023` | Lamp Broken | $881 \times 476$ | **54.1%** ($\ge 30\%$) | **625.4** (Sharp) | CC0 Institutional | 0 Plates, 0 Faces | Purged (0 Tags) | **QUALIFIED (Tier 2)** |
| `CS_VAL_024` | Scratch | $637 \times 442$ | **45.3%** ($\ge 30\%$) | **1113.9** (Sharp) | CC0 Institutional | 0 Plates, 0 Faces | Purged (0 Tags) | **QUALIFIED (Tier 2)** |
| `CS_VAL_025` | Dent | $637 \times 444$ | **60.1%** ($\ge 30\%$) | **1218.0** (Sharp) | CC0 Institutional | 0 Plates, 0 Faces | Purged (0 Tags) | **QUALIFIED (Tier 2)** |

### Evaluation of Additional Sub-800x600 Wikimedia Candidates:
- **`CS_VAL_016` (Dent, $640 \times 480$, Missouri Hail):** Occupies $72.0\%$ damage area; Laplacian Var 310.6; Public Domain; 0 PII; 0 EXIF. **QUALIFIED (Tier 2).**
- **`CS_VAL_017` (Dent, $720 \times 960$ Portrait, Hail Damage):** Occupies $65.0\%$ damage area; Laplacian Var 1247.1; Public Domain; 0 PII; 0 EXIF. Under the proposed orientation-agnostic rule ($\min \ge 400, \max \ge 600$), this file is **QUALIFIED (Tier 2).**

All 25 candidates are fully evaluated in [batch_01_revised_eligibility.csv](file:///C:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/independent_validation_plan/batch_01_revised_eligibility.csv).

---

## 5. Scientific Rationale, Computer Vision Principles & Domain Shift Risks

### A. Computer Vision Rationale: Feature Pyramid Hierarchy
Modern object detectors like YOLOv8 utilize a Feature Pyramid Network (FPN) with three detection heads operating at strides 8, 16, and 32:
- **P3 Head (Stride 8):** Specialized for small objects (e.g. tiny clearcoat scratches or small hail dimples on a full vehicle shot).
- **P4 Head (Stride 16):** Specialized for medium objects (e.g. broken headlights, medium dents).
- **P5 Head (Stride 32):** Specialized for large objects (e.g. whole-bumper collisions, large panels).

When a detector is presented with a **Tier 2 Macro Crop**, the damage defect occupies a large portion of the visual receptive field. This triggers detection primarily through the **P4 and P5 heads** rather than P3. Incorporating macro images directly validates whether the model's high-level semantic features recognize damage textures independent of global vehicle silhouette priors.

### B. Domain Shift Risks & Failure Modes
Permitting macro crops introduces three distinct operational risks:
1. **Contextual Prior Loss (False Positive Vulnerability):**
   Full-vehicle shots allow the detector to use global geometry (e.g. knowing where the hood ends and the bumper begins). In isolated macro crops, high-contrast natural features (panel seams, door gaps, rubber window trim, sharp body character lines) lose their contextual anchor and may trigger spurious false-positive crack or scratch detections.
2. **Anchor Scale Mismatch:**
   If model weights are calibrated primarily on small defects, evaluating on macro crops tests multi-scale transfer. While desirable for insurance inspection apps, a dataset dominated by macro crops would penalize detectors optimized for walkaround appraisal.
3. **Background Texture Ambiguity:**
   In close-up crops, reflections of tree branches, overhead power lines, or specular sun glints on metallic clearcoat closely resemble long scratches. Without the vehicle's surrounding context, distinguishing a true scratch from a reflection is significantly more difficult.

### C. Risk Mitigation Strategy (Enforced Quotas)
To prevent macro crops from distorting benchmark integrity, the proposed `v1.1` specification establishes strict safeguards:
- **Hard Quota Ceiling:** Tier 2 Macro imagery is strictly capped at **maximum 30.0% of total dataset instances** (e.g. no more than 60 of 200 images).
- **Stratified Evaluation Reporting:** Model benchmark reports must evaluate and report performance **disaggregated by tier** (Tier 1 Precision/Recall vs. Tier 2 Precision/Recall) in addition to overall aggregate metrics, preventing performance on macro crops from obscuring walkaround deficiencies.

---

## 6. Revised Class-Coverage Projection (Strict Qualified Data Only)

In strict accordance with project governance, **projected candidate discoveries are NOT counted as acquired or annotated data**. The table below reflects strictly the images acquired and verified in Batch 1:

| Damage Category | v1.0 Certified Valid (Single-Tier 800x600) | Proposed v1.1 Qualified (Dual-Tier Architecture) | Net Reclaimed | Validation Dataset Target | Remaining Deficit Under Proposed v1.1 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Tire Flat** | 7 | **7** (Tier 1) | 0 | 30+ instances | **23 instances** |
| **Glass Shatter** | 6 | **6** (Tier 1) | 0 | 40+ instances | **34 instances** |
| **Dent** | 2 | **4** (2 Tier 1 + 2 Tier 2) | +2 | 90+ instances | **86 instances** |
| **Crack** | **0** | **2** (2 Tier 2) | **+2** | 60+ instances | **58 instances** |
| **Lamp Broken** | **0** | **2** (2 Tier 2) | **+2** | 45+ instances | **43 instances** |
| **Scratch** | **0** | **1** (1 Tier 2) | **+1** | 100+ instances | **99 instances** |
| **Total Qualified** | **15 images** | **23 images (15 Tier 1 + 8 Tier 2)** | **+8** | **200+ images** | **177 images remaining** |

### Tier Distribution in Qualified Batch 1:
- **Tier 1 (Walkaround):** 15 images (**65.2%** of qualified Batch 1)
- **Tier 2 (Macro Component):** 8 images (**34.8%** of qualified Batch 1)
*(Note: To meet the final dataset quota of $\le 30\%$ Tier 2 across the 200-image dataset, subsequent batches must allocate at least 72% to Tier 1 walkarounds).*

---

## 7. Approval Checklist & Unresolved Questions for User Decision

Before `v1.1` can be formally applied to project files or manifests, the following checklist items require explicit user determination:

### A. Formal Approval Checklist
- [ ] **Decision Point 1: Dual-Tier Architecture Approval:** Does the project approve establishing a two-tier evaluation standard separating Full-Vehicle Walkarounds from Macro Component Inspections?
- [ ] **Decision Point 2: Macro Resolution Threshold Selection:** Does the project approve $\text{Width} \ge 600\text{ px}$ AND $\text{Height} \ge 400\text{ px}$ (accommodating 6 HITL CC0 images) over $640 \times 400$ (which disqualifies 5 HITL images by 3–11 pixels)?
- [ ] **Decision Point 3: Damage Area Occupancy Requirement:** Is the $\ge 30.0\%$ localized damage bounding box occupancy threshold approved as a hard prerequisite for Tier 2 qualification?
- [ ] **Decision Point 4: Portrait Orientation Authorization:** Is orientation-agnostic evaluation ($\min \ge 400, \max \ge 600$) explicitly authorized for Tier 2 component imagery?
- [ ] **Decision Point 5: Dataset Allocation Ceiling:** Is the maximum 30.0% cap on Tier 2 images approved to protect the validation benchmark against macro domain shift?

### B. Unresolved Governance Questions
1. **Quarantine Handling of Existing Processed Copies:**  
   If `v1.1` is approved, should the 8 currently quarantined processed copies in `batch_01/processed/` be officially certified and linked to `acquisition_manifest.csv`? If `v1.1` is rejected, should they be deleted from `processed/` and moved permanently to `batch_01/rejected/`?
2. **Annotation Protocol Adaptation:**  
   Should dual-blind annotators be instructed to label full component outlines (e.g. whole bumper) or tight damage polygons on Tier 2 macro crops? (Proposed recommendation: tight damage polygons with component type recorded in metadata).

---

## 8. Current Governance Gate Status

- **Amendment Proposal is COMPLETE and preserved in DRAFT.**
- **Specification v1.0 remains FROZEN and UNMODIFIED.**
- **No image files, manifests, checkpoints, or production scripts have been altered.**
- **Awaiting formal user sign-off on the approval checklist before taking any further action.**
