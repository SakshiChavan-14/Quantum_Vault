from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth import get_current_active_user
from app.repositories.dashboard_repository import DashboardRepository
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import (
    DashboardOverviewResponse,
    StorageResponse,
    DashboardRecentFilesResponse,
    DashboardActivityResponse
)
from app.models.user import User

router = APIRouter()

def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    return DashboardService(DashboardRepository(db))

@router.get("/overview", response_model=DashboardOverviewResponse)
def get_overview(
    current_user: User = Depends(get_current_active_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    return dashboard_service.get_overview(current_user.id)

@router.get("/storage", response_model=StorageResponse)
def get_storage(
    current_user: User = Depends(get_current_active_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    return dashboard_service.get_storage(current_user.id)

@router.get("/recent-files", response_model=DashboardRecentFilesResponse)
def get_recent_files(
    current_user: User = Depends(get_current_active_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    return dashboard_service.get_recent_files(current_user.id)

@router.get("/activity", response_model=DashboardActivityResponse)
def get_activity(
    current_user: User = Depends(get_current_active_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    return dashboard_service.get_activity(current_user.id)
