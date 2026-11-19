# ClaimSense AI — Phase 9.6: Benchmark Cryptographic & Dataset Integrity Audit

**Document ID:** `REP-PH9-6-INTEG-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.6 — Independent Benchmark Evaluation & Candidate Model Validation  
**Execution Date:** 2026-11-20  
**Status:** CRYPTOGRAPHICALLY VERIFIED & AUDITED  

---

## 1. Executive Summary

This report establishes the cryptographic verification of all benchmark datasets, model checkpoints, and configuration files before and after the execution of the Phase 9.6 independent evaluation.

In accordance with Section 12 of the Phase 9.6 mandate:
- All benchmark test images remained completely unchanged.
- All benchmark labels remained completely unchanged.
- Zero evaluation outputs or predictions were written into source dataset directories.
- Zero benchmark test images were copied or ingested into training splits.

---

## 2. Dataset & Configuration Checksum Verification Table

| File / Artifact | Relpath | Pre-Benchmark SHA-256 | Post-Benchmark SHA-256 | Invariance Status |
|---|---|---|---|---|
| **Dataset Config** | `datasets/CarDD_300/data.yaml` | `72abd2d88c7805392f9d55431a4d9e6c299be4d20df69122a61f78c7c2652320` | `72abd2d88c7805392f9d55431a4d9e6c299be4d20df69122a61f78c7c2652320` | **100% INVARIANT (PASS)** |
| **Data Config (Abs)**| `data/cardd.yaml` | `0555f33f4a3d651d2cc6125920e5f6b669338710f2d416ecc61275199d92efb7` | `0555f33f4a3d651d2cc6125920e5f6b669338710f2d416ecc61275199d92efb7` | **100% INVARIANT (PASS)** |
| **Production Model** | `models/phase5/best.pt` | `49630ae8d5c0066d0532a2a38efede809920a6fccd3eed59a76eb3b65f009390` | `49630ae8d5c0066d0532a2a38efede809920a6fccd3eed59a76eb3b65f009390` | **100% INVARIANT (PASS)** |
| **Candidate P9-T01** | `runs/phase9/retraining/P9-T01/checkpoints/best.pt` | `e3e60fd2911819ec996ed5ce1591ced26530692be7d55ec22d55e4c2fde51e80` | `e3e60fd2911819ec996ed5ce1591ced26530692be7d55ec22d55e4c2fde51e80` | **100% INVARIANT (PASS)** |
| **Candidate P9-T02** | `runs/phase9/retraining/P9-T02/checkpoints/best.pt` | `91a943a9a246a0748d6f8f07a0b0860ad5872c3f229ab2f69930bb37db6ca721` | `91a943a9a246a0748d6f8f07a0b0860ad5872c3f229ab2f69930bb37db6ca721` | **100% INVARIANT (PASS)** |

---

## 3. Directory Isolation & Read-Only Conformance

1. **Source Dataset Integrity:** `datasets/CarDD_300/test/images` contains 45 images with identical modification times; `datasets/CarDD_300/test/labels` contains 45 label files with identical modification times.
2. **Output Containment:** All generated metrics, CSV records, and visual comparison assets were written exclusively to:
   `runs/phase9/independent_evaluation/`
3. **Database Safeguard:** `data/claimsense.db` was verified before and after evaluation. Zero records were inserted or modified during benchmarking.
4. **Conclusion:** **INTEGRITY AUDIT PASSED WITH ZERO DISCREPANCIES.**
