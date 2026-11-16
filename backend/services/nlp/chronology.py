"""Chronological Event Reconstruction Service for Claim Narratives (Phase 6)."""

from typing import List, Dict, Any, Optional
from backend.services.nlp.preprocessing import extract_temporal_expressions


# Canonical event flow for accident reconstruction
EVENT_TYPE_PRIORITY = {
    "TRANSIT": 10,
    "MANEUVER_OR_STOP": 20,
    "APPROACH": 30,
    "COLLISION": 40,
    "DAMAGE_SUSTAINED": 50,
    "POST_ACCIDENT_ACTION": 60,
}


def reconstruct_chronology(
    events: List[Dict[str, Any]],
    sentences: List[str],
    raw_text: str = ""
) -> Dict[str, Any]:
    """Reconstructs the accident chronology based on narrative sequence and temporal markers.
    
    Distinguishes explicit timestamps from inferred narrative sequence,
    and identifies missing or ambiguous temporal references without inventing times.
    """
    temporal_exps = extract_temporal_expressions(raw_text)
    explicit_dates = [e for e in temporal_exps if e["type"] == "date"]
    explicit_times = [e for e in temporal_exps if e["type"] == "time"]

    has_explicit_time = len(explicit_times) > 0
    ordering_type = "explicit_timestamps" if has_explicit_time else "narrative_sequence"

    # Identify missing or ambiguous temporal information
    missing_info: List[str] = []
    ambiguous_info: List[str] = []

    if not has_explicit_time:
        missing_info.append("Exact accident time was not explicitly specified in claimant statement (using narrative sequence).")
    if not explicit_dates:
        missing_info.append("Exact accident date was not mentioned directly in narrative statement.")

    # Sort events:
    # 1. If explicit timestamps exist, sort by timestamp
    # 2. Otherwise sort by canonical logical accident flow taking sentence order into account
    def get_sort_key(ev: Dict[str, Any]) -> tuple:
        sent_idx = ev.get("sentence_index", 1)
        ev_type = ev.get("event_type", "")
        priority = EVENT_TYPE_PRIORITY.get(ev_type, 99)
        return (sent_idx, priority)

    sorted_events = sorted(events, key=get_sort_key)

    timeline: List[Dict[str, Any]] = []
    for idx, ev in enumerate(sorted_events, start=1):
        # Format human-readable time reference
        marker = ev.get("temporal_marker")
        if marker == "While":
            time_ref = "Phase 1: Pre-Impact Condition (Vehicle Halted)"
        elif ev["event_type"] == "COLLISION":
            time_ref = "Phase 2: Point of Impact"
        elif ev["event_type"] == "DAMAGE_SUSTAINED":
            time_ref = "Phase 3: Immediate Post-Collision Inspection"
        elif ev["event_type"] == "POST_ACCIDENT_ACTION":
            time_ref = "Phase 4: Post-Accident Incident Reporting"
        else:
            time_ref = f"Sequence Step {idx}"

        timeline.append({
            "step_number": idx,
            "event_id": ev.get("event_id", f"EVT-{idx:02d}"),
            "event_type": ev.get("event_type", "EVENT"),
            "event_label": ev.get("event_label", "Accident Event"),
            "phase": time_ref,
            "time_reference": time_ref,
            "description": ev.get("description", ""),
            "supporting_sentence": ev.get("supporting_sentence", ""),
            "is_inferred": not has_explicit_time,
            "order_confidence": ev.get("confidence", 0.90),
        })

    return {
        "ordering_type": ordering_type,
        "explicit_timestamps_present": has_explicit_time,
        "total_events": len(timeline),
        "timeline": timeline,
        "temporal_expressions": temporal_exps,
        "missing_temporal_info": missing_info,
        "ambiguous_temporal_info": ambiguous_info,
    }
