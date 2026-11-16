"""Field normalization and comparison logic across documents (Phase 7)."""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Set, Tuple

from backend.services.verification.rules import (
    SEVERITY_CRITICAL,
    SEVERITY_HIGH,
    SEVERITY_LOW,
    SEVERITY_MEDIUM,
    STATUS_INCONCLUSIVE,
    STATUS_MATCH,
    STATUS_MISMATCH,
    STATUS_MISSING_IN_SOURCE,
)


# =========================================================================
# Name Normalization & Comparison
# =========================================================================

_HONORIFIC_PREFIXES = {
    "mr",
    "mrs",
    "ms",
    "dr",
    "prof",
    "shri",
    "smt",
    "kumari",
    "master",
    "adv",
}


def normalize_name(name: Any) -> str:
    """Normalizes person names by removing honorifics, punctuation, and extra whitespace."""
    if not name:
        return ""
    text = str(name).strip().lower()
    # Remove punctuation
    text = re.sub(r"[^\w\s]", " ", text)
    tokens = text.split()
    # Filter out honorifics
    filtered = [t for t in tokens if t not in _HONORIFIC_PREFIXES]
    return " ".join(filtered) if filtered else text


def _levenshtein_distance(s1: str, s2: str) -> int:
    """Computes Damerau-Levenshtein distance accounting for transpositions."""
    d: Dict[Tuple[int, int], int] = {}
    len1 = len(s1)
    len2 = len(s2)
    for i in range(-1, len1 + 1):
        d[(i, -1)] = i + 1
    for j in range(-1, len2 + 1):
        d[(-1, j)] = j + 1

    for i in range(len1):
        for j in range(len2):
            cost = 0 if s1[i] == s2[j] else 1
            d[(i, j)] = min(
                d[(i - 1, j)] + 1,          # deletion
                d[(i, j - 1)] + 1,          # insertion
                d[(i - 1, j - 1)] + cost,    # substitution
            )
            if i > 0 and j > 0 and s1[i] == s2[j - 1] and s1[i - 1] == s2[j]:
                d[(i, j)] = min(d[(i, j)], d[(i - 2, j - 2)] + cost)  # transposition

    return d[(len1 - 1, len2 - 1)]


def compare_names(name_a: str, name_b: str) -> Tuple[bool, float, str]:
    """Compares two names taking honorifics, word ordering, and minor typos into account.
    
    Returns:
        (is_match, confidence, explanation)
    """
    norm_a = normalize_name(name_a)
    norm_b = normalize_name(name_b)

    if not norm_a or not norm_b:
        return False, 0.5, "One or both name values are empty"

    if norm_a == norm_b:
        return True, 1.0, f"Names match exactly ('{name_a}' == '{name_b}')"

    tokens_a = set(norm_a.split())
    tokens_b = set(norm_b.split())

    # Exact token set match (handles 'Rajesh Sharma' vs 'Sharma, Rajesh')
    if tokens_a == tokens_b:
        return True, 0.98, f"Name word tokens match with differing ordering ('{name_a}' vs '{name_b}')"

    # Subset match (e.g. 'Rajesh Kumar Sharma' vs 'Rajesh Sharma')
    if tokens_a.issubset(tokens_b) or tokens_b.issubset(tokens_a):
        return True, 0.90, f"Names match with partial middle/initial variation ('{name_a}' vs '{name_b}')"

    # Fuzzy edit distance comparison
    max_len = max(len(norm_a), len(norm_b), 1)
    dist = _levenshtein_distance(norm_a, norm_b)
    similarity = 1.0 - (dist / max_len)

    if similarity >= 0.80:
        return True, round(similarity, 2), f"Names match with minor character variation ({dist} char typo, '{name_a}' ~ '{name_b}')"

    return False, round(similarity, 2), f"Names do not match ('{name_a}' vs '{name_b}')"


# =========================================================================
# Vehicle Registration Normalization & Comparison
# =========================================================================

# Standard OCR character confusions in alphanumeric license plates
_OCR_CHAR_MAP = {
    "O": "0",
    "I": "1",
    "Z": "2",
    "S": "5",
    "B": "8",
    "G": "6",
}


def normalize_vehicle_reg(reg: Any, apply_ocr_fixes: bool = False) -> str:
    """Standardizes vehicle license plate strings by stripping whitespace and non-alphanumerics."""
    if not reg:
        return ""
    cleaned = re.sub(r"[^A-Za-z0-9]", "", str(reg)).upper()
    if apply_ocr_fixes and len(cleaned) >= 4:
        # In Indian plates: LL-NN-LL-NNNN (positions 2,3 and trailing 4 are usually digits)
        chars = list(cleaned)
        # Apply mapping to digits where digits are expected
        for idx in range(len(chars)):
            # If position looks like a digit slot (last 4 characters)
            if idx >= len(chars) - 4 and chars[idx] in _OCR_CHAR_MAP:
                chars[idx] = _OCR_CHAR_MAP[chars[idx]]
        cleaned = "".join(chars)
    return cleaned


def compare_vehicle_registrations(reg_a: str, reg_b: str) -> Tuple[bool, float, str]:
    """Compares vehicle registrations with OCR substitution tolerance."""
    raw_norm_a = normalize_vehicle_reg(reg_a, apply_ocr_fixes=False)
    raw_norm_b = normalize_vehicle_reg(reg_b, apply_ocr_fixes=False)

    if not raw_norm_a or not raw_norm_b:
        return False, 0.5, "One or both vehicle registrations are empty"

    if raw_norm_a == raw_norm_b:
        return True, 1.0, f"Vehicle registration matches exactly ('{reg_a}' == '{reg_b}')"

    # Try with OCR digit ambiguity normalization
    ocr_norm_a = normalize_vehicle_reg(reg_a, apply_ocr_fixes=True)
    ocr_norm_b = normalize_vehicle_reg(reg_b, apply_ocr_fixes=True)

    if ocr_norm_a == ocr_norm_b:
        return True, 0.92, f"Vehicle registration matches accounting for common OCR character confusion ('{reg_a}' ~ '{reg_b}')"

    return False, 1.0, f"Vehicle registration numbers conflict ('{reg_a}' vs '{reg_b}')"


# =========================================================================
# Date Normalization & Comparison
# =========================================================================

_DATE_PATTERNS = [
    (re.compile(r"(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})"), "ymd"),
    (re.compile(r"(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})"), "dmy"),
]

_MONTH_NAMES = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}


def normalize_date(val: Any) -> Optional[date]:
    """Parses various date string formats into standard Python date."""
    if not val:
        return None
    if isinstance(val, (date, datetime)):
        return val if isinstance(val, date) else val.date()

    text = str(val).strip().lower()

    # Try textual dates like '28 Sep 2026' or 'September 28, 2026'
    textual_m = re.search(r"(\d{1,2})\s+([a-z]+)\s+(\d{4})", text)
    if textual_m:
        d_val = int(textual_m.group(1))
        m_str = textual_m.group(2)[:3]
        y_val = int(textual_m.group(3))
        if m_str in _MONTH_NAMES:
            try:
                return date(y_val, _MONTH_NAMES[m_str], d_val)
            except ValueError:
                pass

    textual_m2 = re.search(r"([a-z]+)\s+(\d{1,2}),?\s+(\d{4})", text)
    if textual_m2:
        m_str = textual_m2.group(1)[:3]
        d_val = int(textual_m2.group(2))
        y_val = int(textual_m2.group(3))
        if m_str in _MONTH_NAMES:
            try:
                return date(y_val, _MONTH_NAMES[m_str], d_val)
            except ValueError:
                pass

    # Numeric formats
    for pattern, kind in _DATE_PATTERNS:
        m = pattern.search(text)
        if m:
            try:
                if kind == "ymd":
                    return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
                elif kind == "dmy":
                    # Assume day/month/year for standard international/Indian format
                    d = int(m.group(1))
                    mo = int(m.group(2))
                    y = int(m.group(3))
                    # Sanity check: if month > 12 and day <= 12, swap
                    if mo > 12 >= d:
                        d, mo = mo, d
                    return date(y, mo, d)
            except ValueError:
                continue

    return None


def compare_dates(date_a: str, date_b: str) -> Tuple[str, float, str]:
    """Compares two dates across evidence sources."""
    d_a = normalize_date(date_a)
    d_b = normalize_date(date_b)

    if not d_a and not d_b:
        return STATUS_MISSING_IN_SOURCE, 1.0, "Accident date missing in both sources"
    if not d_a or not d_b:
        present = date_a if d_a else date_b
        return (
            STATUS_MISSING_IN_SOURCE,
            0.9,
            f"Date present in one source ('{present}') but missing or unparseable in other",
        )

    if d_a == d_b:
        return STATUS_MATCH, 1.0, f"Accident dates match ({d_a.isoformat()})"
    return (
        STATUS_MISMATCH,
        1.0,
        f"Conflicting accident dates observed ({d_a.isoformat()} vs {d_b.isoformat()})",
    )


# =========================================================================
# Policy Validity Period vs Accident Date
# =========================================================================

def parse_policy_period(text: str) -> Tuple[Optional[date], Optional[date]]:
    """Extracts start and end dates from a policy coverage or validity text snippet."""
    if not text:
        return None, None

    # Search for date pairs like '2024-01-01 to 2025-01-01' or '01/01/2024 - 31/12/2024'
    parts = re.split(r"\s+(?:to|until|-|through)\s+", str(text), flags=re.IGNORECASE)
    if len(parts) >= 2:
        d1 = normalize_date(parts[0])
        d2 = normalize_date(parts[1])
        if d1 and d2:
            return (min(d1, d2), max(d1, d2))

    # Try extracting all dates from the text
    found_dates = []
    for pattern, kind in _DATE_PATTERNS:
        for m in pattern.finditer(text):
            try:
                if kind == "ymd":
                    found_dates.append(date(int(m.group(1)), int(m.group(2)), int(m.group(3))))
                elif kind == "dmy":
                    found_dates.append(date(int(m.group(3)), int(m.group(2)), int(m.group(1))))
            except ValueError:
                continue

    if len(found_dates) >= 2:
        found_dates.sort()
        return found_dates[0], found_dates[-1]

    return None, None


def compare_policy_validity(
    accident_date_val: Any,
    validity_val: Any = None,
    policy_start_val: Any = None,
    policy_end_val: Any = None,
) -> Tuple[str, str, float, str]:
    """Compares the accident date against policy coverage start and end dates.
    
    Returns:
        (status, severity, confidence, explanation)
    """
    acc_d = normalize_date(accident_date_val)
    if not acc_d:
        return (
            STATUS_INCONCLUSIVE,
            SEVERITY_LOW,
            0.5,
            "Accident date is missing or unparseable; cannot evaluate policy coverage validity.",
        )

    # Determine start and end dates
    start_d = normalize_date(policy_start_val)
    end_d = normalize_date(policy_end_val)

    if (not start_d or not end_d) and validity_val:
        p_start, p_end = parse_policy_period(validity_val)
        start_d = start_d or p_start
        end_d = end_d or p_end

    if not start_d and not end_d:
        return (
            STATUS_INCONCLUSIVE,
            SEVERITY_LOW,
            0.6,
            "Policy validity coverage period could not be extracted with high confidence from documents. "
            "Policy validity cannot be verified or disproven from OCR data alone.",
        )

    # Check boundaries
    if start_d and acc_d < start_d:
        return (
            STATUS_MISMATCH,
            SEVERITY_CRITICAL,
            1.0,
            f"Accident date ({acc_d.isoformat()}) occurred BEFORE policy effective start date ({start_d.isoformat()}).",
        )

    if end_d and acc_d > end_d:
        return (
            STATUS_MISMATCH,
            SEVERITY_CRITICAL,
            1.0,
            f"Accident date ({acc_d.isoformat()}) occurred AFTER policy expiry date ({end_d.isoformat()}).",
        )

    coverage_str = f"{start_d.isoformat() if start_d else 'earlier'} to {end_d.isoformat() if end_d else 'open'}"
    return (
        STATUS_MATCH,
        SEVERITY_LOW,
        1.0,
        f"Accident date ({acc_d.isoformat()}) falls safely within the active policy coverage window ({coverage_str}).",
    )


# =========================================================================
# Policy Number Normalization & Comparison
# =========================================================================

def normalize_policy_num(pol: Any) -> str:
    """Strips punctuation, hyphens, and whitespace from policy numbers."""
    if not pol:
        return ""
    return re.sub(r"[^A-Za-z0-9]", "", str(pol)).upper()


def compare_policy_numbers(pol_a: str, pol_b: str) -> Tuple[bool, float, str]:
    """Compares two policy number strings."""
    norm_a = normalize_policy_num(pol_a)
    norm_b = normalize_policy_num(pol_b)

    if not norm_a or not norm_b:
        return False, 0.5, "One or both policy numbers are empty"

    if norm_a == norm_b:
        return True, 1.0, f"Policy numbers match exactly ('{pol_a}' == '{pol_b}')"

    # Substring match (e.g. prefix stripped)
    if (len(norm_a) >= 6 and norm_a in norm_b) or (len(norm_b) >= 6 and norm_b in norm_a):
        return True, 0.90, f"Policy numbers match as substring/prefix variation ('{pol_a}' ~ '{pol_b}')"

    return False, 1.0, f"Policy numbers conflict ('{pol_a}' vs '{pol_b}')"
