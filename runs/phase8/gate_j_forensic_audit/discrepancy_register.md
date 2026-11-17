# ClaimSense AI — Phase 8: Gate J Discrepancy Register

**Audit Date:** 2026-11-17  
**Governance Gate:** Gate J — Benchmark Forensic Integrity Audit  
**Scope:** Forensic Anomaly & Discrepancy Tracking across Gate I Artifacts  
**Status:** COMPLETE

---

## 1. Discrepancy Classification Taxonomy

Each tracked item is assigned a formal audit severity:
- **PASS:** No discrepancy found, or discrepancy within expected numerical floating-point tolerances ($\le 0.0001$).
- **WARNING:** An observable numerical divergence or artifact resulting from established library conventions, parameter selections, or domain characteristics. Does not compromise data integrity or invalidate benchmark conclusions.
- **FAIL:** A calculation error, dataset corruption, hash mismatch, or protocol violation that compromises benchmark validity.

---

## 2. Itemized Discrepancy Register

### Item DISC-001: Precision = 1.0000 with Recall = 0.0000 in Zero-Detection Classes
- **Affected Artifact:** `runs/phase8/gate_i_benchmark/per_class_metrics.csv`
- **Affected Entries:**
  - Production Baseline: Scratch (Class 1) — P=1.0000, R=0.0000
  - Phase 8 Session 2: Scratch (Class 1) — P=1.0000, R=0.0000
  - Phase 8 Session 2: Crack (Class 2) — P=1.0000, R=0.0000
  - Phase 8 Session 4: Crack (Class 2) — P=1.0000, R=0.0000
- **Severity:** **WARNING (Explained Artifact)**
- **Root Cause:** In `ultralytics.utils.metrics.ap_per_class`, the precision curve is interpolated over 1000 confidence samples with `np.interp(-x, -conf[i], precision[:, 0], left=1)`. When a class has no detections exceeding the global best-mean-F1 threshold, recall is 0.0, but precision falls into the left-extrapolation zone and returns `1.0`. Mathematically, $TP=0$ and $FP=0$, making precision $0/0$ (undefined).
- **Impact Analysis:** Has zero impact on mAP@50 or mAP@50:95 because AP is computed from the area under the PR curve, which correctly evaluates to $\approx 0.0000$. It inflates macro precision slightly if interpreted literally.
- **Governance Action:** Document in Gate J deliverables. In `raw_count_reconciliation.csv`, recompute raw precision directly from confusion matrix counts ($P = 0.0000$).

---

### Item DISC-002: Divergence Between Raw Confusion Matrix Precision and Reported Curve Precision
- **Affected Artifacts:** `confusion_matrices/` vs `overall_metrics.csv` / `per_class_metrics.csv`
- **Observation:** Raw confusion matrix precision at `conf = 0.001` is $\approx 0.0003 - 0.0013$, whereas reported macro precision in `overall_metrics.csv` is $0.1690 - 0.3473$.
- **Severity:** **WARNING (Explained Methodological Distinction)**
- **Root Cause:** 
  1. The confusion matrices were dumped by Ultralytics at the evaluation threshold (`conf = 0.001`), capturing all background proposals across all images.
  2. The reported summary precision (`box.mp` in `overall_metrics.csv`) is evaluated at the specific confidence threshold $x[i]$ that maximizes the mean F1 score across all classes (typically $conf \approx 0.15 - 0.25$).
  3. At $conf \approx 0.20$, the vast majority of background false positives are discarded, raising precision from $0.001$ to $0.17 - 0.35$, while reducing recall.
- **Impact Analysis:** Both numbers are methodologically correct within their respective definitions: raw matrix represents the unthresholded validation state, while reported precision represents the optimal F1 operating point.
- **Governance Action:** Fully reconciled in `evaluation_protocol_audit.md` and `raw_count_reconciliation.csv`.

---

### Item DISC-003: Confusion Matrix Background False-Positive Inflation
- **Affected Artifacts:** `runs/phase8/gate_i_benchmark/confusion_matrices/`
- **Observation:** Column 6 (background) contains 6,259 detections for Production Baseline, 2,423 for Session 2, and 2,185 for Session 4.
- **Severity:** **WARNING (Explained Evaluation Behavior)**
- **Root Cause:** Standard YOLO evaluation runs with `conf = 0.001` to construct complete PR curves. At this threshold, minor ambient lighting shifts, body seams, and specular reflections generate proposals. When matched against the clean 44-image validation set (which contains only 47 true instances), thousands of proposals match background.
- **Impact Analysis:** This is normal behavior for YOLO validation at $conf = 0.001$. However, it highlights the risk of using fine-tuned models without a calibrated operational confidence threshold.
- **Governance Action:** Confirmed as expected YOLO validation behavior. Emphasize that models require operational threshold filtering ($conf \ge 0.25$) in production.

---

### Item DISC-004: Floating-Point Rounding Delta ($\le 0.0001$) in Composite Recomputation
- **Affected Artifacts:** `tier_composite_reconciliation.csv`
- **Observation:** Discrepancies of $0.0001$ between reported composite metrics and recomputed values:
  - Production Baseline Composite Precision: Reported = 0.1998, Recomputed from rounded inputs = 0.1997 ($\Delta = 0.0001$).
  - Session 2 Composite F1: Reported = 0.1428, Recomputed = 0.1429 ($\Delta = 0.0001$).
  - Session 4 Composite F1: Reported = 0.1549, Recomputed = 0.1548 ($\Delta = 0.0001$).
- **Severity:** **PASS (Within Tolerances)**
- **Root Cause:** `execute_gate_i_benchmark.py` maintained float64 variables in memory during composite calculation before rounding to 4 decimal places. Recomputing from already-rounded 4-decimal input values introduces a $10^{-4}$ rounding artifact.
- **Impact Analysis:** Negligible. Zero impact on substantive performance comparisons.
- **Governance Action:** Certified as mathematically acceptable.

---

### Item DISC-005: 45% to 0.6% mAP Divergence Between CarDD Test Set and Independent Pilot
- **Affected Domain:** Overall Model Generalization Performance
- **Observation:** Models achieved $\approx 44 - 45\%$ mAP@50 during CarDD in-distribution training/validation, but only $0.16 - 0.60\%$ mAP@50 on `CarDD_Independent_Val_v1`.
- **Severity:** **WARNING (Substantive Domain Generalization Failure)**
- **Root Cause:** Exhaustive audit confirmed zero software bugs, zero label mismatches, and zero coordinate errors. The divergence is purely domain-driven:
  - Heavy sensor, lighting, and compression shift from Chinese surveillance video to clean Western photography.
  - Granularity gap: Dense, overlapping bounding box clusters in CarDD vs strict single-enclosing unified AABBs in the independent dataset.
  - Class blindness: Complete inability to detect real-world `lamp broken` and `tire flat` damage from walkaround perspectives.
- **Impact Analysis:** Substantively validates the entire Phase 8 acquisition program. Proves that CarDD test metrics were an in-distribution illusion and that deploying models based solely on CarDD benchmarks would have caused severe production failures.
- **Governance Action:** Certified as a real domain effect. Reinforces the recommendation to **REJECT PRODUCTION PROMOTION**.

---

## 3. Discrepancy Summary Table

| Discrepancy ID | Summary | Classification | Resolution / Status |
| :---: | :--- | :---: | :--- |
| **DISC-001** | Precision=1.0 with Recall=0.0 in zero-detection classes | **WARNING** | Resolved: Ultralytics interpolation artifact explained |
| **DISC-002** | Raw confusion matrix precision vs reported curve precision | **WARNING** | Resolved: Conf=0.001 trace vs max-F1 threshold reconciled |
| **DISC-003** | Thousands of background proposals in confusion matrix | **WARNING** | Resolved: Standard YOLO validation behavior at conf=0.001 |
| **DISC-004** | 0.0001 rounding delta in composite recomputations | **PASS** | Resolved: Verified within float rounding tolerance |
| **DISC-005** | CarDD test mAP (~0.45) vs Independent pilot mAP (~0.006) | **WARNING** | Resolved: Genuine domain shift confirmed; zero bugs |

**Overall Audit Result: ZERO FAILURES (0 FAIL). ALL DISCREPANCIES FULLY RECONCILED.**
