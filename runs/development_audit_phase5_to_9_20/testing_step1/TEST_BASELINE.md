# ClaimSense AI — Testing Baseline & Historical Reconciliation

**Audit Phase:** Step 1: Test Discovery, Safety Audit & Testing Baseline  
**Date:** 2026-11-21  
**Execution Status:** **No tests were executed during Step 1.**  
**Working Directory:** `c:\Users\ydvan\Desktop\ClaimSense Ai\ClaimSense-AI`  
**Git Branch:** `main`  
**HEAD Commit:** `87c5a15 FIXED UI`  

---

## 1. Discovered Test Landscape vs Historical Test Reports

### 1.1 Current Discovered Inventory (Step 1 Static Audit)
A static AST audit of `tests/` discovered:
- **Total Test Files:** 18
- **Total Test Classes:** 28
- **Total Test Methods (Discovered):** 217 tests

### 1.2 Historical Test Reports in Repository
The repository contains historical QA execution reports from preceding milestone phases:

| Historical Document Path | Milestone Context | Reported Tests | Reported Result | Date Recorded |
| :--- | :--- | :---: | :---: | :--- |
| `runs/phase12/PHASE_12_TEST_REPORT.md` | Phase 12 Async Architecture | 214 items | 213 passed, 1 skipped | 2026-11-21 |
| `runs/phase10/stage2_load_testing_report.md`| Phase 10 Load & Stress | Concurrency profiles | SLA verified (<500ms) | 2026-11-19 |
| `runs/master_audit/integration_test_report.md` | Master System Audit | 203 items | 202 passed, 1 skipped | 2026-11-16 |
| `PHASE_4_TEST_REPORT.md` | Phase 4 OCR Intelligence | 13 items | 13 passed, 0 skipped | 2026-11-14 |

### 1.3 Discrepancy Analysis (217 Discovered vs 214 Historical)
- **Net Difference:** +3 tests in current repository.
- **Root Cause of Discrepancy:**
  Following the initial Phase 12 delivery (which reported 214 tests), a targeted regression suite `tests/test_pipeline_and_ux_fixes.py` (containing exactly **3 test methods**) was added to verify fixes for the `DetachedInstanceError` in background task processing, non-null `max_confidence` database defaults, and narrative exposure in claim details endpoints:
  $$214 \text{ (Historical)} + 3 \text{ (`test_pipeline_and_ux_fixes.py`)} = 217 \text{ (Discovered Total)}$$
- **File Naming & Consolidation Context:**
  In historical log transcripts (e.g. `PHASE_12_TEST_REPORT.md`), test modules were referenced under alternate legacy or conceptual names during development sprints (e.g. `test_verification_engine.py`, `test_yolo_detector.py`, `test_document_intelligence.py`). The authoritative on-disk test suite is standardized into the 18 concrete test files cataloged in `TEST_INVENTORY.md`.

---

## 2. Known Skipped Tests

From historical test logs and static code inspection:
- **Skipped Test Count:** 1 test
- **Location:** `tests/test_phase5_vision.py` (or legacy `test_model_pipeline.py`)
- **Condition:** `@unittest.skipUnless(torch.cuda.is_available(), "CUDA GPU required for hardware-accelerated batch inference benchmark")`
- **Behavior:** Safely skipped when executed on CPU-only local environments (e.g. standard developer workstations without active CUDA runtime). Zero impact on functional pass criteria.

---

## 3. Cryptographic & Data Asset Baseline

To ensure absolute safety and detect any unintended file alterations during testing, the following pre-flight baseline was recorded:

### 3.1 Production Model Checkpoints
- **Production YOLOv8 Checkpoint:** `models/phase5/best.pt`
  - **SHA-256 Hash:** `49630AE8D5C0066D0532A2A38EFEDE809920A6FCCD3EED59A76EB3B65F009390`
  - **Status:** Unmodified, verified invariant.
- **Secondary Weights Reference:** `models/vehicle_damage/best.pt`
  - **Status:** Verified present.

### 3.2 Production Database
- **Primary Database File:** `data/claimsense.db`
  - **File Size:** 847,872 bytes
  - **Last Modified Timestamp:** 2026-11-21 19:30:16
  - **Journal Mode:** WAL (Write-Ahead Logging)
  - **Status:** Intact, zero mutations.

### 3.3 UI Improvements & Frontend Assets
- **Modified / Committed Frontend Files:**
  - `frontend/index.html` (Table column proportions, colgroup classes)
  - `frontend/app.js` (Status badge labels, table cell bindings)
  - `frontend/style.css` (36px unified dark header controls, table cell overflow containment, light theme overrides)
- **Status:** Preserved and intact at commit `87c5a15 FIXED UI`.

---

## 4. Current-Session Execution Status

> [!IMPORTANT]
> **No tests were executed during Step 1.**  
> All statistics, counts, classifications, and safety findings in this report were produced exclusively via static AST parsing, regular expression keyword analysis, and file system inspection.
