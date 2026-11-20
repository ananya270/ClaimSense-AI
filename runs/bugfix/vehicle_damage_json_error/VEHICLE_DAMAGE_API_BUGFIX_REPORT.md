# ClaimSense AI — Bugfix Verification Report
## Vehicle Replacement Image Upload → YOLOv8 Damage Detection → JSON Parsing Error Resolution

**Audit Date:** 2026-11-20  
**Status:** FIXED AND VERIFIED  
**Component Scope:** Flask Claims API, Computer Vision Service (CarDD YOLOv8n), Frontend SPA Response Parsing, Replacement Vehicle Photograph Pipeline  

---

### 1. Original Bug Description & Symptoms

When a claimant or assessor conducted a Policy Claim Lookup, opened the **Claim Record & Algorithmic Verification Details** modal, uploaded or submitted a replacement vehicle accident photograph, and clicked **"Analyze Vehicle Damage"**, the frontend exhibited the following error in the AI inspection panel:

```text
Error: Unexpected token '<', "<!doctype "... is not valid JSON
```

#### Observed Symptoms
1. **Frontend Crash:** The vehicle damage inspection section failed to render detected bounding boxes and instead rendered a raw JavaScript `SyntaxError` banner.
2. **Missing Annotated Visualization:** While the original vehicle photo loaded, the AI Annotated Damage (YOLOv8) visualization frame remained blank with the placeholder intact.
3. **Underlying Database Integrity Failure:** On subsequent analysis execution, SQLite raised an integrity violation:
   ```text
   (sqlite3.IntegrityError) NOT NULL constraint failed: vehicle_damage_analyses.max_confidence
   ```
4. **Disjointed Replacement Flow:** When opening claim details via Policy Lookup rather than wizard submission, the active claim context was unlinked, and no inline replacement photo upload existed in the modal.

---

### 2. Exact Root Cause Analysis

A multi-layered root cause across backend and frontend layers triggered this failure:

1. **Frontend Unhandled Non-JSON Response Parser:**
   In `frontend/app.js`, `btnAnalyzeDamage.onclick` unconditionally executed `const anData = await anRes.json();` without checking `anRes.ok` or inspecting `anRes.headers.get("content-type")`. When an unhandled error, proxy gateway error, dev-server routing fallback (e.g., Live Server port 5500 serving `index.html`), or redirect occurred, the browser received an HTML document starting with `<!doctype html>`. Invoking `response.json()` on HTML syntax immediately threw `SyntaxError: Unexpected token '<', "<!doctype "... is not valid JSON`.

2. **SQLite Schema / ORM Column Mismatch (`max_confidence` NOT NULL Constraint):**
   In `backend/services/vision/service.py`, `process_claim_damage_detection` inserts an initial `in-flight` record into `vehicle_damage_analyses` before commencing YOLOv8 inference. While the Python model definition had `max_confidence = Column(Float, nullable=True)`, the actual persistent production database schema (`data/claimsense.db`) enforced strict `NOT NULL` constraints on legacy columns:
   - `max_confidence` (NOT NULL)
   - `total_damages_detected` (NOT NULL)
   - `average_confidence` (NOT NULL)
   - `inference_time_ms` (NOT NULL)
   - `original_image_path` (NOT NULL)
   Because `active_rec` omitted `max_confidence` and `total_damages_detected`, SQLite aborted the transaction with `IntegrityError: NOT NULL constraint failed: vehicle_damage_analyses.max_confidence`.

3. **Missing `@csrf.exempt` on Replacement Upload Route:**
   The multipart endpoint `@claims_bp.route("/claims/<claim_id>/replace-image", methods=["POST"])` lacked `@csrf.exempt`. Unlike `/analyze-damage`, fetch requests from external scripts or unauthenticated sessions could trigger CSRF rejections resulting in non-JSON responses.

4. **Missing Inline Modal Replacement Component:**
   In `frontend/index.html` and `app.js`, the replacement image upload form was isolated inside the initial submission success view (`#submission-success-card`). When a user opened historical claims from **Policy Claim Lookup**, there was no mechanism inside `#modal-claim-details` to upload a replacement photo, and `currentActiveClaimId` was never synchronized upon opening the modal.

---

### 3. Failing Endpoints & HTTP Status Matrix

| Endpoint | Method | Previous Failure Mode | Fixed Status & Content-Type |
| :--- | :--- | :--- | :--- |
| `/api/claims/<id>/analyze-damage` | `POST` | `500 Internal Server Error` (IntegrityError) / `HTML` | `200 OK` (`application/json`) with detections |
| `/api/claims/<id>/replace-image` | `POST` | `400 CSRF Validation Failed` or silent unhandled response | `200 OK` (`application/json`) with validation status |
| `/api/claims/<id>/replace-image` (invalid) | `POST` | Inconsistent validation handling | `400 Bad Request` (`requires_replacement: true`) |
| `/api/claims/<id>/annotated-image` | `GET` | Missing prioritized lookup for replacement annotated files | `200 OK` (`image/jpeg`) streamed directly |
| `/api/claims/<id>/damage-history` | `GET` | Handled properly | `200 OK` (`application/json`) with analysis runs |

---

### 4. Technical Resolution & Architecture Changes

#### A. Backend Changes
1. **`backend/services/vision/service.py`:**
   - Populated all required fields in the initial in-flight `VehicleDamageAnalysis` record (`max_confidence=0.0`, `total_damages_detected=0`, `average_confidence=0.0`, `inference_time_ms=0.0`, `damage_categories="[]"`, `detected_categories="[]"`).
   - Ensured `process_claim_damage_detection` explicitly prioritizes `image_type="REPLACEMENT_VEHICLE_ACCIDENT"` over original flagged graphics.
2. **`backend/routes/claims.py`:**
   - Decorated `replace_claim_image` with `@csrf.exempt`.
   - Added validation check to reject synthetic graphics/non-vehicle images uploaded as replacements with `400 Bad Request` and forensic reason (`requires_replacement: true`).
   - Hardened `analyze_claim_vehicle_damage` to explicitly prioritize replacement images and wrapped pipeline execution in a structured JSON error handler.
   - Enhanced `get_claim_evidence_file` to support `file_type="replacement_image"` and prioritized replacement photos in standard `image` queries.
   - Enhanced `get_claim_annotated_image` to discover `annotated_replacement_vehicle_image_*` files.
3. **`backend/app.py`:**
   - Hardened global error handling with `@app.errorhandler(Exception)` ensuring all unhandled server exceptions, Werkzeug HTTP errors, and routing faults always emit valid `application/json` payloads, preventing raw HTML leakage.
4. **`backend/database/models.py`:**
   - Added explicit column defaults (`default=0.0`, `default="[]"`) to `VehicleDamageAnalysis` columns to guarantee backward compatibility with existing SQLite schemas.

#### B. Frontend Changes
1. **`frontend/app.js` (`safeFetchJson` & `getApiUrl`):**
   - Implemented `safeFetchJson(endpoint, options)`: Inspects HTTP status and `Content-Type`. Safely parses JSON when `application/json` is returned. If HTML or plaintext is returned, extracts `<title>` and status code without executing `response.json()`, entirely preventing JSON parsing errors.
   - Implemented `getApiUrl(endpoint)`: Detects if running on alternative dev servers (e.g., Live Server port 5500) and automatically redirects API traffic to `http://127.0.0.1:5001`.
   - Updated `openClaimDetailsModal(claimId)` to immediately set `currentActiveClaimId = claimId`.
   - Wired up `#btn-toggle-replace-modal` and `#modal-form-replace-image` directly inside `#modal-damage-section`.
   - Replaced fragile `anRes.json()` with `safeFetchJson` in `#btn-analyze-damage`. If `requires_replacement` is true, smoothly reveals the replacement upload box and highlights the invalid graphic badge.
2. **`frontend/index.html`:**
   - Added `#modal-replace-container` and `#modal-form-replace-image` inside the Claim Details modal.
   - Added `📷 Replace Photo` action button in `#modal-damage-section`.
3. **`frontend/style.css`:**
   - Added responsive, dark enterprise styling for `.replace-image-box`, `.replace-image-header`, `.replace-image-form`, and modal controls.

---

### 5. API Response Contracts

#### POST `/api/claims/<claim_id>/analyze-damage`
**Success (200 OK):**
```json
{
  "success": true,
  "claim_id": "CLM-20261119-7BSU",
  "analysis": {
    "id": 42,
    "claim_id": "CLM-20261119-7BSU",
    "model_name": "YOLOv8n-CarDD",
    "total_detections": 9,
    "damage_categories": ["dent", "glass shatter", "lamp broken", "scratch", "tire flat"],
    "highest_confidence": 0.8844,
    "average_confidence": 0.6215,
    "analysis_status": "completed",
    "inference_time_ms": 3832.98,
    "detections": [...]
  }
}
```

**Rejection for Flagged / Synthetic Evidence (400 Bad Request):**
```json
{
  "success": false,
  "error": "Invalid Vehicle Evidence",
  "message": "Uploaded file 'graphic.jpg' is flagged as invalid_graphic (Synthetic graphic / policy document card detected...).",
  "validation": {
    "is_valid_vehicle_photo": false,
    "status": "invalid_graphic",
    "reason": "Uniform color distribution..."
  },
  "requires_replacement": true
}
```

---

### 6. Automated Regression & Test Evidence

#### Dedicated 15-Point Regression Test Suite (`tests/test_replacement_damage_bugfix.py`)
All 15 targeted test scenarios passed with 100% success in 21.2s:

| # | Test Scenario | Method / Endpoint | Status Code | Result |
| :---: | :--- | :--- | :---: | :---: |
| 1 | Missing / Invalid Claim ID format | `POST /api/claims/INVALID/analyze-damage` | `400` | PASS |
| 2 | Nonexistent Claim ID | `POST /api/claims/CLM-20261120-9999/analyze-damage` | `404` | PASS |
| 3 | Unauthenticated access without session | `POST /api/claims/<id>/analyze-damage` | `401` | PASS |
| 4 | Unauthorized user access isolation | `POST /api/claims/<id>/replace-image` (User B) | `403` | PASS |
| 5 | Claim with missing vehicle photograph on disk | `POST /api/claims/<id>/analyze-damage` | `400` | PASS |
| 6 | Synthetic graphic rejected with `requires_replacement` | `POST /api/claims/<id>/analyze-damage` | `400` | PASS |
| 7 | Authentic replacement image upload | `POST /api/claims/<id>/replace-image` | `200` | PASS |
| 8 | Synthetic image uploaded as replacement rejected | `POST /api/claims/<id>/replace-image` | `400` | PASS |
| 9 | Successful damage detection on replacement image | `POST /api/claims/<id>/analyze-damage` | `200` | PASS |
| 10 | Verified replacement image analyzed (not original) | SQLite `vehicle_damage_analyses` audit | `200` | PASS |
| 11 | Original evidence file preserved on disk | File existence check on disk | `PASS` | PASS |
| 12 | Original evidence record preserved in database | SQLite `claim_images` audit (2 records) | `PASS` | PASS |
| 13 | Annotated image streaming endpoint | `GET /api/claims/<id>/annotated-image` | `200` (JPEG) | PASS |
| 14 | Damage history endpoint returns all runs | `GET /api/claims/<id>/damage-history` | `200` | PASS |
| 15 | Strict JSON content type enforcement across APIs | Content-Type header validation | `application/json` | PASS |

#### Full Repository Test Suite
```text
Ran 173 tests in 108.709s
OK (skipped=1)
```

---

### 7. Production Model Integrity Verification

Baseline cryptographic SHA-256 hashes recorded before and after execution:

- **YOLOv8 Production Model Checkpoint (`models/phase5/best.pt`):**
  - Expected: `49630ae8d5c0066d0532a2a38efede809920a6fccd3eed59a76eb3b65f009390`
  - Measured: `49630ae8d5c0066d0532a2a38efede809920a6fccd3eed59a76eb3b65f009390`
  - **Verdict: UNCHANGED & PRESERVED**

---

### 8. Final Audit Status

VEHICLE DAMAGE DETECTION BUGFIX: FIXED AND VERIFIED — PRODUCTION MODEL AND DATABASE PRESERVED
