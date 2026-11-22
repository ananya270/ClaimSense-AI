# ClaimSense AI — Test Safety Audit & Isolation Assessment

**Audit Phase:** Step 1: Test Discovery, Safety Audit & Testing Baseline  
**Date:** 2026-11-21  
**Inspection Mode:** Strictly Static Inspection-Only (Zero Test Execution)  
**Safety Status:** Audit Complete — High-Risk Tests Identified & Isolated  

---

## 1. Safety Audit Findings & Destructive Operation Search

A comprehensive static analysis was conducted across all 18 test files to detect destructive operations, real data mutations, model alterations, and unisolated environmental couplings.

### 1.1 Database Operations (`data/claimsense.db`)
- **Default Factory Fallback Vulnerability:**
  In `backend/app.py`, calling `create_app()` without arguments defaults to `config_class=Config`. `Config.DATABASE_PATH` points directly to `BASE_DIR / "data" / "claimsense.db"`.
  - **Identified Risk in `tests/test_health.py`:** Line 10 invokes `self.app = create_app()` without passing a test configuration. Executing `test_health.py` unisolated triggers `init_database("sqlite:///data/claimsense.db")` and calls `migrate_existing_claims_from_disk(Path("uploads"))`. This directly attaches to the live production database.
- **Direct Production Database Query in `tests/test_phase5_vision.py`:**
  In line 945, `test_production_database_historical_claim_records_preserved` explicitly connects to `self.repo_root / "data" / "claimsense.db"` to assert historical preservation of claim `CLM-20261116-KCM0`. While read-only in intent, running queries against the live database during test execution violates strict environment isolation.
- **Self-Isolated Test Modules:**
  16 out of 18 test modules correctly configure isolated SQLite databases via `tempfile.TemporaryDirectory` or `tempfile.mkdtemp` (e.g. `test_auth.db`, `test_phase11.db`, `test_phase12.db`), ensuring zero mutation of production records.
- **Engine Leakage on Windows:**
  Several test modules (e.g. `test_document_processing.py`, `test_phase6_nlp.py`, `test_phase7_verification.py`) initialize SQLite engines without calling `backend.database.db.close_engine()` in `tearDownClass`. On Windows, this can leave SQLite file locks active when `shutil.rmtree` attempts directory cleanup.

### 1.2 File System & Upload Operations (`uploads/`, `reports/`)
- **Real Upload Folder Protection:**
  Production uploads reside in `c:\Users\ydvan\Desktop\ClaimSense Ai\ClaimSense-AI\uploads` and reports in `reports/`.
  - In `test_replacement_damage_bugfix.py`, line 207 executes `f.unlink()`. Audit confirms this operates strictly within `self.upload_dir = self.tmp / "uploads"`, an ephemeral temporary directory created in `setUp`. Live uploads are unaffected.
  - In `test_phase11_production.py`, `test_phase12_async.py`, `test_e2e.py`, and `test_pipeline_and_ux_fixes.py`, all upload and report directories are isolated under `tempfile.mkdtemp`.
  - `shutil.rmtree` calls are present in 7 modules (`test_e2e.py`, `test_phase11_production.py`, `test_phase12_async.py`, `test_phase6_nlp.py`, `test_phase7_cross_source_failures.py`, `test_phase7_verification.py`, `test_pipeline_and_ux_fixes.py`). All instances target the ephemeral test directory (`cls.temp_dir` / `self.temp_dir`).

### 1.3 Production AI/ML Model Weights (`models/phase5/best.pt`)
- **Production Checkpoint Verification:**
  - File: `models/phase5/best.pt`
  - SHA-256 Hash: `49630AE8D5C0066D0532A2A38EFEDE809920A6FCCD3EED59A76EB3B65F009390`
- **Model Training / Overwrite Operations:**
  - No test file attempts model retraining, weight overwriting, or automated model promotion.
  - In `tests/test_phase5_vision.py` and `tests/test_e2e.py`, real model inference is executed via `VehicleDamageDetector.get_instance()`. While read-only, loading `best.pt` into PyTorch requires significant RAM and CPU/GPU memory.

### 1.4 Task Queue, Broker & Redis Safety
- **Queue Broker Type:**
  In Phase 12, asynchronous processing supports both `threaded` and `redis` brokers.
  - In `tests/test_phase12_async.py`, `QUEUE_BROKER_TYPE = "threaded"` is hardcoded in `TestConfig`. Tests utilize Python's in-memory `queue.Queue`.
  - No test file connects to production Redis (port 6379), issues `FLUSHDB`, or issues `FLUSHALL`.
  - Worker execution in `test_11_worker_cli_single_run` runs in `--single-run` mode against the in-memory threaded broker, preventing dangling daemon threads.

### 1.5 Global Environment & Module Mutation
- In `tests/test_security.py`, line 57 and 68 perform `importlib.reload(backend.config)` within a `unittest.mock.patch.dict(os.environ)` block to test production secret validation. If interrupted, module reloads can mutate global configuration settings for subsequent test modules running in the same process.

---

## 2. Test Suite Classification Matrix

Each test file has been categorized into one of three safety classifications:
1. **`SAFE TO RUN`** (10 modules): Self-isolated, does not touch live databases, models, or queues.
2. **`SAFE ONLY WITH ISOLATION`** (7 modules): Requires environment variables, mocks, or global engine resets before execution.
3. **`DO NOT RUN YET`** (1 module): Directly touches live production database or loads live production weights without sandboxing.

| Test File Name | Test Purpose | Potential Side Effects | Safety Classification | Reason | Isolation Requirements |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `tests/test_auth.py` | Auth endpoints & password security | Ephemeral SQLite DB in tempdir | **SAFE TO RUN** | Self-contained `setUp`/`tearDown`, isolated DB | None |
| `tests/test_claims.py` | Multipart intake & claim validation | Ephemeral SQLite DB in tempdir | **SAFE TO RUN** | Self-contained `setUp`/`tearDown`, isolated DB | None |
| `tests/test_database.py` | Schema tables, constraints, migrations | Ephemeral SQLite DB in tempdir | **SAFE TO RUN** | Uses isolated `test_claimsense.db` | None |
| `tests/test_document_processing.py` | OCR text extraction & normalization | Ephemeral SQLite DB in tempdir | **SAFE ONLY WITH ISOLATION** | Engine handles left open without class teardown | Call `close_engine()` between test fixtures |
| `tests/test_e2e.py` | Master 10-stage end-to-end integration | Real YOLO inference, temp DB | **SAFE ONLY WITH ISOLATION** | Compute-heavy; invokes live YOLO & PyMuPDF | Verify CPU/RAM availability; isolated tempdir |
| `tests/test_health.py` | Liveness, readiness, metrics APIs | **Touches live `claimsense.db`** | **SAFE ONLY WITH ISOLATION** | `create_app()` defaults to live database path | Must inject `TESTING=True` and temp `DATABASE_URL` |
| `tests/test_load_validation.py` | Load profiles & synthetic fixtures | Isolated server factory | **SAFE TO RUN** | Validates config and synthetic bytes | None |
| `tests/test_ownership_and_receipt.py` | IDOR security & PDF receipt generation | Ephemeral SQLite DB in tempdir | **SAFE TO RUN** | Fully isolated temp directory and test database | None |
| `tests/test_phase11_production.py` | WAL mode, online backups, report freeze | Temporary DB backup & snapshots | **SAFE TO RUN** | Uses dedicated isolated `tempfile.mkdtemp` | None |
| `tests/test_phase12_async.py` | Async task intake, threaded broker | In-memory queue, temp DB | **SAFE TO RUN** | Threaded broker, isolated tempdir, zero Redis impact | None |
| `tests/test_phase5_vision.py` | CarDD YOLOv8 model & historical check | **Touches live `claimsense.db` & `best.pt`** | **DO NOT RUN YET** | Directly accesses `data/claimsense.db` in line 945 | Isolate DB path; mock or protect production DB |
| `tests/test_phase6_nlp.py` | NLP narrative analysis & scoring | Ephemeral SQLite DB in tempdir | **SAFE ONLY WITH ISOLATION** | Lacks `close_engine()` before `rmtree` in teardown | Ensure engine closed before directory removal |
| `tests/test_phase7_cross_source_failures.py`| Boundary failure scenarios A–R | Ephemeral SQLite DB in tempdir | **SAFE ONLY WITH ISOLATION** | Lacks `close_engine()` before `rmtree` in teardown | Ensure engine closed before directory removal |
| `tests/test_phase7_verification.py` | Multi-source corroboration engine | Ephemeral SQLite DB in tempdir | **SAFE ONLY WITH ISOLATION** | Lacks `close_engine()` before `rmtree` in teardown | Ensure engine closed before directory removal |
| `tests/test_pipeline_and_ux_fixes.py` | Regression for async & model fixes | Ephemeral SQLite DB in tempdir | **SAFE TO RUN** | Fully isolated `tempfile.mkdtemp` and clean teardown | None |
| `tests/test_replacement_damage_bugfix.py` | Replacement image damage re-analysis | `f.unlink()` inside tempdir | **SAFE TO RUN** | Unlinks only test synthetic files in temp folder | None |
| `tests/test_security.py` | CSRF, CORS, secrets, XML escaping | Mutates `os.environ` via reload | **SAFE ONLY WITH ISOLATION** | `importlib.reload(backend.config)` modifies state | Run in isolated sub-process or at end of run |
| `tests/test_ui_redesign.py` | Static HTML/CSS/JS frontend audit | Pure static text file inspection | **SAFE TO RUN** | Zero DB, zero network, read-only file inspection | None |

---

## 3. Classification Summary

- **SAFE TO RUN:** 10 Modules (55.6%)
- **SAFE ONLY WITH ISOLATION:** 7 Modules (38.9%)
- **DO NOT RUN YET:** 1 Module (5.5%) — `tests/test_phase5_vision.py`

### Highest-Risk Tests
1. **`tests/test_phase5_vision.py` (Method `test_production_database_historical_claim_records_preserved`)**:
   - Risk: Direct SQLite connection to `data/claimsense.db`.
   - Mitigation: Provide a detached snapshot of `claimsense.db` or patch the database path before executing.
2. **`tests/test_health.py` (`HealthEndpointTestCase.setUp`)**:
   - Risk: Calls unparameterized `create_app()`, opening live `claimsense.db`.
   - Mitigation: Inject test environment variables (`DATABASE_URL=sqlite:///:memory:`) before running.
3. **`tests/test_security.py` (`test_production_startup_failure_with_insecure_secret`)**:
   - Risk: `importlib.reload(backend.config)` alters module-level state.
   - Mitigation: Run in a separate pytest invocation.
