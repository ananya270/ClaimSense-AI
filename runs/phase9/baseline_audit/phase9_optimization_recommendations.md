# ClaimSense AI — Phase 9.0: Optimization Opportunity Analysis & Technical Roadmap

**Document ID:** `AUD-PH9-OPT-REC-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.0 — Baseline Audit  
**Date:** 2026-11-19  
**Governing Standard:** `acquisition_specification.md` v1.1-ACTIVE  
**Audit Scope:** Evidence-Based Identification of Model Deficiencies and Technical Proposals for Phase 9 Optimization

---

## 1. Executive Summary

Based on the empirical evidence gathered during Phase 8 (Gate N experiments, Gate O independent benchmark, and Gate P forensic audit), this document outlines the core optimization opportunities for Phase 9. Each technical recommendation directly addresses a proven limitation in the existing models without introducing unverified assumptions.

---

## 2. Core Technical Challenges & Root-Cause Evidence

| Problem Area | Empirical Evidence | Root-Cause Analysis | Impact on Insurance Operations |
| :--- | :--- | :--- | :--- |
| **Structural Crack Recall Deficit** | EXP02 achieved **0.0% recall** (0/14 TP) on structural cracks; Production achieved 0.0% precision with 1,139 false crack alarms. | 1. Extreme training under-representation (only 3 crack instances in DA training cohort).<br/>2. Severe spatial downsampling at 640x640 attenuating hairline features.<br/>3. Glare-suppression penalties in negative mining suppressing weak crack signals. | High risk of undetected frame, bumper, or windshield fractures, leading to hazardous underpaid claims. |
| **Rare-Class Imbalance** | Dents account for **45.8%** of CarDD annotations; Cracks, Lamp Broken, and Tire Flat historically accounted for $< 10\%$ each. | Extreme loss dominance by dent and scratch classes during backpropagation; gradients from rare classes are overwhelmed by common classes. | Inconsistent multi-class detection, requiring manual human adjuster intervention. |
| **Daylight Specularity & Reflection** | Production generated **6,503 false alarms** on 75 test images (869 on 11 clean vehicles). | High-frequency specular reflections and asphalt textures mimic defect edges when models lack background penalty training. | Severe adjuster alert fatigue, rendering automated triaging unusable without human filters. |
| **Aggregate Operational Recall Trade-Off** | EXP02 precision reached **48.2%**, but aggregate recall was limited to **16.2%** at $\tau=0.25$. | A global confidence threshold ($\tau=0.25$) is too conservative for subtle scratches and hairline cracks while being appropriate for large dents. | Genuine defects with confidence scores between $0.10$ and $0.24$ are dropped. |
| **Input Resolution vs Compute Contradiction** | Session 3 (1024px) dropped mAP from 0.4414 to 0.3989 due to batch reduction to 2. | Doubling resolution quadruples memory consumption ($O(H \cdot W)$), forcing small batch sizes that introduce high gradient variance. | Inability to train native high-resolution models without gradient accumulation or memory-efficient backbones. |

---

## 3. Evidence-Based Optimization Recommendations for Phase 9

### 1. Structural Crack Recovery: High-Resolution Sliced Inference (SAHI) & Patch Training
* **Evidence:** Downsampling an authentic $3024 \times 4032$ vehicle image to $640 \times 640$ compresses a 2mm hairline crack down to $< 0.3$ pixels, making feature detection physically impossible for standard CNN/transformer backbones.
* **Proposed Mechanism:**
  - Implement **Sliced Aided Hyper Inference (SAHI)** or tile-based inference ($2 \times 2$ or $3 \times 3$ overlapping crops at native resolution).
  - Train a dedicated high-resolution sub-network or specialized head focused on cropped regions of interest (ROI) where panel boundaries and seams occur.

### 2. Rare-Class Loss Re-Weighting & Dynamic Focal Loss
* **Evidence:** In `CarDD_DomainAdaptation_v1`, cracks represent only 3/75 annotations, causing crack loss gradients to be diluted by 96%.
* **Proposed Mechanism:**
  - Implement inverse-frequency class weighting ($\alpha_c = \frac{1}{\sqrt{N_c}}$) in YOLOv8's classification loss ($\mathcal{L}_{cls}$).
  - Increase the focusing parameter $\gamma$ in focal loss (from 1.5 to 2.5) to down-weight easy background examples and force model capacity onto hard rare classes (cracks and punctured tires).

### 3. Balanced Negative Background Mining Ratio
* **Evidence:** In EXP01 and EXP02, clean vehicles comprised **37.5% of all images** (45/120 images). While this eliminated 99.55% of false positives, it over-penalized subtle authentic features.
* **Proposed Mechanism:**
  - Calibrate the negative image ratio to **15%–20%** of the training cohort (approximately 1 negative image for every 4–5 defect images).
  - Use selective hard-negative mining (images with harsh glare or reflections) rather than random clean vehicles.

### 4. Specular Reflection Augmentation (Daylight Robustness)
* **Evidence:** Daylight walkarounds exhibit bright sunlight specular spots that trigger false dent/crack proposals.
* **Proposed Mechanism:**
  - Introduce synthetic specular glare augmentation during training (random high-intensity white/yellow Gaussian blobs and linear reflections across panels).
  - Apply random brightness contrast shifts specifically targeting the Value (V) channel in HSV color space to train the network to ignore lighting glares.

### 5. Multi-Scale Training with Gradient Accumulation
* **Evidence:** Session 3 showed that halving batch size to 2 caused gradient noise that degraded mAP50.
* **Proposed Mechanism:**
  - Maintain an effective batch size of **16** using gradient accumulation (`accumulate=4` with physical `batch=4` or `accumulate=8` with physical `batch=2`).
  - Train with multi-scale jitter (`imgsz=640` with random scale variations between 480 and 800) to ensure scale invariance across near and far perspectives.

### 6. Per-Class Operational Threshold Calibration
* **Evidence:** Evaluating all six classes with a single threshold $\tau=0.25$ discards subtle cracks and scratches while allowing dent false alarms.
* **Proposed Calibration:**
  - **Dents:** $\tau = 0.30$ (High visual salience; suppress glare).
  - **Scratches:** $\tau = 0.20$ (Moderate subtlety; balance precision).
  - **Cracks:** $\tau = 0.15$ (Low optical contrast; recover recall).
  - **Glass Shatter:** $\tau = 0.25$ (High structural contrast).
  - **Lamp Broken:** $\tau = 0.25$ (Consistent geometric context).
  - **Tire Flat:** $\tau = 0.35$ (High context; suppress tire tread noise).

### 7. Transfer Learning & Backbone Freezing Strategy
* **Evidence:** Fine-tuning the entire network with standard learning rates led to loss of general feature representation.
* **Proposed Mechanism:**
  - Freeze the first 10 layers of YOLOv8 (the CSPDarknet backbone) during the first 10 epochs to preserve low-level edge and texture filters.
  - Fine-tune strictly the neck (PAN-FPN) and detection heads with a reduced learning rate (`lr0 = 0.0005`, `lrf = 0.01`, cosine annealing).

---

## 4. Phase 9 Proposed Experiment Roadmap (Pre-Training Overview)

* **Experiment 9.1 (Baseline Replication & Re-anchoring):** Establish an exact reproducible baseline on current hardware.
* **Experiment 9.2 (Loss & Class Re-weighting):** Implement focal loss calibration and rare class weighting to restore crack gradient magnitude.
* **Experiment 9.3 (Resolution & SAHI Evaluation):** Evaluate patch slicing for sub-millimeter crack detection.
* **Experiment 9.4 (Dynamic Per-Class Post-Processing):** Calibrate per-class operational thresholds on the development set.

*Execution Notice:* No training experiments will be initiated until explicit human authorization is received.
