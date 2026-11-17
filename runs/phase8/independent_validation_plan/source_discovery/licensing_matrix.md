# ClaimSense AI — Independent Validation Dataset: Licensing Matrix

**Document Version:** 1.0  
**Audit Date:** 2026-11-17  
**Scope:** Legal, commercial, and machine-learning rights evaluation of candidate vehicle damage image sources  
**Governing Principle:** Public accessibility does NOT equal commercial permission. Every approval requires verifiable legal text.

---

## 1. Source Licensing Evaluation Matrix

| Source ID | Source Name | Documented License | Commercial Use Explicitly Allowed? | ML Training & Benchmark Permitted? | Internal Dataset Storage Permitted? | Attribution Required? | Status Classification |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **SRC-01** | **Roboflow Car Damage V5** | **Creative Commons Attribution 4.0 International (CC BY 4.0)** | **YES** | **YES** | **YES** | YES | **APPROVED** |
| **SRC-02** | **Hugging Face Car Parts & Damage** | **MIT License** | **YES** | **YES** | **YES** | YES | **APPROVED** |
| **SRC-03** | **Kaggle Coco Car Damage** | **Creative Commons CC0 1.0 Universal (Public Domain)** | **YES** | **YES** | **YES** | NO (Applied) | **APPROVED** |
| **SRC-04** | **Kaggle Car Damage Assessment** | **Creative Commons CC0 1.0 Universal (Public Domain)** | **YES** | **YES** | **YES** | NO (Applied) | **APPROVED** |
| **SRC-05** | **Kaggle Insurance Claim Damage** | **Apache License, Version 2.0** | **YES** | **YES** | **YES** | YES | **APPROVED** |
| **SRC-06** | **Wikimedia Commons Collections** | **CC-BY 4.0 / CC0 / Public Domain** (per-image verified) | **YES** | **YES** | **YES** | YES | **APPROVED** |
| **SRC-07** | **SKKU TQVCD Dataset** | **None (No License File / All Rights Reserved)** | **NO** | **UNSPECIFIED** | **NO** | N/A | **REJECTED** |
| **SRC-08** | **Mendeley Data SYNDCAR** | **CC BY-NC 4.0 / Non-Commercial + Synthetic** | **NO** | Academic Only | N/A | N/A | **REJECTED** |
| **SRC-09** | **Copart / IAAI Scraping** | **Proprietary Auction Terms of Service (Section 2: Anti-Scraping)** | **NO** | **PROHIBITED** | **NO** | N/A | **REJECTED** |
| **SRC-10** | **Commercial Stock (Getty / Adobe)** | **Commercial Royalty-Free (AI Training Prohibited in Standard Terms)** | Paid Custom Only | **PROHIBITED** without AI Addendum | Conditional | N/A | **REJECTED** |

---

## 2. In-Depth Documentary Legal Analysis by Source

### A. SRC-01: Roboflow Car Damage V5 — **APPROVED**
- **Direct License Reference:** `https://creativecommons.org/licenses/by/4.0/`
- **Official Grant of Rights:** Under CC BY 4.0 Section 2(a)(1): *"Subject to the terms and conditions of this Public License, the Licensor hereby grants You a worldwide, royalty-free, non-sublicensable, non-exclusive, irrevocable license to exercise the Licensed Rights in the Licensed Material to: (A) reproduce and Share the Licensed Material, in whole or in part; and (B) produce, adapt, and Share Adapted Material."*
- **Commercial Clause:** Section 2(a)(1) explicitly authorizes exercising these rights *"for any purpose, even commercially."*
- **Machine Learning Applicability:** Extracting feature embeddings, training, evaluating, and validating models constitutes a legal exercise of computational analysis on adapted material.
- **Attribution Obligation:** Section 3(a)(1) mandates retaining author credit, a notice referring to CC BY 4.0, and a disclaimer of warranties. The ClaimSense dataset manifest will include: `"Attribution: Roboflow Community / Car Damage V5 project (CC BY 4.0)"`.
- **Verdict:** Fully cleared for enterprise ML validation.

---

### B. SRC-02: Hugging Face Car Parts & Damage Dataset — **APPROVED**
- **Direct License Reference:** `https://huggingface.co/datasets/DrBimmer/car-parts-and-damage-dataset/blob/main/README.md` (MIT License)
- **Official Grant of Rights:** *"Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the 'Software'), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software..."*
- **Commercial Clause:** Explicitly unconstrained.
- **Attribution Obligation:** Retain original copyright notice in dataset documentation.
- **Verdict:** Fully cleared for enterprise ML validation.

---

### C. SRC-03 & SRC-04: Kaggle CC0 Public Domain Datasets — **APPROVED**
- **Direct License Reference:** `https://creativecommons.org/publicdomain/zero/1.0/`
- **Official Grant of Rights:** Under CC0 1.0 Universal Section 2: *"To the greatest extent permitted by, but not in contravention of, applicable law, Affirmer hereby overtly, fully, permanently, irrevocably and unconditionally waives, abandons, and surrenders all of Affirmer's Copyright and Related Rights..."*
- **Commercial Clause:** Fully permitted without royalty or copyright restriction.
- **Attribution Obligation:** Legally none, but full provenance records will be preserved in `dataset_manifest.json`.
- **Verdict:** Zero-friction enterprise clearance.

---

### D. SRC-05: Kaggle Insurance Claim Damage Dataset — **APPROVED**
- **Direct License Reference:** `https://www.apache.org/licenses/LICENSE-2.0`
- **Official Grant of Rights:** Under Section 2: *"Subject to the terms and conditions of this License, each Contributor hereby grants to You a perpetual, worldwide, non-exclusive, no-charge, royalty-free, irrevocable copyright license to reproduce, prepare Derivative Works of, publicly display, publicly perform, sublicense, and distribute the Work and such Derivative Works..."*
- **Commercial Clause:** Explicitly permitted for commercial and enterprise applications.
- **Attribution Obligation:** Maintain original Apache copyright notices in accompanying documentation.
- **Verdict:** Fully cleared.

---

### E. SRC-06: Wikimedia Commons Automotive Collections — **APPROVED (SELECTIVE)**
- **Direct License Reference:** Per-file licensing tags under Wikimedia Commons terms.
- **Selection Criteria:** Only images carrying **CC-BY 2.0 / 3.0 / 4.0**, **CC0**, or **Public Domain** will be ingested.
- **Copyleft Warning:** Images licensed under **CC BY-SA (Share-Alike)** are flagged as **CONDITIONAL** and excluded from the primary target pool to avoid legal ambiguity regarding whether internal model validation benchmarks trigger reciprocal share-alike licensing.
- **Verdict:** APPROVED for CC-BY and CC0 items.

---

### F. SRC-07: SKKU TQVCD Dataset — **REJECTED**
- **Documentary Finding:** Repository `dxlabskku/TQVCD` contains no `LICENSE` file.
- **Legal Status:** Under the Berne Convention and US/International copyright law, lack of an explicit license means **All Rights Reserved** by default. Public hosting on GitHub does not grant commercial use or offline modification rights.
- **Verdict:** REJECTED. Cannot be used without written bilateral licensing agreement.

---

### G. SRC-08: Mendeley Data SYNDCAR — **REJECTED**
- **Documentary Finding:** Licensed under CC BY-NC 4.0 (Non-Commercial) and composed entirely of 3D computer graphics.
- **Legal Status:** Non-commercial restriction prohibits commercial use; synthetic data violates the authenticity mandate.
- **Verdict:** REJECTED on dual legal and technical grounds.

---

### H. SRC-09: Salvage Auction Scraping (Copart / IAAI) — **REJECTED**
- **Documentary Finding:** Section 2 of Copart Terms of Service strictly prohibits: *"scraping, data mining, harvesting, crawling or using any automated means to access the Site for any purpose without our express written permission."*
- **Legal Status:** Ingesting scraped images constitutes an actionable breach of contract (CFAA / Computer Misuse).
- **Verdict:** REJECTED. Commercial enterprise ingestion without an API contract is illegal.

---

### I. SRC-10: Stock Photography Providers — **REJECTED**
- **Documentary Finding:** Standard Royalty-Free licenses from Getty Images and Adobe Stock prohibit: *"using content in machine learning, artificial intelligence, or biometric recognition technologies unless specifically authorized."*
- **Legal Status:** Requires custom enterprise AI training addenda; also violates user constraint against paid purchasing.
- **Verdict:** REJECTED.

---

## 3. Privacy, Consent & GDPR/CCPA Safeguards

Even with open copyright licensing (CC-BY, CC0, MIT, Apache), personal data rights are distinct from copyright:
1. **License Plates:** License plate numbers constitute Personal Identifiable Information (PII) under GDPR (Article 4) and CCPA.
2. **Identifiable Individuals:** Any person whose face or distinguishing body features appear in damage photos retains personality rights.
3. **Legal Compliance Action:** 100% of candidate images from approved sources will be processed through the PII scrubbing pipeline (solid black plate masking + facial blurring) prior to dataset lock.
