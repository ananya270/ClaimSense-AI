# ClaimSense AI — Phase 9.11: Final Model Lineage & Checkpoint Provenance

**Project:** ClaimSense AI (Final-Year B.Tech Major Project)  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.11 — Final Documentation, Reproducibility & Project Sign-off  
**Document Classification:** Cryptographic Model Registry & Checkpoint Ledger  
**Date:** 2026-11-20

---

## 1. Executive Summary

This document establishes the official model provenance, cryptographic hashes, and operational status for all vehicle damage detection checkpoints evaluated across Phase 9.

To eliminate ambiguity between production assets and research candidates, every checkpoint is explicitly classified into one of four governance states: **Production**, **Staging**, **Rejected**, or **Experimental Control**.

---

## 2. Checkpoint Provenance & Cryptographic Ledger

```
+----------------------------------------------------------------------------------------------------+
| 1. AUTHORITATIVE PRODUCTION MODEL                                                                  |
+----------------------------------------------------------------------------------------------------+
| Designation:       Phase 5 Fine-Tuned Baseline                                                     |
| Checkpoint Path:   models/phase5/best.pt                                                           |
| Symlink / Mirror:  models/vehicle_damage/best.pt                                                   |
| Architecture:      Ultralytics YOLOv8n (Nano Object Detection)                                     |
| Parameters:        3,006,238 parameters (225 layers, 0 gradients)                                  |
| Input Resolution:  416 x 416 pixels                                                                |
| File Size:         6,472,810 bytes (6.17 MB)                                                       |
| Last Modified:     2026-11-16 09:08:07                                                             |
| SHA-256 Hash:      49630ae8d5c0066d0532a2a38efede809920a6fccd3eed59a76eb3b65f009390               |
| Benchmark mAP50:   0.1833 (Track A Independent CarDD Benchmark)                                    |
| Benchmark Precision: 0.2264                                                                        |
| Benchmark Recall:  0.2432                                                                          |
| Operational Status:ACTIVE PRODUCTION SINGLETON (PROTECTED, IMMUTABLE)                              |
| Governance Record: Re-certified as Authoritative at Gate 9.8 (Retain Existing Model)               |
+----------------------------------------------------------------------------------------------------+

+----------------------------------------------------------------------------------------------------+
| 2. CANDIDATE RETRAINED MODEL                                                                       |
+----------------------------------------------------------------------------------------------------+
| Designation:       Phase 9.5 Run T02 (High-Resolution Scaling)                                     |
| Checkpoint Path:   runs/phase9/retraining/P9-T02/checkpoints/best.pt                               |
| Architecture:      Ultralytics YOLOv8n (Nano Object Detection)                                     |
| Parameters:        3,006,238 parameters (225 layers, 0 gradients)                                  |
| Input Resolution:  640 x 640 pixels                                                                |
| File Size:         6,503,658 bytes (6.20 MB)                                                       |
| Last Modified:     2026-11-19 22:45:10                                                             |
| SHA-256 Hash:      91a943a9a246a0748d6f8f07a0b0860ad5872c3f229ab2f69930bb37db6ca721               |
| Benchmark mAP50:   0.2490 (+35.8% overall mAP gain over baseline)                                  |
| Benchmark Precision: 0.4194 (+85.2% precision increase, -85.4% false positives)                     |
| Benchmark Recall:  0.1757 (-27.8% recall trade-off across broad damage categories)                 |
| Crack Recall @ 0.25: 0.0000% (0 / 13 independent benchmark cracks detected)                        |
| Operational Status:REJECTED FOR PRODUCTION PROMOTION — PRESERVED FOR RESEARCH ONLY                 |
| Rejection Reason:  Failed zero-tolerance structural crack criterion; recall regression on dents,   |
|                    scratches, lamps, and flat tires.                                               |
+----------------------------------------------------------------------------------------------------+

+----------------------------------------------------------------------------------------------------+
| 3. EXPERIMENTAL CONTROL RUN                                                                        |
+----------------------------------------------------------------------------------------------------+
| Designation:       Phase 9.5 Run T01 (Reproducibility Baseline at 416x416)                          |
| Checkpoint Path:   runs/phase9/retraining/P9-T01/checkpoints/best.pt                               |
| Architecture:      Ultralytics YOLOv8n (Nano Object Detection)                                     |
| Input Resolution:  416 x 416 pixels                                                                |
| File Size:         6,503,658 bytes                                                                 |
| SHA-256 Hash:      4863aa9920efeb4db358e6587bbd6c52a36b3ce983b6fa0f12ad26693a20626b               |
| Operational Status:EXPERIMENTAL CONTROL (ARCHIVED)                                                 |
| Purpose:           Empirically confirmed reproducible retraining dynamics from base weights.       |
+----------------------------------------------------------------------------------------------------+

+----------------------------------------------------------------------------------------------------+
| 4. UPSTREAM PRETRAINED WEIGHTS                                                                     |
+----------------------------------------------------------------------------------------------------+
| Designation:       Ultralytics YOLOv8n Official Pretrained Weights                                 |
| Checkpoint Path:   yolov8n.pt                                                                      |
| SHA-256 Hash:      f59b3d833e2ff32e194b5bb8e08d211dc7c5bdf144b90d2c8412c47ccfc83b36               |
| Operational Status:UPSTREAM FOUNDATION CHECKPOINT (READ-ONLY)                                      |
+----------------------------------------------------------------------------------------------------+
```

---

## 3. Class Index & Labeling Schema Invariance

All evaluated models adhere to the identical 6-class CarDD taxonomy:

```json
{
  "0": "dent",
  "1": "scratch",
  "2": "crack",
  "3": "glass shatter",
  "4": "lamp broken",
  "5": "tire flat"
}
```

No class label renaming, deletion, or reordering occurred across any phase. Downstream rules in `backend/services/verification/rules.py` remain 100% interoperable.

---

## 4. Final Deployment Statement

The authoritative production model is **`models/phase5/best.pt`** (SHA-256: `49630ae8d5c0066d0532a2a38efede809920a6fccd3eed59a76eb3b65f009390`). No model promotion, replacement, or deployment modification was executed during Phase 9.
