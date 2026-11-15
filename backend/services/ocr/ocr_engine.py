"""OCR helpers for image and scanned-document text extraction."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from backend.services.ocr.image_preprocessor import preprocess_image


def ocr_image(image_path: str | Path, preprocess: bool = True) -> str:
    """Run OCR on an image using pytesseract if available."""
    image_path = Path(image_path)
    if not image_path.exists():
        return ""

    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return ""

    source = str(preprocess_image(str(image_path)) if preprocess else image_path)
    try:
        result = pytesseract.image_to_string(Image.open(source), config="--psm 6")
    except Exception:
        result = ""
    return result.strip()


def perform_ocr(file_path: str | Path) -> str:
    """Convenience wrapper for OCR of images or scanned page snapshots."""
    return ocr_image(file_path)
