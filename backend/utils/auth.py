"""Authentication helpers and authorization decorators for ClaimSense AI."""
from functools import wraps
from typing import Optional
from flask import session, jsonify

from backend.database.db import get_db_session
from backend.database.models import User, Claim


def get_current_user_id() -> Optional[int]:
    """Returns the current user ID stored in session, if any."""
    return session.get("user_id")


def get_current_user() -> Optional[dict]:
    """Retrieves current authenticated user dictionary or None."""
    user_id = session.get("user_id")
    if not user_id:
        return None

    with get_db_session() as db:
        user = db.query(User).filter_by(id=user_id).first()
        if user and user.is_active:
            return user.to_dict()
    return None


def login_required(f):
    """Decorator requiring active session authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({
                "success": False,
                "error": "Unauthorized",
                "message": "Authentication required to access this resource.",
            }), 401
        return f(*args, **kwargs)
    return decorated_function


def can_user_access_claim(claim: Claim, user_id: Optional[int], user_role: Optional[str]) -> bool:
    """Evaluates whether a user is authorized to view or download receipts for a claim.

    Rules:
    - Assessors and Admins have global access.
    - Owners (matching user_id) have access.
    - Anonymous/unowned claims (e.g. legacy/test claims with user_id is None) can be accessed.
    - Other users are forbidden.
    """
    if user_role in ("assessor", "admin"):
        return True

    if claim.user_id is None:
        # Backward-compatible access for test/anonymous claims
        return True

    if user_id is not None and claim.user_id == user_id:
        return True

    return False
