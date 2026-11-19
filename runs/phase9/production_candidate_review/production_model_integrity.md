# ClaimSense AI — Phase 9.7: Production Model Integrity & Lineage Audit

**Document ID:** `AUD-PH9-7-PROD-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.7 — Production Model vs Candidate Comparative Analysis & Promotion Readiness Review  
**Execution Date:** 2026-11-20  
**Status:** PRODUCTION ASSET VERIFIED UNMODIFIED  

---

## 1. Production Model Identity & Specification

| Specification Dimension | Documented Value |
|---|---|
| **Model Role** | Active Production Vehicle Damage Detector |
| **Model Identifier** | `PROD-BASELINE` (Phase 5 Production Checkpoint) |
| **Serving Checkpoint Path** | `models/phase5/best.pt` |
| **Base Architecture** | YOLOv8n (Nano Detection Head, 3,133,922 parameters) |
| **Training Input Resolution** | $416\times 416$ pixels |
| **Training Dataset** | CarDD_300 (train: 210 images, val: 45 images) |
| **Training Duration** | 5 epochs (SGD optimizer, momentum=0.937, $\text{lr}_0=0.01$) |
| **Serving Pipeline Module** | `backend/services/vision/damage_detector.py` |
| **Serving Endpoint** | `POST /api/claims/<claim_id>/analyze-damage` |
| **Production Operational Thresholds** | Confidence $\tau = 0.25$, $\text{IoU} \ge 0.40$ |

---

## 2. Cryptographic Checksum Audit

In accordance with Phase 9.7 Section 1 and Section 2:

- **Measured Local Checkpoint Path:** `c:/Users/ydvan/Desktop/ClaimSense Ai/ClaimSense-AI/models/phase5/best.pt`
- **Measured File Size:** 6,472,810 bytes
- **Measured SHA-256 Digest:**
  `49630ae8d5c0066d0532a2a38efede809920a6fccd3eed59a76eb3b65f009390`
- **File System Modification Timestamp:** Invariant across Phase 9.0, 9.1, 9.2, 9.4, 9.5, 9.6, and 9.7.
- **Historical Hash Reconciliation:**
  - The historical reference hash `90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565` (6,472,234 bytes) originates from the initial 1-epoch test run checkpoint `runs/detect/models/test_run/test_epoch/weights/best.pt`.
  - The active serving production checkpoint `models/phase5/best.pt` has consistently maintained SHA-256 `49630ae8...` throughout all Phase 8 and Phase 9 audits.

---

## 3. Production Service Integrity Checklist

- [x] Checkpoint file `models/phase5/best.pt` has NOT been overwritten or renamed.
- [x] Checkpoint permissions remain read-only.
- [x] No weights or parameter layers have been modified.
- [x] Production Flask service (`task-694`) continues serving the active Phase 5 model.
- [x] Zero writes to production database `data/claimsense.db`.
- [x] Audit Verdict: **PASS — 100% UNMODIFIED**.
