"""Automated orchestration script for Phase 10 Stage 2 Load Testing.

Spawns an isolated Flask server, benchmarks 10, 25, and 50 concurrent user profiles,
evaluates SQLite DELETE vs WAL journal modes, measures system resource utilization,
validates SLAs, and produces structured performance metrics.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List

import psutil
import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.load.config import (
    LOAD_TEST_PORT,
    PROFILES,
    SLA_TARGETS,
)

PYTHON_EXE = sys.executable
OUTPUT_DIR = PROJECT_ROOT / "runs" / "phase10" / "load_test_artifacts"


def safe_float(val, default=0.0) -> float:
    """Safely converts string or None to float, handling 'N/A' from Locust."""
    if val is None or val == "" or val == "N/A":
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def wait_for_server(url: str, proc: subprocess.Popen = None, log_path: Path = None, timeout: float = 30.0) -> bool:
    """Polls ping endpoint until server is responsive."""
    start = time.time()
    while time.time() - start < timeout:
        if proc and proc.poll() is not None:
            err_msg = ""
            if log_path and log_path.exists():
                err_msg = log_path.read_text(encoding="utf-8", errors="ignore")[-2000:]
            print(f"Server process terminated prematurely with code {proc.returncode}:\n{err_msg}")
            return False
        try:
            r = requests.get(f"{url}/api/load-test/ping", timeout=1.0)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def run_single_locust_profile(
    profile_name: str,
    users: int,
    spawn_rate: float,
    run_time: str,
    host_url: str,
    output_prefix: Path,
    server_pid: int,
) -> Dict[str, Any]:
    """Executes a single headless Locust benchmark and collects telemetry."""
    print(f"\n======================================================================")
    print(f"Executing Load Profile: {profile_name} ({users} users, spawn_rate={spawn_rate}/s, duration={run_time})")
    print(f"======================================================================")

    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    csv_prefix = str(output_prefix)
    json_path = output_prefix.with_suffix(".json")

    locust_cmd = [
        PYTHON_EXE,
        "-m",
        "locust",
        "-f",
        str(PROJECT_ROOT / "tests" / "load" / "locustfile.py"),
        "--headless",
        "-u",
        str(users),
        "-r",
        str(spawn_rate),
        "-t",
        run_time,
        "--host",
        host_url,
        "--csv",
        csv_prefix,
        "--json-file",
        str(json_path),
        "--only-summary",
    ]

    # Start locust process
    locust_proc = subprocess.Popen(
        locust_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Monitor CPU and Memory while running
    cpu_samples = []
    mem_samples = []
    server_process = psutil.Process(server_pid) if server_pid and psutil.pid_exists(server_pid) else None

    while locust_proc.poll() is None:
        try:
            if server_process and server_process.is_running():
                cpu = server_process.cpu_percent(interval=0.5)
                mem = server_process.memory_info().rss / (1024 * 1024)  # MB
                cpu_samples.append(cpu)
                mem_samples.append(mem)
            else:
                time.sleep(0.5)
        except Exception:
            time.sleep(0.5)

    stdout, stderr = locust_proc.communicate()

    # Parse JSON results
    metrics = {
        "profile": profile_name,
        "users": users,
        "spawn_rate": spawn_rate,
        "run_time": run_time,
        "exit_code": locust_proc.returncode,
        "cpu_peak_pct": round(max(cpu_samples) if cpu_samples else 0.0, 2),
        "cpu_mean_pct": round(sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0.0, 2),
        "memory_peak_mb": round(max(mem_samples) if mem_samples else 0.0, 2),
        "memory_mean_mb": round(sum(mem_samples) / len(mem_samples) if mem_samples else 0.0, 2),
    }

    # Parse Locust stats CSV if generated
    stats_csv = Path(f"{csv_prefix}_stats.csv")
    if stats_csv.exists():
        import csv
        with open(stats_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            endpoint_stats = []
            aggregated = None
            for row in reader:
                if row.get("Name") == "Aggregated":
                    aggregated = row
                else:
                    endpoint_stats.append(row)

            if aggregated:
                num_requests = int(aggregated.get("Request Count", 0))
                num_failures = int(aggregated.get("Failure Count", 0))
                error_rate = (num_failures / num_requests * 100.0) if num_requests > 0 else 0.0

                metrics.update({
                    "total_requests": num_requests,
                    "successful_requests": num_requests - num_failures,
                    "failed_requests": num_failures,
                    "error_rate_pct": round(error_rate, 4),
                    "requests_per_second": safe_float(aggregated.get("Requests/s")),
                    "mean_latency_ms": safe_float(aggregated.get("Average Response Time")),
                    "min_latency_ms": safe_float(aggregated.get("Min Response Time")),
                    "max_latency_ms": safe_float(aggregated.get("Max Response Time")),
                    "p50_latency_ms": safe_float(aggregated.get("50%")),
                    "p90_latency_ms": safe_float(aggregated.get("90%")),
                    "p95_latency_ms": safe_float(aggregated.get("95%")),
                    "p99_latency_ms": safe_float(aggregated.get("99%")),
                    "endpoints": endpoint_stats,
                })

    # Parse failure details
    failures_csv = Path(f"{csv_prefix}_failures.csv")
    metrics["failures_breakdown"] = []
    if failures_csv.exists():
        import csv
        with open(failures_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            metrics["failures_breakdown"] = list(reader)

    print(f"Results for {profile_name}:")
    print(f"  Requests: {metrics.get('total_requests', 0)} total, {metrics.get('failed_requests', 0)} failed ({metrics.get('error_rate_pct', 0)}% error rate)")
    print(f"  Throughput: {metrics.get('requests_per_second', 0)} RPS")
    print(f"  Mean Latency: {metrics.get('mean_latency_ms', 0)} ms (Target: <500 ms)")
    print(f"  p95 Latency: {metrics.get('p95_latency_ms', 0)} ms")
    print(f"  p99 Latency: {metrics.get('p99_latency_ms', 0)} ms")
    print(f"  Max Latency: {metrics.get('max_latency_ms', 0)} ms")
    print(f"  Server CPU: Mean {metrics.get('cpu_mean_pct', 0)}%, Peak {metrics.get('cpu_peak_pct', 0)}%")
    print(f"  Server Mem: Mean {metrics.get('memory_mean_mb', 0)} MB, Peak {metrics.get('memory_peak_mb', 0)} MB")

    return metrics


def execute_full_load_benchmark() -> Dict[str, Any]:
    """Runs isolated server instances under DELETE and WAL modes, executing all target profiles."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    all_results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sla_targets": SLA_TARGETS,
        "profiles": {},
        "journal_mode_comparison": {},
    }

    # ------------------------------------------------------------------
    # Step 1: Baseline Profiles under Standard DELETE Journal Mode
    # ------------------------------------------------------------------
    print("\n>>> STARTING PHASE 10 STAGE 2 LOAD TESTING: DEFAULT DELETE MODE <<<")
    temp_dir_delete = tempfile.mkdtemp(prefix="claimsense_load_del_")
    server_proc_del = None
    try:
        server_log_path = OUTPUT_DIR / "server_delete.log"
        server_log_file = open(server_log_path, "w", encoding="utf-8")
        server_cmd = [
            PYTHON_EXE,
            str(PROJECT_ROOT / "tests" / "load" / "server.py"),
            "--dir",
            temp_dir_delete,
            "--port",
            str(LOAD_TEST_PORT),
        ]
        server_proc_del = subprocess.Popen(
            server_cmd,
            stdout=server_log_file,
            stderr=subprocess.STDOUT,
            text=True,
        )

        host_url = f"http://127.0.0.1:{LOAD_TEST_PORT}"
        if not wait_for_server(host_url, proc=server_proc_del, log_path=server_log_path, timeout=30.0):
            raise RuntimeError(f"Load test server failed to start on {host_url}")

        print(f"Isolated test server running on {host_url} (DELETE mode)")

        # Run 10 Users Profile
        p10_res = run_single_locust_profile(
            profile_name="10_users_delete",
            users=PROFILES["10_users"]["users"],
            spawn_rate=PROFILES["10_users"]["spawn_rate"],
            run_time=PROFILES["10_users"]["run_time"],
            host_url=host_url,
            output_prefix=OUTPUT_DIR / "run_10_users_delete",
            server_pid=server_proc_del.pid,
        )
        all_results["profiles"]["10_users_delete"] = p10_res

        # Run 25 Users Profile
        p25_res = run_single_locust_profile(
            profile_name="25_users_delete",
            users=PROFILES["25_users"]["users"],
            spawn_rate=PROFILES["25_users"]["spawn_rate"],
            run_time=PROFILES["25_users"]["run_time"],
            host_url=host_url,
            output_prefix=OUTPUT_DIR / "run_25_users_delete",
            server_pid=server_proc_del.pid,
        )
        all_results["profiles"]["25_users_delete"] = p25_res

        # Run 50 Users Profile
        p50_res = run_single_locust_profile(
            profile_name="50_users_delete",
            users=PROFILES["50_users"]["users"],
            spawn_rate=PROFILES["50_users"]["spawn_rate"],
            run_time=PROFILES["50_users"]["run_time"],
            host_url=host_url,
            output_prefix=OUTPUT_DIR / "run_50_users_delete",
            server_pid=server_proc_del.pid,
        )
        all_results["profiles"]["50_users_delete"] = p50_res

    finally:
        if server_proc_del:
            server_proc_del.terminate()
            try:
                server_proc_del.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_proc_del.kill()
        try:
            if 'server_log_file' in locals() and not server_log_file.closed:
                server_log_file.close()
            shutil.rmtree(temp_dir_delete, ignore_errors=True)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Step 2: High-Concurrency Benchmark under SQLite WAL Mode
    # ------------------------------------------------------------------
    print("\n>>> STARTING PHASE 10 STAGE 2 LOAD TESTING: ISOLATED WAL MODE <<<")
    temp_dir_wal = tempfile.mkdtemp(prefix="claimsense_load_wal_")
    server_proc_wal = None
    try:
        server_wal_log_path = OUTPUT_DIR / "server_wal.log"
        server_wal_log_file = open(server_wal_log_path, "w", encoding="utf-8")
        server_cmd_wal = [
            PYTHON_EXE,
            str(PROJECT_ROOT / "tests" / "load" / "server.py"),
            "--dir",
            temp_dir_wal,
            "--port",
            str(LOAD_TEST_PORT),
            "--wal",
        ]
        server_proc_wal = subprocess.Popen(
            server_cmd_wal,
            stdout=server_wal_log_file,
            stderr=subprocess.STDOUT,
            text=True,
        )

        host_url = f"http://127.0.0.1:{LOAD_TEST_PORT}"
        if not wait_for_server(host_url, proc=server_proc_wal, log_path=server_wal_log_path, timeout=30.0):
            raise RuntimeError(f"WAL load test server failed to start on {host_url}")

        print(f"Isolated test server running on {host_url} (WAL mode)")

        # Run 50 Users Stress Profile under WAL Mode
        p50_wal_res = run_single_locust_profile(
            profile_name="50_users_wal",
            users=PROFILES["50_users"]["users"],
            spawn_rate=PROFILES["50_users"]["spawn_rate"],
            run_time=PROFILES["50_users"]["run_time"],
            host_url=host_url,
            output_prefix=OUTPUT_DIR / "run_50_users_wal",
            server_pid=server_proc_wal.pid,
        )
        all_results["profiles"]["50_users_wal"] = p50_wal_res

        all_results["journal_mode_comparison"] = {
            "delete_mode_50_users": {
                "mean_latency_ms": p50_res.get("mean_latency_ms"),
                "p95_latency_ms": p50_res.get("p95_latency_ms"),
                "p99_latency_ms": p50_res.get("p99_latency_ms"),
                "rps": p50_res.get("requests_per_second"),
                "error_rate_pct": p50_res.get("error_rate_pct"),
            },
            "wal_mode_50_users": {
                "mean_latency_ms": p50_wal_res.get("mean_latency_ms"),
                "p95_latency_ms": p50_wal_res.get("p95_latency_ms"),
                "p99_latency_ms": p50_wal_res.get("p99_latency_ms"),
                "rps": p50_wal_res.get("requests_per_second"),
                "error_rate_pct": p50_wal_res.get("error_rate_pct"),
            },
        }

    finally:
        if server_proc_wal:
            server_proc_wal.terminate()
            try:
                server_proc_wal.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_proc_wal.kill()
        try:
            if 'server_wal_log_file' in locals() and not server_wal_log_file.closed:
                server_wal_log_file.close()
            shutil.rmtree(temp_dir_wal, ignore_errors=True)
        except Exception:
            pass

    # Save consolidated results JSON
    results_file = OUTPUT_DIR / "consolidated_load_test_results.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    print(f"\nConsolidated load test results saved to: {results_file}")
    return all_results


if __name__ == "__main__":
    execute_full_load_benchmark()
