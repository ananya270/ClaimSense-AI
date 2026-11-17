# ClaimSense AI — Specification Amendment Approval Checklist (v1.1)

**Document Identifier:** `approval_checklist.md`  
**Governing Standard:** `runs/phase8/independent_validation_plan/macro_tier_amendment_proposal.md`  
**Target Action:** Decision on ratifying Dual-Tier Resolution Standard (v1.1) vs. Maintaining Single-Tier Status Quo (v1.0)  
**Date:** 2026-11-17  
**Status:** **AWAITING USER SIGN-OFF**  

---

## 1. Executive Decision Matrix

Review the decision points below and select the authorized direction:

| Decision Area | Option A: Maintain v1.0 Status Quo | Option B: Ratify Proposed v1.1 Dual-Tier Standard | User Selection |
| :--- | :--- | :--- | :---: |
| **Minimum Resolution Standard** | Single-tier: $\text{Width} \ge 800\text{ px}$ AND $\text{Height} \ge 600\text{ px}$ across all images. | Dual-tier: Tier 1 (Walkaround) $\ge 800 \times 600$; Tier 2 (Macro) $\ge 600 \times 400$. | [ ] Option A<br>[ ] Option B |
| **Humans in the Loop CC0 Sourcing** | Completely disqualified. All 6 Batch 1 HITL images permanently rejected. Zero future HITL use. | Approved for Tier 2 Macro inspection imagery meeting $\ge 600 \times 400$ and $\ge 30\%$ damage occupancy. | [ ] Option A<br>[ ] Option B |
| **Batch 1 Certified Yield** | **15 valid images** (7 Tire Flat, 6 Glass Shatter, 2 Dent, **0 Crack, 0 Lamp, 0 Scratch**). | **23 qualified images** (7 Tire, 6 Glass, 4 Dent, **2 Crack, 2 Lamp, 1 Scratch**). | [ ] Option A<br>[ ] Option B |
| **Macro Dataset Allocation Cap** | N/A (Macro crops prohibited). | Strictly capped at **$\le 30.0\%$ of total 200+ image dataset** ($\ge 70.0\%$ reserved for walkarounds). | [ ] Approved<br>[ ] Rejected |
| **Damage Area Occupancy Rule** | N/A. | Enforce hard requirement: localized damage bounding box must occupy **$\ge 30.0\%$ of total image area**. | [ ] Approved<br>[ ] Rejected |
| **Orientation Rule for Macro Tier** | Strict: Width $\ge 800$, Height $\ge 600$ (Portrait orientation disqualified). | Orientation-agnostic for Tier 2: $\min(w, h) \ge 400$ AND $\max(w, h) \ge 600$ (Portrait permitted). | [ ] Approved<br>[ ] Rejected |
| **Evaluation Reporting Requirement** | Single aggregate mAP metric. | Mandated disaggregated reporting: report Tier 1 vs Tier 2 Precision, Recall, and F1 separately. | [ ] Approved<br>[ ] Rejected |

---

## 2. Itemized Verification & Compliance Checklist

Verify that all foundational data governance, legal, and privacy prerequisites are satisfied before authorization:

### A. Legal & Licensing Verification
- [x] **Primary Source Deeds Verified:** All candidate files originate from Humans in the Loop (CC0) or Wikimedia Commons (Public Domain / CC BY 2.0).
- [x] **Zero Viral Licensing:** Zero CC BY-SA, GFDL, or ambiguous licenses ingested or planned.
- [x] **Attribution Preservation:** Itemized contributor metadata preserved in `license_attribution_manifest.csv`.

### B. Quality & Technical Gate Verification
- [x] **Optical Blur Screening:** Measured Discrete Laplacian Variance $\sigma_{\nabla}^2 \ge 50.0$ verified for all qualified files.
- [x] **Zero Near-Duplicates:** Minimum pairwise dHash Hamming distance = 16 (threshold $\le 4$).
- [x] **Damage Area Quantification:** All 8 proposed Tier 2 candidates verified to occupy $\ge 45.0\%$ damage area (exceeding the $\ge 30.0\%$ threshold).

### C. Privacy & Security Verification
- [x] **Zero PII Leakage:** All 7 visible license plates redacted with $\ge 15\%$ dilated solid black `[0, 0, 0]` masks (zero entropy).
- [x] **Zero Face Exposure:** Zero human faces present in any candidate image.
- [x] **Zero Damage Occlusion:** Redaction masks overlap $0.0\%$ of damage instances.
- [x] **EXIF Decoupling:** Processed evaluation copies contain strictly 0 EXIF tags. Technical settings isolated in provenance JSON sidecars.
- [x] **Restricted Access Isolation:** Raw unredacted binaries remain locked in `batch_01/raw_restricted/`.

---

## 3. Quarantined Asset Disposition Instructions

Indicate the required disposition for the 8 currently quarantined processed copies in `batch_01/processed/` (`CS_VAL_016`, `017`, `020`, `021`, `022`, `023`, `024`, `025`):

- [ ] **If Option B (v1.1) is ratified:**  
  Promote all 8 quarantined images to officially certified status, update `acquisition_manifest.csv` to designate them as `Tier 2 (Macro Component)`, and include them in the active dataset.
- [ ] **If Option A (v1.0) is maintained:**  
  Permanently remove all 8 images from `batch_01/processed/`, move their files to `batch_01/rejected/`, and update manifests to reflect a final 15-image Batch 1 dataset.

---

## 4. Authorization Sign-Off Block

```
Project: ClaimSense AI
Phase: Phase 8 — Independent Validation Dataset Acquisition
Specification Amendment: v1.1-DRAFT (Dual-Tier Resolution Architecture)

Authorized Direction: [ ] Option A (Maintain v1.0)    [ ] Option B (Ratify v1.1)

Authorizing Stakeholder / User: ___________________________
Authorization Date:             ___________________________
Formal Comments / Directives:   ___________________________
```

---

## 5. Current State
- All proposal files, impact reports, and checklists are preserved in `runs/phase8/independent_validation_plan/`.
- No files have been deleted, overwritten, or modified.
- Existing v1.0 specifications remain active and frozen.
- Checkpoints remain completely untouched.
- **Execution is PAUSED awaiting your direction.**
