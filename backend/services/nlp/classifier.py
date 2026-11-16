"""Accident Type Classification Service using Linguistic Pattern Matching (Phase 6)."""

import re
from typing import Dict, Any, List


# Classification rules with weighted patterns and keywords
ACCIDENT_CLASSES = [
    {
        "type": "Rear-end collision",
        "keywords": [
            r"\brear-ended\b", r"\brear\s+ended\b", r"\bhit\s+from\s+behind\b",
            r"\bstruck\s+from\s+behind\b", r"\brear\s+collision\b", r"\btail-ended\b",
            r"\bhit\s+the\s+back\b", r"\bstruck\s+my\s+rear\b", r"\brear\s+impact\b"
        ],
        "weight": 1.0,
        "description": "Vehicle was impacted from the rear by another trailing vehicle while moving or stationary",
    },
    {
        "type": "Head-on collision",
        "keywords": [
            r"\bhead-on\b", r"\bhead\s+on\b", r"\bfront\s+to\s+front\b",
            r"\boncoming\s+traffic\b", r"\boncoming\s+vehicle\b", r"\bfrontal\s+collision\b"
        ],
        "weight": 1.0,
        "description": "Frontal collision between two vehicles traveling in opposite directions",
    },
    {
        "type": "Side-impact collision",
        "keywords": [
            r"\bt-bone\b", r"\bt-boned\b", r"\bside-swipe\b", r"\bsideswiped\b",
            r"\bbroadsided\b", r"\bside\s+impact\b", r"\bstruck\s+on\s+the\s+side\b",
            r"\bdoor\s+collision\b"
        ],
        "weight": 1.0,
        "description": "Lateral impact against the side panels or doors of the vehicle",
    },
    {
        "type": "Multi-vehicle collision",
        "keywords": [
            r"\bchain\s+reaction\b", r"\bpile-up\b", r"\bpileup\b",
            r"\bthree\s+vehicles\b", r"\bmultiple\s+vehicles\b", r"\bmultiple\s+cars\b"
        ],
        "weight": 1.0,
        "description": "Compound accident involving three or more vehicles in sequence",
    },
    {
        "type": "Rollover",
        "keywords": [
            r"\brolled\s+over\b", r"\brollover\b", r"\bflipped\s+over\b",
            r"\boverturned\b", r"\broof\s+crush\b", r"\bupside\s+down\b"
        ],
        "weight": 1.0,
        "description": "Vehicle tipped onto its side or roof during an impact or loss of stability",
    },
    {
        "type": "Single-vehicle accident",
        "keywords": [
            r"\bhit\s+a\s+(?:tree|pole|divider|barrier|wall|curb|railing)\b",
            r"\bswerved\s+to\s+avoid\b", r"\blost\s+control\b", r"\bskidded\s+off\b",
            r"\boff\s+the\s+road\b", r"\bditched\b"
        ],
        "weight": 0.95,
        "description": "Collision involving only the insured vehicle impacting a fixed object or roadway hazard",
    },
]


def classify_accident_type(text: str) -> Dict[str, Any]:
    """Classifies accident type from claimant narrative using rule-based linguistic pattern matching.
    
    Returns structured classification, confidence score, supporting text, and method.
    If narrative is ambiguous or empty, returns 'UNKNOWN'.
    """
    if not text or not text.strip():
        return {
            "accident_type": "UNKNOWN",
            "confidence": 0.0,
            "classification_method": "Linguistic Pattern Matching",
            "supporting_text": "No narrative text provided.",
            "description": "Unclassified due to absence of narrative statement.",
            "matched_patterns": [],
        }

    lower_text = text.lower()
    matches: List[Dict[str, Any]] = []

    for cls_def in ACCIDENT_CLASSES:
        matched_kws = []
        for kw_pat in cls_def["keywords"]:
            match = re.search(kw_pat, lower_text)
            if match:
                matched_kws.append(match.group(0))

        if matched_kws:
            # Score based on pattern weight and frequency
            confidence = min(0.98, round((0.85 + (len(matched_kws) * 0.05)) * cls_def.get("weight", 1.0), 2))
            matches.append({
                "type": cls_def["type"],
                "confidence": confidence,
                "keywords": matched_kws,
                "description": cls_def["description"],
            })

    if not matches:
        return {
            "accident_type": "Other / Unclassified",
            "confidence": 0.50,
            "classification_method": "Linguistic Pattern Matching",
            "supporting_text": text.strip()[:160],
            "description": "Narrative does not contain explicit collision type keywords.",
            "matched_patterns": [],
        }

    # Select highest confidence match
    matches.sort(key=lambda x: x["confidence"], reverse=True)
    best = matches[0]

    # Find the sentence containing the best keyword
    supporting_sentence = ""
    for kw in best["keywords"]:
        for sent in text.split("."):
            if kw in sent.lower():
                supporting_sentence = sent.strip() + "."
                break
        if supporting_sentence:
            break

    return {
        "accident_type": best["type"],
        "confidence": round(best["confidence"], 2),
        "classification_method": "Linguistic Pattern Matching",
        "supporting_text": supporting_sentence or text.strip()[:160],
        "description": best["description"],
        "matched_patterns": best["keywords"],
    }
