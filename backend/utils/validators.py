"""Validation and sanitization utilities for ClaimSense AI."""
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
    return bool(re.match(r"^CLM-\d{8}-[A-Z0-9]{4}$", claim_id))


def get_file_extension(filename: str) -> str:
    """Returns lowercase file extension without leading dot."""
    if "." in filename:
        return filename.rsplit(".", 1)[1].lower()
    return ""


def validate_claim_form_fields(data: Dict[str, str]) -> Tuple[bool, List[str]]:
    """Validates presence and basic format of required claim text fields."""
    errors = []
    for field in REQUIRED_TEXT_FIELDS:
        value = data.get(field, "").strip() if data.get(field) else ""
        if not value:
            errors.append(f"Missing required field: '{field}'")

    # Validate date format (YYYY-MM-DD or DD/MM/YYYY)
    accident_date = data.get("accident_date", "").strip() if data.get("accident_date") else ""
    if accident_date:
        valid_date = False
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
            try:
                datetime.strptime(accident_date, fmt)
                valid_date = True
                break
            except ValueError:
                continue
        if not valid_date:
            errors.append(
                f"Invalid date format for 'accident_date': '{accident_date}'. Expected YYYY-MM-DD."
            )

    return (len(errors) == 0, errors)


def validate_claim_files(files_dict) -> Tuple[bool, List[str]]:
    """Validates that all required files are present and match allowed extensions."""
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

        if file_key == "vehicle_image":
            if ext not in ALLOWED_IMAGE_EXTENSIONS:
                errors.append(
                    f"File '{file_key}' has invalid format '.{ext}'. Allowed formats: {', '.join(sorted(ALLOWED_IMAGE_EXTENSIONS))}."
                )
        else:
            if ext not in ALLOWED_DOCUMENT_EXTENSIONS:
                errors.append(
                    f"File '{file_key}' has invalid format '.{ext}'. Allowed formats: {', '.join(sorted(ALLOWED_DOCUMENT_EXTENSIONS))}."
                )

    return (len(errors) == 0, errors)


def sanitize_and_resolve_path(base_dir: Path, filename: str) -> Path:
    """Secures filename and prevents path traversal attacks."""
    clean_name = secure_filename(filename)
    if not clean_name:
        clean_name = f"file_{secrets.token_hex(4)}"

    target_path = (base_dir / clean_name).resolve()
    base_resolved = base_dir.resolve()

    # Verify target stays strictly inside base_dir
    if not str(target_path).startswith(str(base_resolved)):
        raise ValueError(f"Path traversal detected for filename: {filename}")

    return target_path
