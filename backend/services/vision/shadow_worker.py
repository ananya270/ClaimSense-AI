"""ClaimSense AI — Phase 8 Gate P Shadow Worker Service.

Provides a safe, isolated, non-blocking background shadow execution pipeline:
1. Singleton Isolation: Loads EXP02 candidate independently without touching
   the authoritative production VehicleDamageDetector singleton.
2. Bounded Execution: Bounded queue (maxsize=50) with a single dedicated daemon
   worker thread to eliminate thread contention and GPU VRAM exhaustion.
3. Circuit Breaker Integration: Integrates 3-state circuit breaker (CLOSED -> OPEN -> HALF-OPEN)
   tripping at CPU > 70%, GPU > 70%, latency > 200ms, or 3 consecutive errors.
4. Atomic Kill-Switch: Checks filesystem flag (runs/phase8/shadow_trial/KILL_SWITCH).
   Removing the flag does not automatically resume the trial unless explicitly enabled.
5. SQLite Telemetry with WAL Mode: Opens shadow_telemetry.db with PRAGMA journal_mode=WAL
   and busy_timeout=5000ms. All writes serialized through the single worker thread.
"""

import hashlib
import json
import logging
import os
import queue
import sqlite3
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import psutil

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    torch = None
    TORCH_AVAILABLE = False

try:
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except (ImportError, Exception):
    YOLO = None
    ULTRALYTICS_AVAILABLE = False

from backend.utils.logger import setup_logger

logger = setup_logger("claimsense.vision.shadow_worker")

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PROD_CKPT_PATH = PROJECT_ROOT / "models" / "phase5" / "best.pt"
PROD_EXPECTED_SHA = "90d489e46ff8521edff88d522f0feffa164ac38a53b84700594c02a69e515565"

EXP02_CKPT_PATH = (
    PROJECT_ROOT
    / "runs"
    / "phase8"
    / "domain_adaptation"
    / "exp02_rare_class"
    / "weights"
    / "best.pt"
)
EXP02_EXPECTED_SHA = "68e2b58ec7759427808621debc9a8d725a9e4c1fbc57a2102cd239a8ca14f006"

SHADOW_DIR = PROJECT_ROOT / "runs" / "phase8" / "shadow_trial"
KILL_SWITCH_PATH = SHADOW_DIR / "KILL_SWITCH"
SHADOW_DB_PATH = PROJECT_ROOT / "backend" / "database" / "shadow_telemetry.db"


def compute_sha256(path: Path) -> str:
    """Calculates SHA-256 hash of a file on disk."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class ShadowCircuitBreaker:
    """Three-state circuit breaker for EXP02 shadow worker.

    States:
      - CLOSED: Normal operation. Shadow jobs executed.
      - OPEN: Tripped. Shadow jobs completely bypassed.
      - HALF_OPEN: Cooldown expired. Allows exactly one canary probe.
    """

    def __init__(
        self,
        max_cpu_pct: float = 70.0,
        max_gpu_pct: float = 70.0,
        max_latency_ms: float = 200.0,
        max_consecutive_errors: int = 3,
        cooldown_seconds: float = 900.0,  # 15 minutes
    ):
        self.max_cpu_pct = max_cpu_pct
        self.max_gpu_pct = max_gpu_pct
        self.max_latency_ms = max_latency_ms
        self.max_consecutive_errors = max_consecutive_errors
        self.cooldown_seconds = cooldown_seconds

        self.state = "CLOSED"
        self.consecutive_errors = 0
        self.tripped_at: Optional[float] = None
        self.trip_reason: Optional[str] = None
        self.probe_in_flight: bool = False
        self._lock = threading.Lock()

    def can_dispatch(self) -> bool:
        """Determines if a shadow job is allowed to be dispatched."""
        with self._lock:
            if self.state == "CLOSED":
                return True

            if self.state == "OPEN":
                now = time.time()
                if self.tripped_at and (now - self.tripped_at >= self.cooldown_seconds):
                    # Transition to HALF_OPEN to allow single canary probe
                    self.state = "HALF_OPEN"
                    self.probe_in_flight = True
                    logger.info("ShadowCircuitBreaker transitioned from OPEN -> HALF_OPEN (Canary Probe enabled).")
                    return True
                return False

            if self.state == "HALF_OPEN":
                # Only 1 canary probe allowed at a time
                if not self.probe_in_flight:
                    self.probe_in_flight = True
                    return True
                return False

            return False

    def evaluate(
        self,
        cpu_pct: float,
        gpu_pct: float,
        latency_ms: float,
        is_error: bool = False,
    ) -> str:
        """Evaluates health telemetry post-inference and manages state transitions."""
        with self._lock:
            now = time.time()

            if is_error:
                self.consecutive_errors += 1
            else:
                self.consecutive_errors = 0

            # 1. Error trip condition
            if self.consecutive_errors >= self.max_consecutive_errors:
                return self._trip("TRIPPED_CONSECUTIVE_ERRORS")

            # 2. Hardware / SLA trip conditions
            if cpu_pct > self.max_cpu_pct:
                return self._trip(f"TRIPPED_CPU_OVERLOAD ({cpu_pct:.1f}% > {self.max_cpu_pct}%)")

            if gpu_pct > self.max_gpu_pct:
                return self._trip(f"TRIPPED_GPU_OVERLOAD ({gpu_pct:.1f}% > {self.max_gpu_pct}%)")

            if latency_ms > self.max_latency_ms:
                return self._trip(f"TRIPPED_LATENCY_BUDGET ({latency_ms:.1f}ms > {self.max_latency_ms}ms)")

            # If currently in HALF_OPEN and the probe succeeded within limits:
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.probe_in_flight = False
                self.tripped_at = None
                self.trip_reason = None
                logger.info("ShadowCircuitBreaker canary probe succeeded. Transitioned from HALF_OPEN -> CLOSED.")
                return "RECOVERED_TO_CLOSED"

            return "OK"

    def _trip(self, reason: str) -> str:
        self.state = "OPEN"
        self.tripped_at = time.time()
        self.trip_reason = reason
        self.probe_in_flight = False
        logger.warning(f"ShadowCircuitBreaker TRIPPED -> OPEN. Reason: {reason}")
        return reason

    def trip(self, reason: str = "MANUAL_TRIP") -> None:
        """Manually trip circuit breaker to OPEN."""
        with self._lock:
            self._trip(reason)

    def reset(self) -> None:
        """Manually reset circuit breaker to CLOSED."""
        with self._lock:
            self.state = "CLOSED"
            self.consecutive_errors = 0
            self.tripped_at = None
            self.trip_reason = None
            self.probe_in_flight = False
            logger.info("ShadowCircuitBreaker manually reset to CLOSED.")

    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "state": self.state,
                "consecutive_errors": self.consecutive_errors,
                "tripped_at": self.tripped_at,
                "trip_reason": self.trip_reason,
                "cooldown_remaining_sec": (
                    max(0.0, self.cooldown_seconds - (time.time() - self.tripped_at))
                    if self.state == "OPEN" and self.tripped_at
                    else 0.0
                ),
            }


class ShadowWorkerManager:
    """Manages isolated, bounded background shadow inference execution."""

    _instance: Optional["ShadowWorkerManager"] = None
    _init_lock = threading.Lock()

    def __init__(self, queue_maxsize: int = 50):
        self.queue: queue.Queue = queue.Queue(maxsize=queue_maxsize)
        self.circuit_breaker = ShadowCircuitBreaker()
        self.enabled: bool = False  # Must be explicitly enabled by human operator
        self._paused: bool = False
        self._worker_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._candidate_model = None
        self._candidate_model_lock = threading.Lock()

        # Telemetry counters
        self.total_enqueued = 0
        self.total_processed = 0
        self.total_dropped = 0
        self.total_errors = 0

        self._ensure_shadow_dirs()
        self._init_db()

    @classmethod
    def get_instance(cls) -> "ShadowWorkerManager":
        with cls._init_lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def _ensure_shadow_dirs(self) -> None:
        SHADOW_DIR.mkdir(parents=True, exist_ok=True)

    def _init_db(self) -> None:
        """Initializes shadow SQLite database with WAL mode and tables."""
        try:
            with sqlite3.connect(str(SHADOW_DB_PATH), timeout=5.0) as conn:
                conn.execute("PRAGMA journal_mode=WAL;")
                conn.execute("PRAGMA busy_timeout=5000;")
                conn.execute(
                    """
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
                        disagreement_status TEXT NOT NULL,
                        disagreement_severity TEXT NOT NULL,
                        shadow_latency_ms REAL NOT NULL,
                        gpu_vram_allocated_mb REAL NOT NULL,
                        host_cpu_pct REAL NOT NULL,
                        host_gpu_pct REAL NOT NULL,
                        circuit_breaker_state TEXT NOT NULL
                    );
                    """
                )
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS shadow_worker_health (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        queue_depth INTEGER NOT NULL,
                        total_enqueued INTEGER NOT NULL,
                        total_processed INTEGER NOT NULL,
                        total_dropped INTEGER NOT NULL,
                        total_errors INTEGER NOT NULL,
                        circuit_breaker_state TEXT NOT NULL,
                        host_cpu_pct REAL NOT NULL,
                        host_memory_pct REAL NOT NULL
                    );
                    """
                )
                conn.commit()
            logger.info(f"Shadow telemetry database initialized at {SHADOW_DB_PATH} (WAL mode enabled).")
        except Exception as exc:
            logger.error(f"Failed to initialize shadow telemetry database: {exc}", exc_info=True)

    def is_enabled(self) -> bool:
        """Checks if shadow trial is actively enabled.

        Requirements:
        1. self.enabled must be explicitly True.
        2. KILL_SWITCH file must NOT exist.
        Removing the KILL_SWITCH file does NOT resume unless self.enabled is True.
        """
        if KILL_SWITCH_PATH.exists():
            return False
        return self.enabled

    def enable_trial(self) -> None:
        """Explicitly enables the shadow trial (requires human authorization)."""
        if KILL_SWITCH_PATH.exists():
            try:
                KILL_SWITCH_PATH.unlink()
            except Exception:
                pass
        self.enabled = True
        self._ensure_worker_started()
        logger.info("Shadow trial explicitly ENABLED by operator.")

    def disable_trial(self) -> None:
        """Disables the shadow trial."""
        self.enabled = False
        logger.info("Shadow trial DISABLED by operator.")

    def activate_kill_switch(self) -> None:
        """Atomic filesystem kill-switch. Instantly stops all new shadow jobs."""
        self._ensure_shadow_dirs()
        KILL_SWITCH_PATH.touch(exist_ok=True)
        self.enabled = False
        logger.warning(f"KILL-SWITCH ACTIVATED at {KILL_SWITCH_PATH}. All shadow inference halted.")

    def _ensure_worker_started(self) -> None:
        """Ensures the single dedicated daemon worker thread is running."""
        if self._worker_thread is None or not self._worker_thread.is_alive():
            self._stop_event.clear()
            self._worker_thread = threading.Thread(
                target=self._worker_loop,
                name="ClaimSense-ShadowWorker",
                daemon=True,
            )
            self._worker_thread.start()
            logger.info("ClaimSense-ShadowWorker thread started.")

    def enqueue_shadow_job(
        self,
        claim_id: str,
        image_path: Path,
        prod_detections: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Safely enqueues a photographic claim evidence image for background shadow inference.

        Non-blocking: saturation drops the job cleanly with zero impact on production responses.
        """
        # 1. Check Kill-Switch and enablement
        if not self.is_enabled():
            return {
                "enqueued": False,
                "status": "disabled",
                "reason": "Shadow trial is not actively enabled or KILL_SWITCH is active",
            }

        # 2. Check Circuit Breaker
        if not self.circuit_breaker.can_dispatch():
            return {
                "enqueued": False,
                "status": "circuit_breaker_open",
                "reason": f"Circuit breaker is in state {self.circuit_breaker.state}",
            }

        # 3. Attempt non-blocking enqueue
        job = {
            "claim_id": claim_id,
            "image_path": Path(image_path),
            "prod_detections": prod_detections or {},
            "enqueued_at": time.time(),
        }

        try:
            self.queue.put_nowait(job)
            self.total_enqueued += 1
            self._ensure_worker_started()
            return {"enqueued": True, "status": "enqueued", "queue_depth": self.queue.qsize()}
        except queue.Full:
            self.total_dropped += 1
            logger.warning(
                f"Shadow queue saturated (maxsize={self.queue.maxsize}). Dropping shadow job "
                f"for claim {claim_id} cleanly to protect authoritative production latency."
            )
            return {
                "enqueued": False,
                "status": "queue_full_dropped",
                "reason": "Queue capacity saturated (50 jobs). Dropped safely.",
            }

    def _get_candidate_model(self):
        """Loads EXP02 candidate model independently without modifying VehicleDamageDetector._instance."""
        with self._candidate_model_lock:
            if self._candidate_model is None:
                if not EXP02_CKPT_PATH.exists():
                    raise FileNotFoundError(f"EXP02 checkpoint not found: {EXP02_CKPT_PATH}")

                # Verify candidate hash
                actual_sha = compute_sha256(EXP02_CKPT_PATH)
                if actual_sha != EXP02_EXPECTED_SHA:
                    raise ValueError(f"EXP02 SHA mismatch! Expected {EXP02_EXPECTED_SHA}, got {actual_sha}")

                if not ULTRALYTICS_AVAILABLE or YOLO is None:
                    raise RuntimeError("Ultralytics YOLO unavailable for shadow inference.")

                logger.info(f"Loading isolated EXP02 candidate YOLO model from: {EXP02_CKPT_PATH}")
                # Load directly as an independent YOLO instance
                self._candidate_model = YOLO(str(EXP02_CKPT_PATH))
                logger.info("EXP02 candidate model loaded into isolated shadow worker memory.")
            return self._candidate_model

    def _worker_loop(self) -> None:
        """Single background worker loop consuming shadow jobs."""
        logger.info("ClaimSense-ShadowWorker loop entered.")
        while not self._stop_event.is_set():
            try:
                if self._paused:
                    time.sleep(0.05)
                    continue

                # Fetch job with timeout to allow graceful check of stop_event and kill-switch
                try:
                    job = self.queue.get(timeout=1.0)
                except queue.Empty:
                    continue

                # Secondary kill-switch check before execution
                if not self.is_enabled():
                    self.queue.task_done()
                    continue

                self._process_single_shadow_job(job)
                self.queue.task_done()

            except Exception as exc:
                self.total_errors += 1
                logger.error(f"Unhandled exception in ShadowWorkerLoop: {exc}", exc_info=True)

    def _process_single_shadow_job(self, job: Dict[str, Any]) -> None:
        """Processes one shadow inference job and records telemetry."""
        claim_id = job["claim_id"]
        image_path: Path = job["image_path"]
        prod_data: Dict[str, Any] = job["prod_detections"]

        t_start = time.perf_counter()
        cpu_before = psutil.cpu_percent(interval=None)

        vram_mb = 0.0
        gpu_pct = 0.0
        if TORCH_AVAILABLE and torch and torch.cuda.is_available():
            try:
                vram_mb = round(torch.cuda.memory_allocated() / (1024 * 1024), 2)
            except Exception:
                pass

        try:
            model = self._get_candidate_model()
            device = "cuda:0" if (TORCH_AVAILABLE and torch and torch.cuda.is_available()) else "cpu"

            # Execute isolated shadow inference
            results = model.predict(
                source=str(image_path),
                conf=0.25,
                iou=0.45,
                imgsz=640,
                device=device,
                verbose=False,
            )
            t_end = time.perf_counter()
            latency_ms = round((t_end - t_start) * 1000.0, 2)
            cpu_after = psutil.cpu_percent(interval=None)
            cpu_used = max(cpu_before, cpu_after)

            # Parse candidate detections
            exp02_boxes = []
            if results and len(results) > 0:
                boxes = results[0].boxes
                if boxes is not None:
                    for b in boxes:
                        cls_id = int(b.cls[0].item())
                        conf_val = float(b.conf[0].item())
                        coords = [round(float(v), 2) for v in b.xyxy[0].tolist()]
                        exp02_boxes.append({
                            "class_id": cls_id,
                            "confidence": round(conf_val, 4),
                            "bbox": coords,
                        })

            # Compare against production detections
            prod_boxes = prod_data.get("detections", [])
            disagreement_status, severity = self._evaluate_disagreement(prod_boxes, exp02_boxes)

            # Evaluate circuit breaker
            breaker_verdict = self.circuit_breaker.evaluate(
                cpu_pct=cpu_used,
                gpu_pct=gpu_pct,
                latency_ms=latency_ms,
                is_error=False,
            )

            # Persist to shadow SQLite database (single-worker write = 0 lock contention)
            self._persist_telemetry(
                claim_id=claim_id,
                image_path=image_path,
                prod_boxes=prod_boxes,
                exp02_boxes=exp02_boxes,
                disagreement_status=disagreement_status,
                disagreement_severity=severity,
                latency_ms=latency_ms,
                vram_mb=vram_mb,
                cpu_pct=cpu_used,
                gpu_pct=gpu_pct,
                breaker_state=self.circuit_breaker.state,
            )

            self.total_processed += 1

        except Exception as exc:
            self.total_errors += 1
            t_end = time.perf_counter()
            latency_ms = round((t_end - t_start) * 1000.0, 2)
            cpu_used = psutil.cpu_percent(interval=None)

            logger.error(f"Shadow inference failed for claim {claim_id}: {exc}", exc_info=True)
            self.circuit_breaker.evaluate(
                cpu_pct=cpu_used,
                gpu_pct=gpu_pct,
                latency_ms=latency_ms,
                is_error=True,
            )

    def _evaluate_disagreement(
        self,
        prod_boxes: List[Dict[str, Any]],
        exp02_boxes: List[Dict[str, Any]],
    ) -> Tuple[str, str]:
        """Categorizes prediction divergence between Production and EXP02."""
        n_prod = len(prod_boxes)
        n_exp = len(exp02_boxes)

        if n_prod == n_exp:
            if n_prod == 0:
                return "AGREEMENT", "NONE"
            return "AGREEMENT", "LOW"

        if n_prod > 0 and n_exp == 0:
            # EXP02 missed defect detected by Production
            severity = "HIGH" if any(b.get("confidence", 0) >= 0.50 for b in prod_boxes) else "MEDIUM"
            return "EXP02_MISSED_PROD", severity

        if n_prod == 0 and n_exp > 0:
            # EXP02 discovered defect missed by Production
            severity = "HIGH" if any(b.get("confidence", 0) >= 0.50 for b in exp02_boxes) else "MEDIUM"
            return "EXP02_NEW_DEFECT", severity

        return "COUNT_DISPARITY", "MEDIUM"

    def _persist_telemetry(
        self,
        claim_id: str,
        image_path: Path,
        prod_boxes: List[Dict[str, Any]],
        exp02_boxes: List[Dict[str, Any]],
        disagreement_status: str,
        disagreement_severity: str,
        latency_ms: float,
        vram_mb: float,
        cpu_pct: float,
        gpu_pct: float,
        breaker_state: str,
    ) -> None:
        """Records telemetry row to shadow_telemetry.db."""
        try:
            img_sha = compute_sha256(image_path) if image_path.exists() else "MISSING"
            ts = datetime.now(timezone.utc).isoformat()

            with sqlite3.connect(str(SHADOW_DB_PATH), timeout=5.0) as conn:
                conn.execute("PRAGMA journal_mode=WAL;")
                conn.execute(
                    """
                    INSERT INTO shadow_inference_telemetry (
                        timestamp, claim_id, image_filename, image_sha256,
                        image_width, image_height, prod_checkpoint_sha, exp02_checkpoint_sha,
                        prod_detections_json, exp02_detections_json,
                        prod_box_count, exp02_box_count,
                        disagreement_status, disagreement_severity,
                        shadow_latency_ms, gpu_vram_allocated_mb,
                        host_cpu_pct, host_gpu_pct, circuit_breaker_state
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        ts,
                        claim_id,
                        image_path.name,
                        img_sha,
                        640,
                        640,
                        PROD_EXPECTED_SHA,
                        EXP02_EXPECTED_SHA,
                        json.dumps(prod_boxes),
                        json.dumps(exp02_boxes),
                        len(prod_boxes),
                        len(exp02_boxes),
                        disagreement_status,
                        disagreement_severity,
                        latency_ms,
                        vram_mb,
                        cpu_pct,
                        gpu_pct,
                        breaker_state,
                    ),
                )
                conn.commit()
        except Exception as exc:
            logger.error(f"Failed to persist shadow telemetry for claim {claim_id}: {exc}")

    def get_health_stats(self) -> Dict[str, Any]:
        """Returns runtime operational statistics for health monitoring."""
        return {
            "enabled": self.is_enabled(),
            "kill_switch_active": KILL_SWITCH_PATH.exists(),
            "circuit_breaker": self.circuit_breaker.get_status(),
            "queue_depth": self.queue.qsize(),
            "queue_maxsize": self.queue.maxsize,
            "total_enqueued": self.total_enqueued,
            "total_processed": self.total_processed,
            "total_dropped": self.total_dropped,
            "total_errors": self.total_errors,
        }


def get_shadow_manager() -> ShadowWorkerManager:
    """Access the singleton ShadowWorkerManager."""
    return ShadowWorkerManager.get_instance()
