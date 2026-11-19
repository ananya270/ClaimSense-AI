# ClaimSense AI — Phase 9.1: Evaluated Model Checkpoint Inventory

**Document ID:** `REP-PH9-1-INV-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.1 — Model Performance Re-evaluation  
**Date:** 2026-11-19  
**Governing Standard:** `acquisition_specification.md` v1.1-ACTIVE  
**Execution Mode:** STRICTLY READ-ONLY EVALUATION. ZERO MODEL TRAINING, ZERO RETRAINING.

---

## 1. Executive Summary

This inventory documents all model checkpoints evaluated during Phase 9.1. Every candidate model was inspected on disk prior to inference. Cryptographic SHA-256 hashes were computed and reconciled against the known reference hashes established in Phase 9.0 and Gate P.

**Governance Certification:**
- No model checkpoint was overwritten, moved, or deleted.
- Missing checkpoints are reported transparently without silent substitution.
- Production baseline `models/phase5/best.pt` remains authoritative.

---

## 2. Model Checkpoint Inventory Table

| Checkpoint Name | Checkpoint Path | File Size (Bytes) | Cryptographic SHA-256 | Availability Status | Evaluation Status |
| :--- | :--- | :---: | :--- | :---: | :---: |
| **Production Baseline (Phase 5 - 5ep)** | `models/phase5/best.pt` | 6,472,810 | `49630ae8d5c0066d0532a2a38efede809920a6fccd3eed59a76eb3b65f009390` | **AVAILABLE** | **EVALUATED (Tracks A, B, Latency)** |
| **Historical Production Reference (1ep)** | `runs/detect/models/test_run/test_epoch/weights/best.pt` | 6,472,234 | `90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565` | **AVAILABLE** | **EVALUATED (Tracks A, B, Latency)** |
| **CarDD Damage YOLOv8n Standalone** | `models/cardd_damage_yolov8n.pt` | 6,472,810 | `49630ae8d5c0066d0532a2a38efede809920a6fccd3eed59a76eb3b65f009390` | **AVAILABLE** | **EVALUATED (Tracks A, B, Latency)** |
| **Phase 5 Last Epoch Checkpoint** | `models/phase5/last.pt` | 6,472,810 | `406a5fa1f5eb9b0e4c7254f73606be711e2858b70a9b6f105d5810794525dfdd` | **AVAILABLE** | **EVALUATED (Tracks A, B, Latency)** |
| **Phase 8 Session 1** | `runs/phase8/session_1/weights/best.pt` | — | Expected: `d670258e7cb7ecd5d86e1b99f9821578568a9b7877f095af75118706a4d7ccd0` | **MISSING** | Reconciled via historical logs |
| **Phase 8 Session 2** | `runs/phase8/session_2/weights/best.pt` | — | Expected: `2ee0a56749ceba72da863fd3496f080ee06f26409daa4e9588fb69ee149333c5` | **MISSING** | Reconciled via historical logs |
| **Phase 8 Session 3 (1024 Res)** | `runs/phase8/session_3_1024/weights/best.pt` | — | Expected: `9f0d6e2f4b52eb30f52e989eb199e4155454a50aed485c788258f06aaab61ebc` | **MISSING** | Reconciled via historical logs |
| **Phase 8 Session 4** | `runs/phase8/session_4_training_01/weights/best.pt` | — | Expected: `ea53eee94e508bbb81620b47b2a23c9826341b6b5a6981d9371e476cb9d0594f` | **MISSING** | Reconciled via historical logs |
| **EXP01 Negative Mining** | `runs/phase8/domain_adaptation/exp01_negative_mining/weights/best.pt` | — | Expected: `3ebd2a5c6ed2ca0aa58601d31c7918b95f5a2436fdab5ba34fd214dded366dc1` | **MISSING** | Reconciled via historical logs |
| **EXP02 Rare Class Expansion** | `runs/phase8/domain_adaptation/exp02_rare_class/weights/best.pt` | — | Expected: `68e2b58ec7759427808621debc9a8d725a9e4c1fbc57a2102cd239a8ca14f006` | **MISSING** | Reconciled via historical logs |
| **EXP03 Unified Multiscale** | `runs/phase8/domain_adaptation/exp03_unified_multiscale/weights/best.pt` | — | Expected: `550fa1c01b9f401f190658b7499ae4f442d9afdf93c72b2c4df00e369f815f01` | **MISSING** | Reconciled via historical logs |

---

## 3. Provenance & Discrepancy Reconciliation

### 1. The Dual Production Checkpoints
During Phase 9.0 and Phase 9.1, two distinct production-tier weights were identified on disk:
- **Active Production Checkpoint (`models/phase5/best.pt`):**
  - SHA-256: `49630ae8d5c0066d0532a2a38efede809920a6fccd3eed59a76eb3b65f009390`
  - Training configuration: 5 epochs on CarDD_300 (`imgsz=416`, `batch=16`).
  - Empirical metrics: `mAP50 = 0.1932`, `FP/image = 2.53`.
- **Historical Reference Checkpoint (`test_epoch/weights/best.pt`):**
  - SHA-256: `90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565`
  - Training configuration: 1 epoch test run on CarDD_300 (`imgsz=416`, `batch=16`).
  - Empirical metrics: `mAP50 = 0.0042`, `FP/image = 28.64`.
  - **Forensic Insight:** The 1-epoch binary explains the severe 6,503 false-positive count documented in Gate P. The 5-epoch model (`models/phase5/best.pt`) has much more mature feature convergence, cutting false positives down by over 90% (114 vs 1,289 on the test set).

### 2. Missing Historical Checkpoints
The physical `.pt` files for Sessions 1–4 and EXP01–EXP03 were excluded from the git remote via `.gitignore` (`runs/**/weights/`). However, all execution logs, loss curves, confusion matrices, and benchmark reports from Gate O and Gate P remain 100% accessible in the repository.

---

## 4. Inventory Artifact Link
The complete machine-readable inventory is serialized in:
[`runs/phase9/model_evaluation/phase9_1_checkpoint_inventory.csv`](file:///c:/Users/ydvan/Desktop/ClaimSense%20Ai/ClaimSense-AI/runs/phase9/model_evaluation/phase9_1_checkpoint_inventory.csv)
