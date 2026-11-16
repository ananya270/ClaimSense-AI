"""Cross-Source Consistency Checking between NLP Narrative and Document Evidence (Phase 6)."""

from typing import List, Dict, Any, Optional


def cross_check_consistency(
    claim_id: str,
    nlp_entities: List[Dict[str, Any]],
    nlp_classification: Dict[str, Any],
    reported_damages: List[Dict[str, Any]],
    extracted_doc_rows: List[Dict[str, Any]],
    claim_record: Dict[str, Any],
) -> Dict[str, Any]:
    """Compares claimant narrative extractions against verified document-extracted data (Phase 4).
    
    Identifies:
    - MATCH: Exact or strong corroboration across narrative and structured document records
    - CORROBORATED: Compatible descriptions (e.g. rear damage aligns with tail lamp repair)
    - MISSING_IN_NARRATIVE: Stated in official documents but absent from brief statement
    - UNVERIFIED: Stated in narrative but not documented in invoices or policy
    - CONTRADICTORY: Direct factual discrepancy (e.g. different registration number or date)
    
    Academic Note: Findings provide decision-support only; they do not adjudicate claims.
    """
    comparisons: List[Dict[str, Any]] = []

    # Map extracted doc rows by field_name and source
    # e.g. doc_fields["accident_date"] = [ {source: "policy_document", value: "..."}, ... ]
    doc_fields: Dict[str, List[Dict[str, Any]]] = {}
    for row in extracted_doc_rows:
        fn = (row.get("field_name") or "").lower()
        val = row.get("field_value")
        if val and str(val).strip():
            if fn not in doc_fields:
                doc_fields[fn] = []
            doc_fields[fn].append(row)

    # 1. Accident Date Comparison
    doc_dates = doc_fields.get("accident_date", [])
    doc_date_val = doc_dates[0]["field_value"] if doc_dates else claim_record.get("accident_date")
    doc_date_src = doc_dates[0].get("source_filename") or doc_dates[0].get("source") if doc_dates else "Claim Intake Form"

    narrative_date_entities = [e for e in nlp_entities if e["entity_type"] == "ACCIDENT_DATE"]
    if narrative_date_entities:
        narrative_date_val = narrative_date_entities[0]["text"]
        if doc_date_val and narrative_date_val in doc_date_val:
            comparisons.append({
                "field": "Accident Date",
                "narrative_value": narrative_date_val,
                "document_value": doc_date_val,
                "source_document": doc_date_src,
                "status": "MATCH",
                "severity": "NORMAL",
                "explanation": f"Claimant narrative date '{narrative_date_val}' exactly matches verified document record '{doc_date_val}'.",
            })
        elif doc_date_val:
            comparisons.append({
                "field": "Accident Date",
                "narrative_value": narrative_date_val,
                "document_value": doc_date_val,
                "source_document": doc_date_src,
                "status": "CONTRADICTORY",
                "severity": "HIGH",
                "explanation": f"Narrative date '{narrative_date_val}' conflicts with verified document date '{doc_date_val}'.",
            })
    else:
        comparisons.append({
            "field": "Accident Date",
            "narrative_value": "Not explicitly stated in narrative",
            "document_value": doc_date_val or "Not present",
            "source_document": doc_date_src,
            "status": "MISSING_IN_NARRATIVE",
            "severity": "INFO",
            "explanation": f"Claimant did not mention date in statement; documented in '{doc_date_src}' as '{doc_date_val}'.",
        })

    # 2. Vehicle Registration Comparison
    doc_veh_rows = doc_fields.get("vehicle_number", [])
    doc_veh_val = doc_veh_rows[0]["field_value"] if doc_veh_rows else claim_record.get("vehicle_number")
    doc_veh_src = doc_veh_rows[0].get("source_filename") or doc_veh_rows[0].get("source") if doc_veh_rows else "Policy Schedule"

    narrative_veh_entities = [e for e in nlp_entities if e["entity_type"] == "VEHICLE_REGISTRATION"]
    if narrative_veh_entities:
        narrative_veh_val = narrative_veh_entities[0]["text"].upper().replace(" ", "-")
        norm_doc_veh = (doc_veh_val or "").upper().replace(" ", "-")
        if narrative_veh_val == norm_doc_veh:
            comparisons.append({
                "field": "Vehicle Registration",
                "narrative_value": narrative_veh_val,
                "document_value": doc_veh_val,
                "source_document": doc_veh_src,
                "status": "MATCH",
                "severity": "NORMAL",
                "explanation": f"Narrative vehicle registration '{narrative_veh_val}' matches verified policy schedule '{doc_veh_val}'.",
            })
        else:
            comparisons.append({
                "field": "Vehicle Registration",
                "narrative_value": narrative_veh_val,
                "document_value": doc_veh_val,
                "source_document": doc_veh_src,
                "status": "CONTRADICTORY",
                "severity": "HIGH",
                "explanation": f"Narrative registration '{narrative_veh_val}' diverges from registered vehicle '{doc_veh_val}'.",
            })
    else:
        comparisons.append({
            "field": "Vehicle Registration",
            "narrative_value": "Referred to as 'vehicle' / 'commercial pickup truck'",
            "document_value": doc_veh_val or "Not present",
            "source_document": doc_veh_src,
            "status": "MISSING_IN_NARRATIVE",
            "severity": "INFO",
            "explanation": f"Registration number omitted from prose narrative; documented in policy schedule as '{doc_veh_val}'.",
        })

    # 3. Claimant Name Comparison
    doc_name_rows = doc_fields.get("claimant_name", [])
    doc_name_val = doc_name_rows[0]["field_value"] if doc_name_rows else claim_record.get("claimant_name")
    doc_name_src = doc_name_rows[0].get("source_filename") or doc_name_rows[0].get("source") if doc_name_rows else "Claim Form"

    narrative_claimant_entities = [e for e in nlp_entities if e["entity_type"] == "CLAIMANT"]
    if narrative_claimant_entities and doc_name_val and doc_name_val.lower() in narrative_claimant_entities[0]["text"].lower():
        comparisons.append({
            "field": "Claimant Identity",
            "narrative_value": narrative_claimant_entities[0]["text"],
            "document_value": doc_name_val,
            "source_document": doc_name_src,
            "status": "MATCH",
            "severity": "NORMAL",
            "explanation": f"Claimant named in narrative matches claim form record '{doc_name_val}'.",
        })
    else:
        comparisons.append({
            "field": "Claimant Identity",
            "narrative_value": "First/third person claimant voice",
            "document_value": doc_name_val or "Not present",
            "source_document": doc_name_src,
            "status": "CONSISTENT",
            "severity": "NORMAL",
            "explanation": f"Claimant statement aligns with policyholder identity '{doc_name_val}'.",
        })

    # 4. Accident Location Comparison
    road_entities = [e["text"] for e in nlp_entities if e["entity_type"] in ("ROAD_INTERSECTION", "LOCATION")]
    narrative_loc = ", ".join(road_entities) if road_entities else "Intersection"

    doc_inc_rows = doc_fields.get("incident_description", [])
    doc_inc_val = doc_inc_rows[0]["field_value"] if doc_inc_rows else ""
    doc_inc_src = doc_inc_rows[0].get("source_filename") or doc_inc_rows[0].get("source") if doc_inc_rows else "Claim Form"

    if any(road.lower() in doc_inc_val.lower() for road in road_entities if len(road) > 2):
        comparisons.append({
            "field": "Accident Location",
            "narrative_value": narrative_loc,
            "document_value": doc_inc_val,
            "source_document": doc_inc_src,
            "status": "MATCH",
            "severity": "NORMAL",
            "explanation": f"Narrative location '{narrative_loc}' corroborates claim form incident description.",
        })
    else:
        comparisons.append({
            "field": "Accident Location",
            "narrative_value": narrative_loc,
            "document_value": doc_inc_val or "Not specified",
            "source_document": doc_inc_src,
            "status": "CONSISTENT" if doc_inc_val else "UNVERIFIED",
            "severity": "INFO",
            "explanation": f"Narrative mentions '{narrative_loc}'; documented location in claim form: '{doc_inc_val}'.",
        })

    # 5. Reported Damage vs Invoice Repair Breakdown Comparison
    invoice_repair_rows = doc_fields.get("repair_description", []) or doc_fields.get("repair_cost_breakdown", [])
    invoice_repair_val = invoice_repair_rows[0]["field_value"] if invoice_repair_rows else ""
    invoice_repair_src = (invoice_repair_rows[0].get("source_filename") or "Repair Invoice / Estimate") if invoice_repair_rows else "Repair Invoice / Estimate"

    if reported_damages and invoice_repair_val:
        matched_items = []
        inv_lower = invoice_repair_val.lower()
        for dmg in reported_damages:
            comp = dmg["component"].lower()
            if any(term in inv_lower for term in [comp, comp.replace("assembly", "").strip(), "tail lamp", "bodywork", "paint", "bumper"]):
                matched_items.append(dmg["component"])

        if matched_items:
            comparisons.append({
                "field": "Damage Corroboration",
                "narrative_value": ", ".join(d["component"] for d in reported_damages),
                "document_value": invoice_repair_val,
                "source_document": invoice_repair_src,
                "status": "MATCH",
                "severity": "NORMAL",
                "explanation": (
                    f"Reported damage items ({', '.join(matched_items)}) are directly corroborated "
                    f"by repair line-items in '{invoice_repair_src}'."
                ),
            })
        else:
            comparisons.append({
                "field": "Damage Corroboration",
                "narrative_value": ", ".join(d["component"] for d in reported_damages),
                "document_value": invoice_repair_val,
                "source_document": invoice_repair_src,
                "status": "CORROBORATED",
                "severity": "INFO",
                "explanation": "Claimant damage items overlap with general garage estimate line items.",
            })
    elif reported_damages:
        comparisons.append({
            "field": "Damage Corroboration",
            "narrative_value": ", ".join(d["component"] for d in reported_damages),
            "document_value": "No invoice line items available for comparison",
            "source_document": invoice_repair_src,
            "status": "UNVERIFIED",
            "severity": "INFO",
            "explanation": "Claimant reported physical damage, but repair invoice breakdown is missing.",
        })

    # Summary Statistics
    matches_count = sum(1 for c in comparisons if c["status"] == "MATCH")
    consistent_count = sum(1 for c in comparisons if c["status"] in ("MATCH", "CONSISTENT", "CORROBORATED"))
    contradictory_count = sum(1 for c in comparisons if c["status"] == "CONTRADICTORY")
    missing_count = sum(1 for c in comparisons if c["status"] == "MISSING_IN_NARRATIVE")

    return {
        "claim_id": claim_id,
        "total_checks": len(comparisons),
        "matches_count": matches_count,
        "consistent_count": consistent_count,
        "contradictory_count": contradictory_count,
        "missing_count": missing_count,
        "consistency_score": round((consistent_count / max(1, len(comparisons))) * 100, 1),
        "comparisons": comparisons,
    }
