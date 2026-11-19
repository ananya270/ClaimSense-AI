# ClaimSense AI — Phase 9.5: Training Execution Log & Chronology

**Document ID:** `REP-PH9-5-LOG-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.5 — Controlled Retraining and Experiment Execution  
**Execution Date:** 2026-11-20  
**Status:** ALL TRAINING RUNS COMPLETE & QUARANTINED  

---

## 1. Executive Summary & Governance Protocol

Phase 9.5 executes controlled model retraining to investigate and resolve the structural crack detection bottleneck (0% historical recall) while preserving non-crack damage detection performance.

In strict compliance with the **Phase 9.5 Operational Mandate**:
1. All candidate checkpoints are written to isolated quarantine directories under `runs/phase9/retraining/`.
2. The active production model `models/phase5/best.pt` remains strictly untouched and read-only.
3. Historical checkpoints (Session 1–4, EXP01, EXP02, EXP03) remain unmodified.
4. Production database (`data/claimsense.db`) and APIs remain untouched.
5. All runs use fixed seed 42 and reproducible training configs.

---

## 2. Chronological Training Job Register

### Job 1: Experiment P9-T01 (Reproducible Baseline)
- **Experiment ID:** `P9-T01`
- **Objective:** Establish the reproducible control anchor matching Phase 5 parameters.
- **Start Time:** 2026-11-19 23:55:05 IST
- **End Time:** 2026-11-19 23:59:20 IST
- **Duration:** 255.36 seconds (4.26 min)
- **Base Checkpoint:** `yolov8n.pt` (SHA-256: `f59b3d833e2ff32e194b5bb8e08d211dc7c5bdf144b90d2c8412c47ccfc83b36`)
- **Key Hyperparameters:**
  - Architecture: YOLOv8n
  - Epochs: 5
  - Image Resolution: $416\times 416$
  - Batch Size: 16
  - Optimizer: SGD ($\text{lr}_0=0.01$, momentum=0.937)
  - Loss Weights: `box=7.5, cls=0.5, dfl=1.5`
  - Seed: 42
  - Device: CPU (Intel Core i5-1035G1)
- **Exit Code:** 0 (SUCCESS)
- **Quarantined Best Checkpoint:** `runs/phase9/retraining/P9-T01/checkpoints/best.pt`
  - SHA-256: `e3e60fd2911819ec996ed5ce1591ced26530692be7d55ec22d55e4c2fde51e80`
- **Validation Outcome:**
  - Overall mAP@50: 0.2732
  - Overall Recall: 0.4046
  - Crack Recall: 0.0000 (0/11 detections)
  - Baseline replicated with high fidelity.

---

### Job 2: Experiment P9-T02 (Resolution Comparison — 640x640)
- **Experiment ID:** `P9-T02`
- **Objective:** Evaluate the effect of higher spatial resolution ($640\times 640$) in preserving slender sub-grid crack features.
- **Start Time:** 2026-11-20 00:02:00 IST
- **End Time:** 2026-11-20 00:11:37 IST
- **Duration:** 577.54 seconds (9.63 min)
- **Base Checkpoint:** `yolov8n.pt`
- **Key Hyperparameters:**
  - Architecture: YOLOv8n
  - Epochs: 5
  - Image Resolution: $640\times 640$
  - Batch Size: 8
  - Optimizer: SGD ($\text{lr}_0=0.01$)
  - Loss Weights: `box=7.5, cls=0.5, dfl=1.5`
  - Seed: 42
  - Device: CPU
- **Exit Code:** 0 (SUCCESS)
- **Quarantined Best Checkpoint:** `runs/phase9/retraining/P9-T02/checkpoints/best.pt`
  - SHA-256: `91a943a9a246a0748d6f8f07a0b0860ad5872c3f229ab2f69930bb37db6ca721`
- **Validation Outcome:**
  - Overall mAP@50: 0.3093 (+13.2% relative gain)
  - Overall Precision: 0.4028
  - Overall Recall: 0.3540
  - Crack AP@50: 0.0076 (38x increase over baseline)
  - Crack Recall: 0.0000 (0/11 at rigid $\tau=0.25$)

---

## 3. Quarantined Checkpoint Register

| Experiment ID | Checkpoint Relpath | Size (Bytes) | SHA-256 Digest | Status |
|---|---|---|---|---|
| **Production Ref** | `models/phase5/best.pt` | 6,472,810 | `49630ae8d5c0066d0532a2a38efede809920a6fccd3eed59a76eb3b65f009390` | **FROZEN / UNTOUCHED** |
| **P9-T01 Best** | `runs/phase9/retraining/P9-T01/checkpoints/best.pt` | 6,472,874 | `e3e60fd2911819ec996ed5ce1591ced26530692be7d55ec22d55e4c2fde51e80` | **QUARANTINED** |
| **P9-T01 Last** | `runs/phase9/retraining/P9-T01/checkpoints/last.pt` | 6,472,874 | `13937a8f4b6bcdca2fdfc780f19fc5adc014f1bc069e3c14fa51f81a66519b5d` | **QUARANTINED** |
| **P9-T02 Best** | `runs/phase9/retraining/P9-T02/checkpoints/best.pt` | 6,503,658 | `91a943a9a246a0748d6f8f07a0b0860ad5872c3f229ab2f69930bb37db6ca721` | **QUARANTINED** |
| **P9-T02 Last** | `runs/phase9/retraining/P9-T02/checkpoints/last.pt` | 6,503,658 | `c8d977ae2fd2509c298346588cc1dc45bd9d6ab9e618e164297eba87c61b3246` | **QUARANTINED** |

---

## 4. Safety & Boundary Audit Checklist

- [x] Production checkpoint `models/phase5/best.pt` verified unchanged.
- [x] Production database `data/claimsense.db` verified unchanged.
- [x] Flask production API and UI code verified unmodified.
- [x] Frozen test splits and Gate O / Gate P datasets untouched.
- [x] Zero Git commit or push actions triggered.
- [x] All candidate artifacts quarantined inside `runs/phase9/retraining/`.
