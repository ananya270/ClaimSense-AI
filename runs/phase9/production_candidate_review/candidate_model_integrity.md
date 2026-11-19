# ClaimSense AI — Phase 9.7: Best Candidate Model Integrity & Provenance Audit

**Document ID:** `AUD-PH9-7-CAND-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.7 — Production Model vs Candidate Comparative Analysis & Promotion Readiness Review  
**Execution Date:** 2026-11-20  
**Status:** CANDIDATE ASSET AUDITED & STRICTLY QUARANTINED  

---

## 1. Candidate Identification & Selection Rationale

Among all experimental trials conducted in Phase 9.5 (`P9-T01` through `P9-T08`), **Experiment P9-T02** was determined to be the strongest eligible candidate based on verified empirical evidence:

1. **Highest Global Ranking on Validation Split:** Achieved validation mAP@50 of **0.3093** (vs 0.2732 baseline and 0.2714 production reference).
2. **Superior Performance on Held-Out Test Benchmark:** Achieved independent test mAP@50 of **0.2490** (vs 0.1833 production baseline, $+35.8\%$ relative gain).
3. **Sub-Threshold Crack Feature Activation:** Demonstrated the highest continuous crack representation of any trained model, with Crack AP@50 increasing by **$+47.1\%$ relative** ($0.0138 \to 0.0203$).
4. **Massive False-Positive Suppression:** Reduced false alarms on clean vehicle panels by **$85.4\%$** (123 FPs in production $\to$ 18 FPs in P9-T02), elevating operational precision from $0.2264$ to **$0.4194$ (+85.2% relative gain)**.

---

## 2. Candidate Specifications & Lineage

| Specification Dimension | Documented Value |
|---|---|
| **Candidate Identifier** | `P9-T02-BEST` |
| **Experiment ID** | `P9-T02` |
| **Experimental Description** | Spatial Resolution Scaling ($640\times 640$ vs $416\times 416$ baseline) |
| **Quarantined Checkpoint Path** | `runs/phase9/retraining/P9-T02/checkpoints/best.pt` |
| **Last Epoch Checkpoint Path** | `runs/phase9/retraining/P9-T02/checkpoints/last.pt` |
| **Base Pretrained Checkpoint** | `yolov8n.pt` (SHA-256: `f59b3d833e2ff32e194b5bb8e08d211dc7c5bdf144b90d2c8412c47ccfc83b36`) |
| **Training Input Resolution** | $640\times 640$ pixels |
| **Training Batch Size** | 8 |
| **Training Duration** | 5 epochs (SGD optimizer, momentum=0.937, $\text{lr}_0=0.01$, $\text{lrf}=0.01$) |
| **Loss Formulations** | Box loss weight: 7.5, Class loss weight: 0.5, DFL weight: 1.5 |
| **Deterministic Random Seed** | 42 |
| **Dataloader Worker Count** | 0 (single CPU process to guarantee determinism) |
| **Training Execution Date** | 2026-11-20 00:02:00 IST to 00:11:37 IST |
| **Total Training Runtime** | 577.54 seconds ($\approx 9.63\text{ minutes}$) |
| **Hardware Platform** | Intel(R) Core(TM) i5-1035G1 CPU @ 1.00GHz (Ice Lake) |

---

## 3. Cryptographic Checksum Audit

- **Best Checkpoint Relpath:** `runs/phase9/retraining/P9-T02/checkpoints/best.pt`
  - File Size: 6,503,658 bytes
  - Cryptographic SHA-256: `91a943a9a246a0748d6f8f07a0b0860ad5872c3f229ab2f69930bb37db6ca721`
- **Last Checkpoint Relpath:** `runs/phase9/retraining/P9-T02/checkpoints/last.pt`
  - File Size: 6,503,658 bytes
  - Cryptographic SHA-256: `c8d977ae2fd2509c298346588cc1dc45bd9d6ab9e618e164297eba87c61b3246`
- **Dataset YAML Hash:** `data/cardd.yaml` (SHA-256: `0555f33f4a3d651d2cc6125920e5f6b669338710f2d416ecc61275199d92efb7`)

---

## 4. Quarantine & Non-Deployment Verification

- [x] Checkpoint resides strictly within isolated directory `runs/phase9/retraining/P9-T02/`.
- [x] Checkpoint has NOT been copied to `models/phase5/`.
- [x] Checkpoint has NOT been loaded by production backend service `backend/app.py`.
- [x] Checkpoint remains quarantined pending Phase 9.7 decision.
