"""Health, readiness, liveness, and telemetry routes for ClaimSense AI (Production Hardened)."""
import os
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from flask import Blueprint, current_app, jsonify
from sqlalchemy import text

from backend.database.db import get_engine, get_db_session
from backend.database.models import Claim, User

health_bp = Blueprint("health", __name__)
_START_TIME = time.time()


@health_bp.route("/health", methods=["GET"])
def health_check():
    """Lightweight health-check endpoint returning system operational status."""
    return jsonify({
        "status": "healthy",
        "project": "ClaimSense AI",
        "description": "AI-Powered Insurance Claim Verification Decision-Support Prototype",
        "version": "1.0.0",
        "phase": "Phase 11 - Production Hardening & Operational Deployment",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": current_app.config.get("FLASK_ENV", "development"),
    }), 200


@health_bp.route("/health/live", methods=["GET"])
def liveness_probe():
    """Lightweight Kubernetes / Docker liveness probe confirming process is responsive."""
    return jsonify({
        "status": "alive",
        "uptime_seconds": round(time.time() - _START_TIME, 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }), 200


@health_bp.route("/health/ready", methods=["GET"])
def readiness_probe():
    """Comprehensive readiness probe verifying DB, storage, and ML asset availability."""
    checks = {
        "database": False,
        "storage_uploads": False,
        "ml_model_present": False,
    }
    details = {}

    # 1. Database Connectivity & Journal Mode
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            checks["database"] = (result == 1)

            # Query journal mode for SQLite
            if str(engine.url).startswith("sqlite"):
                mode = conn.execute(text("PRAGMA journal_mode")).scalar()
                details["sqlite_journal_mode"] = str(mode).upper()
    except Exception as exc:
        details["database_error"] = str(exc)

    # 2. Upload Storage Accessibility
    try:
        upload_folder = Path(current_app.config.get("UPLOAD_FOLDER", "uploads"))
        upload_folder.mkdir(parents=True, exist_ok=True)
        test_file = upload_folder / ".probe_check"
        test_file.write_text("ok", encoding="utf-8")
        test_file.unlink(missing_ok=True)
        checks["storage_uploads"] = True
    except Exception as exc:
        details["storage_error"] = str(exc)

    # 3. Model Weight Checkpoint
    model_path = Path(current_app.config.get("BASE_DIR", ".")) / "models" / "phase5" / "best.pt"
    checks["ml_model_present"] = model_path.exists()
    details["model_checkpoint"] = "verified" if model_path.exists() else "missing"

    all_ready = all(checks.values())
    status_code = 200 if all_ready else 503

    return jsonify({
        "status": "ready" if all_ready else "not_ready",
        "ready": all_ready,
        "checks": checks,
        "details": details,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }), status_code


@health_bp.route("/health/metrics", methods=["GET"])
def system_metrics():
    """Operational telemetry endpoint exposing uptime, entity counts, and system profile."""
    uptime = round(time.time() - _START_TIME, 2)
    counts = {"claims": 0, "users": 0}

    try:
        with get_db_session() as db:
            counts["claims"] = db.query(Claim).count()
            counts["users"] = db.query(User).count()
    except Exception:
        pass

    memory_mb = None
    try:
        import psutil
        process = psutil.Process()
        memory_mb = round(process.memory_info().rss / (1024 * 1024), 2)
    except Exception:
        pass

    return jsonify({
        "status": "ok",
        "uptime_seconds": uptime,
        "entity_counts": counts,
        "memory_rss_mb": memory_mb,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }), 200
