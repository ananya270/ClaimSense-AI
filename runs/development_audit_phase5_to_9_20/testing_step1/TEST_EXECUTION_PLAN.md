# ClaimSense AI — Phased Safe Test Execution Plan

**Audit Phase:** Step 1: Test Discovery, Safety Audit & Testing Baseline  
**Date:** 2026-11-21  
**Status:** Planning Only — **STRICTLY NO TESTS EXECUTED DURING STEP 1**  
**Execution Condition:** This document outlines the prospective sequence to be executed in subsequent testing phases.

---

## 1. Phased Execution Architecture Overview

To guarantee zero corruption of `data/claimsense.db`, protect `models/phase5/best.pt`, and prevent side effects on user data, testing is broken down into 7 sequential steps:

```
[Step A: Safe Isolated Unit Tests]
              │
              ▼
[Step B: Backend & API Tests (with Environment Overrides)]
              │
              ▼
[Step C: AI/ML & NLP Validation Tests]
              │
              ▼
[Step D: Async Task Processing & Queue Tests]
              │
              ▼
[Step E: Security & Production Hardening Tests]
              │
              ▼
[Step F: High-Compute End-to-End & Vision Integration Tests]
              │
              ▼
[Step G: Full Regression Suite Verification]
```

---

## 2. Granular Step-by-Step Execution Plan

### Step A — Safe Isolated Unit Tests
**Purpose:** Verify pure unit logic, database models, static frontend assets, and load testing configurations without starting servers or touching live services.

- **Target Modules:**
  - `tests/test_database.py` (4 tests)
  - `tests/test_load_validation.py` (5 tests)
  - `tests/test_ui_redesign.py` (6 tests)
- **Exact Command:**
  ```powershell
  .\.venv\Scripts\python.exe -m pytest tests/test_database.py tests/test_load_validation.py tests/test_ui_redesign.py -v
  ```
- **Required Environment Variables:**
  ```powershell
  $env:FLASK_ENV="development"
  $env:TESTING="True"
  ```
- **Dependencies:** None. Standard python packages.
- **Estimated Execution Time:** ~3–5 seconds.
- **Data Isolation Strategy:** Ephemeral temporary directory via `tempfile.TemporaryDirectory()`; read-only disk reads for UI tests.
- **Expected Outcome:** 15 passing tests (or 1 assertion failure in `test_ui_redesign.py` reflecting recent colgroup changes).
- **Risks & Mitigation:** None. Zero network, zero live DB interaction.

---

### Step B — Backend and API Tests
**Purpose:** Validate claim ingestion, authentication, and document processing endpoints using test-only temporary databases.

- **Target Modules:**
  - `tests/test_auth.py` (11 tests)
  - `tests/test_claims.py` (12 tests)
  - `tests/test_ownership_and_receipt.py` (6 tests)
  - `tests/test_health.py` (4 tests — **MUST BE ISOLATED**)
  - `tests/test_document_processing.py` (13 tests)
- **Exact Command:**
  ```powershell
  # Must override DATABASE_URL and UPLOAD_FOLDER to protect production database from test_health.py
  $env:DATABASE_URL="sqlite:///:memory:"
  $env:DATABASE_PATH="data/test_ephemeral.db"
  $env:UPLOAD_FOLDER="uploads/test_ephemeral"
  .\.venv\Scripts\python.exe -m pytest tests/test_auth.py tests/test_claims.py tests/test_ownership_and_receipt.py tests/test_health.py tests/test_document_processing.py -v
  ```
- **Required Environment Variables:**
  - `DATABASE_URL="sqlite:///:memory:"`
  - `UPLOAD_FOLDER="uploads/test_ephemeral"`
  - `SECRET_KEY="test-secret-key-32chars-minimum-len"`
- **Dependencies:** PyMuPDF, python-docx, reportlab.
- **Estimated Execution Time:** ~10–15 seconds.
- **Data Isolation Strategy:** Temporary directories created in `setUp`; memory DB injected to intercept `test_health.py`'s unparameterized `create_app()`.
- **Expected Outcome:** 46 passing tests.
- **Risks & Mitigation:** If `DATABASE_URL` is omitted, `test_health.py` attaches to `data/claimsense.db`. Strict environment variable enforcement prevents this.

---

### Step C — AI / ML & Corroboration Tests
**Purpose:** Verify NLP narrative parsing, discrepancy detection, and cross-source corroboration algorithms without modifying models or datasets.

- **Target Modules:**
  - `tests/test_phase6_nlp.py` (14 tests)
  - `tests/test_phase7_verification.py` (32 tests)
  - `tests/test_phase7_cross_source_failures.py` (18 tests)
  - `tests/test_replacement_damage_bugfix.py` (15 tests)
- **Exact Command:**
  ```powershell
  .\.venv\Scripts\python.exe -m pytest tests/test_phase6_nlp.py tests/test_phase7_verification.py tests/test_phase7_cross_source_failures.py tests/test_replacement_damage_bugfix.py -v
  ```
- **Required Environment Variables:**
  ```powershell
  $env:TESTING="True"
  $env:FLASK_ENV="development"
  ```
- **Dependencies:** Ultralytics (YOLOv8), NumPy, Pillow.
- **Estimated Execution Time:** ~20–30 seconds.
- **Data Isolation Strategy:** Each test class spins up an isolated SQLite database (`test_phase6.db`, `test_phase7.db`, etc.) and isolated upload directories via `mkdtemp`.
- **Expected Outcome:** 79 passing tests.
- **Risks & Mitigation:** SQLite file lock on Windows if engine is not detached before directory removal. Handled via `ignore_errors=True` in `rmtree`.

---

### Step D — Async Processing & Queue Tests
**Purpose:** Verify asynchronous task enqueuing, stage progression telemetry, worker execution, idempotency, and bug regressions.

- **Target Modules:**
  - `tests/test_phase12_async.py` (11 tests)
  - `tests/test_pipeline_and_ux_fixes.py` (3 tests)
- **Exact Command:**
  ```powershell
  .\.venv\Scripts\python.exe -m pytest tests/test_phase12_async.py tests/test_pipeline_and_ux_fixes.py -v
  ```
- **Required Environment Variables:**
  ```powershell
  $env:TESTING="True"
  $env:QUEUE_BROKER_TYPE="threaded"
  $env:ASYNC_PROCESSING_ENABLED="True"
  ```
- **Dependencies:** Threaded broker, SQLite WAL.
- **Estimated Execution Time:** ~10–15 seconds.
- **Data Isolation Strategy:** In-memory queue (`queue.Queue`), isolated temporary database, isolated background thread execution.
- **Expected Outcome:** 14 passing tests.
- **Risks & Mitigation:** Worker thread timeout. Mitigated by setting `TASK_TIMEOUT_SECONDS=5` in test config.

---

### Step E — Security & Hardening Tests
**Purpose:** Verify CSRF protection, CORS origin validation, rate limiting, production secret enforcement, SQLite WAL mode, and online database backups.

- **Target Modules:**
  - `tests/test_security.py` (8 tests)
  - `tests/test_phase11_production.py` (12 tests)
- **Exact Command:**
  ```powershell
  .\.venv\Scripts\python.exe -m pytest tests/test_security.py tests/test_phase11_production.py -v
  ```
- **Required Environment Variables:**
  ```powershell
  $env:TESTING="True"
  ```
- **Dependencies:** Flask-WTF, Flask-Limiter, reportlab.
- **Estimated Execution Time:** ~12–18 seconds.
- **Data Isolation Strategy:** Dedicated temporary directories for backup simulation; `patch.dict(os.environ)` for security checks with immediate environment restoration.
- **Expected Outcome:** 20 passing tests.
- **Risks & Mitigation:** `importlib.reload(backend.config)` in `test_security.py`. Running Step E in its own command ensures mutated config does not leak to other suites.

---

### Step F — High-Compute End-to-End & Vision Integration Tests
**Purpose:** Execute full 10-stage end-to-end integration and validate YOLOv8 vehicle damage detection.

- **Target Modules:**
  - `tests/test_e2e.py` (13 tests)
  - `tests/test_phase5_vision.py` (30 tests — **PROTECTED / ISOLATED COPY REQUIRED**)
- **Pre-Flight Safety Action:**
  Before executing `test_phase5_vision.py`, create a temporary read-only copy of `data/claimsense.db` into a sandbox location, or point `test_phase5_vision.py` to a test database so the live database is never directly accessed.
- **Exact Command:**
  ```powershell
  .\.venv\Scripts\python.exe -m pytest tests/test_e2e.py tests/test_phase5_vision.py -v
  ```
- **Required Environment Variables:**
  ```powershell
  $env:TESTING="True"
  $env:YOLO_VERBOSE="False"
  ```
- **Dependencies:** PyTorch, TorchVision, Ultralytics, CarDD-300 dataset (`datasets/CarDD_300/`).
- **Estimated Execution Time:** ~35–55 seconds.
- **Data Isolation Strategy:** Deep copy of CarDD test images; isolated temporary database for E2E runs.
- **Expected Outcome:** 42 passing tests, 1 safely skipped test (CUDA hardware check on CPU environment).
- **Risks & Mitigation:** Heavy CPU/RAM usage during YOLO inference. Run sequentially, not in parallel.

---

### Step G — Full Regression Suite Verification
**Purpose:** Final verification of the entire ClaimSense AI test surface across all 18 test modules in a single unified run.

- **Exact Command:**
  ```powershell
  $env:DATABASE_URL="sqlite:///:memory:"
  .\.venv\Scripts\python.exe -m pytest tests/ -q
  ```
- **Estimated Execution Time:** ~90–120 seconds.
- **Expected Outcome:** 216 passed, 1 skipped (217 total).

---

## 3. Strict Execution Policy

> [!CAUTION]
> **No tests were executed during Step 1.**  
> The above plan is documented strictly for future sequential execution after safety validation and authorization.
