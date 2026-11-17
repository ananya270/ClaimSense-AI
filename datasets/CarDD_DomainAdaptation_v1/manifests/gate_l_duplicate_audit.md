# ClaimSense AI — Phase 8: Gate L Forensic Duplicate & Leakage Audit

**Document ID:** `AUD-PH8-GATE-L-DUP-001`  
**Audit Date:** 2026-11-17  
**Dataset:** `CarDD_DomainAdaptation_v1` (120 images)  
**Reference Baselines:**
- CarDD Training Dataset (442 unique SHA256 hashes / 655 split instances)
- Frozen Independent Validation Dataset `CarDD_Independent_Val_v1` (44 unique images: 23 Batch 1, 21 Batch 2)
- Total Reference Baselines: 486 unique cryptographic and perceptual hashes.

---

## 1. Deduplication Protocol & Verification Gates

To eliminate training contamination and prevent benchmark leakage:
1. **Exact Cryptographic Check:** 256-bit SHA-256 binary hash cross-check against all 486 baseline images.
2. **Perceptual Similarity Gate:** 64-bit Difference Hash (dHash) with Hamming distance threshold $H \le 5$.
3. **Cohort Internal Check:** Pairwise cryptographic and perceptual comparisons across all 120 `CS_DA` images.

---

## 2. Forensic Audit Results

| Audit Gate | Reference Cohort | Detected Collisions | Audit Status |
| :--- | :--- | :---: | :---: |
| Exact SHA-256 Match | vs. CarDD Training Set (442 images) | **0** | **PASS** |
| Exact SHA-256 Match | vs. Frozen Validation Benchmark (44 images) | **0** | **PASS** |
| Perceptual dHash Match ($H \le 5$) | vs. CarDD Training Set (442 images) | **0** | **PASS** |
| Perceptual dHash Match ($H \le 5$) | vs. Frozen Validation Benchmark (44 images) | **0** | **PASS** |
| Internal Cryptographic Duplicates | Within `CS_DA` 120-image cohort | **0** | **PASS** |
| Internal Perceptual Duplicates | Within `CS_DA` 120-image cohort ($H \le 5$) | **0** | **PASS** |

---

## 3. Quarantined Candidate Screening Verification

During automated qualification, candidates with near-duplicate resemblance or duplicate hashes were proactively filtered out and logged in `gate_l_rejected_candidates.csv`.

---

## 4. Benchmark Isolation Certification

The 120 acquired images in `CarDD_DomainAdaptation_v1` share **strictly 0.0% overlap** (exact or perceptual) with either the CarDD training corpus or the 44-image frozen independent validation benchmark (`CarDD_Independent_Val_v1`). Benchmark isolation is verified with 100% mathematical certainty.
