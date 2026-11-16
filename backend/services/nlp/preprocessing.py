"""Text Preprocessing and Sentence Segmentation for Claim Narratives (Phase 6)."""

import re
import unicodedata
from typing import List, Dict, Any, Tuple


# Common English contractions mapping
CONTRACTIONS = {
    r"\bwasn't\b": "was not",
    r"\bdidn't\b": "did not",
    r"\bcouldn't\b": "could not",
    r"\bwouldn't\b": "would not",
    r"\bshouldn't\b": "should not",
    r"\bisn't\b": "is not",
    r"\baren't\b": "are not",
    r"\bweren't\b": "were not",
    r"\bcan't\b": "cannot",
    r"\bdon't\b": "do not",
    r"\bdoesn't\b": "does not",
    r"\bit's\b": "it is",
    r"\bthere's\b": "there is",
    r"\bthat's\b": "that is",
    r"\bi'm\b": "i am",
    r"\bi've\b": "i have",
    r"\bwe've\b": "we have",
    r"\bthey've\b": "they have",
}

# Standard title and sentence abbreviations that should not trigger sentence splits
PROTECTED_ABBREVIATIONS = [
    r"Mr\.", r"Mrs\.", r"Ms\.", r"Dr\.", r"Prof\.", r"St\.", r"Ave\.", r"Rd\.",
    r"No\.", r"Nos\.", r"vs\.", r"etc\.", r"e\.g\.", r"i\.e\.", r"approx\.",
    r"a\.m\.", r"p\.m\.", r"AM", r"PM", r"A\.M\.", r"P\.M\."
]


def normalize_text(text: str) -> str:
    """Normalizes text while preserving the original claimant meaning.
    
    Performs unicode normalization, expands contractions, standardizes quotation marks,
    and removes redundant whitespace.
    """
    if not text or not isinstance(text, str):
        return ""

    # Unicode normalization (NFKC)
    normalized = unicodedata.normalize("NFKC", text)

    # Standardize curly quotes and apostrophes
    normalized = normalized.replace("’", "'").replace("‘", "'")
    normalized = normalized.replace("“", '"').replace("”", '"')
    normalized = normalized.replace("—", " - ").replace("–", " - ")

    # Expand contractions case-insensitively
    for pattern, replacement in CONTRACTIONS.items():
        normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)

    # Standardize whitespace (tabs, multiple spaces, linebreaks)
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r"\r?\n+", "\n", normalized)
    normalized = normalized.strip()

    return normalized


def segment_sentences(text: str) -> List[str]:
    """Segments raw or normalized text into distinct sentences.
    
    Protects known abbreviations from false-splitting and cleanly handles
    consecutive punctuation.
    """
    if not text or not text.strip():
        return []

    cleaned = normalize_text(text)

    # Temporarily mask protected abbreviations with placeholders
    masked = cleaned
    placeholders: Dict[str, str] = {}
    for idx, abbr_pat in enumerate(PROTECTED_ABBREVIATIONS):
        matches = list(re.finditer(abbr_pat, masked, flags=re.IGNORECASE))
        for m in reversed(matches):
            token = f"__ABBR_{idx}_{m.start()}__"
            placeholders[token] = m.group(0)
            masked = masked[:m.start()] + token + masked[m.end():]

    # Sentence boundary split: period, exclamation, question mark followed by space or newline
    raw_sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'])", masked)

    # If re.split didn't split (e.g. single sentence or semicolon/newline delimited), check newlines
    final_sentences: List[str] = []
    for s in raw_sentences:
        lines = [line.strip() for line in s.split("\n") if line.strip()]
        for line in lines:
            # Unmask placeholders
            for token, orig in placeholders.items():
                line = line.replace(token, orig)
            line = line.strip()
            if line:
                final_sentences.append(line)

    return final_sentences if final_sentences else [cleaned]


def extract_temporal_expressions(text: str) -> List[Dict[str, Any]]:
    """Extracts explicit date, time, and temporal connective expressions from text."""
    if not text:
        return []

    expressions: List[Dict[str, Any]] = []

    # 1. Explicit Dates (e.g. 2026-09-28, 28/09/2026, 28th September 2026, Sep 28, 2026)
    date_patterns = [
        (r"\b\d{4}-\d{2}-\d{2}\b", "iso_date"),
        (r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", "numeric_date"),
        (r"\b\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)(?:\s*,?\s*\d{2,4})?\b", "word_date"),
        (r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?(?:\s*,?\s*\d{2,4})?\b", "word_date"),
    ]

    for pat, exp_type in date_patterns:
        for match in re.finditer(pat, text, flags=re.IGNORECASE):
            expressions.append({
                "type": "date",
                "subtype": exp_type,
                "text": match.group(0),
                "start": match.start(),
                "end": match.end(),
            })

    # 2. Explicit Clock Times (e.g. 10:30 AM, 4:15pm, 14:00 hrs, around 3 PM)
    time_patterns = [
        (r"\b(?:around|at|approx(?:\.|\s+)?|roughly)?\s*(\d{1,2}:\d{2}(?::\d{2})?\s*(?:am|pm|hrs|hours)?)\b", "clock_time"),
        (r"\b(?:around|at|approx(?:\.|\s+)?|roughly)?\s*(\d{1,2}\s*(?:am|pm))\b", "clock_time_hour"),
    ]

    for pat, exp_type in time_patterns:
        for match in re.finditer(pat, text, flags=re.IGNORECASE):
            raw_val = match.group(0).strip()
            # Avoid matching pure numbers
            if any(term in raw_val.lower() for term in [":", "am", "pm", "hrs", "around", "at", "approx"]):
                expressions.append({
                    "type": "time",
                    "subtype": exp_type,
                    "text": raw_val,
                    "start": match.start(),
                    "end": match.end(),
                })

    # 3. Relative or Time-of-Day Markers
    tod_patterns = [
        (r"\b(?:in\s+the\s+)?(morning|afternoon|evening|night|broad\s+daylight|midday|midnight|rush\s+hour)\b", "time_of_day"),
        (r"\b(while|when|then|after|subsequently|prior\s+to|before|at\s+that\s+moment|suddenly|immediately|later)\b", "temporal_marker"),
    ]

    for pat, exp_type in tod_patterns:
        for match in re.finditer(pat, text, flags=re.IGNORECASE):
            expressions.append({
                "type": "temporal_marker" if exp_type == "temporal_marker" else "time_of_day",
                "subtype": exp_type,
                "text": match.group(0),
                "start": match.start(),
                "end": match.end(),
            })

    # Deduplicate overlapping matches
    expressions.sort(key=lambda x: x["start"])
    unique_expressions: List[Dict[str, Any]] = []
    last_end = -1
    for exp in expressions:
        if exp["start"] >= last_end:
            unique_expressions.append(exp)
            last_end = exp["end"]

    return unique_expressions


def extract_keywords_and_phrases(text: str) -> List[str]:
    """Extracts salient domain keywords from claimant descriptions."""
    if not text:
        return []

    domain_terms = [
        "intersection", "signal", "traffic light", "red light", "rear-ended",
        "commercial truck", "pickup truck", "truck", "car", "vehicle",
        "bumper", "trunk", "tail lamp", "assembly", "damage", "collision",
        "hit", "struck", "halting", "stopped", "braking", "overtaking",
        "lane change", "highway", "road", "crossroad", "junction",
        "headlight", "windshield", "door", "fender", "dent", "scratch", "crack"
    ]

    found: List[str] = []
    lower_text = text.lower()
    for term in domain_terms:
        if re.search(r"\b" + re.escape(term) + r"\b", lower_text):
            found.append(term)

    return found
