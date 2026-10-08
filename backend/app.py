import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from backend.config import Config
from backend.routes.health import health_bp
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

    # Initialize CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Ensure required runtime directories exist
    config_class.ensure_directories()

    # Register blueprints
    app.register_blueprint(health_bp, url_prefix="/api")

    # Serve Frontend UI
    @app.route("/", methods=["GET"])
    def index():
        return send_from_directory(app.static_folder, "index.html")

    # Error Handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "error": "Bad Request",
            "message": str(error.description if hasattr(error, "description") else error),
            "status_code": 400,
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Resource Not Found",
            "message": "The requested endpoint or resource was not found on this server.",
            "status_code": 404,
        }), 404

    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({
            "error": "File Too Large",
            "message": "The uploaded file exceeds the maximum allowed payload size (16MB).",
            "status_code": 413,
        }), 413

    @app.errorhandler(500)
    def internal_server_error(error):
        logger.error(f"Internal server error encountered: {error}")
        return jsonify({
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
