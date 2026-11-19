# ClaimSense AI — Phase 9.10: Known Issues & Limitations Register

**Project:** ClaimSense AI  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.10 — End-to-End System Validation & Reliability Audit  
**Date of Record:** 2026-11-20  
**Audit Status:** OPEN ISSUES DOCUMENTED & CATEGORIZED

---

## 1. Overview & Purpose

This register maintains an objective, unvarnished record of all identified defects, architectural trade-offs, environmental warnings, and domain-specific failure modes across ClaimSense AI.

Documenting these issues ensures transparent risk management and establishes a concrete roadmap for future optimization phases.

---

## 2. Issues & Limitations Matrix

| Issue ID | Domain / Subsystem | Severity | Issue Summary | Production Impact | Operational Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ISS-01** | Vision / Model Weights | **HIGH** | Structural crack detection failure (0/13 cracks detected on independent CarDD benchmark at $\tau=0.25$). | Cracks in body panels or glass require manual adjuster review. | **OPEN** (Promotion blocked at Gate 9.8) |
| **ISS-02** | Vision / Model Weights | **MEDIUM** | Multi-class recall trade-off in high-resolution candidate (P9-T02 reduced dent/scratch recall). | Candidate P9-T02 rejected; production baseline retained. | **RESOLVED VIA RETENTION** |
| **ISS-03** | Document / OCR | **LOW** | PyMuPDF `fitz` API deprecation warning (`The fitz API is deprecated...`). | None. Future compatibility warning only. | **OPEN (Scheduled for Phase 10)** |
| **ISS-04** | Vision / Host Environment | **LOW** | Ultralytics settings write restriction in Windows sandbox (`[Errno 13] Permission denied`). | None. Ultralytics falls back cleanly to in-memory config. | **OPEN (Environmental)** |
| **ISS-05** | Database / Testing | **LOW** | SQLAlchemy SQLite unclosed connection warning during unit test teardowns. | None. In-memory temporary test artifacts only. | **OPEN (Test Harness Only)** |
| **ISS-06** | Vision / Fallback Pipeline | **MEDIUM** | OpenCV fallback pipeline produces bounding contours without semantic damage classification. | Active only when YOLO weights are missing; 0 false detections. | **BY DESIGN** |
| **ISS-07** | Ingestion / Media Formats | **LOW** | iOS `.heic` photos rejected unless converted to `.jpg`/`.png` due to missing `pi_heif`. | User receives clean validation message requesting JPEG/PNG. | **OPEN (Dependency Enhancement)** |

---

## 3. Deep-Dive Issue Profiles & Remediation Strategies

### ISS-01: Structural Crack Detection Deficit
- **Root Cause Forensic:**
  - CarDD dataset contains significant annotation imbalance: cracks account for only ~6.8% of damage instances.
  - Cracks exhibit extreme aspect ratios (long, hairline structures with widths $< 5$ px), which suffer spatial resolution loss during standard downsampling.
  - Reflections, body panel creases, and lighting gradients create visual ambiguity.
- **Empirical Evidence:**
  - Production Baseline: mAP50 = 0.0002; Crack Recall at $\tau=0.25$: 0.0000% (0/13).
  - Candidate P9-T02 ($640\times 640$): mAP50 = 0.0076 (38x gain); Crack Recall at $\tau=0.25$: 0.0000% (0/13).
- **Remediation Roadmap:**
  1. Implement Sliced Aided Hyper Inference (SAHI) to evaluate small image patches at native sensor resolution.
  2. Adopt Oriented Bounding Boxes (YOLOv8-OBB) or Instance Segmentation (YOLOv8-seg) to capture hairline geometries without large rectangular background noise.
  3. Augment training with synthetic cracks using generative adversarial inpainting.

---

### ISS-03: PyMuPDF Deprecation Warning
- **Log Observation:**
  `FutureWarning: The fitz API is deprecated and will be removed in future. Use import pymupdf instead.`
- **Impact:** Python 3.14 deprecation advisory; functions normally.
- **Remediation:** Refactor `import fitz` to `import pymupdf` across `backend/services/ocr/` during Phase 10 maintenance.

---

### ISS-04: Ultralytics Settings Permission Warning
- **Log Observation:**
  `ERROR Error writing to C:\Users\ydvan\AppData\Roaming\Ultralytics\settings.json: [Errno 13] Permission denied`
- **Impact:** Sandboxed Windows environments restrict writes to user AppData Roaming; Ultralytics defaults to internal parameters without performance impact.
- **Remediation:** Set `YOLO_CONFIG_DIR=scratch/ultralytics` in `.env` to redirect settings file to workspace scratch.

---

### ISS-06: OpenCV Fallback Pipeline Semantic Limitation
- **Behavior:** If YOLO checkpoint files are absent, the detector switches to `opencv_traditional_cv`.
- **Operational Reality:** It detects edge anomalies and draws diagnostic contours, but sets `total_detections = 0` and `damage_categories = []` to prevent hallucinating false insurance claims.
- **Remediation:** Intended system design. Production model files must remain present in `models/phase5/best.pt`.

---

## 4. Operational Risk Assessment

| Risk Category | Risk Level | Mitigation in Place |
| :--- | :--- | :--- |
| **System Crash / Outage** | **Very Low** | Concurrency mutexes, input sanitization, and 100% test pass rate guard uptime. |
| **Data Corruption / Loss** | **Very Low** | Scoped transactions with automatic rollback prevent dirty writes. |
| **Security / Unauthorized Access**| **Very Low** | HTTPOnly cookies, RBAC enforcement, extension sniffing, and forensic image filters active. |
| **Under-Detection of Cracks** | **Moderate** | Addressed by cross-source verification: claims reporting cracks with no vision detection are flagged for manual adjuster review rather than auto-rejected. |
