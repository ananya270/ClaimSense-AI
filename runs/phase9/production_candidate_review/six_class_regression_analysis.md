# ClaimSense AI — Phase 9.7: Six-Class Performance & Regression Audit

**Document ID:** `REG-PH9-7-CLASSES-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.7 — Production Model vs Candidate Comparative Analysis & Promotion Readiness Review  
**Execution Date:** 2026-11-20  
**Status:** SIX-CLASS COMPARATIVE AUDIT COMPLETE  

---

## 1. Executive Summary

This report delivers a class-by-class regression audit evaluating whether candidate `P9-T02` causes regression on any non-crack vehicle damage category (dent, scratch, glass shatter, lamp broken, and tire flat) relative to the active production baseline (`models/phase5/best.pt`).

Evaluations were conducted on the frozen **CarDD independent test split** ($N=45$ images, 148 verified damage instances) under operational thresholds ($\tau=0.25, \text{IoU}\ge 0.40$).

---

## 2. Six-Class Master Comparison Matrix

| Class ID | Damage Class | Support | Metric | Production Baseline (`models/phase5/best.pt`) | Candidate P9-T02 (`P9-T02-BEST`) | Absolute Delta | Relative Delta | Class Trend Verdict |
|---|---|---|---|---|---|---|---|---|
| **0** | **Dent** | 49 | TP / FP / FN | 13 / 59 / 36 | 2 / 4 / 47 | -11 / -55 / +11 | — | **Precision Improved / Recall Regressed** |
| | | | Precision | 0.1806 | **0.3333** | **+0.1527** | **+84.55%** | FPs collapsed from 59 to 4 |
| | | | Recall | 0.2653 | 0.0408 | -0.2245 | -84.62% | Predictions below $\tau=0.25$ |
| | | | F1-Score | 0.2149 | 0.0727 | -0.1422 | -66.17% | Uncalibrated threshold penalty |
| | | | AP@50 | 0.1175 | 0.0867 | -0.0308 | -26.21% | Moderate continuous ranking |
| **1** | **Scratch** | 53 | TP / FP / FN | 6 / 26 / 47 | 2 / 5 / 51 | -4 / -21 / +4 | — | **Precision Improved / Recall Regressed** |
| | | | Precision | 0.1875 | **0.2857** | **+0.0982** | **+52.37%** | FPs fell from 26 to 5 |
| | | | Recall | 0.1132 | 0.0377 | -0.0755 | -66.70% | High miss rate on faint scratches |
| | | | F1-Score | 0.1412 | 0.0667 | -0.0745 | -52.76% | Uncalibrated threshold penalty |
| | | | AP@50 | 0.0836 | 0.0408 | -0.0428 | -51.20% | Subtle abrasions penalized |
| **2** | **Crack** | **13** | TP / FP / FN | 0 / 0 / 13 | 0 / 0 / 13 | 0 / 0 / 0 | — | **Unchanged at 0% Operational Recall** |
| | | | Precision | 0.0000 | 0.0000 | 0.0000 | 0.0% | Zero detections $\ge 0.25$ |
| | | | Recall | **0.0000%** | **0.0000%** | **0.0000** | **0.0%** | **Universal Failure at $\tau=0.25$** |
| | | | F1-Score | 0.0000 | 0.0000 | 0.0000 | 0.0% | Zero operational utility |
| | | | AP@50 | 0.0138 | **0.0203** | **+0.0065** | **+47.10%** | **Sub-threshold gain (+47%)** |
| **3** | **Glass Shatter** | 12 | TP / FP / FN | 3 / 10 / 9 | **7 / 4 / 5** | **+4 / -6 / -4** | — | **MASSIVE IMPROVEMENT (STAR CLASS)** |
| | | | Precision | 0.2308 | **0.6364** | **+0.4056** | **+175.7%** | High certainty on fracture webs |
| | | | Recall | 0.2500 | **0.5833** | **+0.3333** | **+133.3%** | Detected 7 of 12 instances |
| | | | F1-Score | 0.2400 | **0.6087** | **+0.3687** | **+153.6%** | F1 more than doubled |
| | | | AP@50 | 0.2924 | **0.6577** | **+0.3653** | **+124.9%** | Best performing class in model |
| **4** | **Lamp Broken** | 15 | TP / FP / FN | 9 / 22 / 6 | 2 / 5 / 13 | -7 / -17 / +7 | — | **Precision Improved / Recall Regressed** |
| | | | Precision | 0.2903 | 0.2857 | -0.0046 | -1.58% | Comparable precision |
| | | | Recall | 0.6000 | 0.1333 | -0.4667 | -77.78% | Lens cracks fell below $\tau=0.25$ |
| | | | F1-Score | 0.3913 | 0.1818 | -0.2095 | -53.54% | Lower operational F1 |
| | | | AP@50 | 0.1928 | 0.1859 | -0.0069 | -3.58% | Stable continuous ranking |
| **5** | **Tire Flat** | 6 | TP / FP / FN | 5 / 6 / 1 | 0 / 0 / 6 | -5 / -6 / +5 | — | **Zero FPs / Suppressed Recall at $\tau=0.25$** |
| | | | Precision | 0.4545 | 0.0000 | -0.4545 | -100.0% | Zero predictions $\ge 0.25$ |
| | | | Recall | 0.8333 | 0.0000 | -0.8333 | -100.0% | Zero predictions $\ge 0.25$ |
| | | | F1-Score | 0.5882 | 0.0000 | -0.5882 | -100.0% | Zero predictions $\ge 0.25$ |
| | | | AP@50 | 0.3994 | **0.5026** | **+0.1032** | **+25.84%** | **Continuous AP increased +26%** |

---

## 3. Analysis of Class Regression & Trade-Offs

### 3.1 The Star Improvement: Glass Shatter
- Glass shatter detection is a standout success for P9-T02.
- Due to the higher spatial resolution ($640\times 640$), the fine intricate spiderweb fracture patterns on laminated windscreens and tempered side windows are clearly captured.
- True positives rose from 3 to 7, false positives fell from 10 to 4, and F1 rose from $0.2400$ to **$0.6087$ (+153.6%)**.

### 3.2 The False-Positive Trade-off: Dent, Scratch, and Lamp Broken
- In the Production Baseline, the model was heavily prone to false alarms:
  - 59 false dents on metallic panel reflections.
  - 26 false scratches on body seams and lighting glare.
  - 22 false lamp broken predictions.
- Candidate P9-T02 virtually eliminated these spurious detections (total FPs dropped from 123 to 18, an $85.4\%$ reduction).
- **The Trade-Off:** Because P9-T02 distributes probabilities over a finer grid, prediction confidence scores shifted downwards. At the rigid threshold $\tau=0.25$, true positive detections also dropped, causing a regression in operational recall.

### 3.3 The Tire Flat Anomaly
- In continuous ranking metrics, Tire Flat AP@50 actually **improved by $+25.8\%$** ($0.3994 \to 0.5026$) with zero false alarms.
- However, because all predicted bounding boxes had confidence between $0.15$ and $0.24$, none passed the uncalibrated $\tau=0.25$ operational filter, resulting in zero operational recall.

---

## 4. Synthesis Conclusion

Candidate P9-T02 is **NOT an unconditional improvement across all classes**. While it delivers a massive breakthrough in glass shatter detection and false-positive suppression, its conservative prediction profile creates substantial operational recall regression across dent, scratch, lamp broken, and tire flat when evaluated at the uncalibrated $\tau=0.25$ threshold.
