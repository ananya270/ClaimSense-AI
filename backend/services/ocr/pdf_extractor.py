"""PDF text extraction with OCR fallback for digital and scanned documents."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.services.ocr.ocr_engine import ocr_image


class DocumentExtractionError(ValueError):
    """Raised when a document cannot be opened or extracted safely."""


def _safe_pdf_pages(pdf_path: str) -> List[str]:
    try:
        import fitz  # PyMuPDF
    except ImportError:
        res = _extract_pdf_text_builtin(Path(pdf_path))
        return [p.get("text", "") for p in res.get("pages", [])]

    try:
        doc = fitz.open(pdf_path)
    except Exception:
        raise DocumentExtractionError("The PDF is unreadable or corrupted.")

    try:
        extracted_pages: List[str] = []
        for page_number in range(len(doc)):
            page = doc.load_page(page_number)
            text = page.get_text("text").strip()
            extracted_pages.append(text)
        return extracted_pages
    finally:
        doc.close()


def _extract_pdf_text_builtin(path: Path) -> Dict[str, Any]:
    """Pure-Python fallback for extracting text from standard and FlateDecode PDF streams."""
    try:
        data = path.read_bytes()
    except Exception as exc:
        raise DocumentExtractionError(f"Could not read PDF file: {exc}") from exc

    page_matches = list(re.finditer(rb"/Type\s*/Page\b", data))
    page_count = max(1, len(page_matches)) if page_matches else 1

    text_parts: List[str] = []
    stream_matches = re.finditer(rb"stream[\r\n]+(.*?)[\r\n]+endstream", data, re.DOTALL)
    for m in stream_matches:
        raw_stream = m.group(1)
        decompressed = None
        try:
            import zlib
            decompressed = zlib.decompress(raw_stream)
        except Exception:
            decompressed = raw_stream

        # Extract (text) Tj
        tj_matches = re.findall(rb"\((.*?)\)\s*Tj", decompressed)
        for tj in tj_matches:
            try:
                decoded = tj.replace(b"\\(", b"(").replace(b"\\)", b")").replace(b"\\\\", b"\\")
                val = decoded.decode("latin-1", errors="ignore").strip()
                if val:
                    text_parts.append(val)
            except Exception:
                pass

        # Extract [(text)...] TJ
        tj_arrays = re.findall(rb"\[(.*?)\]\s*TJ", decompressed)
        for arr in tj_arrays:
            parts = re.findall(rb"\((.*?)\)", arr)
            combined = "".join(p.replace(b"\\(", b"(").replace(b"\\)", b")").decode("latin-1", errors="ignore") for p in parts).strip()
            if combined:
                text_parts.append(combined)

    full_text = "\n".join(text_parts).strip()
    pages = [{"page_number": 1, "text": full_text, "ocr_used": False}] if full_text else []
    return {
        "document_type": "text_pdf" if full_text else "pdf",
        "page_count": page_count,
        "full_text": full_text,
        "pages": pages,
        "ocr_used": False,
        "is_empty": not bool(full_text),
        "warning": None if full_text else "No text extracted by built-in PDF stream reader.",
    }


def _ocr_pdf_page(pdf_path: str, page_number: int) -> str:
    try:
        import fitz  # PyMuPDF
    except ImportError:
        return ""

    try:
        doc = fitz.open(pdf_path)
        page = doc.load_page(page_number)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        tmp_path = f"{pdf_path}.page{page_number + 1}.png"
        pix.save(tmp_path)
        try:
            return ocr_image(tmp_path)
        finally:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
    except Exception:
        return ""
    finally:
        try:
            doc.close()
        except Exception:
            pass


def extract_pdf_text(pdf_path: str | os.PathLike[str], ocr_fallback: bool = True) -> Dict[str, Any]:
    """Extract native PDF text page by page and fall back to OCR when needed."""
    path = Path(pdf_path)
    if not path.exists():
        raise DocumentExtractionError(f"PDF file does not exist: {path}")

    if path.suffix.lower() != ".pdf":
        raise DocumentExtractionError("File does not have a .pdf extension.")

    pages: List[Dict[str, Any]] = []
    extracted_texts: List[str] = []
    try:
        import fitz  # PyMuPDF
    except ImportError:
        return _extract_pdf_text_builtin(path)

    try:
        doc = fitz.open(str(path))
    except Exception as exc:
        raise DocumentExtractionError("The PDF file is corrupted or cannot be opened.") from exc

    try:
        if doc.is_encrypted:
            try:
                if not doc.authenticate(""):
                    return {
                        "document_type": "encrypted_pdf",
                        "page_count": len(doc),
                        "full_text": "",
                        "pages": [],
                        "ocr_used": False,
                        "is_empty": True,
                        "warning": "The PDF is password-protected and cannot be processed without a password.",
                    }
            except Exception:
                return {
                    "document_type": "encrypted_pdf",
                    "page_count": len(doc),
                    "full_text": "",
                    "pages": [],
                    "ocr_used": False,
                    "is_empty": True,
                    "warning": "The PDF is password-protected and cannot be processed without a password.",
                }

        page_count = len(doc)
        for index in range(page_count):
            page = doc.load_page(index)
            text = (page.get_text("text") or "").strip()
            used_ocr = False
            if ocr_fallback and len(text) < 40:
                ocr_text = _ocr_pdf_page(str(path), index)
                if ocr_text.strip():
                    text = ocr_text.strip()
                    used_ocr = True
            extracted_texts.append(text)
            pages.append({
                "page_number": index + 1,
                "text": text,
                "ocr_used": used_ocr,
            })

        full_text = "\n\n".join(page["text"] for page in pages).strip()
        non_empty = [page for page in pages if page["text"].strip()]
        if not non_empty:
            document_type = "scanned_pdf"
        elif len(non_empty) < len(pages):
            document_type = "mixed_pdf"
        else:
            document_type = "text_pdf"

        warning = None
        if not full_text.strip():
            warning = "No readable text was extracted from this PDF. The file may be scanned, malformed, image-backed, or require OCR support that is unavailable in the environment."

        return {
            "document_type": document_type,
            "page_count": page_count,
            "full_text": full_text,
            "pages": pages,
            "ocr_used": any(page["ocr_used"] for page in pages),
            "is_empty": not bool(full_text.strip()),
            "warning": warning,
            "error": warning,
        }
    finally:
        doc.close()


def extract_pdf_pages(path: str | os.PathLike[str]) -> List[str]:
    """Compatibility helper returning plain page text strings."""
    result = extract_pdf_text(path)
    return [page.get("text", "") for page in result.get("pages", [])]


def extract_pdf_keywords(path: str | os.PathLike[str]) -> List[str]:
    """Extract a shallow keyword list from PDF text to support classification."""
    text = extract_pdf_text(path).get("full_text", "")
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9/\-]+", text)
    return [token.lower() for token in tokens if len(token) > 3][:30]
