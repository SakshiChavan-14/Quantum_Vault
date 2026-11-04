import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.base import TimestampMixin


def generate_uuid():
    return str(uuid.uuid4())


class AuditLog(TimestampMixin, Base):
    """
    AuditLog model representing persistent security, file, crypto, and auth events in QuantumVault.
    """
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
        comment="Unique audit log identifier"
    )

    user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User who triggered or is associated with event"
    )

    file_id: Mapped[str | None] = mapped_column(
        ForeignKey("files.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Target file identifier if applicable"
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Specific event name (e.g. FILE_UPLOAD_SUCCESS, INTEGRITY_CHECK_FAILED)"
    )

    event_category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Category: AUTH, FILE, CRYPTO, SECURITY, SYSTEM"
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="Status: SUCCESS, FAILURE, WARNING, INFO"
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Human-readable event summary"
    )

    metadata_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Sanitized JSON metadata (non-sensitive details)"
    )

    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
        comment="Client IP address"
    )

    # Relationships
    user: Mapped["User | None"] = relationship("User", foreign_keys=[user_id])
    file: Mapped["File | None"] = relationship("File", foreign_keys=[file_id])

    __table_args__ = (
        Index("idx_audit_user_id", "user_id"),
        Index("idx_audit_file_id", "file_id"),
        Index("idx_audit_event_type", "event_type"),
        Index("idx_audit_event_category", "event_category"),
        Index("idx_audit_status", "status"),
        Index("idx_audit_created_at", "created_at"),
    )
