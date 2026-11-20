# ClaimSense AI — Master Technical Remediation Backlog

**Auditor:** Senior QA Architect & System Integration Auditor  
**Project:** ClaimSense AI (Major Project)  
**Scope:** Actionable Technical Backlog for Project Owner Review & Remediation  
**Status:** **PENDING PROJECT OWNER APPROVAL (READ-ONLY AUDIT — ZERO CODE EDITS PERFORMED)**  

---

## 1. Remediation Backlog Summary

| Item ID | Priority Tier | Domain / Subsystem | Defect / Requirement Description | Estimated Effort | Target Phase |
| :--- | :---: | :--- | :--- | :---: | :---: |
| **REM-01** | **P1 (Critical)** | Machine Learning (CV) | Structural crack detection failure ($F1=0.00$); class-weighted focal loss & SAHI | 3–5 Days | Phase 9.12 / 10-ML |
| **REM-02** | **P1 (Critical)** | Systems QA | Multi-user high-concurrency stress testing (50+ users via Locust) | 1–2 Days | Phase 10.1 |
| **REM-03** | **P2 (Major)** | DevOps / Deployment | Production containerization (`Dockerfile` and `docker-compose.yml`) | 1 Day | Phase 11.1 |
| **REM-04** | **P2 (Major)** | Integration QA | Chaining remaining 15 REST endpoints in master E2E integration scenario | 1 Day | Phase 10.2 |
| **REM-05** | **P2 (Major)** | Observability | Prometheus metrics endpoint (`/metrics`) and live monitoring telemetry | 1–2 Days | Phase 11.2 |
| **REM-06** | **P3 (Moderate)**| Governance / Docs | Disambiguate Phase 10 E2E milestone from Phase 10 Retraining proposal | 0.5 Day | Documentation |
| **REM-07** | **P3 (Moderate)**| Governance / Docs | Synchronize `README.md` status badges and descriptions with audit reality | 0.5 Day | Documentation |
| **REM-08** | **P3 (Minor)** | Code Maintenance | Refactor PyMuPDF deprecated imports (`import fitz` $\rightarrow$ `import pymupdf`) | 0.5 Day | Phase 4 / Core |
| **REM-09** | **P3 (Moderate)**| Security | Automated DAST vulnerability scanning (OWASP ZAP baseline) | 1 Day | Phase 10 / Security |

---

## 2. Granular Remediation Specifications

### REM-01: ML Retraining for Structural Crack Detection ($F1=0.00$)
- **Problem:** In production model `models/phase5/best.pt` and candidate `P9-T02`, zero structural cracks were detected on the CarDD independent benchmark cohort.
- **Root Cause:** Hailine crack features vanish during $32\times$ strided convolutional downsampling; severe class imbalance in CarDD ($<4\%$ cracks) biases gradients toward dents and scratches.
- **Remediation Specification:**
  1. Fine-tune YOLOv8 using class-weighted focal loss with $\alpha_{\text{crack}} = 2.8$ and $\gamma = 2.0$.
  2. Implement Slicing Aided Hyper Inference (SAHI) with $640\times 640$ overlapping tiles to preserve hairline crack pixel density without downsampling.
  3. Validate against the CarDD independent benchmark requiring crack recall $\ge 0.50$ and precision $\ge 0.40$.

### REM-02: Multi-User Concurrency & Load Stress Testing
- **Problem:** Concurrency was only tested for 2 threads accessing the same claim mutex; multi-user connection pooling under load was unmeasured.
- **Remediation Specification:**
  1. Author a Locust test harness simulating 25 to 50 concurrent claimants submitting claims, polling status, and downloading PDFs.
  2. Measure response time degradation (p50, p95, p99) and identify potential SQLite database lock contention (`sqlite3.OperationalError: database is locked`).
  3. Configure connection pooling or evaluate SQLite WAL mode with appropriate busy timeouts.

### REM-03: Production Containerization
- **Problem:** `Dockerfile` and `docker-compose.yml` are completely absent from the repository.
- **Remediation Specification:**
  1. Author a multi-stage `Dockerfile`:
     - Base: `python:3.12-slim-bookworm` or `3.13-slim`.
     - System dependencies: `tesseract-ocr`, `libgl1-mesa-glx`, `libglib2.0-0`.
     - Python dependencies: `requirements.txt` with PyTorch CPU-only wheels.
  2. Author `docker-compose.yml` with persistent volume mappings for `data/` and `uploads/`.

### REM-04: Master E2E Chaining of Non-Primary Endpoints
- **Problem:** 15 endpoints are tested only in isolated unit test files.
- **Remediation Specification:**
  1. Enhance `scratch/test_e2e_system_validation.py` into a formal repository test `tests/test_e2e_full_master.py`.
  2. Chain all 26 endpoints into a cohesive workflow: user signup $\rightarrow$ login $\rightarrow$ csrf $\rightarrow$ claim submit $\rightarrow$ policy lookup $\rightarrow$ search $\rightarrow$ image replace $\rightarrow$ analyze damage $\rightarrow$ history $\rightarrow$ annotated image $\rightarrow$ nlp analyze $\rightarrow$ nlp get $\rightarrow$ verify $\rightarrow$ findings $\rightarrow$ receipt $\rightarrow$ document report $\rightarrow$ raw evidence $\rightarrow$ logout.

### REM-05: Real-Time Observability & Monitoring Daemon
- **Problem:** Telemetry database exists in SQLite, but no live Prometheus exporter or real-time dashboard is deployed.
- **Remediation Specification:**
  1. Add `prometheus_flask_exporter` to export request counts, latencies, and error codes at `/metrics`.
  2. Configure structured JSON logging with daily log rotation.

### REM-06 & REM-07: Documentation Discrepancy Synchronization
- **Remediation Specification:**
  1. In `README.md`, update Phase 10 operational status to:  
     `Conditionally Complete (Single-User E2E Complete; Multi-User Stress Pending)`
  2. Update Phase 11 operational status to:  
     `Partially Implemented (Academic Docs Complete; Containerization Pending)`
  3. Renumber ML crack retraining from "Phase 10 Retraining" to "Phase 9.12 / 10-ML Retraining".

### REM-08: PyMuPDF Deprecated Import Refactoring
- **Problem:** `fitz/__init__.py:17: FutureWarning: The fitz API is deprecated and will be removed in future. Use import pymupdf instead.`
- **Remediation Specification:**
  Replace `import fitz` with `import pymupdf as fitz` or `import pymupdf` across:
  - `backend/services/ocr/document_validator.py`
  - `backend/services/ocr/extractor.py`
  - `backend/services/receipt.py`
  - `tests/test_document_processing.py`
