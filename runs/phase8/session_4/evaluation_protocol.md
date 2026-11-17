# Phase 8 — Session 4 Head-to-Head Benchmark Evaluation Protocol (Revised)

**Project:** ClaimSense AI  
**Module:** Phase 8 Session 4 Rigorous Evaluation Protocol & Benchmark Methodology  
**Date:** November 17, 2026  
**Candidate Under Evaluation:** Proposed Session 4 Checkpoint (`runs/phase8/session_4_training_01/weights/best.pt`)  
**Baseline Comparator:** Session 2 Staging Best Checkpoint (`runs/phase8/session_2/weights/best.pt`)  
**Production Control:** Phase 5 Production Model (`models/phase5/best.pt`)  
**Evaluation Dataset:** Untouched Frozen CarDD Test Split (`datasets/CarDD_300/test/`)  
**Status:** **REVISED PROTOCOL — Audit Only (Awaiting Execution Approval)**  

---

## 1. Objective & Strict Methodological Principles

The purpose of this protocol is to conduct an unbiased, mathematically rigorous, and reproducible head-to-head benchmark evaluation between the proposed **Session 4 candidate** (trained on `CarDD_Expanded_v1` with 310 images) and the **Session 2 baseline** (trained on 210 images).

### Core Methodological Principles
1. **Identical Test Set:** Both models are evaluated against the exact same **45 test images** and **148 ground-truth annotations** in `datasets/CarDD_300/test/`.
2. **Strict Test Split Isolation:** The frozen test set is accessed **strictly once** for the final post-training evaluation. It is permanently excluded from:
   - Training loss optimization.
   - Validation loss monitoring or early-stopping triggers.
   - Hyperparameter selection or augmentation policy tuning.
3. **Identical Inference Conditions:** Both models execute with identical resolution (640px), confidence thresholds, NMS settings, hardware, and evaluator codebase.
4. **Multi-Metric Human Review (No Automated Single-Threshold Promotion):** Promotion is defined as a comprehensive multi-metric decision reviewed by human claims assessors, rather than an automated threshold trigger.

---

## 2. Reconciled Baseline Test Performance (Session 2 Ground Truth)

In previous documentation drafts, an ungrounded 48% target was mistakenly referenced for Dent due to confusing validation split metrics (where Dent achieved ~50.56% on 44 validation instances) with the test split.

The **actual ground-truth test performance** of Session 2 on the 45 test images (148 instances) is reconciled below:

```
+---------------------+-------------------+---------------------+-------------------+-------------------+--------------------+
| Class Name & Index  | Test Instances    | Session 2 mAP@50    | Session 2 Recall  | Session 2 Prec.   | Baseline Status    |
+---------------------+-------------------+---------------------+-------------------+-------------------+--------------------+
| Overall (All 6)     | 148 instances     | **41.17%**          | 37.84%            | 53.40%            | Primary Baseline   |
| 0: dent             | 49 instances      | **26.20%**          | 18.37%            | 53.50%            | Actual Test Base   |
| 1: scratch          | 53 instances      | **15.36%**          | 9.43%             | 37.89%            | Actual Test Base   |
| 2: crack            | 13 instances      | **1.99%**           | 0.00% (@ std IoU) | 0.00% (@ std IoU) | Deficit Baseline   |
| 3: glass shatter    | 12 instances      | 61.12%              | 58.33%            | 75.20%            | Anchored Feature   |
| 4: lamp broken      | 15 instances      | 70.62%              | 66.67%            | 78.40%            | Anchored Feature   |
| 5: tire flat        | 6 instances       | 71.71%              | 75.00%            | 73.60%            | Anchored Feature   |
+---------------------+-------------------+---------------------+-------------------+-------------------+--------------------+
```
*(Reference: `runs/phase8/post_benchmark_analysis/post_benchmark_report.md` lines 12–16).*

---

## 3. Evaluation Hyperparameters & Hardware Configuration

```
+-----------------------------------+---------------------------------------------------------------+
| Parameter                         | Fixed Standard Specification                                  |
+-----------------------------------+---------------------------------------------------------------+
| Evaluation Framework              | Ultralytics YOLOv8 (v8.4.215) / PyTorch 2.11.0+cu128          |
| Hardware Device                   | CUDA 0 (NVIDIA GeForce RTX 3050 Laptop GPU, 4.00 GB VRAM)     |
| Test Images Directory             | datasets/CarDD_300/test/images (45 images)                    |
| Test Labels Directory             | datasets/CarDD_300/test/labels (45 label files)               |
| Input Image Size (`imgsz`)        | 640 x 640 px (letterbox preserved)                            |
| Batch Size                        | 1 (single-frame sequential evaluation for latency precision)  |
| DataLoader Workers                | workers = 0 (enforces Windows multiprocessing stability)      |
| Curve Evaluation Confidence       | conf = 0.001 (standard for full PR-curve mAP integration)     |
| Operational Decision Confidence   | conf = 0.250 (standard operational deployment threshold)      |
| NMS IoU Threshold (`iou`)         | iou = 0.60                                                    |
| Half Precision (FP16)             | half = True (AMP acceleration matching production inference)  |
| Max Detections per Image          | max_det = 300                                                 |
+-----------------------------------+---------------------------------------------------------------+
```

---

## 4. Multi-Metric Human-Reviewed Decision Framework

Model promotion is governed by a holistic evaluation across multiple operational dimensions. A model is **NOT** promoted automatically based on a single metric spike.

```
+-----------------------------------+-----------------------------------+-----------------------------------------------------------+
| Evaluation Dimension              | Reconciled Baseline (Session 2)   | Multi-Metric Review Criteria for Human Assessment         |
+-----------------------------------+-----------------------------------+-----------------------------------------------------------+
| **Overall mAP@50**                | 41.17%                            | Target: >= 41.17% (Demonstrates overall net improvement)  |
| **Overall mAP@50-95**             | 22.84%                            | Target: >= 22.84% (Localization quality retained)         |
| **Crack mAP@50**                  | 1.99% (Recall = 0.00%)            | Target: > 1.99% (Must demonstrate real recall on cracks)  |
| **Dent mAP@50**                   | 26.20%                            | Target: >= 26.20% (Must not regress on metal deformation) |
| **Scratch mAP@50**                | 15.36%                            | Target: >= 15.36% (Must improve recall on long scrapes)   |
| **False Positive Count (FP)**     | Dent: 10, Scratch: 20, Crack: 3   | Decreased FP rate on specular reflections and panel seams |
| **False Negative Count (FN)**     | Dent: 31, Scratch: 41, Crack: 13  | Reduced FN count across unanchored damage classes         |
| **Anchored Classes Retention**    | Glass: 61.1%, Lamp: 70.6%, Tire: 71.7% | No catastrophic forgetting on anchored components   |
| **Inference Latency**             | ~14.2 ms/frame                    | Real-time constraint: <= 25.0 ms/frame (RTX 3050)         |
| **Visual Batch Audit**            | Val batch 0-2 pred inspect        | Human inspection confirms tight, non-redundant boxes      |
+-----------------------------------+-----------------------------------+-----------------------------------------------------------+
```

### Human Sign-Off Requirement
The model may only be promoted to production if human appraisal engineers review the full scorecard (P, R, F1, mAP50, mAP50-95, confusion matrices, and test prediction batches) and formally verify that the gain in `crack` detection does not come at the cost of unacceptable regressions in other classes.

---

## 5. Output Path Protection & Non-Overwriting Guarantees

All evaluation and training directories are strictly segregated:
- **Session 4 Audit Deliverables:** `runs/phase8/session_4/` (Protected audit directory).
- **Session 4 Training Destination:** `runs/phase8/session_4_training_01/` (Dedicated independent new directory).
- **Session 4 Benchmark Evaluation Destination:** `runs/phase8/session_4_training_01/eval/` (Dedicated evaluation sub-folder).
- **Session 2 Outputs:** `runs/phase8/session_2/` (Frozen, read-only baseline).
- **Session 3 Outputs:** `runs/phase8/session_3_1024/` (Frozen, read-only experiment).
- **Production Model:** `models/phase5/best.pt` (Frozen, read-only production checkpoint).

`exist_ok: false` is enforced in all configuration scripts to prevent accidental overwrites.
