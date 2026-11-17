# ClaimSense AI — Phase 8: Independent Evaluation Checklist & Protocol

**Document Version:** 1.0 (Evaluation Governance Protocol)  
**Audit Date:** 2026-11-17  
**Scope:** Controlled benchmarking protocol, environmental invariance criteria, metric checklist, and validation safeguards for 3-way evaluation on `CarDD_Independent_Val_v1`  
**Execution State:** **SPECIFICATION ONLY.** No model loading, evaluation, or checkpoint modification executed.

---

## 1. 3-Way Checkpoint Benchmarking Scope

The independent evaluation will execute a head-to-head comparison across three frozen checkpoints on the newly curated, immutable independent validation suite:

| Checkpoint Identifier | Model File Path | Verified SHA-256 Checksum | Origin / Training Lineage |
| :--- | :--- | :---: | :--- |
| **Production Baseline** | `models/phase5/best.pt` | `90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565` | Phase 5 Production Deployment |
| **Session 2 Checkpoint** | `runs/phase8/session_2/weights/best.pt` | `2ee0a56749ceba72da863fd3496f080ee06f26409daa4e9588fb69ee149333c5` | 210-image training split |
| **Session 4 Checkpoint** | `runs/phase8/session_4_training_01/weights/best.pt` | `ea53eee94e508bbb81620b47b2a23c9826341b6b5a6981d9371e476cb9d0594f` | 310-image expanded training split |

**Evaluation Dataset:** `datasets/CarDD_Independent_Val_v1/` (235 curated authentic images, zero overlap with CarDD training or validation sets).

---

## 2. Controlled Hyperparameters & Environmental Invariance

To ensure rigorous scientific validity, all three checkpoints must be evaluated under **strictly identical execution parameters**:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                      Controlled Evaluation Hyperparameters                             │
├──────────────────────────────┬──────────────────────────┬──────────────────────────────┤
│ Parameter                    │ Standard Value           │ Invariance Requirement       │
├──────────────────────────────┼──────────────────────────┼──────────────────────────────┤
│ Image Resolution (`imgsz`)   │ 640 x 640                │ Identical for all 3 models   │
│ Compute Device (`device`)    │ CUDA:0 (NVIDIA RTX 3050) │ Dedicated GPU execution      │
│ Precision Mode (`amp`)       │ FP16 Automatic Mixed     │ Identical for all 3 models   │
│ Batch Size (`batch`)         │ 4 (Fallback: 2 on OOM)   │ Identical for all 3 models   │
│ NMS IoU Threshold (`iou`)    │ 0.45                     │ Identical for all 3 models   │
│ Operating Confidence (`conf`)│ 0.25 (Fixed operational) │ Identical for all 3 models   │
│ Calibration Sweep Range      │ [0.05, 0.10, 0.15, 0.20, │ Identical 8 operating points │
│                              │  0.25, 0.30, 0.40, 0.50] │ for PR-curve tracing         │
│ Metric Match IoU Threshold   │ IoU >= 0.50              │ Hungarian 1-to-1 matching    │
│ Ultralytics Version          │ 8.4.215                  │ Frozen runtime environment   │
└──────────────────────────────┴──────────────────────────┴──────────────────────────────┘
```

---

## 3. Mandatory Pre- and Post-Evaluation Checkpoint Integrity

Before and after the evaluation run, the evaluator script must automatically compute and log SHA-256 hashes for all three weight files:

```python
assert sha256("models/phase5/best.pt") == "90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565"
assert sha256("runs/phase8/session_2/weights/best.pt") == "2ee0a56749ceba72da863fd3496f080ee06f26409daa4e9588fb69ee149333c5"
assert sha256("runs/phase8/session_4_training_01/weights/best.pt") == "ea53eee94e508bbb81620b47b2a23c9826341b6b5a6981d9371e476cb9d0594f"
```
Any hash discrepancy immediately aborts the evaluation report.

---

## 4. Comprehensive Output Metric Checklist

The evaluation suite must compute and tabularize the following metrics for each of the six damage classes (Dent, Scratch, Crack, Glass shatter, Lamp broken, Tire flat) as well as overall macro/micro totals:

- [ ] **True Positives (TP):** Ground-truth instances correctly localized with $\text{IoU} \ge 0.50$ and correct class ID.
- [ ] **False Positives (FP) — Background:** Detections on undamaged vehicle surfaces, panel seams, or road clutter.
- [ ] **False Positives (FP) — Cross-Class:** Detections where damage exists but the model assigned an incorrect class (e.g. labeling a crack as a scratch).
- [ ] **False Negatives (FN):** Ground-truth damage instances missed by the model ($\text{conf} < 0.25$ or $\text{IoU} < 0.50$).
- [ ] **Precision ($P$):** $P = \frac{TP}{TP + FP_{\text{bg}} + FP_{\text{cross}}}$ at operating point $\text{conf}=0.25$.
- [ ] **Recall ($R$):** $R = \frac{TP}{TP + FN}$ at operating point $\text{conf}=0.25$.
- [ ] **F1-Score ($F_1$):** $F_1 = \frac{2 P R}{P + R}$ at operating point $\text{conf}=0.25$.
- [ ] **mAP@50:** Mean Average Precision calculated at $\text{IoU}=0.50$ across full recall spectrum.
- [ ] **mAP@50-95:** Mean Average Precision averaged across 10 IoU thresholds ($0.50:0.05:0.95$).
- [ ] **Latency Benchmark:**
  - 10-batch warm-up run prior to timing.
  - CUDA event timing recording Pre-process time, Inference forward-pass time, and NMS post-process time (reported in milliseconds per image).
- [ ] **Diagnostic Artifacts:**
  - Full $6 \times 6$ confusion matrices (raw counts and row-normalized).
  - Class-wise PR curves across confidence sweep.
  - Visual overlay crops of top-5 worst false positives and top-5 false negatives per class.

---

## 5. Decision Safeguards & Promotion Governance

1. **Multi-Metric Human Review:**  
   Model promotion is not determined by a single composite metric. A candidate checkpoint must demonstrate:
   - No regression on high-severity structural classes (Glass shatter, Crack, Tire flat).
   - Statistically significant improvement in overall mAP50 without causing unacceptable false positive inflation on reflections.
   - Stable inference latency under $\le 35\text{ ms}$ on the target GPU.
2. **Zero Automatic Replacement:**  
   Under no circumstances will an evaluation script overwrite `models/phase5/best.pt`. Production promotion requires separate written executive authorization following review of the benchmark report.
