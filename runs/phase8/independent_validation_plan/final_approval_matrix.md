# ClaimSense AI — Phase 8: Final Independent Dataset Ratification Approval Matrix

**Document Identifier:** `final_approval_matrix.md`  
**Governing Standard:** `runs/phase8/independent_validation_plan/final_v1_1_ratification_readiness.md`  
**Target Dataset:** `CarDD_Independent_Val_v1`  
**Execution Mode:** STRICTLY READ-ONLY / DECISION FRAMEWORK ONLY  
**Date:** 2026-11-17  
**Status:** **AWAITING USER MULTI-GATE SIGN-OFF**  

---

## 1. Architectural Overview of the Five Distinct Governance Gates

To ensure strict compliance with project governance and prevent unauthorized cascading actions, ratification is partitioned into **five distinct, independently signable gates**:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   FIVE-GATE RATIFICATION ARCHITECTURE                  │
├────────────────────────────────────────────────────────────────────────┤
│ GATE A: Approval of Dual-Tier Architecture Principle                   │
│         (Separates Walkarounds >=800x600 from Macro >=600x400)         │
│                                    │                                   │
│                                    ▼                                   │
│ GATE B: Formal Activation of v1.1 Specification Files                  │
│         (Promotes acquisition_specification.md to v1.1)                │
│                                    │                                   │
│                                    ▼                                   │
│ GATE C: Authorization of Dual-Blind Annotation Work                    │
│         (Unlocks Reviewer A & B for the 8 Quarantined Macro Images)    │
│                                    │                                   │
│                                    ▼                                   │
│ GATE D: Promotion of Post-Annotation Adjudicated Images                │
│         (Certifies verified images into active dataset manifests)      │
│                                    │                                   │
│                                    ▼                                   │
│ GATE E: Batch 2 Acquisition Authorization                              │
│         (Unlocks acquisition of subsequent 50 candidates)              │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Itemized Gate Evaluation & Decision Matrix

| Gate ID | Scope of Authority | Pre-Conditions Required | Technical Impact if Approved | Consequence if Deferred / Rejected | User Sign-Off |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **GATE A** | **Approval of Dual-Tier Architecture Principle** | Consistency audit complete; quota arithmetic verified ($N \ge 27$). | Establishes Tier 1 ($\ge 800 \times 600$) and Tier 2 ($\ge 600 \times 400$ with $\ge 30\%$ AABB damage occupancy). | Dataset remains Single-Tier v1.0 ($\ge 800 \times 600$). Macro crops permanently barred. | [ ] Approved<br>[ ] Deferred<br>[ ] Rejected |
| **GATE B** | **Activation of v1.1 Specification Documents** | Gate A approved. Specification drafts finalized. | Promotes `macro_tier_amendment_proposal.md` from DRAFT to ACTIVE specification `v1.1`. Archives `v1.0`. | `v1.0` remains active baseline. Quarantined images cannot be processed. | [ ] Approved<br>[ ] Deferred<br>[ ] Rejected |
| **GATE C** | **Authorization of Dual-Blind Annotation Work** | Gate B approved. Annotation guidelines ratified (AABB occupancy rule). | Authorizes Reviewer A and Reviewer B to generate independent blind labels for `CS_VAL_016`, `017`, `020`–`025`. | Quarantined images remain unannotated. No human labels generated. | [ ] Approved<br>[ ] Deferred<br>[ ] Rejected |
| **GATE D** | **Promotion of Eligible Adjudicated Images** | Gate C completed. $\text{IoU} \ge 0.50$ consensus reached. Adjudicated $\text{AABB} \ge 30.0\%$ verified. | Formally promotes qualifying images from `batch_01/processed/` quarantine to certified evaluation status in `acquisition_manifest.csv`. | Quarantined images remain excluded from model evaluation benchmarks. | [ ] Approved<br>[ ] Deferred<br>[ ] Rejected |
| **GATE E** | **Batch 2 Candidate Acquisition Authorization** | Gates A & B approved. Manifests synchronized. | Authorizes controlled download and screening of up to 50 new candidate images under v1.1 dual-tier quotas ($\ge 71\%$ Tier 1). | Image acquisition remains locked at Batch 1. No new downloads. | [ ] Approved<br>[ ] Deferred<br>[ ] Rejected |

---

## 3. Detailed Gate Specifications

### Gate A: Dual-Tier Architecture Approval
- **Core Definition:** Formal project acceptance that real-world claims imagery consists of both Full-Vehicle Walkarounds ($\ge 800 \times 600$, context $\ge 60\%$) and Macro Component Inspections ($\ge 600 \times 400$, damage $\ge 30\%$).
- **Quota Ceiling:** Maximum 30.0% of final cumulative dataset instances allocated to Tier 2 ($\ge 70.0\%$ reserved for Tier 1).
- **Measurement Standard:** Damage occupancy is defined strictly as the **Axis-Aligned Bounding Box (AABB)** area enclosing the primary defect relative to total image area ($w \times h$).

### Gate B: v1.1 Specification Activation
- **File Update Protocol:** Overwrites active specification documents with versioned `v1.1` text only after Gate A sign-off:
  - Updates `runs/phase8/independent_validation_plan/acquisition_specification.md` to `v1.1`.
  - Updates `runs/phase8/independent_validation_plan/stage_1_preparation/acquisition_pipeline_spec.md` to `v1.1`.
- **Archival:** Preserves immutable copy of `v1.0` in `runs/phase8/independent_validation_plan/archive/v1_0/`.

### Gate C: Dual-Blind Annotation Authorization
- **Workflow:** Deploys Reviewer A and Reviewer B under isolated conditions (no pre-labels, no model predictions, no inter-communicated labels).
- **Consensus Rule:** Matches boxes where $\text{class}_A == \text{class}_B$ and $\text{IoU} \ge 0.50$.
- **Adjudication:** Senior Adjudicator C resolves class conflicts (e.g. `CS_VAL_022` lamp vs glass) and boundary disagreements (e.g. `CS_VAL_024` continuous scratch line vs segmented boxes).

### Gate D: Quarantined Asset Promotion
- **Post-Annotation Screening:** Each adjudicated bounding box is evaluated against the $\ge 30.0\%$ occupancy floor:
  $$\text{Verified Occupancy} = \frac{\text{Area}(\text{BBox}_{\text{adjudicated}})}{\text{Width} \times \text{Height}} \ge 0.30$$
- **Disposition:**
  - If $\ge 30.0\%$ AND class confirmed: Promoted to certified evaluation status.
  - If $< 30.0\%$ OR ambiguous: Quarantined permanently and moved to `batch_01/rejected/`.

### Gate E: Batch 2 Acquisition Authorization
- **Acquisition Cap:** Strictly 50 candidate images.
- **Quota Target:** Minimum 36 Tier 1 Walkaround candidates (72.0%) and maximum 14 Tier 2 Macro candidates (28.0%).
- **Class Prioritization:** Heavy emphasis on **Crack** (Target: 25+), **Lamp Broken** (Target: 20+), and **Scratch** (Target: 30+).

---

## 4. Formal Sign-Off Section

```
Project: ClaimSense AI
Phase: Phase 8 — Independent Real-World Validation Dataset
Ratification Stage: Final Evidence-Readiness Review

GATE A (Dual-Tier Principle):       [ ] APPROVED    [ ] REJECTED    [ ] DEFERRED
GATE B (v1.1 Activation):           [ ] APPROVED    [ ] REJECTED    [ ] DEFERRED
GATE C (Annotation Authorization):  [ ] APPROVED    [ ] REJECTED    [ ] DEFERRED
GATE D (Image Promotion Protocol):  [ ] APPROVED    [ ] REJECTED    [ ] DEFERRED
GATE E (Batch 2 Acquisition):       [ ] APPROVED    [ ] REJECTED    [ ] DEFERRED

Authorizing Stakeholder: ___________________________
Authorization Date:      ___________________________
Executive Directive:     ___________________________
```
