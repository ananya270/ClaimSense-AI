"""Execute complete Phase 5 YOLOv8 Computer Vision Damage Detection for CLM-20261116-CRQY."""
import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime, timezone
import shutil

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.config import Config
from backend.database.db import init_database, get_db_session
from backend.database.models import (
    Claim, Document, ClaimImage, ExtractedInformation,
    VehicleDamageAnalysis, VehicleDamageDetection
)
from backend.services.vision.damage_detector import VehicleDamageDetector
from backend.services.vision.visualization import create_annotated_image
from backend.services.receipt import (
    generate_document_intelligence_report_pdf,
    generate_claim_receipt_pdf
)

def run():
    claim_id = "CLM-20261116-CRQY"
    print(f"=== Starting Phase 5 Execution for Claim: {claim_id} ===")

    init_database(Config.SQLALCHEMY_DATABASE_URI)

    # 1. Verify model and instantiate detector
    model_path = BASE_DIR / "models" / "phase5" / "best.pt"
    if not model_path.exists():
        raise FileNotFoundError(f"Trained YOLO checkpoint not found at: {model_path}")
    print(f"[Model] Checkpoint verified at: {model_path} ({model_path.stat().st_size:,} bytes)")

    detector = VehicleDamageDetector.get_instance(model_path=model_path)
    print(f"[Model] Loaded YOLOv8 classes: {detector.class_names}")

    # 2. Retrieve validated replacement vehicle photograph
    claim_upload_dir = BASE_DIR / "uploads" / claim_id
    images_dir = claim_upload_dir / "images"
    target_img_path = images_dir / "replacement_vehicle_image_asdfghjkl.jpg"

    if not target_img_path.exists():
        raise FileNotFoundError(f"Replacement image not found at: {target_img_path}")
    print(f"[Image] Input photograph: {target_img_path.name} ({target_img_path.stat().st_size:,} bytes)")

    # 3. Execute actual YOLOv8 inference
    print("[Inference] Executing model inference on input photograph...")
    t0 = time.perf_counter()
    analysis_result = detector.detect_damage(target_img_path, conf_threshold=0.15)
    t1 = time.perf_counter()
    measured_latency_ms = round((t1 - t0) * 1000.0, 2)

    total_detections = analysis_result["total_detections"]
    detected_cats = analysis_result["damage_categories"]
    highest_conf = analysis_result["highest_confidence"]
    device = analysis_result.get("device", "cpu")

    print(f"[Inference] Completed in {measured_latency_ms:.2f} ms on {device.upper()}")
    print(f"[Inference] Total detections: {total_detections}")
    print(f"[Inference] Peak confidence: {highest_conf * 100:.1f}%")
    print(f"[Inference] Detected categories: {', '.join(detected_cats)}")

    # 4. Generate annotated photograph
    annotated_filename = f"annotated_{target_img_path.name}"
    annotated_target_path = images_dir / annotated_filename
    print(f"[Annotation] Creating annotated image with bounding boxes: {annotated_target_path.name}...")
    create_annotated_image(
        target_img_path,
        analysis_result["detections"],
        output_path=annotated_target_path
    )
    print(f"[Annotation] Annotated image saved ({annotated_target_path.stat().st_size:,} bytes)")

    rel_img_path = str(target_img_path.relative_to(BASE_DIR / "uploads"))
    rel_annotated_path = str(annotated_target_path.relative_to(BASE_DIR / "uploads"))

    # 5. Persist results in SQLite database
    avg_conf = 0.0
    if analysis_result["detections"]:
        avg_conf = sum(d["confidence"] for d in analysis_result["detections"]) / len(analysis_result["detections"])

    now_utc = datetime.now(timezone.utc)

    with get_db_session() as db:
        claim = db.query(Claim).filter_by(claim_id=claim_id).first()
        if not claim:
            raise ValueError(f"Claim {claim_id} not found in database!")

        # Find replacement ClaimImage record
        claim_img = db.query(ClaimImage).filter_by(
            claim_id=claim_id,
            original_filename="asdfghjkl.jpg"
        ).first()

        # Remove previous analysis records for this claim if any exist
        existing_analyses = db.query(VehicleDamageAnalysis).filter_by(claim_id=claim_id).all()
        for ea in existing_analyses:
            db.delete(ea)
        db.flush()

        analysis_record = VehicleDamageAnalysis(
            claim_id=claim_id,
            image_id=claim_img.image_id if claim_img else None,
            image_path=rel_img_path,
            original_image_path=rel_img_path,
            annotated_image_path=rel_annotated_path,
            model_name="YOLOv8n-CarDD",
            model_version="1.0.0",
            total_detections=total_detections,
            total_damages_detected=total_detections,
            damage_categories=json.dumps(detected_cats),
            detected_categories=json.dumps(detected_cats),
            highest_confidence=highest_conf,
            max_confidence=highest_conf,
            average_confidence=round(avg_conf, 4),
            analysis_status="completed",
            processing_time_ms=measured_latency_ms,
            inference_time_ms=measured_latency_ms,
            device=device,
            created_at=now_utc,
            updated_at=now_utc,
        )
        db.add(analysis_record)
        db.flush()

        for det in analysis_result["detections"]:
            bbox = det.get("bbox", [0, 0, 0, 0])
            detection_rec = VehicleDamageDetection(
                analysis_id=analysis_record.id,
                detection_index=det.get("detection_index", 1),
                category=det.get("category", "damage"),
                confidence=det.get("confidence", 0.0),
                bbox_x1=bbox[0],
                bbox_y1=bbox[1],
                bbox_x2=bbox[2],
                bbox_y2=bbox[3],
                location_region=det.get("location_region", "center"),
                created_at=now_utc,
            )
            db.add(detection_rec)

        db.commit()
        print(f"[Database] VehicleDamageAnalysis ID {analysis_record.id} and {total_detections} detections committed successfully.")

        # Serialize full claim dict for PDF generation
        claim_dict = claim.to_dict(include_evidence=True)
        extracted_rows = [
            row.to_dict() for row in db.query(ExtractedInformation)
            .filter_by(claim_id=claim_id)
            .order_by(ExtractedInformation.created_at.asc())
            .all()
        ]

    # 6. Update metadata.json
    meta_file = claim_upload_dir / "metadata.json"
    if meta_file.exists():
        with open(meta_file, "r", encoding="utf-8") as f:
            meta = json.load(f)
        meta["latest_damage_analysis"] = claim_dict.get("damage_analysis")
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
        print(f"[Metadata] {meta_file.name} updated with latest_damage_analysis.")

    # 7. Generate Consolidated PDF Report (Page 5 will now include actual YOLOv8 results)
    print("[PDF] Generating consolidated document intelligence report...")
    report_bytes = generate_document_intelligence_report_pdf(
        claim_dict,
        extracted_rows,
        upload_root=str(BASE_DIR / "uploads")
    )
    report_dir = BASE_DIR / "reports" / claim_id
    report_dir.mkdir(parents=True, exist_ok=True)
    report_pdf_path = report_dir / f"document_report_{claim_id}.pdf"
    report_pdf_path.write_bytes(report_bytes)
    # Also sync to claim uploads
    (claim_upload_dir / f"document_report_{claim_id}.pdf").write_bytes(report_bytes)
    print(f"[PDF] Report PDF generated: {report_pdf_path} ({len(report_bytes):,} bytes)")

    # 8. Generate Submission Receipt PDF
    print("[Receipt] Generating updated submission receipt...")
    receipt_bytes = generate_claim_receipt_pdf(claim_dict)
    receipt_pdf_path = report_dir / f"receipt_{claim_id}.pdf"
    receipt_pdf_path.write_bytes(receipt_bytes)
    # Also sync to claim uploads
    (claim_upload_dir / f"receipt_{claim_id}.pdf").write_bytes(receipt_bytes)
    print(f"[Receipt] Receipt PDF generated: {receipt_pdf_path} ({len(receipt_bytes):,} bytes)")

    print("=== Phase 5 Execution for CLM-20261116-CRQY completed successfully! ===")

if __name__ == "__main__":
    run()

