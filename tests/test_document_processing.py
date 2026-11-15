"""Phase 4 document processing validation tests."""

import io
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from backend.database.db import close_engine, get_db_session, init_database
from backend.database.models import Claim
from backend.services.ocr.document_service import process_document, save_extracted_fields
from backend.services.ocr.document_validator import validate_document_file
from backend.services.ocr.field_extractor import extract_insurance_fields
from backend.services.ocr.text_extractor import extract_txt_file
from backend.services.receipt import generate_document_intelligence_report_pdf, validate_vehicle_image


class Phase4DocumentProcessingTests(unittest.TestCase):
    """Exercise the new OCR and extraction utilities without requiring external OCR runtime."""

    def test_validate_document_file_accepts_text_document(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "claim_form.txt"
            path.write_text("Claimant Name: Ansh Gupta\nPolicy Number: POL-2026-007\n", encoding="utf-8")

            result = validate_document_file(path, max_size_bytes=1_000_000)
            self.assertTrue(result["is_valid"])
            self.assertEqual(result["extension"], "txt")

    def test_extract_txt_file_reads_utf8_text(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "notes.txt"
            path.write_text("Policy Number: POL-2026-007\nVehicle Number: UP14AB1234\n", encoding="utf-8")
            self.assertIn("Policy Number", extract_txt_file(path))

    def test_extract_insurance_fields_returns_expected_keys(self):
        text = (
            "Claimant Name: Ananya Chauhan\n"
            "Policy Number: POL-2026-883\n"
            "Vehicle Number: UP-14-AB-1234\n"
            "Accident Date: 2026-09-12\n"
        )
        fields = extract_insurance_fields(text)
        self.assertEqual(fields["claimant_name"], "Ananya Chauhan")
        self.assertEqual(fields["policy_number"], "POL-2026-883")
        self.assertEqual(fields["vehicle_number"], "UP-14-AB-1234")
        self.assertEqual(fields["accident_date"], "2026-09-12")

    def test_process_document_handles_plain_text_claim_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "claim_form.txt"
            path.write_text(
                "Claimant Name: Ansh Gupta\n"
                "Policy Number: POL-2026-199\n"
                "Vehicle Number: DL-05-AB-5678\n"
                "Accident Date: 2026-11-15\n",
                encoding="utf-8",
            )
            output = process_document(path)
            self.assertTrue(output["is_valid"])
            self.assertIn("claimant_name", output["structured_fields"])
            self.assertTrue(output["document_type"] in {"claim_form", "policy_document", "other"})

    def test_generate_document_intelligence_report_pdf(self):
        claim = {
            "claim_id": "CLM-20261115-ABCD",
            "status": "SUBMITTED",
            "claimant_name": "Ansh Gupta",
            "policy_number": "POL-2026-199",
            "vehicle_number": "DL-05-AB-5678",
            "accident_date": "2026-11-15",
            "created_at": "2026-11-15T06:00:00+00:00",
            "documents": [
                {"original_filename": "policy_document.pdf", "document_type": "POLICY_DOCUMENT", "file_extension": "pdf"},
            ],
            "images": [
                {"original_filename": "vehicle_photo.jpg", "image_type": "VEHICLE_ACCIDENT"},
            ],
        }
        extracted = [
            {"field_name": "claimant_name", "field_value": "Ansh Gupta", "source": "claim_form", "created_at": "2026-11-15T06:00:00+00:00"},
            {"field_name": "policy_number", "field_value": "POL-2026-199", "source": "policy_document", "created_at": "2026-11-15T06:00:00+00:00"},
        ]
        pdf_bytes = generate_document_intelligence_report_pdf(claim, extracted)
        self.assertGreater(len(pdf_bytes), 1000)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_generate_document_intelligence_report_pdf_handles_valid_and_invalid_images(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            upload_root = Path(tmpdir)
            claim_dir = upload_root / "CLM-VALID-IMAGES"
            image_dir = claim_dir / "images"
            image_dir.mkdir(parents=True, exist_ok=True)

            rgb_image = Image.new("RGB", (120, 80), color=(255, 0, 0))
            rgb_image_path = image_dir / "vehicle_photo.jpg"
            rgb_image.save(rgb_image_path, format="JPEG")

            rotated = Image.new("RGB", (80, 120), color=(0, 255, 0))
            exif = Image.Exif()
            exif[274] = 6
            rotated_path = image_dir / "rotated_image.jpg"
            rotated.save(rotated_path, format="JPEG", exif=exif)

            cmyk = Image.new("CMYK", (100, 70), color=(0, 200, 200, 0))
            cmyk_path = image_dir / "garage_estimate_cmyk.jpg"
            cmyk.save(cmyk_path, format="JPEG")

            broken_path = image_dir / "broken_image.jpg"
            broken_path.write_bytes(b"not a valid image file")

            claim = {
                "claim_id": "CLM-VALID-IMAGES",
                "status": "SUBMITTED",
                "claimant_name": "Test Claimant",
                "policy_number": "POL-2026-999",
                "vehicle_number": "UP20AA0001",
                "accident_date": "2026-10-15",
                "created_at": "2026-10-15T09:00:00+00:00",
                "documents": [
                    {
                        "original_filename": "policy.pdf",
                        "document_type": "POLICY_DOCUMENT",
                        "file_extension": "pdf",
                        "file_path": "CLM-VALID-IMAGES/documents/policy.pdf",
                        "file_size": 2048,
                    }
                ],
                "images": [
                    {
                        "original_filename": "vehicle_photo.jpg",
                        "image_type": "VEHICLE_ACCIDENT",
                        "file_path": "CLM-VALID-IMAGES/images/vehicle_photo.jpg",
                        "file_size": rgb_image_path.stat().st_size,
                    },
                    {
                        "original_filename": "rotated_image.jpg",
                        "image_type": "VEHICLE_ACCIDENT",
                        "file_path": "CLM-VALID-IMAGES/images/rotated_image.jpg",
                        "file_size": rotated_path.stat().st_size,
                    },
                    {
                        "original_filename": "garage_estimate_cmyk.jpg",
                        "image_type": "GARAGE_ESTIMATE",
                        "file_path": "CLM-VALID-IMAGES/images/garage_estimate_cmyk.jpg",
                        "file_size": cmyk_path.stat().st_size,
                    },
                    {
                        "original_filename": "broken_image.jpg",
                        "image_type": "VEHICLE_ACCIDENT",
                        "file_path": "CLM-VALID-IMAGES/images/broken_image.jpg",
                        "file_size": broken_path.stat().st_size,
                    },
                ],
            }
            extracted = [
                {"field_name": "claimant_name", "field_value": "Test Claimant", "field_status": "success", "source": "claim_form", "source_filename": "claim_form.pdf", "extraction_method": "pdf_text_extraction"},
                {"field_name": "policy_number", "field_value": "POL-2026-999", "field_status": "success", "source": "policy_document", "source_filename": "policy.pdf", "extraction_method": "pdf_text_extraction"},
                {"field_name": "vehicle_number", "field_value": "", "field_status": "not_found", "source": "garage_estimate.pdf", "source_filename": "garage_estimate.pdf", "extraction_method": "pdf_text_extraction"},
            ]

            pdf_bytes = generate_document_intelligence_report_pdf(claim, extracted, upload_root=upload_root)
            self.assertTrue(pdf_bytes.startswith(b"%PDF"))
            self.assertGreater(len(pdf_bytes), 5000)

    def test_save_extracted_fields_records_missing_status_and_deduplicates(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "claimsense.db"
            db_uri = f"sqlite:///{db_path.as_posix()}"
            init_database(db_uri)
            try:
                with get_db_session() as db:
                    db.add(Claim(
                        claim_id="CLM-TEST-0001",
                        claimant_name="Test Claimant",
                        policy_number="POL-TEST-001",
                        vehicle_number="DL-05-AB-9999",
                        accident_date="2026-11-15",
                        claim_description="Synthetic claim for validation.",
                        status="SUBMITTED",
                    ))

                rows = [
                    {"field_name": "claimant_name", "field_value": "Ansh Gupta", "source": "claim_form"},
                    {"field_name": "claimant_name", "field_value": "Ansh Gupta", "source": "claim_form"},
                    {"field_name": "accident_date", "field_value": "", "source": "policy_document"},
                ]

                saved = save_extracted_fields("CLM-TEST-0001", rows)
                self.assertEqual(len(saved), 2)
                self.assertEqual(saved[0]["field_status"], "extracted")
                self.assertEqual(saved[1]["field_status"], "not_present")

                pdf = generate_document_intelligence_report_pdf(
                    {"claim_id": "CLM-TEST-0001", "status": "SUBMITTED", "documents": [], "images": []},
                    saved,
                )
                self.assertTrue(pdf.startswith(b"%PDF"))
            finally:
                close_engine()

    def test_status_aliases_are_normalized_consistently(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "claimsense.db"
            init_database(f"sqlite:///{db_path.as_posix()}")
            try:
                with get_db_session() as db:
                    db.add(Claim(
                        claim_id="CLM-STATUS-0001",
                        claimant_name="Status Claimant",
                        policy_number="POL-STATUS-001",
                        vehicle_number="MH-12-AB-1234",
                        accident_date="2026-09-28",
                        claim_description="Status validation claim.",
                        status="SUBMITTED",
                    ))

                rows = [
                    {"field_name": "claimant_name", "field_value": "Rajesh Sharma", "field_status": "match", "source": "claim_form"},
                    {"field_name": "policy_number", "field_value": "", "field_status": "not_found", "source": "invoice_document"},
                ]
                saved = save_extracted_fields("CLM-STATUS-0001", rows)
                status_outcomes = {item["field_name"]: item["field_status"] for item in saved}
                self.assertEqual(status_outcomes["claimant_name"], "matched")
                self.assertEqual(status_outcomes["policy_number"], "not_present")
            finally:
                close_engine()

    def test_validate_vehicle_image_detects_synthetic_graphic_vs_photo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # 1. Synthetic graphic with > 80% uniform flat background
            graphic_path = Path(tmpdir) / "synthetic_graphic.jpg"
            img = Image.new("RGB", (300, 200), color=(250, 250, 250))
            for y in range(40, 70):
                for x in range(50, 150):
                    img.putpixel((x, y), (20, 50, 180))
            img.save(graphic_path, format="JPEG")

            val_graphic = validate_vehicle_image(graphic_path)
            self.assertFalse(val_graphic["is_valid_vehicle_photo"])
            self.assertEqual(val_graphic["status"], "invalid_graphic")

            # 2. Simulated photo with rich color variation across pixels
            photo_path = Path(tmpdir) / "vehicle_photo.jpg"
            photo_img = Image.new("RGB", (100, 100))
            for y in range(100):
                for x in range(100):
                    photo_img.putpixel((x, y), ((x * 7) % 256, (y * 5 + x * 3) % 256, (x * 2 + y * 9) % 256))
            photo_img.save(photo_path, format="JPEG")

            val_photo = validate_vehicle_image(photo_path)
            self.assertTrue(val_photo["is_valid_vehicle_photo"])
            self.assertEqual(val_photo["status"], "validated_photo")

    def test_field_extractor_does_not_concatenate_entire_document(self):
        # Policy doc without description
        policy_text = (
            "CLAIMSENSE AI\n"
            "Policy Number: POL-2024-88391\n"
            "Vehicle Registration: MH-12-DE-4052\n"
            "Accident Date: 2026-09-28\n"
        )
        fields = extract_insurance_fields(policy_text)
        self.assertEqual(fields["policy_number"], "POL-2024-88391")
        self.assertEqual(fields["vehicle_number"], "MH-12-DE-4052")
        self.assertEqual(fields["accident_date"], "2026-09-28")
        self.assertEqual(fields["incident_description"], "")

        # Claim form with explicit description
        claim_form_text = (
            "Claimant: Rajesh Sharma\n"
            "Policy Number: POL-2024-88391\n"
            "Claim Description: Rear-end collision at MG Road intersection.\n"
            "Accident Date: 2026-09-28\n"
        )
        fields_cf = extract_insurance_fields(claim_form_text)
        self.assertEqual(fields_cf["claimant_name"], "Rajesh Sharma")
        self.assertEqual(fields_cf["incident_description"], "Rear-end collision at MG Road intersection.")

        # Garage estimate with itemized breakdown
        inv_text = (
            "Garage Estimate\n"
            "Claim Amount: INR 84500\n"
            "Bodywork and paint: 38500\n"
            "Tail lamp replacement: 16000\n"
            "Labor and miscellaneous: 30000\n"
        )
        fields_inv = extract_insurance_fields(inv_text)
        self.assertEqual(fields_inv["claim_amount"], "84500")
        self.assertIn("Bodywork and paint: 38500", fields_inv["repair_cost_breakdown"])
        self.assertIn("Tail lamp replacement", fields_inv["repair_description"])

    def test_pdf_report_distinguishes_database_narrative_and_handles_flagged_image(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            upload_root = Path(tmpdir)
            img_dir = upload_root / "images"
            img_dir.mkdir(parents=True, exist_ok=True)
            graphic_path = img_dir / "rear_bumper_damage.jpg"
            img = Image.new("RGB", (200, 150), color=(248, 249, 250))
            img.save(graphic_path, format="JPEG")

            claim = {
                "claim_id": "CLM-20261115-93K5",
                "status": "SUBMITTED",
                "claimant_name": "Rajesh Sharma",
                "policy_number": "POL-2024-88391",
                "vehicle_number": "MH-12-DE-4052",
                "accident_date": "2026-09-28",
                "claim_description": "While halting at an intersection signal on MG Road, vehicle was rear-ended.",
                "documents": [
                    {"original_filename": "policy_schedule_88391.pdf", "document_type": "POLICY_DOCUMENT", "file_extension": "pdf"},
                    {"original_filename": "signed_claim_form.pdf", "document_type": "CLAIM_FORM", "file_extension": "pdf"},
                ],
                "images": [
                    {"original_filename": "rear_bumper_damage.jpg", "image_type": "VEHICLE_ACCIDENT", "file_path": "images/rear_bumper_damage.jpg"},
                ],
            }
            extracted = [
                {"field_name": "policy_number", "field_value": "POL-2024-88391", "source_filename": "policy_schedule_88391.pdf", "extraction_method": "pdf_text_extraction"},
                {"field_name": "claimant_name", "field_value": "Rajesh Sharma", "source_filename": "signed_claim_form.pdf", "extraction_method": "pdf_text_extraction"},
                {"field_name": "incident_description", "field_value": "Rear-end collision at MG Road intersection.", "source_filename": "signed_claim_form.pdf", "extraction_method": "pdf_text_extraction"},
            ]

            pdf_bytes = generate_document_intelligence_report_pdf(claim, extracted, upload_root=upload_root)
            self.assertTrue(pdf_bytes.startswith(b"%PDF"))
            self.assertGreater(len(pdf_bytes), 4000)

    def test_replace_image_endpoint_preserves_original_and_updates_validation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            from backend.app import create_app
            from backend.config import Config

            tmp = Path(tmpdir)
            class TestCfg(Config):
                TESTING = True
                UPLOAD_FOLDER = tmp / "uploads"
                DATABASE_PATH = tmp / "test.db"
                SQLALCHEMY_DATABASE_URI = f"sqlite:///{(tmp / 'test.db').as_posix()}"

            app = create_app(TestCfg)
            client = app.test_client()

            # Create an initial claim
            claim_payload = {
                "claimant_name": "Rajesh Sharma",
                "policy_number": "POL-2024-88391",
                "vehicle_number": "MH-12-DE-4052",
                "accident_date": "2026-09-28",
                "claim_description": "Rear-end collision on MG Road.",
                "policy_document": (io.BytesIO(b"Policy text POL-2024-88391"), "policy.pdf"),
                "claim_form": (io.BytesIO(b"Claim form text"), "form.pdf"),
                "invoice_document": (io.BytesIO(b"Invoice text INR 84500"), "invoice.pdf"),
                "vehicle_image": (io.BytesIO(b"\xff\xd8\xff\xe0" + b"\x00" * 200), "graphic.jpg"),
            }
            res = client.post("/api/claims", data=claim_payload, content_type="multipart/form-data")
            self.assertEqual(res.status_code, 201)
            cid = res.get_json()["claim_id"]

            orig_img_path = tmp / "uploads" / cid / "images" / "vehicle_image_graphic.jpg"
            self.assertTrue(orig_img_path.exists())

            # Now replace the image with a replacement photograph
            img_buf = io.BytesIO()
            new_img = Image.new("RGB", (300, 200), color=(120, 140, 160))
            for x in range(300):
                for y in range(200):
                    new_img.putpixel((x, y), ((x * 3) % 256, (y * 5) % 256, (x + y) % 256))
            new_img.save(img_buf, format="JPEG")
            img_buf.seek(0)

            rep_res = client.post(
                f"/api/claims/{cid}/replace-image",
                data={"vehicle_image": (img_buf, "actual_damage_photo.jpg")},
                content_type="multipart/form-data",
            )
            self.assertEqual(rep_res.status_code, 200)
            rep_data = rep_res.get_json()
            self.assertTrue(rep_data["success"])
            self.assertTrue(rep_data["original_preserved"])
            # Verify original file was preserved
            self.assertTrue(orig_img_path.exists())
            # Verify new file exists
            new_img_path = tmp / "uploads" / cid / "images" / "replacement_vehicle_image_actual_damage_photo.jpg"
            self.assertTrue(new_img_path.exists())
            self.assertTrue(rep_data["validation"]["is_valid_vehicle_photo"])
            close_engine()

    def test_dataset_evaluations_produce_reproducible_metrics(self):
        repo_root = Path(__file__).resolve().parents[1]
        from backend.services.dataset_evaluation import (
            evaluate_funsd_dataset,
            evaluate_sroie_dataset,
            verify_cadd_dataset,
        )
        # Test CarDD
        cardd = verify_cadd_dataset(repo_root / "datasets" / "CarDD_300")
        self.assertEqual(cardd["image_count"], 300)
        self.assertEqual(cardd["status"], "ready_for_phase_5")
        self.assertEqual(len(cardd["damage_categories"]), 6)

        # Test FUNSD
        funsd = evaluate_funsd_dataset(repo_root / "datasets" / "FUNSD")
        self.assertEqual(funsd["total_samples"], 199)
        self.assertGreater(funsd["overall_metrics"]["key_value_link_f1"], 0.50)

        # Test SROIE
        sroie = evaluate_sroie_dataset(repo_root / "datasets" / "SROIE" / "train-00000-of-00001.parquet")
        self.assertEqual(sroie["evaluated_samples"], 626)
        self.assertGreater(sroie["metrics"]["field_extraction_precision"], 0.70)


if __name__ == "__main__":
    unittest.main()
