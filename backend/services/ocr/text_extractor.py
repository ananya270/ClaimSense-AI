"""Text extraction utilities for TXT, PDF, DOCX, and image-backed documents."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from backend.services.ocr.docx_extractor import extract_docx
from backend.services.ocr.pdf_extractor import DocumentExtractionError, extract_pdf_text


def extract_txt_file(path: str | Path) -> str:
    """Read plain text files with UTF-8 fallback to Latin-1."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Text file does not exist: {file_path}")

    text = file_path.read_bytes()
    for encoding in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            return text.decode(encoding)
        except UnicodeDecodeError:
            continue
    return text.decode("utf-8", errors="replace")


def extract_text_from_file(path: str | Path) -> Dict[str, Any]:
    """Extract text from supported file types and return a normalized result dict."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")

    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        try:
            result = extract_pdf_text(file_path)
            error = result.get("error") or result.get("warning")
            return {
                "document_type": result.get("document_type", "pdf"),
                "text": result.get("full_text", ""),
                "page_count": result.get("page_count", 0),
                "pages": result.get("pages", []),
                "is_empty": result.get("is_empty", True),
                "ocr_used": result.get("ocr_used", False),
                "error": error,
                "warning": result.get("warning"),
            }
        except DocumentExtractionError as exc:
            return {"document_type": "pdf", "text": "", "pages": [], "error": str(exc), "is_empty": True}
    if suffix == ".docx":
        try:
            text = extract_docx(file_path)
            return {"document_type": "docx", "text": text, "pages": [], "is_empty": not bool(text.strip())}
        except Exception as exc:
            return {"document_type": "docx", "text": "", "pages": [], "error": str(exc), "is_empty": True}
    if suffix == ".txt":
        text = extract_txt_file(file_path)
        return {"document_type": "txt", "text": text, "pages": [], "is_empty": not bool(text.strip())}
    if suffix.lower() in {".png", ".jpg", ".jpeg"}:
        from backend.services.ocr.ocr_engine import ocr_image

        text = ocr_image(str(file_path))
        return {"document_type": "image", "text": text, "pages": [], "is_empty": not bool(text.strip())}
    return {"document_type": "unknown", "text": "", "pages": [], "is_empty": True}
