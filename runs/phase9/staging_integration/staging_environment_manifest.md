# ClaimSense AI — Phase 9.9: Staging Environment Manifest

**Project:** ClaimSense AI  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.9 — Controlled Candidate Integration & Compatibility Verification  
**Governance State:** Category A: RETAIN EXISTING PRODUCTION MODEL (Read-Only Staging Mode)  
**Execution Timestamp:** 2026-11-20T00:35:00+05:30  
**Host Environment:** Windows 11 (AMD64)

---

## 1. Executive Summary & Governance Directive

Per the authoritative decision rendered in **Phase 9.8 (Final Model Selection, Approval & Sign-off)**, Candidate Checkpoint `P9-T02` was designated as **Category A: RETAIN EXISTING PRODUCTION MODEL**. Although `P9-T02` demonstrated higher precision and mAP50 (+35.8%), it failed the zero-tolerance structural crack detection criteria (0.0000% operational recall at confidence threshold $\tau=0.25$, detecting 0 of 13 independent benchmark cracks) and suffered operational recall regressions across dents, scratches, lamps, and tires.

In strict compliance with Phase 9.9 protocol:
- **No model replacement** has occurred.
- **No production database modification** has occurred.
- **No production service endpoints** have been reconfigured.
- This phase executes exclusively as a **read-only staging compatibility verification** to empirically evaluate candidate integration ergonomics, singleton isolation, API contract parity, and regression stability in an isolated staging construct.

---

## 2. System Runtime Environment Specifications

The staging verification was performed in an isolated execution harness within the repository workspace, leveraging the active Python virtual environment:

| Component | Specification | Verification Method |
| :--- | :--- | :--- |
| **Operating System** | Windows 11 Pro 64-bit (10.0.26100) | `sys.platform`, OS Environment |
| **Python Runtime** | Python 3.14.6 (`MSC v.1944 64 bit (AMD64)`) | `sys.version` |
| **Deep Learning Framework** | PyTorch 2.15.0+cpu | `torch.__version__` |
| **Computer Vision Engine** | Torchvision 0.29.2+cpu | `torchvision.__version__` |
| **Object Detection Framework**| Ultralytics YOLOv8 8.4.214 | `ultralytics.__version__` |
| **Hardware Compute Mode** | CPU (x86_64, Multithreaded) | `torch.cuda.is_available() == False` |
| **Traditional CV Fallback** | OpenCV (`cv2`) 4.10.0 / 4.12.0 | `cv2.__version__` |
| **Backend Web Framework** | Flask 3.1.x / SQLAlchemy 2.0.x | Application dependency graph |

---

## 3. Checkpoint Manifest & Cryptographic Integrity

Both the authoritative production model and the experimental candidate model were cryptographically verified using SHA-256 before initiating staging tests:

```
+----------------------------------------------------------------------------------------------------+
| Model Identification & Hash Verification                                                           |
+----------------------------------------------------------------------------------------------------+
| 1. Authoritative Production Model (Phase 5 Baseline):                                              |
|    Path:           c:/Users/ydvan/Desktop/ClaimSense Ai/ClaimSense-AI/models/phase5/best.pt        |
|    Filesize:       6,472,810 bytes (6.17 MB)                                                       |
|    SHA-256 Hash:   49630ae8d5c0066d0532a2a38efede809920a6fccd3eed59a76eb3b65f009390               |
|    Last Modified:  2026-11-16 09:08:07                                                             |
|    Status:         ACTIVE PRODUCTION SINGLETON (PROTECTED, IMMUTABLE)                              |
|                                                                                                    |
| 2. Candidate Model (Phase 9.5 Run T02 - High Resolution 640x640):                                  |
|    Path:           c:/Users/ydvan/Desktop/ClaimSense Ai/ClaimSense-AI/runs/phase9/retraining/      |
|                    P9-T02/checkpoints/best.pt                                                      |
|    Filesize:       6,503,658 bytes (6.20 MB)                                                       |
|    SHA-256 Hash:   91a943a9a246a0748d6f8f07a0b0860ad5872c3f229ab2f69930bb37db6ca721               |
|    Last Modified:  2026-11-19 22:45:10                                                             |
|    Status:         REJECTED FOR PROMOTION — STAGING COMPATIBILITY BENCHMARK ONLY                   |
|                                                                                                    |
| 3. Upstream Pretrained Checkpoint:                                                                 |
|    Path:           c:/Users/ydvan/Desktop/ClaimSense Ai/ClaimSense-AI/yolov8n.pt                   |
|    SHA-256 Hash:   f59b3d833e2ff32e194b5bb8e08d211dc7c5bdf144b90d2c8412c47ccfc83b36               |
+----------------------------------------------------------------------------------------------------+
```

---

## 4. Staging Isolation Architecture

To ensure zero risk to operational assets, the following isolation boundaries were strictly maintained:

1. **Singleton & Memory Isolation**:
   - `VehicleDamageDetector.get_instance()` was audited. When invoked with a custom candidate path, the detector automatically detects path divergence from the initialized production singleton, logs an explicit architectural warning, and instantiates an isolated detached object while preserving `cls._instance` pointing to `models/phase5/best.pt`.
2. **Database Isolation**:
   - Production Database: `data/claimsense.db` (462,848 bytes, mtime: `2026-11-19 22:11:49`).
   - Staging & Test Execution: All tests utilized ephemeral in-memory or temporary SQLite instances (e.g. `sqlite:///:memory:` or `AppData/Local/Temp/tmp.../test_phase5.db`), strictly preventing writes to `data/claimsense.db`.
3. **Daemon & Network Isolation**:
   - The production server process (Task `task-694`, running on `127.0.0.1:5001`) remained active, uninterrupted, and isolated from staging test commands.
4. **Filesystem Boundaries**:
   - Production asset upload directories (`uploads/`) and report storage (`reports/`) remained untouched.
   - All Phase 9.9 verification artifacts are strictly confined to `runs/phase9/staging_integration/` and transient scratch paths.
