"""Claim submission routes for ClaimSense AI."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from flask import Blueprint, current_app, jsonify, request
from werkzeug.utils import secure_filename

from backend.utils.logger import setup_logger
from backend.utils.validators import (
    generate_claim_id,
    is_valid_claim_id_format,
    validate_claim_form_fields,
    validate_claim_files,
    sanitize_and_resolve_path,
)

logger = setup_logger("claimsense.claims")

claims_bp = Blueprint("claims", __name__)


@claims_bp.route("/claims", methods=["POST"])
def submit_claim():
    """Handles claim submission with multipart form data.

    Validates required text fields and files, safely stores uploads,
    generates a standardized Claim ID, and saves claim metadata.
    """
    form_data = request.form.to_dict()
    files_dict = request.files

    # 1. Validate text fields
    fields_valid, field_errors = validate_claim_form_fields(form_data)
    if not fields_valid:
        logger.warning(f"Claim submission rejected due to form errors: {field_errors}")
        return jsonify({
            "success": False,
            "error": "Validation Error",
            "message": "Form validation failed.",
            "details": field_errors,
        }), 400

    # 2. Validate uploaded files
    files_valid, file_errors = validate_claim_files(files_dict)
    if not files_valid:
        logger.warning(f"Claim submission rejected due to file errors: {file_errors}")
        return jsonify({
            "success": False,
            "error": "Validation Error",
            "message": "Uploaded files validation failed.",
            "details": file_errors,
        }), 400

    try:
        # 3. Generate unique claim ID
        claim_id = generate_claim_id()
        upload_base = Path(current_app.config["UPLOAD_FOLDER"])
        claim_dir = upload_base / claim_id
        docs_dir = claim_dir / "documents"
        images_dir = claim_dir / "images"

        docs_dir.mkdir(parents=True, exist_ok=True)
        images_dir.mkdir(parents=True, exist_ok=True)

        saved_files = {}

        # 4. Save documents safely
        doc_fields = ["policy_document", "claim_form", "invoice_document"]
        for field in doc_fields:
            file_obj = files_dict[field]
            clean_filename = secure_filename(file_obj.filename)
            prefix = field
            dest_filename = f"{prefix}_{clean_filename}" if clean_filename else f"{prefix}.bin"
            target_path = sanitize_and_resolve_path(docs_dir, dest_filename)
            file_obj.save(str(target_path))
            saved_files[field] = {
                "original_name": file_obj.filename,
                "saved_as": dest_filename,
                "relative_path": str(target_path.relative_to(upload_base)),
                "size_bytes": target_path.stat().st_size,
            }

        # 5. Save vehicle image safely
        img_file = files_dict["vehicle_image"]
        clean_img_name = secure_filename(img_file.filename)
        dest_img_name = f"vehicle_image_{clean_img_name}" if clean_img_name else "vehicle_image.jpg"
        target_img_path = sanitize_and_resolve_path(images_dir, dest_img_name)
        img_file.save(str(target_img_path))
        saved_files["vehicle_image"] = {
            "original_name": img_file.filename,
            "saved_as": dest_img_name,
            "relative_path": str(target_img_path.relative_to(upload_base)),
            "size_bytes": target_img_path.stat().st_size,
        }

        # 6. Save claim metadata JSON
        metadata = {
            "claim_id": claim_id,
            "claimant_name": form_data["claimant_name"].strip(),
            "policy_number": form_data["policy_number"].strip(),
            "vehicle_number": form_data["vehicle_number"].strip(),
            "accident_date": form_data["accident_date"].strip(),
            "claim_description": form_data["claim_description"].strip(),
            "files": saved_files,
            "status": "SUBMITTED",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        metadata_path = claim_dir / "metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Successfully processed and stored claim: {claim_id}")

        return jsonify({
            "success": true_or_bool(True),
            "claim_id": claim_id,
            "message": "Claim submitted successfully",
            "data": {
                "claim_id": claim_id,
                "claimant_name": metadata["claimant_name"],
                "policy_number": metadata["policy_number"],
                "vehicle_number": metadata["vehicle_number"],
                "accident_date": metadata["accident_date"],
                "claim_description": metadata["claim_description"],
                "files_count": len(saved_files),
                "created_at": metadata["created_at"],
            },
        }), 201

    except Exception as e:
        logger.error(f"Error while processing claim submission: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Server Error",
            "message": "Failed to store claim submission files.",
            "details": str(e),
        }), 500


def true_or_bool(val: bool) -> bool:
    return val


@claims_bp.route("/claims/<claim_id>", methods=["GET"])
def get_claim(claim_id: str):
    """Retrieves submitted claim metadata by Claim ID."""
    if not is_valid_claim_id_format(claim_id):
        return jsonify({
            "success": False,
            "error": "Invalid Claim ID format",
            "message": "Claim ID must follow format CLM-YYYYMMDD-XXXX.",
        }), 400

    upload_base = Path(current_app.config["UPLOAD_FOLDER"])
    metadata_path = upload_base / claim_id / "metadata.json"

    if not metadata_path.exists():
        return jsonify({
            "success": False,
            "error": "Not Found",
            "message": f"Claim with ID '{claim_id}' was not found.",
        }), 404

    try:
        with open(metadata_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify({
            "success": True,
            "claim_id": claim_id,
            "data": data,
        }), 200
    except Exception as e:
        logger.error(f"Failed to read metadata for claim {claim_id}: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Server Error",
            "message": "Failed to read claim records.",
        }), 500
