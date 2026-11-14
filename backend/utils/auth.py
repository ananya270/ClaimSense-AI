"""Authentication helpers and authorization decorators for ClaimSense AI."""
from functools import wraps
from typing import Optional, Dict, Any
from flask import session, jsonify

from backend.database.db import get_db_session
from backend.database.models import User, Claim


def get_current_user_id() -> Optional[int]:
    """Returns the current user ID stored in session, if any."""
    return session.get("user_id")


def get_current_user() -> Optional[Dict[str, Any]]:
    """Retrieves current authenticated user dictionary or None if unauthenticated/inactive."""
    user_id = session.get("user_id")
    if not user_id:
        return None

    with get_db_session() as db:
        user = db.query(User).filter_by(id=user_id).first()
        if user and user.is_active:
            return user.to_dict()
    return None


def login_required(f):
    """Decorator requiring an active authenticated user session."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({
                "success": False,
                "error": "Unauthorized",
                "message": "Authentication required to access this resource.",
            }), 401

        # Verify active user in database
        with get_db_session() as db:
            user = db.query(User).filter_by(id=user_id).first()
            if not user or not user.is_active:
                session.clear()
                return jsonify({
                    "success": False,
                    "error": "Unauthorized",
                    "message": "Active user account required to access this resource.",
                }), 401

        return f(*args, **kwargs)
    return decorated_function


def can_user_access_claim(claim: Claim, user_id: Optional[int], user_role: Optional[str]) -> bool:
    """Evaluates whether a user is authorized to view or download receipts for a claim.

    Rules:
    - Assessors and Admins have global audit access.
    - Claim owners (matching user_id) have access.
    - Unowned / legacy claims without user_id are NOT accessible to standard users
      or anonymous callers; they require authorized assessor/admin roles.
    - Other users are strictly forbidden.
    """
    if user_role in ("assessor", "admin"):
        return True

    if claim.user_id is None:
        # Unowned/legacy claims are restricted to assessor/admin review
        return False

    if user_id is not None and claim.user_id == user_id:
        return True

    return False


def can_user_access_claim_dict(claim_dict: Dict[str, Any], user_id: Optional[int], user_role: Optional[str]) -> bool:
    """Evaluates access authorization for file-based / legacy metadata dictionaries.

    Ensures that fallback paths enforce the exact same ownership rules as database queries.
    """
    if user_role in ("assessor", "admin"):
        return True

    owner_id = claim_dict.get("user_id")
    if owner_id is None:
        # Unowned/legacy records require assessor/admin access
        return False

    if user_id is not None and owner_id == user_id:
        return True

    return False
