class FolderException(Exception):
    """Base exception for Folder domain"""
    pass

class FolderNotFound(FolderException):
    """Raised when a folder cannot be found"""
    pass

class DuplicateFolderName(FolderException):
    """Raised when a folder name already exists at the same level"""
    pass

class InvalidParentFolder(FolderException):
    """Raised when a parent folder is invalid for the operation"""
    pass

class SystemFolderOperation(FolderException):
    """Raised when attempting to modify a protected system folder"""
    pass

class FolderCircularReference(FolderException):
    """Raised when attempting to move a folder into itself or its descendants"""
    pass

class FolderMoveNotAllowed(FolderException):
    """Raised when a folder movement is invalid for other reasons"""
    pass
