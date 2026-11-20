# ClaimSense AI &mdash; Multi-User Concurrency & Load Testing Framework

> **Module:** `tests/load`  
> **Milestone:** Phase 10 Stage 2 (Systems Reliability & Concurrency Validation)  
> **Tooling:** Locust 2.47+, Python 3.13, gevent, psutil  

---

## 1. Overview & Purpose

This framework provides deterministic, reproducible multi-user load testing for the ClaimSense AI platform. It evaluates application throughput, latency percentiles, error rates, and SQLite database concurrency under realistic concurrent usage.

### Evaluated Workload Profiles:
1. **10 Concurrent Users:** Baseline concurrency profile (spawn rate: 2/s, duration: 30s).
2. **25 Concurrent Users:** Moderate concurrent profile (spawn rate: 5/s, duration: 45s).
3. **50 Concurrent Users:** Peak stress profile (spawn rate: 10/s, duration: 60s).

---

## 2. Realistic User Scenarios

Simulated users interact with the ClaimSense AI REST API through weighted realistic user tasks:

| Priority / Weight | Task Description | Target Endpoint | HTTP Method |
|:---:|:---|:---|:---:|
| **Setup (`on_start`)** | CSRF Token Acquisition | `/api/auth/csrf-token` | `GET` |
| **Setup (`on_start`)** | User Authentication & Session Establishment | `/api/auth/login` | `POST` |
| **25%** | User Claim Listing | `/api/my-claims` | `GET` |
| **25%** | Policy Lookup & Prevalidation | `/api/claims/policy/<policy_number>` | `GET` |
| **20%** | Claim Details & Evidence Manifest | `/api/claims/<claim_id>` | `GET` |
| **15%** | Cross-Source Verification Summary | `/api/claims/<claim_id>/verification/summary` | `GET` |
| **10%** | Granular Comparison Findings | `/api/claims/<claim_id>/verification/findings` | `GET` |
| **5%** | Controlled Multipart Claim Ingestion | `/api/claims` | `POST` |

---

## 3. Strict Database & Infrastructure Safety Rules

> [!CAUTION]
> **Safety Guardrails:**
> 1. **Zero Production Database Writes:** Load tests NEVER target `data/claimsense.db`.
> 2. **Isolated Ephemeral Environments:** Load test instances operate against dedicated temporary databases (e.g. `data/test_load_isolated.db` or temporary directories) with pre-seeded test fixtures.
> 3. **Production Weights Invariance:** Model weights (`models/phase5/best.pt`) are strictly read-only.
> 4. **Uploads Protection:** Test uploads are written to isolated temporary directories (`data/test_load_uploads/`) and purged after execution.
> 5. **Controlled WAL Evaluation:** SQLite Write-Ahead Logging (`PRAGMA journal_mode=WAL;`) is evaluated exclusively in the isolated test database to determine concurrency improvements before any production rollout.

---

## 4. Execution Guide

### Automated End-to-End Orchestration (Recommended)
The automated runner starts an isolated Flask test server, pre-seeds test users and claims, executes the 10, 25, and 50 user load profiles sequentially, monitors CPU/memory via `psutil`, tests SQLite `DELETE` vs `WAL` modes, and outputs consolidated metrics:

```powershell
# Run the automated load test suite
.\.venv\Scripts\python.exe tests/load/run_load_test.py
```

### Manual Headless Execution via Locust CLI
To run Locust against an active server instance manually:

```powershell
# 1. Start an isolated server instance on port 5002
# 2. Run Locust headless (e.g. 25 users, 5/s spawn rate, 45 seconds)
.\.venv\Scripts\python.exe -m locust -f tests/load/locustfile.py --headless -u 25 -r 5.0 -t 45s --host http://127.0.0.1:5002 --csv runs/phase10/locust_25users --only-summary
```

---

## 5. Acceptance Criteria & Target SLAs

- **Mean Response Latency:** $< 500$ ms
- **95th Percentile Latency (p95):** $< 1000$ ms
- **Error Rate:** $< 0.1\%$ total failures
- **Database Concurrency:** Zero unhandled SQLite database lock errors (`sqlite3.OperationalError: database is locked`)
- **Data Integrity:** Zero corrupted records, zero lost committed transactions, strict cross-user data isolation.
