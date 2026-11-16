"""Accident Event Extraction Service for Claim Narratives (Phase 6)."""

import re
from typing import List, Dict, Any
from backend.services.nlp.preprocessing import segment_sentences


# Event classification rules mapping actions and keywords to structured event types
EVENT_PATTERNS = [
    {
        "type": "MANEUVER_OR_STOP",
        "label": "Vehicle Stationary / Halting at Signal",
        "patterns": [
            r"\b(?:halting|halted|stopped|stopping|waiting|stationary|braked|brought\s+to\s+a\s+halt)\b.*?\b(?:intersection|signal|traffic\s+light|red\s+light|crossroad)?",
            r"\b(?:while\s+halting|at\s+an\s+intersection\s+signal)\b",
        ],
        "default_desc": "Subject vehicle was halted or waiting stationary at an intersection signal",
        "confidence": 0.94,
    },
    {
        "type": "TRANSIT",
        "label": "Vehicle in Transit / Driving",
        "patterns": [
            r"\b(?:travelling|traveling|driving|moving|cruising|proceeding|in\s+transit)\b.*?\b(?:on|along)?\s*([A-Za-z0-9\s.-]+(?:Road|Rd|Highway|Street|St))?",
            r"\b(?:was\s+on\s+my\s+way|heading\s+towards)\b",
        ],
        "default_desc": "Subject vehicle was traveling along the roadway",
        "confidence": 0.90,
    },
    {
        "type": "APPROACH",
        "label": "Secondary Vehicle Approach",
        "patterns": [
            r"\b(?:commercial\s+pickup\s+truck|pickup\s+truck|truck|other\s+vehicle|car)\b.*?\b(?:approached|came|was\s+speeding|behind)\b",
            r"\b(?:from\s+behind|from\s+the\s+rear)\b",
        ],
        "default_desc": "Secondary vehicle approached from behind the subject vehicle",
        "confidence": 0.88,
    },
    {
        "type": "COLLISION",
        "label": "Vehicular Impact / Collision Occurred",
        "patterns": [
            r"\b(?:rear-ended|rear\s+ended|hit\s+from\s+behind|struck\s+from\s+behind|rammed\s+into|collided\s+with|crashed\s+into|impact\s+occurred|sideswiped|t-boned|head-on)\b",
            r"\b(?:was\s+hit|was\s+struck|collided)\b",
        ],
        "default_desc": "Impact occurred when secondary vehicle struck the subject vehicle",
        "confidence": 0.98,
    },
    {
        "type": "DAMAGE_SUSTAINED",
        "label": "Physical Damage Incurred",
        "patterns": [
            r"\b(?:damage\s+observed|damage\s+was\s+observed|sustained\s+damage|damaged|dented|broken|shattered|cracked)\b.*?\b(?:on|to|at)?",
            r"\b(?:damage\s+on\s+the\s+rear\s+bumper|trunk\s+hatch|tail\s+lamp)\b",
        ],
        "default_desc": "Vehicle sustained physical component damage following collision",
        "confidence": 0.95,
    },
    {
        "type": "POST_ACCIDENT_ACTION",
        "label": "Post-Accident Reporting / Mitigation",
        "patterns": [
            r"\b(?:reported|notified|called\s+police|filed\s+claim|exchanged\s+details|towed|moved\s+to\s+side)\b",
        ],
        "default_desc": "Driver reported incident or initiated claim procedures",
        "confidence": 0.89,
    },
]


def extract_events(text: str, sentences: List[str]) -> List[Dict[str, Any]]:
    """Identifies and extracts structured accident events from claimant narrative sentences."""
    if not text or not sentences:
        return []

    events: List[Dict[str, Any]] = []
    event_counter = 1

    for sent_idx, sent in enumerate(sentences, start=1):
        lower_sent = sent.lower()

        # Check for event patterns in current sentence
        matched_event_types_in_sent = set()
        for ev_def in EVENT_PATTERNS:
            ev_type = ev_def["type"]
            if ev_type in matched_event_types_in_sent:
                continue

            for pat in ev_def["patterns"]:
                match = re.search(pat, lower_sent)
                if match:
                    # Construct specific description based on sentence context
                    desc = ev_def["default_desc"]
                    if ev_type == "MANEUVER_OR_STOP" and "intersection" in lower_sent:
                        desc = "Vehicle halted stationary at an intersection signal"
                    elif ev_type == "COLLISION" and ("rear-ended" in lower_sent or "from behind" in lower_sent):
                        truck_match = "commercial pickup truck" if "commercial pickup truck" in lower_sent else (
                            "pickup truck" if "pickup truck" in lower_sent else "another vehicle"
                        )
                        desc = f"Vehicle was struck from behind by {truck_match} (rear-end impact)"
                    elif ev_type == "DAMAGE_SUSTAINED":
                        # List extracted components if present in sentence
                        panels = []
                        if "rear bumper" in lower_sent:
                            panels.append("rear bumper")
                        if "trunk" in lower_sent:
                            panels.append("trunk hatch")
                        if "tail lamp" in lower_sent:
                            panels.append("right tail lamp assembly")
                        if panels:
                            desc = f"Damage observed on {', '.join(panels)}"

                    # Identify temporal marker in sentence
                    temporal_marker = None
                    if re.search(r"\bwhile\b", lower_sent):
                        temporal_marker = "While"
                    elif re.search(r"\bthen\b", lower_sent):
                        temporal_marker = "Then"
                    elif re.search(r"\bafter\b", lower_sent):
                        temporal_marker = "After"
                    elif re.search(r"\bsuddenly\b", lower_sent):
                        temporal_marker = "Suddenly"

                    events.append({
                        "event_id": f"EVT-{event_counter:02d}",
                        "event_type": ev_type,
                        "event_label": ev_def["label"],
                        "description": desc,
                        "sequence_index": event_counter,
                        "supporting_sentence": sent,
                        "temporal_marker": temporal_marker,
                        "sentence_index": sent_idx,
                        "confidence": ev_def["confidence"],
                    })
                    event_counter += 1
                    matched_event_types_in_sent.add(ev_type)
                    break

    return events
