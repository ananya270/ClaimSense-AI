# ClaimSense AI — Step 8: Final Regression Test Inventory

**Date:** 2026-11-22  
**Branch:** `main`  
**HEAD Commit:** `c25e2b571dcebe73e76c2ad1b22c6b9971563c9c`  
**Phase:** Step 8 — Full Isolated Regression Suite (Final Testing Phase)  

---

## 1. Executive Summary & Audit Baseline

Step 8 represents the culmination of the ClaimSense AI testing campaign (Steps 1–7). Its objective is to validate all approved test suites in a consolidated, strictly isolated regression campaign without any code changes, without environment drift, and with complete isolation from production resources.

### 1.1 Protected Resources Baseline
| Resource | Pre-Flight Verified State | Isolation Mandate |
| :--- | :--- | :--- |
| **Production Database** (`data/claimsense.db`) | Size: `888,832` bytes<br>Timestamp: `2026-11-22 16:41:42` | Strictly protected. Zero reads, writes, schema migrations, or test connections allowed. |
| **YOLO Model Checkpoint** (`models/phase5/best.pt`) | SHA-256: `49630AE8D5C0066D0532A2A38EFEDE809920A6FCCD3EED59A76EB3B65F009390`<br>Size: `6,472,810` bytes | Read-only. No weights or model files modified. |
| **Async Broker & Queues** (`Redis :6379`) | Port 6379 inactive. Production workers offline. | Zero real redis connections or background task dispatches. |
| **Storage Folders** (`uploads/`, `reports/`) | Production baselines preserved. | All tests must use isolated `tempfile.TemporaryDirectory`. |
| **Frontend Preserved Files** | `frontend/style.css`<br>`frontend/index.html` | Approved unstaged modifications verified intact. Must not be reverted. |
| **Untouched Frontend Code** | `frontend/app.js` | Strictly clean (matches HEAD commit). |

---

## 2. Test Selection, Exclusions & Safety Classification

### 2.1 Approved Test Selection Across Groups
| Group | Scope / Domain | Test Files | Total Tests | Safety Classification |
| :---: | :--- | :--- | :---: | :---: |
| **1** | Unit & Core Baseline | `test_database.py`<br>`test_load_validation.py`<br>`test_ui_redesign.py` | 15 | **SAFE** |
| **2** | Backend & API Regression | `test_health.py`<br>`test_claims.py`<br>`test_auth.py`<br>`test_ownership_and_receipt.py` | 33 | **SAFE** |
| **3** | AI/ML, NLP & Verification | `test_document_processing.py`<br>`test_phase6_nlp.py`<br>`test_phase7_verification.py`<br>`test_phase7_cross_source_failures.py` | 66 | **SAFE** |
| **4** | Computer Vision Regression | `test_replacement_damage_bugfix.py`<br>`test_phase5_vision.py` *(excluding line 945)* | 44 | **SAFE** *(with 1 excluded)* |
| **5** | Async Worker Regression | `test_phase12_async.py` | 14 | **SAFE** |
| **6** | Security Regression | `test_security.py`<br>`test_phase11_production.py` *(security subset)* | 16 | **SAFE / SAFE WITH ISOLATION** |
| **7** | Final Consolidated Suite | All approved compatible test suites | Consolidated | **SAFE SEQUENTIAL** |

### 2.2 Excluded Tests (DO NOT RUN)
| Test Location | Test Function | Exclusion Justification |
| :--- | :--- | :--- |
| `tests/test_phase5_vision.py` (Line 945) | `test_production_database_historical_claim_records_preserved` | **CRITICAL SAFETY VIOLATION:** Directly opens a SQLite connection to `data/claimsense.db` and queries production claim records. Must be strictly excluded via pytest filter (`-k "not test_production_database_historical_claim_records_preserved"`). |

### 2.3 Isolated Subprocess Requirement
| Test Location | Test Function | Isolation Requirement |
| :--- | :--- | :--- |
| `tests/test_security.py` (Line 49) | `test_production_startup_failure_with_insecure_secret` | **ENVIRONMENT ISOLATION:** Mocks `FLASK_ENV=production` and calls `importlib.reload(backend.config)`. Must be executed in its own isolated process to prevent polluting global config state for other test suites. |

---

## 3. Detailed Test Group Mapping

### Group 1: Unit & Core Baseline (15 Tests)
- **`tests/test_database.py` (5 tests):**
  - `test_init_database_creates_tables`: Validates SQLAlchemy table creation in temp SQLite.
  - `test_user_model_password_hashing`: Validates bcrypt hashing & verification.
  - `test_claim_and_document_relationships`: Validates claim-to-document cascading foreign keys.
  - `test_analysis_result_serialization`: Validates JSON serialization of verification results.
  - `test_db_session_context_manager`: Validates session rollback on exception.
- **`tests/test_load_validation.py` (5 tests):**
  - `test_01_load_config_and_sla_definitions`: Validates SLA configs (10, 25, 50 users).
  - `test_02_synthetic_binary_fixtures`: Validates magic bytes for synthetic PDF/JPEG test files.
  - `test_03_claim_payload_generator`: Validates deterministic payload generator.
  - `test_04_isolated_database_seeding`: Validates isolated seeding in temp SQLite.
  - `test_05_load_test_app_factory_and_journal_mode`: Validates temp test server factory & WAL pragmas.
- **`tests/test_ui_redesign.py` (5 tests):**
  - `test_html_contains_split_pane_structure`: Validates dual-pane layout in `frontend/index.html`.
  - `test_css_contains_glassmorphism_tokens`: Validates CSS variables and blur filters.
  - `test_css_responsive_breakpoints`: Validates `@media (max-width: 900px)` mobile layout.
  - `test_cross_source_table_markup`: Validates table markup for verification badges.
  - `test_badge_overlap_fix_preserved`: Validates UI regression fix from Step 2.1.

### Group 2: Backend & API Regression (33 Tests)
- **`tests/test_health.py` (2 tests):** Basic health & ping endpoints.
- **`tests/test_claims.py` (10 tests):** Claim creation, file uploads, missing field rejections (400), claim retrieval, status transitions, PDF receipt endpoints.
- **`tests/test_auth.py` (11 tests):** User registration, password complexity, duplicate rejections (409), login, cookie issuance, logout, inactive user lockout (403).
- **`tests/test_ownership_and_receipt.py` (10 tests):** Claim ownership binding, IDOR access controls (403/401/200 RBAC), policy search boundaries, my-claims query isolation, PDF receipt access controls.

### Group 3: AI/ML & Verification Regression (66 Tests)
- **`tests/test_document_processing.py` (17 tests):** OCR text extraction, regex entity extraction (dates, amounts, policy numbers), corrupt document handling, bounding box coordinate parsing.
- **`tests/test_phase6_nlp.py` (15 tests):** RoBERTa/Transformers sentiment, text classification, accident narrative semantic extraction, inconsistency detection.
- **`tests/test_phase7_verification.py` (19 tests):** Cross-source consistency evaluation (repair estimate vs claim form vs policy schedule), discrepancy scoring, fraud indicator computation.
- **`tests/test_phase7_cross_source_failures.py` (15 tests):** Edge case failure modes, corrupt cross-source documents, conflicting timestamps, vehicle number mismatch flagging.

### Group 4: Computer Vision Regression (44 Tests)
- **`tests/test_replacement_damage_bugfix.py` (15 tests):** Replacement vs repair decision engine, damage severity thresholds, edge case part matching.
- **`tests/test_phase5_vision.py` (29 approved tests, 1 excluded):** YOLO inference wrappers, bounding box IoU calculation, multi-damage detection, image format validation, resolution checks.

### Group 5: Async Worker Regression (14 Tests)
- **`tests/test_phase12_async.py` (14 tests across 5 groups):**
  - Task lifecycle & stage transitions (`ProcessingTask` ORM)
  - Duplicate task enqueue prevention & idempotency
  - HTTP 202 Accepted multipart submission
  - HTTP 201 Created synchronous fallback (`?sync=true`)
  - Status polling endpoint (`GET /api/claims/<id>/status`)
  - Cross-tenant status isolation (IDOR 403/401)
  - Task retry endpoint (`POST /retry-task`)
  - Error capture & dead-letter queue routing
  - In-memory fallback worker execution
  - Thread worker lifecycle & recovery

### Group 6: Security Regression (16 Tests)
- **`tests/test_security.py` (8 tests):**
  - `test_production_startup_failure_with_insecure_secret` (Isolated)
  - `test_cors_origin_restriction`
  - `test_csrf_protection_when_enabled`
  - `test_rate_limiting_enforcement`
  - `test_pdf_receipt_special_xml_characters_safety`
  - `test_db_transaction_failure_cleans_up_upload_directory`
  - `test_path_traversal_sanitization`
  - `test_magic_byte_validator_functions`
- **`tests/test_phase11_production.py` (8 security tests):**
  - Correlation ID propagation (`X-Request-ID`)
  - Defensive security headers (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`)
  - SQLite WAL pragmas (`busy_timeout=5000`, `foreign_keys=1`)
  - Database online backup & SHA-256 verification
  - Structured JSON audit logging
  - Tamper-evident immutable PDF report snapshots
  - Role-based report freeze & download authorization
  - Containerization & Nginx proxy security manifests

---

## 4. Execution Plan & Sequential Order

```
[Phase 0: Pre-flight Baseline Verification] (Complete)
      │
      ▼
[Group 1: Unit & Core Baseline] (15 tests)
      │
      ▼
[Group 2: Backend & API Regression] (33 tests)
      │
      ▼
[Group 3: AI/ML & Verification Regression] (66 tests)
      │
      ▼
[Group 4: Computer Vision Regression] (44 tests, excluding line 945)
      │
      ▼
[Group 5: Async Worker Regression] (14 tests)
      │
      ▼
[Group 6: Security Regression] (16 tests: 1 isolated + 15 standard)
      │
      ▼
[Group 7: Final Consolidated Sequential Suite] (All approved compatible suites)
      │
      ▼
[Phase 6 & 7: Final Safety Verification & Audit Reports]
```
