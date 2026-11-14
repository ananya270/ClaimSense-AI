"""Authentication endpoints for ClaimSense AI (Phase 3 Hardened)."""
import re
from flask import Blueprint, jsonify, request, session
from flask_wtf.csrf import generate_csrf
from sqlalchemy import or_

from backend.database.db import get_db_session
from backend.database.models import User
from backend.extensions import limiter
from backend.utils.logger import setup_logger

logger = setup_logger("claimsense.auth")

auth_bp = Blueprint("auth", __name__)

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_]{3,30}$")


def _get_request_data() -> dict:
    """Helper to extract payload from JSON or form-data."""
    if request.is_json:
        return request.get_json(silent=True) or {}
    return request.form.to_dict() or {}


@auth_bp.route("/auth/csrf-token", methods=["GET"])
def get_csrf_token():
    """Generates and returns a fresh CSRF token for state-changing requests."""
    token = generate_csrf()
    return jsonify({
        "success": True,
        "csrf_token": token,
    }), 200


@auth_bp.route("/auth/signup", methods=["POST"])
@limiter.limit("10 per minute")
def signup():
    """Registers a new user account with hashed password, complexity verification, and rate limiting."""
    data = _get_request_data()

    full_name = data.get("full_name", "").strip()
    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    confirm_password = data.get("confirm_password", "")

    # 1. Check required fields
    if not all([full_name, username, email, password, confirm_password]):
        return jsonify({
            "success": False,
            "error": "Validation Error",
            "message": "All fields are required (full_name, username, email, password, confirm_password).",
        }), 400

    # 2. Email format validation
    if not EMAIL_REGEX.match(email):
        return jsonify({
            "success": False,
            "error": "Validation Error",
            "message": "Invalid email format. Please provide a valid email address.",
        }), 400

    # 3. Username format validation
    if not USERNAME_REGEX.match(username):
        return jsonify({
            "success": False,
            "error": "Validation Error",
            "message": "Username must be 3-30 characters long and contain only letters, numbers, or underscores.",
        }), 400

    # 4. Password validation (minimum 8 characters, letters and numbers)
    if len(password) < 8 or not re.search(r"[a-zA-Z]", password) or not re.search(r"\d", password):
        return jsonify({
            "success": False,
            "error": "Validation Error",
            "message": "Password must be at least 8 characters long and contain both letters and numbers.",
        }), 400

    if password != confirm_password:
        return jsonify({
            "success": False,
            "error": "Validation Error",
            "message": "Password and confirmation password do not match.",
        }), 400

    # 5. Check uniqueness in database
    with get_db_session() as db:
        existing_user = db.query(User).filter_by(username=username).first()
        if existing_user:
            return jsonify({
                "success": False,
                "error": "Conflict",
                "message": f"Username '{username}' is already taken.",
            }), 409

        existing_email = db.query(User).filter_by(email=email).first()
        if existing_email:
            return jsonify({
                "success": False,
                "error": "Conflict",
                "message": f"Email '{email}' is already registered.",
            }), 409

        # Create user record with default 'user' role
        new_user = User(
            full_name=full_name,
            username=username,
            email=email,
            role="user",
            is_active=True,
        )
        new_user.set_password(password)
        db.add(new_user)
        db.flush()
        logger.info(f"New user registered successfully: id={new_user.id}, username='{username}'")

    return jsonify({
        "success": True,
        "message": "Account created successfully",
    }), 201


@auth_bp.route("/auth/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    """Authenticates user credentials, rotates session to prevent fixation, and establishes session."""
    data = _get_request_data()

    identifier = (
        data.get("identifier")
        or data.get("username")
        or data.get("email")
        or ""
    ).strip()
    password = data.get("password", "")

    if not identifier or not password:
        return jsonify({
            "success": False,
            "error": "Validation Error",
            "message": "Both username/email and password are required.",
        }), 400

    with get_db_session() as db:
        user = db.query(User).filter(
            or_(User.username == identifier, User.email == identifier.lower())
        ).first()

        # Generic authentication failure message to prevent username enumeration
        if not user or not user.check_password(password):
            logger.warning(f"Failed login attempt for identifier: '{identifier}'")
            return jsonify({
                "success": False,
                "error": "Invalid credentials",
                "message": "Invalid username/email or password.",
            }), 401

        if not user.is_active:
            return jsonify({
                "success": False,
                "error": "Account Inactive",
                "message": "This account is currently inactive. Please contact an administrator.",
            }), 403

        # Rotate and establish secure session (mitigate session fixation)
        session.clear()
        session["user_id"] = user.id
        session["username"] = user.username
        session["role"] = user.role

        user_info = user.to_dict()
        logger.info(f"User logged in successfully: username='{user.username}', role='{user.role}'")

    return jsonify({
        "success": True,
        "message": "Login successful",
        "user": user_info,
    }), 200


@auth_bp.route("/auth/logout", methods=["POST"])
def logout():
    """Logs out current authenticated user and clears session state completely."""
    username = session.get("username", "anonymous")
    session.clear()
    logger.info(f"User '{username}' logged out successfully.")
    return jsonify({
        "success": True,
        "message": "Logged out successfully",
    }), 200


@auth_bp.route("/auth/me", methods=["GET"])
def get_me():
    """Returns currently authenticated user profile if session and account are active."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({
            "success": False,
            "error": "Unauthorized",
            "message": "Authentication required.",
        }), 401

    with get_db_session() as db:
        user = db.query(User).filter_by(id=user_id).first()
        if not user or not user.is_active:
            session.clear()
            return jsonify({
                "success": False,
                "error": "Unauthorized",
                "message": "Active user account not found.",
            }), 401

        return jsonify({
            "success": True,
            "user": user.to_dict(),
        }), 200
