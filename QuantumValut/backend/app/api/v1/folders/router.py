from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.repositories.folder_repository import FolderRepository
from app.services.folder_service import FolderService
from app.schemas.folder import FolderCreate, FolderUpdate, FolderResponse, TreeResponse, BreadcrumbItem, MoveFolderRequest

router = APIRouter()

def get_folder_service(db: Session = Depends(get_db)) -> FolderService:
    return FolderService(FolderRepository(db))

@router.post("", response_model=FolderResponse, status_code=status.HTTP_201_CREATED)
def create_folder(
    folder_data: FolderCreate,
    current_user: User = Depends(get_current_active_user),
    service: FolderService = Depends(get_folder_service)
):
    return service.create_folder(folder_data, current_user.id)

@router.get("/root", response_model=List[FolderResponse])
def get_root_folders(
    current_user: User = Depends(get_current_active_user),
    service: FolderService = Depends(get_folder_service)
):
    return service.get_root_folders(current_user.id)

@router.get("/{folder_id}/children", response_model=List[FolderResponse])
def get_child_folders(
    folder_id: str,
    current_user: User = Depends(get_current_active_user),
    service: FolderService = Depends(get_folder_service)
):
    return service.get_child_folders(folder_id, current_user.id)

@router.patch("/{folder_id}", response_model=FolderResponse)
def update_folder(
    folder_id: str,
    update_data: FolderUpdate,
    current_user: User = Depends(get_current_active_user),
    service: FolderService = Depends(get_folder_service)
):
    return service.update_folder(folder_id, update_data, current_user.id)

@router.delete("/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_folder(
    folder_id: str,
    current_user: User = Depends(get_current_active_user),
    service: FolderService = Depends(get_folder_service)
):
    service.soft_delete_folder(folder_id, current_user.id)

@router.post("/{folder_id}/restore", status_code=status.HTTP_204_NO_CONTENT)
def restore_folder(
    folder_id: str,
    current_user: User = Depends(get_current_active_user),
    service: FolderService = Depends(get_folder_service)
):
    service.restore_folder(folder_id, current_user.id)

@router.get("/tree", response_model=TreeResponse)
def get_tree(
    current_user: User = Depends(get_current_active_user),
    service: FolderService = Depends(get_folder_service)
):
    return service.get_tree(current_user.id)

@router.get("/{folder_id}/breadcrumbs", response_model=List[BreadcrumbItem])
def get_breadcrumbs(
    folder_id: str,
    current_user: User = Depends(get_current_active_user),
    service: FolderService = Depends(get_folder_service)
):
    return service.get_breadcrumbs(folder_id, current_user.id)

@router.post("/{folder_id}/move", response_model=FolderResponse)
def move_folder(
    folder_id: str,
    request: MoveFolderRequest,
    current_user: User = Depends(get_current_active_user),
    service: FolderService = Depends(get_folder_service)
):
    return service.move_folder(folder_id, request, current_user.id)
