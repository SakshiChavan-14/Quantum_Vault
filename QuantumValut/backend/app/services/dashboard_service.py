from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.dashboard import (
    DashboardOverviewResponse,
    StorageResponse,
    DashboardRecentFilesResponse,
    DashboardActivityResponse,
    UserSummary,
    DashboardStatistics
)

class DashboardService:
    def __init__(self, repository: DashboardRepository):
        self.repository = repository

    def get_overview(self, user_id: str) -> DashboardOverviewResponse:
        data = self.repository.get_user_summary(user_id)
        if not data:
            raise ValueError("User not found")
            
        user = UserSummary(
            id=data["id"],
            full_name=data["full_name"],
            email=data["email"],
            avatar_url=data["avatar_url"],
            is_verified=data["is_verified"]
        )
        
        statistics = DashboardStatistics(**data["statistics"])
        return DashboardOverviewResponse(user=user, statistics=statistics)

    def get_storage(self, user_id: str) -> StorageResponse:
        data = self.repository.get_storage_summary(user_id)
        return StorageResponse(**data)

    def get_recent_files(self, user_id: str) -> DashboardRecentFilesResponse:
        files = self.repository.get_recent_files(user_id)
        return DashboardRecentFilesResponse(files=files)

    def get_activity(self, user_id: str) -> DashboardActivityResponse:
        activities = self.repository.get_recent_activity(user_id)
        return DashboardActivityResponse(activities=activities)
