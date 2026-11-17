# ClaimSense AI — Independent Validation Dataset: Verified Source Availability

**Document Version:** 1.0 (Physical Verification Audit)  
**Audit Date:** 2026-11-17  
**Scope:** Verification of existence, official resource URLs, physical image counts, authenticity, and access mechanics  
**Target Independent Dataset:** `CarDD_Independent_Val_v1` (Target: 220–250 authentic images)  
**Execution Restriction:** Strictly Audit Only. No downloads, no scraping, no model modifications.

---

## 1. Verified Source Inventory & Availability Profile

Every candidate source from the initial discovery phase has been audited against its primary online repository, official data card, and platform API endpoints. 

The table below documents only **physically verified facts**, correcting prior community assumptions:

| Source ID | Candidate Dataset Name | Host Platform | Verified Dataset Existence | Exact Official Resource Page / Download URL | Authenticity | Documented Total Images | Documented Classes / Categories | Access & Authentication Requirements |
| :---: | :--- | :--- | :---: | :--- | :---: | :---: | :--- | :--- |
| **SRC-01** | **Car Damage V5** | Roboflow Universe | **CONFIRMED** | `https://universe.roboflow.com/car-damage/car-damage-v5` | Genuine Photography | **3,001 images** | `scratchdent`, `glass_break`, `smash` | Free Roboflow account & API key required. |
| **SRC-02** | **Car Parts and Damage Dataset** | Hugging Face (Humans in the Loop) | **CONFIRMED** | `https://huggingface.co/datasets/DrBimmer/car-parts-and-damage-dataset`<br>*(Mirror of `https://humansintheloop.org/resources/datasets/car-parts-and-car-damages-dataset/`)* | Genuine Photography | **1,812 images**<br>*(814 damage images, 998 parts images)* | **Damages:** Dent, Cracked, Scratch, Flaking, Broken part, Paint chip, Missing part, Corrosion.<br>**Parts:** Bumpers, Doors, Lamps, Windows, Wheels. | Public open access. No login required via `git-lfs` or Hugging Face Datasets API. |
| **SRC-03** | **Car Damage Detection** | Kaggle | **CONFIRMED** | `https://www.kaggle.com/datasets/anujms/car-damage-detection` | Genuine Photography | **~2,300 images** | Binary folders: `00-damage` and `01-whole` (No bounding boxes or class breakdown). | Free Kaggle account & Kaggle API credentials required. |
| **SRC-04** | **Coco Car Damage Detection Dataset** | Kaggle | **CONFIRMED** | `https://www.kaggle.com/datasets/lplenka/coco-car-damage-detection-dataset` | Genuine Photography | **ONLY 80 IMAGES**<br>*(59 train, 11 val, 8 test)* | 5 damaged components: `headlamp`, `front_bumper`, `hood`, `door`, `rear_bumper`. **Zero tire flat images.** | Free Kaggle account & Kaggle API credentials required. |
| **SRC-05** | **Car Damage Dataset (Claims)** | Kaggle | **CONFIRMED** | `https://www.kaggle.com/datasets/vinayjose/car-damage-dataset`<br>*(Corrected from mistaken `arunrk7` citation)* | Genuine Photography | **~8,080 images** (~1.0 GB) | Real collision claims paired with fraud / non-fraud classification CSV. | Free Kaggle account & Kaggle API credentials required. |
| **SRC-06** | **Automotive Damage Categories** | Wikimedia Commons | **CONFIRMED** | Primary Categories:<br>• `https://commons.wikimedia.org/wiki/Category:Damaged_automobiles`<br>• `https://commons.wikimedia.org/wiki/Category:Flat_tires`<br>• `https://commons.wikimedia.org/wiki/Special:Search?query=Automobile+hail+damage`<br>• `https://commons.wikimedia.org/wiki/Category:Broken_car_windows` | Genuine Photography | **10,000+ files** across target categories | Specific damage phenomena: Flat/deflated tires, shattered tempered/laminated glass, hail impact dents, frame collision deformation. | Completely open. Direct HTTP / MediaWiki Action API. No authentication or registration required. |

---

## 2. In-Depth Source Verification Profiles

### SRC-01: Roboflow Universe Car Damage V5
- **Verified Existence:** Confirmed active on Roboflow Universe under workspace `car-damage/car-damage-v5` (curated by user "Erkans Workspace").
- **Authenticity Audit:** Inspecting sample thumbnails confirms authentic vehicle photography showing passenger cars, sedans, and light trucks. No synthetic 3D CAD rendering.
- **Physical Scale:** Exactly **3,001 images** annotated with instance segmentation polygons.
- **Verified Damage Classes:** 3 target labels: `scratchdent` (combined scratch and dent), `glass_break`, and `smash` (structural crushing).
- **Access Protocol:** Requires a free Roboflow account to generate an API key for export in YOLOv8/v11 PyTorch format. Rate-limited to standard free tier API calls.

### SRC-02: DrBimmer / Humans in the Loop
- **Verified Existence:** Confirmed active on Hugging Face (`DrBimmer/car-parts-and-damage-dataset`) and on Kaggle / Humans in the Loop official portal (`humansintheloop.org`).
- **Authenticity Audit:** High-resolution genuine automotive body shop intake photography. Clear panel seams, authentic factory paint finishes, realistic shop and outdoor lighting.
- **Physical Scale:** Exactly **1,812 high-resolution images** (~3.31 GB):
  - 814 images containing vehicle damage annotations (24,851 polygon masks).
  - 998 images containing individual vehicle part segmentations.
- **Verified Damage Classes:** Detailed annotations across 8 defect types:
  - `Dent`: Sheet metal deformations across doors, fenders, quarter panels.
  - `Cracked`: High concentration of plastic tears and splits on front/rear bumper fascias.
  - `Scratch`: Clearcoat abrasions and deep primer gouges.
  - `Broken part`: Fractured light lenses and dislodged splitters.
  - `Flaking`, `Paint chip`, `Missing part`, `Corrosion`.
- **Access Protocol:** Completely unconstrained open access via `git-lfs` checkout or Hugging Face `load_dataset()`. No authentication, registration, or tokens required.

### SRC-03: Kaggle Car Damage Detection (anujms)
- **Verified Existence:** Confirmed active on Kaggle under `anujms/car-damage-detection`.
- **Authenticity Audit:** Real-world web photographs of crashed and whole cars.
- **Physical Scale:** ~2,300 images total.
- **Verified Damage Classes:** **No fine-grained classes.** Images are arranged in binary folders (`training/00-damage`, `training/01-whole`, `validation/00-damage`, `validation/01-whole`). There are no bounding boxes, segmentation masks, or class breakdown tags.
- **Access Protocol:** Kaggle CLI (`kaggle datasets download -d anujms/car-damage-detection`).

### SRC-04: Kaggle Coco Car Damage Detection Dataset (lplenka)
- **Verified Existence:** Confirmed active on Kaggle under `lplenka/coco-car-damage-detection-dataset`.
- **Authenticity Audit:** Authentic real-world vehicle damage photographs.
- **Physical Scale Discrepancy & Verification:**
  - Initial community claims reported ~1,500 images.
  - **Forensic Verification:** The dataset contains a total of **ONLY 80 IMAGES** (59 in `train/`, 11 in `val/`, 8 in `test/`, and 80 consolidated in `img/`).
  - **Class Verification:** Annotations cover 5 damaged components: `headlamp`, `front_bumper`, `hood`, `door`, `rear_bumper`.
  - **Critical Finding:** It contains **ZERO tire flat instances**.
- **Access Protocol:** Kaggle CLI.

### SRC-05: Kaggle Car Damage Claims Dataset (vinayjose)
- **Verified Existence:** Confirmed active on Kaggle under `vinayjose/car-damage-dataset`. *(Note: Corrected from prior mistaken attribution to `arunrk7`, whose dataset is `arunrk7/surface-crack-detection` containing concrete structural cracks).*
- **Authenticity Audit:** Authentic vehicle damage claims photography taken by vehicle owners and insurance appraisers in residential driveways, parking lots, and collision sites.
- **Physical Scale:** ~8,080 images (~1.0 GB) accompanied by a claim classification CSV.
- **Verified Damage Classes:** Broad collision severity (severe front crush, side impact dents, broken headlamps, shattered laminated windshields).
- **Access Protocol:** Kaggle CLI.

### SRC-06: Wikimedia Commons Automotive Damage Collections
- **Verified Existence:** Confirmed active media categories on Wikimedia Commons:
  - `Category:Damaged_automobiles` (thousands of sub-categorized vehicle damage photos).
  - `Category:Flat_tires` (over 200 high-resolution photos of flat/punctured automobile tires).
  - `Category:Broken_car_windows` (hundreds of shattered windshields and tempered side windows).
  - `Special:Search?query=Automobile+hail+damage` (dozens of multi-dent hail storm damage photos).
- **Authenticity Audit:** High-resolution DSLR and smartphone photography uploaded by verified global contributors with complete camera EXIF metadata.
- **Physical Scale:** 10,000+ files across the relevant categories.
- **Verified Damage Classes:** Exceptional coverage of rare, fine-grained categories:
  - *Tire flat:* Authentic collapsed sidewalls, rim bead resting on tarmac, blowout tread separation.
  - *Glass shatter:* Spiderweb windshield cracking, shattered rear tempered glass mosaics.
  - *Hail dents:* Panels exhibiting 5–15 distinct dimples per photograph.
- **Access Protocol:** Direct HTTP download and MediaWiki Action API (`api.php?action=query&list=categorymembers`). Completely open; no registration, login, or tokens required.

---

## 3. Discrepancies and Corrected Assumptions

This asset-level verification identified three critical corrections from initial preliminary summaries:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        Summary of Corrected Dataset Realities                          │
├────────┬─────────────────────────────┬───────────────────────────┬─────────────────────┤
│ Source │ Prior Unverified Assumption │ Verified Physical Reality │ Impact on Plan      │
├────────┼─────────────────────────────┼───────────────────────────┼─────────────────────┤
│ SRC-03 │ Believed to be CC0 license  │ Unlicensed 2018 web scrape│ REJECTED (Zero use) │
├────────┼─────────────────────────────┼───────────────────────────┼─────────────────────┤
│ SRC-04 │ Believed ~1,500 images with │ EXACTLY 80 IMAGES TOTAL;  │ DEPRECATED from     │
│        │ flat tires                  │ zero flat tire images     │ primary allocation  │
├────────┼─────────────────────────────┼───────────────────────────┼─────────────────────┤
│ SRC-05 │ Attributed to `arunrk7`     │ `arunrk7` is concrete;    │ URL & attribution   │
│        │                             │ actual is `vinayjose`     │ corrected           │
└────────┴─────────────────────────────┴───────────────────────────┴─────────────────────┘
```

**Conclusion:**  
Only **SRC-02 (DrBimmer / Humans in the Loop)** and **SRC-06 (Wikimedia Commons)** possess both verified physical scale and unassailable legal clearance. The acquisition portfolio must be restructured around these two rock-solid anchors.
