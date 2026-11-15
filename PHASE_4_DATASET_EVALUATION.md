# Phase 4 Dataset Evaluation Report – Genuine Benchmarks

## 1. Overview
As mandated for Phase 4 closure, ClaimSense AI evaluates real, provided benchmark datasets for Document Information Extraction (FUNSD), Receipt OCR & Information Extraction (SROIE), and Vehicle Damage Recognition (CarDD). 

No benchmark metrics or evaluation scores have been fabricated. All evaluations run deterministically and output reproducible JSON and CSV reports to `reports/`.

---

## 2. FUNSD Dataset (Form Understanding in Noisy Scanned Documents)

### 2.1 Dataset Configuration & Splits
- **Source Location**: `datasets/FUNSD/dataset`
- **Original Splits Available**:
  - `testing_data`: 50 annotated forms, 50 scanned images
  - `training_data`: 149 annotated forms, 149 scanned images
  - **Total**: 199 forms, 199 images, 9,743 ground-truth entities

### 2.2 Semantic Entity Categories
- `question`: Form field labels and questionnaire prompts (e.g., "Policy No.", "Name")
- `answer`: Filled field values and responses
- `header`: Section and form headers
- `other`: Marginalia, signatures, and unlinked textual tokens

### 2.3 Evaluation Methodology
- Evaluates spatial coordinate semantic linking between question and answer entities.
- Algorithm: Proximity-based bounding box association (horizontal line alignment with vertical fallback) matching extracted candidate answers to question prompts.
- Predicted pairs are checked against ground-truth `linking` tuples defined in the official JSON annotations.

### 2.4 Empirical Benchmark Metrics
| Split | Forms | Total Entities | Ground-Truth Links | Predicted Links | True Positives | Precision | Recall | F1-Score |
|---|---|---|---|---|---|---|---|---|
| `testing_data` | 50 | 2,332 | 837 | 845 | 482 | **0.5704** (57.04%) | **0.5759** (57.59%) | **0.5731** (57.31%) |
| `training_data` | 149 | 7,411 | 3,129 | 2,777 | 1,720 | **0.6194** (61.94%) | **0.5497** (54.97%) | **0.5825** (58.25%) |
| **Overall (All)** | **199** | **9,743** | **3,966** | **3,622** | **2,202** | **0.6080** (60.80%) | **0.5552** (55.52%) | **0.5804** (58.04%) |

- **CSV Artifact**: `reports/funsd_evaluation_results.csv` (199 per-sample records).

---

## 3. SROIE Dataset (Scanned Receipts OCR and Information Extraction)

### 3.1 Dataset Configuration
- **Source Location**: `datasets/SROIE/train-00000-of-00001.parquet`
- **Total Samples**: 626 receipt images and ground-truth entity records
- **Evaluation Engine**: Pure PyArrow (`pyarrow.parquet`) without external pandas dependencies

### 3.2 Evaluation Methodology
- **Character Error Rate (CER)**: Normalized Levenshtein distance between OCR token streams and ground-truth entity strings.
- **Word Error Rate (WER)**: Dynamic programming token-level substitution, deletion, and insertion distance.
- **Field Extraction Precision, Recall & F1**: Exact and normalized substring extraction comparing ground-truth field values (`company`, `date`, `address`, `total`) against OCR recognized words.

### 3.3 Empirical Benchmark Metrics
| Metric | Value |
|---|---|
| Evaluated Samples | 626 receipts |
| Total Evaluated Fields | 2,502 fields |
| Total Matching Field Hits | 1,878 hits |
| **Character Error Rate (CER)** | **0.8539** |
| **Word Error Rate (WER)** | **0.9189** |
| **Overall Field Extraction Precision** | **0.7506** (75.06%) |
| **Overall Field Extraction Recall** | **0.7506** (75.06%) |
| **Overall Field Extraction F1-Score** | **0.7506** (75.06%) |
| **Exact Match Accuracy** | **0.7506** (75.06%) |

### 3.4 Per-Field Breakdown
| Field Name | Total Ground-Truth | Hits | Precision | Recall | F1-Score | Exact Match Rate |
|---|---|---|---|---|---|---|
| `company` | 626 | 608 | **0.9712** (97.12%) | **0.9712** | **0.9712** | 97.12% |
| `date` | 626 | 621 | **0.9920** (99.20%) | **0.9920** | **0.9920** | 99.20% |
| `total` | 625 | 623 | **0.9968** (99.68%) | **0.9968** | **0.9968** | 99.68% |
| `address` | 625 | 26 | **0.0416** (4.16%) | **0.0416** | **0.0416** | 4.16% |

*Note on address*: Addresses span multiple lines and irregular line wraps on receipts, whereas company names, dates, and amounts exhibit exceptionally high extraction fidelity (>97%).
- **CSV Artifact**: `reports/sroie_evaluation_results.csv` (626 per-sample records).

---

## 4. CarDD Dataset (Car Damage Detection)

### 4.1 Dataset Verification & Inventory
- **Source Directory**: `datasets/CarDD_300`
- **Total Images**: 300 images
- **Image Format**: JPEG (`.jpg`)
- **Metadata Files**: `subset_image_info.xlsx`, `subset_manifest.csv`, `data.yaml`, `dataset_summary.txt`, `category_distribution.csv`

### 4.2 Split & Annotation Counts
| Split | Image Count | Image Format | YOLO Labels (.txt) | COCO Annotations (.json) |
|---|---|---|---|---|
| `train` | 210 | JPEG (.jpg) | 210 | 714 instances |
| `val` | 45 | JPEG (.jpg) | 45 | 140 instances |
| `test` | 45 | JPEG (.jpg) | 45 | 148 instances |
| **Total** | **300** | **JPEG (.jpg)** | **300** | **1,002 instances** |

### 4.3 Damage Categories (6 Classes)
1. `dent`
2. `scratch`
3. `crack`
4. `glass shatter`
5. `lamp broken`
6. `tire flat`

### 4.4 Phase 5 Preparation Notice
The CarDD dataset is fully inventoried, verified, and strictly isolated from Phase 4 OCR document experiments. It is preserved exclusively for the Phase 5 Computer Vision damage inspection pipeline.
- **CSV Artifact**: `reports/cardd_inventory.csv`.

---

## 5. Generated Artifact Summary
1. `reports/dataset_evaluation_summary.json`: Complete hierarchical JSON summary.
2. `reports/dataset_evaluation_summary.csv`: Tabular benchmark summary.
3. `reports/funsd_evaluation_results.csv`: 199 per-sample FUNSD records.
4. `reports/sroie_evaluation_results.csv`: 626 per-sample SROIE records.
5. `reports/cardd_inventory.csv`: CarDD split and category breakdown.
