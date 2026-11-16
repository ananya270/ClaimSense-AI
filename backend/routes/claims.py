"""Claim submission, retrieval, search, and receipt routes for ClaimSense AI (Phase 3 Hardened)."""
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
from backend.database.models import (
    User,
    Claim,
    Document,
    ClaimImage,
    ExtractedInformation,
    VehicleDamageAnalysis,
    VehicleDamageDetection,
)
from backend.services.ocr.document_service import ingest_extracted_claim_data, process_document
from backend.services.receipt import (
    generate_claim_receipt_pdf,
    generate_document_intelligence_report_pdf,
    validate_vehicle_image,
)
from backend.services.vision import (
    VehicleDamageDetector,
    create_annotated_image,
    get_model_evaluation_metrics,
)
from backend.extensions import csrf
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
    """Handles authenticated multipart claim submission.

    Validates required text fields, file extensions, and file signatures,
    safely writes uploads to isolated disk directories, and persists
    structured claim and evidence records in SQLite database linked
    strictly to the authenticated session user.
    """
    # 1. Enforce active user session authentication
    current_user_id = session.get("user_id")
    if not current_user_id:
        return jsonify({
            "success": False,
            "error": "Unauthorized",
            "message": "Authentication required. Please sign in before submitting an insurance claim.",
        }), 401

    with get_db_session() as db:
        user = db.query(User).filter_by(id=current_user_id).first()
        if not user or not user.is_active:
            session.clear()
            return jsonify({
                "success": False,
                "error": "Unauthorized",
                "message": "An active user account is required to submit a claim.",
            }), 401

    form_data = request.form.to_dict()
    files_dict = request.files

    # 2. Validate text fields
    fields_valid, field_errors = validate_claim_form_fields(form_data)
    if not fields_valid:
        logger.warning(f"Claim submission rejected due to form errors: {field_errors}")
        return jsonify({
            "success": False,
            "error": "Validation Error",
            "message": "Form validation failed.",
            "details": field_errors,
        }), 400

    # 3. Validate uploaded files (presence, extensions, 0-byte checks, signatures)
    files_valid, file_errors = validate_claim_files(files_dict)
    if not files_valid:
        logger.warning(f"Claim submission rejected due to file errors: {file_errors}")
        return jsonify({
            "success": False,
            "error": "Validation Error",
            "message": "Uploaded files validation failed.",
            "details": file_errors,
        }), 400

    claim_dir = None
    try:
        # 4. Generate unique claim ID and isolated directories
        claim_id = generate_claim_id()
        upload_base = Path(current_app.config["UPLOAD_FOLDER"])
        claim_dir = upload_base / claim_id
        docs_dir = claim_dir / "documents"
        images_dir = claim_dir / "images"

        docs_dir.mkdir(parents=True, exist_ok=True)
        images_dir.mkdir(parents=True, exist_ok=True)

        saved_files = {}

        # 5. Save evidentiary documents safely
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

        # 6. Save vehicle image safely
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

        # 7. Persist claim metadata JSON (Backward compatibility)
        submission_time = datetime.now(timezone.utc)
        incident_location = form_data.get("incident_location", "").strip() or None
        metadata = {
            "claim_id": claim_id,
            "user_id": current_user_id,
            "claimant_name": form_data["claimant_name"].strip(),
            "policy_number": form_data["policy_number"].strip(),
            "vehicle_number": form_data["vehicle_number"].strip(),
            "accident_date": form_data["accident_date"].strip(),
            "incident_location": incident_location,
            "claim_description": form_data["claim_description"].strip(),
            "files": saved_files,
            "status": "SUBMITTED",
            "created_at": submission_time.isoformat(),
        }

        metadata_path = claim_dir / "metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        # 8. Persist to SQLite Database linked to authenticated user
        with get_db_session() as db:
            claim_record = Claim(
                claim_id=claim_id,
                user_id=current_user_id,
                claimant_name=metadata["claimant_name"],
                policy_number=metadata["policy_number"],
                vehicle_number=metadata["vehicle_number"],
                accident_date=metadata["accident_date"],
                incident_location=incident_location,
                claim_description=metadata["claim_description"],
                status="SUBMITTED",
                created_at=submission_time,
                updated_at=submission_time,
            )
            db.add(claim_record)
            db.flush()

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

        # 8. Phase 4 document intelligence pipeline (best-effort extraction)
        processed_documents = []
        for field in doc_fields:
            file_obj = files_dict[field]
            stored_path = upload_base / saved_files[field]["relative_path"]
            processed = process_document(stored_path, file_obj.filename)
            processed_documents.append(processed)

        try:
            ingest_extracted_claim_data(claim_id, processed_documents)
        except Exception as exc:
            logger.warning(f"Best-effort Phase 4 extraction storage skipped for claim {claim_id}: {exc}")

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
                "status": "SUBMITTED",
                "files_count": len(saved_files),
                "created_at": metadata["created_at"],
            },
        }), 201

    except Exception as e:
        logger.error(f"Error while processing claim submission: {str(e)}", exc_info=True)
        # Clean up partially written directory on failure
        if claim_dir and claim_dir.exists():
            try:
                shutil.rmtree(claim_dir, ignore_errors=True)
            except Exception:
                pass
        return jsonify({
            "success": False,
            "error": "Server Error",
            "message": "Failed to store claim submission files or database record.",
        }), 500


@claims_bp.route("/claims/<claim_id>", methods=["GET"])
def get_claim(claim_id: str):
    """Retrieves submitted claim metadata by Claim ID with strict access control."""
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

        if claim:
            # Enforce access authorization
            if not can_user_access_claim(claim, user_id, user_role):
                if not user_id:
                    return jsonify({
                        "success": False,
                        "error": "Unauthorized",
                        "message": "Authentication required to access this claim record.",
                    }), 401
                return jsonify({
                    "success": False,
                    "error": "Forbidden",
                    "message": "You do not have permission to view this claim.",
                }), 403

            claim_data = claim.to_dict(include_evidence=True)
            upload_base = Path(current_app.config["UPLOAD_FOLDER"])
            metadata_path = upload_base / claim_id / "metadata.json"
            if metadata_path.exists():
                try:
                    with open(metadata_path, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    if "vehicle_image_validation" in meta:
                        claim_data["vehicle_image_validation"] = meta["vehicle_image_validation"]
                        if "vehicle_image" in claim_data.get("files", {}):
                            claim_data["files"]["vehicle_image"]["validation_status"] = meta["vehicle_image_validation"].get("status")
                    if "archived_images" in meta:
                        claim_data["archived_images"] = meta["archived_images"]
                except Exception:
                    pass

            return jsonify({
                "success": True,
                "data": claim_data,
            }), 200

    # Fallback to metadata.json on disk if database record is missing
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

        # Enforce authorization on disk fallback read
        if not can_user_access_claim_dict(data, user_id, user_role):
            if not user_id:
                return jsonify({
                    "success": False,
                    "error": "Unauthorized",
                    "message": "Authentication required to access this claim record.",
                }), 401
            return jsonify({
                "success": False,
                "error": "Forbidden",
                "message": "You do not have permission to view this claim.",
            }), 403

        return jsonify({
            "success": True,
            "data": data,
        }), 200
    except Exception as e:
        logger.error(f"Failed to read metadata for claim {claim_id}: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Server Error",
            "message": "Failed to read claim records.",
        }), 500


@claims_bp.route("/claims/<claim_id>/extracted", methods=["GET"])
def get_claim_extractions(claim_id: str):
    """Fetch database-backed extracted fields for a claim as part of Phase 4 analysis."""
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
            return jsonify({
                "success": False,
                "error": "Not Found",
                "message": f"Claim with ID '{claim_id}' was not found.",
            }), 404

        if not can_user_access_claim(claim, user_id, user_role):
            if not user_id:
                return jsonify({
                    "success": False,
                    "error": "Unauthorized",
                    "message": "Authentication required to view extracted claim fields.",
                }), 401
            return jsonify({
                "success": False,
                "error": "Forbidden",
                "message": "You do not have permission to access extracted claim fields.",
            }), 403

        rows = db.query(ExtractedInformation).filter_by(claim_id=claim_id).order_by(ExtractedInformation.created_at.asc()).all()
        return jsonify({
            "success": True,
            "claim_id": claim_id,
            "count": len(rows),
            "fields": [record.to_dict() for record in rows],
        }), 200


@claims_bp.route("/claims/policy/<policy_number>", methods=["GET"])
def search_claims_by_policy(policy_number: str):
    """Searches and retrieves all claims associated with a specific Policy Number."""
    clean_policy = (policy_number or "").strip()
    if not clean_policy:
        return jsonify({
            "success": False,
            "error": "Validation Error",
            "message": "Policy number parameter cannot be empty.",
        }), 400

    user_id = session.get("user_id")
    user_role = session.get("role")

    if not user_id:
        return jsonify({
            "success": False,
            "error": "Unauthorized",
            "message": "Authentication required to search claims by policy number.",
        }), 401

    with get_db_session() as db:
        query = db.query(Claim).filter(Claim.policy_number.ilike(clean_policy))

        # Restrict standard users to their own claims; assessors and admins can search globally
        if user_role not in ("assessor", "admin"):
            query = query.filter_by(user_id=user_id)

        claims = query.order_by(desc(Claim.created_at)).all()

        if not claims:
            return jsonify({
                "success": False,
                "error": "Not Found",
                "message": f"No claims found matching policy number '{clean_policy}'.",
                "count": 0,
                "claims": [],
            }), 404

        return jsonify({
            "success": True,
            "policy_number": clean_policy,
            "count": len(claims),
            "claims": [c.to_dict(include_evidence=True) for c in claims],
        }), 200


@claims_bp.route("/claims/search", methods=["GET"])
def search_claims():
    """Unified search endpoint for claims by Claim ID or Policy Number."""
    user_id = session.get("user_id")
    user_role = session.get("role")

    if not user_id and user_role not in ("assessor", "admin"):
        return jsonify({
            "success": False,
            "error": "Unauthorized",
            "message": "Authentication required to search claims.",
        }), 401

    query_str = request.args.get("q", "").strip()
    if not query_str:
        return jsonify({
            "success": False,
            "error": "Validation Error",
            "message": "Search query must not be empty.",
        }), 400

    with get_db_session() as db:
        query = db.query(Claim)
        if user_role not in ("assessor", "admin"):
            query = query.filter_by(user_id=user_id)

        query = query.filter(
            (Claim.claim_id.ilike(f"%{query_str}%")) | (Claim.policy_number.ilike(f"%{query_str}%"))
        )
        claims = query.order_by(desc(Claim.created_at)).all()

        return jsonify({
            "success": True,
            "query": query_str,
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


@claims_bp.route("/claims/<claim_id>/document-report", methods=["GET"])
def get_claim_document_report(claim_id: str):
    """Serves the Phase 4 document intelligence report PDF for an eligible claim."""
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
            return jsonify({
                "success": False,
                "error": "Not Found",
                "message": f"Claim with ID '{claim_id}' was not found.",
            }), 404

        if not can_user_access_claim(claim, user_id, user_role):
            if not user_id:
                return jsonify({
                    "success": False,
                    "error": "Unauthorized",
                    "message": "Authentication required to access this document intelligence report.",
                }), 401
            return jsonify({
                "success": False,
                "error": "Forbidden",
                "message": "You are not authorized to access this document intelligence report.",
            }), 403

        claim_dict = claim.to_dict(include_evidence=True)
        extracted_rows = [
            row.to_dict() for row in db.query(ExtractedInformation)
            .filter_by(claim_id=claim_id)
            .order_by(ExtractedInformation.created_at.asc())
            .all()
        ]

    try:
        pdf_bytes = generate_document_intelligence_report_pdf(
            claim_dict,
            extracted_rows,
            upload_root=current_app.config.get("UPLOAD_FOLDER"),
        )
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"document_report_{claim_id}.pdf",
        )
    except Exception as e:
        logger.error(f"Error generating document intelligence report for claim {claim_id}: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Report Generation Error",
            "message": "Failed to generate the document intelligence report.",
        }), 500


@claims_bp.route("/claims/<claim_id>/evidence/<file_type>", methods=["GET"])
def get_claim_evidence_file(claim_id: str, file_type: str):
    """Safely serves an uploaded evidence document or photograph for a claim."""
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
            return jsonify({
                "success": False,
                "error": "Not Found",
                "message": f"Claim with ID '{claim_id}' was not found.",
            }), 404

        if not can_user_access_claim(claim, user_id, user_role):
            if not user_id:
                return jsonify({
                    "success": False,
                    "error": "Unauthorized",
                    "message": "Authentication required to view evidence files.",
                }), 401
            return jsonify({
                "success": False,
                "error": "Forbidden",
                "message": "You are not authorized to view evidence for this claim.",
            }), 403

        upload_base = Path(current_app.config["UPLOAD_FOLDER"])
        target_file_path = None
        target_filename = None

        doc_type_mapping = {
            "policy": "POLICY_DOCUMENT",
            "policy_document": "POLICY_DOCUMENT",
            "claim_form": "CLAIM_FORM",
            "invoice": "INVOICE",
            "invoice_document": "INVOICE",
        }

        clean_type = file_type.lower()
        if clean_type in doc_type_mapping:
            doc = db.query(Document).filter_by(
                claim_id=claim_id,
                document_type=doc_type_mapping[clean_type],
            ).first()
            if doc and doc.file_path:
                target_file_path = upload_base / doc.file_path
                target_filename = doc.original_filename
        elif clean_type in ("image", "vehicle_image", "photo"):
            img = db.query(ClaimImage).filter_by(claim_id=claim_id).order_by(ClaimImage.created_at.desc()).first()
            if img and img.file_path:
                target_file_path = upload_base / img.file_path
                target_filename = img.original_filename

        if not target_file_path or not target_file_path.exists():
            return jsonify({
                "success": False,
                "error": "Not Found",
                "message": f"Evidence file for '{file_type}' was not found.",
            }), 404

        as_attachment = request.args.get("download", "0") == "1"
        return send_file(
            str(target_file_path),
            as_attachment=as_attachment,
            download_name=target_filename,
        )


@claims_bp.route("/claims/<claim_id>/receipt", methods=["GET"])
def get_claim_receipt(claim_id: str):
    """Generates and serves official claim submission receipt in PDF or JSON format with authorization."""
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

            try:
                with open(metadata_path, "r", encoding="utf-8") as f:
                    claim_dict = json.load(f)
            except Exception as e:
                logger.error(f"Failed to read disk metadata for claim receipt {claim_id}: {e}")
                return jsonify({
                    "success": False,
                    "error": "Server Error",
                    "message": "Failed to parse claim records.",
                }), 500

            # Enforce authorization on disk fallback receipt generation
            if not can_user_access_claim_dict(claim_dict, user_id, user_role):
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
        }), 500


@claims_bp.route("/claims/<claim_id>/replace-image", methods=["POST"])
@claims_bp.route("/claims/<claim_id>/images", methods=["POST"])
def replace_claim_image(claim_id: str):
    """Allows uploading a replacement actual accident photograph for a claim.

    Preserves the original uploaded file on disk and in history, executes
    forensic vehicle image validation on the new photograph, and updates the
    claim evidence validation status.
    """
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
            return jsonify({
                "success": False,
                "error": "Not Found",
                "message": f"Claim with ID '{claim_id}' was not found.",
            }), 404

        if not can_user_access_claim(claim, user_id, user_role):
            if not user_id:
                return jsonify({
                    "success": False,
                    "error": "Unauthorized",
                    "message": "Authentication required to replace claim evidence image.",
                }), 401
            return jsonify({
                "success": False,
                "error": "Forbidden",
                "message": "You are not authorized to modify evidence for this claim.",
            }), 403

        files_dict = request.files
        img_file = files_dict.get("vehicle_image") or files_dict.get("image") or files_dict.get("file")
        if not img_file or not img_file.filename:
            return jsonify({
                "success": False,
                "error": "Validation Error",
                "message": "No vehicle photograph file was provided in the request.",
            }), 400

        clean_img_name = secure_filename(img_file.filename)
        ext = clean_img_name.rsplit(".", 1)[-1].lower() if "." in clean_img_name else ""
        if ext not in {"jpg", "jpeg", "png"}:
            return jsonify({
                "success": False,
                "error": "Validation Error",
                "message": "Invalid file format. Vehicle photograph must be a JPEG or PNG image.",
            }), 400

        upload_base = Path(current_app.config["UPLOAD_FOLDER"])
        claim_dir = upload_base / claim_id
        images_dir = claim_dir / "images"
        images_dir.mkdir(parents=True, exist_ok=True)

        dest_img_name = f"replacement_vehicle_image_{clean_img_name}" if clean_img_name else "replacement_vehicle_image.jpg"
        target_img_path = sanitize_and_resolve_path(images_dir, dest_img_name)
        img_file.save(str(target_img_path))

        img_size_bytes = target_img_path.stat().st_size
        img_rel_path = str(target_img_path.relative_to(upload_base))

        # Forensic image validation
        validation = validate_vehicle_image(target_img_path)

        # Record replacement image in database while preserving original flagged file in audit history
        existing_img = db.query(ClaimImage).filter_by(claim_id=claim_id).order_by(ClaimImage.created_at.desc()).first()
        prev_filename = existing_img.original_filename if existing_img else "unknown"

        new_img_rec = ClaimImage(
            claim_id=claim_id,
            image_type="REPLACEMENT_VEHICLE_ACCIDENT",
            file_path=img_rel_path,
            original_filename=img_file.filename,
            stored_filename=dest_img_name,
            file_extension=ext,
            file_size=img_size_bytes,
            created_at=datetime.now(timezone.utc),
        )
        db.add(new_img_rec)
        db.commit()

        # Update metadata.json while preserving previous files in history
        metadata_path = claim_dir / "metadata.json"
        if metadata_path.exists():
            try:
                with open(metadata_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                if "archived_images" not in meta:
                    meta["archived_images"] = []
                if "vehicle_image" in meta.get("files", {}):
                    meta["archived_images"].append(meta["files"]["vehicle_image"])
                meta["files"]["vehicle_image"] = {
                    "original_name": img_file.filename,
                    "saved_as": dest_img_name,
                    "relative_path": img_rel_path,
                    "size_bytes": img_size_bytes,
                    "replaced_at": datetime.now(timezone.utc).isoformat(),
                    "validation_status": validation.get("status"),
                }
                meta["vehicle_image_validation"] = validation
                with open(metadata_path, "w", encoding="utf-8") as f:
                    json.dump(meta, f, indent=2)
            except Exception as exc:
                logger.warning(f"Could not update metadata.json for claim {claim_id}: {exc}")

        logger.info(f"Replacement vehicle photograph uploaded for claim {claim_id}: {clean_img_name} ({validation.get('status')})")

        return jsonify({
            "success": True,
            "claim_id": claim_id,
            "message": "Replacement accident photograph uploaded and evaluated successfully.",
            "original_preserved": True,
            "archived_image": prev_filename,
            "new_image": {
                "original_filename": img_file.filename,
                "stored_filename": dest_img_name,
                "relative_path": img_rel_path,
                "file_size": img_size_bytes,
            },
            "validation": validation,
        }), 200


@claims_bp.route("/claims/<claim_id>/analyze-damage", methods=["POST"])
@csrf.exempt
def analyze_claim_vehicle_damage(claim_id: str):
    """Executes AI vehicle damage detection using YOLOv8 fine-tuned on CarDD.

    Localizes damages, identifies categories, generates annotated image,
    and stores results in SQLite database.
    """
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
            return jsonify({
                "success": False,
                "error": "Not Found",
                "message": f"Claim with ID '{claim_id}' was not found.",
            }), 404

        if not can_user_access_claim(claim, user_id, user_role):
            if not user_id:
                return jsonify({
                    "success": False,
                    "error": "Unauthorized",
                    "message": "Authentication required to analyze damage for this claim.",
                }), 401
            return jsonify({
                "success": False,
                "error": "Forbidden",
                "message": "You do not have permission to analyze damage for this claim.",
            }), 403

        # Locate vehicle photograph
        upload_base = Path(current_app.config["UPLOAD_FOLDER"])
        claim_dir = upload_base / claim_id
        images_dir = claim_dir / "images"

        target_img_path = None
        claim_image_rec = None

        # Prioritize latest ClaimImage in DB
        db_img = (
            db.query(ClaimImage)
            .filter_by(claim_id=claim_id)
            .order_by(desc(ClaimImage.created_at))
            .first()
        )
        if db_img and db_img.file_path:
            candidate = upload_base / db_img.file_path
            if candidate.exists():
                target_img_path = candidate
                claim_image_rec = db_img

        # Fallback to inspecting images directory on disk
        if not target_img_path and images_dir.exists():
            replacements = list(images_dir.glob("replacement_vehicle_image_*"))
            if replacements:
                target_img_path = replacements[-1]
            else:
                vehicle_imgs = list(images_dir.glob("vehicle_image_*"))
                if vehicle_imgs:
                    target_img_path = vehicle_imgs[-1]

        if not target_img_path or not target_img_path.exists():
            return jsonify({
                "success": False,
                "error": "Missing Evidence",
                "message": "No vehicle accident photograph found for this claim.",
            }), 400

        # Forensic authenticity verification: prevent running inference on synthetic graphics/document cards
        img_validation = validate_vehicle_image(target_img_path)
        if not img_validation.get("is_valid_vehicle_photo"):
            return jsonify({
                "success": False,
                "error": "Invalid Vehicle Evidence",
                "message": (
                    f"Uploaded file '{target_img_path.name}' is flagged as {img_validation.get('status', 'invalid')} "
                    f"({img_validation.get('reason')}). Damage inspection cannot be performed on synthetic graphics or document renders. "
                    f"Please upload an authentic replacement vehicle photograph before running AI damage analysis."
                ),
                "validation": img_validation,
                "requires_replacement": True,
            }), 400

        # Allow confidence threshold override from JSON or query params
        req_json = request.get_json(silent=True) or {}
        try:
            conf_thresh = float(req_json.get("conf_threshold") or request.args.get("conf", 0.15))
        except (TypeError, ValueError):
            conf_thresh = 0.15

        # Run damage detection
        try:
            detector = VehicleDamageDetector.get_instance()
            analysis_result = detector.detect_damage(target_img_path, conf_threshold=conf_thresh)
        except Exception as exc:
            logger.error(f"Damage detection failed for claim {claim_id}: {exc}", exc_info=True)
            return jsonify({
                "success": False,
                "error": "Inference Error",
                "message": f"Computer vision analysis failed: {str(exc)}",
            }), 500

        # Generate annotated image
        annotated_filename = f"annotated_{target_img_path.name}"
        annotated_target_path = images_dir / annotated_filename
        rel_annotated_path = None
        try:
            create_annotated_image(
                target_img_path,
                analysis_result["detections"],
                output_path=annotated_target_path,
            )
            rel_annotated_path = str(annotated_target_path.relative_to(upload_base))
        except Exception as exc:
            logger.warning(f"Could not save annotated image for claim {claim_id}: {exc}")

        rel_img_path = str(target_img_path.relative_to(upload_base))

        # Store in SQLite database
        avg_conf = 0.0
        if analysis_result["detections"]:
            avg_conf = sum(d["confidence"] for d in analysis_result["detections"]) / len(analysis_result["detections"])

        now_utc = datetime.now(timezone.utc)
        analysis_record = VehicleDamageAnalysis(
            claim_id=claim_id,
            image_id=claim_image_rec.image_id if claim_image_rec else None,
            image_path=rel_img_path,
            original_image_path=rel_img_path,
            annotated_image_path=rel_annotated_path,
            model_name=analysis_result["model_name"],
            model_version=analysis_result["model_version"],
            total_detections=analysis_result["total_detections"],
            total_damages_detected=analysis_result["total_detections"],
            damage_categories=json.dumps(analysis_result["damage_categories"]),
            detected_categories=json.dumps(analysis_result["damage_categories"]),
            highest_confidence=analysis_result["highest_confidence"],
            max_confidence=analysis_result["highest_confidence"],
            average_confidence=round(avg_conf, 4),
            analysis_status="completed",
            processing_time_ms=analysis_result["processing_time_ms"],
            inference_time_ms=analysis_result["processing_time_ms"],
            device=analysis_result["device"],
            created_at=now_utc,
            updated_at=now_utc,
        )
        db.add(analysis_record)
        db.flush()

        # Add individual detection records
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
                created_at=datetime.now(timezone.utc),
            )
            db.add(detection_rec)

        db.commit()

        # Update metadata.json if present
        meta_file = claim_dir / "metadata.json"
        if meta_file.exists():
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                meta["latest_damage_analysis"] = analysis_record.to_dict()
                with open(meta_file, "w", encoding="utf-8") as f:
                    json.dump(meta, f, indent=2)
            except Exception as exc:
                logger.warning(f"Failed to update metadata.json with damage analysis: {exc}")

        logger.info(
            f"Successfully completed vehicle damage analysis for {claim_id}: "
            f"{analysis_result['total_detections']} detections ({', '.join(analysis_result['damage_categories']) or 'None'}) "
            f"in {analysis_result['processing_time_ms']}ms"
        )

        return jsonify({
            "success": True,
            "claim_id": claim_id,
            "analysis": analysis_record.to_dict(),
        }), 200


@claims_bp.route("/claims/<claim_id>/damage-analysis", methods=["GET"])
def get_claim_damage_analysis(claim_id: str):
    """Retrieves the latest vehicle damage analysis for a claim."""
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
            return jsonify({
                "success": False,
                "error": "Not Found",
                "message": f"Claim with ID '{claim_id}' was not found.",
            }), 404

        if not can_user_access_claim(claim, user_id, user_role):
            if not user_id:
                return jsonify({
                    "success": False,
                    "error": "Unauthorized",
                    "message": "Authentication required to access damage analysis.",
                }), 401
            return jsonify({
                "success": False,
                "error": "Forbidden",
                "message": "You do not have permission to access damage analysis for this claim.",
            }), 403

        latest_analysis = (
            db.query(VehicleDamageAnalysis)
            .filter_by(claim_id=claim_id)
            .order_by(desc(VehicleDamageAnalysis.id))
            .first()
        )

        if not latest_analysis:
            return jsonify({
                "success": False,
                "error": "Not Analyzed",
                "message": "No vehicle damage analysis has been executed for this claim yet.",
                "analyzed": False,
            }), 404

        return jsonify({
            "success": True,
            "claim_id": claim_id,
            "analyzed": True,
            "analysis": latest_analysis.to_dict(),
        }), 200


@claims_bp.route("/claims/<claim_id>/damage-history", methods=["GET"])
def get_claim_damage_history(claim_id: str):
    """Retrieves all vehicle damage analysis runs for a claim."""
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
            return jsonify({
                "success": False,
                "error": "Not Found",
                "message": f"Claim with ID '{claim_id}' was not found.",
            }), 404

        if not can_user_access_claim(claim, user_id, user_role):
            if not user_id:
                return jsonify({
                    "success": False,
                    "error": "Unauthorized",
                    "message": "Authentication required to view damage history.",
                }), 401
            return jsonify({
                "success": False,
                "error": "Forbidden",
                "message": "You do not have permission to view damage history for this claim.",
            }), 403

        analyses = (
            db.query(VehicleDamageAnalysis)
            .filter_by(claim_id=claim_id)
            .order_by(desc(VehicleDamageAnalysis.id))
            .all()
        )

        return jsonify({
            "success": True,
            "claim_id": claim_id,
            "total_runs": len(analyses),
            "history": [a.to_dict() for a in analyses],
        }), 200


@claims_bp.route("/claims/<claim_id>/annotated-image", methods=["GET"])
def get_claim_annotated_image(claim_id: str):
    """Streams the AI-annotated vehicle damage photograph."""
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
            return jsonify({
                "success": False,
                "error": "Not Found",
                "message": f"Claim with ID '{claim_id}' was not found.",
            }), 404

        if not can_user_access_claim(claim, user_id, user_role):
            if not user_id:
                return jsonify({
                    "success": False,
                    "error": "Unauthorized",
                    "message": "Authentication required to access annotated image.",
                }), 401
            return jsonify({
                "success": False,
                "error": "Forbidden",
                "message": "You do not have permission to access annotated image.",
            }), 403

        upload_base = Path(current_app.config["UPLOAD_FOLDER"])
        latest = (
            db.query(VehicleDamageAnalysis)
            .filter_by(claim_id=claim_id)
            .order_by(desc(VehicleDamageAnalysis.id))
            .first()
        )

        annotated_path = None
        if latest and latest.annotated_image_path:
            candidate = upload_base / latest.annotated_image_path
            if candidate.exists():
                annotated_path = candidate

        if not annotated_path:
            # Check images directory on disk
            images_dir = upload_base / claim_id / "images"
            if images_dir.exists():
                annotated_files = list(images_dir.glob("annotated_*"))
                if annotated_files:
                    annotated_path = annotated_files[-1]

        if not annotated_path or not annotated_path.exists():
            return jsonify({
                "success": False,
                "error": "Not Found",
                "message": "Annotated damage image not found. Please run damage analysis first.",
            }), 404

        return send_file(
            str(annotated_path),
            mimetype="image/jpeg",
            as_attachment=request.args.get("download") == "true",
            download_name=annotated_path.name,
        )


@claims_bp.route("/vision/status", methods=["GET"])
@claims_bp.route("/vision/metrics", methods=["GET"])
@claims_bp.route("/model/status", methods=["GET"])
@claims_bp.route("/phase5/metrics", methods=["GET"])
def get_vision_status():
    """Returns the operational status of the vehicle damage detection model and CarDD benchmark."""
    try:
        detector = VehicleDamageDetector.get_instance()
        eval_metrics = get_model_evaluation_metrics()
        return jsonify({
            "success": True,
            "status": "ready",
            "model_name": detector.model_name,
            "model_version": detector.model_version,
            "model_path": str(detector.model_path),
            "device": detector.device,
            "dataset": "CarDD",
            "classes": detector.model.names if hasattr(detector.model, "names") else {},
            "evaluation_metrics": eval_metrics.get("overall_metrics"),
            "per_class_metrics": eval_metrics.get("per_class_metrics"),
            "latency_metrics": eval_metrics.get("latency_metrics"),
            "full_evaluation": eval_metrics,
        }), 200
    except Exception as exc:
        return jsonify({
            "success": False,
            "status": "error",
            "message": str(exc),
        }), 500


