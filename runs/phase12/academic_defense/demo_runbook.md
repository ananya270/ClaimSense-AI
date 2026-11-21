# ClaimSense AI — Academic Presentation & Live Demonstration Runbook
## 12-Minute Reproducible Defense Script for Project Examiners

---

## 1. Pre-Demonstration Environment Setup (T - 5 Minutes)

### 1.1 Verify Checkpoint & Clean State
Open terminal and navigate to repository root:
```powershell
cd "c:\Users\ydvan\Desktop\ClaimSense Ai\ClaimSense-AI"
.\.venv\Scripts\python.exe -c "import hashlib; print('Model SHA-256:', hashlib.sha256(open('models/phase5/best.pt', 'rb').read()).hexdigest())"
```
*Expected Output:* `49630ae8d5c0066d0532a2a38efede809920a6fccd3eed59a76eb3b65f009390`

### 1.2 Start Background Worker & Web Application
In Terminal 1 (Application Server):
```powershell
.\.venv\Scripts\python.exe run.py
```
In Terminal 2 (Optional Standalone Worker Daemon if testing external worker):
```powershell
.\.venv\Scripts\python.exe scripts/run_worker.py --broker threaded
```

---

## 2. Live Demonstration Flow (Minute-by-Minute)

### Minute 0 - 2: Introduction & Problem Context
- **Examiner Visual:** Project title screen on `http://127.0.0.1:5001`.
- **Spoken Narrative:**
  > "Good morning, respected examiners. Today we present ClaimSense AI, an asynchronous, multi-modal decision-support prototype engineered to eliminate claim fraud and assessment delays in motor insurance. Currently, processing a four-document claim takes human assessors over a week. ClaimSense AI automates cross-source evidence triangulation across document OCR, YOLOv8 computer vision, and chronological narrative NLP."

### Minute 2 - 4: Authenticated Ingestion & Fast Intake (HTTP 202 Accepted)
- **Action:**
  1. Click **Sign In** $\rightarrow$ Login as `assessor` (or claimant).
  2. Click **Submit New Claim**.
  3. Enter:
     - Policy Number: `POL-2026-9901`
     - Vehicle Registration: `DL-01-AB-1234`
     - Accident Date: `2026-11-20`
     - Location: `Expressway Ring Road`
     - Narrative: `"Traveling northbound when a sudden deceleration caused front bumper collision with guardrail."`
  4. Attach evidence files: `sample_policy.pdf`, `sample_claim_form.pdf`, `sample_invoice.pdf`, `sample_car_damage.jpg`.
  5. Click **Submit Claim Package**.
- **Demonstration Highlight:**
  - Notice the instant response time ($< 100\text{ ms}$).
  - Point to the **Asynchronous Pipeline Status Card** that dynamically appears on screen:
    - Stage 1: `Intake ✓`
    - Stage 2: `OCR Extracting...`
    - Stage 3: `YOLOv8 CarDD Detecting...`
    - Stage 4: `NLP Narrative Chronology...`
    - Stage 5: `Multi-Source Triangulation...`
  - Within seconds, progress bar completes to 100% and turns vibrant green: `AI Multi-Source Verification Completed ✓`.

### Minute 4 - 6: Algorithmic Verification Details & YOLOv8 Damage Localization
- **Action:**
  - Click **🔍 View Claim & AI Damage Analysis**.
- **Demonstration Highlight:**
  - Show the **Claim Record & Algorithmic Verification Details** modal.
  - Highlight the **Vehicle Damage Detection (YOLOv8)** panel:
    - Display bounding boxes identifying damaged vehicle components (dents, scratches, bumper cracks) with individual confidence scores.
    - Show CarDD model metrics badge: Precision 31.4%, Recall 34.6%, mAP@50 19.3%.
  - Point out that flat graphic / clipart uploads are rejected safely by the anti-spoof heuristic before reaching inference.

### Minute 6 - 8: Multi-Source Triangulation & Discrepancy Findings
- **Action:**
  - Scroll down to the **Phase 7 Cross-Source Triangulation** table.
- **Demonstration Highlight:**
  - Point out the **Consistency Score** (e.g., $85.5\%$) and status (`CORROBORATED`).
  - Demonstrate an intentional discrepancy scenario (e.g., date on invoice later than inspection date, or rear damage claimed when front damage was photographed). Show how findings are categorized by severity (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).

### Minute 8 - 10: Production Reliability, Telemetry & Audit Reports
- **Action:**
  - Open a browser tab to `http://127.0.0.1:5001/api/health/ready` and `/api/health/metrics`.
- **Demonstration Highlight:**
  - Point out `task_queue: true`, `sqlite_journal_mode: WAL`, and real-time task queue depth counters.
  - Return to the UI and click **📄 Download PDF Receipt** and **📊 Download Document Report** to demonstrate cryptographic report snapshot immutability.

### Minute 10 - 12: Technical Defense & Viva Q&A
- Invite examiner questions, referencing the architecture diagrams and benchmark latency reductions.
