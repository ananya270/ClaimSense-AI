# ClaimSense AI — Wikimedia Commons License & Candidate Summary

**Audit Date:** 2026-11-17 12:17:13
**API Endpoint:** `https://commons.wikimedia.org/w/api.php`
**Execution Mode:** Strictly Read-Only API Query (Zero Binaries Downloaded)

## 1. Audit Summary Statistics

- **Total Candidate Files Audited:** 98
- **Approved Files (CC0, Public Domain, or CC BY):** 36
- **Excluded Files (CC BY-SA, GFDL, Unknown):** 62
- **Exclusion Rate:** 63.3%

## 2. Category Breakdown

| Category | Focus | Audited | Approved (CC0/CC-BY) | Excluded (CC BY-SA/GFDL) |
| :--- | :--- | :---: | :---: | :---: |
| `Category:Flat_tires` | tire_flat | 38 | **16** | 22 |
| `Category:Broken_car_windows` | glass_shatter | 30 | **4** | 26 |
| `Category:Automobile_hail_damage` | dent_hail | 0 | **0** | 0 |
| `Category:Damaged_automobiles` | collision_general | 30 | **16** | 14 |

## 3. Approved Candidates Overview

Approved candidates satisfy all of the following criteria:
1. Documented license is strictly **CC0 1.0, Public Domain, or CC BY (2.0, 2.5, 3.0, 4.0)**.
2. No copyleft / Share-Alike (SA) provisions that could trigger model weight licensing debates.
3. Commercial computational evaluation is explicitly permitted.
4. Required attribution strings are recorded in `wikimedia_candidate_manifest.csv`.

## 4. Exclusion Rationale

All excluded files in `wikimedia_excluded_files.csv` carry:
- **CC BY-SA 3.0 / 4.0:** Excluded under the precautionary principle regarding neural network weight derivations.
- **GFDL:** Excluded due to documentation-focused terms and burdensome reprint/distribution requirements.
- **Unknown / Unspecified:** Excluded due to missing machine-readable metadata in MediaWiki `extmetadata`.
