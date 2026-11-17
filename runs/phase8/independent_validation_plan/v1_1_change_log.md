# ClaimSense AI — Specification v1.1 Formal Change Log
## Detailed Reconciliation & Clause-by-Clause Diff (v1.0 vs. v1.1-DRAFT)

**Document Identifier:** `v1_1_change_log.md`  
**Baseline Specification:** `runs/phase8/independent_validation_plan/acquisition_specification.md` (v1.0 Active)  
**Proposed Candidate Specification:** `runs/phase8/independent_validation_plan/v1_1_final_candidate.md` (v1.1-DRAFT)  
**Date:** 2026-11-17  
**Status:** **AUDIT & SPECIFICATION CHANGE LOG — AWAITING FORMAL GATE B RATIFICATION**  

---

## 1. Executive Summary of Changes

The transition from **Specification v1.0** to **Specification v1.1-DRAFT** addresses critical operational lessons learned from the Batch 1 Acquisition (25 attempted images). While `v1.0` successfully prevented low-resolution web scrapes through a single-tier resolution gate ($\ge 800 \times 600$), it inadvertently caused a **complete wipeout of close-up component imagery**, reducing candidate representation of Crack, Scratch, and Lamp Broken to zero.

Specification `v1.1` amends the baseline to establish:
1. **A Dual-Tier Resolution Standard:** Separating Full-Vehicle Walkarounds ($\ge 800 \times 600$) from Macro Component Inspections ($\ge 600 \times 400$).
2. **A Rigorous Damage Occupancy Floor:** Requiring that macro damage occupy at least $30.0\%$ of total image area, preventing low-information crops.
3. **An Anti-Inflation Safeguard & Continuous Defect Rule:** Enforcing tight bounding boxes and permitting single unified AABBs for continuous scratches/cracks.
4. **An Architectural Quota Ceiling:** Capping Tier 2 macro imagery at $\le 30.0\%$ of cumulative final dataset instances.
5. **A Definitive Class Disambiguation Rule (Rule 6):** Eliminating recurring confusion by classifying vehicle lighting fixtures strictly as `lamp broken` (Class 4).
6. **A Codified Dual-Blind Annotation & Senior Adjudication Protocol:** Guaranteeing uncorrupted ground truth through isolated double-blind labeling, IoU consensus, and formal adjudication.
7. **A Quad-Metric Validation Benchmark Architecture:** Mandating disaggregated Tier 1 and Tier 2 reporting alongside empirical pooled evaluations and a fixed-weight composite index ($0.70 / 0.30$).

---

## 2. Clause-by-Clause Specification Diff

| Section / Dimension | Baseline Specification v1.0 (Active) | Proposed Specification v1.1 (DRAFT) | Operational & Technical Rationale |
| :--- | :--- | :--- | :--- |
| **Resolution Architecture** | Single-tier: $\text{Width} \ge 800\text{ px}$ AND $\text{Height} \ge 600\text{ px}$. | Dual-tier: Tier 1 Walkaround ($\ge 800 \times 600$) AND Tier 2 Macro ($\ge 600 \times 400$). | Prevents disqualification of authentic component crops while preserving walkaround resolution. |
| **Tier 2 Dimensional Standard** | Not defined. Macro crops barred under single-tier gate. | $\min(w, h) \ge 400\text{ px}$ AND $\max(w, h) \ge 600\text{ px}$ (orientation-agnostic). | Accommodates vertical portrait component damage (e.g. pillars, roof rails, vertical door seams). |
| **Damage Area Occupancy Floor** | Not defined. | Localized damage AABB must occupy $\ge 30.0\%$ of total image area ($W \times H$). | Guarantees that macro images provide dense localized defect evidence, not empty sheet metal. |
| **Anti-Inflation Rule** | Not defined. | Bounding boxes must tightly bound physical defect. Artificially inflated boxes expressly prohibited. | Prevents annotators from artificially expanding boxes to reach 30.0% occupancy threshold. |
| **Continuous Defect Rule (Safeguard 5)** | General recommendation. | Continuous scratches/cracks on a single panel must use a single unified AABB. Separate boxes required only at panel gaps. | Eliminates artificial fragmentation of long scratch marks; matches insurance panel repair modeling. |
| **Dataset Quota Allocation** | Monolithic 200+ images. No tier quotas. | $\ge 70.0\%$ Tier 1 Walkaround (minimum); $\le 30.0\%$ Tier 2 Macro (hard ceiling). | Prevents macro component bias; ensures primary evaluation remains full-vehicle walkarounds. |
| **Class Disambiguation Rule (Rule 6)** | General CarDD class taxonomy; no lighting fixture disambiguation. | **Rule 6 Codified:** Damage to lighting fixtures is strictly `lamp broken` (4). `glass shatter` (3) is reserved for glazing. | Eliminates inter-annotator conflict between shattered headlamp lenses and side window glass. |
| **Annotation Protocol** | High-level guidelines in `annotation_protocol.md`. | **Codified Dual-Blind Protocol:** Independent Reviewers A & B, automated $\text{IoU} \ge 0.50$ consensus, Senior Adjudicator C. | Guarantees zero cognitive bias, zero model pre-label leakage, and full auditability of all ground truth. |
| **Validation Benchmark Architecture** | Single aggregate dataset mAP calculation. | **Quad-Metric Reporting:**<br>1. Stratified Tier 1<br>2. Stratified Tier 2<br>3. Empirical Pooled<br>4. Composite Index ($0.70 / 0.30$). | Prevents metric masking; provides underwriters with separate walkaround vs. repair teardown performance. |
| **Pooled vs. Composite Relationship** | Implicitly treated as single metric. | Explicit mathematical proof that $\text{mAP}_{\text{pooled}} \neq \text{mAP}_{\text{composite}}$. Both mandated. | Prevents false equivalence claims; adheres to mathematical rigor of non-linear AP curves. |

---

## 3. Empirical Impact Analysis on Candidate Eligibility

### 3.1 Batch 1 Candidate Survival Comparison

| Damage Class | Attempted Batch 1 Candidates | Certified under v1.0 Single-Tier | Eligible under v1.1 Dual-Tier | Net Change | Practical Impact on Class Representation |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Dent** | 6 | 2 | 5 | **$+3$** | Restores hail damage clusters (`CS_VAL_016`, `017`) and fender dent (`025`). |
| **Scratch** | 1 | 0 | 1 | **$+1$** | Restores continuous key scratch (`CS_VAL_024`) from zero representation. |
| **Crack** | 2 | 0 | 2 | **$+2$** | Restores bumper cracks (`CS_VAL_020`, `021`) from zero representation. |
| **Glass Shatter** | 7 | 6 | 6 | $0$ | Preserves 6 valid walkarounds; 1 rejected for blur (`011`). |
| **Lamp Broken** | 2 | 0 | 2 | **$+2$** | Restores smashed headlamp (`CS_VAL_022`) and cracked taillight (`023`). |
| **Tire Flat** | 7 | 7 | 7 | $0$ | Preserves 7 valid walkarounds; 1 rejected for blur (`005`). |
| **Total Qualified** | **25 Attempted** | **15 Qualified (60.0%)** | **23 Qualified (92.0%)** | **$+8$** | **Eliminates zero-class representation; restores all 6 damage categories.** |

### 3.2 Dimensional Threshold Selection: $600 \times 400$ vs. $640 \times 400$
The empirical rationale for setting the Tier 2 floor at $600 \times 400$ rather than $640 \times 400$:
- 5 out of 6 Humans in the Loop candidate crops have widths between $629\text{ px}$ and $637\text{ px}$.
- A $640 \times 400$ threshold disqualifies 5 authentic images by a margin of only $3$ to $11$ pixels.
- A $600 \times 400$ threshold retains $100\%$ of authentic CC0 component crops without compromising visual sharpness (all exceed $\sigma^2_{\nabla} \ge 300.0$, far above the $50.0$ blur floor).

---

## 4. Legal, Privacy & Governance Invariance

Specification `v1.1` maintains 100% adherence to all legal, privacy, and data governance restrictions established in `v1.0`:
1. **Copyright & Licensing:** Ingestion remains strictly limited to verified CC0, Public Domain, and CC BY files. Zero viral copyleft (no CC BY-SA, GFDL).
2. **Privacy & Redaction:** All images undergo EXIF decoupling and 100% zero-entropy solid black-box redaction ($[0,0,0]$) over license plates and human faces.
3. **Data Integrity:** Deduplication ensures zero exact SHA-256 collisions and minimum perceptual dHash distance $\ge 16$ against training/validation splits.
4. **Model Isolation:** Strict evaluation-only usage; zero gradient training or fine-tuning.

---

## 5. Specification Ratification Sign-Off Checklist

```
========================================================================================
                          SPECIFICATION RATIFICATION SIGN-OFF
========================================================================================

Document:             runs/phase8/independent_validation_plan/v1_1_final_candidate.md
Change Log:           runs/phase8/independent_validation_plan/v1_1_change_log.md
Target Version:       v1.1 (Dual-Tier Resolution Architecture)

Formal Gate B Decision:
[ ] APPROVED    [ ] REJECTED    [ ] DEFERRED

Authorizing Stakeholder: ___________________________________________________________
Date:                    ___________________________________________________________
========================================================================================
```
