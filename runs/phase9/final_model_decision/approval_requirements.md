# ClaimSense AI — Phase 9.8: Governance Approval Gates & Sign-off Requirements

**Document ID:** `APP-PH9-8-GATES-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.8 — Final Model Selection, Approval & Sign-off  
**Execution Date:** 2026-11-20  
**Status:** FORMAL GOVERNANCE SPECIFICATION  

---

## 1. Executive Governance Policy

In accordance with project governance rules:
> *"Do not interpret technical eligibility as project-owner approval. No model promotion, deployment, replacement, or production modification is authorized without explicit human sign-off."*

This document formalizes the sign-off hierarchy, decision authority, and prerequisite criteria required to officially close Phase 9 and authorize Phase 10 architectural retraining.

---

## 2. Sign-Off Authorization Hierarchy

| Role / Authority | Stakeholder | Decision Scope | Sign-Off Status |
|---|---|---|---|
| **Project Owner / Lead** | B.Tech Project Committee / Lead Owner | Final model selection, promotion approval, phase transition authorization. | **AWAITING EXPLICIT REVIEW** |
| **Lead ML Engineer** | AI Assistant / Model Developer | Technical audit, benchmark integrity verification, metric certification. | **CERTIFIED & SUBMITTED** |
| **Backend & Systems DevOps** | Production Infrastructure Lead | API compatibility, runtime latency SLA, database integrity assurance. | **CERTIFIED & UNTOUCHED** |

---

## 3. Prerequisite Conditions for Future Model Promotion (Phase 10 Gates)

To obtain promotion approval in future optimization cycles, a candidate checkpoint must satisfy all of the following non-negotiable criteria:

1. **Non-Zero Crack Recall Gate:**
   - Candidate must achieve **Operational Crack Recall $\ge 25.0\%$** at operational confidence threshold ($\tau = 0.25$, $\text{IoU} \ge 0.40$) on the frozen CarDD test set.
   - Zero-crack recall will trigger an automatic disqualification from production promotion.
2. **General Recall Preservation Gate:**
   - Overall operational recall must not regress by more than $5\%$ relative to the production baseline ($24.32\%$).
   - Operational recall on common classes (dent, scratch, lamp broken) must remain $\ge 15.0\%$.
3. **Precision & False-Positive Floor:**
   - Operational precision must remain $\ge 35.0\%$.
   - False-positive rate must not exceed $1.0\text{ FP/image}$ on clean vehicle panels.
4. **Inference Latency SLA:**
   - Mean single-image CPU inference latency must remain $\le 150\text{ ms}$ (P95 $\le 200\text{ ms}$).
5. **Multi-Source Cross-Verification Compatibility:**
   - Inference outputs must integrate seamlessly with `backend/services/vision/damage_detector.py` without requiring database schema changes or API contract breaks.

---

## 4. Current Approval Gate Verdict

- **Decision Submitted:** **CATEGORY A — RETAIN EXISTING PRODUCTION MODEL (`models/phase5/best.pt`).**
- **Candidate P9-T02 Action:** **REMAIN QUARANTINED UNDER `runs/phase9/retraining/P9-T02/`.**
- **Production Asset Action:** **ZERO REPLACEMENT / ZERO DEPLOYMENT.**
