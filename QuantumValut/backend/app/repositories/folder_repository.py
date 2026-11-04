from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select, update, func
from app.models.folder import Folder
from app.schemas.folder import FolderCreate, FolderUpdate

class FolderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_folder_by_id(self, folder_id: str) -> Optional[Folder]:
        stmt = select(Folder).where(Folder.id == folder_id)
        return self.db.execute(stmt).scalar_one_or_none()
        
    def get_folder_by_name_and_parent(self, owner_id: str, parent_id: Optional[str], name: str) -> Optional[Folder]:
        stmt = select(Folder).where(
            Folder.owner_id == owner_id,
            Folder.parent_id == parent_id,
            Folder.name == name
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_root_folders(self, owner_id: str) -> List[Folder]:
        stmt = select(Folder).where(
            Folder.owner_id == owner_id,
            Folder.parent_id.is_(None),
            Folder.deleted_at.is_(None)
        ).order_by(Folder.sort_order, Folder.name)
        return list(self.db.execute(stmt).scalars().all())

    def get_all_active_folders(self, owner_id: str) -> List[Folder]:
        stmt = select(Folder).where(
            Folder.owner_id == owner_id,
            Folder.deleted_at.is_(None)
        ).order_by(Folder.sort_order, Folder.name)
        return list(self.db.execute(stmt).scalars().all())

    def get_child_folders(self, parent_id: str) -> List[Folder]:
        stmt = select(Folder).where(
            Folder.parent_id == parent_id,
            Folder.deleted_at.is_(None)
        ).order_by(Folder.sort_order, Folder.name)
        return list(self.db.execute(stmt).scalars().all())

    def create_folder(self, folder: Folder) -> Folder:
        self.db.add(folder)
        self.db.commit()
        self.db.refresh(folder)
        return folder

    def update_folder(self, folder: Folder) -> Folder:
        self.db.commit()
        self.db.refresh(folder)
        return folder

    def save(self) -> None:
        self.db.commit()
