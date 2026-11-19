# ClaimSense AI — Phase 9.2: Structural Crack Detection Remediation Recommendations

**Project:** ClaimSense AI  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.2 — Structural Crack Detection Failure Analysis & Root Cause Investigation  
**Target Milestone:** EXP04 (Targeted Structural Crack & Rare Class Optimization)  
**Status:** COMPLETE & PROPOSED FOR HUMAN RATIFICATION  

---

## 1. Executive Remediation Framework

Based on the quantitative findings in `phase9_2_root_cause_analysis.md`, the failure of structural crack detection is driven by a trifecta of:
1. **Annotation Contradiction & Noise:** Co-occurring scratch overlap teaching the model that cracks are scratches.
2. **Feature Vanishing:** Resizing $1000\times 667$ images to $640\times 640$ on a P3-P5 feature pyramid destroys narrow hairline fracture gradients.
3. **Severe Class Imbalance & Loss Attenuation:** Cracks represent only $12.7\%$ of training annotations, allowing scratch and dent gradients to dominate optimization.

To overcome the historical $0.0\%$ recall barrier in EXP04, a structured 4-pillar remediation program is required:

```
+---------------------------------------------------------------------------------------------------+
| 4-PILLAR EXP04 REMEDIATION ROADMAP                                                                |
+---------------------------------------------------------------------------------------------------+
| Pillar 1: Evidence-Backed Dataset Expansion                                                        |
|   - Ingest 78 cracks from the vetted 100-image CarDD pool (Hamming >= 15).                         |
|   - Acquire 40 authentic daylight walkaround bumper fracture instances.                           |
|   - Reach 200+ total training crack instances (target 25-30% class share).                        |
|                                                                                                   |
| Pillar 2: Annotation Disambiguation & Relabeling                                                  |
|   - Enforce strict mutual exclusivity between cosmetic scratches and structural cracks.           |
|   - Eliminate overlapping bounding boxes on the same panel defect.                                |
|   - Apply standardized bounding-box tightness rules to high-elongation fractures.                  |
|                                                                                                   |
| Pillar 3: Model Architecture & High-Resolution Training                                          |
|   - Upgrade training resolution to 1024x1024 (or multi-scale 640-1024).                           |
|   - Integrate P2 feature pyramid layer (stride 4) to preserve sub-pixel lesion edges.              |
|   - Implement Wise-IoU / Inner-IoU loss to stabilize slender bounding-box regression.             |
|                                                                                                   |
| Pillar 4: Loss Rebalancing & Training Hyperparameters                                             |
|   - Assign class-weighting factor alpha_crack = 2.5x - 3.0x in classification loss.               |
|   - Bias Mosaic and MixUp augmentations toward crack-containing image tiles.                       |
|   - Implement SAHI (Slicing Aided Hyper Inference) for inference on high-resolution walkarounds.  |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Pillar 1: Evidence-Backed Dataset Requirements

### Quantitative Deficit Analysis:
- Current training set: **91 crack instances** across 210 images ($12.75\%$ share).
- Dent training instances: 230 ($32.2\%$).
- Scratch training instances: 204 ($28.6\%$).
- Ratio of scratch-to-crack: **$2.24 : 1$**. Ratio of dent-to-crack: **$2.53 : 1$**.

### Target Training Distribution for EXP04:
To reach parity and provide adequate statistical coverage across fracture morphologies:
1. **Immediate Local Asset Ingestion (The 100-Image CarDD Pool):**
   - Source: `runs/phase8/cardd_100_selection_manifest.json`.
   - Vetted status: Cryptographically checked, min Hamming distance $\ge 15$ against `CarDD_300`.
   - Ingestion yield: **+78 crack instances**, +56 scratches, +39 dents across 100 images.
   - Post-ingestion training crack count: **169 crack instances** ($169 / 864 = 19.56\%$ share).
2. **Targeted Outdoor Walkaround Crack Ingestion:**
   - Source: Authentic daylight vehicle damage photography (plastic bumper splits, headlamp bracket fractures, rocker panel cracks).
   - Target acquisition: **35 to 50 crack instances** across 30–40 new images.
   - Target final training crack count: **$205 - 220$ crack instances** ($\approx 25\%$ share of all training defects).

---

## 3. Pillar 2: Annotation Disambiguation & Relabeling Protocol

The audit revealed 14 severe cases of overlapping scratch and crack boxes on identical damage features. The following rules must be codified:

### Rule 1: Structural Depth Priority (Mutual Exclusivity)
- If a damage lesion penetrates the panel surface creating a through-fracture, split, or seam separation in plastic/metal, the **entire lesion must be labeled exclusively as `crack`**.
- It is **strictly prohibited** to draw an overarching `scratch` box over a crack lesion. Surrounding minor scuffs within 20 mm of the fracture boundary are considered part of the fracture impact zone.

### Rule 2: Multi-Branch and Slender Fracture Tightness
- For single continuous linear cracks: the bounding box must fit the active fissure snugly.
- For spider-web / radiating fracture patterns (shattered plastic fascia):
  - If the fissures are within 50 mm of each other: annotate as a single composite `crack` box.
  - If distinct isolated fractures occur on separate body panels: annotate as independent crack boxes.

### Rule 3: Separation of Cosmetic Scratches from Panel Cracks
- **Scratch (Class 1):** Surface abrasion, clearcoat scuff, primer gouge without material separation.
- **Crack (Class 2):** Complete physical separation of panel substrate, visible depth fissure, or plastic bumper tear.

---

## 4. Pillar 3: Architecture & High-Resolution Training Strategy

### 1. Training at High Resolution ($1024\times 1024$)
- Feature resolution analysis showed median crack dimensions are $68.9\text{ px} \times 69.4\text{ px}$ on $1000\times 667$ images.
- Training at $1024\times 1024$ preserves feature scale at $1.02\times$ native resolution, preventing downsampling loss.
- Small cracks ($<15\text{ px}$) will occupy $>2.0$ cells at P3 instead of vanishing below $1.0$ cell.

### 2. High-Resolution P2 Feature Pyramid Level (Stride 4)
- Standard YOLOv8 starts feature detection at P3 (stride 8, $80\times 80$ at $640\times 640$).
- Adding a P2 detection head ($160\times 160$ at $640\times 640$, or $256\times 256$ at $1024\times 1024$) introduces stride-4 receptive fields specifically tuned for thin line features like cracks and wires.

### 3. Slender Bounding-Box Regression Loss (Wise-IoU / Inner-IoU)
- Standard CIOU loss penalizes aspect ratio deviation via:
  $$v = \frac{4}{\pi^2} (\arctan \frac{w^{gt}}{h^{gt}} - \arctan \frac{w}{h})^2$$
  On elongated defects ($>6:1$), small boundary shifts produce massive gradients that destabilize training.
- Replacing CIOU with **Inner-IoU** or **Wise-IoU v3** decouples scale and aspect-ratio sensitivity, dramatically accelerating convergence on slender fractures.

---

## 5. Pillar 4: Loss Rebalancing & Training Hyperparameters for EXP04

### Recommended Hyperparameter Configuration:
```yaml
# Proposed EXP04 Configuration
model: yolov8n.pt (fine-tuned from Phase 5 baseline or Session 2)
imgsz: 1024
epochs: 30
batch: 8  # Adjusted for CPU / memory headroom
optimizer: AdamW
lr0: 0.001
lrf: 0.01

# Loss Rebalancing
cls: 1.5           # Elevated classification weight
box: 7.5           # Bounding-box regression weight
dfl: 1.5           # Distribution focal loss weight

# Class Weighting
class_weights:
  dent: 1.0
  scratch: 1.0
  crack: 2.8       # 2.8x focal loss boost on structural crack
  glass shatter: 1.2
  lamp broken: 1.2
  tire flat: 1.5

# Augmentation Strategy
mosaic: 1.0        # Enabled
mixup: 0.15        # Slight mixup for regularization
copy_paste: 0.30   # Rare class copy-paste specifically targeting crack lesions
degrees: 10.0      # Rotational invariance for slanted cracks
fliplr: 0.5
flipud: 0.2
```

---

## 6. Inference Pipeline Recommendations

1. **Patch-Based Inference (SAHI):**
   - For high-resolution authentic vehicle photographs ($1920\times 1080$ and $4000\times 3000$), resize-based inference obliterates hairline cracks.
   - Incorporate Slicing Aided Hyper Inference (SAHI) with $640\times 640$ sliding windows and $20\%$ overlap.
   - Slices maintain $100\%$ pixel fidelity, enabling the standard detector to identify tiny cracks without architectural bloating.
2. **Class-Specific Calibrated Thresholds:**
   - Preserve $\tau=0.25$ for dent and scratch.
   - Post-EXP04, establish calibrated operational thresholds per class based on harmonic F1 optimization.

---

## 7. Next Steps & Phase Progression

- Phase 9.2 is complete and all findings are empirically sealed.
- **NO retraining or model modification has taken place.**
- Human executive sign-off is required before progressing to **Phase 9.3 (Dataset Preparation & EXP04 Training)**.
