# ClaimSense AI — Phase 8: Corrected Batch 1 Acquisition & Screening Summary

**Document Identifier:** `corrected_batch_01_summary.md`  
**Audit Standard:** Declared Engineering Specification (`acquisition_pipeline_spec.md`)  
**Hard Resolution Gate:** Width $\ge 800\text{ px}$ AND Height $\ge 600\text{ px}$ (Strict; No unexempted orientation swaps)  
**Optical Blur Gate:** Laplacian Variance $\ge 50.0$  
**Dataset Target Root:** `datasets/CarDD_Independent_Val_v1/`  
**Audit Date:** 2026-11-17  

---

## 1. Executive Summary & Inventory Counts

Following the forensic audit of Batch 1 acquisition, the screening results have been corrected to strictly enforce the declared $800 \times 600$ resolution gate without runtime exemptions:

- **Total Candidates Attempted:** **25 images**
- **Certified Valid & Screened:** **15 images (60.0%)**
- **Total Disqualified / Rejected:** **10 images (40.0%)**
  - **Resolution Gate Disqualifications:** **8 images (32.0%)** failing Width $\ge 800$ OR Height $\ge 600$.
  - **Optical Blur Gate Disqualifications:** **2 images (8.0%)** failing Laplacian Variance $\ge 50.0$.
- **Exact Bit Duplicates:** **0** (Pre-screened via SHA-256).
- **Perceptual Near-Duplicates:** **0** (Minimum dHash Hamming distance = 16, well above threshold $\le 4$).
- **Storage Metrics:**
  - Raw Restricted Storage (`batch_01/raw_restricted/`): **89.53 MB** (25 unredacted raw files preserved for audit)
  - Certified Valid Processed Copies (`batch_01/processed/`): **45.31 MB** (15 fully compliant evaluation copies)
  - Disqualified Raw Copies: **44.22 MB** (10 quarantined candidates)

---

## 2. Corrected Damage Class Distribution

Strict application of the $800 \times 600$ gate creates a critical distribution imbalance that must be addressed in Batch 2:

| Primary Damage Category | Source Repository | Attempted | Certified Valid | Rejected (Res) | Rejected (Blur) | Valid Rate | Class Deficit Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Tire Flat** | Wikimedia Commons | 8 | **7** | 0 | 1 | 87.5% | **Strong** (7 / 30 Target) |
| **Glass Shatter** | Wikimedia Commons | 7 | **6** | 0 | 1 | 85.7% | **Strong** (6 / 40 Target) |
| **Dent (Hail)** | Wikimedia Commons | 4 | **2** | 2 | 0 | 50.0% | Moderate (2 / 90 Target) |
| **Crack** | Humans in the Loop (CC0) | 2 | **0** | 2 | 0 | **0.0%** | **CRITICAL DEFICIT (0 / 60)** |
| **Lamp Broken** | Humans in the Loop (CC0) | 2 | **0** | 2 | 0 | **0.0%** | **CRITICAL DEFICIT (0 / 45)** |
| **Scratch** | Humans in the Loop (CC0) | 1 | **0** | 1 | 0 | **0.0%** | **CRITICAL DEFICIT (0 / 100)** |
| **Dent (Body)** | Humans in the Loop (CC0) | 1 | **0** | 1 | 0 | **0.0%** | Deficit |
| **Total Batch 1** | Approved Sources Only | **25** | **15** | **8** | **2** | **60.0%** | **3 Classes Completely Unrepresented** |

> [!WARNING]
> **Zero Survivors for Crack, Lamp Broken, and Scratch:**  
> All 6 candidates from Humans in the Loop (`CS_VAL_020` to `CS_VAL_025`) failed the $800 \times 600$ resolution gate because their native crops range between $629 \times 419$ and $881 \times 476$. Consequently, Batch 1 contains **strictly zero valid instances** of Crack, Lamp Broken, or Scratch.

---

## 3. Disqualification Breakdown

### A. Resolution Gate Failures (8 Images)
| Image ID | Source | Stated Category | Dimensions | Orientation | Exact Gate Failure |
| :--- | :--- | :--- | :---: | :---: | :--- |
| `CS_VAL_016` | Wikimedia Commons | Dent | $640 \times 480$ | Landscape | Width $640 < 800$ AND Height $480 < 600$ |
| `CS_VAL_017` | Wikimedia Commons | Dent | $720 \times 960$ | Portrait | Width $720 < 800$ (Portrait unexempted in spec) |
| `CS_VAL_020` | Humans in the Loop | Crack | $637 \times 419$ | Landscape | Width $637 < 800$ AND Height $419 < 600$ |
| `CS_VAL_021` | Humans in the Loop | Crack | $637 \times 440$ | Landscape | Width $637 < 800$ AND Height $440 < 600$ |
| `CS_VAL_022` | Humans in the Loop | Lamp Broken | $629 \times 471$ | Landscape | Width $629 < 800$ AND Height $471 < 600$ |
| `CS_VAL_023` | Humans in the Loop | Lamp Broken | $881 \times 476$ | Landscape | Width $881 \ge 800$ (PASS), but Height $476 < 600$ (FAIL) |
| `CS_VAL_024` | Humans in the Loop | Scratch | $637 \times 442$ | Landscape | Width $637 < 800$ AND Height $442 < 600$ |
| `CS_VAL_025` | Humans in the Loop | Dent | $637 \times 444$ | Landscape | Width $637 < 800$ AND Height $444 < 600$ |

### B. Optical Blur Gate Failures (2 Images)
| Image ID | Source | Stated Category | Dimensions | Laplacian Var | Gate Threshold | Exact Failure |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| `CS_VAL_005` | Wikimedia Commons | Tire Flat | $4000 \times 3000$ | **45.2** | $\ge 50.0$ | Motion/focus blur on wheel face |
| `CS_VAL_011` | Wikimedia Commons | Glass Shatter | $5577 \times 3718$ | **31.8** | $\ge 50.0$ | Defocus blur across shattered pane |

---

## 4. Legal & Licensing Compliance of Certified Valid Images

Every one of the 15 certified valid images holds a clean, non-viral, fully documented license:

- **Creative Commons Attribution 2.0 Generic (CC BY 2.0):** **10 images** (Wikimedia Commons photographers with verified attribution metadata).
- **Public Domain Dedication:** **5 images** (4 Wikimedia community CC0 uploads + 1 U.S. Federal Government FEMA release).
- **Creative Commons CC0 1.0 Universal (HITL):** **0 certified valid images** (All 6 HITL CC0 files were legally approved but failed the technical resolution gate).
- **Ambiguous, Copyleft (CC BY-SA / GFDL), or Scraping Sources:** **Strictly 0 images** attempted or accepted.

---

## 5. Certified Cryptographic Manifest (15 Valid Images)

| Image ID | Filename | Category | License | Raw SHA-256 | Processed SHA-256 | Resolution | PII Redacted |
| :--- | :--- | :---: | :--- | :--- | :--- | :---: | :---: |
| `CS_VAL_001` | `CS_VAL_001.jpg` | Tire Flat | Public Domain | `61e9559606713207...` | `3a54fc42f7fb0862...` | $2369 \times 1473$ | **YES** |
| `CS_VAL_002` | `CS_VAL_002.jpg` | Tire Flat | CC BY 2.0 | `6b2b4a1de0b74689...` | `4f2f04280479cec8...` | $3264 \times 2448$ | **YES** |
| `CS_VAL_003` | `CS_VAL_003.jpg` | Tire Flat | CC BY 2.0 | `4cbae1a160b4803d...` | `0787a1a50a04f5c9...` | $3072 \times 2304$ | **YES** |
| `CS_VAL_004` | `CS_VAL_004.jpg` | Tire Flat | Public Domain | `5e248f36b5d46c91...` | `e12dc07d1eac6e0d...` | $4272 \times 2856$ | **YES** |
| `CS_VAL_006` | `CS_VAL_006.jpg` | Tire Flat | CC BY 2.0 | `03de2888fc806df7...` | `dfafa2f0c5f88afd...` | $4272 \times 2848$ | **YES** |
| `CS_VAL_007` | `CS_VAL_007.jpg` | Tire Flat | Public Domain | `a311ab0381d26bee...` | `b2c614dd4a02457d...` | $4272 \times 2856$ | **YES** |
| `CS_VAL_008` | `CS_VAL_008.jpg` | Tire Flat | Public Domain | `b58aba814e5f7209...` | `e9e0da46e3ce9fde...` | $4272 \times 2856$ | **YES** |
| `CS_VAL_009` | `CS_VAL_009.jpg` | Glass Shatter | CC BY 2.0 | `15ab86aae308d93e...` | `ae2077b98aea7abb...` | $6016 \times 4016$ | NO |
| `CS_VAL_010` | `CS_VAL_010.jpg` | Glass Shatter | CC BY 2.0 | `1cbc1c99fc622f61...` | `644f11ad6a3c78e6...` | $6048 \times 4032$ | NO |
| `CS_VAL_012` | `CS_VAL_012.jpg` | Glass Shatter | CC BY 2.0 | `498af9a06d7d0726...` | `890d04a109586c48...` | $1280 \times 960$ | NO |
| `CS_VAL_013` | `CS_VAL_013.jpg` | Glass Shatter | CC BY 2.0 | `bef238ff5b23238f...` | `6f3a89ad7216ef8a...` | $6016 \times 4016$ | NO |
| `CS_VAL_014` | `CS_VAL_014.jpg` | Glass Shatter | CC BY 2.0 | `1f83b35662d143da...` | `e50ff811dd2c4f84...` | $6048 \times 4032$ | NO |
| `CS_VAL_015` | `CS_VAL_015.jpg` | Glass Shatter | Public Domain | `accff2eecb506d89...` | `690f0f9efa23c960...` | $3000 \times 1993$ | NO |
| `CS_VAL_018` | `CS_VAL_018.jpg` | Dent | CC BY 2.0 | `4deec7a845e01871...` | `55293be0ba953ca2...` | $2999 \times 2249$ | NO |
| `CS_VAL_019` | `CS_VAL_019.jpg` | Dent | CC BY 2.0 | `9ee83582d6838745...` | `ad18a93620a2026c...` | $3640 \times 2756$ | NO |

---

## 6. Strategic Takeaways for Batch 2

1. **Resolution vs. Source Compatibility:**
   The Humans in the Loop repository (`DrBimmer/car-parts-and-damage-dataset`) cannot supply images under the $800 \times 600$ gate without pre-filtering for its minority of high-resolution files. Most files in `File1/img` are web-scale VGA-class crops ($637 \times 419$ to $637 \times 444$).
2. **Mitigation Options for Batch 2 Acquisition:**
   - **Option A (High-Res Wikimedia Discovery):** Query Wikimedia Commons specifically for DSLR/high-resolution CC BY/CC0 photography of vehicle panel cracks, broken headlamps/taillamps, and deep key scratches ($\ge 800 \times 600$).
   - **Option B (Formal Specification Amendment):** Formally review whether localized component damage photography (where the damage fills $\ge 40\%$ of the frame) should be permitted under a dual-tier standard: $\text{Width} \ge 640\text{ px}$ AND $\text{Height} \ge 400\text{ px}$ (matching CarDD benchmark inputs), while full-vehicle photography remains $\ge 800 \times 600$.
