# ClaimSense AI — Independent Dataset Model Evaluation Protocol

**Scope:** Head-to-Head Comparative Benchmark of Session 2 vs Session 4 on `CarDD_Independent_Val_v1` (200+ Images)  
**Frozen Candidate Checkpoints:**
1. **Production Baseline:** `models/phase5/best.pt` (SHA-256: `90d489e4...`)
2. **Phase 8 Session 2:** `runs/phase8/session_2/weights/best.pt` (SHA-256: `2ee0a567...`)
3. **Phase 8 Session 4:** `runs/phase8/session_4_training_01/weights/best.pt` (SHA-256: `ea53eee9...`)

---

## 1. Controlled Execution Protocol

All checkpoints will be evaluated using strictly identical inference and environment settings:
- **Hardware Device:** CUDA:0 (NVIDIA GeForce RTX 3050 Laptop GPU, 4.00 GB VRAM)
- **Image Resolution:** $640 \times 640$ (`imgsz=640`)
- **Batch Size:** `batch=4` (with automated fallback to `batch=2` on OOM)
- **Precision:** FP16 (AMP enabled)
- **Evaluator:** Ultralytics YOLO Validator v8.4.215
- **Pre- and Post-Execution Hashes:** Cryptographic SHA-256 verification before and after inference to ensure zero weight modification.

---

## 2. Evaluation Operating Modes

To evaluate both general feature quality and operational deployment readiness, each model will be benchmarked under three distinct evaluation modes:

### Mode 1: Continuous Curve Integration (mAP Mode)
- **Operating Parameters:** Confidence continuum $[0.001, 1.0]$, $IoU \in [0.50, 0.95]$
- **Metrics Extracted:**
  - Overall & Per-Class $mAP@50$
  - Overall & Per-Class $mAP@50-95$
  - Global Curve-Max-F1 Precision, Recall, and F1
- **Purpose:** Evaluates whether Session 4's gains in Dent (+39.9%) and Crack (+358.8%) generalize beyond the CarDD distribution to authentic insurance imagery.

### Mode 2: Fixed Operational Cutoff ($conf = 0.25, IoU = 0.45$)
- **Operating Parameters:** Rigid uniform cutoff $\tau = 0.25$ across all damage classes.
- **Metrics Extracted:**
  - True Positives ($TP$), False Negatives ($FN$)
  - Cross-Class False Positives ($FP_{cross}$)
  - Background False Positives ($FP_{bg}$)
  - Empirical Operational Precision, Recall, and F1
- **Purpose:** Audits real-world behavior under a traditional fixed-threshold deployment.

### Mode 3: Blind Hypothesis Test of Class-Calibrated Thresholds
- **Hypothesis Evaluated:** Testing the advisory class-calibrated operating thresholds derived during the Phase 8 calibration study **without re-tuning**:
  $$\tau_{\text{dent}} = 0.25, \quad \tau_{\text{scratch}} = 0.10, \quad \tau_{\text{crack}} = 0.10, \quad \tau_{\text{glass}} = 0.25, \quad \tau_{\text{lamp}} = 0.25, \quad \tau_{\text{tire}} = 0.35$$
- **Purpose:** Tests whether lowering thresholds for fine-grained classes (scratch and crack) recovers recall on authentic real-world claims without causing an explosion of background false alarms on unobserved imagery.

---

## 3. Standardized Latency & Throughput Benchmarking

- **Warm-Up Phase:** 15 forward passes on dummy tensors on CUDA:0 prior to recording time.
- **Timing Technique:** Dedicated CUDA events (`torch.cuda.Event(enable_timing=True)`) with explicit hardware barrier synchronization (`torch.cuda.synchronize()`) for each of the 200+ images.
- **Metrics Recorded:** Mean latency (ms/img), Median latency (ms/img), 95th percentile latency (ms/img), Minimum/Maximum latency, and Throughput (FPS).

---

## 4. Multi-Metric Human Promotion Decision Framework

Any future promotion of Session 4 or Session 2 to production must be approved through a documented human review board based on the following gates:

```
========================================================================================================
                                 PRODUCTION PROMOTION DECISION GATES
========================================================================================================
Gate ID   Evaluation Metric                 Target Threshold                       Mandatory Gate?
--------------------------------------------------------------------------------------------------------
GATE-1    Checkpoint Hash Integrity         100% Match Pre & Post Eval             YES (Hard Stop)
GATE-2    Production Baseline Delta         Overall mAP@50 > Baseline + 20.0%      YES (Hard Stop)
GATE-3    Hairline Crack Recovery           Crack Recall >= 25.0% (at tested mode) YES (Critical Blindspot)
GATE-4    Dent Localization Quality         Dent mAP@50 >= 30.0%                   YES (Claim Volume)
GATE-5    Scratch Recall Preservation       Scratch Recall >= 20.0%                YES (Core Defect)
GATE-6    Background False Alarm Rate       FP_bg <= 1.5 false alarms / image      YES (Appraiser Trust)
GATE-7    Real-Time Inference Latency       Mean Latency <= 35.0 ms/image          YES (Mobile Sync)
========================================================================================================
```

*Final Sign-Off: Requires joint authorization from Lead ML Engineer, Computer Vision Architect, and Insurance Domain Lead.*
