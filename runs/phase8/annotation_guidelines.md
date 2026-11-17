# ClaimSense AI — Vehicle Damage Annotation Guidelines (Phase 8 Standard)

**Project:** ClaimSense AI  
**Document:** Standard Operating Procedure (SOP) for Vehicle Damage Annotation  
**Target Architecture:** YOLOv8n (Multi-Class Damage Localization)  
**Applicability:** Human annotators, QA auditors, and pre-ingestion linting tools  
**Date:** November 17, 2026  
**Status:** Approved Standard Operating Procedure  

---

## 1. Purpose & Core Principles

The accuracy of deep learning object detectors is bounded by the consistency of training annotations. During the Phase 8 audit, inconsistent box granularity (slicing single scratches into arbitrary fragments), omission of collision-associated cracks, and confusion between specular glare and surface scratches were identified as the primary causes of small-damage detection failure.

This guideline establishes strict, unambiguous standards for labeling vehicle damage on real insurance claim photographs.

### Golden Rules
1. **Physical Continuity Rule:** A continuous damage path across a single panel is **one instance**.
2. **Receptive Field Safety Rule:** Every bounding box must maintain a **minimum dimension of 16x16 pixels**; sub-pixel features must be symmetrically padded into adjacent background texture.
3. **Panel Boundary Separation Rule:** Damage spanning multiple panels must be partitioned at the panel shutline.
4. **Authenticity Guarantee:** Only authentic, real-world vehicle damage photographs are annotated. No synthetic or generated images.

---

## 2. Guideline A — Continuous Scratches (`scratch`, Class 1)

```
INCORRECT (Fragmented Slices):
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ Frag 1 │ │ Frag 2 │ │ Frag 3 │ │ Frag 4 │  <-- Penalizes model with IoU < 0.45
└────────┘ └────────┘ └────────┘ └────────┘

CORRECT (Unified Single Bounding Box):
┌─────────────────────────────────────────┐
│       Single Unified Bounding Box       │  <-- Matches model detection cleanly
└─────────────────────────────────────────┘
```

### 2.1 Single Panel Scrapes
- **Rule:** A continuous scratch, key mark, or abrasive rub mark extending across a single body panel (e.g. front door, rear bumper, hood) must be enclosed in **a single, tightly bounded rectangular box**.
- **Prohibited:** Dividing a continuous line into multiple segments (e.g., 3 to 6 adjacent boxes) is strictly forbidden.

### 2.2 Multi-Panel Damage Transitions
- **Rule:** If a scratch extends continuously across two adjacent body panels (e.g., front door to rear door, or fender to front door):
  - The scratch must be split into **two discrete bounding boxes**, cleanly divided at the panel shutline/gap.
  - **Reason:** In automotive damage claims and repair estimating, panels are repaired, repainted, or replaced independently. Binding two separate panels in one box distorts localized panel part attribution.

### 2.3 Swirl Marks vs. Scratch Instances
- **Swirl Marks / Micro-Abrasions:** Diffuse circular buffer swirls covering an entire panel are paint finish wear, not insurable collision/vandalism scratches. **Do NOT annotate.**
- **Stone Chipping / Gravel Rash:** Multiple tiny paint chips on the front bumper lower lip should only be annotated if individual chips exceed 16x16 px; otherwise, if concentrated, label the region under `scratch` with a single regional bounding box.

---

## 3. Guideline B — Hairline Cracks (`crack`, Class 2)

```
HAIRLINE CRACK PADDING RULE (Minimum 16x16 px):
┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐
   | (Crack Line)
   |  <-- 3 px actual width
   |
└ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘
<─── 16 px Box ────> (Symmetric 6.5 px background padding on each side)
```

### 3.1 Definition & Target Materials
- `crack` covers structural fractures, splits, and tears in:
  1. **Plastic & Composites:** Bumper covers, front grilles, air dams, wheel arch liners, side mirror housings.
  2. **Sheet Metal:** Stamped metal seam tears, door jamb splits, A/B/C pillar fracture lines.
  3. **Fiberglass:** Spider-web cracking and stress tears in aftermarket or specialty body panels.

### 3.2 Minimum Dimensions & Symmetrical Padding
- **Issue:** Fine hairline cracks often have a physical width of 2 to 5 pixels on camera. A 3-pixel wide box completely collapses in the YOLO P3 head (stride 8).
- **Rule:** The bounding box must have a **minimum width and height of 16 pixels** in native image resolution.
- **Padding:** Expand the box boundary symmetrically into the adjacent undamaged paint/plastic texture. The center of the box must remain aligned with the centroid of the fracture line.

### 3.3 Collision Perimeter Inspection
- **Mandatory Check:** Whenever an image exhibits severe impact damage (`dent`, `lamp broken`, `glass shatter`), the annotator must carefully inspect:
  - Bumper cover mounting ears and fender seams.
  - The perimeter surrounding crushed headlamp or tail lamp bezels.
  - Sharp crease apexes in crushed body panels.
- If a split is visible, annotate it as `crack`. Never omit a crack because a larger `dent` encompasses it.

### 3.4 Distinguishing Cracks from Panel Gaps
- **Panel Shutlines / Gaps:** The manufactured gap between hood and fender, or door and body, is **NOT a crack**.
- **Verification:** Look for manufactured rubber weatherstripping, uniform width, and factory paint beveling. Cracks exhibit jagged edges, non-uniform opening widths, and exposed substrate (black/gray raw plastic or unpainted metal).

---

## 4. Guideline C — Low-Contrast & Crease Dents (`dent`, Class 0)

### 4.1 Shallow Dents Without Paint Loss
- **Identification:** Soft depressions (door dings, shopping cart impacts) often have intact paint and no contrast change. They are identified by **distorted reflection lines** (bent reflection of overhead light poles, distorted horizon lines, or curved reflection waves).
- **Bounding Box Rule:** The box must enclose the entire distorted reflection zone, from the point where the reflection first curves out of line to where it returns to the true body contour.

### 4.2 Body Character Crease Dents
- **Definition:** Dents that crush across stamped styling crease lines (e.g., upper door waistline, fender flared ridges).
- **Rule:** The box must encompass the full vertical and horizontal extent of the depression, including the flattened portion of the crease line.

### 4.3 Hail Damage Protocol
- **Individual Hail Dents:** When hail dents are discrete and separated by $\ge 20\text{ px}$ of undamaged metal, annotate each indentation with an individual box.
- **Catastrophic Hail Fields:** On vehicle hoods or roofs with 30+ overlapping hail dents per panel, annotate the affected panel zone as a single bounding box with the metadata tag `cluster: true` to prevent ground truth box saturation.

### 4.4 Avoiding Factory Styling Lines
- **False-Positive Trap:** Aggressive aerodynamic scoops, hood power bulges, and scalloped door contours are factory styling, not dents.
- **Check:** Compare symmetry with the opposite vehicle side whenever visible. Factory styling is smooth, symmetric, and terminates at design shutlines.

---

## 5. Guideline D — Overlapping Damage Categories & Co-Occurrence

In real accidents, damage categories frequently co-occur in the same spatial region. The following matrix governs permissible overlap:

| Spatial Co-Occurrence | Allowed? | Bounding Box Rule | Real-World Scenario |
| :--- | :---: | :--- | :--- |
| **`crack` inside `dent`** | **YES** | Draw parent `dent` box around overall panel depression; draw tighter `crack` box around the material split within the depression. | Plastic bumper cover caved in with fracture split at center of impact. |
| **`scratch` inside `dent`** | **YES** | Draw `dent` box around depression; draw `scratch` box around the paint abrasion streak. | Vehicle side-swiped: door panel dented inward while obstacle gouges clear-coat. |
| **`lamp broken` + `crack`** | **YES** | Draw `lamp broken` around shattered lens; draw `crack` on the cracked plastic mounting tab or bumper surround. | Headlamp crushed backward, fracturing bumper mounting flange. |
| **`glass shatter` + `scratch`** | **NO** | Label strictly as `glass shatter`. Glass fractures with surface scratches are part of window failure. | Windshield impacted by debris. |

---

## 6. Guideline E — Specular Glare, Reflections & False-Positive Traps

To eliminate false-positive spikes during high-resolution evaluation, annotators and QA reviewers must recognize visual distractors:

### 6.1 Direct Sunlight Reflection Lines
- **Visual Appearance:** Bright, sharp, high-contrast white streaks running along the curvature of hood edges and wheel arches.
- **Distinction from Scratches:**
  - Glare lines fade smoothly into panel highlight halos; scratches have sharp, abrupt boundaries.
  - Glare lines follow the exact vehicle curvature vector; scratches cut across panel contours at random impact angles.
  - Glare lines do not display white primer or black plastic substrate depth.
- **Rule:** **NEVER annotate specular sunlight highlights as scratches.**

### 6.2 Workshop Overhead Fluorescent Lights
- **Visual Appearance:** Straight, parallel white bars reflected in polished, waxed vehicle paint.
- **Rule:** Verify whether the white line reflects overhead light tube geometry. **NEVER annotate.**

### 6.3 Dirt Trails & Water Droplet Streaks
- **Visual Appearance:** Semi-translucent, brown/gray vertical trails from rain run-off or road dust.
- **Rule:** Look for translucency and organic flow patterns. If the paint underneath is intact, **DO NOT annotate**.

---

## 7. Scale Constraints & Quality Lint Thresholds

All annotations must pass the automated pre-ingestion linter (`scripts/lint_annotations.py`):

| Parameter | Minimum Allowed | Maximum Allowed | Action on Violation |
| :--- | :---: | :---: | :--- |
| **Normalized Coordinates ($x_c, y_c, w, h$)** | $0.0000$ | $1.0000$ | Hard Reject: Box outside image boundary |
| **Box Width / Height (Native Pixels)** | $16\text{ px}$ | $W_{\text{img}}, H_{\text{img}}$ | Hard Reject: Expand box symmetrically to 16px |
| **Normalized BBox Area ($w \times h$)** | $0.0008$ | $0.9500$ | Flag for Manual Review if $< 0.0008$ |
| **Same-Class IoU Overlap** | $0.00$ | $0.35$ | Hard Reject: Merge overlapping boxes |
| **Aspect Ratio ($\max(w/h, h/w)$)** | $1:1$ | $20:1$ | Flag for Review if $> 20:1$ (except single-line scratches) |
