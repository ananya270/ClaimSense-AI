# ClaimSense AI — Independent Validation Dataset: Privacy and Provenance Review

**Document Version:** 1.0 (Governance & Safeguards Audit)  
**Audit Date:** 2026-11-17  
**Scope:** Forensic evaluation of privacy anonymization, provenance architecture, deduplication, and annotation protocols  
**Target Independent Dataset:** `CarDD_Independent_Val_v1` (Target: 220–250 authentic images)  
**Execution Restriction:** Strictly Audit Only. No downloads, no scraping, no model modifications.

---

## 1. Technical & Legal Reality of Privacy Anonymization

### The Limitations of Gaussian Blur
In computer vision workflows, applying a standard Gaussian blur (such as a $31 \times 31$ kernel) is frequently proposed as an anonymization technique. However, forensic analysis confirms that **arbitrary Gaussian blur parameters are legally and technically insufficient** to guarantee privacy compliance:

1. **Reversibility via Modern Deconvolution:**  
   Gaussian blurring is a linear, spatially invariant mathematical convolution. In high-resolution inspection photography, characters on embossed metal vehicle registration plates retain substantial low-frequency and gradient boundary energy. Modern deep learning architectures (e.g., deblurring generative networks like DeblurGAN-v2, ESRGAN, and specialized blind deconvolution algorithms) can reconstruct legible alphanumeric characters from blurred patches.
2. **Regulatory Standards under GDPR and CPRA:**  
   Under **GDPR Recital 26**, personal data is legally anonymized only if the data subject is rendered *permanently and irreversibly unidentifiable* by "all the means reasonably likely to be used." European Data Protection Authorities (such as CNIL and the EDPB) have consistently ruled that reversible masking constitutes *pseudonymization*, not *anonymization*. If vehicle registration numbers can be recovered, the dataset remains governed by GDPR Article 83 with statutory liability up to €20M or 4% of global turnover.
3. **Vehicle Registration as PII:**  
   In the European Union (CJEU Case C-582/14 *Breyer*) and under the California Consumer Privacy Act (CCPA / CPRA § 1798.140), license plates and Vehicle Identification Numbers (VINs) constitute Personally Identifiable Information when they can be linked to a registered vehicle owner through state DMV or police databases.

---

## 2. Irreversible Redaction & Anonymization Protocol

To eliminate re-identification risk, ClaimSense AI will implement an **irreversible destruction protocol** rather than simple spatial filtering:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                     ClaimSense Multi-Tier Redaction Hierarchy                          │
├───────────────────┬──────────────────────────────────┬─────────────────────────────────┤
│ Target Element    │ Primary Redaction Mechanism      │ Secondary Safeguard             │
├───────────────────┼──────────────────────────────────┼─────────────────────────────────┤
│ License Plates    │ Solid Opaque Masking             │ Manual Boundary Inspection      │
│ (Front & Rear)    │ (Black rectangle: [0, 0, 0])     │ (Verify zero edge bleed)        │
├───────────────────┼──────────────────────────────────┼─────────────────────────────────┤
│ VIN Tags / Barcode│ Solid Opaque Masking             │ Rejection if VIN overlaps with  │
│ Stickers          │ (Black rectangle: [0, 0, 0])     │ damage region                   │
├───────────────────┼──────────────────────────────────┼─────────────────────────────────┤
│ Human Faces       │ Solid Masking OR Multi-Scale     │ Complete image crop if subject  │
│ (Technicians)     │ Pixelation + Uniform Noise       │ is on image margin              │
├───────────────────┼──────────────────────────────────┼─────────────────────────────────┤
│ Shop Signage / PII│ Opaque Masking over phone        │ Retain undamaged body context   │
│ Invoices          │ numbers and commercial logos     │                                 │
└───────────────────┴──────────────────────────────────┴─────────────────────────────────┘
```

### Technical Specification:
1. **Solid Opaque Masking (Zero-Entropy Redaction):**  
   For all vehicle license plates and VIN barcodes, the pixel values within the bounding polygon are explicitly overwritten:
   $$I_{\text{redacted}}(x, y) = [0, 0, 0] \quad \forall (x, y) \in \mathcal{R}_{\text{PII}}$$
   Replacing the underlying pixels with uniform black zeros completely destroys spatial entropy, making algorithmic or neural reconstruction mathematically impossible.
2. **Two-Stage Verification Pipeline:**
   - *Stage 1 (Automated):* Run automated YOLOv8-Plate detector and RetinaFace detector to identify candidate PII coordinates.
   - *Stage 2 (Human Audit):* Both Reviewer A and Reviewer B in the Dual-Blind protocol must independently verify that 100% of visible plates, reflective stamps, and face contours are completely masked. Any image where PII cannot be masked without destroying the primary damage feature is rejected.

---

## 3. Dual-Layer Provenance Architecture

A critical tension in dataset engineering exists between **privacy preservation** (which requires scrubbing EXIF metadata) and **scientific/legal provenance** (which requires preserving capture details, hashes, and chain of custody).

ClaimSense AI resolves this through a **Dual-Layer Provenance Architecture**:

```
                       Dual-Layer Provenance Architecture
                       
   [Original Ingested Photograph (Quarantined Raw Storage)]
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
   ┌───────────────────────┐   ┌─────────────────────────────────────────┐
   │ Layer 1: Stripped ML  │   │ Layer 2: Secure Immutable Manifest      │
   │ Image Files           │   │ (`dataset_manifest.json`)               │
   ├───────────────────────┤   ├─────────────────────────────────────────┤
   │ • All EXIF stripped   │   │ • Unique Image UUID (e.g., CS-VAL-042)  │
   │ • PII solidly redacted│   │ • Source ID & Verified Repository URL   │
   │ • JPEG Q=95 encoded   │   │ • Original Photographer / Author Credit │
   │ • Deployed to model   │   │ • Documented License Name & Version     │
   │   evaluators          │   │ • Raw Image SHA-256 Checksum            │
   │ • Zero privacy leaks  │   │ • Processed Image SHA-256 Checksum      │
   │                       │   │ • Perceptual dHash & pHash Values       │
   │                       │   │ • Technical EXIF (Camera, Lens, ISO)   │
   │                       │   │ • (All GPS Coordinates Permanently Purged)│
   └───────────────────────┘   └─────────────────────────────────────────┘
```

### Layer 1: Stripped Image Artifacts (`datasets/CarDD_Independent_Val_v1/images/`)
- All EXIF metadata (specifically `GPSInfo`, `DateTimeOriginal`, `CameraSerialNumber`, `Artist`, and `XPAuthor`) is stripped using Pillow's `exif_transpose` followed by un-tagged byte encoding.
- These image files are completely decoupled from individual user identity or physical location, safe for distribution across developer and evaluation environments.

### Layer 2: Secure Immutable Manifest (`datasets/CarDD_Independent_Val_v1/dataset_manifest.json`)
- Maintained as an encrypted or write-protected JSON audit record.
- Preserves legal chain of custody, enabling ClaimSense to prove license compliance, demonstrate attribution, and verify data authenticity during commercial due diligence or intellectual property audits.

---

## 4. Multi-Stage Cryptographic & Perceptual Deduplication

To prevent circular data contamination (e.g., identical images scraped across multiple Kaggle datasets or duplicate vehicle angles), ingestion will follow a 3-tier deduplication filter:

```
Candidate Image ──> [Gate 1: SHA-256 Byte Match] ──(Match)──> REJECT (Exact Duplicate)
                           │ (Unique)
                           ▼
                    [Gate 2: Difference Hash (dHash)] ──(Hamming <= 4)──> QUARANTINE (Near-Dup)
                           │ (Hamming > 4)
                           ▼
                    [Gate 3: Perceptual Hash (pHash)] ──(Hamming <= 6)──> MANUAL AUDIT
                           │ (Passes)
                           ▼
                    Admitted to Annotation Pool
```

### Hash Threshold Specifications:
1. **Cryptographic SHA-256:**
   $$\text{SHA256}(B_1) == \text{SHA256}(B_2) \implies \text{Immediate Rejection (Exact Bit Duplicate)}$$
2. **Difference Hashing (dHash, 64-bit):**  
   Tracks horizontal gradient changes. Robust against JPEG recompression, minor color balance shifts, and resolution downscaling:
   $$\text{HammingDistance}(\text{dHash}_1, \text{dHash}_2) \le 4 \implies \text{Flagged as Near-Duplicate}$$
3. **Perceptual Hashing (pHash, DCT-based):**  
   Evaluates low-frequency structural components. Protects against crop variants and aspect-ratio padding:
   $$\text{HammingDistance}(\text{pHash}_1, \text{pHash}_2) \le 6 \implies \text{Manual Adjudicator Review}$$

---

## 5. Original Source Attribution & Notice Preservation

To fulfill statutory obligations under **CC BY 4.0 (Section 3)**, **MIT (License Notice)**, and **Apache 2.0 (Section 4)**:

1. **Automated Notice Artifacts:** Every evaluation package generated from `CarDD_Independent_Val_v1` will automatically bundle:
   - `ATTRIBUTION.md`: Markdown document citing each contributing photographer or institutional author, repository URL, and license deed.
   - `LICENSE_NOTICES.txt`: Plaintext concatenation of the MIT, CC BY 4.0, CC0 1.0, and Apache 2.0 license deeds.
2. **Attribution Manifest Fields:** Each entry in `dataset_manifest.json` will contain explicit attribution text ready for automatic insertion into enterprise compliance reports:
   ```json
   {
     "image_id": "CS-VAL-001",
     "source_id": "SRC-02",
     "attribution_text": "Humans in the Loop: Car Parts and Car Damages Dataset, CC0 1.0 Universal",
     "source_url": "https://humansintheloop.org/resources/datasets/car-parts-and-car-damages-dataset/"
   }
   ```

---

## 6. Phase 8 Dual-Blind Human Annotation Protocol

To guarantee gold-standard ground truth without relying on unverified community bounding boxes, the annotation pipeline enforces a strict **Dual-Blind protocol with Senior Adjudication**:

```
                       Dual-Blind Human Annotation Pipeline
                       
                      [235 Anonymized Validation Images]
                                      │
                     ┌────────────────┴────────────────┐
                     ▼                                 ▼
           ┌───────────────────┐             ┌───────────────────┐
           │   Reviewer A      │             │   Reviewer B      │
           │ (Blind Labeling)  │             │ (Blind Labeling)  │
           └───────────────────┘             └───────────────────┘
                     │                                 │
                     └────────────────┬────────────────┘
                                      ▼
                        [Automated Consensus Engine]
                                      │
            ┌─────────────────────────┴─────────────────────────┐
            │                                                   │
  (IoU >= 0.70 & Class Match)                         (IoU < 0.70 OR Class Mismatch)
            │                                                   │
            ▼                                                   ▼
┌───────────────────────┐                             ┌───────────────────────┐
│ Consensus Accepted    │                             │  Senior Adjudicator   │
│ (Averaged Bounding Box)                             │  Resolution & Logging │
└───────────────────────┘                             └───────────────────────┘
            │                                                   │
            └─────────────────────────┬─────────────────────────┘
                                      ▼
                   [Final Verified Ground Truth Labels]
```

### Consensus & Adjudication Rules:
1. **Agreement Metrics:**
   - **Intersection over Union (IoU):** $\text{IoU} = \frac{\text{Box}_A \cap \text{Box}_B}{\text{Box}_A \cup \text{Box}_B} \ge 0.70$.
   - **Categorical Agreement:** Both reviewers must select the identical class ID (0: Dent, 1: Scratch, 2: Crack, 3: Glass shatter, 4: Lamp broken, 5: Tire flat).
   - **Cohen's Kappa ($\kappa$):** Computed across all instances; target benchmark agreement $\kappa \ge 0.85$.
2. **Adjudication Logging:**  
   When reviewers disagree on category (e.g. superficial paint scratch vs structural bumper tear) or bounding box boundaries ($\text{IoU} < 0.70$), Senior Adjudicator C reviews the high-resolution crop, assigns the definitive ground truth, and writes an explanatory rationale to `annotation_adjudication_log.json`.
