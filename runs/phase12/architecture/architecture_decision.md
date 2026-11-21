# ClaimSense AI — Architectural Decision Record (ADR): Task Queue & Asynchronous Processing

**Status:** APPROVED & IMPLEMENTED  
**Date:** 2026-11-21  
**Milestone:** Phase 12  
**Context:** Decoupling compute-heavy OCR, YOLOv8 vision, and NLP narrative analysis from synchronous claim intake.

---

## 1. Context & Problem Statement

In Phase 11, claim submission executed synchronously within the WSGI HTTP request path. Processing a four-file claim required an average of **3,140 ms** across multipart parsing, disk persistence, PyMuPDF bitmap rendering, Tesseract OCR, YOLOv8 inference, NLP chronology extraction, and cross-source verification.

Under multi-user concurrency (tested in Phase 10 with Locust up to 50 users), synchronous 3+ second CPU-bound operations saturated WSGI threads (Gunicorn/Waitress), causing response latency to spike to 673 ms mean / 3,140 ms peak and risking gateway timeouts.

---

## 2. Decision Drivers

1. **Portability & Cross-Platform Developer Experience:** Native Windows development and self-contained automated pytest execution must run with zero configuration overhead and without requiring external Linux daemons.
2. **Production Container Scalability:** In production multi-container Docker deployments, web ingestion heads (`claimsense-app`) must asynchronously offload compute to dedicated worker containers (`claimsense-worker`).
3. **Idempotency & Duplicate Prevention:** Accidental double-clicks on claim submission must not dispatch duplicate neural-network inference passes or duplicate damage records.
4. **Reliability & Crash Recovery:** Workers that restart or crash mid-processing must not orphan claims; orphaned jobs must be detected and recovered automatically.
5. **Zero Regression Guarantee:** Backward compatibility with legacy synchronous endpoints (`?sync=true` or `ASYNC_PROCESSING_ENABLED=false`) must preserve 100% pass rates across existing test suites.

---

## 3. Evaluated Alternatives

| Dimension | Option A: Celery + Redis | Option B: RQ (Redis Queue) | Option C: Pluggable Dual-Engine Broker (SELECTED) |
| :--- | :--- | :--- | :--- |
| **Windows Local Dev** | Fails (`fork()` unsupported; requires billiard/gevent hacks) | Fails (`os.fork()` unsupported on Windows) | **Native Pass** (Threaded broker with SQLite state) |
| **Docker Production** | Excellent | Excellent | **Excellent** (Redis list protocol `RPUSH`/`BLPOP`) |
| **External Dependency in Tests**| Requires live Redis instance or mock overhead | Requires live Redis or mock overhead | **Zero Dependency** (Runs isolated SQLite thread pool) |
| **Architectural Complexity** | High (Kombu, Flower, broker/result backend) | Moderate | **Minimal / Maintainable** (Dual-broker abstraction) |
| **Dual-Write Dual-Loss Protection**| Requires separate outbox daemon | Requires separate outbox daemon | **Integrated** (Atomic SQLite transaction + task record) |

---

## 4. Architectural Verdict: Pluggable Dual-Engine Architecture

We adopt **Option C: Pluggable Dual-Engine Architecture** implemented via `TaskManager`:
- **Production Engine (`RedisTaskBroker`):** Utilizes lightweight, atomic Redis list commands (`RPUSH` and `BLPOP`) on queue `claimsense:tasks:claims`. Dedicated worker processes consume jobs and execute pipelines in isolated Linux containers.
- **Local / Test Engine (`ThreadedTaskBroker`):** Utilizes an in-process `ThreadPoolExecutor` with persistent SQLite task state. Automatically activated when Redis is absent or when running local tests.
- **Transactional Consistency:** A `ProcessingTask` database record is committed in the same database session as the `Claim`, ensuring dual-write integrity before dispatching to the broker.
