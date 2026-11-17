# ClaimSense AI — Phase 8 Project Handover Document
## Engineering Architecture, Operational Runbooks & Governance Roadmap

**Document ID:** `HND-PH8-FINAL-001`  
**Date:** 2026-11-17  
**Audience:** ClaimSense AI Engineering Team, ML Operations, Claims Leadership  
**Program Scope:** Phase 8 Final Completion & Handover (Gates A–P)  
**Roadmap Boundary:** **Phase 8 ends strictly at Gate P. No Gate Q exists.**  
**Operational Status:** **SYSTEM IN STANDBY — LIVE SHADOW TRIAL NOT STARTED**

---

## 1. System Architecture State

```
+----------------------------------------------------------------------------------------------------+
|                                  SYSTEM ARCHITECTURE AT HANDOVER                                   |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|    POST /api/claims  ──► [ Synchronous Production Engine ]                                         |
|                                 ├──► models/phase5/best.pt (100% Authoritative)                     |
|                                 ├──► backend/database/claimsense.db (100% Authoritative)             |
|                                 └──► Customer Response & Official Receipt (<500ms SLA)             |
|                                                                                                    |
|                          [ Asynchronous Shadow Trial Gateway ]                                     |
|                                 ├──► Checked: shadow_mgr.is_enabled()                             |
|                                 │      └──► False by default (STANDBY)                             |
|                                 │      └──► Checked: runs/phase8/shadow_trial/KILL_SWITCH          |
|                                 │                                                                  |
|                                 ├──► Checked: circuit_breaker.can_dispatch()                       |
|                                 │      └──► Tripped if CPU/GPU >70%, Latency >200ms, Errors >=3    |
|                                 │                                                                  |
|                                 ├──► Bounded Queue: queue.Queue(maxsize=50)                        |
|                                 │      └──► Drops overflow safely without affecting caller         |
|                                 │                                                                  |
|                                 ├──► Isolated Single Worker Thread: ClaimSense-ShadowWorker        |
|                                 │      └──► Loads EXP02 independently (Zero singleton mutation)    |
|                                 │                                                                  |
|                                 └──► Telemetry DB: backend/database/shadow_telemetry.db (WAL Mode)  |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
```

---

## 2. Operational Runbooks for Future Trial Activation

### Runbook 1: Activating the 14-Day Live Shadow Trial (Requires Leadership Authorization)
1. Ensure the kill-switch flag does not exist:
   ```powershell
   Remove-Item "runs\phase8\shadow_trial\KILL_SWITCH" -ErrorAction SilentlyContinue
   ```
2. In Python or backend configuration, explicitly enable the trial manager:
   ```python
   from backend.services.vision.shadow_worker import get_shadow_manager
   shadow_mgr = get_shadow_manager()
   shadow_mgr.enable_trial()
   ```
3. Verify that `shadow_telemetry.db` is recording telemetry:
   ```powershell
   .venv\Scripts\python.exe scripts\run_daily_shadow_monitor.py --hours 1
   ```

### Runbook 2: Emergency Instant Rollback (Zero-Restart Kill-Switch)
If any anomaly, latency spike, or operational risk is detected during trial execution:
1. Touch the filesystem kill-switch flag:
   ```powershell
   New-Item -ItemType File -Path "runs\phase8\shadow_trial\KILL_SWITCH" -Force
   ```
2. The running backend will instantly (<1 ms) reject all new shadow jobs. Zero process restarts required.
3. Verify the production checkpoint remains untouched:
   ```powershell
   Get-FileHash models\phase5\best.pt -Algorithm SHA256
   # Must equal: 90D489E46FF8521EDFF88D522F0FEFFA164AC38A53B84700594C02A69E515565
   ```

### Runbook 3: Daily Health Monitoring Cadence
Execute the automated daily monitor every 24 hours:
```powershell
.venv\Scripts\python.exe scripts\run_daily_shadow_monitor.py --hours 24
```
* Generates a daily markdown audit report in `runs/phase8/shadow_trial/reports/`.
* Evaluates latency percentiles against targets ($\text{p50} \le 100$ ms, $\text{p99} \le 200$ ms).
* Raises an alert if `models/phase5/best.pt` SHA-256 changes.

### Runbook 4: Extracting Double-Blind Adjudication Queue
To extract divergent predictions for expert adjuster review:
```powershell
.venv\Scripts\python.exe scripts\extract_adjudication_queue.py --max-cases 200
```
* Generates `blind_adjudication_queue.csv` with randomized Model A vs Model B labels.
* Stores the unblinded ground-truth key in `runs/phase8/shadow_trial/adjudication/adjudication_sealed_key.json` (quarantined from adjusters).

---

## 3. Volume Strategy Decision Protocol

When scheduling the live trial, leadership must select between the two approved volume pathways:
* **Option A: Authorized Historical Replay Protocol**
  * Replays authentic CarDD test images and authorized Phase 7 customer uploads through the shadow queue with `is_offline_replay = 1`.
  * Fulfills the target quota of 200 cases to allow statistically significant Cohen's Kappa ($\kappa \ge 0.70$).
* **Option B: Formal Low-Volume Waiver Protocol**
  * Evaluates strictly live organic claims submitted during the 14 days (expected $N \approx 5\text{--}15$ disagreements).
  * Requires leadership sign-off on a low-volume statistical waiver before trial conclusion.

---

## 4. Governance Prerequisites for Any Future Production Promotion

EXP02 **CANNOT** be promoted to production without fulfilling the following mandatory criteria:
1. **Resolution of Structural Crack Recall (Risk 1):** Additional real-world training images featuring cracked bumpers and torn sheet metal must be acquired and fine-tuned into candidate weights to resolve the current 0.0% crack recall.
2. **Double-Blind Adjuster Superiority:** Expert adjusters must rate the candidate model equal or superior to the production baseline in $\ge 75\%$ of adjudicated disagreement cases.
3. **Clean-Vehicle False-Alarm Rate:** Clean vehicle false alarms must remain $\le 5\%$ across live traffic.
4. **Formal Executive Sign-Off:** Signed authorization from ML Engineering and Insurance Operations leadership.

---

## 5. Handover Certification

* **Program Status:** **PHASE 8 CONCLUDED AT GATE P.**
* **Codebase & Asset Integrity:** 100% verified, clean, and invariant.
* **Handover Authority:** Autonomous Engineering Governance (DeepMind)
