"""
Audit Log Service for QuantumVault.
Provides centralized, fail-safe security and operational audit logging.
"""

import json
from typing import Optional, Dict, Any, List
from loguru import logger
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.repositories.audit_log_repository import AuditLogRepository


class AuditLogService:
    """
    Service for logging and querying security and operational events.
    
    Categories:
    - AUTH: User registration, login, logout, session refresh
    - FILE: Upload, download, rename, move, delete
    - CRYPTO: PQC key generation, encapsulation, decapsulation, key wrap/unwrap
    - SECURITY: Unauthorized access, authentication tag failure, integrity check failure
    - SYSTEM: Internal configuration or infrastructure events
    
    Statuses:
    - SUCCESS, FAILURE, WARNING, INFO
    """

    # Sensitive key patterns that must NEVER be persisted in metadata
    BLOCKED_METADATA_KEYS = {
        "password",
        "password_hash",
        "confirm_password",
        "token",
        "access_token",
        "refresh_token",
        "secret_key",
        "kyber_secret_key",
        "shared_secret",
        "crypto_master_key",
        "dek",
        "kek",
        "plaintext",
        "file_content",
    }

    def __init__(self, repository: AuditLogRepository):
        self.repository = repository

    @classmethod
    def _sanitize_metadata(cls, metadata: Optional[Dict[str, Any]]) -> Optional[str]:
        """Sanitize metadata dictionary and return safe JSON string."""
        if not metadata or not isinstance(metadata, dict):
            return None

        clean_dict = {}
        for k, v in metadata.items():
            key_lower = str(k).lower()
            if any(blocked in key_lower for blocked in cls.BLOCKED_METADATA_KEYS):
                continue
            # Convert non-serializable objects to string
            try:
                json.dumps(v)
                clean_dict[k] = v
            except (TypeError, ValueError):
                clean_dict[k] = str(v)

        return json.dumps(clean_dict) if clean_dict else None

    def log_event(
        self,
        event_type: str,
        event_category: str,
        status: str,
        message: str,
        user_id: Optional[str] = None,
        file_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
    ) -> Optional[AuditLog]:
        """
        Record a persistent audit log event (fail-safe).
        
        Args:
            event_type: Specific event name (e.g. FILE_UPLOAD_SUCCESS)
            event_category: Category (AUTH, FILE, CRYPTO, SECURITY, SYSTEM)
            status: Status (SUCCESS, FAILURE, WARNING, INFO)
            message: Human-readable message
            user_id: Optional user UUID
            file_id: Optional file UUID
            metadata: Optional safe dictionary of attributes
            ip_address: Optional client IP
            
        Returns:
            Created AuditLog record, or None if logging encountered an internal error
        """
        try:
            sanitized_json = self._sanitize_metadata(metadata)
            entry = AuditLog(
                user_id=user_id,
                file_id=file_id,
                event_type=event_type,
                event_category=event_category,
                status=status,
                message=message,
                metadata_json=sanitized_json,
                ip_address=ip_address,
            )
            return self.repository.create_log(entry)
        except Exception as e:
            logger.error(f"Audit log persistence failed for {event_type}: {e}")
            return None

    def log_file_event(
        self,
        event_type: str,
        status: str,
        message: str,
        user_id: Optional[str] = None,
        file_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[AuditLog]:
        """Convenience method for FILE category events."""
        return self.log_event(
            event_type=event_type,
            event_category="FILE",
            status=status,
            message=message,
            user_id=user_id,
            file_id=file_id,
            metadata=metadata,
        )

    def log_security_event(
        self,
        event_type: str,
        status: str,
        message: str,
        user_id: Optional[str] = None,
        file_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[AuditLog]:
        """Convenience method for SECURITY category events."""
        return self.log_event(
            event_type=event_type,
            event_category="SECURITY",
            status=status,
            message=message,
            user_id=user_id,
            file_id=file_id,
            metadata=metadata,
        )

    def log_auth_event(
        self,
        event_type: str,
        status: str,
        message: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
    ) -> Optional[AuditLog]:
        """Convenience method for AUTH category events."""
        return self.log_event(
            event_type=event_type,
            event_category="AUTH",
            status=status,
            message=message,
            user_id=user_id,
            metadata=metadata,
            ip_address=ip_address,
        )

    def get_user_logs(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[AuditLog]:
        """Retrieve audit history for a user."""
        return self.repository.get_logs_by_user(user_id=user_id, limit=limit, offset=offset)

    def get_file_logs(
        self,
        file_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[AuditLog]:
        """Retrieve audit history for a file."""
        return self.repository.get_logs_by_file(file_id=file_id, limit=limit, offset=offset)
