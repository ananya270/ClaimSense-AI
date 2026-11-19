# ClaimSense AI — Phase 9.6: Evaluation Protocol & Metric Definitions

**Document ID:** `PROT-PH9-6-EVAL-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.6 — Independent Benchmark Evaluation & Candidate Model Validation  
**Execution Date:** 2026-11-20  
**Status:** FROZEN PROTOCOL SPECIFICATION  

---

## 1. Overview & Evaluation Principles

To guarantee uncompromised scientific validity, all models benchmarked during Phase 9.6 were subjected to a single, frozen, standardized evaluation protocol.

- **No Threshold Tuning on Test Data:** Operational confidence thresholds were fixed strictly at historical production values ($\tau = 0.25$, $\text{IoU} \ge 0.40$).
- **Dual-Track Evaluation:** Both standard continuous PR-curve metrics (mAP@50, mAP@50-95) and discrete operational decision metrics (TP, FP, FN, Precision, Recall, F1) were measured.
- **Strict Separation of Cohorts:** The frozen CarDD test set, Gate O authentic validation set, and Gate P forensic set are evaluated and reported independently.

---

## 2. Mathematical Metric Definitions

### 2.1 Intersection over Union (IoU)
For a predicted bounding box $B_{\text{pred}} = [x_1, y_1, x_2, y_2]$ and ground truth box $B_{\text{gt}} = [x'_1, y'_1, x'_2, y'_2]$:
$$\text{IoU}(B_{\text{pred}}, B_{\text{gt}}) = \frac{\text{Area}(B_{\text{pred}} \cap B_{\text{gt}})}{\text{Area}(B_{\text{pred}} \cup B_{\text{gt}})}$$

### 2.2 Operational Matching Criteria
A prediction is designated a **True Positive (TP)** if:
1. $\text{class}(B_{\text{pred}}) == \text{class}(B_{\text{gt}})$
2. $\text{confidence}(B_{\text{pred}}) \ge \tau \quad (\tau = 0.25)$
3. $\text{IoU}(B_{\text{pred}}, B_{\text{gt}}) \ge 0.40$
4. The ground-truth box $B_{\text{gt}}$ has not been previously claimed by a higher-confidence prediction (greedy non-replacement matching).

A prediction failing condition 1, 3, or 4 is designated a **False Positive (FP)**.  
Any ground-truth box with no matching prediction is designated a **False Negative (FN)**.

### 2.3 Operational Precision, Recall, and F1-Score
$$\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}}$$
$$\text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}}$$
$$F_1 = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$

### 2.4 Mean Average Precision (mAP)
Average Precision (AP) is calculated as the area under the interpolated Precision-Recall curve across all confidence thresholds:
$$\text{AP} = \sum_{k=1}^N (R_k - R_{k-1}) P_{\text{interp}}(R_k)$$
- **mAP@50:** Mean AP across all classes at IoU threshold $0.50$.
- **mAP@50-95:** Mean AP averaged over 10 IoU thresholds from $0.50$ to $0.95$ with step $0.05$.

---

## 3. Evaluation Cohort Specifications

| Cohort Name | Track | Image Count | Ground Truth Instances | Provenance / Characterization | Role in Benchmark |
|---|---|---|---|---|---|
| **CarDD Frozen Test Split** | Track A | 45 | 148 | Verified CarDD collision damage test set; held out from all training. | Primary Independent Statistical Benchmark |
| **CarDD_Independent_Val_v1** | Track B | 44 | 47 | Dual-blind annotated real-world vehicle walkarounds (Gate O). | Real-World Generalization Benchmark |
| **Gate P Forensic Cohort** | Track C | 75 | 167 | Forensic diagnostic cohort compiled during Gate P audit. | Failure-Mode Forensic Verification |
| **Gate L Development Cohort** | Track D | 30 | 19 | Authentic development walkarounds used for prior tuning. | Diagnostic Reference Only (Non-Independent) |

---

## 4. Hardware & Execution Control

- **Execution Environment:** PyTorch 2.15.0+cpu, Ultralytics YOLOv8 8.4.214, Python 3.14.6.
- **Host CPU:** Intel Core i5-1035G1 CPU @ 1.00GHz.
- **Worker Configuration:** Single-threaded dataloader (`workers=0`) to eliminate non-deterministic race conditions.
