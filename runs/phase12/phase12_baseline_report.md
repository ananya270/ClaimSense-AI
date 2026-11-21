# ClaimSense AI — Phase 12 Baseline & Preflight Audit Report
## Asynchronous Processing, Production Reliability & Academic Defense Readiness

**Document Reference:** `runs/phase12/phase12_baseline_report.md`  
**Governance Date:** November 21, 2026  
**Auditor Roles:** Principal Software Architect, Senior Backend Engineer, DevOps Engineer, QA Lead & Academic Advisor  
**Target Branch:** `feature/phase12-async-processing`  
**Base Commit:** `4f2d993678a9af4ff8aec991ba3503fd2c7fafcf` (`feat(phase11): complete production hardening, containerization and operational readiness`)  

---

## 1. Repository & Preflight State

- **Active Branch:** `feature/phase12-async-processing` (branched from `feature/phase11-deployment-hardening`)
- **Base Commit SHA:** `4f2d993678a9af4ff8aec991ba3503fd2c7fafcf`
- **Remote Origin:** `https://github.com/anshg8252/ClaimSense-AI.git`
- **Local Working Tree:** Clean (0 uncommitted modifications, 0 staged changes)
- **Python Runtime:** Python 3.14.6 64-bit on Windows 11 (`Windows-11-10.0.26300-SP0`)
- **Virtual Environment:** `.venv` active with Flask 3.1.3, SQLAlchemy 2.0.46, ReportLab 4.4.11, Ultralytics 8.4.18, PyTorch 2.11.0.dev.

---

## 2. Production Safety Invariants & Cryptographic Baselines

| Asset | Path | Baseline Metric | Status |
|:---|:---|:---|:---:|
| **Production Model Checkpoint** | `models/phase5/best.pt` | SHA-256: `49630ae8d5c0066d0532a2a38efede809920a6fccd3eed59a76eb3b65f009390` | **VERIFIED IMMUTABLE** |
| **Production SQLite Database** | `data/claimsense.db` | SHA-256: `0a55d4e7571ed24694563f28b0fe385eb1bc4e42b853dd53ce0e44fd45d43d55` | **VERIFIED PROTECTED** |
| **Customer Uploads Inventory** | `uploads/` | 151 files, 23 claim directories | **VERIFIED PROTECTED** |
| **Active Production Tables** | `claimsense.db` | 23 claims, 17 users, 6 report snapshots | **VERIFIED INTACT** |

---

## 3. Existing Test Baseline

- **Total Test Modules:** 16 modules in `tests/`
- **Total Tests Collected:** 203 items
- **Baseline Test Results:** **202 passed, 1 skipped, 0 failures, 0 errors in 127.11s (100% pass rate)**.
- **Skipped Test:** `test_kcm0_history_and_integrity_preserved` (historical mock calibration).

---

## 4. Current Claim Ingestion Flow & Latency Forensics

### Existing Synchronous Pipeline (`POST /api/claims`):
1. **Request Intake:** Multipart HTTP POST received with claimant form metadata and 4 evidentiary files.
2. **File Validation & Disk Write:** Authenticates user session, validates file formats and magic bytes, sanitizes filenames with `secure_filename()`, writes files to `uploads/<claim_id>/`.
3. **Database Relational Commit:** Inserts `Claim` and `Document` records in `data/claimsense.db`.
4. **Synchronous OCR Extraction:** Executes Tesseract OCR across policy schedule and invoice (~800–1200 ms).
5. **Synchronous YOLOv8 Damage Detection:** Runs `models/phase5/best.pt` on uploaded vehicle image (~50–150 ms warm, up to ~2,500 ms cold).
6. **Synchronous NLP Narrative Parsing:** Parses free-text narrative for chronological event reconstruction (~15 ms).
7. **Synchronous Cross-Source Verification:** Executes Phase 7 triangulation engine linking narrative, OCR, and vision (~35 ms).
8. **HTTP Response:** Returns HTTP 201 Created with full claim dictionary.

### Empirical Latency Measurements:
- **Mean Single-User Submission Time:** **~3,100 ms to 3,650 ms**
- **Under Concurrency (50 Users):** Mean latency reaches **673.28 ms** (WAL mode) and **740.51 ms** (DELETE mode); p95 reaches **1,400 ms**; maximum response spike reaches **4,502 ms**.
- **Root Cause:** All computational OCR and neural-network forward passes execute synchronously within the WSGI intake thread, tying up server worker threads and blocking incoming requests.

---

## 5. Phase 12 Target Architecture & Objectives

1. **Sub-100ms Ingestion Latency:** Decouple OCR, YOLOv8, and verification into background workers; return `HTTP 202 Accepted` immediately upon secure upload persistence.
2. **Reliable Polling Status API:** Expose `GET /api/claims/<claim_id>/status` with clear stage progression (`queued` -> `ocr_processing` -> `damage_analysis` -> `cross_source_verification` -> `completed` / `failed`).
3. **Robust Worker Architecture:** Dual-engine broker support (Redis-backed for Docker/cloud deployments; in-process threaded pool with persistent SQLite state for standalone/local development).
4. **Academic Defense Package:** Comprehensive viva question bank ($\ge 80$ technical Q&As), presentation slides outline, demo runbook, and architectural documentation.
