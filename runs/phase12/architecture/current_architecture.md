# ClaimSense AI — Current Architecture Investigation & Bottleneck Analysis
## Pre-Phase 12 Pipeline Decomposition

**Document Reference:** `runs/phase12/architecture/current_architecture.md`  
**Governance Date:** November 21, 2026  
**Subsystems Audited:** `backend/routes/claims.py`, `backend/services/ocr/`, `backend/services/vision/`, `backend/services/verification/`, `backend/services/receipt.py`

---

## 1. Existing Synchronous Claim Ingestion Flow

The current implementation in `backend/routes/claims.py` (`POST /api/claims`) processes the entire claim verification pipeline synchronously inside the WSGI request-response thread:

```mermaid
sequenceDiagram
    autonumber
    actor Claimant as User / Web Client
    participant WSGI as Flask WSGI Thread (POST /api/claims)
    participant FS as Local Filesystem (uploads/)
    participant DB as SQLite DB (claims, documents)
    participant OCR as Tesseract OCR Pipeline
    participant YOLO as YOLOv8 Neural Model (models/phase5/best.pt)
    participant NLP as Rule-Based NLP Service
    participant VERIF as Phase 7 Cross-Source Engine

    Claimant->>WSGI: Multipart Form (Policy PDF, Claim PDF, Invoice PDF, Vehicle JPEG)
    Note over WSGI,FS: Step 1: Authentication & File Persistence (~25ms)
    WSGI->>WSGI: Validate Session, CSRF, Magic Bytes & Filenames
    WSGI->>FS: Write 4 evidentiary binaries to uploads/{claim_id}/
    WSGI->>DB: INSERT Claim, INSERT Documents
    
    Note over WSGI,OCR: Step 2: Synchronous Document Intelligence (~1200ms)
    WSGI->>OCR: Ingest & Parse Policy & Repair Invoice
    OCR->>DB: INSERT ExtractedInformation (7-12 entity rows)
    
    Note over WSGI,YOLO: Step 3: Synchronous Computer Vision (~1500ms cold, ~100ms warm)
    WSGI->>YOLO: Run Bounding-Box Detection on Vehicle JPEG
    YOLO->>FS: Synthesize Annotated Overlay Image
    YOLO->>DB: INSERT VehicleDamageAnalysis, INSERT Detections
    
    Note over WSGI,NLP: Step 4: Synchronous NLP Chronology (~15ms)
    WSGI->>NLP: Parse Accident Narrative & Temporal Markers
    NLP->>DB: INSERT ClaimNLPAnalysis
    
    Note over WSGI,VERIF: Step 5: Synchronous Triangulation Engine (~35ms)
    WSGI->>VERIF: Run Cross-Source Verification (Narrative vs OCR vs Vision)
    VERIF->>DB: INSERT ClaimVerificationRun, INSERT Findings
    
    Note over WSGI,Claimant: Step 6: HTTP Response
    WSGI-->>Claimant: HTTP 201 Created (Claim JSON Payload)
```

---

## 2. Quantitative Bottleneck Analysis

From our empirical benchmarks across 6,901 requests in Phase 10:

| Stage in `POST /api/claims` | Typical Duration | CPU / I/O Profile | Bottleneck Classification |
|:---|:---:|:---:|:---:|
| 1. Ingestion, Auth, & File Writes | ~25 ms | Disk I/O | Negligible |
| 2. Tesseract OCR (Policy & Invoice) | ~950 – 1,400 ms | Heavy CPU | **Critical Bottleneck** |
| 3. YOLOv8 Damage Detection | ~85 – 2,500 ms | Heavy CPU / GPU | **Critical Bottleneck** |
| 4. NLP Narrative Chronology | ~15 ms | In-Memory Heuristics | Negligible |
| 5. Cross-Source Verification | ~35 ms | Relational Queries & Rules | Negligible |
| **Total Synchronous Latency** | **~2,800 – 4,100 ms** | **Synchronous Block** | **SLA Failure under Concurrency** |

### Concurrency Impact:
- When 50 concurrent users submit claims, the single-thread execution locks the worker thread for ~3.1 seconds.
- In SQLite `DELETE` mode, writing OCR and damage detection results inside the same transaction causes reader-writer serialization.
- Tail latency ($p95$) spikes to **1,400 ms** (WAL) and **2,000 ms** (DELETE), with maximum spikes exceeding **4,500 ms**.

---

## 3. Decoupling Blueprint for Phase 12

To achieve sub-100ms intake latency, the pipeline must be split into two discrete tiers:

1. **Intake Tier (`POST /api/claims`):**
   - Execute authentication, input validation, and file writes to `uploads/<claim_id>/`.
   - Insert `Claim` record with status `PENDING_ANALYSIS`.
   - Enqueue a `process_claim_task(claim_id)` background job.
   - Return **HTTP 202 Accepted** immediately with `{claim_id, task_id, status: "queued", status_url: "/api/claims/<claim_id>/status"}` in $<80\text{ ms}$.

2. **Background Worker Tier (`claimsense-worker`):**
   - Dequeued by dedicated background workers.
   - Executes OCR, YOLOv8 vision, NLP, and cross-source verification sequentially.
   - Updates task status across transparent stages (`ocr_processing` -> `damage_analysis` -> `cross_source_verification` -> `completed`).
   - Assessor / claimant UI polls `GET /api/claims/<claim_id>/status` to visualize live progression.
