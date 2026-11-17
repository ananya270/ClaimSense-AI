# ClaimSense AI — Independent Real-World Validation Dataset Specification

**Target Dataset Identifier:** `CarDD_Independent_Val_v1`  
**Dataset Scale:** Minimum 200 authentic vehicle-damage images (target: 220–250 to allow quarantine attrition)  
**Primary Objective:** Provide a completely unobserved, distributionally diverse, authentic real-world test split for unbiased evaluation of ClaimSense damage detection models (Session 2, Session 4, Production).  
**Strict Isolation Rule:** This dataset must **never** be used for gradient training, fine-tuning, optimizer steps, or threshold tuning.

---

## 1. Target Class Instance Allocation & Distribution

To overcome the statistical variance of the 45-image CarDD test split (where Crack had only 13 instances and Tire Flat had only 6), the 200-image independent dataset mandates minimum target instance representations:

| Damage Class | Class ID | Minimum Image Count | Target Instance Count | Priority Level | Key Target Visual Archetypes |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Dent** | 0 | 70 | 90+ | Medium | Sheet metal depressions, crease dents, hail damage, bumper push-ins. |
| **Scratch** | 1 | 75 | 100+ | **High** | Clear-coat abrasions, deep key scratches, scraped paint down to primer/metal. |
| **Crack** | 2 | 50 | 60+ | **Critical** | Hairline bumper fractures, split plastic grilles, cracked composite panels. |
| **Glass Shatter** | 3 | 35 | 40+ | Medium | Star breaks, bullseye chips, spiderweb windshields, shattered side windows. |
| **Lamp Broken** | 4 | 40 | 45+ | Medium | Cracked headlight lens, shattered taillight casing, detached fog lamp. |
| **Tire Flat** | 5 | 25 | 30+ | Medium | Deflated sidewall rim-pinch, blown tread, bead separation on diverse rim sizes. |

*Note: Multi-damage images (e.g. side-impact collision featuring dent + scratch + cracked bumper + broken headlamp) are explicitly encouraged to test co-occurrence detection.*

---

## 2. Source Diversity & Acquisition Criteria

To ensure genuine real-world validity and eliminate benchmark dataset artifacts, images must be acquired from independent, authentic operational sources:

### A. Primary Eligible Sources
1. **Public Insurance Claim Repositories & Salvage Auctions:**
   - IAAI / Copart public salvage listings (authentic real-world accident and hail damage).
   - Insurance industry open datasets and claims adjustment audit libraries.
2. **Vehicle Inspection & Fleet Audit Imagery:**
   - Commercial fleet turn-in inspection logs.
   - Rental return walkaround photographs.
   - Independent body-shop repair intake estimates.
3. **Public Academic & Open Datasets (Disjoint from CarDD):**
   - Disjoint splits from Roboflow Universe vehicle damage projects (verified real imagery).
   - OpenImages / COCO vehicle damage subsets (excluding any overlapping source origins).

### B. Strict Ineligibility & Disqualification Criteria
- **NO Synthetic or AI-Generated Images:** Absolutely zero Midjourney, Stable Diffusion, or 3D-rendered images (no synthetic vehicle damage).
- **NO Overlapping CarDD Sourcing:** Zero images originating from the official CarDD repository, Kaggle CarDD releases, or Baidu/Google search scrapers used in CarDD compilation.
- **NO Extreme Resolution Degradation:** Reject any image below $1024 \times 768$ resolution or with heavy JPEG block compression artifacts.
- **NO Watermarked or Heavily Text-Overlaid Images:** Images with prominent watermarks over damage areas must be rejected.

---

## 3. Environmental & Camera Variation Criteria

The dataset must reflect the full operational variability encountered by mobile claims apps and inspection cameras:

| Variable | Requirement & Target Quotas | Rationale |
| :--- | :--- | :--- |
| **Camera Distance** | • Close-up inspection (0.5m – 1.0m): 35%<br>• Mid-range component view (1.5m – 2.5m): 45%<br>• Full-vehicle walkaround (3.0m – 5.0m): 20% | Tests model scale invariance and multi-scale feature pyramids. |
| **Camera Angle** | • Normal (orthogonal to panel): 40%<br>• Oblique / Glancing angle (30°– 60°): 45%<br>• Overhead / Low-angle: 15% | Surface scratches and hairline cracks are often only visible at glancing angles. |
| **Lighting Conditions** | • Diffuse / Overcast daylight: 35%<br>• Direct sunlight with specular reflections: 35%<br>• Low-light / Garage / Indoor inspection: 20%<br>• Night-time with smartphone flash: 10% | Directly audits known false-positive vulnerability on specular sun glints. |
| **Vehicle Colors** | • Metallic / High-gloss (silver, grey, white): 45%<br>• Dark / Deep shades (black, dark blue): 35%<br>• Bright / Non-neutral (red, yellow, blue): 20% | High-contrast paint reflects light differently, triggering spurious dent/scratch calls. |
| **Surface Condition** | • Clean / Washed panels: 50%<br>• Wet / Rain-streaked panels: 25%<br>• Dusty / Road-grime covered: 25% | Tests suppression of water-spot and dirt false positives. |

---

## 4. Vehicle Panel Representation

The 200+ images must provide balanced spatial coverage across all major vehicle body assemblies:
- **Front Assembly (30%):** Front bumper, grille, hood, front fenders, headlights, windshield.
- **Rear Assembly (25%):** Rear bumper, trunk lid / liftgate, taillights, rear windshield, quarter panels.
- **Side Assemblies (30%):** Front/rear doors, rocker panels, side mirrors, side windows, A/B/C pillars.
- **Running Gear (15%):** Wheels, tires, wheel arches, underbody trim.

---

## 5. Ingestion Verification Checklist (Per-Image)

Every acquired candidate image must pass an automated pre-ingestion validation test:
1. File is a valid, uncorrupted image (readable via OpenCV and PIL).
2. Resolution is at least $1024 \times 768$ (native).
3. SHA-256 hash is computed and verified unique (zero deduplication collisions against existing CarDD splits).
4. Perceptual hashing (pHash / dHash) confirms hamming distance $> 10$ from all images in `datasets/CarDD_300/` and `datasets/CarDD_Expanded_v1/`.
5. EXIF metadata is parsed and documented where available (Camera make, exposure time, focal length, ISO, capture timestamp).
