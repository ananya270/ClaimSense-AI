# ClaimSense AI — Step 4: AI/ML, NLP & Cross-Source Verification Test Inventory

**Audit Phase:** Step 4: AI/ML, NLP & Cross-Source Verification Testing  
**Date:** 2026-11-22  
**Target Scope:** Document Processing (OCR/PyMuPDF), Claimant Narrative NLP, Cross-Source Verification Engine, Edge-Case & Failure Scenarios A–R  
**Inspection Mode:** Pre-Execution Static Inspection & Safety Assessment  

---

## 1. Objective & Scope

Step 4 focuses on evaluating the intelligence and verification pipeline of ClaimSense AI:
1. **Document Processing & OCR:** Extraction of key policy and claim fields from digital PDF, DOCX, and TXT files, table parsing, image type validation, and Document Intelligence Report generation.
2. **Phase 6 NLP Analysis:** Natural language narrative parsing, contraction expansion, entity extraction (locations, road intersections, other parties, vehicle registrations), chronological timeline reconstruction, accident categorization, and narrative damage extraction.
3. **Phase 7 Cross-Source Verification:** Multi-source consistency cross-referencing (Policy vs Intake Form vs Repair Invoice vs Claimant Narrative vs Vision Detections), discrepancy scoring, status determinations (`CONSISTENT`, `REVIEW_REQUIRED`, `INSUFFICIENT_EVIDENCE`), severity classifications, and fuzzy date/name/registration normalization.
4. **Scenarios A through R (Resilience & Edge Cases):** 18 failure and boundary scenarios testing missing documents, corrupted PDFs/images, synthetic vs real vehicle photos, null OCR returns, multi-claim policy collisions, and YOLOv8 inference fallbacks.

---

## 2. Test Selection & Safety Classification Matrix

| # | Test File | Test Class | Methods | Subsystem & Functionality Tested | Safety Classification | Isolation Mechanism | Group |
| :-: | :--- | :--- | :-: | :--- | :---: | :--- | :-: |
| 1 | `tests/test_document_processing.py` | `Phase4DocumentProcessingTests` | 13 | Document file validation, plain text claim extraction, insurance field extraction, Document Intelligence PDF report generation, synthetic vs photo image detection, field deduplication, status alias normalization | **SAFE TO RUN** | Ephemeral `tempfile.TemporaryDirectory()`, per-test isolated SQLite databases, `close_engine()` cleanup in `finally:` blocks | **Group 1** |
| 2 | `tests/test_phase6_nlp.py` | `TestPhase6NLP` | 14 | Text normalization & contraction expansion, abbreviation-safe sentence segmentation, entity extraction (roads, dates, plates, parties), chronological event reconstruction, accident type classification, narrative damage extraction, cross-check consistency | **SAFE TO RUN** | Ephemeral `tempfile.mkdtemp()`, isolated `test_phase6.db`, isolated uploads/reports directories, `shutil.rmtree` teardown | **Group 2** |
| 3 | `tests/test_phase7_verification.py` | `TestPhase7CrossSourceVerification` | 32 | Exact policy/claim field matching, fuzzy name matching, registration normalization & OCR digit substitutions, date normalization across formats, invoice vs damage comparisons, narrative vs vision corroboration, visual-only finding thresholds, overall score & status calculation | **SAFE TO RUN** | Ephemeral `tempfile.mkdtemp()`, isolated `test_phase7.db`, isolated uploads/reports directories, `shutil.rmtree` teardown | **Group 3** |
| 4 | `tests/test_phase7_cross_source_failures.py` | `TestPhase7CrossSourceFailures` | 18 | Boundary scenarios A–R: complete claim (A), missing policy (B), missing form (C), missing invoice (D), missing photo (E), corrupt PDF (F), corrupt image (G), synthetic image (H), replacement photo (I), null OCR (J), date format variances (K), plate conflicts (L), date conflicts (M), YOLO model fault tolerance (N), shared policy collision (O), non-existent claim (P), partial pipeline failure (Q), repeated idempotent requests (R) | **SAFE TO RUN** | Ephemeral `tempfile.mkdtemp()`, isolated `test_p7_failures.db`, isolated uploads/reports directories, `shutil.rmtree` teardown | **Group 4** |

**Total Step 4 Inventory:** 77 tests across 4 modules.

---

## 3. Mandatory Safety & Resource Isolation Verification

All 4 test modules adhere strictly to production isolation protocols:
- **Database Isolation:** Zero queries or migrations against `data/claimsense.db`. Each module or test case instantiates its own isolated SQLite database under `tempfile.mkdtemp()` or `tempfile.TemporaryDirectory()`.
- **Uploads & Reports Isolation:** Ephemeral folders created for each test run; live user files in `uploads/` and `reports/` are protected from read or delete operations.
- **Model Checkpoints:** Model weights (`models/phase5/best.pt`) remain unmodified (SHA-256 invariant). No model retraining or promotion routines are called.
- **Redis & Queues:** In-memory mocks or pure synchronous unit functions utilized; zero network socket connections or queue flushes against production Redis.
- **Code & Test Integrity:** Application code, business logic, and test files remain strictly untouched.

---

## 4. Planned Sequential Execution Strategy

1. **Group 1:** `tests/test_document_processing.py` (13 tests)
2. **Group 2:** `tests/test_phase6_nlp.py` (14 tests)
3. **Group 3:** `tests/test_phase7_verification.py` (32 tests)
4. **Group 4:** `tests/test_phase7_cross_source_failures.py` (18 tests)
