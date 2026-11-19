# ClaimSense AI — Phase 9.4: Multi-Metric Model Selection & Safety Policy

**Document ID:** `REP-PH9-4-POLICY-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.4 — Training Strategy & Hyperparameter Optimization Planning  
**Governing Standard:** Gate P Final Operational Review & Phase 9 Evaluation Protocol  
**Status:** MODEL SELECTION GOVERNANCE SPECIFIED  

---

## 1. Executive Summary & Core Policy Mandate

Model selection must **never** be based on a single composite metric or simple precision score. In Phase 8, model EXP02 achieved high precision ($0.4821$) and drastically reduced false alarms ($29\text{ FP}$ vs $6,503\text{ FP}$), but it achieved this by severely suppressing sensitivity—detecting **$0 / 14$ structural cracks** and dropping aggregate operational recall to a catastrophic **$16.17\%$**. Consequently, EXP02 was quarantined and blocked from promotion at Gate P.

This policy establishes strict, multi-dimensional gating criteria ensuring that no model can be promoted if it achieves precision gains at the expense of safety-critical defect recall.

---

## 2. Multi-Dimensional Metric Evaluation Framework

Every candidate model checkpoint produced in future optimization experiments must be evaluated across four mandatory engineering tiers:

```
+-------------------------------------------------------------------------------------------------+
| TIER 1: DETECTION QUALITY & GENERALIZATION (Track A)                                            |
|   - Mean Average Precision at IoU=0.50 (mAP50)                                                  |
|   - Mean Average Precision across IoU 0.50 to 0.95 (mAP50-95)                                   |
|   - Precision, Recall, Macro-F1 across all 6 classes                                            |
+-------------------------------------------------------------------------------------------------+
| TIER 2: SAFETY-CRITICAL CRACK SENSITIVITY (Operational Track B at tau=0.25, IoU >= 0.40)        |
|   - Structural Crack Recall (Crack FN count must be minimized)                                  |
|   - Structural Crack Precision and Crack F1-Score                                               |
|   - Crack-to-Scratch Misclassification Rate                                                     |
+-------------------------------------------------------------------------------------------------+
| TIER 3: COMPREHENSIVE DAMAGE-CLASS ROBUSTNESS                                                   |
|   - Dent Recall (Must maintain >= 20.0%)                                                        |
|   - Scratch Recall (Must maintain >= 15.0%)                                                     |
|   - Rare-Class Recall: Glass Shatter (>= 30%), Lamp Broken (>= 15%), Tire Flat (>= 25%)         |
+-------------------------------------------------------------------------------------------------+
| TIER 4: OPERATIONAL & HARDWARE EFFICIENCY                                                       |
|   - False Positives per Image (Must be <= 3.0 FP/image on authentic vehicles)                   |
|   - P95 Inference Latency (Must be <= 200 ms on standard hardware)                              |
|   - Peak Memory Footprint (Must be <= 1.0 GB RAM / VRAM)                                        |
+-------------------------------------------------------------------------------------------------+
```

---

## 3. Strict Non-Negotiable Gate Gating Rules

### Rule 1: The Anti-EXP02 Suppression Circuit Breaker
- A candidate model is **IMMEDIATELY REJECTED** if it detects **$0$ structural cracks** on the frozen evaluation cohorts at the operational threshold ($\tau=0.25$, $\text{IoU}\ge 0.40$).
- High precision or low false-alarm counts **cannot compensate** for zero crack detection.

### Rule 2: Minimum Aggregate Recall Floor
- The model must achieve an aggregate operational recall across all damage classes of **$\ge 20.0\%$** on the CarDD frozen test cohort and **$\ge 18.0\%$** on composite cohorts. Any model with overall recall below $18.0\%$ is disqualified.

### Rule 3: False-Alarm Ceiling
- The model must maintain an operational false-positive rate of **$\le 3.5\text{ FP/image}$** on test vehicles and produce zero false positives on clean undamaged negative walkarounds.

### Rule 4: Harmonic Macro-F1 Selection
- Overall model ranking must use the **Harmonic Macro-F1 score**:
  $$\text{Macro-F1}_{\text{harmonic}} = \frac{6}{\sum_{c=0}^5 \frac{1}{\text{F1}_c + \epsilon}}$$
  Because the harmonic mean heavily penalizes near-zero values, a model with $0.0\%$ crack F1 receives a near-zero harmonic score, mathematically preventing suppression models from winning the ranking.

---

## 4. Formal Approval & Authorization Requirements

- **Production Promotion Authority:** Promotion of any model to replace `models/phase5/best.pt` requires:
  1. Full compliance with Tier 1 through Tier 4 metrics.
  2. Multi-seed verification ($\sigma < 0.015$).
  3. Formal written authorization from the Project Owner.
- **Threshold Modification Authority:** Any alteration to the production operational confidence threshold ($\tau=0.25$) or IoU threshold ($0.40$) requires explicit Project Owner sign-off.
