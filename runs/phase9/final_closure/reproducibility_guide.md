# ClaimSense AI — Phase 9.11: Complete Scientific Reproducibility Guide

**Project:** ClaimSense AI (Final-Year B.Tech Major Project)  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.11 — Final Documentation, Reproducibility & Project Sign-off  
**Document Classification:** Standard Operating Procedure (SOP) & Runbook  
**Date:** 2026-11-20

---

## 1. Prerequisites & Environment Specifications

The ClaimSense AI platform is designed for cross-platform deployment across Windows 10/11, Linux (Ubuntu 20.04+), and macOS (Apple Silicon / Intel).

| Component | Minimum Specification | Recommended Specification |
| :--- | :--- | :--- |
| **Operating System** | Windows 10/11 64-bit or Linux x86_64 | Windows 11 Pro 64-bit |
| **Python Runtime** | Python 3.10.x | Python 3.11.x – 3.14.x (Tested: 3.14.6) |
| **System Memory (RAM)**| 8 GB RAM | 16 GB RAM |
| **Disk Space** | 5 GB free disk space | 10 GB free SSD storage |
| **Hardware Compute** | Multicore CPU (x86_64) | 4+ CPU Cores (GPU optional, not required) |

---

## 2. Environment Setup & Dependency Installation

### Step 1: Clone Repository & Create Virtual Environment
```bash
# Clone the repository
git clone https://github.com/anshg8252/ClaimSense-AI.git
cd ClaimSense-AI

# Create isolated Python virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# On Linux / macOS (Bash):
source .venv/bin/activate
```

### Step 2: Install Pinned Dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Copy the sample environment template:
```bash
# On Windows PowerShell:
Copy-Item .env.example .env

# On Linux / Bash:
cp .env.example .env
```
Ensure the `.env` file contains at least:
```ini
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
SECRET_KEY=claimsense-ai-dev-secret-key-change-in-production
DATABASE_PATH=data/claimsense.db
```

---

## 3. Cryptographic Checkpoint Verification

Before running inference, verify the integrity of the authoritative production model:

### On Windows PowerShell:
```powershell
Get-FileHash -Algorithm SHA256 models/phase5/best.pt
```

### On Linux / Bash:
```bash
sha256sum models/phase5/best.pt
```

**Expected Hash Digest:**
```
49630ae8d5c0066d0532a2a38efede809920a6fccd3eed59a76eb3b65f009390
```
If the calculated hash does not match, the checkpoint has been corrupted or modified and should be restored from backup.

---

## 4. Running the Web Application

To start the ClaimSense AI local development server:

```powershell
python backend/app.py
```

The application will initialize the database schema in `data/claimsense.db` (if not present) and bind to:
```
http://127.0.0.1:5000 (or http://127.0.0.1:5001 if port 5000 is occupied)
```

### Accessing the Web UI:
- **Claimant Portal:** `http://127.0.0.1:5000/`
- **Claim Submission Form:** `http://127.0.0.1:5000/claims`
- **Assessor Verification Dashboard:** `http://127.0.0.1:5000/assessment`
- **Health Check Endpoint:** `http://127.0.0.1:5000/api/health`

---

## 5. Executing the Full Automated Regression Suite

To execute the complete regression test suite:

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

### Expected Output:
```
Ran 158 tests in ~75-80s
OK (skipped=1)
```
- Total test count: **158 tests**.
- 1 test is conditionally skipped when YOLO weights are active (`test_opencv_fallback_pipeline`).
- All tests operate using ephemeral in-memory or temporary SQLite databases in `AppData/Local/Temp/`, leaving the production database completely pristine.

---

## 6. Reproducing Independent Benchmark Evaluations

To reproduce the Phase 9.6 independent CarDD evaluation on Track A:

```powershell
python -c "
from ultralytics import YOLO
model = YOLO('models/phase5/best.pt')
results = model.val(data='datasets/CarDD_300/data.yaml', split='test', imgsz=416, conf=0.15, iou=0.50, device='cpu')
print('Production Benchmark Results:')
print(f'mAP50: {results.box.map50:.4f}')
print(f'mAP50-95: {results.box.map:.4f}')
"
```

### Expected Benchmark Results:
- Production mAP50: `~0.1833`
- Evaluated on 45 test images containing 148 annotated damage instances.
