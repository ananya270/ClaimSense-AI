# ClaimSense AI — Independent Validation Dataset: Source Risk Register

**Document Version:** 1.0  
**Audit Date:** 2026-11-17  
**Scope:** Risk identification, impact rating, and mitigation protocols for candidate vehicle damage image sources  
**Target Independent Dataset:** `CarDD_Independent_Val_v1` (Target: 220–250 authentic images)  
**Execution Restriction:** Audit only. No image downloads, no scraping, no model fine-tuning.

---

## 1. Risk Governance Overview

Evaluating and deploying an independent real-world validation dataset for an insurance-claim AI product involves multi-dimensional risks spanning legal liability, computational integrity, privacy compliance, and model generalizability. 

This Risk Register establishes a formal risk taxonomy across five core dimensions:
1. **Legal & Intellectual Property Risks (LGL)**
2. **Data Quality & Sensor Artifact Risks (QLT)**
3. **Privacy & Regulatory Compliance Risks (PRV)**
4. **Domain Shift & Operational Bias Risks (DSH)**
5. **Provenance & Dataset Integrity Risks (PRV-INT)**

Risk severity is evaluated on a $5 \times 5$ matrix where $\text{Risk Score} = \text{Likelihood} \times \text{Impact}$ (Scale 1–25: Low 1–6, Medium 7–14, High 15–19, Critical 20–25).

---

## 2. Risk Matrix Summary

| Risk ID | Risk Dimension | Risk Description | Likelihood (1–5) | Impact (1–5) | Score (1–25) | Severity Level | Mitigation Status |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **LGL-01** | Legal / IP | Ingestion of images with ambiguous provenance or missing commercial rights | 4 | 5 | **20** | **CRITICAL** | Mitigated by Strict White-List |
| **LGL-02** | Legal / IP | Viral Copyleft Contamination (e.g., CC BY-SA, GPL derivatives) | 3 | 5 | **15** | **HIGH** | Exclude Share-Alike licenses |
| **LGL-03** | Legal / IP | Breach of Platform Terms of Service (automated scraping of Copart/IAAI) | 5 | 5 | **25** | **CRITICAL** | Fully Rejected (`SRC-09`) |
| **PRV-01** | Privacy / PII | Visible license plates and registration tags in claim photos | 5 | 4 | **20** | **CRITICAL** | Automated & Manual Blur Gate |
| **PRV-02** | Privacy / PII | Identifiable human faces (technicians, owners, bystanders) | 4 | 4 | **16** | **HIGH** | Face Anonymization & Crop |
| **PRV-03** | Privacy / PII | Embedded GPS / EXIF geolocation metadata | 4 | 3 | **12** | **MEDIUM** | Automated Metadata Stripping |
| **QLT-01** | Quality | Low resolution (<640×640) or severe digital compression artifacts | 4 | 4 | **16** | **HIGH** | Minimum Resolution Gate |
| **QLT-02** | Quality | Watermarks, timestamps, camera HUD overlays, and shop banners | 3 | 3 | **9** | **MEDIUM** | Automated & Manual OCR Gate |
| **QLT-03** | Quality | Severe camera motion blur or out-of-focus optics | 3 | 3 | **9** | **MEDIUM** | Laplacian Blur Filter Gate |
| **DSH-01** | Domain Shift | Severe salvage total-loss bias vs minor consumer insurance claims | 4 | 4 | **16** | **HIGH** | Stratified Claim-Severity Quota |
| **DSH-02** | Domain Shift | Workshop background artifacts (lifts, machinery, fluorescent glare) | 3 | 3 | **9** | **MEDIUM** | Natural Environment Balance |
| **DSH-03** | Domain Shift | Vehicle fleet demographic skew (exotic models vs consumer sedans/SUVs) | 2 | 3 | **6** | **LOW** | Fleet Demographic Filter |
| **INT-01** | Provenance | Cross-source duplicate images (circular scraping across public datasets) | 4 | 3 | **12** | **MEDIUM** | SHA256 & Perceptual Hashing |
| **INT-02** | Provenance | Trusting unverified external labels as gold-standard ground truth | 5 | 4 | **20** | **CRITICAL** | Dual-Blind Re-Annotation |

---

## 3. In-Depth Risk Analyses and Mitigation Strategies

### Dimension 1: Legal & Intellectual Property

#### `LGL-01`: Ambiguous Ingestion & Missing Commercial Rights
- **Threat Vector:** Many public repositories on GitHub, Kaggle, or Google Drive aggregate images scraped from Google Images or vehicle insurance portals without explicit copyright licenses. Under US Code Title 17 and international copyright law, unlicensed works remain "All Rights Reserved" to the original photographer.
- **Impact:** Statutory copyright infringement damages, forced deletion of training checkpoints, enterprise commercial liability.
- **Mitigation Protocol:** 
  1. Enforce strict blacklisting of any repository lacking an explicit `LICENSE` file (`SRC-07` SKKU TQVCD rejected).
  2. Restrict ingestion exclusively to sources with verifiable enterprise-cleared licenses: CC BY 4.0 (`SRC-01`), MIT (`SRC-02`), CC0 (`SRC-03`, `SRC-04`), Apache 2.0 (`SRC-05`), and verified CC-BY/CC0 Wikimedia items (`SRC-06`).
  3. Every ingested image must have its direct repository commit, URL, and license text logged in `dataset_manifest.json`.

#### `LGL-02`: Viral Copyleft Contamination (Share-Alike)
- **Threat Vector:** Creative Commons Attribution-ShareAlike (CC BY-SA 3.0 / 4.0) requires any derivative work to be distributed under the same license. In machine learning, whether model weights or benchmark outputs derived from CC BY-SA data constitute "Adapted Material" is legally unsettled and carries risk for proprietary commercial software.
- **Impact:** Risk of copyleft obligations extending to proprietary models or evaluation suites.
- **Mitigation Protocol:**
  1. Disallow CC BY-SA images from the primary candidate pool.
  2. For Wikimedia Commons (`SRC-06`), filter explicitly for CC0, Public Domain, or CC BY (unrestricted derivative creation) licenses only.

#### `LGL-03`: Breach of Terms of Service (Auction Scraping)
- **Threat Vector:** Commercial salvage platforms (Copart, IAAI) have strict anti-scraping clauses in their Terms of Service (CFAA enforceable).
- **Impact:** IP blacklisting, legal cease-and-desist, reputational damage.
- **Mitigation Protocol:** Strict zero-tolerance ban on automated scraping of commercial platforms (`SRC-09` permanently REJECTED).

---

### Dimension 2: Privacy & Regulatory Compliance

#### `PRV-01`: Visible Vehicle License Plates and VINs
- **Threat Vector:** Vehicle damage photographs taken on public roads or at body shops frequently capture state/national license plates and VIN barcodes in windshield corners. Under GDPR (Article 4) and California CPRA, license plates linked to registered vehicle owners constitute Personally Identifiable Information (PII).
- **Impact:** Heavy regulatory fines (GDPR Article 83 up to €20M), privacy complaints, inability to distribute evaluation reports.
- **Mitigation Protocol:**
  1. **Automated Anonymization Stage:** Run a high-recall license plate detection model (e.g. YOLO-Plate detector) followed by Gaussian blurring ($31 \times 31$ kernel) or black rectangular masking over all license plates.
  2. **Manual Inspection Stage:** Reviewer 1 and Reviewer 2 in the Phase 8 Dual-Blind review must verify 100% masking of all visible license plates and VIN tags prior to dataset promotion.

#### `PRV-02`: Identifiable Human Faces
- **Threat Vector:** Body shop technicians, towing operators, or vehicle owners often appear in reflection or standing adjacent to damaged panels.
- **Impact:** Biometric privacy violations (e.g., Illinois BIPA), GDPR right to privacy.
- **Mitigation Protocol:**
  1. Apply automated facial detection and aggressive pixelation/blurring.
  2. If a human subject occupies more than 15% of the frame or obstructs damage, reject the image entirely from the validation benchmark.

#### `PRV-03`: Embedded EXIF Geolocation Metadata
- **Threat Vector:** Smartphone JPEG/HEIC files contain EXIF metadata including precise latitude/longitude coordinates, device serial numbers, and acquisition timestamps.
- **Impact:** Unintentional disclosure of private residential addresses or accident locations.
- **Mitigation Protocol:**
  1. Run an automated EXIF scrubbing script (`PIL.ImageOps.exif_transpose` followed by saving without `exif_bytes`) on every ingested image.
  2. Retain technical metadata (resolution, color space) in `dataset_manifest.json` while stripping all personal and GPS tags.

---

### Dimension 3: Data Quality & Sensor Artifacts

#### `QLT-01`: Low Resolution and Heavy Compression
- **Threat Vector:** Web-scraped thumbnails or heavily compressed JPEG images introduce block DCT artifacts, ringing around edges, and blur that obscure hairline cracks and scratches.
- **Impact:** False negatives during evaluation; model penalized for sensor limitations rather than detection capability.
- **Mitigation Protocol:**
  1. Enforce strict minimum resolution threshold: **Width $\ge 800\text{ px}$ and Height $\ge 600\text{ px}$** (or equivalent 0.48 MP minimum).
  2. Reject any image exhibiting severe JPEG compression quantization artifacts (structural similarity index SSIM degradation).

#### `QLT-02`: Watermarks, Timestamps, and HUD Overlays
- **Threat Vector:** Insurance appraisal apps, body shop cameras, or stock aggregators frequently stamp dates, timecodes, claims numbers, or company watermarks across images.
- **Impact:** Deep neural networks may develop spurious correlations (e.g. associating yellow timestamp text with severe collision damage).
- **Mitigation Protocol:**
  1. Reject any candidate image where watermarks or text overlays overlap with the damaged vehicle region.
  2. Minor perimeter date stamps outside the vehicle silhouette must be cropped or inpainted prior to final inclusion.

#### `QLT-03`: Motion Blur & Optical Defocus
- **Threat Vector:** Low-light handheld inspection photos suffer from hand shake and slow shutter speeds.
- **Impact:** Fine scratches and plastic cracks become indistinguishable from shadows.
- **Mitigation Protocol:** Compute the Laplacian variance of each candidate image:
  $$\text{Var}(\nabla^2 I) < 100 \implies \text{Flagged as Blurry / Rejected}$$

---

### Dimension 4: Domain Shift & Operational Bias

#### `DSH-01`: Catastrophic Total-Loss Salvage Bias
- **Threat Vector:** Salvage auction repositories skew heavily towards rollover crashes, burned vehicles, and totaled chassis. In real-world insurance claim intake, 75%+ of claims represent minor to moderate repairable damage (parking lot dents, curb rash, bumper scuffs, windshield chips).
- **Impact:** Over-indexing on catastrophic crush damage causes models to fail on high-volume consumer claims.
- **Mitigation Protocol:**
  - Enforce a 3-tier severity stratification quota:
    - **Minor Damage (Cosmetic):** 40% (88–100 images) — scratches, dings, rock chips, minor cracks.
    - **Moderate Damage (Repairable):** 40% (88–100 images) — bumper fascia splits, dented quarter panels, broken lamps, flat tires.
    - **Severe Damage (Structural):** 20% (44–50 images) — crushed fenders, frame deformation, shattered windows.

#### `DSH-02`: Background and Environmental Distortion
- **Threat Vector:** Images captured exclusively inside mechanic repair bays feature hydraulic lifts, tool chests, and intense overhead fluorescent tubes that cast harsh specular highlights.
- **Impact:** Session 2 and Session 4 calibration studies proved that specular reflections are the #1 source of false positive dent detections.
- **Mitigation Protocol:** Mandate environmental balance: at least 60% of validation images must be outdoor natural lighting (driveways, parking lots, street curbs, overcast/sunny skies).

---

### Dimension 5: Provenance & Dataset Integrity

#### `INT-01`: Circular Scraping and Cross-Source Duplication
- **Threat Vector:** Public Kaggle and Roboflow datasets often fork or re-upload identical images from earlier research papers or public Flickr albums.
- **Impact:** Data leakage between validation splits, artificially inflated sample counts, and skewed evaluation metrics.
- **Mitigation Protocol:**
  1. Calculate cryptographic **SHA-256** hash for every ingested image. Reject exact byte duplicates.
  2. Compute **Difference Hash (dHash)** and **Average Hash (aHash)** with an 8-bit hamming distance threshold:
     $$\text{HammingDistance}(h_1, h_2) \le 4 \implies \text{Duplicate Flagged for Manual Review}$$

#### `INT-02`: Unverified Community Annotations
- **Threat Vector:** Community labels on Kaggle or Roboflow are often produced by crowdsourced annotators with inconsistent class definitions (e.g. labeling broken headlamp as "dent" or labeling whole bumper as "scratch").
- **Impact:** Evaluating ClaimSense against noisy ground truth corrupts benchmark validity.
- **Mitigation Protocol:**
  - Completely discard external annotations.
  - Apply the **Phase 8 Dual-Blind Annotation Protocol**: Two independent professional annotators label every image from scratch, followed by senior adjudicator consensus resolution.

---

## 4. Pre-Ingestion Acceptance Gates

To guarantee that only high-integrity images enter the independent validation suite, every candidate image must pass five sequential automated and manual gates:

```
[Candidate Image Pool (Approved Sources)]
                   │
                   ▼
       ┌───────────────────────┐
       │ Gate 1: Legal Audit   │ ──(Fails)──> [REJECT: LGL Violation]
       └───────────────────────┘
                   │ (Passes)
                   ▼
       ┌───────────────────────┐
       │ Gate 2: Privacy Scrub │ ──(Fails)──> [REJECT: PII Unresolvable]
       └───────────────────────┘
                   │ (Passes: Blurred/Stripped)
                   ▼
       ┌───────────────────────┐
       │ Gate 3: Technical QLT │ ──(Fails)──> [REJECT: Low-res/Blur/Watermark]
       └───────────────────────┘
                   │ (Passes: >800x600, Sharp)
                   ▼
       ┌───────────────────────┐
       │ Gate 4: Deduplication │ ──(Fails)──> [REJECT: Duplicate Hash]
       └───────────────────────┘
                   │ (Passes: Unique SHA256/dHash)
                   ▼
       ┌───────────────────────┐
       │ Gate 5: Domain Quota  │ ──(Fails)──> [HOLD: Category Overflow]
       └───────────────────────┘
                   │ (Passes: Fits Stratified Tier)
                   ▼
[Admitted to CarDD_Independent_Val_v1 Raw Pool for Dual-Blind Annotation]
```
