# ClaimSense AI — Phase 8: Batch 1 Acquisition & Screening Report

**Execution Date:** 2026-11-17 07:21:20 UTC

**Dataset Location:** `datasets/CarDD_Independent_Val_v1/`

**Scope & Batch Cap:** Batch 1 (Strictly 25 Images Maximum)

---

## 1. Executive Summary & Inventory Counts

- **Total Candidates Processed:** 25
- **Total Accepted & Fully Screened:** **23 images (92.0%)**
- **Total Rejected Images:** **2 images (8.0%)**
- **Exact Bit Duplicates Detected:** 0
- **Perceptual Near-Duplicates Detected:** 0
- **Raw Restricted Binary Storage (`batch_01/raw_restricted/`):** 89.53 MB (25 files)
- **Sanitized Evaluation Storage (`batch_01/processed/`):** 48.10 MB (23 files)

---

## 2. Damage Class Distribution

| Primary Damage Category | Source Repository | Candidates | Accepted | Usability Rate | Priority Justification |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Tire Flat** | Wikimedia Commons | 8 | **7** | 87.5% | Critical deficit class (Target 30) |
| **Glass Shatter** | Wikimedia Commons | 7 | **6** | 85.7% | Deficit class (Target 40) |
| **Dent (Hail)** | Wikimedia Commons | 4 | **4** | 100.0% | Authentic multi-dent hailstorm patterns |
| **Crack** | Humans in the Loop (CC0) | 2 | **2** | 100.0% | Authentic bumper & panel fractures |
| **Lamp Broken** | Humans in the Loop (CC0) | 2 | **2** | 100.0% | Smashed headlight / taillight housings |
| **Scratch** | Humans in the Loop (CC0) | 1 | **1** | 100.0% | Deep longitudinal key & panel scratches |
| **Dent (Body)** | Humans in the Loop (CC0) | 1 | **1** | 100.0% | Fender impact dent |
| **Total Batch 1** | Approved Sources Only | **25** | **23** | **92.0%** | Full 6-class representation |

---

## 3. Legal & License Compliance Breakdown

- **Creative Commons CC0 1.0 Universal:** 6 images (Humans in the Loop institutional repository)
- **Public Domain Dedication:** 6 images (Wikimedia Commons / U.S. Federal Government FEMA / NWS / CC0)
- **Creative Commons Attribution 2.0 Generic (CC BY 2.0):** 13 images (Individually verified Wikimedia Commons photographers)
- **Strictly Excluded (Zero Tolerance):** Roboflow V5, Kaggle Insurance Claims, Kaggle COCO, Kaggle Damage, CC BY-SA, GFDL, unknown licenses. **Zero copyleft or unverified files ingested.**

---

## 4. Privacy Protection & Provenance Decoupling Audit

1. **PII Redaction Protocol:**
   - Visible vehicle registration plates were identified and redacted using dilated solid black boxes (`[0, 0, 0]` RGB zero-entropy overwrite).
   - Bounding boxes were dilated by **at least 15%** along each dimension (`dilation_pct = 0.15`) to eliminate edge-glow or font residue.
   - Tested interior pixel entropy: verified 100% solid zero `[0, 0, 0]`.
   - Redaction damage occlusion: 0.0% overlap with target damage (plates located at bumper center; flat tires and window glass physically isolated).

2. **EXIF Decoupling:**
   - Processed evaluation copies contain **strictly 0 EXIF tags** (verified by `len(Image.getexif()) == 0`).
   - Technical camera parameters (ISO, exposure, camera model, acquisition date) and complete provenance URLs have been preserved in separate decoupled sidecar files: `datasets/CarDD_Independent_Val_v1/manifests/provenance/{image_id}_provenance.json`.
   - Unredacted original files remain isolated in `batch_01/raw_restricted/` and are inaccessible to evaluation pipelines.

---

## 5. Cryptographic Registry of Acquired Images

| Image ID | Filename | Category | Source | Raw SHA-256 | Processed SHA-256 | Resolution | PII Redacted |
| :--- | :--- | :---: | :--- | :--- | :--- | :---: | :---: |
| `CS_VAL_001` | `CS_VAL_001.jpg` | Tire Flat | Wikimedia Commons | `61e9559606713207...` | `3a54fc42f7fb0862...` | 2369x1473 | YES |
| `CS_VAL_002` | `CS_VAL_002.jpg` | Tire Flat | Wikimedia Commons | `6b2b4a1de0b74689...` | `4f2f04280479cec8...` | 3264x2448 | YES |
| `CS_VAL_003` | `CS_VAL_003.jpg` | Tire Flat | Wikimedia Commons | `4cbae1a160b4803d...` | `0787a1a50a04f5c9...` | 3072x2304 | YES |
| `CS_VAL_004` | `CS_VAL_004.jpg` | Tire Flat | Wikimedia Commons | `5e248f36b5d46c91...` | `e12dc07d1eac6e0d...` | 4272x2856 | YES |
| `CS_VAL_006` | `CS_VAL_006.jpg` | Tire Flat | Wikimedia Commons | `03de2888fc806df7...` | `dfafa2f0c5f88afd...` | 4272x2848 | YES |
| `CS_VAL_007` | `CS_VAL_007.jpg` | Tire Flat | Wikimedia Commons | `a311ab0381d26bee...` | `b2c614dd4a02457d...` | 4272x2856 | YES |
| `CS_VAL_008` | `CS_VAL_008.jpg` | Tire Flat | Wikimedia Commons | `b58aba814e5f7209...` | `e9e0da46e3ce9fde...` | 4272x2856 | YES |
| `CS_VAL_009` | `CS_VAL_009.jpg` | Glass Shatter | Wikimedia Commons | `15ab86aae308d93e...` | `ae2077b98aea7abb...` | 6016x4016 | NO |
| `CS_VAL_010` | `CS_VAL_010.jpg` | Glass Shatter | Wikimedia Commons | `1cbc1c99fc622f61...` | `644f11ad6a3c78e6...` | 6048x4032 | NO |
| `CS_VAL_012` | `CS_VAL_012.jpg` | Glass Shatter | Wikimedia Commons | `498af9a06d7d0726...` | `890d04a109586c48...` | 1280x960 | NO |
| `CS_VAL_013` | `CS_VAL_013.jpg` | Glass Shatter | Wikimedia Commons | `bef238ff5b23238f...` | `6f3a89ad7216ef8a...` | 6016x4016 | NO |
| `CS_VAL_014` | `CS_VAL_014.jpg` | Glass Shatter | Wikimedia Commons | `1f83b35662d143da...` | `e50ff811dd2c4f84...` | 6048x4032 | NO |
| `CS_VAL_015` | `CS_VAL_015.jpg` | Glass Shatter | Wikimedia Commons | `accff2eecb506d89...` | `690f0f9efa23c960...` | 3000x1993 | NO |
| `CS_VAL_016` | `CS_VAL_016.jpg` | Dent | Wikimedia Commons | `ebdd8fb644b513d2...` | `85d9b3ae126ada36...` | 640x480 | NO |
| `CS_VAL_017` | `CS_VAL_017.jpg` | Dent | Wikimedia Commons | `09148efc0d7e9578...` | `9fb3e63e622554c2...` | 720x960 | NO |
| `CS_VAL_018` | `CS_VAL_018.jpg` | Dent | Wikimedia Commons | `4deec7a845e01871...` | `55293be0ba953ca2...` | 2999x2249 | NO |
| `CS_VAL_019` | `CS_VAL_019.jpg` | Dent | Wikimedia Commons | `9ee83582d6838745...` | `ad18a93620a2026c...` | 3640x2756 | NO |
| `CS_VAL_020` | `CS_VAL_020.jpg` | Crack | Humans in the Loop | `0154d1bc05aa40d5...` | `55866fcfc9b6fa56...` | 637x419 | NO |
| `CS_VAL_021` | `CS_VAL_021.jpg` | Crack | Humans in the Loop | `5691ef5aabc07572...` | `c5aaa55ec92dbe18...` | 637x440 | NO |
| `CS_VAL_022` | `CS_VAL_022.jpg` | Lamp Broken | Humans in the Loop | `ce430325e3b1e769...` | `5b9a9ec63c23d26a...` | 629x471 | NO |
| `CS_VAL_023` | `CS_VAL_023.jpg` | Lamp Broken | Humans in the Loop | `df7505f32bdac459...` | `5bc61fc1e45d62ab...` | 881x476 | NO |
| `CS_VAL_024` | `CS_VAL_024.jpg` | Scratch | Humans in the Loop | `4b1207e4852a8362...` | `e77120e391f1b261...` | 637x442 | NO |
| `CS_VAL_025` | `CS_VAL_025.jpg` | Dent | Humans in the Loop | `ce9a7c5ce57d9fa8...` | `a401005f3b776efb...` | 637x444 | NO |

---

## 6. Next Steps & Stage 1 Gate Status

- **Stage 1 Batch 1 is COMPLETE (23/25 images accepted and sanitized; 2 rejected due to optical blur).**
- In accordance with project governance, **acquisition is now paused**. No further images will be downloaded, no annotations will be applied, and no models will be trained or evaluated without explicit user authorization for Batch 2.
