# ClaimSense AI — Data Governance, Privacy & Provenance Checklist

**Target Corpus:** `CarDD_Independent_Val_v1` (200+ Images)  
**Standard Compliance:** Commercial Licensing, GDPR/CCPA Privacy, ISO 27001 Data Integrity, AI Ethics.

---

## 1. Provenance Schema & Metadata Tracking

Every ingested image must be cataloged in a machine-readable governance manifest (`dataset_manifest.json`) capturing the following mandatory fields:

```json
{
  "image_id": "EXP-VAL-001",
  "filename": "EXP-VAL-001.jpg",
  "sha256": "4f8a12b...",
  "acquisition_metadata": {
    "source_domain": "fleet_inspection_partner_alpha",
    "source_url_or_intake_id": "INSP-2026-Q1-9982",
    "acquisition_date": "2026-11-20",
    "ingested_by": "qa_data_engineer_01",
    "license_type": "Commercial-Permitted / Open-Commercial-Usage"
  },
  "exif_audit": {
    "camera_make": "Samsung",
    "camera_model": "Galaxy S23",
    "focal_length_mm": 5.4,
    "iso": 50,
    "exposure_time_sec": "1/250",
    "gps_coordinates_stripped": true
  },
  "privacy_compliance": {
    "license_plate_redacted": true,
    "faces_redacted": true,
    "vin_redacted": true,
    "pii_audit_signoff": "compliance_officer_signoff_20261120"
  },
  "vehicle_context": {
    "vehicle_type": "Sedan",
    "body_panel": "Front Bumper / Driver Side Fender",
    "panel_color": "Metallic Silver",
    "lighting_environment": "Direct Sunlight / Specular Glint",
    "cleanliness": "Clean Surface"
  },
  "annotation_governance": {
    "reviewer_a_id": "annotator_102",
    "reviewer_b_id": "annotator_105",
    "adjudicator_id": "senior_appraiser_01",
    "status": "APPROVED_GOLD_STANDARD"
  }
}
```

---

## 2. Privacy & PII Scrubbing Protocol

Prior to entering the active validation pool, all candidate imagery must undergo automated and human-in-the-loop PII scrubbing:
1. **License Plate Obfuscation:** Any visible license plate must be irreversibly masked using solid black fill or heavy Gaussian blur ($\sigma \ge 15$).
2. **Facial Obfuscation:** Any bystanders, vehicle occupants, or inspection personnel reflected in glass or standing near the vehicle must be completely blurred.
3. **EXIF Sanitization:** All GPS latitude/longitude, altitude, device serial numbers, and personal owner tags embedded in EXIF headers must be stripped using an EXIF sanitizer prior to disk persistence.
4. **VIN & Paperwork Redaction:** Vehicle Identification Numbers stamped on windshield corners or inspection intake clipboards visible in the frame must be redacted.

---

## 3. Train / Validation / Test Strict Separation Safeguards

To prevent subtle data contamination or hyperparameter overfitting:

### Rule 1: Strict Physical Storage Segregation
- The independent validation dataset must reside in a dedicated, isolated storage path:
  `datasets/CarDD_Independent_Val_v1/`
- It must **never** be copied into or referenced by `datasets/CarDD_300/` or `datasets/CarDD_Expanded_v1/`.

### Rule 2: Cryptographic & Perceptual Anti-Leakage Audit
Before benchmarking, the dataset will be audited against all training splits:
1. **SHA-256 Matching:** Zero image file hash collisions against `train/` or `val/`.
2. **Perceptual Hash Distance:** Hamming distance computed via pHash must be $> 10$ across all training images, ensuring no near-duplicates (e.g. photos taken 1 second apart from slightly different angles).

### Rule 3: Zero-Training & Zero-Threshold-Tuning Constraint
- **No Weight Updates:** The dataset will never be passed to `model.train()`.
- **No Optimizer Tuning:** Learning rate schedules or loss weights will not be evaluated on this dataset.
- **No Threshold Calibration on this Set:** Operating thresholds calibrated in Phase 8 were derived from CarDD. They will be evaluated **blindly as fixed candidates** on this dataset. Tuning thresholds on this set to boost numbers is strictly prohibited.

---

## 4. Pre-Benchmark Governance Sign-Off Checklist

Before any model runs on the independent validation dataset:
- [ ] Exactly 200+ unique physical image files exist on disk in `images/`.
- [ ] Exactly 200+ corresponding verified label files exist in `labels/`.
- [ ] Manifest file `dataset_manifest.json` is 100% complete with zero null fields in governance tags.
- [ ] PII review sign-off completed for 100% of images.
- [ ] License clearance records archived in legal compliance directory.
- [ ] Read-only filesystem attributes applied to prevent accidental in-place modifications.
