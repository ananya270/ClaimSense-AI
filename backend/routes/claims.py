"""Claim submission, retrieval, search, and receipt routes for ClaimSense AI (Phase 3)."""
import io
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from flask import Blueprint, current_app, jsonify, request, session, send_file
from werkzeug.utils import secure_filename
from sqlalchemy import desc

from backend.database.db import get_db_session
from backend.database.models import Claim, Document, ClaimImage
from backend.services.receipt import generate_claim_receipt_pdf
from backend.utils.auth import get_current_user_id, can_user_access_claim
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
    """Handles multipart claim submission.

    Validates required text fields and files, safely writes uploads to disk,
    stores metadata.json (backward compatibility), and persists structured
    claim and evidence records in SQLite database.
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

    # Retrieve current user if authenticated
    current_user_id = session.get("user_id")

    claim_dir = None
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
        doc_type_mapping = {
            "policy_document": "POLICY_DOCUMENT",
            "claim_form": "CLAIM_FORM",
            "invoice_document": "INVOICE",
        }

        saved_docs_metadata = []
        for field in doc_fields:
            file_obj = files_dict[field]
            clean_filename = secure_filename(file_obj.filename)
            prefix = field
            dest_filename = f"{prefix}_{clean_filename}" if clean_filename else f"{prefix}.bin"
            target_path = sanitize_and_resolve_path(docs_dir, dest_filename)
            file_obj.save(str(target_path))

            ext = clean_filename.rsplit(".", 1)[-1].lower() if "." in clean_filename else ""
            size_bytes = target_path.stat().st_size
            rel_path = str(target_path.relative_to(upload_base))

            saved_files[field] = {
                "original_name": file_obj.filename,
                "saved_as": dest_filename,
                "relative_path": rel_path,
                "size_bytes": size_bytes,
            }
            saved_docs_metadata.append({
                "document_type": doc_type_mapping.get(field, "OTHER"),
                "file_path": rel_path,
                "original_filename": file_obj.filename,
                "stored_filename": dest_filename,
                "file_extension": ext,
                "file_size": size_bytes,
            })

        # 5. Save vehicle image safely
        img_file = files_dict["vehicle_image"]
        clean_img_name = secure_filename(img_file.filename)
        dest_img_name = f"vehicle_image_{clean_img_name}" if clean_img_name else "vehicle_image.jpg"
        target_img_path = sanitize_and_resolve_path(images_dir, dest_img_name)
        img_file.save(str(target_img_path))

        img_ext = clean_img_name.rsplit(".", 1)[-1].lower() if "." in clean_img_name else ""
        img_size_bytes = target_img_path.stat().st_size
        img_rel_path = str(target_img_path.relative_to(upload_base))

        saved_files["vehicle_image"] = {
            "original_name": img_file.filename,
            "saved_as": dest_img_name,
            "relative_path": img_rel_path,
            "size_bytes": img_size_bytes,
        }

        # 6. Save claim metadata JSON (Backward compatibility)
        submission_time = datetime.now(timezone.utc)
        metadata = {
            "claim_id": claim_id,
            "user_id": current_user_id,
            "claimant_name": form_data["claimant_name"].strip(),
            "policy_number": form_data["policy_number"].strip(),
            "vehicle_number": form_data["vehicle_number"].strip(),
            "accident_date": form_data["accident_date"].strip(),
            "claim_description": form_data["claim_description"].strip(),
            "files": saved_files,
            "status": "SUBMITTED",
            "created_at": submission_time.isoformat(),
        }

        metadata_path = claim_dir / "metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        # 7. Persist to SQLite Database
        with get_db_session() as db:
            claim_record = Claim(
                claim_id=claim_id,
                user_id=current_user_id,
                claimant_name=metadata["claimant_name"],
                policy_number=metadata["policy_number"],
                vehicle_number=metadata["vehicle_number"],
                accident_date=metadata["accident_date"],
                claim_description=metadata["claim_description"],
                status="SUBMITTED",
                created_at=submission_time,
                updated_at=submission_time,
            )
            db.add(claim_record)
            db.flush()

            # Add documents
            for doc_meta in saved_docs_metadata:
                doc_record = Document(
                    claim_id=claim_id,
                    document_type=doc_meta["document_type"],
                    file_path=doc_meta["file_path"],
                    original_filename=doc_meta["original_filename"],
                    stored_filename=doc_meta["stored_filename"],
                    file_extension=doc_meta["file_extension"],
                    file_size=doc_meta["file_size"],
                    created_at=submission_time,
                )
                db.add(doc_record)

            # Add image
            img_record = ClaimImage(
                claim_id=claim_id,
                image_type="VEHICLE_ACCIDENT",
                file_path=img_rel_path,
                original_filename=img_file.filename,
                stored_filename=dest_img_name,
                file_extension=img_ext,
                file_size=img_size_bytes,
                created_at=submission_time,
            )
            db.add(img_record)

        logger.info(f"Successfully processed and stored claim in disk and SQLite: {claim_id}")

        return jsonify({
            "success": True,
            "claim_id": claim_id,
            "message": "Claim submitted successfully",
            "receipt_url": f"/api/claims/{claim_id}/receipt",
            "data": {
                "claim_id": claim_id,
                "user_id": current_user_id,
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
        # Attempt safe cleanup if directory was partially written
        if claim_dir and claim_dir.exists():
            try:
                shutil.rmtree(claim_dir)
            except Exception:
                pass
        return jsonify({
            "success": False,
            "error": "Server Error",
            "message": "Failed to store claim submission files or database record.",
            "details": str(e),
        }), 500


@claims_bp.route("/claims/<claim_id>", methods=["GET"])
def get_claim(claim_id: str):
    """Retrieves submitted claim metadata by Claim ID with access control."""
    if not is_valid_claim_id_format(claim_id):
        return jsonify({
            "success": False,
            "error": "Invalid Claim ID format",
            "message": "Claim ID must follow format CLM-YYYYMMDD-XXXX.",
        }), 400

    user_id = session.get("user_id")
    user_role = session.get("role")

    with get_db_session() as db:
        claim = db.query(Claim).filter_by(claim_id=claim_id).first()

        if not claim:
            # Fallback check on disk (in case legacy un-migrated)
            upload_base = Path(current_app.config["UPLOAD_FOLDER"])
            metadata_path = upload_base / claim_id / "metadata.json"
            if not metadata_path.exists():
                return jsonify({
                    "success": False,
                    "error": "Not Found",
                    "message": f"Claim with ID '{claim_id}' was not found.",
                }), 404

            # Ingest on the fly
            with open(metadata_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return jsonify({
                "success": True,
                "claim_id": claim_id,
                "data": data,
            }), 200

        # Enforce access authorization
        if not can_user_access_claim(claim, user_id, user_role):
            if not user_id:
                return jsonify({
                    "success": False,
                    "error": "Unauthorized",
                    "message": "Authentication required to view this claim.",
                }), 401
            return jsonify({
                "success": False,
                "error": "Forbidden",
                "message": "You do not have permission to access this claim record.",
            }), 403

        claim_data = claim.to_dict(include_evidence=True)
        return jsonify({
            "success": True,
            "claim_id": claim_id,
            "data": claim_data,
        }), 200


@claims_bp.route("/claims/policy/<policy_number>", methods=["GET"])
def get_claims_by_policy(policy_number: str):
    """Search claims associated with a policy number.

    Requires authentication to protect policyholders' personal evidence.
    """
    user_id = session.get("user_id")
    user_role = session.get("role")

    if not user_id:
        return jsonify({
            "success": False,
            "error": "Unauthorized",
            "message": "Authentication required to search claims by policy number.",
        }), 401

    clean_policy = policy_number.strip()
    if not clean_policy:
        return jsonify({
            "success": False,
            "error": "Validation Error",
            "message": "Policy number must not be empty.",
        }), 400

    with get_db_session() as db:
        query = db.query(Claim).filter(Claim.policy_number.ilike(clean_policy))

        # Accessors and admins can view any claim under the policy
        if user_role not in ("assessor", "admin"):
            query = query.filter_by(user_id=user_id)

        claims = query.order_by(desc(Claim.created_at)).all()

        if not claims:
            return jsonify({
                "success": False,
                "error": "Not Found",
                "message": f"No claims found for policy '{clean_policy}' under your account.",
            }), 404

        return jsonify({
            "success": True,
            "policy_number": clean_policy,
            "count": len(claims),
            "claims": [c.to_dict(include_evidence=True) for c in claims],
        }), 200


@claims_bp.route("/my-claims", methods=["GET"])
def get_my_claims():
    """Retrieves all claims submitted by the currently authenticated user."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({
            "success": False,
            "error": "Unauthorized",
            "message": "Authentication required to access personal claim history.",
        }), 401

    with get_db_session() as db:
        claims = (
            db.query(Claim)
            .filter_by(user_id=user_id)
            .order_by(desc(Claim.created_at))
            .all()
        )
        return jsonify({
            "success": True,
            "count": len(claims),
            "claims": [c.to_dict(include_evidence=True) for c in claims],
        }), 200


@claims_bp.route("/claims/<claim_id>/receipt", methods=["GET"])
def get_claim_receipt(claim_id: str):
    """Generates and serves official claim submission receipt in PDF or JSON format."""
    if not is_valid_claim_id_format(claim_id):
        return jsonify({
            "success": False,
            "error": "Invalid Claim ID format",
            "message": "Claim ID must follow format CLM-YYYYMMDD-XXXX.",
        }), 400

    user_id = session.get("user_id")
    user_role = session.get("role")

    with get_db_session() as db:
        claim = db.query(Claim).filter_by(claim_id=claim_id).first()

        claim_dict = None
        if claim:
            if not can_user_access_claim(claim, user_id, user_role):
                if not user_id:
                    return jsonify({
                        "success": False,
                        "error": "Unauthorized",
                        "message": "Authentication required to access this claim receipt.",
                    }), 401
                return jsonify({
                    "success": False,
                    "error": "Forbidden",
                    "message": "You are not authorized to download this claim receipt.",
                }), 403
            claim_dict = claim.to_dict(include_evidence=True)
        else:
            # Fallback to metadata.json on disk if available
            upload_base = Path(current_app.config["UPLOAD_FOLDER"])
            metadata_path = upload_base / claim_id / "metadata.json"
            if not metadata_path.exists():
                return jsonify({
                    "success": False,
                    "error": "Not Found",
                    "message": f"Claim with ID '{claim_id}' was not found.",
                }), 404
            with open(metadata_path, "r", encoding="utf-8") as f:
                claim_dict = json.load(f)

    # Format check: format=pdf (default) vs format=json
    requested_format = request.args.get("format", "pdf").lower()
    if requested_format == "json" or request.headers.get("Accept") == "application/json":
        return jsonify({
            "success": True,
            "receipt_type": "SUBMISSION_RECEIPT",
            "claim_id": claim_dict.get("claim_id"),
            "policy_number": claim_dict.get("policy_number"),
            "claimant_name": claim_dict.get("claimant_name"),
            "vehicle_number": claim_dict.get("vehicle_number"),
            "accident_date": claim_dict.get("accident_date"),
            "claim_description": claim_dict.get("claim_description"),
            "status": claim_dict.get("status", "SUBMITTED"),
            "created_at": claim_dict.get("created_at"),
            "documents": claim_dict.get("documents", []),
            "images": claim_dict.get("images", []),
            "disclaimer": (
                "This receipt confirms submission and registration of the claim evidence. "
                "It does not represent approval, rejection, fraud confirmation, or final "
                "insurance claim verification."
            ),
        }), 200

    # Generate PDF
    try:
        pdf_bytes = generate_claim_receipt_pdf(claim_dict)
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"receipt_{claim_id}.pdf",
        )
    except Exception as e:
        logger.error(f"Error generating PDF receipt for claim {claim_id}: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Receipt Generation Error",
            "message": "Failed to generate receipt PDF.",
            "details": str(e),
        }), 500
