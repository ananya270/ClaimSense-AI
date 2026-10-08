"""Health check route for ClaimSense AI."""
from datetime import datetime, timezone
from flask import Blueprint, jsonify, current_app

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    """Health-check endpoint returning system operational status."""
    return jsonify({
        "status": "healthy",
        "project": "ClaimSense AI",
        "description": "AI-Powered Insurance Claim Verification Decision-Support Prototype",
        "version": "1.0.0",
        "phase": "Phase 1 - Project Foundation",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": current_app.config.get("FLASK_ENV", "development"),
    }), 200
