# ClaimSense AI — Master Documentation Discrepancies Register

**Auditor:** Senior QA Architect & System Integration Auditor  
**Project:** ClaimSense AI (Major Project)  
**Scope:** Forensic Comparison of Documentation Claims vs Physical Codebase Reality  
**Total Discrepancies Cataloged:** 6  
**Auditor Severity Assessment:** 2 Major, 3 Moderate, 1 Minor  

---

## 1. Executive Summary

This register formally documents all discrepancies identified between the repository's documentation (`README.md`, `DEVELOPMENT_LOG.md`, Phase 9 reports) and the physical codebase reality. A technical auditor must separate documented aspirations from reproducible engineering facts.

---

## 2. Catalog of Identified Discrepancies

### Discrepancy 01: Premature "Completed in Phase 9.10" Claim for Phase 10
- **Documented Claim:** In `README.md` (Line 384):  
  `| **Phase 10** | Full System Integration & E2E Testing | **Completed in Phase 9.10** | ... |`
- **Physical Codebase Reality:**  
  The original Phase 10 roadmap specification (Commit `01efe2f`) explicitly mandated *"End-to-end stress testing, multi-user concurrency, edge-case hardening."* While single-user end-to-end workflows and edge-case hardening were completed in Phase 9.10, **multi-user high-concurrency load testing (e.g. 50+ concurrent virtual users via Locust or JMeter) was not executed**.
- **Severity:** **MAJOR**  
- **Auditor Verdict:** Phase 10 status in `README.md` should be updated from `Completed in Phase 9.10` to `Conditionality Complete (Single-User E2E Complete; Multi-User Load Testing Pending)`.

---

### Discrepancy 02: Missing Production Containerization for Phase 11
- **Documented Claim:** In `README.md` (Line 385):  
  `| **Phase 11** | Deployment, Monitoring & Documentation | **Phase 9.11 Ready** | Production model re-certified, reproducibility guide, academic evidence summary, project owner sign-off. |`
- **Physical Codebase Reality:**  
  The original Phase 11 scope (Commit `01efe2f`) mandated *"Production containerization, continuous monitoring, academic defense."* Forensic inspection of the repository confirms that **no `Dockerfile` or `docker-compose.yml` exists anywhere in the repository**. Furthermore, no live monitoring daemon or metrics exporter is deployed. Only the documentation package (reproducibility guide and academic summary) exists.
- **Severity:** **MAJOR**  
- **Auditor Verdict:** Phase 11 cannot be described as "Ready" or "Complete" without a working production containerization setup.

---

### Discrepancy 03: Dual "Phase 10" Architectural Nomenclature Conflict
- **Documented Claim:**  
  - In `runs/phase9/final_model_decision/final_model_comparison.md` and `model_selection_scorecard.md`, "Phase 10" is defined as a future machine learning retraining iteration targeting structural crack detection failure via class-weighted focal loss ($\alpha_{\text{crack}} = 2.8$) and multi-scale tiling.
  - In `README.md` (Line 384) and git history, "Phase 10" is defined as "Full System Integration & E2E Testing".
- **Physical Codebase Reality:**  
  Two entirely different project efforts share the identical milestone identifier ("Phase 10"), causing severe confusion between QA integration and ML retraining.
- **Severity:** **MODERATE**  
- **Auditor Verdict:** The project owner must officially rename the proposed crack retraining iteration to *Phase 9.12* or *Phase 10-ML*, preserving *Phase 10.0* exclusively for Systems Integration.

---

### Discrepancy 04: Misidentified Skipped Test in Phase 9.10 Footnote
- **Documented Claim:** In `runs/phase9/system_validation/regression_test_report.md` (Line 43):  
  `*\*Note: 1 test (`test_opencv_fallback_pipeline` in `test_phase5_vision.py`) is conditionally skipped when YOLO weights are present...*`
- **Physical Codebase Reality:**  
  Empirical execution of `unittest discover` proves that `test_opencv_fallback_pipeline` actually executes and passes. The single skipped test is actually:  
  `tests.test_phase5_vision.Phase5VisionTestSuite.test_kcm0_history_and_integrity_preserved` (Line 959).  
  The test conditionally skips because historical claim `CLM-20261116-KCM0` is absent from `data/claimsense.db`.
- **Severity:** **MINOR**  
- **Auditor Verdict:** Factual error in Phase 9.10 footnote. Corrected in Phase 10.0 and Master Audit reports.

---

### Discrepancy 05: Monolithic E2E API Chaining vs Unit Test Coverage
- **Documented Claim:** Phase 9.10 Executive Summary asserts: *"Audited 26 distinct API routes across Authentication, Claims, Vision, NLP, Verification, and Reporting"*.
- **Physical Codebase Reality:**  
  In the dedicated end-to-end integration script (`scratch/test_e2e_system_validation.py`), **11 endpoints** were chained sequentially. The remaining **15 endpoints** were tested in isolation within unit test files (`tests/test_*.py`). No untested endpoints exist in the repository, but monolithic chaining of all 26 endpoints was not achieved in a single script run.
- **Severity:** **MODERATE**  
- **Auditor Verdict:** Clarify that 26 endpoints are verified across the aggregate test suite, while 11 endpoints form the primary E2E chain.

---

### Discrepancy 06: Missing Standalone Phase 0, 10, and 11 Formal Specifications
- **Documented Claim:** The roadmap implies structured formal specification documents for each phase.
- **Physical Codebase Reality:**  
  While Phase 3 (`docs/PHASE_3_STABILIZATION_REPORT.md`), Phase 4 (`PHASE_4_COMPLETION_REPORT.md`), Phase 8 (Gates A–P), and Phase 9 (9.0–9.11) have comprehensive standalone reports, **Phase 0, Phase 10, and Phase 11 exist only as brief markdown headers and roadmap table cells in `DEVELOPMENT_LOG.md` and `README.md`**.
- **Severity:** **MODERATE**  
- **Auditor Verdict:** Formal specification documents should be authored for Phase 10 and Phase 11 to establish immutable acceptance criteria.
