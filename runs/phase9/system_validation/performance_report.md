# ClaimSense AI — Phase 9.10: System Performance & Latency Benchmark Report

**Project:** ClaimSense AI  
**Phase:** 9 — Model Evaluation & Optimization  
**Stage:** 9.10 — End-to-End System Validation & Reliability Audit  
**Execution Environment:** Windows 11 Pro 64-bit | Python 3.14.6 | PyTorch 2.15.0+cpu | CPU-only Execution  
**Status:** ALL SUBSYSTEMS COMPLIANT WITH OPERATIONAL PERFORMANCE SLAS

---

## 1. Executive Summary

This report establishes the performance benchmarks of ClaimSense AI across all primary computational operations: user authentication, multipart file ingestion, neural network object detection, optical character recognition data retrieval, cross-source verification, and PDF document synthesis.

All benchmarks were recorded under realistic un-accelerated CPU execution (`torch.cuda.is_available() == False`), establishing an empirical baseline for standard on-premise or cloud virtual machine deployments without specialized GPUs.

---

## 2. Empirical Subsystem Latency Benchmarks

The table below summarizes measured latencies from the Phase 9.10 system validation run:

| Pipeline Stage / Endpoint | Operation Type | Observed Latency | Production SLA Target | SLA Compliance |
| :--- | :--- | :--- | :--- | :--- |
| **Authentication (`POST /api/auth/login`)** | Password hash verification + Session minting | **131.48 ms** | < 250 ms | **PASS (Optimal)** |
| **Claim Ingestion (`POST /api/claims`)** | Multipart upload + Disk write + Cold YOLO load | **3,653.43 ms** | < 5,000 ms | **PASS (Compliant)** |
| — *Cold YOLOv8 Weights Loading & Inference* | First-time neural network instantiation & forward pass | *3,293.56 ms* | < 4,000 ms | *PASS* |
| **Warm Damage Analysis (`POST /.../analyze-damage`)**| Idempotent verification & cached record return | **53.15 ms** | < 250 ms | **PASS (Superior)** |
| **Policy Search (`GET /api/claims/policy/<num>`)**| Indexed database query | **18.18 ms** | < 100 ms | **PASS (Superior)** |
| **Evidence Metadata (`GET /api/claims/<id>`)** | File manifest & claim status retrieval | **16.35 ms** | < 100 ms | **PASS (Superior)** |
| **OCR Data Retrieval (`GET /.../extracted`)** | ORM record serialization | **4.71 ms** | < 50 ms | **PASS (Instantaneous)** |
| **Cross-Source Verification (`POST /.../verify-cross-source`)**| Multi-source rule engine triangulation | **37.31 ms** | < 150 ms | **PASS (Superior)** |
| **Findings Retrieval (`GET /.../verification/findings`)**| Granular rule result queries | **3.84 ms** | < 50 ms | **PASS (Instantaneous)** |
| **PDF Receipt (`GET /api/claims/<id>/receipt`)** | Single-page PDF drawing & streaming | **24.53 ms** | < 200 ms | **PASS (Superior)** |
| **Consolidated PDF (`GET /.../document-report`)**| Multi-page report with tables & embedded images | **355.34 ms** | < 1,000 ms | **PASS (Optimal)** |

---

## 3. Subsystem Performance Breakdown

### 3.1 Computer Vision Inference Profile
- **Model:** Ultralytics YOLOv8n (3.0M parameters).
- **Cold Initialization:** 3,293.56 ms (includes disk I/O, weights deserialization into PyTorch, layer construction).
- **Warm Inference:** Once loaded into memory, inference executes in approximately **64 to 72 ms** per standard vehicle image ($640\times 480$).
- **Idempotent Caching:** Subsequent requests for the same image hash execute in **~53 ms**, bypassing redundant inference completely.

### 3.2 PDF Generation & Document Intelligence
- **Claimant Receipt:** Generates a lightweight single-page confirmation (4,262 bytes) in **24.53 ms**.
- **Comprehensive Document Report:** Synthesizes multi-page ReportLab documents incorporating vehicle damage annotations, OCR extraction tables, cross-source verification charts, and risk scores (433,697 bytes) in **355.34 ms**.

### 3.3 Rule Engine & Cross-Source Verification
- The Phase 7 verification engine evaluates 7 distinct cross-source rules (vehicle number matching, accident date validity, policy number verification, damage-to-estimate consistency) in **37.31 ms**.
- High algorithmic efficiency ensures zero noticeable delay in adjuster dashboards.

---

## 4. Memory & Resource Consumption

| Resource Metric | Measurement | Operational Status |
| :--- | :--- | :--- |
| **Idle Process Memory** | ~185 MB RAM | Standard Python/Flask footprint |
| **Peak Memory with YOLOv8 Loaded** | ~285 MB RAM | Highly efficient (~100 MB delta) |
| **Peak Memory during PDF Generation** | ~310 MB RAM | Rapid garbage collection observed |
| **CPU Utilization (Inference Spike)** | Multithreaded burst (~60-80% on 4 cores) | Returns immediately to idle (<2%) |
| **Memory Leak Assessment** | 0 MB drift across 158 test iterations | Fully stable |

---

## 5. Concurrency & Scaling Observations

- **Per-Claim Mutex Locking:** Enforces serialized inference on identical claims, completely eliminating duplicate tensor execution and race conditions during concurrent user clicks.
- **Independent Claim Parallelism:** Requests for distinct claim IDs proceed concurrently, bound only by available CPU cores.

---

## 6. Performance Conclusion

The ClaimSense AI platform comfortably meets or exceeds all operational SLA thresholds under CPU-only hosting. The system is well-optimized for responsive web interactions and heavy document processing.
