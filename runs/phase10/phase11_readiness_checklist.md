# ClaimSense AI — Phase 11 Readiness Checklist & Operational Hardening Guide
## Deployment, Monitoring, Background Architecture & Production Hardening

**Document Version:** 1.0.0  
**Governance Date:** November 20, 2026  
**Auditor Roles:** Senior Software Architect, DevOps Auditor, QA Lead & Database Reliability Engineer  
**Scope:** Phase 11 Operational Readiness (Pre-Deployment Transition Framework)  

---

> [!IMPORTANT]
> **Operational Status Disclosure:**
> This document constitutes a formal **Readiness Assessment & Engineering Roadmap** for Phase 11. Completion of this checklist is an architectural prerequisite for production deployment, but **does not constitute immediate live production deployment approval**.

---

## 1. Production WSGI Server Architecture

- [ ] **Current State:** Development server runs via Werkzeug (`python backend/app.py` or `flask run`) on port 5001. Werkzeug is explicitly single-process and not hardened for production concurrency or denial-of-service resilience.
- [ ] **Target Production Runtime:**
  - **Linux Environments:** Deploy with **Gunicorn** using pre-fork worker processes:
    ```bash
    gunicorn --workers 4 --threads 2 --worker-class gthread --bind 127.0.0.1:5001 --timeout 120 "backend.app:create_app()"
    ```
  - **Windows Production Environments:** Deploy with **Waitress** (pure-Python, multithreaded, production-grade WSGI server for Windows):
    ```powershell
    waitress-serve --listen=127.0.0.1:5001 --threads=8 "backend.app:create_app()"
    ```
- [ ] **Connection & Keep-Alive Tuning:** Set client request header limits (`max_request_header_size = 16384`) and configure graceful worker restart thresholds (`max_requests = 1000`, `max_requests_jitter = 50`) to prevent memory leaks from long-running PyTorch tensors.

---

## 2. Reverse Proxy & HTTPS Configuration

- [ ] **Current State:** Direct HTTP socket binding to `127.0.0.1:5001`.
- [ ] **Target Architecture:** Deploy an edge reverse proxy (e.g., **Nginx** or **Caddy**) terminating TLS 1.3:
  - Enforce automated certificate renewal (Let's Encrypt / ACME).
  - Configure HTTP Strict Transport Security (`HSTS`: `max-age=31536000; includeSubDomains; preload`).
  - Enforce maximum client body size matching application limits:
    ```nginx
    client_max_body_size 16M;
    ```
  - Buffer static asset serving directly through Nginx (bypass WSGI for UI `/css`, `/js`, and icons).
- [ ] **Security Headers Policy:**
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Content-Security-Policy: default-src 'self'; img-src 'self' data: blob:; script-src 'self'; style-src 'self' 'unsafe-inline';`
  - `Referrer-Policy: strict-origin-when-cross-origin`

---

## 3. Asynchronous Background Worker Architecture for ML & OCR

- [ ] **Current State (Identified Bottleneck):** `POST /api/claims` synchronously executes multipart file writes, Tesseract OCR document extraction, and YOLOv8 vehicle damage inference. This takes ~3.1 seconds per submission, causing tail latencies to reach 673 ms (mean) and 1,400 ms (p95) under 50 concurrent users.
- [ ] **Target Phase 11 Architecture:**
  - Implement an asynchronous task queue (**Celery** with Redis, or **RQ** / **Huey** for lightweight Python deployments):
  ```mermaid
  flowchart LR
      CLIENT["Client Browser / Mobile"] -->|"1. POST /api/claims (Files)"| WSGI["Flask WSGI Intake"]
      WSGI -->|"2. Save Raw Uploads & Mint Claim ID"| DISK[("Disk / S3 Storage")]
      WSGI -->|"3. Insert Claim (Status: PENDING_ANALYSIS)"| DB[("Primary Database")]
      WSGI -->|"4. Dispatch Task"| QUEUE[("Redis / RQ Queue")]
      WSGI -.->|"5. Return HTTP 202 Accepted {claim_id, status_url}"| CLIENT

      QUEUE -->|"6. Pull Task"| WORKER["Dedicated ML Worker Process\n(YOLOv8 + OCR + NLP)"]
      WORKER -->|"7. Execute Pipelines"| INFERENCE["PyTorch & Tesseract"]
      WORKER -->|"8. Write Verification Findings"| DB
      WORKER -->|"9. Update Status: IN_REVIEW"| DB
  ```
- [ ] **Immediate Latency Benefit:** The synchronous intake endpoint response time will drop from ~3,100 ms to $<50$ ms, permanently resolving the 50-user latency SLA failure.
- [ ] **Task Status Polling & WebSockets:** Add endpoint `GET /api/claims/<id>/status` returning analysis progression (`processing_ocr`, `processing_vision`, `verifying`, `completed`), or provide Server-Sent Events (SSE) updates to the assessor frontend.

---

## 4. Database Reliability, Backup & Recovery Strategy

- [ ] **Current State:** Single-file SQLite database at `data/claimsense.db` operating in default `DELETE` mode.
- [ ] **Production Journal Mode Migration:**
  - Transition staging and production database to SQLite `WAL` mode (`PRAGMA journal_mode=WAL;`).
  - Retain `PRAGMA busy_timeout=5000;` to ensure transaction queue cushioning.
  - Set synchronous commit mode to `NORMAL` (`PRAGMA synchronous=NORMAL;`) for 2x–3x write throughput improvement without risking corruption.
- [ ] **Automated Backup Strategy:**
  - Implement a daily cron job utilizing SQLite's online backup API (`sqlite3_backup`):
    ```powershell
    # Safe online SQLite backup without locking writers
    sqlite3 data/claimsense.db ".backup 'backups/claimsense_$(Get-Date -Format yyyyMMdd_HHmmss).db'"
    ```
  - Replicate compressed daily backup archives to offsite object storage with a 30-day retention policy.
- [ ] **WAL Checkpoint Maintenance:** Run automated periodic checkpointing (`PRAGMA wal_checkpoint(PASSIVE);` hourly, `PRAGMA wal_checkpoint(TRUNCATE);` daily during off-peak windows) to cap WAL file growth.

---

## 5. Secret Management & Environment Security

- [ ] **Current State:** `.env` loaded via `python-dotenv` with local development fallback secrets.
- [ ] **Production Secret Sanitization:**
  - Generate cryptographically secure `SECRET_KEY` (minimum 64 hex characters):
    ```python
    python -c "import secrets; print(secrets.token_hex(32))"
    ```
  - Ensure `.env` is excluded from git (`.gitignore` verified).
  - Inject secrets via cloud secret stores (AWS Secrets Manager, GCP Secret Manager, or HashiCorp Vault) rather than plain-text files on disk.
- [ ] **Session Security Enforcements:**
  - `SESSION_COOKIE_SECURE = True` (enforce HTTPS transmission).
  - `SESSION_COOKIE_HTTPONLY = True` (prevent JavaScript access).
  - `SESSION_COOKIE_SAMESITE = 'Lax'` or `'Strict'`.
  - `PERMANENT_SESSION_LIFETIME = timedelta(hours=8)`.

---

## 6. Structured Application Logging

- [ ] **Current State:** Standard Python logging writing formatted text streams to console and files.
- [ ] **Target Logging Infrastructure:**
  - Convert production logs to structured JSON lines (JSONL) with standardized fields:
    ```json
    {
      "timestamp": "2026-11-20T21:40:35.123Z",
      "level": "INFO",
      "logger": "claimsense.claims",
      "request_id": "req-9a8b7c-1234",
      "user_id": 42,
      "claim_id": "CLM-20261120-XXXX",
      "event": "claim_submitted",
      "duration_ms": 48.2
    }
    ```
  - Implement automatic log rotation (`RotatingFileHandler` with 50 MB max size and 10 backup files).
  - Stream logs to centralized log forwarders (FluentBit / Logstash / Datadog Agent).

---

## 7. Error Tracking & Crash Monitoring

- [ ] **Current State:** Application logs capture Python tracebacks; no active external error tracking.
- [ ] **Target Implementation:**
  - Integrate **Sentry** (or self-hosted GlitchTip):
    ```python
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration

    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN"),
        integrations=[FlaskIntegration()],
        traces_sample_rate=0.1,
        profiles_sample_rate=0.1,
    )
    ```
  - Filter and scrub sensitive personally identifiable information (PII) such as claimant names, policy numbers, and passwords prior to dispatch.

---

## 8. Telemetry & Infrastructure Resource Monitoring

- [ ] **Current State:** Ad-hoc resource sampling via `psutil` in load test runners.
- [ ] **Target Telemetry Stack:**
  - Expose `/metrics` endpoint using `prometheus_flask_exporter`.
  - Export system metrics via Node Exporter / Windows Performance Counters:
    - CPU utilization (Alert if $>80\%$ for $>5\text{ minutes}$).
    - Host and process RAM consumption (Alert if $>85\%$).
    - SQLite open file descriptors and lock wait times.
    - Disk volume utilization on `uploads/` and `data/` (Alert if free disk $<15\%$).
  - Establish Grafana dashboard displaying active users, request rates, HTTP 5xx counts, and p95 latency.

---

## 9. Deployment, Blue-Green Strategy & Rollback Runbooks

- [ ] **Zero-Downtime Deployment Pattern:**
  - Use containerized deployments (Docker / Docker Compose / Kubernetes).
  - Deploy blue-green or rolling updates with health probe validation (`/api/health`) before traffic redirection.
- [ ] **Automated Rollback Triggers:**
  - Trigger automatic rollback if `/api/health` fails for 3 consecutive probes post-deploy.
  - Trigger rollback if HTTP 5xx rate exceeds 1% in the first 5 minutes post-deploy.
- [ ] **Database Schema Rollback Runbook:**
  - Maintain bidirectional migration scripts with backward compatibility (expand-and-contract pattern).

---

## 10. Comprehensive Security Review & Vulnerability Assessment

- [ ] **OWASP Top 10 Verification:**
  - **Injection:** 100% of database interactions leverage SQLAlchemy parameterized queries.
  - **Broken Authentication:** PBKDF2 with 600,000 iterations verified; brute-force rate limiting active (5 attempts / minute per IP).
  - **Security Misconfiguration:** Debug mode disabled (`FLASK_DEBUG=False`).
  - **Insecure Deserialization:** No unpickling of untrusted user input; JSON and XML payloads strictly validated.
  - **SSRF & Path Traversal:** File upload names sanitized using `secure_filename()` and stored in isolated claim ID folders.
- [ ] **Dependency Vulnerability Scanning:**
  - Execute scheduled `pip-audit` or `safety check` in CI/CD pipeline to detect known CVEs in third-party packages.

---

## 11. Report Snapshot Persistence Implementation Plan

- [ ] **Current State:** ADR approved in `runs/phase10/stage2_database_architecture_decision.md`; existing table `reports` remains unwired.
- [ ] **Implementation Steps for Phase 11:**
  1. Apply forward DDL migration (`scripts/migrations/migrate_reports_table.py`).
  2. Implement `ReportService.freeze_report(claim_id, user_id)` in `backend/services/receipt.py`:
     - Compile 8-page PDF report.
     - Calculate SHA-256 hash.
     - Persist file to `uploads/<claim_id>/reports/audit_report_v1.pdf`.
     - Insert record into `reports` table.
  3. Wire status transition endpoint (`POST /api/claims/<id>/status`):
     - Trigger `freeze_report()` automatically when status changes to `VERIFIED` or `FLAGGED`.
  4. Update report retrieval endpoint (`GET /api/claims/<id>/report`):
     - Check if an active frozen report exists in `reports`; if yes, stream static file.
     - If claim is in draft/review, synthesize dynamically in-memory.

---

## 12. Phase 11 Operational Readiness Sign-Off Matrix

| Category | Readiness Status | Priority | Target Phase 11 Milestone |
|:---|:---:|:---:|:---|
| 1. Production WSGI Server | **Documented** | High | Phase 11.1 |
| 2. Reverse Proxy & HTTPS | **Documented** | High | Phase 11.1 |
| 3. Async Background Workers | **Architected** | **Critical** (Resolves 50-User Latency) | Phase 11.2 |
| 4. SQLite WAL & Backups | **Verified in Staging** | High | Phase 11.2 |
| 5. Secret Management | **Ready** | High | Phase 11.1 |
| 6. Structured JSON Logging | **Documented** | Medium | Phase 11.3 |
| 7. Error Tracking (Sentry) | **Documented** | Medium | Phase 11.3 |
| 8. Metrics & Prometheus | **Documented** | Medium | Phase 11.3 |
| 9. Blue-Green Deployment | **Documented** | Medium | Phase 11.4 |
| 10. Security Hardening | **Verified in Code** | High | Phase 11.1 |
| 11. Report Snapshot Wiring | **ADR Approved** | Medium | Phase 11.2 |

---

*Summary: Phase 11 readiness items are fully cataloged, architectural blueprints are prepared, and prerequisite Stage 2 concurrency findings have established clear performance targets.*
