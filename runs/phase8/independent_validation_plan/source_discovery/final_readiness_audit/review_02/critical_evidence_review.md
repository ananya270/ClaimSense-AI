# ClaimSense AI — Phase 8: Critical Evidence-Based Acquisition Gate Review

**Document Version:** 2.0 (Forensic Gate Review)  
**Audit Date:** 2026-11-17  
**Scope:** Critical evidence-backed review of candidate vehicle damage image sources, image-level licensing scope, physical availability, and privacy controls  
**Target Independent Dataset:** `CarDD_Independent_Val_v1` (Target: 220–250 authentic images)  
**Execution Boundary:** **Strictly Audit-Only.** No downloads, no image ingestion, no annotation, no model training, no checkpoint modification, no external permission requests.

---

## 1. Forensic License Verification at Actual Image Level

A legally defensible machine learning pipeline requires establishing copyright title and licensing scope at the **individual image file level**, rather than relying on repository-level tags or platform dropdown selections.

### A. SRC-02: DrBimmer / Humans in the Loop
- **Exact Official URLs:**
  - *Root Institutional Release:* `https://humansintheloop.org/resources/datasets/car-parts-and-car-damages-dataset/`
  - *Institutional Kaggle Portal:* `https://www.kaggle.com/datasets/humansintheloop/car-parts-and-car-damages`
  - *Hugging Face Distribution Mirror:* `https://huggingface.co/datasets/DrBimmer/car-parts-and-damage-dataset`
- **Official License Declarations:**
  - *Root License:* **Creative Commons CC0 1.0 Universal (Public Domain Dedication)**
  - *Mirror License:* **MIT License** (applied by user DrBimmer on Hugging Face)
- **Image-Level License Scope:**  
  *Crucial Legal Distinction:* The MIT license attached by DrBimmer on Hugging Face is a software license designed for source code and converter scripts. However, the root publisher—**Humans in the Loop** (an international social enterprise specializing in ethical AI data annotation)—officially dedicated the entire dataset, including raw image files and polygon segmentation masks, to the public domain under **CC0 1.0 Universal**. Under CC0 Section 2, the affirmer overt and unconditionally surrenders all copyright and related rights in the material worldwide.
- **Publisher Authority Evidence:**  
  Humans in the Loop curated, commissioned, and managed the annotation of these 1,812 vehicle inspection images in 2020 through a structured trainee program in partnership with Beetroot Academy. While the institutional provenance is verified and widely cited, the documentation does not publish individual photographer release deeds. However, as an institutional open-access dataset published under CC0 1.0, it possesses the highest verifiable chain of title available in public computer vision research.
- **Commercial & Model Rights:**  
  CC0 1.0 explicitly allows commercial evaluation, model training, internal redistribution, adaptation, and model weight deployment without royalty or licensing restriction.
- **Attribution & Notice:**  
  Legally unconstrained under CC0; enterprise practice mandates preserving attribution: `"Humans in the Loop: Car Parts and Car Damages Dataset (CC0 1.0 Universal)"`.
- **Decision:** **APPROVED (Primary Anchor)**

---

### B. SRC-01: Roboflow Car Damage V5
- **Exact Official URL:** `https://universe.roboflow.com/car-damage/car-damage-v5`
- **Uploader / Curator:** User "Erkans Workspace"
- **Declared License:** Creative Commons Attribution 4.0 International (`CC BY 4.0`)
- **Image-Level License Scope:**  
  *Uploader-Selected vs. True Asset Ownership:* The CC BY 4.0 tag was chosen by uploader "Erkans Workspace" on Roboflow Universe. Under Section 4 and Section 8 of the Roboflow Terms of Use Agreement, uploaders represent they possess sufficient rights to license public datasets. However, Roboflow disclaims all title warranties and operates under DMCA Safe Harbor notice-and-takedown.
- **Publisher Authority Gap:**  
  There is zero documentary evidence that user Erkans Workspace took these 3,001 photographs, employed the photographers, or obtained copyright assignments from vehicle owners or insurance adjusters. Inspection of sample imagery shows varied international vehicles, body shop bays, and residential streets typical of web-aggregated search engine scraping.
- **Legal Risk:**  
  Under the common-law doctrine of *nemo dat quod non habet*, an uploader cannot grant a CC BY 4.0 license over photographs owned by third parties. While internal evaluation for benchmark validation might be argued under statutory Fair Use (17 U.S.C. § 107), Fair Use is an affirmative legal defense evaluated on a case-by-case balancing test—**not an absolute statutory guarantee**.
- **Decision:** **CONDITIONAL (Quarantined)**  
  *Blocking Condition:* Cannot be approved for unrestricted commercial pipeline use without documentary proof of uploader copyright authority. Permitted only as an auxiliary internal benchmark pool with strict non-redistribution and mandatory solid PII redaction.

---

### C. SRC-05: Kaggle Car Damage Dataset (vinayjose)
- **Exact Official URL:** `https://www.kaggle.com/datasets/vinayjose/car-damage-dataset`  
  *(Corrected from mistaken citation `arunrk7`, which hosts `surface-crack-detection` for concrete).*
- **Uploader / Curator:** User Vinay Jose
- **Declared License:** Apache License, Version 2.0 (Self-Reported)
- **Image-Level License Scope:**  
  *Software License Mismatch & Title Gap:* Apache 2.0 is authored by the Apache Software Foundation for software codebases. Section 2 grants copyright licenses from "each Contributor" for "Contributions" authored by them. Vinay Jose assembled ~8,080 vehicle damage claim photographs paired with a CSV classification file for insurance fraud prediction research.
- **Publisher Authority Gap:**  
  The photographs originate from automobile insurance damage claim files, appraisal walkarounds, and accident scenes. Vinay Jose does not hold copyright ownership over the thousands of insurer claim photos. Applying an Apache 2.0 license to third-party claim photos is legally ineffective regarding the underlying imagery.
- **Legal Risk:**  
  Incorporating third-party insurance claim photos carries potential copyright infringement claims and privacy liabilities if policyholder details or registration tags are exposed.
- **Decision:** **CONDITIONAL (Quarantined)**  
  *Blocking Condition:* Apache 2.0 does not legally cover the photographs. Usable strictly within an internal, non-redistributed benchmarking sandbox under a documented internal Fair Use risk assessment.

---

### D. SRC-06: Wikimedia Commons Automotive Damage Collections
- **Exact Official Category URLs:**
  - `https://commons.wikimedia.org/wiki/Category:Damaged_automobiles`
  - `https://commons.wikimedia.org/wiki/Category:Flat_tires`
  - `https://commons.wikimedia.org/wiki/Special:Search?query=Automobile+hail+damage`
  - `https://commons.wikimedia.org/wiki/Category:Broken_car_windows`
- **Curator / Host:** Wikimedia Foundation & Global Contributor Community
- **Documented Licenses:** Individual per-file deeds: **CC0, Public Domain, CC BY 2.0/3.0/4.0, and CC BY-SA 2.0/3.0/4.0**.
- **Image-Level License Scope:**  
  Unlike platforms that apply a single blanket tag, Wikimedia Commons requires every single image file to carry an independent description page with verified contributor identity, camera EXIF metadata, and exact license text.
- **The Share-Alike (CC BY-SA) Copyleft Risk:**  
  A significant portion of Wikimedia files is licensed under **CC BY-SA (Share-Alike)**. In computer vision and intellectual property law, whether training a deep neural network on CC BY-SA imagery creates an "Adapted Work" or "Derivative Work" that legally obligates the developer to release the trained model weights under CC BY-SA is an **unresolved legal question**.  
  *Strict Risk Control:* To prevent copyleft contamination of ClaimSense AI models, **all CC BY-SA files are strictly REJECTED**. Only files independently verified as **CC0, Public Domain, or CC BY (unrestricted derivative creation)** are eligible for acquisition.
- **Attribution & Notice:**  
  For CC BY files, Section 3 mandates citing author credit, source link, and license deed (e.g. `"Photo by [Contributor], Wikimedia Commons, CC BY 4.0"`).
- **Decision:** **APPROVED (Selective Per-File Filter)**

---

### E. Disqualified Sources (SRC-03 & SRC-04)
- **SRC-03 (anujms / Kaggle):** Official URL `https://www.kaggle.com/datasets/anujms/car-damage-detection`. Forensic verification reveals **no open-source or Creative Commons license tag**. It is an unlicensed 2018 web scrape. **Status: REJECTED.**
- **SRC-04 (lplenka / Kaggle):** Official URL `https://www.kaggle.com/datasets/lplenka/coco-car-damage-detection-dataset`. Contains **only 80 total images** and **zero flat tire images**. Incapable of supporting statistical volume or targeted classes. **Status: REJECTED (Deprecated).**

---

## 2. Physical Availability vs. Realistic Usable Estimates

Projected instance yields must not be described as "guaranteed" or "statistically robust" prior to physical ingestion. Computer vision data curation exhibits inevitable fallout due to optical blur, low resolution, ambiguous damage boundaries, and PII conflicts.

The table below strictly separates **documented facts**, **verified physical counts**, **legally cleared counts**, and **estimated usable counts post-screening**:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        Physical Availability & Usability Funnel                        │
├────────┬─────────────────┬──────────┬──────────┬──────────┬──────────┬─────────────────┤
│ Source │ Source Name     │ Doc Count│ Ver Count│ Access   │ Cleared  │ Est Usable Post-│
│ ID     │                 │ (Card)   │ (Audit)  │ Count    │ Count    │ Screening       │
├────────┼─────────────────┼──────────┼──────────┼──────────┼──────────┼─────────────────┤
│ SRC-02 │ DrBimmer / HITL │ 1,812    │ 1,812    │ 1,812    │ 1,812    │ ~115 (Targeted) │
│ SRC-06 │ Wikimedia Comm. │ 10,000+  │ ~1,200*  │ ~1,200   │ ~350**   │ ~60 (Targeted)  │
│ SRC-01 │ Roboflow V5     │ 3,001    │ 3,001    │ 3,001    │ 0***     │ ~35 (Internal)  │
│ SRC-05 │ Kaggle Insurance│ 8,080    │ 8,080    │ 8,080    │ 0***     │ ~25 (Internal)  │
│ SRC-03 │ Kaggle anujms   │ ~2,300   │ ~2,300   │ ~2,300   │ 0        │ 0 (Rejected)    │
│ SRC-04 │ Kaggle lplenka  │ 80       │ 80       │ 80       │ 80       │ 0 (Deprecated)  │
└────────┴─────────────────┴──────────┴──────────┴──────────┴──────────┴─────────────────┤
│ Total  │ Target Portfolio│ 25,273   │ 16,473   │ 16,473   │ 2,242    │ 235 Target Imgs │
└────────┴─────────────────┴──────────┴──────────┴──────────┴──────────┴─────────────────┘
```
*\*Approximate verified candidate files across target sub-categories (`Flat_tires`, `Broken_car_windows`, `Damaged_automobiles`, `Automobile_hail_damage`).*  
*\*\*Files strictly verified as CC0, Public Domain, or CC BY (excluding CC BY-SA).*  
*\*\*\*Legally cleared for commercial distribution: 0. Cleared for internal evaluation under Fair Use: conditional.*

### Realistic Target Quotas & Yield Uncertainties:
- **Tire Flat (Target: 30+ instances):** Requires approximately 25–28 dedicated images from Wikimedia Commons `Category:Flat_tires`. If screening eliminates 20% due to blur or tire bead ambiguity, a candidate pool of at least 40 images must be reviewed.
- **Crack (Target: 60+ instances):** Sourced from SRC-02 `Cracked` class. Inspection must filter out superficial paint scratches that do not penetrate plastic bumper substrates.
- **Screening Fallout Assumption:** We estimate an intake fallout rate of **25%–35%** during automated blur, resolution, and PII checks. To secure 235 usable images, approximately **320–350 raw candidate images** must be staged.

---

## 3. Privacy, Provenance & Technical Redaction Review

### Defensible Analysis of Redaction & Information Loss
We specifically avoid absolute claims such as "mathematically impossible reconstruction" without engineering context. 

1. **Solid Opaque Masking Analysis:**
   - Setting pixel values within a bounding box to $[0, 0, 0]$ (black fill) destroys the underlying pixel intensity values. Inversion of the interior pixel data is mathematically impossible because the original matrix elements are replaced with a constant scalar.
   - *Residual Information Risks:* However, solid masking introduces **boundary high-frequency step artifacts**. Furthermore, privacy leaks can persist through:
     - Unmasked reflections of license plate numbers or human faces on polished car panels or chrome bumpers.
     - Partial alphanumeric characters visible on edge borders if the bounding box is not dilated.
     - Contextual metadata (e.g. state inspection stickers, dealer license plate frames identifying specific municipalities).
   - *Technical Mitigation:* The pipeline must enforce **bounding box dilation by $\ge 15\%$** around detected plate coordinates to capture edge characters and reflection flares.
2. **Impact on Model Usability:**
   - Applying black rectangular masks over license plates and badges alters the receptive field of convolutional and transformer layers.
   - If damage (e.g. bumper crack or grill dent) directly abuts a license plate bracket, solid masking could occlude part of the damage contour.
   - *Rule:* If solid PII masking occludes more than **20% of a damage instance**, the image must be **rejected from the validation dataset** rather than compromised.
3. **Dual-Layer Provenance Integrity:**
   - **Layer 1 (Public ML Image):** Image files are stripped of all EXIF headers (`piexif.remove`), ensuring no accidental leakage of GPS latitude/longitude, camera serial numbers, or owner names.
   - **Layer 2 (Immutable Audit Manifest):** Stored in `dataset_manifest.json` outside the image files:
     - Cryptographic SHA-256 hash of original unredacted file.
     - Cryptographic SHA-256 hash of redacted file.
     - Perceptual difference hash (64-bit dHash and pHash).
     - Full URL, author credit, license name, and date of acquisition.
     - Technical capture settings (ISO, focal length) retained without personal identifiers.

---

## 4. Source-by-Source Decision Register

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        Source Acquisition Decision Register                            │
├────────┬───────────────────────────┬──────────────┬────────────────────────────────────┤
│ ID     │ Source Name               │ Decision     │ Primary Evidence & Conditions      │
├────────┼───────────────────────────┼──────────────┼────────────────────────────────────┤
│ SRC-02 │ DrBimmer / Humans in Loop │ APPROVED     │ CC0 1.0 Universal institutional    │
│        │                           │              │ dedication by Humans in the Loop.  │
├────────┼───────────────────────────┼──────────────┼────────────────────────────────────┤
│ SRC-06 │ Wikimedia Commons         │ APPROVED     │ Per-file CC0/CC-BY verified deeds. │
│        │                           │              │ CC BY-SA strictly excluded.        │
├────────┼───────────────────────────┼──────────────┼────────────────────────────────────┤
│ SRC-01 │ Roboflow Universe V5      │ CONDITIONAL  │ Uploader chain of title unverified.│
│        │                           │              │ Quarantined for internal eval only.│
├────────┼───────────────────────────┼──────────────┼────────────────────────────────────┤
│ SRC-05 │ Kaggle Insurance (vinay)  │ CONDITIONAL  │ Apache 2.0 does not cover photos.  │
│        │                           │              │ Quarantined for internal eval only.│
├────────┼───────────────────────────┼──────────────┼────────────────────────────────────┤
│ SRC-03 │ Kaggle anujms             │ REJECTED     │ No license tag; unlicensed scrape. │
├────────┼───────────────────────────┼──────────────┼────────────────────────────────────┤
│ SRC-04 │ Kaggle lplenka            │ REJECTED     │ Only 80 images; zero flat tires.   │
└────────┴───────────────────────────┴──────────────┴────────────────────────────────────┘
```

---

## 5. Exact Evidence Required Before Authorization

Prior to executing physical image downloads or dataset staging, the following evidentiary items must be formally verified:

1. **For SRC-06 (Wikimedia Commons):**
   - An automated script query must generate an itemized manifest of candidate Wikimedia URLs verifying that every individual file carries a `CC0`, `Public Domain`, or `CC BY` license tag on Wikimedia Commons API, with zero `CC BY-SA` files admitted.
2. **For SRC-01 & SRC-05 (Conditional Sources):**
   - Formal sign-off on the **Internal Fair Use Risk Evaluation** confirming that images from Roboflow V5 and Vinay Jose Kaggle will be stored exclusively in a secure, access-controlled directory, will not be distributed externally or packaged into public commercial software, and will be used strictly for offline validation benchmark scoring.
3. **Privacy Redaction Dilation Specification:**
   - Validation that the automated PII masking pipeline dilates bounding boxes by 15% and enforces mandatory human inspector verification of reflection channels.
