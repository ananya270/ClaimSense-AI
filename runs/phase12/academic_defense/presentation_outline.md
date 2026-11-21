# ClaimSense AI — Academic Major Project Defense Presentation Deck
## Slide-by-Slide Defense Structure (16 Slides)

---

### Slide 1: Title & Candidacy
- **Title:** ClaimSense AI — Automated Multi-Source Insurance Claim Corroboration & Decision-Support System
- **Subtitle:** An Asynchronous, Multi-Modal Deep Learning Framework for Fraud Detection and Claim Triage
- **Candidate:** Principal Project Candidate & Team
- **Supervisor / Department:** Department of Computer Science & Engineering
- **Date & Academic Year:** Final Major Project Evaluation — 2026
- *Presenter Notes:* Introduce the team, acknowledge faculty advisors, and articulate the central thesis: replacing error-prone manual claim verification with automated, multi-source algorithmic triangulation.

---

### Slide 2: Industry Problem Formulation & The "Paperwork Bottleneck"
- **Key Metrics:** \$40 Billion annual global motor insurance fraud; 7–21 day average settlement latency.
- **Three Systemic Vulnerabilities:**
  1. *Fabricated Documentation:* Forged repair estimates and non-matching policy dates.
  2. *Exaggerated Damage:* Billing for undamaged vehicular components or downloading photos of damaged cars from the web.
  3. *Assessor Cognitive Fatigue:* Human adjusters reviewing 40+ claims daily cannot cross-reference every receipt line item against visual damage.
- *Visual:* Infographic showing claimant $\rightarrow$ 14-day delay $\rightarrow$ human error.

---

### Slide 3: Project Objectives & Research Scope
- **Core Mission:** Design and implement a production-grade, multi-modal decision-support prototype.
- **Specific Technical Deliverables:**
  - Fast asynchronous ingestion with $<100\text{ ms}$ response times.
  - Custom-trained YOLOv8 computer vision model for localized damage classification.
  - Optical Character Recognition (OCR) pipeline for tabular PDF invoice and policy extraction.
  - Natural Language Processing (NLP) engine for temporal chronology and component ontology mapping.
  - Phase 7 Cross-Source Triangulation algorithm producing an objective Consistency Score ($0-100\%$).
  - Full production hardening: WSGI, Nginx reverse proxy, Docker multi-container compose, and WAL SQLite.

---

### Slide 4: System Architecture & Distributed Decoupling
- **Architecture Overview:** Edge $\rightarrow$ Application $\rightarrow$ Task Broker $\rightarrow$ Worker Pool $\rightarrow$ Persistence.
- **Phase 12 Breakthrough:** Transition from synchronous 3.14-second blocking HTTP calls to non-blocking asynchronous intake (`HTTP 202 Accepted`) with real-time client polling.
- *Visual:* Full-page architecture diagram (`system_architecture.md`).

---

### Slide 5: The Intake Subsystem & Pluggable Dual-Engine Broker
- **Fast Response:** decodes multipart uploads, persists evidence to disk, and commits DB records in $78.4\text{ ms}$.
- **Dual Broker Implementation:**
  - *Redis 7 (Production):* Atomic `RPUSH`/`BLPOP` queue for containerized micro-workers.
  - *ThreadPoolExecutor (Local Fallback):* In-process pool with persistent SQLite task tracking for zero-dependency Windows dev and pytest runs.
- **Task Idempotency:** Atomic duplicate suppression preventing redundant GPU/CPU passes.

---

### Slide 6: Computer Vision Pipeline — YOLOv8 CarDD Model
- **Model Choice:** YOLOv8n (3.2M parameters) fine-tuned on CarDD-300 dataset.
- **Detected Classes:** Scratch, Dent, Crack, Tear, Shatter.
- **Anti-Spoofing Heuristic:** Sobel edge entropy and color variance checks reject non-photographic graphics, clip-art, and memes before reaching inference.
- *Visual:* Annotated vehicle photograph displaying bounding boxes, class labels, and CarDD model metrics badge.

---

### Slide 7: Document Intelligence & OCR Extraction Pipeline
- **Engine:** PyMuPDF $300\text{ DPI}$ rendering $\rightarrow$ Adaptive Thresholding $\rightarrow$ Tesseract OCR.
- **Structured Field Extraction:** Regular expressions and token proximity algorithms parsing policy numbers, invoice grand totals, and garage repair dates.
- **Fault-Tolerant Isolation:** Best-effort processing prevents document corruption from failing the overall claim package.

---

### Slide 8: Chronological Forensics & Narrative NLP
- **Temporal Entity Extraction:** Normalizing narrative incident dates and times to ISO-8601 UTC.
- **Ontology Mapping:** Mapping driver narrative terms ("smashed grill", "bent radiator") to vehicular anatomical ontologies.
- **Anomaly Detection:** Flagging estimates issued prior to the stated accident date or claims filed beyond policy coverage terms.

---

### Slide 9: Multi-Source Triangulation & The Consistency Score
- **Algorithmic Corroboration Formulation:**
  $$S_c = 100 \times \left(1.0 - \sum w_i \cdot \delta_i\right)$$
- **Triangulation Matrix:** Cross-checking (Invoice Line Items $\leftrightarrow$ YOLO Detections), (Policy Dates $\leftrightarrow$ Accident Date), and (Narrative Component $\leftrightarrow$ Photo Centroid).
- **Advisory Classification:** Corroborated ($\ge 80\%$), Review Required ($50-80\%$), Suspect Discrepancy ($< 50\%$).
- *Visual:* Screenshot of the Algorithmic Verification Details modal.

---

### Slide 10: Production Hardening & Operational Reliability
- **WSGI Integration:** Gunicorn pre-forked workers via `wsgi.py`.
- **Database Tuning:** SQLite Write-Ahead Logging (`WAL`), 5000ms busy timeout, and automated live backups via `scripts/backup_database.py`.
- **Defense-in-Depth Security:** Cryptographic CSRF tokens, strict IDOR role-based access control, path sanitization, and security HTTP headers.
- **Container Architecture:** Multi-container `docker-compose.yml` orchestrating `app`, `worker`, `redis`, and `nginx`.

---

### Slide 11: Observability, Telemetry & Real-Time UX
- **Probing Standards:** `/api/health/live` (Kubernetes liveness) and `/api/health/ready` (Readiness verifying DB, storage, weights, and queue).
- **Operational Metrics:** `/api/health/metrics` exposing memory RSS, uptime, and live queue status counts.
- **Client UX:** Real-time polling with progress bar progression and step badge highlights without page refreshes.

---

### Slide 12: Empirical Performance & Latency Benchmarks
- **Intake Latency Reduction:** **3,140 ms** (Synchronous) $\rightarrow$ **78.4 ms** (Asynchronous) = **97.5% reduction**.
- **Concurrency Scalability:** System remains responsive under burst submissions without WSGI thread starvation.
- *Visual:* Mermaid XY chart comparing latency curves.

---

### Slide 13: Testing & Quality Assurance Verification
- **Total Test Suite:** **213 Automated Tests** across 12 phases with **100% Pass Rate**.
- **Coverage Domains:** Unit, integration, security IDOR, OCR resilience, concurrency idempotency, and regression suites.
- **Production Asset Protection:** Model weight SHA-256 (`models/phase5/best.pt`) verified identical before and after all implementations.

---

### Slide 14: System Limitations & Edge Cases (Honest Academic Disclosure)
- **Dataset Scope:** CarDD-300 subset constrained on rare commercial/motorcycle geometries.
- **Monocular 2D Limits:** Cannot inspect hidden internal engine/transmission mechanical damage.
- **Single-Writer DB Ceiling:** SQLite WAL handles tens of concurrent submissions; enterprise scale ($>1,000\text{/s}$) requires PostgreSQL clustering.

---

### Slide 15: Future Work & Production Scaling Roadmap
- Full 4,000+ CarDD dataset retraining with generative weather augmentation.
- 3D Gaussian Splatting / Photogrammetry for volumetric dent measurement.
- Multimodal LLM integration (Gemini Flash / GPT-4o) for complex handwritten receipts.
- Merkle-tree cryptographic anchoring for legal non-repudiation in dispute tribunals.

---

### Slide 16: Conclusion & Viva Defense
- **Summary:** Delivered a fully functional, production-hardened, asynchronous decision-support prototype.
- **Open for Questions:** Thank you, esteemed examiners. We invite your questions and welcome live demonstration scenarios.
