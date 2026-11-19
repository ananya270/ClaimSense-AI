# ClaimSense AI — Phase 9.4: Training Strategy & Hyperparameter Optimization Master Plan

**Document ID:** `REP-PH9-4-FINAL-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.4 — Training Strategy & Hyperparameter Optimization Planning  
**Previous Stages:** Phase 9.0 (Audited), Phase 9.1 (Audited), Phase 9.2 (Audited)  
**Status:** PLANNING & SPECIFICATION COMPLETE — AWAITING PROJECT OWNER APPROVAL  
**Date:** 2026-11-19  

---

## 1. Mandatory Prerequisite Verification & Blocker Audit

In accordance with Section 1 of the Phase 9.4 mandate, an audit of all prerequisite Phase 9 milestones was conducted:

| Phase | Milestone Name | Expected Location | Completion Report Status | Audit Verdict |
|---|---|---|---|---|
| **Phase 9.0** | Baseline Audit & Environment Verification | `runs/phase9/baseline_audit/` | `phase9_phase9_0_completion_report.md` | **VERIFIED COMPLETE** |
| **Phase 9.1** | Model Performance Re-evaluation | `runs/phase9/model_evaluation/` | `phase9_1_completion_report.md` | **VERIFIED COMPLETE** |
| **Phase 9.2** | Structural Crack Detection Failure Analysis | `runs/phase9/crack_investigation/` | `phase9_2_completion_report.md` | **VERIFIED COMPLETE** |
| **Phase 9.3** | Dataset Quality, Class Distribution & Annotation Audit | `runs/phase9/dataset_audit/` | None (`runs/phase9/dataset_audit/` absent) | **PREREQUISITE GAP IDENTIFIED / FORMAL BLOCKER** |

### Prerequisite Audit Findings:
1. **Phases 9.0, 9.1, and 9.2 are fully completed and internally consistent.** Their findings align cryptographically on dataset counts (300 images in CarDD_300, 115 cracks), checkpoint hashes (`49630ae...`), and failure modes ($0.0\%$ operational crack recall).
2. **Phase 9.3 Gap:** The standalone directory `runs/phase9/dataset_audit/` was not executed prior to Phase 9.4. However, the foundational data distributions and annotation quality metrics were directly audited in Phase 9.0 (`phase9_dataset_inventory.md`) and Phase 9.2 (`phase9_2_dataset_crack_inventory.csv`, `phase9_2_annotation_quality_audit.csv`).
3. **Formal Blocker Governance:** In strict adherence to Prerequisite Rule 5, this gap is formally declared as a prerequisite caveat. Full execution of future training experiments is gated upon explicit Project Owner review and ratification.

---

## 2. Verified Baseline & Checkpoint Hash Reconciliation

- **Active Production Checkpoint (`models/phase5/best.pt`):**
  - **Recalculated SHA-256:** `49630ae8d5c0066d0532a2a38efede809920a6fccd3eed59a76eb3b65f009390`
  - **Size:** 6,472,810 bytes
  - **Configuration:** 5 epochs fine-tuning on `CarDD_300` at `imgsz: 416`, SGD optimizer, `box: 7.5`, `cls: 0.5`.
  - **Performance:** mAP50 = $0.1932$, overall recall = $18.24\%$, crack recall = $0.0\%$.
- **Historical Reference Checkpoint (`90d489...`):**
  - Found on disk at `runs/detect/models/test_run/test_epoch/weights/best.pt` (SHA-256: `90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565`, 6,472,234 bytes).
  - Provenance: 1-epoch unconverged CPU smoke test that outputted 6,503 false alarms during Gate P.

---

## 3. The Three Primary Evidence-Backed Bottlenecks

1. **Class Confusion & Annotation Contradiction (Scratch Dominance):**
   - $46.2\%$ of structural cracks are localized with high spatial overlap (IoU up to $0.56$) but misclassified as `scratch`.
   - 14 CarDD training annotations exhibit overlapping `scratch` and `crack` boxes on the exact same physical lesion, teaching the network contradictory gradients.
2. **Feature Vanishing on Sub-Grid Fissures:**
   - Median crack normalized area is $0.0069$ ($8.0\times$ smaller than dent and $6.5\times$ smaller than scratch).
   - Under $640\times 640$ resizing and standard P3-P5 feature pyramids, hairline cracks measure under 15 pixels and collapse into zero active feature cells.
3. **Multi-Level Class Imbalance:**
   - Cracks represent only $12.75\%$ of training annotations ($91$ cracks vs $258$ scratches and $234$ dents). Scratches outnumber cracks by $2.84 : 1$.

---

## 4. Recommended Training Strategy & Architecture Plan (EXP04 Roadmap)

1. **P2 High-Resolution Feature Pyramid:**
   - Extend the neck architecture to include a stride-4 (P2) detection head to capture fine-grained fracture boundaries.
2. **High-Resolution Training ($832\times 832$ / $1024\times 1024$):**
   - Eliminates feature vanishing by preserving native image resolution.
3. **Class-Weighted Loss & Rebalanced Objectives:**
   - Apply focal class weighting $\alpha_{\text{crack}} = 2.8\times$.
   - Elevate classification loss weight from `cls: 0.5` to `cls: 1.5` to force discrimination between scratches and cracks.
4. **Slender Defect Regression Loss (Wise-IoU v3):**
   - Replaces standard CIoU to prevent aspect-ratio instability on elongated fissures ($2.70:1$ average, up to $14.3:1$).
5. **Annotation Disambiguation & Copy-Paste Augmentation:**
   - Remove contradictory overlapping scratch annotations from crack lesions.
   - Ingest 78 cracks from the vetted 100-image CarDD pool and deploy rare-class Copy-Paste ($0.30$).
6. **Inference Pipeline Slicing (SAHI):**
   - Deploy Slicing Aided Hyper Inference on ultra-high-resolution vehicle walkarounds.

---

## 5. Rejected Strategies & Rationale

- **REJECTED: Naive Image Oversampling:** Repeating the 56 crack images without augmentation causes rapid overfitting on background panel textures.
- **REJECTED: Lowering Operational Confidence Threshold to 0.05:** Empirical sensitivity testing proved that dropping $\tau$ to $0.05$ produces $0$ additional true cracks while causing a $6.73\times$ false-positive explosion ($147 \to 990\text{ FP}$).
- **REJECTED: Pure Inference Resolution Scaling without Retraining:** Tested in Phase 9.2; yields $\text{TP}=0$ across all resolutions (640, 832, 1024) while increasing latency by $129\%$.
- **REJECTED: Aggressive Blurring or High-Alpha MixUp:** Blurring obliterates hairline crack edges.

---

## 6. Proposed Experiment Sequence (P9-T01 through P9-T08)

- **P9-T01:** Reproducible Baseline (Resolution 640, 30 epochs, deterministic seed 42).
- **P9-T02:** Resolution Isolation (640 vs 832 vs 1024).
- **P9-T03:** Moderate General Augmentation (Photometric jitter + rotation $\pm 10^\circ$).
- **P9-T04:** Crack-Oriented Copy-Paste Augmentation ($0.30$ probability).
- **P9-T05:** Class-Weighted Loss ($\alpha_{\text{crack}} = 2.8\times$, `cls: 1.5`).
- **P9-T06:** Optimizer & Loss Formulation (AdamW + Wise-IoU).
- **P9-T07:** Composite Candidate EXP04 on Expanded/Cleaned Dataset.
- **P9-T08:** Multi-Seed Statistical Confirmation (Seeds 42, 123, 999).

---

## 7. Resource Feasibility & Dataset Safety

- **Compute Feasibility:** Total cumulative compute runtime is estimated at **$8.4\text{ CPU hours}$** across all trials. Peak memory footprint is $\le 3.2\text{ GB RAM}$. Storage consumption is $\approx 170\text{ MB}$, representing $<0.15\%$ of the $111.88\text{ GB}$ available disk space.
- **Dataset Safety:** Strict isolation is maintained across all partitions. Gate O independent benchmark (44 images) remains frozen. Gate L dev cohort is quarantined. Zero gradient updates on test or benchmark data.

---

## 8. Explicit Approval Requirements Before Phase 9.5 Execution

Before launching any model training or Phase 9.5 trials:
1. Formal Project Owner sign-off on the Phase 9.4 Master Plan.
2. Project Owner decision on whether to formally execute standalone Phase 9.3 or ratify the dataset audits embedded in Phase 9.0 and Phase 9.2.
3. Confirmation of the anti-suppression gating rule (disqualifying any model with $0$ crack detections).
