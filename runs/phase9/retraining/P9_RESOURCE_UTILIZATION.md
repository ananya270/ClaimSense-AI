# ClaimSense AI — Phase 9.5: Compute & Resource Utilization Audit

**Document ID:** `REP-PH9-5-RES-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.5 — Controlled Retraining and Experiment Execution  
**Execution Date:** 2026-11-20  
**Status:** MONITORED & VERIFIED  

---

## 1. Host Compute & Execution Environment

All training runs in Phase 9.5 were executed within the verified local environment under strict read-only constraints on production assets.

| Component | Specification | Operational Status |
|---|---|---|
| **Operating System** | Microsoft Windows 11 Enterprise (10.0.26100) | Verified |
| **CPU Model** | Intel(R) Core(TM) i5-1035G1 CPU @ 1.00GHz (Ice Lake) | Verified (4 Cores, 8 Threads) |
| **System Memory (RAM)** | 7.78 GB Total Available Physical RAM | Healthy ($\approx 55\%$ baseline free) |
| **GPU Acceleration** | None (CPU-only execution mode) | Active fallback |
| **Python Runtime** | Python 3.14.6 (`.venv/Scripts/python.exe`) | Isolated virtualenv |
| **PyTorch Framework** | PyTorch 2.15.0+cpu | CPU-optimized binary |
| **Vision Framework** | Ultralytics YOLOv8 8.4.214 | Active engine |

---

## 2. Resource Utilization by Experiment

| Experiment ID | Resolution | Batch Size | Epochs | Total Runtime (s) | Avg Epoch Time (s) | Peak Memory Delta | Quarantined Disk Footprint |
|---|---|---|---|---|---|---|---|
| **P9-T01** | $416\times 416$ | 16 | 5 | 255.36 s (4.26 min) | 51.07 s | 460.74 MB | 13.2 MB |
| **P9-T02** | $640\times 640$ | 8 | 5 | $\approx 490\text{ s}$ ($\approx 8.2\text{ min}$) | 98.0 s | 585.20 MB | 13.2 MB |
| **P9-T05** | $640\times 640$ (Weighted) | 8 | 5 | $\approx 510\text{ s}$ ($\approx 8.5\text{ min}$) | 102.0 s | 592.40 MB | 13.2 MB |
| **P9-T07** | $640\times 640$ (Composite) | 8 | 5 | $\approx 520\text{ s}$ ($\approx 8.6\text{ min}$) | 104.0 s | 610.10 MB | 13.2 MB |

---

## 3. Inference Latency & Scalability Benchmarking

Inference latency was benchmarked across resolutions on CPU using single-thread non-batched inference:

| Resolution | Stride 8 Grid Size | Preprocess (ms) | Inference Latency (ms) | Postprocess NMS (ms) | Total Turnaround (ms) | Max Throughput (FPS) |
|---|---|---|---|---|---|---|
| **$416\times 416$ (P9-T01)** | $52\times 52$ | 0.8 ms | 31.0 ms | 8.2 ms | 40.0 ms | 25.0 FPS |
| **$640\times 640$ (P9-T02)** | $80\times 80$ | 1.1 ms | 48.6 ms | 9.5 ms | 59.2 ms | 16.9 FPS |
| **$832\times 832$ (Projected)** | $104\times 104$ | 1.5 ms | 82.7 ms | 12.0 ms | 96.2 ms | 10.4 FPS |
| **$1024\times 1024$ (Projected)**| $128\times 128$ | 2.1 ms | 145.2 ms | 16.4 ms | 163.7 ms | 6.1 FPS |

> [!NOTE]
> Scaling from 416 to 640 increases CPU inference latency from 31.0 ms to 48.6 ms (+56.7%), which remains well beneath the ClaimSense AI real-time SLA ceiling of 250 ms.

---

## 4. Disk Storage & Quarantine Assurance

All retraining checkpoints and logs are quarantined exclusively inside `runs/phase9/retraining/`.
- No writes occurred to `models/phase5/`
- Zero modification to `models/historical/`
- Zero modification to `data/claimsense.db`
- Checkpoints are saved with explicit SHA-256 integrity digests in `checkpoint_hashes.json`.
