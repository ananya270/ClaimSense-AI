# ClaimSense AI — Phase 8 Remaining Operational Risks & Limitations

**Document ID:** `RSK-PH8-GATE-P-001`  
**Review Date:** 2026-11-17  
**Governing Standard:** `acquisition_specification.md` v1.1-ACTIVE  
**Candidate Model:** Phase 8 EXP02 (Rare Class Expansion)  
**Authoritative Production Baseline:** `models/phase5/best.pt` (SHA-256: `90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565`)

---

## 1. Critical Operational Deficiencies & Failure Modes

### Risk 1: Zero Crack Recall at Operational Threshold ($\tau=0.25$)
* **Finding:** Both the Production Baseline and EXP02 candidate achieved **Recall = 0.0000 (0 True Positives out of 14 ground-truth crack instances)** at the fixed operational threshold $\tau = 0.25$ across the 75 ground-truth evaluation set.
* **Mechanism:** Automotive body cracks and bumper fracture lines are extremely thin, high-aspect-ratio features. When images are downsampled to $640 \times 640$, fine fissure edges lose spatial continuity. Furthermore, the penalty weights introduced in negative mining suppress low-confidence line activations, causing all crack predictions to fall below $\tau = 0.25$.
* **Operational Impact:** The model is currently incapable of autonomously detecting panel fractures, bumper stress cracks, or torn composite covers.
* **Mitigation & Boundary Control:**
  1. Automated claim triage cannot rule out cracks based on a negative vision prediction.
  2. Claims involving structural fracture or bumper tearing must be routed to human adjusters with an automated flag: `UNSUPPORTED_DEFECT_CLASS: CRACK`.

### Risk 2: Low Aggregate Recall & Missed Damage Risk
* **Finding:** On the combined 75-image labeled set, EXP02 achieved an aggregate **Micro Recall of 16.17% (27 True Positives / 167 ground-truth defects)** and **Macro Recall of 17.38%**. Approximately **83.8% of annotated defects were missed** at $\tau = 0.25$.
* **Mechanism:** In shifting from Production (which predicted thousands of overlapping boxes) to EXP02 (which predicted only 56 total boxes), the candidate model prioritized false-positive suppression over sensitivity. High-confidence detections are exceptionally reliable (Precision = 48.2% vs 0.5%), but subtle or minor cosmetic damage is frequently suppressed.
* **Operational Impact:** If ClaimSense AI were deployed to adjudicate payouts autonomously, it would severely under-estimate physical damage severity and under-compensate policyholders.
* **Mitigation & Boundary Control:**
  1. EXP02 predictions must be restricted to an assistive suggestion layer for human adjusters, never an authoritative denial engine.
  2. A confidence ladder must be implemented where detections with $0.10 \le \tau < 0.25$ trigger secondary human inspection flags rather than silent discard.

### Risk 3: Scope of Glare Suppression Findings (Sample Size Boundedness)
* **Finding:** The reported 100% false-positive reduction on clean vehicles was measured on an authentic cohort of **exactly 11 clean vehicle walkaround images** (869 false alarms in Production vs 0 in EXP02).
* **Forensic Caveat:** While this 100% suppression on 11 images proves the negative mining mechanism operates correctly, **it cannot be generalized as a universal guarantee against all daylight glare or reflections**. Real-world vehicle photography involves infinite permutations of metallic paint pearls, direct low-angle solar glare, artificial forecourt floodlights, wet paint, and patterned tree reflections.
* **Operational Impact:** Sporadic glare-induced false positives will occur in live production streams.
* **Mitigation & Boundary Control:**
  1. Do not market or certify "zero false alarms on clean cars."
  2. The upcoming 14-day shadow trial must monitor clean-vehicle false alarms across at least 500 uncurated customer submissions.

### Risk 4: Separation of Verified Labeled Metrics from Qualitative Claim Observations
* **Finding:** Observations on the 14 customer uploads in `uploads/CLM-*/` (showing clean predictions on replacement cars and 1-2 boxes on damaged vehicles) are **UNVERIFIED QUALITATIVE OBSERVATIONS**.
* **Governance Standard:** Customer uploads lack audited, dual-blind ground-truth bounding boxes. Any statement that EXP02 "correctly assessed" an unlabeled customer claim is an observational hypothesis, not a mathematically certified performance metric.
* **Mitigation & Boundary Control:** All customer upload data must be categorized as "Unverified Telemetry" in all engineering and executive dashboards.

---

## 2. Summary Risk Register

| Risk ID | Failure Category | Severity | Probability | Operational Impact | Mandated Safeguard |
| :---: | :--- | :---: | :---: | :--- | :--- |
| **RSK-CRK-01** | Zero Crack Recall | **HIGH** | **100%** | Missed bumper tears and panel fissures. | Mandatory human escalation on structural claims. |
| **RSK-REC-02** | Low Aggregate Recall (16.2%) | **HIGH** | **83.8%** | Severe under-estimation of cosmetic damage. | Assistive review only; no automated denial. |
| **RSK-GLR-03** | Daylight Glare Generalization | **MEDIUM** | **MEDIUM** | Occasional false alarms on exotic pearl paints/sun glare. | 14-day shadow monitoring on $\ge 500$ real claims. |
| **RSK-TRN-04** | Annotation Protocol Disparity | **MEDIUM** | **HIGH** | IoU drops between unified and fragmented boxes. | Retain IoU 0.40 audit standard for walkaround evaluation. |
