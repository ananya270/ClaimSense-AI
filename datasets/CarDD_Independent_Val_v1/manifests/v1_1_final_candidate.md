# ClaimSense AI — Independent Validation Dataset Specification
## Final Proposed Candidate Specification (v1.1-DRAFT)

**Document Identifier:** `v1_1_final_candidate.md`  
**Supersedes (Upon User Ratification):** `runs/phase8/independent_validation_plan/acquisition_specification.md` (v1.0 Active)  
**Target Dataset Identifier:** `CarDD_Independent_Val_v1`  
**Dataset Scale:** Minimum 200 authentic vehicle-damage images (Target: 220–250 to absorb attrition)  
**Governing Standard:** Antigravity / ClaimSense AI Dataset Governance Standard  
**Date:** 2026-11-17  
**Status:** **DRAFT CANDIDATE SPECIFICATION — AWAITING FORMAL GATE B RATIFICATION**  

---

## 1. Dataset Purpose & Core Governance Principles

### 1.1 Objective
`CarDD_Independent_Val_v1` is an independent, legally unencumbered, distributionally diverse validation dataset designed to provide gold-standard real-world benchmarking for ClaimSense vehicle damage detection models (Session 2, Session 4, Production).

### 1.2 Strict Isolation & Anti-Contamination Mandate
- **Evaluation Only:** This dataset must **NEVER** be used for gradient training, backpropagation, fine-tuning, learning-rate scheduling, data augmentation optimization, or confidence-threshold calibration.
- **Leakage Prevention:** Candidates are sourced from independent repositories completely disjoint from the CarDD training and validation corpora.

---

## 2. Target Damage Class Representation & Allocation

To overcome the statistical sample shortages of the 45-image CarDD test split, the independent validation dataset establishes the following class representation targets:

| Damage Class | Class ID | Minimum Image Count | Target Instance Count | Priority Level | Target Morphologies & Visual Archetypes |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Dent** | 0 | 70 | 90+ | Medium | Sheet metal depressions, crease dents, hail damage clusters, bumper push-ins. |
| **Scratch** | 1 | 75 | 100+ | **High** | Surface clear-coat scuffs, deep key scratches down to metal/primer, curb scrapes. |
| **Crack** | 2 | 50 | 60+ | **Critical** | Hairline bumper fractures, structural splits in plastic fascias, cracked composites. |
| **Glass Shatter** | 3 | 35 | 40+ | Medium | Windshield star chips, radial cracks, bullseyes, shattered tempered side/rear glass. |
| **Lamp Broken** | 4 | 40 | 45+ | Medium | Cracked headlamp lenses, shattered taillight housings, broken fog lamps, exposed reflectors. |
| **Tire Flat** | 5 | 25 | 30+ | Medium | Deflated sidewall rim-pinch, blown-out tread strips, bead separation on diverse rim types. |

*Multi-Damage Images:* Images featuring co-occurring defects (e.g. side impact with dent + scratch + cracked bumper + shattered glass) are encouraged to test multi-label co-occurrence detection.

---

## 3. The Dual-Tier Resolution Architecture

Candidate images are categorized upon ingestion into one of two mutually exclusive tiers:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 v1.1 DUAL-TIER RESOLUTION ARCHITECTURE                                 │
├──────────────────────────────────┬─────────────────────────────────────────────────────────────────────┤
│ TIER 1: Full-Vehicle Walkaround  │ TIER 2: Macro Component Inspection                                  │
├──────────────────────────────────┼─────────────────────────────────────────────────────────────────────┤
│ • Role: Global vehicle context,  │ • Role: High-resolution localized fracture, scratch depth,          │
│   multi-panel damage, alignment. │   shattered lens texture, component tear-down inspection.           │
│ • Dimensional Floor:             │ • Dimensional Floor:                                                │
│   Width >= 800 px AND            │   min(Width, Height) >= 400 px AND                                  │
│   Height >= 600 px               │   max(Width, Height) >= 600 px                                      │
│ • Orientation: Free (Landscape / │ • Orientation: Orientation-Agnostic                                 │
│   Portrait, both >= 600 and 800) │   (Supports 600x400 landscape & 400x600 portrait crops)             │
│ • Context Rule: Vehicle body     │ • Damage Occupancy Floor: Localized defect AABB must occupy         │
│   must occupy >= 60% of frame.   │   at least 30.0% of the total image area.                           │
│ • Quota Share: Minimum 70.0% of  │ • Quota Share Ceiling: Maximum 30.0% of cumulative final            │
│   cumulative final dataset.      │   dataset instances (hard ceiling).                                 │
└──────────────────────────────────┴─────────────────────────────────────────────────────────────────────┘
```

### 3.1 Tier 1 — Full-Vehicle Walkaround Standard
- **Resolution Floor:** $\text{Width} \ge 800\text{ px}$ AND $\text{Height} \ge 600\text{ px}$ (Total pixels $\ge 480,000$).
- **Visual Stance:** Camera distance 1.5m to 5.0m; captures the full vehicle silhouette, complete body assemblies (front clip, rear quarter, full side profile), or multiple contiguous panels.
- **Dataset Allocation Quota:** $\ge 70.0\%$ of cumulative final validation dataset instances.

### 3.2 Tier 2 — Macro Component Inspection Standard
- **Resolution Floor:** $\min(\text{width}, \text{height}) \ge 400\text{ px}$ AND $\max(\text{width}, \text{height}) \ge 600\text{ px}$ (Total pixels $\ge 240,000$).
- **Orientation Agnosticism:** Orientation-agnostic, explicitly admitting portrait crops (e.g. $720 \times 960$, $400 \times 600$) for vertical component defects such as door seams, pillars, and roof rails.
- **Damage Area Occupancy Floor:** Localized vehicle damage must occupy **at least 30.0% of total image area** ($W \times H$).
- **Dataset Allocation Ceiling:** Strictly capped at **$\le 30.0\%$ of cumulative final validation dataset instances**.

---

## 4. Verified AABB Damage Occupancy Requirements

### 4.1 Mathematical Occupancy Formulation
Damage occupancy for candidate image $I$ with dimensions $W \times H$ is defined strictly as:

$$\text{Occupancy}(I) = \frac{\sum_{k=1}^{K} \text{Area}(\text{AABB}_k)}{W \times H} = \frac{\sum_{k=1}^{K} (x_{2,k} - x_{1,k}) \times (y_{2,k} - y_{1,k})}{W \times H} \ge 0.3000 \quad (30.0\%)$$

Where:
- $K$ is the number of validated defect instances on the target component.
- Overlapping bounding box areas are unioned to prevent double-counting.
- Bounding box coordinates $[x_1, y_1, x_2, y_2]$ must be derived strictly from the **final adjudicated ground truth**. Pre-screening heuristic estimates have zero legal or certification standing.

### 4.2 Prohibition of Artificially Inflated Bounding Boxes
- **Anti-Inflation Safeguard:** Bounding boxes must tightly delineate the physical defect and its immediate transition inflection zone.
- **Strict Prohibition:** Annotators are expressly forbidden from expanding box boundaries into undamaged sheet metal or background scenery solely to satisfy the 30.0% occupancy threshold. Any candidate relying on inflated margins is disqualified.

### 4.3 Continuous Scratches & Cracks Unified AABB Rule (Safeguard 5)
- **Unified AABB Permitted:** A continuous, unbroken scratch or crack traversing a single vehicle body panel must be bounded as a **single unified enclosing Axis-Aligned Bounding Box (AABB)** representing the continuous defect footprint.
- **Panel Seam Boundary Rule:** If a long scratch or crack crosses a distinct panel gap or assembly seam (e.g. fender-to-door), annotators must generate separate bounding boxes on each respective panel to conform to automotive repair labor standards.

---

## 5. Class Taxonomy & Disambiguation Rules

### 5.1 Official 6-Class Taxonomy
1. `dent` (Class ID: 0): Plastic or sheet metal impact deformation, concave depressions, creases, hail dimples.
2. `scratch` (Class ID: 1): Paint clear-coat abrasions, key scrapes, paint gouges down to primer or metal.
3. `crack` (Class ID: 2): Structural splits, fractures in plastic bumper fascias, composite splits, torn trim.
4. `glass shatter` (Class ID: 3): Structural chips, star breaks, radial fractures, shattered vehicle glazing.
5. `lamp broken` (Class ID: 4): Fractured lenses, shattered lighting housings, missing lamps, exposed reflector bowls.
6. `tire flat` (Class ID: 5): Deflated tire profiles, rim-pinched sidewalls, delaminated blowouts.

### 5.2 Lighting Fixtures vs. Vehicle Glazing Disambiguation Rule (Rule 6)
To eliminate recurring annotator conflict:
> **RULE 6 (Lighting vs. Glazing):**  
> *Damage to any vehicle lighting fixture (headlamps, taillights, auxiliary driving lamps, fog lamps, turn signal indicators)—including cracked outer lenses, shattered polycarbonate fragments, missing lens segments, cracked reflector bowls, or displaced lighting bezels—must strictly be classified as `lamp broken` (Class 4).*  
> *The class `glass shatter` (Class 3) is reserved exclusively for vehicle structural and window glazing: laminated windshields, side door windows, rear windshields (backlights), vent glass, and panoramic sunroof panes. A headlamp with shattered lens glass is `lamp broken`, NEVER `glass shatter`.*

---

## 6. Independent Dual-Blind Human Annotation & Adjudication Protocol

Ground truth annotations must be produced through an isolated dual-blind pipeline:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 DUAL-BLIND ANNOTATION WORKFLOW                                   │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│       ┌────────────────────────┐                    ┌────────────────────────┐                   │
│       │      REVIEWER A        │                    │      REVIEWER B        │                   │
│       │  Independent Blind     │                    │  Independent Blind     │                   │
│       │  Annotation            │                    │  Annotation            │                   │
│       └───────────┬────────────┘                    └───────────┬────────────┘                   │
│                   │                                             │                                │
│                   └──────────────────────┬──────────────────────┘                                │
│                                          │                                                       │
│                                          ▼                                                       │
│                           ┌─────────────────────────────┐                                        │
│                           │      CONSENSUS ENGINE       │                                        │
│                           │   IoU >= 0.50 & Class Match │                                        │
│                           └──────────────┬──────────────┘                                        │
│                                          │                                                       │
│                      ┌───────────────────┴───────────────────┐                                   │
│                      │                                       │                                   │
│            [Consensus Achieved]                    [Conflict / Disagreement]                     │
│                      │                                       │                                   │
│                      ▼                                       ▼                                   │
│        ┌───────────────────────────┐           ┌───────────────────────────┐                     │
│        │   COORDINATE MERGE        │           │   SENIOR ADJUDICATOR C    │                     │
│        │ Mean Box Coordinates      │           │ Independent Blind Review  │                     │
│        │ Class Confirmed           │           │ Binding Coordinate Choice │                     │
│        └─────────────┬─────────────┘           └─────────────┬─────────────┘                     │
│                      │                                       │                                   │
│                      └───────────────────┬───────────────────┘                                   │
│                                          │                                                       │
│                                          ▼                                                       │
│                           ┌─────────────────────────────┐                                        │
│                           │  OCCUPANCY VERIFICATION     │                                        │
│                           │ Area(AABB) / (W * H) >= 30% │                                        │
│                           └──────────────┬──────────────┘                                        │
│                                          │                                                       │
│                      ┌───────────────────┴───────────────────┐                                   │
│                      ▼                                       ▼                                   │
│            [Occupancy >= 30.0%]                     [Occupancy < 30.0%]                          │
│                      │                                       │                                   │
│                      ▼                                       ▼                                   │
│        ┌───────────────────────────┐           ┌───────────────────────────┐                     │
│        │ CERTIFIED TIER 2 IMAGE    │           │ PERMANENTLY REJECTED      │                     │
│        │ Promoted to Valid Manifest│           │ Moved to batch_01/rejected│                     │
│        └───────────────────────────┘           └───────────────────────────┘                     │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 6.1 Reviewer Independence & Isolation
- Annotators A and B work in complete isolation.
- Neither reviewer has access to the other reviewer's labels, pre-screening metadata, YOLO model detections, or preliminary occupancy calculations.
- Zero model-assisted pre-labeling (no YOLO, SAM, or automated bounding box seeding).

### 6.2 Mathematical Consensus Thresholds
A prediction box $b_A$ from Reviewer A and $b_B$ from Reviewer B are defined as **Consensus** if and only if:
1. $\text{Class}(b_A) == \text{Class}(b_B)$
2. $\text{IoU}(b_A, b_B) \ge 0.50$

When consensus is reached, the final box coordinates are the arithmetic mean:

$$b_{\text{gold}} = \frac{1}{2}(b_A + b_B) = \left[ \frac{x_{1,A} + x_{1,B}}{2}, \frac{y_{1,A} + y_{1,B}}{2}, \frac{x_{2,A} + x_{2,B}}{2}, \frac{y_{2,A} + y_{2,B}}{2} \right]$$

### 6.3 Senior Adjudication (Adjudicator C)
The Senior Adjudicator is triggered when:
1. **Class Conflict:** $\text{Class}(b_A) \neq \text{Class}(b_B)$ (resolved via Rule 6 and defect morphology).
2. **Boundary Conflict:** $\text{IoU}(b_A, b_B) < 0.50$ (resolved via Safeguard 5).
3. **Missing Box:** One reviewer identifies an instance that the other omitted ($\text{IoU} < 0.10$).

Adjudicator C issues a binding, documented decision with physical rationale.

---

## 7. Validation Benchmark & Disaggregated Evaluation Methodology

To prevent scale and contextual distortion, model evaluation must enforce a **Quad-Metric Benchmark Reporting Architecture**:

$$\text{mAP@0.50}_{\text{composite}} = 0.70 \times \text{mAP@0.50}_{\text{Tier1}} + 0.30 \times \text{mAP@0.50}_{\text{Tier2}}$$

$$\text{mAP@0.50:0.95}_{\text{composite}} = 0.70 \times \text{mAP@0.50:0.95}_{\text{Tier1}} + 0.30 \times \text{mAP@0.50:0.95}_{\text{Tier2}}$$

### 7.1 Separation of Pooled and Composite Metrics
- **Pooled mAP ($\text{mAP}_{\text{pooled}}$):** True empirical operational performance across all concatenated detections.
- **Composite Index ($\text{mAP}_{\text{composite}}$):** Fixed-weight governance index ($70\% / 30\%$) insulated from batch sampling shifts.
- **Mandate:** Pooled and Composite mAP are mathematically non-equivalent ($\text{mAP}_{\text{pooled}} \neq \text{mAP}_{\text{composite}}$) and must both be reported side-by-side in all formal evaluation artifacts.

---

## 8. Multi-Attribute Ingestion & Governance Gates

Every candidate image must pass seven automated ingestion verification gates:
1. **Dimensional Gate:** Satisfies Tier 1 ($\ge 800 \times 600$) OR Tier 2 ($\min \ge 400, \max \ge 600$).
2. **Optical Sharpness Gate:** Laplacian blur variance $\sigma^2_{\nabla} \ge 50.0$.
3. **Damage Occupancy Gate:** Tier 2 images must verify $\ge 30.0\%$ AABB occupancy.
4. **License & Legal Provenance Gate:** Exclusively CC0, Public Domain, or CC BY; commercial ML evaluation permitted; zero viral copyleft (no CC BY-SA, GFDL).
5. **Privacy & PII Redaction Gate:** EXIF decoupled; 100% zero-entropy solid black-box redaction ($[0,0,0]$) over all visible license plates and human faces.
6. **Deduplication Gate:** Cryptographic SHA-256 uniqueness and perceptual dHash distance $\ge 16$ against training/validation corpora.
7. **Cumulative Quota Gate:** Cumulative dataset Tier 2 share must remain $\le 30.0\%$.

---

## 9. Specification Governance Status

```
========================================================================================
                          SPECIFICATION RATIFICATION STATUS
========================================================================================

Document:             runs/phase8/independent_validation_plan/v1_1_final_candidate.md
Version:              v1.1-DRAFT (Final Candidate)
Governing Baseline:   acquisition_specification.md (v1.0 Active)

Current Status:       DRAFT PROPOSAL — AWAITING FORMAL GATE B RATIFICATION
Activation Rule:      This specification possesses NO legal force until the User executes 
                      GATE B approval. Specification v1.0 remains fully active.
========================================================================================
```
