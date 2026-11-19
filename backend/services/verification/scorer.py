"""Transparent Consistency Score Calculation Engine (Phase 7).

Computes an objective, explainable multi-source consistency score based on
transparently weighted verification rules, excluding missing and not-applicable
evidence fields from the denominator.
"""

from typing import Any, Dict, List, Optional
from backend.services.verification.rules import RuleFinding


class ConsistencyScoreResult:
    """Encapsulates the mathematical calculation and explanation of consistency scoring."""

    def __init__(
        self,
        score: Optional[float],
        overall_status: str,  # CONSISTENT, REVIEW_REQUIRED, CONFLICTING, INSUFFICIENT_DATA
        evaluated_count: int,
        matching_count: int,
        mismatching_count: int,
        missing_count: int,
        unverified_count: int,
        not_applicable_count: int,
        high_severity_count: int,
        medium_severity_count: int,
        low_severity_count: int,
        explanation: str,
        formula_breakdown: Dict[str, Any],
    ):
        self.score = score
        self.overall_status = overall_status
        self.evaluated_count = evaluated_count
        self.matching_count = matching_count
        self.mismatching_count = mismatching_count
        self.missing_count = missing_count
        self.unverified_count = unverified_count
        self.not_applicable_count = not_applicable_count
        self.high_severity_count = high_severity_count
        self.medium_severity_count = medium_severity_count
        self.low_severity_count = low_severity_count
        self.explanation = explanation
        self.formula_breakdown = formula_breakdown

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": self.score,
            "overall_status": self.overall_status,
            "evaluated_count": self.evaluated_count,
            "matching_count": self.matching_count,
            "mismatching_count": self.mismatching_count,
            "missing_count": self.missing_count,
            "unverified_count": self.unverified_count,
            "not_applicable_count": self.not_applicable_count,
            "high_severity_count": self.high_severity_count,
            "medium_severity_count": self.medium_severity_count,
            "low_severity_count": self.low_severity_count,
            "explanation": self.explanation,
            "formula_breakdown": self.formula_breakdown,
            "disclaimer": (
                "The consistency score is an objective mathematical index of multi-source document agreement. "
                "It does not represent a fraud probability or legal validity assessment."
            ),
        }


def calculate_consistency_score(
    findings: List[RuleFinding],
    min_evaluated_rules: int = 2,
    unverified_credit_ratio: float = 0.25,
) -> ConsistencyScoreResult:
    """Calculates a transparent consistency score from rule findings.
    
    Guarantees:
    1. Only evaluated rules contribute to the score.
    2. Missing and NOT_APPLICABLE fields are strictly excluded from the denominator.
    3. Unverified fields are mathematically distinguished from matching fields.
    4. When insufficient information exists, returns INSUFFICIENT_DATA status.
    5. Produces an exact formula breakdown explaining every calculation step.
    """
    total_evaluated = 0
    total_matching = 0
    total_mismatching = 0
    total_missing = 0
    total_unverified = 0
    total_not_applicable = 0

    high_sev = 0
    med_sev = 0
    low_sev = 0

    earned_points = 0.0
    denominator_weight = 0.0

    rule_contributions = []

    for f in findings:
        st = f.status.upper()
        w = float(f.weight)

        if st == "MATCH":
            total_evaluated += 1
            total_matching += 1
            earned = w * 1.0
            earned_points += earned
            denominator_weight += w
            rule_contributions.append({
                "rule_id": f.rule_id,
                "status": st,
                "weight": w,
                "credit_ratio": 1.0,
                "points_earned": earned,
            })
            if f.severity == "HIGH":
                high_sev += 1
            elif f.severity == "MEDIUM":
                med_sev += 1
            else:
                low_sev += 1

        elif st == "MISMATCH":
            total_evaluated += 1
            total_mismatching += 1
            earned = 0.0
            earned_points += earned
            denominator_weight += w
            rule_contributions.append({
                "rule_id": f.rule_id,
                "status": st,
                "weight": w,
                "credit_ratio": 0.0,
                "points_earned": earned,
            })
            if f.severity == "HIGH":
                high_sev += 1
            elif f.severity == "MEDIUM":
                med_sev += 1
            else:
                low_sev += 1

        elif st == "UNVERIFIED":
            total_evaluated += 1
            total_unverified += 1
            earned = w * unverified_credit_ratio
            earned_points += earned
            denominator_weight += w
            rule_contributions.append({
                "rule_id": f.rule_id,
                "status": st,
                "weight": w,
                "credit_ratio": unverified_credit_ratio,
                "points_earned": earned,
            })
            low_sev += 1

        elif st == "MISSING":
            total_missing += 1
            # Excluded from denominator

        elif st == "NOT_APPLICABLE":
            total_not_applicable += 1
            # Excluded from denominator

    # Check for insufficient data
    if total_evaluated < min_evaluated_rules or denominator_weight <= 0.0:
        explanation = (
            f"Insufficient data to compute an objective consistency score: only {total_evaluated} rule(s) "
            f"could be evaluated against submitted evidence (minimum {min_evaluated_rules} required). "
            f"{total_missing} required field(s) are missing."
        )
        return ConsistencyScoreResult(
            score=None,
            overall_status="INSUFFICIENT_DATA",
            evaluated_count=total_evaluated,
            matching_count=total_matching,
            mismatching_count=total_mismatching,
            missing_count=total_missing,
            unverified_count=total_unverified,
            not_applicable_count=total_not_applicable,
            high_severity_count=high_sev,
            medium_severity_count=med_sev,
            low_severity_count=low_sev,
            explanation=explanation,
            formula_breakdown={
                "earned_points": earned_points,
                "denominator_weight": denominator_weight,
                "rules": rule_contributions,
                "insufficient_data": True,
            },
        )

    # Standard formula calculation
    raw_score = (earned_points / denominator_weight) * 100.0
    final_score = round(max(0.0, min(100.0, raw_score)), 1)

    # Determine overall status
    if high_sev > 0 or final_score < 60.0:
        overall_status = "CONFLICTING"
    elif total_mismatching > 0 or final_score < 85.0:
        overall_status = "REVIEW_REQUIRED"
    else:
        overall_status = "CONSISTENT"

    explanation = (
        f"Consistency score of {final_score}% calculated across {total_evaluated} evaluated verification rules "
        f"with combined weight {denominator_weight:.1f} ({total_matching} matching, {total_mismatching} mismatching, "
        f"{total_unverified} unverified). {total_missing} missing and {total_not_applicable} not-applicable "
        f"rules were excluded from the denominator. "
        f"Formula: (Earned Points {earned_points:.1f} / Total Evaluated Weight {denominator_weight:.1f}) × 100."
    )

    return ConsistencyScoreResult(
        score=final_score,
        overall_status=overall_status,
        evaluated_count=total_evaluated,
        matching_count=total_matching,
        mismatching_count=total_mismatching,
        missing_count=total_missing,
        unverified_count=total_unverified,
        not_applicable_count=total_not_applicable,
        high_severity_count=high_sev,
        medium_severity_count=med_sev,
        low_severity_count=low_sev,
        explanation=explanation,
        formula_breakdown={
            "earned_points": round(earned_points, 2),
            "denominator_weight": round(denominator_weight, 2),
            "unverified_credit_ratio": unverified_credit_ratio,
            "rules": rule_contributions,
            "insufficient_data": False,
        },
    )
