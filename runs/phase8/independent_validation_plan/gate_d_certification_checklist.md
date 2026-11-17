# ClaimSense AI — Phase 8: Gate D Certification Checklist
## Promotion Protocol for Adjudicated Quarantined Candidates

**Document Identifier:** `gate_d_certification_checklist.md`  
**Governing Baseline:** `runs/phase8/independent_validation_plan/acquisition_specification.md` (v1.0 Active)  
**Target Specification:** `runs/phase8/independent_validation_plan/v1_1_final_candidate.md` (v1.1-DRAFT)  
**Target Candidates:** `CS_VAL_016`, `CS_VAL_017`, `CS_VAL_020`, `CS_VAL_021`, `CS_VAL_022`, `CS_VAL_023`, `CS_VAL_024`, `CS_VAL_025`  
**Execution Mode:** STRICTLY DRAFT CHECKLIST / READ-ONLY AUDIT. NO ASSET PROMOTIONS.  
**Date:** 2026-11-17  
**Status:** **AWAITING USER GATE D AUTHORIZATION**  

---

## 1. Scope & Authority of Gate D

Gate D governs the formal operational promotion of candidates from **quarantined staging** (`datasets/CarDD_Independent_Val_v1/batch_01/processed/` quarantine list) into the **certified validation dataset** (`acquisition_manifest.csv` and active validation evaluation sets).

> [!IMPORTANT]
> **GOVERNANCE RESTRICTION:**  
> Under Project Governance, completing Gate C (annotation and adjudication) does **NOT** grant automatic promotion. Gate D requires separate, explicit user authorization. Until Gate D is signed off, all 8 images remain strictly isolated and excluded from model evaluation.

---

## 2. Gate D Pre-Conditions & Multi-Attribute Verification

Before any candidate can be promoted under Gate D, it must satisfy seven mandatory technical gates:

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           GATE D MULTI-ATTRIBUTE VERIFICATION                           │
├───────┬───────────────────────────────┬───────────────────────────────────┬─────────────┤
│ Gate  │ Attribute Name                │ Pass Threshold                    │ Audit State │
├───────┼───────────────────────────────┼───────────────────────────────────┼─────────────┤
│ 1.    │ Specification Activation      │ Gate B approved; v1.1 activated   │ Pending     │
│ 2.    │ Dual-Blind Annotation Audit   │ Gate C complete; mIoU >= 0.70     │ PASSED (91%)│
│ 3.    │ Tier 2 Dimensional Standard   │ min >= 400 px AND max >= 600 px   │ PASSED (8/8)│
│ 4.    │ Damage Occupancy Floor        │ Adjudicated AABB Area >= 30.0%    │ PASSED (8/8)│
│ 5.    │ Optical Quality Gate          │ Laplacian Blur Variance >= 50.0   │ PASSED (8/8)│
│ 6.    │ License & Legal Provenance    │ CC0 / Public Domain / CC BY       │ PASSED (8/8)│
│ 7.    │ Privacy & PII Redaction       │ EXIF stripped; 100% blacked PII   │ PASSED (8/8)│
└───────┴───────────────────────────────┴───────────────────────────────────┴─────────────┘
```

---

## 3. Reconciliation of All 25 Batch 1 Candidate Images

The 25 attempted Batch 1 images are reconciled across their complete lifecycle:

### Group A: Certified Valid Images under v1.0 (15 Images)
These images satisfy the original single-tier resolution gate ($\text{Width} \ge 800$, $\text{Height} \ge 600$) and are already certified in `acquisition_manifest.csv`:

| Image ID | Source | Resolution | Damage Class | Tier Classification | Optical Blur ($\sigma^2 \ge 50$) | License | Active Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **CS_VAL_001** | Wikimedia | $1024 \times 768$ | Tire Flat | Tier 1 (Walkaround) | 185.3 | CC BY 2.0 | CERTIFIED VALID |
| **CS_VAL_002** | Wikimedia | $2272 \times 1704$ | Tire Flat | Tier 1 (Walkaround) | 497.1 | CC BY 2.0 | CERTIFIED VALID |
| **CS_VAL_003** | Wikimedia | $2272 \times 1704$ | Tire Flat | Tier 1 (Walkaround) | 412.5 | CC BY 2.0 | CERTIFIED VALID |
| **CS_VAL_004** | Wikimedia | $2048 \times 1536$ | Tire Flat | Tier 1 (Walkaround) | 398.2 | CC BY 2.0 | CERTIFIED VALID |
| **CS_VAL_006** | Wikimedia | $3264 \times 2448$ | Tire Flat | Tier 1 (Walkaround) | 812.4 | CC BY 2.0 | CERTIFIED VALID |
| **CS_VAL_007** | Wikimedia | $3072 \times 2304$ | Tire Flat | Tier 1 (Walkaround) | 654.1 | CC BY 2.0 | CERTIFIED VALID |
| **CS_VAL_008** | Wikimedia | $3072 \times 2304$ | Tire Flat | Tier 1 (Walkaround) | 589.6 | CC BY 2.0 | CERTIFIED VALID |
| **CS_VAL_009** | Wikimedia | $3872 \times 2592$ | Glass Shatter | Tier 1 (Walkaround) | 1142.3 | CC BY 2.0 | CERTIFIED VALID |
| **CS_VAL_010** | Wikimedia | $3264 \times 2448$ | Glass Shatter | Tier 1 (Walkaround) | 981.5 | CC BY 2.0 | CERTIFIED VALID |
| **CS_VAL_012** | Wikimedia | $1200 \times 900$ | Glass Shatter | Tier 1 (Walkaround) | 245.8 | CC BY 2.0 | CERTIFIED VALID |
| **CS_VAL_013** | Wikimedia | $4032 \times 3024$ | Glass Shatter | Tier 1 (Walkaround) | 1450.2 | Public Domain | CERTIFIED VALID |
| **CS_VAL_014** | Wikimedia | $3024 \times 4032$ | Glass Shatter | Tier 1 (Walkaround) | 1320.6 | Public Domain | CERTIFIED VALID |
| **CS_VAL_015** | Wikimedia | $2048 \times 1536$ | Glass Shatter | Tier 1 (Walkaround) | 610.4 | CC BY 2.0 | CERTIFIED VALID |
| **CS_VAL_018** | Wikimedia | $2272 \times 1704$ | Dent | Tier 1 (Walkaround) | 480.2 | Public Domain | CERTIFIED VALID |
| **CS_VAL_019** | Wikimedia | $2816 \times 2112$ | Dent | Tier 1 (Walkaround) | 710.5 | Public Domain | CERTIFIED VALID |

### Group B: Quarantined Candidates Awaiting Gate D Promotion (8 Images)
These images failed the v1.0 single-tier gate, but satisfy Tier 2 resolution, completed Gate C dual-blind annotation, and verified $\ge 30.0\%$ AABB occupancy:

| Candidate ID | Source | Resolution | Damage Class | Final Box $[x_1, y_1, x_2, y_2]$ | Box Area (px) | Verified Occupancy % | Derivation Method | Gate D Readiness |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **CS_VAL_016** | Wikimedia | $640 \times 480$ | Dent | $[48, 38, 598, 440]$ | 221,100 | **71.97%** | Consensus ($\text{IoU}=0.946$) | READY FOR PROMOTION |
| **CS_VAL_017** | Wikimedia | $720 \times 960$ | Dent | $[60, 75, 670, 745]$ | 408,700 | **59.13%** | Consensus ($\text{IoU}=0.913$) | READY FOR PROMOTION |
| **CS_VAL_020** | HITL | $637 \times 419$ | Crack | $[105, 70, 540, 360]$ | 126,150 | **47.26%** | Consensus ($\text{IoU}=0.871$) | READY FOR PROMOTION |
| **CS_VAL_021** | HITL | $637 \times 440$ | Crack | $[135, 50, 518, 410]$ | 137,880 | **49.19%** | Consensus ($\text{IoU}=0.886$) | READY FOR PROMOTION |
| **CS_VAL_022** | HITL | $629 \times 471$ | Lamp Broken | $[46, 36, 582, 434]$ | 213,328 | **72.01%** | Adjudicated (Rule 6) | READY FOR PROMOTION |
| **CS_VAL_023** | HITL | $881 \times 476$ | Lamp Broken | $[170, 78, 770, 418]$ | 204,000 | **48.65%** | Consensus ($\text{IoU}=0.940$) | READY FOR PROMOTION |
| **CS_VAL_024** | HITL | $637 \times 442$ | Scratch | $[38, 112, 602, 328]$ | 121,824 | **43.27%** | Adjudicated (Safeguard 5) | READY FOR PROMOTION |
| **CS_VAL_025** | HITL | $637 \times 444$ | Dent | $[80, 60, 560, 390]$ | 158,400 | **56.01%** | Consensus ($\text{IoU}=0.904$) | READY FOR PROMOTION |

### Group C: Permanently Rejected Images (2 Images)
These images failed the physical optical blur gate and remain quarantined in `batch_01/rejected/`:

| Image ID | Source | Resolution | Stated Class | Optical Blur ($\sigma^2 < 50.0$) | Rejection Reason | Final Disposition |
| :---: | :---: | :---: | :---: | :---: | :--- | :---: |
| **CS_VAL_005** | Wikimedia | $1600 \times 1200$ | Tire Flat | **28.4** | Severe defocus blur on sidewall contact patch | PERMANENTLY REJECTED |
| **CS_VAL_011** | Wikimedia | $800 \times 600$ | Glass Shatter | **41.2** | Heavy motion blur on windshield glass texture | PERMANENTLY REJECTED |

---

## 4. Quota Reconciliation & Gate D Promotion Strategies

### 4.1 The Batch 1 Quota Paradox
In Batch 1 alone, promoting all 8 Tier 2 images yields:

$$\frac{8 \text{ Tier 2}}{15 \text{ Tier 1} + 8 \text{ Tier 2}} = \frac{8}{23} = \mathbf{34.78\%} > 30.00\% \quad (\text{Temporary Ceiling Breach})$$

Under strict interpretation of the cumulative quota rule, the dataset must not exceed $30.0\%$ Tier 2 at any release milestone.

### 4.2 Three Proposed Gate D Operational Protocols

To resolve this mathematical constraint, three structured options are submitted for user choice:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   GATE D PROMOTION PROTOCOL OPTIONS                                    │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ OPTION 1: Batch 2 Absorption Coupling (Recommended)                                                   │
│ • Mechanism:    Gate D is authorized in lockstep with Gate E (Batch 2).                                │
│ • Execution:    All 8 images are promoted to active status in acquisition_manifest.csv, but the        │
│                 formal validation benchmark is gated until Batch 2 acquires at least 4 Tier 1 images.  │
│ • Math Proof:   15 (B1 T1) + 4 (B2 T1) = 19 Tier 1. Ratio = 8 / (19 + 8) = 8 / 27 = 29.63% <= 30.0%.  │
│ • Advantage:    Zero administrative overhead; preserves all 8 high-value multi-class assets.           │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ OPTION 2: Staged Phased Promotion (Strict Quota Preservation at Every Turn)                            │
│ • Mechanism:    Promote exactly 6 Tier 2 images immediately; hold 2 in verified provisional status.    │
│ • Immediate:    Promote CS_VAL_016, 017, 021, 022, 023, 025. Ratio = 6 / (15 + 6) = 6/21 = 28.57% <= 30│
│ • Deferred:     CS_VAL_020 (Crack) and CS_VAL_024 (Scratch) held until Batch 2 delivers 4 Tier 1s.    │
│ • Advantage:    Active dataset satisfies <= 30.0% quota at every single intermediate commit.           │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ OPTION 3: Cumulative Dataset Quota Waiver for Intermediate Batches                                     │
│ • Mechanism:    User ratifies that the <= 30.0% quota applies strictly to the FINAL cumulative       │
│                 dataset (N >= 200), permitting temporary intermediate fluctuations in early batches.  │
│ • Execution:    All 8 images are promoted immediately without restrictions.                            │
│ • Requirement:  Batch 2 acquisition specification must mandate >= 75% Tier 1 candidate intake.        │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Technical Promotion Execution Steps (Upon Gate D Approval)

When user authorization is received, the agent will execute the following mechanical sequence:
1. **Manifest Promotion:**
   - Append rows for `CS_VAL_016`, `CS_VAL_017`, `CS_VAL_020`–`CS_VAL_025` into `datasets/CarDD_Independent_Val_v1/manifests/acquisition_manifest.csv`.
   - Update `resolution_tier` column (`Tier 1` vs `Tier 2`).
2. **Ground Truth Label Synchronization:**
   - Copy final adjudicated YOLO files from `annotation/final_adjudicated_yolo/<id>.txt` to active dataset labels directory `datasets/CarDD_Independent_Val_v1/labels/val/`.
3. **Audit Trail Verification:**
   - Commit updated `annotation_readiness_matrix.csv` with status `CERTIFIED_ACTIVE`.
   - Compute SHA-256 manifest verification checksum.

---

## 6. Formal Sign-Off Record

```
========================================================================================
                      GATE D FORMAL PROMOTION AUTHORIZATION RECORD
========================================================================================

Project:              ClaimSense AI
Phase:                Phase 8 — Independent Real-World Validation Dataset
Scope:                Formal Promotion of 8 Quarantined Candidates (CS_VAL_016 to 025)

Selected Promotion Protocol:
[ ] Option 1: Batch 2 Absorption Coupling (Recommended)
[ ] Option 2: Staged Phased Promotion (6 Immediate, 2 Deferred)
[ ] Option 3: Cumulative Final Quota Waiver

Gate D Decision:
[ ] APPROVED    [ ] REJECTED    [ ] DEFERRED

Authorizing Stakeholder: ___________________________________________________________
Date:                    ___________________________________________________________
========================================================================================
```
