# ClaimSense AI — Phase 9.7: Promotion Readiness Scorecard

**Document ID:** `SCR-PH9-7-SCORE-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.7 — Production Model vs Candidate Comparative Analysis & Promotion Readiness Review  
**Execution Date:** 2026-11-20  
**Candidate Evaluated:** `P9-T02-BEST` (`runs/phase9/retraining/P9-T02/checkpoints/best.pt`)  
**Production Reference:** `PROD-BASELINE` (`models/phase5/best.pt`)  
**Status:** PROMOTION READINESS EVALUATED — CANDIDATE NOT PROMOTION-READY  

---

## 1. Master Promotion Readiness Scorecard

| Evaluation Dimension | Status | Verified Evidence | Remaining Risk |
|---|---|---|---|
| **Checkpoint Integrity** | **PASS** | Pre/post SHA-256 hashes 100% invariant across all checkpoints (`models/phase5/best.pt`: `49630ae8...`, `P9-T02`: `91a943a9...`). | Zero risk of weight tampering. |
| **Independent Evaluation Provenance** | **PASS** | Verified on frozen held-out CarDD test split ($N=45$ images, 148 annotations) with strict separation from training. | Provenance certified. |
| **Overall Detection Performance** | **PASS** | Global ranking mAP@50 improved by **$+35.8\%$ relative** ($0.1833 \to 0.2490$); mAP@50-95 rose **$+36.2\%$** ($0.1161 \to 0.1581$). | None. Continuous PR-curve demonstrates superior ranking. |
| **Structural Crack Detection** | **FAIL** | **Operational recall is $0.0000\%$ (0 of 13 detected)** at $\tau=0.25$. While continuous AP@50 increased $+47.1\%$, no crack proposal reaches the $0.25$ operational threshold. | **CRITICAL BLOCKER:** Model fails primary project objective of detecting structural cracks. |
| **Six-Class Performance** | **CONDITIONAL** | Glass shatter improved dramatically (F1 $+153\%$, AP50 $+125\%$). However, dent and scratch recall regressed at uncalibrated $\tau=0.25$. | Potential claim dispute risk on subtle dents/scratches without threshold calibration. |
| **False-Positive Behavior** | **PASS** | Spurious detections plummeted by **$85.4\%$** (123 FPs in production $\to$ 18 in P9-T02), raising precision from $0.2264$ to **$0.4194$ (+85.2%)**. | Highly favorable for reducing spurious claim repair costs. |
| **False-Negative Behavior** | **CONDITIONAL** | Total false negatives increased from 112 to 135 (+20.5%) due to applying a rigid $\tau=0.25$ threshold to a conservative model. | Uninspected vehicle damage if deployed without threshold adjustment. |
| **Generalization** | **CONDITIONAL** | Strong precision generalization; however, minority sample size ($N_{\text{crack}}=13$) limits statistical certainty on crack recovery. | Requires larger dedicated crack cohort for Phase 10. |
| **Latency & Resources** | **PASS** | Mean CPU inference latency is **$90.65\text{ ms}$** (P95: $131.27\text{ ms}$), well within the $250\text{ ms}$ SLA ceiling. Throughput is $11.03\text{ FPS}$. | Acceptable CPU compute overhead (+33.5 ms vs production). |
| **Reproducibility** | **PASS** | Deterministic training with fixed seed 42 replicated baseline performance within $0.66\%$ mAP margin. | Full scientific reproducibility achieved. |
| **Dataset Integrity** | **PASS** | All source dataset YAMLs, manifests, and image directories verified 100% invariant with zero test leakage. | Verified dataset protection. |
| **Operational Compatibility** | **CONDITIONAL** | Candidate uses identical YOLOv8 input tensor structure, but requires confidence threshold re-calibration ($\tau \approx 0.15$) before deployment. | Requires Project Owner approval for threshold adjustment. |

---

## 2. Decision Synthesis & Category Classification

According to the decision framework established in Section 10:

- [ ] **Category A — NOT BETTER THAN PRODUCTION**
- [x] **Category B — IMPROVED BUT NOT PROMOTION-READY**
- [ ] **Category C — CONDITIONALLY PROMISING**
- [ ] **Category D — ELIGIBLE FOR PHASE 9.8 FINAL REVIEW**

### Formal Justification for Category B:
Candidate `P9-T02` achieves undeniable engineering improvements: it increases global mAP@50 by $+35.8\%$, elevates operational precision by $+85.2\%$, eliminates $85.4\%$ of false alarms, and demonstrates a $+47.1\%$ gain in sub-threshold crack feature representations. 

**However**, because it achieves **$0.0000\%$ operational recall on structural cracks (0 of 13 detected)** and exhibits operational recall regression at the rigid uncalibrated threshold $\tau=0.25$, **it fails the core Phase 9 requirement for structural crack detection**. It cannot be declared promotion-ready.
