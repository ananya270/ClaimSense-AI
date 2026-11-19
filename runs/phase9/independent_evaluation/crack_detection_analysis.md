# ClaimSense AI — Phase 9.6: Structural Crack Detection Forensic Benchmark

**Document ID:** `REP-PH9-6-CRACK-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.6 — Independent Benchmark Evaluation & Candidate Model Validation  
**Execution Date:** 2026-11-20  
**Status:** FORENSIC BENCHMARK COMPLETE — DEFINITIVE FINDINGS  

---

## 1. Executive Summary & Core Objective

The central motivation of Phase 9 was to investigate and remediate the catastrophic failure of ClaimSense AI vision checkpoints on **structural crack detection** (historically 0% recall across Gate O, Gate P, and CarDD validation splits).

This report delivers the comprehensive evaluation of structural crack detection on the frozen **CarDD independent test benchmark** ($N=45$ images, containing 13 verified ground-truth crack instances across 10 images).

---

## 2. Structural Crack Benchmark Performance Matrix (CarDD Test Split, 13 Instances)

| Model Evaluated | Eval Resolution | Crack Ground Truth | Crack Predictions ($\tau\ge 0.25$) | Crack TP | Crack FP | Crack FN | Crack Precision | Crack Recall | Crack F1 | Crack AP@50 | Crack AP@50-95 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Production Baseline** (`models/phase5/best.pt`) | $416\times 416$ | 13 | 0 | 0 | 0 | 13 | 0.0000 | **0.0000 (0/13)** | 0.0000 | 0.0138 | 0.0027 |
| **P9-T01 Baseline Candidate** | $416\times 416$ | 13 | 1 | 0 | 1 | 13 | 0.0000 | **0.0000 (0/13)** | 0.0000 | 0.0019 | 0.0003 |
| **P9-T02 Resolution Scaling** | $640\times 640$ | 13 | 0 | 0 | 0 | 13 | 0.0000 | **0.0000 (0/13)** | 0.0000 | **0.0203** | **0.0064** |

---

## 3. Forensic Analysis Across Visual Failure Modes

### 3.1 Sub-Threshold Feature Activation vs Operational Threshold
- In **P9-T02** ($640\times 640$), the continuous PR-curve metric **Crack AP@50** increased by **$+47.1\%$ relative** over the Production Baseline ($0.0138 \to 0.0203$) and by **$10.7\times$** over P9-T01 ($0.0019 \to 0.0203$).
- This demonstrates that higher spatial resolution preserves fine linear fissure representations in the stride-8 feature pyramids ($80\times 80$ grid).
- **However**, at the rigid operational confidence threshold of **$\tau = 0.25$**, the classification head outputs peak crack probabilities in the range $0.08 - 0.18$. As a result, **zero predictions survive the confidence filter**, resulting in **$0.0000\%$ operational recall (0 out of 13 detected)**.

### 3.2 Scratch-to-Crack Feature Confusion
- Visual inspection of the 10 crack-containing test images (`000042`, `000513`, `001874`, `002252`, `002707`, `002801`, `003226`, `003354`, `003418`, `003734`) reveals that in several instances, true fracture fissures on bumper plastic and headlight housings were classified by the model as **scratch** or **dent** rather than crack.
- Because scratches outnumber cracks by $4.08:1$ in the training split, the classifier has learned a strong inductive bias that linear paint defects are scratches.

### 3.3 Aspect Ratio & Thin Feature Distortion
- Ground-truth cracks exhibit median aspect ratios ($W/H$ or $H/W$) exceeding **$6.4:1$** with physical fissure widths frequently $<6\text{ pixels}$.
- Standard anchor-free center-distance regression in YOLOv8 suffers severe gradient penalty when bounding boxes are extremely narrow, causing the network to collapse confidence on slender bounding boxes to avoid loss penalties.

---

## 4. Definitive Benchmark Verdict

> [!CAUTION]
> **Definitive Conclusion:** While Experiment `P9-T02` demonstrated measurable feature-level activation (Crack AP@50 increased to $0.0203$), **NO CANDIDATE CHECKPOINT ACHIEVED NON-ZERO STRUCTURAL CRACK RECALL AT THE OPERATIONAL THRESHOLD ($\tau=0.25$)**.
>
> In accordance with Phase 9.6 Section 6 and Section 11:
> *"A candidate with zero structural crack recall must not be presented as a successful crack-detection solution, regardless of its overall precision or mAP. If no candidate detects structural cracks reliably, state that clearly."*
>
> Therefore, **neither candidate checkpoint solves the structural crack detection problem**, and neither candidate is eligible for production promotion as a crack detection solution without architectural or loss reweighting interventions (such as P2-layer high-resolution heads or focal class-loss weighting).
