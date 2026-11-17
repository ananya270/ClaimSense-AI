# ClaimSense AI — Phase 8: Gate I Checkpoint Integrity Report

**Benchmark Execution Date:** 2026-11-17  
**Governance Gate:** Gate I — Independent Model Benchmark Execution Authorization  
**Active Specification:** `acquisition_specification.md` — v1.1-ACTIVE  
**Execution Mode:** STRICTLY BENCHMARK ONLY (Read-Only / Zero Modifications)

---

## 1. Executive Summary

In strict accordance with Gate I governance mandates, all three model checkpoints evaluated during the independent benchmark were cryptographically hashed (SHA-256) immediately prior to inference execution and immediately following inference completion. 

All three checkpoints remained **100% byte-for-byte immutable and unaltered** throughout the benchmark workflow. No model weights, hyperparameters, configs, or metadata were modified, fine-tuned, or overwritten.

---

## 2. Checkpoint SHA-256 Verification Matrix

| Checkpoint Name | File Path | Pre-Benchmark SHA-256 | Post-Benchmark SHA-256 | Verification Status |
| :--- | :--- | :--- | :--- | :---: |
| **Production Baseline (Phase 5)** | `models/phase5/best.pt` | `90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565` | `90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565` | **MATCH (PASS)** |
| **Phase 8 Session 2** | `runs/phase8/session_2/weights/best.pt` | `2ee0a56749ceba72da863fd3496f080ee06f26409daa4e9588fb69ee149333c5` | `2ee0a56749ceba72da863fd3496f080ee06f26409daa4e9588fb69ee149333c5` | **MATCH (PASS)** |
| **Phase 8 Session 4** | `runs/phase8/session_4_training_01/weights/best.pt` | `ea53eee94e508bbb81620b47b2a23c9826341b6b5a6981d9371e476cb9d0594f` | `ea53eee94e508bbb81620b47b2a23c9826341b6b5a6981d9371e476cb9d0594f` | **MATCH (PASS)** |

---

## 3. Checkpoint Architectural Metadata

| Property | Production Baseline | Phase 8 Session 2 | Phase 8 Session 4 |
| :--- | :--- | :--- | :--- |
| **Model Architecture** | YOLOv8n (Detection) | YOLOv8n (Detection) | YOLOv8n (Detection) |
| **Parameters** | 3,133,922 | 3,133,922 | 3,133,922 |
| **GFLOPs** | 8.6 | 8.6 | 8.6 |
| **Number of Layers** | 73 (fused) | 73 (fused) | 73 (fused) |
| **Input Resolution** | 640 × 640 | 640 × 640 | 640 × 640 |
| **Classes Configured** | 6 classes (dent, scratch, crack, glass shatter, lamp broken, tire flat) | 6 classes (dent, scratch, crack, glass shatter, lamp broken, tire flat) | 6 classes (dent, scratch, crack, glass shatter, lamp broken, tire flat) |
| **Evaluation Device** | NVIDIA GeForce RTX 3050 Laptop GPU (CUDA:0) | NVIDIA GeForce RTX 3050 Laptop GPU (CUDA:0) | NVIDIA GeForce RTX 3050 Laptop GPU (CUDA:0) |

---

## 4. Integrity Safeguard Compliance

1. **Immutable File Access:** Checkpoint files were accessed in read-only binary mode (`rb`) for SHA-256 calculation and PyTorch model loading (`weights_only=False` under Ultralytics engine).
2. **Zero In-Place Writes:** All benchmark outputs, predictions, evaluation caches, and metrics were directed exclusively into designated isolation folders under `runs/phase8/gate_i_benchmark/`.
3. **Zero Production Promotion:** Production baseline pointer `models/phase5/best.pt` was not updated, replaced, symlinked, or altered.

---

## 5. Certification

I hereby certify that all evaluated model checkpoints remained cryptographically identical before and after benchmark execution, verifying complete adherence to Gate I non-destructive protocols.
