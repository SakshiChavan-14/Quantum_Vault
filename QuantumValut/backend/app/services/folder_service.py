from typing import List, Optional
from datetime import datetime, timezone
from app.repositories.folder_repository import FolderRepository
from app.schemas.folder import FolderCreate, FolderUpdate, FolderResponse, TreeResponse, FolderTreeNode, BreadcrumbItem, MoveFolderRequest
from app.models.folder import Folder
from app.exceptions.FolderExceptions import (
    FolderNotFound,
    DuplicateFolderName,
    InvalidParentFolder,
    SystemFolderOperation,
    FolderCircularReference,
    FolderMoveNotAllowed
)

class FolderService:
    def __init__(self, repository: FolderRepository):
        self.repository = repository

    def _validate_parent(self, parent_id: Optional[str], current_user_id: str) -> Optional[Folder]:
        if not parent_id:
            return None
            
        parent = self.repository.get_folder_by_id(parent_id)
        if not parent:
            raise InvalidParentFolder("Parent folder does not exist")
        if parent.owner_id != current_user_id:
            raise InvalidParentFolder("You do not own the parent folder")
        if parent.deleted_at is not None:
            raise InvalidParentFolder("Parent folder is deleted")
            
        return parent

    def _check_duplicate_name(self, owner_id: str, parent_id: Optional[str], name: str) -> None:
        duplicate = self.repository.get_folder_by_name_and_parent(owner_id, parent_id, name)
        if duplicate and duplicate.deleted_at is None:
            raise DuplicateFolderName(f"Folder '{name}' already exists in this location")

    def get_folder_by_id(self, folder_id: str, current_user_id: str) -> FolderResponse:
        folder = self.repository.get_folder_by_id(folder_id)
        if not folder or folder.owner_id != current_user_id or folder.deleted_at is not None:
            raise FolderNotFound("Folder not found")
        return FolderResponse.model_validate(folder)

    def get_root_folders(self, current_user_id: str) -> List[FolderResponse]:
        folders = self.repository.get_root_folders(current_user_id)
        return [FolderResponse.model_validate(f) for f in folders]

    def get_child_folders(self, parent_id: str, current_user_id: str) -> List[FolderResponse]:
        parent = self.repository.get_folder_by_id(parent_id)
        if not parent or parent.owner_id != current_user_id or parent.deleted_at is not None:
            raise FolderNotFound("Parent folder not found")
            
        folders = self.repository.get_child_folders(parent_id)
        return [FolderResponse.model_validate(f) for f in folders]

    def create_folder(self, folder_data: FolderCreate, current_user_id: str) -> FolderResponse:
        parent = self._validate_parent(folder_data.parent_id, current_user_id)
        
        self._check_duplicate_name(current_user_id, folder_data.parent_id, folder_data.name)
        
        now = datetime.now(timezone.utc)
        
        new_folder = Folder(
            owner_id=current_user_id,
            parent_id=folder_data.parent_id,
            name=folder_data.name,
            description=folder_data.description,
            color=folder_data.color,
            icon_name=folder_data.icon_name,
            sort_order=folder_data.sort_order,
            is_favorite=folder_data.is_favorite,
            is_shared=folder_data.is_shared,
            is_system=folder_data.is_system,
            folder_size=0,
            file_count=0,
            children_count=0,
            last_activity_at=now,
            created_by=current_user_id,
            updated_by=current_user_id
        )
        
        created = self.repository.create_folder(new_folder)
        
        if parent:
            parent.children_count += 1
            parent.last_activity_at = now
            parent.updated_by = current_user_id
            self.repository.save()
            
        return FolderResponse.model_validate(created)

    def update_folder(self, folder_id: str, update_data: FolderUpdate, current_user_id: str) -> FolderResponse:
        folder = self.repository.get_folder_by_id(folder_id)
        if not folder or folder.owner_id != current_user_id or folder.deleted_at is not None:
            raise FolderNotFound("Folder not found")
            
        if folder.is_system:
            raise SystemFolderOperation("System folders cannot be modified")
            
        if update_data.name is not None and update_data.name != folder.name:
            self._check_duplicate_name(current_user_id, folder.parent_id, update_data.name)
            folder.name = update_data.name
            
        if update_data.description is not None:
            folder.description = update_data.description
        if update_data.color is not None:
            folder.color = update_data.color
        if update_data.icon_name is not None:
            folder.icon_name = update_data.icon_name
        if update_data.sort_order is not None:
            folder.sort_order = update_data.sort_order
        if update_data.is_favorite is not None:
            folder.is_favorite = update_data.is_favorite
            
        folder.last_activity_at = datetime.now(timezone.utc)
        folder.updated_by = current_user_id
        folder.version += 1
        
        updated = self.repository.update_folder(folder)
        return FolderResponse.model_validate(updated)

    def soft_delete_folder(self, folder_id: str, current_user_id: str) -> bool:
        folder = self.repository.get_folder_by_id(folder_id)
        if not folder or folder.owner_id != current_user_id or folder.deleted_at is not None:
            raise FolderNotFound("Folder not found")
            
        if folder.is_system:
            raise SystemFolderOperation("System folders cannot be deleted")
            
        if folder.children_count > 0:
            raise InvalidParentFolder("Cannot delete folder with active children")
            
        now = datetime.now(timezone.utc)
        folder.deleted_at = now
        folder.last_activity_at = now
        folder.updated_by = current_user_id
        folder.version += 1
        
        if folder.parent_id:
            parent = self.repository.get_folder_by_id(folder.parent_id)
            if parent:
                parent.children_count = max(0, parent.children_count - 1)
                parent.last_activity_at = now
                parent.updated_by = current_user_id
                
        self.repository.save()
        return True

    def restore_folder(self, folder_id: str, current_user_id: str) -> bool:
        folder = self.repository.get_folder_by_id(folder_id)
        if not folder or folder.deleted_at is None:
            raise FolderNotFound("Deleted folder not found")
            
        if folder.owner_id != current_user_id:
            raise FolderNotFound("Deleted folder not found")
            
        parent = None
        if folder.parent_id:
            parent = self.repository.get_folder_by_id(folder.parent_id)
            if not parent:
                raise InvalidParentFolder("Parent folder does not exist")
            if parent.deleted_at is not None:
                raise InvalidParentFolder("Parent folder is deleted")
                
        self._check_duplicate_name(current_user_id, folder.parent_id, folder.name)
        
        now = datetime.now(timezone.utc)
        folder.deleted_at = None
        folder.last_activity_at = now
        folder.updated_by = current_user_id
        folder.version += 1
        
        if parent:
            parent.children_count += 1
            parent.last_activity_at = now
            parent.updated_by = current_user_id
            
        self.repository.save()
        return True

    def get_tree(self, current_user_id: str) -> TreeResponse:
        all_folders = self.repository.get_all_active_folders(current_user_id)
        
        folder_dict = {f.id: FolderTreeNode.model_validate(f) for f in all_folders}
        tree_roots = []
        
        for folder in all_folders:
            node = folder_dict[folder.id]
            if folder.parent_id is None:
                tree_roots.append(node)
            else:
                if folder.parent_id in folder_dict:
                    folder_dict[folder.parent_id].children.append(node)
                    
        return TreeResponse(items=tree_roots)

    def get_breadcrumbs(self, folder_id: str, current_user_id: str) -> List[BreadcrumbItem]:
        all_folders = self.repository.get_all_active_folders(current_user_id)
        folder_dict = {f.id: f for f in all_folders}
        
        if folder_id not in folder_dict:
            raise FolderNotFound("Folder not found")
            
        breadcrumbs = []
        current = folder_dict[folder_id]
        
        seen_ids = set()
        while current:
            if current.id in seen_ids:
                raise FolderCircularReference("Circular reference detected in breadcrumbs")
            seen_ids.add(current.id)
            
            breadcrumbs.insert(0, BreadcrumbItem(id=current.id, name=current.name))
            if current.parent_id and current.parent_id in folder_dict:
                current = folder_dict[current.parent_id]
            else:
                break
                
        return breadcrumbs

    def move_folder(self, folder_id: str, request: MoveFolderRequest, current_user_id: str) -> FolderResponse:
        folder = self.repository.get_folder_by_id(folder_id)
        if not folder or folder.owner_id != current_user_id or folder.deleted_at is not None:
            raise FolderNotFound("Folder not found")
            
        if folder.is_system:
            raise SystemFolderOperation("System folders cannot be moved")
            
        if request.new_parent_id == folder_id:
            raise FolderCircularReference("Cannot move a folder into itself")
            
        new_parent = self._validate_parent(request.new_parent_id, current_user_id)
        
        if request.new_parent_id == folder.parent_id:
            return FolderResponse.model_validate(folder)
            
        self._check_duplicate_name(current_user_id, request.new_parent_id, folder.name)
        
        # Check circular reference
        if request.new_parent_id:
            all_folders = self.repository.get_all_active_folders(current_user_id)
            folder_dict = {f.id: f for f in all_folders}
            
            current_parent = folder_dict.get(request.new_parent_id)
            while current_parent:
                if current_parent.id == folder_id:
                    raise FolderCircularReference("Cannot move a folder into its descendant")
                current_parent = folder_dict.get(current_parent.parent_id)
                
        old_parent_id = folder.parent_id
        old_parent = None
        if old_parent_id:
            old_parent = self.repository.get_folder_by_id(old_parent_id)
            
        now = datetime.now(timezone.utc)
        
        if old_parent:
            old_parent.children_count = max(0, old_parent.children_count - 1)
            old_parent.last_activity_at = now
            old_parent.updated_by = current_user_id
            
        if new_parent:
            new_parent.children_count += 1
            new_parent.last_activity_at = now
            new_parent.updated_by = current_user_id
            
        folder.parent_id = request.new_parent_id
        folder.last_activity_at = now
        folder.updated_by = current_user_id
        folder.version += 1
        
        updated = self.repository.update_folder(folder)
        self.repository.save()
        
        return FolderResponse.model_validate(updated)
