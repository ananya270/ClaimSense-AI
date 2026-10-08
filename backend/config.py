"""Configuration module for ClaimSense AI backend."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory is project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from project root if it exists
load_dotenv(BASE_DIR / ".env")


class Config:
    """Base application configuration."""

    # Project paths
    BASE_DIR = BASE_DIR
    BACKEND_DIR = BASE_DIR / "backend"
    FRONTEND_DIR = BASE_DIR / "frontend"
    UPLOAD_FOLDER = BASE_DIR / os.getenv("UPLOAD_FOLDER", "uploads")
    REPORTS_FOLDER = BASE_DIR / "reports"
    DATA_FOLDER = BASE_DIR / "data"

    # Flask settings
    SECRET_KEY = os.getenv("SECRET_KEY", "claimsense-ai-dev-secret-key-change-in-production")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 5000))

    # Upload constraints
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))  # 16 MB default
    ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "docx"}

    # Database
    DATABASE_PATH = BASE_DIR / os.getenv("DATABASE_PATH", "backend/database/claimsense.db")

    # Risk thresholds
    RISK_THRESHOLD_LOW = int(os.getenv("RISK_THRESHOLD_LOW", 30))
    RISK_THRESHOLD_MEDIUM = int(os.getenv("RISK_THRESHOLD_MEDIUM", 60))

    # LLM Settings (for future phase)
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")

    @classmethod
    def ensure_directories(cls):
        """Ensure necessary runtime directories exist."""
        cls.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        cls.REPORTS_FOLDER.mkdir(parents=True, exist_ok=True)
        cls.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
