# ClaimSense AI — Phase 8: Dual-Blind Annotation Protocol & Workflow

**Document Version:** 1.0 (Annotation Governance Specification)  
**Audit Date:** 2026-11-17  
**Scope:** Class-specific taxonomy, distinction criteria, dual-blind review workflows, adjudication rules, and quality acceptance metrics  
**Target Independent Dataset:** `CarDD_Independent_Val_v1` (Target: 220–250 authentic images)  
**Execution State:** **SPECIFICATION ONLY.** No annotations or dataset modifications executed.

---

## 1. Class-Specific Damage Taxonomy & Boundary Guidance

To guarantee benchmark integrity, annotators must adhere to rigorous, mutually exclusive category definitions across all six canonical classes:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        Damage Category Taxonomy & Ground Truth Rules                   │
├───────┬───────────────┬──────────────────────────────────┬─────────────────────────────┤
│ Class │ Name          │ Physical Phenomenon              │ Bounding Box Boundary Rule  │
├───────┼───────────────┼──────────────────────────────────┼─────────────────────────────┤
│ 0     │ Dent          │ Mechanical deformation of metal  │ Enclose complete shadow &   │
│       │               │ or composite body panels         │ specular perimeter          │
├───────┼───────────────┼──────────────────────────────────┼─────────────────────────────┤
│ 1     │ Scratch       │ Linear clearcoat/primer abrasion │ Tight box around continuous │
│       │               │ with intact underlying substrate │ scratch or dense cluster    │
├───────┼───────────────┼──────────────────────────────────┼─────────────────────────────┤
│ 2     │ Crack         │ Structural substrate through-tear│ Tight box enclosing severed │
│       │               │ or plastic bumper split          │ split gap & stress edges    │
├───────┼───────────────┼──────────────────────────────────┼─────────────────────────────┤
│ 3     │ Glass shatter │ Spiderweb laminated fracture or  │ Complete fractured window or│
│       │               │ granular tempered mosaic         │ impact bloom perimeter      │
├───────┼───────────────┼──────────────────────────────────┼─────────────────────────────┤
│ 4     │ Lamp broken   │ Polycarbonate lens fracture,     │ Tight box around damaged    │
│       │               │ puncture, or dislodged housing   │ light assembly unit         │
├───────┼───────────────┼──────────────────────────────────┼─────────────────────────────┤
│ 5     │ Tire flat     │ Depressurized pneumatic tire with│ Enclose collapsed sidewall &│
│       │               │ bead resting on pavement/rim     │ ground-rim contact patch    │
└───────┴───────────────┴──────────────────────────────────┴─────────────────────────────┘
```

---

## 2. Critical Distinction: Physical Crack vs. Superficial Scratch

A major source of error identified during the Session 2 and Session 4 calibration audits was the misclassification of thermoplastic bumper cracks as scratches (which caused Crack mAP50 to drop to 1.99%).

Annotators must apply the following **Definitive Diagnostic Criteria**:

```
                  Physical Crack vs. Superficial Scratch Diagnostic
                  
        Does the defect penetrate completely through the component substrate?
                                       │
                     ┌─────────────────┴─────────────────┐
                     ▼                                   ▼
                   [YES]                               [NO]
        • Substrate is split or severed     • Substrate remains continuous
        • Visible gap / displacement seam   • Paint clearcoat or primer displaced
        • Jagged through-tear in plastic    • Underneath metal/plastic intact
                     │                                   │
                     ▼                                   ▼
             CLASS 2: CRACK                     CLASS 1: SCRATCH
```

### Specific Component Guidance:
- **Thermoplastic Bumpers (PP / PU):** Modern bumper fascias flex upon impact; when the yield stress is exceeded, the plastic tears along stress risers (often radiating from fog light bezels, wheel arches, or grille tabs). Any visible separation gap is **Class 2 (Crack)**, even if accompanied by adjacent paint scraping.
- **Clearcoat Scuffs & Rub Marks:** Wide parallel surface scuffs on bumper corners where paint is abraded but the plastic shell remains structurally intact are **Class 1 (Scratch)**.
- **Compound Co-occurrence:** If a panel exhibits a structural crack surrounded by paint scratches, annotators must label the crack with a tight bounding box around the fracture line and label the surrounding abrasion cluster as an overlapping **Class 1 (Scratch)**.

---

## 3. Dual-Blind Annotation Protocol Workflow

To prevent observer bias and eliminate noise from third-party community labels, the annotation pipeline enforces complete isolation between two independent annotators:

```
                      [235 Curated Anonymized Images]
                                     │
                    ┌────────────────┴────────────────┐
                    ▼                                 ▼
          ┌───────────────────┐             ┌───────────────────┐
          │    Reviewer A     │             │    Reviewer B     │
          │ (Isolated Studio) │             │ (Isolated Studio) │
          └───────────────────┘             └───────────────────┘
                    │                                 │
                    ▼                                 ▼
          [YOLO Labels: Set A]              [YOLO Labels: Set B]
                    │                                 │
                    └────────────────┬────────────────┘
                                     ▼
                    [Automated Discrepancy Engine]
                                     │
           ┌─────────────────────────┴─────────────────────────┐
           │ Consensus Met:                                    │ Discrepancy Flagged:
           │ • Class_A == Class_B                              │ • Class_A != Class_B
           │ • IoU >= 0.70                                     │ • IoU < 0.70 OR Unmatched
           │                                                   │
           ▼                                                   ▼
┌───────────────────────┐                             ┌───────────────────────┐
│ Consensus Accepted    │                             │  Senior Adjudicator C │
│ • Average Coordinates │                             │  Definitive Decision  │
│ • Write to Gold Set   │                             │  Log Rationale to JSON│
└───────────────────────┘                             └───────────────────────┘
           │                                                   │
           └─────────────────────────┬─────────────────────────┘
                                     ▼
                      [Immutable Gold Ground Truth]
```

### Detailed Workflow Stages:
1. **Stage 4.1: Blind Annotation:** Reviewer A and Reviewer B independently annotate the 235 images using a standardized tool (CVAT or Label Studio) with no access to each other's work or external labels.
2. **Stage 4.2: Automated IoU Matching:** The engine computes the Hungarian matching between Set A and Set B bounding boxes using an IoU matrix.
3. **Stage 4.3: Consensus Criteria:**
   - Matches satisfying $\text{Class}_A == \text{Class}_B$ AND $\text{IoU} \ge 0.70$ are automatically promoted. The golden bounding box is calculated as the mean:
     $$\bar{x}_c = \frac{x_{cA} + x_{cB}}{2}, \quad \bar{y}_c = \frac{y_{cA} + y_{cB}}{2}, \quad \bar{w} = \frac{w_A + w_B}{2}, \quad \bar{h} = \frac{h_A + h_B}{2}$$
4. **Stage 4.4: Senior Adjudication:**
   - Any instance where $\text{Class}_A \ne \text{Class}_B$, $\text{IoU} < 0.70$, or where an instance was detected by only one reviewer is routed to Senior Adjudicator C.
   - Adjudicator C inspects the high-resolution crop, makes the definitive binding determination, and writes an explanatory entry to `adjudication_log.json`.

---

## 4. Annotation Quality Metrics & Acceptance Criteria

Prior to promoting `CarDD_Independent_Val_v1` to the evaluation suite, the dataset must satisfy three strict statistical quality thresholds:

1. **Inter-Annotator Agreement (Cohen's Kappa):**
   $$\kappa = \frac{p_o - p_e}{1 - p_e} \ge 0.85$$
   Where $p_o$ is the observed proportional agreement across all damage categories and $p_e$ is the expected chance agreement. A score of $\kappa \ge 0.85$ indicates near-perfect reliability.
2. **Spatial Alignment Threshold:**
   $$\text{Mean IoU}_{\text{consensus}} \ge 0.80$$
   Demonstrating consistent bounding box tightness across both annotators.
3. **100% Adjudication Completeness:**
   Every discrepancy flagged by the engine must have a documented adjudicator decision with zero unresolved records remaining in `adjudication_log.json`.
