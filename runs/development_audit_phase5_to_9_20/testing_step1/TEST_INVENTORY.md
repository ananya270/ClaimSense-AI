# ClaimSense AI — Test Inventory & Architecture Analysis

**Audit Phase:** Step 1: Test Discovery, Safety Audit & Testing Baseline  
**Date:** 2026-11-21  
**Inspection Mode:** Strictly Static Inspection-Only (Zero Test Execution)  
**Repository:** ClaimSense AI  
**Directory Analyzed:** `tests/`  

---

## 1. Test Frameworks & Testing Tools

The test harness relies on standard Python testing tools and third-party validation libraries:

| Tool / Framework | Version / Source | Role & Usage |
| :--- | :--- | :--- |
| **pytest** | `9.2.0` (installed in `.venv`) | Primary test runner and assertion framework |
| **unittest** | Python 3.14 Standard Library | Core test case structure (`unittest.TestCase`) used across all test files |
| **unittest.mock** | Python 3.14 Standard Library | Function mocking (`patch`, `MagicMock`, `patch.dict`) for auth, email, and time |
| **Locust** | `tests/load/` | Distributed load, concurrency, and performance benchmark framework |
| **PyMuPDF / PIL** | Project Virtualenv | Synthetic test artifact generation (PDF, DOCX, synthetic JPEG buffers) |
| **SQLite WAL** | Built-in / In-Memory | Transient test databases for storage isolation |

### Test Configuration Files
- **`pytest.ini`**: Not present in project root. Pytest executes using default root discovery rules.
- **`pyproject.toml` / `setup.cfg` / `tox.ini`**: Not present in project root.
- **`conftest.py`**: Not present in `tests/` or project root. Fixtures are defined inside `unittest.TestCase.setUp` and `setUpClass` methods within each test module.
- **CI Workflows (`.github/workflows`)**: Not configured in repository.

---

## 2. Test File Inventory & Granular Mapping

Static AST parsing identified **18 test modules** containing **217 distinct test methods**:

| # | Test File Path | Test Classes | Test Count | Primary Category | Target Subsystem / SUT |
| :-: | :--- | :--- | :-: | :--- | :--- |
| 1 | `tests/test_auth.py` | `AuthenticationTestCase` | 11 | Unit / API / Security | User registration, password hashing, session tokens, login/logout |
| 2 | `tests/test_claims.py` | `ClaimSubmissionTestCase` | 12 | API / Unit / Database | Claim multipart upload, ID assignment (`CLM-YYYYMMDD-XXXX`), file storage |
| 3 | `tests/test_database.py` | `DatabaseArchitectureTestCase` | 4 | Database | Relational schema tables, constraints, foreign keys, legacy disk migration |
| 4 | `tests/test_document_processing.py` | `Phase4DocumentProcessingTests` | 13 | OCR / Unit | Text extraction, OCR field extraction, PyMuPDF, python-docx, OCR fallback |
| 5 | `tests/test_e2e.py` | `MasterSystemE2ETestSuite` | 13 | Integration / Regression | Full 10-stage end-to-end pipeline (Auth $\rightarrow$ YOLO $\rightarrow$ OCR $\rightarrow$ NLP $\rightarrow$ Reports) |
| 6 | `tests/test_health.py` | `HealthEndpointTestCase` | 4 | API / Deployment | Health status endpoints (`/api/health`, `/api/health/ready`, `/api/health/metrics`) |
| 7 | `tests/test_load_validation.py` | `LoadTestingValidationTestCase` | 5 | Deployment / Regression | Load test profiles, SLA assertions, synthetic byte fixtures |
| 8 | `tests/test_ownership_and_receipt.py` | `ClaimOwnershipAndReceiptTestCase` | 6 | API / Security / Unit | IDOR tenant scoping, policy lookup, PDF intake receipt generation |
| 9 | `tests/test_phase11_production.py` | `TestPhase11ProductionHardening` | 12 | Deployment / Regression | SQLite WAL pragma, online backups with SHA-256, report snapshot freeze |
| 10 | `tests/test_phase12_async.py` | `TestPhase12AsyncProcessing` | 11 | Async / Broker / Worker | Async claim intake (202 Accepted), threaded queue broker, worker daemon |
| 11 | `tests/test_phase5_vision.py` | `Phase5VisionTestSuite` | 30 | Computer Vision / AI/ML | CarDD-300 dataset integrity, trained YOLOv8 model loading, 6-class detection |
| 12 | `tests/test_phase6_nlp.py` | `TestPhase6NLP` | 14 | NLP / AI/ML | Claimant narrative NLP analysis, entity extraction, timeline generation |
| 13 | `tests/test_phase7_cross_source_failures.py` | `TestPhase7CrossSourceFailures` | 18 | Integration / Regression | Failure scenarios A–R: contradictory repair costs, missing documents, VIN errors |
| 14 | `tests/test_phase7_verification.py` | `TestPhase7CrossSourceVerification` | 32 | Integration / AI/ML | Cross-source corroboration (Policy vs Intake vs OCR vs NLP vs YOLOv8) |
| 15 | `tests/test_pipeline_and_ux_fixes.py` | `TestCriticalBugFixes` | 3 | Regression | Fix validation for async DetachedInstanceError, non-null max_confidence |
| 16 | `tests/test_replacement_damage_bugfix.py` | `VehicleDamageBugfixTestSuite` | 15 | Computer Vision / Regression| Replacement image upload, damage re-analysis, visual comparison tracking |
| 17 | `tests/test_security.py` | `SecurityAndEdgeCaseTestCase` | 8 | Security | Production secret enforcement, CSRF tokens, CORS boundaries, rate limits |
| 18 | `tests/test_ui_redesign.py` | `TestUIUXRedesign` | 6 | Frontend / Unit | HTML DOM elements, modal layouts, CSS styles, translation dictionaries |
| **TOTAL** | **18 Files** | **28 Classes** | **217** | **13 Categories** | **Complete System Surface Area** |

---

## 3. Categorized Test Taxonomy (13 Categories)

### 1. Unit Tests (45 Tests)
- `tests/test_auth.py` (11 tests): Password hashing, session validation, user creation.
- `tests/test_document_processing.py` (13 tests): Low-level text parsing, PDF parser units, DOCX table extractors.
- `tests/test_ownership_and_receipt.py` (6 tests): Policy ID parsing, receipt formatting functions.
- `tests/test_pipeline_and_ux_fixes.py` (3 tests): VehicleDamageAnalysis model default initialization.
- `tests/test_ui_redesign.py` (6 tests): Static frontend template and styling asset verification.
- `tests/test_load_validation.py` (6 tests): Synthetic binary signatures and payload generators.

### 2. API Tests (33 Tests)
- `tests/test_auth.py` (11 tests): `/api/auth/register`, `/api/auth/login`, `/api/auth/me`, `/api/auth/logout`.
- `tests/test_claims.py` (12 tests): `/api/claims` POST and GET endpoints.
- `tests/test_health.py` (4 tests): `/api/health`, `/api/health/ready`, `/api/health/metrics`.
- `tests/test_ownership_and_receipt.py` (6 tests): `/api/claims/<id>/receipt`, `/api/claims/policy/<num>`.

### 3. Integration Tests (63 Tests)
- `tests/test_e2e.py` (13 tests): Complete inter-module pipeline integration.
- `tests/test_phase7_verification.py` (32 tests): Multi-source corroboration combining vision, OCR, and narrative.
- `tests/test_phase7_cross_source_failures.py` (18 tests): Boundary integration and conflicting data detection.

### 4. Database Tests (8 Tests)
- `tests/test_database.py` (4 tests): Table definitions, foreign key cascades, unique constraints, legacy migrations.
- `tests/test_claims.py` (subset): Claim record persistence, status state-machine transitions.

### 5. AI / ML Tests (76 Tests)
- `tests/test_phase5_vision.py` (30 tests): YOLOv8 checkpoint loading, 6-class damage categorization, confidence thresholds.
- `tests/test_phase6_nlp.py` (14 tests): Narrative sentiment, damage entity mapping, consistency evaluation.
- `tests/test_phase7_verification.py` (32 tests): Discrepancy scoring and decision-support algorithms.

### 6. OCR Tests (13 Tests)
- `tests/test_document_processing.py` (13 tests): PyMuPDF digital text extraction, Tesseract OCR fallback, table extraction.

### 7. Computer Vision / YOLO Tests (45 Tests)
- `tests/test_phase5_vision.py` (30 tests): Bounding-box coordinate extraction, IoU evaluation, model architecture checks.
- `tests/test_replacement_damage_bugfix.py` (15 tests): Dynamic damage re-computation upon replacement image submission.

### 8. NLP Tests (14 Tests)
- `tests/test_phase6_nlp.py` (14 tests): Timeline extraction, claimant narrative consistency, impact description parsing.

### 9. Async / Broker / Worker Tests (14 Tests)
- `tests/test_phase12_async.py` (11 tests): Threaded task broker, task queue telemetry, async claim response (202 Accepted), worker polling.
- `tests/test_pipeline_and_ux_fixes.py` (subset): Session isolation across async pipeline steps.

### 10. Frontend Tests (6 Tests)
- `tests/test_ui_redesign.py` (6 tests): Static verification of `index.html`, `style.css`, and `app.js` contracts.

### 11. Security Tests (14 Tests)
- `tests/test_security.py` (8 tests): Secret key enforcement, CSRF defense, CORS origins, rate limiting, XML injection in PDF generation.
- `tests/test_ownership_and_receipt.py` (subset): Multi-tenant ownership and IDOR authorization barriers.

### 12. Regression Tests (42 Tests)
- `tests/test_phase11_production.py` (12 tests): Hardened runtime configuration regressions.
- `tests/test_pipeline_and_ux_fixes.py` (3 tests): Dedicated Phase 12 UX and ORM bug regressions.
- `tests/test_replacement_damage_bugfix.py` (15 tests): Missing evidence handling and replacement upload regressions.
- `tests/test_phase7_cross_source_failures.py` (12 tests): Edge-case corroboration regressions.

### 13. Deployment Tests (21 Tests)
- `tests/test_health.py` (4 tests): Liveness, readiness, and metrics endpoints for orchestrators.
- `tests/test_phase11_production.py` (12 tests): WSGI server compatibility, SQLite backup scripts, JSON logging format.
- `tests/test_load_validation.py` (5 tests): Concurrency profile sanity and SLA bounds.

---

## 4. Ancillary & Load Test Components

Outside of standard unit/integration test suites, the repository includes load and validation harnesses:

1. **`tests/load/`**:
   - `locustfile.py`: Simulates concurrent users submitting claims and querying status.
   - `run_load_test.py`: Standalone benchmarking runner evaluating 10, 25, and 50 concurrent virtual users.
   - `config.py` & `server.py`: Load test configurations and isolated mock server factory.
2. **`scripts/` Test Utilities**:
   - `scripts/execute_gate_p_offline_smoke_test.py`: Controlled shadow smoke test runner.
   - `scripts/test_pii_redaction_logic.py`: License plate and PII redaction test utility.
   - `scripts/run_phase8_smoke_test.py`: Phase 8 smoke test runner.

---

## 5. Summary Statement

- **Total Test Files:** 18
- **Total Test Classes:** 28
- **Total Discovered Tests:** 217
- **Test Frameworks:** Pytest 9.2.0, Unittest, Locust
- **Status:** All files identified and cataloged without running tests.
