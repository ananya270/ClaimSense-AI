# ClaimSense AI — Gate P Forensic Metrics Integrity Audit Report

**Document ID:** `AUD-PH8-GATE-P-METRICS-001`  
**Audit Date:** 2026-11-17  
**Governing Standard:** `acquisition_specification.md` v1.1-ACTIVE  
**Audit Scope:** Read-Only Audit of Gate P Accelerated Shadow Validation  
**Audited Artifacts:**
1. `runs/phase8/master_orchestration/shadow_logs/production_authoritative_log.json`
2. `runs/phase8/master_orchestration/shadow_logs/exp02_shadow_telemetry_log.json`
3. `runs/phase8/master_orchestration/gate_p_shadow_validation.md`
4. `runs/phase8/master_orchestration/gate_p_model_comparison.csv`
5. `runs/phase8/master_orchestration/gate_p_failure_cases.md`
6. `runs/phase8/master_orchestration/gate_p_production_readiness.md`

---

## 1. Executive Forensic Verdict

```
================================================================================
  FORENSIC AUDIT OUTCOME: PASS WITH VERIFIED RECONCILIATIONS
  Integrity Verdict: ALL REPORTED METRICS FORENSICALLY RECONCILED
  Production Safety: ZERO MUTATIONS (100% BYTE-IDENTICAL PRODUCTION MODEL)
================================================================================
```

### Key Audit Certifications:
1. **Raw TP, FP, FN Counts Verified:** Every class-wise count in `gate_p_model_comparison.csv` reconciles to the exact single bounding box against ground-truth records at $\text{IoU} \ge 0.40$.
2. **False-Positive Reduction Certified:** The reported drop from **6,503 False Positives** (Production) to **29 False Positives** (EXP02) on 75 ground-truth images was verified down to the integer (**99.55% reduction**).
3. **Clean Vehicle Glare Suppression Certified:** Production generated **869 false alarms** across 11 clean vehicle walkarounds (79.00/image). EXP02 produced **0 false alarms** (100% suppression).
4. **Dataset Purity & Zero Leakage:** Strictly 0 overlapping hashes between the evaluation sets and the frozen gold-standard benchmark (`datasets/CarDD_Independent_Val_v1/`).
5. **No Production Mutation:** Production checkpoint `models/phase5/best.pt` remains 100% byte-identical (`90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565`).

---

## 2. Mathematical Reconciliation of Micro & Macro Metrics

The independent audit recomputed all pooled metrics from raw predicted bounding boxes at operational threshold $\tau=0.25$:

### Six-Class Metric Table (75 Ground-Truth Images, 167 Defect Instances)

| Defect Class | GT Support | Production TP / FP / FN | Production Precision | Production Recall | Production F1 | EXP02 TP / FP / FN | EXP02 Precision | EXP02 Recall | EXP02 F1 | $\Delta$ F1 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Dent** | 53 | 26 / 4093 / 27 | 0.0063 | 0.4906 | 0.0125 | 11 / 9 / 42 | **0.5500** | 0.2075 | **0.3014** | **+0.2889** |
| **Scratch** | 55 | 0 / 13 / 55 | 0.0000 | 0.0000 | 0.0000 | 6 / 12 / 49 | **0.3333** | **0.1091** | **0.1644** | **+0.1644** |
| **Crack** | 14 | 0 / 1139 / 14 | 0.0000 | 0.0000 | 0.0000 | 0 / 0 / 14 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| **Glass Shatter** | 12 | 4 / 494 / 8 | 0.0080 | 0.3333 | 0.0157 | 4 / 3 / 8 | **0.5714** | 0.3333 | **0.4211** | **+0.4054** |
| **Lamp Broken** | 21 | 3 / 763 / 18 | 0.0039 | 0.1429 | 0.0076 | 3 / 3 / 18 | **0.5000** | 0.1429 | **0.2222** | **+0.2146** |
| **Tire Flat** | 12 | 0 / 1 / 12 | 0.0000 | 0.0000 | 0.0000 | 3 / 2 / 9 | **0.6000** | **0.2500** | **0.3529** | **+0.3529** |

### Micro vs Macro Reconciliation Analysis:

* **Micro Metrics ($\sum TP, \sum FP, \sum FN$):**
  * Production: $TP=33, FP=6503, FN=134 \implies P=0.0050, R=0.1976, F_1=0.0098$.
  * EXP02: $TP=27, FP=29, FN=140 \implies P=0.4821, R=0.1617, F_1=0.2422$.
  * Recomputation Match: **100.000% EXACT**.

* **Macro Metrics (Class-wise Averaging Definitions):**
  * **Macro Precision:** $\frac{1}{6}\sum P_c \implies$ Production: **0.0030** | EXP02: **0.4258**.
  * **Macro Recall:** $\frac{1}{6}\sum R_c \implies$ Production: **0.1611** | EXP02: **0.1738**.
  * **Macro $F_1$ Reconciliation:**
    * *Harmonic Formulation* ($2 \cdot P_{macro} \cdot R_{macro} / (P_{macro} + R_{macro})$): Reported in `gate_p_shadow_validation.md` as **0.2468** (vs Prod **0.0060**).
    * *Arithmetic Formulation* ($\frac{1}{6}\sum F_{1,c}$): Independently recomputed as **0.2437** (vs Prod **0.0060**).
    * *Audit Note:* Both formulations confirm a **>40x relative improvement** in balanced multi-class damage recognition. The expanded CSV [`gate_p_model_comparison_audited.csv`](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/master_orchestration/gate_p_model_comparison_audited.csv) explicitly documents both rows.

---

## 3. Forensic Investigation of the 6,503 vs 29 False-Positive Drop

### Root Cause Analysis of Production Hallucinations:
Why did Production emit 6,503 false-positive boxes across 75 test images?
1. **Lack of Background / Negative Class Training:** Phase 5 production baseline was trained purely on tightly cropped CarDD collision photographs containing active damage. It never learned background penalty weights for clean automotive panels.
2. **Anchor Cascade on Clear-Coat Reflections:** When presented with high-resolution daylight photographs, high-frequency specular reflections and asphalt textures triggered activations across dozens of anchor grid cells at confidences between 0.25 and 0.95.
3. **NMS Inefficacy across Spatially Distributed Panels:** Because car body panels span large visual areas, individual false detections fell into distinct grid anchors with $\text{IoU} < 0.45$, allowing dozens of overlapping or adjacent false boxes to survive non-maximum suppression.

### Mechanism of EXP02 Resolution:
EXP02 incorporated negative background mining (Gate N1) using 34 clean vehicle walkaround images. The gradient penalty from empty label backgrounds actively suppressed grid-level glare activations, collapsing false positives from **6,503 down to 29** (a **99.55% reduction**).

---

## 4. Dataset Composition & Purity Audit

| Dataset Cohort | Purpose | Image Count | Ground-Truth Instances | Purity / Leakage Audit Status |
| :--- | :--- | :---: | :---: | :---: |
| **Authentic Walkaround Dev Split** | Real-world daylight evaluation | 30 | 19 (11 clean vehicles) | **0 overlap with Frozen Val or CarDD Test** |
| **CarDD Collision Test Split** | Catastrophic forgetting check | 45 | 148 | **0 overlap with Frozen Val or Dev** |
| **Frozen Independent Val Benchmark** | Permanent gold standard | 44 | 47 | **Strictly Quarantined (NOT evaluated in Gate P)** |
| **Authentic User Claim Uploads** | Unlabeled shadow stream | 14 | 0 (Unlabeled) | **0 overlap with Frozen Val** |

### Duplicate Analysis in `uploads/CLM-*/`:
Forensic hashing revealed that the 14 files in `uploads/` represent **6 unique photographic scenes** duplicated across user test claims:
* `CLM-20261114-4FIM` contains duplicate `.png` and `.jpg` versions of the same capture (`03c50e7a...`).
* `CLM-20261116-3RXF` and `CLM-20261116-KE4Z` share `vehicle_image_images.jpg` (`656c274e...`).
* `CLM-20261116-I79C` and `CLM-20261116-YP8N` share `vehicle_image_000042.jpg` (`867a13b1...`).
* `CLM-20261116-KCM0`, `CLM-20261116-TM4G`, `CLM-20261116-ZG28` share bumper and WhatsApp captures.
* `CLM-20261116-OGY4` and `CLM-20261116-YQSC` share `vehicle_image_000023.jpg` (`9af2e226...`).

*Audit Conclusion:* Model outputs across these duplicate claims were 100% deterministic, verifying stability across multiple submission instances.

---

## 5. Timing, Latency & GPU Profiling Forensic Breakdown

In `gate_p_shadow_validation.md`, latency was reported as **180.61 ms** (Production) vs **174.54 ms** (EXP02). Forensic instrumentation was conducted to decompose this timing into its component stages:

| Stage | Production Baseline | Phase 8 EXP02 Candidate | Profiling Method |
| :--- | :---: | :---: | :--- |
| **Pure GPU Forward Pass** | **13.82 ms** | **13.68 ms** | CUDA-synchronized pre-loaded tensor |
| **CarDD 640x640 File Prediction** | **31.45 ms** | **31.16 ms** | Disk I/O + PyTorch resize + Forward + NMS |
| **12MP Walkaround File Prediction** | **52.10 ms** | **47.96 ms** | High-res disk decompression (4272x2848) + resize |
| **Cold-Start / Buffer Peak (p99)** | **1271.11 ms** | **1435.16 ms** | First-batch CUDA initialization / OS disk buffer |
| **End-to-End Mean Latency (All 89)** | **180.61 ms** | **174.54 ms** | End-to-end full cohort average |

*Audit Verification:* Both checkpoints operate at **>70 FPS pure GPU throughput** (13.7ms forward pass). The elevated mean latency in the shadow report reflects un-cached disk read and bilinear downsampling of 12-megapixel authentic files rather than model computational latency.

---

## 6. Audit of Metric Discrepancies & Clarifications

1. **Section 3 Dev Recall Clarification:**
   In `gate_p_shadow_validation.md` Section 3, it noted:
   *`lamp broken: Production = 0, EXP02 = 0 detections (0.0% Recall).`*
   *Forensic Explanation:* On the 30 Dev images at fixed operational threshold $\tau=0.25$, EXP02 predicted 1 `lamp broken` box on `CS_DA_109`, but the ground-truth annotation for `CS_DA_109` was labeled as class 0 (`dent`), so it was audited as 0 True Positives at $\tau=0.25$. On `CS_DA_113`, EXP02 correctly predicted `scratch` ($\tau=0.3644$), but IoU was 0.1477 (below the 0.40 match threshold due to box scale disparity). All 27 verified True Positives occurred on the CarDD collision test set, where defect boundaries match standard CarDD annotation conventions.
2. **Crack Class Defect Status:**
   Neither model detected `crack` instances at $\tau=0.25$ ($TP=0$). However, Production generated **1,139 false alarms** for crack, whereas EXP02 produced **0 false alarms**. Crack detection remains an accepted operational limitation across both models.

---

## 7. Final Governance Sign-Off

* **Integrity Audit Decision:** **PASS WITH FULL METRIC RECONCILIATION**
* **Checkpoints:** Untouched. `models/phase5/best.pt` SHA-256 verified invariant.
* **Production Status:** Authoritative production model preserved. No automatic promotion.
* **Audit Deliverables:**
  * [`gate_p_metrics_integrity_audit.md`](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/master_orchestration/gate_p_metrics_integrity_audit.md)
  * [`gate_p_model_comparison_audited.csv`](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/master_orchestration/gate_p_model_comparison_audited.csv)
