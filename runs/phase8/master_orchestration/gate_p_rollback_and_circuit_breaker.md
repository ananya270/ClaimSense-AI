# ClaimSense AI — Gate P Rollback & Circuit Breaker Specification

**Document ID:** `SAF-PH8-GATE-P-CB-001`  
**Date:** 2026-11-17  
**Governing Standard:** `acquisition_specification.md` v1.1-ACTIVE  
**System Role:** Failsafe Isolation, Automated Decoupling & Instant Rollback  
**Production Checkpoint Status:** **100% UNTOUCHED (`90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565`)**

---

## 1. Circuit Breaker Architecture & State Machine

To guarantee that the shadow trial cannot destabilize the production backend, an automated hardware and latency circuit breaker governs the background worker:

```
+----------------------------------------------------------------------------------------------------+
|                                    CIRCUIT BREAKER STATE MACHINE                                   |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|    [ CLOSED: Normal Operation ]                                                                    |
|         │                                                                                          |
|         ├──► Trigger: CPU/GPU > 70% OR Latency > 200ms OR 3 Consecutive Errors                    |
|         │                                                                                          |
|         ▼                                                                                          |
|    [ OPEN: Tripped / Shadow Disabled ] ──► Shadow worker terminates immediately.                   |
|         │                                  Production traffic completely isolated.                 |
|         │                                  Zero shadow inference executed.                         |
|         │                                                                                          |
|         ├──► After 15-minute cooldown & automated resource check                                   |
|         ▼                                                                                          |
|    [ HALF-OPEN: Canary Probe ] ──► Runs 1 test probe inference on dummy tensor.                    |
|         │                                                                                          |
|         ├──► Probe Latency < 100ms & Hardware < 50% ──► Transitions to [ CLOSED ]                 |
|         └──► Probe Fails ──► Re-enters [ OPEN ] for 60 minutes + Alert Escalation                  |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
```

### Verified Threshold Trip Conditions:
* **Hardware Overload:** Host CPU utilization $> 70\%$ OR GPU utilization $> 70\%$.
* **Latency Budget Exhaustion:** Single shadow inference latency $> 200$ ms.
* **Consecutive Error Breaker:** 3 consecutive unhandled inference exceptions.
* **Memory Leak Safeguard:** Peak GPU VRAM $> 3000$ MB.
* **Integrity Guard:** Any attempted write to `claimsense.db` immediately aborts the worker.

---

## 2. Emergency Instant Rollback Procedure

If any anomaly or instability is detected, the trial can be terminated instantly in under 10 seconds:

### Step 1: Immediate Shadow Decoupling
Set environment variable or config toggle:
```bash
export CLAIMSENSE_SHADOW_TRIAL_ENABLED=False
```
*(Or in `backend/config.py`: `SHADOW_TRIAL_ENABLED = False`).*
The application instantly skips shadow worker spawning. Zero restarts required.

### Step 2: Terminate Detached Worker
If running as a background worker thread or process:
```powershell
# Verify no orphaned shadow worker process exists
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*shadow*" } | Stop-Process -Force
```

### Step 3: Verify Production Baseline Integrity
Verify the authoritative production checkpoint has remained untouched:
```powershell
Get-FileHash models\phase5\best.pt -Algorithm SHA256
# Expected: 90D489E46FF8521EDFF88D522F0FEFFA164AC38A53B84700594C02A69E515565
```

### Step 4: Verify Database Immutability
Confirm `backend/database/claimsense.db` contains zero shadow artifacts:
```powershell
.venv\Scripts\python.exe -c "
import sqlite3
con = sqlite3.connect('backend/database/claimsense.db')
tables = [r[0] for r in con.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()]
print('Active production tables:', tables)
assert 'shadow_telemetry' not in tables, 'CRITICAL: Shadow tables leaked into production database!'
"
```

---

## 3. Non-Invasive Safety Test Execution Log

The circuit breaker and immutability controls were tested non-invasively on 2026-11-17 via `scratch/test_shadow_safety_mechanisms.py`:

| Verification Step | Test Scope | Result | Certification |
| :--- | :--- | :---: | :---: |
| **Check 1** | Production Checkpoint SHA-256 (`models/phase5/best.pt`) | `90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565` | **MATCH OK** |
| **Check 2** | EXP02 Candidate SHA-256 (`exp02_rare_class/weights/best.pt`) | `68e2b58ec7759427808621debc9a8d725a9e4c1fbc57a2102cd239a8ca14f006` | **MATCH OK** |
| **Check 3** | Production Database Presence (`backend/database/claimsense.db`) | Verified | **PASS** |
| **Check 4** | Circuit Breaker CPU > 70% Overload Trip | State -> OPEN | **PASS** |
| **Check 5** | Circuit Breaker GPU > 70% Overload Trip | State -> OPEN | **PASS** |
| **Check 6** | Circuit Breaker Latency > 200ms Budget Trip | State -> OPEN | **PASS** |
| **Check 7** | Circuit Breaker Consecutive Error Trip | State -> OPEN | **PASS** |
| **Check 8** | Database Immutability Post-Test | 0 Modifications | **PASS** |
