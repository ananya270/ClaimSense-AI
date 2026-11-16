"""Phase 7: Cross-Source Verification Rules, Status Constants, and Decision-Support Policies."""

# Comparison Statuses
STATUS_MATCH = "MATCH"
STATUS_MISMATCH = "MISMATCH"
STATUS_MISSING_IN_SOURCE = "MISSING_IN_SOURCE"
STATUS_INCONCLUSIVE = "INCONCLUSIVE"
STATUS_NOT_VISUALLY_CONFIRMED = "NOT_VISUALLY_CONFIRMED"
STATUS_VISUAL_ONLY_FINDING = "VISUAL_ONLY_FINDING"
STATUS_POTENTIAL_DISCREPANCY = "POTENTIAL_DISCREPANCY"

ALL_STATUSES = {
    STATUS_MATCH,
    STATUS_MISMATCH,
    STATUS_MISSING_IN_SOURCE,
    STATUS_INCONCLUSIVE,
    STATUS_NOT_VISUALLY_CONFIRMED,
    STATUS_VISUAL_ONLY_FINDING,
    STATUS_POTENTIAL_DISCREPANCY,
}

# Severity Levels
SEVERITY_LOW = "LOW"
SEVERITY_MEDIUM = "MEDIUM"
SEVERITY_HIGH = "HIGH"
SEVERITY_CRITICAL = "CRITICAL"

ALL_SEVERITIES = {
    SEVERITY_LOW,
    SEVERITY_MEDIUM,
    SEVERITY_HIGH,
    SEVERITY_CRITICAL,
}

# Overall Verification Assessment Statuses
OVERALL_CONSISTENT = "CONSISTENT"
OVERALL_REVIEW_REQUIRED = "REVIEW_REQUIRED"
OVERALL_INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"

ALL_OVERALL_STATUSES = {
    OVERALL_CONSISTENT,
    OVERALL_REVIEW_REQUIRED,
    OVERALL_INSUFFICIENT_EVIDENCE,
}

DECISION_SUPPORT_DISCLAIMER = (
    "ClaimSense AI Cross-Source Verification provides structured decision support for "
    "insurance claims assessors by cross-referencing multi-source evidentiary documentation. "
    "Findings highlight corroborations, variances, and omissions across sources. "
    "They do not constitute an automated legal adjudication, claim approval, or fraud declaration."
)
