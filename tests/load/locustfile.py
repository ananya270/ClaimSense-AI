"""Locust load test suite for ClaimSense AI concurrent multi-user evaluation."""

import io
import itertools
import random
from locust import HttpUser, task, between, events
from typing import Optional, List

from tests.load.config import (
    TEST_USERS,
    PRESEEDED_POLICIES,
    MINIMAL_VALID_PDF_BYTES,
    MINIMAL_VALID_JPEG_BYTES,
    generate_claim_payload,
)

# Thread-safe user index distributor
_user_cycle = itertools.cycle(range(len(TEST_USERS)))
_submission_counter = itertools.count(1)

# Global pool of active claim IDs for reading
KNOWN_CLAIM_IDS: List[str] = []


class ClaimSenseUser(HttpUser):
    """Simulated authenticated insurance claimant / assessor interacting with ClaimSense AI."""

    # Realistic user think-time between actions (0.2s - 0.8s)
    wait_time = between(0.2, 0.8)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_index = next(_user_cycle)
        self.user_data = TEST_USERS[self.user_index]
        self.csrf_token: Optional[str] = None
        self.authenticated: bool = False
        self.personal_claims: List[str] = []

    def on_start(self):
        """Authenticates simulated user before initiating concurrent tasks."""
        self._authenticate()

    def _authenticate(self):
        """Fetches CSRF token and establishes authenticated Flask session."""
        # 1. Fetch CSRF token
        with self.client.get(
            "/api/auth/csrf-token",
            name="[Auth] 01_get_csrf_token",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    self.csrf_token = data.get("csrf_token")
                    resp.success()
                except Exception as e:
                    resp.failure(f"Failed to parse CSRF response: {e}")
            else:
                resp.failure(f"Failed to obtain CSRF token: status {resp.status_code}")

        # 2. Authenticate session
        headers = {}
        if self.csrf_token:
            headers["X-CSRFToken"] = self.csrf_token

        with self.client.post(
            "/api/auth/login",
            json={
                "identifier": self.user_data["username"],
                "password": self.user_data["password"],
            },
            headers=headers,
            name="[Auth] 02_login_session",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                self.authenticated = True
                try:
                    data = resp.json()
                    new_token = data.get("csrf_token")
                    if new_token:
                        self.csrf_token = new_token
                    resp.success()
                except Exception:
                    resp.success()
            else:
                resp.failure(f"Authentication failed for user {self.user_data['username']}: {resp.status_code}")

    @task(25)
    def task_list_claims(self):
        """User browses their existing submitted claims."""
        if not self.authenticated:
            return

        with self.client.get(
            "/api/my-claims",
            name="[Read] 01_list_my_claims",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    claims = data.get("claims", [])
                    for c in claims:
                        cid = c.get("claim_id")
                        if cid and cid not in self.personal_claims:
                            self.personal_claims.append(cid)
                        if cid and cid not in KNOWN_CLAIM_IDS:
                            KNOWN_CLAIM_IDS.append(cid)
                    resp.success()
                except Exception as e:
                    resp.failure(f"Error parsing my-claims: {e}")
            else:
                resp.failure(f"Failed to fetch my-claims: {resp.status_code}")

    @task(25)
    def task_policy_lookup(self):
        """User or assessor verifies policy validity and coverage window."""
        if not self.authenticated:
            return

        policy_number = random.choice(PRESEEDED_POLICIES)
        with self.client.get(
            f"/api/claims/policy/{policy_number}",
            name="[Read] 02_policy_lookup",
            catch_response=True,
        ) as resp:
            if resp.status_code in (200, 404):
                resp.success()
            else:
                resp.failure(f"Policy lookup error: {resp.status_code}")

    @task(20)
    def task_claim_details(self):
        """User inspects comprehensive claim details and evidence manifests."""
        if not self.authenticated:
            return

        target_claim_id = self._get_target_claim_id()
        if not target_claim_id:
            return

        with self.client.get(
            f"/api/claims/{target_claim_id}",
            name="[Read] 03_claim_details",
            catch_response=True,
        ) as resp:
            if resp.status_code in (200, 403):
                # 403 is valid if attempting to access another user's claim under RBAC
                resp.success()
            else:
                resp.failure(f"Claim details error: {resp.status_code}")

    @task(15)
    def task_verification_summary(self):
        """User or assessor views cross-source verification summary."""
        if not self.authenticated:
            return

        target_claim_id = self._get_target_claim_id()
        if not target_claim_id:
            return

        with self.client.get(
            f"/api/claims/{target_claim_id}/verification/summary",
            name="[Read] 04_verification_summary",
            catch_response=True,
        ) as resp:
            if resp.status_code in (200, 403, 404):
                resp.success()
            else:
                resp.failure(f"Verification summary error: {resp.status_code}")

    @task(10)
    def task_verification_findings(self):
        """User or assessor inspects granular comparison findings."""
        if not self.authenticated:
            return

        target_claim_id = self._get_target_claim_id()
        if not target_claim_id:
            return

        with self.client.get(
            f"/api/claims/{target_claim_id}/verification/findings",
            name="[Read] 05_verification_findings",
            catch_response=True,
        ) as resp:
            if resp.status_code in (200, 403, 404):
                resp.success()
            else:
                resp.failure(f"Verification findings error: {resp.status_code}")

    @task(5)
    def task_submit_claim(self):
        """Controlled claim ingestion: simulates user submitting a claim with 4 synthetic files."""
        if not self.authenticated:
            return

        seq = next(_submission_counter)
        payload = generate_claim_payload(self.user_index + 1, seq)

        headers = {}
        if self.csrf_token:
            headers["X-CSRFToken"] = self.csrf_token

        files = {
            "policy_document": ("policy.pdf", io.BytesIO(MINIMAL_VALID_PDF_BYTES), "application/pdf"),
            "claim_form": ("claim_form.pdf", io.BytesIO(MINIMAL_VALID_PDF_BYTES), "application/pdf"),
            "invoice_document": ("invoice.pdf", io.BytesIO(MINIMAL_VALID_PDF_BYTES), "application/pdf"),
            "vehicle_image": ("vehicle.jpg", io.BytesIO(MINIMAL_VALID_JPEG_BYTES), "image/jpeg"),
        }

        with self.client.post(
            "/api/claims",
            data=payload,
            files=files,
            headers=headers,
            name="[Write] 06_submit_claim",
            catch_response=True,
        ) as resp:
            if resp.status_code == 201:
                try:
                    data = resp.json()
                    cid = data.get("claim_id")
                    if cid:
                        self.personal_claims.append(cid)
                        if cid not in KNOWN_CLAIM_IDS:
                            KNOWN_CLAIM_IDS.append(cid)
                    resp.success()
                except Exception:
                    resp.success()
            else:
                resp.failure(f"Claim submission failed with status {resp.status_code}: {resp.text[:100]}")

    def _get_target_claim_id(self) -> Optional[str]:
        """Returns a claim ID to query, preferring user's own claims."""
        if self.personal_claims:
            return random.choice(self.personal_claims)
        if KNOWN_CLAIM_IDS:
            return random.choice(KNOWN_CLAIM_IDS)
        return None
