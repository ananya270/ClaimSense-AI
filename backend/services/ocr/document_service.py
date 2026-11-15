"""High-level document processing service for ClaimSense AI Phase 4."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from backend.database.db import get_db_session
from backend.database.models import ExtractedInformation
from backend.services.ocr.document_classifier import classify_document
from backend.services.ocr.document_validator import validate_document_file
from backend.services.ocr.field_extractor import extract_insurance_fields
from backend.services.ocr.text_extractor import extract_text_from_file


_VALID_FIELD_STATUSES = {
    "extracted",
    "matched",
    "mismatched",
    "not_present",
    "unreadable",
    "extraction_failed",
    "insufficient_information",
    "not_applicable",
}


def _canonicalize_status(status: Any) -> str:
    if status is None:
        return ""
    normalized = str(status).strip().lower().replace(" ", "_")
    aliases = {
        "success": "extracted",
        "extracted_value": "extracted",
        "extracted": "extracted",
        "not_found": "not_present",
        "not_found_field": "not_present",
        "not_present": "not_present",
        "failed": "extraction_failed",
        "failure": "extraction_failed",
        "extraction_failed": "extraction_failed",
        "match": "matched",
        "matched": "matched",
        "mismatch": "mismatched",
        "mismatched": "mismatched",
        "unreadable": "unreadable",
        "insufficient_information": "insufficient_information",
        "not_applicable": "not_applicable",
    }
    return aliases.get(normalized, normalized)


def _normalize_field_value(value: Any) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    if not normalized:
        return None
    return normalized


def _infer_field_status(field_value: Any, explicit_status: Any = None) -> str:
    if explicit_status is not None:
        status = _canonicalize_status(explicit_status)
        if status in _VALID_FIELD_STATUSES:
            return status
    normalized = _normalize_field_value(field_value)
    if normalized is None:
        return "not_present"
    return "extracted"


def process_document(file_path: str | Path, original_filename: str | None = None) -> Dict[str, Any]:
    """Validate, extract, classify, and parse structured information from a single document."""
    path = Path(file_path)
    source_name = original_filename or path.name

    validation = validate_document_file(path, max_size_bytes=16 * 1024 * 1024)
    if not validation["is_valid"]:
        return {
            "file": str(path),
            "original_filename": source_name,
            "is_valid": False,
            "errors": validation["errors"],
            "document_type": "unknown",
            "structured_fields": {},
            "text": "",
            "extraction_method": "validation_failed",
        }

    extraction = extract_text_from_file(path)
    text = extraction.get("text", "")
    classification = classify_document(path, text)
    fields = extract_insurance_fields(text)

    method = "pdf_text_extraction"
    if path.suffix.lower() == ".docx":
        method = "docx_text_extraction"
    elif path.suffix.lower() == ".txt":
        method = "txt_text_extraction"
    elif path.suffix.lower() in {".png", ".jpg", ".jpeg"}:
        method = "ocr_image_extraction"
    if extraction.get("ocr_used"):
        method = "ocr_fallback"

    error = extraction.get("error") or extraction.get("warning")
    if not text and not error:
        error = "No readable text was extracted from the document."

    return {
        "file": str(path),
        "original_filename": source_name,
        "is_valid": True,
        "document_type": classification.get("document_type", "other"),
        "classification_confidence": classification.get("confidence", 0.0),
        "structured_fields": fields,
        "text": text,
        "pages": extraction.get("pages", []),
        "page_count": extraction.get("page_count", len(extraction.get("pages", []))),
        "ocr_used": extraction.get("ocr_used", False),
        "error": error,
        "warning": extraction.get("warning"),
        "extraction_method": method,
    }


def save_extracted_fields(claim_id: str, extracted_rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Persist a list of extracted key/value rows to the database for a claim.

    Records with blank values are recorded with an explicit status instead of being treated as
    successful extractions. Duplicate rows are ignored when they represent the same field/value
    from the same source and document context.
    """
    records: List[Dict[str, Any]] = []
    seen: set[Tuple[str, str, str, str, str]] = set()
    with get_db_session() as session:
        for item in extracted_rows:
            field_name = str(item.get("field_name") or "unknown").strip()
            if not field_name:
                continue
            value = _normalize_field_value(item.get("field_value"))
            source = str(item.get("source") or "unknown").strip() or "unknown"
            source_filename = str(item.get("source_filename") or "").strip() or None
            page_number = item.get("page_number")
            extraction_method = str(item.get("extraction_method") or item.get("method") or "").strip() or None
            supporting_text = item.get("supporting_text")
            confidence_score = item.get("confidence_score")
            error_message = item.get("error_message")
            field_status = _infer_field_status(value, item.get("field_status"))

            dedupe_key = (
                claim_id,
                field_name.lower(),
                source.lower(),
                (source_filename or "").lower(),
                str(page_number or ""),
                (value or ""),
            )
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)

            row = ExtractedInformation(
                claim_id=claim_id,
                field_name=field_name,
                field_value=value,
                field_status=field_status,
                source=source,
                source_filename=source_filename,
                page_number=int(page_number) if page_number is not None and str(page_number).strip() else None,
                extraction_method=extraction_method,
                supporting_text=str(supporting_text).strip() if supporting_text is not None else None,
                confidence_score=float(confidence_score) if confidence_score is not None and str(confidence_score).strip() else None,
                error_message=str(error_message).strip() if error_message is not None else None,
                evaluation_metadata=item.get("evaluation_metadata"),
            )
            session.add(row)
            records.append({
                "claim_id": claim_id,
                "field_name": field_name,
                "field_value": row.field_value,
                "field_status": row.field_status,
                "source": source,
                "source_filename": source_filename,
                "page_number": row.page_number,
                "extraction_method": extraction_method,
                "supporting_text": row.supporting_text,
                "confidence_score": row.confidence_score,
                "error_message": row.error_message,
                "evaluation_metadata": row.evaluation_metadata,
            })
    return records


def ingest_extracted_claim_data(claim_id: str, processed_documents: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert processed document results into the database-backed `extracted_information` rows."""
    rows: List[Dict[str, Any]] = []
    for document in processed_documents:
        doc_type = str(document.get("document_type") or "unknown")
        source_filename = str(document.get("original_filename") or "unknown").strip() or "unknown"
        extraction_method = str(document.get("extraction_method") or "document_parsing").strip()
        text = str(document.get("text") or "")
        pages = document.get("pages") or []
        page_texts = []
        for page in pages:
            if isinstance(page, dict):
                page_text = str(page.get("text") or "")
                page_number = page.get("page_number")
                page_texts.append((page_number, page_text))

        fields = document.get("structured_fields", {}) or {}
        for name, value in fields.items():
            if name in {"raw_text_length"}:
                continue
            support = ""
            if value:
                for line in text.splitlines():
                    if str(value).lower() in line.lower():
                        support = line.strip()
                        break
                if not support:
                    support = str(value)[:120]
            else:
                support = None
            rows.append({
                "field_name": name,
                "field_value": value,
                "source": doc_type,
                "source_filename": source_filename,
                "page_number": page_texts[0][0] if page_texts else None,
                "extraction_method": extraction_method,
                "supporting_text": support,
                "field_status": _infer_field_status(value),
                "error_message": document.get("error"),
            })
    return save_extracted_fields(claim_id, rows)


def summarize_dataset(dataset_root: str | Path) -> Dict[str, Any]:
    """Provide a lightweight summary of dataset folders used for experimentation."""
    dataset_path = Path(dataset_root)
    if not dataset_path.exists():
        return {"dataset_root": str(dataset_path), "files": [], "count": 0}

    results = []
    for child in sorted(dataset_path.iterdir()):
        results.append({
            "name": child.name,
            "type": "directory" if child.is_dir() else "file",
            "size": child.stat().st_size if child.is_file() else 0,
        })
    return {"dataset_root": str(dataset_path), "files": results, "count": len(results)}
