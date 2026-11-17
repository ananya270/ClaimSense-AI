# Phase 8 — CarDD Dataset Readiness & Annotation Audit

**Project:** ClaimSense AI  
**Module:** Phase 8 Computer Vision Dataset & Annotation Quality Audit  
**Date:** November 17, 2026  
**Audited Dataset:** `datasets/CarDD_300/` (Train: 210 images, Val: 45 images, Test: 45 images; Total: 300 images)  
**Status:** Completed — Audit Findings Documented (No Labels Modified)  

---

## 1. Executive Summary

This audit evaluates the CarDD dataset used for fine-tuning YOLOv8n damage detection within ClaimSense AI. Following the regression observed in Session 3 (1024px) against Session 2 (640px), this investigation directly examines whether dataset volume, class imbalance, annotation granularity, or visual domain coverage form the true bottleneck for small-damage detection (`crack`, `scratch`, `dent`).

### Key Findings
1. **Severe Class Imbalance:** `crack` represents only **91 training instances** across 56 images (out of 210 train images), compared to 258 `scratch` and 234 `dent` instances.
2. **Extreme Scale Disparity:** Median normalized bounding box area for `crack` is **0.0069** (0.69% of image area) — **8x smaller than dent (0.0552)** and **62x smaller than glass shatter (0.4317)**. 
3. **Fragmented Scratch Labeling:** Over 12% of training images (26 images) represent single continuous scratches as multiple (3 to 6) disjoint bounding boxes, confusing bounding box regression and penalizing IoU matching.
4. **Widespread Missing Crack Labels:** 100 out of 210 training images exhibit severe impact damage (`dent`, `lamp broken`, `glass shatter`) on bumper and body panels, but contain zero crack annotations.
5. **Lighting and Specular Glare Ambiguity:** Glossy paint reflections on curved panels (hood, fender arcs) closely mimic scratch geometry, causing high false-positive rates on high-resolution passes.

---

## 2. Image and Instance Distribution Across Splits

The 300-image dataset is partitioned into 210 train (70%), 45 validation (15%), and 45 test (15%) images.

### Instance & Image Presence Table

| Damage Class | Train Instances (Images) | Val Instances (Images) | Test Instances (Images) | Total Instances | % of All Instances |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`dent`** | 234 (142) | 44 (31) | 49 (30) | **327** | 33.6% |
| **`scratch`** | 258 (154) | 60 (36) | 53 (29) | **371** | 38.1% |
| **`crack`** | **91 (56)** | **11 (10)** | **13 (10)** | **115** | **11.8%** |
| **`glass shatter`** | 45 (45) | 10 (10) | 12 (12) | **67** | 6.9% |
| **`lamp broken`** | 64 (62) | 10 (10) | 15 (15) | **89** | 9.2% |
| **`tire flat`** | 22 (22) | 5 (5) | 6 (6) | **33** | 3.4% |
| **TOTAL** | **714 (210)** | **140 (45)** | **148 (45)** | **1,002** | **100.0%** |

> [!WARNING]
> While `dent` and `scratch` have over 300 instances, `crack` has only 91 training instances. In the validation split, there are only 11 crack instances across 10 images; a single missed detection alters crack recall by **9.09%**, producing high variance during validation.

---

## 3. Normalized Bounding Box Area Distributions by Class

Normalized box area is calculated as $\text{Area} = \frac{W_{\text{box}} \times H_{\text{box}}}{W_{\text{img}} \times H_{\text{img}}}$.

| Class | Train Min Area | Train 25th % | **Train Median Area** | Train 75th % | Train Max Area | Median at 640x640 (px) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`crack`** | **0.000175** | **0.00288** | **0.00690** | **0.01955** | 0.4497 | **~53 x 53 px** |
| **`scratch`** | 0.001862 | 0.01931 | **0.04324** | 0.09845 | 0.7597 | ~133 x 133 px |
| **`dent`** | 0.000202 | 0.02105 | **0.05523** | 0.12480 | 0.7892 | ~150 x 150 px |
| **`lamp broken`** | 0.009664 | 0.04892 | **0.10068** | 0.18450 | 0.5346 | ~203 x 203 px |
| **`tire flat`** | 0.015259 | 0.08210 | **0.17102** | 0.31200 | 0.6844 | ~265 x 265 px |
| **`glass shatter`** | 0.014845 | 0.24500 | **0.43168** | 0.68200 | 1.0000 | ~420 x 420 px |

### Key Observations
1. **Micro-Scale Nature of Cracks:** 25% of all cracks have an area smaller than $0.00288$ (~34x34 pixels at 640x640). Several extreme hairline cracks have areas below $0.0005$ (< 15x15 pixels).
2. **Receptive Field Mismatch:** In YOLOv8n, the deepest detection head (P5, stride 32) downsamples a 640px image to a 20x20 feature grid. A median crack occupies less than 1 grid cell at P5, forcing the model to rely entirely on the shallow P3 head (80x80 grid, stride 8) where semantic context is lowest.

---

## 4. Annotation Granularity & Inconsistency Inspection

### 4.1 Continuous Scratches Fragmented into Arbitrary Multiple Boxes
In multiple vehicle photos, continuous key scratches, scrape marks along door panels, and bumper rub marks are labeled inconsistently:
- **Image `000112.jpg`:** A single scrape along the lower rocker panel is partitioned into **4 fragmented bounding boxes** (`[0.216, 0.943]`, `[0.099, 0.674]`, `[0.198, 0.762]`, `[0.423, 0.881]`).
- **Image `000512.jpg`:** A continuous diagonal scrape mark is labeled as **5 vertical slice boxes** (`xc` positions: `0.121`, `0.144`, `0.324`, `0.394`, `0.399`).
- **Image `000792.jpg`:** A continuous rear bumper scrape is split into **5 adjacent boxes**.

**Effect on Training:**
- The network is penalized when it outputs a single coherent bounding box covering the entire scrape (IoU with any single fragment is $< 0.45$, counting as a False Positive and False Negative).
- Conversely, when the model attempts to predict multiple small boxes, non-maximum suppression (NMS) frequently merges them or drops adjacent fragments.

### 4.2 Unusually Small and Clustered Bounding Boxes
- **Image `000265.jpg`:** Contains 4 tiny dent boxes crammed against the left image boundary:
  - Box 1: area `0.000202` (width 0.017, height 0.012)
  - Box 2: area `0.000494` (width 0.023, height 0.021)
  - Box 3: area `0.000543` (width 0.026, height 0.021)
  - Box 4: area `0.000554` (width 0.023, height 0.024)
- **Image `000008.jpg`:** Features a crack box of area `0.000442` (width 0.0156, height 0.0283).
- **Image `000904.jpg`:** Features a crack box of width `0.0098` (approx. 6 pixels wide).

Boxes smaller than 16x16 pixels in 640px images lack sufficient internal texture for standard convolutional backbones to distinguish vehicle damage from sensor noise or jpeg compression artifacts.

### 4.3 Missing Crack Annotations
In an audit of images exhibiting structural impact, **100 out of 210 training images** (47.6%) contain dented bumpers or shattered lamps where bumper splits, plastic fractures, and seam tear-outs are visually evident but completely omitted from the annotation files:
- **`000134.jpg`:** Bumper detachment with visible plastic tearing labeled only as `dent` and `lamp broken`.
- **`000292.jpg`:** Front corner collision showing fractured bumper fascia labeled only as `dent` and `glass shatter`.
- **`000298.jpg`:** Front headlight housing fractured into fender with evident seam crack labeled only as `dent` and `lamp broken`.

**Effect on Model:**
When the model correctly detects a crack in these collision regions, the unannotated ground truth causes the evaluation evaluator to penalize the correct prediction as a **False Positive**, suppressing model confidence for cracks.

---

## 5. Visual Representation & Domain Coverage Audit

| Domain Dimension | Current CarDD Representation | Identified Coverage Gap | Impact on ClaimSense AI |
| :--- | :--- | :--- | :--- |
| **Lighting Conditions** | Predominantly bright daylight / flat workshop lights | Severe lack of direct sunlight, sunset low-angle glare, night/streetlamp lighting, and rainy overcast conditions | High false positives on sunlight glare lines; failure to identify scratches in shadows |
| **Vehicle Paint Finishes** | Mostly solid gloss paints (white, red, black) | Minimal metallic flake, pearlescent, satin/matte wraps, or two-tone paint finishes | Specular reflections on metallic paint misclassified as scratches (+10 FP in Session 3) |
| **Panel Curvature** | Flat side door panels and rear hatches dominate | Under-representation of wheel arch lips, body character crease lines, A/B/C pillars, and contoured plastic fascias | Dents along body crease lines are frequently missed or confused with natural styling curves |
| **Damage Geometry** | Standard frontal impacts and straight scrapes | Minimal hail damage (multi-point micro-dents), gravel rash/stone chipping, underbody scrape, or complex multi-axial crumples | Low recall on shallow hail dents and dispersed road rash |

---

## 6. Proposed Corrections for Human Review

*(Strict Safeguard: No annotations have been modified. These proposals are cataloged solely for human review and offline validation.)*

| Target Image | Split | Proposed Correction Type | Description & Proposed Coordinates | Rationale |
| :--- | :---: | :--- | :--- | :--- |
| **`000112.jpg`** | Train | Consolidation | Merge 4 fragmented scratch boxes (lines 2-5) into 1 contiguous bounding box: `1 0.2240 0.8120 0.4400 0.3200` | Eliminates fragmentation; unifies scrape mark into single coherent instance |
| **`000512.jpg`** | Train | Consolidation | Merge 5 fragmented scratch boxes (lines 1-5) into 1 contiguous box: `1 0.2600 0.4600 0.3800 0.7200` | Prevents NMS penalty on unified diagonal scratch |
| **`000265.jpg`** | Train | Consolidation / Filter | Merge 4 tiny dent boxes into 1 cluster box: `0 0.0220 0.5950 0.0450 0.1600` | Eliminates sub-15px noise boxes that disrupt anchor regression |
| **`000134.jpg`** | Train | Addition (Review) | Add missing crack box at bumper fracture seam: `2 0.3820 0.6150 0.0650 0.1200` | Captures unannotated plastic tear accompanying lamp impact |
| **`000298.jpg`** | Train | Addition (Review) | Add missing crack box at fender-lamp seam: `2 0.4410 0.5280 0.0820 0.0950` | Prevents correct bumper split detection from being penalized as FP |

---

## 7. Audit Conclusion & Readiness Verdict

The CarDD dataset in its current state is **NOT READY** for further brute-force training sessions. 
- The regression observed in Session 3 (1024px) was not a failure of image resolution, but the direct consequence of extreme class imbalance (91 cracks vs 371 scratches) and annotation fragmentation/omission.
- Running additional training epochs on this raw dataset will continue to overfit macro-damages while stagnating on fine surface damage.
- The project must proceed with **annotation correction and targeted data expansion** prior to any future training experiment.
