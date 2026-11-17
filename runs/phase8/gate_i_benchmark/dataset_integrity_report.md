# ClaimSense AI — Phase 8: Gate I Dataset Integrity Report

**Dataset Name:** `CarDD_Independent_Val_v1`  
**Evaluation Scope:** 44 Images, 47 Ground-Truth Instances  
**Active Specification:** `acquisition_specification.md` — v1.1-ACTIVE  
**Audit Timestamp:** 2026-11-17  
**Governance Gate:** Gate I — Independent Model Benchmark Execution Authorization

---

## 1. Executive Summary

This report documents the cryptographic integrity, tier composition, and label validation of the independent validation dataset `CarDD_Independent_Val_v1` evaluated under Gate I.

Immediately prior to benchmark execution, all 44 images and 44 ground-truth label files were cryptographically hashed (SHA-256) and verified against the certified inventory. Following benchmark completion across all three checkpoints and evaluation splits, a second post-benchmark SHA-256 verification was conducted.

**Audit Result:** 100% PASS. All 44 images and 44 labels remained completely untouched and immutable.

---

## 2. Dataset Composition & Macro Quota Reconciliation

Under active specification `v1.1-ACTIVE`, the independent validation dataset adheres to strict dual-tier resolution boundaries and a cumulative macro-tier ceiling of $\le 30.00\%$.

### 2.1 Tier Composition Summary

| Batch ID | Total Accepted Images | Tier 1 (Walkaround) | Tier 2 (Macro) | Tier 2 Macro Share | Compliance Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Batch 1** (`batch_01`) | 23 | 15 | 8 | 34.78% | Batch-level quarantine lifted via Gate D/H |
| **Batch 2** (`batch_02`) | 21 | 21 | 0 | 0.00% | 100% Tier 1 quota remediation |
| **Cumulative Total** | **44** | **36** | **8** | **18.18%** | **PASS ($\le 30.00\%$ Quota Ceiling)** |

$$\text{Cumulative Macro Share} = \frac{8}{44} = 18.1818\% \le 30.0000\%$$
$$\text{Safety Headroom Below Quota Ceiling} = 30.00\% - 18.18\% = +11.82\%$$

The dataset satisfies all macro-tier quota constraints with substantial headroom.

---

## 3. Ground-Truth Class & Instance Distribution

The 44 evaluation images contain **47 verified ground-truth damage instances** established through dual-blind annotation (Reviewer A & Reviewer B) and adjudicated under Senior Adjudicator C.

| Class ID | Class Name | Image Count | Instance Count | % of Instances | Tier 1 Instances | Tier 2 Instances |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **0** | **Dent** | 9 | 9 | 19.15% | 7 | 2 |
| **1** | **Scratch** | 4 | 4 | 8.51% | 2 | 2 |
| **2** | **Crack** | 6 | 6 | 12.77% | 4 | 2 |
| **3** | **Glass Shatter** | 10 | 13 | 27.66% | 13 | 0 |
| **4** | **Lamp Broken** | 6 | 6 | 12.77% | 5 | 1 |
| **5** | **Tire Flat** | 9 | 9 | 19.15% | 8 | 1 |
| **Total** | — | **44** | **47** | **100.00%** | **39** | **8** |

*Note on Multi-Instance Images:* 
- `CS_VAL_019`: 2 instances (1 Glass Shatter + 1 Dent)
- `CS_VAL_040`: 2 instances (1 Glass Shatter + 1 Dent)
- `CS_VAL_045`: 2 instances (2 Glass Shatter panels)

---

## 4. Cryptographic Hash Verification

### 4.1 Verification Protocol
- Pre-benchmark SHA-256 hashes were loaded from `runs/phase8/independent_validation_plan/gate_g_image_label_inventory.csv`.
- All 44 image binaries and 44 label text files were re-hashed prior to staging.
- All 44 image binaries and 44 label text files were re-hashed upon benchmark completion.

### 4.2 Verification Outcome
- **Total Files Audited:** 88 files (44 `.jpg` images + 44 `.txt` label files)
- **Pre-Benchmark Match Rate:** 88 / 88 (100.00%)
- **Post-Benchmark Match Rate:** 88 / 88 (100.00%)
- **Corrupted / Altered Files:** 0
- **External Overlap with CarDD Training Data (655 images):** 0 collisions
- **Internal Cross-Batch Duplicates:** 0 collisions

---

## 5. Certification

I hereby certify that the 44 images and 47 ground-truth instances comprising `CarDD_Independent_Val_v1` were preserved in an immutable, audited state throughout the Gate I benchmark execution.
