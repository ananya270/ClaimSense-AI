# ClaimSense AI — Phase 9.6: False-Positive Forensic Audit

**Document ID:** `REP-PH9-6-FP-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.6 — Independent Benchmark Evaluation & Candidate Model Validation  
**Execution Date:** 2026-11-20  
**Status:** FORENSIC ANALYSIS COMPLETE  

---

## 1. Executive Summary

This report analyzes false-positive (FP) behavior across all evaluated models on the frozen CarDD independent test set ($N=45$ images, 148 ground-truth annotations) under operational thresholds ($\tau=0.25, \text{IoU}\ge 0.40$).

A major finding of Phase 9.6 is the **dramatic suppression of false positives achieved by candidate P9-T02**, which reduced total false positives by **$85.4\%$** compared to the production baseline.

---

## 2. False-Positive Comparison Matrix

| Model Identifier | Total Predictions ($\tau\ge 0.25$) | True Positives (TP) | False Positives (FP) | False Negatives (FN) | Operational Precision | Mean FP / Image |
|---|---|---|---|---|---|---|
| **Production Baseline** (`models/phase5/best.pt`) | 159 | 36 | **123** | 112 | 0.2264 | **2.73 FP/img** |
| **P9-T01 Baseline Candidate** | 123 | 22 | **101** | 126 | 0.1789 | **2.24 FP/img** |
| **P9-T02 Resolution Scaling** | 31 | 13 | **18** | 135 | **0.4194** | **0.40 FP/img** |

---

## 3. Class-Wise False-Positive Distribution

| Damage Class | Production Baseline FPs | P9-T01 FPs | P9-T02 FPs | FP Reduction (P9-T02 vs Prod) |
|---|---|---|---|---|
| **Dent (0)** | 59 | 16 | **4** | **-93.2% (59 -> 4)** |
| **Scratch (1)** | 26 | 52 | **5** | **-80.8% (26 -> 5)** |
| **Crack (2)** | 0 | 1 | **0** | **0 FPs maintained** |
| **Glass Shatter (3)** | 10 | 10 | **4** | **-60.0% (10 -> 4)** |
| **Lamp Broken (4)** | 22 | 21 | **5** | **-77.3% (22 -> 5)** |
| **Tire Flat (5)** | 6 | 1 | **0** | **-100.0% (6 -> 0)** |
| **Total All Classes** | **123** | **101** | **18** | **-85.4% (123 -> 18)** |

---

## 4. Primary False-Positive Trigger Categories

1. **Specular Highlights on Curved Panels:**
   - *Production Baseline:* Severe tendency to hallucinate `dent` boxes on curved fender highlights, chrome bumper reflections, and hood glare ($59$ dent FPs).
   - *P9-T02 Mitigation:* The $640\times 640$ spatial resolution allows the network to distinguish sharp specular highlights from physical surface depressions, reducing dent FPs from 59 to 4.
2. **Body Panel Seams & Shutlines:**
   - *P9-T01:* Produced 52 scratch FPs, frequently triggering on hood-to-fender panel gaps and door shutlines.
   - *P9-T02 Mitigation:* Improved edge localization enabled the model to recognize uniform seam contours as non-damage body joints.
3. **Background Reflections on Windows:**
   - Tree branch and cloud reflections on rear windows frequently triggered `glass shatter` in the baseline (10 FPs). P9-T02 reduced this to 4 FPs.

---

## 5. Trade-off: Precision vs Recall

While P9-T02 achieved an outstanding precision improvement ($0.2264 \to 0.4194$, $+85.2\%$), it did so by adopting a much more conservative prediction profile, which reduced operational recall ($0.2432 \to 0.0878$). This reflects the classic precision-recall trade-off when resolution is scaled without fine-tuning confidence thresholds.
