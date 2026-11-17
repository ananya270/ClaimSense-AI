# ClaimSense AI — Phase 8: Batch 1 Forensic Quality & Manifest Audit

**Audit Date:** 2026-11-17  
**Execution Type:** Strictly Read-Only Forensic Audit  
**Audited Target:** Batch 1 Ingestion (`datasets/CarDD_Independent_Val_v1/batch_01/`)  
**Declared Specification Documents:**  
- `runs/phase8/independent_validation_plan/acquisition_specification.md`
- `runs/phase8/independent_validation_plan/stage_1_preparation/acquisition_pipeline_spec.md`  

---

## Executive Summary of Audit Findings

| Audit Dimension | Declared Engineering Standard | Runtime Observed State | Audit Verdict | Corrective Action |
| :--- | :--- | :--- | :---: | :--- |
| **Resolution Gate** | Width $\ge 800\text{ px}$ AND Height $\ge 600\text{ px}$ | Script relaxed to $\min \ge 400, \max \ge 600$ | **CRITICAL DEVIATION** | 8 images retroactively disqualified. Final valid count drops from 23 to **15**. |
| **Portrait Orientation** | Width $\ge 800$, Height $\ge 600$ | Evaluator treated $720 \times 960$ as passing | **GATE FAILURE** | `CS_VAL_017` ($720 < 800$) disqualified. No silent orientation exemptions permitted. |
| **Licensing Integrity** | Verified CC0, PD, or CC BY only | All 25 files verified; zero copyleft | **PASSED (100%)** | Zero viral/ambiguous licenses. All 15 valid files have clean commercial rights. |
| **Cryptographic Integrity**| SHA-256 matches disk bytes | 25 raw files, 23 processed files | **PASSED (100%)** | 100% cryptographic parity verified against manifests. |
| **Deduplication** | Exact $\Delta = 0$, dHash $\Delta \le 4$ | Exact = 0; Min pairwise dHash = 16 | **PASSED (100%)** | Zero exact or perceptual near-duplicates. |
| **PII & Privacy Masking**| $\ge 15\%$ dilated solid black `[0,0,0]` | 7 plates masked; 100% solid zero | **PASSED (100%)** | Zero PII leakage; 0.0% damage occlusion; 0 faces detected. |
| **EXIF Decoupling** | Strictly 0 EXIF tags in evaluation copies | 100% of processed copies have 0 tags | **PASSED (100%)** | Privacy tags purged; technical settings preserved in provenance JSON sidecars. |
| **Frozen Checkpoints** | Unmodified production & session weights | Hashes identical to initial baseline | **PASSED (100%)** | All 3 model checkpoints remain completely frozen. |

---

## 1. Resolution Gate Audit — CRITICAL

### A. Declared Technical Standard
In `acquisition_pipeline_spec.md` (Stage 2: Quality & De-Duplication Screening), the resolution requirement is explicitly codified as:
$$\text{Width} \ge 800\text{ px} \quad \text{AND} \quad \text{Height} \ge 600\text{ px}$$
The specification explicitly notes that high spatial resolution is required to prevent anti-aliasing and interpolation blur from obscuring hairline bumper cracks and paint scratches during inference resizing.

### B. Explanation for Prior Runtime Acceptance
During the initial dry runs of Batch 1 acquisition (`task-4022`), all 6 candidate images from Humans in the Loop (`CS_VAL_020` through `CS_VAL_025`) failed the resolution gate because their native dimensions are $637 \times 419$, $637 \times 440$, $629 \times 471$, $881 \times 476$, $637 \times 442$, and $637 \times 444$.

In the subsequent execution turn, the runtime script author observed that:
1. The standard CarDD evaluation test set utilizes standard VGA $640 \times 480$ resolution.
2. The YOLO evaluation architecture downsamples/pads inputs to $640 \times 640$.
3. The Humans in the Loop photos are authentic macro inspection photographs of vehicle components.

Based on this reasoning, the author modified the script's filtering condition to:
```python
if min(w, h) < 400 or max(w, h) < 600:
    # reject
```
This relaxed condition permitted images with width $\ge 600$ and height $\ge 400$ (such as $637 \times 419$ and $640 \times 480$) to pass, and simultaneously permitted the portrait photo `CS_VAL_017` ($720 \times 960$) by treating width and height interchangeably.

**Audit Assessment:**  
While the author's technical observation regarding CarDD's $640 \times 480$ baseline was contextually understandable, **relaxing an engineering requirement in code without a formal amendment to the approved project specification violates data governance protocols**. In a forensic quality audit, the written engineering contract is authoritative. Consequently, all 8 images failing the written $800 \times 600$ requirement must be formally disqualified.

---

### C. Resolution Gate Failure Inventory (8 Disqualified Images)

The table below itemizes the 8 candidate images that fail the declared $800 \times 600$ resolution standard:

| Image ID | File Title | Category | Source | Width | Height | Orientation | Measured Deficit | Audit Verdict |
| :--- | :--- | :---: | :--- | :---: | :---: | :---: | :--- | :---: |
| `CS_VAL_016` | `Damaged car from hail in Missouri...jpg` | Dent | Wikimedia | 640 | 480 | Landscape | Width $640 < 800$ ($-20.0\%$), Height $480 < 600$ ($-20.0\%$) | **DISQUALIFIED** |
| `CS_VAL_017` | `Hail damage car.jpg` | Dent | Wikimedia | 720 | 960 | Portrait | Width $720 < 800$ ($-10.0\%$) (No portrait exemption in spec) | **DISQUALIFIED** |
| `CS_VAL_020` | `Car damages 100.png` | Crack | Humans in Loop | 637 | 419 | Landscape | Width $637 < 800$ ($-20.4\%$), Height $419 < 600$ ($-30.2\%$) | **DISQUALIFIED** |
| `CS_VAL_021` | `Car damages 101.png` | Crack | Humans in Loop | 637 | 440 | Landscape | Width $637 < 800$ ($-20.4\%$), Height $440 < 600$ ($-26.7\%$) | **DISQUALIFIED** |
| `CS_VAL_022` | `Car damages 102.jpg` | Lamp Broken | Humans in Loop | 629 | 471 | Landscape | Width $629 < 800$ ($-21.4\%$), Height $471 < 600$ ($-21.5\%$) | **DISQUALIFIED** |
| `CS_VAL_023` | `Car damages 103.png` | Lamp Broken | Humans in Loop | 881 | 476 | Landscape | Width $881 \ge 800$ (PASS), but Height $476 < 600$ ($-20.7\%$) | **DISQUALIFIED** |
| `CS_VAL_024` | `Car damages 104.png` | Scratch | Humans in Loop | 637 | 442 | Landscape | Width $637 < 800$ ($-20.4\%$), Height $442 < 600$ ($-26.3\%$) | **DISQUALIFIED** |
| `CS_VAL_025` | `Car damages 105.png` | Dent | Humans in Loop | 637 | 444 | Landscape | Width $637 < 800$ ($-20.4\%$), Height $444 < 600$ ($-26.0\%$) | **DISQUALIFIED** |

---

### D. Recalculated Batch 1 Totals Under Strict Resolution Gate

$$\begin{aligned}
\text{Total Candidates Attempted} &= 25 \\
\text{Resolution Gate Failures} &= 8 \quad (32.0\%) \\
\text{Optical Blur Gate Failures} &= 2 \quad (8.0\%) \\
\text{Total Disqualified Candidates} &= 10 \quad (40.0\%) \\
\mathbf{Certified\ Valid\ Images} &= \mathbf{15} \quad \mathbf{(60.0\%)}
\end{aligned}$$

---

## 2. Complete License Reconciliation (All 25 Attempted Files)

The audit reconciled the legal deed, copyright ownership, upstream permissions, and current screening status for all 25 attempted images:

| Image ID | Source Repository | Category | Exact License Deed | Official License URL | Author / Contributor | Commercial ML Eval | Derivative Works | Attribution Required | Screening Verdict | Entered Processed? |
| :--- | :--- | :---: | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `CS_VAL_001` | Wikimedia Commons | Tire Flat | Public Domain | `https://creativecommons.org/publicdomain/zero/1.0/` | Bull-Doser | YES | YES | NO | **ACCEPTED** | YES |
| `CS_VAL_002` | Wikimedia Commons | Tire Flat | CC BY 2.0 | `https://creativecommons.org/licenses/by/2.0` | Greg Gjerdingen | YES | YES | YES | **ACCEPTED** | YES |
| `CS_VAL_003` | Wikimedia Commons | Tire Flat | CC BY 2.0 | `https://creativecommons.org/licenses/by/2.0` | Riley | YES | YES | YES | **ACCEPTED** | YES |
| `CS_VAL_004` | Wikimedia Commons | Tire Flat | Public Domain | `https://creativecommons.org/publicdomain/zero/1.0/` | OSX | YES | YES | NO | **ACCEPTED** | YES |
| `CS_VAL_005` | Wikimedia Commons | Tire Flat | CC BY 2.0 | `https://creativecommons.org/licenses/by/2.0` | Riley | YES | YES | YES | **REJECTED (Blur)** | NO |
| `CS_VAL_006` | Wikimedia Commons | Tire Flat | CC BY 2.0 | `https://creativecommons.org/licenses/by/2.0` | Charlie | YES | YES | YES | **ACCEPTED** | YES |
| `CS_VAL_007` | Wikimedia Commons | Tire Flat | Public Domain | `https://creativecommons.org/publicdomain/zero/1.0/` | OSX | YES | YES | NO | **ACCEPTED** | YES |
| `CS_VAL_008` | Wikimedia Commons | Tire Flat | Public Domain | `https://creativecommons.org/publicdomain/zero/1.0/` | OSX | YES | YES | NO | **ACCEPTED** | YES |
| `CS_VAL_009` | Wikimedia Commons | Glass Shatter | CC BY 2.0 | `https://creativecommons.org/licenses/by/2.0` | Shixart1985 | YES | YES | YES | **ACCEPTED** | YES |
| `CS_VAL_010` | Wikimedia Commons | Glass Shatter | CC BY 2.0 | `https://creativecommons.org/licenses/by/2.0` | Shixart1985 | YES | YES | YES | **ACCEPTED** | YES |
| `CS_VAL_011` | Wikimedia Commons | Glass Shatter | CC BY 2.0 | `https://creativecommons.org/licenses/by/2.0` | Shixart1985 | YES | YES | YES | **REJECTED (Blur)** | NO |
| `CS_VAL_012` | Wikimedia Commons | Glass Shatter | CC BY 2.0 | `https://creativecommons.org/licenses/by/2.0` | Daniel Ramirez | YES | YES | YES | **ACCEPTED** | YES |
| `CS_VAL_013` | Wikimedia Commons | Glass Shatter | CC BY 2.0 | `https://creativecommons.org/licenses/by/2.0` | Shixart1985 | YES | YES | YES | **ACCEPTED** | YES |
| `CS_VAL_014` | Wikimedia Commons | Glass Shatter | CC BY 2.0 | `https://creativecommons.org/licenses/by/2.0` | Shixart1985 | YES | YES | YES | **ACCEPTED** | YES |
| `CS_VAL_015` | Wikimedia Commons | Glass Shatter | Public Domain | `https://www.fema.gov` | Win Henderson / FEMA | YES | YES | NO | **ACCEPTED** | YES |
| `CS_VAL_016` | Wikimedia Commons | Dent | Public Domain | `https://www.weather.gov` | US National Weather Service | YES | YES | NO | **REJECTED (Res)** | YES* (Quarantined) |
| `CS_VAL_017` | Wikimedia Commons | Dent | Public Domain | `https://creativecommons.org/publicdomain/zero/1.0/` | Simiprof | YES | YES | NO | **REJECTED (Res)** | YES* (Quarantined) |
| `CS_VAL_018` | Wikimedia Commons | Dent | CC BY 2.0 | `https://creativecommons.org/licenses/by/2.0` | James St. John | YES | YES | YES | **ACCEPTED** | YES |
| `CS_VAL_019` | Wikimedia Commons | Dent | CC BY 2.0 | `https://creativecommons.org/licenses/by/2.0` | James St. John | YES | YES | YES | **ACCEPTED** | YES |
| `CS_VAL_020` | Humans in the Loop | Crack | CC0 1.0 Universal | `https://creativecommons.org/publicdomain/zero/1.0/` | Humans in the Loop | YES | YES | NO | **REJECTED (Res)** | YES* (Quarantined) |
| `CS_VAL_021` | Humans in the Loop | Crack | CC0 1.0 Universal | `https://creativecommons.org/publicdomain/zero/1.0/` | Humans in the Loop | YES | YES | NO | **REJECTED (Res)** | YES* (Quarantined) |
| `CS_VAL_022` | Humans in the Loop | Lamp Broken | CC0 1.0 Universal | `https://creativecommons.org/publicdomain/zero/1.0/` | Humans in the Loop | YES | YES | NO | **REJECTED (Res)** | YES* (Quarantined) |
| `CS_VAL_023` | Humans in the Loop | Lamp Broken | CC0 1.0 Universal | `https://creativecommons.org/publicdomain/zero/1.0/` | Humans in the Loop | YES | YES | NO | **REJECTED (Res)** | YES* (Quarantined) |
| `CS_VAL_024` | Humans in the Loop | Scratch | CC0 1.0 Universal | `https://creativecommons.org/publicdomain/zero/1.0/` | Humans in the Loop | YES | YES | NO | **REJECTED (Res)** | YES* (Quarantined) |
| `CS_VAL_025` | Humans in the Loop | Dent | CC0 1.0 Universal | `https://creativecommons.org/publicdomain/zero/1.0/` | Humans in the Loop | YES | YES | NO | **REJECTED (Res)** | YES* (Quarantined) |

*\*Note: Images marked "YES* (Quarantined)" are currently present in `batch_01/processed/` due to the prior execution script, but have been formally retroactively disqualified and marked for exclusion from the final evaluation dataset.*

### Confirmation of License Cleanliness:
- **Zero Ambiguous Licenses:** 100% of the 25 files have verifiable, primary-source public deeds.
- **Zero Copyleft Infections:** No CC BY-SA, GFDL, or viral licenses were ingested.
- **Commercial ML Use Permitted:** All accepted files permit commercial internal evaluation and benchmark testing without royalty or downstream model weight contamination.

---

## 3. Quality and Privacy Forensic Audit

### A. Cryptographic Hash Audit (Disk Byte Verification)
- **Raw Files (`batch_01/raw_restricted/`):** All 25 raw files were re-hashed directly from disk. 100% match their recorded SHA-256 hashes in `acquisition_manifest.csv`.
- **Processed Files (`batch_01/processed/`):** All 23 existing processed copies match their recorded SHA-256 hashes.
- **Integrity Status:** **PASS (Zero tampering or file corruption).**

### B. Deduplication & Perceptual Distance Audit
- **Exact Bit Collisions:** Re-evaluated pairwise against all 25 raw SHA-256 hashes. **0 exact collisions detected.**
- **Perceptual dHash Audit:** Recomputed 64-bit difference hashes for all 25 images. Pairwise Hamming distance calculation across all $\binom{25}{2} = 300$ pairs revealed:
  - **Minimum Pairwise Hamming Distance:** **16** (between `CS_VAL_004` Ford Cortina and `CS_VAL_008` Toyota Corolla).
  - **Deduplication Threshold:** Distance $\le 4$ indicates near-duplicate.
  - **Margin of Separation:** $16 \gg 4$.
  - **Audit Verdict:** **PASS (Zero perceptual duplicates).**

### C. Optical Blur Audit (Laplacian Variance)
Images were evaluated using the discrete 2D Laplacian operator. At the operational threshold of $\sigma_{\nabla}^2 \ge 50.0$:
- 2 images failed and were rejected:
  - `CS_VAL_005`: Laplacian Variance = **45.2** (Wheel hub face out of focus).
  - `CS_VAL_011`: Laplacian Variance = **31.8** (Severe lens defocus on shattered rear window).
- 23 images passed $\sigma_{\nabla}^2 \ge 50.0$.
- *Note on Ultra-High Resolution Images ($> 20\text{ MP}$):* Candidates `CS_VAL_009` (24 MP) and `CS_VAL_010` (24 MP) exhibited variances of 66.4 and 60.8 when downscaled to 1080p, while native unscaled crops showed sharp edge gradients (109.6 on `CS_VAL_009`). Both clearly pass visual inspection and the 50.0 threshold.

### D. PII Redaction Audit (Solid Zero-Entropy Verification)
All processed images were audited for visible vehicle license plates and human faces:
1. **License Plate Masking:** 7 passenger vehicle images (`CS_VAL_001`, `002`, `003`, `004`, `006`, `007`, `008`) contained visible license plates. In each case:
   - A dilated solid black bounding box ($\ge 15\%$ expansion along each axis) was applied.
   - Array analysis of pixel values inside the masked region confirmed:
     $$\text{All pixels} \equiv [0, 0, 0] \implies \text{Entropy} = 0.0$$
   - Zero edge-bleed, zero transparent alpha gradients, and zero residual alphanumeric characters.
2. **Damage Occlusion:** The masked plates reside exclusively on lower bumper assemblies. In all 7 cases, target damage (flat tires) is situated at the wheel arch/rim. **Damage occlusion was verified to be exactly 0.0%** (well below the $\le 20\%$ ceiling).
3. **Face Detection:** Zero human faces or bystanders were detected in any of the 25 candidate images.
4. **Audit Verdict:** **PASS (Zero PII leakage).**

### E. EXIF Removal Audit
- Processed images in `batch_01/processed/` were probed with `PIL.Image.getexif()`.
- **Result:** **100% of processed images contain exactly 0 EXIF tags.**
- Technical camera parameters (ISO, exposure time, camera model) and acquisition timestamps have been successfully decoupled into independent provenance JSON sidecars in `manifests/provenance/`.
- Unredacted original files remain strictly isolated in `batch_01/raw_restricted/`.
- **Audit Verdict:** **PASS (Zero metadata leakage).**

---

## 4. Corrected Deliverables Summary

The following authoritative corrected manifests and reports have been generated and cross-referenced in both `runs/phase8/independent_validation_plan/batch_01/` and `datasets/CarDD_Independent_Val_v1/manifests/`:

1. [corrected_batch_01_summary.md](file:///C:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/independent_validation_plan/batch_01/corrected_batch_01_summary.md): Comprehensive summary reporting 15 valid images and 10 rejected candidates.
2. [corrected_screening_results.csv](file:///C:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/independent_validation_plan/batch_01/corrected_screening_results.csv): Itemized 25-row audit record detailing gate measurements, PII verification, and screening outcomes.
3. [resolution_gate_failures.csv](file:///C:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/independent_validation_plan/batch_01/resolution_gate_failures.csv): Dedicated failure analysis for the 8 images disqualified by the $800 \times 600$ resolution standard.
4. [corrected_license_reconciliation.csv](file:///C:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/independent_validation_plan/batch_01/corrected_license_reconciliation.csv): Master 25-row licensing reconciliation mapping legal permissions to screening outcomes.
5. [batch_01_forensic_audit.md](file:///C:/Users/ansh9/Desktop/Claimsense%20Ai/runs/phase8/independent_validation_plan/batch_01/batch_01_forensic_audit.md): This comprehensive forensic report.

---

## 5. Critical Strategic Assessment for Batch 2

Strictly enforcing the $800 \times 600$ gate leaves Batch 1 with **15 certified valid images**, distributed across only 3 damage categories:
- **Tire Flat:** 7 images (Strong progress toward 30-instance goal)
- **Glass Shatter:** 6 images (Strong progress toward 40-instance goal)
- **Dent:** 2 images (Hail damage)
- **Crack:** **0 images** (CRITICAL DEFICIT)
- **Lamp Broken:** **0 images** (CRITICAL DEFICIT)
- **Scratch:** **0 images** (CRITICAL DEFICIT)

### The Underlying Sourcing Conflict:
The Humans in the Loop repository (`SRC-02`) has verified institutional CC0 rights, but its dataset (`DrBimmer/car-parts-and-damage-dataset/Car damages dataset/File1/img`) is composed almost entirely of localized web-scale bounding-box crops ($629 \times 419$ to $881 \times 476$). Under a strict $800 \times 600$ standard, virtually the entire HITL repository is disqualified.

### Two Mutually Exclusive Strategic Paths for Batch 2:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PATH FORWARD OPTIONS                            │
├──────────────────────────────────┬─────────────────────────────────────┤
│ OPTION A: Preserve Strict Gate   │ OPTION B: Formal Tiered Amendment   │
│ Keep Width >= 800 & Height >= 600│ Amend Specification via RFC         │
├──────────────────────────────────┼─────────────────────────────────────┤
│ • Discard all HITL sub-800 crops.│ • Tier 1 (Full-Vehicle Walkaround): │
│ • Restrict Batch 2 exclusively to│   Width >= 800 AND Height >= 600.   │
│   Wikimedia Commons DSLR photos  │ • Tier 2 (Macro Component Crop):    │
│   for Crack, Lamp, and Scratch.  │   Width >= 640 AND Height >= 400,   │
│ • Pros: Zero change to spec.     │   provided damage fills >= 30% area.│
│ • Cons: Higher sourcing scarcity │ • Pros: Reclaims 6 HITL CC0 images  │
│   for macro vehicle cracks/lamps.│   and mirrors CarDD 640x480 baseline│
│                                  │ • Cons: Requires formal spec update.│
└──────────────────────────────────┴─────────────────────────────────────┘
```

---

## 6. Current Status & Governance Gate

- **Forensic Quality Audit is COMPLETE.**
- All existing files and raw binaries remain **100% preserved and untouched**.
- No new images have been acquired.
- No annotations have been applied.
- No models have been trained or evaluated.
- Production and Phase 7 assets remain locked.
- **Execution is PAUSED awaiting user direction on Option A vs Option B before Batch 2 authorization.**
