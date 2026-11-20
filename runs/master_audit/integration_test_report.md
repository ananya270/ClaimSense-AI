# ClaimSense AI — Master System Integration & Workflow Audit Report

**Auditor:** Senior QA Architect & System Integration Auditor  
**Project:** ClaimSense AI (Major Project)  
**Scope:** Multi-Modal Pipeline Integration, Workflow Orchestration, and Data Flow  
**Workflows Audited:** 10 / 10 Workflows Executed & Verified  
**Integration Status:** **FUNCTIONALLY INTEGRATED (SINGLE-THREAD FULLY VERIFIED / HIGH-CONCURRENCY STRESS PENDING)**  

---

## 1. Executive Summary

ClaimSense AI integrates five major computational disciplines into a single automated insurance intelligence platform:
1. **Web & Identity Architecture** (Flask, Werkzeug, SQLite)
2. **Document Processing & OCR** (PyMuPDF, Tesseract, python-docx)
3. **Computer Vision Object Detection** (Ultralytics YOLOv8 fine-tuned on CarDD)
4. **Natural Language Processing** (Rule-based entity extraction and event chronology)
5. **Deterministic Verification & Document Generation** (Damerau-Levenshtein, ReportLab PDF)

This audit verified the end-to-end data pipelines connecting these modules. All 10 documented workflows executed sequentially without deadlocks, unhandled exceptions, or schema mismatches.

---

## 2. Ten-Workflow Verification Breakdown

The table below catalogs empirical results for each workflow tested:

| Workflow ID | Workflow Name | Participating Subsystems | Input Evidence | Key Measured Output | Observed Latency | Verification Status |
| :---: | :--- | :--- | :--- | :--- | :---: | :---: |
| **WF-01** | User Authentication | Web, DB, Auth | Username & password | HTTPOnly cookie, User object without password | 131.5 ms | **PASS** |
| **WF-02** | Claim Intake & Storage | Web, OCR, Vision, DB | 4 files (PDFs + CarDD photo) | Claim ID minted (`CLM-...`), files stored, DB row created | 3,653.4 ms | **PASS** |
| **WF-03** | Policy Index Lookup | Web, DB | Policy number `POL-2026-9901` | Query results isolated by policy | 18.2 ms | **PASS** |
| **WF-04** | Evidence Inspection | Web, Storage, DB | Claim ID | 4 files verified on disk with valid photo flag | 16.4 ms | **PASS** |
| **WF-05** | Damage Detection | Computer Vision, DB | Photo `000023.jpg` | 5 damage boxes (`dent`, `lamp broken`, `scratch`, `tire flat`) | 53.2 ms (warm) | **PASS** |
| **WF-06** | OCR Field Retrieval | OCR, DB | Claim ID | Extracted policy dates, vehicle number, claimant name | 4.7 ms | **PASS** |
| **WF-07** | Invoice Corroboration | Verification, OCR, CV | Invoice items vs detections | Bumper & lamp items corroborated with damage boxes | 37.3 ms | **PASS** |
| **WF-08** | Cross-Source Rules | Verification, NLP, OCR | All evidence sources | Consistency score computed across 7 formal rules | (Included above) | **PASS** |
| **WF-09** | Granular Findings | Verification, DB | Claim ID | 7–9 classified findings with severity and match status | 3.8 ms | **PASS** |
| **WF-10** | Consolidated PDF | Reporting, Graphics, DB | Verified claim record | Receipt (4.2 KB) and 8-page Document PDF (433.7 KB) | 355.3 ms | **PASS** |

---

## 3. Cross-Module Data Flow Analysis

### 3.1 Ingestion to Computer Vision
- During `POST /api/claims`, the file validator verifies the photographic nature of `vehicle_image`.
- The upload handler writes the file to `uploads/CLM-YYYYMMDD-XXXX/images/vehicle_image.jpg` and registers a `ClaimImage` record in SQLite.
- Damage analysis is triggered inline or via `POST /api/claims/<id>/analyze-damage`.
- The detector normalizes pixel bounding boxes to relative float coordinates ($0.0 \le x, y, w, h \le 1.0$), ensuring resolution invariance across upstream and downstream modules.

### 3.2 Vision and OCR to Cross-Source Engine
- Extracted invoice line items (e.g. `"Rear Bumper Dent Repair"`, `"Tail Lamp Assembly"`) are normalized into structured tokens.
- The verification engine matches invoice part tokens against YOLOv8 detected class categories (`dent`, `lamp broken`) and localized vehicle zones.
- Detected visual damages without corresponding invoice entries are tagged `VISUAL_ONLY_FINDING`.
- Invoice line items lacking visual bounding boxes are tagged `NOT_CONFIRMED`.

### 3.3 Scoring & Evidence Coverage
- The Phase 7 scoring formula applies formal calibrated weights:
  $$\text{raw\_points} = (N_{\text{match}} \times 1.0) + (N_{\text{visual\_only}} \times 0.60) + (N_{\text{not\_confirmed}} \times 0.70) + (N_{\text{inconclusive}} \times 0.50) + (N_{\text{discrepancy}} \times 0.35)$$
- Inconclusive evidence (e.g. unparsed policy dates) receives a neutral $0.50$ factor rather than inflating consistency.
- Evidence coverage percentage communicates completeness:
  $$\text{coverage} = \frac{\text{evaluated\_with\_data}}{\text{total\_comparisons}} \times 100.0$$

---

## 4. Concurrency & Mutex Thread Safety

- **Mechanism:** In [`backend/services/vision/service.py`](file:///c:/Users/ydvan/Desktop/ClaimSense%20Ai/ClaimSense-AI/backend/services/vision/service.py), per-claim re-entrant threading locks (`_get_claim_lock(claim_id)`) serialize concurrent requests for the same claim.
- **Empirical Behavior:** When two concurrent threads request damage analysis for the same claim, Thread 1 acquires the mutex and runs inference; Thread 2 waits, acquires the mutex after Thread 1 finishes, and immediately reuses the persisted database record without redundant tensor calculation.
- **Limitation:** While per-claim thread safety is verified, system-wide connection pool saturation under 50+ concurrent users was not tested.
