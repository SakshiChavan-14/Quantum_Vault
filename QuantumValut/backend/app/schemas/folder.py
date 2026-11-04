from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

class FolderBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    color: Optional[str] = Field(None, max_length=50)
    icon_name: Optional[str] = Field(None, max_length=100)
    sort_order: int = Field(default=0)
    is_favorite: bool = Field(default=False)
    is_shared: bool = Field(default=False)
    is_system: bool = Field(default=False)

class FolderCreate(FolderBase):
    parent_id: Optional[str] = None

class FolderUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    parent_id: Optional[str] = None
    description: Optional[str] = Field(None, max_length=1000)
    color: Optional[str] = Field(None, max_length=50)
    icon_name: Optional[str] = Field(None, max_length=100)
    sort_order: Optional[int] = None
    is_favorite: Optional[bool] = None

class FolderSummary(FolderBase):
    id: str
    owner_id: str
    parent_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

class FolderResponse(FolderSummary):
    children: List["FolderSummary"] = []
    
    model_config = ConfigDict(from_attributes=True)

class FolderTreeNode(FolderSummary):
    children: List["FolderTreeNode"] = []

    model_config = ConfigDict(from_attributes=True)

class TreeResponse(BaseModel):
    items: List[FolderTreeNode] = []

class BreadcrumbItem(BaseModel):
    id: str
    name: str

class MoveFolderRequest(BaseModel):
    new_parent_id: Optional[str] = None
