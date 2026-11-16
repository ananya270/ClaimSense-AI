"""Comprehensive Unit and Integration Tests for Phase 7: Cross-Source Verification & Intelligent Claim Validation."""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

from backend.app import create_app
from backend.config import Config
from backend.database.db import get_db_session, init_database
from backend.database.models import (
    Claim,
    ClaimNLPAnalysis,
    ClaimVerificationRun,
    ExtractedInformation,
    VehicleDamageAnalysis,
    VehicleDamageDetection,
    VerificationFinding,
)
from backend.services.receipt import generate_document_intelligence_report_pdf
from backend.services.verification import (
    ClaimVerificationService,
    compare_dates,
    compare_invoice_vs_damage,
    compare_names,
    compare_narrative_vs_vision,
    compare_policy_numbers,
    compare_policy_validity,
    compare_vehicle_registrations,
    compute_verification_score_and_summary,
    normalize_date,
    normalize_name,
    normalize_policy_num,
    normalize_vehicle_reg,
    OVERALL_CONSISTENT,
    OVERALL_INSUFFICIENT_EVIDENCE,
    OVERALL_REVIEW_REQUIRED,
    SEVERITY_CRITICAL,
    SEVERITY_HIGH,
    SEVERITY_LOW,
    SEVERITY_MEDIUM,
    STATUS_INCONCLUSIVE,
    STATUS_MATCH,
    STATUS_MISMATCH,
    STATUS_MISSING_IN_SOURCE,
    STATUS_NOT_VISUALLY_CONFIRMED,
    STATUS_POTENTIAL_DISCREPANCY,
    STATUS_VISUAL_ONLY_FINDING,
)


class TestPhase7CrossSourceVerification(unittest.TestCase):
    """Test suite validating Phase 7 multi-source consistency and cross-corroboration."""

    @classmethod
    def setUpClass(cls):
        cls.test_dir = tempfile.mkdtemp()
        cls.db_path = Path(cls.test_dir) / "test_phase7.db"
        cls.upload_dir = Path(cls.test_dir) / "uploads"
        cls.upload_dir.mkdir(parents=True, exist_ok=True)

        class CustomConfig(Config):
            TESTING = True
            UPLOAD_FOLDER = cls.upload_dir
            REPORTS_FOLDER = Path(cls.test_dir) / "reports"
            DATA_FOLDER = Path(cls.test_dir) / "data"
            DATABASE_PATH = cls.db_path
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{cls.db_path.as_posix()}"
            RATELIMIT_ENABLED = False
            WTF_CSRF_ENABLED = False

        cls.app = create_app(CustomConfig)
        cls.client = cls.app.test_client()

        with cls.app.app_context():
            init_database(CustomConfig.SQLALCHEMY_DATABASE_URI)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.test_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # 1. Exact Matching Policy and Claim Fields
    # -------------------------------------------------------------------------
    def test_exact_matching_policy_and_claim_fields(self):
        """Verify exact matching across policy numbers, claimant names, and vehicle registration."""
        # Policy
        m_pol, c_pol, _ = compare_policy_numbers("POL-2024-88391", "POL-2024-88391")
        self.assertTrue(m_pol)
        self.assertEqual(c_pol, 1.0)

        # Name
        m_nam, c_nam, _ = compare_names("Rajesh Sharma", "Rajesh Sharma")
        self.assertTrue(m_nam)
        self.assertEqual(c_nam, 1.0)

        # Vehicle Registration
        m_veh, c_veh, _ = compare_vehicle_registrations("MH-12-DE-4052", "MH-12-DE-4052")
        self.assertTrue(m_veh)
        self.assertEqual(c_veh, 1.0)

    # -------------------------------------------------------------------------
    # 2. Name Normalization (Honorifics, Word Order, Minor Typos)
    # -------------------------------------------------------------------------
    def test_name_normalization_and_fuzzy_matching(self):
        """Verify name normalization strips honorifics and handles token reordering and minor typos."""
        # Strips titles like Mr., Dr., Shri
        self.assertEqual(normalize_name("Mr. Rajesh Sharma"), "rajesh sharma")
        self.assertEqual(normalize_name("Dr. Rajesh Kumar"), "rajesh kumar")
        self.assertEqual(normalize_name("Shri Rajesh Sharma"), "rajesh sharma")

        # Word reordering: 'Rajesh Sharma' vs 'Sharma, Rajesh'
        m1, c1, _ = compare_names("Rajesh Sharma", "Sharma, Rajesh")
        self.assertTrue(m1)
        self.assertGreaterEqual(c1, 0.95)

        # Partial/middle name variation
        m2, c2, _ = compare_names("Rajesh Kumar Sharma", "Rajesh Sharma")
        self.assertTrue(m2)
        self.assertGreaterEqual(c2, 0.88)

        # Minor OCR typo / edit distance
        m3, c3, _ = compare_names("Rajesh Sharma", "Rajehs Sharma")
        self.assertTrue(m3)
        self.assertGreaterEqual(c3, 0.85)

        # Unrelated names
        m4, _, _ = compare_names("Rajesh Sharma", "Vikram Singh")
        self.assertFalse(m4)

    # -------------------------------------------------------------------------
    # 3. Vehicle Registration Normalization & OCR Substitution
    # -------------------------------------------------------------------------
    def test_vehicle_registration_normalization_and_ocr_substitutions(self):
        """Verify normalization strips hyphens/spaces and handles common OCR character confusion (0/O, 1/I)."""
        # Spacing and hyphens
        self.assertEqual(normalize_vehicle_reg("MH-12-DE-4052"), "MH12DE4052")
        self.assertEqual(normalize_vehicle_reg("MH 12 DE 4052"), "MH12DE4052")

        # Exact match with formatting variance
        m1, c1, _ = compare_vehicle_registrations("MH-12-DE-4052", "MH 12 DE 4052")
        self.assertTrue(m1)
        self.assertEqual(c1, 1.0)

        # Common OCR substitution: 'O' instead of '0' in digit slots
        m2, c2, expl2 = compare_vehicle_registrations("MH-12-DE-4052", "MH-12-DE-4O52")
        self.assertTrue(m2)
        self.assertGreaterEqual(c2, 0.90)
        self.assertIn("OCR", expl2)

        # Common OCR substitution: 'I' instead of '1'
        m3, c3, _ = compare_vehicle_registrations("DL-01-AB-1234", "DL-01-AB-I234")
        self.assertTrue(m3)
        self.assertGreaterEqual(c3, 0.90)

        # Actual different vehicles
        m4, _, _ = compare_vehicle_registrations("MH-12-DE-4052", "DL-04-XY-9999")
        self.assertFalse(m4)

    # -------------------------------------------------------------------------
    # 4. Date Normalization (Formats: YYYY-MM-DD, DD/MM/YYYY, Textual)
    # -------------------------------------------------------------------------
    def test_date_normalization_across_formats(self):
        """Verify parsing across ISO, slash, hyphen, and textual calendar dates."""
        d1 = normalize_date("2026-09-28")
        d2 = normalize_date("28/09/2026")
        d3 = normalize_date("28-09-2026")
        d4 = normalize_date("28 Sep 2026")
        d5 = normalize_date("September 28, 2026")

        expected = date(2026, 9, 28)
        self.assertEqual(d1, expected)
        self.assertEqual(d2, expected)
        self.assertEqual(d3, expected)
        self.assertEqual(d4, expected)
        self.assertEqual(d5, expected)

    # -------------------------------------------------------------------------
    # 5. Policy Validity Date Window Comparison
    # -------------------------------------------------------------------------
    def test_policy_validity_window_comparison(self):
        """Verify active policy validity matching, pre-effective, expired, and unreadable handling."""
        # Active coverage: 2026-01-01 to 2026-12-31, accident on 2026-09-28
        st1, sev1, conf1, _ = compare_policy_validity(
            accident_date_val="2026-09-28",
            policy_start_val="2026-01-01",
            policy_end_val="2026-12-31",
        )
        self.assertEqual(st1, STATUS_MATCH)
        self.assertEqual(sev1, SEVERITY_LOW)
        self.assertEqual(conf1, 1.0)

        # Expired policy: policy ended 2026-05-01, accident on 2026-09-28 -> CRITICAL MISMATCH
        st2, sev2, _, expl2 = compare_policy_validity(
            accident_date_val="2026-09-28",
            policy_start_val="2025-05-01",
            policy_end_val="2026-05-01",
        )
        self.assertEqual(st2, STATUS_MISMATCH)
        self.assertEqual(sev2, SEVERITY_CRITICAL)
        self.assertIn("AFTER policy expiry date", expl2)

        # Pre-effective policy: policy starts 2026-10-01, accident on 2026-09-28 -> CRITICAL MISMATCH
        st3, sev3, _, expl3 = compare_policy_validity(
            accident_date_val="2026-09-28",
            policy_start_val="2026-10-01",
            policy_end_val="2027-10-01",
        )
        self.assertEqual(st3, STATUS_MISMATCH)
        self.assertEqual(sev3, SEVERITY_CRITICAL)
        self.assertIn("BEFORE policy effective start date", expl3)

        # Unreadable / missing validity dates -> INCONCLUSIVE (never assume invalid solely on missing OCR)
        st4, sev4, _, expl4 = compare_policy_validity(
            accident_date_val="2026-09-28",
            validity_val=None,
        )
        self.assertEqual(st4, STATUS_INCONCLUSIVE)
        self.assertEqual(sev4, SEVERITY_LOW)
        self.assertIn("cannot be verified or disproven from OCR data alone", expl4)

    # -------------------------------------------------------------------------
    # 6. Conflicting Accident Dates (Direct Mismatch)
    # -------------------------------------------------------------------------
    def test_conflicting_accident_dates(self):
        """Verify that conflicting dates across claim form and intake return MISMATCH with HIGH severity."""
        st, conf, expl = compare_dates("2026-09-28", "2026-10-15")
        self.assertEqual(st, STATUS_MISMATCH)
        self.assertEqual(conf, 1.0)
        self.assertIn("Conflicting", expl)

    # -------------------------------------------------------------------------
    # 7. Missing Source Values
    # -------------------------------------------------------------------------
    def test_missing_source_values(self):
        """Verify that missing dates or fields return MISSING_IN_SOURCE without treating as fraudulent."""
        st, conf, expl = compare_dates("2026-09-28", "")
        self.assertEqual(st, STATUS_MISSING_IN_SOURCE)
        self.assertEqual(conf, 0.9)

    # -------------------------------------------------------------------------
    # 8. Inconclusive Comparisons
    # -------------------------------------------------------------------------
    def test_inconclusive_comparisons(self):
        """Verify unparseable or ambiguous data returns INCONCLUSIVE."""
        st, sev, _, expl = compare_policy_validity("unparseable date string", "invalid validity")
        self.assertEqual(st, STATUS_INCONCLUSIVE)
        self.assertEqual(sev, SEVERITY_LOW)

    # -------------------------------------------------------------------------
    # 9. NLP Narrative vs OCR Comparisons
    # -------------------------------------------------------------------------
    def test_nlp_narrative_vs_ocr_comparisons(self):
        """Verify cross-source comparison between Phase 6 narrative entities and Phase 4 structured doc rows."""
        res = ClaimVerificationService.execute_cross_source_verification(
            claim_id="CLM-20261116-NLP1",
            claim_record={
                "claim_id": "CLM-20261116-NLP1",
                "claimant_name": "Rajesh Sharma",
                "policy_number": "POL-2024-88391",
                "vehicle_number": "MH-12-DE-4052",
                "accident_date": "2026-09-28",
                "incident_location": "MG Road",
                "claim_description": "Vehicle MH-12-DE-4052 was hit on 2026-09-28 near MG Road.",
            },
            extracted_doc_rows=[
                {"field_name": "policy_number", "field_value": "POL-2024-88391", "source": "policy_document", "source_filename": "policy.pdf"},
                {"field_name": "claimant_name", "field_value": "Rajesh Sharma", "source": "policy_document", "source_filename": "policy.pdf"},
                {"field_name": "vehicle_number", "field_value": "MH-12-DE-4052", "source": "claim_form", "source_filename": "claim.pdf"},
                {"field_name": "accident_date", "field_value": "2026-09-28", "source": "claim_form", "source_filename": "claim.pdf"},
            ],
            nlp_analysis={
                "original_narrative": "Vehicle MH-12-DE-4052 was hit on 2026-09-28 near MG Road.",
                "entities": [
                    {"entity_type": "VEHICLE_REGISTRATION", "text": "MH-12-DE-4052"},
                    {"entity_type": "ACCIDENT_DATE", "text": "2026-09-28"},
                    {"entity_type": "LOCATION", "text": "MG Road"},
                ],
                "reported_damages": [],
            },
        )

        statuses = [f["comparison_status"] for f in res["findings"]]
        self.assertIn(STATUS_MATCH, statuses)
        self.assertEqual(res["mismatched_comparisons"], 0)
        self.assertGreaterEqual(res["consistency_score"], 80.0)

    # -------------------------------------------------------------------------
    # 10. NLP Damage vs YOLO Damage Corroboration (MATCH)
    # -------------------------------------------------------------------------
    def test_nlp_damage_vs_yolo_damage_corroboration(self):
        """Verify that narrative reported damage matching YOLOv8 detections yields STATUS_MATCH."""
        reported = [
            {"component": "Rear Bumper", "spatial_region": "rear", "reported_condition": "Dented"},
            {"component": "Right Tail Lamp Assembly", "spatial_region": "rear_right", "reported_condition": "Broken"},
        ]
        vision = {
            "detection_method": "YOLOv8",
            "total_detections": 2,
            "detections": [
                {"category": "dent", "confidence": 0.92, "location_region": "rear", "bbox": [50, 100, 200, 250]},
                {"category": "lamp broken", "confidence": 0.88, "location_region": "rear_right", "bbox": [180, 80, 260, 150]},
            ],
        }

        findings = compare_narrative_vs_vision(reported, vision)
        self.assertEqual(len(findings), 2)
        for f in findings:
            self.assertEqual(f["comparison_status"], STATUS_MATCH)
            self.assertEqual(f["severity"], SEVERITY_LOW)
            self.assertGreaterEqual(f["confidence"], 0.85)

    # -------------------------------------------------------------------------
    # 11. Narrative Damage Without Visual Confirmation (NOT_VISUALLY_CONFIRMED)
    # -------------------------------------------------------------------------
    def test_narrative_damage_without_visual_confirmation(self):
        """Verify reported damage not detected in photograph produces NOT_VISUALLY_CONFIRMED non-punitively."""
        reported = [
            {"component": "Radiator Grill", "spatial_region": "front", "reported_condition": "Cracked"},
        ]
        vision = {
            "detection_method": "YOLOv8",
            "total_detections": 1,
            "detections": [
                {"category": "dent", "confidence": 0.90, "location_region": "rear", "bbox": [10, 10, 50, 50]},
            ],
        }

        findings = compare_narrative_vs_vision(reported, vision)
        reported_finding = [f for f in findings if "Radiator Grill" in f["field_name"]][0]
        self.assertEqual(reported_finding["comparison_status"], STATUS_NOT_VISUALLY_CONFIRMED)
        self.assertEqual(reported_finding["severity"], SEVERITY_MEDIUM)
        self.assertIn("not detected in the provided vehicle photograph", reported_finding["explanation"])

    # -------------------------------------------------------------------------
    # 12. Visual-Only Damage Findings (VISUAL_ONLY_FINDING)
    # -------------------------------------------------------------------------
    def test_visual_only_damage_findings(self):
        """Verify genuine YOLO detection not mentioned in narrative produces VISUAL_ONLY_FINDING."""
        reported = [
            {"component": "Rear Bumper", "spatial_region": "rear", "reported_condition": "Dented"},
        ]
        vision = {
            "detection_method": "YOLOv8",
            "total_detections": 2,
            "detections": [
                {"category": "dent", "confidence": 0.92, "location_region": "rear", "bbox": [50, 100, 200, 250]},
                {"category": "glass shatter", "confidence": 0.84, "location_region": "center", "bbox": [100, 50, 300, 180]},
            ],
        }

        findings = compare_narrative_vs_vision(reported, vision)
        visual_only = [f for f in findings if f["comparison_status"] == STATUS_VISUAL_ONLY_FINDING]
        self.assertEqual(len(visual_only), 1)
        self.assertEqual(visual_only[0]["severity"], SEVERITY_LOW)
        self.assertIn("glass shatter", visual_only[0]["normalized_value_b"])

    # -------------------------------------------------------------------------
    # 13. Invoice vs Damage Comparisons (Supported, Unreported, Missing)
    # -------------------------------------------------------------------------
    def test_invoice_vs_damage_comparisons(self):
        """Verify invoice repair items are matched to reported damage or flagged as potential discrepancies."""
        reported = [
            {"component": "Rear Bumper", "spatial_region": "rear"},
            {"component": "Tail Lamp", "spatial_region": "rear_right"},
        ]
        vision = {
            "detections": [
                {"category": "dent", "location_region": "rear"},
                {"category": "lamp broken", "location_region": "rear_right"},
            ]
        }
        invoice_items = [
            "Tail lamp replacement",
            "Rear bumper bodywork and paint",
            "Air conditioning compressor replacement",  # Unrelated to collision
        ]

        findings = compare_invoice_vs_damage(invoice_items, reported, vision)
        self.assertEqual(len(findings), 3)

        st_map = {f["field_name"]: f["comparison_status"] for f in findings}
        self.assertEqual(st_map["Invoice Item: Tail lamp replacement"], STATUS_MATCH)
        self.assertEqual(st_map["Invoice Item: Rear bumper bodywork and paint"], STATUS_MATCH)
        self.assertEqual(st_map["Invoice Item: Air conditioning compressor replacement"], STATUS_POTENTIAL_DISCREPANCY)

    # -------------------------------------------------------------------------
    # 14. Confidence Threshold Behavior
    # -------------------------------------------------------------------------
    def test_confidence_threshold_behavior(self):
        """Verify findings include accurate confidence values reflecting detection confidence."""
        reported = [{"component": "Rear Bumper", "spatial_region": "rear"}]
        vision_low = {
            "detection_method": "YOLOv8",
            "detections": [{"category": "dent", "confidence": 0.35, "location_region": "rear"}],
        }
        vision_high = {
            "detection_method": "YOLOv8",
            "detections": [{"category": "dent", "confidence": 0.94, "location_region": "rear"}],
        }

        f_low = compare_narrative_vs_vision(reported, vision_low)[0]
        f_high = compare_narrative_vs_vision(reported, vision_high)[0]

        self.assertEqual(f_low["confidence"], 0.35)
        self.assertEqual(f_high["confidence"], 0.94)

    # -------------------------------------------------------------------------
    # 15. Severity Classification (LOW, MEDIUM, HIGH, CRITICAL)
    # -------------------------------------------------------------------------
    def test_severity_classification(self):
        """Verify that severities are assigned appropriately: LOW for matches, HIGH for dates, CRITICAL for policy expiry."""
        findings = [
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW},
            {"comparison_status": STATUS_NOT_VISUALLY_CONFIRMED, "severity": SEVERITY_MEDIUM},
            {"comparison_status": STATUS_MISMATCH, "severity": SEVERITY_HIGH},
            {"comparison_status": STATUS_MISMATCH, "severity": SEVERITY_CRITICAL},
        ]
        res = compute_verification_score_and_summary(findings)
        self.assertEqual(res["critical_severity_count"], 1)
        self.assertEqual(res["high_severity_count"], 1)
        self.assertEqual(res["overall_status"], OVERALL_REVIEW_REQUIRED)

    # -------------------------------------------------------------------------
    # 16. Consistency Score Calculation & Neutral Assessment
    # -------------------------------------------------------------------------
    def test_consistency_score_and_neutral_assessment(self):
        """Verify consistency score calculation and that claims are never labeled fraudulent."""
        # 1. High match set -> CONSISTENT
        consistent_findings = [
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW},
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW},
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW},
            {"comparison_status": STATUS_MISSING_IN_SOURCE, "severity": SEVERITY_LOW},  # Missing should not penalize
        ]
        r1 = compute_verification_score_and_summary(consistent_findings)
        self.assertEqual(r1["overall_status"], OVERALL_CONSISTENT)
        self.assertGreaterEqual(r1["consistency_score"], 90.0)

        # 2. Critical mismatch -> REVIEW_REQUIRED
        critical_findings = [
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW},
            {"comparison_status": STATUS_MISMATCH, "severity": SEVERITY_CRITICAL},
        ]
        r2 = compute_verification_score_and_summary(critical_findings)
        self.assertEqual(r2["overall_status"], OVERALL_REVIEW_REQUIRED)
        self.assertLess(r2["consistency_score"], 70.0)
        self.assertIn("CRITICAL", r2["recommendations"][0])
        # Neutral phrasing
        self.assertNotIn("fraudulent", r2["disclaimer"].lower())
        self.assertIn("decision support", r2["disclaimer"].lower())

        # 3. All missing -> INSUFFICIENT_EVIDENCE
        missing_findings = [
            {"comparison_status": STATUS_MISSING_IN_SOURCE, "severity": SEVERITY_LOW},
            {"comparison_status": STATUS_MISSING_IN_SOURCE, "severity": SEVERITY_LOW},
        ]
        r3 = compute_verification_score_and_summary(missing_findings)
        self.assertEqual(r3["overall_status"], OVERALL_INSUFFICIENT_EVIDENCE)

    # -------------------------------------------------------------------------
    # 17. Duplicate Prevention and Rerun Idempotency
    # -------------------------------------------------------------------------
    def test_duplicate_prevention_and_idempotency(self):
        """Verify calling verify_claim without force reuses persisted run without creating duplicates."""
        claim_id = "CLM-20261116-IDEM"
        now_utc = datetime.now(timezone.utc)

        with get_db_session() as db:
            c = Claim(
                claim_id=claim_id,
                claimant_name="Aarav Sharma",
                policy_number="POL-111",
                vehicle_number="MH-01-AA-1111",
                accident_date="2026-10-10",
                claim_description="Front bumper damaged in minor parking mishap.",
                status="SUBMITTED",
                created_at=now_utc,
            )
            db.add(c)
            db.commit()

        # Run 1
        res1 = ClaimVerificationService.verify_claim(claim_id, force=False)
        run_id_1 = res1["id"]

        # Run 2 without force
        res2 = ClaimVerificationService.verify_claim(claim_id, force=False)
        run_id_2 = res2["id"]
        self.assertEqual(run_id_1, run_id_2)

        # Run 3 with force=True
        res3 = ClaimVerificationService.verify_claim(claim_id, force=True)
        run_id_3 = res3["id"]
        self.assertNotEqual(run_id_1, run_id_3)

        # Verify database contains both runs
        with get_db_session() as db:
            runs = db.query(ClaimVerificationRun).filter_by(claim_id=claim_id).all()
            self.assertEqual(len(runs), 2)

    # -------------------------------------------------------------------------
    # 18. Database Persistence and Querying
    # -------------------------------------------------------------------------
    def test_database_persistence_and_querying(self):
        """Verify ClaimVerificationRun and VerificationFinding ORM persistence and cascade relationships."""
        claim_id = "CLM-20261116-PERS"
        now_utc = datetime.now(timezone.utc)

        with get_db_session() as db:
            c = Claim(
                claim_id=claim_id,
                claimant_name="Sunil Patil",
                policy_number="POL-222",
                vehicle_number="KA-01-BB-2222",
                accident_date="2026-09-01",
                claim_description="Rear-ended at signal.",
                status="SUBMITTED",
                created_at=now_utc,
            )
            db.add(c)
            db.commit()

        res = ClaimVerificationService.verify_claim(claim_id, force=True)
        self.assertEqual(res["claim_id"], claim_id)
        self.assertGreater(len(res["findings"]), 0)

        with get_db_session() as db:
            claim_loaded = db.query(Claim).filter_by(claim_id=claim_id).first()
            self.assertIsNotNone(claim_loaded)
            c_dict = claim_loaded.to_dict(include_evidence=True)
            self.assertIsNotNone(c_dict.get("verification"))
            verif_dict = c_dict["verification"]
            self.assertEqual(verif_dict["claim_id"], claim_id)
            self.assertIn("findings", verif_dict)

    # -------------------------------------------------------------------------
    # 19. API Authentication and Authorization Controls
    # -------------------------------------------------------------------------
    def test_api_authentication_and_authorization(self):
        """Verify 401 Unauthorized for unauthenticated callers and 200 for authorized assessor/admin."""
        claim_id = "CLM-20261116-AUTH"
        now_utc = datetime.now(timezone.utc)

        with get_db_session() as db:
            c = Claim(
                claim_id=claim_id,
                claimant_name="Karan Malhotra",
                policy_number="POL-333",
                vehicle_number="MH-03-CC-3333",
                accident_date="2026-08-15",
                claim_description="Vehicle hit while parked.",
                status="SUBMITTED",
                created_at=now_utc,
            )
            db.add(c)
            db.commit()

        # 1. Unauthenticated POST -> 401
        with self.client.session_transaction() as sess:
            sess.clear()

        unauth_post = self.client.post(f"/api/claims/{claim_id}/verify-cross-source")
        self.assertEqual(unauth_post.status_code, 401)

        # 2. Unauthenticated GET -> 401
        unauth_get = self.client.get(f"/api/claims/{claim_id}/verification")
        self.assertEqual(unauth_get.status_code, 401)

        # 3. Authenticated session as admin
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["username"] = "admin"
            sess["role"] = "admin"

        auth_post = self.client.post(f"/api/claims/{claim_id}/verify-cross-source")
        self.assertEqual(auth_post.status_code, 200)
        p_json = auth_post.get_json()
        self.assertTrue(p_json["success"])
        self.assertEqual(p_json["claim_id"], claim_id)

        # Verification query endpoints
        get_res = self.client.get(f"/api/claims/{claim_id}/verification")
        self.assertEqual(get_res.status_code, 200)
        self.assertTrue(get_res.get_json()["verified"])

        findings_res = self.client.get(f"/api/claims/{claim_id}/verification/findings")
        self.assertEqual(findings_res.status_code, 200)
        self.assertGreaterEqual(findings_res.get_json()["total_findings"], 1)

        summary_res = self.client.get(f"/api/claims/{claim_id}/verification/summary")
        self.assertEqual(summary_res.status_code, 200)
        self.assertIn("consistency_score", summary_res.get_json())

    # -------------------------------------------------------------------------
    # 20. Invalid and Nonexistent Claim Handling
    # -------------------------------------------------------------------------
    def test_invalid_and_nonexistent_claim_handling(self):
        """Verify 400 Bad Request on invalid format and 404 Not Found on nonexistent claims."""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["username"] = "admin"
            sess["role"] = "admin"

        # Invalid format
        inv_post = self.client.post("/api/claims/INVALID-ID/verify-cross-source")
        self.assertEqual(inv_post.status_code, 400)

        inv_get = self.client.get("/api/claims/INVALID-ID/verification")
        self.assertEqual(inv_get.status_code, 400)

        # Nonexistent claim
        non_post = self.client.post("/api/claims/CLM-20261116-NONX/verify-cross-source")
        self.assertEqual(non_post.status_code, 404)

        non_get = self.client.get("/api/claims/CLM-20261116-NONX/verification")
        self.assertEqual(non_get.status_code, 404)

    # -------------------------------------------------------------------------
    # 21. PDF Report Generation with Phase 7 Section
    # -------------------------------------------------------------------------
    def test_pdf_report_generation_with_phase7(self):
        """Verify generate_document_intelligence_report_pdf outputs 8 pages when Phase 7 verification is present."""
        claim_dict = {
            "claim_id": "CLM-20261116-PDF7",
            "claimant_name": "Rajesh Sharma",
            "policy_number": "POL-2024-88391",
            "vehicle_number": "MH-12-DE-4052",
            "accident_date": "2026-09-28",
            "claim_description": "Rear bumper and tail lamp damaged in intersection signal collision.",
            "status": "SUBMITTED",
            "documents": [],
            "images": [],
            "verification": {
                "overall_status": "CONSISTENT",
                "consistency_score": 92.5,
                "total_comparisons": 6,
                "matched_comparisons": 5,
                "mismatched_comparisons": 0,
                "missing_evidence_count": 1,
                "engine_version": "1.0.0",
                "processing_time_ms": 14.2,
                "recommendations": ["All primary evidence sources corroborate consistently."],
                "findings": [
                    {
                        "comparison_id": "CMP-POL-001",
                        "field_name": "Policy Number",
                        "source_a": "Policy Document",
                        "source_b": "Claim Form",
                        "original_value_a": "POL-2024-88391",
                        "original_value_b": "POL-2024-88391",
                        "comparison_status": "MATCH",
                        "severity": "LOW",
                    },
                    {
                        "comparison_id": "CMP-NAM-002",
                        "field_name": "Claimant Name",
                        "source_a": "Policy Document",
                        "source_b": "Claim Form",
                        "original_value_a": "Rajesh Sharma",
                        "original_value_b": "Rajesh Sharma",
                        "comparison_status": "MATCH",
                        "severity": "LOW",
                    },
                ],
            },
        }
        rows = [
            {"field_name": "accident_date", "field_value": "2026-09-28", "source": "policy_document"},
            {"field_name": "vehicle_number", "field_value": "MH-12-DE-4052", "source": "policy_document"},
        ]

        pdf_bytes = generate_document_intelligence_report_pdf(
            claim_dict,
            rows,
            upload_root=str(self.upload_dir),
            include_phase7=True,
        )
        self.assertGreater(len(pdf_bytes), 5000)

        import fitz
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            self.assertEqual(len(doc), 8)
            page7_text = doc[6].get_text()
            self.assertIn("Cross-Source Verification", page7_text)
            self.assertIn("CONSISTENT", page7_text)
            self.assertIn("92.5%", page7_text)

    # -------------------------------------------------------------------------
    # 22. Missing Phase 5/6 Upstream Results Handled Gracefully
    # -------------------------------------------------------------------------
    def test_missing_upstream_results_handled_gracefully(self):
        """Verify verification completes successfully even when vision and NLP results are unavailable."""
        claim_id = "CLM-20261116-GRAC"
        now_utc = datetime.now(timezone.utc)

        with get_db_session() as db:
            c = Claim(
                claim_id=claim_id,
                claimant_name="Nitin Joshi",
                policy_number="POL-555",
                vehicle_number="MH-05-EE-5555",
                accident_date="2026-07-20",
                claim_description="Minimal description without image.",
                status="SUBMITTED",
                created_at=now_utc,
            )
            db.add(c)
            db.commit()

        # Execute verification with no vision or OCR document data
        res = ClaimVerificationService.verify_claim(claim_id, force=True)
        self.assertEqual(res["claim_id"], claim_id)
        self.assertEqual(res["processing_status"], "completed")
        self.assertIn(res["overall_status"], [OVERALL_CONSISTENT, OVERALL_INSUFFICIENT_EVIDENCE])

    # -------------------------------------------------------------------------
    # 23. Low-Confidence YOLO Detections Produce Inconclusive Corroboration
    # -------------------------------------------------------------------------
    def test_low_confidence_yolo_detection_produces_inconclusive(self):
        """Verify that candidate detections with confidence between 0.25 and 0.50 produce STATUS_INCONCLUSIVE."""
        reported = [
            {"component": "Right Tail Lamp Assembly", "spatial_region": "rear_right", "reported_condition": "Damaged"}
        ]
        # Low confidence (0.301) matching detection
        vision = {
            "detection_method": "YOLOv8",
            "total_detections": 1,
            "detections": [
                {
                    "category": "lamp broken",
                    "confidence": 0.301,
                    "location_region": "rear_right",
                    "bbox": [345.8, 239.8, 700.0, 362.9],
                }
            ],
        }

        findings = compare_narrative_vs_vision(reported, vision)
        self.assertEqual(len(findings), 1)
        finding = findings[0]
        self.assertEqual(finding["comparison_status"], STATUS_INCONCLUSIVE)
        self.assertEqual(finding["severity"], SEVERITY_LOW)
        self.assertEqual(finding["confidence"], 0.3)
        self.assertIn("low confidence", finding["explanation"].lower())
        self.assertIn("insufficient to confirm or refute", finding["explanation"].lower())

    # -------------------------------------------------------------------------
    # 24. Overlapping Bounding Boxes Clustered and Noise Filtered
    # -------------------------------------------------------------------------
    def test_overlapping_visual_detections_clustered(self):
        """Verify multiple detections in same spatial region are clustered into a single finding with overlap count."""
        reported = [
            {"component": "Rear Bumper", "spatial_region": "rear", "reported_condition": "Damaged"}
        ]
        vision = {
            "detection_method": "YOLOv8",
            "total_detections": 6,
            "detections": [
                # Matches reported rear bumper
                {"category": "dent", "confidence": 0.95, "location_region": "rear", "bbox": [0, 0, 100, 100]},
                # 3 overlapping dents in center_left (conf >= 0.40)
                {"category": "dent", "confidence": 0.90, "location_region": "center_left", "bbox": [10, 20, 80, 90]},
                {"category": "dent", "confidence": 0.82, "location_region": "center_left", "bbox": [15, 25, 85, 95]},
                {"category": "dent", "confidence": 0.65, "location_region": "center_left", "bbox": [20, 30, 90, 100]},
                # 1 glass shatter in center
                {"category": "glass shatter", "confidence": 0.88, "location_region": "center", "bbox": [50, 50, 150, 150]},
                # 1 noisy sub-threshold detection (< 0.40) which should be filtered out
                {"category": "crack", "confidence": 0.28, "location_region": "center_left", "bbox": [12, 22, 40, 50]},
            ],
        }

        findings = compare_narrative_vs_vision(reported, vision)
        # Expected:
        # 1 MATCH (Rear Bumper)
        # 1 VISUAL_ONLY_FINDING for dent in center_left (clustered from 3 detections, max conf 0.90)
        # 1 VISUAL_ONLY_FINDING for glass shatter in center (conf 0.88)
        # Sub-threshold crack (0.28) omitted
        self.assertEqual(len(findings), 3)

        match_findings = [f for f in findings if f["comparison_status"] == STATUS_MATCH]
        self.assertEqual(len(match_findings), 1)

        visual_findings = [f for f in findings if f["comparison_status"] == STATUS_VISUAL_ONLY_FINDING]
        self.assertEqual(len(visual_findings), 2)

        dent_cl = [f for f in visual_findings if "Dent" in f["field_name"]][0]
        self.assertEqual(dent_cl["confidence"], 0.90)
        self.assertEqual(dent_cl["evidence_references"]["overlapping_detections_count"], 3)
        self.assertIn("3 overlapping detections", dent_cl["explanation"])

    # -------------------------------------------------------------------------
    # 25. Multiple Visual-Only Findings Trigger Review Required
    # -------------------------------------------------------------------------
    def test_multiple_visual_only_findings_trigger_review_required(self):
        """Verify that >= 3 visual-only findings trigger OVERALL_REVIEW_REQUIRED and score is not inflated."""
        findings = [
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW},
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW},
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW},
            {"comparison_status": STATUS_VISUAL_ONLY_FINDING, "severity": SEVERITY_LOW},
            {"comparison_status": STATUS_VISUAL_ONLY_FINDING, "severity": SEVERITY_LOW},
            {"comparison_status": STATUS_VISUAL_ONLY_FINDING, "severity": SEVERITY_LOW},
        ]
        res = compute_verification_score_and_summary(findings)
        # Score calculation: (3 * 1.0 + 3 * 0.60) / 6 = 4.8 / 6 = 80.0%
        self.assertEqual(res["consistency_score"], 80.0)
        # Multiple unlisted damage detections require human review for pre-existing damage
        self.assertEqual(res["overall_status"], OVERALL_REVIEW_REQUIRED)
        self.assertTrue(any("unlisted in claimant statement" in r for r in res["recommendations"]))

    # -------------------------------------------------------------------------
    # 26. Invoice Corroboration Semantics (Components vs Labor vs Discrepancies)
    # -------------------------------------------------------------------------
    def test_invoice_corroboration_semantics_and_overhead(self):
        """Verify distinct corroboration semantics for components, repair overhead, and unrelated items."""
        reported = [
            {"component": "Rear Bumper", "spatial_region": "rear"},
            {"component": "Right Tail Lamp Assembly", "spatial_region": "rear_right"},
        ]
        vision = {
            "detections": [
                {"category": "dent", "location_region": "rear"},
            ]
        }
        invoice_items = [
            "Tail lamp replacement",               # Documented component
            "Bodywork and paint",                  # Standard repair overhead
            "Labor and miscellaneous",             # Standard repair overhead
            "Front fog lamp assembly",             # Unrelated component (directional "front" must not match)
            "Transmission fluid flush",            # Completely unrelated mechanical item
        ]

        findings = compare_invoice_vs_damage(invoice_items, reported, vision)
        self.assertEqual(len(findings), 5)

        st_map = {f["field_name"]: f for f in findings}

        # 1. Component match
        lamp_f = st_map["Invoice Item: Tail lamp replacement"]
        self.assertEqual(lamp_f["comparison_status"], STATUS_MATCH)
        self.assertIn("documented damage to 'right tail lamp assembly'", lamp_f["explanation"])

        # 2. Repair overhead (labor & paint)
        body_f = st_map["Invoice Item: Bodywork and paint"]
        self.assertEqual(body_f["comparison_status"], STATUS_MATCH)
        self.assertIn("standard workshop labor or refinishing operations", body_f["explanation"])

        labor_f = st_map["Invoice Item: Labor and miscellaneous"]
        self.assertEqual(labor_f["comparison_status"], STATUS_MATCH)
        self.assertIn("standard workshop labor or refinishing operations", labor_f["explanation"])

        # 3. Discrepancy: Front fog lamp (not matched despite "front" word)
        fog_f = st_map["Invoice Item: Front fog lamp assembly"]
        self.assertEqual(fog_f["comparison_status"], STATUS_POTENTIAL_DISCREPANCY)
        self.assertEqual(fog_f["severity"], SEVERITY_MEDIUM)

        # 4. Discrepancy: Transmission fluid
        trans_f = st_map["Invoice Item: Transmission fluid flush"]
        self.assertEqual(trans_f["comparison_status"], STATUS_POTENTIAL_DISCREPANCY)
        self.assertEqual(trans_f["severity"], SEVERITY_MEDIUM)

    # -------------------------------------------------------------------------
    # 27. All MATCH Findings With No Inconclusive Results
    # -------------------------------------------------------------------------
    def test_all_match_findings_no_inconclusive(self):
        """Verify that a claim with all MATCH findings and 0 inconclusive results achieves 100% score, 100% coverage, and CONSISTENT status."""
        findings = [
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW, "field_name": "Policy Number"},
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW, "field_name": "Claimant Name"},
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW, "field_name": "Vehicle Registration"},
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW, "field_name": "Damage: Rear Bumper"},
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW, "field_name": "Invoice Item: Bumper repair"},
        ]
        res = compute_verification_score_and_summary(findings)
        self.assertEqual(res["consistency_score"], 100.0)
        self.assertEqual(res["evidence_coverage_percentage"], 100.0)
        self.assertEqual(res["overall_status"], OVERALL_CONSISTENT)
        self.assertEqual(res["cv_unevaluated_count"], 0)
        self.assertEqual(res["inconclusive_count"], 0)
        self.assertTrue(any("corroborate consistently" in r for r in res["recommendations"]))

    # -------------------------------------------------------------------------
    # 28. MATCH Findings Plus Policy Validity INCONCLUSIVE
    # -------------------------------------------------------------------------
    def test_match_findings_plus_policy_inconclusive(self):
        """Verify that when only policy validity dates are unparseable (1 inconclusive), score is uninflated, coverage is high, and advisory recommendation is generated."""
        findings = [
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW, "field_name": "Policy Number"},
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW, "field_name": "Claimant Name"},
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW, "field_name": "Vehicle Registration"},
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW, "field_name": "Damage: Rear Bumper"},
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW, "field_name": "Invoice Item: Bumper repair"},
            {"comparison_status": STATUS_INCONCLUSIVE, "severity": SEVERITY_LOW, "field_name": "Policy Coverage Validity Window"},
        ]
        res = compute_verification_score_and_summary(findings)
        # Score: (5 * 1.0 + 1 * 0.5) / 6 = 5.5 / 6 = 91.7%
        self.assertEqual(res["consistency_score"], 91.7)
        # Coverage: 5 evaluated out of 6 = 83.3%
        self.assertEqual(res["evidence_coverage_percentage"], 83.3)
        self.assertEqual(res["overall_status"], OVERALL_CONSISTENT)
        self.assertEqual(res["inconclusive_count"], 1)
        self.assertEqual(res["cv_unevaluated_count"], 0)
        self.assertTrue(any("Policy validity coverage period could not be confirmed" in r for r in res["recommendations"]))

    # -------------------------------------------------------------------------
    # 29. MATCH Findings Plus Unavailable Computer Vision Analysis
    # -------------------------------------------------------------------------
    def test_match_findings_plus_unavailable_computer_vision(self):
        """Verify that when Computer Vision was not executed for reported damages, overall status requires review and score is not 100%."""
        findings = [
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW, "field_name": "Policy Number"},
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW, "field_name": "Claimant Name"},
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW, "field_name": "Vehicle Registration"},
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW, "field_name": "Incident Location"},
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW, "field_name": "Invoice Item: Bodywork"},
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW, "field_name": "Invoice Item: Paint"},
            # 3 vehicle damage items with CV unexecuted
            {
                "comparison_status": STATUS_INCONCLUSIVE,
                "severity": SEVERITY_LOW,
                "field_name": "Damage: Rear Bumper",
                "source_b": "Vehicle Photograph (Computer Vision)",
                "original_value_b": "Analysis not executed / failed",
                "evidence_references": {"reason": "vision_analysis_unavailable"},
            },
            {
                "comparison_status": STATUS_INCONCLUSIVE,
                "severity": SEVERITY_LOW,
                "field_name": "Damage: Trunk Hatch",
                "source_b": "Vehicle Photograph (Computer Vision)",
                "original_value_b": "Analysis not executed / failed",
                "evidence_references": {"reason": "vision_analysis_unavailable"},
            },
            {
                "comparison_status": STATUS_INCONCLUSIVE,
                "severity": SEVERITY_LOW,
                "field_name": "Damage: Tail Lamp",
                "source_b": "Vehicle Photograph (Computer Vision)",
                "original_value_b": "Analysis not executed / failed",
                "evidence_references": {"reason": "vision_analysis_unavailable"},
            },
        ]
        res = compute_verification_score_and_summary(findings)
        # Score: (6 * 1.0 + 3 * 0.5) / 9 = 7.5 / 9 = 83.3%
        self.assertEqual(res["consistency_score"], 83.3)
        self.assertEqual(res["evidence_coverage_percentage"], 66.7)
        self.assertEqual(res["cv_unevaluated_count"], 3)
        # MUST require review because core physical damage was never visually confirmed!
        self.assertEqual(res["overall_status"], OVERALL_REVIEW_REQUIRED)
        self.assertTrue(any("Computer Vision damage analysis was not executed or failed for 3" in r for r in res["recommendations"]))

    # -------------------------------------------------------------------------
    # 30. Multiple Unavailable Evidence Sources (Sample Claim Reproduction)
    # -------------------------------------------------------------------------
    def test_multiple_unavailable_evidence_sources(self):
        """Reproduce the sample claim: 6 MATCH, 4 INCONCLUSIVE (3 CV unexecuted + 1 policy validity unverified)."""
        findings = [
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW, "field_name": "Policy Number"},
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW, "field_name": "Claimant Name"},
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW, "field_name": "Vehicle Registration"},
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW, "field_name": "Incident Location"},
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW, "field_name": "Invoice Item: Bodywork and paint"},
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW, "field_name": "Invoice Item: Labor and misc"},
            {"comparison_status": STATUS_INCONCLUSIVE, "severity": SEVERITY_LOW, "field_name": "Policy Coverage Validity Window"},
            {
                "comparison_status": STATUS_INCONCLUSIVE,
                "severity": SEVERITY_LOW,
                "field_name": "Damage: Rear Bumper",
                "source_b": "Vehicle Photograph (Computer Vision)",
                "original_value_b": "Analysis not executed / failed",
                "evidence_references": {"reason": "vision_analysis_unavailable"},
            },
            {
                "comparison_status": STATUS_INCONCLUSIVE,
                "severity": SEVERITY_LOW,
                "field_name": "Damage: Trunk Hatch",
                "source_b": "Vehicle Photograph (Computer Vision)",
                "original_value_b": "Analysis not executed / failed",
                "evidence_references": {"reason": "vision_analysis_unavailable"},
            },
            {
                "comparison_status": STATUS_INCONCLUSIVE,
                "severity": SEVERITY_LOW,
                "field_name": "Damage: Right Tail Lamp Assembly",
                "source_b": "Vehicle Photograph (Computer Vision)",
                "original_value_b": "Analysis not executed / failed",
                "evidence_references": {"reason": "vision_analysis_unavailable"},
            },
        ]
        res = compute_verification_score_and_summary(findings)
        # Score: (6 * 1.0 + 4 * 0.5) / 10 = 8.0 / 10 = 80.0% (NOT 100%)
        self.assertEqual(res["consistency_score"], 80.0)
        self.assertEqual(res["evidence_coverage_percentage"], 60.0)
        self.assertEqual(res["inconclusive_count"], 4)
        self.assertEqual(res["cv_unevaluated_count"], 3)
        # Status MUST be REVIEW_REQUIRED (NOT CONSISTENT)
        self.assertEqual(res["overall_status"], OVERALL_REVIEW_REQUIRED)
        # Assessor recommendations must explain both CV missing and policy validity unconfirmed
        self.assertTrue(any("Computer Vision damage analysis was not executed or failed for 3" in r for r in res["recommendations"]))
        self.assertTrue(any("Policy validity coverage period could not be confirmed" in r for r in res["recommendations"]))
        self.assertTrue(any("Evidence coverage is limited" in r for r in res["recommendations"]))

    # -------------------------------------------------------------------------
    # 31. Genuine MISMATCH Findings
    # -------------------------------------------------------------------------
    def test_genuine_mismatch_findings(self):
        """Verify that genuine MISMATCH findings receive zero points, trigger penalties, and require review."""
        findings = [
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW, "field_name": "Policy Number"},
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW, "field_name": "Claimant Name"},
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW, "field_name": "Damage: Rear Bumper"},
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW, "field_name": "Damage: Tail Lamp"},
            {"comparison_status": STATUS_MISMATCH, "severity": SEVERITY_HIGH, "field_name": "Accident Date"},
        ]
        res = compute_verification_score_and_summary(findings)
        # (4 * 1.0 + 0.0) / 5 = 80.0% - 15.0 penalty = 65.0%
        self.assertEqual(res["consistency_score"], 65.0)
        self.assertEqual(res["mismatched_comparisons"], 1)
        self.assertEqual(res["overall_status"], OVERALL_REVIEW_REQUIRED)
        self.assertTrue(any("Direct factual discrepancies observed" in r for r in res["recommendations"]))

    # -------------------------------------------------------------------------
    # 32. Score and Overall Status Consistency Across Edge Cases
    # -------------------------------------------------------------------------
    def test_score_and_overall_status_consistency(self):
        """Verify mathematical consistency and logical harmony between score, coverage, and overall status."""
        # A claim with unexecuted CV damage cannot be CONSISTENT even with 10 matches
        many_matches_unexecuted_cv = [
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW, "field_name": f"Field {i}"}
            for i in range(10)
        ] + [
            {
                "comparison_status": STATUS_INCONCLUSIVE,
                "severity": SEVERITY_LOW,
                "field_name": "Damage: Bumper",
                "source_b": "Vehicle Photograph (Computer Vision)",
                "original_value_b": "Analysis not executed / failed",
                "evidence_references": {"reason": "vision_analysis_unavailable"},
            }
        ]
        res1 = compute_verification_score_and_summary(many_matches_unexecuted_cv)
        self.assertEqual(res1["overall_status"], OVERALL_REVIEW_REQUIRED)
        self.assertLess(res1["consistency_score"], 100.0)
        self.assertLess(res1["evidence_coverage_percentage"], 100.0)

        # Full match claim has 100% score and 100% coverage
        full_matches = [
            {"comparison_status": STATUS_MATCH, "severity": SEVERITY_LOW, "field_name": f"Field {i}"}
            for i in range(5)
        ]
        res2 = compute_verification_score_and_summary(full_matches)
        self.assertEqual(res2["overall_status"], OVERALL_CONSISTENT)
        self.assertEqual(res2["consistency_score"], 100.0)
        self.assertEqual(res2["evidence_coverage_percentage"], 100.0)


if __name__ == "__main__":
    unittest.main()
