"""
Pydantic schemas for file operations in QuantumVault API.
These define request/response validation and serialization.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class FileBase(BaseModel):
    """Base file model with common fields."""
    
    original_filename: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=1000)
    is_favorite: bool = False
    mime_type: str = "application/octet-stream"
    file_extension: Optional[str] = None


class FileCreate(BaseModel):
    """Request model for file upload."""
    
    folder_id: Optional[str] = Field(None, description="Target folder ID")
    is_favorite: bool = False
    description: Optional[str] = Field(None, max_length=1000)


class FileUpdate(BaseModel):
    """Request model for file updates (rename, move, etc)."""
    
    original_filename: Optional[str] = Field(None, min_length=1, max_length=500)
    folder_id: Optional[str] = Field(None, description="New folder ID")
    description: Optional[str] = Field(None, max_length=1000)
    is_favorite: Optional[bool] = None


class FileResponse(BaseModel):
    """Response model for single file data."""
    
    id: str
    original_filename: str
    file_size: int
    mime_type: str
    file_extension: Optional[str]
    description: Optional[str]
    is_favorite: bool
    is_shared: bool
    is_encrypted: bool
    encryption_algorithm: Optional[str]
    version: int
    access_count: int
    created_at: datetime
    updated_at: datetime
    last_accessed_at: Optional[datetime]
    deleted_at: Optional[datetime]
    folder_id: Optional[str]
    owner_id: str

    class Config:
        from_attributes = True


class FileListItem(BaseModel):
    """Simplified file model for list responses."""
    
    id: str
    original_filename: str
    file_size: int
    mime_type: str
    file_extension: Optional[str]
    is_favorite: bool
    is_encrypted: bool
    created_at: datetime
    last_accessed_at: Optional[datetime]
    access_count: int

    class Config:
        from_attributes = True


class FileListResponse(BaseModel):
    """Response model for paginated file list."""
    
    items: List[FileListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class FileRenameRequest(BaseModel):
    """Request model for renaming a file."""
    
    new_filename: str = Field(..., min_length=1, max_length=500)


class FileMoveRequest(BaseModel):
    """Request model for moving file to another folder."""
    
    folder_id: Optional[str] = Field(None, description="Target folder ID (None/null for root/My Drive)")
    new_folder_id: Optional[str] = Field(None, description="Target folder ID (None/null for root/My Drive)")

    def get_destination_folder_id(self) -> Optional[str]:
        """Return resolved destination folder ID."""
        if self.folder_id is not None:
            return self.folder_id
        return self.new_folder_id


class FileSearchRequest(BaseModel):
    """Request model for searching files."""
    
    query: str = Field(..., min_length=1, max_length=256)
    folder_id: Optional[str] = Field(None)
    file_type: Optional[str] = Field(None, max_length=100)
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class FileSearchResponse(BaseModel):
    """Response model for search results."""
    
    items: List[FileListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class FileStorageStats(BaseModel):
    """Storage usage statistics for a user."""
    
    total_storage_bytes: int = 0
    used_storage_bytes: int = 0
    available_storage_bytes: int = 0
    file_count: int = 0
    percentage_used: float = 0.0


class RecentFileResponse(BaseModel):
    """Recent file for activity feed."""
    
    id: str
    original_filename: str
    file_size: int
    mime_type: str
    file_extension: Optional[str]
    accessed_at: Optional[datetime]
    action: str = Field(default="uploaded")  # uploaded, downloaded, shared, etc

    class Config:
        from_attributes = True


class FileShareInfo(BaseModel):
    """Information about shared files."""
    
    file_id: str
    share_link: str
    shared_by: str
    shared_at: datetime
    expires_at: Optional[datetime]
    access_level: str = "view"  # view, edit, download


class UploadProgressResponse(BaseModel):
    """Response for tracking upload progress."""
    
    file_id: Optional[str] = None
    uploaded_bytes: int = 0
    total_bytes: int = 0
    percentage: int = 0
    status: str = "uploading"  # uploading, processing, completed, failed
    message: Optional[str] = None


class BulkFileOperation(BaseModel):
    """Request model for bulk file operations."""
    
    file_ids: List[str] = Field(..., min_length=1, max_length=100)
    operation: str = Field(..., pattern="^(delete|move|archive|unarchive)$")
    target_folder_id: Optional[str] = None


class BulkFileOperationResponse(BaseModel):
    """Response for bulk operations."""
    
    successful: List[str]
    failed: List[dict]  # {"file_id": str, "error": str}
    total_processed: int


class FileEncryptionMetadata(BaseModel):
    """Metadata for encrypted files."""
    
    is_encrypted: bool
    encryption_algorithm: Optional[str]
    key_derivation: Optional[str] = "PBKDF2"
    key_iterations: Optional[int] = 100000
    salt_hex: Optional[str] = None
    iv_hex: Optional[str] = None


class FolderContentsResponse(BaseModel):
    """Response containing folder contents (files and subfolders)."""
    
    folder_id: str
    folder_name: str
    files: List[FileListItem]
    subfolders: List[dict] = []  # {"id": str, "name": str, "file_count": int}
    total_files: int
    total_size: int
