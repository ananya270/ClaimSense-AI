# ClaimSense AI — Phase 8: Stage 1 Acquisition Readiness Report

**Document Version:** 1.0 (Comprehensive Readiness Review)  
**Audit Date:** 2026-11-17  
**Scope:** Stage 1 independent validation dataset acquisition preparation, source feasibility, pipeline verification, annotation workflow, and evaluation protocol  
**Execution State:** **PREPARATION ONLY.** Acquisition gate remains **LOCKED**.

---

## 1. Executive Summary & Operational Readiness Verdict

```
                     =====================================================
                     STAGE 1 ACQUISITION GATE VERDICT: OPERATIONALLY READY
                                  (PENDING USER AUTHORIZATION)
                     =====================================================
```

Stage 1 preparation is **operationally ready** from an engineering, architectural, and legal compliance standpoint:
1. **Hail Damage Discovery Complete:** MediaWiki API cross-search surfaced **35 verified CC0/CC-BY candidate files** (documented in `wikimedia_hail_candidates.csv`), resolving the hail category query gap.
2. **Approved Source Allocation Finalized:** A realistic 235-image plan allocates **190 images from Humans in the Loop (CC0)** and **45 images from Wikimedia Commons (CC0/CC-BY)**, completely excluding Roboflow and Kaggle Insurance to prevent unverified copyright title risks.
3. **Pipeline Validated in Dry-Run:** `acquisition_dry_run.py` was implemented and validated across all 8 pipeline gates (SHA-256 deduplication, 64-bit dHash, resolution $>800\times600$, Laplacian blur, EXIF purge into sidecar, solid zero-entropy PII masking with $\ge 15\%$ dilation, and 20% damage occlusion threshold). Live download was prevented.
4. **Dual-Blind Protocol Formulated:** Detailed diagnostic criteria distinguishing physical cracks from superficial scratches, inter-annotator agreement thresholds ($\kappa \ge 0.85$, $\text{IoU} \ge 0.70$), and senior adjudication workflows are codified.
5. **Evaluation Protocol Codified:** A controlled 3-way benchmarking checklist establishes environmental invariance across Production Baseline, Session 2, and Session 4 checkpoints.

---

## 2. Source-Wise Verified Candidate Counts

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        Verified Candidate Inventory Summary                            │
├────────┬─────────────────┬──────────┬──────────┬──────────┬──────────┬─────────────────┤
│ Source │ Source Name     │ Doc Count│ License- │ Actually │ Est. Post│ Target Stage 1  │
│ ID     │                 │ (Card)   │ Verified │ Accessible│ Screening│ Allocation Plan │
├────────┼─────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ SRC-02 │ Humans in Loop  │ 1,812    │ 1,812    │ 1,812    │ ~580     │ **190 images**  │
│        │ (Institutional) │          │ (CC0)    │ (HF/API) │ (Clean)  │ (80.9%)         │
├────────┼─────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ SRC-06 │ Wikimedia Comm. │ 10,000+  │ 71*      │ 71       │ ~45      │ **45 images**   │
│        │ (General + Hail)│          │ (CC0/BY) │ (API)    │ (Vehicle)│ (19.1%)         │
├────────┼─────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ Total  │ Approved Pool   │ 11,812   │ 1,883    │ 1,883    │ ~625     │ **235 images**  │
└────────┴─────────────────┴──────────┴──────────┴──────────┴──────────┴─────────────────┘
```
*\*Comprises 36 general damage files (`wikimedia_candidate_manifest.csv`) + 35 hail damage files (`wikimedia_hail_candidates.csv`).*

---

## 3. Remaining Blockers & Critical Category Bottlenecks

While the pipeline is operationally ready, two critical class-instance bottlenecks and two governance prerequisites remain:

1. **Tire Flat Category Bottleneck (Target: 30+ instances, Projected Yield: ~18):**  
   - Humans in the Loop contains zero flat tires.
   - Wikimedia Commons `Category:Flat_tires` provided only 16 approved CC0/CC-BY candidates (22 were CC BY-SA).
   - *Status:* Ingestion of 16 approved photos yields ~18 instances, creating a deficit of 12 instances against the 30-instance target.
   - *Remediation Path:* Prior to freezing annotations, execute an expanded search on Wikimedia Commons across non-English categories (`Category:Punctured tires`, French `Pneu crevé`, German `Reifenpanne`).
2. **Glass Shatter Category Constraint (Target: 40+ instances, Projected Yield: ~26):**  
   - Approved candidate window photos total ~12–14 files, yielding ~26 instances.
   - *Remediation Path:* Traverse vehicle vandalism subcategories on Wikimedia Commons.
3. **Chrome Reflection Channel Inspection:**  
   - Unit tests proved that while 15% bounding box dilation captures immediate edge flares (<9px), specular reflections of plate digits on curved chrome bumpers can extend 15–30px.
   - *Requirement:* Mandatory manual inspection of reflection channels during the Dual-Blind protocol.
4. **Explicit User Authorization:**  
   - Physical execution of Stage 1 image downloading and staging requires separate written user authorization.

---

## 4. Stage 1 Preparation Deliverables Inventory & Checksums

All eight deliverables for Stage 1 preparation are saved in `runs/phase8/independent_validation_plan/stage_1_preparation/` with cryptographic SHA-256 hashes:

| Deliverable File | Type | Size | SHA-256 Checksum |
| :--- | :---: | :---: | :--- |
| `source_allocation_plan.md` | Markdown Plan | 13,135 B | `f4a3a9b863500a88bb7dc6403a38f55aa1a11bb77c910ba6400dd7a7f9c564e7` |
| `wikimedia_hail_candidates.csv` | CSV Manifest | 11,279 B | `62baeb9c58e79766ccfd7be744dbb12a398f229895092e8aecf3cca51fb41b2c` |
| `wikimedia_hail_search_report.md` | Markdown Report | 5,868 B | `eed13e3afc614bc13040b586b337b9c1ef727217b50cfdaabf19d23a7a705175` |
| `acquisition_pipeline_spec.md` | Markdown Spec | 10,905 B | `bb09c3273b090dbb2a9864b31ccd4966b2cce84a2557a3d1ec9995c8c46e770f` |
| `acquisition_dry_run.py` | Python Script | 5,455 B | `c5639b705465cd1cb6f2053792ac25b0fd2fb33b2aca6251c1f72ec3239e605a` |
| `annotation_workflow.md` | Markdown Spec | 11,618 B | `6c093e96712e8f195820b3156fe113986fa1e37d59f07bbc4be3bfba73d5c1b0` |
| `independent_evaluation_checklist.md` | Markdown Spec | 7,069 B | `b1b6ac7dd09883cdae0b352dd88c0ef41e45ceba06f31f05246eb1d8aa3d70f6` |
| `stage_1_readiness_report.md` | Markdown Report | ~7,500 B | *(Self-referential summary report)* |
