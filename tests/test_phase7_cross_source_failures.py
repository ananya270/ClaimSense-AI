"""Comprehensive Automated Tests for Phase 7 Cross-Source Verification (Scenarios A through R).

Ensures robust verification, isolated claim evidence retrieval, resilient OCR consumption,
graceful handling of missing/corrupt evidence, YOLOv8 model fault tolerance, and cross-claim isolation.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch, MagicMock

from backend.app import create_app
from backend.config import Config
from backend.database.db import get_db_session, init_database
from backend.database.models import (
    Claim,
    ClaimImage,
    ClaimNLPAnalysis,
    ClaimVerificationRun,
    Document,
    ExtractedInformation,
    User,
    VehicleDamageAnalysis,
    VehicleDamageDetection,
    VerificationFinding,
)
from backend.services.verification import (
    ClaimVerificationService,
    VerificationPipelineError,
    OVERALL_CONSISTENT,
    OVERALL_INSUFFICIENT_EVIDENCE,
    OVERALL_REVIEW_REQUIRED,
    SEVERITY_CRITICAL,
    SEVERITY_HIGH,
    SEVERITY_LOW,
    SEVERITY_MEDIUM,
    STATUS_MATCH,
    STATUS_MISMATCH,
    STATUS_MISSING_IN_SOURCE,
    STATUS_NOT_PRESENT,
    STATUS_INCONCLUSIVE,
    normalize_amount,
    normalize_date,
    normalize_name,
    normalize_policy_num,
    normalize_vehicle_reg,
    compare_amounts,
    compare_dates,
    compare_names,
    compare_policy_numbers,
    compare_vehicle_registrations,
)


class TestPhase7CrossSourceFailures(unittest.TestCase):
    """Test suite covering Phase 7 verification scenarios A through R."""

    @classmethod
    def setUpClass(cls):
        cls.test_dir = tempfile.mkdtemp()
        cls.db_path = Path(cls.test_dir) / "test_p7_failures.db"
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
    # Scenario A: Complete valid claim with all evidence
    # -------------------------------------------------------------------------
    def test_scenario_a_complete_valid_claim_with_all_evidence(self):
        """Scenario A: Complete valid claim with policy, form, invoice, photo, NLP, and vision."""
        claim_id = "CLM-20261119-SCNA"
        now_utc = datetime.now(timezone.utc)

        with get_db_session() as db:
            c = Claim(
                claim_id=claim_id,
                claimant_name="Vikram Mehta",
                policy_number="POL-2024-1100",
                vehicle_number="MH-02-CD-5678",
                accident_date="2026-08-10",
                claim_description="Front bumper damaged when hitting pole at low speed.",
                status="SUBMITTED",
                created_at=now_utc,
            )
            db.add(c)

            # Add documents
            doc_p = Document(
                claim_id=claim_id,
                document_type="POLICY_DOCUMENT",
                file_path="uploads/pol.pdf",
                original_filename="policy.pdf",
                stored_filename="pol_1.pdf",
                file_extension="pdf",
                file_size=1024,
                created_at=now_utc,
            )
            doc_c = Document(
                claim_id=claim_id,
                document_type="CLAIM_FORM",
                file_path="uploads/claim.pdf",
                original_filename="claim_form.pdf",
                stored_filename="clm_1.pdf",
                file_extension="pdf",
                file_size=1024,
                created_at=now_utc,
            )
            doc_i = Document(
                claim_id=claim_id,
                document_type="INVOICE",
                file_path="uploads/inv.pdf",
                original_filename="invoice.pdf",
                stored_filename="inv_1.pdf",
                file_extension="pdf",
                file_size=1024,
                created_at=now_utc,
            )
            db.add_all([doc_p, doc_c, doc_i])

            # Add image
            img = ClaimImage(
                claim_id=claim_id,
                image_type="VEHICLE_ACCIDENT",
                file_path="uploads/car.jpg",
                original_filename="car.jpg",
                stored_filename="car_1.jpg",
                file_extension="jpg",
                file_size=2048,
                created_at=now_utc,
            )
            db.add(img)

            # Add OCR extractions
            ocr_items = [
                ("policy_number", "POL-2024-1100", "policy_document"),
                ("claimant_name", "Vikram Mehta", "policy_document"),
                ("vehicle_number", "MH 02 CD 5678", "policy_document"),
                ("policy_start_date", "2026-01-01", "policy_document"),
                ("policy_expiry_date", "2026-12-31", "policy_document"),
                ("policy_number", "POL-2024-1100", "claim_form"),
                ("claimant_name", "Vikram Mehta", "claim_form"),
                ("vehicle_number", "MH-02-CD-5678", "claim_form"),
                ("accident_date", "2026-08-10", "claim_form"),
                ("claim_amount", "15000", "claim_form"),
                ("repair_cost", "15000", "invoice"),
                ("vehicle_number", "MH-02-CD-5678", "invoice"),
                ("invoice_date", "2026-08-12", "invoice"),
            ]
            for fn, fv, src in ocr_items:
                db.add(ExtractedInformation(
                    claim_id=claim_id,
                    field_name=fn,
                    field_value=fv,
                    field_status="extracted",
                    source=src,
                    confidence_score=0.95,
                    created_at=now_utc,
                ))

            # Add NLP Analysis
            nlp = ClaimNLPAnalysis(
                claim_id=claim_id,
                original_narrative="Front bumper damaged when hitting pole at low speed.",
                extracted_entities=json.dumps([
                    {"text": "MH-02-CD-5678", "entity_type": "VEHICLE_REGISTRATION", "confidence": 0.95},
                    {"text": "2026-08-10", "entity_type": "DATE", "confidence": 0.90},
                ]),
                damage_descriptions=json.dumps([
                    {"part": "front bumper", "damage_type": "dent", "severity": "moderate"}
                ]),
                accident_type="COLLISION_FIXED_OBJECT",
                accident_type_confidence=0.92,
                cross_consistency_findings="[]",
                missing_information="[]",
                ambiguous_information="[]",
                nlp_engine_version="1.0.0",
                processing_status="completed",
                created_at=now_utc,
            )
            db.add(nlp)

            # Add Vision Analysis
            vis = VehicleDamageAnalysis(
                claim_id=claim_id,
                total_detections=1,
                damage_categories=json.dumps(["dent"]),
                highest_confidence=0.88,
                analysis_status="completed",
                created_at=now_utc,
            )
            db.add(vis)
            db.flush()

            det = VehicleDamageDetection(
                analysis_id=vis.id,
                detection_index=0,
                category="dent",
                confidence=0.88,
                bbox_x1=10.0,
                bbox_y1=10.0,
                bbox_x2=100.0,
                bbox_y2=100.0,
                location_region="front_bumper",
                created_at=now_utc,
            )
            db.add(det)
            db.commit()

        # Execute verification
        res = ClaimVerificationService.verify_claim(claim_id, force=True)
        self.assertEqual(res["claim_id"], claim_id)
        self.assertGreater(res["consistency_score"], 80.0)
        self.assertIn(res["overall_status"], [OVERALL_CONSISTENT, OVERALL_REVIEW_REQUIRED])
        self.assertGreaterEqual(res["matched_comparisons"], 4)
        self.assertEqual(res["mismatched_comparisons"], 0)

    # -------------------------------------------------------------------------
    # Scenario B: Missing policy document
    # -------------------------------------------------------------------------
    def test_scenario_b_missing_policy_document(self):
        """Scenario B: Missing policy document handled safely without crash."""
        claim_id = "CLM-20261119-SCNB"
        now_utc = datetime.now(timezone.utc)

        with get_db_session() as db:
            c = Claim(
                claim_id=claim_id,
                claimant_name="Amina Khan",
                policy_number="POL-MISS-001",
                vehicle_number="KA-01-XY-1234",
                accident_date="2026-07-20",
                claim_description="Scratched side door.",
                status="SUBMITTED",
                created_at=now_utc,
            )
            db.add(c)
            # Add only claim form OCR
            db.add(ExtractedInformation(
                claim_id=claim_id,
                field_name="policy_number",
                field_value="POL-MISS-001",
                source="claim_form",
                created_at=now_utc,
            ))
            db.commit()

        res = ClaimVerificationService.verify_claim(claim_id, force=True)
        self.assertEqual(res["claim_id"], claim_id)
        # Should record missing policy document / missing evidence without crash
        self.assertGreater(res["missing_evidence_count"], 0)
        self.assertIn("findings", res)

    # -------------------------------------------------------------------------
    # Scenario C: Missing claim form
    # -------------------------------------------------------------------------
    def test_scenario_c_missing_claim_form(self):
        """Scenario C: Missing claim form document handled gracefully."""
        claim_id = "CLM-20261119-SCNC"
        now_utc = datetime.now(timezone.utc)

        with get_db_session() as db:
            c = Claim(
                claim_id=claim_id,
                claimant_name="Rohan Verma",
                policy_number="POL-MISS-002",
                vehicle_number="DL-03-ZZ-9999",
                accident_date="2026-06-15",
                claim_description="Rear light cracked.",
                status="SUBMITTED",
                created_at=now_utc,
            )
            db.add(c)
            # Add only policy OCR
            db.add(ExtractedInformation(
                claim_id=claim_id,
                field_name="policy_number",
                field_value="POL-MISS-002",
                source="policy_document",
                created_at=now_utc,
            ))
            db.commit()

        res = ClaimVerificationService.verify_claim(claim_id, force=True)
        self.assertEqual(res["claim_id"], claim_id)
        self.assertIsInstance(res["findings"], list)

    # -------------------------------------------------------------------------
    # Scenario D: Missing invoice
    # -------------------------------------------------------------------------
    def test_scenario_d_missing_invoice(self):
        """Scenario D: Missing repair invoice does not mark a conflict for fields not expected."""
        claim_id = "CLM-20261119-SCND"
        now_utc = datetime.now(timezone.utc)

        with get_db_session() as db:
            c = Claim(
                claim_id=claim_id,
                claimant_name="Pooja Nair",
                policy_number="POL-MISS-003",
                vehicle_number="KL-07-AA-1111",
                accident_date="2026-05-10",
                claim_description="Mirror damaged.",
                status="SUBMITTED",
                created_at=now_utc,
            )
            db.add(c)
            db.add(ExtractedInformation(
                claim_id=claim_id,
                field_name="policy_number",
                field_value="POL-MISS-003",
                source="policy_document",
                created_at=now_utc,
            ))
            db.add(ExtractedInformation(
                claim_id=claim_id,
                field_name="policy_number",
                field_value="POL-MISS-003",
                source="claim_form",
                created_at=now_utc,
            ))
            db.commit()

        res = ClaimVerificationService.verify_claim(claim_id, force=True)
        self.assertEqual(res["claim_id"], claim_id)
        # Policy number should match between policy and claim form
        pol_matches = [f for f in res["findings"] if f["field_name"] == "Policy Number" and f["comparison_status"] == STATUS_MATCH]
        self.assertTrue(len(pol_matches) > 0)

    # -------------------------------------------------------------------------
    # Scenario E: Missing vehicle photograph
    # -------------------------------------------------------------------------
    def test_scenario_e_missing_vehicle_photograph(self):
        """Scenario E: Missing vehicle photograph leaves vision findings inconclusive without pipeline failure."""
        claim_id = "CLM-20261119-SCNE"
        now_utc = datetime.now(timezone.utc)

        with get_db_session() as db:
            c = Claim(
                claim_id=claim_id,
                claimant_name="Devendra Joshi",
                policy_number="POL-MISS-004",
                vehicle_number="GJ-01-MM-4444",
                accident_date="2026-04-01",
                claim_description="Dent on right door.",
                status="SUBMITTED",
                created_at=now_utc,
            )
            db.add(c)
            db.commit()

        res = ClaimVerificationService.verify_claim(claim_id, force=True)
        self.assertEqual(res["claim_id"], claim_id)
        # Vision finding should indicate unavailable or inconclusive
        vis_findings = [f for f in res["findings"] if "Visual" in f["field_name"] or "Vision" in f["field_name"]]
        for vf in vis_findings:
            self.assertIn(vf["comparison_status"], [STATUS_INCONCLUSIVE, STATUS_MISSING_IN_SOURCE, STATUS_NOT_PRESENT])

    # -------------------------------------------------------------------------
    # Scenario F: Invalid or corrupted PDF
    # -------------------------------------------------------------------------
    def test_scenario_f_invalid_or_corrupted_pdf(self):
        """Scenario F: Extraction records with error or failure status do not crash Phase 7."""
        claim_id = "CLM-20261119-SCNF"
        now_utc = datetime.now(timezone.utc)

        with get_db_session() as db:
            c = Claim(
                claim_id=claim_id,
                claimant_name="Sneha Rao",
                policy_number="POL-CORRUPT-PDF",
                vehicle_number="MH-12-GG-1212",
                accident_date="2026-03-15",
                claim_description="Windshield shattered.",
                status="SUBMITTED",
                created_at=now_utc,
            )
            db.add(c)
            # Extracted row marked failed with error message
            db.add(ExtractedInformation(
                claim_id=claim_id,
                field_name="policy_number",
                field_value=None,
                field_status="failed",
                error_message="Corrupted PDF bytes or OCR failure",
                source="policy_document",
                created_at=now_utc,
            ))
            db.commit()

        res = ClaimVerificationService.verify_claim(claim_id, force=True)
        self.assertEqual(res["claim_id"], claim_id)
        self.assertIn(res["overall_status"], [OVERALL_INSUFFICIENT_EVIDENCE, OVERALL_REVIEW_REQUIRED, OVERALL_CONSISTENT])

    # -------------------------------------------------------------------------
    # Scenario G: Invalid image file
    # -------------------------------------------------------------------------
    def test_scenario_g_invalid_image_file(self):
        """Scenario G: Corrupted image file handled safely without crashing the verification run."""
        claim_id = "CLM-20261119-SCNG"
        now_utc = datetime.now(timezone.utc)

        with get_db_session() as db:
            c = Claim(
                claim_id=claim_id,
                claimant_name="Tarun Das",
                policy_number="POL-BAD-IMG",
                vehicle_number="WB-02-JJ-5555",
                accident_date="2026-02-20",
                claim_description="Front bumper damage.",
                status="SUBMITTED",
                created_at=now_utc,
            )
            db.add(c)
            # Corrupted image file entry
            img = ClaimImage(
                claim_id=claim_id,
                image_type="VEHICLE_ACCIDENT",
                file_path="uploads/corrupt.jpg",
                original_filename="corrupt.jpg",
                stored_filename="corrupt_1.jpg",
                file_extension="jpg",
                file_size=0,
                created_at=now_utc,
            )
            db.add(img)
            db.commit()

        # Mock vision processing failure
        with patch("backend.services.vision.process_claim_damage_detection", return_value={"success": False, "message": "Corrupted image file"}):
            res = ClaimVerificationService.verify_claim(claim_id, force=True)
            self.assertEqual(res["claim_id"], claim_id)
            self.assertIn("findings", res)

    # -------------------------------------------------------------------------
    # Scenario H: Synthetic vehicle image
    # -------------------------------------------------------------------------
    def test_scenario_h_synthetic_vehicle_image(self):
        """Scenario H: Synthetic image rejected by forensic filter does not produce false positive corroboration."""
        claim_id = "CLM-20261119-SCNH"
        now_utc = datetime.now(timezone.utc)

        with get_db_session() as db:
            c = Claim(
                claim_id=claim_id,
                claimant_name="Gaurav Singh",
                policy_number="POL-SYNTH-001",
                vehicle_number="HR-26-SS-7777",
                accident_date="2026-01-10",
                claim_description="Extensive car crash.",
                status="SUBMITTED",
                created_at=now_utc,
            )
            db.add(c)
            # Image flagged as synthetic graphic
            img = ClaimImage(
                claim_id=claim_id,
                image_type="VEHICLE_ACCIDENT_SYNTHETIC",
                file_path="uploads/synthetic.png",
                original_filename="synthetic.png",
                stored_filename="syn_1.png",
                file_extension="png",
                file_size=4096,
                created_at=now_utc,
            )
            db.add(img)
            # Add NLP reported damages
            nlp = ClaimNLPAnalysis(
                claim_id=claim_id,
                original_narrative="Extensive car crash.",
                extracted_entities="[]",
                damage_descriptions=json.dumps([{"part": "hood", "damage_type": "crush"}]),
                accident_type="COLLISION",
                accident_type_confidence=0.85,
                cross_consistency_findings="[]",
                missing_information="[]",
                ambiguous_information="[]",
                nlp_engine_version="1.0.0",
                processing_status="completed",
                created_at=now_utc,
            )
            db.add(nlp)
            db.commit()

        res = ClaimVerificationService.verify_claim(claim_id, force=True)
        # Without genuine accident photo, visual corroboration must NOT falsely claim MATCH
        vis_matches = [f for f in res["findings"] if "Visual" in f["field_name"] and f["comparison_status"] == STATUS_MATCH]
        self.assertEqual(len(vis_matches), 0)

    # -------------------------------------------------------------------------
    # Scenario I: Valid replacement vehicle photograph
    # -------------------------------------------------------------------------
    def test_scenario_i_valid_replacement_vehicle_photograph(self):
        """Scenario I: Replacement photograph correctly linked to claim and verified."""
        claim_id = "CLM-20261119-SCNI"
        now_utc = datetime.now(timezone.utc)

        with get_db_session() as db:
            c = Claim(
                claim_id=claim_id,
                claimant_name="Meera Iyer",
                policy_number="POL-REPLACE-001",
                vehicle_number="TN-09-RR-8888",
                accident_date="2026-02-15",
                claim_description="Scratched rear bumper.",
                status="SUBMITTED",
                created_at=now_utc,
            )
            db.add(c)
            # Replacement image uploaded
            img = ClaimImage(
                claim_id=claim_id,
                image_type="VEHICLE_ACCIDENT_REPLACEMENT",
                file_path="uploads/replacement_bumper.jpg",
                original_filename="replacement_bumper.jpg",
                stored_filename="rep_1.jpg",
                file_extension="jpg",
                file_size=5120,
                created_at=now_utc,
            )
            db.add(img)
            # Vision detection associated with the replacement image
            vis = VehicleDamageAnalysis(
                claim_id=claim_id,
                total_detections=1,
                damage_categories=json.dumps(["scratch"]),
                highest_confidence=0.91,
                analysis_status="completed",
                created_at=now_utc,
            )
            db.add(vis)
            db.flush()

            det = VehicleDamageDetection(
                analysis_id=vis.id,
                detection_index=0,
                category="scratch",
                confidence=0.91,
                bbox_x1=20.0,
                bbox_y1=20.0,
                bbox_x2=120.0,
                bbox_y2=120.0,
                location_region="rear_bumper",
                created_at=now_utc,
            )
            db.add(det)

            # NLP reported damage
            nlp = ClaimNLPAnalysis(
                claim_id=claim_id,
                original_narrative="Scratched rear bumper.",
                extracted_entities="[]",
                damage_descriptions=json.dumps([{"part": "rear bumper", "damage_type": "scratch"}]),
                accident_type="SCRATCH",
                accident_type_confidence=0.88,
                cross_consistency_findings="[]",
                missing_information="[]",
                ambiguous_information="[]",
                nlp_engine_version="1.0.0",
                processing_status="completed",
                created_at=now_utc,
            )
            db.add(nlp)
            db.commit()

        res = ClaimVerificationService.verify_claim(claim_id, force=True)
        self.assertEqual(res["claim_id"], claim_id)
        # Should detect corroborated damage
        corrob_findings = [f for f in res["findings"] if "Damage:" in f["field_name"] and f["comparison_status"] == STATUS_MATCH]
        self.assertTrue(len(corrob_findings) > 0)

    # -------------------------------------------------------------------------
    # Scenario J: OCR extraction returning null values
    # -------------------------------------------------------------------------
    def test_scenario_j_ocr_extraction_returning_null_values(self):
        """Scenario J: Null OCR extraction values normalized safely without throwing exceptions."""
        claim_id = "CLM-20261119-SCNJ"
        now_utc = datetime.now(timezone.utc)

        with get_db_session() as db:
            c = Claim(
                claim_id=claim_id,
                claimant_name="Nitin Gadkari",
                policy_number="POL-NULL-001",
                vehicle_number="MH-01-NN-0001",
                accident_date="2026-03-01",
                claim_description="Front grill dent.",
                status="SUBMITTED",
                created_at=now_utc,
            )
            db.add(c)
            # Add OCR rows with None values
            db.add(ExtractedInformation(
                claim_id=claim_id,
                field_name="policy_number",
                field_value=None,
                source="policy_document",
                created_at=now_utc,
            ))
            db.add(ExtractedInformation(
                claim_id=claim_id,
                field_name="claimant_name",
                field_value="",
                source="claim_form",
                created_at=now_utc,
            ))
            db.add(ExtractedInformation(
                claim_id=claim_id,
                field_name="claim_amount",
                field_value=None,
                source="invoice",
                created_at=now_utc,
            ))
            db.commit()

        # Must execute without AttributeError or TypeError
        res = ClaimVerificationService.verify_claim(claim_id, force=True)
        self.assertEqual(res["claim_id"], claim_id)
        self.assertIsInstance(res["findings"], list)

    # -------------------------------------------------------------------------
    # Scenario K: Different date formats
    # -------------------------------------------------------------------------
    def test_scenario_k_different_date_formats(self):
        """Scenario K: Various date formats (YYYY-MM-DD, DD/MM/YYYY, MM-DD-YYYY) normalized and matched."""
        # Unit test normalize_date
        d1 = normalize_date("2026-08-15")
        d2 = normalize_date("15/08/2026")
        d3 = normalize_date("15-08-2026")
        d4 = normalize_date("August 15, 2026")
        self.assertEqual(d1, d2)
        self.assertEqual(d1, d3)
        self.assertEqual(d1, d4)

        # Integration test across policy and claim form
        claim_id = "CLM-20261119-SCNK"
        now_utc = datetime.now(timezone.utc)

        with get_db_session() as db:
            c = Claim(
                claim_id=claim_id,
                claimant_name="Alok Nath",
                policy_number="POL-DATE-001",
                vehicle_number="DL-08-AA-1234",
                accident_date="15/08/2026",
                claim_description="Dent on door.",
                status="SUBMITTED",
                created_at=now_utc,
            )
            db.add(c)
            db.add(ExtractedInformation(
                claim_id=claim_id,
                field_name="accident_date",
                field_value="2026-08-15",
                source="claim_form",
                created_at=now_utc,
            ))
            db.commit()

        res = ClaimVerificationService.verify_claim(claim_id, force=True)
        acc_matches = [f for f in res["findings"] if f["field_name"] == "Accident Date" and f["comparison_status"] == STATUS_MATCH]
        self.assertTrue(len(acc_matches) > 0)

    # -------------------------------------------------------------------------
    # Scenario L: Conflicting vehicle registration numbers
    # -------------------------------------------------------------------------
    def test_scenario_l_conflicting_vehicle_registration_numbers(self):
        """Scenario L: Conflicting vehicle registration numbers result in MISMATCH with HIGH severity."""
        claim_id = "CLM-20261119-SCNL"
        now_utc = datetime.now(timezone.utc)

        with get_db_session() as db:
            c = Claim(
                claim_id=claim_id,
                claimant_name="Sanjay Dutt",
                policy_number="POL-CONFLICT-REG",
                vehicle_number="MH-01-AB-1111",
                accident_date="2026-04-10",
                claim_description="Fender hit.",
                status="SUBMITTED",
                created_at=now_utc,
            )
            db.add(c)
            db.add(ExtractedInformation(
                claim_id=claim_id,
                field_name="vehicle_number",
                field_value="KA-05-XY-9999",  # Conflicting registration
                source="claim_form",
                created_at=now_utc,
            ))
            db.commit()

        res = ClaimVerificationService.verify_claim(claim_id, force=True)
        veh_mismatches = [f for f in res["findings"] if "Vehicle Registration" in f["field_name"] and f["comparison_status"] == STATUS_MISMATCH]
        self.assertTrue(len(veh_mismatches) > 0)
        self.assertEqual(veh_mismatches[0]["severity"], SEVERITY_HIGH)

    # -------------------------------------------------------------------------
    # Scenario M: Conflicting accident dates
    # -------------------------------------------------------------------------
    def test_scenario_m_conflicting_accident_dates(self):
        """Scenario M: Conflicting accident dates produce MISMATCH with HIGH severity."""
        claim_id = "CLM-20261119-SCNM"
        now_utc = datetime.now(timezone.utc)

        with get_db_session() as db:
            c = Claim(
                claim_id=claim_id,
                claimant_name="Kavita Krishnan",
                policy_number="POL-CONFLICT-DATE",
                vehicle_number="UP-16-CC-2222",
                accident_date="2026-05-01",
                claim_description="Side collision.",
                status="SUBMITTED",
                created_at=now_utc,
            )
            db.add(c)
            db.add(ExtractedInformation(
                claim_id=claim_id,
                field_name="accident_date",
                field_value="2026-06-15",  # Different date
                source="claim_form",
                created_at=now_utc,
            ))
            db.commit()

        res = ClaimVerificationService.verify_claim(claim_id, force=True)
        date_mismatches = [f for f in res["findings"] if f["field_name"] == "Accident Date" and f["comparison_status"] == STATUS_MISMATCH]
        self.assertTrue(len(date_mismatches) > 0)
        self.assertEqual(date_mismatches[0]["severity"], SEVERITY_HIGH)

    # -------------------------------------------------------------------------
    # Scenario N: Missing YOLOv8 model or inference failure
    # -------------------------------------------------------------------------
    def test_scenario_n_missing_yolov8_model_or_inference_failure(self):
        """Scenario N: YOLOv8 model missing or inference exception handled without failing document checks."""
        claim_id = "CLM-20261119-SCNN"
        now_utc = datetime.now(timezone.utc)

        with get_db_session() as db:
            c = Claim(
                claim_id=claim_id,
                claimant_name="Anil Kapoor",
                policy_number="POL-YOLO-FAIL",
                vehicle_number="MH-02-AK-2424",
                accident_date="2026-07-04",
                claim_description="Scratched bumper in parking lot.",
                status="SUBMITTED",
                created_at=now_utc,
            )
            db.add(c)
            img = ClaimImage(
                claim_id=claim_id,
                image_type="VEHICLE_ACCIDENT",
                file_path="uploads/car_yolo_test.jpg",
                original_filename="car_yolo_test.jpg",
                stored_filename="car_yolo_1.jpg",
                file_extension="jpg",
                file_size=2048,
                created_at=now_utc,
            )
            db.add(img)
            # Document OCR matching
            db.add(ExtractedInformation(
                claim_id=claim_id,
                field_name="policy_number",
                field_value="POL-YOLO-FAIL",
                source="policy_document",
                created_at=now_utc,
            ))
            db.add(ExtractedInformation(
                claim_id=claim_id,
                field_name="policy_number",
                field_value="POL-YOLO-FAIL",
                source="claim_form",
                created_at=now_utc,
            ))
            db.commit()

        # Mock YOLOv8 to raise RuntimeError
        with patch("backend.services.vision.process_claim_damage_detection", side_effect=RuntimeError("YOLOv8 weights file not accessible")):
            res = ClaimVerificationService.verify_claim(claim_id, force=True)
            self.assertEqual(res["claim_id"], claim_id)
            # Document comparison must still succeed!
            pol_matches = [f for f in res["findings"] if f["field_name"] == "Policy Number" and f["comparison_status"] == STATUS_MATCH]
            self.assertTrue(len(pol_matches) > 0)

    # -------------------------------------------------------------------------
    # Scenario O: Multiple claims sharing the same policy number
    # -------------------------------------------------------------------------
    def test_scenario_o_multiple_claims_sharing_same_policy_number(self):
        """Scenario O: Ensure evidence from one claim never leaks into another sharing the same policy."""
        claim_1_id = "CLM-20261119-SHR1"
        claim_2_id = "CLM-20261119-SHR2"
        shared_policy = "POL-SHARED-7777"
        now_utc = datetime.now(timezone.utc)

        with get_db_session() as db:
            c1 = Claim(
                claim_id=claim_1_id,
                claimant_name="Claimant Alpha",
                policy_number=shared_policy,
                vehicle_number="MH-01-AA-0001",
                accident_date="2026-01-01",
                claim_description="Front collision Alpha.",
                status="SUBMITTED",
                created_at=now_utc,
            )
            c2 = Claim(
                claim_id=claim_2_id,
                claimant_name="Claimant Beta",
                policy_number=shared_policy,
                vehicle_number="DL-02-BB-0002",
                accident_date="2026-06-01",
                claim_description="Rear dent Beta.",
                status="SUBMITTED",
                created_at=now_utc,
            )
            db.add_all([c1, c2])

            # Claim 1 OCR
            db.add(ExtractedInformation(
                claim_id=claim_1_id,
                field_name="vehicle_number",
                field_value="MH-01-AA-0001",
                source="claim_form",
                created_at=now_utc,
            ))
            # Claim 2 OCR
            db.add(ExtractedInformation(
                claim_id=claim_2_id,
                field_name="vehicle_number",
                field_value="DL-02-BB-0002",
                source="claim_form",
                created_at=now_utc,
            ))
            db.commit()

        res1 = ClaimVerificationService.verify_claim(claim_1_id, force=True)
        res2 = ClaimVerificationService.verify_claim(claim_2_id, force=True)

        self.assertEqual(res1["claim_id"], claim_1_id)
        self.assertEqual(res2["claim_id"], claim_2_id)

        # Claim 1 findings must not mention Beta or DL-02-BB-0002
        for f in res1["findings"]:
            self.assertNotIn("Claimant Beta", str(f.get("original_value_a", "")))
            self.assertNotIn("Claimant Beta", str(f.get("original_value_b", "")))
            self.assertNotIn("DL-02-BB-0002", str(f.get("original_value_a", "")))
            self.assertNotIn("DL-02-BB-0002", str(f.get("original_value_b", "")))

        # Claim 2 findings must not mention Alpha or MH-01-AA-0001
        for f in res2["findings"]:
            self.assertNotIn("Claimant Alpha", str(f.get("original_value_a", "")))
            self.assertNotIn("Claimant Alpha", str(f.get("original_value_b", "")))
            self.assertNotIn("MH-01-AA-0001", str(f.get("original_value_a", "")))
            self.assertNotIn("MH-01-AA-0001", str(f.get("original_value_b", "")))

    # -------------------------------------------------------------------------
    # Scenario P: Claim ID referencing nonexistent evidence / nonexistent claim
    # -------------------------------------------------------------------------
    def test_scenario_p_nonexistent_claim_and_nonexistent_evidence(self):
        """Scenario P: Nonexistent claim raises VerificationPipelineError with 404 CLAIM_NOT_FOUND."""
        nonexistent_id = "CLM-20261119-NONX"
        with self.assertRaises(VerificationPipelineError) as ctx:
            ClaimVerificationService.verify_claim(nonexistent_id, force=True)

        err_dict = ctx.exception.to_dict()
        self.assertEqual(err_dict["error_code"], "CLAIM_NOT_FOUND")
        self.assertEqual(err_dict["stage"], "evidence_retrieval")

    # -------------------------------------------------------------------------
    # Scenario Q: Partial pipeline failure
    # -------------------------------------------------------------------------
    def test_scenario_q_partial_pipeline_failure(self):
        """Scenario Q: Individual field comparison exceptions do not abort overall verification."""
        claim_id = "CLM-20261119-SCNQ"
        now_utc = datetime.now(timezone.utc)

        with get_db_session() as db:
            c = Claim(
                claim_id=claim_id,
                claimant_name="Sunita Williams",
                policy_number="POL-PARTIAL-001",
                vehicle_number="KA-04-SS-1111",
                accident_date="2026-04-12",
                claim_description="Front damage.",
                status="SUBMITTED",
                created_at=now_utc,
            )
            db.add(c)
            # Normal OCR
            db.add(ExtractedInformation(
                claim_id=claim_id,
                field_name="policy_number",
                field_value="POL-PARTIAL-001",
                source="policy_document",
                created_at=now_utc,
            ))
            db.add(ExtractedInformation(
                claim_id=claim_id,
                field_name="policy_number",
                field_value="POL-PARTIAL-001",
                source="claim_form",
                created_at=now_utc,
            ))
            db.commit()

        # Mock compare_names to simulate an unhandled exception inside a single comparison
        with patch("backend.services.verification.service.compare_names", side_effect=ValueError("Unexpected name parsing failure")):
            res = ClaimVerificationService.verify_claim(claim_id, force=True)
            self.assertEqual(res["claim_id"], claim_id)
            # Other comparisons (like policy number) should still succeed!
            pol_matches = [f for f in res["findings"] if f["field_name"] == "Policy Number" and f["comparison_status"] == STATUS_MATCH]
            self.assertTrue(len(pol_matches) > 0)

    # -------------------------------------------------------------------------
    # Scenario R: Repeated Run Verification requests (idempotency vs force)
    # -------------------------------------------------------------------------
    def test_scenario_r_repeated_run_verification_requests(self):
        """Scenario R: Repeated calls without force reuse existing run; calls with force re-execute cleanly."""
        claim_id = "CLM-20261119-SCNR"
        now_utc = datetime.now(timezone.utc)

        with get_db_session() as db:
            c = Claim(
                claim_id=claim_id,
                claimant_name="Rajiv Gandhi",
                policy_number="POL-REPEAT-001",
                vehicle_number="DL-01-RR-9999",
                accident_date="2026-05-20",
                claim_description="Scratched rear bumper.",
                status="SUBMITTED",
                created_at=now_utc,
            )
            db.add(c)
            db.commit()

        # First execution (force=True)
        run1 = ClaimVerificationService.verify_claim(claim_id, force=True)
        run_id_1 = run1["run_id"]
        self.assertIsNotNone(run_id_1)

        # Second execution without force -> should reuse existing run
        run2 = ClaimVerificationService.verify_claim(claim_id, force=False)
        self.assertEqual(run2["run_id"], run_id_1)

        # Third execution with force=True -> creates a fresh run with new run_id
        run3 = ClaimVerificationService.verify_claim(claim_id, force=True)
        self.assertNotEqual(run3["run_id"], run_id_1)


if __name__ == "__main__":
    unittest.main()
