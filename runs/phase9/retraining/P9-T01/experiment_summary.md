# ClaimSense AI — Phase 9.5: Experiment Summary P9-T01

**Experiment ID:** `P9-T01`  
**Description:** Reproducible Baseline Verification (Resolution 416, 5 epochs, SGD, CarDD_300)  
**Execution Date:** 2026-11-19 23:55:00 IST  
**Status:** COMPLETE (QUARANTINED)  

---

## 1. Experiment Overview

Experiment `P9-T01` establishes the controlled, scientifically reproducible baseline against which all Phase 9 optimization trials are compared. It mirrors the exact architecture (`yolov8n.pt`), resolution ($416\times 416$), optimizer (SGD, $\text{lr}_0=0.01$), loss parameters ($\text{box}=7.5, \text{cls}=0.5, \text{dfl}=1.5$), and epoch count (5 epochs) of the Phase 5 production baseline, using deterministic random seed 42.

All training artifacts and checkpoints are strictly quarantined in:
`runs/phase9/retraining/P9-T01/`

---

## 2. Quantitative Results

### Overall Model Performance (CarDD_300 Validation Split, N=45 images, 140 damage instances)

| Metric | Measured Value | Production Baseline Ref (`models/phase5/best.pt`) | Delta |
|---|---|---|---|
| **Precision (all classes)** | 0.3838 | 0.4285 | -0.0447 |
| **Recall (all classes)** | 0.4046 | 0.4071 | -0.0025 |
| **mAP@50 (all classes)** | 0.2732 | 0.2714 | +0.0018 |
| **mAP@50-95 (all classes)**| 0.1774 | 0.1832 | -0.0058 |
| **Inference Latency (CPU)** | 31.0 ms | 31.2 ms | -0.2 ms |

### Class-Wise Validation Performance Breakdown

| Class ID | Class Name | Instances | Precision | Recall | F1-Score | mAP@50 | mAP@50-95 |
|---|---|---|---|---|---|---|---|
| 0 | dent | 44 | 0.1199 | 0.0776 | 0.0942 | 0.0723 | 0.0312 |
| 1 | scratch | 60 | 0.0260 | 0.0500 | 0.0342 | 0.0235 | 0.0092 |
| **2** | **crack** | **11** | **1.0000** | **0.0000** | **0.0000** | **0.0002** | **0.0002** |
| 3 | glass shatter | 10 | 0.3976 | 0.7000 | 0.5071 | 0.5572 | 0.4574 |
| 4 | lamp broken | 10 | 0.1448 | 0.8000 | 0.2452 | 0.2341 | 0.1360 |
| 5 | tire flat | 5 | 0.6148 | 0.8000 | 0.6953 | 0.7519 | 0.4304 |

---

## 3. Analysis & Key Findings

1. **Reproduction Fidelity:** The retrained model closely replicates the production baseline with an mAP@50 of **0.2732** (within $0.66\%$ of the production baseline $0.2714$).
2. **Structural Crack Failure Confirmed:** Crack recall is **0.0000%** (0 of 11 instances detected). The precision is reported as 1.0000 solely due to the zero-detection edge case at confidence $\tau=0.25$.
3. **Severe Imbalance:** Structural cracks represent only $7.8\%$ of validation annotations and $6.8\%$ of training annotations. Without class-reweighting or resolution scaling, the detection head completely collapses crack predictions to background.
4. **Hardware & Compute Footprint:** Training completed in **255.36 seconds** ($\approx 4.25\text{ min}$) on Intel Core i5-1035G1 CPU, utilizing a peak memory overhead of $460.74\text{ MB}$.

---

## 4. Checkpoint Integrity & Quarantine Status

- **Initial Base Checkpoint:** `yolov8n.pt` (`f59b3d833e2ff32e194b5bb8e08d211dc7c5bdf144b90d2c8412c47ccfc83b36`)
- **Quarantined Best Checkpoint:** `runs/phase9/retraining/P9-T01/checkpoints/best.pt`
  - File Size: 6,472,874 bytes
  - SHA-256: `e3e60fd2911819ec996ed5ce1591ced26530692be7d55ec22d55e4c2fde51e80`
- **Quarantined Last Checkpoint:** `runs/phase9/retraining/P9-T01/checkpoints/last.pt`
  - File Size: 6,472,874 bytes
  - SHA-256: `13937a8f4b6bcdca2fdfc780f19fc5adc014f1bc069e3c14fa51f81a66519b5d`

> [!IMPORTANT]
> The candidate checkpoint is quarantined and was NOT deployed to production. `models/phase5/best.pt` remains unmodified.
