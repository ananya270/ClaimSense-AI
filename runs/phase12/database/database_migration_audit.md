# ClaimSense AI — Phase 12 Database Migration & Schema Audit
## Processing Tasks Persistence & Idempotency Audit

**Document Reference:** `runs/phase12/database/database_migration_audit.md`  
**Governance Date:** November 21, 2026  
**Subsystems:** SQLAlchemy ORM, SQLite Migration Engine, Task Persistence  

---

## 1. Schema Specification: `processing_tasks` Table

To track asynchronous claim processing lifecycles without mutating existing business tables (`claims`, `documents`, `extracted_information`, `vehicle_damage_analyses`, `reports`), Phase 12 introduces a dedicated `processing_tasks` table.

```sql
CREATE TABLE IF NOT EXISTS processing_tasks (
    task_id VARCHAR(64) PRIMARY KEY,
    claim_id VARCHAR(32) NOT NULL REFERENCES claims(claim_id),
    user_id INTEGER REFERENCES users(id),
    task_type VARCHAR(64) NOT NULL DEFAULT 'CLAIM_PIPELINE',
    status VARCHAR(32) NOT NULL DEFAULT 'QUEUED',
    current_stage VARCHAR(64) NOT NULL DEFAULT 'INTAKE',
    progress_percent INTEGER NOT NULL DEFAULT 0,
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    error_code VARCHAR(64),
    error_message TEXT,
    result_metadata TEXT,
    worker_id VARCHAR(64),
    created_at DATETIME NOT NULL,
    started_at DATETIME,
    completed_at DATETIME,
    updated_at DATETIME NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_processing_tasks_task_id ON processing_tasks(task_id);
CREATE INDEX IF NOT EXISTS ix_processing_tasks_claim_id ON processing_tasks(claim_id);
CREATE INDEX IF NOT EXISTS ix_processing_tasks_status ON processing_tasks(status);
CREATE INDEX IF NOT EXISTS ix_processing_tasks_user_id ON processing_tasks(user_id);
```

---

## 2. Field Functionality & Invariant Matrix

| Column Name | Data Type | Constraint | Purpose / Invariant |
|:---|:---:|:---:|:---|
| `task_id` | VARCHAR(64) | PRIMARY KEY | Unique UUID or deterministic identifier (`task-<claim_id>`). |
| `claim_id` | VARCHAR(32) | NOT NULL, FK, Indexed | Foreign key to `claims.claim_id`. One-to-many relationship. |
| `user_id` | INTEGER | FK, Indexed, Nullable | Claimant user ID for strict ownership and RBAC enforcement. |
| `task_type` | VARCHAR(64) | NOT NULL | Type of job (`CLAIM_PIPELINE`, `REPLACEMENT_VISION`, `REPORT_FREEZE`). |
| `status` | VARCHAR(32) | NOT NULL, Indexed | Lifecycle status: `QUEUED`, `PROCESSING`, `COMPLETED`, `FAILED`, `CANCELLED`. |
| `current_stage` | VARCHAR(64) | NOT NULL | Granular progression: `INTAKE`, `OCR_PROCESSING`, `DAMAGE_ANALYSIS`, `NLP_CHRONOLOGY`, `CROSS_SOURCE_VERIFICATION`, `COMPLETED`. |
| `progress_percent` | INTEGER | NOT NULL (0-100) | Numerical progress indicator for client-side visual progress bars. |
| `retry_count` | INTEGER | NOT NULL | Number of retries executed after transient failures. |
| `max_retries` | INTEGER | NOT NULL | Maximum retry limit (default: 3) to prevent poison pill loops. |
| `error_code` | VARCHAR(64) | Nullable | Machine-readable error code (e.g., `OCR_FAILED`, `CORRUPTION_DETECTED`). |
| `error_message` | TEXT | Nullable | Safe, sanitized error description (zero stack traces or internal paths). |
| `result_metadata`| TEXT | Nullable | Serialized JSON containing summary metrics upon successful completion. |
| `worker_id` | VARCHAR(64) | Nullable | Unique identifier of the processing worker/thread. |
| `timestamps` | DATETIME | ISO 8601 UTC | `created_at`, `started_at`, `completed_at`, `updated_at`. |

---

## 3. Migration Safety & Backward-Compatibility Verification

1. **Non-Destructive DDL:** The migration is additive only. Existing tables (`claims`, `users`, `reports`) are untouched.
2. **Automated Deployment:** Implemented in `backend/database/db.py:_ensure_schema_migrations()`, executing automatically during `init_database()`.
3. **Data Integrity Audit:**
   - Pre-migration row count on production database: 23 claims, 17 users, 6 reports.
   - Post-migration row count: identical; zero data rows altered or dropped.
4. **Rollback Plan:**
   - Drop the `processing_tasks` table: `DROP TABLE IF EXISTS processing_tasks;`
   - Reverts schema to Phase 11 without impacting claim history or reports.
