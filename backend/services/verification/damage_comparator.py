"""Cross-corroboration of damage evidence: NLP narrative, YOLOv8 vision, and repair invoices (Phase 7)."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from backend.services.verification.rules import (
    SEVERITY_HIGH,
    SEVERITY_LOW,
    SEVERITY_MEDIUM,
    STATUS_INCONCLUSIVE,
    STATUS_MATCH,
    STATUS_MISMATCH,
    STATUS_MISSING_IN_SOURCE,
    STATUS_NOT_VISUALLY_CONFIRMED,
    STATUS_POTENTIAL_DISCREPANCY,
    STATUS_VISUAL_ONLY_FINDING,
)

# Minimum confidence required for a YOLOv8 detection to visually confirm a reported damage claim
VISUAL_CONFIRMATION_THRESHOLD = 0.50

# Minimum confidence required for an unmatched detection to be surfaced as a visual-only finding
VISUAL_ONLY_MIN_CONFIDENCE = 0.40

# Component keywords mapped to compatible YOLO CarDD categories and spatial regions
_COMPONENT_MAP: Dict[str, Dict[str, Any]] = {
    "rear bumper": {
        "regions": {"rear", "rear_left", "rear_right", "center"},
        "categories": {"dent", "scratch", "crack"},
    },
    "trunk hatch": {
        "regions": {"rear", "center"},
        "categories": {"dent", "scratch", "crack"},
    },
    "tail lamp": {
        "regions": {"rear", "rear_left", "rear_right"},
        "categories": {"lamp broken", "crack"},
    },
    "front bumper": {
        "regions": {"front", "front_left", "front_right", "center"},
        "categories": {"dent", "scratch", "crack"},
    },
    "radiator grill": {
        "regions": {"front", "center"},
        "categories": {"dent", "crack"},
    },
    "headlamp": {
        "regions": {"front", "front_left", "front_right"},
        "categories": {"lamp broken", "crack"},
    },
    "hood": {
        "regions": {"front", "center"},
        "categories": {"dent", "scratch", "crack"},
    },
    "windshield": {
        "regions": {"front", "center"},
        "categories": {"glass shatter", "crack"},
    },
    "rear window": {
        "regions": {"rear", "center"},
        "categories": {"glass shatter", "crack"},
    },
    "side door": {
        "regions": {"left_side", "right_side", "center"},
        "categories": {"dent", "scratch", "crack"},
    },
    "quarter panel": {
        "regions": {"rear_left", "rear_right", "front_left", "front_right"},
        "categories": {"dent", "scratch", "crack"},
    },
    "fender": {
        "regions": {"front_left", "front_right", "front"},
        "categories": {"dent", "scratch", "crack"},
    },
    "tire": {
        "regions": {"rear_left", "rear_right", "front_left", "front_right"},
        "categories": {"tire flat"},
    },
}


def _match_component_profile(component_name: str) -> Optional[Dict[str, Any]]:
    name_clean = component_name.lower().strip()
    for key, profile in _COMPONENT_MAP.items():
        if key in name_clean:
            return profile
    return None


def compare_narrative_vs_vision(
    reported_damages: List[Dict[str, Any]],
    vision_analysis: Optional[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Compares claimant-reported damage items (Phase 6) with Computer Vision detections (Phase 5).
    
    Returns structured comparison records.
    """
    findings: List[Dict[str, Any]] = []

    if not reported_damages and not vision_analysis:
        return findings

    # Handle missing vision analysis
    if not vision_analysis or vision_analysis.get("analysis_status") == "failed":
        for dmg in reported_damages:
            findings.append({
                "field_name": f"Damage: {dmg.get('component', 'Vehicle Component')}",
                "source_a": "Claim Narrative (NLP)",
                "source_b": "Vehicle Photograph (Computer Vision)",
                "original_value_a": dmg.get("component"),
                "original_value_b": "Analysis not executed / failed",
                "normalized_value_a": dmg.get("component"),
                "normalized_value_b": "No Vision Data",
                "comparison_status": STATUS_INCONCLUSIVE,
                "severity": SEVERITY_LOW,
                "confidence": 0.5,
                "explanation": (
                    f"Claimant reported damage to '{dmg.get('component')}', but Computer Vision "
                    "damage analysis has not been executed or photographic evidence was unavailable."
                ),
                "evidence_references": {
                    "reported_component": dmg.get("component"),
                    "spatial_region": dmg.get("spatial_region"),
                },
            })
        return findings

    detection_method = vision_analysis.get("detection_method", "YOLOv8")
    is_opencv_fallback = "opencv" in detection_method.lower()
    raw_detections = vision_analysis.get("detections", [])
    total_detections = vision_analysis.get("total_detections", len(raw_detections))

    # If OpenCV fallback was used without semantic bounding boxes
    if is_opencv_fallback:
        for dmg in reported_damages:
            findings.append({
                "field_name": f"Damage: {dmg.get('component', 'Vehicle Component')}",
                "source_a": "Claim Narrative (NLP)",
                "source_b": "Vehicle Photograph (OpenCV Diagnostic)",
                "original_value_a": dmg.get("component"),
                "original_value_b": "OpenCV structural contours only",
                "normalized_value_a": dmg.get("component"),
                "normalized_value_b": "Structural Contours",
                "comparison_status": STATUS_INCONCLUSIVE,
                "severity": SEVERITY_LOW,
                "confidence": 0.6,
                "explanation": (
                    f"Automated semantic damage detection was not executed (OpenCV fallback was utilized). "
                    f"Cannot confirm or refute reported '{dmg.get('component')}' without semantic class prediction."
                ),
                "evidence_references": {
                    "detection_method": "OpenCV Fallback",
                    "reported_component": dmg.get("component"),
                },
            })
        return findings

    # Genuine YOLOv8 detections available
    matched_detection_indices = set()

    for idx, dmg in enumerate(reported_damages):
        comp_name = dmg.get("component", "Unknown Component")
        spatial_region = (dmg.get("spatial_region") or "").lower()
        profile = _match_component_profile(comp_name)

        target_categories = profile["categories"] if profile else set()
        target_regions = profile["regions"] if profile else {spatial_region}

        # Find all candidate detections matching component category and region
        candidates = []
        for d_idx, det in enumerate(raw_detections):
            cat = (det.get("category") or "").lower()
            reg = (det.get("location_region") or "").lower()

            category_match = cat in target_categories or not target_categories
            region_match = reg in target_regions or spatial_region in reg or not spatial_region

            if category_match and region_match:
                candidates.append((d_idx, det))

        # Sort candidate detections by confidence descending to evaluate the strongest evidence
        candidates.sort(key=lambda x: x[1].get("confidence", 0.0), reverse=True)

        if candidates:
            best_idx, best_det = candidates[0]
            conf = best_det.get("confidence", 0.0)
            cat = best_det.get("category", "damage")
            reg = best_det.get("location_region", spatial_region)

            if conf >= VISUAL_CONFIRMATION_THRESHOLD:
                # High-confidence detection confirms claimant's damage report
                matched_detection_indices.add(best_idx)
                findings.append({
                    "field_name": f"Damage: {comp_name}",
                    "source_a": "Claim Narrative (NLP)",
                    "source_b": "Vehicle Photograph (YOLOv8)",
                    "original_value_a": f"{comp_name} ({dmg.get('reported_condition', 'Damaged')})",
                    "original_value_b": f"YOLO detected '{cat}' (conf: {conf*100:.1f}%)",
                    "normalized_value_a": comp_name.lower(),
                    "normalized_value_b": cat.lower(),
                    "comparison_status": STATUS_MATCH,
                    "severity": SEVERITY_LOW,
                    "confidence": round(conf, 2),
                    "explanation": (
                        f"Claimant-reported damage on '{comp_name}' is visually corroborated by YOLOv8 "
                        f"detection of '{cat}' with {conf*100:.1f}% confidence."
                    ),
                    "evidence_references": {
                        "reported_component": comp_name,
                        "detection_category": cat,
                        "confidence": conf,
                        "bbox": best_det.get("bbox"),
                    },
                })
            elif conf >= 0.25:
                # Low-confidence detection is ambiguous: cannot confirm or refute with certainty
                matched_detection_indices.add(best_idx)
                findings.append({
                    "field_name": f"Damage: {comp_name}",
                    "source_a": "Claim Narrative (NLP)",
                    "source_b": "Vehicle Photograph (YOLOv8)",
                    "original_value_a": f"{comp_name} ({dmg.get('reported_condition', 'Damaged')})",
                    "original_value_b": f"Low-confidence YOLO detection '{cat}' (conf: {conf*100:.1f}%)",
                    "normalized_value_a": comp_name.lower(),
                    "normalized_value_b": cat.lower(),
                    "comparison_status": STATUS_INCONCLUSIVE,
                    "severity": SEVERITY_LOW,
                    "confidence": round(conf, 2),
                    "explanation": (
                        f"Potential YOLOv8 detection of '{cat}' in {reg} has low confidence ({conf*100:.1f}%), "
                        f"which is insufficient to confirm or refute reported '{comp_name}' damage."
                    ),
                    "evidence_references": {
                        "reported_component": comp_name,
                        "detection_category": cat,
                        "confidence": conf,
                        "bbox": best_det.get("bbox"),
                    },
                })
            else:
                findings.append({
                    "field_name": f"Damage: {comp_name}",
                    "source_a": "Claim Narrative (NLP)",
                    "source_b": "Vehicle Photograph (YOLOv8)",
                    "original_value_a": comp_name,
                    "original_value_b": "No matching damage detected in photograph",
                    "normalized_value_a": comp_name.lower(),
                    "normalized_value_b": "Not Detected",
                    "comparison_status": STATUS_NOT_VISUALLY_CONFIRMED,
                    "severity": SEVERITY_MEDIUM,
                    "confidence": 0.80,
                    "explanation": (
                        f"Claimant reported damage on '{comp_name}', but no corresponding damage category "
                        "was identified by the vision model (not detected in the provided vehicle photograph). "
                        "Note: Damage may be off-camera, internal, or obscured by photo angle."
                    ),
                    "evidence_references": {
                        "reported_component": comp_name,
                        "spatial_region": spatial_region,
                    },
                })
        else:
            findings.append({
                "field_name": f"Damage: {comp_name}",
                "source_a": "Claim Narrative (NLP)",
                "source_b": "Vehicle Photograph (YOLOv8)",
                "original_value_a": comp_name,
                "original_value_b": "No matching damage detected in photograph",
                "normalized_value_a": comp_name.lower(),
                "normalized_value_b": "Not Detected",
                "comparison_status": STATUS_NOT_VISUALLY_CONFIRMED,
                "severity": SEVERITY_MEDIUM,
                "confidence": 0.80,
                "explanation": (
                    f"Claimant reported damage on '{comp_name}', but no corresponding damage category "
                    "was identified by the vision model (not detected in the provided vehicle photograph). "
                    "Note: Damage may be off-camera, internal, or obscured by photo angle."
                ),
                "evidence_references": {
                    "reported_component": comp_name,
                    "spatial_region": spatial_region,
                },
            })

    # Identify Visual-Only findings (detections not mentioned in narrative)
    # Cluster unmatched detections by (category, region) to avoid inflating duplicate/overlapping bounding boxes
    unmatched_clusters: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
    for d_idx, det in enumerate(raw_detections):
        if d_idx not in matched_detection_indices:
            conf = det.get("confidence", 0.0)
            if conf >= VISUAL_ONLY_MIN_CONFIDENCE:
                cat = (det.get("category") or "damage").lower()
                reg = (det.get("location_region") or "unspecified").lower()
                cluster_key = (cat, reg)
                if cluster_key not in unmatched_clusters:
                    unmatched_clusters[cluster_key] = []
                unmatched_clusters[cluster_key].append(det)

    for (cat, reg), cluster_dets in unmatched_clusters.items():
        # Select highest-confidence detection as representative of this damage region
        cluster_dets.sort(key=lambda x: x.get("confidence", 0.0), reverse=True)
        rep_det = cluster_dets[0]
        max_conf = rep_det.get("confidence", 0.0)
        overlap_count = len(cluster_dets)

        if overlap_count > 1:
            explanation = (
                f"Computer Vision detected '{cat}' in the {reg} region ({max_conf*100:.1f}% confidence, "
                f"with {overlap_count} overlapping detections in this region) that was not explicitly listed "
                "in claimant prose statement. This commonly occurs when drivers summarize only the primary point of impact "
                "or due to model bounding box clustering on contiguous damage."
            )
        else:
            explanation = (
                f"Computer Vision detected '{cat}' in the {reg} region ({max_conf*100:.1f}% confidence) "
                "that was not explicitly listed in claimant prose statement. "
                "This commonly occurs when drivers summarize only the primary point of impact."
            )

        findings.append({
            "field_name": f"Visual Detection: {cat.title()}",
            "source_a": "Claim Narrative (NLP)",
            "source_b": "Vehicle Photograph (YOLOv8)",
            "original_value_a": "Not explicitly listed in prose statement",
            "original_value_b": f"Detected '{cat}' in {reg} (conf: {max_conf*100:.1f}%)",
            "normalized_value_a": "Unlisted",
            "normalized_value_b": cat,
            "comparison_status": STATUS_VISUAL_ONLY_FINDING,
            "severity": SEVERITY_LOW,
            "confidence": round(max_conf, 2),
            "explanation": explanation,
            "evidence_references": {
                "detection_category": cat,
                "location_region": reg,
                "confidence": max_conf,
                "bbox": rep_det.get("bbox"),
                "overlapping_detections_count": overlap_count,
            },
        })

    return findings


def compare_invoice_vs_damage(
    invoice_items: List[str],
    reported_damages: List[Dict[str, Any]],
    vision_analysis: Optional[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Compares repair invoice line items with reported damage and vision detections."""
    findings: List[Dict[str, Any]] = []

    if not invoice_items and not reported_damages:
        return findings

    if not invoice_items:
        findings.append({
            "field_name": "Repair Invoice Alignment",
            "source_a": "Repair Invoice / Estimate",
            "source_b": "Reported / Detected Damage",
            "original_value_a": "No invoice line items available",
            "original_value_b": f"{len(reported_damages)} damage item(s) reported",
            "normalized_value_a": "Missing",
            "normalized_value_b": "Reported",
            "comparison_status": STATUS_MISSING_IN_SOURCE,
            "severity": SEVERITY_LOW,
            "confidence": 1.0,
            "explanation": "No itemized repair invoice or estimate breakdown was submitted with claim documentation.",
            "evidence_references": {},
        })
        return findings

    # Generic non-distinguishing component nouns and direction stop words
    generic_nouns = {"assembly", "system", "part", "component", "unit", "cover", "trim", "bracket", "housing"}
    directional_stop_words = {"front", "rear", "left", "right", "center", "side", "upper", "lower", "inner", "outer"}

    # Extract specific damaged component keywords from narrative
    documented_components: List[str] = []
    for dmg in reported_damages:
        c = (dmg.get("component") or "").lower().strip()
        if c:
            documented_components.append(c)

    # Extract detected damage categories from vision
    vision_categories: set[str] = set()
    has_vision_detections = False
    if vision_analysis:
        for det in vision_analysis.get("detections", []):
            cat = (det.get("category") or "").lower().strip()
            if cat:
                vision_categories.add(cat)
                has_vision_detections = True

    has_any_documented_damage = bool(documented_components or has_vision_detections)

    # Standard repair operations, refinishing, and shop overhead
    overhead_terms = {
        "paint", "labor", "labour", "bodywork", "fitting", "repair", "alignment",
        "consumables", "gst", "tax", "towing", "inspection", "miscellaneous", "misc",
    }

    for item in invoice_items:
        item_clean = item.strip()
        item_lower = item_clean.lower()
        if not item_clean:
            continue

        item_words = set(re.sub(r"[^\w\s]", "", item_lower).split())

        # 1. Check for specific component match
        matched_comp = None
        for comp in documented_components:
            # Check against known component profiles first
            profile_matched = False
            for k in _COMPONENT_MAP:
                if k in comp:
                    profile_matched = True
                    # If component key has multiple words (e.g. 'tail lamp', 'side door'), require full key or primary noun
                    if k in item_lower:
                        matched_comp = comp
                        break
                    # Primary component nouns (e.g. 'bumper', 'windshield', 'fender', 'tire')
                    nouns = [w for w in k.split() if w not in directional_stop_words and w not in generic_nouns]
                    if any(n in item_words for n in nouns if len(n) > 3 and n != "lamp"):
                        matched_comp = comp
                        break
            if matched_comp:
                break

            if not profile_matched:
                # For custom components, strip directional and generic words
                comp_tokens = [
                    w for w in re.sub(r"[^\w\s]", "", comp).split()
                    if len(w) > 3 and w not in directional_stop_words and w not in generic_nouns
                ]
                if comp_tokens and all(tok in item_lower for tok in comp_tokens):
                    matched_comp = comp
                    break

        # Check against vision categories (e.g. "Dent removal", "Windshield glass replacement")
        matched_category = None
        if not matched_comp:
            for cat in vision_categories:
                if cat in item_lower or any(cw in item_lower for cw in cat.split() if len(cw) > 3 and cw not in generic_nouns):
                    matched_category = cat
                    break

        # 2. Check if item represents standard labor/shop overhead supporting vehicle repair
        is_overhead_item = bool(item_words & overhead_terms)

        if matched_comp:
            findings.append({
                "field_name": f"Invoice Item: {item_clean}",
                "source_a": "Repair Invoice / Estimate",
                "source_b": "Incident Damage Evidence",
                "original_value_a": item_clean,
                "original_value_b": f"Corroborated by documented damage to '{matched_comp}'",
                "normalized_value_a": item_clean.lower(),
                "normalized_value_b": "Corroborated Component",
                "comparison_status": STATUS_MATCH,
                "severity": SEVERITY_LOW,
                "confidence": 0.95,
                "explanation": f"Repair invoice line item '{item_clean}' directly aligns with documented damage to '{matched_comp}'.",
                "evidence_references": {"invoice_item": item_clean, "matched_component": matched_comp},
            })
        elif matched_category:
            findings.append({
                "field_name": f"Invoice Item: {item_clean}",
                "source_a": "Repair Invoice / Estimate",
                "source_b": "Incident Damage Evidence",
                "original_value_a": item_clean,
                "original_value_b": f"Corroborated by vision damage class '{matched_category}'",
                "normalized_value_a": item_clean.lower(),
                "normalized_value_b": "Corroborated Damage Class",
                "comparison_status": STATUS_MATCH,
                "severity": SEVERITY_LOW,
                "confidence": 0.90,
                "explanation": f"Repair invoice line item '{item_clean}' aligns with vision-detected damage '{matched_category}'.",
                "evidence_references": {"invoice_item": item_clean, "matched_category": matched_category},
            })
        elif is_overhead_item and has_any_documented_damage:
            findings.append({
                "field_name": f"Invoice Item: {item_clean}",
                "source_a": "Repair Invoice / Estimate",
                "source_b": "Incident Damage Evidence",
                "original_value_a": item_clean,
                "original_value_b": "Standard repair labor / overhead supporting documented repairs",
                "normalized_value_a": item_clean.lower(),
                "normalized_value_b": "Repair Labor / Overhead",
                "comparison_status": STATUS_MATCH,
                "severity": SEVERITY_LOW,
                "confidence": 0.95,
                "explanation": f"Repair invoice line item '{item_clean}' represents standard workshop labor or refinishing operations supporting documented vehicle repairs.",
                "evidence_references": {"invoice_item": item_clean},
            })
        else:
            findings.append({
                "field_name": f"Invoice Item: {item_clean}",
                "source_a": "Repair Invoice / Estimate",
                "source_b": "Incident Damage Evidence",
                "original_value_a": item_clean,
                "original_value_b": "Uncorroborated in narrative or vehicle photographs",
                "normalized_value_a": item_clean.lower(),
                "normalized_value_b": "Uncorroborated",
                "comparison_status": STATUS_POTENTIAL_DISCREPANCY,
                "severity": SEVERITY_MEDIUM,
                "confidence": 0.85,
                "explanation": (
                    f"Invoice includes '{item_clean}' which has no apparent connection to the "
                    "reported accident narrative or photographic damage detections. "
                    "Review recommended to confirm relatedness to claimed incident."
                ),
                "evidence_references": {"invoice_item": item_clean},
            })

    return findings
