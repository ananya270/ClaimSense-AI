"""Validation and sanitization utilities for ClaimSense AI (Hardened)."""
import os
import re
import secrets
import string
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple
from werkzeug.utils import secure_filename

# Allowed file extensions per document category
ALLOWED_DOCUMENT_EXTENSIONS = {"pdf", "docx", "png", "jpg", "jpeg"}
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg"}

# Required form fields
REQUIRED_TEXT_FIELDS = [
    "claimant_name",
    "policy_number",
    "vehicle_number",
    "accident_date",
    "claim_description",
]

# Required upload files
REQUIRED_FILE_FIELDS = [
    "policy_document",
    "claim_form",
    "invoice_document",
    "vehicle_image",
]


def generate_claim_id() -> str:
    """Generates a standardized Claim ID in the format: CLM-YYYYMMDD-XXXX."""
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    chars = string.ascii_uppercase + string.digits
    random_suffix = "".join(secrets.choice(chars) for _ in range(4))
    return f"CLM-{date_str}-{random_suffix}"


def is_valid_claim_id_format(claim_id: str) -> bool:
    """Verifies if a claim ID matches the CLM-YYYYMMDD-XXXX pattern."""
    if not claim_id or not isinstance(claim_id, str):
        return False
    return bool(re.match(r"^CLM-\d{8}-[A-Z0-9]{4}$", claim_id))


def get_file_extension(filename: str) -> str:
    """Returns lowercase file extension without leading dot."""
    if filename and "." in filename:
        return filename.rsplit(".", 1)[1].lower()
    return ""


def validate_claim_form_fields(data: Dict[str, str]) -> Tuple[bool, List[str]]:
    """Validates presence, length, and basic format of required claim text fields."""
    errors = []
    for field in REQUIRED_TEXT_FIELDS:
        value = data.get(field, "").strip() if data.get(field) else ""
        if not value:
            errors.append(f"Missing required field: '{field}'")
        elif len(value) > 2000:
            errors.append(f"Field '{field}' exceeds maximum allowed length.")

    # Validate date format (YYYY-MM-DD or common standard separators)
    accident_date = data.get("accident_date", "").strip() if data.get("accident_date") else ""
    if accident_date:
        valid_date = False
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
            try:
                dt = datetime.strptime(accident_date, fmt)
                # Ensure date is reasonable (not in far future)
                if dt.year < 1990 or dt.year > 2100:
                    break
                valid_date = True
                break
            except ValueError:
                continue
        if not valid_date:
            errors.append(
                f"Invalid date format for 'accident_date': '{accident_date}'. Expected YYYY-MM-DD."
            )

    return (len(errors) == 0, errors)


MAGIC_BYTES = {
    "pdf": [b"%PDF"],
    "jpg": [b"\xff\xd8\xff"],
    "jpeg": [b"\xff\xd8\xff"],
    "png": [b"\x89PNG"],
    "docx": [b"PK\x03\x04"],
}


def is_valid_magic_bytes(stream, ext: str) -> bool:
    """Verifies that the file stream matches known magic byte signatures."""
    signatures = MAGIC_BYTES.get(ext.lower())
    if not signatures:
        return True
    try:
        header = stream.read(512)
        if hasattr(stream, "seek"):
            stream.seek(0)
    except Exception:
        return False
    return any(header.startswith(sig) for sig in signatures)


def validate_claim_files(files_dict) -> Tuple[bool, List[str]]:
    """Validates file presence, extensions, non-zero size, and magic byte signatures."""
    errors = []

    for file_key in REQUIRED_FILE_FIELDS:
        file_obj = files_dict.get(file_key)
        if not file_obj or not file_obj.filename or file_obj.filename.strip() == "":
            errors.append(f"Missing required file: '{file_key}'")
            continue

        filename = file_obj.filename
        ext = get_file_extension(filename)

        if not ext:
            errors.append(f"File '{file_key}' must have a valid file extension.")
            continue

        # Extension check
        if file_key == "vehicle_image":
            if ext not in ALLOWED_IMAGE_EXTENSIONS:
                errors.append(
                    f"File '{file_key}' has invalid format '.{ext}'. Allowed formats: {', '.join(sorted(ALLOWED_IMAGE_EXTENSIONS))}."
                )
                continue
        else:
            if ext not in ALLOWED_DOCUMENT_EXTENSIONS:
                errors.append(
                    f"File '{file_key}' has invalid format '.{ext}'. Allowed formats: {', '.join(sorted(ALLOWED_DOCUMENT_EXTENSIONS))}."
                )
                continue

        # File content inspection (0-byte check & signature verification)
        stream = getattr(file_obj, "stream", file_obj)
        if hasattr(stream, "read") and hasattr(stream, "seek"):
            try:
                header = stream.read(512)
                stream.seek(0)
            except Exception as e:
                errors.append(f"Could not read content from '{file_key}'.")
                continue

            if len(header) == 0:
                errors.append(f"File '{file_key}' is empty (0 bytes).")
                continue

            if not is_valid_magic_bytes(stream, ext):
                errors.append(
                    f"File '{file_key}' content signature does not match declared extension '.{ext}'."
                )

    return (len(errors) == 0, errors)


def sanitize_and_resolve_path(base_dir: Path, filename: str) -> Path:
    """Secures filename and prevents path traversal attacks."""
    if not filename or "\x00" in filename:
        filename = f"file_{secrets.token_hex(4)}.bin"

    if ".." in filename or filename.startswith("/") or filename.startswith("\\"):
        raise ValueError(f"Path traversal detected for filename: {filename}")

    clean_name = secure_filename(filename)
    if not clean_name:
        clean_name = f"file_{secrets.token_hex(4)}.bin"

    base_resolved = base_dir.resolve()
    target_path = (base_dir / clean_name).resolve()

    # Verify target stays strictly inside base_dir
    try:
        target_path.relative_to(base_resolved)
    except ValueError:
        raise ValueError(f"Path traversal detected for filename: {filename}")

    return target_path
