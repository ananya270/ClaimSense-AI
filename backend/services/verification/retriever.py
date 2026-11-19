"""Cross-Source Evidence and Extracted Data Retriever for Phase 7.

Aggregates structured data across Phase 4 (document OCR & extraction),
Phase 5 (computer vision vehicle damage detection), Phase 6 (NLP narrative analysis),
and primary database claim records for a specific Claim ID.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.database.models import (
    Claim,
    Document,
    ClaimImage,
    ExtractedInformation,
    VehicleDamageAnalysis,
    ClaimNLPAnalysis,
)


class CrossSourceContext:
    """Consolidated container holding all cross-source records for a claim."""

    def __init__(self, claim_id: str):
        self.claim_id = claim_id
        self.claim_record: Dict[str, Any] = {}
        self.policy_doc: Dict[str, Any] = {}
        self.claim_form: Dict[str, Any] = {}
        self.invoice: Dict[str, Any] = {}
        self.intake_submission: Dict[str, Any] = {}
        self.nlp_data: Optional[Dict[str, Any]] = None
        self.vision_data: Optional[Dict[str, Any]] = None
        self.document_inventory: List[Dict[str, Any]] = []
        self.image_inventory: List[Dict[str, Any]] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "claim_record": self.claim_record,
            "policy_doc": self.policy_doc,
            "claim_form": self.claim_form,
            "invoice": self.invoice,
            "intake_submission": self.intake_submission,
            "nlp_data": self.nlp_data,
            "vision_data": self.vision_data,
            "document_inventory": self.document_inventory,
            "image_inventory": self.image_inventory,
        }


def retrieve_cross_source_context(
    claim_id: str,
    db_session: Any,
    upload_folder: Optional[Path] = None,
) -> CrossSourceContext:
    """Retrieves and organizes all extracted evidence and metadata for a claim.
    
    Guarantees that all gathered information strictly belongs to the specified Claim ID.
    """
    ctx = CrossSourceContext(claim_id=claim_id)

    # 1. Primary Claim Record
    claim = db_session.query(Claim).filter_by(claim_id=claim_id).first()
    if claim:
        ctx.claim_record = claim.to_dict(include_evidence=False)
        ctx.intake_submission = {
            "claimant_name": claim.claimant_name,
            "policy_number": claim.policy_number,
            "vehicle_number": claim.vehicle_number,
            "accident_date": claim.accident_date,
            "claim_description": claim.claim_description,
            "status": claim.status,
            "source_label": "Intake Submission Record (Database)",
        }

    # 2. Document & Image Inventories
    docs = db_session.query(Document).filter_by(claim_id=claim_id).all()
    ctx.document_inventory = [d.to_dict() for d in docs]

    images = db_session.query(ClaimImage).filter_by(claim_id=claim_id).all()
    ctx.image_inventory = [img.to_dict() for img in images]

    # 3. Phase 4 Extracted Information Rows
    extracted_rows = db_session.query(ExtractedInformation).filter_by(claim_id=claim_id).all()
    for row in extracted_rows:
        source_type = (row.source or "").lower()
        fn = (row.source_filename or "").lower()
        val = row.field_value
        fld = row.field_name

        # Map to appropriate source bucket using source type and filename hints
        if "policy" in source_type and "claim_form" not in fn and "signed_claim" not in fn:
            target = ctx.policy_doc
            target.setdefault("source_label", "Policy Schedule Document")
            target.setdefault("filename", row.source_filename or "policy_schedule.pdf")
        elif "claim_form" in source_type or "signed_claim" in fn or "claim_form" in fn:
            target = ctx.claim_form
            target.setdefault("source_label", "Signed Claim Form")
            target.setdefault("filename", row.source_filename or "signed_claim_form.pdf")
        elif "invoice" in source_type or "estimate" in fn or "garage" in fn:
            target = ctx.invoice
            target.setdefault("source_label", "Repair Invoice / Estimate")
            target.setdefault("filename", row.source_filename or "garage_estimate.pdf")
        else:
            target = ctx.policy_doc

        # Assign extracted field value if valid
        if val is not None and str(val).strip() and str(val).strip().lower() != "none":
            target[fld] = str(val).strip()
            # Retain extraction metadata
            target[f"{fld}_confidence"] = row.confidence_score
            target[f"{fld}_page"] = row.page_number
            target[f"{fld}_evidence"] = row.supporting_text

    # 4. Phase 6 NLP Analysis Record
    nlp_rec = (
        db_session.query(ClaimNLPAnalysis)
        .filter_by(claim_id=claim_id)
        .order_by(ClaimNLPAnalysis.id.desc())
        .first()
    )
    if nlp_rec:
        ctx.nlp_data = nlp_rec.to_dict()
    else:
        # Fallback check in claim_record or metadata.json if present
        if ctx.claim_record.get("nlp_analysis"):
            ctx.nlp_data = ctx.claim_record["nlp_analysis"]
        elif upload_folder:
            meta_path = upload_folder / claim_id / "metadata.json"
            if meta_path.exists():
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    ctx.nlp_data = meta.get("latest_nlp_analysis") or meta.get("nlp_analysis")
                except Exception:
                    pass

    # 5. Phase 5 Computer Vision Damage Analysis Record
    dmg_rec = (
        db_session.query(VehicleDamageAnalysis)
        .filter_by(claim_id=claim_id)
        .order_by(VehicleDamageAnalysis.id.desc())
        .first()
    )
    if dmg_rec and dmg_rec.total_detections is not None:
        ctx.vision_data = dmg_rec.to_dict()
    else:
        # Fallback check in metadata.json
        if upload_folder:
            meta_path = upload_folder / claim_id / "metadata.json"
            if meta_path.exists():
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    dmg = meta.get("latest_damage_analysis") or meta.get("damage_analysis")
                    if dmg and isinstance(dmg, dict) and dmg.get("detections") is not None:
                        ctx.vision_data = dmg
                except Exception:
                    pass

    return ctx
