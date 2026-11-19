# ClaimSense AI — Phase 9.6: Candidate Model Decision Framework & Classification Matrix

**Document ID:** `DEC-PH9-6-DECISION-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.6 — Independent Benchmark Evaluation & Candidate Model Validation  
**Execution Date:** 2026-11-20  
**Status:** CANDIDATE CLASSIFICATION COMPLETE (ALL CANDIDATES QUARANTINED)  

---

## 1. Executive Summary & Decision Mandate

In strict accordance with Phase 9.6 Section 11:
- No candidate model is promoted to production during Phase 9.6.
- Candidate models are classified into objective governance categories based on measured evidence across the frozen independent benchmark.
- A candidate model exhibiting 0% structural crack recall cannot be classified as a successful resolution of the crack detection failure mode.

---

## 2. Master Candidate Decision Matrix (Track A: Frozen CarDD Test Set)

| Model Identifier | Evaluated Track / Cohort | Operational Precision ($\tau=0.25$) | Operational Recall ($\tau=0.25$) | Operational F1 | Standard mAP@50 | Standard mAP@50-95 | Crack Recall ($\tau=0.25$) | Crack AP@50 | CPU Latency (ms) | Governance Decision & Classification |
|---|---|---|---|---|---|---|---|---|---|---|
| **Production Baseline** (`models/phase5/best.pt`) | Track A (CarDD Test, 45 imgs) | 0.2264 | 0.2432 | 0.2345 | 0.1833 | 0.1161 | **0.0000 (0/13)** | 0.0138 | 57.11 ms | **Active Production Reference (Retained)** |
| **P9-T01-BEST** | Track A (CarDD Test, 45 imgs) | 0.1789 | 0.1486 | 0.1624 | 0.1869 | 0.1114 | **0.0000 (0/13)** | 0.0019 | 56.96 ms | **NO MEANINGFUL IMPROVEMENT (Quarantined)** |
| **P9-T02-BEST** | Track A (CarDD Test, 45 imgs) | **0.4194** | 0.0878 | 0.1453 | **0.2490** | **0.1581** | **0.0000 (0/13)** | **0.0203** | 90.65 ms | **IMPROVED BUT TRADE-OFFS PRESENT (Quarantined)** |

---

## 3. Detailed Classification Justifications

### 3.1 P9-T01 Candidate: `NO MEANINGFUL IMPROVEMENT`
- **Justification:** P9-T01 successfully replicates the production baseline under deterministic execution flags ($mAP@50 = 0.1869$ vs $0.1833$). However, operational precision ($0.1789$) and recall ($0.1486$) exhibit minor degradation compared to production, and structural crack recall remains at $0.0000\%$. As an experimental control, it validates reproducibility but provides no operational performance gain.

### 3.2 P9-T02 Candidate: `IMPROVED BUT TRADE-OFFS PRESENT`
- **Positive Attributes:**
  - Significant global ranking improvement: **mAP@50 increased by $+35.8\%$ relative** ($0.1833 \to 0.2490$).
  - Outstanding precision enhancement: **Operational precision rose $+85.2\%$ relative** ($0.2264 \to 0.4194$).
  - Massive false-positive suppression: **Total false positives dropped $85.4\%$** ($123 \to 18$).
  - Sub-threshold crack feature activation: **Crack AP@50 increased to $0.0203$** (highest among all evaluated models).
  - Glass shatter detection dramatically improved ($F1: 0.2400 \to 0.6087$).
- **Trade-Offs & Blockers:**
  - **Zero Crack Recall at Operational Threshold:** At $\tau=0.25$, Crack Recall remains at **$0.0000\%$ (0 of 13 detected)**. It does not meet the primary project objective of solving the crack detection failure mode.
  - **Operational Recall Drop:** At $\tau=0.25$, overall recall dropped from $0.2432$ to $0.0878$ due to the model's conservative prediction profile.
  - **Latency Increase:** CPU inference latency increased from $57.11\text{ ms}$ to $90.65\text{ ms}$ ($+58.7\%$), though it remains well beneath the $250\text{ ms}$ SLA ceiling.

---

## 4. Production Deployment Recommendation

- **Verdict:** **NO CANDIDATE PROMOTED TO PRODUCTION.**
- **Rationale:** `models/phase5/best.pt` remains the active production checkpoint. While P9-T02 demonstrates superior precision and higher overall mAP, promoting it would fail the project mandate of achieving reliable structural crack detection and would introduce severe operational recall regression without re-calibrated confidence thresholds.
- **Quarantine Action:** Both candidate checkpoints (`P9-T01-BEST` and `P9-T02-BEST`) remain strictly quarantined under `runs/phase9/retraining/`.
