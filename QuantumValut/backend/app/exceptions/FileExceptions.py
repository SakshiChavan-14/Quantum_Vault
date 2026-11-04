"""
Custom exceptions for file operations in QuantumVault.
"""


class FileException(Exception):
    """Base exception for file-related errors."""
    pass


class FileNotFound(FileException):
    """Raised when a file cannot be found."""
    pass


class FileSizeExceeded(FileException):
    """Raised when file size exceeds maximum allowed limit."""
    pass


class InvalidFileType(FileException):
    """Raised when file type/extension is not allowed."""
    pass


class StorageQuotaExceeded(FileException):
    """Raised when user exceeds storage quota."""
    pass


class FileAccessDenied(FileException):
    """Raised when user doesn't have permission to access file."""
    pass


class UploadFailed(FileException):
    """Raised when file upload fails."""
    pass


class FileAlreadyExists(FileException):
    """Raised when file with same name already exists in folder."""
    pass


class InvalidFolder(FileException):
    """Raised when target folder is invalid or inaccessible."""
    pass


class EncryptionFailed(FileException):
    """Raised when file encryption fails."""
    pass


class DecryptionFailed(FileException):
    """Raised when file decryption fails."""
    pass


class FileDeletionFailed(FileException):
    """Raised when file deletion fails."""
    pass


class FileIntegrityCompromised(FileException):
    """Raised when SHA-256 integrity verification or authentication tag fails on download."""
    pass


class UnsupportedEncryptionAlgorithm(FileException):
    """Raised when encountering an unknown or unsupported encryption algorithm."""
    pass
