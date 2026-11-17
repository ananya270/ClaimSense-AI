# ClaimSense AI — v1.1 Specification Final Ratification Checklist

**Document Identifier:** `final_ratification_checklist.md`  
**Governing Standard:** `runs/phase8/independent_validation_plan/v1_1_consistency_audit.md`  
**Target Action:** Stakeholder Decision on Ratification of Proposed v1.1 Dual-Tier Standard  
**Date:** 2026-11-17  
**Status:** **AWAITING USER RATIFICATION SIGN-OFF**  

---

## 1. Stakeholder Decision Points

Please review each decision area and select the authorized direction:

### Decision 1: Specification Baseline
- [ ] **Option A: Maintain v1.0 Status Quo (Strict Single-Tier $\ge 800 \times 600$):**
  - Disqualifies all 6 Humans in the Loop CC0 images permanently.
  - Certifies Batch 1 at strictly **15 valid images** (7 Tire Flat, 6 Glass Shatter, 2 Dent, **0 Crack, 0 Lamp, 0 Scratch**).
  - Quarantines and removes `CS_VAL_016`, `017`, `020`, `021`, `022`, `023`, `024`, `025` to `rejected/`.
  - Batch 2 must source Crack, Lamp, and Scratch exclusively from Wikimedia Commons DSLR photography $\ge 800 \times 600$.
- [ ] **Option B: Ratify v1.1 Dual-Tier Standard (Walkaround $\ge 800 \times 600$; Macro $\ge 600 \times 400$):**
  - Formally establishes Tier 1 (Walkaround) and Tier 2 (Macro Component).
  - Certifies Batch 1 at **23 valid images** (15 Tier 1 + 8 Tier 2), restoring Crack (2), Lamp Broken (2), and Scratch (1).
  - Reclaims institutional CC0 sourcing from Humans in the Loop.

---

### Decision 2: Macro Quota Scope & Accounting Rule
*(Applies only if Option B is selected)*
- [ ] **Global Dataset Constraint (Recommended):**
  - Confirms that the $\le 30.0\%$ Tier 2 ceiling applies to the cumulative multi-batch dataset (Target: 200+ images), rather than strictly per batch.
  - Acknowledges that Batch 1 contains **34.78% macro imagery (8 / 23)** in isolation, and mandates that subsequent batches maintain at least **71.0% Tier 1 walkarounds** to bring the cumulative dataset into compliance (achieved as early as $N = 27$ images).
- [ ] **Strict Per-Batch Quota:**
  - Enforces $\le 30.0\%$ within every single batch. Under this rule, Batch 1 may only certify $\lfloor 23 \times 0.30 \rfloor = 6$ macro images; 2 macro images must be deferred to Batch 2.

---

### Decision 3: Damage Occupancy Metric Definition
*(Applies only if Option B is selected)*
- [ ] **Axis-Aligned Bounding Box (AABB) Area (Recommended):**
  - Explicitly codifies that the $\ge 30.0\%$ damage occupancy requirement is defined as:
    $$\frac{\text{Area}(\text{BBox}_{\text{damage}})}{\text{Width} \times \text{Height}} \ge 0.30$$
  - Aligns with standard YOLO object detection ground-truth representations and correctly qualifies longitudinal scratches (`CS_VAL_024` at 45.3% box area) and hairline fractures (`CS_VAL_020` at 59.3% box area).
- [ ] **Semantic Pixel Mask Area:**
  - Requires actual damaged surface pixels to cover $\ge 30.0\%$ of the image. (Note: Disqualifies linear scratches and hairline cracks, restricting macro crops solely to shattered lenses and massive panel dents).

---

### Decision 4: Quarantine Asset Promotion
*(Applies only if Option B is selected)*
- [ ] **Promote Quarantined Processed Copies:**
  - Formally promote `CS_VAL_016`, `CS_VAL_017`, `CS_VAL_020`, `CS_VAL_021`, `CS_VAL_022`, `CS_VAL_023`, `CS_VAL_024`, and `CS_VAL_025` from quarantined status to certified Tier 2 evaluation status.
  - Update `acquisition_manifest.csv` to record their tier classification and SHA-256 links.

---

### Decision 5: Model Evaluation Reporting Mandate
- [ ] **Mandated Disaggregated Reporting (Approved):**
  - In all downstream benchmark evaluations on `CarDD_Independent_Val_v1`, evaluators must report Precision, Recall, and F1 disaggregated for Tier 1 and Tier 2 separately, in addition to composite metrics.

---

## 2. Ratification Sign-Off Block

```
Project: ClaimSense AI
Specification Ratification: Dual-Tier Architecture (v1.1)

Selected Direction:   [ ] Option A (Maintain v1.0)    [ ] Option B (Ratify v1.1)
Quota Rule:           [ ] Global Dataset Constraint   [ ] Strict Per-Batch Quota
Occupancy Rule:       [ ] AABB Bounding Box Area      [ ] Semantic Pixel Mask Area

Authorizing Stakeholder / User: ___________________________
Authorization Date:             ___________________________
Formal Comments / Directives:   ___________________________
```

---

## 3. Governance State
- All consistency audit artifacts, CSVs, and checklists are written and preserved.
- No files have been deleted, overwritten, or modified.
- Existing v1.0 specifications remain active and frozen.
- Checkpoints remain completely untouched.
- **Execution is PAUSED awaiting your direction.**
