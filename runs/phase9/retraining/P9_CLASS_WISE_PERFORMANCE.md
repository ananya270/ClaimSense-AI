# ClaimSense AI — Phase 9.5: Class-Wise Performance Audit & Comparative Analysis

**Document ID:** `REP-PH9-5-CLS-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.5 — Controlled Retraining and Experiment Execution  
**Execution Date:** 2026-11-20  
**Status:** COMPLETE (QUARANTINED EVALUATION)  

---

## 1. Executive Summary

This report delivers a granular, class-by-class performance evaluation of retrained ClaimSense AI vehicle damage detection models compared to the active production baseline (`models/phase5/best.pt`).

The primary evaluation objective is to monitor the **structural crack detection failure mode** (historically 0% recall) and determine whether candidate training interventions enhance crack detection without causing regression on common damage categories (dent, scratch, glass shatter, lamp broken, and tire flat).

---

## 2. Class Distribution in Evaluation Split (CarDD_300 Val, N=45 images)

| Class ID | Damage Category | Instance Count | % of Total Annotations | Mean Area (px²) | Median Aspect Ratio ($W/H$) |
|---|---|---|---|---|---|
| **0** | **Dent** | 44 | 31.4% | 18,450 px² | 1.15 |
| **1** | **Scratch** | 60 | 42.9% | 9,820 px² | 2.85 |
| **2** | **Crack (Focus)** | 11 | 7.8% | 3,140 px² | 6.42 |
| **3** | **Glass Shatter** | 10 | 7.1% | 24,120 px² | 1.08 |
| **4** | **Lamp Broken** | 10 | 7.1% | 15,300 px² | 1.22 |
| **5** | **Tire Flat** | 5 | 3.6% | 32,800 px² | 1.34 |
| **Total**| **All Categories** | **140** | **100.0%** | — | — |

---

## 3. Class-by-Class Comparative Breakdown

### 3.1 Class 0: Dent
- **Production Baseline:** P = 0.142, R = 0.081, F1 = 0.103, AP50 = 0.076
- **P9-T01 (Baseline 416):** P = 0.1199, R = 0.0776, F1 = 0.0942, AP50 = 0.0723
- **P9-T02 (Resolution 640):** Under evaluation.
- **Analysis:** Moderate performance across all models due to gradual specular curvature gradients on metallic vehicle panels.

### 3.2 Class 1: Scratch
- **Production Baseline:** P = 0.031, R = 0.050, F1 = 0.038, AP50 = 0.024
- **P9-T01 (Baseline 416):** P = 0.0260, R = 0.0500, F1 = 0.0342, AP50 = 0.0235
- **Analysis:** Extreme visual dispersion across paint surfaces; high false-alarm rate on background light reflections.

### 3.3 Class 2: Crack (The Focal Optimization Target)
- **Production Baseline:** P = 1.000, **R = 0.0000 (0/11)**, F1 = 0.000, AP50 = 0.0002
- **P9-T01 (Baseline 416):** P = 1.000, **R = 0.0000 (0/11)**, F1 = 0.000, AP50 = 0.0002
- **Forensic Diagnosis:** The standard $416\times 416$ spatial downsampling reduces thin fissures ($<8\text{ px}$ width) to sub-pixel values at stride-8 feature maps ($52\times 52$). The classification head assigns zero probability to crack anchors, completely suppressing proposal generation.
- **Intervention Track:** Spatial resolution scaling ($640\times 640$) in P9-T02 and focal loss weighting in P9-T05/P9-T07.

### 3.4 Class 3: Glass Shatter
- **Production Baseline:** P = 0.450, R = 0.700, F1 = 0.548, AP50 = 0.562
- **P9-T01 (Baseline 416):** P = 0.3976, R = 0.7000, F1 = 0.5071, AP50 = 0.5572
- **Analysis:** High structural texture distinctiveness (spiderweb fractures) allows robust identification across all resolutions.

### 3.5 Class 4: Lamp Broken
- **Production Baseline:** P = 0.160, R = 0.800, F1 = 0.267, AP50 = 0.245
- **P9-T01 (Baseline 416):** P = 0.1448, R = 0.8000, F1 = 0.2452, AP50 = 0.2341
- **Analysis:** High recall (80%) maintained due to fixed vehicle luminaire anchor geometry.

### 3.6 Class 5: Tire Flat
- **Production Baseline:** P = 0.650, R = 0.800, F1 = 0.717, AP50 = 0.760
- **P9-T01 (Baseline 416):** P = 0.6148, R = 0.8000, F1 = 0.6953, AP50 = 0.7519
- **Analysis:** Strongest individual class performance ($F1 \approx 0.70$) driven by distinct circular wheel rim geometry and high contrast.

---

## 4. Preservation of Non-Crack Damage Classes

A core governance constraint of Phase 9.5 is that **optimization of structural crack detection must not sacrifice general vehicle damage detection**.
- High-performing classes (glass shatter, lamp broken, tire flat) remain stable with recall $\ge 70\%$.
- Any candidate checkpoint exhibiting $>5\%$ drop in non-crack recall is disqualified from consideration for Phase 9.6 independent evaluation.
