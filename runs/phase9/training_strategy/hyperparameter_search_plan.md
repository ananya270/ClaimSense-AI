# ClaimSense AI — Phase 9.4: Hyperparameter Search & Optimization Plan

**Document ID:** `REP-PH9-4-HPARAM-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.4 — Training Strategy & Hyperparameter Optimization Planning  
**Search Paradigm:** Staged Sequential Factor Isolation (Anti-Cartesian Design)  
**Status:** SEARCH SPECIFICATION COMPLETE (NO TRAINING AUTHORIZED)  

---

## 1. Search Philosophy & Anti-Cartesian Design

A full Cartesian-product grid search across 10 hyperparameters with 3–4 values each would generate over $2,500$ training permutations. On CPU/local GPU hardware, this would require months of continuous compute.

To eliminate compute waste while maintaining scientific rigor, Phase 9.4 adopts a **Staged Sequential Factor Isolation Plan**:
1. **Stage 1:** Establish a deterministic, reproducible baseline at fixed parameters.
2. **Stage 2:** Vary input resolution independently (640 vs 832 vs 1024) while holding all other factors constant.
3. **Stage 3:** Test crack-oriented augmentation on the winning resolution.
4. **Stage 4:** Test imbalance mitigation (loss weighting vs copy-paste) on the winning augmentation.
5. **Stage 5:** Evaluate optimizer and loss rebalancing.
6. **Stage 6:** Synthesize top factors into a single composite candidate (EXP04).
7. **Stage 7:** Multi-seed verification (3 seeds) to confirm statistical significance.

---

## 2. Structured Hyperparameter Search Specification Table

| Hyperparameter | Current Baseline | Candidate Values | Search Stage | Theoretical Justification | Resource Impact | Primary Risk | Evaluation Metric |
|---|---|---|---|---|---|---|---|
| **Input Resolution (`imgsz`)** | 416 (train) / 640 (infer) | 640, 832, 1024 | Stage 2 | Preserves sub-grid crack pixels; prevents feature vanishing. | Memory: $1.0\times \to 2.6\times$; Epoch time: $45\text{s} \to 150\text{s}$. | Out of memory on large batches; slower inference. | Crack Recall, mAP50, Latency |
| **Batch Size (`batch`)** | 16 | 4, 8, 16 | Stage 2 | Matched to available RAM/VRAM at higher resolutions. | Lower batch = lower memory footprint. | Small batch gradients can be noisy without gradient accumulation. | Gradient Stability |
| **Initial Learning Rate (`lr0`)** | 0.01 | 0.0003, 0.001, 0.005 | Stage 5 | Lower LR prevents destroying pre-trained feature detectors. | Negligible | Too low = premature plateau; too high = loss divergence. | Loss Convergence Curve |
| **Optimizer** | SGD (momentum 0.937) | SGD, AdamW | Stage 5 | AdamW handles sparse gradient updates on rare classes better. | $+10\%$ RAM for second-order moment tracking. | May overfit faster if weight decay is too low. | Validation Loss, Macro-F1 |
| **Weight Decay** | 0.0005 | 0.0001, 0.0005, 0.001 | Stage 5 | Regularizes higher-capacity models at high resolution. | Negligible | High decay suppresses faint crack edge weights. | Validation Generalization Gap |
| **Epoch Horizon (`epochs`)** | 5 | 30, 50 (Patience: 15) | Stage 1 | Allows full convergence; 5 epochs was severely undertrained. | Linear increase in total training runtime. | Overfitting beyond 30 epochs on small dataset. | Early Stopping Trigger Epoch |
| **Class Loss Weight (`cls`)** | 0.5 | 0.5, 1.0, 1.5 | Stage 5 | Penalizes scratch vs crack misclassification $3\times$ more. | Negligible | Too high may increase false alarms on background. | Scratch vs Crack Confusion Rate |
| **Crack Class Weight ($\alpha_{\text{crack}}$)** | 1.0 (unweighted) | 1.0, 2.0, 2.8, 3.5 | Stage 4 | Directly offsets the $2.84:1$ instance deficit. | Negligible | $\alpha > 3.5$ triggers hallucinated crack predictions. | Crack Precision vs Recall Trade-off |
| **Rare-Class Copy-Paste** | 0.0 | 0.0, 0.15, 0.30 | Stage 3 | Multiplies crack instances without distorting background. | Negligible | Unrealistic edge artifacts if blending is poor. | Crack TP on Validation Set |
| **Random Seeds** | 0 | 42, 123, 999 | Stage 7 | Verifies that gains are statistically robust, not seed luck. | $3\times$ runtime for winning configuration. | None | Metric Variance ($\sigma < 0.015$) |

---

## 3. Early Stopping & Convergence Criteria

To prevent wasting compute:
- **Patience:** Set to **15 epochs** without improvement in validation Macro-F1.
- **Minimum Epochs:** Every run must complete at least **15 epochs** to bypass learning-rate warmup and initial mosaic adaptation.
- **Divergence Guardrail:** If validation loss increases continuously for 5 consecutive epochs after epoch 10, abort run immediately.
