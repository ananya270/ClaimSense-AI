# ClaimSense AI — Phase 8: Gate N Training Integrity & Forensic Log

**Document ID:** `LOG-PH8-GATE-N-INTEG-001`  
**Execution Date:** 2026-11-17  
**Host Architecture:** Windows x86_64, CUDA 12.8, PyTorch 2.11.0+cu128  
**Compute Accelerator:** NVIDIA GeForce RTX 3050 Laptop GPU (4096 MiB VRAM)  
**Governing Gate:** Gate N (Controlled Domain Adaptation Experiments)

---

## 1. Checkpoint Provenance & Cryptographic Audit

Every checkpoint utilized and produced during Gate N was cryptographically snapshotted:

| Experiment / Checkpoint | File Path | File Size | SHA-256 Checksum |
| :--- | :--- | :---: | :--- |
| **Session 4 Initializer** | `runs/phase8/session_4_training_01/weights/best.pt` | 6.25 MB | `ea53eee94e508bbb81620b47b2a23c9826341b6b5a6981d9371e476cb9d0594f` |
| **EXP01 Best Checkpoint** | `c:\Users\ansh9\Desktop\Claimsense Ai\runs\phase8\domain_adaptation\exp01_negative_mining\weights\best.pt` | 6.25 MB | `3ebd2a5c6ed2ca0aa58601d31c7918b95f5a2436fdab5ba34fd214dded366dc1` |
| **EXP01 Last Checkpoint** | `c:\Users\ansh9\Desktop\Claimsense Ai\runs\phase8\domain_adaptation\exp01_negative_mining\weights\last.pt` | 6.25 MB | `487740108aea4d541ea4d043c51a76dccb6aedbb4b2f84436074de6b1dba1215` |
| **EXP02 Best Checkpoint** | `c:\Users\ansh9\Desktop\Claimsense Ai\runs\phase8\domain_adaptation\exp02_rare_class\weights\best.pt` | 6.25 MB | `68e2b58ec7759427808621debc9a8d725a9e4c1fbc57a2102cd239a8ca14f006` |
| **EXP02 Last Checkpoint** | `c:\Users\ansh9\Desktop\Claimsense Ai\runs\phase8\domain_adaptation\exp02_rare_class\weights\last.pt` | 6.25 MB | `bea2a8dc59788235b332f030c96ec06594b3f02b66df9270ad925dd82f0fcb2f` |
| **EXP03 Best Checkpoint** | `c:\Users\ansh9\Desktop\Claimsense Ai\runs\phase8\domain_adaptation\exp03_unified_multiscale\weights\best.pt` | 6.25 MB | `550fa1c01b9f401f190658b7499ae4f442d9afdf93c72b2c4df00e369f815f01` |
| **EXP03 Last Checkpoint** | `c:\Users\ansh9\Desktop\Claimsense Ai\runs\phase8\domain_adaptation\exp03_unified_multiscale\weights\last.pt` | 6.25 MB | `457ba42401acb84c2554b951cf9e9c0b352d468a000d883dff44da532431f9d5` |

---

## 2. Hardware Resource & Thermal Telemetry

| Run | Duration | VRAM Pre-Run | VRAM Peak/Post | GPU Device | Determinism |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **EXP01 (Negative Mining)** | 107.76s | 218.0 MB | 206.0 MB | NVIDIA GeForce RTX 3050 Laptop GPU | Seed=42, deterministic=True |
| **EXP02 (Rare Class)** | 140.44s | 310.0 MB | 202.0 MB | NVIDIA GeForce RTX 3050 Laptop GPU | Seed=42, deterministic=True |
| **EXP03 (Multi-Scale)** | 290.19s | 326.0 MB | 204.0 MB | NVIDIA GeForce RTX 3050 Laptop GPU | Seed=42, deterministic=True |

---

## 3. Strict Boundary Verification
1. **Production Checkpoint Invariance:** `models/phase5/best.pt` remained untouched and read-only.
2. **Benchmark Isolation:** The frozen 44-image validation benchmark (`datasets/CarDD_Independent_Val_v1/`) was NEVER accessed, loaded, or evaluated during Gate N.
3. **Selection Exclusivity:** Checkpoint qualification and winner selection were derived 100% from `data/da_dev.yaml` (30 images).
