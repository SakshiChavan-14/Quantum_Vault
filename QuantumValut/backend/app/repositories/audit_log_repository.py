"""
Audit Log Repository for QuantumVault.
Handles persistence and retrieval of security and system audit logs.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.audit_log import AuditLog


class AuditLogRepository:
    """Repository for audit log database operations."""

    def __init__(self, db: Session):
        self.db = db

    def create_log(self, log_entry: AuditLog) -> AuditLog:
        """Persist a new audit log record."""
        self.db.add(log_entry)
        self.db.commit()
        self.db.refresh(log_entry)
        return log_entry

    def get_logs_by_user(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[AuditLog]:
        """Retrieve audit logs for a specific user."""
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.user_id == user_id)
            .order_by(desc(AuditLog.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_logs_by_file(
        self,
        file_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[AuditLog]:
        """Retrieve audit logs associated with a specific file."""
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.file_id == file_id)
            .order_by(desc(AuditLog.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_recent_logs(self, limit: int = 100) -> List[AuditLog]:
        """Retrieve most recent audit logs across the system."""
        return (
            self.db.query(AuditLog)
            .order_by(desc(AuditLog.created_at))
            .limit(limit)
            .all()
        )
