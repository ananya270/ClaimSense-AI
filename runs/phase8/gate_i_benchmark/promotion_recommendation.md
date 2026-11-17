# ClaimSense AI — Phase 8: Gate I Production Promotion Recommendation

**Document Date:** 2026-11-17  
**Governance Scope:** Gate I Evaluation & Model Promotion Assessment  
**Active Specification:** `acquisition_specification.md` — v1.1-ACTIVE  
**Evaluated Artifacts:**
1. Production Baseline (Phase 5): `models/phase5/best.pt`
2. Phase 8 Session 2: `runs/phase8/session_2/weights/best.pt`
3. Phase 8 Session 4: `runs/phase8/session_4_training_01/weights/best.pt`
**Evaluation Dataset:** `CarDD_Independent_Val_v1` (44 Images, 47 Ground-Truth Instances)

---

## 1. Definitive Recommendation

> [!CAUTION]
> **GOVERNANCE DECISION: REJECT PRODUCTION REPLACEMENT — DO NOT PROMOTE ANY CANDIDATE CHECKPOINT.**  
>
> The Production Baseline (`models/phase5/best.pt`) must remain **unaltered and active** in production. Neither Session 2 nor Session 4 meets the required production reliability criteria for deployment. Furthermore, in strict compliance with Gate I governance directives, this benchmark must be formally categorized as a **44-image independent pilot benchmark**, not final real-world validation.

---

## 2. Comparative Performance Scorecard

| Metric | Production Baseline (Phase 5) | Phase 8 Session 2 | Phase 8 Session 4 | Best Performer |
| :--- | :---: | :---: | :---: | :---: |
| **Empirical Pooled mAP@50** | 0.0016 | 0.0019 | **0.0060** | Phase 8 Session 4 (+275% vs Base) |
| **Empirical Pooled mAP@50:95** | 0.0004 | 0.0003 | **0.0008** | Phase 8 Session 4 (+100% vs Base) |
| **Fixed-Weight Composite mAP@50** | **0.0103** | 0.0019 | 0.0054 | Production Baseline (via Tier 2) |
| **Fixed-Weight Composite mAP@50:95** | **0.0032** | 0.0003 | 0.0007 | Production Baseline (via Tier 2) |
| **Empirical Precision (All)** | 0.1690 | **0.3473** | 0.1894 | Phase 8 Session 2 |
| **Empirical Recall (All)** | **0.2400** | 0.0128 | 0.0256 | Production Baseline |
| **Empirical F1-Score** | **0.1984** | 0.0247 | 0.0452 | Production Baseline |
| **Tier 1 (Walkaround) mAP@50** | 0.0010 | 0.0020 | **0.0063** | Phase 8 Session 4 |
| **Tier 2 (Macro) mAP@50** | **0.0320** | 0.0016 | 0.0033 | Production Baseline |
| **Glass Shatter AP@50** | 0.0015 | 0.0099 | **0.0339** | Phase 8 Session 4 (+2160% vs Base) |
| **Dent AP@50** | **0.0058** | 0.0013 | 0.0009 | Production Baseline |
| **Lamp Broken AP@50** | 0.0000 | 0.0000 | 0.0000 | None (All models failed) |
| **Tire Flat AP@50** | 0.0000 | 0.0000 | 0.0000 | None (All models failed) |
| **Mean Latency (CUDA RTX 3050)** | 131.42 ms | **80.89 ms** | 85.69 ms | Phase 8 Session 2 (-38.4%) |
| **Throughput (FPS)** | 7.6 FPS | **12.4 FPS** | 11.7 FPS | Phase 8 Session 2 (+63.2%) |

---

## 3. Forensic Performance & Failure Mode Analysis

### 3.1 Domain Shift & In-Distribution vs Out-of-Distribution Dynamics
All three evaluated models were trained exclusively on the CarDD dataset (Chinese highway collision imagery captured with specific surveillance/handheld cameras under distinct environmental, lighting, and aspect ratio profiles). 

When tested on the `CarDD_Independent_Val_v1` pilot dataset (composed of high-resolution European and North American multi-angle vehicle inspection imagery and curated Wikimedia Commons incident photographs), **all models experienced severe domain shock**:
1. **Background Proposal Explosion:** Across all 44 evaluation images, each model produced thousands of spurious background proposals (Production Baseline: 6,259 background false-positive proposals on panel surfaces; Session 2: 2,423; Session 4: 2,185). At default detection confidence ($0.001$ for validation evaluation), car reflection highlights, body seams, and wheel rims trigger extensive false alarms.
2. **Severe Recall Degradation in Fine-Tuned Sessions:** While Session 2 and Session 4 succeeded in suppressing noise (increasing precision from 0.169 to 0.347 and reducing inference latency from 131 ms to 81–85 ms), they suffered catastrophic recall collapse on out-of-domain walkaround images (Session 2 recall fell to $1.28\%$, Session 4 fell to $2.56\%$).
3. **Class Blind Spots:** Neither the Production Baseline nor either Phase 8 checkpoint achieved non-zero Average Precision on **Lamp Broken** (0.0000 AP) or **Tire Flat** (0.0000 AP) on independent data. This reveals that the CarDD representations for tire deflation and broken headlamp/taillamp fixtures fail to transfer to standard photographic walkaround angles.

### 3.2 Tier 1 vs Tier 2 Performance Divergence
- **Production Baseline** exhibits strong preference for **Tier 2 Macro crops** ($\text{mAP@50} = 0.0320$, Recall $= 0.3750$), but fails on **Tier 1 Walkaround imagery** ($\text{mAP@50} = 0.0010$). This is because CarDD's native training images predominantly feature close-up framing of severe structural impacts.
- **Phase 8 Session 4** shows the reverse profile: it achieves its highest performance on **Tier 1 Walkarounds** ($\text{mAP@50} = 0.0063$, driven by Glass Shatter $\text{AP@50} = 0.0365$), but suffers on Tier 2 Macro ($\text{mAP@50} = 0.0033$).

### 3.3 Latency & Operational Trade-offs
Both Phase 8 fine-tuned checkpoints demonstrate noticeable speedups on the local NVIDIA RTX 3050 GPU (Session 2: $80.89\text{ ms} / 12.4\text{ FPS}$; Session 4: $85.69\text{ ms} / 11.7\text{ FPS}$) compared to the Production Baseline ($131.42\text{ ms} / 7.6\text{ FPS}$). However, operational latency gains cannot justify replacing production code when model detection recall on real-world damage drops below $3\%$.

---

## 4. Architectural Characterization of Pilot Evaluation

> [!IMPORTANT]
> **Pilot Benchmark Status:**  
> This evaluation of 44 images and 47 instances constitutes an **independent pilot benchmark**. While statistically invaluable for diagnosing cross-domain transferability and establishing rigorous zero-contamination baselines, $N=44$ images cannot serve as the final real-world production certification gate. 
> 
> Under the approved Phase 8 Acquisition Plan, full certification requires scaling the independent dataset across subsequent controlled tranches toward the target scale ($N \ge 200\text{--}250\text{ images}$) with representation across lighting, weather, paint color, and damage severity.

---

## 5. Strategic Roadmap & Next Actions

1. **Maintain Production Baseline:** Retain `models/phase5/best.pt` in `models/` without alteration.
2. **Do Not Deploy Confidence Thresholds:** Withhold deployment of new operating thresholds (`conf_threshold`, `iou_threshold`) to Phase 7 production services until domain-adapted checkpoints are trained.
3. **Domain Adaptation & Synthetic Augmentation:** Checkpoint performance proves that direct transfer without domain alignment is inadequate. Future model iterations must explore:
   - Mosaic / MixUp / Copy-Paste augmentations focused on independent camera perspectives.
   - Contrastive domain adaptation between CarDD and independent walkaround imagery.
4. **Acquisition Scaling:** Proceed with future acquisition planning only upon formal governance authorization.
