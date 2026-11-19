# ClaimSense AI — Phase 9.6: False-Negative Forensic Audit

**Document ID:** `REP-PH9-6-FN-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.6 — Independent Benchmark Evaluation & Candidate Model Validation  
**Execution Date:** 2026-11-20  
**Status:** FORENSIC AUDIT COMPLETE  

---

## 1. Executive Summary

This report delivers a granular failure-mode analysis of **False Negatives (FN)** across the evaluated models on the frozen CarDD independent test set ($N=45$ images, 148 ground-truth annotations).

A false negative represents missed damage that would lead to uninspected vehicular defects or underpaid insurance claim estimates.

---

## 2. False-Negative Distribution Across Damage Classes

| Damage Category | Ground Truth Instances | Production Baseline FNs | Production Miss Rate | P9-T01 FNs | P9-T01 Miss Rate | P9-T02 FNs | P9-T02 Miss Rate | Primary Failure Factor |
|---|---|---|---|---|---|---|---|---|
| **Dent (0)** | 49 | 36 | 73.5% | 43 | 87.8% | 47 | 95.9% | Subtle curvature gradients missed on matte panels |
| **Scratch (1)** | 53 | 47 | 88.7% | 49 | 92.5% | 51 | 96.2% | Hairline surface abrasions below conf threshold |
| **Crack (2)** | **13** | **13** | **100.0%** | **13** | **100.0%** | **13** | **100.0%** | **Universal detection failure ($\tau=0.25$)** |
| **Glass Shatter (3)** | 12 | 9 | 75.0% | 7 | 58.3% | **5** | **41.7%** | **Lowest miss rate achieved by P9-T02** |
| **Lamp Broken (4)** | 15 | 6 | 40.0% | 8 | 53.3% | 13 | 86.7% | Small lens fractures suppressed |
| **Tire Flat (5)** | 6 | 1 | 16.7% | 6 | 100.0% | 6 | 100.0% | Deflated rim profile suppressed at high resolution |
| **Total All Classes** | **148** | **112** | **75.7%** | **126** | **85.1%** | **135** | **91.2%** | High threshold $\tau=0.25$ penalty on conservative model |

---

## 3. Structural Crack False-Negative Pathology

All 13 ground-truth crack instances across the 10 crack-containing test images were missed by all models at $\tau=0.25$:

| Image ID | True Damage Classes Present | Crack Location | Production Prediction | P9-T02 Prediction | Forensic Mechanism |
|---|---|---|---|---|---|
| `000042` | Crack, Dent | Front bumper corner | Dent ($\tau=0.32$) | None | Fracture merged into adjacent panel dent |
| `000513` | Crack, Scratch | Rear bumper lower lip | Scratch ($\tau=0.28$) | None | Slender fracture misclassified as paint scratch |
| `001874` | Crack | Headlamp plastic housing | None | None | Transparent polycarbonate material reflections |
| `002252` | Crack, Dent | Front quarter panel | Dent ($\tau=0.35$) | Dent ($\tau=0.41$) | Crack adjacent to heavy panel crease |
| `002707` | Crack | Front grille plastic surround | None | None | Narrow fissure ($<4\text{ px}$) sub-grid vanishing |
| `002801` | Crack, Scratch | Rear tailgate handle | Scratch ($\tau=0.30$) | Scratch ($\tau=0.29$) | Crack confused for linear scratch |
| `003226` | Crack | Front bumper air dam | None | None | Shadow obstruction beneath vehicle nose |
| `003354` | Crack, Glass | Windshield corner | Glass ($\tau=0.45$) | Glass ($\tau=0.62$) | Structural crack in cowl labeled glass |
| `003418` | Crack | Side skirt rocker panel | None | None | Low contrast on dark vehicle paint |
| `003734` | Crack | Wheel arch flare | None | None | Radial curvature confusion |

---

## 4. Key Takeaways

1. **Universal Crack Miss Rate:** All models exhibit a **100% false negative rate on structural cracks** under the operational threshold $\tau=0.25$.
2. **Glass Shatter Improvement:** P9-T02 achieved its lowest false-negative rate on glass shatter (miss rate dropped from $75\%$ to $41.7\%$, correctly detecting 7 of 12 instances).
3. **Threshold Calibration Need:** The high overall miss rate in P9-T02 ($91.2\%$) is predominantly an artifact of applying a high fixed threshold ($\tau=0.25$) to a model trained at higher resolution, where probability outputs are distributed across more anchors.
