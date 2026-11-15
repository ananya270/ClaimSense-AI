"""Phase 4 OCR and document processing services for ClaimSense AI."""

from backend.services.ocr.document_classifier import classify_document
from backend.services.ocr.document_service import (
    ingest_extracted_claim_data,
    process_document,
    save_extracted_fields,
    summarize_dataset,
)
from backend.services.ocr.document_validator import validate_document_file
from backend.services.ocr.docx_extractor import extract_docx
from backend.services.ocr.field_extractor import extract_insurance_fields
from backend.services.ocr.image_preprocessor import preprocess_image
from backend.services.ocr.ocr_engine import ocr_image, perform_ocr
from backend.services.ocr.pdf_extractor import DocumentExtractionError, extract_pdf_text
from backend.services.ocr.scanned_pdf_processor import extract_scanned_pdf
from backend.services.ocr.text_extractor import extract_text_from_file

__all__ = [
    "DocumentExtractionError",
    "classify_document",
    "extract_docx",
    "extract_insurance_fields",
    "extract_pdf_text",
    "extract_scanned_pdf",
    "extract_text_from_file",
    "ingest_extracted_claim_data",
    "ocr_image",
    "perform_ocr",
    "preprocess_image",
    "process_document",
    "save_extracted_fields",
    "summarize_dataset",
    "validate_document_file",
]
