# ClaimSense AI — Phase 8: Final v1.1 Ratification Readiness Review
## Dual-Tier Resolution Architecture & Quarantined Candidate Governance

**Document Identifier:** `final_v1_1_ratification_readiness.md`  
**Governing Baseline:** `runs/phase8/independent_validation_plan/acquisition_specification.md` (v1.0 Active)  
**Target Specification:** `runs/phase8/independent_validation_plan/macro_tier_amendment_proposal.md` (v1.1-DRAFT)  
**Target Dataset:** `CarDD_Independent_Val_v1`  
**Execution Mode:** STRICTLY READ-ONLY / AUDIT & GOVERNANCE PROPOSAL ONLY  
**Date:** 2026-11-17  
**Status:** **PENDING FORMAL USER RATIFICATION**  

---

## Executive Summary

This document presents the final evidence-backed readiness review for the proposed **Dual-Tier Resolution Architecture (`v1.1-DRAFT`)** of the independent real-world validation dataset (`CarDD_Independent_Val_v1`).

Following the completion of the Batch 1 Acquisition (25 attempted candidates), forensic quality verification revealed that under the active **Single-Tier Specification v1.0** (requiring strictly $\text{Width} \ge 800\text{ px}$ and $\text{Height} \ge 600\text{ px}$), **15 images** are certified valid, **2 images** are rejected for optical blur, and **8 images** fail the single-tier resolution gate despite possessing authentic, high-value damage depictions (cracks, broken lamps, scratches, and hail dent clusters).

This review formally establishes:
1. **v1.0 Baseline Preserved:** Specification `v1.0` remains the sole legally active baseline until explicit user sign-off.
2. **Dual-Tier Specification (v1.1-DRAFT):** Establishes mathematical definitions for Tier 1 (Walkaround) and Tier 2 (Macro Component), with orientation agnosticism and strict damage occupancy requirements ($\ge 30.0\%$).
3. **Provisional Pre-Screening Disclaimer:** Pre-screening Axis-Aligned Bounding Box (AABB) estimates are **provisional heuristic approximations** and cannot certify images into the dataset.
4. **Dual-Blind Annotation Workflow:** A 4-stage protocol (independent blind annotation, IoU consensus matching, senior adjudication, coordinate verification) mandated before any quarantined candidate can be considered for certification.
5. **Itemized Evidence & Adjudication Status:** Detailed forensic breakdown of all 8 quarantined images, specifically highlighting edge cases (`CS_VAL_024` scratch AABB vs. pixel mask; `CS_VAL_022` lamp boundary).
6. **Disaggregated Benchmark Reporting Mandate:** Requirement that validation benchmarks report Tier 1, Tier 2, and Composite metrics separately to preserve evaluation integrity.
7. **Five-Gate Ratification Matrix:** Decoupling architectural approval, specification activation, annotation authorization, asset promotion, and Batch 2 acquisition into five independently signable governance gates.

---

## 1. Specification Baseline & Proposed v1.1 Architecture

### 1.1 Specification Status
- **Active Standard:** `v1.0` remains 100% active and enforced.
- **Draft Standard:** `v1.1-DRAFT` is strictly a proposal undergoing ratification review.
- **No Automatic Promotion:** No quarantined candidate (`CS_VAL_016`, `CS_VAL_017`, `CS_VAL_020`–`CS_VAL_025`) has been promoted to the certified dataset or included in active evaluation manifests.

### 1.2 Exact Proposed v1.1 Definitions

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 v1.1 DUAL-TIER RESOLUTION ARCHITECTURE                                 │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ TIER 1: Full-Vehicle Walkaround Inspection                                                             │
│ • Dimensional Floor:  Width >= 800 px  AND  Height >= 600 px                                           │
│ • Orientation:        Landscape or Portrait (both dimensions must satisfy >= 800 and >= 600)           │
│ • Visual Stance:      Global vehicle context, multi-panel perspective, full silhouette, or assemblies  │
│ • Target Quota Share: >= 70.0% of cumulative final validation dataset instances                        │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ TIER 2: Macro Component Inspection                                                                     │
│ • Dimensional Floor:  min(Width, Height) >= 400 px  AND  max(Width, Height) >= 600 px                 │
│ • Orientation:        Orientation-Agnostic (supports 600x400 landscape and 400x600 portrait crops)     │
│ • Damage Occupancy:   >= 30.0% of total image area (Width * Height)                                   │
│ • Metric Standard:    Measured via verified YOLO Axis-Aligned Bounding Box (AABB)                      │
│ • Target Quota Share: <= 30.0% of cumulative final validation dataset instances (hard ceiling)         │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Mathematical Formulation of Damage Occupancy

For any candidate image $I$ with dimensions $W \times H$, damage occupancy is defined as:

$$\text{Occupancy}(I) = \frac{\sum_{k=1}^{K} \text{Area}(\text{AABB}_k)}{W \times H} = \frac{\sum_{k=1}^{K} (x_{2,k} - x_{1,k}) \times (y_{2,k} - y_{1,k})}{W \times H}$$

Where:
- $K$ is the number of validated damage instances on the target component.
- In multi-instance scenarios (e.g. hail clusters), overlapping areas between bounding boxes must be subtracted to prevent double-counting.
- Under Tier 2 eligibility, $\text{Occupancy}(I) \ge 0.3000$ (30.0%).

---

## 2. Provisional Nature of Pre-Screening Occupancy Estimates

### 2.1 Heuristic Visual Estimates vs. Ground Truth
During the Batch 1 quality audit, heuristic bounding boxes were plotted to verify that candidates satisfied the basic premise of macro component imagery. The resulting occupancy figures (e.g. `CS_VAL_016`: 72.0%, `CS_VAL_020`: 59.3%, `CS_VAL_022`: 76.1%, `CS_VAL_024`: 45.3%):

> [!WARNING]
> **PROVISIONAL ESTIMATES DISCLAIMER:**  
> The pre-screening occupancy values reported in the Batch 1 screening manifests are **preliminary, single-observer heuristic visual estimates**. They are **NOT GROUND TRUTH** and have **NO FORMAL LEGAL OR STATISTICAL STANDING**. They cannot be used to certify an image into `CarDD_Independent_Val_v1`.

### 2.2 Certification Dependency
Under governance protocols, an image is certified into Tier 2 **if and only if**:
1. Dual-blind independent human annotators generate coordinates.
2. Annotator agreement satisfies $\text{IoU} \ge 0.50$ (or is formally resolved by Senior Adjudicator C).
3. The final adjudicated bounding box independently measures $\ge 30.0\%$ area occupancy.

---

## 3. Independent Dual-Blind Annotation Workflow for Quarantined Images

To guarantee objective, uncorrupted ground truth, all 8 quarantined images must undergo an independent dual-blind annotation process.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 DUAL-BLIND ANNOTATION WORKFLOW                                   │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│       ┌────────────────────────┐                    ┌────────────────────────┐                   │
│       │      REVIEWER A        │                    │      REVIEWER B        │                   │
│       │  Independent Blind     │                    │  Independent Blind     │                   │
│       │  Annotation            │                    │  Annotation            │                   │
│       └───────────┬────────────┘                    └───────────┬────────────┘                   │
│                   │                                             │                                │
│                   └──────────────────────┬──────────────────────┘                                │
│                                          │                                                       │
│                                          ▼                                                       │
│                           ┌─────────────────────────────┐                                        │
│                           │      CONSENSUS ENGINE       │                                        │
│                           │   IoU >= 0.50 & Class Match │                                        │
│                           └──────────────┬──────────────┘                                        │
│                                          │                                                       │
│                      ┌───────────────────┴───────────────────┐                                   │
│                      │                                       │                                   │
│            [Consensus Achieved]                    [Conflict / Disagreement]                     │
│                      │                                       │                                   │
│                      ▼                                       ▼                                   │
│        ┌───────────────────────────┐           ┌───────────────────────────┐                     │
│        │   COORDINATE MERGE        │           │   SENIOR ADJUDICATOR C    │                     │
│        │ Mean Box Coordinates      │           │ Independent Blind Review  │                     │
│        │ Class Confirmed           │           │ Binding Coordinate Choice │                     │
│        └─────────────┬─────────────┘           └─────────────┬─────────────┘                     │
│                      │                                       │                                   │
│                      └───────────────────┬───────────────────┘                                   │
│                                          │                                                       │
│                                          ▼                                                       │
│                           ┌─────────────────────────────┐                                        │
│                           │  OCCUPANCY VERIFICATION     │                                        │
│                           │ Area(AABB) / (W * H) >= 30% │                                        │
│                           └──────────────┬──────────────┘                                        │
│                                          │                                                       │
│                      ┌───────────────────┴───────────────────┐                                   │
│                      ▼                                       ▼                                   │
│            [Occupancy >= 30.0%]                     [Occupancy < 30.0%]                          │
│                      │                                       │                                   │
│                      ▼                                       ▼                                   │
│        ┌───────────────────────────┐           ┌───────────────────────────┐                     │
│        │ CERTIFIED TIER 2 IMAGE    │           │ PERMANENTLY REJECTED      │                     │
│        │ Promoted to Valid Manifest│           │ Moved to batch_01/rejected│                     │
│        └───────────────────────────┘           └───────────────────────────┘                     │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Protocol Specifications
1. **Blind Isolation:** Reviewers A and B annotate the 8 raw processed images without access to each other's work, pre-screening metadata, YOLO model detections, or preliminary occupancy numbers.
2. **Annotation Taxonomy:** Annotators use the official 6-class CarDD taxonomy:
   - `dent` (0)
   - `scratch` (1)
   - `crack` (2)
   - `glass shatter` (3)
   - `lamp broken` (4)
   - `tire flat` (5)
3. **Consensus Algorithm:**
   - Boxes match if $\text{Class}_A == \text{Class}_B$ AND $\text{IoU}(A, B) \ge 0.50$.
   - Where consensus is achieved, final box coordinates are the arithmetic mean of $A$ and $B$.
4. **Adjudication Engine (Senior Adjudicator C):**
   - Invoked when $\text{IoU} < 0.50$, classes disagree, or boundary scope differs.
   - Adjudicator C inspects the physical damage morphology and issues a final, binding label and bounding box.

---

## 4. Quarantined Candidate Evidence Status & Adjudication Dependencies

The 8 quarantined images are audited in `annotation_readiness_matrix.csv`. Their specific technical challenges and certification dependencies are detailed below:

| Candidate ID | Source | Resolution | Damage Class | Provisional AABB % | Evidence Status | Technical Challenge & Certification Dependency |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **CS_VAL_016** | Wikimedia | $640 \times 480$ | Dent | 72.0% | PROVISIONAL (High Conf.) | **Hail Cluster Granularity:** Annotators must be guided whether to bound the entire dimpled hood panel or individual hail dimples. Since the cluster covers the hood, cluster AABB is 72.0%. |
| **CS_VAL_017** | Wikimedia | $720 \times 960$ | Dent | 65.0% | PROVISIONAL (High Conf.) | **Portrait Orientation:** Requires formal ratification of orientation-agnostic Tier 2 rules. Sheet metal hail dents occupy $> 65\%$ of vertical frame. |
| **CS_VAL_020** | HITL | $637 \times 419$ | Crack | 59.3% | PROVISIONAL (Mod. Conf.) | **Bumper Fracture Boundary:** Reviewers must reach consensus on crack termination endpoints along displaced plastic bumper flange. |
| **CS_VAL_021** | HITL | $637 \times 440$ | Crack | 51.4% | PROVISIONAL (Mod. Conf.) | **Mounting Seam vs. Split:** Reviewers must distinguish authentic impact fracture from OEM bumper assembly seams. |
| **CS_VAL_022** | HITL | $629 \times 471$ | Lamp Broken | 76.1% | **UNRESOLVED BOUNDARY** | **Assembly vs. Lens Boundary & Class Conflict:** Smashed headlamp presents shattered glass/polycarbonate inside a crushed housing. Risk of annotator choosing `glass shatter` vs. `lamp broken`. Adjudication rule must mandate: *damage to vehicle lighting fixtures is strictly `lamp broken`*, bounding the entire fractured assembly. |
| **CS_VAL_023** | HITL | $881 \times 476$ | Lamp Broken | 54.1% | PROVISIONAL (High Conf.) | **Height Floor Failure ($476 < 600$):** Clear taillight lens fracture. Passes Tier 2 dimensional rules ($\min=476 \ge 400, \max=881 \ge 600$). Clear housing boundary. |
| **CS_VAL_024** | HITL | $637 \times 442$ | Scratch | 45.3% | **UNRESOLVED AREA EVIDENCE** | **AABB vs. Pixel Mask Discrepancy:** Severe diagonal door key scratch. The bounding box enclosing the scratch diagonal occupies **45.3%** of the frame, but physical scratch pixel area is **$< 1.5\%$**. If annotators segment the stroke into 4 smaller bounding boxes, each box occupies $< 8\%$, causing the image to FAIL Tier 2. Adjudication rule must explicitly define: *continuous scratch streaks are bounded as a single contiguous AABB*. |
| **CS_VAL_025** | HITL | $637 \times 444$ | Dent | 60.1% | PROVISIONAL (High Conf.) | **Concave Deformation Inflection Rim:** Fender impact dent. Annotators must identify the subtle outer rim of deformation across the curved wheel arch. |

---

## 5. Macro Quota Arithmetic & Dataset Scale Projections

In Batch 1, 8 candidates are proposed for Tier 2 out of 23 qualified images, yielding a preliminary ratio of:

$$\frac{8}{23} = 34.78\% > 30.00\% \quad (\text{Temporary Quota Violation})$$

The consistency audit confirmed that this temporary ratio is a mathematical artifact of small batch sizing ($N=23$) and does not invalidate the candidates.

### 5.1 Minimum Absorption Scale
To bring 8 Tier 2 images strictly within the $\le 30.0\%$ ceiling without dropping any image:

$$N_{\text{min}} = \left\lceil \frac{8}{0.30} \right\rceil = \mathbf{27\text{ images}}$$

Acquiring just **4 additional Tier 1 Walkaround images** in Batch 2 immediately brings the cumulative dataset to $\frac{8}{27} = 29.63\% \le 30.0\%$.

### 5.2 Target Scale Scenarios

| Final Dataset Target ($N$) | Max Permitted Tier 2 ($\le 30\%$) | Current Proposed Tier 2 | Available Tier 2 Headroom | Min Required Tier 1 ($\ge 70\%$) | Current Certified Tier 1 | Required Tier 1 Acquisitions |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **27 (Absorption Min)** | 8 | 8 | 0 | 19 | 15 | **4** |
| **100 (Mid-Scale)** | 30 | 8 | 22 | 70 | 15 | **55** |
| **200 (Primary Target)** | 60 | 8 | 52 | 140 | 15 | **125** |
| **220 (Extended)** | 66 | 8 | 58 | 154 | 15 | **139** |
| **250 (Full Production)** | 75 | 8 | 67 | 175 | 15 | **160** |

Across all realistic dataset scales ($N=200$ to $250$), **at least 70% of all future acquisitions must strictly be Tier 1 Walkaround images**, ensuring that macro component imagery remains a controlled secondary component.

---

## 6. Mandated Disaggregated Benchmark Reporting Protocol

To prevent macro component inspection images from skewing walkaround damage detection benchmarks, the evaluation protocol (`evaluation_protocol.md`) must enforce **disaggregated multi-tier reporting**:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│                           MANDATED VALIDATION BENCHMARK ARCHITECTURE                           │
├────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                │
│   ┌─────────────────────────┐    ┌─────────────────────────┐    ┌──────────────────────────┐   │
│   │    TIER 1 BENCHMARK     │    │    TIER 2 BENCHMARK     │    │   COMPOSITE BENCHMARK    │   │
│   │   Walkaround Context    │    │   Macro Inspection      │    │    Full Real-World Mix   │   │
│   │   (Width, Height >=800) │    │   (Damage Area >=30%)   │    │   (Weighted Combined)    │   │
│   ├─────────────────────────┤    ├─────────────────────────┤    ├──────────────────────────┤   │
│   │ • mAP@0.50 (Walkaround) │    │ • mAP@0.50 (Macro)      │    │ • Overall mAP@0.50       │   │
│   │ • mAP@0.50:0.95         │    │ • mAP@0.50:0.95         │    │ • Overall mAP@0.50:0.95  │   │
│   │ • Precision / Recall    │    │ • Precision / Recall    │    │ • Class-Wise Metrics     │   │
│   │ • False Positive Rate   │    │ • Local IoU Tightness   │    │ • Macro Bias Coefficient │   │
│   └─────────────────────────┘    └─────────────────────────┘    └──────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 6.1 Scientific Rationale
1. **Scale Invariance Isolation:** Full-vehicle walkarounds test the model's ability to detect small damage signatures in broad context; macro component images test the model's ability to delineate severe localized damage without full vehicle cues.
2. **Prevention of Metric Masking:** A model with poor performance on subtle door dents in walkaround shots could appear artificially competent if macro images dominate the test set.
3. **Insurance Carrier Utility:** Underwriters require distinct validation metrics for mobile claimant smartphone walkarounds vs. repair shop tear-down macro photos.

---

## 7. The Five-Gate Ratification Matrix

Governance decisions are divided into five distinct, sequentially gated authorizations:

| Gate | Title | Required Input Condition | Operational Authority Granted | Current Status |
| :---: | :--- | :--- | :--- | :---: |
| **GATE A** | **Approval of Dual-Tier Architecture Principle** | Review of consistency audit and mathematical quota proofs. | Accepts dual-tier structure: Tier 1 ($\ge 800 \times 600$), Tier 2 ($\ge 600 \times 400$, $\ge 30\%$ AABB occupancy, $\le 30\%$ ceiling). | **AWAITING USER SIGN-OFF** |
| **GATE B** | **Activation of v1.1 Specification Documents** | Gate A approved. Specification texts finalized. | Authorizes archiving `v1.0` to `archive/v1_0/` and promoting `v1.1-DRAFT` to active specification files. | **AWAITING USER SIGN-OFF** |
| **GATE C** | **Authorization of Dual-Blind Annotation Work** | Gate B approved. Annotation guidelines ratified. | Unlocks Reviewer A and Reviewer B to perform independent dual-blind labeling of the 8 quarantined images. | **AWAITING USER SIGN-OFF** |
| **GATE D** | **Promotion of Eligible Adjudicated Images** | Gate C completed. Consensus reached and verified $\text{Occupancy} \ge 30.0\%$. | Formally moves qualifying candidates from quarantine to active certified status in `acquisition_manifest.csv`. | **AWAITING USER SIGN-OFF** |
| **GATE E** | **Batch 2 Candidate Acquisition Authorization** | Gates A & B approved. Manifests synchronized. | Authorizes download and screening of up to 50 candidate images for Batch 2 ($\ge 72\%$ Tier 1, $\le 28\%$ Tier 2). | **AWAITING USER SIGN-OFF** |

---

## 8. Ratification Sign-Off Framework

```
========================================================================================
                      FORMAL USER RATIFICATION RECORD (PHASE 8)
========================================================================================

Project:              ClaimSense AI
Component:            Phase 8 Independent Validation Dataset (CarDD_Independent_Val_v1)
Review Document:      runs/phase8/independent_validation_plan/final_v1_1_ratification_readiness.md
Accompanying Files:   final_approval_matrix.md
                      annotation_readiness_matrix.csv
                      v1_1_consistency_audit.md

[ ] GATE A: Dual-Tier Architecture Principle
    [ ] Approved    [ ] Rejected    [ ] Deferred

[ ] GATE B: Formal Activation of v1.1 Specification Files
    [ ] Approved    [ ] Rejected    [ ] Deferred

[ ] GATE C: Dual-Blind Annotation of 8 Quarantined Images
    [ ] Approved    [ ] Rejected    [ ] Deferred

[ ] GATE D: Promotion Protocol for Adjudicated Images
    [ ] Approved    [ ] Rejected    [ ] Deferred

[ ] GATE E: Batch 2 Candidate Acquisition (50 Candidates)
    [ ] Approved    [ ] Rejected    [ ] Deferred

----------------------------------------------------------------------------------------
User Signature / Directive: ___________________________________________________________
Timestamp:                  ___________________________________________________________
========================================================================================
```

> [!IMPORTANT]
> **GOVERNANCE COMMITMENT:**  
> Until explicit user sign-off is recorded for one or more gates, the agent remains in **STRICTLY READ-ONLY** mode. No files will be overwritten, no images will be promoted, no annotation tools will be launched, and no new images will be acquired.
