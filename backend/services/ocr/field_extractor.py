"""Insurance document field extraction and normalization."""

from __future__ import annotations

import re
from typing import Any, Dict


def _clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def extract_insurance_fields(text: str) -> Dict[str, Any]:
    """Roughly extract claimant, policy, vehicle, accident, and financial fields from document text."""
    text = text or ""
    policy = ""
    claimant_name = ""
    vehicle_number = ""
    accident_date = ""
    claim_amount = ""
    incident_description = ""
    repair_breakdown_items = []
    repair_items = []

    # Policy Number
    pm = re.search(
        r"(?:policy\s*(?:number|no|no\.)\s*[:#-]?\s*)([A-Z0-9][A-Z0-9\-]{3,})",
        text,
        flags=re.IGNORECASE,
    )
    if pm:
        policy = pm.group(1).strip()

    # Claimant Name - bound before newline or subsequent known field labels
    cm = re.search(
        r"(?:claimant\s*(?:name|full\s*name)?|insured\s*name|name\s*of\s*claimant)[\s:]+([A-Za-z'\.\-]+(?:\s+[A-Za-z'\.\-]+)*)(?=\r|\n|policy|vehicle|accident|date|amount|$)",
        text,
        flags=re.IGNORECASE,
    )
    if cm:
        val = cm.group(1).strip()
        if not re.search(r"^(?:policy|vehicle|registration|date|accident)", val, re.IGNORECASE):
            claimant_name = val

    # Vehicle Registration / Plate
    vm = re.search(
        r"(?:vehicle\s*(?:registration|no|number)|reg\s*(?:no|number)|number\s*plate)[\s:]+([A-Z]{2}[\-0-9A-Z]{2,})",
        text,
        flags=re.IGNORECASE,
    )
    if vm:
        vehicle_number = vm.group(1).upper().strip()

    # Accident Date
    dm = re.search(
        r"(?:accident\s*date|date\s*of\s*accident|claim\s*date|incident\s*date)[\s:]+(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4})",
        text,
        flags=re.IGNORECASE,
    )
    if dm:
        accident_date = dm.group(1).strip()

    # Claim / Invoice Amount
    am = re.search(
        r"(?:claim\s*amount|total\s*amount|estimate\s*amount|repair\s*cost)[\s:]+(?:INR\s*)?([0-9,]+(?:\.\d{2})?)",
        text,
        flags=re.IGNORECASE,
    )
    if am:
        claim_amount = am.group(1).replace(",", "").strip()

    # Explicit Incident Description (from claim form or narrative block)
    im = re.search(
        r"(?:claim\s*description|incident\s*(?:description|details)|accident\s*(?:description|details)|description\s*of\s*(?:accident|incident|claim))[\s:]+([^\r\n]+)",
        text,
        flags=re.IGNORECASE,
    )
    if im:
        incident_description = im.group(1).strip()

    # Repair cost breakdown and description from invoice line items
    for line in text.splitlines():
        line = line.strip()
        m = re.match(r"^([A-Za-z\s]+)[\s:\-]+(?:INR\s*)?([0-9,]+(?:\.\d{2})?)$", line)
        if m:
            item_name = m.group(1).strip()
            item_cost = m.group(2).replace(",", "").strip()
            if item_name.lower() not in {
                "claim amount",
                "total amount",
                "policy number",
                "accident date",
                "vehicle registration",
                "claimsense ai",
            }:
                repair_breakdown_items.append(f"{item_name}: {item_cost}")
                repair_items.append(item_name)

    repair_cost_breakdown = "; ".join(repair_breakdown_items)
    repair_description = "; ".join(repair_items)

    return {
        "claimant_name": _clean(claimant_name),
        "policy_number": _clean(policy),
        "vehicle_number": _clean(vehicle_number),
        "accident_date": _clean(accident_date),
        "incident_description": _clean(incident_description),
        "repair_description": _clean(repair_description),
        "claim_amount": _clean(claim_amount),
        "repair_cost_breakdown": _clean(repair_cost_breakdown),
        "claim_description": _clean(incident_description or repair_description),
        "raw_text_length": len(text.strip()),
    }
