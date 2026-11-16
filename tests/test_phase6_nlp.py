"""Unit and Integration Tests for Phase 6: NLP Claim Narrative Analysis."""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timezone

from backend.app import create_app
from backend.config import Config
from backend.database.db import init_database, get_db_session
from backend.database.models import Claim, ExtractedInformation, ClaimNLPAnalysis
from backend.services.nlp import (
    ClaimNLPService,
    normalize_text,
    segment_sentences,
    extract_keywords_and_phrases,
    extract_temporal_expressions,
    extract_entities,
    extract_events,
    reconstruct_chronology,
    classify_accident_type,
    extract_reported_damages,
    cross_check_consistency,
)
from backend.services.receipt import generate_document_intelligence_report_pdf


class TestPhase6NLP(unittest.TestCase):
    """Test suite for Phase 6 NLP Analysis, Chronology, and Cross-Source Consistency."""

    @classmethod
    def setUpClass(cls):
        cls.test_dir = tempfile.mkdtemp()
        cls.db_path = Path(cls.test_dir) / "test_phase6.db"
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

        cls.app = create_app(CustomConfig)
        cls.client = cls.app.test_client()

        with cls.app.app_context():
            init_database(CustomConfig.SQLALCHEMY_DATABASE_URI)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.test_dir, ignore_errors=True)

    def test_text_preprocessing_and_normalization(self):
        """Verify text normalization, contraction expansion, and whitespace standardization."""
        raw = "While  halting at an   intersection signal on MG Road, wasn't able to move. Vehicle didn't stop."
        normalized = normalize_text(raw)
        self.assertIn("was not", normalized)
        self.assertIn("did not", normalized)
        self.assertNotIn("  ", normalized)

    def test_sentence_segmentation_with_abbreviations(self):
        """Verify sentence segmentation correctly protects abbreviations like Mr. and No."""
        text = "The driver Mr. Sharma was driving on MG Road. Vehicle No. 4052 was halted at 10:30 a.m. at the signal. Damage was observed."
        sentences = segment_sentences(text)
        self.assertEqual(len(sentences), 3)
        self.assertIn("Mr. Sharma", sentences[0])
        self.assertIn("Vehicle No. 4052", sentences[1])
        self.assertIn("Damage was observed.", sentences[2])

    def test_entity_extraction(self):
        """Verify extraction of locations, roads, vehicle types, parties, and registrations."""
        narrative = "While halting at an intersection signal on MG Road, vehicle was rear-ended by a commercial pickup truck."
        entities = extract_entities(narrative, claimant_name_hint="Rajesh Sharma")
        types = [e["entity_type"] for e in entities]
        texts = [e["text"] for e in entities]

        self.assertIn("ROAD_INTERSECTION", types)
        self.assertIn("LOCATION", types)
        self.assertIn("OTHER_PARTY", types)
        self.assertIn("VEHICLE", types)

        # Check specific extracted spans
        self.assertTrue(any("MG Road" in t for t in texts))
        self.assertTrue(any("commercial pickup truck" in t for t in texts))

    def test_explicit_registration_and_date_extraction(self):
        """Verify extraction of explicit vehicle registration plates and calendar dates."""
        text = "On 2026-09-28 at 10:30 AM, vehicle MH-12-DE-4052 was struck on Ring Road."
        entities = extract_entities(text)
        types = [e["entity_type"] for e in entities]
        self.assertIn("VEHICLE_REGISTRATION", types)
        self.assertIn("ACCIDENT_DATE", types)
        self.assertIn("ACCIDENT_TIME", types)

    def test_accident_event_extraction(self):
        """Verify structured extraction of maneuver, collision, and damage events."""
        sentences = [
            "While halting at an intersection signal on MG Road, vehicle was rear-ended by a commercial pickup truck.",
            "Damage observed on the rear bumper, trunk hatch, and right tail lamp assembly."
        ]
        text = " ".join(sentences)
        events = extract_events(text, sentences)
        ev_types = [ev["event_type"] for ev in events]

        self.assertIn("MANEUVER_OR_STOP", ev_types)
        self.assertIn("COLLISION", ev_types)
        self.assertIn("DAMAGE_SUSTAINED", ev_types)

    def test_chronological_reconstruction(self):
        """Verify that events are sequenced chronologically with phase indicators."""
        sentences = [
            "While halting at an intersection signal on MG Road, vehicle was rear-ended by a commercial pickup truck.",
            "Damage observed on the rear bumper, trunk hatch, and right tail lamp assembly."
        ]
        text = " ".join(sentences)
        events = extract_events(text, sentences)
        chronology = reconstruct_chronology(events, sentences, raw_text=text)

        self.assertEqual(chronology["ordering_type"], "narrative_sequence")
        self.assertFalse(chronology["explicit_timestamps_present"])
        self.assertGreaterEqual(chronology["total_events"], 3)
        self.assertTrue(any("Exact accident time" in m for m in chronology["missing_temporal_info"]))

    def test_accident_type_classification(self):
        """Verify accurate rule-based classification across different collision scenarios."""
        # 1. Rear-end
        c1 = classify_accident_type("Vehicle was rear-ended at a signal by a truck.")
        self.assertEqual(c1["accident_type"], "Rear-end collision")
        self.assertGreaterEqual(c1["confidence"], 0.85)

        # 2. Head-on
        c2 = classify_accident_type("A frontal head-on collision occurred with an oncoming vehicle.")
        self.assertEqual(c2["accident_type"], "Head-on collision")

        # 3. Side-impact / T-bone
        c3 = classify_accident_type("Vehicle was sideswiped and T-boned on the driver side.")
        self.assertEqual(c3["accident_type"], "Side-impact collision")

        # 4. Single-vehicle
        c4 = classify_accident_type("Vehicle lost control on wet surface and hit a barrier.")
        self.assertEqual(c4["accident_type"], "Single-vehicle accident")

        # 5. Rollover
        c5 = classify_accident_type("Car skidded off the embankment and rolled over onto its roof.")
        self.assertEqual(c5["accident_type"], "Rollover")

        # 6. Unknown / Empty
        c6 = classify_accident_type("")
        self.assertEqual(c6["accident_type"], "UNKNOWN")

    def test_damage_description_extraction(self):
        """Verify extraction of claimant-reported damage items and spatial regions."""
        text = "Damage observed on the rear bumper, trunk hatch, and right tail lamp assembly."
        sentences = segment_sentences(text)
        damages = extract_reported_damages(text, sentences)

        components = [d["component"] for d in damages]
        self.assertIn("Rear Bumper", components)
        self.assertIn("Trunk Hatch", components)
        self.assertIn("Right Tail Lamp Assembly", components)

        for d in damages:
            self.assertEqual(d["evidence_type"], "Claimant-Reported Narrative (Non-Visual)")
            self.assertIn(d["reported_condition"], ["Damaged", "Dented", "Broken / Shattered", "Scratched", "Cracked"])

    def test_cross_source_consistency(self):
        """Verify cross-source comparison logic between narrative and structured document records."""
        entities = [
            {"entity_type": "ROAD_INTERSECTION", "text": "MG Road"},
            {"entity_type": "LOCATION", "text": "intersection signal"},
        ]
        classification = {"accident_type": "Rear-end collision", "confidence": 0.90}
        reported_damages = [
            {"component": "Rear Bumper", "spatial_region": "rear"},
            {"component": "Right Tail Lamp Assembly", "spatial_region": "rear_right"},
        ]
        extracted_doc_rows = [
            {"field_name": "accident_date", "field_value": "2026-09-28", "source": "policy_document", "source_filename": "policy.pdf"},
            {"field_name": "vehicle_number", "field_value": "MH-12-DE-4052", "source": "policy_document", "source_filename": "policy.pdf"},
            {"field_name": "claimant_name", "field_value": "Rajesh Sharma", "source": "claim_form", "source_filename": "claim_form.pdf"},
            {"field_name": "incident_description", "field_value": "Rear-end collision at MG Road intersection.", "source": "claim_form", "source_filename": "claim_form.pdf"},
            {"field_name": "repair_description", "field_value": "Tail lamp replacement and bumper repair", "source": "invoice_document", "source_filename": "estimate.pdf"},
        ]
        claim_rec = {"claim_id": "CLM-TEST-0001", "claimant_name": "Rajesh Sharma"}

        consistency = cross_check_consistency(
            claim_id="CLM-TEST-0001",
            nlp_entities=entities,
            nlp_classification=classification,
            reported_damages=reported_damages,
            extracted_doc_rows=extracted_doc_rows,
            claim_record=claim_rec,
        )

        self.assertGreaterEqual(consistency["total_checks"], 4)
        statuses = [c["status"] for c in consistency["comparisons"]]
        self.assertIn("MATCH", statuses)
        self.assertIn("MISSING_IN_NARRATIVE", statuses)

    def test_database_persistence_and_querying(self):
        """Verify ClaimNLPAnalysis entity persistence in SQLite database."""
        claim_id = "CLM-TEST-NLP-1"
        now_utc = datetime.now(timezone.utc)

        with get_db_session() as db:
            claim = Claim(
                claim_id=claim_id,
                claimant_name="Aarav Patel",
                policy_number="POL-2026-111",
                vehicle_number="GJ-01-AB-1234",
                accident_date="2026-10-15",
                claim_description="While halting at an intersection signal on MG Road, vehicle was rear-ended by a truck.",
                status="SUBMITTED",
                created_at=now_utc,
            )
            db.add(claim)
            db.flush()

            analysis_rec = ClaimNLPAnalysis(
                claim_id=claim_id,
                original_narrative=claim.claim_description,
                normalized_narrative=normalize_text(claim.claim_description),
                accident_type="Rear-end collision",
                accident_type_confidence=0.92,
                classification_method="Linguistic Pattern Matching",
                classification_supporting_text="Vehicle was rear-ended by a truck.",
                extracted_entities=json.dumps([{"entity_type": "LOCATION", "text": "MG Road"}]),
                events_timeline=json.dumps([{"step_number": 1, "description": "Halted at signal"}]),
                damage_descriptions=json.dumps([{"component": "Rear Bumper", "reported_condition": "Damaged"}]),
                cross_consistency_findings=json.dumps({"consistency_score": 80.0}),
                missing_information=json.dumps(["Exact time omitted"]),
                ambiguous_information=json.dumps([]),
                nlp_engine_version="1.0.0",
                processing_status="completed",
                processing_time_ms=12.5,
                created_at=now_utc,
                updated_at=now_utc,
            )
            db.add(analysis_rec)
            db.commit()

        # Query back and verify
        with get_db_session() as db:
            c = db.query(Claim).filter_by(claim_id=claim_id).first()
            self.assertIsNotNone(c)
            d = c.to_dict()
            self.assertIsNotNone(d.get("nlp_analysis"))
            nlp_d = d["nlp_analysis"]
            self.assertEqual(nlp_d["accident_type"], "Rear-end collision")
            self.assertEqual(len(nlp_d["entities"]), 1)
            self.assertEqual(len(nlp_d["timeline"]), 1)

    def test_api_endpoints(self):
        """Verify Phase 6 backend REST endpoints for NLP analysis, entities, and chronology."""
        claim_id = "CLM-20261116-TEST"
        now_utc = datetime.now(timezone.utc)

        with get_db_session() as db:
            claim = Claim(
                claim_id=claim_id,
                claimant_name="Vikram Singh",
                policy_number="POL-2026-999",
                vehicle_number="KA-03-CD-5678",
                accident_date="2026-11-01",
                claim_description="While halting at an intersection signal on MG Road, vehicle was rear-ended by a commercial pickup truck. Damage observed on the rear bumper.",
                status="SUBMITTED",
                created_at=now_utc,
            )
            db.add(claim)
            db.commit()

        # Simulate authenticated admin session
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["username"] = "admin"
            sess["role"] = "admin"

        # 1. Trigger NLP Analysis
        post_res = self.client.post(f"/api/claims/{claim_id}/analyze-description")
        self.assertEqual(post_res.status_code, 200)
        data = post_res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["analysis"]["accident_type"], "Rear-end collision")

        # 2. GET /nlp-analysis
        get_res = self.client.get(f"/api/claims/{claim_id}/nlp-analysis")
        self.assertEqual(get_res.status_code, 200)
        self.assertTrue(get_res.get_json()["analyzed"])

        # 3. GET /nlp-entities
        ent_res = self.client.get(f"/api/claims/{claim_id}/nlp-entities")
        self.assertEqual(ent_res.status_code, 200)
        self.assertGreaterEqual(ent_res.get_json()["total_entities"], 1)

        # 4. GET /nlp-chronology
        chron_res = self.client.get(f"/api/claims/{claim_id}/nlp-chronology")
        self.assertEqual(chron_res.status_code, 200)
        self.assertGreaterEqual(chron_res.get_json()["total_steps"], 1)

        # 5. GET /nlp-classification
        cls_res = self.client.get(f"/api/claims/{claim_id}/nlp-classification")
        self.assertEqual(cls_res.status_code, 200)
        self.assertEqual(cls_res.get_json()["accident_type"], "Rear-end collision")

        # 6. GET /nlp-consistency
        cons_res = self.client.get(f"/api/claims/{claim_id}/nlp-consistency")
        self.assertEqual(cons_res.status_code, 200)
        self.assertIn("comparisons", cons_res.get_json()["consistency"])

    def test_pdf_report_generation_with_phase6(self):
        """Verify that generate_document_intelligence_report_pdf outputs 7 pages including Page 6 NLP."""
        claim_dict = {
            "claim_id": "CLM-TEST-PDF-1",
            "claimant_name": "Rajesh Sharma",
            "policy_number": "POL-2024-88391",
            "vehicle_number": "MH-12-DE-4052",
            "accident_date": "2026-09-28",
            "claim_description": "While halting at an intersection signal on MG Road, vehicle was rear-ended by a commercial pickup truck. Damage observed on the rear bumper, trunk hatch, and right tail lamp assembly.",
            "status": "SUBMITTED",
            "documents": [],
            "images": [],
        }
        rows = [
            {"field_name": "accident_date", "field_value": "2026-09-28", "source": "policy_document"},
            {"field_name": "vehicle_number", "field_value": "MH-12-DE-4052", "source": "policy_document"},
        ]

        pdf_bytes = generate_document_intelligence_report_pdf(claim_dict, rows, upload_root=str(self.upload_dir))
        self.assertGreater(len(pdf_bytes), 5000)

        import fitz
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        self.assertEqual(len(doc), 7)
        page6_text = doc[5].get_text()
        self.assertIn("NLP Claim Description Analysis", page6_text)
        self.assertIn("Rear-end collision", page6_text)
        self.assertIn("Reconstructed Chronological Event Timeline", page6_text)


if __name__ == "__main__":
    unittest.main()
