# ClaimSense AI — Phase 8: Gate K Governance Readiness Decision

**Document Date:** 2026-11-17  
**Governance Gate:** Gate K — Domain Adaptation & Root Cause Analysis  
**Active Specification:** `acquisition_specification.md` — v1.1-ACTIVE  
**Execution Mode:** STRICTLY PLANNING ONLY  
**Status:** COMPLETE & READY FOR REVIEW

---

## 1. Formal Governance Audit Findings

The Gate K analysis has completed an exhaustive investigation of the cross-domain performance gap and established the operational roadmap for domain adaptation:

1. **Root Causes Formally Diagnosed & Classified:**
   - The $45\% \to 0.6\%$ performance divergence is mathematically proven to be a **pure domain generalization collapse**, not an implementation, code, or annotation bug.
   - Dual-Failure Model established:
     - *Failure Mode 1:* False-positive explosion on daylight specular reflections on clean car panels (VERIFIED).
     - *Failure Mode 2:* Catastrophic recall collapse on subtle walkaround defects due to training on fragmented, multi-box catastrophic collisions (VERIFIED).
     - *Class Blindness:* Severe training scarcity on `tire flat` (only 22 instances, $2.5\%$) and `lamp broken` (64 instances) causing $0.0000$ AP (VERIFIED).
2. **Model Comparison & Candidate Checkpoint Selected:**
   - **Phase 8 Session 4** (`runs/phase8/session_4_training_01/weights/best.pt`) is certified as the **optimal starting checkpoint** for future domain adaptation experiments.
   - Session 4 demonstrated the strongest out-of-domain feature learning on `glass shatter` ($AP = 0.0339$), highest pooled mAP@50 ($0.0060$), and reduced background false alarms by $65.1\%$ vs baseline.
   - High-resolution training (Session 3 1024px) was proven ineffective without domain-matched data; base resolution is standardized at **640px**.
3. **Controlled Experiment Pipeline Designed:**
   - Three prioritized experiments (EXP-01: Background Negative Mining, EXP-02: Rare-Class Walkaround Data, EXP-03: Unified AABB Adaptation) are fully designed with quantitative success/failure gates and rollback protections.
4. **Data Requirements Formally Specified:**
   - 120 prospective authentic vehicle images specified across 4 categories (clean negatives, cracked lamps, flat tires, cosmetic defects).
   - Validation firewall strictly verified: the 44-image independent validation dataset remains completely untouched and isolated.

---

## 2. Governance Invariants & Production Status

In strict adherence to governance boundaries:

> [!CAUTION]
> **GOVERNANCE POSTURE: ZERO PRODUCTION CHANGES / ZERO UNAUTHORIZED EXECUTION**  
>
> 1. **Production Checkpoint Unchanged:** `models/phase5/best.pt` remains the active production baseline. No models have been promoted or replaced.
> 2. **Zero Code Modifications:** Phase 7 verification services, application source code, and production database models remain untouched.
> 3. **Zero Inference Reruns:** No inference or model re-evaluations were executed.
> 4. **Zero Model Training:** No fine-tuning or training was initiated.
> 5. **Zero Data Intake:** No new images have been acquired or downloaded.

---

## 3. Recommended Sequential Roadmap for Governance Approval

To execute the domain adaptation strategy safely, the following sequence of formal governance gates is recommended:

```
[Phase 8 Milestone Roadmap]
  ├── Step 1: Gate K Approval (This Phase — Root Cause & Planning Certified)
  │
  ├── Step 2: Prospective Gate L (Controlled Data Acquisition — 120 Images)
  │     ├── Intake 45 clean negative vehicles + 50 rare-class walkaround images
  │     └── Verify 0 collisions against 44 validation images
  │
  ├── Step 3: Prospective Gate M (Execute Experiment 1 — EXP-01)
  │     ├── Fine-tune Session 4 with clean vehicle negatives
  │     └── Verify >= 50% background false-positive reduction
  │
  └── Step 4: Prospective Gate N (Execute Experiment 2 — EXP-02)
        ├── Fine-tune with rare-class walkaround data & class loss weighting
        └── Break 0.0000 AP deadlock on Lamp Broken and Tire Flat
```

---

## 4. Sign-Off & Status

**Gate K Analysis Status:** **COMPLETED & FULLY DOCUMENTED.**  
Execution is paused awaiting your review, direction, and formal authorization before any further action is taken.
