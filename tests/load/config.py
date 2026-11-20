"""Load testing configuration, user pools, and synthetic fixtures for ClaimSense AI."""

import os
from pathlib import Path
from typing import Dict, Any, List

# Target Server Configuration
LOAD_TEST_HOST = os.getenv("LOAD_TEST_HOST", "http://127.0.0.1:5002")
LOAD_TEST_PORT = int(os.getenv("LOAD_TEST_PORT", 5002))

# Load Profiles Configuration
PROFILES = {
    "10_users": {
        "users": 10,
        "spawn_rate": 2.0,
        "run_time": "30s",
        "description": "Controlled baseline concurrency with 10 simulated users",
    },
    "25_users": {
        "users": 25,
        "spawn_rate": 5.0,
        "run_time": "45s",
        "description": "Moderate concurrent workload with 25 simulated users",
    },
    "50_users": {
        "users": 50,
        "spawn_rate": 10.0,
        "run_time": "60s",
        "description": "Peak stress workload with 50 simulated users",
    },
}

# SLA Acceptance Thresholds
SLA_TARGETS = {
    "max_mean_latency_ms": 500.0,
    "max_p95_latency_ms": 1000.0,
    "max_p99_latency_ms": 2000.0,
    "max_error_rate_pct": 0.1,  # < 0.1% failures
    "allow_sqlite_lock_errors": False,
    "zero_data_corruption": True,
}

# Pre-seeded User Accounts for Load Testing
NUM_TEST_USERS = 50
DEFAULT_USER_PASSWORD = "LoadTestPassword123!"

TEST_USERS: List[Dict[str, str]] = [
    {
        "full_name": f"Load Test User {i:02d}",
        "username": f"load_user_{i:02d}",
        "email": f"load_user_{i:02d}@claimsense-test.local",
        "password": DEFAULT_USER_PASSWORD,
        "role": "user",
    }
    for i in range(1, NUM_TEST_USERS + 1)
]

# Additional Assessor Account for Administrative Queries
ASSESSOR_USER = {
    "full_name": "Senior Assessor Load",
    "username": "load_assessor",
    "email": "assessor_load@claimsense-test.local",
    "password": DEFAULT_USER_PASSWORD,
    "role": "assessor",
}

# Pre-seeded Policies
PRESEEDED_POLICIES = [
    "POL-2026-8812",
    "POL-LOAD-1001",
    "POL-LOAD-1002",
    "POL-LOAD-1003",
    "POL-LOAD-1004",
    "POL-LOAD-1005",
]

# Synthetic File Fixtures (Deterministic Binary Signatures)
MINIMAL_VALID_PDF_BYTES = (
    b"%PDF-1.4\n"
    b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
    b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n"
    b"4 0 obj\n<< /Length 44 >>\nstream\nBT /F1 12 Tf 72 712 Td (Load Test Document) ET\nendstream\nendobj\n"
    b"xref\n0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000060 00000 n \n0000000117 00000 n \n0000000209 00000 n \n"
    b"trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n304\n%%EOF\n"
)

# 1x1 Minimal Valid JPEG Bytes
MINIMAL_VALID_JPEG_BYTES = (
    b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00"
    b"\xFF\xDB\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t"
    b"\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a"
    b"\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342"
    b"\xFF\xC0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00"
    b"\xFF\xC4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b"
    b"\xFF\xDA\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xFF\xD9"
)

# Template Form Data for Controlled Claim Ingestion
def generate_claim_payload(user_index: int, sequence_id: int) -> Dict[str, Any]:
    """Generates synthetic form metadata for a controlled claim submission."""
    user = TEST_USERS[(user_index - 1) % len(TEST_USERS)]
    policy = PRESEEDED_POLICIES[sequence_id % len(PRESEEDED_POLICIES)]
    return {
        "claimant_name": user["full_name"],
        "policy_number": policy,
        "vehicle_number": f"DL-01-AB-{1000 + (sequence_id % 9000)}",
        "accident_date": "2026-11-15",
        "incident_location": "Connaught Place Outer Ring, New Delhi",
        "claim_description": (
            f"Load test vehicle collision incident sequence {sequence_id}. "
            "Front bumper impact with minor dent and scratch damage at moderate speed."
        ),
    }
