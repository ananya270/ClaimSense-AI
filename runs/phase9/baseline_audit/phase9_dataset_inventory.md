# ClaimSense AI — Phase 9.0: Dataset Inventory & Provenance Audit

**Document ID:** `AUD-PH9-DATA-INV-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.0 — Baseline Audit  
**Date:** 2026-11-19  
**Governing Standard:** `acquisition_specification.md` v1.1-ACTIVE  
**Audit Scope:** Full Inventory, Annotation Schema, Provenance, and Licensing Verification of All Computer Vision Datasets

---

## 1. Executive Summary

This inventory documents all image datasets, annotation stores, and evaluation splits available within the ClaimSense AI ecosystem. Every dataset was analyzed to confirm image counts, defect class representations, annotation formats, deduplication status, and licensing provenance.

**Strict Governance Rule:** The frozen Gate O validation benchmark (`CarDD_Independent_Val_v1`) remains quarantined and invariant. Dataset counts are reported independently without artificial aggregation.

---

## 2. Dataset Master Inventory Table

| Dataset Identifier | Physical Directory | Total Images | Partition Distribution | Annotation Format | Total Annotations | Provenance & Licensing | Status in Repo |
| :--- | :--- | :---: | :--- | :--- | :---: | :--- | :---: |
| **CarDD_300** | `datasets/CarDD_300/` | **300** | Train: 210<br/>Val: 45<br/>Test: 45 | COCO JSON + YOLO TXT (`nc=6`) | 542 instances across splits | Curated from CarDD (ICCV 2023); Research-permissive academic license | Fully present on disk (images + labels) |
| **CarDD 100 Expansion Pool** | `datasets/CarDD_Expanded_v1/` (Additions) | **100** | Train addition: 100 | YOLO TXT (`nc=6`) | ~178 instances | Sourced from broader CarDD release to bolster rare defect instances | Merged into `CarDD_Expanded_v1` |
| **CarDD_Expanded_v1** | `datasets/CarDD_Expanded_v1/` | **355** | Train: 310<br/>Val: 45 | YOLO TXT (`nc=6`) | 720 instances (Train: 622, Val: 98) | CarDD (ICCV 2023) augmented split | Configs & manifests present |
| **CarDD_Independent_Val_v1** (Frozen Benchmark) | `datasets/CarDD_Independent_Val_v1/` | **44** | Single Frozen Partition (36 Tier 1, 8 Tier 2 macro) | YOLO TXT (`nc=6`) + Detailed CSV Audit Records | **47 defect instances** | Authentic real-world vehicle images; CC-BY-4.0 / CC0 / Permissive Commercial | Fully locked & certified (`gate_g_sha256_snapshot.csv`) |
| **CarDD_DomainAdaptation_v1** (Gate L/M) | `datasets/CarDD_DomainAdaptation_v1/` | **120** | Train: 90 (75%)<br/>Dev: 30 (25%) | YOLO TXT (`nc=6`) + CSV Adjudication Registers | **75 defect instances** + **45 zero-label clean images** | Authentic daylight walkaround photography; CC-BY / CC0 / Open Source | Manifests, splits & labels fully tracked |

---

## 3. Class-Wise Annotation Breakdown by Dataset

| Defect Class | CarDD_300 (Total: 542) | CarDD_Expanded_v1 (Train: 622) | CarDD_Independent_Val_v1 (Total: 47) | CarDD_DomainAdaptation_v1 (Total: 75) | Imbalance & Representation Analysis |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **0: Dent** | 248 (45.8%) | 284 (45.7%) | 9 (19.1%) | 13 (17.3%) | Heavily dominant in CarDD collision data; moderate representation in walkarounds. |
| **1: Scratch** | 124 (22.9%) | 148 (23.8%) | 4 (8.5%) | 9 (12.0%) | Moderately represented; high intra-class variance (hairline clear-coat to deep primer gouges). |
| **2: Crack** | 56 (10.3%) | 78 (12.5%) | 6 (12.8%) | **3 (4.0%)** | **Severely underrepresented in Domain Adaptation**; primary root cause of 0% crack recall in EXP02. |
| **3: Glass Shatter** | 62 (11.4%) | 58 (9.3%) | 13 (27.7%) | 0 (0.0%) | Distinct structural damage mode; highly visible in independent validation set. |
| **4: Lamp Broken** | 32 (5.9%) | 32 (5.1%) | 6 (12.8%) | 25 (33.3%) | Expanded aggressively in Gate L to address historic missing detection of headlights/taillights. |
| **5: Tire Flat** | 20 (3.7%) | 22 (3.5%) | 9 (19.1%) | 25 (33.3%) | Expanded aggressively in Gate L to address historic flat tire detection failure. |
| **Negative Backgrounds (Clean)** | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | **45 (37.5% of images)** | 45 clean walkaround images containing 0 bounding boxes; vital for false-positive suppression. |

---

## 4. Technical Characteristics & Quality Inspection

### 1. Image Dimensions & Resolutions
- **CarDD_300:** Ranges from `800x600` to `1920x1080` (native photographic resolutions). Normalized to 416x416 (Phase 5) or 640x640 (Session 1–2).
- **Independent Validation Benchmark (`CarDD_Independent_Val_v1`):**
  - Tier 1: $\ge 800 \times 600$ (36 images; full-vehicle and multi-panel perspectives).
  - Tier 2 Macro: $\ge 600 \times 400$ with defect occupancy $\ge 30\%$ of image area (8 images; macro close-ups).
- **Domain Adaptation (`CarDD_DomainAdaptation_v1`):**
  - High-resolution smartphone and camera walkarounds (`1200x900` up to `4032x3024`).
  - Represents authentic daylight illumination, varying angles, and realistic pavement/background environments.

### 2. Annotation Quality & Dual-Blind Adjudication
- **CarDD_300:** Bounding boxes derived directly from polygon segmentation masks of the CarDD benchmark.
- **Independent Validation Set:** Certified via double-blind annotation protocol (Reviewer A, Reviewer B) with Senior Examiner adjudication recorded in `manifests/annotation/adjudication/adjudication_records.csv`. Zero unverified labels.
- **Domain Adaptation Set:** Certified via double-blind annotation protocol recorded in `datasets/CarDD_DomainAdaptation_v1/manifests/annotation/adjudication_register.csv`. 100% of disputed boundaries reconciled under Specification v1.1 Rule 6.

### 3. Missing, Corrupt, or Truncated Labels
- An automated audit of all label text files across `CarDD_300`, `CarDD_Independent_Val_v1`, and `CarDD_DomainAdaptation_v1` verified:
  - Coordinate format: Strictly normalized YOLO format (`class_id x_center y_center width height`).
  - Coordinate bounds: $0.0 \le x, y, w, h \le 1.0$.
  - Missing labels: Zero unlinked images (every image has a matching label `.txt` or is explicitly recorded as a negative background).

---

## 5. Licensing & Provenance Summary

1. **CarDD Subsets (`CarDD_300`, `CarDD_Expanded_v1`):**
   - Source: Open-source CarDD project (Car Damage Detection Dataset, Wang et al., ICCV 2023).
   - Terms: Permissive academic and open research license.
2. **Independent Benchmark (`CarDD_Independent_Val_v1`):**
   - Provenance: 44 authentic vehicular defect images curated from public repositories and licensed under Creative Commons (CC-BY-4.0, CC-BY-SA, CC0, and public domain). Detailed attributions archived in `manifests/license_attribution_manifest.csv`.
3. **Domain Adaptation Cohort (`CarDD_DomainAdaptation_v1`):**
   - Provenance: 120 authentic walkaround images curated under CC-BY and CC0 licenses. Documented in `manifests/gate_l_license_audit.md`. Zero copyright restrictions.

---

## 6. Dataset Inventory Certification

* **Dataset Authenticity:** 100% verified against historical manifests.
* **Integrity Status:** No label corruption, coordinate overflow, or unaccounted files detected.
* **Quarantine Compliance:** The frozen 44-image benchmark is isolated and documented.
