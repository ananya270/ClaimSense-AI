"""Database package for ClaimSense AI (Phase 3)."""
from backend.database.models import (
    Base,
    User,
    Claim,
    Document,
    ClaimImage,
    ExtractedInformation,
    ImageAnalysis,
    VerificationResult,
    RiskAssessment,
    Report,
)
from backend.database.db import (
    init_database,
    get_db_session,
    get_engine,
    migrate_existing_claims_from_disk,
)

__all__ = [
    "Base",
    "User",
    "Claim",
    "Document",
    "ClaimImage",
    "ExtractedInformation",
    "ImageAnalysis",
    "VerificationResult",
    "RiskAssessment",
    "Report",
    "init_database",
    "get_db_session",
    "get_engine",
    "migrate_existing_claims_from_disk",
]
