"""Transparent, explainable consistency scoring and assessment classification (Phase 7)."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from backend.services.verification.rules import (
    DECISION_SUPPORT_DISCLAIMER,
    OVERALL_CONSISTENT,
    OVERALL_INSUFFICIENT_EVIDENCE,
    OVERALL_REVIEW_REQUIRED,
    SEVERITY_CRITICAL,
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


def compute_verification_score_and_summary(
    findings: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Calculates an explainable consistency score, breakdown metrics, and review recommendations.
    
    Principles:
    1. Missing evidence is NOT penalized as a mismatch.
    2. Inconclusive comparisons are treated as neutral information.
    3. No double-counting of the same discrepancy.
    4. Findings provide decision support, never an automated claim rejection.
    """
    total = len(findings)
    if total == 0:
        return {
            "consistency_score": 100.0,
            "evidence_coverage_percentage": 0.0,
            "overall_status": OVERALL_INSUFFICIENT_EVIDENCE,
            "total_comparisons": 0,
            "matched_comparisons": 0,
            "mismatched_comparisons": 0,
            "missing_evidence_count": 0,
            "inconclusive_count": 0,
            "high_severity_count": 0,
            "critical_severity_count": 0,
            "cv_unevaluated_count": 0,
            "status_breakdown": {},
            "severity_breakdown": {},
            "recommendations": ["No evidence sources available for cross-source comparison."],
            "disclaimer": DECISION_SUPPORT_DISCLAIMER,
        }

    status_counts: Dict[str, int] = {}
    severity_counts: Dict[str, int] = {
        SEVERITY_LOW: 0,
        SEVERITY_MEDIUM: 0,
        SEVERITY_HIGH: 0,
        SEVERITY_CRITICAL: 0,
    }

    # Sub-classify specific inconclusive categories for actionable reporting
    cv_unevaluated_count = 0
    policy_validity_inconclusive = False
    other_inconclusive_count = 0

    for f in findings:
        st = f.get("comparison_status", STATUS_INCONCLUSIVE)
        sv = f.get("severity", SEVERITY_LOW)
        status_counts[st] = status_counts.get(st, 0) + 1
        severity_counts[sv] = severity_counts.get(sv, 0) + 1

        if st == STATUS_INCONCLUSIVE:
            fn = str(f.get("field_name", "")).lower()
            orig_b = str(f.get("original_value_b", "")).lower()
            src_b = str(f.get("source_b", "")).lower()
            ev_ref = f.get("evidence_references", {}) or {}
            reason = str(ev_ref.get("reason", "")).lower()

            if (
                "damage:" in fn
                or "vision" in src_b
                or "analysis not executed" in orig_b
                or "no vision data" in orig_b
                or reason == "vision_analysis_unavailable"
                or "opencv" in orig_b
            ):
                cv_unevaluated_count += 1
            elif "policy" in fn or "validity" in fn or "coverage" in fn:
                policy_validity_inconclusive = True
            else:
                other_inconclusive_count += 1

    matched = status_counts.get(STATUS_MATCH, 0)
    mismatched = status_counts.get(STATUS_MISMATCH, 0)
    missing = status_counts.get(STATUS_MISSING_IN_SOURCE, 0)
    inconclusive = status_counts.get(STATUS_INCONCLUSIVE, 0)
    not_confirmed = status_counts.get(STATUS_NOT_VISUALLY_CONFIRMED, 0)
    visual_only = status_counts.get(STATUS_VISUAL_ONLY_FINDING, 0)
    potential_discrepancy = status_counts.get(STATUS_POTENTIAL_DISCREPANCY, 0)

    high_sev = severity_counts.get(SEVERITY_HIGH, 0)
    crit_sev = severity_counts.get(SEVERITY_CRITICAL, 0)

    # Evaluated items are those with actual observable data compared across sources
    # (i.e. excluding missing sources and unverified inconclusive items)
    evaluated_with_data = matched + mismatched + not_confirmed + visual_only + potential_discrepancy
    coverage_percentage = round((evaluated_with_data / total) * 100.0, 1) if total > 0 else 0.0

    # Total items evaluated in the consistency scoring formula:
    # Inconclusive findings represent neutral information (0.50 weight).
    # Missing evidence is NOT penalized as a mismatch and is excluded from evaluated denominator.
    scoring_items = evaluated_with_data + inconclusive

    if scoring_items == 0:
        score = 50.0 if missing > 0 else 100.0
        overall_status = OVERALL_INSUFFICIENT_EVIDENCE
    else:
        # Weighted points:
        # Match = 1.0 (positive corroboration)
        # Inconclusive = 0.50 (neutral: neither confirmed match nor conflict; reflects unverified state)
        # Visual only = 0.60 (unmentioned damage: consistent with impact/vehicle state but uncorroborated by narrative)
        # Not visually confirmed = 0.70 (partial, since camera angles vary)
        # Potential discrepancy = 0.35 (uncertainty/variance)
        # Mismatch = 0.0 (direct conflict)
        raw_points = (
            (matched * 1.0)
            + (visual_only * 0.60)
            + (not_confirmed * 0.70)
            + (potential_discrepancy * 0.35)
            + (inconclusive * 0.50)
            + (mismatched * 0.0)
        )
        base_score = (raw_points / scoring_items) * 100.0

        # Apply specific severity penalties (bounded)
        penalties = (crit_sev * 25.0) + (high_sev * 15.0)
        score = max(0.0, min(100.0, round(base_score - penalties, 1)))

        # Determine overall assessment status
        # 1. Critical/High discrepancies or direct mismatches always require assessor review
        if crit_sev > 0 or high_sev > 0 or mismatched > 0:
            overall_status = OVERALL_REVIEW_REQUIRED
        # 2. Insufficient data: missing evidence dominates or fewer than 2 items could be evaluated
        elif missing >= (total * 0.6) or evaluated_with_data < 2:
            overall_status = OVERALL_INSUFFICIENT_EVIDENCE
        # 3. Review required when:
        #    - Reported vehicle damage was not evaluated by Computer Vision (cv_unevaluated_count > 0)
        #    - Multiple unmentioned visual damage findings detected (visual_only >= 3)
        #    - Substantial inconclusive evidence (inconclusive >= 3)
        #    - Score drops below acceptable threshold (< 70.0)
        elif score < 70.0 or visual_only >= 3 or cv_unevaluated_count > 0 or inconclusive >= 3:
            overall_status = OVERALL_REVIEW_REQUIRED
        # 4. Consistent: evaluated items corroborate without core unverified evidence
        else:
            overall_status = OVERALL_CONSISTENT

    # Generate actionable, complete assessor recommendations
    recommendations: List[str] = []
    if crit_sev > 0:
        recommendations.append(
            "CRITICAL: Policy coverage period conflict identified. Verify policy endorsement and renewal history before proceeding."
        )
    if high_sev > 0 or mismatched > 0:
        recommendations.append(
            "Direct factual discrepancies observed in core identity, registration, or dates. Human assessor review required."
        )
    if cv_unevaluated_count > 0:
        recommendations.append(
            f"Automated Computer Vision damage analysis was not executed or failed for {cv_unevaluated_count} reported vehicle damage item(s). "
            "Execute automated vehicle damage detection or perform manual photographic damage assessment."
        )
    if not_confirmed > 0:
        recommendations.append(
            f"{not_confirmed} reported vehicle damage item(s) were not visually confirmed by Computer Vision. Request additional multi-angle vehicle photographs."
        )
    if visual_only >= 3:
        recommendations.append(
            f"Computer Vision detected {visual_only} damage item(s) unlisted in claimant statement. Assessor review recommended to inspect vehicle pre-existing damage records."
        )
    elif visual_only > 0:
        recommendations.append(
            f"Computer Vision detected {visual_only} damage item(s) unlisted in claimant statement. Check vehicle pre-existing damage inspection records."
        )
    if policy_validity_inconclusive:
        recommendations.append(
            "Policy validity coverage period could not be confirmed from document OCR data alone. "
            "Verify active policy effective dates against policy schedule or underwriting records."
        )
    if other_inconclusive_count > 0:
        recommendations.append(
            f"{other_inconclusive_count} comparison(s) returned inconclusive results due to ambiguous or unparseable evidentiary data. Manual verification advised."
        )
    if potential_discrepancy > 0:
        recommendations.append(
            "Repair invoice contains items with uncertain damage correspondence. Review garage estimate against claimed impact points."
        )
    if missing > 0:
        recommendations.append(
            f"{missing} evidence field(s) were missing across documentation. Consider requesting supplementary documents if relevant to adjudication."
        )
    if coverage_percentage < 70.0 and total >= 3:
        recommendations.append(
            f"Evidence coverage is limited ({coverage_percentage}% of checks evaluated). "
            "Consistency score reflects evaluated items with neutral weighting for unevaluated evidence."
        )
    if not recommendations:
        recommendations.append(
            "All evaluated evidence sources corroborate consistently. Low probability of documentary discrepancy."
        )

    return {
        "consistency_score": score,
        "evidence_coverage_percentage": coverage_percentage,
        "overall_status": overall_status,
        "total_comparisons": total,
        "matched_comparisons": matched,
        "mismatched_comparisons": mismatched,
        "missing_evidence_count": missing,
        "inconclusive_count": inconclusive,
        "high_severity_count": high_sev,
        "critical_severity_count": crit_sev,
        "cv_unevaluated_count": cv_unevaluated_count,
        "status_breakdown": status_counts,
        "severity_breakdown": severity_counts,
        "recommendations": recommendations,
        "disclaimer": DECISION_SUPPORT_DISCLAIMER,
    }
