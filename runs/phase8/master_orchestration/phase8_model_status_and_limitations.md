# ClaimSense AI — Phase 8 Model Status & Technical Limitations Report

**Document ID:** `REP-PH8-MODELS-001`  
**Date:** 2026-11-17  
**Governing Standard:** `acquisition_specification.md` v1.1-ACTIVE  
**Audit Scope:** Model Evolution, Checkpoint Provenance, and Technical Limitations  
**Promotion Verdict:** **EXP02 IS NOT PROMOTED TO PRODUCTION. PRODUCTION CHECKPOINT REMAINS AUTHORITATIVE.**

---

## 1. Authoritative Production Model vs Candidate Status

```
================================================================================
  MODEL PROMOTION STATUS RECORD:
  PRODUCTION CHECKPOINT: models/phase5/best.pt  --> 100% AUTHORITATIVE
  CANDIDATE CHECKPOINT:  EXP02 (Rare Class)     --> QUARANTINED (NOT PROMOTED)
================================================================================
```

### Checkpoint Provenance Table:

| Model Identity | Checkpoint Path | Cryptographic SHA-256 | Current Operational Status |
| :--- | :--- | :--- | :--- |
| **Authoritative Production** | `models/phase5/best.pt` | `90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565` | **ACTIVE PRODUCTION BASELINE** |
| **Candidate EXP02** | `runs/phase8/.../exp02_rare_class/weights/best.pt` | `68e2b58ec7759427808621debc9a8d725a9e4c1fbc57a2102cd239a8ca14f006` | **QUARANTINED (SHADOW ONLY)** |
| **Session 2 Historical** | `runs/phase8/session_2/weights/best.pt` | `2ee0a56749ceba72da863fd3496f080ee06f26409daa4e9588fb69ee149333c5` | Historical Reference Only |
| **Session 4 Initializer** | `runs/phase8/session_4_training_01/weights/best.pt` | `ea53eee94e508bbb81620b47b2a23c9826341b6b5a6981d9371e476cb9d0594f` | Transfer Initializer Only |

---

## 2. Benchmark History & Domain Adaptation Experiments

### 1. Phase 8 Benchmark History (Session 2 vs Session 4)
* **Production Baseline (`models/phase5/best.pt`):** Fine-tuned purely on CarDD collision crops. In Gate I independent benchmarking on 44 real-world walkaround images, the production baseline scored **0.0% precision and 0.0% recall at operational threshold $\tau=0.25$**. In accelerated shadow validation across 75 ground-truth images, it generated **6,503 false-positive bounding boxes** due to daylight specular reflections and panel seams.
* **Session 2:** Introduced initial fine-tuning on expanded CarDD batches. Demonstrated modest recall improvements on collision crops but failed to control daylight reflection noise.
* **Session 4:** Introduced high-resolution training ($1024 \times 1024$) and improved multi-class weighting. Showed the highest raw recall among early models but retained high false-positive rates on clean panels. Selected as the pre-trained transfer initializer for Gate N domain adaptation experiments.

### 2. Gate N Domain Adaptation Experiments (EXP01–EXP03)
Trained on 90 authentic real-world daylight walkaround images and evaluated on the 30-image Dev split:
* **EXP01 (Negative Mining):** Fine-tuned with 45 negative clean vehicles. Achieved 68.2% false-positive reduction on Dev data but suffered recall degradation on subtle scratches.
* **EXP02 (Rare Class Expansion):** Fine-tuned with balanced rare class weighting (`lamp broken`, `tire flat`) + negative clean walkarounds. **Achieved 87.0% false-positive reduction on Dev data** and activated detection on previously blind rare categories. Selected as the primary candidate model.
* **EXP03 (Unified MultiScale):** Trained across $512\text{--}768$ image sizes with Mosaic augmentation. Exhibited bounding box instability and missed tiny scratch details.

---

## 3. Exhaustive Analysis of Known Technical Limitations

Despite dramatic improvements in false-alarm suppression, EXP02 exhibits critical technical limitations that preclude immediate production replacement:

```
+-------------------------------------------------------------------------------------------------------------+
|                                    EXP02 TECHNICAL LIMITATIONS MATRIX                                       |
+---+----------------------------+---------------------------------------+------------------------------------+
| # | Limitation Description     | Observed Forensic Metric              | Operational Consequence            |
+---+----------------------------+---------------------------------------+------------------------------------+
| 1 | Zero Crack Recall          | 0.0% Recall (0/6 Cracks Detected)     | Critical structural damage missed  |
| 2 | Low Aggregate Recall       | 16.2% Recall @ tau=0.25 (75 Images)   | Significant under-detection rate   |
| 3 | Non-Independent Dev Bias   | Dev Split (30 Images) used for tuning | Optimistic performance estimates   |
| 4 | Collision Bias Disparity   | Higher recall on CarDD than daylight  | Domain disparity remains active    |
+---+----------------------------+---------------------------------------+------------------------------------+
```

### Limitation 1: Zero Crack Recall (CRITICAL SEVERITY)
* **Forensic Finding:** In the Gate O gold-standard independent benchmark on frozen 44 images, EXP02 detected **0 out of 6 confirmed structural crack instances (Recall = 0.0%)**.
* **Root Cause Analysis:** Real-world structural cracks on vehicles (bumper tears, fractured splitters) exhibit narrow, hairline aspect ratios ($>10:1$). The Gate N training split contained only cosmetic scratches and dent walkarounds, providing zero gradient signal for structural fractures.
* **Operational Blast Radius:** If EXP02 were granted authoritative status, policyholders with cracked bumpers or fractured structural fascias would have their damage completely ignored, leading to severe under-payout disputes.

### Limitation 2: Low Aggregate Operational Recall
* **Forensic Finding:** In the Gate P forensic metrics audit across 75 ground-truth images at operational threshold $\tau=0.25$, EXP02 achieved:
  * **Precision:** **48.2%** (27 TP / 29 FP)
  * **Recall:** **16.2%** (27 TP / 140 FN)
  * **Micro $F_1$:** **0.2422**
* **Root Cause:** EXP02 achieved its 99.55% false-positive suppression by raising effective feature activation barriers. While this successfully suppressed reflection noise, it inadvertently suppressed genuine low-contrast dents and faint scratches.

### Limitation 3: Non-Independent Dev Cohort Evaluation
* **Scientific Clarification:** The 30-image domain adaptation Dev cohort (`datasets/domain_adaptation_dev`) was utilized during Gate N for hyperparameter selection and candidate ranking. Results reported on these 30 images **must never be represented as independent validation**. True independent validation is strictly represented by the frozen 44-image Gate O benchmark (`CarDD_Independent_Val_v1`).

---

## 4. Formal Model Governance Stance

```
================================================================================
  1. EXP02 IS STRICTLY AN ASSISTIVE SHADOW CANDIDATE.
  2. EXP02 CANNOT AUTOMATICALLY DENY, ADJUST, OR LOWER ANY CLAIM PAYOUT.
  3. PRODUCTION BASELINE models/phase5/best.pt REMAINS 100% AUTHORITATIVE.
  4. FUTURE PROMOTION REQUIRES RETRAINING ON CRACKS & EXPLICIT HUMAN APPROVAL.
================================================================================
```
