"""DOCX paragraph, table, header, and footer text extraction.

This module is prepared for Phase 4 OCR and multi-format document processing.
It is isolated to prevent broken imports during Phase 3 operations.
"""
from pathlib import Path
from typing import List
from zipfile import BadZipFile, ZipFile

from backend.services.ocr.pdf_extractor import DocumentExtractionError

try:
    from docx import Document as WordDocument
    from docx.opc.exceptions import PackageNotFoundError
except ImportError:  # pragma: no cover - dependency may be optional at runtime.
    WordDocument = None
    PackageNotFoundError = Exception


def extract_docx(path: Path) -> str:
    """Extract text from paragraphs, tables, and section headers/footers."""
    if WordDocument is None:
        raise DocumentExtractionError("python-docx is not installed; DOCX extraction is unavailable.")

    try:
        with ZipFile(path) as archive:
            members = archive.infolist()
            if len(members) > 2000 or sum(member.file_size for member in members) > 64 * 1024 * 1024:
                raise DocumentExtractionError(
                    "The DOCX expands beyond the 64 MB processing limit."
                )
        document = WordDocument(path)
    except DocumentExtractionError:
        raise
    except (PackageNotFoundError, BadZipFile, OSError, ValueError, KeyError) as exc:
        raise DocumentExtractionError("The DOCX file is corrupt or cannot be opened.") from exc

    content: List[str] = []
    content.extend(paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip())
    for table in document.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            if any(cells):
                content.append(" | ".join(cells))
    for section in document.sections:
        for region in (section.header, section.footer):
            content.extend(
                paragraph.text.strip()
                for paragraph in region.paragraphs
                if paragraph.text.strip()
            )
    return "\n".join(content)
