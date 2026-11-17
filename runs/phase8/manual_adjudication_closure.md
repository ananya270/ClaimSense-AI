# Phase 8 — Manual Annotation Adjudication Closure Report

**Project:** ClaimSense AI  
**Module:** Phase 8 Dataset Quality & Human Review Adjudication Closure  
**Date:** November 17, 2026  
**Audited Dataset:** `datasets/CarDD_Expanded_v1/train/labels/` (210 files)  
**Quarantined Queue Size:** **78 Pending Cases** (16 Scratches, 2 Tiny Dents, 60 Missing Crack Candidates)  
**Status:** **Formally Closed — Strict Safe Quarantine Enforced (Zero Unapproved Modifications Applied)**  

---

## 1. Executive Summary & Adjudication Policy

In accordance with Phase 8 operational directives:
> **"Do not apply any correction without explicit human approval. Keep unresolved cases quarantined."**

The 78 cases identified during the dataset readiness audit and human review screening have undergone rigorous forensic evaluation. Because no explicit human assessor approval was granted to alter these annotations, **zero unapproved modifications or label additions were made**. 

All 78 cases are maintained in their safe, untouched state within `datasets/CarDD_Expanded_v1/train/labels/`.

### Adjudication Decision Summary

```
+---------------------------------------------------------------------------------------------------+
| Category               | Case Count | Recommendation              | Final Closure Decision        |
+------------------------+------------+-----------------------------+-------------------------------+
| Multi-Segment Scratch  | 16 Cases   | KEEP AS SEPARATE BOXES      | QUARANTINED (UNCONSOLIDATED)  |
| Suspicious Tiny Dents  | 2 Cases    | FLAG AS HOOD SHUTLINE       | QUARANTINED (KEPT IN LABEL)   |
| Missing Crack Candidates| 60 Cases  | REJECT AUTOMATED INJECTION  | QUARANTINED (ZERO ADDITIONS)  |
+------------------------+------------+-----------------------------+-------------------------------+
| Total Cases Evaluated  | 78 Cases   | Complete Human Review Queue | 100% QUARANTINED AS SAFE      |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Category A: Multi-Segment Scratch Adjudication (16 Cases)

### Background & Assessment
Multi-segment scratches can either represent:
1. A continuous single scratch stroke erroneously partitioned by automated labeling or annotation artifacts, or
2. Distinct scratch incidents occurring across separate body panels, contours, or separated by large stretches of intact, undamaged vehicle paint.

During Stage 2 review, 11 wide-span cases were initially quarantined, and an additional 5 cases were reclassified from approval to quarantine during Stage 3 visual verification (`000118.jpg`, `000512.jpg`, `001724.jpg`, `001875.jpg`, and `002921.jpg`) because consolidation would have expanded the bounding box area by $>2.5\times$ or enclosed $>30\%$ of the entire image frame.

### Forensic Decision: **REJECT CONSOLIDATION / KEEP SEPARATE**
Consolidating these multi-segment scratch instances into a giant envelope box forces the object detection model to associate large expanses of pristine, unblemished paint with the `scratch` class. This directly exacerbates false-positive detections on specular reflections and clean body lines.

In strict compliance with the directive, **all 16 scratch cases remain unconsolidated as separate, tight bounding boxes** in `datasets/CarDD_Expanded_v1/train/labels/`.

### Registry of 16 Quarantined Scratch Cases

| Case ID | Image Filename | Native Res | Original Boxes | Enclosing Area (% Frame) | Expansion Ratio | Closure Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **MQ-SC-01** | `000118.jpg` | 1000x664 | 3 boxes | 49.3% | 2.27x | **QUARANTINED (Separate)** |
| **MQ-SC-02** | `000512.jpg` | 1000x667 | 5 boxes | 31.3% | 2.85x | **QUARANTINED (Separate)** |
| **MQ-SC-03** | `001724.jpg` | 1000x667 | 2 boxes | 37.8% | 2.62x | **QUARANTINED (Separate)** |
| **MQ-SC-04** | `001875.jpg` | 1000x667 | 4 boxes | 39.4% | 3.12x | **QUARANTINED (Separate)** |
| **MQ-SC-05** | `002921.jpg` | 1000x664 | 3 boxes | 34.2% | 2.74x | **QUARANTINED (Separate)** |
| **MQ-SC-06** | `000411.jpg` | 1000x667 | 3 boxes | 24.6% | 2.18x | **QUARANTINED (Separate)** |
| **MQ-SC-07** | `000782.jpg` | 1000x667 | 4 boxes | 28.1% | 2.45x | **QUARANTINED (Separate)** |
| **MQ-SC-08** | `000853.jpg` | 1000x667 | 3 boxes | 32.5% | 2.60x | **QUARANTINED (Separate)** |
| **MQ-SC-09** | `001004.jpg` | 1000x667 | 3 boxes | 29.8% | 2.31x | **QUARANTINED (Separate)** |
| **MQ-SC-10** | `001150.jpg` | 1000x667 | 3 boxes | 26.4% | 2.05x | **QUARANTINED (Separate)** |
| **MQ-SC-11** | `001170.jpg` | 1000x667 | 4 boxes | 35.1% | 2.89x | **QUARANTINED (Separate)** |
| **MQ-SC-12** | `001297.jpg` | 1000x667 | 3 boxes | 22.9% | 2.14x | **QUARANTINED (Separate)** |
| **MQ-SC-13** | `001476.jpg` | 1000x667 | 3 boxes | 27.0% | 2.38x | **QUARANTINED (Separate)** |
| **MQ-SC-14** | `001716.jpg` | 1000x667 | 4 boxes | 38.6% | 3.01x | **QUARANTINED (Separate)** |
| **MQ-SC-15** | `002444.jpg` | 1000x667 | 3 boxes | 21.5% | 2.02x | **QUARANTINED (Separate)** |
| **MQ-SC-16** | `002677.jpg` | 1000x667 | 3 boxes | 30.2% | 2.51x | **QUARANTINED (Separate)** |

---

## 3. Category B: Suspicious Tiny Dent Adjudication (2 Cases in `001149.jpg`)

### Background & Forensic Coordinates
In `datasets/CarDD_300/train/labels/001149.txt`, two sub-16px bounding boxes were flagged as potential label noise:
- **MQ-DT-01 (Line 3):** `0 0.597875 0.439123 0.054330 0.011439`  
  *Pixel Dimensions:* Width = 54.3 px, Height = 11.4 px. Height ratio to image is 1.1%.
- **MQ-DT-02 (Line 4):** `0 0.796400 0.416469 0.063380 0.015727`  
  *Pixel Dimensions:* Width = 63.4 px, Height = 15.7 px. Height ratio to image is 1.5%.

### Visual Evidence & Assessment
Both boxes sit directly along the horizontal hood shutline seam / cowl gap of the vehicle. While they exhibit minor panel gap variation under grazing light, they are highly suspect as shutline shadow artifacts rather than true impact deformations.

### Forensic Decision: **RETAIN IN LABEL FILE / AWAIT FORMAL HUMAN SIGN-OFF**
Deleting ground-truth annotations without explicit human adjuster confirmation violates the strict safeguards of Phase 8. Therefore, **Lines 3 and 4 remain present in `datasets/CarDD_Expanded_v1/train/labels/001149.txt`**. They are formally documented in the manifest as flagged edge cases, but have not been deleted.

---

## 4. Category C: Missing-Crack Candidates (60 Cases: `MQ-CR-01` to `MQ-CR-60`)

### Background & Assessment
Auditing CarDD collision images revealed 60 scenes depicting heavy front-end or rear-end collisions where bumper covers, grilles, or headlamps suffered significant crushing, but no `crack` (class 2) bounding box was annotated.

### Forensic Decision: **REJECT AUTOMATIC LABEL INJECTION / ZERO ADDITIONS**
Automated or heuristic injection of bounding boxes based on collision severity is scientifically invalid:
1. **Substrate Ambiguity:** High-resolution zoom reveals that many crushed plastic panels suffer plastic deformation or mounting tab shearing without visible surface fissure cracks.
2. **Class Collision:** Labeling complex crush zones as `crack` without visual fissure proof causes feature confusion between `dent` (crushed metal/plastic) and `crack` (structural fracture).
3. **Guardrail Compliance:** Injecting unverified annotations directly breaches the mandate: *"Do not infer missing damage without visual evidence. Do not automatically add missing labels."*

**Outcome:** Zero missing crack labels were added to the training set. All 60 candidate scenes retain their pristine ground-truth annotations.

---

## 5. Closure Audit & Verification

1. **Reversibility Guarantee:**  
   The baseline ground-truth labels remain 100% preserved in `datasets/CarDD_300/train/labels/` and its bit-identical backup `datasets/CarDD_300/train/labels_backup_original/`.
2. **Isolation Guarantee:**  
   The staged training dataset `datasets/CarDD_Expanded_v1/train/labels/` contains **only the 35 verified and approved consolidations** (34 scratch merges + 1 dent merge in `000265.txt`).
3. **Quarantine Guarantee:**  
   None of the 78 pending cases were modified, deleted, or fabricated.
4. **Readiness:**  
   The manual adjudication queue is formally closed. No unresolved proposals remain in an indeterminate state.
