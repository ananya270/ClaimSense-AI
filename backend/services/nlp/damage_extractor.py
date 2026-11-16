"""Claimant-Reported Damage Description Extraction Service (Phase 6)."""

import re
from typing import List, Dict, Any


# Vehicle components commonly reported damaged in accident statements
VEHICLE_COMPONENTS = [
    (r"\brear\s+bumper\b", "Rear Bumper", "rear"),
    (r"\bfront\s+bumper\b", "Front Bumper", "front"),
    (r"\bbumper\b", "Bumper (Unspecified)", "unspecified"),
    (r"\btrunk\s+hatch\b", "Trunk Hatch", "rear"),
    (r"\btrunk\s+lid|boot\s+lid|trunk|boot\b", "Trunk / Boot", "rear"),
    (r"\bright\s+tail\s+lamp\s+assembly|right\s+tail\s+lamp|right\s+tail\s+light\b", "Right Tail Lamp Assembly", "rear_right"),
    (r"\bleft\s+tail\s+lamp\s+assembly|left\s+tail\s+lamp|left\s+tail\s+light\b", "Left Tail Lamp Assembly", "rear_left"),
    (r"\btail\s+lamp\s+assembly|tail\s+lamp|tail\s+light|taillight\b", "Tail Lamp Assembly", "rear"),
    (r"\bheadlight\s+assembly|headlamp|headlight\b", "Headlight Assembly", "front"),
    (r"\bwindshield|windscreen\b", "Windshield Glass", "front"),
    (r"\brear\s+windshield|rear\s+glass\b", "Rear Windshield Glass", "rear"),
    (r"\bhood|bonnet\b", "Hood / Bonnet", "front"),
    (r"\bfender\b", "Fender Panel", "side"),
    (r"\bquarter\s+panel\b", "Quarter Panel", "side"),
    (r"\bdoor\s+panel|driver\s+door|passenger\s+door|front\s+door|rear\s+door|door\b", "Door Assembly", "side"),
    (r"\bside\s+mirror|rearview\s+mirror|wing\s+mirror\b", "Side Mirror", "side"),
    (r"\bradiator|grille|grill\b", "Front Grille / Radiator", "front"),
    (r"\bwheel|rim|tire|tyre\b", "Wheel / Tire", "lower"),
    (r"\broof\b", "Roof Panel", "top"),
]

# Severity and damage descriptors
DAMAGE_MODIFIERS = [
    r"\b(?:damage|damaged|dent|dented|scratch|scratched|crack|cracked|broken|shatter|shattered|crushed|smashed|bent|torn)\b"
]


def extract_reported_damages(text: str, sentences: List[str]) -> List[Dict[str, Any]]:
    """Extracts vehicle damage descriptions stated explicitly by the claimant in the narrative.
    
    IMPORTANT: These represent claimant-reported damages from the text statement,
    NOT computer-vision-confirmed damages.
    """
    if not text or not sentences:
        return []

    damages: List[Dict[str, Any]] = []
    seen_components = set()

    # Redundancy suppression mapping: if key has matched, suppress values
    SUPPRESSIONS = {
        "Rear Bumper": ["Bumper (Unspecified)"],
        "Front Bumper": ["Bumper (Unspecified)"],
        "Trunk Hatch": ["Trunk / Boot"],
        "Right Tail Lamp Assembly": ["Tail Lamp Assembly"],
        "Left Tail Lamp Assembly": ["Tail Lamp Assembly"],
        "Rear Windshield Glass": ["Windshield Glass"],
    }

    for sent_idx, sent in enumerate(sentences, start=1):
        lower_sent = sent.lower()

        # Check if the sentence has any damage indicator
        has_damage_word = any(re.search(mod, lower_sent) for mod in DAMAGE_MODIFIERS)
        if not has_damage_word:
            continue

        matched_spans = []

        for comp_pat, comp_name, spatial_region in VEHICLE_COMPONENTS:
            if comp_name in seen_components:
                continue

            # Check if suppressed by an already matched component
            if any(comp_name in SUPPRESSIONS.get(prev, []) for prev in seen_components):
                continue

            match = re.search(comp_pat, lower_sent)
            if match:
                m_start, m_end = match.start(), match.end()
                # Check span overlap with existing matched spans in this sentence
                if any(not (m_end <= s_start or m_start >= s_end) for s_start, s_end in matched_spans):
                    continue

                matched_spans.append((m_start, m_end))

                # Determine stated damage condition
                stated_condition = "Damaged"
                if re.search(r"\bdent\b|\bdented\b", lower_sent):
                    stated_condition = "Dented"
                elif re.search(r"\bscratch\b|\bscratched\b", lower_sent):
                    stated_condition = "Scratched"
                elif re.search(r"\bbroken\b|\bshatter\b", lower_sent):
                    stated_condition = "Broken / Shattered"
                elif re.search(r"\bcrack\b|\bcracked\b", lower_sent):
                    stated_condition = "Cracked"

                damages.append({
                    "component": comp_name,
                    "reported_condition": stated_condition,
                    "spatial_region": spatial_region,
                    "supporting_sentence": sent,
                    "evidence_type": "Claimant-Reported Narrative (Non-Visual)",
                    "matched_text": match.group(0),
                    "sentence_index": sent_idx,
                })
                seen_components.add(comp_name)

    return damages
