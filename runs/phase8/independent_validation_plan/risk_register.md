# ClaimSense AI — Phase 8 Model Weaknesses & Production Risk Register

**Context:** Analysis of known failure modes, visual edge cases, and statistical vulnerabilities identified during Phase 8 training, benchmarking, and calibration.

---

## 1. Risk Matrix Overview

| Risk ID | Failure Mode / Vulnerability | Severity | Probability | Impact Area | Mitigation & Operational Protocol |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **RSK-01** | **Session 4 Scratch Recall Regression at High Cutoff** | **HIGH** | **HIGH** | Scratch Detection | Lower scratch operating threshold to $0.10 - 0.12$; test class-specific thresholding in blind evaluation. |
| **RSK-02** | **Panel Seams & Body Cutline Confusion** | **MEDIUM** | **HIGH** | Crack & Scratch | Aspect ratio filtering; require morphological connectivity; train negative edge examples in future phases. |
| **RSK-03** | **Specular Highlights / Sun Glint False Dents** | **MEDIUM** | **HIGH** | Dent Precision | Enforce minimum confidence $\tau_{dent} \ge 0.25$; integrate lighting normalization in Phase 7 verification engine. |
| **RSK-04** | **Hairline Crack Scale Attenuation at 640px** | **HIGH** | **MEDIUM** | Crack Recall | 100-image expansion helped (+358% mAP), but fine cracks still require high resolution or patched inference for sub-millimeter detection. |
| **RSK-05** | **Small Benchmark Sample Size Overfitting** | **CRITICAL** | **HIGH** | Evaluation Integrity | Build the 200+ image independent dataset; strictly prohibit threshold re-tuning on the test split. |
| **RSK-06** | **Domain Shift from CarDD to Operational Claims** | **HIGH** | **MEDIUM** | Generalization | Source real insurance claims and salvage intake photographs; test on unseen camera sensors and vehicle classes. |
| **RSK-07** | **Wheel Arch Shadow / Trim Tire-Flat Alarms** | **LOW** | **MEDIUM** | Tire Flat Precision | Calibrate tire threshold to $\tau_{tire} \ge 0.35$; verify wheel hub presence prior to flagging deflation. |

---

## 2. In-Depth Failure Mode Analysis

### A. RSK-01: Session 4 Scratch Confidence Attenuation
- **Observed Behavior:**
  - In Session 2, scratches at $\tau=0.25$ achieved 10 TPs (18.9% recall) and 36 TPs at $\tau=0.001$.
  - In Session 4, scratches at $\tau=0.25$ dropped to 3 TPs (5.7% recall), while maintaining 37 TPs at $\tau=0.001$ and 12 TPs at $\tau=0.10$.
- **Root Cause:**
  - The expansion of 100 images added 133 scratch annotations, many of which had varying contrast.
  - AdamW weight decay ($0.0005$) and mosaic augmentations regularized scratch features, driving network confidence for thin, low-contrast streaks downward into the $0.08 - 0.18$ band.
- **Mitigation:**
  - In the Phase 7 verification engine, implement **class-conditioned thresholding** ($\tau_{scratch} = 0.10 - 0.12$).
  - In future training (Phase 9), introduce targeted high-contrast scratch loss weighting (`cls_pw` or focal gamma adjustment).

---

### B. RSK-02: Panel Seams & Body Shut-Lines Misclassified as Cracks
- **Observed Behavior:**
  - High-contrast lines formed where the front bumper meets the fender or where the hood meets the front fascia trigger false crack detections (accounting for 8.1% of false alarms).
- **Root Cause:**
  - Plastic bumper cracks and panel cutlines share identical low-level visual signatures: dark linear trajectories with high contrast against lighter body panels.
- **Mitigation:**
  - Incorporate negative background examples (clean vehicle body seams with zero damage) in training data.
  - Spatial filtering: penalize crack predictions that run parallel to known panel boundaries.

---

### C. RSK-03: Specular Reflection Confusion on Curved Sheet Metal
- **Observed Behavior:**
  - Bright sun reflections on curved doors and quarter panels account for 17.7% of false positives at $\tau=0.25$ (Session 4).
- **Root Cause:**
  - Dents distort reflected light, creating high-gradient highlights bordered by shadow. Smooth, non-damaged compound curves (such as wheel arch flares) reflect sunlight with similar gradient profiles.
- **Mitigation:**
  - Operating threshold $\tau_{dent} \ge 0.25$ eliminates 75% of specular false positives.
  - Polarization or multi-exposure fusion if claims app guides user capture.

---

### D. RSK-04: Hairline Cracks vs Input Resolution
- **Observed Behavior:**
  - Hairline fractures are only 1–3 pixels wide on a native $4000 \times 3000$ camera sensor. Downsampling to $640 \times 640$ reduces the crack width to sub-pixel or single-pixel dimensions, diluting convolutional activation.
- **Mitigation:**
  - Closing mosaic augmentations at Epoch 16 in Session 4 stabilized crack gradients, boosting Crack mAP from 1.99% to 9.13%.
  - Future architecture consideration: Tiled/sliding-window inference (SAHI) on high-resolution crops for claims where user reports bumper impact.

---

### E. RSK-05: Small CarDD Test Set Overfitting
- **Observed Behavior:**
  - 45 test images containing only 13 cracks and 6 flat tires. A single True Positive shift alters Crack recall by 7.7% and Tire recall by 16.7%.
- **Root Cause:**
  - The CarDD benchmark test split is too small for definitive enterprise SLAs.
- **Mitigation:**
  - The `CarDD_Independent_Val_v1` specification establishes at least 200 images with 60+ crack and 30+ tire instances to provide statistical significance ($p < 0.05$).

---

## 3. Risk Governance & Escalation Triggers

| Trigger Condition | Immediate Action | Escalation Pathway |
| :--- | :--- | :--- |
| **Scratch recall on new validation set < 15%** | Halt model rollout; evaluate Session 2 vs Session 4 ensemble. | ML Engineering Lead |
| **False alarm rate > 2.0 FP / image on clean vehicles** | Increase operational threshold to $\tau \ge 0.25$ across all classes. | Quality Assurance Lead |
| **Divergence between Reviewer A & B > 30%** | Pause annotation pipeline; revise annotation guidelines. | Data Annotation Manager |
| **PII redaction audit failure** | Immediate quarantine of affected image batch; trigger automated re-scrubbing. | Compliance / Legal Officer |
