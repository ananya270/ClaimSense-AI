"""Field Normalization and Value Comparison Utilities for Cross-Source Verification (Phase 7).

Provides transparent normalization, missing-value discrimination, and comparison
functions across names, policy numbers, vehicle registrations, dates, financial amounts,
and descriptive texts.
"""

import re
import unicodedata
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Tuple


HONORIFICS_PATTERN = re.compile(
    r"\b(?:mr|mrs|ms|dr|shri|smt|prof|adv|shree)\b\.?",
    re.IGNORECASE,
)

MISSING_LITERALS = {
    "",
    "none",
    "null",
    "n/a",
    "na",
    "not_present",
    "not present",
    "not_available",
    "not available",
    "-",
    "—",
    "unknown",
    "undefined",
}


def is_missing(val: Any) -> bool:
    """Returns True if the value represents a missing, blank, or null field."""
    if val is None:
        return True
    s = str(val).strip().lower()
    return s in MISSING_LITERALS


def normalize_whitespace(text: str) -> str:
    """Collapses multiple spaces, tabs, and newlines into single spaces."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def normalize_text(val: Any) -> str:
    """Basic text normalization: Unicode NFKC, strip whitespace, and lower-casing."""
    if is_missing(val):
        return ""
    s = unicodedata.normalize("NFKC", str(val))
    return normalize_whitespace(s).lower()


def normalize_name(name: Any) -> str:
    """Normalizes person names by removing honorifics, punctuation, and extra whitespace."""
    if is_missing(name):
        return ""
    s = unicodedata.normalize("NFKC", str(name))
    s = HONORIFICS_PATTERN.sub("", s)
    s = re.sub(r"[^\w\s]", " ", s)
    return normalize_whitespace(s).lower()


def compare_names(name1: Any, name2: Any) -> Tuple[bool, float, str]:
    """Compares two claimant names using token-set invariance and fuzzy similarity.
    
    Returns:
        (is_match, similarity_ratio, explanation)
    """
    if is_missing(name1) or is_missing(name2):
        return False, 0.0, "One or both names are missing or not present."

    norm1 = normalize_name(name1)
    norm2 = normalize_name(name2)

    if not norm1 or not norm2:
        return False, 0.0, "Normalized name is empty after removing titles/honorifics."

    if norm1 == norm2:
        return True, 1.0, f"Exact name match: '{name1}' == '{name2}'"

    tokens1 = set(norm1.split())
    tokens2 = set(norm2.split())

    # Inverted token order match (e.g. "Rajesh Sharma" vs "Sharma Rajesh")
    if tokens1 == tokens2 and tokens1:
        return True, 1.0, f"Token-set match with transposed order: '{name1}' vs '{name2}'"

    # Subset match (e.g. "Rajesh Kumar Sharma" vs "Rajesh Sharma")
    if tokens1.issubset(tokens2) or tokens2.issubset(tokens1):
        ratio = len(tokens1 & tokens2) / max(len(tokens1), len(tokens2))
        return True, round(ratio, 2), f"Subset name match (middle name omission/inclusion): '{name1}' vs '{name2}'"

    # Character similarity (Levenshtein-like token ratio)
    sim = calculate_string_similarity(norm1, norm2)
    if sim >= 0.85:
        return True, round(sim, 2), f"Close phonetic/character similarity ({sim:.0%}): '{name1}' vs '{name2}'"

    return False, round(sim, 2), f"Name mismatch: '{name1}' differs significantly from '{name2}'"


def normalize_policy_number(val: Any) -> str:
    """Normalizes insurance policy numbers by removing non-alphanumeric chars and upper-casing."""
    if is_missing(val):
        return ""
    s = str(val).strip().upper()
    return re.sub(r"[^A-Z0-9]", "", s)


def normalize_vehicle_registration(val: Any) -> str:
    """Normalizes vehicle license plate numbers by removing dashes, spaces, and punctuation."""
    if is_missing(val):
        return ""
    s = str(val).strip().upper()
    return re.sub(r"[^A-Z0-9]", "", s)


def format_vehicle_registration_display(val: Any) -> str:
    """Formats standardized Indian registration numbers (e.g. MH12DE4052 -> MH-12-DE-4052)."""
    clean = normalize_vehicle_registration(val)
    if not clean:
        return ""
    # Standard 10-char state-rto-series-number: e.g. MH 12 DE 4052
    m = re.match(r"^([A-Z]{2})(\d{1,2})([A-Z]{1,3})(\d{1,4})$", clean)
    if m:
        state, rto, series, num = m.groups()
        return f"{state}-{int(rto):02d}-{series}-{num}"
    return clean


def parse_and_normalize_date(val: Any) -> Optional[date]:
    """Parses various date string formats into standard datetime.date."""
    if is_missing(val):
        return None
    if isinstance(val, date):
        return val
    if isinstance(val, datetime):
        return val.date()

    date_str = str(val).strip()

    # Known format candidates
    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%m/%d/%Y",
        "%m-%d-%Y",
        "%Y/%m/%d",
        "%d %b %Y",
        "%d %B %Y",
        "%b %d, %Y",
        "%B %d, %Y",
        "%d-%b-%Y",
        "%d-%B-%Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue

    # Regex extraction fallback for dates embedded in text (e.g. "2026-09-28" or "28/09/2026")
    iso_match = re.search(r"\b(20\d{2})[-/.](0[1-9]|1[0-2])[-/.](0[1-9]|[12]\d|3[01])\b", date_str)
    if iso_match:
        try:
            return date(int(iso_match.group(1)), int(iso_match.group(2)), int(iso_match.group(3)))
        except ValueError:
            pass

    dmy_match = re.search(r"\b(0[1-9]|[12]\d|3[01])[-/.](0[1-9]|1[0-2])[-/.](20\d{2})\b", date_str)
    if dmy_match:
        try:
            return date(int(dmy_match.group(3)), int(dmy_match.group(2)), int(dmy_match.group(1)))
        except ValueError:
            pass

    return None


def date_difference_days(date1_val: Any, date2_val: Any) -> Optional[int]:
    """Returns absolute difference in days between two dates, or None if either unparsable."""
    d1 = parse_and_normalize_date(date1_val)
    d2 = parse_and_normalize_date(date2_val)
    if d1 is None or d2 is None:
        return None
    return abs((d1 - d2).days)


def parse_currency_amount(val: Any) -> Optional[float]:
    """Extracts numeric financial amount from formatted currency strings."""
    if is_missing(val):
        return None
    if isinstance(val, (int, float)):
        return float(val)

    s = str(val).strip()
    # Strip currency labels and non-numeric chars except digits and decimal point
    cleaned = re.sub(r"(?i)\b(?:inr|rs|usd|eur|aud|gbp)\b", "", s)
    cleaned = re.sub(r"[₹$,/\s]", "", cleaned)

    match = re.search(r"[-+]?\d+(?:\.\d+)?", cleaned)
    if match:
        try:
            return float(match.group(0))
        except ValueError:
            return None
    return None


def parse_itemized_breakdown(breakdown_str: Any) -> List[Dict[str, Any]]:
    """Parses itemized repair cost breakdown strings into structured records.
    
    Example:
        'Bodywork and paint: 38500; Tail lamp replacement: 16000; Labor and miscellaneous: 30000'
    Returns:
        [
            {'item': 'Bodywork and paint', 'amount': 38500.0, 'raw': 'Bodywork and paint: 38500'},
            ...
        ]
    """
    if is_missing(breakdown_str):
        return []

    text = str(breakdown_str).strip()
    # Split by semicolon, newline, or pipe
    segments = re.split(r"[;\n|]+", text)
    items: List[Dict[str, Any]] = []

    for seg in segments:
        seg = seg.strip()
        if not seg:
            continue
        if ":" in seg:
            parts = seg.split(":", 1)
            name = parts[0].strip()
            amt = parse_currency_amount(parts[1])
            if amt is not None:
                items.append({
                    "item": name,
                    "amount": amt,
                    "raw": seg,
                })
        elif "-" in seg and any(char.isdigit() for char in seg):
            parts = seg.rsplit("-", 1)
            name = parts[0].strip()
            amt = parse_currency_amount(parts[1])
            if amt is not None:
                items.append({
                    "item": name,
                    "amount": amt,
                    "raw": seg,
                })
        else:
            amt = parse_currency_amount(seg)
            if amt is not None:
                items.append({
                    "item": seg,
                    "amount": amt,
                    "raw": seg,
                })

    return items


def calculate_string_similarity(s1: str, s2: str) -> float:
    """Calculates character bigram Dice-coefficient similarity between two strings."""
    if not s1 and not s2:
        return 1.0
    if not s1 or not s2:
        return 0.0
    if s1 == s2:
        return 1.0

    s1_norm = normalize_whitespace(s1.lower())
    s2_norm = normalize_whitespace(s2.lower())

    if len(s1_norm) < 2 or len(s2_norm) < 2:
        return 1.0 if s1_norm == s2_norm else 0.0

    bigrams1 = [s1_norm[i:i+2] for i in range(len(s1_norm) - 1)]
    bigrams2 = [s2_norm[i:i+2] for i in range(len(s2_norm) - 1)]

    counts1: Dict[str, int] = {}
    for bg in bigrams1:
        counts1[bg] = counts1.get(bg, 0) + 1

    matches = 0
    for bg in bigrams2:
        if counts1.get(bg, 0) > 0:
            matches += 1
            counts1[bg] -= 1

    total = len(bigrams1) + len(bigrams2)
    return (2.0 * matches) / total if total > 0 else 0.0


def calculate_token_overlap(text1: str, text2: str) -> float:
    """Calculates Jaccard token overlap similarity between two narrative descriptions."""
    if not text1 or not text2:
        return 0.0

    tokens1 = set(re.findall(r"\b\w{3,}\b", text1.lower()))
    tokens2 = set(re.findall(r"\b\w{3,}\b", text2.lower()))

    # Remove standard English stopwords
    stopwords = {
        "the", "and", "was", "for", "with", "that", "this", "from",
        "were", "which", "vehicle", "car", "has", "had", "been",
    }
    tokens1 -= stopwords
    tokens2 -= stopwords

    if not tokens1 or not tokens2:
        return 0.0

    intersection = tokens1 & tokens2
    union = tokens1 | tokens2
    return len(intersection) / len(union) if union else 0.0
