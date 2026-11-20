"""Isolated load-test server runner for ClaimSense AI Phase 10 Stage 2."""

import argparse
import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from datetime import datetime, timezone
from flask import Flask, jsonify
from sqlalchemy import text
from werkzeug.security import generate_password_hash

from backend.app import create_app
from backend.config import Config
from backend.database.db import init_database, get_db_session, get_engine
from backend.database.models import (
    User,
    Claim,
    Document,
    ClaimImage,
    ClaimVerificationRun,
    VerificationFinding,
)
from tests.load.config import (
    TEST_USERS,
    ASSESSOR_USER,
    DEFAULT_USER_PASSWORD,
    PRESEEDED_POLICIES,
    LOAD_TEST_PORT,
)


def seed_test_database(db_path: Path, enable_wal: bool = False):
    """Initializes schema and pre-populates test users and claims in isolated test DB."""
    # Ensure parent directory
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db_uri = f"sqlite:///{db_path.as_posix()}"
    engine = init_database(db_uri)

    # Configure journal mode and busy timeout
    with engine.begin() as conn:
        if enable_wal:
            conn.execute(text("PRAGMA journal_mode=WAL;"))
        else:
            conn.execute(text("PRAGMA journal_mode=DELETE;"))
        conn.execute(text("PRAGMA busy_timeout=5000;"))

    # Seed users
    with get_db_session() as db:
        # Check if users already exist
        existing_count = db.query(User).count()
        if existing_count == 0:
            # Pre-compute password hash once for all load test users for rapid initialization
            shared_hash = generate_password_hash(DEFAULT_USER_PASSWORD)
            for u in TEST_USERS:
                user = User(
                    full_name=u["full_name"],
                    username=u["username"],
                    email=u["email"],
                    password_hash=shared_hash,
                    role=u["role"],
                    is_active=True,
                )
                db.add(user)

            # Seed assessor user
            assessor = User(
                full_name=ASSESSOR_USER["full_name"],
                username=ASSESSOR_USER["username"],
                email=ASSESSOR_USER["email"],
                password_hash=shared_hash,
                role=ASSESSOR_USER["role"],
                is_active=True,
            )
            db.add(assessor)
            db.flush()

            # Seed 10 pre-existing claims for read workflows
            now = datetime.now(timezone.utc)
            for i in range(1, 11):
                cid = f"CLM-20261120-L{i:03d}"
                claim = Claim(
                    claim_id=cid,
                    user_id=1 + (i % len(TEST_USERS)),
                    claimant_name=TEST_USERS[(i - 1) % len(TEST_USERS)]["full_name"],
                    policy_number=PRESEEDED_POLICIES[(i - 1) % len(PRESEEDED_POLICIES)],
                    vehicle_number=f"DL-01-AB-{2000 + i}",
                    accident_date="2026-11-10",
                    incident_location="Sector 62, Noida",
                    claim_description=f"Pre-seeded test collision claim {i} with front left dent.",
                    status="SUBMITTED",
                    created_at=now,
                    updated_at=now,
                )
                db.add(claim)
                db.flush()

                # Add sample verification run
                v_run = ClaimVerificationRun(
                    run_id=f"RUN-{cid}-001",
                    claim_id=cid,
                    engine_version="1.0.0",
                    overall_status="REVIEW_REQUIRED" if i % 2 == 0 else "CONSISTENT",
                    consistency_score=85.0 if i % 2 == 0 else 95.0,
                    total_comparisons=5,
                    matched_comparisons=4,
                    mismatched_comparisons=1 if i % 2 == 0 else 0,
                    missing_evidence_count=0,
                    inconclusive_count=0,
                    high_severity_count=1 if i % 2 == 0 else 0,
                    critical_severity_count=0,
                    summary="Automated load test verification run.",
                    recommendations="Review uncorroborated damage.",
                    processing_status="completed",
                    created_at=now,
                    updated_at=now,
                )
                db.add(v_run)
                db.flush()

                finding = VerificationFinding(
                    run_id=v_run.id,
                    claim_id=cid,
                    comparison_id="CMP-NARRATIVE-VS-VISION-01",
                    source_a="Claimant Narrative",
                    source_b="Computer Vision YOLOv8",
                    field_name="damage_front_bumper",
                    original_value_a="Front bumper dent",
                    original_value_b="Dent (confidence 0.78)",
                    comparison_status="MATCH",
                    severity="LOW",
                    confidence=0.90,
                    explanation="Visual damage matches narrative description.",
                    created_at=now,
                )
                db.add(finding)


def make_load_test_app(isolated_dir: Path, enable_wal: bool = False) -> Flask:
    """Creates a configured Flask app instance isolated in temporary directory."""
    db_path = isolated_dir / "test_load.db"
    upload_dir = isolated_dir / "uploads"
    reports_dir = isolated_dir / "reports"

    upload_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    class LoadTestConfig(Config):
        TESTING = False
        FLASK_ENV = "testing"
        DEBUG = False
        PORT = LOAD_TEST_PORT
        HOST = "127.0.0.1"
        SECRET_KEY = "load-test-secret-key-phase10-stage2-verification-key"
        UPLOAD_FOLDER = upload_dir
        REPORTS_FOLDER = reports_dir
        DATABASE_PATH = db_path
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path.as_posix()}"
        RATELIMIT_ENABLED = False  # Disabled for load testing to evaluate raw application concurrency
        WTF_CSRF_ENABLED = True    # Keep CSRF enabled to evaluate authentic token lifecycle
        WTF_CSRF_CHECK_DEFAULT = True

    # Seed DB first
    seed_test_database(db_path, enable_wal=enable_wal)

    app = create_app(LoadTestConfig)

    # Health diagnostic for Locust warmup
    @app.route("/api/load-test/ping", methods=["GET"])
    def load_ping():
        with get_engine().connect() as conn:
            mode = conn.execute(text("PRAGMA journal_mode;")).scalar()
            timeout = conn.execute(text("PRAGMA busy_timeout;")).scalar()
        return jsonify({
            "status": "ready",
            "journal_mode": mode,
            "busy_timeout": timeout,
            "database_path": str(db_path),
        }), 200

    return app


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run isolated ClaimSense AI load test server.")
    parser.add_argument("--dir", type=str, required=True, help="Isolated working directory for DB and uploads.")
    parser.add_argument("--wal", action="store_true", help="Enable SQLite WAL mode instead of DELETE mode.")
    parser.add_argument("--port", type=int, default=LOAD_TEST_PORT, help="Port to listen on.")
    args = parser.parse_args()

    isolated_path = Path(args.dir).resolve()
    app = make_load_test_app(isolated_path, enable_wal=args.wal)
    print(f"[LOAD_SERVER_READY] Listening on http://127.0.0.1:{args.port} (WAL={args.wal})", flush=True)
    app.run(host="127.0.0.1", port=args.port, threaded=True, debug=False)
