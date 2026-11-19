# ClaimSense AI — Phase 9.2: Investigation Completion & Certification Report

**Project:** ClaimSense AI  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.2 — Structural Crack Detection Failure Analysis & Root Cause Investigation  
**Previous Stage:** Phase 9.1 — Model Performance Re-evaluation & Comparative Benchmark  
**Previous Milestone:** Phase 8 officially closed at Gate P  
**Status:** COMPLETED & FULLY SEALED  
**Date:** 2026-11-19  

---

## 1. Executive Summary

Phase 9.2 was formally executed to conduct an evidence-backed forensic investigation into the catastrophic failure of structural crack detection across all ClaimSense AI vehicle damage detection models. Historically, all models—including the Phase 5 production baseline, Session 2, EXP01, EXP02, and EXP03—exhibited a **$0.0\%$ operational recall ceiling** on structural cracks in both the Gate O independent validation benchmark ($0/6$) and the Gate P combined forensic audit ($0/14$).

In strict accordance with the Mission guidelines:
- **Zero models were trained or fine-tuned.**
- **No checkpoint or weight file was modified or overwritten.**
- **No dataset, label file, or benchmark split was altered.**
- **No production database write or live shadow trial was initiated.**
- All experiments and deliverables were executed inside an isolated workspace under `runs/phase9/crack_investigation/`.

The investigation successfully identified the **three confirmed root causes** of crack detection failure:
1. **Class Confusion (Scratch Dominance):** In $61.5\%$ of test failures, the model successfully localized the damage lesion (IoU up to $0.56$), but misclassified it as `scratch` ($46.2\%$) or absorbed it into `dent` ($15.4\%$).
2. **Annotation Inconsistency & Co-occurring Overlap:** $35.7\%$ of CarDD crack annotations exhibit severe anomalies, including 14 cases where annotators drew overlapping `scratch` and `crack` boxes on the exact same physical feature, providing self-contradictory supervisory signals.
3. **Feature Vanishing on Sub-Grid Scales:** Cracks have a median normalized area of only $0.0069$ (nearly $8\times$ smaller than scratches and dents), with lower-quartile fissures spanning under $15\times 15$ pixels, which completely vanish during resizing to $640\times 640$ on YOLOv8's P3-P5 feature pyramids.

---

## 2. Deliverables Inventory & Cryptographic Integrity

All 10 requested deliverables have been generated, validated, and stored in `runs/phase9/crack_investigation/`:

| # | File Name | Type | Size | SHA-256 Checksum |
|---|---|---|---|---|
| 1 | `phase9_2_dataset_crack_inventory.csv` | Data Inventory | 1,709 bytes | `7028e9a8eb5ffee2b2bf1127a9c99c425953bc4c775ce1f22e15fd0dda5cd78b` |
| 2 | `phase9_2_annotation_quality_audit.csv` | Quality Audit | 23,688 bytes | `03c4315f33d5e906d84b8f4335ac74a8b309b96147d5acb6e40c69f6bd03168f` |
| 3 | `phase9_2_crack_detection_failures.csv` | Failure Tracking | 2,926 bytes | `5bb1d5691c9af0b41cb0aba72f23496297063c9181fde3e3bfed23ba7a030443` |
| 4 | `phase9_2_scratch_vs_crack_confusion.csv` | Confusion Matrix | 1,608 bytes | `f453d30c9567f547ff0d58645b72f7841f1a3068020979ceef316fa600055124` |
| 5 | `phase9_2_confidence_sensitivity.csv` | Sensitivity Study | 1,105 bytes | `eb5ba234d634eca0b375ae484da024f328759c29e38d3abeb7dd67951e8b05cb` |
| 6 | `phase9_2_resolution_sensitivity.csv` | Scale Study | 738 bytes | `b445507566f81b19ec5903d4808f356b1e075af7425fa05b01e3f53ae664ce84` |
| 7 | `phase9_2_visual_forensic_gallery/` | Image Gallery | 10 files | 10 annotated high-resolution comparison photographs |
| 8 | `phase9_2_root_cause_analysis.md` | Core Report | 14,820 bytes | Comprehensive forensic evidence documentation |
| 9 | `phase9_2_remediation_recommendations.md` | Strategy Plan | 10,250 bytes | 4-pillar EXP04 optimization roadmap |
| 10 | `phase9_2_completion_report.md` | Final Sign-off | This Document | Formal verification and milestone closure |

---

## 3. Quantitative Synthesis of Investigation Findings

### 1. Dataset-Level Inventory
- **`CarDD_300` Subset:** 300 images total, containing **115 structural crack instances** (train: 91, val: 11, test: 13).
- **Additional 100-Image CarDD Pool:** Contains **78 high-priority crack instances** vetted for zero leakage (min Hamming distance $\ge 15$).
- **Expanded CarDD Dataset (`CarDD_Expanded_v1`):** 210 train images, 91 cracks (consolidated from baseline).
- **Independent Validation Benchmark (Gate O):** 44 frozen images, **6 verified crack instances**.
- **Domain Adaptation Dev Cohort (Gate L):** 30 authentic walkaround images, **0 crack instances** (identifying a major external data deficit).

### 2. Geometry & Scale Analysis
- Median crack normalized area: **$0.0069$** ($68.9\text{ px} \times 69.4\text{ px}$ on native $1000\times 667$ images).
- Cross-class scale disparity: Cracks are **$7.95\times$ smaller than scratches** (median $0.0451$), **$7.96\times$ smaller than dents** (median $0.0549$), and **$62.56\times$ smaller than glass shatter** (median $0.4317$).
- Aspect ratio elongation: Mean $2.70:1$, max $14.31:1$, making standard CIOU axis-aligned bounding boxes highly inefficient.

### 3. Annotation Quality Findings
- $41$ of $115$ crack annotations ($35.7\%$) exhibit anomalies.
- $14$ cases exhibit severe co-occurring overlap where annotators placed both a `crack` box and a `scratch` box over the exact same panel lesion.
- $8$ cases feature sub-grid boxes (area $<0.0005$, $<15\text{ px}$).

### 4. Operational Failure Breakdown (Test Set, 13 Cracks)
- **Misclassified as `scratch`:** $6$ cases ($46.2\%$) with IoU up to $0.56$.
- **Absorbed into `dent`:** $2$ cases ($15.4\%$) with IoU up to $0.54$.
- **Feature Vanishing (zero proposal):** $5$ cases ($38.5\%$).
- **True Positives Detected at Operational Threshold ($\tau=0.25$, $\text{IoU}\ge 0.40$):** **$0$ ($0.0\%$ recall)**.

### 5. Threshold & Resolution Sensitivity Experiments
- **Confidence Sensitivity ($\tau \in [0.05, 0.50]$):** Reducing threshold to $\tau=0.05$ fails to recover any true crack detections ($\text{TP}=0$), while increasing false positives from $147$ to $990$ (a $6.73\times$ increase).
- **Resolution Sensitivity ($640$ vs $832$ vs $1024$):** Purely increasing inference resolution on an existing model trained at $640\times 640$ yields zero additional true crack detections ($\text{TP}=0$ across all resolutions), while increasing inference latency from $82.7\text{ ms}$ to $189.6\text{ ms}$.

---

## 4. Final Engineering Verdict & Phase Sign-Off

1. **Available Cracks:** $115$ in `CarDD_300`, $78$ in the additional 100-image pool, $6$ in Gate O independent validation. Exactly $0$ in Gate L authentic walkaround dev split.
2. **Class Imbalance:** Cracks constitute only $12.75\%$ of training annotations, outnumbered $2.8\times$ by scratches and $2.6\times$ by dents.
3. **Confirmed Root Causes:**
   - Visual class confusion with cosmetic scratches.
   - Self-contradictory annotation overlap in source dataset.
   - High-stride feature pyramid vanishing on sub-grid defects.
4. **Unresolved Hypotheses:** None. All 8 hypotheses were tested and classified with empirical measurements.
5. **Remediation Plan for EXP04:**
   - Ingest 78 cracks from the 100-image pool + acquire 40 authentic walkaround cracks (target $200+$ training cracks).
   - Clean contradictory overlapping annotations.
   - Train at $1024\times 1024$ with P2 high-resolution feature pyramid (stride 4).
   - Implement Wise-IoU loss and $2.8\times$ crack class weighting.
   - Utilize SAHI slicing for ultra-high-resolution inference.

Phase 9.2 is hereby officially certified as **COMPLETE**. In accordance with Phase 9 governance, **all execution is paused awaiting explicit human authorization before commencing Phase 9.3 or any model training.**
