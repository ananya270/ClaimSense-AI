# ClaimSense AI — Phase 9.4: Experiment Matrix & Experimental Specifications

**Document ID:** `REP-PH9-4-MATRIX-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.4 — Training Strategy & Hyperparameter Optimization Planning  
**Status:** PROPOSED EXPERIMENT MATRIX COMPLETE (STRICTLY PLANNING ONLY — NO EXECUTION)  

---

## 1. Overview of Proposed Experiment Sequence

The proposed experiment suite consists of eight staged trials (`P9-T01` through `P9-T08`). Each experiment isolates a single engineering dimension before combining winning factors into the final candidate configuration.

```
+-------------------------------------------------------------------------------------------------+
| EXPERIMENT DEPENDENCY GRAPH                                                                     |
+-------------------------------------------------------------------------------------------------+
|                                                                                                 |
|   [P9-T01: Reproducible Baseline] (Resolution 640, 30 epochs, fixed seed)                       |
|          |                                                                                      |
|          +---> [P9-T02: Resolution Isolation] (640 vs 832 vs 1024)                              |
|          |            |                                                                         |
|          +------------+---> [P9-T03: Moderate Augmentation] (HSV, Flip, Light Rot)              |
|          |                         |                                                            |
|          +-------------------------+---> [P9-T04: Crack-Biased Copy-Paste Augmentation]         |
|          |                                      |                                               |
|          +--------------------------------------+---> [P9-T05: Class-Weighted Loss (alpha=2.8)] |
|          |                                                   |                                  |
|          +---------------------------------------------------+---> [P9-T06: Optimizer & Loss]   |
|                                                                          |                      |
|   [P9-T07: Composite Candidate EXP04] <----------------------------------+                      |
|          |                                                                                      |
|          v                                                                                      |
|   [P9-T08: Multi-Seed Statistical Ratification] (Seeds: 42, 123, 999)                          |
+-------------------------------------------------------------------------------------------------+
```

---

## 2. Detailed Experiment Specifications

### Experiment P9-T01: Reproducible Baseline
- **Hypothesis:** Extending training from 5 epochs to 30 epochs at matched resolution ($640\times 640$) with deterministic seeds will improve overall mAP50 by $\ge 3\%$ and reduce false positives without degrading precision.
- **Independent Variable:** Epochs ($5 \to 30$), input resolution ($416 \to 640$).
- **Controlled Variables:** Model (`yolov8n.pt`), dataset (`CarDD_300`), optimizer (SGD), LR0 ($0.01$), loss weights (`7.5 / 0.5 / 1.5`), seed (42).
- **Dataset Split:** `CarDD_300` train (210), val (45), test (45).
- **Evaluation Metrics:** Overall mAP50, mAP50-95, Macro-F1, operational recall at $\tau=0.25$.
- **Expected Resources:** CPU training: $\approx 22\text{ min}$; Peak RAM: $1.2\text{ GB}$.
- **Success Criteria:** Validation $\text{mAP50} \ge 0.220$ (baseline: $0.1932$); zero NaN losses.
- **Failure Criteria:** Validation loss divergence; $\text{mAP50} < 0.180$.
- **Dependencies:** None (Baseline Anchor).

---

### Experiment P9-T02: Resolution Comparison (640 vs 832 vs 1024)
- **Hypothesis:** Training at higher spatial resolution ($832\times 832$ and $1024\times 1024$) will preserve sub-grid crack features, increasing crack feature activations without reducing overall detection recall.
- **Independent Variable:** `imgsz` ($640$, $832$, $1024$).
- **Controlled Variables:** Epochs (30), batch size (adjusted: 16 at 640, 8 at 832, 4 at 1024), seed (42), loss weights.
- **Evaluation Metrics:** Crack validation recall, overall mAP50, training time per epoch, inference latency.
- **Expected Resources:** 1024 resolution: $\approx 75\text{ min}$ on CPU; Peak RAM: $3.2\text{ GB}$.
- **Success Criteria:** Crack validation proposals formed ($\ge 2$ true positives at $\tau=0.10$); overall mAP50 $\ge 0.230$.
- **Failure Criteria:** Out-of-memory error; latency $>250\text{ ms}$.
- **Dependencies:** P9-T01.

---

### Experiment P9-T03: Moderate General Augmentation
- **Hypothesis:** Moderate rotational invariance ($\pm 10^\circ$) and photometric jitter (`hsv_v: 0.3`, `hsv_s: 0.5`) will improve model robustness to lighting variations without destroying fine linear features.
- **Independent Variable:** Augmentation hyperparameter set.
- **Controlled Variables:** Best resolution from P9-T02, epochs (30), optimizer, seed (42).
- **Success Criteria:** Val mAP50 improvement of $\ge 1.5\%$ over P9-T02; lower validation loss gap.
- **Failure Criteria:** Degradation of small-object recall (glass shatter or lamp broken).
- **Dependencies:** P9-T02.

---

### Experiment P9-T04: Crack-Oriented Copy-Paste Augmentation
- **Hypothesis:** Injecting segmented crack lesions onto clean panels via Copy-Paste ($0.30$ probability) will artificially increase crack exposure by $3\times$, breaking classification head suppression.
- **Independent Variable:** `copy_paste: 0.30` specifically targeting crack masks.
- **Controlled Variables:** P9-T03 configuration.
- **Success Criteria:** Crack validation recall $\ge 15.0\%$ at $\tau=0.25$; overall recall $\ge 20.0\%$.
- **Failure Criteria:** Bounding-box edge artifacts; false-positive explosion on panel seams.
- **Dependencies:** P9-T03.

---

### Experiment P9-T05: Class-Weighted Classification Loss
- **Hypothesis:** Applying an explicit weighting factor $\alpha_{\text{crack}} = 2.8\times$ in classification focal loss will counterbalance the $2.84:1$ instance deficit and eliminate scratch-versus-crack misclassification.
- **Independent Variable:** Class loss weights (`alpha_crack: 2.8`, others: 1.0).
- **Controlled Variables:** P9-T04 configuration.
- **Success Criteria:** Crack-to-scratch confusion rate reduced from $46.2\%$ to $<15\%$; crack operational recall $\ge 25.0\%$.
- **Failure Criteria:** Crack false positives increase by $>5.0\text{ FP/image}$ on clean vehicle walkarounds.
- **Dependencies:** P9-T04.

---

### Experiment P9-T06: Optimizer & Loss Formulation (AdamW + Wise-IoU)
- **Hypothesis:** Switching to AdamW (`lr0: 0.001`, `weight_decay: 0.0005`) and elevating classification loss weight (`cls: 1.5`, `box: 7.5`) will accelerate convergence on rare classes and stabilize regression on high-aspect-ratio slender cracks.
- **Independent Variable:** Optimizer (AdamW), `cls: 1.5`.
- **Controlled Variables:** Best settings from P9-T05.
- **Success Criteria:** Faster loss convergence (within 20 epochs); stable box regression for aspect ratios $>6:1$.
- **Failure Criteria:** Loss instability or early plateau.
- **Dependencies:** P9-T05.

---

### Experiment P9-T07: Composite Candidate Model (EXP04 Candidate)
- **Hypothesis:** Combining the winning resolution, crack-oriented copy-paste, class-weighted loss, and AdamW optimizer on the cleaned dataset (scratch-crack overlaps removed + 78 vetted cracks ingested) will achieve $\ge 35.0\%$ crack recall while raising overall mAP50 to $\ge 0.280$.
- **Independent Variable:** Full optimized configuration on expanded training set.
- **Evaluation Metrics:** Track A (mAP50, mAP50-95), Track B ($\tau=0.25$, $\text{IoU}\ge 0.40$), Gate O benchmark, Gate P cohort.
- **Success Criteria:** Crack operational recall $\ge 30.0\%$ (breaking the $0.0\%$ historical ceiling); overall recall $\ge 25.0\%$; false positives $\le 2.5\text{ FP/img}$.
- **Dependencies:** P9-T01 through P9-T06.

---

### Experiment P9-T08: Multi-Seed Statistical Confirmation
- **Hypothesis:** The performance gains of P9-T07 are deterministic and reproducible across multiple random initializations.
- **Independent Variable:** Random seeds (`42`, `123`, `999`).
- **Controlled Variables:** Identical P9-T07 configuration.
- **Success Criteria:** Inter-run variance $\sigma(\text{mAP50}) < 0.015$; crack recall remains $>25\%$ across all three seeds.
- **Dependencies:** P9-T07.
