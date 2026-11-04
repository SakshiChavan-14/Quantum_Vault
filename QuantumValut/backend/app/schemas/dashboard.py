from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class UserSummary(BaseModel):
    id: str
    full_name: str
    email: str
    avatar_url: Optional[str] = None
    is_verified: bool
    
    model_config = ConfigDict(from_attributes=True)

class DashboardStatistics(BaseModel):
    total_files: int
    total_folders: int
    favorites: int
    shared_files: int

class DashboardOverviewResponse(BaseModel):
    user: UserSummary
    statistics: DashboardStatistics

class StorageResponse(BaseModel):
    used_storage: int
    available_storage: int
    total_storage: int
    percentage_used: float

class FileItem(BaseModel):
    id: str
    name: str
    size: int
    mime_type: str
    created_at: datetime
    updated_at: datetime
    is_starred: bool
    encryption_algorithm: Optional[str] = None
    file_hash: Optional[str] = None

class DashboardRecentFilesResponse(BaseModel):
    files: List[FileItem]

class ActivityItem(BaseModel):
    id: str
    action: str
    target_name: Optional[str] = None
    created_at: datetime

class DashboardActivityResponse(BaseModel):
    activities: List[ActivityItem]
