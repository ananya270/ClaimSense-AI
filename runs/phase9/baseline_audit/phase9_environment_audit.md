# ClaimSense AI — Phase 9.0: Environment & Hardware Audit

**Document ID:** `AUD-PH9-ENV-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.0 — Baseline Audit  
**Date:** 2026-11-19  
**Governing Standard:** `acquisition_specification.md` v1.1-ACTIVE  
**Execution Mode:** STRICTLY READ-ONLY AUDIT. ZERO RETRAINING, ZERO INFERENCE.

---

## 1. Executive Summary

This environment audit establishes the technical runtime profile of the host machine prior to commencing Phase 9 model optimization experiments. All system parameters, framework versions, compute devices, and storage constraints were inspected directly in the active execution workspace (`c:\Users\ydvan\Desktop\ClaimSense Ai\ClaimSense-AI`).

---

## 2. Software Runtime Profile

| Parameter | Inspected Value | Audit Status |
| :--- | :--- | :---: |
| **Python Version** | `3.14.6` (tags/v3.14.6:c63aec6, Jun 10 2026, 10:26:10) [MSC v.1944 64 bit (AMD64)] | Certified |
| **Operating System** | Windows 11 Enterprise / Pro (`Windows-11-10.0.26300-SP0`) | Certified |
| **PyTorch Version** | `2.15.0+cpu` | **CPU Build Detected** |
| **Ultralytics Version** | `8.4.214` | Certified |
| **CUDA Available (PyTorch)** | `False` (`torch.cuda.is_available() == False`) | **Hardware / Driver Boundary** |
| **OpenCV (cv2)** | Active (Used for structural damage filtering & heuristic heuristics) | Certified |
| **Pillow (PIL)** | Active (`PIL.Image` supporting JPEG/PNG/WebP image processing) | Certified |
| **PyMuPDF (fitz)** | Active (`fitz` 1.25.x / `pymupdf` supporting claim evidence extraction) | Certified |
| **SQLAlchemy** | `2.0.44` (SQLite backend with foreign keys & WAL telemetry) | Certified |
| **Flask** | `3.1.2` (Authoritative claim submission & inspection server) | Certified |

---

## 3. Compute & Acceleration Constraints

1. **Active Environment Acceleration:**
   The active Python virtual environment (`.venv`) is configured with a CPU-only binary distribution of PyTorch (`torch-2.15.0+cpu`). GPU acceleration via CUDA is currently not available within this active interpreter.
2. **Historical Training Hardware Context:**
   Historical training records from Phase 8 (Session 1, Session 2, Session 3, Session 4, and EXP01–EXP03) were executed on a dedicated GPU host:
   - GPU Model: `NVIDIA GeForce RTX 3050 Laptop GPU`
   - Dedicated VRAM: `4096 MB` (4.00 GB)
   - Host Architecture: Windows x86_64, CUDA 12.x / PyTorch cu121
3. **Implications for Phase 9 Optimization:**
   - **Offline Evaluation & Validation:** The CPU runtime is fully capable of running single-image validation passes, benchmark scoring, metric reconciliation, and dataset audits.
   - **Model Training (Phase 9.1+):** Conducting multi-epoch YOLOv8 training on CPU will result in elevated training latency (~15–20 minutes per epoch at 640x640 on CarDD subsets).
   - **Operational Action Item:** Before initiating Phase 9.1 training, the engineering team must determine whether to install CUDA-enabled PyTorch (`torch torchvision --index-url https://download.pytorch.org/whl/cu121`) if a compatible NVIDIA GPU is physically present on the host, or establish strict CPU batching constraints (e.g., `batch=4`, `imgsz=416` or `640`, frozen backbone).

---

## 4. Storage & Filesystem Capacity

| Metric | Measured Value | Availability Status |
| :--- | :--- | :---: |
| **Workspace Drive** | `C:\` (Local NVMe/SSD Storage) | Healthy |
| **Total Disk Capacity** | `293.74 GB` | Adequate |
| **Disk Space Consumed** | `181.86 GB` | Adequate |
| **Free Storage Available** | **`111.88 GB` (38.1% free)** | **Abundant headroom** |

*Storage Evaluation:* With `111.88 GB` of free disk space, the repository possesses more than sufficient storage for training artifacts, YOLO cache files, checkpoint snapshots, tensorboard logs, and audit reports without risk of disk exhaustion.

---

## 5. Environment Readiness Certification

* **Read-Only Baseline Status:** **CERTIFIED READY FOR AUDIT.**
* **Training Hardware Readiness:** **BLOCKED PENDING COMPUTE ENABLING / CONFIGURATION DECISION.** Full training must not be launched until acceleration options are selected.
