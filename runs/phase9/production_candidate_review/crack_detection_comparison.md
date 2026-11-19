# ClaimSense AI — Phase 9.7: Structural Crack Detection Safety & Comparative Review

**Document ID:** `REV-PH9-7-CRACK-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.7 — Production Model vs Candidate Comparative Analysis & Promotion Readiness Review  
**Execution Date:** 2026-11-20  
**Status:** CRITICAL SAFETY REVIEW COMPLETE — ZERO RECALL LIMITATION CONFIRMED  

---

## 1. Executive Summary & Purpose

The defining objective of the Phase 9 optimization program was to resolve the catastrophic failure of ClaimSense AI computer vision models to detect vehicular **structural cracks**.

Historical evaluations consistently revealed complete failure:
- **Phase 8 Gate O Independent Benchmark:** 0/6 structural cracks detected.
- **Phase 8 Gate P Forensic Cohort:** 0/14 structural cracks detected across the combined 75-image cohort.
- **EXP02 Historical Reference:** Despite achieving 16.2% aggregate operational recall, EXP02 achieved **0.0% structural crack recall**.

This review conducts a rigorous forensic comparison between the active **Production Baseline** (`models/phase5/best.pt`) and the strongest candidate **P9-T02** (`runs/phase9/retraining/P9-T02/checkpoints/best.pt`) to establish whether genuine, operational crack detection capability has been achieved.

---

## 2. Side-by-Side Crack Performance Matrix (Track A: Frozen CarDD Test Split, 13 Instances)

| Metric | Production Baseline (`models/phase5/best.pt`) | Candidate P9-T02 (`P9-T02-BEST`) | Absolute Delta | Relative Delta | Evaluation Conformance |
|---|---|---|---|---|---|
| **Evaluated Images with Cracks** | 10 | 10 | 0 | 0.0% | 100% matched cohort |
| **Ground-Truth Crack Instances** | 13 | 13 | 0 | 0.0% | 100% matched annotations |
| **Crack True Positives (TP)** | 0 | 0 | 0 | 0.0% | Identical ($\tau=0.25, \text{IoU}\ge 0.40$) |
| **Crack False Positives (FP)** | 0 | 0 | 0 | 0.0% | Zero spurious crack hallucinations |
| **Crack False Negatives (FN)** | 13 | 13 | 0 | 0.0% | **100% Miss Rate on Both Models** |
| **Operational Crack Precision** | 0.0000 | 0.0000 | 0.0000 | 0.0% | No crack proposals $\ge 0.25$ |
| **Operational Crack Recall** | **0.0000% (0/13)** | **0.0000% (0/13)** | **0.0000** | **0.0%** | **Universal Failure at $\tau=0.25$** |
| **Operational Crack F1-Score** | 0.0000 | 0.0000 | 0.0000 | 0.0% | Zero operational utility |
| **Continuous Crack AP@50** | 0.0138 | **0.0203** | **+0.0065** | **+47.10%** | **Measurable Sub-Threshold Gain** |
| **Continuous Crack AP@50-95** | 0.0027 | **0.0064** | **+0.0037** | **+137.0%** | Feature boundary sharpening |

---

## 3. Forensic Analysis Across Failure Modes

### 3.1 Sub-Threshold Feature Activation vs Operational Confidence Barrier
- In candidate **P9-T02**, continuous **Crack AP@50** increased by **$+47.1\%$ relative** over the Production Baseline ($0.0138 \to 0.0203$) and by **$10.7\times$** over P9-T01 ($0.0019 \to 0.0203$).
- This provides definitive empirical evidence that **scaling spatial resolution from $416\times 416$ to $640\times 640$ preserves fine fissure activations** at the stride-8 feature pyramid ($80\times 80$ grid). At $416\times 416$, these activations vanish completely.
- **The Critical Blocker:** Even though feature activations exist, the classification head outputs peak softmax confidences for crack anchors in the range of **$0.08$ to $0.18$**. Under the frozen production operational threshold of **$\tau = 0.25$**, **every single crack proposal is filtered out**, resulting in **$0.0000\%$ operational recall**.

### 3.2 Scratch-to-Crack Class Confusion
- In test image `000513` (rear bumper fracture) and test image `002801` (tailgate handle fracture), the visual fracture was detected by P9-T02, but classified as **scratch** ($\tau=0.29$) rather than crack.
- This is a direct consequence of dataset imbalance: the training split contains $4.08\times$ more scratches than cracks. The model has learned that high-aspect-ratio linear features are almost always scratches.

### 3.3 Aspect Ratio & Thin Feature Distortion
- True structural cracks in CarDD exhibit median aspect ratios ($W/H$ or $H/W$) of **$6.42:1$** with physical fissure widths frequently $<6\text{ pixels}$.
- Standard anchor-free box regression in YOLOv8 assigns heavy gradient loss penalties to tight bounding boxes with extreme aspect ratios, causing the head to collapse confidence on slender boxes.

---

## 4. Mandatory Decision Rule Ratification

In strict adherence to Phase 9.7 Section 4:
> *"A candidate must not be declared production-ready solely because overall precision, F1, or mAP improves. If the candidate still has zero structural crack recall on an eligible crack-containing independent cohort, explicitly identify this as a critical unresolved limitation. Do not hide this result behind aggregate metrics."*

### Final Safety Verdict:
**CRITICAL UNRESOLVED LIMITATION CONFIRMED.**  
Candidate P9-T02 still achieves **0.0000% operational recall on structural cracks (0 of 13 detected)**. While spatial resolution scaling activates sub-threshold crack features (Crack AP50 rose $+47.1\%$), **P9-T02 DOES NOT SOLVE THE CRACK DETECTION PROBLEM AT THE PRODUCTION OPERATIONAL THRESHOLD**. It cannot be approved as promotion-ready.
