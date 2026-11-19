# ClaimSense AI — Phase 9.8: Risk & Limitation Register

**Document ID:** `REG-PH9-8-RISK-001`  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.8 — Final Model Selection, Approval & Sign-off  
**Execution Date:** 2026-11-20  
**Status:** ACTIVE GOVERNANCE RISK REGISTER  

---

## 1. Overview & Risk Management Framework

This register enumerates all verified technical, operational, and architectural risks identified during the Phase 9 model optimization cycle. Each entry documents the root cause, severity, impact on ClaimSense AI claim verification, and recommended architectural mitigation for Phase 10.

---

## 2. Technical & Forensic Risk Matrix

| Risk ID | Risk Category | Description & Empirical Evidence | Severity | Likelihood | Operational Impact on Insurance Workflow | Architectural Remediation Track |
|---|---|---|---|---|---|---|
| **RSK-01** | Crack Detection Failure | Both production and candidate P9-T02 achieve **0.0000% operational recall (0/13 detected)** on structural cracks at $\tau=0.25$. | **CRITICAL** | **100% (Confirmed)** | Structural fissures on bumpers, grilles, and chassis members are completely overlooked by computer vision. | Implement class-weighted focal loss ($\alpha_{\text{crack}}=2.8$) and multi-scale P2 layer in Phase 10. |
| **RSK-02** | Scratch Confusion | Fractures on plastic bumpers and handles are misclassified as scratches due to $4.08:1$ scratch-to-crack training imbalance. | **HIGH** | **HIGH** | Major structural failure miscategorized as cosmetic paint abrasion, causing inaccurate claim loss estimates. | Resample crack instances with targeted augmentation and apply rare-class focal penalties. |
| **RSK-03** | Threshold Mismatch | Scaling resolution to $640\times 640$ distributes anchor confidences; rigid $\tau=0.25$ causes an operational recall collapse ($24.3\% \to 8.8\%$). | **HIGH** | **HIGH** | High-resolution candidate misses $91.2\%$ of damages if deployed without re-calibrated confidence thresholds. | Implement class-adaptive dynamic confidence thresholds ($\tau_{\text{crack}}=0.12, \tau_{\text{dent}}=0.18, \tau_{\text{glass}}=0.30$). |
| **RSK-04** | Small Minority Support | CarDD test split contains only 13 crack instances across 10 images; CarDD validation contains only 11 instances. | **MEDIUM** | **MEDIUM** | Statistical power is limited when validating fine-grained recall recovery on unseen datasets. | Ingest 78 vetted external crack instances in Phase 10 training and establish a dedicated $N \ge 60$ crack benchmark. |
| **RSK-05** | Production Blindspot | Retaining `models/phase5/best.pt` in production means the system continues to miss structural cracks. | **HIGH** | **HIGH** | Computer vision cannot detect cracks independently. | Mitigated by Phase 7 multi-source cross-verification: narrative NLP and OCR invoice items cross-validate crack evidence. |

---

## 3. Risk Mitigation & Compensation in Existing Pipeline

While computer vision cannot currently detect structural cracks independently:
- **Phase 7 Cross-Source Verification Safety Net:** ClaimSense AI does not rely solely on YOLOv8. The cross-verification engine (`backend/services/verification/`) evaluates damage claims across three independent modalities:
  1. **Document Intelligence (OCR):** Extracts repair line items (e.g., *"cracked front bumper assembly replacement"*).
  2. **Narrative Analysis (NLP):** Extracts incident statements (e.g., *"vehicle struck curb causing structural fracture to front lip"*).
  3. **Computer Vision (YOLOv8):** Performs visual damage detection.
- When computer vision fails to detect a crack but both OCR and NLP provide supporting evidence, Phase 7 flags the claim as `INCONCLUSIVE_DAMAGE` or `EVIDENCE_MISMATCH` with high-severity review triggers, preventing fraudulent or under-compensated claims from slipping through uninspected.
