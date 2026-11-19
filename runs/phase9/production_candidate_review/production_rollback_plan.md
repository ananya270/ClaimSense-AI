# ClaimSense AI — Phase 9.7: Production Rollback & Checkpoint Preservation Plan

**Document ID:** `SOP-PH9-7-ROLLBACK-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.7 — Production Model vs Candidate Comparative Analysis & Promotion Readiness Review  
**Execution Date:** 2026-11-20  
**Status:** THEORETICAL SPECIFICATION ONLY (NO EXECUTION PERMITTED)  

---

## 1. Executive Purpose & Safety Statement

In strict compliance with Phase 9.7 Section 11:
> *"Prepare a theoretical rollback and preservation plan without executing it. Do not copy, replace, rename, or modify production artifacts. Do not activate a candidate model. Do not modify application code."*

This document defines the formal operational procedure to safeguard the production environment and execute an instantaneous zero-loss rollback if a candidate checkpoint is ever authorized for pilot deployment in future phases.

---

## 2. Checkpoint Provenance & Cryptographic Signatures

### 2.1 Current Active Production Asset
- **Filesystem Path:** `models/phase5/best.pt`
- **File Size:** 6,472,810 bytes
- **SHA-256 Checksum:** `49630ae8d5c0066d0532a2a38efede809920a6fccd3eed59a76eb3b65f009390`
- **Serving Configuration:**
  - Input resolution: $416\times 416$
  - Operational confidence: $\tau = 0.25$
  - Operational IoU: $\text{IoU} = 0.40$
  - Service Module: `backend/services/vision/damage_detector.py`
  - Active Service Process: Port 5001 (`task-694`)

### 2.2 Quarantined Candidate Asset (Under Consideration for Future Retraining)
- **Filesystem Path:** `runs/phase9/retraining/P9-T02/checkpoints/best.pt`
- **File Size:** 6,503,658 bytes
- **SHA-256 Checksum:** `91a943a9a246a0748d6f8f07a0b0860ad5872c3f229ab2f69930bb37db6ca721`
- **Status:** **STRICTLY QUARANTINED — INACTIVE**

---

## 3. Pre-Deployment Backup & Isolation Requirements

Prior to any potential future deployment authorization (Phase 10):
1. **Cold Snapshot Creation:**
   ```powershell
   Copy-Item -Path "models/phase5/best.pt" -Destination "backups/checkpoints/production_phase5_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').pt" -Force
   ```
2. **Cryptographic Validation:** Validate that the snapshot SHA-256 matches `49630ae8...` exactly.
3. **Database Freeze:** Take an atomic snapshot of SQLite production database `data/claimsense.db` before activating any schema or inference alterations.

---

## 4. Rollback Triggers & Circuit-Breakers

A mandatory, automated rollback to `models/phase5/best.pt` must be triggered immediately if any of the following conditions occur in production:
1. **Inference Latency Breach:** P95 latency exceeds $250\text{ ms}$ over 50 consecutive user requests.
2. **Detection Failure Spike:** Percentage of claims returning zero detections exceeds $65\%$ over a 24-hour evaluation window.
3. **Internal Server Error (HTTP 500):** Any unhandled tensor shape or CUDA/CPU mismatch exception in `analyze-damage`.
4. **False Positive Spike:** Customer dispute rate on hallucinated structural damage increases by $>10\%$.

---

## 5. Step-by-Step Emergency Rollback Execution Procedure

If a circuit-breaker is tripped:

1. **Step 1: Terminate Active Backend Worker:**
   Stop the serving Flask instance gracefully to release file locks on `models/phase5/best.pt`.
2. **Step 2: Restore Verified Checkpoint:**
   ```powershell
   Copy-Item -Path "backups/checkpoints/production_phase5_backup_*.pt" -Destination "models/phase5/best.pt" -Force
   ```
3. **Step 3: Verify Restored Hash:**
   Confirm SHA-256 returns:
   `49630ae8d5c0066d0532a2a38efede809920a6fccd3eed59a76eb3b65f009390`
4. **Step 4: Restart Serving Process:**
   Restart Flask on port 5001.
5. **Step 5: Execute Automated Health Probe:**
   Send `GET /api/health` and verify HTTP 200 OK with `model_available: true`.

---

## 6. Current Operational Safety Status

- Current Production Checkpoint Status: **ACTIVE & UNCHANGED**.
- Candidate Deployment Status: **NONE (ZERO DEPLOYMENT OCCURRED)**.
- Rollback Execution Status: **IDLE (STANDBY ONLY)**.
