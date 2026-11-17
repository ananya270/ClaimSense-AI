# ClaimSense AI — Phase 8: Gate L Legal & Licensing Audit

**Document ID:** `AUD-PH8-GATE-L-LIC-001`  
**Audit Date:** 2026-11-17  
**Dataset:** `CarDD_DomainAdaptation_v1`  
**Governing Specification:** `acquisition_specification.md` v1.1-ACTIVE  
**Audited Population:** 120 / 120 authentic real-world vehicle images  
**Audit Boundary:** Affirmative Legal Title & Commercial Exploitation Verification

---

## 1. Executive Summary

Every image binary in `CarDD_DomainAdaptation_v1` underwent forensic legal screening prior to admission:
- **Approved Permissive Deeds:** CC0 1.0 Universal, Public Domain (PD / PD-user / PD-USGov), Creative Commons Attribution (CC BY 2.0, CC BY 2.5, CC BY 3.0, CC BY 4.0).
- **Strictly Prohibited & Excluded:** Copyleft / viral licenses (CC BY-SA 2.0/3.0/4.0, GFDL), non-commercial restrictions (CC BY-NC), no-derivatives restrictions (CC BY-ND), and commercial/unverified copyrights.

**Audit Finding:** **100.0% COMPLIANT (ZERO VIOLATIONS)**. Zero copyleft, zero unverified, and zero restricted licenses were admitted into the corpus.

---

## 2. License Taxonomy & Distribution Register

| License Deed | Legal Scope & Permissibility | Count | Population Share (%) |
| :--- | :--- | :---: | :---: |
| `Public Domain` | Unencumbered commercial reuse, modification, and model training | 61 | 50.8% |
| `CC BY 2.0` | Unencumbered commercial reuse, modification, and model training | 45 | 37.5% |
| `CC0` | Unencumbered commercial reuse, modification, and model training | 5 | 4.2% |
| `CC BY 3.0` | Unencumbered commercial reuse, modification, and model training | 4 | 3.3% |
| `CC BY 4.0` | Unencumbered commercial reuse, modification, and model training | 3 | 2.5% |
| `CC BY 2.5` | Unencumbered commercial reuse, modification, and model training | 1 | 0.8% |
| `CC BY 2.0 de` | Unencumbered commercial reuse, modification, and model training | 1 | 0.8% |
| **Total** | **Fully Audited & Verified Permissive Licenses** | **120** | **100.0%** |

---

## 3. Attribution & Provenance Register

Every image is accompanied by an immutable JSON provenance sidecar in `datasets/CarDD_DomainAdaptation_v1/provenance/`:
- **Repository Platform:** Canonical Wikimedia Commons release.
- **Original Photographer Attribution:** Recorded directly from verified EXTMETADATA records.
- **Deed URI:** Validated against Creative Commons deed registry.
- **Pre- and Post-Redaction Hashes:** Cryptographically tracked with SHA-256 and perceptual dHash.

---

## 4. Chain of Title & Model Encumbrance Conclusion

1. **Downstream Commercial Right:** All admitted images grant worldwide perpetual reproduction, distribution, and commercial AI/ML model training rights.
2. **Copyleft Shield:** Admitting zero CC BY-SA or GFDL assets ensures that downstream model checkpoints (weights, architectures, latent spaces) remain completely unencumbered by viral copyleft requirements.
3. **Legal Status:** **PASS (UNENCUMBERED)**.
