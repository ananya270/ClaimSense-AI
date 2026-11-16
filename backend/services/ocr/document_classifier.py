"""Document classification helpers for insurance evidence documents."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def classify_document(file_path: str | Path | None = None, text: str = "") -> Dict[str, Any]:
    """Classify a document as policy, claim form, invoice, or other based on content keywords and file type."""
    source_text = (text or "").lower().strip()
    filename = (str(file_path or "")).lower()
    ext = Path(file_path).suffix.lower() if file_path else ""

    # Photographic evidence without structured document text should not be classified as a textual document
    if ext in {".jpg", ".jpeg", ".png"} and len(source_text) < 15:
        return {
            "document_type": "image",
            "confidence": 0.95,
            "source_text_length": len(source_text),
        }

    if any(token in source_text for token in ["policy", "coverage", "schedule", "insured"]):
        label = "policy_document"
        confidence = 0.87
    elif any(token in source_text for token in ["claim form", "claimant", "accident date", "vehicle number"]):
        label = "claim_form"
        confidence = 0.84
    elif any(token in source_text for token in ["invoice", "repair estimate", "garage", "amount due", "bill"]):
        label = "invoice_document"
        confidence = 0.88
    elif ext not in {".jpg", ".jpeg", ".png"} and any(token in filename for token in ["policy", "schedule"]):
        label = "policy_document"
        confidence = 0.72
    elif ext not in {".jpg", ".jpeg", ".png"} and any(token in filename for token in ["claim", "form"]):
        label = "claim_form"
        confidence = 0.7
    elif ext not in {".jpg", ".jpeg", ".png"} and any(token in filename for token in ["invoice", "estimate", "bill"]):
        label = "invoice_document"
        confidence = 0.7
    else:
        label = "other"
        confidence = 0.5

    return {
        "document_type": label,
        "confidence": confidence,
        "source_text_length": len(source_text),
    }
