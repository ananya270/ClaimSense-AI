# Phase 8 – Post-Benchmark Error Analysis and Staging Review

**Status:** Completed  
**Candidate Checkpoint in Staging:** `runs/phase8/session_2/weights/best.pt`  
**Production Model:** `models/phase5/best.pt` (100% UNTOUCHED, SHA256: `90d489e46ff8521e...`)  
**Phase 7 Status:** Frozen & Unmodified  

---

## 1. Executive Summary & Review Scope

Following the completion of the Phase 8 benchmark on the untouched 45-image CarDD test split, a forensic error analysis was conducted focusing on the three most difficult vehicle damage classes:
1. **`dent`** (Test: 49 instances | mAP@50: 26.20% | Recall: 18.37% | Precision: 53.50%)
2. **`scratch`** (Test: 53 instances | mAP@50: 15.36% | Recall: 9.43% | Precision: 37.89%)
3. **`crack`** (Test: 13 instances | mAP@50: 1.99% | Recall: 0.00% @ standard IoU | Precision: 0.00% @ standard IoU)

All investigations were performed without modifying any checkpoints, without training additional epochs, and without using the test split for hyperparameter tuning.

---

## 2. False Negative & False Positive Forensic Analysis

### A. Class: `dent`
- **Error Counts (conf=0.25, IoU=0.3):** 18 True Positives, 31 False Negatives, 10 False Positives.
- **Bounding Box Geometry:** Mean normalized area = `0.0988`, Median = `0.0538` (~5–10% of vehicle image).
- **Failure Patterns Identified:**
  1. **Subtle Reflection Gradients (Low Contrast):** In images such as `000152.jpg`, `001236.jpg`, and `001493.jpg`, dents consist of smooth metallic surface curvature changes without paint chipping or harsh cast shadows. The model localizes these dents, but outputs confidence scores between `0.07` and `0.18`, causing them to be suppressed by standard `conf=0.25` thresholds.
  2. **Compound Panel Dents:** Large body panel creases spanning across multiple panels (e.g., door + quarter panel) are frequently predicted as two separate smaller boxes, while annotators grouped them into a single macro box, or vice versa.
- **False Positive Drivers:** Deep shadows near wheel wells or specular glare highlights on convex bumpers are occasionally misclassified as shallow dents (e.g., `000687.jpg` conf=0.41, `002661.jpg` conf=0.41).

### B. Class: `scratch`
- **Error Counts (conf=0.25, IoU=0.3):** 12 True Positives, 41 False Negatives, 20 False Positives.
- **Bounding Box Geometry:** Mean normalized area = `0.0849`, Median = `0.0565`.
- **Failure Patterns Identified:**
  1. **Annotation Granularity Fragmentation:** In images like `000042.jpg`, human annotators drew up to 6 separate fragmented boxes covering short segments of a single continuous key scratch. The model typically predicts 1 or 2 cohesive bounding boxes enclosing the entire scratch line. While semantically accurate, this causes IoU with individual micro-boxes to drop below 0.3, registering simultaneously as an FN (missed micro-box) and FP (unmatched macro-box).
  2. **Specular / Glass Surface Confusion:** Scratches on clear-coat over dark paint or near window glass borders are sometimes misclassified as `glass shatter` (e.g., `000042.jpg` pred conf=0.38).
  3. **Hairline Superficial Scratches:** Very faint surface scuffs lack high-frequency edges and are lost during downsampling to 640x640.

### C. Class: `crack`
- **Error Counts (conf=0.25, IoU=0.3):** 0 True Positives @ standard IoU, 13 False Negatives, 3 False Positives.
- **Bounding Box Geometry:** Mean normalized area = `0.0156`, Median = `0.0053` (**10x to 20x smaller** than dents or scratches).
- **Failure Patterns Identified:**
  1. **Resolution Downsampling Loss:** Hairline bumper or panel cracks are often only 1 to 3 pixels wide on a 1000x667 image. Resizing to 640x640 with letterboxing blends these fine structural edges into neighboring panel textures.
  2. **Missing Ground Truth Annotations:** In `000042.jpg`, the model predicted a genuine bumper fracture with high confidence (`conf=0.573`), but the ground truth annotator had only labeled a crack on the opposite side of the vehicle, penalizing the model with an unwarranted false positive.
  3. **Structural Panel Gap Ambiguity:** The visual signature of a deep crack closely resembles normal panel alignment gaps or shadow seams between bumper fascia and fenders.

---

## 3. Dataset Distribution & Imbalance Audit

| Split | dent | scratch | crack | glass shatter | lamp broken | tire flat | Total Boxes | Images |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Train** | 234 (32.8%) | 258 (36.1%) | 91 (12.7%) | 45 (6.3%) | 64 (9.0%) | 22 (3.1%) | 714 | 210 |
| **Val** | 44 (31.4%) | 60 (42.9%) | 11 (7.9%) | 10 (7.1%) | 10 (7.1%) | 5 (3.6%) | 140 | 45 |
| **Test** | 49 (33.1%) | 53 (35.8%) | 13 (8.8%) | 12 (8.1%) | 15 (10.1%) | 6 (4.1%) | 148 | 45 |
| **Total** | **327** | **371** | **115** | **67** | **89** | **33** | **1,002** | **300** |

### Root Cause Synthesis: Why Did Some Classes Excel While Others Struggled?
- **Anchored Classes (`glass shatter`, `tire flat`, `lamp broken`):**
  - These damage types are bound to distinct, fixed anatomical components (wheels, headlight housings, windshield frames).
  - Even with only 22 training instances, `tire flat` achieved **71.71% test mAP@50** because the neural network leverages the prominent visual context of the wheel assembly.
- **Unanchored Classes (`dent`, `scratch`, `crack`):**
  - These damage types can appear anywhere across arbitrary sheet metal, plastic, or composite panels under infinite variations of curvature, lighting, and paint color.
  - They lack fixed contextual anchors and require substantially more diverse training samples and higher pixel resolution to achieve high recall.

---

## 4. Training Configuration & Augmentation Audit

Inspection of `runs/phase8/session_2/args.yaml` reveals the following pipeline constraints:

| Augmentation Parameter | Current Setting | Impact on Small/Fine Damage |
| :--- | :---: | :--- |
| `degrees` (Rotation) | `0.0` | **No rotational invariance.** Slanted scratches or angled panel cracks cannot be generalized from vertical/horizontal samples. |
| `shear` & `perspective` | `0.0` | Vehicle photos taken at oblique angles are not simulated. |
| `erasing` (Random Erasing)| `0.4` | **Detrimental for fine damage.** A random 40% erase patch can completely obliterate a 20-pixel crack or scratch line during training. |
| `close_mosaic` | `10` | In a 15-epoch session, mosaic augmentation was disabled after only 5 epochs. |
| `imgsz` | `640` | Insufficient pixel density for 1–2 pixel wide cracks on 1000x667 source images. |

---

## 5. Concrete Recommendations for Future Iterations

### A. Desirable Dataset Expansion (Target Real Annotations)
To elevate `crack`, `scratch`, and `dent` to production-grade parity with `glass shatter` (79%) and `tire flat` (71%):
1. **`crack`:** **+300 to 500 additional labeled images** focusing on plastic bumper fractures, grille cracks, and sheet metal tears.
2. **`scratch`:** **+200 to 300 additional images** covering multi-panel key scratches, paint scuffs under harsh sunlight, and low-contrast surface abrasions.
3. **`dent`:** **+150 to 200 additional images** focusing on shallow hail damage and door dings with subtle reflection cues.

### B. Training & Pipeline Optimization
1. **Resolution Upgrade:** Train at `imgsz=1024` (easily supported by the RTX 3050 Laptop GPU in FP16 with `batch=2`, peak VRAM ~1.8 GB).
2. **Augmentation Tuning:**
   - Set `degrees=10.0` and `fliplr=0.5` for rotational and orientation diversity.
   - Disable random erasing (`erasing=0.0`) to avoid deleting thin crack annotations.
   - Set `mixup=0.1` and retain mosaic longer (`close_mosaic=3`).
3. **Inference Threshold Calibration:**
   - In production, apply class-specific confidence thresholds: e.g., `conf=0.15` for low-contrast `dent`, and `conf=0.35` for high-confidence `glass shatter`.

---

## 6. Strategic Decision: Is Session 3 Justified Now?

### Verdict: **Dataset & Resolution Improvement Should Happen First.**

- **Why Session 3 on the identical 210-image dataset is NOT recommended now:**
  - Session 2 (cumulative 26 epochs) has already extracted the available learning signal from the 91 training cracks and 234 training dents at 640x640.
  - Running 15 more epochs on identical data at 640x640 risks overfitting or memorizing the small training set without solving the fundamental physical resolution limit on hairline cracks.
- **Staging Status:**
  - Keep `runs/phase8/session_2/weights/best.pt` **staged as the primary candidate model** (it vastly outperforms baseline with 41.17% mAP vs 0.12% and 66% fewer false positives).
  - Do not train further until data augmentation adjustments or higher resolution training (`imgsz=1024`) are planned.
