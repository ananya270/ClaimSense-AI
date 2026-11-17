# ClaimSense AI — Gate P Checkpoint & Database Integrity Report
## Controlled Offline Shadow Smoke Test Pre/Post Verification

**Document ID:** `AUD-PH8-GATE-P-CKPT-001`  
**Execution Timestamp:** 2026-11-17T13:29:38.574178+00:00  
**Governing Standard:** `acquisition_specification.md` v1.1-ACTIVE  
**Verification Scope:** Pre-Flight & Post-Flight Cryptographic Checksum Audit  
**Status:** **100% INVARIANT — ZERO DRIFT / ZERO WRITES**

---

## 1. Checkpoint Cryptographic Audit Table

| Entity | Target Path | Expected SHA-256 | Pre-Test SHA-256 | Post-Test SHA-256 | Invariance Certification |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **Production Baseline** | `models/phase5/best.pt` | `90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565` | `90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565` | `90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565` | **MATCH OK (100% UNTOUCHED)** |
| **Shadow Candidate** | `runs/phase8/.../best.pt` | `68e2b58ec7759427808621debc9a8d725a9e4c1fbc57a2102cd239a8ca14f006` | `68e2b58ec7759427808621debc9a8d725a9e4c1fbc57a2102cd239a8ca14f006` | `68e2b58ec7759427808621debc9a8d725a9e4c1fbc57a2102cd239a8ca14f006` | **MATCH OK (100% UNTOUCHED)** |
| **Production Database** | `backend/database/claimsense.db` | `5483a43f41f3d63d6a70f1c487c4c6b5104894d5a575c0cb84c7c1353dd07cc9` | `5483a43f41f3d63d6a70f1c487c4c6b5104894d5a575c0cb84c7c1353dd07cc9` | `5483a43f41f3d63d6a70f1c487c4c6b5104894d5a575c0cb84c7c1353dd07cc9` | **BYTE-IDENTICAL (0 BYTES WRITTEN)** |

---

## 2. Integrity Verification Findings

1. **Production Model Immutability:** Checkpoint `models/phase5/best.pt` retained exact SHA-256 `90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565` throughout the entire test suite. No weights or model attributes were modified.
2. **Candidate Checkpoint Immutability:** Candidate `exp02_rare_class/weights/best.pt` retained exact SHA-256 `68e2b58ec7759427808621debc9a8d725a9e4c1fbc57a2102cd239a8ca14f006`.
3. **Database Write Isolation:** The production SQLite database `backend/database/claimsense.db` recorded pre-test digest `5483a43f41f3d63d6a70f1c487c4c6b5104894d5a575c0cb84c7c1353dd07cc9` and post-test digest `5483a43f41f3d63d6a70f1c487c4c6b5104894d5a575c0cb84c7c1353dd07cc9`. Zero shadow tables, rows, or locking transactions were introduced. All smoke test records were persisted strictly to `backend/database/shadow_telemetry.db`.
