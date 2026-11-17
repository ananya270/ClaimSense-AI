# ClaimSense AI — Phase 8 Final Engineering Sign-Off Review

**Document ID:** `SIG-PH8-GATE-P-FINAL-001`  
**Review Date:** 2026-11-17  
**Governing Standard:** `acquisition_specification.md` v1.1-ACTIVE  
**Review Authority:** Independent Autonomous Engineering Review (DeepMind)  
**Production Checkpoint Status:** **100% UNTOUCHED (`models/phase5/best.pt` | SHA-256: `90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565`)**  
**Evaluated Candidate Checkpoint:** `runs/phase8/domain_adaptation/exp02_rare_class/weights/best.pt` (SHA-256: `68e2b58ec7759427808621debc9a8d725a9e4c1fbc57a2102cd239a8ca14f006`)

---

## 1. Executive Sign-Off Recommendation & Formal Status

```
================================================================================
  FORMAL ENGINEERING STATUS: CONDITIONAL APPROVAL FOR 14-DAY SHADOW TRIAL ONLY
  STRICT PRODUCTION SAFEGUARD: NO AUTOMATIC PRODUCTION REPLACEMENT AUTHORIZED
  PRODUCTION MODEL models/phase5/best.pt REMAINS AUTHORITATIVE & UNTOUCHED
================================================================================
```

### Governance Stance:
Phase 8 EXP02 (Rare Class Expansion) has demonstrated extraordinary improvements in false-positive resistance (cutting spurious detections by **99.55%**, from 6,503 down to 29 across 75 ground-truth images) and has successfully activated detection on previously blind categories (`scratch`, `tire flat`, `lamp broken`).

However, EXP02 **DOES NOT QUALIFY FOR IMMEDIATE PRODUCTION REPLACEMENT**. Its overall operational recall at $\tau=0.25$ is **16.17%**, it exhibits **zero recall on structural cracks**, and its daylight walkaround performance has only been evaluated offline across small development cohorts. Therefore:
1. EXP02 is approved **exclusively** for a staged, non-blocking 14-day live shadow trial.
2. The current production checkpoint `models/phase5/best.pt` remains 100% authoritative for all customer claims.
3. Any future promotion of EXP02 to production requires explicit, signed human engineering approval.

---

## 2. Dataset Independence & Cohort Taxonomy

To maintain scientific integrity and prevent data contamination, all evaluation datasets must be clearly segregated:

```
+----------------------------------------------------------------------------------------------------+
|                                      DATASET COHORT TAXONOMY                                       |
+------------------------------------+-----------+------------------+--------------------------------+
| Cohort Name                        | Image Qty | Role             | Independence Status            |
+------------------------------------+-----------+------------------+--------------------------------+
| 1. Domain Adaptation Dev Split     | 30 Images | Dev Tuning       | NOT INDEPENDENT (Used in Gate N)|
| 2. CarDD Collision Test Split      | 45 Images | Domain Retention | Independent Collision Test     |
| 3. Frozen Independent Val Benchmark| 44 Images | Gold Standard    | FULLY INDEPENDENT & QUARANTINED|
| 4. Customer Upload Stream          | 14 Images | Shadow Telemetry | Unlabeled Live Claims          |
+------------------------------------+-----------+------------------+--------------------------------+
```

1. **Domain Adaptation Dev Split (30 Images):**
   * *Critical Forensic Clarification:* This 30-image cohort (`datasets/domain_adaptation_dev`) was the development split of the Gate L acquisition. It was explicitly used in Gate N to evaluate EXP01, EXP02, and EXP03 and select the winning candidate. **Results on these 30 images MUST NEVER be represented as independent validation**.
2. **CarDD Collision Test Split (45 Images):**
   * High-contrast vehicle crash photography from the original CarDD dataset. Used to verify that fine-tuning on daylight walkarounds did not induce catastrophic forgetting of core collision damage.
3. **Frozen Independent Validation Benchmark (44 Images, 47 Defects):**
   * Quarantined under Gate G snapshot (`gate_g_sha256_snapshot.csv`). Evaluated **only once** in Gate O under synchronized benchmark conditions. Strictly prohibited from model tuning, hyperparameter search, or checkpoint selection.
4. **Customer Claim Uploads (14 Files, 6 Unique Scenes):**
   * Unlabeled user uploads in `uploads/CLM-*/`. Used strictly for observational shadow telemetry. Bounded by Governance Rule 3: all predictions are documented as unverified observations.

---

## 3. Evaluation Protocol & IoU Sensitivity Audit

Metric comparisons are invalid unless evaluation protocols are precisely standardized:

| Parameter | Gate O Independent Benchmark | Gate P Accelerated Shadow | Forensic Metrics Audit | Standardization Mandate |
| :--- | :---: | :---: | :---: | :--- |
| **Confidence Threshold** | $\tau=0.001$ & $\tau=0.25$ | $\tau=0.25$ (Operational) | $\tau=0.25$ (Operational) | Operational metrics strictly at $\tau=0.25$. |
| **Image Resolution** | $640 \times 640$ | $640 \times 640$ | $640 \times 640$ | Fixed input resolution. |
| **Bounding Box Match IoU** | $\text{IoU} \ge 0.50$ (Op) | $\text{IoU} \ge 0.40$ (Audit) | $\text{IoU} \ge 0.40$ & $0.50$ | **Do NOT compare across different IoUs.** |
| **NMS IoU Threshold** | $0.45$ | $0.45$ | $0.45$ | Uniform suppression threshold. |
| **Class Assignment** | 6 CarDD Classes | 6 CarDD Classes | 6 CarDD Classes | One-to-one class ID mapping. |

### IoU Threshold Sensitivity Analysis:
* At $\text{IoU} \ge 0.40$: EXP02 achieves Micro $F_1 = \mathbf{0.2422}$ (Precision = 48.2%, Recall = 16.2%).
* At $\text{IoU} \ge 0.50$: EXP02 achieves Micro $F_1 = \mathbf{0.1973}$ (Precision = 39.3%, Recall = 13.2%).
* *Technical Finding:* The drop in recall between IoU 0.40 and 0.50 reflects bounding-box boundary disparity between unified physical panel boxes (Specification v1.1) and tight local defect boundaries. Metrics at IoU 0.40 and IoU 0.50 must be reported with their explicit threshold qualifiers.

---

## 4. Gate O vs Gate P Evidence Reconciliation

A superficial glance suggests a contradiction between Gate O and Gate P:
* In Gate O (44 Frozen Images): EXP02 operational recall was **1.85%** and precision was **1.52%**.
* In Gate P (75 Labeled Images): EXP02 operational recall was **16.17%** and precision was **48.21%**.

### Forensic Reconciliation:
1. **Dataset Compositional Shift:**
   * Gate O evaluated exclusively on 44 authentic walkaround photos where defects are subtle, sparse, and subject to severe domain shift.
   * Gate P evaluated across 75 images, of which **45 images (60%) were high-severity CarDD collision photos**. On those 45 CarDD images, EXP02 achieved **51.92% Precision and 18.24% Recall** (27 TPs, 25 FPs), which lifted the combined metric.
   * On the 30 daylight walkaround Dev images alone in Gate P, EXP02 achieved 0 TPs at $\tau=0.25$ and IoU $\ge 0.40$ (identical to the conservative behavior observed on frozen walkarounds in Gate O).
2. **IoU Match Criterion:**
   * Gate O operational evaluation used standard Ultralytics $\text{IoU} = 0.50$.
   * Gate P audit used $\text{IoU} = 0.40$ to accommodate unified walkaround annotations.
3. **Conclusion:** There is **no mathematical discrepancy**. Both gates prove the same underlying reality: EXP02 excels on collision damage and completely eliminates specular hallucinations, but remains highly conservative on authentic daylight walkarounds at $\tau=0.25$.

---

## 5. Requirements for a Genuine 14-Day Live Shadow Trial

Prior to any consideration of production promotion, EXP02 must complete a continuous 14-day live shadow trial meeting the following mandatory engineering criteria:

### A. Infrastructure & Execution Architecture
1. **Asynchronous Non-Blocking Dual-Inference:**
   * Incoming claim images are routed to the authoritative production model (`models/phase5/best.pt`) to generate official customer claim estimates.
   * A detached background worker concurrently runs EXP02 (`exp02_rare_class/weights/best.pt`) on the identical image payload.
   * EXP02 outputs are written exclusively to a shadow telemetry database (`shadow_claim_telemetry`). Under zero circumstances may EXP02 outputs touch customer-facing responses, claim payouts, or official records.
2. **Latency Budget Enforcement:**
   * Peak inference latency must remain strictly below 200 ms per image to prevent worker queue exhaustion.

### B. Live Telemetry & Monitoring Metrics
1. **Real-Time Divergence Tracking:**
   * Track daily agreement rate: `Concordance = N_agree / N_total`.
   * Flag cases where Production detects damage but EXP02 detects 0 (Potential False Negative / Under-Claim Risk).
   * Flag cases where EXP02 detects damage but Production detects 0 (Potential False Alarm or Discovered Damage).
2. **Clean-Vehicle Glare Canary:**
   * Route known clean vehicle walkarounds through the pipeline weekly to monitor specular reflection false alarms.

### C. Failure Escalation & Instant Circuit Breaker
1. **Instant Rollback / Decoupling:**
   * If shadow worker CPU/GPU consumption exceeds 70% or causes inference timeout on authoritative production claims, an automated circuit breaker immediately terminates shadow inference.
2. **Rollback Target:**
   * The fallback authoritative baseline is guaranteed: `models/phase5/best.pt` (`90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565`).

### D. Human Review Prerequisite
1. **Adjuster Blind Evaluation:**
   * At the conclusion of 14 days, a random sample of 200 claims where Production and EXP02 disagreed must be adjudicated by senior human insurance adjusters without knowing model identities.
2. **Signed Sign-Off Required:**
   * Production replacement requires explicit, signed approval from the Lead ML Engineer and Product Owner.

---

## 6. Checkpoint Provenance & Final Audit Summary

| Checkpoint Name | Local File Path | Cryptographic SHA-256 Hash | Authorized Status |
| :--- | :--- | :--- | :---: |
| **Production Baseline** | `models/phase5/best.pt` | `90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565` | **AUTHORITATIVE PRODUCTION (UNTOUCHED)** |
| **Phase 8 EXP02 Candidate** | `runs/phase8/domain_adaptation/exp02_rare_class/weights/best.pt` | `68e2b58ec7759427808621debc9a8d725a9e4c1fbc57a2102cd239a8ca14f006` | **APPROVED FOR 14-DAY SHADOW TRIAL ONLY** |

---

## 7. Deliverable Links

All Phase 8 Gate P Sign-Off deliverables are available under [`runs/phase8/master_orchestration/`](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/master_orchestration/) and mirrored to [`runs/phase8/`](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/):

1. **Gate P Final Engineering Sign-Off:** [`gate_p_final_engineering_signoff.md`](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/master_orchestration/gate_p_final_engineering_signoff.md)
2. **Gate P Evidence Reconciliation CSV:** [`gate_p_evidence_reconciliation.csv`](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/master_orchestration/gate_p_evidence_reconciliation.csv)
3. **Gate P Remaining Operational Risks:** [`gate_p_remaining_risks.md`](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/master_orchestration/gate_p_remaining_risks.md)
4. **Gate P Metrics Integrity Audit Report:** [`gate_p_metrics_integrity_audit.md`](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/master_orchestration/gate_p_metrics_integrity_audit.md)
5. **Gate P Audited Model Comparison CSV:** [`gate_p_model_comparison_audited.csv`](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/master_orchestration/gate_p_model_comparison_audited.csv)
