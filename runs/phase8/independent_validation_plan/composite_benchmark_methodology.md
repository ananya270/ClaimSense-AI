# ClaimSense AI — Independent Validation Benchmark Methodology
## Disaggregated & Composite Evaluation Architecture (v1.1-DRAFT)

**Document Identifier:** `composite_benchmark_methodology.md`  
**Governing Standard:** `runs/phase8/independent_validation_plan/v1_1_final_candidate.md`  
**Target Dataset:** `CarDD_Independent_Val_v1`  
**Execution Mode:** SPECIFICATION & MATHEMATICAL GOVERNANCE ONLY  
**Date:** 2026-11-17  
**Status:** **DRAFT SPECIFICATION — PENDING RATIFICATION**  

---

## 1. Executive Summary & Problem Formulation

In a dual-tier validation dataset comprising both **Full-Vehicle Walkarounds (Tier 1)** and **Macro Component Inspections (Tier 2)**, standard aggregate benchmark reporting presents severe methodological hazards:

1. **Scale-Distribution Asymmetry:**  
   In Tier 1 walkarounds, damage instances typically occupy $0.2\%\text{--}5.0\%$ of the image area in broad vehicle context. In Tier 2 macro inspections, damage instances occupy $\ge 30.0\%$ of the frame. A single unified metric conceals whether model improvements stem from superior fine-grained localization or simply large-scale macro detection.
2. **The Non-Linearity of Average Precision (AP):**  
   Average Precision ($\text{AP}$) is defined as the area under the non-convex Precision-Recall ($\text{PR}$) curve generated from globally sorted detection confidences. Because the sorting operator is non-linear, **the weighted average of stratified APs is mathematically distinct from the pooled AP of concatenated detections**.
3. **Insurance Stakeholder Requirements:**  
   Insurance underwriting and claims triage workflows operate in distinct camera regimes: mobile app user walkarounds (Tier 1) vs. repair facility teardown/supplement close-ups (Tier 2). Decision-makers require isolated visibility into performance across each capture mode.

To resolve these challenges, this specification formally establishes a **Quad-Metric Validation Architecture**:
- **Metric 1: Tier 1 Walkaround Benchmark** (Disaggregated)
- **Metric 2: Tier 2 Macro Component Benchmark** (Disaggregated)
- **Metric 3: Full-Dataset Pooled Benchmark** (Empirical Operational Benchmark)
- **Metric 4: Fixed-Weight Composite Benchmark Index** (Governance Leaderboard Benchmark)

---

## 2. Mathematical Proof: Pooled mAP vs. Weighted Stratified mAP

### 2.1 Formal Definition of Mean Average Precision (mAP)
For a dataset $\mathcal{D}$ and class $c \in \{0, \dots, C-1\}$, let $\mathcal{G}_c$ denote the set of ground-truth instances ($N_c = |\mathcal{G}_c|$) and $\mathcal{P}_c$ denote the set of model predictions.

Predictions $\mathcal{P}_c$ are sorted in descending order of confidence score $s$:

$$\mathcal{P}_c = \langle p_1, p_2, \dots, p_M \rangle, \quad s(p_1) \ge s(p_2) \ge \dots \ge s(p_M)$$

At each rank $k \in \{1, \dots, M\}$, cumulative True Positives ($TP_k$) and False Positives ($FP_k$) are evaluated against $\mathcal{G}_c$ using intersection-over-union threshold $\tau$ (e.g. $\tau = 0.50$):

$$\text{Precision}(k) = \frac{TP_k}{TP_k + FP_k}, \quad \text{Recall}(k) = \frac{TP_k}{N_c}$$

Under the standard 101-point COCO interpolation standard, the Average Precision for class $c$ is:

$$\text{AP}_c(\mathcal{D}) = \frac{1}{101} \sum_{r \in \{0.00, 0.01, \dots, 1.00\}} p_{\text{interp}}(r), \quad p_{\text{interp}}(r) = \max_{\tilde{r} \ge r} \text{Precision}(\tilde{r})$$

Mean Average Precision ($\text{mAP}$) across all $C$ classes is:

$$\text{mAP}(\mathcal{D}) = \frac{1}{C} \sum_{c=0}^{C-1} \text{AP}_c(\mathcal{D})$$

### 2.2 Stratified Partitioning
Let the dataset $\mathcal{D}$ be partitioned into disjoint subsets:
- $\mathcal{D}_1$: Tier 1 Walkaround images ($N_{1,c}$ ground-truth instances of class $c$).
- $\mathcal{D}_2$: Tier 2 Macro Component images ($N_{2,c}$ ground-truth instances of class $c$).
- $\mathcal{D} = \mathcal{D}_1 \cup \mathcal{D}_2$, with $N_c = N_{1,c} + N_{2,c}$.

Let $\mathcal{P}_{1,c}$ and $\mathcal{P}_{2,c}$ be the prediction sets on $\mathcal{D}_1$ and $\mathcal{D}_2$, respectively.

### 2.3 Mathematical Proof of Inequality
**Theorem:** *In general, the pooled Average Precision $\text{AP}_c(\mathcal{D}_1 \cup \mathcal{D}_2)$ CANNOT be expressed as a linear weighted combination of the stratum Average Precisions $\text{AP}_c(\mathcal{D}_1)$ and $\text{AP}_c(\mathcal{D}_2)$:*

$$\text{AP}_c(\mathcal{D}_1 \cup \mathcal{D}_2) \neq w_1 \text{AP}_c(\mathcal{D}_1) + w_2 \text{AP}_c(\mathcal{D}_2) \quad \text{for any fixed } w_1, w_2 \ge 0$$

**Proof:**
1. **Confidence Rank Interleaving:**  
   In the pooled evaluation, $\mathcal{P}_{1,c}$ and $\mathcal{P}_{2,c}$ are merged into a single sorted list $\mathcal{P}_c = \text{Sort}(\mathcal{P}_{1,c} \cup \mathcal{P}_{2,c})$. The rank of any prediction $p \in \mathcal{P}_{1,c}$ in the pooled list depends on how many predictions in $\mathcal{P}_{2,c}$ possess higher confidence scores:
   $$\text{Rank}_{\text{pooled}}(p) = \text{Rank}_{\mathcal{P}_{1,c}}(p) + \sum_{q \in \mathcal{P}_{2,c}} \mathbb{I}[s(q) > s(p)]$$
2. **Non-Local False Positive Distortion:**  
   If a high-confidence false positive $q \in \mathcal{P}_{2,c}$ appears at rank $k$, it increments $FP$ in the pooled denominator for all subsequent ranks $m > k$, reducing $\text{Precision}(m)$ for predictions originating from $\mathcal{D}_1$, even though $q$ never existed in $\mathcal{D}_1$.
3. **Recall Denominator Shift:**  
   A single true positive in $\mathcal{D}_1$ advances recall by $1 / N_{1,c}$ in the stratified evaluation, but only by $1 / (N_{1,c} + N_{2,c})$ in the pooled evaluation. Because the interpolation operator $p_{\text{interp}}(r) = \max_{\tilde{r} \ge r} \text{Precision}(\tilde{r})$ is a non-linear step function, linear superposition fails:
   $$\int_{0}^{1} p_{\text{pooled}}(r) \, dr \neq \frac{N_{1,c}}{N_c} \int_{0}^{1} p_{\mathcal{D}_1}(r) \, dr + \frac{N_{2,c}}{N_c} \int_{0}^{1} p_{\mathcal{D}_2}(r) \, dr$$
   $\blacksquare$

### 2.4 Governance Mandate on Metric Separation
Because $\text{mAP}_{\text{pooled}} \neq \text{mAP}_{\text{weighted}}$, the ClaimSense validation protocol strictly forbids presenting a weighted linear combination of stratified mAP values as equivalent to a pooled test-set evaluation. Both metrics serve distinct, indispensable functions and must be reported simultaneously.

---

## 3. The Quad-Metric Validation Reporting Standard

All future validation runs on `CarDD_Independent_Val_v1` must generate and present the following four benchmark evaluations:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              CLAIMSENSE QUAD-METRIC BENCHMARK REPORT                                   │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. STRATIFIED TIER 1 BENCHMARK (Walkaround Context)                                                    │
│    • Population:   Strictly Tier 1 images (Width >= 800, Height >= 600, Vehicle Context >= 60%)        │
│    • Purpose:      Measures long-range defect detection, context parsing, and small-object recall      │
│    • Key Metrics:  mAP@0.50, mAP@0.50:0.95, Precision, Recall, False Positives per Image (FPPI)        │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. STRATIFIED TIER 2 BENCHMARK (Macro Component Inspection)                                            │
│    • Population:   Strictly Tier 2 images (min >= 400, max >= 600, AABB Occupancy >= 30%)              │
│    • Purpose:      Measures localized fracture delineation, texture analysis, and component boundary    │
│    • Key Metrics:  mAP@0.50, mAP@0.50:0.95, Localization Tightness, Class Disambiguation Accuracy      │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. EMPIRICAL POOLED BENCHMARK (Operational Distribution)                                               │
│    • Population:   All certified images in the active validation split (Tier 1 + Tier 2)               │
│    • Purpose:      True empirical test performance across the raw operational sample mix               │
│    • Calculation:  Concatenated predictions globally ranked and evaluated against unified ground truth │
│    • Key Metrics:  mAP@0.50, mAP@0.50:0.95, Class-Wise AP breakdown                                    │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. FIXED-WEIGHT COMPOSITE BENCHMARK INDEX (Governance & Leaderboards)                                  │
│    • Population:   Synthetic linear index combining Tier 1 and Tier 2 stratified scores                │
│    • Purpose:      Standardized model comparison insulated from batch-to-batch sampling fluctuations   │
│    • Formula:      mAP_composite = 0.70 * mAP_Tier1 + 0.30 * mAP_Tier2                                 │
│    • Weighting:    Strictly 70% Tier 1 (Walkaround) and 30% Tier 2 (Macro), matching spec architecture │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Formal Definition of the Composite Benchmark Index

To track model progress across iterations without distortion from varying Tier 1 / Tier 2 sample proportions across batches, the **Composite Benchmark Index** is defined as:

$$\text{mAP@0.50}_{\text{composite}} = 0.70 \times \text{mAP@0.50}_{\text{Tier1}} + 0.30 \times \text{mAP@0.50}_{\text{Tier2}}$$

$$\text{mAP@0.50:0.95}_{\text{composite}} = 0.70 \times \text{mAP@0.50:0.95}_{\text{Tier1}} + 0.30 \times \text{mAP@0.50:0.95}_{\text{Tier2}}$$

### 4.1 Rationale for 70/30 Fixed Weighting
1. **Alignment with Target Dataset Architecture:**  
   Specification `v1.1` mandates that the final cumulative dataset must consist of $\ge 70.0\%$ Tier 1 images and $\le 30.0\%$ Tier 2 images. The $70 / 30$ weight directly reflects the target distribution.
2. **Insulation from Acquisition Phasing:**  
   During early batches (e.g. Batch 1), the empirical sample ratio may deviate (e.g. 34.8% macro in Batch 1). A pooled score would over-weight macro images during early phases. The fixed composite index guarantees that Tier 1 walkaround performance always commands the dominant 70% share of the benchmark index.
3. **Macro Overfitting Penalty:**  
   A model that achieves $0.95\text{ mAP}$ on macro close-ups but deteriorates to $0.50\text{ mAP}$ on walkarounds will be constrained to:
   $$\text{mAP}_{\text{composite}} = 0.70(0.50) + 0.30(0.95) = 0.350 + 0.285 = \mathbf{0.635}$$
   preventing artificially inflated scores.

---

## 5. Class-Wise Composite Reporting Matrix

In addition to overall mAP, per-class composite scores must be calculated:

$$\text{AP}_{c,\text{composite}} = 0.70 \times \text{AP}_{c,\text{Tier1}} + 0.30 \times \text{AP}_{c,\text{Tier2}}$$

| Class ID | Damage Class | Tier 1 AP@0.50 (Walkaround) | Tier 2 AP@0.50 (Macro) | Pooled AP@0.50 (Empirical) | Composite AP@0.50 ($0.70 / 0.30$) | Stratum Delta ($\text{Tier2} - \text{Tier1}$) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| 0 | Dent | $\text{AP}_{0,T1}$ | $\text{AP}_{0,T2}$ | $\text{AP}_{0,\text{pool}}$ | $0.70 \text{AP}_{0,T1} + 0.30 \text{AP}_{0,T2}$ | $\Delta_0$ |
| 1 | Scratch | $\text{AP}_{1,T1}$ | $\text{AP}_{1,T2}$ | $\text{AP}_{1,\text{pool}}$ | $0.70 \text{AP}_{1,T1} + 0.30 \text{AP}_{1,T2}$ | $\Delta_1$ |
| 2 | Crack | $\text{AP}_{2,T1}$ | $\text{AP}_{2,T2}$ | $\text{AP}_{2,\text{pool}}$ | $0.70 \text{AP}_{2,T1} + 0.30 \text{AP}_{2,T2}$ | $\Delta_2$ |
| 3 | Glass Shatter | $\text{AP}_{3,T1}$ | $\text{AP}_{3,T2}$ | $\text{AP}_{3,\text{pool}}$ | $0.70 \text{AP}_{3,T1} + 0.30 \text{AP}_{3,T2}$ | $\Delta_3$ |
| 4 | Lamp Broken | $\text{AP}_{4,T1}$ | $\text{AP}_{4,T2}$ | $\text{AP}_{4,\text{pool}}$ | $0.70 \text{AP}_{4,T1} + 0.30 \text{AP}_{4,T2}$ | $\Delta_4$ |
| 5 | Tire Flat | $\text{AP}_{5,T1}$ | $\text{AP}_{5,T2}$ | $\text{AP}_{5,\text{pool}}$ | $0.70 \text{AP}_{5,T1} + 0.30 \text{AP}_{5,T2}$ | $\Delta_5$ |
| **All** | **Mean (mAP)** | **$\text{mAP}_{T1}$** | **$\text{mAP}_{T2}$** | **$\text{mAP}_{\text{pool}}$** | **$\text{mAP}_{\text{composite}}$** | **$\Delta_{\text{mean}}$** |

---

## 6. Zero Representation Handling in Stratified Sets

During initial or partial evaluation runs, a specific class might temporarily have zero instances in one stratum (for example, in Batch 1 under v1.0, Tier 1 had 0 Crack, 0 Scratch, 0 Lamp Broken).

### Governing Rule for Missing Strata:
- If class $c$ has $N_{1,c} = 0$ instances in Tier 1:
  $$\text{AP}_{c,\text{Tier1}} = \text{UNDEFINED (N/A)}$$
- In such cases, $\text{AP}_{c,\text{composite}}$ cannot be computed. It must be explicitly marked as `PENDING_REPRESENTATION`, and NOT assigned an arbitrary $0.00$ (which would erroneously penalize the model) nor $1.00$.
- A composite benchmark can only be certified when every class satisfies $N_{1,c} \ge 5$ and $N_{2,c} \ge 3$.

---

## 7. Implementation Checklist for Model Evaluation Harness

When model evaluation is authorized in future phases, the automated benchmark script (`runs/phase8/evaluate_validation.py`) must implement:
1. Two separate evaluation passes: one with image list filtered to `tier == 1`, one filtered to `tier == 2`.
2. One unified evaluation pass with all active images to compute the pooled COCO metrics.
3. Automated synthesis of the fixed-weight composite report according to the formulas above.
4. Export of the 4-way benchmark table in both markdown and CSV formats.
