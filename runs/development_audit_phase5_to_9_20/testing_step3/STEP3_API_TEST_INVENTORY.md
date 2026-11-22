# ClaimSense AI — Step 3: Backend & API Test Inventory & Safety Assessment

**Audit Phase:** Step 3: Isolated Backend & API Testing  
**Date:** 2026-11-22  
**Target Subsystem:** Backend APIs, Authentication, Claim Ingestion, Async Queue Contracts, Health & Security Infrastructure  
**Inspection Mode:** Comprehensive Pre-Execution Safety Audit & Inventory  

---

## 1. Scope & Objective

The objective of Step 3 is to validate backend functionality, authorization boundaries, claim persistence, asynchronous processing contracts, and deployment/health APIs while strictly enforcing production database and data isolation:
- Zero mutations to `data/claimsense.db`
- Zero access/deletion in `uploads/` and `reports/`
- Zero modification to AI/ML model checkpoints (`models/phase5/best.pt`)
- Zero interaction with production Redis instances or external task brokers
- Strict temporary SQLite database and filesystem isolation for all test fixtures

---

## 2. API Test Selection & Safety Classification Matrix

| # | Candidate Test File | Test Class | Methods | API Endpoints & Functionality Covered | Safety Classification | Isolation Requirements | Group |
| :-: | :--- | :--- | :-: | :--- | :---: | :--- | :-: |
| 1 | `tests/test_auth.py` | `AuthenticationTestCase` | 11 | `/api/auth/signup`<br>`/api/auth/login`<br>`/api/auth/me`<br>`/api/auth/logout`<br>Password hashing & complexity | **SAFE TO RUN** | Ephemeral `tempfile.TemporaryDirectory()`, isolated `test_auth.db`, `close_engine()` in `tearDown` | **Group 1** |
| 2 | `tests/test_ownership_and_receipt.py` | `ClaimOwnershipAndReceiptTestCase` | 6 | `/api/claims/my-claims`<br>`/api/claims/<id>` (IDOR tenant check)<br>`/api/claims/policy/<num>`<br>`/api/claims/<id>/receipt` | **SAFE TO RUN** | Ephemeral `tempfile.TemporaryDirectory()`, isolated `test_claims.db`, `close_engine()` in `tearDown` | **Group 1** |
| 3 | `tests/test_claims.py` | `ClaimSubmissionTestCase` | 12 | `/api/claims` (POST multipart)<br>`/api/claims/<id>` (GET)<br>Magic byte validation<br>Claim ID format (`CLM-YYYYMMDD-XXXX`) | **SAFE TO RUN** | Ephemeral `tempfile.TemporaryDirectory()`, isolated `test.db`, seeded test user, `close_engine()` in `tearDown` | **Group 2** |
| 4 | `tests/test_phase12_async.py` | `TestPhase12AsyncProcessing` | 11 | `/api/claims` (POST async 202 Accepted)<br>`/api/claims?sync=true` (POST fallback 201)<br>`/api/claims/<id>/status`<br>`/api/claims/<id>/retry-task`<br>Threaded queue broker, worker daemon | **SAFE TO RUN** | Ephemeral `tempfile.mkdtemp()`, isolated `test_phase12.db`, in-memory `queue.Queue`, single-run worker mode | **Group 3** |
| 5 | `tests/test_pipeline_and_ux_fixes.py` | `TestCriticalBugFixes` | 3 | Async pipeline execution without `DetachedInstanceError`<br>`VehicleDamageAnalysis` null confidence safety<br>Claimant narrative visibility in `/api/claims/<id>` | **SAFE TO RUN** | Ephemeral `tempfile.mkdtemp()`, isolated `test_fixes.db`, `close_engine()` in `tearDownClass` | **Group 3** |
| 6 | `tests/test_phase11_production.py` | `TestPhase11ProductionHardening` | 12 | `wsgi.py` entrypoint<br>`/api/health/live`<br>`/api/health/ready`<br>`/api/health/metrics`<br>`X-Request-ID` correlation ID<br>Security response headers<br>SQLite WAL pragma<br>Online backup utility<br>`/api/claims/<id>/freeze-report` | **SAFE TO RUN** | Ephemeral `tempfile.mkdtemp()`, isolated `test_phase11.db`, `close_engine()` in `tearDownClass` | **Group 4** |
| 7 | `tests/test_health.py` | `HealthEndpointTestCase` | 4 | `/api/health`<br>`/`<br>`/api/nonexistent` (404) | **SAFE ONLY WITH ISOLATION** | `create_app()` defaults to live database path; **MUST** execute with shell environment overrides: `DATABASE_URL=sqlite:///:memory:`, `DATABASE_PATH=data/test_ephemeral.db`, `UPLOAD_FOLDER=uploads/test_ephemeral` | **Group 4** |
| 8 | `tests/test_security.py` | `SecurityAndEdgeCaseTestCase` | 8 | CSRF protection (`X-CSRFToken`)<br>CORS origin whitelisting<br>Rate limiting (`Flask-Limiter`)<br>Production secret enforcement<br>Path traversal defense<br>PDF XML escaping | **SAFE TO RUN** | Ephemeral `tempfile.TemporaryDirectory()`, isolated `test_sec.db`, `close_engine()` in `tearDown` | **Group 4** |

---

## 3. Excluded Test Suites (Out of Scope for Step 3 API Testing)

| Test File | Reason for Exclusion from Step 3 | Scheduled Step |
| :--- | :--- | :---: |
| `tests/test_database.py` | Database unit schema tests already executed in Step 2 (100% pass) | Step 2 (Complete) |
| `tests/test_load_validation.py` | Load profile tests already executed in Step 2 (100% pass) | Step 2 (Complete) |
| `tests/test_ui_redesign.py` | Frontend DOM & CSS regression tests executed in Step 2 & 2.1 (100% pass) | Step 2 / 2.1 (Complete) |
| `tests/test_document_processing.py` | Low-level OCR & document text parsing units (PyMuPDF/Tesseract) | Step 4 (AI/ML & Doc Processing) |
| `tests/test_phase5_vision.py` | High-risk: line 945 connects to `data/claimsense.db`, executes live YOLOv8 model inference | Step 5 (Vision & Model Validation) |
| `tests/test_phase6_nlp.py` | NLP narrative entity extraction and corroboration algorithms | Step 4 (AI/ML & NLP Validation) |
| `tests/test_phase7_verification.py` | Cross-source multi-modal consistency scoring engine | Step 4 (AI/ML & NLP Validation) |
| `tests/test_phase7_cross_source_failures.py` | Conflict scenarios & synthetic mismatch integration tests | Step 4 (AI/ML & NLP Validation) |
| `tests/test_replacement_damage_bugfix.py` | YOLO replacement damage re-analysis and CV bounding box verification | Step 5 (Vision & Model Validation) |
| `tests/test_e2e.py` | Master 10-stage end-to-end integration test (high CPU/RAM) | Step 6 (E2E Integration) |

---

## 4. Execution Sequence by Group

- **Group 1: Authentication & Authorization (17 Tests)**
  - `tests/test_auth.py` (11 tests)
  - `tests/test_ownership_and_receipt.py` (6 tests)
- **Group 2: Claim API & Validation (12 Tests)**
  - `tests/test_claims.py` (12 tests)
- **Group 3: Async API Contracts & Bug Regressions (14 Tests)**
  - `tests/test_phase12_async.py` (11 tests)
  - `tests/test_pipeline_and_ux_fixes.py` (3 tests)
- **Group 4: Health, Security & Deployment Infrastructure (24 Tests)**
  - `tests/test_phase11_production.py` (12 tests)
  - `tests/test_health.py` (4 tests, with strict environment isolation)
  - `tests/test_security.py` (8 tests)

**Total Planned Tests for Step 3:** 67 tests
