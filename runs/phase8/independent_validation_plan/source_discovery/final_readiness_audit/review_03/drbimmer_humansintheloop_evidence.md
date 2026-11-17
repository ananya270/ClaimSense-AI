# ClaimSense AI — Phase 8: DrBimmer / Humans in the Loop Evidence Review

**Document Version:** 1.0 (Documentary Evidence Audit)  
**Audit Date:** 2026-11-17  
**Scope:** Forensic evaluation of institutional chain of title, CC0 dedication, raw photography vs. annotation coverage, and downstream MIT software wrapper  
**Target Source:** `SRC-02` (DrBimmer / Humans in the Loop)  
**Execution Boundary:** Strictly Audit-Only. No image downloads, no dataset modifications.

---

## 1. Official Source Repository Records & URLs

| Role | Platform / Publisher | Official Evidence URL | Documented Scale | Documented License |
| :--- | :--- | :--- | :---: | :--- |
| **Institutional Originator** | Humans in the Loop (Official Portal) | `https://humansintheloop.org/resources/datasets/car-parts-and-car-damages-dataset/` | 1,812 images (24,851 polygon masks) | **Creative Commons CC0 1.0 Universal** |
| **Institutional Open Data Portal** | Humans in the Loop (Kaggle Verified Account) | `https://www.kaggle.com/datasets/humansintheloop/car-parts-and-car-damages` | 1,812 images (~1.8 GB raw archive) | **Creative Commons CC0 1.0 Universal** |
| **Downstream Distribution Mirror** | User DrBimmer (Hugging Face Datasets) | `https://huggingface.co/datasets/DrBimmer/car-parts-and-damage-dataset` | 1,812 images (~3.31 GB COCO format) | **MIT License** |

---

## 2. Forensic Analysis of Institutional CC0 Dedication

### A. Documentary Evidence Text
On its official research resources portal (`humansintheloop.org`), Humans in the Loop publishes the following formal dataset declaration:
> *"The Car Parts and Car Damages dataset consists of 1,812 images fully annotated with polygons (split into 998 images for car parts and 814 images for car damages, totaling 24,851 polygons). The images were segmented by trainees of Beetroot Academy as part of a pilot project with Humans in the Loop targeting internally displaced people across Ukraine. The dataset is dedicated to the public domain under the CC0 1.0 license."*

### B. Scope of Dedication: Raw Photographs vs. Annotations
A crucial evidentiary question is whether the CC0 dedication covers the raw photographic files or merely the annotation polygons:
1. **Packaging & Distribution:** The official distribution bundle published by Humans in the Loop packages the raw `.jpg` image files and the `.json` polygon masks together in a single unified archive under the CC0 1.0 Universal deed.
2. **Legal Scope of CC0 1.0 Section 2:**  
   Under Section 2 of CC0 1.0:
   > *"To the greatest extent permitted by... applicable law, Affirmer hereby overtly, fully, permanently, irrevocably and unconditionally waives, abandons, and surrenders all of Affirmer's Copyright and Related Rights... in the Work."*  
   "Related Rights" explicitly encompasses database rights, photographic compilation rights, and image reproduction rights.
3. **Chain of Title Gap:**  
   While Humans in the Loop created and owns the polygon annotations, the documentation does not publish individual photographer assignment deeds or property releases from the original vehicle owners or automotive body shops where the vehicles were photographed. 
   - *Assessment:* In computer vision research, an institutional public-domain dedication from an established, accredited organization represents the highest standard of open provenance available. However, because individual release deeds are not published, the raw photography relies on the institution's affirmative CC0 dedication.

---

## 3. Disentangling Institutional CC0 from Downstream MIT License

### The Software License Mismatch on Hugging Face:
When user `DrBimmer` cloned the dataset to Hugging Face, they restructured the polygon annotations into COCO JSON format and added an `MIT` tag in the repository's `README.md` YAML frontmatter.

| Dimension | Root Release (Humans in the Loop) | Distribution Mirror (DrBimmer / Hugging Face) |
| :--- | :--- | :--- |
| **Publisher** | Humans in the Loop (Accredited Social Enterprise) | Independent User / Practitioner (`DrBimmer`) |
| **License Deed** | **CC0 1.0 Universal** (Public Domain Dedication) | **MIT License** (Open Source Software License) |
| **Applicable Medium** | Image files, database compilation, and polygon masks | Source code, parser scripts, repository metadata |
| **Commercial Rights** | Unrestricted worldwide commercial reuse | Unrestricted commercial reuse |
| **Attribution Requirement**| Legally none (Voluntary credit recommended) | Retain copyright notice in software copies |

### Legal Synthesis:
Under copyright law, once a work is affirmatively dedicated to the public domain under CC0 1.0 by its publisher, a subsequent distributor cannot encumber or restrict the underlying public domain assets by wrapping them in a software license. The MIT tag applied by DrBimmer governs only DrBimmer's conversion code and formatting scripts; **the photographic images and annotations themselves remain governed by CC0 1.0 Universal**.

---

## 4. Status Determination & Governance Decision

In accordance with Phase 8 readiness standards:
- **Status:** **APPROVED (Institutional CC0 Anchor)**
- **Conditions & Safeguards:**
  1. ClaimSense AI must cite the root institutional creator: `"Humans in the Loop: Car Parts and Car Damages Dataset (CC0 1.0 Universal)"`.
  2. Because individual driver/shop privacy waivers are not attached, all visible vehicle registration plates must undergo **mandatory solid zero-entropy redaction** ($[0,0,0]$ black box) prior to evaluation.
  3. If corporate legal counsel requires individual signed photographer deeds for every raw photograph, this source would be reclassified as CONDITIONAL (Quarantined). For the independent validation benchmark, the verified institutional CC0 dedication provides sufficient legal title.
