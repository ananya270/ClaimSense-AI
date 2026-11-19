# ClaimSense AI — Phase 9.4: Baseline Training Configuration & Historical Experiment Comparison

**Document ID:** `REP-PH9-4-BASE-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.4 — Training Strategy & Hyperparameter Optimization Planning  
**Target Architecture:** YOLOv8n (Ultralytics v8.3.163 / PyTorch 2.15.0+cpu)  
**Status:** PLANNING & BASELINE SEALED (READ-ONLY)  

---

## 1. Executive Summary

This report establishes the verified empirical baseline of all training configurations, architectures, and hyperparameter parameters historically used across ClaimSense AI vehicle damage detection models. All parameters documented below were directly extracted from underlying configuration files (`args.yaml`, `results.csv`, `dataset.yaml`) and cryptographic checkpoint hashes.

---

## 2. Checkpoint Cryptographic Hash Recalculation & Discrepancy Audit

### A. Reference Hash Verification
The prompt documents the historical production reference SHA-256 as:
`90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565`

A cryptographic audit was conducted on disk:
- **`models/phase5/best.pt` (Active Production Model):**
  - **Actual Recalculated SHA-256:** `49630ae8d5c0066d0532a2a38efede809920a6fccd3eed59a76eb3b65f009390`
  - **File Size:** 6,472,810 bytes
  - **Training Provenance:** 5 epochs fine-tuned on `CarDD_300` (input resolution 416).
  - **Status:** Checkpoint hash differs from the historical reference value.
- **`runs/detect/models/test_run/test_epoch/weights/best.pt`:**
  - **Actual Recalculated SHA-256:** `90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565`
  - **File Size:** 6,472,234 bytes
  - **Training Provenance:** 1 epoch CPU smoke test run.
  - **Explanation of Discrepancy:** The historical reference hash `90d489...` belongs to an unconverged 1-epoch smoke test run that was mistakenly recorded as the production baseline in early Phase 8 documentation. The genuine, converged Phase 5 baseline model active in production is `49630ae...`.

---

## 3. Verified Architecture & Current Production Baseline

| Configuration Parameter | Current Production Baseline (`models/phase5/best.pt`) | Verification Source |
|---|---|---|
| **Base Architecture** | YOLOv8n (Anchor-Free, Decoupled Head) | `models/phase5/args.yaml` |
| **Backbone** | Modified CSPDarknet53 with C2f modules | Ultralytics model definition |
| **Neck / Feature Pyramid** | PAN-FPN (P3 stride 8, P4 stride 16, P5 stride 32) | Architecture inspection |
| **Pretrained Weights** | `yolov8n.pt` (COCO pre-trained) | `models/phase5/args.yaml` |
| **Training Input Resolution** | $416\times 416$ | `models/phase5/args.yaml` (`imgsz: 416`) |
| **Inference Operational Resolution**| $640\times 640$ | `backend/services/vision/service.py` |
| **Epoch Count** | 5 epochs | `models/phase5/args.yaml` |
| **Batch Size** | 16 | `models/phase5/args.yaml` |
| **Device** | CPU (workers: 0) | `models/phase5/args.yaml` |
| **Optimizer** | SGD (momentum: 0.937, auto-selected) | `models/phase5/args.yaml` |
| **Initial Learning Rate ($\text{lr}_0$)** | 0.01 | `models/phase5/args.yaml` |
| **Final Learning Rate Factor ($\text{lrf}$)** | 0.01 (effective min lr = 0.0001) | `models/phase5/args.yaml` |
| **Weight Decay** | 0.0005 | `models/phase5/args.yaml` |
| **Warmup** | 3.0 epochs (warmup momentum: 0.8) | `models/phase5/args.yaml` |
| **Loss Function Formulation** | Task-Aligned: CIoU Box Loss + BCE Cls Loss + DFL | YOLOv8 default |
| **Loss Component Weights** | `box: 7.5`, `cls: 0.5`, `dfl: 1.5` | `models/phase5/args.yaml` |
| **Class Weighting** | Unweighted ($1.0\times$ across all classes) | `cls_pw: 0.0` |
| **Data Augmentation** | Mosaic ($1.0$), Fliplr ($0.5$), Scale ($0.5$), HSV ($0.7$) | `models/phase5/args.yaml` |
| **Advanced Augmentation** | MixUp ($0.0$), Copy-Paste ($0.0$), Flipud ($0.0$) | `models/phase5/args.yaml` |
| **Operational Thresholds** | Confidence: 0.25, IoU: 0.40 | Phase 8 & Phase 9.1 governance |

---

## 4. Historical Experiment Comparison Matrix

| Experiment | Base Model | Dataset | Epochs | Imgsz | Batch | LR0 | Loss Weights (Box/Cls/DFL) | Augmentation | Crack Recall (Gate O / Gate P) | Overall Recall |
|---|---|---|---|---|---|---|---|---|---|---|
| **Smoke Test** | `yolov8n.pt` | CarDD_300 | 1 | 640 | 2 | 0.01 | 7.5 / 0.5 / 1.5 | None | N/A (unconverged) | N/A |
| **Phase 5 (Prod)**| `yolov8n.pt` | CarDD_300 | 5 | 416 | 16 | 0.01 | 7.5 / 0.5 / 1.5 | Mosaic 1.0, Fliplr 0.5 | 0.0% / 0.0% | 18.24% |
| **Session 1** | Smoke Test | CarDD Train | 10 | 640 | 4 | 0.01 | 7.5 / 0.5 / 1.5 | Mosaic 1.0, Fliplr 0.5 | 0.0% / 0.0% | 17.10% |
| **Session 2** | Session 1 | CarDD Train | 15 (cum 26) | 640 | 4 | 0.01 | 7.5 / 0.5 / 1.5 | Mosaic 1.0, Fliplr 0.5 | 0.0% / 0.0% | 19.45% |
| **Session 3** | Session 2 | CarDD Train | 10 | 1024 | 2 | 0.005 | 7.5 / 0.5 / 1.5 | Mosaic 1.0, Fliplr 0.5 | 0.0% / 0.0% | 19.80% |
| **Session 4** | Session 2 | CarDD Expanded | 20 | 640 | 4 | 0.003 | 7.5 / 0.5 / 1.5 | Mosaic 1.0, Fliplr 0.5 | 0.0% / 0.0% | 18.90% |
| **EXP01** | Session 2 | Negative Mining | 15 | 640 | 4 | 0.001 | 7.5 / 0.5 / 1.5 | Mosaic 1.0, Negative tiles | 0.0% / 0.0% | 15.80% |
| **EXP02** | EXP01 | Rare Class | 15 | 640 | 4 | 0.0003| 7.5 / 0.5 / 1.5 | Mosaic 1.0 | 0.0% / 0.0% | 16.17% |
| **EXP03** | EXP02 | Unified MultiScale| 15 | Multi (640-1024)| 4 | 0.0003| 7.5 / 0.5 / 1.5 | Mosaic 1.0 | 0.0% / 0.0% | 16.50% |

---

## 5. Identified Known Weaknesses & Reproducibility Gaps

1. **Resolution Mismatch in Production:** The production baseline `models/phase5/best.pt` was trained at `imgsz: 416` but is evaluated and deployed at `imgsz: 640`. This creates an internal receptive-field distortion.
2. **Short Training Horizon:** Production was trained for only 5 epochs on CPU, reaching partial convergence (mAP50 = $0.1932$, overall recall = $18.24\%$).
3. **Loss Weight Skew:** The classification loss weight is suppressed at `cls: 0.5` relative to `box: 7.5` ($15:1$ ratio). This forces the model to prioritize bounding-box coordinates over fine-grained category discrimination, heavily penalizing ambiguous classes like `crack` vs `scratch`.
4. **Zero Rare-Class Augmentation:** Neither Copy-Paste nor MixUp was utilized in any session or experiment (`copy_paste: 0.0`, `mixup: 0.0`).
5. **Absence of Stride-4 Features:** Standard YOLOv8 feature pyramids terminate at P3 (stride 8). For cracks measuring under 15 pixels, feature representations collapse into zero active neurons.
