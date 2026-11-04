import uuid
from datetime import datetime

from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    Integer,
    BigInteger,
    ForeignKey,
    Text,
    Index,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.core.database import Base
from app.core.base import TimestampMixin


def generate_uuid():
    return str(uuid.uuid4())


class File(TimestampMixin, Base):
    """
    File model representing uploaded files in QuantumVault.
    
    Supports:
    - Multiple file formats
    - Folder organization
    - Encryption metadata
    - Soft delete with recovery
    - Version tracking
    """
    
    __tablename__ = "files"

    # Primary Identifiers
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
        comment="Unique file identifier (UUID)"
    )

    # Ownership & Organization
    owner_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="File owner (User ID)"
    )

    folder_id: Mapped[str | None] = mapped_column(
        ForeignKey("folders.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Parent folder (Folder ID)"
    )

    # File Identification
    original_filename: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Original filename as uploaded by user"
    )

    stored_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Hash-based filename for storage"
    )

    # File Metadata
    file_size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="File size in bytes"
    )

    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="application/octet-stream",
        comment="MIME type (e.g., application/pdf)"
    )

    file_extension: Mapped[str] = mapped_column(
        String(20),
        nullable=True,
        comment="File extension (e.g., pdf, docx, jpg)"
    )

    # Storage Path
    storage_path: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
        comment="Relative path to file in storage"
    )

    # Integrity & Security
    file_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
        comment="SHA-256 hash of original file"
    )

    is_encrypted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="Whether file is encrypted (AES-256)"
    )

    encryption_algorithm: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Encryption algorithm (e.g., AES-256)"
    )

    # Legacy Key Storage (Deprecated for new uploads; retained for legacy Fernet files)
    encryption_key_hash: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Legacy Fernet key (deprecated for new uploads)"
    )

    # Post-Quantum Cryptography Metadata (Version 2 - Kyber1024 + AES-256-GCM)
    kyber_ciphertext: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Kyber-1024 KEM ciphertext (hex string)"
    )

    encrypted_dek: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="AES-256 DEK wrapped with HKDF-derived KEK (hex string)"
    )

    encryption_nonce: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        comment="AES-256-GCM 96-bit nonce (hex or base64)"
    )

    # File Description & Organization
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="User-provided file description"
    )

    is_favorite: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="Mark file as favorite"
    )

    is_shared: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="Whether file is shared"
    )

    # Versioning & Tracking
    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        comment="File version number"
    )

    last_modified_by: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who last modified file"
    )

    last_accessed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="Last download/access time"
    )

    # Soft Delete Support
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        index=True,
        comment="Soft delete timestamp"
    )

    # Access Control
    access_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="Number of times file has been downloaded/accessed"
    )

    # ===========================
    # Indexes
    # ===========================
    __table_args__ = (
        Index("idx_file_owner_id", "owner_id"),
        Index("idx_file_folder_id", "folder_id"),
        Index("idx_file_deleted_at", "deleted_at"),
        Index("idx_file_is_favorite", "is_favorite"),
        Index("idx_file_created_at", "created_at"),
        Index("idx_file_hash", "file_hash"),
    )

    # ===========================
    # Relationships
    # ===========================

    # File owner relationship
    owner: Mapped["User"] = relationship(
        "User",
        foreign_keys=[owner_id]
    )

    # Parent folder relationship
    folder: Mapped["Folder | None"] = relationship(
        "Folder",
        foreign_keys=[folder_id],
        back_populates="files"
    )

    # User who last modified file
    modifier: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[last_modified_by]
    )

    # ===========================
    # Methods
    # ===========================

    def to_dict(self):
        """Convert file object to dictionary."""
        return {
            "id": self.id,
            "original_filename": self.original_filename,
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "file_extension": self.file_extension,
            "is_favorite": self.is_favorite,
            "is_shared": self.is_shared,
            "is_encrypted": self.is_encrypted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def mark_accessed(self, accessed_at: datetime) -> None:
        """Mark file as accessed and increment counter."""
        self.last_accessed_at = accessed_at
        self.access_count += 1
