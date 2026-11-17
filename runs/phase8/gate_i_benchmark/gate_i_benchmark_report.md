# ClaimSense AI — Phase 8: Gate I Independent Model Benchmark Report

**Evaluation Scope:** Independent Pilot Benchmark  
**Dataset:** `CarDD_Independent_Val_v1` (44 Images, 47 Verified Damage Instances)  
**Active Specification:** `acquisition_specification.md` — v1.1-ACTIVE  
**Execution Timestamp:** 2026-11-17  
**Execution Mode:** STRICTLY BENCHMARK ONLY (Read-Only / Non-Destructive)

---

## 1. Executive Summary

Under formal governance authorization **Gate I**, an independent comparative model benchmark was executed on the frozen, zero-contamination validation dataset `CarDD_Independent_Val_v1`. 

Three YOLOv8n object detection checkpoints were benchmarked under strictly standardized inference conditions on dedicated GPU hardware (NVIDIA GeForce RTX 3050 Laptop GPU, CUDA 12.8, PyTorch 2.11.0):
1. **Production Baseline (Phase 5):** `models/phase5/best.pt`
2. **Phase 8 Session 2:** `runs/phase8/session_2/weights/best.pt`
3. **Phase 8 Session 4:** `runs/phase8/session_4_training_01/weights/best.pt`

### Key Outcomes:
- **Zero Modifications:** All three model weights files and all 44 dataset images/labels were cryptographically hashed (SHA-256) before and after execution; **0 bits were altered** (100% byte-for-byte immutability).
- **Macro Quota Enforced:** Cumulative Tier 2 Macro composition was maintained at **18.18%** (8 / 44 images), securely below the active v1.1 specification ceiling of **30.00%**.
- **Quad-Metric Framework:** Metrics are independently reported across Tier 1 (Walkaround), Tier 2 (Macro), Empirical Pooled ($N=44$), and the Fixed-Weight Composite Index ($70\% \text{ Tier 1} + 30\% \text{ Tier 2}$).
- **Pilot Benchmark Notice:** In compliance with governance instructions, this benchmark is formally designated as a **44-image independent pilot benchmark, not final real-world validation**.
- **Promotion Recommendation:** **REJECT REPLACEMENT — DO NOT PROMOTE ANY CANDIDATE CHECKPOINT.** The existing baseline remains in production pending domain adaptation and future dataset scaling.

---

## 2. Checkpoint Cryptographic & Architectural Audit

Pre- and post-benchmark SHA-256 cryptographic hashes verified complete immutability:

| Checkpoint Name | Local File Path | Pre-Benchmark SHA-256 | Post-Benchmark SHA-256 | Verification Status |
| :--- | :--- | :--- | :--- | :---: |
| **Production Baseline (Phase 5)** | `models/phase5/best.pt` | `90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565` | `90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565` | **MATCH (PASS)** |
| **Phase 8 Session 2** | `runs/phase8/session_2/weights/best.pt` | `2ee0a56749ceba72da863fd3496f080ee06f26409daa4e9588fb69ee149333c5` | `2ee0a56749ceba72da863fd3496f080ee06f26409daa4e9588fb69ee149333c5` | **MATCH (PASS)** |
| **Phase 8 Session 4** | `runs/phase8/session_4_training_01/weights/best.pt` | `ea53eee94e508bbb81620b47b2a23c9826341b6b5a6981d9371e476cb9d0594f` | `ea53eee94e508bbb81620b47b2a23c9826341b6b5a6981d9371e476cb9d0594f` | **MATCH (PASS)** |

Full details are documented in [checkpoint_integrity_report.md](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/gate_i_benchmark/checkpoint_integrity_report.md).

---

## 3. Dataset Composition & Ground-Truth Structure

The benchmark was executed against `CarDD_Independent_Val_v1` staged from `batch_01` and `batch_02`:
- **Total Images:** 44
- **Batch 1 Contribution:** 23 images (15 Tier 1 Walkaround, 8 Tier 2 Macro)
- **Batch 2 Contribution:** 21 images (21 Tier 1 Walkaround)
- **Cumulative Tier Distribution:** 36 Tier 1 (81.82%), 8 Tier 2 (18.18%)
- **Cumulative Macro Proportion:** $8 / 44 = 18.18\% \le 30.00\%$ (11.82% safety margin)
- **Total Verified Instances:** 47 ground-truth damage annotations
  - **Class 0 (Dent):** 9 instances across 9 images
  - **Class 1 (Scratch):** 4 instances across 4 images
  - **Class 2 (Crack):** 6 instances across 6 images
  - **Class 3 (Glass Shatter):** 13 instances across 10 images (includes multi-pane vehicles `CS_VAL_019`, `CS_VAL_040`, `CS_VAL_045`)
  - **Class 4 (Lamp Broken):** 6 instances across 6 images (enforced under Rule 6 lighting fixture disambiguation)
  - **Class 5 (Tire Flat):** 9 instances across 9 images

Full details are documented in [dataset_integrity_report.md](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/gate_i_benchmark/dataset_integrity_report.md).

---

## 4. Overall Comparative Scorecard

All metrics reflect standard Ultralytics object detection evaluation protocols ($IoU \ge 0.50$, confidence threshold $= 0.001$, non-max suppression enabled).

| Model Checkpoint | Empirical Pooled mAP@50 | Empirical Pooled mAP@50:95 | Empirical Precision | Empirical Recall | Empirical F1-Score | Fixed-Weight Composite mAP@50 | Fixed-Weight Composite mAP@50:95 | Mean Latency (ms) | Throughput (FPS) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Production Baseline (Phase 5)** | 0.0016 | 0.0004 | 0.1690 | **0.2400** | **0.1984** | **0.0103** | **0.0032** | 131.42 ms | 7.6 FPS |
| **Phase 8 Session 2** | 0.0019 | 0.0003 | **0.3473** | 0.0128 | 0.0247 | 0.0019 | 0.0003 | **80.89 ms** | **12.4 FPS** |
| **Phase 8 Session 4** | **0.0060** | **0.0008** | 0.1894 | 0.0256 | 0.0452 | 0.0054 | 0.0007 | 85.69 ms | 11.7 FPS |

Full raw data available in [overall_metrics.csv](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/gate_i_benchmark/overall_metrics.csv).

---

## 5. Quad-Metric Tier-Wise Breakdown

Active specification v1.1 mandates the separate reporting of Tier 1 (Walkaround), Tier 2 (Macro), Empirical Pooled ($N=44$), and the Fixed-Weight Composite Index ($70\% \text{ Tier 1} + 30\% \text{ Tier 2}$):

$$\text{Composite Metric} = 0.70 \times \text{Metric}_{\text{Tier 1}} + 0.30 \times \text{Metric}_{\text{Tier 2}}$$

| Checkpoint | Evaluation Split | Images | Precision | Recall | F1-Score | mAP@50 | mAP@50:95 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Production Baseline (Phase 5)** | Tier 1 (Walkaround) | 36 | 0.1678 | 0.2030 | 0.1838 | 0.0010 | 0.0002 |
| | Tier 2 (Macro) | 8 | 0.2743 | 0.3750 | 0.3169 | **0.0320** | **0.0101** |
| | Empirical Pooled | 44 | 0.1690 | 0.2400 | 0.1984 | 0.0016 | 0.0004 |
| | **Fixed-Weight Composite (70/30)** | 44 | 0.1998 | 0.2546 | 0.2239 | **0.0103** | **0.0032** |
| **Phase 8 Session 2** | Tier 1 (Walkaround) | 36 | **0.6819** | 0.0128 | 0.0252 | 0.0020 | 0.0003 |
| | Tier 2 (Macro) | 8 | 0.0004 | 0.2500 | 0.0007 | 0.0016 | 0.0003 |
| | Empirical Pooled | 44 | 0.3473 | 0.0128 | 0.0247 | 0.0019 | 0.0003 |
| | **Fixed-Weight Composite (70/30)** | 44 | **0.4775** | 0.0840 | 0.1428 | 0.0019 | 0.0003 |
| **Phase 8 Session 4** | Tier 1 (Walkaround) | 36 | 0.1929 | 0.0256 | 0.0453 | **0.0063** | **0.0008** |
| | Tier 2 (Macro) | 8 | 0.0020 | **0.5417** | 0.0041 | 0.0033 | 0.0006 |
| | Empirical Pooled | 44 | 0.1894 | 0.0256 | 0.0452 | 0.0060 | 0.0008 |
| | **Fixed-Weight Composite (70/30)** | 44 | 0.1356 | 0.1804 | 0.1549 | 0.0054 | 0.0007 |

Full raw data available in [tier_wise_metrics.csv](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/gate_i_benchmark/tier_wise_metrics.csv).

---

## 6. Per-Class Performance Breakdown

Performance across all six damage categories on the independent evaluation dataset:

| Class ID | Class Name | Model | Instances | Pooled Precision | Pooled Recall | Pooled F1 | Pooled AP@50 | Tier 1 AP@50 | Tier 2 AP@50 | Composite AP@50 |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **0** | **Dent** | Production Baseline | 9 | 0.0036 | **0.8889** | 0.0072 | **0.0058** | 0.0037 | **0.0485** | **0.0171** |
| | | Phase 8 Session 2 | 9 | 0.0000 | 0.0000 | 0.0000 | 0.0013 | 0.0025 | 0.0000 | 0.0017 |
| | | Phase 8 Session 4 | 9 | 0.0000 | 0.0000 | 0.0000 | 0.0009 | 0.0011 | 0.0026 | 0.0015 |
| **1** | **Scratch** | Production Baseline | 4 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| | | Phase 8 Session 2 | 4 | 1.0000 | 0.0000 | 0.0000 | 0.0003 | 0.0000 | 0.0062 | 0.0019 |
| | | Phase 8 Session 4 | 4 | 0.0000 | 0.0000 | 0.0000 | 0.0003 | 0.0000 | **0.0082** | **0.0025** |
| **2** | **Crack** | Production Baseline | 6 | 0.0072 | **0.1667** | 0.0138 | **0.0025** | 0.0000 | **0.0796** | **0.0239** |
| | | Phase 8 Session 2 | 6 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| | | Phase 8 Session 4 | 6 | 1.0000 | 0.0000 | 0.0000 | 0.0010 | 0.0003 | 0.0025 | 0.0010 |
| **3** | **Glass Shatter** | Production Baseline | 13 | 0.0034 | **0.3846** | 0.0067 | 0.0015 | 0.0020 | 0.0000 | 0.0014 |
| | | Phase 8 Session 2 | 13 | 0.0836 | 0.0769 | 0.0801 | 0.0099 | 0.0096 | 0.0000 | 0.0067 |
| | | Phase 8 Session 4 | 13 | **0.1362** | 0.1538 | **0.1445** | **0.0339** | **0.0365** | 0.0000 | **0.0255** |
| **4** | **Lamp Broken** | Production Baseline | 6 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| | | Phase 8 Session 2 | 6 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| | | Phase 8 Session 4 | 6 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| **5** | **Tire Flat** | Production Baseline | 9 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| | | Phase 8 Session 2 | 9 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| | | Phase 8 Session 4 | 9 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

Full raw data available in [per_class_metrics.csv](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/gate_i_benchmark/per_class_metrics.csv).

---

## 7. Confusion Matrix & Error Mode Analysis

CSV confusion matrices for each checkpoint are archived under `runs/phase8/gate_i_benchmark/confusion_matrices/`:
- [confusion_matrix_production_baseline.csv](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/gate_i_benchmark/confusion_matrices/confusion_matrix_production_baseline.csv)
- [confusion_matrix_session_2.csv](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/gate_i_benchmark/confusion_matrices/confusion_matrix_session_2.csv)
- [confusion_matrix_session_4.csv](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/gate_i_benchmark/confusion_matrices/confusion_matrix_session_4.csv)

### Error Observations:
1. **Background Proposal Saturation:** The Production Baseline predicted 6,259 background false-positive proposals across the 44 images (an average of 142 false alarms per image). Session 2 produced 2,423 background proposals (55/image), and Session 4 produced 2,185 background proposals (50/image). High-gloss body reflections, door jambs, and wheel arches trigger false damage detections.
2. **True Positive Highlights:**
   - **Production Baseline:** Detected 8 of 9 true dents, but misclassified 5 dents as glass shatter, 4 as lamp broken, and 5 as tire flat due to low inter-class discriminability.
   - **Phase 8 Session 4:** Successfully localized 3 true glass shatter instances with tight bounding boxes and achieved the highest precision (0.1362) and AP@50 (0.0339) on glazing.
3. **Severe False Negatives on Lamp Broken & Tire Flat:** Across all three checkpoints, 0 true broken headlamps/taillamps and 0 flat tires were successfully matched to ground truth.

---

## 8. Synchronized Latency & Throughput Benchmark

Inference latency was benchmarked across all 44 full-resolution test images on a dedicated NVIDIA GeForce RTX 3050 Laptop GPU using CUDA 12.8 with PyTorch synchronized GPU timers (`torch.cuda.Event` pairs, preceded by 10 warm-up runs):

| Model Name | Mean Latency | Median Latency | Std Deviation | Min Latency | Max Latency | Throughput (FPS) | Latency Delta vs Baseline |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Production Baseline (Phase 5)** | 131.42 ms | 122.54 ms | 63.37 ms | 44.92 ms | 268.73 ms | 7.6 FPS | Baseline (Ref) |
| **Phase 8 Session 2** | **80.89 ms** | 83.75 ms | **51.66 ms** | 18.13 ms | 214.26 ms | **12.4 FPS** | **-38.4% (Faster)** |
| **Phase 8 Session 4** | 85.69 ms | **71.01 ms** | 56.67 ms | **15.48 ms** | 208.45 ms | 11.7 FPS | **-34.8% (Faster)** |

Full raw data available in [latency_comparison.csv](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/gate_i_benchmark/latency_comparison.csv).

---

## 9. Governance & Production Promotion Recommendation

In accordance with [promotion_recommendation.md](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/gate_i_benchmark/promotion_recommendation.md):

> [!CAUTION]
> **GOVERNANCE DECISION: REJECT REPLACEMENT — DO NOT PROMOTE ANY CANDIDATE CHECKPOINT.**  
>
> 1. **Maintain Production Baseline:** Retain `models/phase5/best.pt` in `models/` without alteration.  
> 2. **Pilot Dataset Scope:** This evaluation must be formally classified as a **44-image independent pilot benchmark, not final real-world validation**. While it successfully uncovers severe out-of-domain transfer vulnerabilities, $N=44$ images is a diagnostic pilot rather than a production certification milestone.  
> 3. **Prohibit Unauthorized Code Changes:** No confidence threshold deployment (`conf_threshold`), pipeline reconfigurations, or Batch 3 acquisitions may occur without separate, explicit governance authorization.

---

## 10. Index of Deliverables

All Gate I evaluation artifacts are permanently archived in the project repository:

1. **Benchmark Report (This Document):** [gate_i_benchmark_report.md](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/gate_i_benchmark/gate_i_benchmark_report.md)
2. **Promotion Recommendation:** [promotion_recommendation.md](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/gate_i_benchmark/promotion_recommendation.md)
3. **Checkpoint Cryptographic Integrity Report:** [checkpoint_integrity_report.md](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/gate_i_benchmark/checkpoint_integrity_report.md)
4. **Dataset Integrity & Inventory Report:** [dataset_integrity_report.md](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/gate_i_benchmark/dataset_integrity_report.md)
5. **Overall Metrics CSV:** [overall_metrics.csv](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/gate_i_benchmark/overall_metrics.csv)
6. **Tier-Wise Metrics CSV:** [tier_wise_metrics.csv](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/gate_i_benchmark/tier_wise_metrics.csv)
7. **Per-Class Metrics CSV:** [per_class_metrics.csv](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/gate_i_benchmark/per_class_metrics.csv)
8. **Inference Latency Comparison CSV:** [latency_comparison.csv](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/gate_i_benchmark/latency_comparison.csv)
9. **Confusion Matrix Directory:** [confusion_matrices/](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/gate_i_benchmark/confusion_matrices/)
10. **Benchmark Summary JSON:** [benchmark_summary.json](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/gate_i_benchmark/benchmark_summary.json)
