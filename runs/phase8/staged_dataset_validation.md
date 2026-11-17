# Phase 8 — Staged Dataset Validation & Integrity Report

**Project:** ClaimSense AI  
**Module:** Phase 8 Working Dataset (`CarDD_Expanded_v1`) Validation & Quality Audit  
**Date:** November 17, 2026  
**Staged Training Split:** `datasets/CarDD_Expanded_v1/train/` (210 Images, 210 Label Files)  
**Correction Manifest:** [runs/phase8/correction_manifest.json](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/correction_manifest.json) (35 Applied Consolidations)  
**Status:** Staging Complete & Validated — Awaiting Authorization  

---

## 1. Executive Summary & Verification Scope

In accordance with the Stage 2 approved scope, the verified annotation consolidations have been staged into an isolated working copy: `datasets/CarDD_Expanded_v1/train/`. 

This validation report provides:
1. **Zero-Tamper Verification:** Empirical proof that original CarDD training labels and backups remain 100% untouched.
2. **Instance Count Deltas:** Complete class-by-class comparison of instance counts before and after consolidation.
3. **Automated Linter Results:** Full validation using `scripts/lint_annotations.py` confirming 0 syntax errors.
4. **Manual Review Queue Status:** Accounting of all 78 cases safely preserved in the review queue.

---

## 2. Zero-Tamper Baseline & Safeguard Verification

Cryptographic SHA-256 checksums were computed across all datasets to confirm strict isolation:

| Component | Target Location | Verification Method | Status |
| :--- | :--- | :--- | :---: |
| **Original CarDD Training Labels** | `datasets/CarDD_300/train/labels/` | SHA-256 match against initial hashes (210 files) | **100% UNTOUCHED** |
| **Original Reversible Backup** | `datasets/CarDD_300/train/labels_backup_original/` | Verified identical bit-for-bit (210 files) | **100% UNTOUCHED** |
| **Validation Dataset** | `datasets/CarDD_300/val/` | Zero files modified or accessed for writing | **FROZEN & ISOLATED** |
| **Test Dataset** | `datasets/CarDD_300/test/` | Zero files modified or accessed for writing | **FROZEN & ISOLATED** |
| **Production Baseline Checkpoint** | `models/phase5/best.pt` | SHA-256: `90d489e46ff8521edff88d522f0feffa164ac...` | **100% UNTOUCHED** |
| **Staged Working Dataset** | `datasets/CarDD_Expanded_v1/train/` | New isolated copy with 35 verified corrections applied | **STAGED & ISOLATED** |

---

## 3. Class Instance Distribution: Original vs. Staged Working Copy

The table below details the change in instance counts resulting from consolidating fragmented sub-boxes into unified bounding envelopes:

| Damage Class | Original CarDD_300 Train | Staged CarDD_Expanded_v1 Train | Instance Delta | Nature of Change |
| :--- | :---: | :---: | :---: | :--- |
| **`dent`** | 234 | **230** | **-4** | Merged 4 tiny sub-15px edge boxes in `000265.jpg` into 1 parent dent box. |
| **`scratch`** | 258 | **204** | **-54** | Consolidated 34 multi-slice scratch images into unified continuous scratch boxes. |
| **`crack`** | 91 | **91** | **+0** | **Strictly unchanged.** No missing crack annotations were automatically injected. |
| **`glass shatter`** | 45 | **45** | **+0** | Unmodified. |
| **`lamp broken`** | 64 | **64** | **+0** | Unmodified. |
| **`tire flat`** | 22 | **22** | **+0** | Unmodified. |
| **TOTAL INSTANCES** | **714** | **656** | **-58** | **58 redundant fragmented boxes consolidated into true physical envelopes.** |

### Key Observations
- The instance count reduction from 714 to 656 does **not** represent lost damage labels. Rather, it eliminates artificial label fragmentation where a single 40cm vehicle scrape was counted as 4 or 5 separate bounding boxes.
- Crack annotations remain at exactly 91 instances; zero synthetic or unverified crack labels were added.

---

## 4. Automated Linter Validation Results (`scripts/lint_annotations.py`)

The automated linter executed across all 210 staged label files in `datasets/CarDD_Expanded_v1/train/labels/`:

```
==========================================================
  CLAIMSENSE AI - ANNOTATION LINTER & INTEGRITY AUDITOR
==========================================================
Target Directory: datasets/CarDD_Expanded_v1/train
Image Directory:  datasets/CarDD_Expanded_v1/train/images (210 images)
Label Directory:  datasets/CarDD_Expanded_v1/train/labels (210 label files)

Results:
  - Total Files Linted:         210
  - Total Syntax Errors:        0 (Hard Failures: 100% Valid YOLO format)
  - Coordinate Range Failures:  0 (All coords strictly within [0.0, 1.0])
  - Invalid Class Index:        0 (All class IDs strictly within 0-5)
  - Guideline Warnings:         13 (Sub-16px, aspect ratio, overlap)
  - Validation Status:          PASSED (Zero Syntax Errors)
```

### Improvement Over Original Dataset
- **Guideline warnings decreased from 18 to 13**: Consolidating `000265.jpg` eliminated 4 sub-15px edge warnings.
- The remaining 13 warnings correspond to cases in the manual review queue (e.g., `001149.jpg` needle boxes and hairline cracks with native narrow dimensions).

---

## 5. Manual Review Queue Status (78 Preserved Cases)

All cases flagged as ambiguous or requiring human assessor inspection remain strictly preserved in the review queue:

| Category | Preserved Cases | Status in Staged Working Copy | Required Next Action |
| :--- | :---: | :--- | :--- |
| **Scratch Cases** | 16 | Retained as original separate boxes | Human visual inspection to decide whether to merge or keep separate. |
| **Dent Cases** | 2 | Retained as original boxes (`001149.jpg`) | Inspect against hood shutline shadow. |
| **Missing Crack Candidates** | 60 | **Zero added to dataset** | Review candidate coordinates against original collision photos. |
| **TOTAL IN QUEUE** | **78** | **Preserved untouched** | **Awaiting human assessor review.** |

---

## 6. Staging Conclusion & Approval Request

1. **Working Staged Dataset:** `datasets/CarDD_Expanded_v1/train/` is fully staged, verified, and lint-clean.
2. **Correction Manifest:** Machine-readable record saved to [runs/phase8/correction_manifest.json](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/correction_manifest.json).
3. **Safeguard Compliance:** Production model untouched, original dataset untouched, no model training launched, Phase 7 frozen.

**STOPPED:** Staging and validation are complete. Awaiting explicit user approval before proceeding to authentic image ingestion or further training.
