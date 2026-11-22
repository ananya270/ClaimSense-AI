# ClaimSense AI — Step 5: Computer Vision & Replacement Damage Test Inventory

**Audit Phase:** Step 5: Computer Vision & Replacement Damage Testing  
**Date:** 2026-11-22  
**Target Scope:** Computer Vision, YOLOv8 Damage Detection, OpenCV Fallback, CarDD-300 Dataset, Replacement Photo Workflows, PDF Page 5 Visual Reports  
**Inspection Mode:** Comprehensive Pre-Execution Safety Audit & Inventory  

---

## 1. Scope & Objective

Step 5 evaluates the Computer Vision and damage detection subsystems:
1. **Replacement Image Workflow & Regression (`tests/test_replacement_damage_bugfix.py`):**
   15 test cases covering authentic vehicle image validation, synthetic graphic rejection, replacement damage re-detection, disk/database history preservation, and JSON content-type integrity.
2. **Phase 5 Vision Test Suite (`tests/test_phase5_vision.py`):**
   30 test cases covering YOLOv8 model loading, CarDD dataset validation, spatial region quadrant calculations, annotated image generation, OpenCV fallback pipelines, CLAHE preprocessing, multi-threaded worker concurrency, and Page 5 visual reports.

---

## 2. Safety Audit & Critical Hazard Assessment

### 2.1 Critical Hazard: `test_kcm0_history_and_integrity_preserved` (Line 941–969)
- **Hazard Mechanism:**
  ```python
  prod_db_path = self.repo_root / "data" / "claimsense.db"
  prod_engine = create_engine(f"sqlite:///{prod_db_path}")
  ProdSession = sessionmaker(bind=prod_engine)
  with ProdSession() as prod_db:
      kcm0_claim = prod_db.query(Claim).filter_by(claim_id="CLM-20261116-KCM0").first()
  ```
- **Risk Assessment:**
  This test explicitly hardcodes a direct path to the live production database (`data/claimsense.db`). It bypasses the test suite's ephemeral database configuration and attempts a direct SQLite connection against production records.
- **Enforced Safety Protocol:**
  In strict adherence to the safety mandate (**DO NOT run this test against production resources**; **If reliable isolation cannot be guaranteed for a test, DO NOT RUN THAT TEST**), `test_kcm0_history_and_integrity_preserved` is classified as **DO NOT RUN** and explicitly excluded from execution via pytest deselect filters (`-k "not test_kcm0_history_and_integrity_preserved"`).

### 2.2 Safe Self-Isolated Tests (44 Tests)
- All 15 tests in `tests/test_replacement_damage_bugfix.py` utilize per-test `tempfile.TemporaryDirectory()`, custom `TestCfg` with ephemeral `test_bugfix.db`, and clean `tearDown()` directory removal.
- The remaining 29 tests in `tests/test_phase5_vision.py` utilize per-test `tempfile.TemporaryDirectory()`, custom `TestCfg` with ephemeral `test_phase5.db`, and clean `tearDown()` directory removal.
- CarDD test image `datasets/CarDD_300/test/images/000023.jpg` is accessed read-only.
- YOLOv8 model weights `models/vehicle_damage/best.pt` (`models/phase5/best.pt`) are loaded strictly in read-only inference mode.

---

## 3. Test Selection & Safety Classification Matrix

| # | Test File | Test Class | Methods | Tested Functionality | Safety Classification | Execution Status | Group |
| :-: | :--- | :--- | :-: | :--- | :---: | :---: | :-: |
| 1 | `tests/test_replacement_damage_bugfix.py` | `VehicleDamageBugfixTestSuite` | 15 | TC 1–15: Claim ID validation, auth/ownership checks, missing photo handling, synthetic graphic rejection, authentic replacement photo upload, YOLOv8 damage detection, annotated image retrieval, disk & DB audit preservation | **SAFE TO RUN** | **APPROVED FOR EXECUTION** | **Group 1** |
| 2 | `tests/test_phase5_vision.py` | `Phase5VisionTestSuite` | 29 | YOLOv8 checkpoint loading, 6 CarDD damage classes, spatial regions, image annotation, OpenCV fallback, CLAHE enhancement, concurrent worker thread safety, PDF Page 5 damage visual report | **SAFE TO RUN** | **APPROVED FOR EXECUTION** | **Group 2** |
| 3 | `tests/test_phase5_vision.py` | `Phase5VisionTestSuite` | 1 | `test_kcm0_history_and_integrity_preserved` (Line 941–969): Direct connection to live `data/claimsense.db` | **DO NOT RUN** | **EXCLUDED (BLOCKED BY SAFETY AUDIT)** | N/A |

**Total Inventory:** 45 tests across 2 modules.  
**Approved for Safe Execution:** 44 tests.  
**Blocked & Excluded:** 1 test (`test_kcm0_history_and_integrity_preserved`).

---

## 4. Phased Execution Plan

1. **Group 1 Execution:**
   - Command: `.\.venv\Scripts\python.exe -m pytest tests/test_replacement_damage_bugfix.py -v`
   - Scope: 15 tests
2. **Group 2 Execution:**
   - Command: `.\.venv\Scripts\python.exe -m pytest tests/test_phase5_vision.py -k "not test_kcm0_history_and_integrity_preserved" -v`
   - Scope: 29 approved tests (excluding the 1 unsafe production DB test)
