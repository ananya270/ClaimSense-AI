# ClaimSense AI — Phase 9.4: Candidate Training Strategies Evaluation

**Document ID:** `REP-PH9-4-STRAT-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.4 — Training Strategy & Hyperparameter Optimization Planning  
**Status:** ARCHITECTURAL & STRATEGIC COMPARISON COMPLETE (PLANNING ONLY)  

---

## 1. Executive Summary

This report designs and evaluates six distinct, architecture-compatible candidate training strategies to address the identified bottlenecks. Each strategy is evaluated for its theoretical advantage, operational risk, failure modes, and expected impact on both crack recall and overall vehicle damage detection accuracy.

---

## 2. Strategy A — Controlled Baseline Retraining

### Core Concept:
Retain the existing YOLOv8n architecture and the standard verified `CarDD_300` split, but retrain from scratch or pre-trained `yolov8n.pt` with fully deterministic seeds, standardized input resolution ($640\times 640$), and extended training (30 epochs vs 5 epochs in Phase 5).

- **Advantages:**
  - Isolates whether the Phase 5 baseline's poor performance was merely an artifact of premature termination (5 epochs) and resolution mismatch ($416\times 416$ train vs $640\times 640$ infer).
  - Establishes a true, scientifically reproducible control for all subsequent experiments.
- **Risks & Trade-offs:**
  - Will not solve the fundamental class imbalance ($12.7\%$ cracks) or the $61.5\%$ class confusion with scratches without targeted interventions.
- **Verdict:** **MANDATORY PREREQUISITE (Experiment P9-T01).**

---

## 3. Strategy B — Class-Imbalance Mitigation

### Evaluated Methods:
1. **Class-Aware Batch Sampling:**
   - *Mechanism:* Structure data loaders so every batch contains at least one image with a `crack` annotation.
   - *Advantage:* Guarantees non-zero gradient updates for the crack classification head on every step.
   - *Risk:* With only 56 crack-containing images in `CarDD_300`, repeated sampling of the same 56 images across 30 epochs could lead to severe feature memorization and overfitting on background vehicle panels.
2. **Controlled Oversampling:**
   - *Mechanism:* Duplicate crack images by $2.0\times$ in the dataset manifest.
   - *Risk:* Overfitting risk is high unless paired with geometric and photometric augmentations.
3. **Class-Weighted Loss ($\alpha_c$):**
   - *Mechanism:* Multiply the classification cross-entropy / focal loss term for class 2 by a weighting scalar:
     $$\mathcal{L}_{\text{cls}} = -\sum_{c=0}^5 \alpha_c y_c \log(\hat{y}_c) \quad \text{with } \alpha_{\text{crack}} = 2.5 - 3.0, \, \alpha_{\text{others}} = 1.0$$
   - *Advantage:* Directly counters the $2.84:1$ instance deficit without duplicating images or causing batch loader distortion.
   - *Risk:* Too high an $\alpha$ can trigger false-positive hallucinations on high-contrast scratches. Must be capped at $3.0\times$.
- **Verdict:** **RECOMMENDED — Class-Weighted Loss + Controlled Augmentation (P9-T05).**

---

## 4. Strategy C — Crack-Oriented Augmentation

### Targeted Transformations:
| Transformation | Target Failure Mode | Parameter Range | Safety Boundary (Avoid Erasing Cracks) |
|---|---|---|---|
| **Rotational Invariance** | Slanted / curved fractures | $\pm 10^\circ$ | High rotation ($>30^\circ$) causes interpolation blur that washes out hairline cracks. |
| **Photometric Contrast Variation** | Low-contrast fractures on dark panels | `hsv_v: 0.3`, `contrast: 1.2` | Do not apply extreme histogram equalization that turns shadows into artificial cracks. |
| **Rare-Class Copy-Paste** | Underrepresentation of crack lesions | `copy_paste: 0.30` | Extract segmented crack instances from vetted pool and paste onto clean body panels. |
| **Horizontal Flipping** | Directional bias | `fliplr: 0.5` | Geometrically valid across vehicle bilateral symmetry. |
| **Controlled Mosaic** | Multi-scale lesion integration | `mosaic: 1.0`, close at ep 20 | Close mosaic for final 10 epochs to allow convergence on natural image statistics. |

### Prohibited Augmentations:
- **Severe Gaussian Blur or Downsampling:** Destroys thin fracture edges.
- **MixUp with High Alpha ($>0.2$):** Alpha blending superimposes two images, reducing the local edge contrast of hairline cracks below the detection threshold.

---

## 5. Strategy D — Resolution & Small-Object Optimization

### Resolution Evaluation Matrix:
| Resolution | Crack Visibility | Receptive Field Stride (P3) | Relative GPU Memory | CPU Training Time / Epoch | Inference Latency |
|---|---|---|---|---|---|
| **$640\times 640$** | Baseline (poor for $<15\text{ px}$) | 8 px ($80\times 80$ grid) | $1.0\times$ (approx 1.2 GB) | $\approx 45\text{ s}$ | $82.7\text{ ms}$ |
| **$832\times 832$** | Moderate (captures $10-15\text{ px}$) | 8 px ($104\times 104$ grid) | $1.7\times$ (approx 2.0 GB) | $\approx 85\text{ s}$ | $118.8\text{ ms}$ |
| **$1024\times 1024$** | Optimal (preserves native pixels) | 8 px ($128\times 128$ grid) | $2.6\times$ (approx 3.2 GB) | $\approx 150\text{ s}$ | $189.6\text{ ms}$ |

### Architectural Modification (P2 Feature Pyramid Layer):
- Standard YOLOv8 operates on P3 (stride 8), P4 (stride 16), P5 (stride 32).
- Integrating a **P2 layer (stride 4)** produces a $256\times 256$ feature grid at $1024\times 1024$ resolution, providing the receptive field necessary to anchor 5–10 pixel fissures without feature vanishing.
- **Verdict:** **HIGH-PRIORITY EXPERIMENTAL TRACK (P9-T02).**

---

## 6. Strategy E — Loss & Optimization Formulation

1. **Optimizer Comparison:**
   - Baseline uses SGD (`momentum: 0.937`).
   - For fine-grained lesion detection with class weighting, **AdamW** (`lr0: 0.001`, `weight_decay: 0.0005`) provides faster convergence and avoids saddle points on highly elongated loss surfaces.
2. **Bounding-Box Regression Loss (Wise-IoU / Inner-IoU):**
   - Replace standard CIoU with **Wise-IoU v3** or **Inner-IoU**.
   - Standard CIoU penalizes aspect ratio deviation, which destabilizes training on $14:1$ elongated cracks. Wise-IoU uses a dynamic non-monotonic focusing mechanism that assigns higher weight to normal-quality anchor boxes and downweights outliers.
3. **Loss Balancing:**
   - Adjust baseline loss weights from `box: 7.5, cls: 0.5` to `box: 7.5, cls: 1.5, dfl: 1.5`. Elevating classification loss by $3.0\times$ directly forces the network to resolve scratch vs crack confusion.

---

## 7. Strategy F — Domain Generalization & Field Robustness

- **Domain Discrepancy:** CarDD images are crash-damaged vehicles in workshops. Real-world insurance claims include outdoor daylight vehicle walkarounds.
- **Safe Implementation:** Ingest authentic walkaround vehicle photographs with vetted crack damage (+40 cracks) into the training dataset.
- **Safety Restriction:** Under NO circumstances may images from Gate O (frozen independent validation) or Gate P (forensic evaluation) be integrated into training. All domain adaptation assets must originate from vetted independent pools (e.g. `CarDD_DomainAdaptation_v1` training split).
