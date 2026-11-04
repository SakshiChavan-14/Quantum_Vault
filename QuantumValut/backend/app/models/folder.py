import uuid
from datetime import datetime

from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    Integer,
    BigInteger,
    ForeignKey,
    UniqueConstraint,
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


class Folder(TimestampMixin, Base):
    __tablename__ = "folders"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid,
    )

    owner_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    parent_id: Mapped[str | None] = mapped_column(
        ForeignKey("folders.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    color: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    icon_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        index=True,
    )

    is_favorite: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    is_shared: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    is_system: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    # Metadata

    folder_size: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
    )

    file_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    children_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    last_activity_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
    )

    created_by: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    updated_by: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        index=True,
        comment="Soft Delete",
    )

    __table_args__ = (
        UniqueConstraint(
            "owner_id",
            "parent_id",
            "name",
            name="uq_folder_owner_parent_name",
        ),
    )

    # ===========================
    # Relationships
    # ===========================

    owner: Mapped["User"] = relationship(
        "User",
        foreign_keys=[owner_id],
        back_populates="folders",
    )

    creator: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by],
    )

    updater: Mapped["User"] = relationship(
        "User",
        foreign_keys=[updated_by],
    )

    parent: Mapped["Folder | None"] = relationship(
        "Folder",
        remote_side=[id],
        back_populates="children",
    )

    children: Mapped[list["Folder"]] = relationship(
        "Folder",
        back_populates="parent",
        cascade="all, delete-orphan",
    )

    files: Mapped[list["File"]] = relationship(
        "File",
        back_populates="folder",
        cascade="all, delete-orphan",
    )