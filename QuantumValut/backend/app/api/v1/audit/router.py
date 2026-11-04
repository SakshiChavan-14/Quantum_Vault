"""
Audit Log API router for QuantumVault.
Provides secure, authenticated access to system and security event history.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.dependencies.auth import get_current_active_user
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.file_repository import FileRepository
from app.services.audit_log_service import AuditLogService
from app.schemas.audit_log import AuditLogResponse
from app.exceptions.FileExceptions import FileNotFound


router = APIRouter()


def get_audit_service(db: Session = Depends(get_db)) -> AuditLogService:
    return AuditLogService(AuditLogRepository(db))


@router.get(
    "/me",
    response_model=List[AuditLogResponse],
    summary="Get current user audit logs",
    tags=["audit"]
)
async def get_my_audit_logs(
    limit: int = Query(50, ge=1, le=200, description="Max logs to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: User = Depends(get_current_active_user),
    audit_service: AuditLogService = Depends(get_audit_service),
):
    """Retrieve audit and security events associated with the authenticated user."""
    logs = audit_service.get_user_logs(user_id=current_user.id, limit=limit, offset=offset)
    return [AuditLogResponse.model_validate(log) for log in logs]


@router.get(
    "/file/{file_id}",
    response_model=List[AuditLogResponse],
    summary="Get audit logs for a specific file",
    tags=["audit"]
)
async def get_file_audit_logs(
    file_id: str,
    limit: int = Query(50, ge=1, le=200, description="Max logs to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: User = Depends(get_current_active_user),
    audit_service: AuditLogService = Depends(get_audit_service),
    db: Session = Depends(get_db),
):
    """Retrieve audit events for a file owned by the authenticated user."""
    file_repo = FileRepository(db)
    file = file_repo.get_active_file_by_id(file_id)
    if not file or file.owner_id != current_user.id:
        raise FileNotFound("File not found")

    logs = audit_service.get_file_logs(file_id=file_id, limit=limit, offset=offset)
    return [AuditLogResponse.model_validate(log) for log in logs]
