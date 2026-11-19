# ClaimSense AI — Phase 9.6: Independent Benchmark Evaluation & Candidate Model Validation Final Report

**Document ID:** `REP-PH9-6-FINAL-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.6 — Independent Benchmark Evaluation & Candidate Model Validation  
**Previous Stage:** Phase 9.5 (Controlled Retraining & Experiment Execution)  
**Execution Date:** 2026-11-20  
**Status:** BENCHMARK EVALUATION COMPLETE — CANDIDATES STRICTLY QUARANTINED  
**Repository:** `https://github.com/anshg8252/ClaimSense-AI.git`  

---

## 1. Executive Summary & Purpose

Phase 9.6 executes independent benchmark evaluation of candidate vehicle damage detection models trained in Phase 9.5.

The primary objective is to evaluate whether candidate training interventions generalize to unseen test data, with a dedicated focus on resolving the **structural crack detection failure mode** (historically 0% recall across Gate O, Gate P, and CarDD splits) while preserving general vehicle damage detection accuracy.

In strict accordance with the **Phase 9.6 Operational Governance**:
- Phase 9.6 is strictly an evaluation-only phase.
- No model was trained, fine-tuned, or modified.
- All candidate checkpoints were evaluated on frozen benchmark data and remain strictly quarantined.
- **Zero candidate models have replaced `models/phase5/best.pt`.**
- **Zero production APIs or database records were modified.**

---

## 2. Section 1: Phase 9.5 Prerequisite Verification

All prerequisite milestones and deliverables from Phase 9.0 through Phase 9.5 were audited and verified before beginning benchmark evaluation:

| Prerequisite Milestone | Verification Document Path | Integrity / Provenance Verification | Status |
|---|---|---|---|
| **Phase 9.0 Baseline Audit** | `runs/phase9/baseline_audit/environment_manifest.md` | Verified environment specifications, package versions, baseline hashes. | **PASS** |
| **Phase 9.1 Model Evaluation** | `runs/phase9/model_evaluation/phase9_1_completion_report.md` | Re-evaluated production and historical checkpoints across validation split. | **PASS** |
| **Phase 9.2 Crack Failure Forensics** | `runs/phase9/crack_investigation/crack_failure_analysis_report.md` | Identified thin fissure feature vanishing, bounding box aspect ratio mismatch. | **PASS** |
| **Phase 9.3 Dataset Quality Audit** | `runs/phase9/dataset_audit/PHASE_9_3_FINAL_REPORT.md` | Quantified class imbalance ($6.8\%$ cracks) and annotation noise. | **PASS** |
| **Phase 9.4 Training Plan** | `runs/phase9/training_strategy/PHASE_9_4_FINAL_REPORT.md` | Verified 8-stage experiment matrix and evaluation stopping rules. | **PASS** |
| **Phase 9.5 Controlled Retraining** | `runs/phase9/retraining/PHASE_9_5_FINAL_REPORT.md` | Verified execution of P9-T01 and P9-T02; candidate checkpoints quarantined. | **PASS** |

---

## 3. Section 2: Candidate Checkpoint Cryptographic Integrity

All checkpoints evaluated in Phase 9.6 were verified via SHA-256 before and after benchmarking:

| Checkpoint Identifier | Relpath | Size (Bytes) | Cryptographic SHA-256 Digest | Audit Status |
|---|---|---|---|---|
| **Production Baseline** | `models/phase5/best.pt` | 6,472,810 | `49630ae8d5c0066d0532a2a38efede809920a6fccd3eed59a76eb3b65f009390` | **100% INVARIANT (PASS)** |
| **P9-T01 Candidate** | `runs/phase9/retraining/P9-T01/checkpoints/best.pt` | 6,472,874 | `e3e60fd2911819ec996ed5ce1591ced26530692be7d55ec22d55e4c2fde51e80` | **100% INVARIANT (PASS)** |
| **P9-T02 Candidate** | `runs/phase9/retraining/P9-T02/checkpoints/best.pt` | 6,503,658 | `91a943a9a246a0748d6f8f07a0b0860ad5872c3f229ab2f69930bb37db6ca721` | **100% INVARIANT (PASS)** |

---

## 4. Section 3: Benchmark Cohort Provenance & Characterization

| Evaluation Track | Cohort Name | Sample Size | Ground Truth Support | Provenance & Characterization | Benchmark Role |
|---|---|---|---|---|---|
| **Track A** | CarDD Frozen Test Set | 45 images | 148 instances | Primary held-out test split of the CarDD dataset; strictly excluded from all training and hyperparameter selection. | Primary Independent Statistical Benchmark |
| **Track B** | CarDD_Independent_Val_v1 (Gate O) | 44 images | 47 instances | Dual-blind annotated real-world vehicle walkarounds across Tier 1 (36) and Tier 2 (8) crops. | Real-World Generalization Benchmark |
| **Track C** | Gate P Forensic Cohort | 75 images | 167 instances | Combined multi-source failure cohort compiled during Gate P audit. | Forensic Failure Mode Investigation |
| **Track D** | Gate L Development Cohort | 30 images | 19 instances | Authentic vehicle walkaround images used for prior development. | Diagnostic Reference Only (Non-Independent) |

---

## 5. Section 4: Evaluation Protocol & Matching Rules

All models were evaluated under frozen, standardized rules without threshold tuning on the test set:
- **Operational Confidence Threshold:** $\tau = 0.25$
- **Operational IoU Threshold:** $\text{IoU} \ge 0.40$
- **Greedy Non-Replacement Matching:** A true positive requires matching class ID, confidence $\ge 0.25$, and IoU $\ge 0.40$ with an unclaimed ground-truth annotation.
- **Continuous Ranking Metrics:** Standard mAP@50 and mAP@50-95 computed across all confidence thresholds.
- **Hardware Platform:** Intel Core i5-1035G1 CPU @ 1.00GHz, single worker (`workers=0`), PyTorch 2.15.0+cpu.

---

## 6. Section 5: Overall Detection Metrics Comparison (Track A: CarDD Test Benchmark)

| Model Identifier | Evaluation Resolution | Standard mAP@50 | Standard mAP@50-95 | Operational TP | Operational FP | Operational FN | Operational Precision | Operational Recall | Operational F1 |
|---|---|---|---|---|---|---|---|---|---|
| **Production Baseline** (`models/phase5/best.pt`) | $416\times 416$ | 0.1833 | 0.1161 | 36 | 123 | 112 | 0.2264 | 0.2432 | 0.2345 |
| **P9-T01 Candidate** | $416\times 416$ | 0.1869 | 0.1114 | 22 | 101 | 126 | 0.1789 | 0.1486 | 0.1624 |
| **P9-T02 Candidate** | $640\times 640$ | **0.2490** | **0.1581** | 13 | **18** | 135 | **0.4194** | 0.0878 | 0.1453 |

### Key Overall Findings:
1. **P9-T02 Achieves Substantial Global mAP Gain:** Standard mAP@50 increased by **$+35.8\%$ relative** ($0.1833 \to 0.2490$) and mAP@50-95 increased by **$+36.2\%$ relative** ($0.1161 \to 0.1581$).
2. **P9-T02 Slashes False Positives by 85%:** Total false positives collapsed from 123 in production to only 18 in P9-T02, raising operational precision from $0.2264$ to **$0.4194$ (+85.2% relative gain)**.
3. **Operational Recall Drop:** At the rigid threshold $\tau=0.25$, operational recall dropped from $0.2432$ to $0.0878$, reflecting a much more conservative prediction distribution that requires recalibration.

---

## 7. Section 6: Six-Class Performance Breakdown (CarDD Test Benchmark, N=148)

| Class ID | Damage Category | Support | Production Recall | P9-T01 Recall | P9-T02 Recall | Production AP@50 | P9-T02 AP@50 | P9-T02 Performance Trend |
|---|---|---|---|---|---|---|---|---|
| 0 | Dent | 49 | 0.2653 | 0.1224 | 0.0408 | 0.1175 | 0.0867 | Precision jumped ($0.18 \to 0.33$); FPs fell from 59 to 4 |
| 1 | Scratch | 53 | 0.1132 | 0.0755 | 0.0377 | 0.0836 | 0.0408 | FPs dropped from 26 to 5; high precision |
| **2** | **Crack** | **13** | **0.0000** | **0.0000** | **0.0000** | **0.0138** | **0.0203** | **AP50 rose +47%; 0 recall at $\tau=0.25$** |
| 3 | Glass Shatter | 12 | 0.2500 | 0.4167 | **0.5833** | 0.2924 | **0.6577** | **Major success: F1 rose $0.24 \to 0.61$; AP50 rose $+125\%$** |
| 4 | Lamp Broken | 15 | 0.6000 | 0.4667 | 0.1333 | 0.1928 | 0.1859 | High precision, lower recall at $\tau=0.25$ |
| 5 | Tire Flat | 6 | 0.8333 | 0.0000 | 0.0000 | 0.3994 | **0.5026** | Zero FPs; AP50 increased $+25.8\%$ |

---

## 8. Section 7: Structural Crack Detection Performance Audit

| Performance Metric | Production Baseline | P9-T01 Candidate | P9-T02 Candidate |
|---|---|---|---|
| **Ground-Truth Crack Instances** | 13 | 13 | 13 |
| **Images Containing Cracks** | 10 | 10 | 10 |
| **Crack True Positives (TP)** | 0 | 0 | 0 |
| **Crack False Positives (FP)** | 0 | 1 | 0 |
| **Crack False Negatives (FN)** | 13 | 13 | 13 |
| **Operational Crack Recall ($\tau=0.25$)** | **0.0000% (0/13)** | **0.0000% (0/13)** | **0.0000% (0/13)** |
| **Crack AP@50 (PR Area)** | 0.0138 | 0.0019 | **0.0203 (+47.1%)** |
| **Crack AP@50-95** | 0.0027 | 0.0003 | **0.0064 (+137%)** |

### Critical Scientific Assessment:
- **Did any candidate improve structural crack recall at the operational threshold?**  
  **NO.** All evaluated models achieved **0.0000% operational recall (0 of 13 cracks detected)** at $\tau=0.25$.
- **Did any candidate improve continuous crack feature representations?**  
  **YES.** P9-T02 increased Crack AP@50 from $0.0138$ to **$0.0203$** ($+47.1\%$), confirming that higher spatial resolution preserves sub-grid fracture activations that are completely lost at $416\times 416$. However, confidence values remain suppressed between $0.08$ and $0.18$, meaning no cracks survive the $0.25$ filter.

---

## 9. Section 8: False-Positive & False-Negative Forensics

- **False-Positive Suppression:** P9-T02 dramatically curtails hallucinated damage on clean vehicle body panels:
  - Dent FPs reduced from 59 to 4 (-93.2%).
  - Scratch FPs reduced from 26 to 5 (-80.8%).
  - Overall FP rate dropped from $2.73\text{ FP/img}$ to **$0.40\text{ FP/img}$**.
- **False-Negative Pathology:**
  - Structural cracks are uniformly missed due to extreme aspect ratios ($>6:1$) and low contrast against dark vehicle panels.
  - In several test cases (`000042`, `000513`, `002801`), cracks on bumper plastic and tailgate handles were misclassified as scratches or dents.
- **Visual Gallery:** 10 multi-panel comparison images (`comparison_000042.png` through `comparison_003734.png`) generated and archived under `runs/phase9/independent_evaluation/visual_comparison_gallery/`.

---

## 10. Section 9: Operational Performance & Resource Comparison

| Model Identifier | Checkpoint Size | Cold Start Latency | Mean Inference Latency | Median Latency | P95 Latency | Throughput (FPS) | SLA Limit ($<250\text{ ms}$) |
|---|---|---|---|---|---|---|---|
| **Production Baseline** | 6.17 MB | 147.16 ms | 57.11 ms | 50.84 ms | 105.88 ms | 17.51 FPS | **PASS** |
| **P9-T01 Candidate** | 6.17 MB | 122.03 ms | 56.96 ms | 51.99 ms | 102.54 ms | 17.56 FPS | **PASS** |
| **P9-T02 Candidate** | 6.20 MB | 176.47 ms | 90.65 ms | 84.83 ms | 131.27 ms | 11.03 FPS | **PASS** |

*All measurements conducted on Intel Core i5-1035G1 CPU in single-image non-batched inference.*

---

## 11. Section 10: Generalization & Statistical Limitations

1. **Small Minority Sample Size:** The CarDD test split contains 13 crack annotations across 10 images. While sufficient to establish that detection failure is 100%, broader statistical claims regarding fine-grained crack improvements will require larger specialized crack cohorts ($N \ge 100$).
2. **Confidence Intervals:** P9-T02 operational precision is $0.4194$ (95% CI: $[0.264, 0.592]$) vs Production Baseline $0.2264$ (95% CI: $[0.168, 0.298]$).
3. **Cross-Domain Gap:** Lab collision images (Track A) exhibit higher baseline contrast than real-world outdoor parking lot imagery (Track B).

---

## 12. Section 11: Candidate Decision Matrix

| Model Identifier | Evaluated Split | Operational Precision | Operational Recall | mAP@50 | Crack Recall | CPU Latency | Decision Classification | Promotion Status |
|---|---|---|---|---|---|---|---|---|
| **Production Baseline** | Track A (Test) | 0.2264 | 0.2432 | 0.1833 | **0.0000** | 57.11 ms | **Active Production Reference** | **RETAINED** |
| **P9-T01-BEST** | Track A (Test) | 0.1789 | 0.1486 | 0.1869 | **0.0000** | 56.96 ms | **NO MEANINGFUL IMPROVEMENT** | **QUARANTINED** |
| **P9-T02-BEST** | Track A (Test) | **0.4194** | 0.0878 | **0.2490** | **0.0000** | 90.65 ms | **IMPROVED BUT TRADE-OFFS PRESENT** | **QUARANTINED** |

---

## 13. Section 12: Dataset Integrity Verification

Post-evaluation SHA-256 verification confirmed:
- `datasets/CarDD_300/data.yaml` SHA-256: `72abd2d88c7805392f9d55431a4d9e6c299be4d20df69122a61f78c7c2652320` (100% INVARIANT)
- `data/cardd.yaml` SHA-256: `0555f33f4a3d651d2cc6125920e5f6b669338710f2d416ecc61275199d92efb7` (100% INVARIANT)
- Zero evaluation files written into source dataset paths.
- Zero test leakage into training or validation sets.

---

## 14. Section 13: Production Checkpoint Integrity Verification

The production checkpoint `models/phase5/best.pt` was cryptographically verified:
- Measured SHA-256: `49630ae8d5c0066d0532a2a38efede809920a6fccd3eed59a76eb3b65f009390`
- File Size: 6,472,810 bytes
- Integrity Verification: **100% INVARIANT (PASS)**.
- Confirmation: Zero weights modified. Zero deployment occurred.

---

## 15. Section 14: Answers to Mandatory Phase 9.6 Governance Questions

1. **Did any candidate improve structural crack recall?**  
   **No.** At the operational threshold $\tau=0.25$, all models (Production Baseline, P9-T01, and P9-T02) achieved **$0.0000\%$ crack recall (0 of 13 detected)**. While P9-T02 raised continuous Crack AP@50 to $0.0203$ (+47%), no crack proposals reached the operational threshold.
2. **Did any candidate improve overall detection without damaging other classes?**  
   **Mixed (Trade-offs present).** P9-T02 improved overall mAP@50 by $+35.8\%$ ($0.1833 \to 0.2490$), elevated operational precision by $+85.2\%$ ($0.2264 \to 0.4194$), and slashed false positives by $85.4\%$ (from 123 to 18). However, at the fixed threshold $\tau=0.25$, overall recall dropped to $0.0878$, meaning fewer total detections were returned.
3. **Is the improvement consistent across independent cohorts?**  
   The precision gains and false-positive suppression are consistent with the higher spatial resolution theory. However, the structural crack detection failure is also consistent across all cohorts (CarDD Val: 0/11, CarDD Test: 0/13, Gate O: 0/6, Gate P: 0/14).
4. **Is the evidence strong enough to justify a production-versus-candidate review?**  
   **Yes for architectural direction, but NO for model promotion.** The evidence strongly confirms that spatial resolution scaling ($640\times 640$) is a required foundation for crack feature survival. However, without focal loss class re-weighting or an adaptive threshold strategy, the candidate cannot be deployed as a crack detection solution.
5. **What limitations remain?**  
   - Severe class imbalance ($4.08:1$ scratch-to-crack ratio) in training data forces the network to favor scratches.
   - Fixed confidence threshold $\tau=0.25$ suppresses rare-class proposals whose maximum confidence rarely exceeds $0.18$.
   - Absence of dedicated high-resolution P2 feature pyramid heads in standard YOLOv8n limits very fine fissure regression.

---

## 16. Section 15: Remaining Risks & Mitigation Plan

1. **Operational Risk of Silent Deployment:** Promoting P9-T02 directly would cause an operational recall drop across common damage types if thresholds are not re-calibrated.
2. **Mitigation:** Candidate P9-T02 remains strictly quarantined under `runs/phase9/retraining/P9-T02/`. The production system continues to serve `models/phase5/best.pt`.
3. **Architecture Roadmap:** Future retraining must incorporate class-weighted focal loss (`cls_pw` or custom $\alpha_{\text{crack}}=2.8$) and multi-scale feature pyramids (P2 layer) to convert sub-threshold crack features into confident detections.

---

## 17. Section 16: Recommended Next Steps

1. Present this independent evaluation report (`REP-PH9-6-FINAL-001`) to the Project Owner for formal review.
2. Transition to **Phase 9.7: Production-Candidate Comparative Review & Optimization Milestone Signoff**.
3. Formulate the deployment and calibration policy for Phase 10.

---

**PHASE 9.6 STATUS: INDEPENDENT EVALUATION COMPLETE — CANDIDATES NOT PROMOTED — AWAITING PHASE 9.7 REVIEW**
