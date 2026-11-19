# ClaimSense AI — Phase 9.0: Six-Class Performance & Defect Forensic Audit

**Document ID:** `AUD-PH9-PERF-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.0 — Baseline Audit  
**Date:** 2026-11-19  
**Governing Standard:** `acquisition_specification.md` v1.1-ACTIVE  
**Audit Scope:** Class-wise Evaluation of All 6 Vehicle Damage Classes, Distinguishing Validation mAP from Operational Metrics ($\tau=0.25$)

---

## 1. Executive Summary

This report establishes the baseline performance across the six canonical vehicle damage categories recognized by ClaimSense AI. To provide complete clarity for Phase 9 optimization, this audit strictly distinguishes between:
1. **Validation mAP50 / mAP50-95 Metrics:** Continuous area-under-the-curve metrics evaluated across all operational thresholds ($0.0 \le \tau \le 1.0$) on independent benchmark datasets.
2. **Operational Threshold Metrics ($\tau=0.25$, $\text{IoU} \ge 0.40$):** Discrete True Positive (TP), False Positive (FP), False Negative (FN), Precision, Recall, and $F_1$ scores evaluated at the active production operating point.

---

## 2. Six-Class Validation Benchmark Performance (AP50 Across Models)

Reconstructed directly from the frozen 44-image independent validation benchmark (`gate_o_per_class_metrics.csv`):

| Defect Class | Production Baseline (Phase 5) | Phase 8 Session 2 | Phase 8 Session 4 | EXP01 (Negative Mining) | EXP02 (Rare Class Expansion) | EXP03 (Multi-Scale) | Historical Class Trajectory |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **0: Dent** | 0.0058 | 0.0013 | 0.0009 | 0.0038 | **0.0088** | 0.0064 | Consistently detected; high precision under EXP02. |
| **1: Scratch** | 0.0000 | 0.0003 | 0.0003 | 0.0002 | **0.0084** | 0.0036 | Zero detection in Production; rescued significantly in EXP02. |
| **2: Crack** | **0.0025** | 0.0000 | 0.0010 | 0.0000 | 0.0005 | 0.0000 | **Severe suppression in all models; near-zero AP50.** |
| **3: Glass Shatter** | 0.0015 | 0.0099 | **0.0339** | 0.0087 | 0.0320 | 0.0104 | Strongest structural feature; Session 4 & EXP02 perform well. |
| **4: Lamp Broken** | 0.0000 | 0.0000 | 0.0000 | 0.0000 | **0.0190** | 0.0049 | Completely absent before Gate N; EXP02 established sensitivity. |
| **5: Tire Flat** | 0.0000 | 0.0000 | 0.0000 | 0.0000 | **0.0083** | 0.0053 | Completely absent before Gate N; EXP02 established sensitivity. |
| **Overall Pooled mAP50** | **0.0016** | **0.0019** | **0.0060** | **0.0021** | **0.0128** | **0.0051** | **EXP02 achieved highest balanced benchmark mAP50.** |

---

## 3. Operational Threshold Metrics ($\tau = 0.25$, $\text{IoU} \ge 0.40$)

Reconstructed from the forensic ground-truth evaluation across 75 test images (167 annotated defect instances) recorded in `gate_p_model_comparison_audited.csv`:

### Detailed Six-Class Operational Comparison Table:

| Defect Class | GT Instances (Support) | Production TP / FP / FN | Production Precision | Production Recall | Production $F_1$ | EXP02 TP / FP / FN | EXP02 Precision | EXP02 Recall | EXP02 $F_1$ | $\Delta F_1$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **0: Dent** | 53 | 26 / 4,093 / 27 | 0.0063 | 0.4906 | 0.0125 | 11 / 9 / 42 | **0.5500** | 0.2075 | **0.3014** | **+0.2889** |
| **1: Scratch** | 55 | 0 / 13 / 55 | 0.0000 | 0.0000 | 0.0000 | 6 / 12 / 49 | **0.3333** | **0.1091** | **0.1644** | **+0.1644** |
| **2: Crack** | 14 | 0 / 1,139 / 14 | 0.0000 | 0.0000 | 0.0000 | 0 / 0 / 14 | 0.0000 | **0.0000** | 0.0000 | **0.0000** |
| **3: Glass Shatter** | 12 | 4 / 494 / 8 | 0.0080 | 0.3333 | 0.0157 | 4 / 3 / 8 | **0.5714** | 0.3333 | **0.4211** | **+0.4054** |
| **4: Lamp Broken** | 21 | 3 / 763 / 18 | 0.0039 | 0.1429 | 0.0076 | 3 / 3 / 18 | **0.5000** | 0.1429 | **0.2222** | **+0.2146** |
| **5: Tire Flat** | 12 | 0 / 1 / 12 | 0.0000 | 0.0000 | 0.0000 | 3 / 2 / 9 | **0.6000** | **0.2500** | **0.3529** | **+0.3529** |
| **Total / Micro Avg** | **167** | **33 / 6,503 / 134** | **0.0050** | **0.1976** | **0.0098** | **27 / 29 / 140** | **0.4821** | **0.1617** | **0.2422** | **+0.2324** |
| **Macro Average (Arithmetic)** | — | — | **0.0030** | **0.1611** | **0.0060** | — | **0.4258** | **0.1738** | **0.2437** | **+0.2377** |

---

## 4. In-Depth Forensic Investigation of Anomalies

### 1. Structural Crack Recall: 0.0% Under EXP02
* **Observed Evidence:** Across all 14 ground-truth crack instances, EXP02 produced **0 True Positives**, **0 False Positives**, and **14 False Negatives** ($R = 0.0\%$, $P = 0.0\%$, $F_1 = 0.0\%$).
* **Forensic Root Causes:**
  1. **Extreme Representation Scarcity:** In the 120-image domain adaptation dataset (`CarDD_DomainAdaptation_v1`), only **3 crack instances** were present (accounting for only 4.0% of defect annotations). In contrast, lamp broken and tire flat each received 25 instances.
  2. **High-Frequency Hairline Attenuation:** Vehicle cracks (bumper cracks, panel fractures) are thin, high-frequency linear boundaries with widths often $< 2$ pixels at native scale. Downsampling to $640 \times 640$ attenuates these features through 32x strided convolutions (down to $20 \times 20$ grid cells).
  3. **Over-Suppression by Negative Mining:** EXP01/EXP02 applied heavy gradient penalties for clear-coat glare. Because crack features are visually subtle and weak, the negative background penalty extinguished crack activations below the $\tau=0.25$ operational threshold.

### 2. Aggregate Operational Recall: 16.2% Under EXP02
* **Observed Evidence:** Aggregate operational recall at $\tau=0.25$ dropped from **19.8% (Production)** to **16.17% (EXP02)**.
* **Analysis:**
  - In Production, recall was artificially inflated by an unconstrained deluge of 6,503 overlapping false-positive proposals, some of which happened to intersect ground-truth bounding boxes by random spatial coverage.
  - EXP02 eliminated random proposals, creating high-precision detections ($P = 48.2\%$ vs Production $0.50\%$). However, because conservative thresholds were learned during negative mining, genuine subtle defects with confidence scores between $0.10$ and $0.24$ were rejected.
  - **Phase 9 Opportunity:** Dynamic per-class threshold calibration (e.g. lowering $\tau$ for cracks and scratches to $0.15$ while keeping $\tau=0.30$ for dents) can recover recall without inducing false-alarm cascades.

### 3. False-Positive Reduction: 99.55% in Gate P Forensic Cohort
* **Observed Evidence:** Production produced **6,503 False Positives** across 75 test images. EXP02 collapsed this count to **29 False Positives**.
* **Mathematical Verification:**
  $$\text{Reduction} = \frac{6503 - 29}{6503} = \frac{6474}{6503} = 99.554\% \approx \mathbf{99.55\%}$$
* **Clean Vehicle Negative Controls:**
  Across 11 authentic daylight walkaround images of completely undamaged vehicles:
  - Production generated **869 false-positive detections** (**79.0 false alarms per clean vehicle**).
  - EXP02 generated **0 false-positive detections** (**0.0 false alarms per clean vehicle, 100.0% clean suppression**).

---

## 5. Performance Audit Conclusion

1. **Precision Breakthrough:** EXP02 resolved the existential false-positive hallucination flaw of Phase 5 production, lifting precision from 0.5% to 48.2%.
2. **Key Limitation Identified:** EXP02 cannot be deployed as an authoritative replacement until the **0% structural crack recall** and **16.2% aggregate recall** deficits are resolved.
3. **Phase 9 Directive:** Model optimization in Phase 9 must focus on restoring crack and scratch sensitivity through multi-scale feature pyramids, localized patch slicing, and targeted class loss weighting.
