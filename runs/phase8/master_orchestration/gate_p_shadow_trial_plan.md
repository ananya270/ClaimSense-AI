# ClaimSense AI — Gate P 14-Day Staged Shadow Trial Execution Plan

**Document ID:** `PLN-PH8-GATE-P-SHADOW-001`  
**Date:** 2026-11-17  
**Governing Standard:** `acquisition_specification.md` v1.1-ACTIVE  
**Trial Status:** **PREPARED — AWAITING EXPLICIT HUMAN AUTHORIZATION (NOT STARTED)**  
**Trial Duration:** 14 Consecutive Calendar Days  
**Authoritative Production Checkpoint:** `models/phase5/best.pt` (SHA-256: `90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565`)  
**Shadow Candidate Checkpoint:** `runs/phase8/domain_adaptation/exp02_rare_class/weights/best.pt` (SHA-256: `68e2b58ec7759427808621debc9a8d725a9e4c1fbc57a2102cd239a8ca14f006`)

---

## 1. Executive Trial Objective & Boundary Governance

The objective of this 14-day staged shadow trial is to evaluate the real-world operational performance of the Phase 8 EXP02 candidate model against authentic live claim photographic streams under true production conditions, **without altering production behavior or impacting policyholders**.

### Core Operational Invariants:
1. **Production Model Remains Authoritative:** Checkpoint `models/phase5/best.pt` exclusively powers all claim determinations, automated damage analyses, receipts, fraud evaluations, and financial payout estimates.
2. **Strict Shadow Isolation:** EXP02 runs asynchronously in an isolated, non-blocking background worker thread. Its outputs are persisted strictly to an isolated shadow telemetry store (`runs/phase8/shadow_trial/shadow_telemetry.db`).
3. **Zero Mutation of Official Records:** Under zero circumstances can EXP02 predictions modify claim status, adjust payout figures, alter database tables (`claims`, `claim_images`, `vehicle_damage_analyses`, `vehicle_damage_detections`), or write to official customer receipts.
4. **No Promotion Permitted During Trial:** EXP02 remains strictly in shadow mode throughout the full 14 calendar days. Automatic promotion is strictly prohibited.
5. **No Extension Beyond Gate P:** Gate P is the final gate of Phase 8. No Gate Q will be created.

---

## 2. Infrastructure & Ingestion Architecture

```
+----------------------------------------------------------------------------------------------------+
|                                SHADOW TRIAL EXECUTION ARCHITECTURE                                 |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|   Customer Claim Submission (POST /api/claims)                                                     |
|            │                                                                                       |
|            ├──► [Synchronous Primary Path]                                                         |
|            │    │                                                                                  |
|            │    ├──► Authoritative Production Model (models/phase5/best.pt)                        |
|            │    ├──► DB Persistence: vehicle_damage_analyses, claimsense.db                         |
|            │    └──► Customer Response & Official Receipt (<500ms SLA)                             |
|            │                                                                                       |
|            └──► [Asynchronous Shadow Path - Non-Blocking Queue]                                    |
|                 │                                                                                  |
|                 ├──► Decoupled Background Worker (Thread / Queue)                                  |
|                 ├──► Hardware Guard: Circuit Breaker Check (CPU/GPU < 70%)                         |
|                 ├──► Shadow Candidate Model (exp02_rare_class/weights/best.pt)                     |
|                 ├──► Operational Parameters: conf=0.25, iou=0.45, imgsz=640                       |
|                 └──► Isolated Telemetry DB: shadow_telemetry.db (NO PRODUCTION DB ACCESS)          |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
```

### Technical Isolation Guardrails:
* **Decoupled Invocation:** The shadow worker is triggered via an in-memory queue or post-response background thread (`threading.Thread(target=_shadow_inference_worker, daemon=True)`).
* **Latency Budget:** Inference latency target on GPU is **$\le 200$ ms/image**. If a single shadow inference exceeds 200 ms, a performance canary is logged.
* **Fail-Safe Exception Isolation:** Any exception occurring in the shadow pipeline is caught, logged to shadow error telemetry, and discarded without propagating to the primary Flask request context.

---

## 3. Trial Phases & Milestone Timeline

The 14-day trial runs for 14 consecutive calendar days upon explicit human activation:

| Trial Phase | Calendar Window | Operational Focus | Mandatory Milestone Gate |
| :--- | :---: | :--- | :--- |
| **Phase A: Pre-Trial Verification** | Day 0 | Checkpoint hash verification, isolated DB creation, circuit breaker self-test. | Human Authorization Sign-Off. |
| **Phase B: Ramp-Up & Stability** | Days 1–3 | 10% to 50% shadow sampling; latency validation; zero production impact verification. | 72-Hour Stability Check (0 production errors). |
| **Phase C: Full Stream Shadowing** | Days 4–10 | 100% shadow ingestion of live claim image uploads; telemetry logging. | Mid-Trial Disagreement Audit. |
| **Phase D: Adjudication Cohort** | Days 11–14 | Assembly of disagreement cohort (target up to 200 claims); canary glare checks. | Adjudication Blind Package Locked. |
| **Phase E: Post-Trial Sign-Off** | Day 15 | Formal engineering review; adjuster double-blind findings; final promotion verdict. | Executive Governance Sign-Off. |

---

## 4. Human Adjudication & Disagreement Target

* **Disagreement Cohort Target:** Target up to **200 real-world claim images** exhibiting prediction disagreement between Production Baseline and EXP02.
* **Integrity Mandate on Sample Counts:** **Never fabricate sample counts.** If live customer claim volume during the 14-day window yields fewer than 200 genuine disagreement cases (e.g. 85 or 120 claims), the actual observed count will be audited and reported without artificial padding or synthetic inflation.
* **Mandatory Review Categories:**
  1. *Suspected Structural Cracks:* Mandatory review of claims involving bumper tears or fractures (compensating for Risk 1: Zero Crack Recall).
  2. *Severe Disagreements:* Claims where one model predicts high damage ($\tau \ge 0.50$) and the other predicts 0 defects.
  3. *Daylight Glare False-Alarm Canaries:* Regular routing of known clean vehicle walkarounds to confirm zero false alarms in production conditions.
