# ClaimSense AI — Stage 1 Acquisition Pipeline Technical Specification

**Document Version:** 1.0 (Production Engineering Spec)  
**Audit Date:** 2026-11-17  
**Scope:** Technical architecture, gate logic, screening algorithms, and provenance sidecar specifications for independent dataset ingestion  
**Target Independent Dataset:** `CarDD_Independent_Val_v1` (Target: 220–250 authentic images)  
**Execution State:** **DRY-RUN ONLY.** Live acquisition functions require `--execute-live-download` and explicit authorization.

---

## 1. Pipeline Architectural Overview

The ClaimSense Stage 1 Ingestion Pipeline processes candidate images through a sequential, non-destructive 6-stage filtering and sanitization architecture:

```
[Candidate Manifests: wikimedia_manifest.csv & drbimmer_manifest.json]
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Stage 1: Manifest Validation & Raw Candidate Staging                  │
│ • Validate candidate license deed (CC0, PD, CC BY only)               │
│ • Stage raw candidate into: datasets/CarDD_Independent_Val_v1/staging/│
│ • Compute and record raw cryptographic SHA-256 hash                   │
└────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Stage 2: Quality & De-Duplication Screening                            │
│ • Resolution Gate: Width >= 800 px AND Height >= 600 px                │
│ • Blur Gate: Laplacian Variance Var(nabla^2 I) >= 100                  │
│ • Exact Bit Deduplication: Reject identical SHA-256 collisions        │
│ • Perceptual Deduplication: Reject 64-bit dHash Hamming distance <= 4  │
└────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Stage 3: Provenance Extraction & Metadata Decoupling                   │
│ • Extract all camera EXIF, GPS, timestamps, device serials            │
│ • Serialize technical EXIF into sidecar: <image_id>_provenance.json   │
│ • Permanently purge GPS latitude/longitude and personal author tags    │
│ • Strip all EXIF markers from distributed evaluation copy             │
└────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Stage 4: Irreversible PII Redaction & Occlusion Safety Gate           │
│ • Automated detection of license plates (YOLO-Plate) & faces          │
│ • Enforce bounding box dilation >= 15% on each axis                   │
│ • Overwrite pixels with solid opaque zero-entropy black: [0, 0, 0]    │
│ • Occlusion Check: If PII mask occludes > 20% of any damage instance,  │
│   REJECT the image completely                                         │
└────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Stage 5: Dual-Inspector Reflection & Detail Review                     │
│ • Manual inspection of specular reflection flares on chrome bumpers   │
│ • Inspection of commercial fleet decals, phone numbers, street signs  │
│ • Apply manual solid mask or crop if secondary identifiers exist      │
└────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Stage 6: Immutable Golden Dataset Manifest Generation                  │
│ • Output sanitized image to: datasets/CarDD_Independent_Val_v1/images/│
│ • Compute processed SHA-256 and processed 64-bit dHash                │
│ • Write immutable record to: dataset_manifest.json                    │
│ • Apply read-only file system write-protection                         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Technical Screening Criteria & Algorithms

### A. Resolution Gate
- **Threshold:** $\text{Width} \ge 800\text{ px}$ AND $\text{Height} \ge 600\text{ px}$ (or equivalent $\ge 0.48\text{ Megapixels}$).
- **Rationale:** High resolution is required to prevent anti-aliasing interpolation artifacts that blur fine-grained hairline cracks and paint clearcoat scratches.

### B. Optical Blur Gate (Laplacian Variance)
- **Algorithm:** Compute the variance of the 2D Laplacian operator across the grayscale image:
  $$\sigma_{\nabla}^2 = \frac{1}{N} \sum_{x,y} \left( \nabla^2 I(x, y) - \mu_{\nabla} \right)^2$$
- **Threshold:** $\sigma_{\nabla}^2 \ge 100.0$.
- **Rejection Logic:** Images exhibiting $\sigma_{\nabla}^2 < 100.0$ suffer from slow shutter speeds, hand shake, or optical defocus and are rejected.

### C. Multi-Tier Deduplication
1. **Tier 1 (Exact Collision):** Compute raw binary SHA-256. If $\text{SHA256}(B_{\text{candidate}}) == \text{SHA256}(B_{\text{existing}})$, discard as exact duplicate.
2. **Tier 2 (Perceptual Difference Hash - dHash):** Compute 64-bit difference hash tracking horizontal intensity gradients.
   $$\text{HammingDistance}(\text{dHash}_1, \text{dHash}_2) \le 4 \implies \text{Quarantined as Near-Duplicate}$$

---

## 3. Provenance Sidecar & EXIF Governance

To resolve the conflict between privacy requirements (which mandate stripping EXIF) and auditability requirements (which mandate preserving camera settings), the pipeline implements a **Dual-Layer Provenance Architecture**:

### A. Provenance Sidecar Schema (`<image_id>_provenance.json`)
Stored in access-controlled staging metadata:
```json
{
  "image_uuid": "CS-VAL-042",
  "source_repository": "Wikimedia Commons",
  "source_file_url": "https://commons.wikimedia.org/wiki/File:Hail_damage_car.jpg",
  "license_deed": "CC0 1.0 Universal",
  "author_photographer": "Simiprof",
  "attribution_string": "Public domain (Uploaded by Simiprof to Wikimedia Commons)",
  "raw_sha256": "a3b8f... (64 hex characters)",
  "raw_dhash": "e1f0c... (16 hex characters)",
  "intake_timestamp_utc": "2026-11-17T12:00:00Z",
  "technical_exif_preserved": {
    "camera_make": "Nikon",
    "camera_model": "D750",
    "focal_length_mm": 50.0,
    "iso_speed": 200,
    "exposure_time": "1/250"
  },
  "purged_privacy_tags": [
    "GPSInfo (Latitude, Longitude, Altitude)",
    "DateTimeOriginal",
    "CameraSerialNumber",
    "XPAuthor"
  ]
}
```

### B. Stripped ML Artifacts
The final JPEG file saved to `datasets/CarDD_Independent_Val_v1/images/` is written using `PIL.Image.save(..., exif=b'')`. The unit test confirmed that reloaded image files contain exactly 0 EXIF metadata tags.

---

## 4. Solid Redaction & 20% Damage Occlusion Safety

### A. Zero-Entropy Solid Masking
- **Bounding Box Dilation:** All automated license plate detections are expanded by $\ge 15\%$ on each axis:
  $$x_1' = \max(0, x_1 - 0.15 \cdot w), \quad x_2' = \min(W, x_2 + 0.15 \cdot w)$$
  $$y_1' = \max(0, y_1 - 0.15 \cdot h), \quad y_2' = \min(H, y_2 + 0.15 \cdot h)$$
- **Pixel Redaction:** Pixel values within the dilated boundary are strictly overwritten:
  $$I_{\text{redacted}}(x, y) = [0, 0, 0] \quad \forall (x, y) \in \mathcal{R}_{\text{dilated}}$$

### B. The 20% Damage Occlusion Rule
- **Definition:** For every ground-truth or candidate damage bounding box $B_{\text{dmg}}$, calculate:
  $$\text{OcclusionRatio} = \frac{\text{Area}(\mathcal{R}_{\text{dilated}} \cap B_{\text{dmg}})}{\text{Area}(B_{\text{dmg}})}$$
- **Enforcement:** If $\text{OcclusionRatio} > 0.20$, the image is **permanently rejected** from the independent validation set.
- **Rationale:** Masks that occlude $>20\%$ of a damage instance truncate edge contours, disrupt crack feature continuity, and corrupt mAP50 IoU evaluation metrics.

### C. Human Review of Reflection Channels
- Automated dilation captures edge flares within 9 pixels of the plate bracket.
- Inspectors in Stage 5 must visually examine the chrome bumper surface, polished front grille, and wet pavement below the plate. If legible reflections of plate characters exist, inspectors apply a manual rectangular solid mask over the reflection patch.

---

## 5. Dry-Run Script Implementation

The acquisition pipeline script is implemented and verified in:  
[`runs/phase8/independent_validation_plan/stage_1_preparation/acquisition_dry_run.py`](file:///c:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/independent_validation_plan/stage_1_preparation/acquisition_dry_run.py)

- Defaults to **DRY-RUN mode**.
- Execution of actual downloads is guarded by `--execute-live-download` and will safely abort without separate written authorization.
