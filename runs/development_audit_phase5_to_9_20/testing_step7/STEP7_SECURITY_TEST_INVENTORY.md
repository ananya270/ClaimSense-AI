# ClaimSense AI — Step 7: Security & Regression Test Inventory

**Date:** 2026-11-22  
**Branch:** `main`  
**HEAD Commit:** `c25e2b571dcebe73e76c2ad1b22c6b9971563c9c`  
**Execution Context:** Step 7 Security & Regression Testing (Testing-Only Phase)  

---

## 1. Baseline & Pre-Flight Safety Status

### 1.1 Protected Resources Status
| Resource | Pre-Flight Status / Baseline | Safety Requirement |
| :--- | :--- | :--- |
| **Production Database** (`data/claimsense.db`) | Size: `888,832` bytes<br>Timestamp: `2026-11-22 16:41:42` | Strictly protected. Zero reads, writes, schema migrations, or test connections allowed. |
| **YOLO Model Checkpoint** (`models/phase5/best.pt`) | SHA-256: `49630AE8D5C0066D0532A2A38EFEDE809920A6FCCD3EED59A76EB3B65F009390`<br>Size: `6,472,810` bytes | Read-only. No weights or model files modified. |
| **Async Tasks & Queues** (`Redis :6379`) | Port 6379 inactive. Production workers offline. | No production worker dispatch or redis cluster interaction. |
| **Storage Folders** (`uploads/`, `reports/`) | Retained as production baselines. | All tests must use isolated `tempfile.TemporaryDirectory`. |
| **Approved Frontend Changes** (`frontend/style.css`, `frontend/index.html`) | Unstaged modifications verified intact. | Preserved without revert, overwrite, or modification. |
| **Untouched Frontend Code** (`frontend/app.js`) | Clean and untouched (matches HEAD). | No modifications allowed. |

---

## 2. Safety Audit & Isolation Classification

Every candidate security test has been analyzed for runtime dependencies, state mutation, and isolation requirements:

1. **SAFE TO RUN (Isolated Temporary DB / Fixtures):**
   - Tests in `tests/test_auth.py`: Use in-memory or `tempfile.TemporaryDirectory` with `test_auth.db`.
   - Tests in `tests/test_ownership_and_receipt.py`: Use isolated `tempfile.TemporaryDirectory` with `test_claims.db`.
   - Tests in `tests/test_phase11_production.py`: Use `tempfile.mkdtemp(prefix="claimsense_phase11_test_")`.
   - Tests in `tests/test_phase12_async.py` (test 06): Uses isolated temp test database and mock session.
   - Tests in `tests/test_security.py` (CORS, CSRF, rate-limit, path traversal, magic bytes, PDF XML escaping, DB rollback): Use `tempfile.TemporaryDirectory` and `test_sec.db`.

2. **SAFE WITH ISOLATION (Module-Reload / Environment Mutation):**
   - `tests/test_security.py::SecurityAndEdgeCaseTestCase::test_production_startup_failure_with_insecure_secret`: Mocks `os.environ` (`FLASK_ENV=production`) and reloads `backend.config`. Must run in its own pytest invocation to prevent polluting global module cache for subsequent tests.

3. **UNSAFE / DO NOT RUN (Production State Exposure):**
   - `tests/test_phase5_vision.py::test_production_database_historical_claim_records_preserved` (Line 945): Directly connects to `data/claimsense.db`. **EXCLUDED FROM EXECUTION.**

---

## 3. Test Group Mapping

### Group 1: Authentication & Session Security (11 Tests)
**Target File:** `tests/test_auth.py`

| Test Name | Security Control Under Test | Isolation Mode | Safety Status |
| :--- | :--- | :--- | :--- |
| `test_01_user_signup_and_hash_storage` | Bcrypt password hashing, salt generation, non-plaintext storage | Temporary DB | SAFE TO RUN |
| `test_02_duplicate_signup_rejection` | User enumeration / collision prevention (HTTP 409) | Temporary DB | SAFE TO RUN |
| `test_03_signup_email_validation` | Email regex / RFC validation (HTTP 400 on malformed email) | Temporary DB | SAFE TO RUN |
| `test_04_signup_password_confirmation_mismatch` | Password confirmation mismatch defense (HTTP 400) | Temporary DB | SAFE TO RUN |
| `test_05_signup_password_length_constraint` | Minimum password length policy enforcement (HTTP 400) | Temporary DB | SAFE TO RUN |
| `test_06_signup_password_complexity` | Password complexity policy (letters, numbers, special characters) | Temporary DB | SAFE TO RUN |
| `test_07_login_successful_with_username_or_email` | Flexible credential authentication, session cookie issuance | Temporary DB | SAFE TO RUN |
| `test_08_login_invalid_credentials_returns_401` | Timing-safe credential rejection, generic 401 error message | Temporary DB | SAFE TO RUN |
| `test_09_session_me_authenticated_and_unauthenticated` | Session token validation, unauthenticated rejection (HTTP 401) | Temporary DB | SAFE TO RUN |
| `test_10_logout_clears_session` | Session invalidation, cookie destruction on logout | Temporary DB | SAFE TO RUN |
| `test_11_inactive_user_cannot_login` | Account lockout / inactive user access prohibition (HTTP 403) | Temporary DB | SAFE TO RUN |

---

### Group 2: Authorization, IDOR & Tenant Isolation (7 Tests)
**Target Files:** `tests/test_ownership_and_receipt.py`, `tests/test_phase12_async.py`

| Test Name | Security Control Under Test | Isolation Mode | Safety Status |
| :--- | :--- | :--- | :--- |
| `test_authenticated_submission_assigns_owner` | Automatic tenancy binding on claim submission | Temporary DB | SAFE TO RUN |
| `test_claim_access_boundaries` | Insecure Direct Object Reference (IDOR) prevention, 403 cross-user, 401 unauth, role RBAC (assessor/admin 200) | Temporary DB | SAFE TO RUN |
| `test_legacy_unowned_claim_protection` | Protection of legacy unowned records from unauthorized exposure | Temporary DB | SAFE TO RUN |
| `test_policy_number_search` | Tenancy-restricted policy searching, 401 unauthenticated guard | Temporary DB | SAFE TO RUN |
| `test_my_claims_endpoint` | Data isolation in user claim history (user sees only own records) | Temporary DB | SAFE TO RUN |
| `test_receipt_generation_pdf_and_json` | Receipt authorization boundary, 403 cross-user, 401 unauth, role RBAC | Temporary DB | SAFE TO RUN |
| `test_06_task_status_unauthorized_isolation` | Async task status polling IDOR prevention (403 cross-claimant, 401 anon) | Temporary DB | SAFE TO RUN |

---

### Group 3: CSRF, Request Validation & API Security (4 Tests)
**Target File:** `tests/test_security.py`

| Test Name | Security Control Under Test | Isolation Mode | Safety Status |
| :--- | :--- | :--- | :--- |
| `test_csrf_protection_when_enabled` | Cross-Site Request Forgery token validation on mutating endpoints (400 on missing/invalid token, 201 on valid) | Temporary DB | SAFE TO RUN |
| `test_rate_limiting_enforcement` | Brute-force throttling on auth endpoints (HTTP 429 Too Many Requests) | Temporary DB | SAFE TO RUN |
| `test_db_transaction_failure_cleans_up_upload_directory` | Rollback integrity: Zero orphaned files on disk upon DB commit failure | Temporary DB & Mock | SAFE TO RUN |
| `test_pdf_receipt_special_xml_characters_safety` | PDF generator injection prevention: XML escaping for `<script>`, `&`, `\"`, `'` in ReportLab | Memory / Pure Unit | SAFE TO RUN |

---

### Group 4: CORS & Upload Security (4 Tests)
**Target Files:** `tests/test_security.py`, `tests/test_load_validation.py`

| Test Name | Security Control Under Test | Isolation Mode | Safety Status |
| :--- | :--- | :--- | :--- |
| `test_cors_origin_restriction` | Cross-Origin Resource Sharing whitelist enforcement, rejection of unauthorized origins | Flask Test Client | SAFE TO RUN |
| `test_path_traversal_sanitization` | Directory traversal rejection (`../../etc/passwd`, `..\..\windows\system32`) | Pure Unit | SAFE TO RUN |
| `test_magic_byte_validator_functions` | File header inspection (magic byte validation for PDF, JPEG, PNG, DOCX) preventing file spoofing | Pure Unit | SAFE TO RUN |
| `test_02_synthetic_binary_fixtures` | Binary payload format integrity (PDF header/EOF, JPEG SOI/EOI markers) | Pure Unit | SAFE TO RUN |

---

### Group 5: Configuration & Deployment Security (9 Tests)
**Target Files:** `tests/test_security.py`, `tests/test_phase11_production.py`

| Test Name | Security Control Under Test | Isolation Mode | Safety Status |
| :--- | :--- | :--- | :--- |
| `test_production_startup_failure_with_insecure_secret` | Production refusal on missing/weak SECRET_KEY | Mock Env Reload | SAFE WITH ISOLATION |
| `test_04_request_correlation_id_injection` | Correlation ID injection & propagation (`X-Request-ID`) for audit traceability | Temp DB / Client | SAFE TO RUN |
| `test_05_defensive_security_headers` | Defense-in-depth HTTP headers (`X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, `Referrer-Policy`) | Temp DB / Client | SAFE TO RUN |
| `test_06_sqlite_wal_pragma_configuration` | SQLite security & concurrency pragmas (foreign keys = 1, busy_timeout = 5000ms) | Temp DB / Engine | SAFE TO RUN |
| `test_07_database_online_backup_utility` | SHA-256 verified zero-downtime database backup & integrity verification | Standalone Temp DB | SAFE TO RUN |
| `test_08_structured_json_logging` | Audit log formatting with user_id, request_id, timestamp, structured schema | Unit / Memory | SAFE TO RUN |
| `test_09_report_snapshot_persistence_lifecycle` | Tamper-evident report immutability with SHA-256 verification and immutable storage | Temp DB & Storage | SAFE TO RUN |
| `test_10_claims_freeze_report_api_endpoint` | RBAC authorization on report freezing & snapshot retrieval (`X-Report-Source: persisted-snapshot`) | Temp DB / Client | SAFE TO RUN |
| `test_11_containerization_manifests_validation` | Nginx reverse proxy `client_max_body_size 16M`, non-root container specs | Manifest Files | SAFE TO RUN |

---

### Group 6: Security Regression Suite (8 Selected Tests)
**Target Files:** Cross-cutting across `tests/test_auth.py`, `tests/test_ownership_and_receipt.py`, `tests/test_phase12_async.py`, `tests/test_security.py`

Cross-cutting regression testing to verify that security controls previously touched or adjacent to Steps 2–6 remain intact:
1. `tests/test_auth.py::AuthTestCase::test_01_user_signup_and_hash_storage`
2. `tests/test_auth.py::AuthTestCase::test_07_login_successful_with_username_or_email`
3. `tests/test_auth.py::AuthTestCase::test_08_login_invalid_credentials_returns_401`
4. `tests/test_ownership_and_receipt.py::ClaimOwnershipAndReceiptTestCase::test_claim_access_boundaries`
5. `tests/test_ownership_and_receipt.py::ClaimOwnershipAndReceiptTestCase::test_legacy_unowned_claim_protection`
6. `tests/test_phase12_async.py::TestPhase12AsyncProcessing::test_06_task_status_unauthorized_isolation`
7. `tests/test_security.py::SecurityAndEdgeCaseTestCase::test_pdf_receipt_special_xml_characters_safety`
8. `tests/test_security.py::SecurityAndEdgeCaseTestCase::test_db_transaction_failure_cleans_up_upload_directory`

---

### Group 7: Final Consolidated Security Regression Suite
Consolidated isolated sequential execution of all 35 unique safe security tests to confirm full passing state, zero cross-test interference, and complete security validation.
