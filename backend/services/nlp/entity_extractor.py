"""Entity Extraction Service for Insurance Claim Descriptions (Phase 6)."""

import re
from typing import List, Dict, Any, Optional
from backend.services.nlp.preprocessing import segment_sentences, extract_temporal_expressions


# Indian and generic vehicle registration number patterns
REGISTRATION_PATTERNS = [
    r"\b[A-Z]{2}[-\s]?[0-9]{1,2}[-\s]?[A-Z]{1,3}[-\s]?[0-9]{4}\b",  # e.g. MH-12-DE-4052, DL 01 AB 1234
    r"\b[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}\b",
    r"\b[0-9]{2}\s*BH\s*[0-9]{4}\s*[A-Z]{1,2}\b",  # BH series
]

# Vehicle classification lexicons
VEHICLE_PATTERNS = [
    (r"\bcommercial\s+pickup\s+truck\b", "commercial_pickup_truck", "Commercial Pickup Truck"),
    (r"\bpickup\s+truck\b", "pickup_truck", "Pickup Truck"),
    (r"\bcommercial\s+truck\b", "commercial_truck", "Commercial Truck"),
    (r"\btruck\b", "truck", "Truck"),
    (r"\btwo-wheeler|motorcycle|motorbike|scooter|bike\b", "two_wheeler", "Two-Wheeler"),
    (r"\bauto|autorickshaw|rickshaw\b", "three_wheeler", "Auto Rickshaw"),
    (r"\bsedan|hatchback|suv|crossover|van\b", "passenger_car_specific", "Passenger Car"),
    (r"\b(?:insured\s+)?vehicle\b", "vehicle_generic", "Vehicle"),
    (r"\bcar\b", "car", "Car"),
    (r"\bbus\b", "bus", "Bus"),
]

# Location / Road / Intersection patterns
ROAD_TERMS = [
    r"\b(?:[A-Z][a-zA-Z0-9.-]+\s+)*(?:[A-Z][a-zA-Z0-9.-]+)\s+(?:Road|Rd\.?|Marg|Street|St\.?|Avenue|Ave\.?|Highway|Expressway|Flyover|Lane)\b",
    r"\b(?:NH|SH)[-\s]?[0-9]+\b",
]

INTERSECTION_TERMS = [
    r"\b(?:intersection\s+signal|traffic\s+signal|traffic\s+light|intersection|junction|roundabout|crossroad|red\s+light|toll\s+plaza)\b"
]

# Weather / road condition terms
WEATHER_ROAD_TERMS = [
    (r"\b(?:heavy\s+rain|raining|downpour|drizzle|stormy)\b", "weather", "Rainy / Precipitation"),
    (r"\b(?:fog|foggy|mist|dense\s+fog|low\s+visibility)\b", "weather", "Foggy / Low Visibility"),
    (r"\b(?:clear\s+weather|sunny|dry\s+weather|clear\s+sky)\b", "weather", "Clear Weather"),
    (r"\b(?:wet\s+road|slippery\s+road|slippery\s+surface|waterlogged|icy\s+road|potholes|pothole)\b", "road_condition", "Slippery / Adverse Road Surface"),
]


def extract_entities(text: str, claimant_name_hint: Optional[str] = None) -> List[Dict[str, Any]]:
    """Extracts typed domain entities from claimant accident narratives.
    
    Identifies:
    - Claimant references
    - Other involved persons / parties
    - Vehicles and vehicle types
    - Vehicle registration numbers
    - Locations, roads, and intersection signals
    - Dates and times
    - Stated damage panels
    - Weather and road conditions
    """
    if not text or not text.strip():
        return []

    sentences = segment_sentences(text)
    entities: List[Dict[str, Any]] = []
    entity_counter = 1

    def add_entity(
        entity_type: str,
        entity_text: str,
        start_char: int,
        end_char: int,
        supporting_sentence: str,
        method: str,
        confidence: float,
        normalized_value: Optional[str] = None,
    ):
        nonlocal entity_counter
        # If overlapping with an existing entity, prefer longer / more specific entity span
        for i, existing in enumerate(entities):
            if not (end_char <= existing["start_char"] or start_char >= existing["end_char"]):
                existing_len = existing["end_char"] - existing["start_char"]
                new_len = end_char - start_char
                if existing_len >= new_len:
                    return
                else:
                    entities[i] = {
                        "entity_id": existing["entity_id"],
                        "entity_type": entity_type,
                        "text": entity_text,
                        "normalized_value": normalized_value or entity_text,
                        "start_char": start_char,
                        "end_char": end_char,
                        "supporting_sentence": supporting_sentence,
                        "extraction_method": method,
                        "confidence": round(confidence, 2),
                    }
                    return

        entities.append({
            "entity_id": f"ENT-{entity_counter:03d}",
            "entity_type": entity_type,
            "text": entity_text,
            "normalized_value": normalized_value or entity_text,
            "start_char": start_char,
            "end_char": end_char,
            "supporting_sentence": supporting_sentence,
            "extraction_method": method,
            "confidence": round(confidence, 2),
        })
        entity_counter += 1

    # Sentence-by-sentence extraction for accurate context attribution
    for sent in sentences:
        sent_offset = text.find(sent)
        if sent_offset == -1:
            sent_offset = 0

        # 1. Vehicle Registration Numbers
        for reg_pat in REGISTRATION_PATTERNS:
            for match in re.finditer(reg_pat, sent, flags=re.IGNORECASE):
                val = match.group(0).upper().replace(" ", "-")
                add_entity(
                    entity_type="VEHICLE_REGISTRATION",
                    entity_text=match.group(0),
                    start_char=sent_offset + match.start(),
                    end_char=sent_offset + match.end(),
                    supporting_sentence=sent,
                    method="regex_ner",
                    confidence=0.98,
                    normalized_value=val,
                )

        # 2. Road and Street Names
        for road_pat in ROAD_TERMS:
            for match in re.finditer(road_pat, sent):
                road_str = match.group(0).strip()
                add_entity(
                    entity_type="ROAD_INTERSECTION",
                    entity_text=road_str,
                    start_char=sent_offset + match.start(),
                    end_char=sent_offset + match.end(),
                    supporting_sentence=sent,
                    method="pattern_rule",
                    confidence=0.94,
                    normalized_value=road_str,
                )

        # 3. Intersection and Signal References
        for int_pat in INTERSECTION_TERMS:
            for match in re.finditer(int_pat, sent, flags=re.IGNORECASE):
                int_str = match.group(0).strip()
                add_entity(
                    entity_type="LOCATION",
                    entity_text=int_str,
                    start_char=sent_offset + match.start(),
                    end_char=sent_offset + match.end(),
                    supporting_sentence=sent,
                    method="pattern_rule",
                    confidence=0.92,
                    normalized_value=int_str.title(),
                )

        # 4. Other Involved Parties / Vehicles
        other_party_patterns = [
            (r"\b(?:a|the)?\s*(commercial\s+pickup\s+truck)\b", "Commercial Pickup Truck"),
            (r"\b(?:a|the)?\s*(commercial\s+truck)\b", "Commercial Truck"),
            (r"\b(?:a|the)?\s*(pickup\s+truck)\b", "Pickup Truck"),
            (r"\b(?:a|the)?\s*(other\s+vehicle|other\s+driver|third\s+party|oncoming\s+vehicle)\b", "Third Party Vehicle/Driver"),
        ]
        for pat, norm in other_party_patterns:
            for match in re.finditer(pat, sent, flags=re.IGNORECASE):
                matched_text = match.group(1) if match.lastindex else match.group(0)
                add_entity(
                    entity_type="OTHER_PARTY",
                    entity_text=matched_text,
                    start_char=sent_offset + match.start(),
                    end_char=sent_offset + match.end(),
                    supporting_sentence=sent,
                    method="pattern_rule",
                    confidence=0.95,
                    normalized_value=norm,
                )

        # 5. Claimant Vehicle References
        claimant_vehicle_patterns = [
            r"\bmy\s+vehicle\b",
            r"\bmy\s+car\b",
            r"\bour\s+vehicle\b",
            r"\bthe\s+insured\s+vehicle\b",
            r"\bthe\s+vehicle\b",
            r"\bvehicle\b",
        ]
        for cv_pat in claimant_vehicle_patterns:
            for match in re.finditer(cv_pat, sent, flags=re.IGNORECASE):
                # Avoid if it's already tagged under other party (e.g. commercial pickup truck)
                start_c = sent_offset + match.start()
                end_c = sent_offset + match.end()
                overlap = any(
                    e["entity_type"] == "OTHER_PARTY" and not (end_c <= e["start_char"] or start_c >= e["end_char"])
                    for e in entities
                )
                if not overlap:
                    add_entity(
                        entity_type="VEHICLE",
                        entity_text=match.group(0),
                        start_char=start_c,
                        end_char=end_c,
                        supporting_sentence=sent,
                        method="pattern_rule",
                        confidence=0.90,
                        normalized_value="Subject Vehicle",
                    )
                    break

        # 6. Claimant Self-References
        claimant_self_patterns = [
            (r"\bI\s+(?:was|am|noticed|observed|halted|stopped|applied)\b", "I"),
            (r"\bmy\b", "my"),
            (r"\bwe\b", "we"),
            (r"\bdriver\b", "driver"),
        ]
        if claimant_name_hint:
            claimant_self_patterns.insert(0, (r"\b" + re.escape(claimant_name_hint) + r"\b", claimant_name_hint))

        for pat, norm in claimant_self_patterns:
            for match in re.finditer(pat, sent, flags=re.IGNORECASE):
                add_entity(
                    entity_type="CLAIMANT",
                    entity_text=match.group(0),
                    start_char=sent_offset + match.start(),
                    end_char=sent_offset + match.end(),
                    supporting_sentence=sent,
                    method="lexical_gazetteer",
                    confidence=0.92,
                    normalized_value="Claimant / Driver",
                )
                break

        # 7. Weather and Road Conditions
        for cond_pat, ent_t, norm in WEATHER_ROAD_TERMS:
            for match in re.finditer(cond_pat, sent, flags=re.IGNORECASE):
                add_entity(
                    entity_type="WEATHER_CONDITION" if ent_t == "weather" else "ROAD_CONDITION",
                    entity_text=match.group(0),
                    start_char=sent_offset + match.start(),
                    end_char=sent_offset + match.end(),
                    supporting_sentence=sent,
                    method="pattern_rule",
                    confidence=0.91,
                    normalized_value=norm,
                )

    # 8. Global Temporal Expressions (Dates & Times)
    temporal_exps = extract_temporal_expressions(text)
    for exp in temporal_exps:
        if exp["type"] in ("date", "time"):
            # Find supporting sentence
            supporting = ""
            for s in sentences:
                if exp["text"].lower() in s.lower():
                    supporting = s
                    break
            add_entity(
                entity_type="ACCIDENT_DATE" if exp["type"] == "date" else "ACCIDENT_TIME",
                entity_text=exp["text"],
                start_char=exp["start"],
                end_char=exp["end"],
                supporting_sentence=supporting or text,
                method="temporal_parser",
                confidence=0.95,
                normalized_value=exp["text"],
            )

    # Sort entities by start_char
    entities.sort(key=lambda x: x["start_char"])
    return entities
