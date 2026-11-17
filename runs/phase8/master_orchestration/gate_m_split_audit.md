# ClaimSense AI — Phase 8: Gate M Leakage-Aware Data Splitting Audit

**Document ID:** `AUD-PH8-GATE-M-SPLIT-001`  
**Audit Date:** 2026-11-17  
**Dataset:** `datasets/CarDD_DomainAdaptation_v1/`  
**Governing Specification:** `acquisition_specification.md` v1.1-ACTIVE  
**Execution Boundary:** Train/Dev Stratification & Isolation Certification (Gate M Pass)

---

## 1. Executive Summary & Split Ratios

The 120-image domain adaptation dataset was partitioned into a **75% Train (90 images)** and **25% Development (30 images)** split using stratified random sampling across all 4 acquisition categories:

| Dataset Split | Clean Undamaged | Broken Lamp | Deflated Tire | Minor Cosmetic | Total Images | Share (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Train Split** | 34 | 19 | 19 | 18 | **90** | **75.0%** |
| **Development Split** | 11 | 6 | 6 | 7 | **30** | **25.0%** |
| **Total Cohort** | **45** | **25** | **25** | **25** | **120** | **100.0%** |

---

## 2. Absolute Benchmark Isolation Certification

To prevent data snooping, benchmark overfitting, and data leakage:
1. **Zero Overlap with Independent Validation Benchmark:**  
   The frozen 44-image validation benchmark (`datasets/CarDD_Independent_Val_v1/`) shares **strictly 0 images and 0 hashes** with either the Train or Dev split.
2. **Usage Boundaries:**  
   The frozen 44-image validation set:
   - Must **NOT** be used for training.
   - Must **NOT** be used for data augmentation.
   - Must **NOT** be used for checkpoint selection.
   - Must **NOT** be used for hyperparameter tuning.
   - Must **NOT** be used for confidence threshold selection.
   - Must **NOT** be used for early stopping.
3. **Internal Split Independence:**  
   $$\\text{Train} \\cap \\text{Dev} = \\emptyset \\quad (|\\text{Train} \\cap \\text{Dev}| = 0)$$

---

## 3. Split Manifests & Configuration Files

* **Train Manifest:** [`datasets/CarDD_DomainAdaptation_v1/manifests/train_split.csv`](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/datasets/CarDD_DomainAdaptation_v1/manifests/train_split.csv) (90 images)
* **Dev Manifest:** [`datasets/CarDD_DomainAdaptation_v1/manifests/dev_split.csv`](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/datasets/CarDD_DomainAdaptation_v1/manifests/dev_split.csv) (30 images)
* **YOLO Dataset Config:** `data/domain_adaptation_dev.yaml`
