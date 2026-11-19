# ClaimSense AI — Phase 9.6: Model Comparison Registry

**Document ID:** `REG-PH9-6-MODELS-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.6 — Independent Benchmark Evaluation & Candidate Model Validation  
**Execution Date:** 2026-11-20  
**Status:** BENCHMARKED & AUDITED (ALL CANDIDATES QUARANTINED)  

---

## 1. Overview & Registry Scope

This registry catalogs the complete set of computer vision damage detection models evaluated during Phase 9.6 across frozen benchmark cohorts.

In strict compliance with governance policies:
- No candidate checkpoint has replaced `models/phase5/best.pt`.
- All candidate checkpoints are read-only and quarantined under `runs/phase9/retraining/`.
- Provenance and cryptographic hashes were verified before and after evaluation.

---

## 2. Model Registry Table

| Model ID | Display Name | Relative Checkpoint Path | SHA-256 Digest (Full) | Training Resolution | Epochs | Batch | Seed | Pretrained Base | Status |
|---|---|---|---|---|---|---|---|---|---|
| **PROD-BASELINE** | Production Baseline (Phase 5) | `models/phase5/best.pt` | `49630ae8d5c0066d0532a2a38efede809920a6fccd3eed59a76eb3b65f009390` | $416\times 416$ | 5 | 16 | 42 | `yolov8n.pt` | **Active Production Reference** |
| **P9-T01-BEST** | P9-T01 Baseline Candidate | `runs/phase9/retraining/P9-T01/checkpoints/best.pt` | `e3e60fd2911819ec996ed5ce1591ced26530692be7d55ec22d55e4c2fde51e80` | $416\times 416$ | 5 | 16 | 42 | `yolov8n.pt` | **Quarantined Control** |
| **P9-T02-BEST** | P9-T02 Resolution Scaling | `runs/phase9/retraining/P9-T02/checkpoints/best.pt` | `91a943a9a246a0748d6f8f07a0b0860ad5872c3f229ab2f69930bb37db6ca721` | $640\times 640$ | 5 | 8 | 42 | `yolov8n.pt` | **Quarantined Candidate** |

---

## 3. Checkpoint Provenance & Lineage Details

### Model 1: Production Baseline (`PROD-BASELINE`)
- **Origin:** Trained during Phase 5 (Model Training & Deployment) on the original CarDD_300 split.
- **Role:** Production reference benchmark for all subsequent ClaimSense AI validation gates.
- **Serving Path:** Loaded by `backend/services/vision/damage_detector.py`.
- **Operational Thresholds:** Confidence $\tau = 0.25$, $\text{IoU} \ge 0.40$.
- **Historical Crack Performance:** 0/6 (Gate O), 0/14 (Gate P), 0/11 (CarDD Val), 0/13 (CarDD Test).

### Model 2: P9-T01 Baseline Candidate (`P9-T01-BEST`)
- **Origin:** Retrained in Phase 9.5 (`P9-T01`) from pre-trained `yolov8n.pt`.
- **Role:** Controlled scientific reproduction anchor isolating non-deterministic variations.
- **Parameters:** Matched resolution ($416\times 416$), SGD ($\text{lr}_0=0.01$), seed 42.

### Model 3: P9-T02 Resolution Scaling Candidate (`P9-T02-BEST`)
- **Origin:** Trained in Phase 9.5 (`P9-T02`) to test spatial resolution preservation on thin fissures.
- **Role:** Top-performing Phase 9.5 candidate ($+13.2\%$ relative val mAP gain, $38\times$ crack AP activation).
- **Parameters:** Resolution $640\times 640$, batch 8, SGD ($\text{lr}_0=0.01$), seed 42.

---

## 4. Cryptographic Integrity Statement

All checkpoint files were verified before and after evaluation. Cryptographic SHA-256 hashes exhibited zero variance (100% invariant). No weights were modified during benchmark execution.
