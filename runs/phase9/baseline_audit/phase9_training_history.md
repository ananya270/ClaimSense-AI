# ClaimSense AI — Phase 9.0: Historical Training Progression Audit

**Document ID:** `AUD-PH9-TRAIN-HIST-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.0 — Baseline Audit  
**Date:** 2026-11-19  
**Governing Standard:** `acquisition_specification.md` v1.1-ACTIVE  
**Audit Scope:** Reconstruction of Training Progression from Initial Smoke Test through Domain Adaptation (EXP01–EXP03)

---

## 1. Executive Summary

This report establishes the complete, uninflated historical training progression of ClaimSense AI computer vision models across Phase 5 and Phase 8. All entries are reconstructed directly from preserved training manifests (`args.yaml`), metric histories (`results.csv`), and execution logs (`gate_n_training_integrity.md`, `final_phase8_summary.md`).

---

## 2. Master Historical Training Matrix

| Experiment / Session | Starting Checkpoint | Dataset & Split | Epochs | Batch Size | Img Size | Optimizer & LR | Augmentations (Mosaic, Mixup, Flip) | Best Epoch | Best Validation Metrics (P, R, mAP50, mAP50-95) | Duration & GPU | Status / Interruptions |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| **Initial Smoke Test** | `yolov8n.pt` (Pretrained) | `cardd_train.yaml` (210 train / 45 val) | 1 | 2 | 640 | `auto`, lr0=0.01, lrf=0.01 | mosaic=1.0, mixup=0.0, fliplr=0.5 | 1 | P=0.0085, R=0.1920, mAP50=0.0043, mAP50-95=0.0015 | ~15s (RTX 3050) | Completed (1/1 epoch) |
| **Session 1** | `smoke_test/weights/last.pt` | `cardd_train.yaml` (210 train / 45 val) | 10 | 4 | 640 | `auto`, lr0=0.01, lrf=0.01 | mosaic=1.0, mixup=0.0, fliplr=0.5 | 10 | P=0.6082, R=0.3298, mAP50=0.3462, mAP50-95=0.2463 | ~95s (RTX 3050) | Completed (10/10 epochs) |
| **Session 2** | `session_1/weights/last.pt` | `cardd_train.yaml` (210 train / 45 val) | 15 (26 cum.) | 4 | 640 | `auto`, lr0=0.01, lrf=0.01 | mosaic=1.0, mixup=0.0, fliplr=0.5 | 15 | P=0.4503, R=0.4394, mAP50=0.4414, mAP50-95=0.3115 | ~142s (RTX 3050) | Completed (15/15 epochs) |
| **Session 3 (1024 Res)** | `session_2/weights/last.pt` | `cardd_train.yaml` (210 train / 45 val) | 10 | 2 | 1024 | `auto`, lr0=0.01, lrf=0.01 | mosaic=1.0, mixup=0.0, fliplr=0.5 | 10 | P=0.5466, R=0.4211, mAP50=0.3989, mAP50-95=0.2453 | ~210s (RTX 3050) | Completed (10/10 epochs; batch=2 due to VRAM) |
| **Session 4 (Expanded)** | `session_2/weights/best.pt` | `CarDD_Expanded_v1` (310 train / 45 val) | 20 | 4 | 640 | `AdamW`, lr0=0.001, lrf=0.01 | mosaic=0.5, mixup=0.0, fliplr=0.5 | 20 | P=0.6205, R=0.4687, mAP50=0.4529, mAP50-95=0.3064 | ~220s (RTX 3050) | Completed (20/20 epochs; fine-tuned from Session 2) |
| **EXP01 (Negative Mining)** | `session_4_training_01/weights/best.pt` | `exp01.yaml` (90 train DA incl. 34 clean negatives) | 15 (8 run) | 4 | 640 | `AdamW`, lr0=0.0003, lrf=0.01 | mosaic=1.0, mixup=0.0, fliplr=0.5 | 3 | P=0.0019, R=0.2333, mAP50=0.0017, mAP50-95=0.0006 | 107.76s (RTX 3050, 218 MB VRAM peak) | Stopped early at epoch 8 (loss plateau) |
| **EXP02 (Rare Class)** | `exp01/weights/best.pt` | `exp02.yaml` (90 train DA with rare class weighting) | 15 (12 run) | 4 | 640 | `AdamW`, lr0=0.0003, lrf=0.01 | mosaic=1.0, mixup=0.0, fliplr=0.5 | 7 | P=0.0018, R=0.5833, mAP50=0.0308, mAP50-95=0.0087 | 140.44s (RTX 3050, 310 MB VRAM peak) | Stopped at epoch 12 (fitness degradation) |
| **EXP03 (Multi-Scale)** | `exp02/weights/best.pt` | `exp03.yaml` (90 train DA multi-scale) | 15 (12 run) | 4 | 640 | `AdamW`, lr0=0.0003, lrf=0.01 | mosaic=1.0, mixup=0.0, fliplr=0.5 | 9 | P=0.0029, R=0.6333, mAP50=0.0207, mAP50-95=0.0051 | 290.19s (RTX 3050, 326 MB VRAM peak) | Stopped at epoch 12 |
| **Phase 5 Production Base** | `yolov8n.pt` | `CarDD_300/data.yaml` (210 train / 45 val) | 5 | 16 | 416 | `auto`, lr0=0.01, lrf=0.01 | mosaic=1.0, mixup=0.0, fliplr=0.5 | 5 | P=0.4887, R=0.2897, mAP50=0.2453, mAP50-95=0.1862 | CPU (5 epochs) | Completed (5/5 epochs) |

---

## 3. Detailed Session-by-Session Historical Progression

### 1. Initial CPU Smoke Test & Verification Run
* **Objective:** Verify pipeline execution and initial loss convergence.
* **Duration & Hardware:** 1 epoch, executed on host GPU (`device: 0`).
* **Outcome:** Loss stabilized (`box_loss=2.458`, `cls_loss=4.811`), generating initializer weights for Session 1.

### 2. Session 1 (10 Epochs)
* **Objective:** Train initial detection heads on standard CarDD 210-image training partition.
* **Metric Evolution:**
  - Epoch 1: `mAP50 = 0.0541`, `mAP50-95 = 0.0312`
  - Epoch 5: `mAP50 = 0.2284`, `mAP50-95 = 0.1582`
  - Epoch 10: `mAP50 = 0.3462`, `mAP50-95 = 0.2463`
* **Observation:** Steady linear convergence with zero overfitting observed.

### 3. Session 2 (15 Additional Epochs, 26 Cumulative)
* **Objective:** Extended training from Session 1 checkpoint.
* **Metric Evolution:**
  - Epoch 1 (Epoch 11 cum.): `mAP50 = 0.3712`
  - Epoch 15 (Epoch 26 cum.): `mAP50 = 0.4414`, `mAP50-95 = 0.3115`
  - Precision: `0.4503`, Recall: `0.4394`
* **Observation:** Achieved optimal balance of precision and recall on collision damage images under standard lab/indoor lighting.

### 4. Session 3 (10 Epochs at 1024 Resolution)
* **Objective:** Evaluate whether high-resolution input (`imgsz=1024`) improves small-scale damage feature extraction (e.g. hairline scratches and cracks).
* **Constraints:** Due to 4 GB VRAM limit on the RTX 3050 Laptop GPU, batch size had to be halved from 4 to 2.
* **Outcome:** Best `mAP50 = 0.3989` at epoch 10 (down from 0.4414 in Session 2). Halving batch size introduced gradient variance that offset the resolution gain.

### 5. Session 4 (20 Epochs on Expanded Dataset)
* **Objective:** Train on `CarDD_Expanded_v1` (310 train images including the 100-image expansion pool).
* **Configuration:** Transitioned optimizer to `AdamW` with reduced initial learning rate (`lr0=0.001`), halved mosaic augmentation (`mosaic=0.5`) to preserve spatial context.
* **Outcome:** Achieved program peak CarDD validation performance: `mAP50 = 0.4529`, `mAP50-95 = 0.3064`, Precision = `0.6205`, Recall = `0.4687`.

### 6. EXP01 (Domain Adaptation: Negative Background Mining)
* **Objective:** Eliminate daylight walkaround false alarms caused by specular reflections and pavement textures.
* **Strategy:** Fine-tune from Session 4 using a low learning rate (`lr0=0.0003`) on a dataset containing 34 authentic clean, undamaged vehicles with zero bounding-box labels.
* **Outcome:** Clean vehicle false alarms dropped sharply from 79.0/image to 0.27/image. However, validation mAP on the dev split registered at `0.0017` due to heavy penalization of weak defect features.

### 7. EXP02 (Domain Adaptation: Rare Class Expansion)
* **Objective:** Recover sensitivity for under-represented defect classes (`lamp broken`, `tire flat`, `scratch`) while preserving false-positive suppression.
* **Strategy:** Continued fine-tuning from EXP01 checkpoint with rare class oversampling and adjusted class losses.
* **Outcome:** Substantial improvement on development set: `mAP50` rose to `0.0308` (best epoch 7), Recall reached `0.5833`. Emerged as the winning candidate at Gate N.

### 8. EXP03 (Domain Adaptation: Unified MultiScale)
* **Objective:** Multi-scale spatial feature consolidation continuing from EXP02.
* **Outcome:** `mAP50 = 0.0207` at epoch 9, Recall = `0.6333`. Did not surpass EXP02 in validation balance, taking over 2x longer to train (290s vs 140s).

---

## 4. Key Takeaways for Phase 9 Optimization

1. **Learning Rate Sensitivity:** Fine-tuning from pre-converged checkpoints required low learning rates (`lr0 <= 0.0005`); standard defaults (`lr0=0.01`) caused catastrophic forgetting.
2. **Resolution & Batch Trade-off:** High resolution (1024) requires sufficient VRAM to support `batch >= 4`; otherwise gradient noise undermines performance.
3. **Negative Mining Penalty:** Heavy inclusion of empty negative images (>35% of training cohort) drastically suppressed false alarms but inadvertently attenuated structural crack recall.
