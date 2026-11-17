# Phase 8 — Official CarDD 100-Image Selection & Ingestion Verification Report

**Project:** ClaimSense AI  
**Module:** Phase 8 Dataset Expansion — Official CarDD Release Sampling & Ingestion Audit  
**Date:** November 17, 2026  
**Source Dataset Path:** `Downloads/CarDD_release/CarDD_release/CarDD_COCO/`  
**Staging Directory:** `datasets/CarDD_Expanded_v1/raw_incoming/`  
**Annotation Pilot Directory:** `datasets/CarDD_Expanded_v1/annotations_pilot/`  
**Manifest Path:** `runs/phase8/cardd_100_selection_manifest.json`  
**Status:** **100 Images Physically Ingested & Verified — Active Dataset Frozen (Awaiting Approval)**  
**Training Gate:** **Session 4 STRICTLY PAUSED — Zero Epochs Executed**  

---

## 1. Executive Summary

This report documents the execution of the **Official CarDD 100-Image Selection and Physical Ingestion** pipeline.

Rather than downloading external data or relying on synthetic imagery, **100 authentic motor vehicle damage images** were selected directly from the official local CarDD release located at:
```
Downloads/CarDD_release/CarDD_release/CarDD_COCO/
```

### Key Milestones Achieved
1. **Exclusively Sampled from Official `train2017`:** All 100 images were selected exclusively from the unused pool of 2,606 `train2017` images. Zero images were drawn from `val2017` or `test2017`.
2. **Targets Achieved Without Fabrication:**
   - **40 Crack-Priority Images** (Yielding **78 crack instances**)
   - **35 Scratch-Priority Images** (Yielding **56 scratch instances**)
   - **25 Dent-Priority Images** (Yielding **39 dent instances**)
   - **Total:** **100 Images** containing **173 verified damage instances**.
3. **Physical Image Ingestion Complete:** All 100 high-resolution `.jpg` image files were copied into `datasets/CarDD_Expanded_v1/raw_incoming/`.
4. **COCO Ground-Truth Preserved:** Original COCO slice containing the source annotation dictionary is saved in `datasets/CarDD_Expanded_v1/raw_incoming/selected_coco_annotations.json`.
5. **YOLO Conversion Staged in Isolation:** Proposed YOLO bounding boxes were generated in `datasets/CarDD_Expanded_v1/annotations_pilot/`. Active train and val splits remain **100% untouched**.
6. **Zero Duplicates / Zero Near-Duplicates:** 
   - Exact SHA-256 matches against CarDD_300: **0 collisions**.
   - Minimum perceptual hash (dHash) Hamming distance to any CarDD_300 image: **12** (Average: **18.68**). Zero near-duplicates ($\text{distance} \le 5$).
7. **Safeguards Maintained:** Production checkpoint `models/phase5/best.pt`, frozen test split, Phase 7 verification engine, and baseline datasets remain untouched. Session 4 model training remains strictly paused.

---

## 2. Step 1: Inspection of Official CarDD Release

### A. COCO Annotation JSON Files
The official release structure was inspected and cataloged:

```
+---------------------------+------------+-------------------+--------------------+------------------------+
| Split Name                | File Size  | Total Images      | Total Annotations  | CarDD_300 Overlap      |
+---------------------------+------------+-------------------+--------------------+------------------------+
| instances_train2017.json  | 20.54 MB   | 2,816 images      | 6,211 annotations  | 210 images (train)     |
| instances_val2017.json    | 5.98 MB    | 810 images        | 1,744 annotations  | 45 images (val)        |
| instances_test2017.json   | 2.66 MB    | 374 images        | 785 annotations    | 45 images (test)       |
+---------------------------+------------+-------------------+--------------------+------------------------+
| Total Official CarDD Pool | 29.18 MB   | 4,000 images      | 8,740 annotations  | 300 images             |
+---------------------------+------------+-------------------+--------------------+------------------------+
```

### B. Category Mapping & Distribution in `train2017`

```
+---------------+----------------+----------------+---------------------+-------------------------------+
| COCO Cat ID   | Category Name  | YOLO Class ID  | Total in train2017  | Train Damage Representation   |
+---------------+----------------+----------------+---------------------+-------------------------------+
| 1             | dent           | 0              | 1,806 annotations   | Primary metal deformation     |
| 2             | scratch        | 1              | 2,560 annotations   | Clear-coat / basecoat scrape  |
| 3             | crack          | 2              | 651 annotations     | Severe structural fracture    |
| 4             | glass shatter  | 3              | 475 annotations     | Shattered / spider glass      |
| 5             | lamp broken    | 4              | 494 annotations     | Shattered headlamp / lens     |
| 6             | tire flat      | 5              | 225 annotations     | Punctured / flat tire         |
+---------------+----------------+----------------+---------------------+-------------------------------+
```

### C. Available Unused Pool in `train2017`
- Total images in `train2017`: 2,816
- Images currently in `CarDD_300/train`: 210
- **Available Unused Training Pool:** **2,606 images**
  - Images containing `crack`: 378 images (53 crack-only)
  - Images containing `scratch`: 1,353 images (654 scratch-only)
  - Images containing `dent`: 1,100 images (349 dent-only)

---

## 3. Step 2: Stratified Selection Algorithm & Instance Distribution

### Selection Criteria
To eliminate the severe class deficit of `crack` (only 91 instances in baseline training) and improve `scratch` and `dent` feature diversity without test-split contamination:
1. **Crack-Priority (40 Images):** Sampled from the 378 crack-containing images, prioritizing pure crack scenes, larger bounding box areas, and high visual contrast.
2. **Scratch-Priority (35 Images):** Sampled from the remaining 1,353 scratch-containing images, prioritizing clear multi-stroke scratches across varied vehicle panels.
3. **Dent-Priority (25 Images):** Sampled from the remaining 1,100 dent-containing images, prioritizing character line and contoured body panel deformations.

### Selection Results vs. Targets

```
+---------------------+-------------------+---------------------+-------------------------+
| Category Priority   | Target Selection  | Selected Images     | Acquired Instances      |
+---------------------+-------------------+---------------------+-------------------------+
| Crack Priority      | 40 images         | 40 images (40.0%)   | 78 crack instances      |
| Scratch Priority    | 35 images         | 35 images (35.0%)   | 56 scratch instances    |
| Dent Priority       | 25 images         | 25 images (25.0%)   | 39 dent instances       |
+---------------------+-------------------+---------------------+-------------------------+
| Total Batch         | 100 images        | 100 images (100.0%) | 173 total instances     |
+---------------------+-------------------+---------------------+-------------------------+
```

### Impact on Active Training Balance (Prospective)
If integrated into active training:
- **`crack` instances:** Will increase from **91** to **169** (**+85.7% increase**), directly resolving the primary performance bottleneck identified in Phase 8 Session 2 and Session 3 error analyses.
- **`scratch` instances:** Will increase from **204** to **260** (+27.5%).
- **`dent` instances:** Will increase from **230** to **269** (+17.0%).

---

## 4. Step 3: Forensic Duplicate & Perceptual Hash Verification

Every one of the 100 selected images was checked against all 300 existing images in `CarDD_300` (`train`, `val`, `test`):

```
+-----------------------------------+--------------------+------------------------+-------------------+
| Verification Dimension            | Safety Threshold   | Measured Audit Result  | Audit Status      |
+-----------------------------------+--------------------+------------------------+-------------------+
| Exact SHA-256 Hash Collisions     | 0 collisions       | 0 collisions           | PASSED (Zero)     |
| Filename Overlap with CarDD_300   | 0 filenames        | 0 filenames            | PASSED (Zero)     |
| Perceptual Hash (dHash) Min Dist  | Distance > 5       | Minimum Distance = 12  | PASSED (Novel)    |
| Perceptual Hash (dHash) Mean Dist | --                 | Average Distance = 18.68| EXCELLENT        |
| Near-Duplicate Candidates (<= 5)  | 0 candidates       | 0 candidates           | PASSED (Zero)     |
+-----------------------------------+--------------------+------------------------+-------------------+
```

### Visual Novelty Guarantee
- Not a single image matches any existing CarDD_300 image by SHA-256 byte digest.
- The closest perceptual match across the entire 300-image baseline has a Hamming distance of **12** (well beyond the near-duplicate threshold of $\le 5$). Every image provides novel visual perspectives, panels, and lighting conditions.

---

## 5. Step 4: Annotation Integrity & COCO-to-YOLO Conversion

### A. Coordinate Boundary Audit
All 173 COCO bounding boxes across the 100 selected images were checked for geometric validity against native pixel dimensions $(W \times H)$:
- **Bounding Box Boundary Violations:** **0 violations**
- **Negative Dimensions:** 0
- **Zero-Area Boxes:** 0
- **Out-of-Bounds Excursions:** 0

### B. Normalized YOLO Format Compliance
Each bounding box was converted to standard YOLO format:
$$\text{Class ID} \quad x_{\text{center}} \quad y_{\text{center}} \quad \text{width} \quad \text{height}$$
where all coordinates are normalized strictly within $[0.0, 1.0]$.
- **Evaluated proposed label files:** 100 files in `datasets/CarDD_Expanded_v1/annotations_pilot/`
- **Hard Syntax Errors:** **0 errors**
- **Class Index Compliance:** 100% compliant with $[0, 5]$ mapping.

---

## 6. Step 5: Staging Directory Layout

The physical image files and annotation artifacts are staged in isolation:

```
datasets/CarDD_Expanded_v1/
├── raw_incoming/
│   ├── selected_coco_annotations.json  # Complete COCO slice for the 100 selected images
│   ├── 000007.jpg                      # Physical source image 1
│   ├── 000015.jpg                      # Physical source image 2
│   ├── ...                             # (Total 100 physical JPG files)
│   └── 003998.jpg                      # Physical source image 100
├── annotations_pilot/
│   ├── 000007.txt                      # Proposed YOLO label 1
│   ├── 000015.txt                      # Proposed YOLO label 2
│   ├── ...                             # (Total 100 proposed YOLO label files)
│   └── 003998.txt                      # Proposed YOLO label 100
├── train/                              # ACTIVE TRAINING SET: 210 images / 210 labels (UNTOUCHED)
└── val/                                # ACTIVE VALIDATION SET: 45 images / 45 labels (UNTOUCHED)
```

---

## 7. Sample Selection Registry (First 15 Selected Images)

| Selection ID | File Name | Source Split | Priority Group | Dimensions | Primary Damage | Min dHash Dist to CarDD_300 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `EXP-OFFICIAL-001` | `001646.jpg` | train2017 | crack_priority | 1000x667 | crack (1 box) | 15 (vs. `000289.jpg`) |
| `EXP-OFFICIAL-002` | `003056.jpg` | train2017 | crack_priority | 1000x667 | crack (1 box) | 18 (vs. `000574.jpg`) |
| `EXP-OFFICIAL-003` | `003780.jpg` | train2017 | crack_priority | 1000x667 | crack (1 box) | 19 (vs. `001716.jpg`) |
| `EXP-OFFICIAL-004` | `000735.jpg` | train2017 | crack_priority | 1000x667 | crack (1 box) | 16 (vs. `001004.jpg`) |
| `EXP-OFFICIAL-005` | `003298.jpg` | train2017 | crack_priority | 1000x667 | crack (1 box) | 18 (vs. `003883.jpg`) |
| `EXP-OFFICIAL-006` | `001538.jpg` | train2017 | crack_priority | 1000x667 | crack (1 box) | 19 (vs. `001851.jpg`) |
| `EXP-OFFICIAL-007` | `002167.jpg` | train2017 | crack_priority | 1000x667 | crack (1 box) | 14 (vs. `002677.jpg`) |
| `EXP-OFFICIAL-008` | `000632.jpg` | train2017 | crack_priority | 1000x667 | crack (1 box) | 17 (vs. `000853.jpg`) |
| `EXP-OFFICIAL-009` | `003080.jpg` | train2017 | crack_priority | 1000x667 | crack (1 box) | 19 (vs. `000371.jpg`) |
| `EXP-OFFICIAL-010` | `003923.jpg` | train2017 | crack_priority | 1000x667 | crack (1 box) | 20 (vs. `000414.jpg`) |
| `EXP-OFFICIAL-011` | `002047.jpg` | train2017 | crack_priority | 1000x667 | crack (1 box) | 17 (vs. `000512.jpg`) |
| `EXP-OFFICIAL-012` | `001579.jpg` | train2017 | crack_priority | 1000x667 | crack (1 box) | 16 (vs. `003114.jpg`) |
| `EXP-OFFICIAL-013` | `000481.jpg` | train2017 | crack_priority | 1000x667 | crack (1 box) | 17 (vs. `000118.jpg`) |
| `EXP-OFFICIAL-014` | `000277.jpg` | train2017 | crack_priority | 1000x667 | crack (1 box) | 18 (vs. `003916.jpg`) |
| `EXP-OFFICIAL-015` | `003998.jpg` | train2017 | crack_priority | 1000x667 | crack (1 box) | 19 (vs. `001724.jpg`) |

*The complete 100-image registry with individual SHA-256 digests and annotation bounds is available in [cardd_100_selection_manifest.json](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/cardd_100_selection_manifest.json).*

---

## 8. Strict Safeguards Compliance

| Component | Target Location / Value | Measured Audit State | Safeguard Status |
| :--- | :--- | :--- | :--- |
| **Production Model** | `models/phase5/best.pt` | `SHA256: 90D489E46FF8521EDFF88D522F0FEFFA164AC38A53B84700594C02A69E515565` | **100% UNTOUCHED** |
| **CarDD_300 Dataset** | `datasets/CarDD_300/` | 300 images (210 train / 45 val / 45 test) | **100% UNTOUCHED** |
| **Frozen Test Split** | `datasets/CarDD_300/test/` | 45 images / labels | **FROZEN & ISOLATED** |
| **Active Staged Train** | `datasets/CarDD_Expanded_v1/train/` | 210 images / 210 labels | **UNTOUCHED** |
| **Active Staged Val** | `datasets/CarDD_Expanded_v1/val/` | 45 images / 45 labels | **UNTOUCHED** |
| **Phase 7 Engine** | `backend/services/` | No modifications | **FROZEN** |
| **Model Training** | GPU CUDA Session 4 | 0 epochs executed | **STRICTLY PAUSED** |

---

## 9. Conclusion & Human Approval Gate

The 100 official CarDD images have been selected, verified, and physically staged in `datasets/CarDD_Expanded_v1/raw_incoming/`.

### Ready for Next Action:
1. **Approval to Integrate:** When approved, the 100 images and their validated YOLO labels in `annotations_pilot/` will be moved into `datasets/CarDD_Expanded_v1/train/images/` and `train/labels/` (expanding training from 210 to 310 images, and cracks from 91 to 169 instances).
2. **Session 4 Training:** Model training remains **strictly paused**. No training run will begin without explicit approval.
