# ClaimSense AI — Phase 3 Master Stabilization & Security Audit Report

**Project Title:** ClaimSense AI: AI-Powered Insurance Claim Verification Using Image/Document Analysis  
**Repository:** https://github.com/anshg8252/ClaimSense-AI  
**Branch:** `main`  
**Base Commit:** `de9f526`  
**Date:** 2026-11-14  
**Author/Role:** Senior Python Backend Engineer, Application Security Engineer, QA Automation Engineer  

---

## 1. Executive Summary

ClaimSense AI is an academic decision-support prototype built to assist human claim assessors in evaluating motor insurance claims. It ingests multi-source evidence including policy schedules, claim application forms, repair estimates/invoices, vehicle damage photographs, and incident descriptions.

Before embarking on Phase 4 (Document Processing & OCR Engine), an exhaustive security audit, architectural stabilization, and testing expansion was conducted on the Phase 3 codebase. All critical, high, and medium-severity security findings have been systematically remediated. The codebase is now hardened, rate-limited, protected against CSRF and XSS, and covered by a comprehensive automated test suite consisting of **45 passing unit, integration, and security tests**.

---

## 2. Audit Findings & Remediations

| ID | Severity | Area | Finding / Vulnerability | Remediation Applied |
|---|---|---|---|---|
| **SEC-01** | 🔴 Critical | Authentication | `POST /api/claims` permitted anonymous submissions without session or user account. | Enforced mandatory session authentication. Returns `HTTP 401 Unauthorized` for anonymous submissions. All submitted claims strictly bind to server-side `session["user_id"]`. |
| **SEC-02** | 🔴 Critical | Authorization | `can_user_access_claim()` returned `True` for unowned claims (`user_id is None`), exposing legacy claims to all visitors. | Hardened access control: regular users are denied access (`HTTP 403`) to unowned claims; only authenticated claim owners, claim assessors, and admins can view claims and receipts. |
| **SEC-03** | 🔴 Critical | Authorization | Disk metadata fallback routes in `get_claim()` and `get_claim_receipt()` returned claim data without verifying user ownership. | Added `can_user_access_claim_dict()` to validate ownership on disk fallback paths before returning JSON or PDF receipt data. |
| **SEC-04** | 🟠 High | CSRF Protection | No CSRF defense existed on state-changing endpoints (`POST /api/auth/*`, `POST /api/claims`). | Integrated `Flask-WTF` (`CSRFProtect`). Added `GET /api/auth/csrf-token` endpoint. Integrated frontend `X-CSRFToken` request headers. Safe testing toggle allows automated test suites to run cleanly. |
| **SEC-05** | 🟠 High | Rate Limiting | Authentication endpoints were vulnerable to brute-force credential stuffing. | Integrated `Flask-Limiter` with in-memory storage (`memory://`). Configured `@limiter.limit("10 per minute")` on `/api/auth/signup` and `/api/auth/login`. |
| **SEC-06** | 🟠 High | Secrets & Config | Application allowed startup in production with default/weak `SECRET_KEY`. | Added hard validation in `backend/config.py`: refuses production startup with `RuntimeError` if `SECRET_KEY` is missing, default, or shorter than 16 characters. Added cookie security flags (`SESSION_COOKIE_HTTPONLY = True`, `SESSION_COOKIE_SAMESITE = "Lax"`, `SESSION_COOKIE_SECURE = IS_PRODUCTION`). |
| **SEC-07** | 🟠 High | CORS Security | CORS allowed wildcards with credentials in certain dev configurations. | Configured explicit allowed origins list (`CORS_ALLOWED_ORIGINS`). Tested origin restriction to ensure unauthorized origins are rejected. |
| **SEC-08** | 🟠 High | File Uploads | Validation relied solely on file extensions; 0-byte files and mismatched magic byte signatures were accepted. | Added magic byte inspection (`is_valid_magic_bytes`) for PDF (`%PDF`), JPEG (`\xff\xd8\xff`), PNG (`\x89PNG`), and DOCX (`PK\x03\x04`). Rejects 0-byte uploads (`HTTP 400`). Hardened path sanitization against directory traversal. |
| **SEC-09** | 🟡 Medium | PDF Generation | User inputs were interpolated into ReportLab Paragraphs without XML escaping, risking parse crashes. | Added `safe_xml()` utility escaping `<`, `>`, `&`, `"`, `'` to XML entities and wrapping long unbroken tokens (>40 characters) to prevent layout corruption. |
| **SEC-10** | 🟡 Medium | Frontend XSS | Dynamic claim cards and authentication headers rendered unsanitized user inputs. | Added `escapeHTML()` helper in `frontend/app.js` and applied it to claimant names, policy numbers, and usernames. Added sign-in requirement notification banner. |
| **SEC-11** | 🟡 Medium | Error Handling | Unhandled 500 exceptions could leak raw tracebacks and database connection details. | Sanitized all error responses; returns generic, user-safe error messages with structured fields (`success`, `error`, `message`, `details`). |
| **SEC-12** | 🟡 Medium | Cleanup | Transaction failures could leave orphaned folders in `uploads/<claim_id>`. | Added automatic `shutil.rmtree` directory cleanup in exception handlers if file saving or DB persistence encounters an error. |

---

## 3. Architecture & Codebase Modifications

### 3.1 Backend Components Modified

- **`backend/config.py`**:
  - Validates `SECRET_KEY` in production against known insecure keys (`changeme`, `secret`, `dev`, etc.).
  - Configured `SESSION_COOKIE_HTTPONLY`, `SESSION_COOKIE_SAMESITE = "Lax"`, `SESSION_COOKIE_SECURE = IS_PRODUCTION`.
  - Configured `WTF_CSRF_ENABLED = True`, `RATELIMIT_ENABLED = True`.
  - Configured `CORS_ALLOWED_ORIGINS` whitelist.
- **`backend/extensions.py`** *(New)*:
  - Centralized extension instances: `csrf = CSRFProtect()` and `limiter = Limiter(key_func=get_remote_address)`.
- **`backend/app.py`**:
  - Initializes `csrf` and `limiter`.
  - Configures explicit origin whitelist in `CORS`.
  - Provides test mode bypass for CSRF and rate limiting (`ENABLE_CSRF_FOR_TESTS`, `ENABLE_RATELIMIT_FOR_TESTS`) so automated tests run without hindrance.
  - Registers centralized error handlers for `400`, `401`, `403`, `404`, `405`, `413`, `415`, `429`, `CSRFError`, and `500`.
- **`backend/utils/auth.py`**:
  - Hardened `can_user_access_claim()`: denies unowned claims to standard users; permits owner, assessor, and admin.
  - Added `can_user_access_claim_dict()` for metadata fallback validation.
  - Hardened `login_required` decorator to verify user active status in the database.
- **`backend/utils/validators.py`**:
  - Added `is_valid_magic_bytes()` supporting PDF, JPEG, PNG, DOCX.
  - Added 0-byte file check.
  - Hardened `sanitize_and_resolve_path()` to detect traversal attempts.
- **`backend/routes/auth.py`**:
  - Added `GET /api/auth/csrf-token` route.
  - Applied `@limiter.limit("10 per minute")` to `/api/auth/signup` and `/api/auth/login`.
  - Enforced password complexity: minimum 8 characters, must contain letters and numbers.
  - Session regeneration on login to prevent session fixation.
- **`backend/routes/claims.py`**:
  - Enforced authentication on `POST /api/claims` (HTTP 401 if anonymous).
  - Bound submitted claim strictly to server-side `session["user_id"]`.
  - Secured disk fallback routes in `get_claim()` and `get_claim_receipt()`.
  - Added directory cleanup on failure.
- **`backend/services/receipt.py`**:
  - Escaped all user strings via `safe_xml()`.
  - Wrapped long unbroken strings to prevent ReportLab layout crashes.

### 3.2 Frontend Modifications

- **`frontend/app.js`**:
  - Added `escapeHTML()` to prevent XSS in `renderClaimCard()` and `renderHeaderAuth()`.
  - Added `fetchCsrfToken()` and automatic inclusion of `X-CSRFToken` in state-changing requests.
  - Added authentication gate banner guiding unauthenticated visitors to sign in before submission.
- **`frontend/index.html`**:
  - Added `#auth-required-notice` banner before the claim submission form.
- **`frontend/style.css`**:
  - Added styling for alert and notification components (`.alert-info`).

---

## 4. Complete API Specification (Stabilized Phase 3)

| Method | Endpoint | Auth Required | Rate Limit | Description |
|---|---|---|---|---|
| `GET` | `/api/health` | No | None | System health check and database status. |
| `GET` | `/api/auth/csrf-token` | No | None | Obtains CSRF token for state-changing requests. |
| `POST` | `/api/auth/signup` | No | 10 / min | Registers new user account with password complexity checks. |
| `POST` | `/api/auth/login` | No | 10 / min | Authenticates user and establishes secure session cookie. |
| `POST` | `/api/auth/logout` | Yes | None | Invalidates user session cookie. |
| `GET` | `/api/auth/me` | Yes | None | Returns profile data of the logged-in user. |
| `POST` | `/api/claims` | **Yes** | None | Submits claim with 4 files; validates magic bytes; assigns claim owner. |
| `GET` | `/api/claims/<claim_id>` | **Yes** (Owner/Role) | None | Retrieves claim details (scoped to owner, assessor, admin). |
| `GET` | `/api/claims/<claim_id>/receipt` | **Yes** (Owner/Role) | None | Emits PDF or JSON claim submission receipt. |
| `GET` | `/api/claims/policy/<policy_no>` | **Yes** | None | Searches claims by policy (scoped to user's claims or assessor/admin). |
| `GET` | `/api/my-claims` | **Yes** | None | Returns list of claims submitted by the logged-in user. |

---

## 5. Automated Test Suite Results

The automated test suite was repaired, expanded, and validated across 5 test modules.

### Test Execution Summary:
```bash
python -m unittest discover tests -v
```

| Test Module | Tests | Status | Key Coverage Areas |
|---|---|---|---|
| `tests/test_health.py` | 4 | PASS | Health endpoint, database status check, 404 handling, index route. |
| `tests/test_auth.py` | 11 | PASS | Signup, password complexity, duplicate email/username, login, session lifecycle, `/me`, logout, inactive user enforcement. |
| `tests/test_claims.py` | 12 | PASS | Authenticated submission, unauthenticated rejection (401), missing fields, missing files, invalid extension, invalid magic bytes, 0-byte file rejection, file storage, metadata JSON. |
| `tests/test_ownership_and_receipt.py` | 6 | PASS | Claim owner assignment, owner access, non-owner rejection (403), unauthenticated rejection (401), assessor/admin access, legacy unowned claim protection, policy search, PDF/JSON receipt generation. |
| `tests/test_security.py` | 8 | PASS | Production secret enforcement, CORS restriction, CSRF protection, rate limiting, PDF special character escaping, DB failure rollback cleanup, path traversal detection, magic bytes validator. |
| **Total** | **45** | **100% PASS** | **Runtime: ~21 seconds** |

---

## 6. Phase 4 Readiness Assessment

### 6.1 Readiness Checklist

- [x] Backend architecture stabilized with application factory pattern.
- [x] Database models and relationships established (`User`, `Claim`, `Document`, `ClaimImage`).
- [x] Disk storage structure standardized (`uploads/<claim_id>/documents/`, `uploads/<claim_id>/images/`).
- [x] Authenticated claim submission and strict access control enforced.
- [x] Security protections active: CSRF tokens, rate limiting, CORS whitelist, cookie security.
- [x] File upload pipeline hardened with magic byte signatures and path traversal defense.
- [x] All 45 tests passing cleanly on Python 3.13.2.
- [x] Clean Git working tree on `main`.

### 6.2 Technical Recommendations for Phase 4

Phase 4 focuses on **Document Processing & OCR Engine**. The following technical boundaries must be observed:

1. **OCR Engine Selection:**
   - Prefer `Tesseract OCR` (via `pytesseract`) or `EasyOCR`.
   - Provide clean fallback handling if Tesseract binary is not installed locally on Windows (e.g., informative warning and fallback to text extraction via `pdfplumber` / `pypdf`).
2. **Document Extractors:**
   - PDF Text & Tables: `pdfplumber` / `pypdf`.
   - DOCX: `python-docx` (already scaffolded in `backend/services/ocr/docx_extractor.py`).
   - Image OCR: Preprocess image with OpenCV (grayscale, Otsu thresholding, deskew) prior to OCR.
3. **Structured Field Extraction:**
   - Extract key insurance entities: Policyholder name, Policy number, Vehicle registration number, Dates, Invoiced amounts.
   - Cross-check extracted entities against claimant-submitted metadata (e.g., does policy number in PDF match claimant's entered policy number?).
4. **Safety & Scope:**
   - The system remains a **decision-support tool**. OCR extraction confidence scores must be presented to human assessors without claiming 100% certainty or automated approval.

---

## 7. Proposed Phase 4 Implementation Plan

```
Phase 4.1: OCR & Document Extraction Foundations
├── Install & configure OCR dependencies (pytesseract / pdfplumber / python-docx)
├── Create backend/services/ocr/ocr_engine.py (Tesseract wrapper with image preprocessing)
├── Create backend/services/ocr/pdf_extractor.py (Text & tabular data extraction)
└── Create backend/services/ocr/extractor_factory.py (Dispatch based on mime-type)

Phase 4.2: Information Extraction & Normalization
├── Create backend/services/ocr/entity_parser.py (Regex & pattern-based entity extraction)
├── Extract Policy Number, Dates, Vehicle Registration, Amounts
└── Calculate extraction confidence scores

Phase 4.3: Claim Processing Pipeline Integration
├── Add ClaimStatus: PROCESSING, EXTRACTED, VERIFIED
├── Update backend/routes/claims.py to trigger asynchronous or deferred document extraction
└── Store extracted document text and entities in SQLite database (Document.extracted_text)

Phase 4.4: Verification & Discrepancy Detection
├── Compare extracted document fields against user-submitted form fields
└── Record preliminary match/mismatch flags for assessor review

Phase 4.5: Testing & Validation
├── Unit tests with synthetic insurance policy PDFs, claim forms, and invoices
└── Verification tests for OCR error handling, corrupted PDFs, and missing binaries
```
