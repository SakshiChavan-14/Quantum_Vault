"""
File API router implementing HTTP endpoints for file operations.
Follows REST conventions and FastAPI best practices.
"""

from fastapi import APIRouter, Depends, File, UploadFile, Query, Path, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.services.file_service import FileService
from app.dependencies.auth import get_current_active_user, get_file_service
from app.schemas.file import (
    FileResponse as FileResponseSchema,
    FileListResponse,
    FileStorageStats,
    FileRenameRequest,
    FileMoveRequest,
    FileSearchRequest,
)
from app.exceptions.FileExceptions import (
    FileNotFound,
    UploadFailed,
)


router = APIRouter()


# ===========================
# Upload Endpoint
# ===========================

@router.post(
    "/upload",
    response_model=FileResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a file",
    tags=["files"]
)
async def upload_file(
    file: UploadFile = File(..., description="File to upload"),
    folder_id: str | None = Query(None, description="Target folder ID"),
    description: str | None = Query(None, description="File description"),
    is_favorite: bool = Query(False, description="Mark as favorite"),
    current_user: User = Depends(get_current_active_user),
    file_service: FileService = Depends(get_file_service),
):
    """
    Upload a file to QuantumVault.
    
    - **file**: The file to upload
    - **folder_id**: Optional target folder (None for root)
    - **description**: Optional file description
    - **is_favorite**: Mark file as favorite
    
    Returns: FileResponse with file details
    """
    try:
        # Read file content
        content = await file.read()
        
        # Upload through service
        result = file_service.upload_file(
            owner_id=current_user.id,
            filename=file.filename,
            file_content=content,
            folder_id=folder_id,
            description=description,
            is_favorite=is_favorite
        )
        
        return result
    except UploadFailed as e:
        raise UploadFailed(str(e))
    except Exception as e:
        raise UploadFailed(f"Upload failed: {str(e)}")


# ===========================
# Download Endpoint
# ===========================

@router.get(
    "/{file_id}/download",
    summary="Download a file",
    tags=["files"]
)
async def download_file(
    file_id: str,
    current_user: User = Depends(get_current_active_user),
    file_service: FileService = Depends(get_file_service),
):
    """
    Download a file from QuantumVault.
    
    - **file_id**: ID of file to download
    
    Returns: File content with appropriate headers
    """
    try:
        file, content = file_service.get_file_for_download(
            file_id=file_id,
            owner_id=current_user.id
        )
        
        return Response(
            content=content,
            media_type=file.mime_type or "application/octet-stream",
            headers={
                "Content-Disposition": f'attachment; filename="{file.original_filename}"'
            }
        )
    except FileNotFound as e:
        raise FileNotFound(str(e))


# ===========================
# Preview Endpoint
# ===========================

@router.get(
    "/{file_id}/preview",
    summary="Preview a file",
    tags=["files"]
)
async def preview_file(
    file_id: str,
    current_user: User = Depends(get_current_active_user),
    file_service: FileService = Depends(get_file_service),
):
    """
    Preview / view a decrypted file inline in the browser.
    
    - **file_id**: ID of file to preview
    
    Returns: File content with inline disposition
    """
    try:
        file, content = file_service.get_file_for_download(
            file_id=file_id,
            owner_id=current_user.id
        )
        
        return Response(
            content=content,
            media_type=file.mime_type or "application/octet-stream",
            headers={
                "Content-Disposition": f'inline; filename="{file.original_filename}"'
            }
        )
    except FileNotFound as e:
        raise FileNotFound(str(e))


# ===========================
# Recent Files
# ===========================

@router.get(
    "/recent",
    summary="Get recent files",
    tags=["files"]
)
async def get_recent_files(
    limit: int = Query(10, ge=1, le=50, description="Number of files"),
    current_user: User = Depends(get_current_active_user),
    file_service: FileService = Depends(get_file_service),
):
    """
    Get recently uploaded/modified files.
    
    - **limit**: Maximum number of files to return
    
    Returns: List of recent files
    """
    return file_service.get_recent_files(
        owner_id=current_user.id,
        limit=limit
    )


# ===========================
# File Details Endpoint
# ===========================

@router.get(
    "/{file_id}",
    response_model=FileResponseSchema,
    summary="Get file details",
    tags=["files"]
)
async def get_file(
    file_id: str,
    current_user: User = Depends(get_current_active_user),
    file_service: FileService = Depends(get_file_service),
):
    """
    Get detailed information about a file.
    
    - **file_id**: ID of file
    
    Returns: FileResponse with file metadata
    """
    return file_service.get_file_by_id(
        file_id=file_id,
        owner_id=current_user.id
    )


# ===========================
# List Folder Contents
# ===========================

@router.get(
    "/folder/{folder_id}",
    response_model=FileListResponse,
    summary="List files in folder",
    tags=["files"]
)
async def list_folder_files(
    folder_id: str = Path(..., description="Folder ID ('null' for root)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    file_service: FileService = Depends(get_file_service),
):
    """
    List all files in a folder with pagination.
    
    - **folder_id**: Target folder ('null' for root/all files)
    - **page**: Page number (1-based)
    - **page_size**: Items per page
    
    Returns: FileListResponse with paginated results
    """
    parsed_folder_id = None if folder_id in (None, "", "null") else folder_id
    return file_service.list_folder_contents(
        folder_id=parsed_folder_id,
        owner_id=current_user.id,
        page=page,
        page_size=page_size
    )


# ===========================
# Delete Endpoint
# ===========================

@router.delete(
    "/{file_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a file",
    tags=["files"]
)
async def delete_file(
    file_id: str,
    current_user: User = Depends(get_current_active_user),
    file_service: FileService = Depends(get_file_service),
):
    """
    Soft delete a file (can be restored).
    
    - **file_id**: ID of file to delete
    
    Returns: Success message
    """
    success = file_service.delete_file(
        file_id=file_id,
        owner_id=current_user.id
    )
    
    return {
        "success": success,
        "message": "File deleted successfully"
    }


# ===========================
# Rename Endpoint
# ===========================

@router.patch(
    "/{file_id}/rename",
    response_model=FileResponseSchema,
    summary="Rename a file",
    tags=["files"]
)
async def rename_file(
    file_id: str,
    request: FileRenameRequest,
    current_user: User = Depends(get_current_active_user),
    file_service: FileService = Depends(get_file_service),
):
    """
    Rename a file.
    
    - **file_id**: ID of file to rename
    - **request**: New filename
    
    Returns: FileResponse with updated file
    """
    return file_service.rename_file(
        file_id=file_id,
        new_filename=request.new_filename,
        owner_id=current_user.id
    )


# ===========================
# Move Endpoint
# ===========================

@router.patch(
    "/{file_id}/move",
    response_model=FileResponseSchema,
    summary="Move file to folder",
    tags=["files"]
)
async def move_file(
    file_id: str,
    request: FileMoveRequest,
    current_user: User = Depends(get_current_active_user),
    file_service: FileService = Depends(get_file_service),
):
    """
    Move file to another folder or root/My Drive.
    
    - **file_id**: ID of file to move
    - **request**: Target folder_id (null for My Drive / root)
    
    Returns: FileResponse with updated file
    """
    destination_folder_id = request.get_destination_folder_id()
    return file_service.move_file(
        file_id=file_id,
        new_folder_id=destination_folder_id,
        owner_id=current_user.id
    )


# ===========================
# Toggle Favorite
# ===========================

@router.patch(
    "/{file_id}/favorite",
    response_model=FileResponseSchema,
    summary="Toggle file favorite status",
    tags=["files"]
)
async def toggle_favorite(
    file_id: str,
    current_user: User = Depends(get_current_active_user),
    file_service: FileService = Depends(get_file_service),
):
    """
    Toggle file favorite status.
    
    - **file_id**: ID of file
    
    Returns: FileResponse with updated file
    """
    return file_service.toggle_favorite(
        file_id=file_id,
        owner_id=current_user.id
    )


# ===========================
# Search Endpoint
# ===========================

@router.get(
    "/search/files",
    response_model=FileListResponse,
    summary="Search files",
    tags=["files"]
)
async def search_files(
    query: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    file_service: FileService = Depends(get_file_service),
):
    """
    Search files by filename.
    
    - **query**: Search query string
    - **page**: Page number
    - **page_size**: Items per page
    
    Returns: FileListResponse with search results
    """
    return file_service.search_files(
        owner_id=current_user.id,
        query=query,
        page=page,
        page_size=page_size
    )



# ===========================
# Storage Statistics
# ===========================

@router.get(
    "/stats/storage",
    response_model=FileStorageStats,
    summary="Get storage statistics",
    tags=["files"]
)
async def get_storage_stats(
    current_user: User = Depends(get_current_active_user),
    file_service: FileService = Depends(get_file_service),
):
    """
    Get user's storage usage statistics.
    
    Returns: FileStorageStats with usage breakdown
    """
    return file_service.get_storage_stats(owner_id=current_user.id)


# ===========================
# Restore Deleted File
# ===========================

@router.post(
    "/{file_id}/restore",
    response_model=FileResponseSchema,
    summary="Restore deleted file",
    tags=["files"]
)
async def restore_file(
    file_id: str,
    current_user: User = Depends(get_current_active_user),
    file_service: FileService = Depends(get_file_service),
):
    """
    Restore a soft-deleted file.
    
    - **file_id**: ID of deleted file
    
    Returns: FileResponse with restored file
    """
    return file_service.restore_file(
        file_id=file_id,
        owner_id=current_user.id
    )
