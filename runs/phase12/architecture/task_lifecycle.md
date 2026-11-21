# ClaimSense AI — Phase 12 Task Lifecycle & State Machine Specification

## 1. Task State Machine Diagram

```mermaid
stateDiagram-v2
    [*] --> QUEUED: Enqueue Claim Task (HTTP 202)
    QUEUED --> PROCESSING: Worker Picks Up Job
    
    state PROCESSING {
        [*] --> INTAKE: 10%
        INTAKE --> OCR_PROCESSING: 25%
        OCR_PROCESSING --> DAMAGE_ANALYSIS: 55%
        DAMAGE_ANALYSIS --> NLP_CHRONOLOGY: 75%
        NLP_CHRONOLOGY --> CROSS_SOURCE_VERIFICATION: 90%
        CROSS_SOURCE_VERIFICATION --> REPORT_PERSISTENCE: 95%
        REPORT_PERSISTENCE --> [*]
    }

    PROCESSING --> COMPLETED: All Stages Succeeded (100%)
    PROCESSING --> QUEUED: Transient Failure & Retries Remain (retry < max_retries)
    PROCESSING --> FAILED: Permanent Failure or Timeout Exhaustion
    FAILED --> QUEUED: Manual Retry via /api/claims/id/retry-task
    COMPLETED --> [*]
```

---

## 2. Valid State Transitions & Invariants

| From State | Allowed To State | Trigger / Condition | Invariant Guaranteed |
| :--- | :--- | :--- | :--- |
| **`[*]`** | **`QUEUED`** | Initial claim intake or manual retry | Task record minted; `progress_percent=5` |
| **`QUEUED`** | **`PROCESSING`** | Worker thread/process claims job | `started_at` timestamp recorded; worker ID stamped |
| **`PROCESSING`**| **`PROCESSING`** | Intermediate stage updates | Monotonically increasing progress percent ($10 \rightarrow 95$) |
| **`PROCESSING`**| **`COMPLETED`** | Terminal verification and report frozen | `completed_at` set; `progress_percent=100`; cannot revert |
| **`PROCESSING`**| **`QUEUED`** | Auto-recovery of stale heartbeat | `retry_count` incremented; stage reset to `INTAKE` |
| **`PROCESSING`**| **`FAILED`** | Unrecoverable error or max retries exceeded | `error_code` and sanitized `error_message` persisted |
| **`FAILED`** | **`QUEUED`** | Explicit call to `POST /retry-task` | Re-evaluated by worker; resets failure status |

---

## 3. Terminal State Immutability

Once a task transitions to **`COMPLETED`**, subsequent task submission calls on the same `claim_id` return the existing task without altering its completed state. Under no circumstances can a completed claim be rolled back to `QUEUED` or `PROCESSING` by background workers.
