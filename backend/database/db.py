"""Database connection, session management, and schema initialization for ClaimSense AI."""

import json
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator, Optional

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session

from backend.database.models import (
    Base,
    User,
    Claim,
    Document,
    ClaimImage,
)
from backend.utils.logger import setup_logger

logger = setup_logger("claimsense.database")

_engine: Optional[Engine] = None
_SessionFactory: Optional[sessionmaker] = None
_scoped_session: Optional[scoped_session] = None


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign key constraints on SQLite connections."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def init_database(db_uri: str) -> Engine:
    """Initializes SQLAlchemy engine, session maker, and creates all tables."""
    global _engine, _SessionFactory, _scoped_session

    connect_args = {}
    if db_uri.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    _engine = create_engine(
        db_uri,
        connect_args=connect_args,
        echo=False,
    )
    _SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    _scoped_session = scoped_session(_SessionFactory)

    # Create tables
    Base.metadata.create_all(bind=_engine)
    logger.info(f"Initialized database schema with URI: {db_uri}")
    return _engine


def get_engine() -> Engine:
    """Returns the current database engine."""
    global _engine
    if _engine is None:
        raise RuntimeError("Database engine has not been initialized. Call init_database() first.")
    return _engine


def close_engine():
    """Disposes engine and closes active connections, releasing file locks."""
    global _engine, _SessionFactory, _scoped_session
    if _scoped_session is not None:
        try:
            _scoped_session.remove()
        except Exception:
            pass
    if _engine is not None:
        try:
            _engine.dispose()
        except Exception:
            pass


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Context manager for scoped database sessions with automatic commit/rollback."""
    global _SessionFactory
    if _SessionFactory is None:
        raise RuntimeError("Database session factory has not been initialized. Call init_database() first.")
    session: Session = _SessionFactory()
    try:
        yield session
        session.commit()
    except Exception as exc:
        session.rollback()
        logger.error(f"Database session rolled back due to error: {exc}")
        raise
    finally:
        session.close()


def migrate_existing_claims_from_disk(upload_dir: Path) -> int:
    """Scans the uploads directory for legacy metadata.json files and ingests them into SQLite.

    Guarantees zero data loss from Phase 2 while populating the database.
    """
    if not upload_dir.exists():
        return 0

    migrated_count = 0
    with get_db_session() as session:
        for claim_path in upload_dir.iterdir():
            if not claim_path.is_dir():
                continue

            metadata_file = claim_path / "metadata.json"
            if not metadata_file.exists():
                continue

            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)

                claim_id = meta.get("claim_id", claim_path.name)

                # Check if already in SQLite
                existing = session.query(Claim).filter_by(claim_id=claim_id).first()
                if existing:
                    continue

                # Parse created_at
                created_at_str = meta.get("created_at")
                created_at = datetime.now(timezone.utc)
                if created_at_str:
                    try:
                        created_at = datetime.fromisoformat(created_at_str)
                    except Exception:
                        pass

                # Create Claim record
                claim = Claim(
                    claim_id=claim_id,
                    user_id=meta.get("user_id"),
                    claimant_name=meta.get("claimant_name", "Unknown Claimant"),
                    policy_number=meta.get("policy_number", "UNKNOWN"),
                    vehicle_number=meta.get("vehicle_number", "UNKNOWN"),
                    accident_date=meta.get("accident_date", "UNKNOWN"),
                    claim_description=meta.get("claim_description", ""),
                    status=meta.get("status", "SUBMITTED"),
                    created_at=created_at,
                    updated_at=created_at,
                )
                session.add(claim)
                session.flush()

                # Ingest Document and Image records from metadata files dict
                files_dict = meta.get("files", {})
                type_map = {
                    "policy_document": "POLICY_DOCUMENT",
                    "claim_form": "CLAIM_FORM",
                    "invoice_document": "INVOICE",
                }

                for file_key, info in files_dict.items():
                    if not isinstance(info, dict):
                        continue
                    original_name = info.get("original_name", file_key)
                    saved_as = info.get("saved_as", file_key)
                    rel_path = info.get("relative_path", "")
                    size_bytes = info.get("size_bytes", 0)
                    ext = original_name.rsplit(".", 1)[-1].lower() if "." in original_name else ""

                    if file_key == "vehicle_image":
                        claim_img = ClaimImage(
                            claim_id=claim_id,
                            image_type="VEHICLE_ACCIDENT",
                            file_path=rel_path,
                            original_filename=original_name,
                            stored_filename=saved_as,
                            file_extension=ext,
                            file_size=size_bytes,
                            created_at=created_at,
                        )
                        session.add(claim_img)
                    else:
                        doc_type = type_map.get(file_key, "OTHER")
                        doc = Document(
                            claim_id=claim_id,
                            document_type=doc_type,
                            file_path=rel_path,
                            original_filename=original_name,
                            stored_filename=saved_as,
                            file_extension=ext,
                            file_size=size_bytes,
                            created_at=created_at,
                        )
                        session.add(doc)

                migrated_count += 1
                logger.info(f"Successfully migrated legacy claim {claim_id} into SQLite database.")

            except Exception as e:
                logger.error(f"Failed to migrate claim from {metadata_file}: {e}")

    return migrated_count
