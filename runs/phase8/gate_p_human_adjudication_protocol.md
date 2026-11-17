# ClaimSense AI — Gate P Human Adjudication Protocol
## Double-Blind Expert Adjuster Disagreement Adjudication

**Document ID:** `PRO-PH8-GATE-P-ADJUD-001`  
**Date:** 2026-11-17  
**Governing Standard:** `acquisition_specification.md` v1.1-ACTIVE  
**Objective:** Independent Human Adjudication of Model Disagreements During 14-Day Shadow Trial  
**Cohort Target:** Target Up to 200 Real-World Disagreement Claims (Conditioned on Volume; No Fabrication)

---

## 1. Methodological Principles & Blind Review Safeguards

To prevent human cognitive bias or favoritism toward the candidate model, all claims selected for human review must adhere to a strict double-blind adjudication protocol:

1. **Complete Model Anonymization:**
   * Predictions are presented to adjusters as **"Model A"** vs **"Model B"**.
   * The mapping of Model A / Model B to Production Baseline / EXP02 is randomized per claim via a cryptographically salted hash (`HMAC-SHA256(claim_id, salt)`).
   * Adjusters are strictly blind to model identities, checkpoint versions, and training histories.
2. **Dual-Adjuster Independent Scoring:**
   * Two senior licensed motor vehicle damage adjusters (Reviewer 1 and Reviewer 2) independently evaluate each claim image.
   * Neither adjuster sees the other's assessment or annotations during the review.
3. **Senior Adjudicator Tie-Breaker:**
   * Any disagreement between Reviewer 1 and Reviewer 2 is adjudicated by a Senior Claims Examiner (Adjudicator C) under Specification v1.1 Rule 6.
4. **Inter-Rater Reliability Requirement:**
   * Inter-adjuster agreement will be tracked using Cohen's Kappa. Minimum acceptable reliability: **$\kappa \ge 0.70$**.

---

## 2. Cohort Assembly & Stratification Rules

### Target Sample Size:
* **Target:** Up to **200 real-world claim images** where Production Baseline and EXP02 predictions diverge.
* **Authenticity Rule:** **Sample counts must never be fabricated.** If the live claim stream yields fewer than 200 disagreement claims during the 14 calendar days (e.g. 115 claims), the trial reports exactly 115 claims. Artificial or synthetic padding is strictly prohibited.

### Stratified Sampling Quotas:
The disagreement cohort will be assembled according to the following priority categories:

| Stratum Code | Divergence Archetype | Target Quota | Selection Priority |
| :---: | :--- | :---: | :---: |
| **STR-01** | High-Confidence Divergence (One model predicts damage $\tau \ge 0.50$, other predicts 0) | Up to 60 Claims | **Highest Priority** |
| **STR-02** | Suspected Crack / Structural Fracture Claims (Risk 1 Oversight) | Up to 40 Claims | **High Priority** |
| **STR-03** | Daylight Glare & Specular Reflection Canary Claims (Risk 3 Verification) | Up to 40 Claims | **High Priority** |
| **STR-04** | Rare Lighting Assembly & Tire Defect Claims (`lamp broken`, `tire flat`) | Up to 40 Claims | **Medium Priority** |
| **STR-05** | Severity & Bounding-Box Boundary Extent Disagreements | Up to 20 Claims | **Standard Priority** |

---

## 3. Human Adjudication Form & Evaluation Criteria

For each claim image, adjusters must answer the following standardized questionnaire:

```
================================================================================
  CLAIMSENSE AI — MOTOR VEHICLE DAMAGE ADJUDICATION RECORD
================================================================================
  Claim Audit ID: ADJ-CLM-[CLAIM_ID]
  Reviewer ID:    [ADJUSTER_INITIALS]
  Review Date:    [YYYY-MM-DD]
--------------------------------------------------------------------------------
1. Physical Damage Ground Truth:
   [ ] Clean / Undamaged Vehicle (Zero Physical Defects)
   [ ] Cosmetic Damage Present (Dent / Scratch / Paint Scuff)
   [ ] Structural Damage Present (Cracked Bumper / Torn Sheet Metal)
   [ ] Lighting Assembly Broken / Fractured Lens
   [ ] Deflated / Flat Tire / Wheel Damage
   [ ] Shattered Glazing / Window Glass

2. Model Assessment (Double-Blind):
   - Model A Detection: [Bounding Box Overlay A]
   - Model B Detection: [Bounding Box Overlay B]

3. Which Model Provided the Operationally Superior Determination?
   ( ) Model A is clearly superior (Accurate damage, no false alarms)
   ( ) Model B is clearly superior (Accurate damage, no false alarms)
   ( ) Both models are acceptable (Minor boundary differences)
   ( ) Neither model is acceptable (Both hallucinated or both missed damage)

4. False Positive Audit:
   - Did Model A hallucinate damage on clean panels/reflections? [YES / NO]
   - Did Model B hallucinate damage on clean panels/reflections? [YES / NO]

5. Qualitative Comments:
   _____________________________________________________________________________
================================================================================
```

---

## 4. Post-Trial Adjudication Decision Thresholds

At the conclusion of the 14-day trial, the blind adjudication scores determine the promotion recommendation:

1. **Promotion Recommendation Prerequisite:**
   * EXP02 must be judged superior or equal to Production in **$\ge 75\%$ of adjudicated disagreement cases**.
   * EXP02 clean-vehicle false alarm rate must be **$\le 5\%$** across the evaluated cohort.
   * Zero unresolved regression incidents on severe structural damage claims.
2. **Rejection Threshold:**
   * If EXP02 misses confirmed physical damage that Production detected in $> 15\%$ of claims, EXP02 is **REJECTED**.
