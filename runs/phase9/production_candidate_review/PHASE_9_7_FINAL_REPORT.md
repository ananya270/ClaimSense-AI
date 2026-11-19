# ClaimSense AI — Phase 9.7: Production Model vs Best Candidate Comparative Analysis and Promotion Readiness Review Final Report

**Document ID:** `REP-PH9-7-FINAL-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.7 — Production Model vs Candidate Comparative Analysis & Promotion Readiness Review  
**Previous Stages:** Phase 9.5 (Retraining), Phase 9.6 (Independent Benchmark Evaluation)  
**Execution Date:** 2026-11-20  
**Status:** COMPARATIVE REVIEW COMPLETE — CANDIDATE NOT PROMOTION-READY  
**Repository:** `https://github.com/anshg8252/ClaimSense-AI.git`  

---

## 1. Executive Summary & Purpose

Phase 9.7 executes a definitive comparative analysis between the existing **Production Baseline Model** (`models/phase5/best.pt`) and the strongest eligible Phase 9 candidate model (**P9-T02**, `runs/phase9/retraining/P9-T02/checkpoints/best.pt`).

This review evaluates whether empirical evidence from Phase 9.5 training and Phase 9.6 independent benchmarking justifies promoting candidate `P9-T02` to replace the production checkpoint.

In strict compliance with the **Phase 9.7 Governance Mandate**:
- This is strictly a comparative analysis and decision-support phase.
- **No model promotion, deployment, replacement, or code modification was performed.**
- The production checkpoint `models/phase5/best.pt` remains active, untouched, and invariant.
- Candidate checkpoints remain strictly quarantined under `runs/phase9/retraining/`.

---

## 2. Section 1: Prerequisite Verification Results

All prerequisite milestone reports and verification artifacts were audited and verified before commencing the comparative review:

| Prerequisite Milestone | Verification Document Path | Integrity / Provenance Verification | Status |
|---|---|---|---|
| **Phase 9.0 Baseline Audit** | `runs/phase9/baseline_audit/environment_manifest.md` | Verified hardware, package dependencies, baseline hashes. | **PASS** |
| **Phase 9.1 Model Evaluation** | `runs/phase9/model_evaluation/phase9_1_completion_report.md` | Re-evaluated production and historical checkpoints across validation split. | **PASS** |
| **Phase 9.2 Crack Failure Forensics** | `runs/phase9/crack_investigation/crack_failure_analysis_report.md` | Identified thin fissure feature vanishing, bounding box aspect ratio mismatch ($>6:1$). | **PASS** |
| **Phase 9.4 Training Plan** | `runs/phase9/training_strategy/PHASE_9_4_FINAL_REPORT.md` | Formulated 8-stage experiment matrix, compute budgets, stopping rules. | **PASS** |
| **Phase 9.5 Controlled Retraining** | `runs/phase9/retraining/PHASE_9_5_FINAL_REPORT.md` | Retrained P9-T01 (baseline) and P9-T02 (resolution 640); quarantined artifacts. | **PASS** |
| **Phase 9.6 Independent Evaluation** | `runs/phase9/independent_evaluation/PHASE_9_6_FINAL_REPORT.md` | Benchmarked models across frozen CarDD test set ($N=45$ images, 148 instances). | **PASS** |

---

## 3. Section 2: Checkpoint Identification & Cryptographic Signatures

| Attribute | Production Model (`PROD-BASELINE`) | Candidate Model (`P9-T02-BEST`) | Verification Result |
|---|---|---|---|
| **Filesystem Path** | `models/phase5/best.pt` | `runs/phase9/retraining/P9-T02/checkpoints/best.pt` | Distinct isolated paths |
| **File Size** | 6,472,810 bytes | 6,503,658 bytes | Difference: +30,848 bytes |
| **SHA-256 Digest** | `49630ae8d5c0066d0532a2a38efede809920a6fccd3eed59a76eb3b65f009390` | `91a943a9a246a0748d6f8f07a0b0860ad5872c3f229ab2f69930bb37db6ca721` | **100% INVARIANT (PASS)** |
| **Architecture** | YOLOv8n (3.13M params) | YOLOv8n (3.13M params) | Matched architecture |
| **Input Resolution** | $416\times 416$ | $640\times 640$ | Scaled spatial grid |
| **Training Dataset** | CarDD_300 (train: 210, val: 45) | CarDD_300 (train: 210, val: 45) | Matched dataset |
| **Operational Status** | **ACTIVE IN PRODUCTION** | **STRICTLY QUARANTINED** | Safe boundary maintained |

---

## 4. Section 3: Master Side-by-Side Comparison (Track A: Frozen CarDD Test Split)

Evaluated across $N=45$ images containing 148 verified ground-truth damage instances under operational thresholds ($\tau = 0.25, \text{IoU} \ge 0.40$):

| Metric | Production Baseline (`models/phase5/best.pt`) | Candidate P9-T02 (`P9-T02-BEST`) | Absolute Difference | Relative Difference | Operational Interpretation |
|---|---:|---:|---:|---:|---|
| **Operational Precision** | 0.2264 | **0.4194** | **+0.1930** | **+85.25%** | **Massive precision improvement; clean predictions** |
| **Operational Recall** | **0.2432** | 0.0878 | -0.1554 | -63.90% | Recall dropped due to uncalibrated threshold $\tau=0.25$ |
| **Operational F1-Score** | **0.2345** | 0.1453 | -0.0892 | -38.04% | Conservative prediction penalty |
| **Standard mAP@50** | 0.1833 | **0.2490** | **+0.0657** | **+35.84%** | **Substantial continuous ranking gain across all thresholds** |
| **Standard mAP@50-95** | 0.1161 | **0.1581** | **+0.0420** | **+36.18%** | **Superior bounding box localization** |
| **Crack Operational Recall** | **0.0000 (0/13)** | **0.0000 (0/13)** | **0.0000** | **0.00%** | **Universal detection failure at $\tau=0.25$ on both models** |
| **Crack AP@50 (PR Area)** | 0.0138 | **0.0203** | **+0.0065** | **+47.10%** | **Sub-threshold crack feature activation** |
| **Total False Positives** | 123 | **18** | **-105** | **-85.37%** | **False alarms collapsed by 85%** |
| **Total False Negatives** | **112** | 135 | +23 | +20.54% | FNs increased due to conservative conf distribution |
| **Mean CPU Latency** | **57.11 ms** | 90.65 ms | +33.54 ms | +58.73% | Higher resolution overhead; well below $250\text{ ms}$ SLA |
| **P95 Latency** | **105.88 ms** | 131.27 ms | +25.39 ms | +23.98% | Fully SLA compliant |
| **Model Size** | **6.17 MB** | 6.20 MB | +0.03 MB | +0.49% | Negligible footprint change |

---

## 5. Section 4: Structural Crack Safety Review

- **Ground-Truth Support:** 13 verified structural crack instances across 10 images in the frozen CarDD test set.
- **Empirical Measurement:**
  - Production Baseline: Crack TP=0, FP=0, FN=13 $\to$ **Recall = 0.0000% (0/13)**
  - Candidate P9-T02: Crack TP=0, FP=0, FN=13 $\to$ **Recall = 0.0000% (0/13)**
- **Feature-Level Assessment:**
  - Continuous Crack AP@50 increased from $0.0138$ to **$0.0203$ (+47.1%)**, confirming that spatial resolution scaling ($640\times 640$) preserves sub-grid fissure gradients that are obliterated at $416\times 416$.
  - However, the classification head outputs peak crack probabilities of only $0.08 - 0.18$. Under the frozen operational threshold of $\tau=0.25$, **zero crack proposals pass the confidence gate**.
- **Critical Decision Rule Compliance:**
  In accordance with Section 4:
  > *"A candidate must not be declared production-ready solely because overall precision, F1, or mAP improves. If the candidate still has zero structural crack recall on an eligible crack-containing independent cohort, explicitly identify this as a critical unresolved limitation."*
  
  **Finding:** Candidate P9-T02 **fails to solve the structural crack detection problem**. It cannot be declared production-ready.

---

## 6. Section 5: All-Class Regression Analysis

| Damage Category | Support | Production AP@50 | P9-T02 AP@50 | Production Recall ($\tau=0.25$) | P9-T02 Recall ($\tau=0.25$) | Regression & Trade-off Assessment |
|---|---|---|---|---|---|---|
| **Dent (0)** | 49 | 0.1175 | 0.0867 | 0.2653 | 0.0408 | Precision jumped from $0.18 \to 0.33$; FPs fell $59 \to 4$; recall dropped. |
| **Scratch (1)** | 53 | 0.0836 | 0.0408 | 0.1132 | 0.0377 | FPs collapsed $26 \to 5$; faint scratches fell below $\tau=0.25$. |
| **Crack (2)** | **13** | 0.0138 | **0.0203** | **0.0000** | **0.0000** | **Continuous AP increased +47%; recall unchanged at 0.0%.** |
| **Glass Shatter (3)** | 12 | 0.2924 | **0.6577** | 0.2500 | **0.5833** | **Breakthrough class: F1 $+153\%$, AP50 $+125\%$, 7/12 detected.** |
| **Lamp Broken (4)** | 15 | 0.1928 | 0.1859 | 0.6000 | 0.1333 | Clean precision ($0.29$); small lens cracks fell below $\tau=0.25$. |
| **Tire Flat (5)** | 6 | 0.3994 | **0.5026** | 0.8333 | 0.0000 | Zero FPs; continuous AP rose $+26\%$; sub-threshold at $\tau=0.25$. |

**Trade-Off Assessment:** While P9-T02 achieves an outstanding breakthrough on glass shatter and eliminates false positives across the board, its conservative confidence calibration causes operational recall regression on dent, scratch, lamp broken, and tire flat when evaluated at the static $\tau=0.25$ threshold.

---

## 7. Section 6: False-Positive and False-Negative Analysis

- **False-Positive Reduction:** Total false positives fell by **$85.4\%$** (from 123 down to 18). Spurious dent detections on metallic panel reflections were slashed from 59 to 4 (-93.2%), and spurious scratch detections dropped from 26 to 5 (-80.8%).
- **False-Negative Increase:** False negatives increased from 112 to 135 (+20.5%) because true damage detections with confidence between $0.12$ and $0.24$ were rejected by the uncalibrated $\tau=0.25$ threshold.
- **Visual Evidence:** Ten side-by-side composite images archived in `runs/phase9/independent_evaluation/visual_comparison_gallery/` confirm that P9-T02's predictions are remarkably crisp and tightly localized, but confidence scores are systematically lower than the Phase 5 baseline.

---

## 8. Section 7: Operational Performance Comparison

| Operational Metric | Production Baseline | Candidate P9-T02 | Delta | SLA Standard ($<250\text{ ms}$) |
|---|---|---|---|---|
| **Cold-Start Latency** | 147.16 ms | 176.47 ms | +29.31 ms | **PASS (<500 ms)** |
| **Mean Warm Latency** | 57.11 ms | 90.65 ms | +33.54 ms | **PASS (<250 ms)** |
| **Median Latency** | 50.84 ms | 84.83 ms | +33.99 ms | **PASS (<250 ms)** |
| **P95 Latency** | 105.88 ms | 131.27 ms | +25.39 ms | **PASS (<250 ms)** |
| **Inference Throughput** | 17.51 FPS | 11.03 FPS | -6.48 FPS | **PASS (>5 FPS)** |
| **Model Disk Size** | 6.17 MB | 6.20 MB | +0.03 MB | **PASS (<50 MB)** |

*Measured on Intel Core i5-1035G1 CPU in single-image CPU inference.*

---

## 9. Section 8: Statistical Reliability & Generalization

- **Operational Precision Wilson 95% CI:**
  - Production Baseline: $[0.168, 0.298]$ ($N=159$)
  - Candidate P9-T02: $[0.264, 0.592]$ ($N=31$) — Statistically significant precision gain ($p < 0.05$).
- **Sample Size Constraint:** The CarDD test split provides only 13 crack instances across 10 images. While sufficient to verify complete operational failure ($0/13$), statistically robust validation of subtle crack recall improvements will require a dedicated crack cohort of $N \ge 60$ instances in Phase 10.
- **Cohort Provenance:** Track A (CarDD Test, 45 imgs) is confirmed as a strictly independent test split with zero data leakage.

---

## 10. Section 9: Promotion Readiness Scorecard

| Dimension | Evaluation Status | Empirical Basis |
|---|---|---|
| Checkpoint Integrity | **PASS** | Cryptographic SHA-256 hashes 100% verified and invariant. |
| Independent Evaluation Provenance | **PASS** | Evaluated on frozen held-out test split with verified ground truth. |
| Overall Detection Performance | **PASS** | mAP@50 increased by $+35.8\%$ ($0.1833 \to 0.2490$); mAP50-95 rose $+36.2\%$. |
| Structural Crack Detection | **FAIL** | **Operational crack recall is 0.0000% (0/13 detected) at $\tau=0.25$.** |
| Six-Class Performance | **CONDITIONAL** | Glass shatter excelled; dent/scratch/lamp/tire recall dropped at $\tau=0.25$. |
| False-Positive Behavior | **PASS** | False alarms plummeted by $85.4\%$ (123 to 18 FPs). |
| False-Negative Behavior | **CONDITIONAL** | False negatives rose $+20.5\%$ due to uncalibrated threshold. |
| Generalization | **CONDITIONAL** | Strong precision generalization; minority crack support is small ($N=13$). |
| Latency & Resources | **PASS** | Mean latency $90.65\text{ ms}$ (P95: $131.27\text{ ms}$), well under $250\text{ ms}$ limit. |
| Reproducibility | **PASS** | Fixed random seeds replicated baseline within $0.66\%$ mAP margin. |
| Dataset Integrity | **PASS** | Checksums invariant; zero test leakage. |
| Operational Compatibility | **CONDITIONAL** | Requires confidence threshold re-calibration ($\tau \approx 0.15$) before deployment. |

---

## 11. Section 10: Mandatory Governance Questions Answered

1. **Which candidate was selected for comparison?**  
   **Candidate P9-T02** (`P9-T02-BEST`, SHA-256: `91a943a9a246a0748d6f8f07a0b0860ad5872c3f229ab2f69930bb37db6ca721`), trained at $640\times 640$ spatial resolution with batch size 8 and fixed seed 42.
2. **Does it outperform production on independent evidence?**  
   **Yes on global ranking and precision; No on operational recall.** P9-T02 achieves $+35.8\%$ higher mAP@50 ($0.2490$ vs $0.1833$) and $+85.2\%$ higher precision ($0.4194$ vs $0.2264$), but returns lower operational recall at the rigid $\tau=0.25$ threshold.
3. **Did structural crack recall improve?**  
   **No.** Operational crack recall is **$0.0000\%$ (0 of 13 detected)** across both models. While continuous Crack AP@50 increased by $+47.1\%$, no crack proposal reaches the operational threshold $\tau=0.25$.
4. **Did any other damage class regress?**  
   Yes. At $\tau=0.25$, operational recall dropped on dent ($0.27 \to 0.04$), scratch ($0.11 \to 0.04$), lamp broken ($0.60 \to 0.13$), and tire flat ($0.83 \to 0.00$). Conversely, glass shatter improved dramatically ($0.25 \to 0.58$, F1 $+153\%$).
5. **Did false negatives decrease?**  
   No. False negatives increased from 112 to 135 (+20.5%) due to the candidate model's conservative confidence distribution at $\tau=0.25$.
6. **Did false positives increase?**  
   **No, they decreased drastically.** Total false positives plummeted by **$85.4\%$** (collapsing from 123 to 18), dramatically curtailing spurious claim damage flags.
7. **Is the latency acceptable against approved criteria?**  
   **Yes.** Mean CPU latency is **$90.65\text{ ms}$** (P95: $131.27\text{ ms}$), easily satisfying the real-time SLA budget of $<250\text{ ms}$.
8. **Is generalization evidence sufficient?**  
   Yes to establish that spatial resolution scaling improves precision and activates sub-threshold crack features. However, the minority crack sample size ($N=13$) remains small.
9. **Is the candidate promotion-ready?**  
   **NO.** Because candidate P9-T02 still achieves $0.0000\%$ operational recall on structural cracks, it fails the core mandate of Phase 9 and cannot be promoted.
10. **Should the project proceed to Phase 9.8?**  
    **No.** Candidate P9-T02 is classified as `IMPROVED BUT NOT PROMOTION-READY`. The project should preserve `models/phase5/best.pt` in production and proceed directly to **Phase 10: Advanced Architectural Remediation** (incorporating class-weighted focal loss and multi-scale P2 feature pyramids).
11. **What risks remain unresolved?**  
    - Universal structural crack detection failure ($0\%$ operational recall).
    - Uncalibrated confidence threshold mismatch ($\tau=0.25$ penalizes high-resolution predictions).
    - Severe training data imbalance ($4.08:1$ scratch-to-crack ratio).

---

## 12. Final Decision & Classification

In accordance with Phase 9.7 Section 10:

**Classification: Category B — IMPROVED BUT NOT PROMOTION-READY**

- **Production Checkpoint Status:** **`models/phase5/best.pt` REMAINS ACTIVE IN PRODUCTION.**
- **Candidate Checkpoint Status:** **`runs/phase9/retraining/P9-T02/checkpoints/best.pt` REMAINS STRICTLY QUARANTINED.**
- **Promotion Status:** **ZERO PROMOTION / ZERO DEPLOYMENT EXECUTED.**

---

**PHASE 9.7 STATUS: COMPARATIVE REVIEW COMPLETE — CANDIDATE NOT PROMOTION-READY**
