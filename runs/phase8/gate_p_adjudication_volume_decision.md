# ClaimSense AI — Gate P Adjudication Volume Decision Framework

**Document ID:** `DEC-PH8-GATE-P-VOL-001`  
**Date:** 2026-11-17  
**Governing Standard:** `acquisition_specification.md` v1.1-ACTIVE  
**Issue:** Disparity Between Production Database Volume and 200-Case Target  
**Status:** **FORMAL DUAL-PATH FRAMEWORK APPROVED**

---

## 1. Forensic Problem Statement

A forensic audit of the ClaimSense AI production database revealed:
* **Total Claims in Production Database:** Exactly **12 claims**.
* **Estimated Organic Submissions (14-Day Window):** 10 to 20 claims.
* **Expected Prediction Concordance:** $80\%\text{--}90\%$ agreement between Production Baseline and EXP02.
* **Expected Organic Disagreement Yield:** Only **1 to 3 cases**.
* **Target Quota for Human Adjudication:** Up to **200 cases**.

### Mandatory Scientific & Compliance Constraints:
1. **Zero Fabrication Rule:** Specification v1.1 Rule 7 strictly prohibits fabricating annotations, claims, synthetic bounding boxes, or artificial telemetry records.
2. **No Data Snooping / Leakage:** Repeatedly cycling the same 12 claim photographs or using frozen validation benchmarks (Gate O 44-image set) is strictly prohibited.
3. **Statistical Power Prerequisite:** Inter-rater reliability (Cohen's $\kappa \ge 0.70$) and model superiority assessments require a statistically viable sample size ($N \ge 30$, target $N \approx 200$).

---

## 2. Approved Dual-Path Decision Framework

To resolve the volume deficit without compromising scientific integrity, two distinct paths are codified:

```
+----------------------------------------------------------------------------------------------------+
|                                ADJUDICATION VOLUME DUAL-PATH DECISION                              |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|    Selectable by Human Engineering Authority prior to Live Trial Initiation:                       |
|                                                                                                    |
|    [ OPTION A: Authorized Historical Replay Protocol ]                                             |
|         │                                                                                          |
|         ├──► Ingest authorized pool of authentic, verified vehicle damage images                    |
|         │    (CarDD independent collision test partition + unblinded customer upload pool)         |
|         ├──► Ingested through shadow queue using offline replay flags                              |
|         ├──► Strictly partitioned: Excluded from live organic SLA metrics                          |
|         └──► Fulfills target quota of 200 cases with genuine physical damage diversity             |
|                                                                                                    |
|    [ OPTION B: Formal Low-Volume Waiver Protocol ]                                                 |
|         │                                                                                          |
|         ├──► Ingest strictly live organic submissions during the 14 calendar days                  |
|         ├──► Accept observed sample size (e.g. N = 5 to 15 disagreement cases)                     |
|         ├──► No synthetic padding or offline replaying injected                                    |
|         └──► Issues formal waiver: Results treated as qualitative / directional;                   |
|              Mandates extended shadow observation before any future promotion decision             |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
```

---

## 3. Detailed Specification of Options

### Option A: Authorized Historical Replay Protocol (Recommended for Statistical Rigor)
* **Data Sources:**
  1. CarDD Collision Test Split (45 images, 45 verified scenes).
  2. Gate L Qualified Secondary Pool (60 daylight walkaround vehicle images, distinct from Dev split).
  3. Pre-Phase 8 Archived Customer Submissions (unblinded historical pool).
* **Protocol Controls:**
  * Replay jobs are tagged with `is_offline_replay = 1` in `shadow_telemetry.db`.
  * Replayed images are fed into the shadow queue sequentially through the single worker thread.
  * Replay metrics are analyzed separately from live customer submissions to ensure zero skew of real-world SLA or latency baselines.
  * Adjusters evaluate anonymized Model A vs Model B outputs under full double-blind conditions.

### Option B: Formal Low-Volume Waiver Protocol (Recommended for Pure Live Isolation)
* **Operational Rules:**
  * Zero historical replaying. The trial ingests strictly what policyholders submit to `POST /api/claims`.
  * At Day 14, `scripts/extract_adjudication_queue.py` extracts all available disagreement cases (e.g., $N=4$ or $N=8$).
  * The final report documents the exact sample size $N$ with a formal statistical limitation disclosure.
  * EXP02 cannot be promoted to production solely on a low-volume cohort; an extension waiver or staged canary rollout is required.

---

## 4. Engineering Recommendation

Antigravity recommends **Option A** if human leadership requires statistically certified superiority ($\kappa \ge 0.70$) at the conclusion of Phase 8, or **Option B** if leadership prioritizes zero synthetic/replay traffic entering the shadow database during the live 14 calendar days.

Both options adhere 100% to Specification v1.1 by eliminating sample fabrication and preserving complete provenance.
