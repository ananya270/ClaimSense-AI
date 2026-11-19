# ClaimSense AI — Phase 9.8: Final Model Selection Scorecard

**Document ID:** `SCR-PH9-8-SCORECARD-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.8 — Final Model Selection, Approval & Sign-off  
**Execution Date:** 2026-11-20  
**Status:** COMPLETE EVALUATION SCORECARD  

---

## 1. Master Model Selection Scorecard

| Evaluation Dimension | Production Baseline (`models/phase5/best.pt`) | Candidate P9-T02 (`P9-T02-BEST`) | Scorecard Status | Governance Analysis & Justification |
|---|---|---|---|---|
| **Checkpoint Integrity** | Hash verified: `49630ae8...` | Hash verified: `91a943a9...` | **PASS** | 100% cryptographic invariance verified before and after evaluation. |
| **mAP@50 Ranking** | 0.1833 | **0.2490 (+35.8%)** | **PASS** | Continuous PR-curve demonstrates superior global ranking. |
| **mAP@50-95 Regression** | 0.1161 | **0.1581 (+36.2%)** | **PASS** | Higher resolution provides tighter bounding box overlap across thresholds. |
| **Operational Precision** | 0.2264 | **0.4194 (+85.2%)** | **PASS** | Outstanding precision gain; spurious claim damage flags collapsed. |
| **Operational Recall** | **0.2432** | 0.0878 (-63.9%) | **FAIL** | Severe recall regression at uncalibrated operational threshold $\tau=0.25$. |
| **Structural Crack Detection** | **0.0000% (0/13)** | **0.0000% (0/13)** | **FAIL** | **CRITICAL FAILURE:** Both models fail to detect a single structural crack at $\tau=0.25$. |
| **Crack Feature Activation** | AP50: 0.0138 | **AP50: 0.0203 (+47.1%)** | **CONDITIONAL** | Sub-threshold feature activation confirmed, but probabilities remain below $0.25$. |
| **Six-Class Stability** | Stable baseline | Mixed (Glass Shatter star class, Dent/Scratch/Lamp/Tire recall dropped) | **CONDITIONAL** | Glass shatter excelled ($F1 +153\%$), but other classes suffered threshold penalties. |
| **False-Positive Behavior** | 123 FPs (2.73/img) | **18 FPs (0.40/img) (-85.4%)** | **PASS** | Dramatic reduction in false alarms across vehicle panels. |
| **False-Negative Behavior** | 112 FNs | 135 FNs (+20.5%) | **CONDITIONAL** | Higher FN rate caused by conservative probability output. |
| **Independent Generalization** | Low baseline | Verified on frozen test split; crack failure invariant | **CONDITIONAL** | Test split verified; crack failure persists across all independent cohorts. |
| **Inference Latency** | 57.11 ms | 90.65 ms (P95: 131.27 ms) | **PASS** | Fully compliant with ClaimSense AI real-time SLA ceiling ($<250\text{ ms}$). |
| **Scientific Reproducibility** | Deterministic baseline | Seed 42 replicated baseline within $0.66\%$ | **PASS** | Fully reproducible execution logs and parameter manifests. |
| **Operational Compatibility** | Active in production | Requires confidence re-calibration ($\tau \approx 0.15$) | **CONDITIONAL** | Tensor shape identical, but serving thresholds must be re-calibrated. |

---

## 2. Decision Category Evaluation

Section 3 requires selecting exactly one of five decision categories:

| Decision Category | Evaluation Against Empirical Evidence | Selection |
|---|---|---|
| **A. RETAIN EXISTING PRODUCTION MODEL** | **The candidate fails the primary project objective (crack detection) and regresses operational recall at $\tau=0.25$. Retaining the existing production checkpoint `models/phase5/best.pt` protects live claim verification workflows from uninspected damage.** | **SELECTED** |
| **B. CANDIDATE REJECTED — FURTHER RESEARCH REQUIRED** | Supported as a secondary classification: Candidate P9-T02 is rejected for production promotion and returned to research for class-loss weighting. | *Subsumed under A* |
| **C. CANDIDATE CONDITIONALLY APPROVED** | Rejected: Candidate cannot be conditionally approved for staging when operational crack recall is 0.0000%. | Rejected |
| **D. CANDIDATE APPROVED FOR STAGING** | Rejected: Fails operational recall and crack recall gates. | Rejected |
| **E. INSUFFICIENT EVIDENCE** | Rejected: Evidence is comprehensive and conclusive ($N=148$ test instances, 10 visual comparisons). | Rejected |

---

## 3. Official Category Selection

**FINAL DECISION: CATEGORY A — RETAIN EXISTING PRODUCTION MODEL**

- The active production model `models/phase5/best.pt` is retained as the serving engine.
- Candidate `P9-T02` is quarantined and rejected for immediate deployment.
- Candidate `P9-T02` is designated as the architectural baseline for Phase 10 retraining.
