"""Document validation and safe-file handling for ClaimSense AI Phase 4."""

from __future__ import annotations

import mimetypes
import os
import uuid
from pathlib import Path
from typing import Iterable, Optional, Union

from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "png", "jpg", "jpeg"}
ALLOWED_DOCUMENT_EXTENSIONS = ALLOWED_EXTENSIONS
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg"}
DANGEROUS_EXTENSIONS = {
    "exe", "bat", "cmd", "scr", "com", "pif", "js", "jar", "vbs", "wsf", "ps1",
    "dll", "so", "dylib", "app", "msi", "sh", "bash"
}


class DocumentValidationError(ValueError):
    """Raised when a document fails validation."""


def get_file_extension(filename: str) -> str:
    """Return lowercase extension without the leading dot."""
    if not filename:
        return ""
    return Path(filename).suffix.lower().lstrip(".")


def _is_pdf_header(data: bytes) -> bool:
    return data.startswith(b"%PDF")


def _is_png_header(data: bytes) -> bool:
    return data.startswith(b"\x89PNG\r\n\x1a\n")


def _is_jpeg_header(data: bytes) -> bool:
    return data.startswith((b"\xff\xd8\xff\xe0", b"\xff\xd8\xff\xe1", b"\xff\xd8\xff\xdb"))


def _looks_like_docx(data: bytes) -> bool:
    return data.startswith(b"PK\x03\x04")


def _detect_format_from_bytes(data: bytes) -> str:
    if _is_pdf_header(data):
        return "pdf"
    if _is_png_header(data):
        return "png"
    if _is_jpeg_header(data):
        return "jpeg"
    if _looks_like_docx(data):
        return "docx"
    if data.strip() and not any(ch in data for ch in (b"\x00",)):
        return "txt"
    return "unknown"


def safe_internal_filename(original_filename: str, prefix: str = "document") -> str:
    """Create a unique, sanitized filename without path traversal risks."""
    clean_name = secure_filename(original_filename or "upload")
    if not clean_name:
        clean_name = f"{prefix}.bin"
    extension = get_file_extension(clean_name)
    safe_prefix = os.path.splitext(clean_name)[0] or prefix
    safe_prefix = secure_filename(safe_prefix) or prefix
    if extension:
        return f"{safe_prefix}_{uuid.uuid4().hex[:12]}.{extension}"
    return f"{safe_prefix}_{uuid.uuid4().hex[:12]}.bin"


def validate_document_file(
    file_obj,
    max_size_bytes: Optional[int] = None,
    allowed_extensions: Optional[Iterable[str]] = None,
) -> dict:
    """Validate uploaded document content and metadata.

    Returns a dictionary with `is_valid`, `errors`, `filename`, `safe_name`, and format metadata.
    """
    max_size_bytes = max_size_bytes or 16 * 1024 * 1024
    allowed_extensions = set((allowed_extensions or ALLOWED_EXTENSIONS))

    errors: list[str] = []
    if hasattr(file_obj, "filename"):
        original_name = getattr(file_obj, "filename", "") or ""
    elif isinstance(file_obj, (str, os.PathLike)):
        original_name = Path(file_obj).name
    else:
        original_name = ""
    filename = secure_filename(original_name)
    extension = get_file_extension(filename or original_name)
    detected_format = "unknown"

    if not filename:
        errors.append("Document filename is required.")
        return {
            "is_valid": False,
            "errors": errors,
            "filename": original_name,
            "safe_name": "",
            "extension": extension,
            "mime_type": "",
            "detected_format": detected_format,
            "size_bytes": 0,
        }

    if any(part in filename for part in ("/", "\\")):
        errors.append("Invalid document filename: path separators are not allowed.")

    if extension.lower() in DANGEROUS_EXTENSIONS:
        errors.append(f"File type '.{extension}' is not allowed for upload.")

    if extension.lower() not in {ext.lower() for ext in allowed_extensions}:
        errors.append(
            f"Unsupported file type '.{extension}'. Allowed types: {', '.join(sorted(allowed_extensions))}."
        )

    stream = getattr(file_obj, "stream", None)
    file_data = b""
    if stream is not None:
        stream.seek(0)
        file_data = stream.read(8192)
        stream.seek(0)
    else:
        file_path = Path(str(file_obj)) if isinstance(file_obj, (str, os.PathLike)) else None
        if file_path and file_path.exists():
            file_data = file_path.read_bytes()[:8192]

    if not file_data:
        errors.append("Document appears to be empty.")
    else:
        detected_format = _detect_format_from_bytes(file_data)
        if extension and detected_format == "unknown":
            errors.append("Document content does not match the declared file type.")
        elif extension and detected_format != "unknown" and extension not in {detected_format, "jpg" if detected_format == "jpeg" else ""}:
            if extension == "jpg" and detected_format == "jpeg":
                pass
            else:
                errors.append(
                    f"The uploaded file header does not match the extension '.{extension}' (detected: '{detected_format}')."
                )

    size_bytes = 0
    if hasattr(file_obj, "content_length"):
        size_bytes = int(file_obj.content_length or 0)
    if size_bytes <= 0:
        try:
            if hasattr(file_obj, "stream"):
                file_obj.stream.seek(0, os.SEEK_END)
                size_bytes = file_obj.stream.tell()
                file_obj.stream.seek(0)
            elif isinstance(file_obj, (str, os.PathLike)):
                size_bytes = Path(file_obj).stat().st_size
        except Exception:
            size_bytes = 0

    if size_bytes <= 0:
        errors.append("Unable to determine uploaded file size.")
    elif size_bytes > max_size_bytes:
        errors.append(f"Uploaded document exceeds the maximum safe size of {max_size_bytes} bytes.")

    mime_type, _ = mimetypes.guess_type(filename)
    safe_name = safe_internal_filename(filename, prefix="document")
    return {
        "is_valid": not errors,
        "errors": errors,
        "filename": original_name,
        "safe_name": safe_name,
        "extension": extension.lower(),
        "mime_type": mime_type or "application/octet-stream",
        "detected_format": detected_format,
        "size_bytes": size_bytes,
    }
