import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.base import TimestampMixin


def generate_uuid():
    return str(uuid.uuid4())


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )

    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    avatar_url: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    # Post-Quantum Kyber-1024 Keys (Server-Side Protected Model)
    kyber_public_key: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="User Kyber-1024 public key in hex (3136 hex characters)"
    )

    kyber_secret_key_encrypted: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="User Kyber-1024 secret key encrypted with CRYPTO_MASTER_KEY"
    )

    # Refresh Tokens
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # Folder Ownership
    folders: Mapped[list["Folder"]] = relationship(
        "Folder",
        foreign_keys="Folder.owner_id",
        back_populates="owner",
        cascade="all, delete-orphan",
    )


class RefreshToken(TimestampMixin, Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    token_hash: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    revoked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="refresh_tokens",
    )