# ClaimSense AI — Image-Level License Scope Matrix

**Document Version:** 2.0 (Forensic Asset-Level Matrix)  
**Audit Date:** 2026-11-17  
**Scope:** Forensic evaluation of image-level copyright title, licensing clauses, derivative rights, and third-party restrictions  
**Target Independent Dataset:** `CarDD_Independent_Val_v1` (Target: 220–250 authentic images)  
**Execution Restriction:** Strictly Audit-Only. No image downloads, no scraping, no model modifications.

---

## 1. Comprehensive Image-Level Licensing Matrix

| Attribute / Source ID | **SRC-01: Roboflow Car Damage V5** | **SRC-02: DrBimmer / Humans in the Loop** | **SRC-03: Kaggle COCO (anujms)** | **SRC-04: Kaggle Damage (lplenka)** | **SRC-05: Kaggle Insurance (vinayjose)** | **SRC-06: Wikimedia Commons Collections** |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Exact Official URL** | `https://universe.roboflow.com/car-damage/car-damage-v5` | Root: `https://humansintheloop.org/resources/datasets/car-parts-and-car-damages-dataset/`<br>Mirror: `https://huggingface.co/datasets/DrBimmer/car-parts-and-damage-dataset` | `https://www.kaggle.com/datasets/anujms/car-damage-detection` | `https://www.kaggle.com/datasets/lplenka/coco-car-damage-detection-dataset` | `https://www.kaggle.com/datasets/vinayjose/car-damage-dataset` | `https://commons.wikimedia.org/wiki/Category:Damaged_automobiles`<br>`https://commons.wikimedia.org/wiki/Category:Flat_tires` |
| **Declared License** | CC BY 4.0 (Uploader chosen) | Root: **CC0 1.0 Universal**<br>Mirror: MIT License | **None / Unspecified** | CC0 1.0 Universal (Self-reported) | Apache License, Version 2.0 (Self-reported) | **CC0, Public Domain, or CC BY** (Selective per-file audit) |
| **Exact License Clause** | Section 2(a)(1): Worldwide, royalty-free license to reproduce and adapt material. | CC0 Section 2: Permanent, irrevocable waiver of all copyright & neighboring rights. | None. Standard Kaggle Terms of Use apply. | CC0 Section 2: Waiver of all copyright & neighboring rights. | Section 2: Perpetual copyright grant from Contributor for Contributions. | Individual per-file deeds (e.g., CC BY 4.0 Section 2 or CC0 waiver). |
| **Does License Cover Images?** | **Ambiguous / Unverified.** Tag applies to workspace; underlying photos are unverified web aggregations. | **YES.** Institutional publisher explicitly dedicated raw image files + polygon masks to CC0. | **NO.** No license attached to imagery. | **Ambiguous.** Small 80-image tutorial set; uploader chain unverified. | **NO.** Apache 2.0 covers software/code; does not legitimately cover third-party claims photos. | **YES.** Wikimedia requires each individual file page to carry its own binding license deed. |
| **Publisher Authority Evidence** | **None.** Roboflow disclaims title; user "Erkans Workspace" provides no ownership proof. | **Documented Institutional Program.** Commissioned and annotated by Humans in the Loop & Beetroot Academy. | **None.** Scraped 2018 web images for tutorial. | **None.** Student export from VGG annotator. | **None.** Practitioner aggregated insurer claim photos for fraud study. | **Verified Individual Records.** Camera EXIF metadata, contributor history, admin review. |
| **Commercial Internal Eval Rights** | Conditional under Fair Use (17 U.S.C. § 107); not guaranteed by license. | **Explicitly Permitted.** CC0 permits all commercial uses worldwide. | **Prohibited.** Unlicensed copyrighted photos. | Permitted under CC0, but volume is trivial (80 imgs). | Conditional under Fair Use; not guaranteed by license. | **Explicitly Permitted.** CC0 and CC BY authorize commercial computational evaluation. |
| **Model Training & Derivative Rights** | Training permitted internally; commercial derivative rights legally exposed. | **Explicitly Permitted.** Model weights, fine-tuning, and adaptations unrestricted. | **Prohibited.** Copyright infringement liability. | Permitted under CC0, but useless scale. | Training permitted internally under Fair Use; derivative distribution exposed. | **Explicitly Permitted.** (Subject to strict exclusion of CC BY-SA files). |
| **Redistribution Restrictions** | Public redistribution of raw images prohibited due to copyright risk. | **None.** Unrestricted redistribution allowed under CC0. | Redistribution strictly prohibited. | Negligible scale. | Public redistribution of raw claim photos prohibited. | Raw images redistributable with CC BY attribution (or zero restriction for CC0). |
| **Attribution Requirements** | Retain credit to "Erkans Workspace / Roboflow Universe". | Voluntary credit to "Humans in the Loop (CC0 1.0)". | N/A (Excluded). | Voluntary credit to "LPLenka (CC0 1.0)". | Retain Apache notice in dataset documentation. | **Mandatory for CC BY:** Cite photographer, source link, and license deed. None for CC0. |
| **Third-Party Rights & PII** | Visible license plates and shop signage; no privacy releases. | Vehicle inspection photos; visible registration plates require solid masking. | Unconstrained web photos with visible plates and faces. | Minor vehicle plates. | Authentic insurance claims; visible registration, VIN tags, repair bills. | Public street photography; visible license plates require solid masking. |
| **Final Decision Status** | **CONDITIONAL (Quarantined)** | **APPROVED (Primary Anchor)** | **REJECTED** | **REJECTED (Deprecated)** | **CONDITIONAL (Quarantined)** | **APPROVED (Selective Filter)** |

---

## 2. In-Depth Legal Analysis of Approved & Conditional Sources

### A. SRC-02: DrBimmer / Humans in the Loop — **APPROVED**
- **Chain of Title Synthesis:**  
  The root dataset was officially published by Humans in the Loop under Creative Commons CC0 1.0 Universal on their official website and Kaggle portal. When DrBimmer mirrored the dataset on Hugging Face, the repository was tagged "MIT". Under copyright law, an MIT license on a repository containing public-domain (CC0) content does not restrict the underlying content: public domain material cannot be retroactively restricted. Therefore, ClaimSense AI relies directly on the **root CC0 1.0 Universal dedication**, which provides unassailable commercial evaluation, model training, and internal adaptation rights.
- **Residual Risk:**  
  While the copyright title is unassailable, the photographs feature vehicles in body shops and outdoor inspection bays where European and international license plates are visible. Under GDPR Article 4(1), license plates constitute personal data. Solid opaque masking ($[0,0,0]$ black box) is legally required.

### B. SRC-06: Wikimedia Commons — **APPROVED (SELECTIVE)**
- **Chain of Title Synthesis:**  
  Wikimedia Commons enforces strict evidentiary standards: every uploaded photograph must have a verified author, upload date, camera metadata, and an explicit Creative Commons or Public Domain deed.
- **The Copyleft Quarantine Rule:**  
  Files licensed under **CC BY-SA (Share-Alike)** are **categorically disqualified**. If CC BY-SA images were ingested into a training or fine-tuning set, copyright holders could assert that resulting neural network weights constitute an "Adapted Work" under Section 1(a) of CC BY-SA 4.0, triggering reciprocal open-sourcing obligations for proprietary ClaimSense AI models.  
  *Operational Rule:* Only files verified via MediaWiki API as carrying `CC0`, `Public Domain`, or `CC BY 2.0/3.0/4.0` will be ingested.

### C. SRC-01 (Roboflow V5) & SRC-05 (Vinay Jose Kaggle) — **CONDITIONAL**
- **The Fair Use Assessment (17 U.S.C. § 107):**  
  Neither source possesses verified asset-level copyright title. However, internal machine learning validation—where images are stored in an access-controlled development environment, are analyzed solely to extract bounding box accuracy metrics, and are never served to end-users or bundled into distributed software—presents a strong non-infringing Fair Use profile (*Authors Guild v. Google, Inc.*, 804 F.3d 202).
- **Mandatory Conditions for Use:**
  1. *Quarantine Boundary:* Stored strictly within `datasets/CarDD_Independent_Val_v1/quarantine_internal/`.
  2. *Zero Redistribution:* Raw images from SRC-01 and SRC-05 will never be redistributed, publicly hosted, or included in client deliverables.
  3. *Strict Volume Cap:* Sourced at no more than 35 images (SRC-01) and 25 images (SRC-05) to maintain Tier 1 predominance (>70% Tier 1).

### D. SRC-03 (anujms) & SRC-04 (lplenka) — **REJECTED**
- **SRC-03:** Completely unlicensed web scrape. Discarded to prevent unnecessary copyright infringement exposure.
- **SRC-04:** While tagged CC0, the physical dataset contains only 80 images, lacks the critical target classes (zero flat tires), and adds no material value over SRC-02 and SRC-06. Discarded to eliminate administrative overhead.
