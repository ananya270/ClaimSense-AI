# Phase 8 — Dataset Expansion Pilot & Quality Assurance Report

**Project:** ClaimSense AI  
**Module:** Phase 8 Computer Vision Dataset Expansion Pilot (Batch 1 — 100 Images)  
**Date:** November 17, 2026  
**Ingestion Directory:** `datasets/CarDD_Expanded_v1/`  
**Status:** Ingestion Architecture & QA Protocols Staged (Awaiting Ingestion Approval)  

---

## 1. Executive Summary

This report establishes the operational framework for **Batch 1 (100 authentic real images)** of the ClaimSense AI dataset expansion pilot. Designed to eliminate the primary bottlenecks identified in earlier audits, this pilot targets the extreme class deficit of `crack` (currently only 91 instances in training) and the high false-positive rates of `scratch` on specular reflections.

### Core Safeguards Maintained
- **Zero In-Place Modifications:** `models/phase5/best.pt` remains 100% untouched and active in production.
- **Model Checkpoints Preserved:** Both Session 2 (640px, 41.17% mAP) and Session 3 (1024px) checkpoints are safely retained in `runs/phase8/`.
- **Phase 7 Frozen:** Verification engine logic is completely isolated.
- **Test Set Strictly Isolated:** The CarDD test split (45 images) remains permanently frozen; no pilot images will enter the test split.
- **Zero Synthetic Data:** All planned acquisitions originate exclusively from authentic motor vehicle accident and repair captures.

---

## 2. Ingestion Directory Structure (`datasets/CarDD_Expanded_v1/`)

The isolated expansion directory has been prepared with full directory separation and schema validation:

```
datasets/CarDD_Expanded_v1/
├── dataset.yaml                     # YOLO configuration (test points to frozen CarDD_300/test)
├── raw_incoming/                    # Raw camera uploads awaiting forensic & EXIF validation
├── provenance/
│   ├── provenance_schema.json       # JSON Schema enforcing source, camera, and damage metadata
│   └── manifests/                   # Per-image provenance records
├── annotations_pilot/               # Stage 1 YOLO format label drafts
├── qa_review/                       # Stage 2 dual-blind review records and IAA scorecards
├── train/
│   ├── images/                      # Curated training images (80% allocation = 80 images)
│   └── labels/                      # Validated YOLO label files
└── val/
    ├── images/                      # Curated validation images (20% allocation = 20 images)
    └── labels/                      # Validated YOLO label files
```

---

## 3. Batch 1 Allocation: Target Distribution (100 Real Images)

The 100 pilot images are stratified to remediate specific detection failure modes:

```
Batch 1 Target Allocation (100 Authentic Real Images):
├── Crack Priority:    40 Images (Target: +65 to +85 instances)
├── Scratch Priority:  35 Images (Target: +45 to +60 instances)
└── Dent Priority:     25 Images (Target: +35 to +45 instances)
```

### Detailed Ingestion Stratification Table

| Priority Focus | Planned Images | Est. Instances | Key Damage Features & Material Types | Target Environmental / Lighting Conditions |
| :--- | :---: | :---: | :--- | :--- |
| **Bumper Plastic Fractures (`crack`)** | 20 | ~35 | Deformed plastic bumper covers with splits, torn mounting ears, and lower lip fractures. | Outdoor diffuse overcast; repair shop bay lighting. |
| **Sheet-Metal & Seam Cracks (`crack`)** | 12 | ~20 | Stamped metal seam tears, door jamb splits, rocker panel fracture stress lines. | Angled workshop inspection lighting; shadow-penetrating fill. |
| **Composite & Lamp Bezels (`crack`)** | 8 | ~15 | Cracks in headlamp/tail lamp plastic housings, fog lamp surrounds, fiberglass grilles. | Macro close-ups with sharp boundary contrast. |
| **Specular Glare Scratches (`scratch`)** | 15 | ~25 | Real scratches on glossy panels with sharp direct sunlight highlights (to teach glare discrimination). | Harsh mid-day sun; high-contrast directional beams. |
| **Metallic & Pearl Paint (`scratch`)** | 12 | ~20 | Scratches through multi-layer clear coats on metallic gray, silver, and pearl white finishes. | Diffuse daylight; workshop fluorescent tubes. |
| **Continuous Single Scrapes (`scratch`)** | 8 | ~10 | Long continuous key scratches and side scrapes spanning across full door or fender panels. | Side profile captures; low-angle illumination. |
| **Body Crease Line Dents (`dent`)** | 12 | ~20 | Impact depressions crossing sharp body styling lines (door waistlines, wheel arch ridges). | Grazing directional light highlighting shadow drops. |
| **Shallow Low-Contrast Dents (`dent`)** | 8 | ~12 | Soft panel depressions without paint loss on white/silver cars (detected via distorted reflections). | Reflections of linear objects (light poles, grid patterns). |
| **Hail Damage Multi-Point (`dent`)** | 5 | ~15 | Roof and hood hail dings (20px to 60px diameter) on metal panels. | High-contrast grazing angle lighting. |
| **TOTAL** | **100** | **~145–190** | **High-fidelity authentic damage representation** | **Balanced across realistic claim conditions** |

---

## 4. Quality Assurance & Dual-Review Protocol

To guarantee that the expanded dataset meets rigorous standards before any model training is permitted, every image and annotation must complete a 4-stage QA gate:

```
[Raw Real Image Ingestion]
           │
           ▼
[Stage 1: Forensic Verification] ──> Reject if synthetic, AI-generated, or EXIF missing
           │
           ▼
[Stage 2: Standardized Annotation] ──> Apply Phase 8 Annotation Guidelines
           │
           ▼
[Stage 3: Automated Linter Check] ──> scripts/lint_annotations.py (zero syntax errors, >=16px)
           │
           ▼
[Stage 4: Dual-Blind Review (>=20%)] ──> Compute Inter-Annotator Agreement (IAA >= 85%)
           │
           ▼
[Approved Ingestion: 80% Train, 20% Val] (Test Split permanently untouched)
```

### 4.1 Automated Pre-Ingestion Linter (`scripts/lint_annotations.py`)
The automated linter developed in Phase 8 verifies:
1. **Class Integrity:** Class index strictly within $[0, 5]$.
2. **Coordinate Clamping:** $0.0 \le x_c, y_c, w, h \le 1.0$.
3. **Minimum Scale Threshold:** Minimum native bounding box dimension $\ge 16\text{ px}$. Sub-16px boxes must be symmetrically padded or flagged.
4. **Intra-Class Overlap:** Bounding boxes of the same class with $\text{IoU} > 0.35$ are flagged for consolidation.
5. **Aspect Ratio Limit:** Non-scratch boxes with aspect ratio $> 20:1$ are flagged for artifact check.

### 4.2 Dual-Blind Review Protocol & Inter-Annotator Agreement (IAA)
- **Sampling Rate:** A minimum of **20 out of 100 images** (20%) are randomly selected and independently annotated by two separate reviewers without viewing each other's annotations.
- **Agreement Metric:** Inter-Annotator Agreement is measured using class-matched Bounding Box IoU:
  $$\text{IAA} = \frac{\text{Matching Annotations } (\text{Class Match} \land \text{IoU} \ge 0.50)}{\text{Total Unique Annotations}} \times 100\%$$
- **Acceptance Threshold:** The pilot batch must achieve **$\text{IAA} \ge 85.0\%$**.
- **Arbitration:** Any discrepancy with $\text{IoU} < 0.50$ or conflicting class assignment is reviewed and adjudicated by the Lead Claims Assessor.

### 4.3 Provenance & Audit Trail
Every image ingested into `datasets/CarDD_Expanded_v1/` receives a JSON manifest complying with `provenance_schema.json`:
- Cryptographic SHA-256 digest of original raw file.
- Acquisition date and source entity (repair facility, claims audit, or salvage assessment).
- Camera EXIF data (make, model, focal length, ISO, original resolution).
- Damage profile (affected panel, paint finish, lighting condition).
- Dual-review approval timestamp and reviewer signatures.

---

## 5. Status & Next Steps

| Component | Status | Next Required Action |
| :--- | :---: | :--- |
| **`models/phase5/best.pt` (Baseline)** | **100% UNTOUCHED** | Retain in production. |
| **Candidate Models (Session 2 & 3)** | **PRESERVED IN STAGING** | Retained for future post-expansion benchmark. |
| **Reversible Training Backup** | **COMPLETED (210 files)** | `datasets/CarDD_300/train/labels_backup_original/` secured. |
| **Annotation Guidelines** | **COMPLETED & APPROVED** | Formally documented in `annotation_guidelines.md`. |
| **Correction Proposals Catalog** | **STAGED FOR REVIEW** | Cataloged in `annotation_correction_proposals.md`. |
| **Ingestion Directory Structure** | **CREATED & CONFIGURED** | `datasets/CarDD_Expanded_v1/` initialized. |
| **Automated Ingestion Linter** | **OPERATIONAL** | Validated via `scripts/lint_annotations.py`. |
| **Model Training** | **STRICTLY PAUSED** | Awaiting pilot acquisition and human review sign-off. |

---

## 6. Review & Approval Request

This concludes the Phase 8 Dataset Cleanup & Expansion Pilot setup. 
- All proposed label corrections are safely cataloged in [annotation_correction_proposals.md](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/annotation_correction_proposals.md) without modifying any existing dataset files.
- The expansion ingestion structure and schema are ready in `datasets/CarDD_Expanded_v1/`.
- No model training has been initiated, and no checkpoints have been modified or promoted.

Awaiting your review and approval before proceeding with image ingestion or applying any proposed label corrections.
