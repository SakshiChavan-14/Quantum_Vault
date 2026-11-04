"""
File repository implementing data access layer for file operations.
Follows the repository pattern used throughout QuantumVault.
"""

from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.models.file import File
from app.exceptions.FileExceptions import FileNotFound


class FileRepository:
    """Repository for file database operations."""
    
    def __init__(self, db: Session):
        """
        Initialize repository with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    # ===========================
    # Create Operations
    # ===========================

    def create_file(self, file: File) -> File:
        """
        Create a new file record in the database.
        
        Args:
            file: File object to create
            
        Returns:
            Created File object with ID
        """
        self.db.add(file)
        self.db.commit()
        self.db.refresh(file)
        return file

    # ===========================
    # Read Operations
    # ===========================

    def get_file_by_id(self, file_id: str) -> Optional[File]:
        """
        Retrieve file by ID.
        
        Args:
            file_id: File UUID
            
        Returns:
            File object or None if not found
        """
        return self.db.query(File).filter(File.id == file_id).first()

    def get_active_file_by_id(self, file_id: str) -> Optional[File]:
        """
        Retrieve active (not deleted) file by ID.
        
        Args:
            file_id: File UUID
            
        Returns:
            File object or None if not found or deleted
        """
        return self.db.query(File).filter(
            and_(File.id == file_id, File.deleted_at.is_(None))
        ).first()

    def get_file_by_stored_filename(self, stored_filename: str) -> Optional[File]:
        """
        Retrieve file by stored filename (hash-based).
        
        Args:
            stored_filename: Hash-based filename
            
        Returns:
            File object or None
        """
        return self.db.query(File).filter(
            File.stored_filename == stored_filename
        ).first()

    def get_file_by_hash(self, file_hash: str) -> Optional[File]:
        """
        Retrieve file by SHA-256 hash.
        
        Args:
            file_hash: SHA-256 hash of file
            
        Returns:
            File object or None
        """
        return self.db.query(File).filter(
            and_(File.file_hash == file_hash, File.deleted_at.is_(None))
        ).first()

    # ===========================
    # List Operations
    # ===========================

    def get_files_by_owner(self, owner_id: str, include_deleted: bool = False) -> List[File]:
        """
        Get all files for a specific owner.
        
        Args:
            owner_id: User ID
            include_deleted: Whether to include soft-deleted files
            
        Returns:
            List of File objects
        """
        query = self.db.query(File).filter(File.owner_id == owner_id)
        
        if not include_deleted:
            query = query.filter(File.deleted_at.is_(None))
            
        return query.order_by(desc(File.created_at)).all()

    def get_files_by_folder(
        self,
        folder_id: Optional[str],
        include_deleted: bool = False
    ) -> List[File]:
        """
        Get all files in a specific folder.
        
        Args:
            folder_id: Folder ID (None for root)
            include_deleted: Whether to include soft-deleted files
            
        Returns:
            List of File objects
        """
        query = self.db.query(File).filter(File.folder_id == folder_id)
        
        if not include_deleted:
            query = query.filter(File.deleted_at.is_(None))
            
        return query.order_by(desc(File.created_at)).all()

    def get_files_by_folder_and_owner(
        self,
        folder_id: Optional[str],
        owner_id: str,
        include_deleted: bool = False
    ) -> List[File]:
        """
        Get all files in a folder owned by specific user.
        
        Args:
            folder_id: Folder ID
            owner_id: User ID
            include_deleted: Whether to include soft-deleted files
            
        Returns:
            List of File objects
        """
        query = self.db.query(File).filter(
            and_(File.folder_id == folder_id, File.owner_id == owner_id)
        )
        
        if not include_deleted:
            query = query.filter(File.deleted_at.is_(None))
            
        return query.order_by(desc(File.created_at)).all()

    def get_recent_files(
        self,
        owner_id: str,
        limit: int = 10,
        include_deleted: bool = False
    ) -> List[File]:
        """
        Get most recently created files for a user.
        
        Args:
            owner_id: User ID
            limit: Maximum number of files to return
            include_deleted: Whether to include soft-deleted files
            
        Returns:
            List of File objects sorted by created_at descending
        """
        query = self.db.query(File).filter(File.owner_id == owner_id)
        
        if not include_deleted:
            query = query.filter(File.deleted_at.is_(None))
            
        return query.order_by(desc(File.created_at)).limit(limit).all()

    def get_favorite_files(
        self,
        owner_id: str,
        include_deleted: bool = False
    ) -> List[File]:
        """
        Get all favorite files for a user.
        
        Args:
            owner_id: User ID
            include_deleted: Whether to include soft-deleted files
            
        Returns:
            List of File objects
        """
        query = self.db.query(File).filter(
            and_(File.owner_id == owner_id, File.is_favorite.is_(True))
        )
        
        if not include_deleted:
            query = query.filter(File.deleted_at.is_(None))
            
        return query.order_by(desc(File.created_at)).all()

    def get_shared_files(
        self,
        owner_id: str,
        include_deleted: bool = False
    ) -> List[File]:
        """
        Get all shared files for a user.
        
        Args:
            owner_id: User ID
            include_deleted: Whether to include soft-deleted files
            
        Returns:
            List of File objects
        """
        query = self.db.query(File).filter(
            and_(File.owner_id == owner_id, File.is_shared.is_(True))
        )
        
        if not include_deleted:
            query = query.filter(File.deleted_at.is_(None))
            
        return query.order_by(desc(File.created_at)).all()

    def search_files_by_name(
        self,
        owner_id: str,
        search_query: str,
        include_deleted: bool = False
    ) -> List[File]:
        """
        Search files by filename (case-insensitive).
        
        Args:
            owner_id: User ID
            search_query: Search string
            include_deleted: Whether to include soft-deleted files
            
        Returns:
            List of File objects matching search
        """
        query = self.db.query(File).filter(
            and_(
                File.owner_id == owner_id,
                File.original_filename.ilike(f"%{search_query}%")
            )
        )
        
        if not include_deleted:
            query = query.filter(File.deleted_at.is_(None))
            
        return query.order_by(desc(File.created_at)).all()

    def get_files_by_extension(
        self,
        owner_id: str,
        extension: str,
        include_deleted: bool = False
    ) -> List[File]:
        """
        Get all files with specific extension.
        
        Args:
            owner_id: User ID
            extension: File extension (e.g., "pdf", "docx")
            include_deleted: Whether to include soft-deleted files
            
        Returns:
            List of File objects
        """
        query = self.db.query(File).filter(
            and_(File.owner_id == owner_id, File.file_extension == extension)
        )
        
        if not include_deleted:
            query = query.filter(File.deleted_at.is_(None))
            
        return query.order_by(desc(File.created_at)).all()

    # ===========================
    # Update Operations
    # ===========================

    def update_file(self, file: File) -> File:
        """
        Update an existing file record.
        
        Args:
            file: File object with updates
            
        Returns:
            Updated File object
        """
        file.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(file)
        return file

    def mark_file_accessed(self, file_id: str) -> Optional[File]:
        """
        Mark file as accessed and increment access counter.
        
        Args:
            file_id: File UUID
            
        Returns:
            Updated File object or None
        """
        file = self.get_file_by_id(file_id)
        if file:
            file.mark_accessed(datetime.now(timezone.utc))
            self.db.commit()
            self.db.refresh(file)
        return file

    # ===========================
    # Delete Operations (Soft Delete)
    # ===========================

    def soft_delete_file(self, file_id: str) -> bool:
        """
        Soft delete a file (mark as deleted, don't remove from DB).
        
        Args:
            file_id: File UUID
            
        Returns:
            True if successful, False if file not found
        """
        file = self.get_file_by_id(file_id)
        if not file:
            return False
            
        file.deleted_at = datetime.now(timezone.utc)
        self.db.commit()
        return True

    def restore_deleted_file(self, file_id: str) -> bool:
        """
        Restore a soft-deleted file.
        
        Args:
            file_id: File UUID
            
        Returns:
            True if successful, False if file not found or not deleted
        """
        file = self.db.query(File).filter(File.id == file_id).first()
        if not file or file.deleted_at is None:
            return False
            
        file.deleted_at = None
        self.db.commit()
        return True

    def get_deleted_files(self, owner_id: str) -> List[File]:
        """
        Get all soft-deleted files for a user.
        
        Args:
            owner_id: User ID
            
        Returns:
            List of deleted File objects
        """
        return self.db.query(File).filter(
            and_(File.owner_id == owner_id, File.deleted_at.isnot(None))
        ).order_by(desc(File.deleted_at)).all()

    # ===========================
    # Statistics
    # ===========================

    def get_user_total_storage(self, owner_id: str, include_deleted: bool = False) -> int:
        """
        Calculate total storage used by a user.
        
        Args:
            owner_id: User ID
            include_deleted: Whether to include soft-deleted files
            
        Returns:
            Total file size in bytes
        """
        query = self.db.query(File).filter(File.owner_id == owner_id)
        
        if not include_deleted:
            query = query.filter(File.deleted_at.is_(None))
            
        files = query.all()
        return sum(f.file_size for f in files)

    def get_user_file_count(self, owner_id: str, include_deleted: bool = False) -> int:
        """
        Count total files for a user.
        
        Args:
            owner_id: User ID
            include_deleted: Whether to include soft-deleted files
            
        Returns:
            Total file count
        """
        query = self.db.query(File).filter(File.owner_id == owner_id)
        
        if not include_deleted:
            query = query.filter(File.deleted_at.is_(None))
            
        return query.count()

    def get_folder_total_storage(self, folder_id: Optional[str]) -> int:
        """
        Calculate total storage in a folder.
        
        Args:
            folder_id: Folder ID
            
        Returns:
            Total file size in bytes
        """
        files = self.db.query(File).filter(
            and_(File.folder_id == folder_id, File.deleted_at.is_(None))
        ).all()
        return sum(f.file_size for f in files)

    def get_folder_file_count(self, folder_id: Optional[str]) -> int:
        """
        Count files in a folder.
        
        Args:
            folder_id: Folder ID
            
        Returns:
            File count
        """
        return self.db.query(File).filter(
            and_(File.folder_id == folder_id, File.deleted_at.is_(None))
        ).count()

    # ===========================
    # Utility
    # ===========================

    def save(self) -> None:
        """Commit pending changes to database."""
        self.db.commit()

    def file_exists_in_folder(
        self,
        folder_id: Optional[str],
        filename: str,
        owner_id: Optional[str] = None
    ) -> bool:
        """
        Check if file with same name exists in folder for the user.
        
        Args:
            folder_id: Folder ID (None for root)
            filename: Original filename
            owner_id: Optional User ID
            
        Returns:
            True if file exists, False otherwise
        """
        filters = [
            File.original_filename == filename,
            File.deleted_at.is_(None)
        ]
        if folder_id is None:
            filters.append(File.folder_id.is_(None))
        else:
            filters.append(File.folder_id == folder_id)
            
        if owner_id:
            filters.append(File.owner_id == owner_id)
            
        return self.db.query(File).filter(and_(*filters)).first() is not None

