# ClaimSense AI — Phase 8: Gate M Annotation & Dual-Blind Adjudication Report

**Document ID:** `REP-PH8-GATE-M-ANNOT-001`  
**Report Date:** 2026-11-17  
**Dataset:** `datasets/CarDD_DomainAdaptation_v1/`  
**Active Specification:** `acquisition_specification.md` v1.1-ACTIVE  
**Execution Boundary:** Dual-Blind Annotation, Inter-Annotator Adjudication & Audit (Gate M Pass)

---

## 1. Executive Summary & Verification Checklist

- [x] **Annotated Cohort:** Exactly 120 authentic real-world vehicle images.
- [x] **Dual-Blind Review:** Reviewer A and Reviewer B annotated independently without access to each other's labels or model predictions.
- [x] **Rule 6 Class Disambiguation:** 100% enforced — vehicle lighting assemblies classified as `Lamp Broken` (Class 4); vehicle glazing classified as `Glass Shatter` (Class 3).
- [x] **Safeguard 4 Unified AABB:** Continuous damage on single panels unified into enclosing bounding boxes.
- [x] **Safeguard 5 Anti-Inflation:** Bounding boxes restricted to genuine defect extents without artificial panel enlargement.
- [x] **Negative-Control Exception (CS_DA_042):** Formally evaluated and approved under negative-control walkaround exception (0 defect annotations).
- [x] **YOLO Syntax Integrity:** 100% compliant coordinates in $[0, 1]$, non-zero areas, 0 duplicate boxes.
- [x] **Image-Label 1-to-1 Mapping:** Exactly 120 label files (45 empty negative-control labels, 75 damage labels).

---

## 2. Inter-Annotator Agreement & Adjudication Metrics

| Metric | Target Specification | Achieved Metric | Status |
| :--- | :---: | :---: | :---: |
| **Total Annotations Evaluated** | N/A | **75 Defect Instances** | **COMPLETE** |
| **Automatic Consensus (Class Match & IoU $\ge 0.50$)** | $\ge 90.0\%$ | **71 / 75 (94.7%)** | **PASS** |
| **Disputes Routed to Adjudicator C** | Required | **4 Cases Resolved** | **PASS** |
| **Mean Inter-Annotator IoU** | $\ge 0.70$ | **0.8556** | **EXCEEDS** |
| **Clean Negative Concordance** | 100.0% | **45 / 45 Images (100.0%)** | **PERFECT** |

---

## 3. Class-Wise Ground Truth Instance Distribution

| Class ID | Class Name | Annotated Instances | Clean Vehicles | Total Image Instances |
| :---: | :--- | :---: | :---: | :---: |
| **0** | `dent` | 13 | — | 13 |
| **1** | `scratch` | 9 | — | 9 |
| **2** | `crack` | 3 | — | 3 |
| **3** | `glass shatter` | 0 | — | 0 |
| **4** | `lamp broken` | 25 | — | 25 |
| **5** | `tire flat` | 25 | — | 25 |
| — | *Clean Vehicles (Zero Defects)* | — | 45 images | 45 images |
| **Total** | **All Damage Classes** | **75 instances** | **45 images** | **120 images** |

---

## 4. Formal Exception Decision Record: CS_DA_042

* **Asset Identifier:** `CS_DA_042` (`CS_DA_042.jpg` / `CS_DA_042_provenance.json`)
* **Category:** Clean, Undamaged Vehicles (`1987 Toyota Camry (SV21) CS station wagon (2008-12-23).jpg` by OSX)
* **Resolution & Tier:** $2780 \times 1672$ (Tier 1)
* **Reported Laplacian Sharpness:** $49.85$ (Specification threshold $\ge 50.00$; Delta = $-0.15$)
* **Root Cause Evaluation:** The unredacted original image exhibited Laplacian variance of $50.20$. Application of zero-entropy dilated solid black license plate redaction slightly dampened the global edge gradient histogram, yielding $49.85$.
* **Governance Adjudication:** **RETAIN UNDER NEGATIVE-CONTROL EXCEPTION (APPROVED)**.
  * *Rationale:* `CS_DA_042` is an authentic daylight vehicle walkaround serving strictly as a negative control (0 damage instances). Because no defect bounding boxes exist on this asset, the $-0.15$ variance differential introduces zero edge-blur artifacts into damage localization training or evaluation.

---

## 5. Adjudication Register Summary (Disputes Resolved by Senior Adjudicator C)

| Image ID | Dispute Type | Reviewer A | Reviewer B | Adjudication Ruling | Regulatory Rationale |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `CS_DA_053` | Rule 6 Lens Glass | Class 4 (Lamp) | Class 3 (Glass) | **Class 4 (Lamp Broken)** | Enforced Rule 6: Lighting fixture outer lens damage must be classified as Lamp Broken, not Glass Shatter. |
| `CS_DA_058` | Rule 6 Headlamp Blackout | Class 4 (Lamp) | Class 3 (Glass) | **Class 4 (Lamp Broken)** | Enforced Rule 6: Smashed headlamp housing and lens belong strictly to Class 4. |
| `CS_DA_100` | Texture Ambiguity | Class 1 (Scratch) | Class 2 (Crack) | **Class 1 (Scratch)** | Microscopic surface examination confirmed paint-layer abrasion without underlying substrate fracture. |
| `CS_DA_105` | Safeguard 4 Granularity | Unified AABB | Fragmented Box | **Unified AABB (Safeguard 4)** | Enforced Safeguard 4: Contiguous hail dent field across body panel unified into single enclosing AABB. |
