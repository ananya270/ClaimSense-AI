# ClaimSense AI — Specification Change Impact Analysis (v1.0 to v1.1-DRAFT)

**Document Identifier:** `specification_change_impact.md`  
**Governing Context:** Phase 8 Independent Validation Dataset Planning  
**Scope of Change:** Transition from Single-Tier Resolution Gate ($800 \times 600$) to Dual-Tier Resolution Architecture (Tier 1: Walkaround $\ge 800 \times 600$; Tier 2: Macro $\ge 600 \times 400$, Damage Area $\ge 30\%$)  
**Target Dataset:** `CarDD_Independent_Val_v1`  
**Date:** 2026-11-17  
**Status:** **PROPOSED CHANGE IMPACT ASSESSMENT — PENDING RATIFICATION**  

---

## 1. Scope & Objective of Proposed Change

This impact analysis evaluates the operational, mathematical, and computer vision consequences of adopting the proposed **v1.1 Dual-Tier Resolution Architecture** across the ClaimSense AI dataset ingestion, annotation, and model evaluation workflows.

```
                  ┌────────────────────────────────────────────────────────┐
                  │                 v1.0 SINGLE-TIER GATE                  │
                  │        Strict Width >= 800 px & Height >= 600 px       │
                  └───────────────────────────┬────────────────────────────┘
                                              │
                      ┌───────────────────────┴───────────────────────┐
                      │                                               │
                      ▼                                               ▼
     ┌─────────────────────────────────┐             ┌─────────────────────────────────┐
     │     PROPOSAL: v1.1 DUAL-TIER    │             │       STATUS QUO: v1.0 STRICT   │
     │ Tier 1: Walkaround >= 800x600   │             │ Reject all sub-800x600 images.  │
     │ Tier 2: Macro >= 600x400 (>=30%)│             │ Batch 1 valid count = 15 images.│
     │ Batch 1 qualified = 23 images.  │             │ 0 Crack, 0 Lamp, 0 Scratch.     │
     └─────────────────────────────────┘             └─────────────────────────────────┘
```

---

## 2. Ingestion Pipeline & Architecture Impact

### A. Gate 2 Logic Modification (`acquisition_pipeline_spec.md`)
In `v1.0`, Gate 2 evaluates a single boolean check:
```python
# v1.0 Single-Tier Gate
if width < 800 or height < 600:
    reject("RESOLUTION_GATE_FAILED")
```

Under proposed `v1.1`, Gate 2 branches into a two-pass classification and validation pipeline:
```python
# proposed v1.1 Dual-Tier Gate
if width >= 800 and height >= 600 and context_ratio >= 0.60:
    assign_tier("TIER_1_WALKAROUND")
    status = "QUALIFIED"
elif min(width, height) >= 400 and max(width, height) >= 600 and damage_area_occupancy >= 0.30:
    assign_tier("TIER_2_MACRO")
    status = "QUALIFIED"
else:
    reject("RESOLUTION_OR_OCCUPANCY_GATE_FAILED")
```

### B. Computational Pipeline Overhead
- **Damage Occupancy Calculation:** Requires pre-screening annotator or automated coarse contour extraction to compute $\text{Area}(\text{BBox}_{\text{damage}}) / (\text{Width} \times \text{Height})$.
- **Tier Tagging in Manifests:** Adds `tier_designation` (`TIER_1` vs `TIER_2`) and `damage_occupancy_ratio` columns to `dataset_manifest.json` and CSV manifests.

---

## 3. Dataset Distribution & Sourcing Impact

### A. Impact on Batch 1 Yield
| Metric | v1.0 Strict Standard | Proposed v1.1 Dual-Tier | Change / Impact |
| :--- | :---: | :---: | :--- |
| **Accepted Images** | 15 (60.0%) | **23 (92.0%)** | **+8 reclaimed images (+32.0%)** |
| **Rejected Images** | 10 (40.0%) | **2 (8.0%)** | Both remaining rejections are genuine optical blur |
| **Tire Flat** | 7 images | 7 images | Balanced (Tier 1) |
| **Glass Shatter** | 6 images | 6 images | Balanced (Tier 1) |
| **Dent** | 2 images | **4 images** | +2 images (1 hail macro, 1 body dent macro) |
| **Crack** | **0 images** | **2 images** | **Rescued from total wipeout** |
| **Lamp Broken** | **0 images** | **2 images** | **Rescued from total wipeout** |
| **Scratch** | **0 images** | **1 image** | **Rescued from total wipeout** |
| **Active Categories** | 3 of 6 classes | **6 of 6 classes** | **Full class diversity established** |

### B. Impact on Sourcing Sourcing Strategy for Batch 2
- **Under v1.0 Strict:** Sourcing for Batch 2 must permanently exclude the entire Humans in the Loop repository (`SRC-02`). Wikimedia Commons would need to be scraped exhaustively for rare DSLR photography of cracked plastic bumpers and scratched door panels, significantly increasing acquisition latency.
- **Under v1.1 Dual-Tier:** Up to 40 additional verified institutional CC0 images from Humans in the Loop become immediately eligible for ingestion in subsequent batches, accelerating the timeline to reach the 200+ image target.

---

## 4. Model Evaluation & Benchmark Validity Impact

### A. Multi-Scale Evaluation Integrity
In operational insurance claims mobile apps, policyholders submit both full walkaround photos and close-up damage photos. 
- Evaluating models **exclusively on full-vehicle shots** fails to measure whether the model's high-level feature extractors handle close-up camera stances.
- Evaluating models **exclusively on macro crops** leads to inflated precision because complex background clutter is excluded.
- The dual-tier architecture establishes a **realistic composite test benchmark** mirroring real-world claims intake.

### B. Mandated Disaggregated Reporting Protocol
To ensure that performance on macro crops does not conceal performance degradation on walkarounds, `v1.1` mandates **disaggregated metric reporting** in all downstream benchmark evaluations:
$$\text{mAP@50}_{\text{Overall}} = w_1 \cdot \text{mAP@50}_{\text{Tier 1}} + w_2 \cdot \text{mAP@50}_{\text{Tier 2}}$$
Where $w_1 \ge 0.70$ and $w_2 \le 0.30$. Evaluators must report Precision, Recall, and F1 separately for Tier 1 and Tier 2 across all 6 damage classes.

---

## 5. Dual-Blind Annotation Workflow Impact

| Annotation Parameter | Tier 1 (Walkaround) Protocol | Tier 2 (Macro Component) Protocol |
| :--- | :--- | :--- |
| **Annotation Granularity** | Panel-level and component context visible. Annotators bound defect with standard bounding box + polygon. | Component boundary often exceeds image frame. Annotators must tightly bound **only the visible defect** (zero whole-panel bounding). |
| **Occlusion Threshold** | Standard 20% occlusion check against global vehicle background. | Stricter 10% occlusion check against surrounding component surface. |
| **Adjudication Rule** | Disagreements on defect vs panel seam resolved via vehicle silhouette context. | Disagreements on defect vs panel seam adjudicated with high-magnification edge inspection. |

---

## 6. Risk Register Updates & Mitigations

| Risk ID | Identified Risk | Severity | Likelihood | Mitigation Strategy in v1.1 |
| :--- | :--- | :---: | :---: | :--- |
| **RSK-MAC-01** | **Macro Domain Shift:** Validation set skews towards close-ups, misrepresenting walkaround appraisal accuracy. | High | Medium | **Hard Tier Ceiling:** Tier 2 is strictly capped at $\le 30.0\%$ of the total dataset. |
| **RSK-MAC-02** | **Panel Seam False Alarms:** In close-up crops, high-contrast door gaps resemble hairline cracks. | Medium | High | **Adjudication Standard:** 3-tier blind adjudication with macro edge review guidelines. |
| **RSK-MAC-03** | **Reflection Confusion:** Specular sun glints on metallic paint resemble deep clearcoat scratches. | Medium | Medium | Inclusion of multi-angle lighting metadata in provenance sidecars. |
| **RSK-MAC-04** | **Specification Drift:** Downstream annotators allow arbitrary low-res thumbnails. | High | Low | **Hard Floor:** No image below $600 \times 400$ or $< 30\%$ damage occupancy is ever permitted. |

---

## 7. Reversibility & Rollback Plan

If project leadership decides **AGAINST** ratifying `v1.1` and elects to maintain `v1.0 Strict`:
1. **Zero Data Loss:** All 25 raw binaries remain safely stored in `batch_01/raw_restricted/`.
2. **Quarantine Execution:** The 8 disqualified processed images in `batch_01/processed/` (`CS_VAL_016`, `017`, `020`, `021`, `022`, `023`, `024`, `025`) will be moved permanently to `batch_01/rejected/`.
3. **Active Manifest Integrity:** `batch_01_forensic_audit.md` and `corrected_batch_01_summary.md` already reflect the certified 15-image `v1.0` state.
4. **Batch 2 Directive:** Batch 2 acquisition will execute exclusively against Wikimedia Commons DSLR sources, targeting $\ge 800 \times 600$ images for Crack, Lamp Broken, and Scratch.
