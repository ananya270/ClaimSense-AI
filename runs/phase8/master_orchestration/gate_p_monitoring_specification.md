# ClaimSense AI — Gate P 14-Day Shadow Trial Monitoring Specification

**Document ID:** `SPC-PH8-GATE-P-MON-001`  
**Date:** 2026-11-17  
**Governing Standard:** `acquisition_specification.md` v1.1-ACTIVE  
**System Target:** Non-Blocking Shadow Telemetry & Health Monitoring  
**Target Invariant:** Zero Disruption to Authoritative Claim Processing

---

## 1. Shadow Telemetry Data Schema

All shadow model outputs and system health telemetry must be recorded in an isolated SQLite database (`runs/phase8/shadow_trial/shadow_telemetry.db`) using the schema below:

```sql
CREATE TABLE IF NOT EXISTS shadow_inference_telemetry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    claim_id TEXT NOT NULL,
    image_filename TEXT NOT NULL,
    image_sha256 TEXT NOT NULL,
    image_width INTEGER NOT NULL,
    image_height INTEGER NOT NULL,
    prod_checkpoint_sha TEXT NOT NULL,
    exp02_checkpoint_sha TEXT NOT NULL,
    prod_detections_json TEXT NOT NULL,
    exp02_detections_json TEXT NOT NULL,
    prod_box_count INTEGER NOT NULL,
    exp02_box_count INTEGER NOT NULL,
    disagreement_status TEXT NOT NULL, -- 'AGREEMENT', 'EXP02_NEW_DEFECT', 'EXP02_MISSED_PROD', 'CLASS_MISMATCH'
    disagreement_severity TEXT NOT NULL, -- 'NONE', 'LOW', 'MEDIUM', 'HIGH', 'CRACK_FLAG'
    shadow_latency_ms REAL NOT NULL,
    gpu_vram_allocated_mb REAL NOT NULL,
    host_cpu_pct REAL NOT NULL,
    host_gpu_pct REAL NOT NULL,
    circuit_breaker_state TEXT NOT NULL -- 'CLOSED', 'OPEN'
);
```

---

## 2. Daily Health Metrics & Service Level Objectives (SLOs)

A daily health report must be automatically compiled every 24 hours during the trial:

| Metric Category | Target SLO | Warning Threshold (Yellow Alert) | Critical Breach Threshold (Circuit Breaker Trip) |
| :--- | :---: | :---: | :---: |
| **Shadow Inference Latency (p50)** | $\le 100$ ms | $> 120$ ms | $> 150$ ms |
| **Shadow Inference Latency (p99)** | $\le 200$ ms | $> 250$ ms | $> 300$ ms |
| **Shadow Worker Error Rate** | $0.00\%$ | $> 0.50\%$ | $> 2.00\%$ (or 3 consecutive errors) |
| **Host System CPU Utilization** | $< 50\%$ | $\ge 60\%$ | $> 70\%$ |
| **GPU Utilization (RTX 3050)** | $< 50\%$ | $\ge 60\%$ | $> 70\%$ |
| **Peak GPU VRAM Footprint** | $\le 2048$ MB | $> 2500$ MB | $> 3000$ MB |
| **Production Claim Impact** | Strictly 0 | 0.001% latency increase | Any production timeout or error |

---

## 3. Disagreement Categorization & Triage Matrix

Every shadow observation is classified automatically according to divergence archetype:

| Category Code | Disagreement Type | Criteria | Action Required |
| :---: | :--- | :--- | :--- |
| **DIS-01** | High-Confidence Divergence | One model predicts $\tau \ge 0.50$, other predicts 0 boxes. | Flagged for Blind Human Review cohort. |
| **DIS-02** | Suspected Crack / Tear | Production or metadata mentions crack; EXP02 predicts 0. | Mandatory Adjuster Escalation (Risk 1). |
| **DIS-03** | Specular Reflection / Glare | EXP02 predicts 0; Production predicts multiple small boxes on sunny panels. | Telemetry logged; evaluated for Canary Glare index. |
| **DIS-04** | Rare Defect Discovery | EXP02 predicts `lamp broken` or `tire flat`; Prod predicts 0. | Flagged for blind physical verification. |
| **DIS-05** | Agreement | Both models predict identical damage categories ($\pm 1$ box). | Standard logging; no review required. |

---

## 4. Daily Operational Audit Cadence

1. **Daily 08:00 UTC Automated Log Scrub:**
   * Script verifies integrity of `shadow_telemetry.db`.
   * Calculates 24-hour mean latency, error counts, and concordance rate.
   * Confirms `models/phase5/best.pt` SHA-256 remains `90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565`.
2. **Daily 17:00 UTC Adjuster Queue Assembly:**
   * Triage script extracts top disagreement cases for the blind adjudication bucket.
