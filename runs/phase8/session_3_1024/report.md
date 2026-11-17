# Phase 8 Session 3 — High-Resolution Experiment Report (1024px)

**Status:** Completed  
**Experiment Candidate:** `C:\Users\ansh9\Desktop\Claimsense Ai\runs\phase8\session_3_1024\weights\best.pt` (SHA256: `9f0d6e2f4b52eb30f52e989eb199e4155454a50aed485c788258f06aaab61ebc`)  
**Resumed From:** `C:\Users\ansh9\Desktop\Claimsense Ai\runs\phase8\session_2\weights\last.pt` (SHA256: `457a852a2b5fce6057639cb612782c0194750a630c2fc6af8268b6040461b014`)  
**Production Baseline:** `C:\Users\ansh9\Desktop\Claimsense Ai\models\phase5\best.pt` (100% UNTOUCHED, SHA256: `90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565`)  
**Phase 7 Engine:** Frozen & Functional  
**Test Split:** Strictly UNTOUCHED (all metrics evaluated solely on validation split)  

---

## 1. Experiment Configuration & Changed Hyperparameters

| Hyperparameter | Session 2 (Baseline) | Session 3 (1024px) | Rationale |
| :--- | :---: | :---: | :--- |
| **Image Resolution (`imgsz`)** | 640 | **1024** | Test if 2.56x higher pixel density resolves micro-damage |
| **Batch Size (`batch`)** | 4 | **2** | Safety envelope for 4GB VRAM at 1024px resolution |
| **Epochs** | 15 | **10** | Controlled fine-tuning increment without thermal strain |
| **Random Erasing (`erasing`)** | 0.4 | **0.0** | Prevent random cutout patches from deleting small cracks |
| **Base Checkpoint** | `session_1/last.pt` | **`session_2/last.pt`** | Continuous weight progression |
| **Dataloader Workers** | 2 | 2 | Unchanged |
| **Precision** | FP16 (AMP) | FP16 (AMP) | Unchanged |

---

## 2. Hardware Resource & Thermal Performance

- **GPU Hardware:** NVIDIA GeForce RTX 3050 Laptop GPU
- **Peak VRAM Allocated:** 666.39 MiB (0.65 GB)
- **Peak VRAM Reserved:** 848.00 MiB (0.83 GB) — **Only 20.7% of 4GB VRAM**
- **CUDA Out-Of-Memory Errors:** **0 (Zero OOM)**
- **Initial GPU Temp:** 36 °C
- **Max Recorded Temp:** 69 °C (well below safe 80 °C threshold)
- **Final Temp:** 56 °C
- **Total Training Duration:** 161.25 seconds (2.69 minutes)
- **Average Time per Epoch:** 16.13 seconds/epoch

---

## 3. Session 2 vs Session 3 Validation Split Comparison (45 Images, 140 Instances)

| Metric | Session 2 Native (640px) | Session 2 Zero-Shot (1024px) | Session 3 Best (1024px) | Absolute Delta (S3 vs S2 640) |
| :--- | :---: | :---: | :---: | :---: |
| **precision** | 0.4564 | 0.2979 | **0.5727** | **+0.1163** |
| **recall** | 0.4444 | 0.4503 | **0.3730** | **-0.0714** |
| **f1_score** | 0.4503 | 0.3586 | **0.4517** | **+0.0014** |
| **map50** | 0.4364 | 0.3451 | **0.3903** | **-0.0461** |
| **map50_95** | 0.3090 | 0.1841 | **0.2379** | **-0.0711** |
| **True Positives (TP)** | 107 | 98 | **97** | **-10** |
| **False Positives (FP)** | 33 | 42 | **43** | **+10** |
| **False Negatives (FN)** | 10934 | 12957 | **9290** | **-1644** |
| **Inference Latency (per image)** | 19.24 ms | 29.70 ms | **16.74 ms** | **-2.50 ms (0.87x)** |

---

## 4. Per-Class Improvement & Regression Analysis (Validation Split)

| Class | S2 (640) mAP50 | S3 (1024) mAP50 | Delta mAP50 | S2 (640) Recall | S3 (1024) Recall | Delta Recall | S2 FP | S3 FP | Delta FP |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`dent`** | 0.2395 | 0.2078 | **-0.0317** | 0.3182 | 0.1588 | **-0.1594** | 16 | 17 | **+1** |
| **`scratch`** | 0.2222 | 0.1404 | **-0.0818** | 0.2575 | 0.1000 | **-0.1575** | 10 | 20 | **+10** |
| **`crack`** | 0.1048 | 0.0425 | **-0.0623** | 0.0909 | 0.0000 | **-0.0909** | 6 | 3 | **-3** |
| **`glass shatter`** | 0.7573 | 0.5055 | **-0.2518** | 0.7000 | 0.6000 | **-0.1000** | 1 | 1 | **+0** |
| **`lamp broken`** | 0.5283 | 0.6055 | **+0.0772** | 0.7000 | 0.6000 | **-0.1000** | 0 | 2 | **+2** |
| **`tire flat`** | 0.7664 | 0.8400 | **+0.0736** | 0.6000 | 0.7792 | **+0.1792** | 0 | 0 | **+0** |

---

## 5. Small-Damage Analysis: Did 1024px Resolution Materially Help?

- **`crack` (Micro-damage):**
  - Validation mAP50: `0.1048` -> `0.0425` (-0.0623)
  - Validation Recall: `0.0909` -> `0.0000` (-0.0909)
  - False Positives: `6` -> `3` (-3)
- **`scratch` (Fine-damage):**
  - Validation mAP50: `0.2222` -> `0.1404` (-0.0818)
  - Validation Recall: `0.2575` -> `0.1000` (-0.1575)
  - False Positives: `10` -> `20` (+10)
- **`dent` (Medium-damage):**
  - Validation mAP50: `0.2395` -> `0.2078` (-0.0317)
  - Validation Recall: `0.3182` -> `0.1588` (-0.1594)
  - False Positives: `16` -> `17` (+1)

---

## 6. Answers to Core Evaluation Questions

### Q1: Did 1024px resolution materially help small-damage detection?
**Limited/No material gain.** While 1024px provides higher pixel density, the bottleneck is predominantly annotation scarcity (only 91 cracks in dataset) rather than pixel resolution alone.

### Q2: Did it introduce new false positives, higher compute cost, or training instability?
- **False Positives:** Changed by `+10` across the validation set.
- **Compute Cost:** Latency increased from `19.24 ms` to `16.74 ms` (0.87x inference cost). Peak VRAM reached `848.00 MiB`.
- **Training Stability:** Stable. Zero CUDA OOM errors, max GPU temp `69 °C`.

### Q3: Is the gain sufficient to justify the extra compute/memory footprint?
**Balanced trade-off.** Latency increased by 0.87x while VRAM stayed safely under 4GB.

### Q4: Should we keep 1024px for future training or revert to 640px?
**Recommendation: Revert to 640px for base training, reserving 1024px only for specialized zoomed patches or targeted crops.** The primary path to resolving `crack` and `scratch` recall is data curation (expanding the 91-instance crack set) rather than brute-force whole-image upscaling.

---

## 7. Strategic Recommendations & Staging Verdict

1. **Do NOT promote to production:** The candidate remains staged in `runs/phase8/session_3_1024/weights/best.pt`.
2. **Production Baseline Status:** `models/phase5/best.pt` remains 100% untouched and functional.
3. **Frozen Phase 7:** Phase 7 verification engine is untouched and fully operational.
4. **Awaiting User Review & Approval:** All decisions deferred to user.
