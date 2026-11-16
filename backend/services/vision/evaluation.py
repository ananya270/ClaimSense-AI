"""Evaluation summary and metrics reader for Phase 5 CarDD vehicle damage model."""

import json
from pathlib import Path
from typing import Dict, Any, Optional

from backend.utils.logger import setup_logger

logger = setup_logger("claimsense.vision.evaluation")


def get_model_evaluation_metrics() -> Dict[str, Any]:
    """Reads empirical CarDD evaluation results from the reports directory."""
    repo_root = Path(__file__).resolve().parents[3]
    candidate_paths = [
        repo_root / "reports" / "phase5" / "evaluation_results.json",
        repo_root / "reports" / "vehicle_damage" / "evaluation_results.json",
    ]

    json_path = None
    for p in candidate_paths:
        if p.exists():
            json_path = p
            break

    if not json_path:
        logger.warning(f"Evaluation results not found in candidate paths: {[str(p) for p in candidate_paths]}")
        return {
            "status": "not_evaluated",
            "message": "Evaluation results file not yet generated.",
        }

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["status"] = "evaluated"
        return data
    except Exception as exc:
        logger.error(f"Error reading evaluation results from {json_path}: {exc}")
        return {
            "status": "error",
            "message": str(exc),
        }
