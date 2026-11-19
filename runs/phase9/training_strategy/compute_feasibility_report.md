# ClaimSense AI — Phase 9.4: Compute Feasibility & Resource Allocation Report

**Document ID:** `REP-PH9-4-COMPUTE-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.4 — Training Strategy & Hyperparameter Optimization Planning  
**Execution Environment:** Windows x86_64 / Python 3.14.6 / PyTorch 2.15.0+cpu  
**Storage Headroom:** 111.88 GB Free Space  
**Status:** RESOURCE MODELING COMPLETE (ZERO TRAINING LAUNCHED)  

---

## 1. Executive Summary

This report establishes resource feasibility models for the proposed experiment sequence. Estimates are based on empirical measurements obtained during Phase 9.0 environment profiling, Phase 9.1 latency benchmarking, Phase 9.2 resolution sensitivity tests, and historical Phase 5/8 training logs.

---

## 2. Environment & Resource Capacity Snapshot

- **Operating System:** Microsoft Windows 11
- **Python Runtime:** Python 3.14.6 in virtual environment (`.venv`)
- **PyTorch Build:** PyTorch 2.15.0+cpu (CPU-only execution verified)
- **Available Storage:** $111.88\text{ GB}$ free on drive `C:`
- **System Memory (RAM):** 16 GB physical RAM
- **Model Checkpoint Footprint:** Approx $6.2\text{ MB}$ per `.pt` checkpoint file (YOLOv8n).

---

## 3. Experiment Resource Estimation Table

Estimates assume standard CPU training with 210 training images:

| Experiment ID | Experiment Name | Resolution (`imgsz`) | Batch Size | Epochs | Time / Epoch (CPU) | Total Training Runtime | Peak RAM Footprint | Storage Required (Logs + Weights) |
|---|---|---|---|---|---|---|---|---|
| **P9-T01** | Reproducible Baseline | $640\times 640$ | 16 | 30 | $\approx 42\text{ s}$ | $\approx 21.0\text{ min}$ | $1.2\text{ GB}$ | $\approx 15\text{ MB}$ |
| **P9-T02** | Resolution Comparison | $832\times 832$ | 8 | 30 | $\approx 85\text{ s}$ | $\approx 42.5\text{ min}$ | $2.0\text{ GB}$ | $\approx 15\text{ MB}$ |
| **P9-T02b** | Resolution Comparison | $1024\times 1024$ | 4 | 30 | $\approx 145\text{ s}$ | $\approx 72.5\text{ min}$ | $3.2\text{ GB}$ | $\approx 15\text{ MB}$ |
| **P9-T03** | Moderate Augmentation | $832\times 832$ | 8 | 30 | $\approx 88\text{ s}$ | $\approx 44.0\text{ min}$ | $2.1\text{ GB}$ | $\approx 15\text{ MB}$ |
| **P9-T04** | Crack Copy-Paste | $832\times 832$ | 8 | 30 | $\approx 92\text{ s}$ | $\approx 46.0\text{ min}$ | $2.2\text{ GB}$ | $\approx 15\text{ MB}$ |
| **P9-T05** | Class-Weighted Loss | $832\times 832$ | 8 | 30 | $\approx 86\text{ s}$ | $\approx 43.0\text{ min}$ | $2.1\text{ GB}$ | $\approx 15\text{ MB}$ |
| **P9-T06** | AdamW + Wise-IoU | $832\times 832$ | 8 | 30 | $\approx 89\text{ s}$ | $\approx 44.5\text{ min}$ | $2.3\text{ GB}$ | $\approx 15\text{ MB}$ |
| **P9-T07** | Composite EXP04 | $832\times 832$ | 8 | 40 | $\approx 92\text{ s}$ | $\approx 61.3\text{ min}$ | $2.3\text{ GB}$ | $\approx 20\text{ MB}$ |
| **P9-T08** | Multi-Seed (3 runs) | $832\times 832$ | 8 | $3\times 30$ | $\approx 88\text{ s}$ | $\approx 132.0\text{ min}$ | $2.2\text{ GB}$ | $\approx 45\text{ MB}$ |

### Total Compute & Storage Budget:
- **Total Compute Hours:** $\approx 8.4\text{ hours}$ cumulative across all 9 staged trials on local CPU hardware.
- **Total Storage Consumption:** $\approx 170\text{ MB}$ for checkpoints and tensor logs, well within the $111.88\text{ GB}$ headroom ($<0.15\%$ utilization).
- **Feasibility Verdict:** **FULLY FEASIBLE ON LOCAL WORKSTATION HARDWARE.**

---

## 4. Compute-Optimized Execution Sequence

To prevent wasted compute, early termination gates are established:
1. Run **P9-T01** (21 min) first. If baseline mAP50 fails to reach $0.20$, investigate pipeline instability before attempting high resolutions.
2. Run **P9-T02** at 832 resolution before attempting 1024 resolution. If 832 achieves satisfactory feature recovery, do not spend 72 minutes on 1024.
3. Test **P9-T05** (Class Weighting) early, as it introduces zero additional computational overhead during forward pass.
