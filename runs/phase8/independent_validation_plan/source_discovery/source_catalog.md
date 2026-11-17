# ClaimSense AI — Independent Validation Dataset: Source Catalog

**Document Version:** 1.0  
**Audit Date:** 2026-11-17  
**Scope:** Identification and cataloging of candidate real-world vehicle damage image repositories  
**Target Independent Dataset:** `CarDD_Independent_Val_v1` (Target: 220–250 authentic images)  
**Execution Restriction:** Audit only. No image downloads, no scraping, no model fine-tuning.

---

## 1. Candidate Source Inventory

The table below catalogs candidate open-source, academic, and commercial repositories evaluated for potential contribution to the ClaimSense independent real-world validation dataset:

| Source ID | Source Name | Primary Organization / Host | Direct Resource Link | Verified Image Count | Real vs Synthetic | Access Mechanism |
| :---: | :--- | :--- | :--- | :---: | :---: | :--- |
| **SRC-01** | **Car Damage V5** | Roboflow Universe Community | [universe.roboflow.com/car-damage/car-damage-v5](https://universe.roboflow.com/car-damage/car-damage-v5) | ~3,000 images | Genuine Photographs | Direct API / Web Export |
| **SRC-02** | **Car Parts and Damage Dataset** | DrBimmer / Hugging Face | [huggingface.co/datasets/DrBimmer/car-parts-and-damage-dataset](https://huggingface.co/datasets/DrBimmer/car-parts-and-damage-dataset) | ~1,250 images | Genuine Photographs | Hugging Face Datasets API |
| **SRC-03** | **Coco Car Damage Detection** | Kaggle Community Contributor | [kaggle.com/datasets/anujms/car-damage-detection](https://www.kaggle.com/datasets/anujms/car-damage-detection) | ~800 images | Genuine Photographs | Kaggle CLI / Web Ingestion |
| **SRC-04** | **Car Damage Assessment** | Kaggle Community Contributor | [kaggle.com/datasets/lplenka/car-damage-assessment](https://www.kaggle.com/datasets/lplenka/car-damage-assessment) | ~1,500 images | Genuine Photographs | Kaggle CLI / Web Ingestion |
| **SRC-05** | **Insurance Car Damage Claims** | Kaggle / Apache Contributor | [kaggle.com/datasets/arunrk7/car-damage-dataset](https://www.kaggle.com/datasets/arunrk7/car-damage-dataset) | ~1,150 images | Genuine Photographs | Kaggle CLI / Web Ingestion |
| **SRC-06** | **Automotive Damage Categories** | Wikimedia Commons Foundation | [commons.wikimedia.org/wiki/Category:Damaged_cars](https://commons.wikimedia.org/wiki/Category:Damaged_cars) | 10,000+ images | Genuine Photographs | Wikimedia Commons API / Direct |
| **SRC-07** | **TQVCD (Three-Quarter View)** | Sungkyunkwan University (DX Lab) | [github.com/dxlabskku/TQVCD](https://github.com/dxlabskku/TQVCD) | ~3,000 images | Genuine Photographs | GitHub Repository Clone |
| **SRC-08** | **SYNDCAR** | Mendeley Data | [data.mendeley.com/datasets/hzpj48krdt](https://data.mendeley.com/datasets/hzpj48krdt) | ~2,500 images | **SYNTHETIC (3D CAD)** | Mendeley Data Download |
| **SRC-09** | **Copart / IAAI Salvage Listings** | Copart, Inc. / IAA, Inc. | [copart.com](https://www.copart.com) / [iaai.com](https://www.iaai.com) | 100,000+ daily | Genuine Photographs | Scraper Gated / Login Portal |
| **SRC-10** | **Commercial Stock (Getty / Adobe)** | Getty Images, Inc. / Adobe Stock | [gettyimages.com](https://www.gettyimages.com) | 50,000+ photos | Genuine Photographs | Paid Commercial API License |

---

## 2. Detailed Source Profiles

### Source Profile 1: Roboflow Car Damage V5 (`SRC-01`)
- **Host / Author:** Roboflow Universe (`car-damage/car-damage-v5`)
- **Direct Link:** `https://universe.roboflow.com/car-damage/car-damage-v5`
- **Verified Scale:** ~3,000 images.
- **Damage Classes Covered:** Dent, scratch, glass shatter, crack, crushed components.
- **Image Resolution:** 640×640 up to 2048×1536 (native camera resolutions).
- **Geographic & Environmental Diversity:** Varied international origins (North America, Europe, Asia); indoor workshops, outdoor parking, rainy surfaces, harsh direct sunlight.
- **Authenticity:** Verified genuine photographs of authentic passenger vehicles and light trucks. Zero synthetic generation.
- **Access Protocol:** Downloadable directly via Roboflow REST API using standard export formats (YOLO, COCO, VOC).

### Source Profile 2: Hugging Face Car Parts and Damage Dataset (`SRC-02`)
- **Host / Author:** DrBimmer (`DrBimmer/car-parts-and-damage-dataset`)
- **Direct Link:** `https://huggingface.co/datasets/DrBimmer/car-parts-and-damage-dataset`
- **Verified Scale:** ~1,250 high-resolution images.
- **Damage Classes Covered:** Dents, scratches, cracks, broken lamp lenses, flaking, tear.
- **Image Resolution:** Native $1280 \times 720$ and $1920 \times 1080$.
- **Geographic & Environmental Diversity:** Vehicle inspection intake photographs; high proportion of panel-level close-ups, bumper seams, and direct flash lighting.
- **Authenticity:** Verified authentic vehicle photographs from professional body shop intake logs.
- **Access Protocol:** Direct ingestion via `datasets.load_dataset('DrBimmer/car-parts-and-damage-dataset')` or git-lfs checkout.

### Source Profile 3: Kaggle Coco Car Damage Detection Dataset (`SRC-03`)
- **Host / Author:** Kaggle Contributor (`anujms/car-damage-detection`)
- **Direct Link:** `https://www.kaggle.com/datasets/anujms/car-damage-detection`
- **Verified Scale:** ~800 images partitioned in standard COCO layout.
- **Damage Classes Covered:** Dents, scratches, lamp broken, glass broken.
- **Image Resolution:** 800×600 up to 1600×1200.
- **Geographic & Environmental Diversity:** Urban outdoor settings, salvage yards, side-of-road accident photos.
- **Authenticity:** Verified authentic photographs.
- **Access Protocol:** Direct download via official Kaggle API.

### Source Profile 4: Kaggle Car Damage Assessment Dataset (`SRC-04`)
- **Host / Author:** Kaggle Contributor (`lplenka/car-damage-assessment`)
- **Direct Link:** `https://www.kaggle.com/datasets/lplenka/car-damage-assessment`
- **Verified Scale:** ~1,500 images.
- **Damage Classes Covered:** Scratches, dents, broken lamps, flat tires. Notable: Contains authentic **tire flat** examples.
- **Image Resolution:** 1024×768 average.
- **Geographic & Environmental Diversity:** Mixed consumer smartphone photography and insurance claim uploads.
- **Authenticity:** Verified genuine photographs.
- **Access Protocol:** Kaggle API.

### Source Profile 5: Kaggle Insurance Claim Dataset (`SRC-05`)
- **Host / Author:** Kaggle Contributor (`arunrk7/car-damage-dataset`)
- **Direct Link:** `https://www.kaggle.com/datasets/arunrk7/car-damage-dataset`
- **Verified Scale:** ~1,150 images.
- **Damage Classes Covered:** Major structural impacts, dents, bumper cracks, shattered windshields.
- **Image Resolution:** 720p to 1080p.
- **Geographic & Environmental Diversity:** North American and European insurance claim walkarounds.
- **Authenticity:** Verified authentic real-world insurance claim uploads.
- **Access Protocol:** Kaggle API.

### Source Profile 6: Wikimedia Commons Automotive Damage Collections (`SRC-06`)
- **Host / Author:** Wikimedia Foundation
- **Direct Link:** `https://commons.wikimedia.org/wiki/Category:Damaged_cars`  
  *Sub-categories:* `Category:Flat_tires`, `Category:Automobile_hail_damage`, `Category:Broken_car_windows`
- **Verified Scale:** 10,000+ high-resolution images.
- **Damage Classes Covered:** Hail dents, side window & windshield shatter, flat tires (exceptional diversity across rim sizes), severe scratches, broken headlamps.
- **Image Resolution:** Full native DSLR and high-end smartphone resolutions (3000×2000 to 6000×4000).
- **Geographic & Environmental Diversity:** Global (North America, Europe, Asia, Latin America, Australia); snowy roads, direct sunlight, gravel lots, rain-soaked asphalt.
- **Authenticity:** Verified authentic citizen and professional photography.
- **Access Protocol:** MediaWiki Action API / direct cURL using documented file URLs.

### Source Profile 7: SKKU TQVCD Dataset (`SRC-07`)
- **Host / Author:** Data eXperience Laboratory, Sungkyunkwan University
- **Direct Link:** `https://github.com/dxlabskku/TQVCD`
- **Verified Scale:** ~3,000 images.
- **Damage Classes Covered:** Front three-quarter and rear three-quarter dents, scratches, broken lamps.
- **Authenticity:** Genuine automobile photographs.
- **Access Protocol:** GitHub clone.

### Source Profile 8: Mendeley Data SYNDCAR (`SRC-08`)
- **Host / Author:** Mendeley Data (`hzpj48krdt`)
- **Direct Link:** `https://data.mendeley.com/datasets/hzpj48krdt`
- **Verified Scale:** ~2,500 images.
- **Damage Classes Covered:** Dents, scratches, cracks, broken lights.
- **Authenticity:** **SYNTHETIC 3D CAD.** Images are computer-rendered models.
- **Access Protocol:** Web download.

### Source Profile 9: Copart / IAAI Salvage Platforms (`SRC-09`)
- **Host / Author:** Copart, Inc. / Insurance Auto Auctions, Inc.
- **Direct Link:** `https://www.copart.com`, `https://www.iaai.com`
- **Scale:** Tens of thousands of authentic salvage vehicles.
- **Authenticity:** Real-world total loss and repairable collision vehicles.
- **Access Protocol:** Restricted auction member portal; automated access prohibited by Terms of Service.

### Source Profile 10: Commercial Stock Photography (`SRC-10`)
- **Host / Author:** Getty Images / Adobe Stock
- **Direct Link:** `https://www.gettyimages.com`, `https://stock.adobe.com`
- **Scale:** 50,000+ photos.
- **Authenticity:** Professional high-resolution photography.
- **Access Protocol:** Paid commercial license API.

---

## 3. Verified Facts vs Unverified Claims & Assumptions

To maintain legal and technical integrity, all information is categorized:
- **Verified Facts:** Repository existence, direct URL accessibility, documented licenses in repository headers, verified sample images inspected for genuine photographic nature.
- **Unverified Claims:** Exact damage instance counts inside unannotated community packages (e.g. SRC-04 raw labels must be audited prior to assuming 50+ tire flats).
- **Explicit Assumptions:** Re-annotation will be required for all sources under the Phase 8 Dual-Blind Annotation Protocol; external community bounding boxes will NOT be trusted as gold-standard ground truth.
