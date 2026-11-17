# ClaimSense AI — Phase 8: Gate O Forensic Failure Archetype Analysis

**Document ID:** `REP-PH8-GATE-O-FAIL-001`  
**Execution Date:** 2026-11-17  
**Dataset:** `CarDD_Independent_Val_v1` (44 Images)  
**Governing Gate:** Gate O (Final Independent Benchmark)

---

## 1. Domain Shift Failure Archetypes & Adaptation Progress

### Archetype 1: Specular Glare & Daylight Body Reflections
* **Mechanism:** Direct sunlight creates localized high-gradient white glare tracks across clear-coat paint, previously triggering false-positive `scratch` and `dent` predictions.
* **Gate N Mitigation (EXP01):** Negative vehicle walkaround training (34 clean vehicle walkarounds with empty labels) penalizes gradient-only activations, driving clean vehicle false-positives down significantly.

### Archetype 2: Rare Defect Morphology (Broken Lamp & Flat Tire)
* **Mechanism:** In raw CarDD, vehicle lighting assemblies and tires were virtually absent or severely under-represented (<1% of instances), leading to 0.0000 AP on authentic vehicles.
* **Gate N Mitigation (EXP02):** Ingested authentic daylight lighting assemblies and deflated tire walkarounds, establishing genuine feature detectors for lens fractures and rim displacement.

### Archetype 3: Annotation Scale Disparity & Unified Bounding Boxes
* **Mechanism:** CarDD fragmented long linear scratches into multiple tiny boxes, causing high false-negative rates on unified physical vehicle panels.
* **Gate N Mitigation (EXP03):** Unified AABB protocol under Specification v1.1 Safeguards 4 & 5 ensured contiguous panel-level defects were learned as cohesive damage entities.

---

## 2. Statistical Uncertainty Due to Benchmark Sample Size

* **Cohort:** Exactly 44 images (36 Tier 1, 8 Tier 2) containing 47 verified defect instances.
* **Confidence Intervals:** Due to the $N=47$ sample size, per-class metrics (especially for rare classes with 3-6 instances) carry a Poisson statistical uncertainty of approximately $\pm 15\% - 25\%$.
* **Governance Significance:** Final production decisions must not rely solely on small-delta benchmark rankings, but must evaluate operational safety, false-positive resistance, and rollback readiness.
