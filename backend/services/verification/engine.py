"""Verification Engine Orchestrator for Cross-Source Consistency (Phase 7).

Coordinates cross-source data retrieval, rule execution, consistency scoring,
and persistent SQLite storage for multi-run verification history.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.database.models import (
    Claim,
    ClaimVerificationRun,
    ClaimVerificationFinding,
)
from backend.services.verification.retriever import retrieve_cross_source_context
from backend.services.verification.rules import (
    BaseVerificationRule,
    DEFAULT_VERIFICATION_RULES,
    RuleFinding,
)
from backend.services.verification.scorer import (
    calculate_consistency_score,
    ConsistencyScoreResult,
)


class VerificationEngine:
    """Singleton service for executing transparent cross-source verification."""

    ENGINE_VERSION = "1.0.0"

    @classmethod
    def run_verification(
        cls,
        claim_id: str,
        db_session: Any,
        upload_folder: Optional[Path] = None,
        custom_rules: Optional[List[BaseVerificationRule]] = None,
    ) -> Dict[str, Any]:
        """Executes full Phase 7 cross-source verification for a claim.
        
        Saves the verification run and rule-level findings to SQLite,
        updates claim metadata on disk, and returns the structured result.
        """
        active_rules = custom_rules if custom_rules is not None else DEFAULT_VERIFICATION_RULES

        # 1. Gather all cross-source evidence for this Claim ID
        ctx = retrieve_cross_source_context(
            claim_id=claim_id,
            db_session=db_session,
            upload_folder=upload_folder,
        )

        # 2. Evaluate all configured verification rules
        findings: List[RuleFinding] = []
        for rule in active_rules:
            try:
                finding = rule.evaluate(ctx)
                findings.append(finding)
            except Exception as e:
                # Fallback safeguard: capture rule evaluation error without crashing engine
                findings.append(RuleFinding(
                    rule_id=rule.rule_id,
                    rule_name=rule.rule_name,
                    category=rule.category,
                    source_fields=[],
                    original_values={},
                    normalized_values={},
                    status="UNVERIFIED",
                    severity="LOW",
                    explanation=f"Rule evaluation encountered an exception: {str(e)}",
                    weight=rule.weight,
                ))

        # 3. Calculate transparent consistency score
        score_res: ConsistencyScoreResult = calculate_consistency_score(findings)

        # 4. Generate unique Verification Run ID
        now_utc = datetime.now(timezone.utc)
        run_suffix = uuid.uuid4().hex[:6].upper()
        run_id = f"VRUN-{now_utc.strftime('%Y%m%d%H%M%S')}-{run_suffix}"

        # 5. Persist Run to SQLite
        vrun = ClaimVerificationRun(
            run_id=run_id,
            claim_id=claim_id,
            overall_status=score_res.overall_status,
            consistency_score=score_res.score,
            evaluated_rules_count=score_res.evaluated_count,
            matching_rules_count=score_res.matching_count,
            mismatching_rules_count=score_res.mismatching_count,
            missing_rules_count=score_res.missing_count,
            unverified_rules_count=score_res.unverified_count,
            high_severity_count=score_res.high_severity_count,
            score_explanation=score_res.explanation,
            engine_version=cls.ENGINE_VERSION,
            created_at=now_utc,
        )
        db_session.add(vrun)
        db_session.flush()

        # 6. Persist Rule Findings
        for f in findings:
            finding_rec = ClaimVerificationFinding(
                run_id=run_id,
                claim_id=claim_id,
                rule_id=f.rule_id,
                rule_name=f.rule_name,
                category=f.category,
                source_fields=json.dumps(f.source_fields),
                original_values=json.dumps(f.original_values),
                normalized_values=json.dumps(f.normalized_values),
                status=f.status,
                severity=f.severity,
                explanation=f.explanation,
                evidence_references=json.dumps(f.evidence_references),
                created_at=now_utc,
            )
            db_session.add(finding_rec)

        db_session.commit()

        # 7. Update disk metadata.json if folder provided
        run_dict = vrun.to_dict(include_findings=True)
        if upload_folder:
            meta_path = upload_folder / claim_id / "metadata.json"
            if meta_path.exists():
                try:
                    with open(meta_path, "r", encoding="utf-8") as file:
                        meta = json.load(file)
                    meta["latest_verification_run"] = run_dict
                    with open(meta_path, "w", encoding="utf-8") as file:
                        json.dump(meta, file, indent=2)
                except Exception:
                    pass

        return {
            "success": True,
            "claim_id": claim_id,
            "verification_run": run_dict,
            "score_result": score_res.to_dict(),
        }

    @classmethod
    def get_latest_run(cls, claim_id: str, db_session: Any) -> Optional[Dict[str, Any]]:
        """Retrieves the latest verification run and findings for a claim."""
        vrun = (
            db_session.query(ClaimVerificationRun)
            .filter_by(claim_id=claim_id)
            .order_by(ClaimVerificationRun.id.desc())
            .first()
        )
        return vrun.to_dict(include_findings=True) if vrun else None

    @classmethod
    def get_history(cls, claim_id: str, db_session: Any) -> List[Dict[str, Any]]:
        """Retrieves summary history of all verification runs for a claim."""
        runs = (
            db_session.query(ClaimVerificationRun)
            .filter_by(claim_id=claim_id)
            .order_by(ClaimVerificationRun.id.desc())
            .all()
        )
        return [r.to_dict(include_findings=False) for r in runs]

    @classmethod
    def get_run_by_id(cls, run_id: str, db_session: Any) -> Optional[Dict[str, Any]]:
        """Retrieves a specific verification run by its unique run_id."""
        vrun = db_session.query(ClaimVerificationRun).filter_by(run_id=run_id).first()
        return vrun.to_dict(include_findings=True) if vrun else None
