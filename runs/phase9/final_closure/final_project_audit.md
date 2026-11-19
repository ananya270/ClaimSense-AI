# ClaimSense AI — Phase 9.11: Final Project & Repository Audit

**Project:** ClaimSense AI (Final-Year B.Tech Major Project)  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.11 — Final Documentation, Reproducibility & Project Sign-off  
**Audit Date:** 2026-11-20  
**Academic Session:** 2026–2027  
**Department:** Computer Science & Engineering, ABES Engineering College  
**Audit Status:** COMPLETE & FACTUALLY VERIFIED

---

## 1. Executive Summary

This document presents the comprehensive repository and project audit of ClaimSense AI at the conclusion of Phase 9. The audit verifies that all codebase structures, installation procedures, environment configurations, model checkpoints, dataset provenance, API endpoints, database schemas, and regression tests accurately reflect the physical state of the repository.

No capabilities, metrics, or certifications have been fabricated. All documented behaviors correspond directly to verified code and experimental logs.

---

## 2. Directory Structure Audit

The ClaimSense AI project follows a strictly modular, decoupled architecture:

```
ClaimSense-AI/
├── backend/                        # Core Application Backend (Flask + SQLAlchemy)
│   ├── app.py                      # Flask Application Factory & App Entrypoint
│   ├── config.py                   # Hardened Environment & Security Configuration
│   ├── extensions.py               # Shared Application Extensions
│   ├── database/                   # SQLite Persistence & ORM Data Models
│   │   ├── db.py                   # Thread-Safe Database Session Management
│   │   ├── models.py               # SQLAlchemy ORM Models (Claim, User, Vision, NLP, etc.)
│   │   └── shadow_telemetry.db     # Asynchronous Shadow Telemetry Database (WAL Mode)
│   ├── routes/                     # RESTful API Route Controllers
│   │   ├── auth.py                 # User Registration, Login, Session Management & CSRF
│   │   ├── claims.py               # Claim Lifecycle, Multipart Uploads, Analysis & Reports
│   │   └── health.py               # System Health, DB Connectivity & Readiness Probes
│   ├── services/                   # Multi-Modal Intelligence Engines
│   │   ├── llm/                    # Language Model Orchestration (Mock / Extensible)
│   │   ├── nlp/                    # Deterministic Accident Narrative Timeline & Entity Parser
│   │   ├── ocr/                    # Document Processing (Tesseract, PyMuPDF, python-docx)
│   │   ├── risk/                   # Composite Claim Risk & Fraud Scoring Module
│   │   ├── verification/           # Phase 7 Cross-Source Corroboration Rule Engine
│   │   └── vision/                 # Phase 5 YOLOv8 Damage Detector & OpenCV Fallback
│   └── utils/                      # Utilities (Logger, Validators, Security Decorators)
├── frontend/                       # Client Presentation Layer (HTML5, Tailwind, JS)
│   ├── static/                     # CSS, JavaScript UI Controllers, Icons
│   └── templates/                  # Jinja2 Dashboard Templates (Claimant, Assessor, Admin)
├── models/                         # Trained Neural Network Checkpoints
│   ├── phase5/best.pt              # Authoritative Production Model (YOLOv8n @ 416x416)
│   └── vehicle_damage/best.pt      # Symlinked / Mirrored Baseline Checkpoint
├── datasets/                       # Computer Vision Training & Evaluation Data
│   └── CarDD_300/                  # Car Damage Dataset (210 Train, 45 Valid, 45 Test)
├── tests/                          # Automated Regression Test Suite (12 Modules, 158 Tests)
├── runs/                           # Experimental Runs, Training Logs & Evaluation Records
│   └── phase9/                     # Complete Phase 9 Forensic Audit & Retraining Artifacts
├── data/                           # Runtime Operational Data & Persistent Databases
│   └── claimsense.db               # Authoritative Production SQLite Database
├── scratch/                        # Temporary Execution Scripts & Benchmark Runbooks
├── .env.example                    # Sample Environment Configuration Template
├── requirements.txt                # Pinned Python Dependencies
└── README.md                       # Comprehensive Project Documentation
```

---

## 3. Configuration & Environment Audit

### 3.1 Environment Security Controls (`backend/config.py`)
- **Secret Key Enforcement:** Refuses to launch in production mode if default or insecure secrets (`secret`, `changeme`, `dev`) are detected.
- **Session Security:** `SESSION_COOKIE_HTTPONLY = True`, `SESSION_COOKIE_SAMESITE = "Lax"`, `SESSION_COOKIE_SECURE = IS_PRODUCTION`.
- **CORS Allowlist:** Restricted to authorized localhost / 127.0.0.1 ports (5000, 5001).
- **Upload Constraints:** Hard cap of 16 MB (`MAX_CONTENT_LENGTH = 16 * 1024 * 1024`); strict file extension whitelist (`pdf`, `png`, `jpg`, `jpeg`, `docx`).

### 3.2 Runtime Dependencies (`requirements.txt`)
- Python Runtime: 3.10 to 3.14 (Verified active: Python 3.14.6 AMD64).
- Core Frameworks: Flask >= 3.0, SQLAlchemy >= 2.0, PyTorch 2.15.0+cpu, Torchvision 0.29.2+cpu, Ultralytics 8.4.214, OpenCV 4.10.0 / 4.12.0, PyMuPDF 1.25.x, ReportLab >= 4.0.

---

## 4. Database Schema Audit

The SQLite production schema (`data/claimsense.db`) defines 9 fully normalized relational tables:

1. `users`: Credentials, hashed passwords (`scrypt`/`pbkdf2`), email, user role (`user`, `assessor`, `admin`).
2. `claims`: Core claim master record (claim ID `CLM-YYYYMMDD-XXXX`, claimant metadata, policy number, vehicle registration, accident date, description, status).
3. `claim_images`: Uploaded photographic evidence, MIME types, file sizes, forensic verification status.
4. `extracted_information`: OCR-parsed key-value pairs (policy dates, insured name, invoice totals).
5. `vehicle_damage_analyses`: Phase 5 YOLO execution records (processing latency, total detections, detection method, model version).
6. `vehicle_damage_detections`: Individual localized damage instances (bounding box normalized coordinates, category, confidence, estimated severity, spatial region).
7. `claim_nlp_analyses`: Narrative extraction records (incident classification, chronological timeline, entity mentions).
8. `claim_verification_runs`: Phase 7 cross-source corroboration executions (composite consistency score, overall status).
9. `verification_findings`: Granular rule engine determinations (`MATCH`, `MISMATCH`, `INSUFFICIENT_EVIDENCE`, rule category, severity).

---

## 5. Audit Verification Statement

All components documented above exist physically on disk, execute cleanly without syntax or import errors, and validate against the approved system architecture.
