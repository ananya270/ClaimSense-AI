# ClaimSense AI — Phase 9.11: Dataset Provenance & Independent Benchmark Specification

**Project:** ClaimSense AI (Final-Year B.Tech Major Project)  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.11 — Final Documentation, Reproducibility & Project Sign-off  
**Document Classification:** Scientific Dataset Registry & Benchmark Standard  
**Date:** 2026-11-20

---

## 1. Executive Summary

This document formalizes the provenance, partition manifests, class balance statistics, and data governance protocols for all dataset splits utilized during ClaimSense AI model training, validation, and independent benchmarking.

To guarantee scientific reproducibility and prevent data leakage, evaluation benchmarks were conducted on strictly sequestered data partitions that were never exposed during model training or hyperparameter tuning.

---

## 2. Dataset Origin & Physical Structure

The computer vision training and evaluation ecosystem is centered on **CarDD (Car Damage Dataset)**, a standardized benchmark dataset for vehicle damage detection and localization:

- **Repository Root:** `datasets/CarDD_300/`
- **Dataset YAML Specification:** `datasets/CarDD_300/data.yaml`
- **Annotation Format:** Standard YOLO Bounding Box Format (`class_id x_center y_center width height` normalized $\in [0.0, 1.0]$).

```
datasets/CarDD_300/
├── train/                          # Supervised Model Retraining Partition
│   ├── images/                     # 210 vehicle accident photographs
│   └── labels/                     # 210 YOLO format annotation text files
├── valid/                          # Hyperparameter Tuning & Early Stopping Partition
│   ├── images/                     # 45 vehicle accident photographs
│   └── labels/                     # 45 YOLO format annotation text files
└── test/                           # Protected Independent Evaluation Benchmark (Track A)
    ├── images/                     # 45 vehicle accident photographs (unseen during training)
    └── labels/                     # 45 YOLO format ground truth annotation files
```

---

## 3. Independent Benchmark Test Partition Manifest (Track A)

The authoritative independent benchmark evaluation (conducted in Phase 9.6) utilized the sequestered `test/` partition:

- **Total Test Images:** 45 photographs
- **Total Ground Truth Damage Instances:** 148 instances

### Ground Truth Class Distribution Breakdown:

| Class ID | Categorical Label | Instance Count | Class Proportion (%) | Geometric & Visual Characteristics |
| :---: | :--- | :---: | :---: | :--- |
| **0** | **Dent** | 59 | 39.86% | Large spatial area; concave sheet metal deformations. |
| **1** | **Scratch** | 50 | 33.78% | Linear / streak paint abrasions; surface-level contrast. |
| **2** | **Crack** | 13 | 8.78% | **Critical Minority:** Fine hairline fractures; narrow width ($<5$ px); low contrast. |
| **3** | **Glass Shatter** | 7 | 4.73% | Webbed / spiderweb windshield fracturing patterns. |
| **4** | **Lamp Broken** | 13 | 8.78% | Headlamp / taillamp assembly structural shatter. |
| **5** | **Tire Flat** | 6 | 4.05% | Deflated wheel rim contact with asphalt / wheel arch drop. |
| **TOTAL** | **All 6 Classes** | **148** | **100.00%** | Comprehensive vehicle damage representation. |

---

## 4. Benchmark Track B: Out-of-Distribution & Robustness Suite

In addition to the standard CarDD test partition, Phase 9 evaluated models on **Track B (Robustness & Fraud Prevention)**:
- **Purpose:** Test model resilience against non-vehicle imagery, synthetic documents, policy diagrams, and low-quality captures.
- **Test Ingestion:** Evaluates whether forensic image filters (`backend/services/receipt.py:validate_vehicle_image`) correctly intercept non-photographic artifacts.
- **Outcome:** The forensic validator correctly flagged and rejected solid graphic cards (`invalid_graphic`), ensuring only authentic vehicle imagery enters the YOLOv8 pipeline.

---

## 5. Benchmark Protocol & Evaluation Standards

To maintain objective evaluation standards across all phases, the evaluation protocol was fixed:

1. **Intersection-over-Union (IoU) Thresholds:**
   - Standard mAP: $IoU = 0.50$ (PASCAL VOC standard).
   - Strict mAP: $IoU \in [0.50 : 0.95]$ in increments of $0.05$ (COCO standard).
2. **Operational Confidence Thresholds ($\tau$):**
   - High Sensitivity: $\tau = 0.10$
   - Default Production Detection: $\tau = 0.15$
   - Strict Decision & Promotion Gate: $\tau = 0.25$
   - High Precision: $\tau = 0.50$
3. **Reproducible Evaluation Harness:**
   - Evaluated via `scratch/evaluate_track_a.py` and `ultralytics.models.yolo.detect.DetectionValidator`.

---

## 6. Data Integrity & Leakage Prevention Statement

It is certified that:
- The independent test set (`datasets/CarDD_300/test/`) was strictly segregated.
- No test set images or labels were present in training manifests or validation splits.
- All benchmark metrics reported in Phase 9 reflect genuine generalization performance on unseen photographic evidence.
