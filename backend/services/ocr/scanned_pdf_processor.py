"""Scanned PDF processing utilities relying on OCR for page-level extraction."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List

from backend.services.ocr.ocr_engine import ocr_image


def extract_scanned_pdf(pdf_path: str | os.PathLike[str]) -> Dict[str, Any]:
    """Rasterize scanned PDF pages and OCR each page individually."""
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"Scanned PDF does not exist: {pdf_path}")

    try:
        import fitz  # PyMuPDF
    except ImportError:
        return {
            "document_type": "scanned_pdf",
            "pages": [],
            "full_text": "",
            "ocr_used": False,
            "warning": "PyMuPDF is not installed; scanned PDF OCR is unavailable.",
        }

    try:
        doc = fitz.open(str(pdf_path))
    except Exception as exc:
        raise ValueError(f"The PDF is unreadable or corrupted: {exc}") from exc

    pages: List[Dict[str, Any]] = []
    texts: List[str] = []
    try:
        for page_number in range(len(doc)):
            page = doc.load_page(page_number)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            temp_image = pdf_path.with_name(f"{pdf_path.stem}_page_{page_number + 1}.png")
            pix.save(str(temp_image))
            try:
                text = ocr_image(temp_image)
            finally:
                try:
                    temp_image.unlink(missing_ok=True)
                except TypeError:
                    try:
                        temp_image.unlink()
                    except OSError:
                        pass
            texts.append(text)
            pages.append({"page_number": page_number + 1, "text": text})
        return {
            "document_type": "scanned_pdf",
            "pages": pages,
            "full_text": "\n\n".join(texts).strip(),
            "ocr_used": True,
            "is_empty": not bool("\n\n".join(texts).strip()),
        }
    finally:
        doc.close()
