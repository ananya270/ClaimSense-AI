# ClaimSense AI — Phase 9.4: Dataset & Benchmark Protection Plan

**Document ID:** `REP-PH9-4-DATA-PROT-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.4 — Training Strategy & Hyperparameter Optimization Planning  
**Governing Standard:** Gate G Cryptographic Integrity Snapshot & Phase 8 Governance  
**Status:** DATASET PARTITIONING & INTEGRITY PROTOCOL SEALED  

---

## 1. Executive Summary

This plan defines mandatory data governance boundaries to eliminate data leakage, prevent evaluation contamination, and protect the scientific integrity of all benchmark cohorts across Phase 9 training experiments.

---

## 2. Cohort Separation & Strict Boundary Taxonomy

```
+-------------------------------------------------------------------------------------------------+
| DATASET COHORT PARTITIONING TAXONOMY                                                            |
+-------------------------------------------------------------------------------------------------+
|                                                                                                 |
| [CATEGORY 1: TRAINING DATA] (Authorized for gradient updates)                                   |
|   - CarDD_300 Train Split (210 images, 714 instances)                                           |
|   - Additional 100-Image CarDD Pool (100 images, 78 cracks) [Verified Hamming >= 15]            |
|   - Domain Adaptation Train Split (90 images)                                                   |
|                                                                                                 |
| [CATEGORY 2: VALIDATION DATA] (Hyperparameter tuning & early stopping)                          |
|   - CarDD_300 Val Split (45 images, 140 instances)                                              |
|                                                                                                 |
| [CATEGORY 3: FROZEN TEST DATA] (Final offline test split evaluation)                            |
|   - CarDD_300 Test Split (45 images, 148 instances)                                             |
|   * RULE: Strictly read-only; no gradient updates; no early-stopping tuning.                     |
|                                                                                                 |
| [CATEGORY 4: DEVELOPMENT TUNING COHORT] (Domain adaptation ranking)                             |
|   - Gate L Dev Walkaround Split (30 images, 19 instances)                                       |
|   * RULE: Must NEVER be described or reported as "independent validation".                     |
|                                                                                                 |
| [CATEGORY 5: FROZEN INDEPENDENT BENCHMARK] (Safety-critical external validation)                |
|   - Gate O Independent Benchmark (44 images, 47 instances, cryptographic snapshot)              |
|   * RULE: Frozen snapshot; zero images may ever be used for training, tuning, or ranking.       |
|                                                                                                 |
| [CATEGORY 6: COMBINED FORENSIC COHORT] (Offline forensic auditing)                              |
|   - Gate P Cohort (75 images: 45 CarDD Test + 30 Gate L Dev)                                    |
|   * RULE: Strictly for forensic comparison across gate transitions.                             |
+-------------------------------------------------------------------------------------------------+
```

---

## 3. Seven-Pillar Data Leakage Prevention Protocol

### Pillar 1: Exact Duplicate Detection (SHA-256 Collisions)
- Every candidate training image must be evaluated against the SHA-256 database of all validation, test, and benchmark images. Any hash match results in immediate candidate disqualification.

### Pillar 2: Near-Duplicate Detection (dHash Hamming Distance $\ge 15$)
- All incoming images must undergo perceptual hashing (difference hash, dHash 64-bit).
- Candidates with a Hamming distance $<15$ to any evaluation image are rejected to eliminate repeated burst captures, angle variations, or post-processed copies.

### Pillar 3: Augmented Copy Isolation
- All augmentations (Mosaic, MixUp, Copy-Paste, Rotation) must be generated dynamically on-the-fly inside the PyTorch data loader pipeline.
- Saving pre-augmented copies to disk in shared directories is strictly prohibited.

### Pillar 4: Cross-Split Separation Enforcement
- Training scripts must read dataset definitions strictly through verified, immutable YAML files (`data/cardd_train.yaml`).
- Hardcoded relative path traversal into evaluation directories is strictly prohibited.

### Pillar 5: Source Image Provenance Tracking
- Every image in the expanded training cohort must have a verifiable entry in a JSON manifest containing `source_dataset`, `source_split`, `original_filename`, `image_sha256`, and `min_hamming_dist`.

### Pillar 6: Annotation Leakage Prevention
- Annotations for validation and test splits must remain locked with read-only filesystem attributes.
- No automated labeling tool or heuristic script may write to evaluation label directories.

### Pillar 7: Prohibition of Evaluation-Driven Epoch Cherry-Picking
- Checkpoint selection must be driven exclusively by Category 2 validation loss and validation Macro-F1. Selecting checkpoints based on performance on Category 3 (Test) or Category 5 (Gate O) is considered severe leakage and grounds for experiment invalidation.
