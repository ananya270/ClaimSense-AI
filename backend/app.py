"""Application factory and main entry point for ClaimSense AI backend (Hardened)."""
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, jsonify, send_from_directory, request, make_response, session
from flask_cors import CORS
from flask_wtf.csrf import CSRFError, generate_csrf

from backend.config import Config
from backend.extensions import csrf, limiter
from backend.routes.health import health_bp
from backend.routes.claims import claims_bp
from backend.routes.auth import auth_bp
from backend.database.db import init_database, migrate_existing_claims_from_disk
from backend.utils.logger import setup_logger

logger = setup_logger("claimsense")


def create_app(config_class=Config) -> Flask:
    """Application factory for ClaimSense AI."""
    app = Flask(
        __name__,
        static_folder=str(config_class.FRONTEND_DIR),
        static_url_path="",
    )
    app.config.from_object(config_class)

    # Initialize CORS with explicit origin whitelist (no wildcard with credentials)
    allowed_origins = [
        origin.strip()
        for origin in getattr(config_class, "CORS_ALLOWED_ORIGINS", "").split(",")
        if origin.strip()
    ]
    if not allowed_origins:
        allowed_origins = ["http://127.0.0.1:5000", "http://localhost:5000"]

    CORS(
        app,
        resources={r"/api/*": {"origins": allowed_origins}},
        supports_credentials=True,
    )

    # In test mode, disable CSRF and rate limiting unless explicitly enabled for security tests
    if app.config.get("TESTING"):
        if not getattr(config_class, "ENABLE_CSRF_FOR_TESTS", False):
            app.config["WTF_CSRF_ENABLED"] = False
            app.config["WTF_CSRF_CHECK_DEFAULT"] = False
        if not getattr(config_class, "ENABLE_RATELIMIT_FOR_TESTS", False):
            app.config["RATELIMIT_ENABLED"] = False

    @app.before_request
    def extract_csrf_from_json():
        """Extract CSRF token from JSON body, headers, cookies, or query params and populate WSGI environ."""
        token = None
        if request.is_json:
            try:
                payload = request.get_json(silent=True)
                if isinstance(payload, dict) and payload.get("csrf_token"):
                    token = str(payload["csrf_token"]).strip()
            except Exception:
                pass

        if not token:
            token = (
                request.headers.get("X-CSRFToken")
                or request.headers.get("X-CSRF-Token")
                or request.cookies.get("claimsense_csrf_token")
                or request.args.get("csrf_token")
            )

        if token:
            request.environ["HTTP_X_CSRFTOKEN"] = str(token)
            request.environ["HTTP_X_CSRF_TOKEN"] = str(token)

    # Initialize Security Extensions (CSRF & Limiter)
    csrf.init_app(app)
    limiter.init_app(app)

    # Ensure required runtime directories exist
    config_class.ensure_directories()

    # Initialize Database & Migrate legacy data if needed
    db_uri = getattr(config_class, "SQLALCHEMY_DATABASE_URI", None)
    if not db_uri:
        db_path = getattr(config_class, "DATABASE_PATH", config_class.BASE_DIR / "data" / "claimsense.db")
        db_uri = f"sqlite:///{Path(db_path).as_posix()}"
    init_database(db_uri)

    try:
        migrate_existing_claims_from_disk(Path(config_class.UPLOAD_FOLDER))
    except Exception as e:
        logger.warning(f"Legacy claim migration skipped or encountered error: {e}")

    # Register blueprints
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(claims_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api")

    # Serve Frontend UI with embedded CSRF token and session initialization
    @app.route("/", methods=["GET"])
    def index():
        token = generate_csrf()
        index_file = Path(app.static_folder) / "index.html"
        if index_file.exists():
            html = index_file.read_text(encoding="utf-8")
            html = html.replace('<meta name="csrf-token" content="">', f'<meta name="csrf-token" content="{token}">')
            resp = make_response(html)
            resp.headers["Content-Type"] = "text/html; charset=utf-8"
            resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            resp.set_cookie("claimsense_csrf_token", token, samesite="Lax", httponly=False)
            return resp
        return send_from_directory(app.static_folder, "index.html")

    @app.after_request
    def set_csrf_cookie(response):
        """Ensures the readable CSRF cookie is synchronized whenever CSRF session exists."""
        if "csrf_token" in session:
            try:
                token = generate_csrf()
                response.set_cookie("claimsense_csrf_token", token, samesite="Lax", httponly=False)
            except Exception:
                pass
        return response

    # Global Error Handlers with Consistent JSON output
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": "Bad Request",
            "message": str(error.description if hasattr(error, "description") else error),
            "status_code": 400,
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            "success": False,
            "error": "Unauthorized",
            "message": str(error.description if hasattr(error, "description") else "Authentication required."),
            "status_code": 401,
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            "success": False,
            "error": "Forbidden",
            "message": str(error.description if hasattr(error, "description") else "Access forbidden."),
            "status_code": 403,
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": "Resource Not Found",
            "message": "The requested endpoint or resource was not found on this server.",
            "status_code": 404,
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": "Method Not Allowed",
            "message": "The requested HTTP method is not allowed for this endpoint.",
            "status_code": 405,
        }), 405

    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({
            "success": False,
            "error": "File Too Large",
            "message": "The uploaded file exceeds the maximum allowed payload size (16MB).",
            "status_code": 413,
        }), 413

    @app.errorhandler(415)
    def unsupported_media_type(error):
        return jsonify({
            "success": False,
            "error": "Unsupported Media Type",
            "message": "The request payload media type is not supported.",
            "status_code": 415,
        }), 415

    @app.errorhandler(429)
    def ratelimit_handler(error):
        return jsonify({
            "success": False,
            "error": "Too Many Requests",
            "message": "Rate limit exceeded. Please wait a moment before trying again.",
            "status_code": 429,
        }), 429

    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):
        return jsonify({
            "success": False,
            "error": "CSRF Validation Failed",
            "message": error.description or "The CSRF token is missing or invalid.",
            "status_code": 400,
        }), 400

    @app.errorhandler(500)
    def internal_server_error(error):
        logger.error(f"Internal server error encountered: {error}")
        return jsonify({
            "success": False,
            "error": "Internal Server Error",
            "message": "An unexpected error occurred on the server.",
            "status_code": 500,
        }), 500

    logger.info("ClaimSense AI application initialized successfully.")
    return app


if __name__ == "__main__":
    app = create_app()
    logger.info(f"Starting server on http://{Config.HOST}:{Config.PORT}")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
