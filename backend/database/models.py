"""SQLAlchemy ORM models for ClaimSense AI (Phase 3)."""
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    """User account entity with role-based access control and hashed passwords."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(120), nullable=False)
    role = Column(String(20), default="user", nullable=False)  # 'user', 'assessor', 'admin'
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    claims = relationship("Claim", back_populates="user", lazy="select")

    def set_password(self, password: str) -> None:
        """Securely hash and store password using Werkzeug."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify plain password against stored Werkzeug hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize user data safely without exposing password hashes."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Claim(Base):
    """Central Claim entity with unique Claim ID and indexed policy number."""
    __tablename__ = "claims"

    claim_id = Column(String(32), primary_key=True, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    claimant_name = Column(String(120), nullable=False)
    policy_number = Column(String(64), nullable=False, index=True)
    vehicle_number = Column(String(32), nullable=False, index=True)
    accident_date = Column(String(32), nullable=False)
    incident_location = Column(String(256), nullable=True)
    claim_description = Column(Text, nullable=False)
    status = Column(String(32), default="SUBMITTED", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="claims")
    documents = relationship("Document", back_populates="claim", cascade="all, delete-orphan", lazy="select")
    images = relationship("ClaimImage", back_populates="claim", cascade="all, delete-orphan", lazy="select")
    extracted_info = relationship("ExtractedInformation", back_populates="claim", cascade="all, delete-orphan", lazy="select")
    image_analyses = relationship("ImageAnalysis", back_populates="claim", cascade="all, delete-orphan", lazy="select")
    verification_results = relationship("VerificationResult", back_populates="claim", cascade="all, delete-orphan", lazy="select")
    risk_assessments = relationship("RiskAssessment", back_populates="claim", cascade="all, delete-orphan", lazy="select")
    reports = relationship("Report", back_populates="claim", cascade="all, delete-orphan", lazy="select")

    def to_dict(self, include_evidence: bool = True) -> Dict[str, Any]:
        """Serializes claim entity to dictionary representation."""
        data = {
            "claim_id": self.claim_id,
            "user_id": self.user_id,
            "claimant_name": self.claimant_name,
            "policy_number": self.policy_number,
            "vehicle_number": self.vehicle_number,
            "accident_date": self.accident_date,
            "incident_location": self.incident_location,
            "claim_description": self.claim_description,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_evidence:
            data["documents"] = [doc.to_dict() for doc in self.documents]
            data["images"] = [img.to_dict() for img in self.images]

            # Construct backward-compatible 'files' dictionary format matching Phase 2
            files_dict = {}
            type_mapping = {
                "POLICY_DOCUMENT": "policy_document",
                "CLAIM_FORM": "claim_form",
                "INVOICE": "invoice_document",
            }
            for doc in self.documents:
                key = type_mapping.get(doc.document_type, doc.document_type.lower())
                files_dict[key] = {
                    "original_name": doc.original_filename,
                    "saved_as": doc.stored_filename,
                    "relative_path": doc.file_path,
                    "size_bytes": doc.file_size,
                }
            for img in self.images:
                files_dict["vehicle_image"] = {
                    "original_name": img.original_filename,
                    "saved_as": img.stored_filename,
                    "relative_path": img.file_path,
                    "size_bytes": img.file_size,
                }
            data["files"] = files_dict
            data["files_count"] = len(self.documents) + len(self.images)

        return data


class Document(Base):
    """Submitted evidentiary documents (Policy Schedule, Claim Form, Invoice)."""
    __tablename__ = "documents"

    document_id = Column(Integer, primary_key=True, autoincrement=True)
    claim_id = Column(String(32), ForeignKey("claims.claim_id"), nullable=False, index=True)
    document_type = Column(String(64), nullable=False)  # POLICY_DOCUMENT, CLAIM_FORM, INVOICE, OTHER
    file_path = Column(String(512), nullable=False)
    original_filename = Column(String(256), nullable=False)
    stored_filename = Column(String(256), nullable=False)
    file_extension = Column(String(16), nullable=False)
    file_size = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    claim = relationship("Claim", back_populates="documents")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "claim_id": self.claim_id,
            "document_type": self.document_type,
            "file_path": self.file_path,
            "original_filename": self.original_filename,
            "stored_filename": self.stored_filename,
            "file_extension": self.file_extension,
            "file_size": self.file_size,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ClaimImage(Base):
    """Submitted photographic evidence of damaged vehicle."""
    __tablename__ = "claim_images"

    image_id = Column(Integer, primary_key=True, autoincrement=True)
    claim_id = Column(String(32), ForeignKey("claims.claim_id"), nullable=False, index=True)
    image_type = Column(String(64), default="VEHICLE_ACCIDENT", nullable=False)
    file_path = Column(String(512), nullable=False)
    original_filename = Column(String(256), nullable=False)
    stored_filename = Column(String(256), nullable=False)
    file_extension = Column(String(16), nullable=False)
    file_size = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    claim = relationship("Claim", back_populates="images")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "image_id": self.image_id,
            "claim_id": self.claim_id,
            "image_type": self.image_type,
            "file_path": self.file_path,
            "original_filename": self.original_filename,
            "stored_filename": self.stored_filename,
            "file_extension": self.file_extension,
            "file_size": self.file_size,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ExtractedInformation(Base):
    """Phase 4 structured extraction storage with evidence and status metadata."""
    __tablename__ = "extracted_information"

    id = Column(Integer, primary_key=True, autoincrement=True)
    claim_id = Column(String(32), ForeignKey("claims.claim_id"), nullable=False, index=True)
    field_name = Column(String(128), nullable=False)
    field_value = Column(Text, nullable=True)
    field_status = Column(String(32), nullable=True, default="not_present")
    source = Column(String(64), nullable=False)  # policy_document, claim_form, invoice
    source_filename = Column(String(255), nullable=True)
    page_number = Column(Integer, nullable=True)
    extraction_method = Column(String(64), nullable=True)
    supporting_text = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    evaluation_metadata = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    claim = relationship("Claim", back_populates="extracted_info")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "claim_id": self.claim_id,
            "field_name": self.field_name,
            "field_value": self.field_value,
            "field_status": self.field_status,
            "source": self.source,
            "source_filename": self.source_filename,
            "page_number": self.page_number,
            "extraction_method": self.extraction_method,
            "supporting_text": self.supporting_text,
            "confidence_score": self.confidence_score,
            "error_message": self.error_message,
            "evaluation_metadata": self.evaluation_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ImageAnalysis(Base):
    """Future schema for Phase 5 (Computer Vision vehicle damage inspection)."""
    __tablename__ = "image_analysis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    claim_id = Column(String(32), ForeignKey("claims.claim_id"), nullable=False, index=True)
    image_id = Column(Integer, ForeignKey("claim_images.image_id"), nullable=True)
    detected_damage = Column(String(128), nullable=True)
    damage_location = Column(String(128), nullable=True)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    claim = relationship("Claim", back_populates="image_analyses")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "claim_id": self.claim_id,
            "image_id": self.image_id,
            "detected_damage": self.detected_damage,
            "damage_location": self.damage_location,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class VerificationResult(Base):
    """Future schema for Phase 7 (Cross-source consistency rule engine)."""
    __tablename__ = "verification_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    claim_id = Column(String(32), ForeignKey("claims.claim_id"), nullable=False, index=True)
    field = Column(String(128), nullable=False)
    source_1 = Column(String(64), nullable=False)
    source_2 = Column(String(64), nullable=False)
    value_1 = Column(Text, nullable=True)
    value_2 = Column(Text, nullable=True)
    result = Column(String(32), nullable=False)  # CONSISTENT, MINOR_MISMATCH, MAJOR_MISMATCH, MISSING_INFORMATION
    explanation = Column(Text, nullable=True)
    severity = Column(String(32), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    claim = relationship("Claim", back_populates="verification_results")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "claim_id": self.claim_id,
            "field": self.field,
            "source_1": self.source_1,
            "source_2": self.source_2,
            "value_1": self.value_1,
            "value_2": self.value_2,
            "result": self.result,
            "explanation": self.explanation,
            "severity": self.severity,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class RiskAssessment(Base):
    """Future schema for Phase 8 (Explainable weighted fraud-risk scoring)."""
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    claim_id = Column(String(32), ForeignKey("claims.claim_id"), nullable=False, index=True)
    risk_level = Column(String(32), nullable=False)  # LOW, MEDIUM, HIGH
    risk_score = Column(Float, nullable=False)
    reasons = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    claim = relationship("Claim", back_populates="risk_assessments")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "claim_id": self.claim_id,
            "risk_level": self.risk_level,
            "risk_score": self.risk_score,
            "reasons": self.reasons,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Report(Base):
    """Future schema for Phase 10 (Assessor verification audit reports)."""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    claim_id = Column(String(32), ForeignKey("claims.claim_id"), nullable=False, index=True)
    report_path = Column(String(512), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    claim = relationship("Claim", back_populates="reports")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "claim_id": self.claim_id,
            "report_path": self.report_path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
