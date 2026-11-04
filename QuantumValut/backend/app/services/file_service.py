"""
File service implementing business logic for file operations.
Handles authorization, validation, and coordination between repositories.
"""

import os
import hmac
import hashlib
from typing import List, Optional, Tuple
from datetime import datetime, timezone
from pathlib import Path
from loguru import logger

from app.models.file import File
from app.models.folder import Folder
from app.models.user import User
from app.repositories.file_repository import FileRepository
from app.repositories.folder_repository import FolderRepository
from app.schemas.file import (
    FileCreate,
    FileUpdate,
    FileResponse,
    FileListItem,
    FileListResponse,
    FileStorageStats,
    RecentFileResponse,
)
from app.exceptions.FileExceptions import (
    FileNotFound,
    FileSizeExceeded,
    InvalidFileType,
    StorageQuotaExceeded,
    FileAccessDenied,
    UploadFailed,
    FileAlreadyExists,
    InvalidFolder,
    EncryptionFailed,
    DecryptionFailed,
    FileIntegrityCompromised,
    UnsupportedEncryptionAlgorithm,
)
from app.services.encryption_service import EncryptionService
from app.services.hash_service import HashService
from app.services.pqc_crypto_service import (
    PQCCryptoService,
    PQC_ENCRYPTION_ALGORITHM,
    PQC_CRYPTO_VERSION,
    LEGACY_ENCRYPTION_ALGORITHM,
)
from app.services.key_protection_service import KeyProtectionService
from app.services.audit_log_service import AuditLogService
from app.repositories.audit_log_repository import AuditLogRepository


class FileService:
    """
    Service layer for file operations.
    Implements business logic, validation, and authorization.
    """

    # Configuration Constants
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
    USER_STORAGE_QUOTA = 5 * 1024 * 1024 * 1024  # 5 GB
    UPLOADS_DIR = Path("uploads")
    
    # Allowed file extensions (can be configured from settings)
    ALLOWED_EXTENSIONS = {
        # Documents
        'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
        'txt', 'rtf', 'odt', 'ods', 'odp',
        # Images
        'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg',
        # Videos
        'mp4', 'avi', 'mov', 'wmv', 'mkv', 'webm',
        # Audio
        'mp3', 'wav', 'flac', 'aac', 'm4a', 'wma',
        # Archives
        'zip', 'rar', '7z', 'tar', 'gz', 'bz2',
        # Code
        'py', 'js', 'java', 'cpp', 'c', 'h', 'html', 'css', 'json',
    }

    def __init__(
        self,
        file_repository: FileRepository,
        folder_repository: FolderRepository
    ):
        """
        Initialize service with repositories.
        
        Args:
            file_repository: FileRepository instance
            folder_repository: FolderRepository instance
        """
        self.file_repo = file_repository
        self.folder_repo = folder_repository
        
        # Ensure uploads directory exists
        self._ensure_uploads_directory()

    # ===========================
    # Directory Management
    # ===========================

    @staticmethod
    def _ensure_uploads_directory() -> None:
        """Create uploads directory if it doesn't exist."""
        FileService.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _get_user_upload_dir(owner_id: str) -> Path:
        """Get or create user-specific uploads directory."""
        user_dir = FileService.UPLOADS_DIR / owner_id
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir

    # ===========================
    # Validation
    # ===========================

    def _validate_file_upload(
        self,
        filename: str,
        file_size: int,
        file_content: Optional[bytes] = None
    ) -> tuple[str, str]:
        """
        Validate file before upload.
        
        Args:
            filename: Original filename
            file_size: File size in bytes
            file_content: File content (for hash calculation)
            
        Returns:
            Tuple of (extension, mime_type)
            
        Raises:
            FileSizeExceeded: If file exceeds max size
            InvalidFileType: If file extension not allowed
        """
        # Check file size
        if file_size > self.MAX_FILE_SIZE:
            raise FileSizeExceeded(
                f"File size exceeds maximum allowed ({self.MAX_FILE_SIZE / 1024 / 1024}MB)"
            )

        # Extract and validate extension
        extension = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        
        if extension and extension not in self.ALLOWED_EXTENSIONS:
            raise InvalidFileType(
                f"File type '{extension}' is not allowed"
            )

        # Determine MIME type
        mime_type = self._get_mime_type(extension)

        return extension, mime_type

    def _validate_storage_quota(self, owner_id: str, additional_size: int) -> None:
        """
        Check if user has storage quota available.
        
        Args:
            owner_id: User ID
            additional_size: Size of new file to upload
            
        Raises:
            StorageQuotaExceeded: If quota would be exceeded
        """
        current_usage = self.file_repo.get_user_total_storage(owner_id)
        
        if current_usage + additional_size > self.USER_STORAGE_QUOTA:
            raise StorageQuotaExceeded(
                f"Storage quota exceeded. Available: "
                f"{(self.USER_STORAGE_QUOTA - current_usage) / 1024 / 1024}MB"
            )

    def _validate_folder_access(
        self,
        folder_id: Optional[str],
        owner_id: str
    ) -> Optional[Folder]:
        """
        Validate that user owns the target folder.
        
        Args:
            folder_id: Folder ID (None for root)
            owner_id: User ID
            
        Returns:
            Folder object or None for root
            
        Raises:
            InvalidFolder: If folder doesn't exist or user doesn't own it
        """
        if not folder_id:
            return None

        folder = self.folder_repo.get_folder_by_id(folder_id)
        
        if not folder or folder.owner_id != owner_id:
            raise InvalidFolder("Folder not found or you don't have access")
        
        if folder.deleted_at is not None:
            raise InvalidFolder("Folder is deleted")

        return folder

    # ===========================
    # File Hashing
    # ===========================

    @staticmethod
    def _calculate_file_hash(file_content: bytes) -> str:
        """
        Calculate SHA-256 hash of file content.
        
        Args:
            file_content: File content bytes
            
        Returns:
            Hexadecimal hash string
        """
        return HashService.calculate_file_hash(file_content)

    @staticmethod
    def _generate_stored_filename(file_hash: str, extension: str) -> str:
        """
        Generate stored filename from hash and extension.
        
        Args:
            file_hash: SHA-256 hash of file
            extension: File extension
            
        Returns:
            Stored filename (e.g., "abc123def456...pdf")
        """
        if extension:
            return f"{file_hash}.{extension}"
        return file_hash

    # ===========================
    # File Upload
    # ===========================

    def upload_file(
        self,
        owner_id: str,
        filename: str,
        file_content: bytes,
        folder_id: Optional[str] = None,
        description: Optional[str] = None,
        is_favorite: bool = False
    ) -> FileResponse:
        """
        Handle complete file upload workflow with Post-Quantum Cryptography (PQC) and Audit Logging.
        
        Args:
            owner_id: User ID (owner)
            filename: Original filename
            file_content: File content bytes
            folder_id: Target folder ID (None for root)
            description: File description
            is_favorite: Mark as favorite
            
        Returns:
            FileResponse with created file details
            
        Raises:
            Various validation and encryption exceptions
        """
        audit_service = AuditLogService(AuditLogRepository(self.file_repo.db))
        file_size = len(file_content)

        audit_service.log_file_event(
            event_type="FILE_UPLOAD_STARTED",
            status="INFO",
            message=f"File upload started for '{filename}' ({file_size} bytes)",
            user_id=owner_id,
            metadata={"filename": filename, "file_size": file_size}
        )

        try:
            # 1. Validate file
            extension, mime_type = self._validate_file_upload(filename, file_size, file_content)

            # 2. Check storage quota
            self._validate_storage_quota(owner_id, file_size)

            # 3. Validate folder access
            folder = self._validate_folder_access(folder_id, owner_id)

            # 4. Check for duplicate filename in folder
            if self.file_repo.file_exists_in_folder(folder_id, filename):
                raise FileAlreadyExists(
                    f"File '{filename}' already exists in this folder"
                )

            # 5. Fetch user and obtain/provision Kyber-1024 public key
            user = self.file_repo.db.query(User).filter(User.id == owner_id).first()
            if not user:
                raise UploadFailed("File owner account not found")

            user_pk, _ = KeyProtectionService.get_or_provision_user_kyber_keys(
                user, db_session=self.file_repo.db
            )

            # 6. Execute PQC Version 2 Encryption (AES-256-GCM + Kyber1024 + HKDF-SHA256 + Key Wrap)
            try:
                pqc_bundle = PQCCryptoService.encrypt_file_pqc(file_content, user_pk)
            except Exception as e:
                logger.error(f"PQC file encryption failed for owner {owner_id}: {e}")
                audit_service.log_event(
                    event_type="FILE_ENCRYPTION_FAILED",
                    event_category="CRYPTO",
                    status="FAILURE",
                    message=f"PQC encryption failed for '{filename}': {str(e)}",
                    user_id=owner_id,
                    metadata={"filename": filename}
                )
                raise UploadFailed(f"Post-quantum encryption failed: {str(e)}")

            encrypted_content = pqc_bundle["encrypted_file_bytes"]
            nonce_hex = pqc_bundle["nonce"].hex()
            kyber_ciphertext = pqc_bundle["kyber_ciphertext"]
            wrapped_dek = pqc_bundle["wrapped_dek"]
            file_hash = pqc_bundle["file_hash"]
            encryption_algorithm = pqc_bundle["algorithm"]

            audit_service.log_event(
                event_type="FILE_ENCRYPTION_SUCCESS",
                event_category="CRYPTO",
                status="SUCCESS",
                message=f"PQC encryption completed for '{filename}' using {encryption_algorithm}",
                user_id=owner_id,
                metadata={"filename": filename, "algorithm": encryption_algorithm, "file_size": file_size}
            )

            # 7. Check if file with same hash already exists in user's storage
            existing = self.file_repo.get_file_by_hash(file_hash)
            if existing and existing.owner_id == owner_id:
                raise FileAlreadyExists("This file already exists in your storage")

            # 8. Stored filename based on plaintext SHA-256 hash
            stored_filename = self._generate_stored_filename(file_hash, extension)

            # 9. Save encrypted file to disk
            try:
                user_dir = self._get_user_upload_dir(owner_id)
                file_path = user_dir / stored_filename
                storage_path = str(file_path.relative_to(self.UPLOADS_DIR))

                with open(file_path, 'wb') as f:
                    f.write(encrypted_content)
            except Exception as e:
                raise UploadFailed(f"Failed to save encrypted file: {str(e)}")

            # 10. Create file record in database
            now = datetime.now(timezone.utc)
            new_file = File(
                owner_id=owner_id,
                folder_id=folder_id,
                original_filename=filename,
                stored_filename=stored_filename,
                file_size=file_size,  # Original plaintext file size
                mime_type=mime_type,
                file_extension=extension,
                storage_path=storage_path,
                file_hash=file_hash,  # SHA-256 hash of original plaintext
                description=description,
                is_favorite=is_favorite,
                is_shared=False,
                is_encrypted=True,
                encryption_algorithm=encryption_algorithm,  # "AES-256-GCM+Kyber1024"
                encryption_key_hash=None,                  # NULL for new PQC files
                kyber_ciphertext=kyber_ciphertext,
                encrypted_dek=wrapped_dek,
                encryption_nonce=nonce_hex,
                version=1,
                last_modified_by=owner_id,
            )

            created_file = self.file_repo.create_file(new_file)
            logger.info(f"PQC file encryption completed successfully for file_id={created_file.id}, owner={owner_id}, algorithm={encryption_algorithm}")

            # 11. Update folder stats
            if folder:
                folder.file_count += 1
                folder.folder_size += file_size
                folder.last_activity_at = now
                folder.updated_by = owner_id
                self.folder_repo.save()

            audit_service.log_file_event(
                event_type="FILE_UPLOAD_SUCCESS",
                status="SUCCESS",
                message=f"File '{filename}' uploaded and encrypted successfully",
                user_id=owner_id,
                file_id=created_file.id,
                metadata={"filename": filename, "file_size": file_size, "algorithm": encryption_algorithm}
            )

            return FileResponse.model_validate(created_file)

        except (FileAlreadyExists, StorageQuotaExceeded, InvalidFileType, InvalidFolder, UploadFailed):
            audit_service.log_file_event(
                event_type="FILE_UPLOAD_FAILED",
                status="FAILURE",
                message=f"Upload failed for '{filename}'",
                user_id=owner_id,
                metadata={"filename": filename}
            )
            raise
        except Exception as e:
            audit_service.log_file_event(
                event_type="FILE_UPLOAD_FAILED",
                status="FAILURE",
                message=f"Upload failed for '{filename}': {str(e)}",
                user_id=owner_id,
                metadata={"filename": filename}
            )
            raise UploadFailed(f"Upload failed: {str(e)}")

    # ===========================
    # File Retrieval
    # ===========================

    def get_file_by_id(self, file_id: str, owner_id: str) -> FileResponse:
        """
        Get file details (requires ownership).
        
        Args:
            file_id: File ID
            owner_id: Current user ID
            
        Returns:
            FileResponse
            
        Raises:
            FileNotFound: If file doesn't exist or user doesn't own it
        """
        file = self.file_repo.get_active_file_by_id(file_id)
        
        if not file or file.owner_id != owner_id:
            raise FileNotFound("File not found")

        return FileResponse.model_validate(file)

    def get_file_for_download(
        self,
        file_id: str,
        owner_id: str
    ) -> Tuple[File, bytes]:
        """
        Retrieve file for download with algorithm dispatch, authenticated decryption, fail-closed integrity verification, and audit logging.
        """
        audit_service = AuditLogService(AuditLogRepository(self.file_repo.db))
        audit_service.log_file_event(
            event_type="FILE_DOWNLOAD_REQUESTED",
            status="INFO",
            message=f"Download requested for file_id {file_id}",
            user_id=owner_id,
            file_id=file_id
        )

        file = self.file_repo.get_active_file_by_id(file_id)
        
        # Check authorization / existence
        if not file:
            audit_service.log_file_event(
                event_type="FILE_DOWNLOAD_FAILED",
                status="FAILURE",
                message=f"File {file_id} not found",
                user_id=owner_id,
                file_id=file_id
            )
            raise FileNotFound("File not found")

        if file.owner_id != owner_id:
            audit_service.log_security_event(
                event_type="UNAUTHORIZED_FILE_ACCESS",
                status="FAILURE",
                message=f"Unauthorized access attempt by user {owner_id} on file {file_id}",
                user_id=owner_id,
                file_id=file_id
            )
            raise FileNotFound("File not found")

        # Read encrypted payload from disk
        file_path = self.UPLOADS_DIR / file.storage_path
        if not file_path.exists():
            audit_service.log_file_event(
                event_type="FILE_DOWNLOAD_FAILED",
                status="FAILURE",
                message=f"File data missing from storage for file {file_id}",
                user_id=owner_id,
                file_id=file_id
            )
            raise FileNotFound("File data not found on storage")

        try:
            with open(file_path, 'rb') as f:
                encrypted_data = f.read()
        except Exception as e:
            raise FileNotFound(f"Failed to read file: {str(e)}")

        # Algorithm Dispatch Logic
        if not file.is_encrypted:
            # Unencrypted file
            decrypted_content = encrypted_data

        elif file.encryption_algorithm in (PQC_ENCRYPTION_ALGORITHM, "AES-256-GCM+Kyber1024", "AES-256-GCM"):
            # CASE 1: Version 2 Post-Quantum Cryptography (AES-256-GCM + Kyber-1024)
            if not (file.kyber_ciphertext and file.encrypted_dek and file.encryption_nonce):
                logger.error(f"Missing required PQC metadata on file {file_id}")
                audit_service.log_security_event(
                    event_type="FILE_DECRYPTION_FAILED",
                    status="FAILURE",
                    message=f"Missing PQC metadata on file {file_id}",
                    user_id=owner_id,
                    file_id=file_id
                )
                raise DecryptionFailed("Missing required Post-Quantum Cryptographic metadata on file record")

            user = self.file_repo.db.query(User).filter(User.id == file.owner_id).first()
            if not user:
                raise DecryptionFailed("File owner record not found")

            try:
                user_sk = KeyProtectionService.get_user_kyber_secret_key(user)
            except Exception as e:
                logger.error(f"Failed to retrieve user Kyber secret key for file {file_id}: {e}")
                audit_service.log_security_event(
                    event_type="KYBER_KEY_RETRIEVAL_FAILED",
                    status="FAILURE",
                    message=f"Failed to retrieve Kyber secret key for user {owner_id}",
                    user_id=owner_id,
                    file_id=file_id
                )
                raise DecryptionFailed("User cryptographic key material unavailable")

            try:
                nonce_bytes = bytes.fromhex(file.encryption_nonce)
            except ValueError:
                raise DecryptionFailed("Malformed encryption nonce in file record")

            try:
                decrypted_content = PQCCryptoService.decrypt_file_pqc(
                    encrypted_file_bytes=encrypted_data,
                    nonce=nonce_bytes,
                    kyber_ciphertext=file.kyber_ciphertext,
                    wrapped_dek=file.encrypted_dek,
                    recipient_kyber_secret_key=user_sk
                )
            except DecryptionFailed as e:
                audit_service.log_security_event(
                    event_type="AES_GCM_AUTHENTICATION_FAILED",
                    status="FAILURE",
                    message=f"AES-GCM authentication or decryption failed for file {file_id}",
                    user_id=owner_id,
                    file_id=file_id
                )
                raise
            except Exception as e:
                logger.error(f"PQC decryption failed for file {file_id}: {e}")
                audit_service.log_security_event(
                    event_type="FILE_DECRYPTION_FAILED",
                    status="FAILURE",
                    message=f"PQC decryption failed for file {file_id}: {str(e)}",
                    user_id=owner_id,
                    file_id=file_id
                )
                raise DecryptionFailed(f"Post-quantum decryption failed: {str(e)}")

            audit_service.log_event(
                event_type="FILE_DECRYPTION_SUCCESS",
                event_category="CRYPTO",
                status="SUCCESS",
                message=f"PQC AES-256-GCM decryption successful for file {file_id}",
                user_id=owner_id,
                file_id=file_id,
                metadata={"algorithm": file.encryption_algorithm}
            )
            logger.info(f"PQC file decryption completed successfully for file_id={file_id}")

        elif file.encryption_algorithm in (LEGACY_ENCRYPTION_ALGORITHM, "AES-128-Fernet", "Fernet") or (
            file.encryption_algorithm is None and file.is_encrypted and file.encryption_key_hash
        ):
            # CASE 2: Legacy Fernet (AES-128-Fernet)
            if not file.encryption_key_hash:
                raise DecryptionFailed("Legacy encryption key missing from file record")

            try:
                decrypted_content = EncryptionService.decrypt_file(
                    encrypted_data,
                    file.encryption_key_hash
                )
            except DecryptionFailed:
                audit_service.log_security_event(
                    event_type="FILE_DECRYPTION_FAILED",
                    status="FAILURE",
                    message=f"Legacy Fernet decryption failed for file {file_id}",
                    user_id=owner_id,
                    file_id=file_id
                )
                raise
            except Exception as e:
                logger.error(f"Legacy Fernet decryption failed for file {file_id}: {e}")
                raise DecryptionFailed(f"Legacy decryption failed: {str(e)}")

            audit_service.log_event(
                event_type="FILE_DECRYPTION_SUCCESS",
                event_category="CRYPTO",
                status="SUCCESS",
                message=f"Legacy Fernet decryption successful for file {file_id}",
                user_id=owner_id,
                file_id=file_id,
                metadata={"algorithm": "AES-128-Fernet"}
            )
            logger.info(f"Legacy Fernet decryption completed successfully for file_id={file_id}")

        else:
            # CASE 3: Unknown or Unsupported Algorithm (Fail Closed)
            logger.error(f"Unsupported encryption algorithm '{file.encryption_algorithm}' on file {file_id}")
            audit_service.log_security_event(
                event_type="UNSUPPORTED_ENCRYPTION_ALGORITHM",
                status="FAILURE",
                message=f"Unsupported encryption algorithm '{file.encryption_algorithm}' on file {file_id}",
                user_id=owner_id,
                file_id=file_id
            )
            raise UnsupportedEncryptionAlgorithm(
                f"Unsupported or unrecognized encryption algorithm: {file.encryption_algorithm}"
            )

        # Strict Constant-Time SHA-256 Integrity Verification (Fail-Closed)
        if file.file_hash:
            calculated_hash = HashService.calculate_file_hash(decrypted_content)
            if not hmac.compare_digest(calculated_hash.lower(), file.file_hash.lower()):
                logger.error(f"SECURITY ALERT - SHA-256 integrity check failed for file_id={file_id}")
                audit_service.log_security_event(
                    event_type="INTEGRITY_CHECK_FAILED",
                    status="FAILURE",
                    message=f"SHA-256 integrity check failed for file {file_id}",
                    user_id=owner_id,
                    file_id=file_id,
                    metadata={"expected_hash": file.file_hash}
                )
                raise FileIntegrityCompromised(
                    f"File integrity verification failed: payload hash mismatch detected for file {file_id}"
                )

        # Mark file as accessed
        self.file_repo.mark_file_accessed(file_id)

        audit_service.log_file_event(
            event_type="FILE_DOWNLOAD_SUCCESS",
            status="SUCCESS",
            message=f"File '{file.original_filename}' downloaded and verified successfully",
            user_id=owner_id,
            file_id=file_id,
            metadata={"filename": file.original_filename, "file_size": file.file_size}
        )

        return file, decrypted_content

    # ===========================
    # File Listing
    # ===========================

    def list_folder_contents(
        self,
        folder_id: Optional[str],
        owner_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> FileListResponse:
        """
        List files in a folder with pagination.
        
        Args:
            folder_id: Folder ID (None for root)
            owner_id: User ID
            page: Page number (1-based)
            page_size: Items per page
            
        Returns:
            FileListResponse with paginated results
        """
        # Validate folder access
        self._validate_folder_access(folder_id, owner_id)

        # Get files
        all_files = self.file_repo.get_files_by_folder_and_owner(
            folder_id, owner_id, include_deleted=False
        )

        # Paginate
        total = len(all_files)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_files = all_files[start:end]

        items = [FileListItem.model_validate(f) for f in paginated_files]

        return FileListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )

    def get_recent_files(
        self,
        owner_id: str,
        limit: int = 10
    ) -> List[RecentFileResponse]:
        """
        Get most recently created files.
        
        Args:
            owner_id: User ID
            limit: Number of files to return
            
        Returns:
            List of RecentFileResponse objects
        """
        files = self.file_repo.get_recent_files(owner_id, limit=limit)
        
        return [
            RecentFileResponse(
                id=f.id,
                original_filename=f.original_filename,
                file_size=f.file_size,
                mime_type=f.mime_type,
                file_extension=f.file_extension,
                accessed_at=f.created_at,
                action="uploaded"
            )
            for f in files
        ]

    # ===========================
    # File Updates
    # ===========================

    def rename_file(
        self,
        file_id: str,
        new_filename: str,
        owner_id: str
    ) -> FileResponse:
        """
        Rename a file.
        
        Args:
            file_id: File ID
            new_filename: New filename
            owner_id: User ID
            
        Returns:
            FileResponse with updated file
            
        Raises:
            FileNotFound: If file doesn't exist
            FileAlreadyExists: If filename already exists in folder
        """
        file = self.file_repo.get_active_file_by_id(file_id)
        
        if not file or file.owner_id != owner_id:
            raise FileNotFound("File not found")

        # Check if new filename already exists in folder
        if self.file_repo.file_exists_in_folder(file.folder_id, new_filename):
            raise FileAlreadyExists(
                f"File '{new_filename}' already exists in this folder"
            )

        # Update filename and extension
        file.original_filename = new_filename
        if '.' in new_filename:
            new_ext = new_filename.rsplit('.', 1)[-1].lower()
            file.file_extension = new_ext

        file.last_modified_by = owner_id
        file.version += 1

        updated = self.file_repo.update_file(file)
        return FileResponse.model_validate(updated)

    def move_file(
        self,
        file_id: str,
        new_folder_id: Optional[str],
        owner_id: str
    ) -> FileResponse:
        """
        Move file to another folder or root/My Drive.
        
        Args:
            file_id: File ID
            new_folder_id: Target folder ID (None for root)
            owner_id: User ID
            
        Returns:
            FileResponse with updated file
            
        Raises:
            FileNotFound: If file doesn't exist or user does not own it
            InvalidFolder: If target folder is invalid or user does not own it
            FileAlreadyExists: If filename already exists in target location
        """
        file = self.file_repo.get_active_file_by_id(file_id)
        
        if not file or file.owner_id != owner_id:
            raise FileNotFound("File not found")

        # Normalize empty string to None (root/My Drive)
        if new_folder_id in ("", "null", "None"):
            new_folder_id = None

        # If already in the target folder, return directly
        if file.folder_id == new_folder_id:
            return FileResponse.model_validate(file)

        # Validate target folder ownership & existence
        dest_folder = self._validate_folder_access(new_folder_id, owner_id)

        # Check if filename exists in target folder for this user
        if self.file_repo.file_exists_in_folder(new_folder_id, file.original_filename, owner_id=owner_id):
            dest_name = dest_folder.name if dest_folder else "My Drive"
            raise FileAlreadyExists(
                f"File '{file.original_filename}' already exists in {dest_name}"
            )

        # Update folder references
        old_folder_id = file.folder_id
        file.folder_id = new_folder_id
        file.last_modified_by = owner_id
        file.version += 1

        updated = self.file_repo.update_file(file)

        # Update folder stats
        now = datetime.now(timezone.utc)
        
        if old_folder_id:
            old_folder = self.folder_repo.get_folder_by_id(old_folder_id)
            if old_folder:
                old_folder.file_count = max(0, old_folder.file_count - 1)
                old_folder.folder_size = max(0, old_folder.folder_size - file.file_size)
                old_folder.last_activity_at = now
                old_folder.updated_by = owner_id

        if new_folder_id:
            new_folder = self.folder_repo.get_folder_by_id(new_folder_id)
            if new_folder:
                new_folder.file_count += 1
                new_folder.folder_size += file.file_size
                new_folder.last_activity_at = now
                new_folder.updated_by = owner_id

        self.folder_repo.save()

        # Audit Logging
        dest_name = dest_folder.name if dest_folder else "My Drive"
        audit_service = AuditLogService(AuditLogRepository(self.file_repo.db))
        audit_service.log_file_event(
            event_type="FILE_MOVED",
            status="SUCCESS",
            message=f"File '{file.original_filename}' moved to {dest_name}",
            user_id=owner_id,
            file_id=file_id,
            metadata={
                "filename": file.original_filename,
                "previous_folder_id": old_folder_id,
                "destination_folder_id": new_folder_id,
                "destination_folder_name": dest_name
            }
        )

        return FileResponse.model_validate(updated)

    def toggle_favorite(
        self,
        file_id: str,
        owner_id: str
    ) -> FileResponse:
        """
        Toggle file favorite status.
        
        Args:
            file_id: File ID
            owner_id: User ID
            
        Returns:
            FileResponse with updated file
        """
        file = self.file_repo.get_active_file_by_id(file_id)
        
        if not file or file.owner_id != owner_id:
            raise FileNotFound("File not found")

        file.is_favorite = not file.is_favorite
        file.last_modified_by = owner_id

        updated = self.file_repo.update_file(file)
        return FileResponse.model_validate(updated)

    # ===========================
    # File Deletion
    # ===========================

    def delete_file(self, file_id: str, owner_id: str) -> bool:
        """
        Soft delete a file.
        
        Args:
            file_id: File ID
            owner_id: User ID
            
        Returns:
            True if successful
            
        Raises:
            FileNotFound: If file doesn't exist
        """
        file = self.file_repo.get_active_file_by_id(file_id)
        
        if not file or file.owner_id != owner_id:
            raise FileNotFound("File not found")

        # Soft delete
        success = self.file_repo.soft_delete_file(file_id)

        if success:
            # Update folder stats
            if file.folder_id:
                folder = self.folder_repo.get_folder_by_id(file.folder_id)
                if folder:
                    folder.file_count = max(0, folder.file_count - 1)
                    folder.folder_size = max(0, folder.folder_size - file.file_size)
                    folder.last_activity_at = datetime.now(timezone.utc)
                    folder.updated_by = owner_id
                    self.folder_repo.save()

        return success

    def restore_file(self, file_id: str, owner_id: str) -> FileResponse:
        """
        Restore a soft-deleted file.
        
        Args:
            file_id: File ID
            owner_id: User ID
            
        Returns:
            FileResponse with restored file
        """
        file = self.file_repo.get_file_by_id(file_id)
        
        if not file or file.owner_id != owner_id or file.deleted_at is None:
            raise FileNotFound("Deleted file not found")

        # Restore
        success = self.file_repo.restore_deleted_file(file_id)

        if success:
            # Update folder stats
            if file.folder_id:
                folder = self.folder_repo.get_folder_by_id(file.folder_id)
                if folder:
                    folder.file_count += 1
                    folder.folder_size += file.file_size
                    folder.last_activity_at = datetime.now(timezone.utc)
                    folder.updated_by = owner_id
                    self.folder_repo.save()

            file = self.file_repo.get_file_by_id(file_id)

        return FileResponse.model_validate(file)

    # ===========================
    # Search
    # ===========================

    def search_files(
        self,
        owner_id: str,
        query: str,
        page: int = 1,
        page_size: int = 20
    ):
        """
        Search files by filename.
        
        Args:
            owner_id: User ID
            query: Search query
            page: Page number
            page_size: Items per page
            
        Returns:
            FileListResponse with search results
        """
        results = self.file_repo.search_files_by_name(owner_id, query)

        total = len(results)
        start = (page - 1) * page_size
        end = start + page_size
        paginated = results[start:end]

        items = [FileListItem.model_validate(f) for f in paginated]

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

    # ===========================
    # Statistics
    # ===========================

    def get_storage_stats(self, owner_id: str) -> FileStorageStats:
        """
        Get storage usage statistics for user.
        
        Args:
            owner_id: User ID
            
        Returns:
            FileStorageStats object
        """
        used = self.file_repo.get_user_total_storage(owner_id)
        available = self.USER_STORAGE_QUOTA - used
        percentage = (used / self.USER_STORAGE_QUOTA * 100) if self.USER_STORAGE_QUOTA > 0 else 0

        return FileStorageStats(
            total_storage_bytes=self.USER_STORAGE_QUOTA,
            used_storage_bytes=used,
            available_storage_bytes=max(0, available),
            file_count=self.file_repo.get_user_file_count(owner_id),
            percentage_used=round(percentage, 2)
        )

    # ===========================
    # Utility
    # ===========================

    @staticmethod
    def _get_mime_type(extension: str) -> str:
        """
        Get MIME type for file extension.
        
        Args:
            extension: File extension
            
        Returns:
            MIME type string
        """
        mime_types = {
            # Documents
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'xls': 'application/vnd.ms-excel',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'ppt': 'application/vnd.ms-powerpoint',
            'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'txt': 'text/plain',
            'rtf': 'application/rtf',
            'odt': 'application/vnd.oasis.opendocument.text',
            # Images
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'bmp': 'image/bmp',
            'webp': 'image/webp',
            'svg': 'image/svg+xml',
            # Videos
            'mp4': 'video/mp4',
            'avi': 'video/x-msvideo',
            'mov': 'video/quicktime',
            'wmv': 'video/x-ms-wmv',
            'mkv': 'video/x-matroska',
            'webm': 'video/webm',
            # Audio
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
            'flac': 'audio/flac',
            'aac': 'audio/aac',
            'm4a': 'audio/mp4',
            'wma': 'audio/x-ms-wma',
            # Archives
            'zip': 'application/zip',
            'rar': 'application/x-rar-compressed',
            '7z': 'application/x-7z-compressed',
            'tar': 'application/x-tar',
            'gz': 'application/gzip',
            'bz2': 'application/x-bzip2',
            # Code
            'py': 'text/x-python',
            'js': 'text/javascript',
            'json': 'application/json',
            'html': 'text/html',
            'css': 'text/css',
        }
        return mime_types.get(extension.lower(), 'application/octet-stream')
