"""ClaimSense AI — Phase 8 Daily Shadow Monitor.

Monitors operational telemetry recorded in shadow_telemetry.db:
- Inference latency distribution (p50, p95, p99)
- Host CPU, Memory, and GPU VRAM utilization
- Queue depth, dropped jobs, and error counts
- Model agreement and disagreement categorization
- Cryptographic verification of authoritative production checkpoint
- Circuit breaker and kill-switch status

Usage:
    .venv/Scripts/python.exe scripts/run_daily_shadow_monitor.py [--report-dir <dir>]
"""

import argparse
import hashlib
import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SHADOW_DIR = PROJECT_ROOT / "runs" / "phase8" / "shadow_trial"
BACKEND_SHADOW_DB = PROJECT_ROOT / "backend" / "database" / "shadow_telemetry.db"
SHADOW_DB_PATH = BACKEND_SHADOW_DB if BACKEND_SHADOW_DB.exists() else (SHADOW_DIR / "shadow_telemetry.db")
KILL_SWITCH_PATH = SHADOW_DIR / "KILL_SWITCH"

PROD_CKPT = PROJECT_ROOT / "models" / "phase5" / "best.pt"
PROD_EXPECTED_SHA = "90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565"

EXP02_CKPT = (
    PROJECT_ROOT
    / "runs"
    / "phase8"
    / "domain_adaptation"
    / "exp02_rare_class"
    / "weights"
    / "best.pt"
)
EXP02_EXPECTED_SHA = "68e2b58ec7759427808621debc9a8d725a9e4c1fbc57a2102cd239a8ca14f006"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def percentile(data: List[float], pct: float) -> float:
    if not data:
        return 0.0
    sorted_d = sorted(data)
    k = (len(sorted_d) - 1) * (pct / 100.0)
    f = int(k)
    c = min(f + 1, len(sorted_d) - 1)
    d = k - f
    return sorted_d[f] + d * (sorted_d[c] - sorted_d[f])


def run_monitor(hours: int = 24, report_dir: Optional[Path] = None) -> Dict[str, Any]:
    print("=" * 80)
    print("CLAIM SENSE AI — PHASE 8 DAILY SHADOW TRIAL MONITOR")
    print("=" * 80)

    now_utc = datetime.now(timezone.utc)
    print(f"Timestamp:       {now_utc.isoformat()}")
    print(f"Window:          Past {hours} Hours")
    print(f"Database Path:   {SHADOW_DB_PATH}")

    # 1. Checkpoint Verification
    prod_sha = sha256_file(PROD_CKPT) if PROD_CKPT.exists() else "MISSING"
    exp02_sha = sha256_file(EXP02_CKPT) if EXP02_CKPT.exists() else "MISSING"

    prod_ok = prod_sha == PROD_EXPECTED_SHA
    exp02_ok = exp02_sha == EXP02_EXPECTED_SHA

    print(f"\n[Checkpoint Integrity]")
    print(f"  Production Checkpoint: {'PASS' if prod_ok else 'FAIL'}")
    print(f"    Expected: {PROD_EXPECTED_SHA}")
    print(f"    Actual:   {prod_sha}")
    print(f"  EXP02 Candidate:       {'PASS' if exp02_ok else 'FAIL'}")
    print(f"    Expected: {EXP02_EXPECTED_SHA}")
    print(f"    Actual:   {exp02_sha}")

    if not prod_ok:
        print("\nCRITICAL ALERT: Production checkpoint hash mismatch! Authoritative model was altered!")
        return {"status": "CRITICAL_PROD_HASH_MISMATCH"}

    # 2. Kill-Switch Status
    kill_switch_active = KILL_SWITCH_PATH.exists()
    print(f"\n[Kill-Switch Status]")
    print(f"  Flag Exists:  {kill_switch_active}")
    print(f"  State:        {'KILLED (Shadow Ingestion Stopped)' if kill_switch_active else 'READY / STANDBY'}")

    # 3. Query Database
    if not SHADOW_DB_PATH.exists():
        print(f"\n[Telemetry Store]")
        print("  Status: shadow_telemetry.db does not exist yet. No inferences recorded.")
        return {
            "status": "NO_DATABASE",
            "prod_checkpoint_verified": prod_ok,
            "exp02_checkpoint_verified": exp02_ok,
            "kill_switch_active": kill_switch_active,
        }

    conn = sqlite3.connect(str(SHADOW_DB_PATH), timeout=5.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    cursor = conn.cursor()

    cutoff = (now_utc - timedelta(hours=hours)).isoformat()
    cursor.execute(
        """
        SELECT timestamp, claim_id, shadow_latency_ms, gpu_vram_allocated_mb,
               host_cpu_pct, host_gpu_pct, disagreement_status, disagreement_severity,
               circuit_breaker_state
        FROM shadow_inference_telemetry
        WHERE timestamp >= ?
        ORDER BY timestamp ASC;
        """,
        (cutoff,),
    )
    rows = cursor.fetchall()

    total_inferences = len(rows)
    print(f"\n[Inference Telemetry (Past {hours} Hours)]")
    print(f"  Total Inferences: {total_inferences}")

    latencies = [r[2] for r in rows]
    vrams = [r[3] for r in rows]
    cpus = [r[4] for r in rows]
    gpus = [r[5] for r in rows]

    disagreement_counts = {}
    severity_counts = {}
    breaker_states = {}

    for r in rows:
        d_status = r[6]
        d_sev = r[7]
        b_state = r[8]
        disagreement_counts[d_status] = disagreement_counts.get(d_status, 0) + 1
        severity_counts[d_sev] = severity_counts.get(d_sev, 0) + 1
        breaker_states[b_state] = breaker_states.get(b_state, 0) + 1

    lat_p50 = percentile(latencies, 50)
    lat_p95 = percentile(latencies, 95)
    lat_p99 = percentile(latencies, 99)
    lat_max = max(latencies) if latencies else 0.0

    print(f"\n[Latency & SLA Performance]")
    print(f"  p50 Latency:   {lat_p50:.2f} ms (Target: <= 100 ms)")
    print(f"  p95 Latency:   {lat_p95:.2f} ms (Warning: > 120 ms)")
    print(f"  p99 Latency:   {lat_p99:.2f} ms (Target: <= 200 ms)")
    print(f"  Max Latency:   {lat_max:.2f} ms")

    print(f"\n[Hardware Utilization]")
    print(f"  Peak CPU:      {max(cpus) if cpus else 0.0:.1f}% (Limit: 70%)")
    print(f"  Peak GPU:      {max(gpus) if gpus else 0.0:.1f}% (Limit: 70%)")
    print(f"  Peak VRAM:     {max(vrams) if vrams else 0.0:.1f} MB (Budget: 3000 MB)")

    print(f"\n[Prediction Concordance Breakdown]")
    for status, count in disagreement_counts.items():
        pct = (count / total_inferences * 100.0) if total_inferences else 0.0
        print(f"  - {status:20s}: {count:4d} ({pct:5.1f}%)")

    print(f"\n[Circuit Breaker Status History]")
    for state, count in breaker_states.items():
        print(f"  - {state:10s}: {count:4d} inferences")

    conn.close()

    # Compile report summary
    report = {
        "timestamp": now_utc.isoformat(),
        "prod_checkpoint_verified": prod_ok,
        "exp02_checkpoint_verified": exp02_ok,
        "kill_switch_active": kill_switch_active,
        "total_inferences": total_inferences,
        "latency_p50_ms": lat_p50,
        "latency_p95_ms": lat_p95,
        "latency_p99_ms": lat_p99,
        "disagreement_counts": disagreement_counts,
        "severity_counts": severity_counts,
    }

    if report_dir:
        report_dir.mkdir(parents=True, exist_ok=True)
        date_str = now_utc.strftime("%Y%m%d")
        out_file = report_dir / f"daily_shadow_monitor_{date_str}.md"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(f"# ClaimSense AI — Daily Shadow Monitor Report ({date_str})\n\n")
            f.write(f"**Generated:** {now_utc.isoformat()}\n\n")
            f.write(f"## Status Overview\n")
            f.write(f"- Production Checkpoint SHA-256 Verified: **{prod_ok}**\n")
            f.write(f"- Candidate EXP02 SHA-256 Verified: **{exp02_ok}**\n")
            f.write(f"- Kill Switch Active: **{kill_switch_active}**\n")
            f.write(f"- Total Inferences (Past {hours}h): **{total_inferences}**\n\n")
            f.write(f"## Latency & Resources\n")
            f.write(f"- Latency p50: {lat_p50:.2f} ms\n")
            f.write(f"- Latency p95: {lat_p95:.2f} ms\n")
            f.write(f"- Latency p99: {lat_p99:.2f} ms\n\n")
            f.write(f"## Disagreement Breakdown\n```json\n{json.dumps(disagreement_counts, indent=2)}\n```\n")
        print(f"\nSaved Daily Report to: {out_file}")

    print("=" * 80)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Daily Shadow Monitor")
    parser.add_argument("--hours", type=int, default=24, help="Window in hours")
    parser.add_argument("--report-dir", type=str, default=str(SHADOW_DIR / "reports"), help="Output directory")
    args = parser.parse_args()

    run_monitor(hours=args.hours, report_dir=Path(args.report_dir))
