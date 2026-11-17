# ClaimSense AI — PII Redaction Logic Test Report

**Execution Date:** 2026-11-17  
**Test Modality:** Synthetic Local Image Patches Only (Zero External Images)  
**Overall Status:** **ALL TESTS PASSED**  

---

## 1. Test Suite Results Summary

| Test Name | Status | Key Metric / Verification Point |
| :--- | :---: | :--- |
| License plate dilation >= 15% and solid zero-entropy masking | **PASS** | Passed unit assertion criteria |
| Boundary truncation clamping | **PASS** | Passed unit assertion criteria |
| Reflection flare capture analysis | **PASS** | Passed unit assertion criteria |
| Damage occlusion threshold rule (20% threshold) | **PASS** | Passed unit assertion criteria |
| EXIF stripping and hash audit trail | **PASS** | Passed unit assertion criteria |

---

## 2. In-Depth Technical Findings & Known Limitations

### A. Bounding Box Dilation >= 15%
- **Finding:** Expanding license plate bounding coordinates by 15% on each axis expands total area by ~32%, cleanly covering edge bevels and mounting screws.
- **Solid Zero-Entropy Redaction:** Confirmed interior pixels strictly overwritten with `[0, 0, 0]`, eliminating spatial gradient recovery.

### B. Reflection and Flare Limitations
- **Critical Engineering Limitation:** Dilation by 15% reliably covers edge flares within a 9-pixel radius. However, specular reflections of embossed plate digits on curved chrome bumpers or polished hoods often extend 15–30 pixels beyond the plate bracket.
- **Mandatory Safeguard:** Automated dilation cannot be assumed to capture remote reflections. **Mandatory human inspection of reflection channels** is required during the Dual-Blind protocol.

### C. Damage Occlusion Threshold (20% Limit)
- **Rule Verification:** When a bumper crack intersected the dilated license plate mask by >20% of its bounding area, the pipeline successfully triggered the `REJECT` decision, preventing corrupted training/eval data.

### D. EXIF Stripping & Hash Auditing
- **Audit Trail:** Confirmed that raw SHA-256 and processed SHA-256 differ as expected, while re-loading the processed image proves exactly 0 EXIF metadata tags remain.
