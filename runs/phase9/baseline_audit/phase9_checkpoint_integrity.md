# ClaimSense AI — Phase 9.0: Checkpoint Integrity & Provenance Audit

**Document ID:** `AUD-PH9-CKPT-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.0 — Baseline Audit  
**Date:** 2026-11-19  
**Governing Standard:** `acquisition_specification.md` v1.1-ACTIVE  
**Audit Scope:** Cryptographic SHA-256 Checksum Verification of All Historical & Production Model Checkpoints

---

## 1. Executive Summary

A cryptographic audit was conducted across the local filesystem to verify the provenance and integrity of all known model checkpoints referenced in Phase 5 and Phase 8 (Gates A–P). 

Every locally accessible `.pt` checkpoint was hashed using SHA-256. The findings confirm that while training logs, configuration manifests (`args.yaml`), and performance metrics (`results.csv`) are 100% intact across all sessions, several binary checkpoint weights are absent from this checkout due to standard `.gitignore` rules (`*.pt`, `runs/**/weights/`).

**Safety Compliance:** In strict accordance with Phase 9 safety directives, no checkpoint was overwritten, no missing file was silently substituted, and `models/phase5/best.pt` remains unmodified.

---

## 2. Checkpoint Cryptographic Audit Table

| Checkpoint Identifier | Target File Path | Known Reference SHA-256 | Actual Local SHA-256 | File Size (Bytes) | Verification Verdict |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **Production Baseline** | `models/phase5/best.pt` | `90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565` | `49630ae8d5c0066d0532a2a38efede809920a6fccd3eed59a76eb3b65f009390` | 6,472,810 | **HASH MISMATCH** *(See Section 3)* |
| **Test Epoch Checkpoint** | `runs/detect/models/test_run/test_epoch/weights/best.pt` | *(Discovered during scan)* | `90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565` | 6,472,234 | **EXACT MATCH TO PROD REF** |
| **Phase 8 Session 1** | `runs/phase8/session_1/weights/best.pt` | `d670258e7cb7ecd5d86e1b99f9821578568a9b7877f095af75118706a4d7ccd0` | *None (File Missing)* | — | **MISSING FILE** |
| **Phase 8 Session 2** | `runs/phase8/session_2/weights/best.pt` | `2ee0a56749ceba72da863fd3496f080ee06f26409daa4e9588fb69ee149333c5` | *None (File Missing)* | — | **MISSING FILE** |
| **Phase 8 Session 3** | `runs/phase8/session_3_1024/weights/best.pt` | `9f0d6e2f4b52eb30f52e989eb199e4155454a50aed485c788258f06aaab61ebc` | *None (File Missing)* | — | **MISSING FILE** |
| **Phase 8 Session 4** | `runs/phase8/session_4_training_01/weights/best.pt` | `ea53eee94e508bbb81620b47b2a23c9826341b6b5a6981d9371e476cb9d0594f` | *None (File Missing)* | — | **MISSING FILE** |
| **EXP01 Negative Mining** | `runs/phase8/domain_adaptation/exp01_negative_mining/weights/best.pt` | `3ebd2a5c6ed2ca0aa58601d31c7918b95f5a2436fdab5ba34fd214dded366dc1` | *None (File Missing)* | — | **MISSING FILE** |
| **EXP02 Rare Class** | `runs/phase8/domain_adaptation/exp02_rare_class/weights/best.pt` | `68e2b58ec7759427808621debc9a8d725a9e4c1fbc57a2102cd239a8ca14f006` | *None (File Missing)* | — | **MISSING FILE** |
| **EXP03 MultiScale** | `runs/phase8/domain_adaptation/exp03_unified_multiscale/weights/best.pt` | `550fa1c01b9f401f190658b7499ae4f442d9afdf93c72b2c4df00e369f815f01` | *None (File Missing)* | — | **MISSING FILE** |

---

## 3. Analysis of the Production Hash Discrepancy

### Detailed Findings:
1. **The Current `models/phase5/best.pt` Binary:**
   - Hash: `49630ae8d5c0066d0532a2a38efede809920a6fccd3eed59a76eb3b65f009390`
   - File size: `6,472,810 bytes`
   - Identical to: `models/cardd_damage_yolov8n.pt`, `models/runs/cardd_damage/weights/best.pt`, and `models/vehicle_damage/best.pt`.
   - Training origin: 5-epoch training run on `CarDD_300` (`data: C:\Users\ydvan\Desktop\ClaimSense Ai\ClaimSense-AI\datasets\CarDD_300\data.yaml`, batch=16, imgsz=416).
2. **The Historical Reference Binary (`90d489e...`):**
   - Hash: `90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565`
   - File size: `6,472,234 bytes`
   - Location: Persisted on disk at `runs/detect/models/test_run/test_epoch/weights/best.pt`.
   - Training origin: 1-epoch initial verification run on `CarDD_300` recorded in `runs/detect/models/test_run/test_epoch/args.yaml`.
3. **Safety Evaluation:**
   Per strict instructions:
   > "Report missing files or hash mismatches explicitly. Never silently replace a missing checkpoint. Do not overwrite models/phase5/best.pt."
   `models/phase5/best.pt` has been left strictly intact. Both binaries are preserved, and their exact cryptographic signatures are documented for Phase 9 governance.

---

## 4. Analysis of Missing Checkpoints (Sessions 1–4, EXP01–03)

### Root Cause:
The repository's `.gitignore` contains the following active exclusions:
```gitignore
*.pth
*.pt
*.h5
*.onnx
*.weights
models/*
!models/.gitkeep
runs/**/weights/
```
Because of these rules, binary weight checkpoints produced during Phase 8 training on the remote/previous GPU host were not committed to git, preventing repository bloat.

### Preserved Forensic Evidence:
Despite the absence of the raw weight weights, **100% of the training execution logs, parameters, and metric curves are preserved in the repository**:
- `args.yaml` files exist for all sessions and experiments, capturing every hyperparameter.
- `results.csv` files exist for all sessions and experiments, recording per-epoch loss, precision, recall, mAP50, and mAP50-95.
- Complete per-class metric evaluations are archived in `runs/phase8/master_orchestration/` (e.g., `gate_o_per_class_metrics.csv` and `gate_p_model_comparison_audited.csv`).

---

## 5. Checkpoint Integrity Conclusion

1. **Local Checkpoints Audited:** 10 `.pt` binaries inspected and hashed.
2. **Missing Reference Checkpoints:** 7 binary files (Session 1, Session 2, Session 3, Session 4, EXP01, EXP02, EXP03).
3. **Discrepancy Documented:** Production reference `90d489e...` resides in `runs/detect/models/test_run/test_epoch/weights/best.pt`, while `models/phase5/best.pt` holds `49630ae...`.
4. **Action:** No binary files were altered, moved, or deleted. All findings are sealed for Phase 9 baseline certification.
