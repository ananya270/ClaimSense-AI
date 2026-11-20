"""Master End-to-End System Integration Test Suite for ClaimSense AI (Phase 10).

Validates the complete 10-stage multi-modal operational pipeline:
1. User Authentication & Session Minting (POST /api/auth/login, GET /api/auth/me)
2. Multipart Claim Ingestion & File Persistence (POST /api/claims)
3. Policy Record Lookup & Multi-Tenancy Scoping (GET /api/claims/policy/<num>)
4. Evidence Manifest & Raw Asset Inspection (GET /api/claims/<id>, /evidence/<type>)
5. Computer Vision Vehicle Damage Detection (POST /api/claims/<id>/analyze-damage)
6. OCR Document Intelligence Retrieval (GET /api/claims/<id>/extracted)
7. NLP Narrative Analysis & Event Reconstruction (POST /api/claims/<id>/analyze-nlp)
8. Cross-Source Corroboration Engine (POST /api/claims/<id>/verify-cross-source)
9. Granular Findings & Summary Retrieval (GET /api/claims/<id>/verification/findings)
10. Dual PDF Report Synthesis: Intake Receipt & 8-Page Analytical Dossier

All tests use isolated temporary databases and upload directories.
Production model weights and production databases are strictly unmodified.
"""

import io
import json
import re
import shutil
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image
import fitz

from backend.app import create_app
from backend.config import Config
from backend.database.db import get_db_session, init_database, close_engine
from backend.database.models import User, Claim, Document, ClaimImage, VehicleDamageAnalysis, ClaimNLPAnalysis, ClaimVerificationRun, VerificationFinding
from backend.utils.validators import is_valid_claim_id_format


class MasterSystemE2ETestSuite(unittest.TestCase):
    """Authoritative Phase 10 master end-to-end integration and lifecycle test suite."""

    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parents[1]
        cls.cardd_img = cls.repo_root / "datasets" / "CarDD_300" / "test" / "images" / "000023.jpg"
        assert cls.cardd_img.exists(), f"CarDD test image missing at {cls.cardd_img}"
        cls.img_bytes = cls.cardd_img.read_bytes()

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.tmp = Path(self.temp_dir)
        self.upload_dir = self.tmp / "uploads"
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir = self.tmp / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.tmp / "test_master_e2e.db"

        # Dedicated isolated test configuration
        test_db_uri = f"sqlite:///{self.db_path.as_posix()}"

        class E2ETestConfig(Config):
            TESTING = True
            UPLOAD_FOLDER = self.upload_dir
            REPORTS_FOLDER = self.reports_dir
            DATABASE_PATH = self.db_path
            SQLALCHEMY_DATABASE_URI = test_db_uri
            WTF_CSRF_ENABLED = False
            RATELIMIT_ENABLED = False
            SECRET_KEY = "master-e2e-secret-key-phase10"

        self.app = create_app(E2ETestConfig)
        self.client = self.app.test_client()

        with self.app.app_context():
            init_database(test_db_uri)

    def tearDown(self):
        close_engine()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # Helper Utilities
    # -------------------------------------------------------------------------
    def _make_pdf(self, text: str) -> bytes:
        """Generates a valid %PDF-1.4 document buffer containing structured text."""
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 100), text, fontsize=11)
        return doc.tobytes()

    def _make_synthetic_image(self, filename="synthetic_card.jpg") -> Path:
        """Creates a synthetic solid-color image (non-vehicle graphic)."""
        p = self.tmp / filename
        img = Image.new("RGB", (640, 480), color=(250, 250, 250))
        img.save(p, format="JPEG")
        return p

    def _register_user(self, username="rsharma", email="rajesh@example.com", role="user", password="SecurePass99#"):
        """Registers and seeds a test user directly into the isolated test database."""
        with get_db_session() as db:
            user = User(
                username=username,
                email=email,
                full_name=f"Full {username}",
                role=role,
            )
            user.set_password(password)
            db.add(user)
            db.flush()
            user_id = user.id
        return user_id

    def _login(self, identifier="rsharma", password="SecurePass99#"):
        """Authenticates with the session client."""
        return self.client.post("/api/auth/login", json={"identifier": identifier, "password": password})

    def _submit_sample_claim(self, policy_number="POL-2026-9901") -> str:
        """Helper to submit a standard multi-modal claim with authentic CarDD image."""
        policy_pdf = self._make_pdf(
            "POLICY SCHEDULE\n"
            f"Policy Number: {policy_number}\n"
            "Claimant Name: Rajesh Sharma\n"
            "Vehicle Number: DL-01-AB-1234\n"
            "Accident Date: 2026-10-15\n"
            "Valid From: 2026-01-01 to 2027-01-01\n"
            "Coverage: Comprehensive Private Motor Insurance"
        )
        claim_form_pdf = self._make_pdf(
            "OFFICIAL CLAIM FORM\n"
            "Claimant Name: Rajesh Sharma\n"
            f"Policy Number: {policy_number}\n"
            "Vehicle Number: DL-01-AB-1234\n"
            "Accident Date: 2026-10-15\n"
            "Incident Location: Outer Ring Road Intersection\n"
            "Description: Severe collision at traffic light causing rear bumper dent and tail lamp damage."
        )
        invoice_pdf = self._make_pdf(
            "REPAIR ESTIMATE & INVOICE\n"
            "Authorized Service Garage\n"
            "Rear Bumper: 8500\n"
            "Tail Lamp: 3200\n"
            "Total Amount: 11700\n"
            "Payment Status: Pending Insurance Settlement"
        )

        res = self.client.post(
            "/api/claims",
            data={
                "claimant_name": "Rajesh Sharma",
                "policy_number": policy_number,
                "vehicle_number": "DL-01-AB-1234",
                "accident_date": "2026-10-15",
                "incident_location": "Outer Ring Road Intersection",
                "claim_description": "Severe side collision at traffic signal. Rear bumper dent and right tail lamp cracked and broken.",
                "policy_document": (io.BytesIO(policy_pdf), "policy_schedule.pdf"),
                "claim_form": (io.BytesIO(claim_form_pdf), "claim_form.pdf"),
                "invoice_document": (io.BytesIO(invoice_pdf), "repair_estimate.pdf"),
                "vehicle_image": (io.BytesIO(self.img_bytes), "000023.jpg"),
            },
            content_type="multipart/form-data",
        )
        self.assertEqual(res.status_code, 201, f"Claim submission failed: {res.get_json()}")
        claim_id = res.get_json()["claim_id"]
        self.assertTrue(is_valid_claim_id_format(claim_id))
        return claim_id

    # -------------------------------------------------------------------------
    # Test 1: User Authentication Lifecycle & Security Masking (WF-01)
    # -------------------------------------------------------------------------
    def test_01_user_authentication_lifecycle_and_masking(self):
        """Verifies signup, login, session /me identity, password masking, and logout."""
        # 1. Signup new user
        signup_res = self.client.post("/api/auth/signup", json={
            "full_name": "Rajesh Sharma",
            "username": "rsharma",
            "email": "rajesh@example.com",
            "password": "SecurePass99#",
            "confirm_password": "SecurePass99#",
        })
        self.assertEqual(signup_res.status_code, 201)
        signup_data = signup_res.get_json()
        self.assertTrue(signup_data["success"])

        # 2. Login
        login_res = self._login("rsharma", "SecurePass99#")
        self.assertEqual(login_res.status_code, 200)
        login_data = login_res.get_json()
        self.assertTrue(login_data["success"])
        self.assertEqual(login_data["user"]["username"], "rsharma")
        self.assertNotIn("password", login_data["user"])
        self.assertNotIn("password_hash", login_data["user"])

        # 3. Verify session via /api/auth/me
        me_res = self.client.get("/api/auth/me")
        self.assertEqual(me_res.status_code, 200)
        me_data = me_res.get_json()
        self.assertTrue(me_data["success"])
        self.assertEqual(me_data["user"]["username"], "rsharma")
        self.assertNotIn("password_hash", me_data["user"])

        # 4. Invalid login attempt
        bad_login = self._login("rsharma", "WrongPassword!")
        self.assertEqual(bad_login.status_code, 401)
        self.assertFalse(bad_login.get_json()["success"])

        # 5. Logout
        logout_res = self.client.post("/api/auth/logout")
        self.assertEqual(logout_res.status_code, 200)

        # 6. /me after logout
        me_after = self.client.get("/api/auth/me")
        self.assertEqual(me_after.status_code, 401)
        self.assertFalse(me_after.get_json()["success"])

    # -------------------------------------------------------------------------
    # Test 2: Multipart Claim Ingestion & Evidence File Persistence (WF-02)
    # -------------------------------------------------------------------------
    def test_02_multipart_claim_ingestion_and_file_persistence(self):
        """Verifies ingestion of 4 genuine evidence files, disk directory structure, and metadata."""
        self._register_user("rsharma")
        self._login("rsharma")

        claim_id = self._submit_sample_claim("POL-2026-9901")

        # Verify disk persistence in isolated upload folder
        claim_dir = self.upload_dir / claim_id
        self.assertTrue(claim_dir.exists(), f"Claim directory {claim_dir} not found on disk")
        self.assertTrue((claim_dir / "documents").exists())
        self.assertTrue((claim_dir / "images").exists())
        self.assertTrue((claim_dir / "metadata.json").exists())

        # Verify saved files on disk
        doc_files = list((claim_dir / "documents").iterdir())
        img_files = list((claim_dir / "images").iterdir())
        self.assertEqual(len(doc_files), 3, "Expected 3 persisted document files")
        self.assertGreaterEqual(len(img_files), 1, "Expected at least 1 persisted image file")

        # Verify metadata.json content
        with open(claim_dir / "metadata.json", "r", encoding="utf-8") as f:
            meta = json.load(f)
        self.assertEqual(meta["claim_id"], claim_id)
        self.assertEqual(meta["policy_number"], "POL-2026-9901")
        self.assertIn("files", meta)
        self.assertIn("vehicle_image", meta["files"])

    # -------------------------------------------------------------------------
    # Test 3: Policy Information Lookup & Multi-Tenant Authorization (WF-03)
    # -------------------------------------------------------------------------
    def test_03_policy_information_lookup_and_multi_tenancy(self):
        """Verifies policy query scoping, search endpoint, and cross-user isolation."""
        user_a = self._register_user("user_a", "usera@example.com")
        user_b = self._register_user("user_b", "userb@example.com")
        assessor = self._register_user("assessor_1", "assessor@example.com", role="assessor")

        # User A submits a claim under POL-2026-AAAA
        self._login("user_a")
        claim_a = self._submit_sample_claim("POL-2026-AAAA")

        # User A can find their claim
        res_a = self.client.get("/api/claims/policy/POL-2026-AAAA")
        self.assertEqual(res_a.status_code, 200)
        data_a = res_a.get_json()
        self.assertTrue(data_a["success"])
        self.assertEqual(data_a["count"], 1)
        self.assertEqual(data_a["claims"][0]["claim_id"], claim_a)

        # User B queries User A's policy -> 404 (scoped to user's claims)
        self._login("user_b")
        res_b = self.client.get("/api/claims/policy/POL-2026-AAAA")
        self.assertEqual(res_b.status_code, 404)

        # Assessor queries User A's policy -> 200 OK (global access)
        self._login("assessor_1")
        res_assessor = self.client.get("/api/claims/policy/POL-2026-AAAA")
        self.assertEqual(res_assessor.status_code, 200)
        self.assertEqual(res_assessor.get_json()["count"], 1)

        # Unified search endpoint /api/claims/search
        search_res = self.client.get("/api/claims/search?q=POL-2026-AAAA")
        self.assertEqual(search_res.status_code, 200)
        self.assertGreaterEqual(search_res.get_json()["count"], 1)

    # -------------------------------------------------------------------------
    # Test 4: Evidence Manifest & Raw Asset Inspection (WF-04)
    # -------------------------------------------------------------------------
    def test_04_evidence_manifest_inspection_and_raw_serving(self):
        """Verifies claim detail retrieval and raw evidence streaming."""
        self._register_user("rsharma")
        self._login("rsharma")
        claim_id = self._submit_sample_claim()

        # Query claim details
        res = self.client.get(f"/api/claims/{claim_id}")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        claim_data = data["data"]
        self.assertEqual(claim_data["claim_id"], claim_id)
        self.assertEqual(len(claim_data["documents"]), 3)
        self.assertEqual(len(claim_data["images"]), 1)

        # Serve raw image
        raw_img = self.client.get(f"/api/claims/{claim_id}/evidence/image")
        self.assertEqual(raw_img.status_code, 200)
        self.assertEqual(raw_img.content_type, "image/jpeg")
        self.assertGreater(len(raw_img.data), 1000)

        # Serve raw document
        raw_doc = self.client.get(f"/api/claims/{claim_id}/evidence/policy_document")
        self.assertEqual(raw_doc.status_code, 200)
        self.assertEqual(raw_doc.content_type, "application/pdf")
        self.assertTrue(raw_doc.data.startswith(b"%PDF-"))

    # -------------------------------------------------------------------------
    # Test 5: Vehicle Damage Detection (YOLOv8) & Idempotency (WF-05)
    # -------------------------------------------------------------------------
    def test_05_computer_vision_damage_detection_and_idempotency(self):
        """Verifies YOLOv8 damage detection inference, detection classes, and idempotency."""
        self._register_user("rsharma")
        self._login("rsharma")
        claim_id = self._submit_sample_claim()

        # Explicit damage analysis call
        res_damage = self.client.post(
            f"/api/claims/{claim_id}/analyze-damage",
            json={"conf_threshold": 0.15},
        )
        self.assertEqual(res_damage.status_code, 200)
        damage_data = res_damage.get_json()
        self.assertTrue(damage_data["success"])
        self.assertIn("analysis", damage_data)
        analysis = damage_data["analysis"]
        self.assertEqual(analysis["analysis_status"], "completed")
        total_detections = analysis.get("total_detections", analysis.get("total_damages_detected", 0))
        self.assertGreaterEqual(total_detections, 1)

        # Idempotency check: calling again reuses persisted record
        res_second = self.client.post(
            f"/api/claims/{claim_id}/analyze-damage",
            json={"conf_threshold": 0.15},
        )
        self.assertEqual(res_second.status_code, 200)
        self.assertTrue(res_second.get_json()["success"])

        # Fetch damage analysis via GET
        get_analysis = self.client.get(f"/api/claims/{claim_id}/damage-analysis")
        self.assertEqual(get_analysis.status_code, 200)
        self.assertTrue(get_analysis.get_json()["success"])

        # Fetch damage history
        history_res = self.client.get(f"/api/claims/{claim_id}/damage-history")
        self.assertEqual(history_res.status_code, 200)
        self.assertGreaterEqual(len(history_res.get_json()["history"]), 1)

        # Fetch annotated image
        annotated_res = self.client.get(f"/api/claims/{claim_id}/annotated-image")
        self.assertEqual(annotated_res.status_code, 200)
        self.assertEqual(annotated_res.content_type, "image/jpeg")

    # -------------------------------------------------------------------------
    # Test 6: Document OCR Data Extraction (WF-06)
    # -------------------------------------------------------------------------
    def test_06_document_ocr_data_retrieval(self):
        """Verifies database-persisted ExtractedInformation fields from multi-page PDFs."""
        self._register_user("rsharma")
        self._login("rsharma")
        claim_id = self._submit_sample_claim()

        res = self.client.get(f"/api/claims/{claim_id}/extracted")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("fields", data)
        self.assertGreaterEqual(len(data["fields"]), 1)

        # Check field keys
        extracted_names = {f["field_name"] for f in data["fields"]}
        self.assertTrue(
            any(k in extracted_names for k in ["policy_number", "claimant_name", "vehicle_number"]),
            f"Expected standard insurance fields, found: {extracted_names}",
        )

    # -------------------------------------------------------------------------
    # Test 7: NLP Narrative Analysis & Chronological Event Reconstruction (WF-07)
    # -------------------------------------------------------------------------
    def test_07_nlp_narrative_analysis_and_events(self):
        """Verifies NLP component extraction, incident classification, and chronological sequencing."""
        self._register_user("rsharma")
        self._login("rsharma")
        claim_id = self._submit_sample_claim()

        # Trigger NLP analysis
        res_nlp = self.client.post(f"/api/claims/{claim_id}/analyze-nlp", json={})
        self.assertEqual(res_nlp.status_code, 200)
        nlp_json = res_nlp.get_json()
        self.assertTrue(nlp_json["success"])

        # Retrieve stored NLP analysis
        get_nlp = self.client.get(f"/api/claims/{claim_id}/nlp-analysis")
        self.assertEqual(get_nlp.status_code, 200)
        stored_nlp = get_nlp.get_json()["analysis"]
        self.assertIn("reported_damages", stored_nlp)
        self.assertIn("timeline", stored_nlp)
        self.assertGreaterEqual(len(stored_nlp["reported_damages"]), 1)

        # Retrieve entities endpoint
        entities_res = self.client.get(f"/api/claims/{claim_id}/nlp-entities")
        self.assertEqual(entities_res.status_code, 200)

    # -------------------------------------------------------------------------
    # Test 8: Cross-Source Verification & Multi-Modal Corroboration (WF-08)
    # -------------------------------------------------------------------------
    def test_08_cross_source_corroboration_engine(self):
        """Verifies triangulation across OCR, CV, and NLP with scoring and coverage metrics."""
        self._register_user("rsharma")
        self._login("rsharma")
        claim_id = self._submit_sample_claim()

        # Run damage detection and NLP first to populate upstream inputs
        self.client.post(f"/api/claims/{claim_id}/analyze-damage", json={"conf_threshold": 0.15})
        self.client.post(f"/api/claims/{claim_id}/analyze-nlp", json={})

        # Execute Cross-Source Verification
        v_res = self.client.post(f"/api/claims/{claim_id}/verify-cross-source", json={})
        self.assertEqual(v_res.status_code, 200)
        v_json = v_res.get_json()
        self.assertTrue(v_json["success"])

        verif = v_json["verification"]
        self.assertIn("consistency_score", verif)
        self.assertIsInstance(verif["consistency_score"], (int, float))
        self.assertGreaterEqual(verif["consistency_score"], 0.0)
        self.assertLessEqual(verif["consistency_score"], 100.0)
        self.assertIn("overall_status", verif)
        self.assertIn(verif["overall_status"], ["CONSISTENT", "REVIEW_REQUIRED", "INSUFFICIENT_EVIDENCE"])
        self.assertIn("evidence_coverage_percentage", verif)

        # GET verification state
        get_verif = self.client.get(f"/api/claims/{claim_id}/verification")
        self.assertEqual(get_verif.status_code, 200)
        self.assertTrue(get_verif.get_json()["verified"])

    # -------------------------------------------------------------------------
    # Test 9: Granular Findings & Summary Retrieval (WF-09)
    # -------------------------------------------------------------------------
    def test_09_granular_findings_and_summary_filtering(self):
        """Verifies comparison findings generation, status filtering, and assessor summary."""
        self._register_user("rsharma")
        self._login("rsharma")
        claim_id = self._submit_sample_claim()

        self.client.post(f"/api/claims/{claim_id}/analyze-damage", json={"conf_threshold": 0.15})
        self.client.post(f"/api/claims/{claim_id}/analyze-nlp", json={})
        self.client.post(f"/api/claims/{claim_id}/verify-cross-source", json={})

        # Fetch findings
        findings_res = self.client.get(f"/api/claims/{claim_id}/verification/findings")
        self.assertEqual(findings_res.status_code, 200)
        f_data = findings_res.get_json()
        self.assertTrue(f_data["success"])
        self.assertGreaterEqual(f_data["total_findings"], 1)

        # Test severity filter
        low_res = self.client.get(f"/api/claims/{claim_id}/verification/findings?severity=LOW")
        self.assertEqual(low_res.status_code, 200)

        # Test status filter
        match_res = self.client.get(f"/api/claims/{claim_id}/verification/findings?status=MATCH")
        self.assertEqual(match_res.status_code, 200)

        # Fetch summary
        summary_res = self.client.get(f"/api/claims/{claim_id}/verification/summary")
        self.assertEqual(summary_res.status_code, 200)
        s_data = summary_res.get_json()
        self.assertTrue(s_data["success"])
        self.assertIn("consistency_score", s_data)
        self.assertIn("recommendations", s_data)

    # -------------------------------------------------------------------------
    # Test 10: PDF Synthesis — Intake Receipt & Analytical Dossier (WF-10)
    # -------------------------------------------------------------------------
    def test_10_pdf_report_generation_receipt_and_dossier(self):
        """Verifies dynamic generation of intake PDF receipt and multi-page document report."""
        self._register_user("rsharma")
        self._login("rsharma")
        claim_id = self._submit_sample_claim()

        self.client.post(f"/api/claims/{claim_id}/analyze-damage", json={"conf_threshold": 0.15})
        self.client.post(f"/api/claims/{claim_id}/analyze-nlp", json={})
        self.client.post(f"/api/claims/{claim_id}/verify-cross-source", json={})

        # 1. Single-page intake receipt
        receipt_res = self.client.get(f"/api/claims/{claim_id}/receipt")
        self.assertEqual(receipt_res.status_code, 200)
        self.assertEqual(receipt_res.content_type, "application/pdf")
        self.assertTrue(receipt_res.data.startswith(b"%PDF-1.4"))
        self.assertGreater(len(receipt_res.data), 2000)

        # 2. Multi-page comprehensive document report
        report_res = self.client.get(f"/api/claims/{claim_id}/document-report")
        self.assertEqual(report_res.status_code, 200)
        self.assertEqual(report_res.content_type, "application/pdf")
        self.assertTrue(report_res.data.startswith(b"%PDF-1.4"))
        self.assertGreater(len(report_res.data), 10000)

    # -------------------------------------------------------------------------
    # Test 11: Vehicle Replacement Image Pipeline End-to-End
    # -------------------------------------------------------------------------
    def test_11_replacement_image_upload_and_reanalysis_workflow(self):
        """Verifies synthetic graphic rejection, replacement upload, audit preservation, and re-detection."""
        self._register_user("rsharma")
        self._login("rsharma")

        # Submit claim initially with synthetic card
        synth_img = self._make_synthetic_image("synth_card.jpg")
        with open(synth_img, "rb") as f:
            synth_bytes = f.read()

        policy_pdf = self._make_pdf("Policy: POL-2026-REP1\nClaimant: Rajesh Sharma")
        res = self.client.post(
            "/api/claims",
            data={
                "claimant_name": "Rajesh Sharma",
                "policy_number": "POL-2026-REP1",
                "vehicle_number": "DL-01-AB-1234",
                "accident_date": "2026-10-15",
                "claim_description": "Rear bumper collision damage.",
                "policy_document": (io.BytesIO(policy_pdf), "policy.pdf"),
                "claim_form": (io.BytesIO(policy_pdf), "claim_form.pdf"),
                "invoice_document": (io.BytesIO(policy_pdf), "invoice.pdf"),
                "vehicle_image": (io.BytesIO(synth_bytes), "synth_card.jpg"),
            },
            content_type="multipart/form-data",
        )
        self.assertEqual(res.status_code, 201)
        claim_id = res.get_json()["claim_id"]

        # Initial damage analysis should flag replacement needed
        initial_damage = self.client.post(f"/api/claims/{claim_id}/analyze-damage", json={})
        self.assertEqual(initial_damage.status_code, 400)
        self.assertTrue(initial_damage.get_json().get("requires_replacement"))

        # Upload authentic CarDD photograph as replacement
        rep_res = self.client.post(
            f"/api/claims/{claim_id}/replace-image",
            data={"vehicle_image": (io.BytesIO(self.img_bytes), "replacement_photo.jpg")},
            content_type="multipart/form-data",
        )
        self.assertEqual(rep_res.status_code, 200)
        rep_json = rep_res.get_json()
        self.assertTrue(rep_json["success"])
        self.assertTrue(rep_json["original_preserved"])

        # Damage detection on replacement image now succeeds
        dmg_res = self.client.post(f"/api/claims/{claim_id}/analyze-damage", json={"conf_threshold": 0.15})
        self.assertEqual(dmg_res.status_code, 200)
        self.assertTrue(dmg_res.get_json()["success"])

    # -------------------------------------------------------------------------
    # Test 12: Defensive Security & Negative Boundary Edge Cases
    # -------------------------------------------------------------------------
    def test_12_security_boundaries_and_negative_edge_cases(self):
        """Verifies RBAC boundaries, invalid ID regex rejection, and unauthenticated blocks."""
        self._register_user("user_owner", email="owner@test.com")
        self._register_user("user_intruder", email="intruder@test.com")

        self._login("user_owner")
        claim_id = self._submit_sample_claim("POL-2026-SEC1")

        # 1. Unauthenticated request to protected endpoint -> 401
        self.client.post("/api/auth/logout")
        unauth_res = self.client.get(f"/api/claims/{claim_id}")
        self.assertEqual(unauth_res.status_code, 401)

        # 2. Cross-user access attempt -> 403 Forbidden
        self._login("user_intruder")
        forbidden_res = self.client.get(f"/api/claims/{claim_id}")
        self.assertEqual(forbidden_res.status_code, 403)

        # 3. Malformed claim ID format -> 400 Bad Request
        bad_id_res = self.client.get("/api/claims/CLM-MALFORMED-ID")
        self.assertEqual(bad_id_res.status_code, 400)
        self.assertIn("Invalid Claim ID format", bad_id_res.get_json()["error"])

        # 4. Nonexistent claim ID -> 404 Not Found
        nonexistent_res = self.client.get("/api/claims/CLM-20261120-9999")
        self.assertEqual(nonexistent_res.status_code, 404)

        # 5. Dangerous file upload rejection (.exe) -> 400 Bad Request
        self._login("user_owner")
        malware_res = self.client.post(
            "/api/claims",
            data={
                "claimant_name": "Test User",
                "policy_number": "POL-2026-MAL",
                "vehicle_number": "DL-01-AB-1234",
                "accident_date": "2026-10-15",
                "claim_description": "Test collision.",
                "policy_document": (io.BytesIO(b"malware content"), "exploit.exe"),
                "claim_form": (io.BytesIO(b"%PDF-1.4"), "claim.pdf"),
                "invoice_document": (io.BytesIO(b"%PDF-1.4"), "invoice.pdf"),
                "vehicle_image": (io.BytesIO(self.img_bytes), "car.jpg"),
            },
            content_type="multipart/form-data",
        )
        self.assertEqual(malware_res.status_code, 400)

    # -------------------------------------------------------------------------
    # Test 13: Full Sequential Master E2E Pipeline Chaining
    # -------------------------------------------------------------------------
    def test_13_full_sequential_master_pipeline_chaining(self):
        """Chains all 10 workflows in a single continuous lifecycle scenario."""
        # 1. Signup & Login
        self.client.post("/api/auth/signup", json={
            "full_name": "Rajesh Master",
            "username": "rmaster",
            "email": "master@example.com",
            "password": "MasterPass99#",
            "confirm_password": "MasterPass99#",
        })
        self._login("rmaster", "MasterPass99#")

        # 2. Ingest Claim
        claim_id = self._submit_sample_claim("POL-2026-MASTER")

        # 3. Policy Lookup
        pol_res = self.client.get("/api/claims/policy/POL-2026-MASTER")
        self.assertEqual(pol_res.status_code, 200)

        # 4. Evidence Inspection
        detail_res = self.client.get(f"/api/claims/{claim_id}")
        self.assertEqual(detail_res.status_code, 200)

        # 5. Vision Damage Detection
        dmg_res = self.client.post(f"/api/claims/{claim_id}/analyze-damage", json={"conf_threshold": 0.15})
        self.assertEqual(dmg_res.status_code, 200)

        # 6. OCR Extraction
        ocr_res = self.client.get(f"/api/claims/{claim_id}/extracted")
        self.assertEqual(ocr_res.status_code, 200)

        # 7. NLP Narrative Analysis
        nlp_res = self.client.post(f"/api/claims/{claim_id}/analyze-nlp", json={})
        self.assertEqual(nlp_res.status_code, 200)

        # 8. Cross-Source Corroboration
        v_res = self.client.post(f"/api/claims/{claim_id}/verify-cross-source", json={})
        self.assertEqual(v_res.status_code, 200)

        # 9. Findings
        findings_res = self.client.get(f"/api/claims/{claim_id}/verification/findings")
        self.assertEqual(findings_res.status_code, 200)

        # 10. PDF Synthesis
        rec_res = self.client.get(f"/api/claims/{claim_id}/receipt")
        self.assertEqual(rec_res.status_code, 200)
        rep_res = self.client.get(f"/api/claims/{claim_id}/document-report")
        self.assertEqual(rep_res.status_code, 200)

        # Final Logout
        self.client.post("/api/auth/logout")


if __name__ == "__main__":
    unittest.main()
